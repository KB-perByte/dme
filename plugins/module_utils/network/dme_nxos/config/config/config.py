#
# -*- coding: utf-8 -*-
# Copyright 2025 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The dme_nxos_config config file.
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
from ansible_collections.cisco.dme_nxos.plugins.module_utils.network.dme_nxos.rm_templates.config import (
    ConfigTemplate,
)


class Config(ResourceModule):
    """
    The dme_nxos_config config class
    """

    def __init__(self, module):
        super(Config, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="config",
            tmplt=ConfigTemplate(),
        )
        self.parsers = []

    def execute_module(self):
        """Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        if self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self._connection.edit_config(candidate=self.commands)
            self.changed = True
        return self.result

    def generate_commands(self):
        """Generate configuration commands to send based on
        want, have and desired state.
        """
        self.flush_request = self.want
        self.commands.append(self.flush_request)
