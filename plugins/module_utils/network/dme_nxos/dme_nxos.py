#
# This code is part of Ansible, but is an independent component.
#
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright: (c) 2017, Red Hat Inc.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from __future__ import absolute_import, division, print_function


__metaclass__ = type


import json
import re

from copy import deepcopy

from ansible.module_utils._text import to_text
from ansible.module_utils.common._collections_compat import Mapping
from ansible.module_utils.connection import Connection, ConnectionError
from ansible.module_utils.six import PY2, PY3
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.config import (
    CustomNetworkConfig,
    NetworkConfig,
    dumps,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    ComplexList,
    to_list,
)


try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


_DEVICE_CONNECTION = None


def get_connection(module):
    global _DEVICE_CONNECTION
    if not _DEVICE_CONNECTION:
        connection_proxy = Connection(module._socket_path)
        cap = json.loads(connection_proxy.get_capabilities())
        # if cap["network_api"] == "cliconf":
        #    conn = Cli(module)
        # elif cap["network_api"] == "nxapi":
        #    conn = HttpApi(module)
        if cap["network_api"] == "dme":
            conn = HttpApi(module)
        _DEVICE_CONNECTION = conn
    return _DEVICE_CONNECTION


class HttpApi:
    def __init__(self, module):
        self._module = module
        self._device_configs = {}
        self._module_context = {}
        self._connection_obj = None

    @property
    def _connection(self):
        if not self._connection_obj:
            self._connection_obj = Connection(self._module._socket_path)

        return self._connection_obj

    def run_commands(self, commands, check_rc=True):
        """Runs list of commands on remote device and returns results"""

        try:
            out = self._connection.send_request(commands)
        except ConnectionError as exc:
            if check_rc is True:
                raise
            out = to_text(exc)

        out = to_list(out)
        if not out[0]:
            return out

        for index, response in enumerate(out):
            if response[0] == "{":
                out[index] = json.loads(response)

        return out

    def get_config(self, flags=None):
        """Retrieves the current config from the device or cache"""
        flags = [] if flags is None else flags

        cmd = "show running-config "
        cmd += " ".join(flags)
        cmd = cmd.strip()

        try:
            return self._device_configs[cmd]
        except KeyError:
            try:
                out = self._connection.send_request(cmd)
            except ConnectionError as exc:
                self._module.fail_json(msg=to_text(exc, errors="surrogate_then_replace"))

            cfg = to_text(out).strip()
            self._device_configs[cmd] = cfg
            return cfg

    def get_diff(
        self,
        candidate=None,
        running=None,
        diff_match="line",
        diff_ignore_lines=None,
        path=None,
        diff_replace="line",
    ):
        diff = {}

        # prepare candidate configuration
        candidate_obj = NetworkConfig(indent=2)
        candidate_obj.load(candidate)

        if running and diff_match != "none" and diff_replace != "config":
            # running configuration
            running_obj = NetworkConfig(indent=2, contents=running, ignore_lines=diff_ignore_lines)
            configdiffobjs = candidate_obj.difference(
                running_obj,
                path=path,
                match=diff_match,
                replace=diff_replace,
            )

        else:
            configdiffobjs = candidate_obj.items

        diff["config_diff"] = dumps(configdiffobjs, "commands") if configdiffobjs else ""
        return diff

    def load_config(self, commands, return_error=False, opts=None, replace=None):
        """Sends the ordered set of commands to the device"""
        if opts is None:
            opts = {}

        responses = []
        try:
            resp = self.edit_config(commands, replace=replace)
        except ConnectionError as exc:
            code = getattr(exc, "code", 1)
            message = getattr(exc, "err", exc)
            err = to_text(message, errors="surrogate_then_replace")
            if opts.get("ignore_timeout") and code:
                responses.append(code)
                return responses
            elif opts.get("catch_clierror") and "400" in code:
                return [code, err]
            elif code and "no graceful-restart" in err:
                if "ISSU/HA will be affected if Graceful Restart is disabled" in err:
                    msg = [""]
                    responses.extend(msg)
                    return responses
                else:
                    self._module.fail_json(msg=err)
            elif code:
                self._module.fail_json(msg=err)

        responses.extend(resp)
        return responses

    def edit_config(self, candidate=None, commit=True, replace=None, comment=None):
        resp = list()
        import debugpy

        debugpy.listen(5003)
        debugpy.wait_for_client()
        # self.check_edit_config_capability(candidate, commit, replace, comment)

        if replace:
            candidate = "config replace {0}".format(replace)

        responses = self._connection.send_request(
            method="POST", path="/api/mo/sys.json", data=candidate
        )
        for response in to_list(responses):
            if response != "{}":
                resp.append(response)
        if not resp:
            resp = [""]

        return resp

    def get_capabilities(self):
        """Returns platform info of the remove device"""
        try:
            capabilities = self._connection.get_capabilities()
        except ConnectionError as exc:
            self._module.fail_json(msg=to_text(exc, errors="surrogate_then_replace"))

        return json.loads(capabilities)

    def check_edit_config_capability(self, candidate=None, commit=True, replace=None, comment=None):
        operations = self._connection.get_device_operations()

        if not candidate and not replace:
            raise ValueError("must provide a candidate or replace to load configuration")

        if commit not in (True, False):
            raise ValueError("'commit' must be a bool, got %s" % commit)

        if replace and not operations.get("supports_replace"):
            raise ValueError("configuration replace is not supported")

        if comment and not operations.get("supports_commit_comment", False):
            raise ValueError("commit comment is not supported")

    def read_module_context(self, module_key):
        try:
            module_context = self._connection.read_module_context(module_key)
        except ConnectionError as exc:
            self._module.fail_json(msg=to_text(exc, errors="surrogate_then_replace"))

        return module_context

    def save_module_context(self, module_key, module_context):
        try:
            self._connection.save_module_context(module_key, module_context)
        except ConnectionError as exc:
            self._module.fail_json(msg=to_text(exc, errors="surrogate_then_replace"))

        return None


