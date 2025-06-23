#!/usr/bin/python
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import absolute_import, division, print_function


__metaclass__ = type


DOCUMENTATION = """
module: nxos_config
extends_documentation_fragment:
- cisco.dme_nxos.nxos
author: Sagar Paul (@KB-perByte)
short_description: Manage Cisco NXOS configuration sections
description:
- Cisco NXOS configurations use a simple block indent file syntax for segmenting configuration
  into sections.  This module provides an implementation for working with NXOS configuration
  sections in a deterministic way.  This module works with either CLI or NXAPI transports.
version_added: 1.0.0
options:
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
  match:
    description:
    - Instructs the module on the way to perform the matching of the set of commands
      against the current device config.  If match is set to I(line), commands are
      matched line by line.  If match is set to I(strict), command lines are matched
      with respect to position.  If match is set to I(exact), command lines must be
      an equal match.  Finally, if match is set to I(none), the module will not attempt
      to compare the source configuration with the running configuration on the remote
      device.
    default: line
    choices:
    - line
    - strict
    - exact
    - none
    type: str
  replace:
    description:
    - Instructs the module on the way to perform the configuration on the device.  If
      the replace argument is set to I(line) then the modified lines are pushed to
      the device in configuration mode.  If the replace argument is set to I(block)
      then the entire command block is pushed to the device in configuration mode
      if any line is not correct. replace I(config) will only work for NX-OS versions
      that support `config replace`.
    default: line
    choices:
    - line
    - block
    - config
    type: str
  backup:
    description:
    - This argument will cause the module to create a full backup of the current C(running-config)
      from the remote device before any changes are made. If the C(backup_options)
      value is not given, the backup file is written to the C(backup) folder in the
      playbook root directory or role root directory, if playbook is part of an ansible
      role. If the directory does not exist, it is created.
    type: bool
    default: false
  running_config:
    description:
    - The module, by default, will connect to the remote device and retrieve the current
      running-config to use as a base for comparing against the contents of source.  There
      are times when it is not desirable to have the task get the current running-config
      for every task in a playbook.  The I(running_config) argument allows the implementer
      to pass in the configuration to use as the base config for comparison.
      The configuration lines for this option should be similar to how it will appear if present
      in the running-configuration of the device including the indentation to ensure idempotency
      and correct diff.
    aliases:
    - config
    type: str
  defaults:
    description:
    - The I(defaults) argument will influence how the running-config is collected
      from the device.  When the value is set to true, the command used to collect
      the running-config is append with the all keyword.  When the value is set to
      false, the command is issued without the all keyword
    type: bool
    default: false
  save_when:
    description:
    - When changes are made to the device running-configuration, the changes are not
      copied to non-volatile storage by default.  Using this argument will change
      that before.  If the argument is set to I(always), then the running-config will
      always be copied to the startup-config and the I(modified) flag will always
      be set to True.  If the argument is set to I(modified), then the running-config
      will only be copied to the startup-config if it has changed since the last save
      to startup-config.  If the argument is set to I(never), the running-config will
      never be copied to the startup-config.  If the argument is set to I(changed),
      then the running-config will only be copied to the startup-config if the task
      has made a change. I(changed) was added in Ansible 2.6.
    default: never
    choices:
    - always
    - never
    - modified
    - changed
    type: str
  diff_against:
    description:
    - When using the C(ansible-playbook --diff) command line argument the module can
      generate diffs against different sources.
    - When this option is configure as I(startup), the module will return the diff
      of the running-config against the startup-config.
    - When this option is configured as I(intended), the module will return the diff
      of the running-config against the configuration provided in the C(intended_config)
      argument.
    - When this option is configured as I(running), the module will return the before
      and after diff of the running-config with respect to any changes made to the
      device configuration.
    choices:
    - startup
    - intended
    - running
    type: str
  diff_ignore_lines:
    description:
    - Use this argument to specify one or more lines that should be ignored during
      the diff.  This is used for lines in the configuration that are automatically
      updated by the system.  This argument takes a list of regular expressions or
      exact line matches.
    type: list
    elements: str
  intended_config:
    description:
    - The C(intended_config) provides the master configuration that the node should
      conform to and is used to check the final running-config against. This argument
      will not modify any settings on the remote device and is strictly used to check
      the compliance of the current device's configuration against.  When specifying
      this argument, the task should also modify the C(diff_against) value and set
      it to I(intended). The configuration lines for this value should be similar to how it
      will appear if present in the running-configuration of the device including the indentation
      to ensure correct diff.
    type: str
  backup_options:
    description:
    - This is a dict object containing configurable options related to backup file
      path. The value of this option is read only when C(backup) is set to I(True),
      if C(backup) is set to I(false) this option will be silently ignored.
    suboptions:
      filename:
        description:
        - The filename to be used to store the backup configuration. If the filename
          is not given it will be generated based on the hostname, current time and
          date in format defined by <hostname>_config.<current-date>@<current-time>
        type: str
      dir_path:
        description:
        - This option provides the path ending with directory name in which the backup
          configuration file will be stored. If the directory does not exist it will
          be created and the filename is either the value of C(filename) or default
          filename as described in C(filename) options description. If the path value
          is not given in that case a I(backup) directory will be created in the current
          working directory and backup configuration will be copied in C(filename)
          within I(backup) directory.
        type: path
    type: dict
notes:
- Unsupported for Cisco MDS
- Abbreviated commands are NOT idempotent, see
  U(https://docs.ansible.com/ansible/latest/network/user_guide/faq.html#why-do-the-config-modules-always-return-changed-true-with-abbreviated-commands).
- To ensure idempotency and correct diff the configuration lines in the relevant module options should be similar to how they
  appear if present in the running configuration on device including the indentation.
"""

