#!/usr/bin/python
# Copyright 2025 Sagar Paul (@KB-perByte)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function


__metaclass__ = type

DOCUMENTATION = """
module: dme_validate
short_description: Validate and convert configuration on DME managed devices.
description: This module validate and converts configuration on DME managed devices.
version_added: 1.0.0
options:
  lines:
    description:
      - The ordered set of commands that should be configured in the section. The commands
        must be the exact same commands as found in the device running-config to ensure
        idempotency and correct diff. Be sure to note the configuration command syntax as
        some commands are automatically modified by the device config parser.
    type: list
    elements: str
    aliases:
      - commands
  parents:
    description:
      - The ordered set of parents that uniquely identify the section or hierarchy the
        commands should be checked against.  If the parents argument is omitted, the
        commands are checked against the set of top level or global commands.
    type: list
    elements: str
  src:
    description:
      - Specifies the source path to the file that contains the configuration or configuration
        template to load. The path to the source file can either be the full path on
        the Ansible control host or a relative path from the playbook or role root directory. This
        argument is mutually exclusive with I(lines), I(parents). The configuration lines in the
        source file should be similar to how it will appear if present in the running-configuration
        of the device including the indentation to ensure idempotency and correct diff.
    type: str
author: Sagar Paul (@KB-perByte)
"""

EXAMPLES = """
# Inventory

# [dme_nxos]
# IAMBATMON

# [dme_nxos:vars]
# ansible_host={{ host_ip }}
# ansible_network_os=cisco.dme.dme
# ansible_user={{ appliance_username }}
# ansible_password={{ appliance_password }}
# ansible_connection=ansible.netcommon.httpapi
# ansible_httpapi_port={{ appliance_nxapi_port }}

# Get specific class and mo information

## Playbook
- name: Config validation on box with direct configuration
  cisco.dme.dme_validate:
    lines:
      - description A really long description for this demo
      - no speed 10000
      - duplex full
      - mtu 4096
      - ip forward
    parents: interface Ethernet1/2

## Output
# TASK [Config validation on box with direct configuration] ****************************************************
#     changed: true
#     model:
#         topSystem:
#             children:
#             -   aclEntity:
#                     children:
#                     -   ipv4aclAF:
#                             children:
#                             -   ipv4aclACL:
#                                     attributes:
#                                         name: ACL1v4344
#                                     children:
#                                     -   ipv4aclACE:
#                                             attributes:
#                                                 action: permit
#                                                 dstPrefix: 0.0.0.0
#                                                 protocol: ip
#                                                 seqNum: '10'
#                                                 srcPrefix: 0.0.0.0
#     valid: true

## Playbook
- name: Config validation on box with direct configuration - Intentional Mistake
  cisco.dme.dme_validate:
    lines:
      - idescription An intentional mistake in description
      - no speed 10000
      - duplex full
      - mtu 4096
      - ip forwarding
    parents: interface Ethernet1/2

## Output
# TASK [Config validation on box with direct configuration  - Intentional Mistake] **************************************************************
# task path: /home/sagpaul/Work/AnsibleNetwork/testathon/dme_nxos_play.yaml:6
# fatal: [IAMBATMON]: FAILED! => 
#     changed: false
#     errors:
#         1: idescription An intentional mistake in description
#         5: ip forwarding
#     model:
#         topSystem:
#             children:
#             -   interfaceEntity:
#                     children:
#                     -   l1PhysIf:
#                             attributes:
#                                 duplex: full
#                                 id: eth1/2
#                                 mtu: '4096'
#                                 speed: auto
#                                 userCfgdFlags: admin_mtu
#     valid: false
"""

RETURN = """
errors:
  description: The configuration as structured data prior to module invocation.
  returned: always
  type: list
  sample: The configuration returned will always be in the same format of the parameters above.
model:
  description: The configuration as structured data prior to module invocation.
  returned: always
  type: list
  sample: The configuration returned will always be in the same format of the parameters above.
valid:
  description: The configuration as structured data prior to module invocation.
  returned: always
  type: list
  sample: The configuration returned will always be in the same format of the parameters above.
changed:
  description: The configuration as structured data after module completion.
  returned: when changed
  type: list
  sample: The configuration returned will always be in the same format of the parameters above.
"""
