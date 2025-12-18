# -*- coding: utf-8 -*-
# Copyright 2025 Sagar Paul (@KB-perByte)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The module file for dme_config module
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.connection import Connection
from ansible.plugins.action import ActionBase
from ansible_collections.ansible.utils.plugins.module_utils.common.argspec_validate import (
    AnsibleArgSpecValidator,
)
from ansible_collections.cisco.dme.plugins.module_utils.dme import DmeRequest
from ansible_collections.cisco.dme.plugins.modules.dme_config import DOCUMENTATION


class ActionModule(ActionBase):
    """
    Action plugin for dme_config module.

    This action plugin handles DME configuration operations by applying
    validated DME model data to the target device.
    """

    def __init__(self, *args, **kwargs):
        super(ActionModule, self).__init__(*args, **kwargs)
        self._result = None
        self._supports_async = True
        self.api_object = "/api/mo/sys.json"

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

    def configure_module_api(self, dme_request, payload):
        """
        Apply DME configuration to the target device.

        Args:
            dme_request: DmeRequest instance for making API calls
            payload: DME model data to apply

        Returns:
            Tuple of (api_response, changed_status)
        """
        if not payload:
            raise ValueError("Configuration payload is required")

        _, api_response = dme_request.post(
            self.api_object,
            data=payload,
        )
        return api_response, True

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

        if self._task.args.get("config") and conn_request:
            (
                self._result["dme_response"],
                self._result["changed"],
            ) = self.configure_module_api(
                conn_request,
                self._task.args["config"],
            )

        return self._result
