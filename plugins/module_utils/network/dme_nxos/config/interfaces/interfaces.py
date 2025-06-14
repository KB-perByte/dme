#
# -*- coding: utf-8 -*-
# Copyright 2025 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function


__metaclass__ = type

"""
The nxos_interfaces config file.
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to its desired end-state is
created.
"""


from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)

from ansible_collections.cisco.dme_nxos.plugins.module_utils.network.dme_nxos.facts.facts import (
    Facts,
)


class Interfaces(ResourceModule):
    """
    The nxos_interfaces config class
    """

    def __init__(self, module):
        super(Interfaces, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="interfaces",
            tmplt=None,
        )
        self.map_config_to_dme = {
            "name": "id",
            "description": "descr",
            "speed": "speed",
            "mtu": "mtu",
            "mac_address": "routerMac",
            "mode": "layer",
            "duplex": "duplex",
            "snmp": "snmpTrapSt",
            "enabled": "adminSt",
        }
        self.l1PhysIf = []
        self.request_stuc = {
            "topSystem": {"children": [{"interfaceEntity": {"children": self.l1PhysIf}}]}
        }

    def execute_module(self):
        """Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        if self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self._connection.edit_config(candidate=self.commands)
        return self.result

    def generate_commands(self):
        """Generate configuration commands to send based on
        want, have and desired state.
        """
        if self.have:
            haved = self.transform_model_dme_to_config(self.have)

        if self.want:
            wantd = self.transform_model_config_to_dme(self.want)

        for intf, data in wantd.items():
            if intf in haved.keys():
                prep_data = {"l1PhysIf": {"attributes": data}}
                self.l1PhysIf.append(prep_data)

        self.flush_request = self.request_stuc
        self.commands.append(self.flush_request)

    def transform_model_dme_to_config(self, raw_config):
        """Transforms the model from dme to config."""

        have_config = {}
        for raw_c in raw_config[0]:
            interface_raw = raw_c.get("l1PhysIf", {}).get("attributes", {})
            have_config[interface_raw["id"]] = interface_raw
        return have_config

    def transform_model_config_to_dme(self, raw_config):
        """Transforms the model from config to dme."""
        want_config = {}
        for raw_c in raw_config:
            if raw_c.get("name"):
                raw_c["name"] = self.resolve_config_interface_name_as_dme(raw_c["name"])
                raw_c["enabled"] = "up" if raw_c.get("enabled") else "down"
                raw_c["snmp"] = "enable" if raw_c.get("snmp") else "disable"
            interface_raw = {self.map_config_to_dme.get(k, k): v for k, v in raw_c.items()}
            want_config[interface_raw["id"]] = interface_raw
        return want_config

    # not in use
    def resolve_config_interface_name_as_dme_for_dn(self, interface_name):
        """Resolves the interface name to dme format."""
        _interface_name = interface_name.lower()
        if _interface_name.startswith("eth"):
            split_interface_name = _interface_name.split("ethernet")
            return "sys/intf/phys-[eth" + split_interface_name[1] + "]"
        return interface_name

    def resolve_config_interface_name_as_dme(self, interface_name):
        """Resolves the interface name to dme format."""
        _interface_name = interface_name.lower()
        if _interface_name.startswith("eth"):
            split_interface_name = _interface_name.split("ethernet")
            return "eth" + split_interface_name[1]
        return interface_name
