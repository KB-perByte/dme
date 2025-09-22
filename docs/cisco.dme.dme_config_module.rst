.. _cisco.dme.dme_config_module:


********************
cisco.dme.dme_config
********************

**A configuration module for configuration using DME model.**


Version added: 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- A configuration module for configuration using DME model.




Parameters
----------

.. raw:: html

    <table  border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="1">Parameter</th>
            <th>Choices/<font color="blue">Defaults</font></th>
            <th width="100%">Comments</th>
        </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>config</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">dictionary</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>A raw DME model, validate it first using dme_validate module and then pass it here for configuration.</div>
                </td>
            </tr>
    </table>
    <br/>




Examples
--------

.. code-block:: yaml

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



Return Values
-------------
Common return values are documented `here <https://docs.ansible.com/ansible/latest/reference_appendices/common_return_values.html#common-return-values>`_, the following are the fields unique to this module:

.. raw:: html

    <table border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="1">Key</th>
            <th>Returned</th>
            <th width="100%">Description</th>
        </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>after</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">list</span>
                    </div>
                </td>
                <td>when changed</td>
                <td>
                            <div>The configuration as structured data after module completion.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">The configuration returned will always be in the same format of the parameters above.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>before</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">list</span>
                    </div>
                </td>
                <td>always</td>
                <td>
                            <div>The configuration as structured data prior to module invocation.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">The configuration returned will always be in the same format of the parameters above.</div>
                </td>
            </tr>
    </table>
    <br/><br/>


Status
------


Authors
~~~~~~~

- Sagar Paul (@KB-perByte)
