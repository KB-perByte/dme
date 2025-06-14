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
from ansible_collections.cisco.dme_nxos.plugins.module_utils.network.dme_nxos.dme_nxos import (
    get_config,
    get_connection,
    load_config,
    run_commands,
    parse_config_block,
    config_to_jsonrpc_payload,
    perform_validation,
)
import json
import q


class Config_validate:
    """
    The dme_nxos_config_validate config class
    """

    def __init__(self, module):
        self.module = module
        self.parsers = []
        self.payload_json = None

    def execute_module(self):
        """Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        # if self.state not in ["parsed", "gathered"]:
        self.generate_commands()
        op = perform_validation(self.module, self.payload_json, "/ins")
        q(op)
        return {1: "gpopd"}

    def generate_commands(self):
        """Generate configuration commands to send based on
        want, have and desired state.
        """
        # q(self.module.params["lines"])
        if any((self.module.params["src"], self.module.params["lines"])):
            config_raw = ""
            if self.module.params["lines"]:
                for raw_config in ["before", "parents", "lines", "after"]:
                    if self.module.params.get(raw_config, {}):
                        for conf in self.module.params.get(raw_config, {}):
                            config_raw += conf + "\n"
            # q(config_raw)

            if config_raw:
                # Parse configuration
                # q(config_raw)
                config_lines = parse_config_block(config_raw)
                # Create JSON-RPC payloads
                # q(config_lines)
                payloads = config_to_jsonrpc_payload(config_lines)
                # q(payloads)
                # Create formatted payload string (like your example)
                self.payload_json = json.dumps(payloads, separators=(",", ":"))
                # q(payload_json)
