# -*- coding: utf-8 -*-
# Copyright 2025 Sagar Paul (@KB-perByte)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The module file for testing
"""

from __future__ import absolute_import, division, print_function


__metaclass__ = type

from ansible.errors import AnsibleActionFail
from ansible.module_utils.connection import Connection
from ansible.module_utils.six import iteritems
from ansible.plugins.action import ActionBase
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.ansible.utils.plugins.module_utils.common.argspec_validate import (
    AnsibleArgSpecValidator,
)

from ansible_collections.cisco.dme.plugins.module_utils.dme import (
    DmeRequest,
)

import q

class ActionModule(ActionBase):
    """action module"""

    def __init__(self, *args, **kwargs):
        super(ActionModule, self).__init__(*args, **kwargs)
        self._result = None
        self._supports_async = True
        self.api_object = "/ins"
        self.api_object_search = "/api/loginspectionrules/search"
        self.api_return = "logInspectionRules"
        self.module_return = "log_inspection_rules"


    def log_files_fn(self, module_params):
        temp_obj = {}
        if module_params.get("log_files"):
            temp_obj = {
                "logFiles": module_params.get("log_files")["log_files"],
            }
        elif module_params.get("logFiles"):
            temp_obj["log_files"] = module_params["logFiles"]["logFiles"]
        return temp_obj

    def configure_module_api(self, dme_request, payload):
        code, api_response = dme_request.get(
            "{0}".format("/api/node/class/ipv4aclACL.json?rsp-prop-include=config-only"),
            data="",
        )
        return api_response, True

    def configure_module_rpc(self, dme_request, payload):
        q(3)
        code, api_response = dme_request.rpc_get(
            "{0}".format(self.api_object),
            data=payload,
        )
        return api_response, True

    def run(self, tmp=None, task_vars=None):
        # import debugpy

        # debugpy.listen(3000)
        # debugpy.wait_for_client()
        self._supports_check_mode = True
        self._result = super(ActionModule, self).run(tmp, task_vars)
        self._result["changed"] = False
        if self._result.get("failed"):
            return self._result
        
        conn = Connection(self._connection.socket_path)
        conn_request = DmeRequest(
            connection=conn,
            task_vars=task_vars,
        )

        # (
        #     self._result[self.module_return],
        #     self._result["changed"],
        # ) = self.configure_module_api(
        #     conn_request,
        #     "",
        # )
        
        q(self._result)
        q("moving to the rpc call")
        q(self._task.args["config"])
        (
            self._result[self.module_return],
            self._result["changed"],
        ) = self.configure_module_rpc(
            conn_request,
            self._task.args["config"],
        )

        return self._result