def nxosCmdRef_import_check():
    """Return import error messages or empty string"""
    msg = ""
    if not HAS_YAML:
        msg += "Mandatory python library 'PyYAML' is not present, try 'pip install PyYAML'\n"
    return msg


def is_json(cmd):
    return to_text(cmd).endswith("| json")


def is_text(cmd):
    return not is_json(cmd)


def to_command(module, commands):
    transform = ComplexList(
        dict(
            command=dict(key=True),
            output=dict(type="str", default="text"),
            prompt=dict(type="list"),
            answer=dict(type="list"),
            newline=dict(type="bool", default=True),
            sendonly=dict(type="bool", default=False),
            check_all=dict(type="bool", default=False),
        ),
        module,
    )

    commands = transform(to_list(commands))

    for item in commands:
        if is_json(item["command"]):
            item["output"] = "json"

    return commands


def get_config(module, flags=None):
    flags = [] if flags is None else flags

    conn = get_connection(module)
    return conn.get_config(flags=flags)


def run_commands(module, commands, check_rc=True):
    # import debugpy

    # debugpy.listen(5003)
    # debugpy.wait_for_client()
    conn = get_connection(module)
    return conn.run_commands(to_command(module, commands), check_rc)


def load_config(module, config, return_error=False, opts=None, replace=None):
    conn = get_connection(module)
    return conn.load_config(config, return_error, opts, replace=replace)


def get_capabilities(module):
    conn = get_connection(module)
    return conn.get_capabilities()


def get_diff(
    self,
    candidate=None,
    running=None,
    diff_match="line",
    diff_ignore_lines=None,
    path=None,
    diff_replace="line",
):
    conn = self.get_connection()
    return conn.get_diff(
        candidate=candidate,
        running=running,
        diff_match=diff_match,
        diff_ignore_lines=diff_ignore_lines,
        path=path,
        diff_replace=diff_replace,
    )


def normalize_interface(name):
    """Return the normalized interface name"""
    if not name:
        return

    def _get_number(name):
        digits = ""
        for char in name:
            if char.isdigit() or char in "/.":
                digits += char
        return digits

    if name.lower().startswith("et"):
        if_type = "Ethernet"
    elif name.lower().startswith("vl"):
        if_type = "Vlan"
    elif name.lower().startswith("lo"):
        if_type = "loopback"
    elif name.lower().startswith("po"):
        if_type = "port-channel"
    elif name.lower().startswith("nv"):
        if_type = "nve"
    else:
        if_type = None

    number_list = name.split(" ")
    if len(number_list) == 2:
        number = number_list[-1].strip()
    else:
        number = _get_number(name)

    if if_type:
        proper_interface = if_type + number
    else:
        proper_interface = name

    return proper_interface


def get_interface_type(interface):
    """Gets the type of interface"""
    if interface.upper().startswith("ET"):
        return "ethernet"
    elif interface.upper().startswith("VL"):
        return "svi"
    elif interface.upper().startswith("LO"):
        return "loopback"
    elif interface.upper().startswith("MG"):
        return "management"
    elif interface.upper().startswith("MA"):
        return "management"
    elif interface.upper().startswith("PO"):
        return "portchannel"
    elif interface.upper().startswith("NV"):
        return "nve"
    else:
        return "unknown"


def default_intf_enabled(name="", sysdefs=None, mode=None):
    """Get device/version/interface-specific default 'enabled' state.
    L3:
     - Most L3 intfs default to 'shutdown'. Loopbacks default to 'no shutdown'.
     - Some legacy platforms default L3 intfs to 'no shutdown'.
    L2:
     - User-System-Default 'system default switchport shutdown' defines the
       enabled state for L2 intf's. USD defaults may be different on some platforms.
     - An intf may be explicitly defined as L2 with 'switchport' or it may be
       implicitly defined as L2 when USD 'system default switchport' is defined.
    """
    if not name:
        return None
    if sysdefs is None:
        sysdefs = {}
    default = False

    if re.search("port-channel|loopback", name):
        default = True
    elif re.search("Vlan", name):
        default = False
    else:
        if mode is None:
            # intf 'switchport' cli is not present so use the user-system-default
            mode = sysdefs.get("mode")

        if mode == "layer3":
            default = sysdefs.get("L3_enabled")
        elif mode == "layer2":
            default = sysdefs.get("L2_enabled")
    return default


def read_module_context(module):
    conn = get_connection(module)
    return conn.read_module_context(module._name)


def save_module_context(module, module_context):
    conn = get_connection(module)
    return conn.save_module_context(module._name, module_context)
