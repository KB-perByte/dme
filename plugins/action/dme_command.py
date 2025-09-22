# -*- coding: utf-8 -*-
# Copyright 2025 Sagar Paul (@KB-perByte)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The module file for dme_commands module
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

from ansible_collections.cisco.dme.plugins.modules.dme_command import (
    DOCUMENTATION,
)


class ActionModule(ActionBase):
    """action module"""

    def __init__(self, *args, **kwargs):
        super(ActionModule, self).__init__(*args, **kwargs)
        self._result = None
        self._supports_async = True
        self.api_object = ""
        self.api_object_search = ""
        self.module_class_return = "class"
        self.module_mo_return = "mo"

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
            
    def configure_class_api(self, dme_request, read_class):
        payload = read_class.get("entry")
        self.api_object = f"/api/node/class/{payload}.json"
        
        if read_class.get("rsp_prop_include"):
            self.api_object = f"{self.api_object}?rsp-prop-include={read_class.get('rsp_prop_include')}"
        
        code, api_response = dme_request.get(
            self.api_object,
            data="",
        )
        return api_response, code

    def configure_mo_api(self, dme_request, read_dn):
        payload = read_dn.get("entry")
        self.api_object = f"/api/mo/{payload}.json"
        
        qt = False
        if read_dn.get("rsp_prop_include"):
            self.api_object = f"{self.api_object}?rsp-prop-include={read_dn.get('rsp_prop_include')}"
        if read_dn.get("rsp_subtree"):
            self.api_object = f"{self.api_object}?rsp-subtree={read_dn.get('rsp_subtree')}"
        if read_dn.get("query_target"):
            self.api_object = f"{self.api_object}?query-target={read_dn.get('query_target')}"
            qt = True
        if read_dn.get("target_subtree_class"):
            self.api_object = f"{self.api_object}{'&' if qt else '?'}target-subtree-class={read_dn.get('target_subtree_class')}"
        
        code, api_response = dme_request.get(
            self.api_object,
            data="",
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

        self.ask = self._task.args
        
        if self.ask.get("read_class"):
            (
                self._result[self.module_class_return],
                self._result["changed"],
            ) = self.configure_class_api(
                conn_request,
                self.ask.get("read_class"),
            )
        if self.ask.get("read_dn"):
            (
                self._result[self.module_mo_return],
                self._result["changed"],
            ) = self.configure_mo_api(
                conn_request,
                self.ask.get("read_dn"),
            )

        return self._result
