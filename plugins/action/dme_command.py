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
from ansible_collections.cisco.dme.plugins.module_utils.dme import DmeRequest
from ansible_collections.cisco.dme.plugins.modules.dme_command import DOCUMENTATION


class ActionModule(ActionBase):
    """
    Action plugin for dme_command module.

    This action plugin handles DME command operations including:
    - Fetching DME class objects
    - Retrieving managed object data by distinguished name
    - Building appropriate API URLs with query parameters
    """

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
        """
        Configure and execute DME class-based API request.

        Args:
            dme_request: DmeRequest instance for making API calls
            read_class: Dictionary containing class query parameters

        Returns:
            Tuple of (api_response, code)
        """
        payload = read_class.get("entry")
        if not payload:
            raise ValueError("Class entry is required for class-based queries")

        self.api_object = f"/api/node/class/{payload}.json"

        if read_class.get("rsp_prop_include"):
            self.api_object = f"{self.api_object}?rsp-prop-include={read_class.get('rsp_prop_include')}"

        code, api_response = dme_request.get(
            self.api_object,
            data="",
        )
        return api_response, code

    def configure_mo_api(self, dme_request, read_dn):
        """
        Configure and execute DME managed object API request.

        Args:
            dme_request: DmeRequest instance for making API calls
            read_dn: Dictionary containing distinguished name query parameters

        Returns:
            Tuple of (api_response, code)
        """
        payload = read_dn.get("entry")
        if not payload:
            raise ValueError("DN entry is required for managed object queries")

        self.api_object = f"/api/mo/{payload}.json"

        # Build query parameters properly
        query_params = []

        if read_dn.get("rsp_prop_include"):
            query_params.append(f"rsp-prop-include={read_dn.get('rsp_prop_include')}")

        if read_dn.get("rsp_subtree"):
            query_params.append(f"rsp-subtree={read_dn.get('rsp_subtree')}")

        if read_dn.get("query_target"):
            query_params.append(f"query-target={read_dn.get('query_target')}")

        if read_dn.get("target_subtree_class"):
            query_params.append(
                f"target-subtree-class={read_dn.get('target_subtree_class')}",
            )

        if query_params:
            self.api_object = f"{self.api_object}?{'&'.join(query_params)}"

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
        self._check_argspec()
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
