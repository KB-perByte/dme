#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2025 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for dme_nxos_config
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: dme_nxos_config
extends_documentation_fragment:
  - cisco.dme_nxos.dme_nxos
author: Sagar Paul (@KB-perByte)
short_description: Manage Cisco NXOS configuration sections
description:
  - Cisco NXOS configurations use a simple block indent file syntax for segmenting configuration
    into sections.  This module provides an implementation for working with NXOS configuration
    sections in a deterministic way.  This module works with either CLI or NXAPI transports.
version_added: 1.0.0
options:
  config:
    description: A dictionary of config options
    type: raw
notes:
  - Unsupported for Cisco MDS
  - Abbreviated commands are NOT idempotent, see
    U(https://docs.ansible.com/ansible/latest/network/user_guide/faq.html#why-do-the-config-modules-always-return-changed-true-with-abbreviated-commands).
  - To ensure idempotency and correct diff the configuration lines in the relevant module options should be similar to how they
    appear if present in the running configuration on device including the indentation.
"""

EXAMPLES = """

"""

RETURN = """
before:
  description: The configuration prior to the module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden), C(deleted) or C(purged)
  type: dict
  sample: >
    This output will always be in the same format as the
    module argspec.
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: dict
  sample: >
    This output will always be in the same format as the
    module argspec.
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden), C(deleted) or C(purged)
  type: list
  sample:
    - sample command 1
    - sample command 2
    - sample command 3
rendered:
  description: The provided configuration in the task rendered in device-native format (offline).
  returned: when I(state) is C(rendered)
  type: list
  sample:
    - sample command 1
    - sample command 2
    - sample command 3
gathered:
  description: Facts about the network resource gathered from the remote device as structured data.
  returned: when I(state) is C(gathered)
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
parsed:
  description: The device native config provided in I(running_config) option parsed into structured data as per module argspec.
  returned: when I(state) is C(parsed)
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cisco.dme_nxos.plugins.module_utils.network.dme_nxos.argspec.config.config import (
    ConfigArgs,
)
from ansible_collections.cisco.dme_nxos.plugins.module_utils.network.dme_nxos.config.config.config import (
    Config,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=ConfigArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )

    result = Config(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
