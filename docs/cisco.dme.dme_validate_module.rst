.. _cisco.dme.dme_validate_module:


**********************
cisco.dme.dme_validate
**********************

**Validate and convert configuration on DME managed devices.**


Version added: 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- This module validate and converts configuration on DME managed devices.




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
                    <b>lines</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The ordered set of commands that should be configured in the section. The commands must be the exact same commands as found in the device running-config to ensure idempotency and correct diff. Be sure to note the configuration command syntax as some commands are automatically modified by the device config parser.</div>
                        <div style="font-size: small; color: darkgreen"><br/>aliases: commands</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>parents</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>The ordered set of parents that uniquely identify the section or hierarchy the commands should be checked against.  If the parents argument is omitted, the commands are checked against the set of top level or global commands.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>src</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Specifies the source path to the file that contains the configuration or configuration template to load. The path to the source file can either be the full path on the Ansible control host or a relative path from the playbook or role root directory. This argument is mutually exclusive with <em>lines</em>, <em>parents</em>. The configuration lines in the source file should be similar to how it will appear if present in the running-configuration of the device including the indentation to ensure idempotency and correct diff.</div>
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
                    <b>changed</b>
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
                    <b>errors</b>
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
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>model</b>
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
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>valid</b>
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
