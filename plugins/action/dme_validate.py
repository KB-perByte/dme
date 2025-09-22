# -*- coding: utf-8 -*-
# Copyright 2025 Sagar Paul (@KB-perByte)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The module file for dme_validate module
"""

from __future__ import absolute_import, division, print_function


__metaclass__ = type

from ansible.module_utils.connection import Connection
from ansible.plugins.action import ActionBase

from ansible_collections.ansible.utils.plugins.module_utils.common.argspec_validate import (
    AnsibleArgSpecValidator,
)

from ansible_collections.cisco.dme.plugins.module_utils.dme import (
    DmeRequest,
)
from ansible_collections.cisco.dme.plugins.modules.dme_validate import (
    DOCUMENTATION,
)


class ActionModule(ActionBase):
    """action module"""

    def __init__(self, *args, **kwargs):
        super(ActionModule, self).__init__(*args, **kwargs)
        self._result = None
        self._supports_async = True
        self.api_object = "/ins"

    def parse_config_block(self, config_text):
        lines = []
        for line in config_text.strip().split("\n"):
            line = line.rstrip()
            if line and not line.strip().startswith("!"):  # Skip empty lines and comments
                lines.append(line)
        return lines

    def _check_argspec(self):
        aav = AnsibleArgSpecValidator(
            data=self._task.args,
            schema=DOCUMENTATION,
            schema_format="doc",
            name=self._task.action,
        )
        valid, errors, self._task.args = aav.validate()
        if not valid:
            self._result["failed"] = True
            self._result["msg"] = errors

    def config_to_jsonrpc_payload(self, config_lines, start_id=1):
        payloads = []

        for i, cmd in enumerate(config_lines):
            payload = {
                "jsonrpc": "2.0",
                "method": "cli_rest",
                "option": "default",
                "params": {"cmd": cmd, "version": 1},
                "id": start_id + i,
            }
            payloads.append(payload)

        return payloads


    def configure_module_rpc(self, dme_request, payload):
        code, api_response = dme_request.rpc_get(
            "{0}".format(self.api_object),
            data=payload,
        )
        return api_response, code


    def run(self, tmp=None, task_vars=None):
        self._supports_check_mode = False
        self._result = super(ActionModule, self).run(tmp, task_vars)
        
        self._check_argspec()
        
        self._result["changed"] = False
        if self._result.get("failed"):
            return self._result
        
        conn = Connection(self._connection.socket_path)
        conn_request = DmeRequest(
            connection=conn,
            task_vars=task_vars,
        )
        
        # code, api_response = conn_request.get(
        #     "/api/node/class/ipv4aclACL.json",
        #     data="",
        # )

        if any((self._task.args.get("src"), self._task.args.get("lines"))):
            config_raw = ""
            if self._task.args.get("lines"):
                for raw_config in ["parents", "lines"]:
                    if self._task.args.get(raw_config, {}):
                        if isinstance(self._task.args.get(raw_config), str):
                            config_raw += self._task.args.get(raw_config) + "\n"
                        else:
                            for conf in self._task.args.get(raw_config, {}):
                                config_raw += conf + "\n"
        
        config_lines = self.parse_config_block(config_raw)
        payloads = self.config_to_jsonrpc_payload(config_lines)
        
        (
            model_response,
            _,
        ) = self.configure_module_rpc(
            conn_request,
            payloads,
        )
        
        self._result["model"] = model_response.get("dme_data", {})
        errorMap = model_response.pop("errors", {})
        
        if errorMap:
            # if "Bad Request" in endpointResponse["error"]:
            config_list = config_raw.split("\n")
            new_err_map = {}
            for idx, cmd in errorMap.items():
                new_err_map[idx] = config_list[idx]
                
            # self._result["failed"] = True
            self._result["changed"] = True
            self._result["valid"] = False
            self._result["errors"] = new_err_map
        else:
            self._result["valid"] = True
            self._result["changed"] = True

        return self._result
