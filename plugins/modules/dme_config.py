#!/usr/bin/python
# Copyright 2025 Sagar Paul (@KB-perByte)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: dme_config
short_description: A configuration module for configuration using DME model.
description: A configuration module for configuration using DME model.
version_added: 1.0.0
options:
  config:
    description: A raw DME model, validate it first using dme_validate module and then pass it here for configuration.
    type: dict
    required: true
  dummy_config:
    description: A raw DME model, validate it first using dme_validate module and then pass it here for configuration.
    type: dict
    required: false
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

# Apply provided configuration in form of DME model

## Playbook

- name: Show DME configuration information
  cisco.dme.dme_command:
    read_dn:
      entry: "sys/intf/phys-[eth1/2]"
      rsp_prop_include: "config-only"

- name: Config validation on box with direct configuration
  cisco.dme.dme_validate:
    lines:
      - description A good description for this demo
    parents: interface Ethernet1/2
  register: result_validation

- name: Config application on box with DME model
  cisco.dme.dme_config:
    config: "{{ result_validation.model }}"

## Output
# TASK [Show DME configuration information] *******************************************************
# changed: [IAMBATMON] =>
#     changed: 200
#     mo:
#         imdata:
#         -   l1PhysIf:
#                 attributes:
#                     FECMode: auto
#                     accessVlan: vlan-1
#                     adminSt: up
#                     autoNeg: 'on'
#                     beacon: 'off'
#                     bw: default
#                     controllerId: ''
#                     delay: '1'
#                     descr: An intentional mistake in description
#                     dfeAdaptiveTuning: enable
#                     dfeTuningDelay: '100'
#                     dn: sys/intf/phys-[eth1/2]
#                     dot1qEtherType: '0x8100'
#                     duplex: auto
#                     id: eth1/2
#                     inhBw: '4294967295'
#                     ituChannel: '32'
#                     layer: Layer2
#                     linkActiveJitterMgmt: disable
#                     linkDebounce: '100'
#                     linkDebounceLinkUp: '0'
#                     linkFlapErrDis: disable
#                     linkFlapErrorMax: '30'
#                     linkFlapErrorSeconds: '420'
#                     linkLog: default
#                     linkLoopback: disable
#                     linkMacUpTimer: '0'
#                     linkMaxBringUpTimer: '0'
#                     linkTransmitReset: enable
#                     mdix: auto
#                     mediaType: none
#                     medium: broadcast
#                     mode: access
#                     mtu: '1500'
#                     name: ''
#                     nativeVlan: vlan-1
#                     packetTimestampEgressSourceId: '0'
#                     packetTimestampIngressSourceId: '0'
#                     packetTimestampState: disable
#                     portT: leaf
#                     routerMac: not-applicable
#                     snmpTrapSt: enable
#                     spanMode: not-a-span-dest
#                     speed: auto
#                     speedGroup: auto
#                     transMode: not-a-trans-port
#                     trunkLog: default
#                     trunkVlans: 1-4094
#                     uniDirectionalEthernet: disable
#                     usage: discovery
#                     userCfgdFlags: ''
#                     voicePortCos: none
#                     voicePortTrust: disable
#                     voiceVlanId: none
#                     voiceVlanType: none
#         totalCount: '1'

# TASK [Config validation on box with direct configuration] *********************************************
# changed: [IAMBATMON] =>
#     changed: true
#     model:
#         topSystem:
#             children:
#             -   interfaceEntity:
#                     children:
#                     -   l1PhysIf:
#                             attributes:
#                                 descr: A good description for this demo
#                                 id: eth1/2
#     valid: true

# TASK [Config application on box with DME model] *****************************************************
# changed: [IAMBATMON] =>
#     changed: true
#     dme_response:
#         imdata: []
"""

RETURN = """
before:
  description: The configuration as structured data prior to module invocation.
  returned: always
  type: list
  sample: The configuration returned will always be in the same format of the parameters above.
after:
  description: The configuration as structured data after module completion.
  returned: when changed
  type: list
  sample: The configuration returned will always be in the same format of the parameters above.
"""
