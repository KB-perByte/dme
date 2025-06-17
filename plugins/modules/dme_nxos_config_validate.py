#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2025 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for dme_nxos_config_validate
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: dme_nxos_config_validate
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
    type: dict
    lines:
      description:
        - The ordered set of commands that should be configured in the section. The commands
          must be the exact same commands as found in the device running-config to ensure idempotency
          and correct diff. Be sure to note the configuration command syntax as some commands are
          automatically modified by the device config parser.
      type: list
      aliases:
        - commands
      elements: str
    parents:
      description:
        - The ordered set of parents that uniquely identify the section or hierarchy the
          commands should be checked against.  If the parents argument is omitted, the
          commands are checked against the set of top level or global commands.
      type: list
      elements: str
    src:
      description:
        - The I(src) argument provides a path to the configuration file to load into the
          remote system.  The path can either be a full system path to the configuration
          file if the value starts with / or relative to the root of the implemented role
          or playbook. This argument is mutually exclusive with the I(lines) and I(parents)
          arguments. The configuration lines in the source file should be similar to how it
          will appear if present in the running-configuration of the device including indentation
          to ensure idempotency and correct diff.
      type: path
    replace_src:
      description:
        - The I(replace_src) argument provides path to the configuration file to load
          into the remote system. This argument is used to replace the entire config with
          a flat-file. This is used with argument I(replace) with value I(config). This
          is mutually exclusive with the I(lines) and I(src) arguments. This argument
          will only work for NX-OS versions that support `config replace`. Use I(nxos_file_copy)
          module to copy the flat file to remote device and then use the path with this argument.
          The configuration lines in the file should be similar to how it
          will appear if present in the running-configuration of the device including the indentation
          to ensure idempotency and correct diff.
      type: str
    before:
      description:
        - The ordered set of commands to push on to the command stack if a change needs
          to be made.  This allows the playbook designer the opportunity to perform configuration
          commands prior to pushing any changes without affecting how the set of commands
          are matched against the system.
      type: list
      elements: str
    after:
      description:
        - The ordered set of commands to append to the end of the command stack if a change
          needs to be made.  Just like with I(before) this allows the playbook designer
          to append a set of commands to be executed after the command set.
      type: list
      elements: str
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
from ansible_collections.cisco.dme_nxos.plugins.module_utils.network.dme_nxos.argspec.config_validate.config_validate import (
    Config_validateArgs,
)
from ansible_collections.cisco.dme_nxos.plugins.module_utils.network.dme_nxos.config.config_validate.config_validate import (
    Config_validate,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=Config_validateArgs.argument_spec,
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

    result = Config_validate(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
