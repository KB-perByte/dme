.. _cisco.dme_nxos.nxos_dme_httpapi:


***********************
cisco.dme_nxos.nxos_dme
***********************

**Use NX-OS DME API to run commands on Cisco NX-OS devices**


Version added: 1.0.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- This httpapi plugin provides DME API capabilities for Cisco NX-OS devices
- Supports authentication, session management, and RESTful operations
- Maintains compatibility with cisco.nxos collection structure




Parameters
----------

.. raw:: html

    <table  border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="1">Parameter</th>
            <th>Choices/<font color="blue">Defaults</font></th>
                <th>Configuration</th>
            <th width="100%">Comments</th>
        </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>become</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">boolean</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">"no"</div>
                </td>
                    <td>
                                <div>var: ansible_become</div>
                    </td>
                <td>
                        <div>Enable privilege escalation</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>become_method</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">-</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">"enable"</div>
                </td>
                    <td>
                                <div>var: ansible_become_method</div>
                    </td>
                <td>
                        <div>Privilege escalation method</div>
                </td>
            </tr>
    </table>
    <br/>








Status
------


Authors
~~~~~~~

- Ansible Networking Team


.. hint::
    Configuration entries for each entry type have a low to high priority order. For example, a variable that is lower in the list will override a variable that is higher up.
