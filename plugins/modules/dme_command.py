#!/usr/bin/python
# Copyright 2025 Sagar Paul (@KB-perByte)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: dme_command
short_description: Fetch arbitrary DME model based on node class.
description: Fetch arbitrary DME model based on node class.
version_added: 1.0.0
options:
  read_class:
    description: Add the node class input to get the list of objects of that DME class.
    type: dict
    suboptions:
      entry:
        description:
          - Add the entry key to get the specific object details.
          - Expects attributes after /api/node/class/{entry}.json
          - Example - ipv4aclACL, l1PhysIf, l2BD, etc.
        type: str
      rsp_prop_include:
        description: Add this option to get specific attributes of the object.
        type: str
        choices:
          - config-only
  read_dn:
    description: Add the dn entry to get the specific object details.
    type: dict
    suboptions:
      entry:
        description:
          - Add the entry key to get the specific mo object details.
          - Expects attributes after /api/mo/{entry}.json
          - Example - sys, sys/intf/phys-[eth1/1], sys/bgp, sys/bd/bd-[vlan-100], etc.
        type: str
      rsp_prop_include:
        description: Add this option to get specific attributes of the object.
        type: str
        choices:
          - config-only
      rsp_subtree:
        description: Specify subtree attributes of the object.
        type: str
        choices:
          - full
      query_target:
        description: Specify query target to start.
        type: str
        choices:
          - subtree
      target_subtree_class:
        description: Specify target subtree of the class to explore.
        type: str
        choices:
          - topSystem
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
- name: Show DME configuration information
  cisco.dme.dme_command:
    read_class:
      entry: "ipv4aclACL"
      rsp_prop_include: "config-only"
    read_dn:
      entry: "sys/intf/phys-[eth1/1]"
      rsp_subtree: "full"