EXAMPLES = """
- name: configure top level configuration and save it
  cisco.dme_nxos.nxos_config:
    lines: hostname {{ inventory_hostname }}
    save_when: modified

- name: diff the running-config against a provided config
  cisco.dme_nxos.nxos_config:
    diff_against: intended
    intended_config: "{{ lookup('file', 'master.cfg') }}"

- cisco.dme_nxos.nxos_config:
    lines:
      - 10 permit ip 192.0.2.1/32 any log
      - 20 permit ip 192.0.2.2/32 any log
      - 30 permit ip 192.0.2.3/32 any log
      - 40 permit ip 192.0.2.4/32 any log
      - 50 permit ip 192.0.2.5/32 any log
    parents: ip access-list test
    before: no ip access-list test
    match: exact

- cisco.dme_nxos.nxos_config:
    lines:
      - 10 permit ip 192.0.2.1/32 any log
      - 20 permit ip 192.0.2.2/32 any log
      - 30 permit ip 192.0.2.3/32 any log
      - 40 permit ip 192.0.2.4/32 any log
    parents: ip access-list test
    before: no ip access-list test
    replace: block

- name: replace config with flat file
  cisco.dme_nxos.nxos_config:
    replace_src: config.txt
    replace: config

- name: for idempotency, use full-form commands
  cisco.dme_nxos.nxos_config:
    lines:
      # - shut
      - shutdown
    # parents: int eth1/1
    parents: interface Ethernet1/1

- name: configurable backup path
  cisco.dme_nxos.nxos_config:
    backup: true
    backup_options:
      filename: backup.cfg
      dir_path: /home/user
"""

RETURN = """
commands:
  description: The set of commands that will be pushed to the remote device
  returned: always
  type: list
  sample: ['hostname foo', 'vlan 1', 'name default']
updates:
  description: The set of commands that will be pushed to the remote device
  returned: always
  type: list
  sample: ['hostname foo', 'vlan 1', 'name default']
backup_path:
  description: The full path to the backup file
  returned: when backup is yes
  type: str
  sample: /playbooks/ansible/backup/nxos_config.2016-07-16@22:28:34
filename:
  description: The name of the backup file
  returned: when backup is yes and filename is not specified in backup options
  type: str
  sample: nxos_config.2016-07-16@22:28:34
shortname:
  description: The full path to the backup file excluding the timestamp
  returned: when backup is yes and filename is not specified in backup options
  type: str
  sample: /playbooks/ansible/backup/nxos_config
date:
  description: The date extracted from the backup file name
  returned: when backup is yes
  type: str
  sample: "2016-07-16"
time:
  description: The time extracted from the backup file name
  returned: when backup is yes
  type: str
  sample: "22:28:34"
"""
from ansible.module_utils._text import to_text
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.cisco.dme_nxos.plugins.module_utils.network.dme_nxos.dme_nxos import (
    get_connection,
)
import json
import base64
import requests


