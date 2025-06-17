#
# -*- coding: utf-8 -*-
# Copyright 2025 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The dme_nxos_config_validate config file.
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to its desired end-state is
created.
"""

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.cisco.dme_nxos.plugins.module_utils.network.dme_nxos.facts.facts import (
    Facts,
)
from ansible_collections.cisco.dme_nxos.plugins.module_utils.network.dme_nxos.rm_templates.config_validate import (
    Config_validateTemplate,
)
from typing import List, Dict, Any
import q
import json


class Config_validate(ResourceModule):
    """
    The dme_nxos_config_validate config class
    """

    def __init__(self, module):
        super(Config_validate, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="config_validate",
            tmplt=Config_validateTemplate(),
        )
        self.parsers = []

    def execute_module(self):
        """Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        if self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            resp = self._connection.validate_config(candidate=self.payload_json)
            q("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG", resp)
        return self.result

    def generate_commands(self):
        """Generate configuration commands to send based on
        want, have and desired state.
        """
        q(self.want)
        if any((self.want.get("src"), self.want.get("lines"))):
            config_raw = ""
            if self.want.get("lines"):
                for raw_config in ["before", "parents", "lines", "after"]:
                    if self.want.get(raw_config, {}):
                        if isinstance(self.want.get(raw_config), str):
                            config_raw += self.want.get(raw_config) + "\n"
                        else:
                            for conf in self.want.get(raw_config, {}):
                                config_raw += conf + "\n"
            # q(config_raw)

            if config_raw:
                # Parse configuration
                # q(config_raw)
                config_lines = self.parse_config_block(config_raw)
                # Create JSON-RPC payloads
                # q(config_lines)
                payloads = self.config_to_jsonrpc_payload(config_lines)
                # q(payloads)
                # Create formatted payload string (like your example)
                # self.payload_json = json.dumps(payloads, separators=(",", ":"))
                self.payload_json = payloads
                # q(self.payload_json)

    def parse_config_block(self, config_text: str) -> List[str]:
        """
        Parse configuration text into individual command lines

        Args:
            config_text (str): Multi-line configuration text

        Returns:
            List[str]: List of individual configuration commands
        """
        lines = []
        for line in config_text.strip().split("\n"):
            line = line.rstrip()
            if line and not line.strip().startswith("!"):  # Skip empty lines and comments
                lines.append(line)
        return lines

    def config_to_jsonrpc_payload(
        self, config_lines: List[str], start_id: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Convert configuration lines to JSON-RPC payloads

        Args:
            config_lines (List[str]): List of configuration commands
            start_id (int): Starting ID for JSON-RPC requests

        Returns:
            List[Dict]: List of JSON-RPC request payloads
        """
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
