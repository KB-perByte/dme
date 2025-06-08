#
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)#!/usr/bin/python
"""
The nxos interfaces fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
from __future__ import absolute_import, division, print_function


__metaclass__ = type

import re

from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils

from ansible_collections.cisco.dme_nxos.plugins.module_utils.network.dme_nxos.argspec.interfaces.interfaces import (
    InterfacesArgs,
)
from ansible_collections.cisco.dme_nxos.plugins.module_utils.network.dme_nxos.utils.utils import (
    get_interface_type,
)


class InterfacesFacts(object):
    """The nxos interfaces fact class"""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = InterfacesArgs.argument_spec

    def _get_interface_config(self, connection):
        return connection.get("/api/node/class/l1PhysIf.json?rsp-prop-include=config-only")

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate the facts for interfaces
        :param connection: the device connection
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        if not data:
            data = self._get_interface_config(connection)

        ansible_facts["ansible_network_resources"].pop("interfaces", None)
        facts = {}
        facts["interfaces"] = []
        if data:
            facts["interfaces"].append(data)

        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts
