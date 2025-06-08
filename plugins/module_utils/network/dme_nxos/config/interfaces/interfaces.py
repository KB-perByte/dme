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

import re

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)

from ansible_collections.cisco.dme_nxos.plugins.module_utils.network.dme_nxos.facts.facts import (
    Facts,
)
from ansible_collections.cisco.dme_nxos.plugins.module_utils.network.dme_nxos.utils.utils import (
    normalize_interface,
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
        self.parsers = [
            "description",
            "speed",
            "mtu",
            "duplex",
            "ip_forward",
            "fabric_forwarding_anycast_gateway",
            "mac_address",
            "logging.link_status",
            "logging.trunk_status",
            "snmp.trap.link_status",
            "service_policy.input",
            "service_policy.output",
            "service_policy.type_options.qos.input",
            "service_policy.type_options.qos.output",
            "service_policy.type_options.queuing.input",
            "service_policy.type_options.queuing.output",
        ]
        if self.state not in ["parsed", "rendered"]:
            self.defaults = {}
        else:
            # For parsed/rendered state, we assume defaults
            self.defaults = {
                "default_mode": "layer3",
                "L2_enabled": True,
            }

    def execute_module(self):
        """Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        if self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def get_switchport_defaults(self):
        """Wrapper method for `_connection.get()`
        This method exists solely to allow the unit test framework to mock device connection calls.
        """
        return self._connection.get(
            "show running-config all | incl 'system default switchport'",
        )

    def generate_commands(self):
        """Generate configuration commands to send based on
        want, have and desired state.
        """
        if self.have:
            haved = self.transform_model_dme_to_config(self.have)

        # if self.want:
        #    wantd = self.transform_model_dme_to_config(self.want)

    def _compare(self, want, have):
        """Leverages the base class `compare()` method and
        populates the list of commands to be run by comparing
        the `want` and `have` data with the `parsers` defined
        for the Interfaces network resource.
        """
        begin = len(self.commands)
        self.compare(parsers=self.parsers, want=want, have=have)

        # Handle the 'enabled' state separately
        want_enabled = want.get("enabled")
        have_enabled = have.get("enabled")
        if want_enabled is not None:
            if want_enabled != have_enabled:
                if want_enabled is True:
                    self.addcmd(want, "enabled", True)
                else:
                    self.addcmd(want, "enabled", False)
        elif not want and self.state == "overridden":
            if have_enabled is not None:
                self.addcmd(have, "enabled", False)
        elif not want and self.state == "deleted":
            if have_enabled:
                self.addcmd(have, "enabled", False)

    def transform_model_dme_to_config(self, raw_config):
        """Transforms the model from dme to config."""

        have_config = {}
        for raw_c in raw_config[0]:
            interface_raw = raw_c.get("l1PhysIf", {}).get("attributes", {})
            have_config[interface_raw["dn"]] = interface_raw
        return have_config
