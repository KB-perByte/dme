# Cisco DME Ansible Collection

An Ansible Collection to manage Cisco appliances supporting Data Management Engine (DME).

## Description

This collection provides modules and plugins to interact with Cisco devices using the Data Management Engine (DME) REST API. The DME is available on various Cisco platforms including NX-OS switches and provides a programmatic interface for configuration management and monitoring.

## Requirements

- Ansible >= 2.16.0
- Python >= 3.6
- `ansible.netcommon` collection
- `ansible.utils` collection

## Installation

### From Ansible Galaxy

```bash
ansible-galaxy collection install cisco.dme
```

### From Source

```bash
git clone https://github.com/KB-perByte/dme.git
cd dme
ansible-galaxy collection build
ansible-galaxy collection install cisco-dme-*.tar.gz
```

## Modules

### dme_command

Fetch arbitrary DME model data based on node class or distinguished name.

**Parameters:**
- `read_class`: Get objects of a specific DME class
- `read_dn`: Get specific managed object details by distinguished name

### dme_validate

Validate and convert configuration on DME managed devices.

**Parameters:**
- `lines`: Configuration commands to validate
- `parents`: Parent configuration context
- `src`: Path to configuration file

### dme_config

Apply configuration using DME model data.

**Parameters:**
- `config`: DME model configuration to apply

## Connection Plugin

### dme

HttpApi plugin for Cisco DME REST API connections.

## Usage Examples

### Inventory Configuration

```ini
[dme_switches]
switch1 ansible_host=192.168.1.100

[dme_switches:vars]
ansible_network_os=cisco.dme.dme
ansible_user=admin
ansible_password=password
ansible_connection=ansible.netcommon.httpapi
ansible_httpapi_port=443
ansible_httpapi_use_ssl=yes
ansible_httpapi_validate_certs=no
```

### Basic Usage

```yaml
---
- name: DME Configuration Example
  hosts: dme_switches
  gather_facts: false
  tasks:
    - name: Get interface information
      cisco.dme.dme_command:
        read_dn:
          entry: "sys/intf/phys-[eth1/1]"
          rsp_prop_include: "config-only"

    - name: Validate configuration
      cisco.dme.dme_validate:
        lines:
          - description "Management Interface"
          - no shutdown
        parents: interface Ethernet1/1
      register: validation_result

    - name: Apply configuration
      cisco.dme.dme_config:
        config: "{{ validation_result.model }}"
      when: validation_result.valid
```

### Advanced Usage

```yaml
---
- name: Advanced DME Operations
  hosts: dme_switches
  gather_facts: false
  tasks:
    - name: Get all IPv4 ACLs
      cisco.dme.dme_command:
        read_class:
          entry: "ipv4aclACL"
          rsp_prop_include: "config-only"

    - name: Get system information with subtree
      cisco.dme.dme_command:
        read_dn:
          entry: "sys"
          rsp_subtree: "full"
          query_target: "subtree"
          target_subtree_class: "topSystem"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
- GitHub Issues: https://github.com/KB-perByte/dme/issues
- Repository: https://github.com/KB-perByte/dme

## License

GNU General Public License v3.0+

See [LICENSE](LICENSE) for full license text.

## Author

- Sagar Paul (@KB-perByte)