def send_dme_request(payloads, host, username, password, port, csrf_token="defaultcsrf123"):
    secure = False

    base_url = f"{'https' if secure else 'http'}://{host}:{port}"
    ins_endpoint = f"{base_url}/ins"

    # Setup session
    session = requests.Session()
    session.verify = False

    # Create authorization header
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    auth_header = f"Basic {encoded_credentials}"
    # Convert payloads to JSON string
    json_payload = json.dumps(payloads, separators=(",", ":"))
    content_length = len(json_payload.encode("utf-8"))

    # Create headers
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Authorization": auth_header,
        "Connection": "keep-alive",
        "Content-Length": str(content_length),
        "Content-Type": "application/json-rpc",
        "Host": f"{host}:{port}",
        "Origin": f"{'https' if secure else 'http'}://{host}:{port}",
        "Referer": f"{'https' if secure else 'http'}://{host}:{port}/",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "anticsrf": csrf_token,
    }

    try:

        response = session.post(ins_endpoint, data=json_payload, headers=headers, timeout=30)
        # response.raise_for_status()

        error_map = {}
        json_response = response.json()
        for data_idx in range(len(json_response)):
            if json_response[data_idx].get("error"):
                error_map[data_idx] = ""

        return json.loads(json_response[-1]["result"]["msg"]), error_map

    except requests.exceptions.RequestException as e:
        print(f"DME request error: {e}")
        return {"error": str(e)}
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return {"error": f"JSON decode error: {e}", "response_text": response.text}


def parse_config_block(config_text):
    lines = []
    for line in config_text.strip().split("\n"):
        line = line.rstrip()
        if line and not line.strip().startswith("!"):  # Skip empty lines and comments
            lines.append(line)
    return lines


def config_to_jsonrpc_payload(config_lines, start_id=1):
    payloads = []

    for i, cmd in enumerate(config_lines):
        payload = {
            "jsonrpc": "2.0",
            "method": "cli_rest",
            "option": "default",
            "params": {"cmd": cmd, "version": 1},
            "id": start_id + i,
        }
        payloads.append(payload)

    return payloads


def process_config_to_dme(config_text):
    config_lines = parse_config_block(config_text)
    payloads = config_to_jsonrpc_payload(config_lines)
    payload_json = json.dumps(payloads, separators=(",", ":"))
    response = send_dme_request(payloads, "xxxxxxxxxx", "cisco", "cisco", "xxxxx")

    return response


def main():
    """main entry point for module execution"""
    backup_spec = dict(filename=dict(), dir_path=dict(type="path"))
    argument_spec = dict(
        src=dict(type="path"),
        replace_src=dict(),
        lines=dict(aliases=["commands"], type="list", elements="str"),
        parents=dict(type="list", elements="str"),
        before=dict(type="list", elements="str"),
        after=dict(type="list", elements="str"),
    )

    mutually_exclusive = [("lines", "src"), ("parents", "src")]

    required_if = [
        ("match", "strict", ["lines", "src"], True),
        ("match", "exact", ["lines", "src"], True),
        ("replace", "block", ["lines", "src"], True),
        ("replace", "config", ["replace_src"]),
        ("diff_against", "intended", ["intended_config"]),
    ]

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=mutually_exclusive,
        required_if=required_if,
        supports_check_mode=True,
    )
    # import debugpy

    # debugpy.listen(5003)
    # debugpy.wait_for_client()
    warnings = list()

    result = {"changed": False, "warnings": warnings}
    # connection = get_connection(module)

    if any((module.params.get("src"), module.params.get("lines"))):
        config_raw = ""
        if module.params.get("lines"):
            for raw_config in ["before", "parents", "lines", "after"]:
                if module.params.get(raw_config, {}):
                    if isinstance(module.params.get(raw_config), str):
                        config_raw += module.params.get(raw_config) + "\n"
                    else:
                        for conf in module.params.get(raw_config, {}):
                            config_raw += conf + "\n"
    endpointResponse, errorMap = process_config_to_dme(config_raw)
    if errorMap:
        # if "Bad Request" in endpointResponse["error"]:
        config_list = config_raw.split("\n")
        new_err_map = {}
        for idx, cmd in errorMap.items():
            new_err_map[idx] = config_list[idx]

        result["isValid"] = False
        result["dme_response"] = endpointResponse
        result["changed"] = True
        result["failed_line_and_command"] = new_err_map
    else:
        result["dme_response"] = endpointResponse
        result["isValid"] = True

    # if module.params["backup"] or (module._diff and module.params["diff_against"] == "running"):

    if result.get("changed") and any((module.params["src"], module.params["lines"])):
        msg = (
            "To ensure idempotency and correct diff the input configuration lines should be"
            " similar to how they appear if present in"
            " the running configuration on device"
        )
        if module.params["src"]:
            msg += " including the indentation"
        if "warnings" in result:
            result["warnings"].append(msg)
        else:
            result["warnings"] = msg

    module.exit_json(**result)


if __name__ == "__main__":
    main()
