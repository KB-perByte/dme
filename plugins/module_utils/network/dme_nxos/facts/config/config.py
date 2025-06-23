# -*- coding: utf-8 -*-
# Copyright 2025 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The dme_nxos config fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.cisco.dme_nxos.plugins.module_utils.network.dme_nxos.rm_templates.config import (
    ConfigTemplate,
)
from ansible_collections.cisco.dme_nxos.plugins.module_utils.network.dme_nxos.argspec.config.config import (
    ConfigArgs,
)


class ConfigFacts(object):
    """The dme_nxos config facts class"""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = ConfigArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate the facts for Config network resource

        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf

        :rtype: dictionary
        :returns: facts
        """
        facts = {}
        objs = []

        if not data:
            data = {}

        ansible_facts["ansible_network_resources"].pop("interfaces", None)
        facts = {}
        facts["interfaces"] = []
        if data:
            facts["interfaces"].append(data)

        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts
