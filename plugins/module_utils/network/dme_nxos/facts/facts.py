#
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function


__metaclass__ = type
"""
The facts class for nxos
this file validates each subset of facts and selectively
calls the appropriate facts gathering function
"""
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts import (
    FactsBase,
)

from ansible_collections.cisco.dme_nxos.plugins.module_utils.network.dme_nxos.facts.interfaces.interfaces import (
    InterfacesFacts,
)
from ansible_collections.cisco.dme_nxos.plugins.module_utils.network.dme_nxos.facts.config.config import (
    ConfigFacts,
)
from ansible_collections.cisco.dme_nxos.plugins.module_utils.network.dme_nxos.facts.legacy.base import (
    Config,
    Default,
    Features,
    Hardware,
    Interfaces,
    Legacy,
)


FACT_LEGACY_SUBSETS = dict(
    default=Default,
    legacy=Legacy,
    hardware=Hardware,
    interfaces=Interfaces,
    config=Config,
    features=Features,
)
NX_FACT_RESOURCE_SUBSETS = dict(
    interfaces=InterfacesFacts,
    config=ConfigFacts,
)


class Facts(FactsBase):
    """The fact class for nxos"""

    VALID_LEGACY_GATHER_SUBSETS = frozenset(FACT_LEGACY_SUBSETS.keys())

    def __init__(self, module, chassis_type="nexus"):
        super(Facts, self).__init__(module)
        self.chassis_type = chassis_type

    def get_resource_subsets(self):
        """Return facts resource subsets based on
        target device model.
        """
        facts_resource_subsets = NX_FACT_RESOURCE_SUBSETS
        return facts_resource_subsets

    def get_facts(self, legacy_facts_type=None, resource_facts_type=None, data=None):
        """Collect the facts for nxos
        :param legacy_facts_type: List of legacy facts types
        :param resource_facts_type: List of resource fact types
        :param data: previously collected conf
        :rtype: dict
        :return: the facts gathered
        """
        VALID_RESOURCE_SUBSETS = self.get_resource_subsets()

        if frozenset(VALID_RESOURCE_SUBSETS.keys()):
            self.get_network_resources_facts(VALID_RESOURCE_SUBSETS, resource_facts_type, data)

        if self.VALID_LEGACY_GATHER_SUBSETS:
            self.get_network_legacy_facts(FACT_LEGACY_SUBSETS, legacy_facts_type)

        return self.ansible_facts, self._warnings