## Output
# TASK [Show DME configuration information] ***************************
# changed: [IAMBATMON] =>
#     changed: true
#     class:
#         imdata:
#         -   ipv4aclACL:
#                 attributes:
#                     dn: sys/acl/ipv4/name-[ACL2v4]
#                     fragments: disabled
#                     ignRoutable: 'no'
#                     name: ACL2v4
#                     perACEStatistics: 'off'
#                     udfPresent: 'no'
#         -   ipv4aclACL:
#                 attributes:
#                     dn: sys/acl/ipv4/name-[ACL1v4]
#                     fragments: disabled
#                     ignRoutable: 'no'
#                     name: ACL1v4
#                     perACEStatistics: 'off'
#                     udfPresent: 'no'
#         -   ipv4aclACL:
#                 attributes:
#                     dn: sys/acl/ipv4/name-[ACL2v411]
#                     fragments: disabled
#                     ignRoutable: 'no'
#                     name: ACL2v411
#                     perACEStatistics: 'off'
#                     udfPresent: 'no'
#         -   ipv4aclACL:
#                 attributes:
#                     dn: sys/acl/ipv4/name-[ACL1v411]
#                     fragments: disabled
#                     ignRoutable: 'no'
#                     name: ACL1v411
#                     perACEStatistics: 'off'
#                     udfPresent: 'no'
#         -   ipv4aclACL:
#                 attributes:
#                     dn: sys/acl/ipv4/name-[ACL2v4113]
#                     fragments: disabled
#                     ignRoutable: 'no'
#                     name: ACL2v4113
#                     perACEStatistics: 'off'
#                     udfPresent: 'no'
#         totalCount: '5'
#    mo:
#        imdata:
#        -   l1PhysIf:
#                attributes:
#                    FECMode: auto
#                    accessVlan: vlan-1
#                    adminSt: up
#                    autoNeg: 'on'
#                    beacon: 'off'
#                    bw: default
#                    childAction: ''
#                    controllerId: ''
#                    delay: '1'
#                    descr: ''
#                    dfeAdaptiveTuning: enable
#                    dfeTuningDelay: '100'
#                    dn: sys/intf/phys-[eth1/1]
#                    dot1qEtherType: '0x8100'
#                    duplex: auto
#                    ethpmCfgFailedBmp: ''
#                    ethpmCfgFailedTs: '0'
#                    ethpmCfgState: '0'
#                    id: eth1/1
#                    inhBw: '4294967295'
#                    ituChannel: '32'
#                    layer: Layer2
#                    linkActiveJitterMgmt: disable
#                    linkDebounce: '100'
#                    linkDebounceLinkUp: '0'
#                    linkFlapErrDis: disable
#                    linkFlapErrorMax: '30'
#                    linkFlapErrorSeconds: '420'
#                    linkLog: default
#                    linkLoopback: disable
#                    linkMacUpTimer: '0'
#                    linkMaxBringUpTimer: '0'
#                    linkTransmitReset: enable
#                    mdix: auto
#                    mediaType: none
#                    medium: broadcast
#                    modTs: '2025-09-17T13:30:01.339+00:00'
#                    mode: access
#                    mtu: '1500'
#                    name: ''
#                    nativeVlan: vlan-1
#                    packetTimestampEgressSourceId: '0'
#                    packetTimestampIngressSourceId: '0'
#                    packetTimestampState: disable
#                    portT: leaf
#                    routerMac: not-applicable
#                    snmpTrapSt: enable
#                    spanMode: not-a-span-dest
#                    speed: auto
#                    speedGroup: auto
#                    status: ''
#                    switchingSt: disabled
#                    transMode: not-a-trans-port
#                    trunkLog: default
#                    trunkVlans: 1-4094
#                    uniDirectionalEthernet: disable
#                    usage: discovery
#                    userCfgdFlags: ''
#                    vlanmgrCfgFailedBmp: ''
#                    vlanmgrCfgFailedTs: '0'
#                    vlanmgrCfgState: '0'
#                    voicePortCos: none
#                    voicePortTrust: disable
#                    voiceVlanId: none
#                    voiceVlanType: none
#                children:
#                -   rmonIfHCOut:
#                        attributes:
#                            broadcastPckts: '0'
#                            broadcastPkts: '0'
#                            clearTs: never
#                            modTs: '2025-09-22T15:08:12.420+00:00'
#                            multicastPkts: '975159439654912'
#                            octets: '65142292964442112'
#                            rn: dbgIfHCOut
#                            ucastPkts: '0'
#                -   rmonEtherStats:
#                        attributes:
#                            broadcastPkts: '1768845133'
#                            cRCAlignErrors: '0'
#                            clearTs: never
#                            collisions: '0'
#                            dropEvents: '0'
#                            fragments: '0'
#                            giantPkts: '0'
#                            ifdowndrop: '0'
#                            ignored: '0'
#                            jabbers: '0'
#                            modTs: '2025-09-22T15:08:12.420+00:00'
#                            multicastPkts: '975159439654912'
#                            octets: '65142292964442112'
#                            overrun: '0'
#                            oversizePkts: '8390891445132722176'
#                            pkts: '975159439654912'
#                            pkts1024to1518Octets: '0'
#                            pkts128to255Octets: '12884901888'
#                            pkts1519to1548Octets: '0'
#                            pkts1519to2500Octets: '0'
#                            pkts256to511Octets: '31452045508608'
#                            pkts512to1023Octets: '0'
#                            pkts64Octets: '484734303993856'
#                            pkts65to127Octets: '0'
#                            rXNoErrors: '0'
#                            rn: dbgEtherStats
#                            rxOversizePkts: '8390891445132722176'
#                            rxPkts1024to1518Octets: '0'
#                            rxPkts128to255Octets: '0'
#                            rxPkts1519to1548Octets: '0'
#                            rxPkts1519to2500Octets: '0'
#                            rxPkts256to511Octets: '0'
#                            rxPkts512to1023Octets: '0'
#                            rxPkts64Octets: '0'
#                            rxPkts65to127Octets: '0'
#                            stompedCRCAlignErrors: '0'
#                            stormSupressedPkts: '0'
#                            tXNoErrors: '975159439654912'
#                            txOversizePkts: '0'
#                            txPkts1024to1518Octets: '0'
#                            txPkts128to255Octets: '12884901888'
#                            txPkts1519to1548Octets: '0'
#                            txPkts1519to2500Octets: '0'
#                            txPkts256to511Octets: '31452045508608'
#                            txPkts512to1023Octets: '0'
#                            txPkts64Octets: '484734303993856'
#                            txPkts65to127Octets: '0'
#                            underrun: '0'
#                            undersizePkts: '0'
#                            watchdog: '0'
#                -   rmonDot3Stats:
#                        attributes:
#                            alignmentErrors: '0'
#                            babble: '0'
#                            carrierSenseErrors: '0'
#                            clearTs: never
#                            controlInUnknownOpcodes: '0'
#                            deferredTransmissions: '0'
#                            excessiveCollisions: '0'
#                            fCSErrors: '0'
#                            frameTooLongs: '0'
#                            inPauseFrames: '0'
#                            inputdribble: '0'
#                            internalMacReceiveErrors: '0'
#                            internalMacTransmitErrors: '0'
#                            lateCollisions: '0'
#                            lostCarrierErrors: '0'
#                            modTs: '2025-09-22T15:08:12.420+00:00'
#                            multipleCollisionFrames: '0'
#                            noCarrierErrors: '0'
#                            outPauseFrames: '0'
#                            rn: dbgDot3Stats
#                            runts: '0'
#                            sQETTestErrors: '0'
#                            singleCollisionFrames: '0'
#                            symbolErrors: '0'
#                -   l1StormCtrlP:
#                        attributes:
#                ...
#         totalCount: '1'
"""

RETURN = """
class:
  description: The configuration as structured data prior to module invocation.
  returned: always
  type: dict
  sample: The configuration returned will always be in the same format of the parameters above.
mo:
  description: The configuration as structured data prior to module invocation.
  returned: always
  type: dict
  sample: The configuration returned will always be in the same format of the parameters above.
"""
