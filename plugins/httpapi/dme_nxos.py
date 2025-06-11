# (c) 2018 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function


__metaclass__ = type

DOCUMENTATION = """
author: Ansible Networking Team (@ansible-network)
name: nxos
short_description: Use NX-API to run commands on Cisco NX-OS platform
description:
- This plugin provides low level abstraction APIs for sending and receiving
  commands using NX-API with devices running Cisco NX-OS.
version_added: 1.0.0
"""

import collections
import json
import re

from ansible.module_utils._text import to_text
from ansible.module_utils.connection import ConnectionError
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import to_list
from ansible_collections.ansible.netcommon.plugins.plugin_utils.httpapi_base import HttpApiBase
from ansible.utils.display import Display

display = Display()

OPTIONS = {
    "format": ["text", "json"],
    "diff_match": ["line", "strict", "exact", "none"],
    "diff_replace": ["line", "block", "config"],
    "output": ["text", "json"],
}


class HttpApi(HttpApiBase):
    def __init__(self, *args, **kwargs):
        super(HttpApi, self).__init__(*args, **kwargs)
        self._device_info = None
        self._module_context = {}

    def login(self, username, password):
        """Login to NX-OS device using DME API"""
        # import debugpy

        # debugpy.listen(5003)
        # debugpy.wait_for_client()
        # if self.connection._auth:
        #    return

        if username and password:
            auth_data = {"aaaUser": {"attributes": {"name": username, "pwd": password}}}

            login_path = "/api/aaaLogin.json"
            try:
                response = self.send_request(method="POST", path=login_path, data=auth_data)

                # Parse authentication response
                if isinstance(response, str):
                    result = json.loads(response)
                else:
                    result = response

                # Extract token from response
                if "imdata" in result and result["imdata"]:
                    token_data = result["imdata"][0]
                    if "aaaLogin" in token_data:
                        self.connection._auth = token_data["aaaLogin"]["attributes"]["token"]
                        display.vvv(
                            f"DME authentication successful",
                            host=self.connection.get_option("host"),
                        )
                        return

                # Check for error messages
                if "error" in result:
                    error_msg = result["error"]["text"]
                    raise ConnectionError(f"Authentication failed: {error_msg}")
                else:
                    raise ConnectionError("Authentication failed: Invalid response format")

            except ConnectionError:
                raise
            except Exception as e:
                raise ConnectionError(f"Authentication failed: {to_text(e)}")
        else:
            raise ConnectionError("Username and password are required for authentication")

    def logout(self):
        """Logout from NX-OS device"""
        if self.connection._auth:
            logout_path = "/api/aaaLogout.json"
            try:
                # Set authentication header for logout
                self.connection.set_option(
                    "headers", {"Cookie": f"APIC-cookie={self.connection._auth}"}
                )
                self.send_request(
                    method="POST",
                    path=logout_path,
                )
                display.vvv("DME logout successful", host=self.connection.get_option("host"))
            except Exception as e:
                display.vvv(f"Logout failed: {to_text(e)}", host=self.connection.get_option("host"))
            finally:
                self.connection._auth = None

    def _refresh_token(self):
        """Refresh authentication token"""
        if not self.connection._auth:
            return

        refresh_path = "/api/aaaRefresh.json"
        try:
            headers = {"Cookie": f"APIC-cookie={self.connection._auth}"}
            response = self.connection.send(path=refresh_path, method="POST", headers=headers)

            # Parse refresh response
            if isinstance(response, str):
                result = json.loads(response)
            else:
                result = response

            if "imdata" in result and result["imdata"]:
                token_data = result["imdata"][0]
                if "aaaRefresh" in token_data:
                    self.connection._auth = token_data["aaaRefresh"]["attributes"]["token"]
                    display.vvv(
                        "Token refreshed successfully", host=self.connection.get_option("host")
                    )
                    return

        except Exception as e:
            display.vvv(
                f"Token refresh failed: {to_text(e)}", host=self.connection.get_option("host")
            )

        # If refresh fails, clear token to force re-authentication
        self.connection._auth = None

    def read_module_context(self, module_key):
        if self._module_context.get(module_key):
            return self._module_context[module_key]

        return None

    def save_module_context(self, module_key, module_context):
        self._module_context[module_key] = module_context

        return None

    def send_request(self, method="GET", path="/", data=None, headers=None, **kwargs):
        """Send request to DME API"""
        # Prepare headers
        if headers is None:
            headers = {}

        # Add authentication if available
        if self.connection._auth and "Cookie" not in headers:
            headers["Cookie"] = f"APIC-cookie={self.connection._auth}"

        headers.setdefault("Content-Type", "application/json")
        headers.setdefault("Accept", "application/json")

        # Prepare data
        if data is not None and not isinstance(data, str):
            data = json.dumps(data)

        try:
            response = self.connection.send(
                path=path, data=data, method=method.upper(), headers=headers, **kwargs
            )

            # Handle token expiration
            if hasattr(response, "status") and response.status in [401, 403]:
                display.vvv(
                    "Token expired, attempting to refresh", host=self.connection.get_option("host")
                )
                self._refresh_token()

                # Retry with new token
                if self.connection._auth:
                    headers["Cookie"] = f"APIC-cookie={self.connection._auth}"
                    response = self.connection.send(
                        path=path, data=data, method=method.upper(), headers=headers, **kwargs
                    )
            if "aaa" or "sys/mo" not in path:
                return json.loads(response[1].read())["imdata"]
            return response

        except Exception as e:
            raise ConnectionError(f"Request failed: {to_text(e)}")

    def _run_queue(self, queue, output):
        if self._become:
            self.connection.queue_message(
                "warning",
                "become has no effect over httpapi. Use network_cli if privilege escalation is required",
            )

        request = request_builder(queue, output)
        headers = {"Content-Type": "application/json"}

        response, response_data = self.connection.send(
            "/ins",
            request,
            headers=headers,
            method="POST",
        )

        try:
            response_data = json.loads(to_text(response_data.getvalue()))
        except ValueError:
            raise ConnectionError(
                "Response was not valid JSON, got {0}".format(to_text(response_data.getvalue())),
            )

        results = handle_response(response_data)
        return results

    def get_device_info(self):
        """Get device information via DME API"""
        if not self._device_info:
            # if not self.connection._auth:
            #    self.login(
            #        self.connection.get_option("remote_user"),
            #        self.connection.get_option("password"),
            #    )
            try:
                # Query system information
                response = self.send_request(method="GET", path="/api/node/class/topSystem.json")

                if isinstance(response, str):
                    result = json.loads(response)
                else:
                    result = response

                if "imdata" in result and result["imdata"]:
                    sys_info = result["imdata"][0]["topSystem"]["attributes"]
                    self._device_info = {
                        "network_os": "nxos",
                        "network_os_version": sys_info.get("version", "unknown"),
                        "network_os_model": sys_info.get("model", "unknown"),
                        "network_os_hostname": sys_info.get("name", "unknown"),
                        "network_os_image": sys_info.get("systemUpTime", "unknown"),
                    }

            except Exception as e:
                display.vvv(
                    f"Failed to get device info: {to_text(e)}",
                    host=self.connection.get_option("host"),
                )
                self._device_info = {
                    "network_os": "nxos",
                    "network_os_version": "unknown",
                    "network_os_model": "unknown",
                    "network_os_hostname": "unknown",
                }

        return self._device_info

    def get_device_operations(self):
        """Return supported device operations"""
        return {
            "supports_diff_replace": False,
            "supports_commit": False,
            "supports_rollback": False,
            "supports_defaults": False,
            "supports_onbox_diff": False,
            "supports_configure_session": False,
            "supports_multiline_delimiter": False,
            "supports_diff_match": False,
            "supports_diff_ignore_lines": False,
            "supports_generate_diff": False,
            "supports_replace": False,
        }

    def get_capabilities(self):
        """Return httpapi capabilities"""
        result = {}
        result["rpc"] = self.get_base_rpc()
        result["device_info"] = self.get_device_info()
        result["device_operations"] = self.get_device_operations()
        result.update(
            {
                "network_api": "dme",
                "has_message_delimiter": False,
                "supports_async": False,
            }
        )
        return json.dumps(result)

    def get_base_rpc(self):
        """Return base RPC methods"""
        return [
            "get_config",
            "edit_config",
            "get",
            "get_capabilities",
            "commit",
            "discard_changes",
            "get_diff",
        ]

    # RPC method implementations
    def get_config(self, source="running", format="json", filter=None):
        """Get configuration via DME API"""
        if source not in ["running", "startup"]:
            raise ConnectionError(f"Unsupported config source: {source}")

        # Map to appropriate DME endpoint
        if source == "running":
            path = "/api/node/mo/sys.json?query-target=subtree&target-subtree-class=*"
        else:
            path = "/api/node/mo/sys/startup.json?query-target=subtree&target-subtree-class=*"

        if filter:
            path += f"&rsp-subtree-filter={filter}"

        return self.send_request(method="GET", path=path)

    def edit_config(self, candidate, format="json", target="running"):
        """Edit configuration via DME API"""
        # import debugpy

        # debugpy.listen(5003)
        # debugpy.wait_for_client()
        if target != "running":
            raise ConnectionError(f"Unsupported config target: {target}")

        # Convert config to DME format if needed
        if isinstance(candidate, str):
            try:
                config_data = json.loads(candidate[0])
            except json.JSONDecodeError:
                raise ConnectionError("Invalid JSON configuration")
        else:
            config_data = candidate[0]

        # Post configuration to DME
        return self.send_request(method="POST", path="/api/mo/sys.json", data=config_data)

    def get(self, path, **kwargs):
        """Generic GET operation"""
        return self.send_request(method="GET", path=path, **kwargs)

    def post(self, path, data=None, **kwargs):
        """Generic POST operation"""
        return self.send_request(method="POST", path=path, data=data, **kwargs)

    def put(self, path, data=None, **kwargs):
        """Generic PUT operation"""
        return self.send_request(method="PUT", path=path, data=data, **kwargs)

    def delete(self, path, **kwargs):
        """Generic DELETE operation"""
        return self.send_request(method="DELETE", path=path, **kwargs)

    def commit(self, comment=None):
        """Commit changes - NX-OS commits automatically via DME"""
        return {"status": "success", "message": "Configuration committed automatically"}

    def discard_changes(self):
        """Discard changes - not applicable for DME API"""
        return {"status": "success", "message": "No pending changes to discard"}

    def get_diff(self, candidate=None, running=None, **kwargs):
        """Get configuration diff - basic implementation"""
        return {"diff": "Diff not supported via DME API"}


def handle_response(response):
    results = []

    if response["ins_api"].get("outputs"):
        for output in to_list(response["ins_api"]["outputs"]["output"]):
            if output["code"] != "200":
                # Best effort messages: some API output keys may not exist on some platforms
                input_data = output.get("input", "")
                msg = output.get("msg", "")
                clierror = output.get("clierror", "")
                raise ConnectionError(
                    "%s: %s: %s" % (input_data, msg, clierror),
                    code=output["code"],
                )
            elif "body" in output:
                result = output["body"]
                if isinstance(result, dict):
                    result = json.dumps(result)

                results.append(result.strip())

    return results


def request_builder(commands, output, version="1.0", chunk="0", sid=None):
    """Encodes a NXAPI JSON request message"""
    output_to_command_type = {
        "text": "cli_show_ascii",
        "json": "cli_show",
        "bash": "bash",
        "config": "cli_conf",
    }

    maybe_output = commands[0].split("|")[-1].strip()
    if maybe_output in output_to_command_type:
        command_type = output_to_command_type[maybe_output]
        commands = [command.split("|")[0].strip() for command in commands]
    else:
        try:
            command_type = output_to_command_type[output]
        except KeyError:
            msg = "invalid format, received %s, expected one of %s" % (
                output,
                ",".join(output_to_command_type.keys()),
            )
            raise ConnectionError(msg)

    if isinstance(commands, (list, set, tuple)):
        commands = " ;".join(commands)

    # Order should not matter but some versions of NX-OS software fail
    # to process the payload properly if 'input' gets serialized before
    # 'type' and the payload of 'input' contains the word 'type'.
    msg = collections.OrderedDict()
    msg["version"] = version
    msg["type"] = command_type
    msg["chunk"] = chunk
    msg["sid"] = sid
    msg["input"] = commands
    msg["output_format"] = "json"

    return json.dumps(dict(ins_api=msg))
