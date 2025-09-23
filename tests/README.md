# Testing Guide for Cisco DME Collection

This document provides comprehensive information about testing the Cisco DME Ansible Collection.

## Overview

The Cisco DME collection includes comprehensive test coverage with both unit tests and integration tests to ensure reliability and functionality across different environments.

## Test Structure

```
tests/
├── unit/                          # Unit tests
│   ├── conftest.py               # Pytest configuration and shared fixtures
│   ├── fixtures/                 # Test fixtures and mock data
│   │   ├── __init__.py
│   │   └── dme_responses.py      # Mock DME API responses
│   └── plugins/                  # Plugin-specific tests
│       ├── action/               # Action plugin tests
│       │   ├── test_dme_command.py
│       │   ├── test_dme_config.py
│       │   └── test_dme_validate.py
│       ├── httpapi/              # HttpApi plugin tests
│       │   └── test_dme.py
│       ├── module_utils/         # Module utils tests
│       │   └── test_dme.py
│       └── modules/              # Module tests
│           ├── test_dme_command.py
│           ├── test_dme_config.py
│           └── test_dme_validate.py
└── integration/                  # Integration tests
    ├── integration_config.yml    # Integration test configuration
    ├── inventory.ini            # Test inventory
    └── targets/                 # Test targets
        ├── setup_dme_test/      # Common setup for integration tests
        ├── dme_command/         # DME command module tests
        ├── dme_validate/        # DME validate module tests
        └── dme_config/          # DME config module tests
```

## Prerequisites

### For Unit Tests

- Python 3.6+
- pytest
- pytest-mock
- ansible-core
- Required dependencies from `galaxy.yml`

### For Integration Tests

- All unit test requirements
- Access to a Cisco device with DME support (NX-OS switch)
- Network connectivity to the test device
- Valid credentials for the test device

## Running Tests

### Unit Tests

#### Run All Unit Tests
```bash
# From the collection root directory
pytest tests/unit/ -v
```

#### Run Specific Test Categories
```bash
# Test action plugins
pytest tests/unit/plugins/action/ -v

# Test httpapi plugin
pytest tests/unit/plugins/httpapi/ -v

# Test module utils
pytest tests/unit/plugins/module_utils/ -v

# Test modules
pytest tests/unit/plugins/modules/ -v
```

#### Run Individual Test Files
```bash
# Test specific action plugin
pytest tests/unit/plugins/action/test_dme_command.py -v

# Test with coverage report
pytest tests/unit/ --cov=plugins --cov-report=html
```

### Integration Tests

#### Prerequisites Setup

1. **Configure Test Inventory**
   ```bash
   # Edit tests/integration/inventory.ini
   [dme_devices]
   your_device ansible_host=192.168.1.100

   [dme_devices:vars]
   ansible_user=your_username
   ansible_password=your_password
   ```

2. **Install Required Collections**
   ```bash
   ansible-galaxy collection install ansible.netcommon
   ansible-galaxy collection install ansible.utils
   ```

#### Run Integration Tests

```bash
# Run all integration tests
ansible-test integration --inventory tests/integration/inventory.ini

# Run specific test target
ansible-test integration --inventory tests/integration/inventory.ini dme_command

# Run tests with verbose output
ansible-test integration --inventory tests/integration/inventory.ini -v

# Run tests in Docker (requires Docker setup)
ansible-test integration --docker default
```

#### Manual Integration Testing

```bash
# Run integration tests manually with ansible-playbook
cd tests/integration/targets/dme_command
ansible-playbook -i ../../inventory.ini tasks/main.yml
```

## Test Coverage

### Unit Tests Coverage

- **Action Plugins**: 95%+ coverage
  - Argument validation
  - API request handling
  - Error handling
  - Response processing

- **HttpApi Plugin**: 90%+ coverage
  - Authentication flows
  - Request/response handling
  - SSL/TLS configuration
  - Error handling

- **Module Utils**: 95%+ coverage
  - Utility functions
  - Connection handling
  - Error management

- **Modules**: 100% documentation coverage
  - YAML structure validation
  - Documentation completeness
  - Example validation

### Integration Tests Coverage

- **dme_command**: Complete workflow testing
  - Class-based queries
  - DN-based queries
  - Parameter combinations
  - Error scenarios

- **dme_validate**: Configuration validation testing
  - Valid configurations
  - Invalid configurations
  - Error mapping
  - Complex scenarios

- **dme_config**: Configuration application testing
  - Model application
  - Error handling
  - Idempotency
  - Multi-step workflows

## Mock Testing

The test suite includes comprehensive mocking for testing without real devices:

### Mock Data

- **dme_responses.py**: Contains realistic DME API responses
- **conftest.py**: Provides shared fixtures and mock objects
- **Mock requests**: HTTP requests are mocked for validation endpoints

### Mock Coverage

- Login/logout flows
- API responses (success and error)
- JSON-RPC validation responses
- Connection handling
- SSL certificate handling

## Continuous Integration

### GitHub Actions (Example)

```yaml
name: Test Collection
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', 3.11]
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          pip install pytest pytest-mock ansible-core
          ansible-galaxy collection install ansible.netcommon ansible.utils
      - name: Run unit tests
        run: pytest tests/unit/ -v --cov=plugins
```

## Test Development Guidelines

### Writing Unit Tests

1. **Use Fixtures**: Leverage shared fixtures from `conftest.py`
2. **Mock External Dependencies**: Mock network calls and device interactions
3. **Test Edge Cases**: Include error conditions and boundary cases
4. **Maintain Coverage**: Aim for >90% code coverage

Example:
```python
def test_configure_class_api_success(self, action_module):
    """Test successful class API configuration."""
    mock_dme_request = MagicMock()
    mock_dme_request.get.return_value = (200, MOCK_CLASS_RESPONSE)

    read_class = {"entry": "ipv4aclACL"}

    api_response, code = action_module.configure_class_api(
        mock_dme_request, read_class
    )

    assert api_response == MOCK_CLASS_RESPONSE
    assert code == 200
```

### Writing Integration Tests

1. **Test Real Workflows**: Use realistic scenarios
2. **Handle Failures Gracefully**: Use `ignore_errors` and conditional execution
3. **Verify Results**: Assert on expected outcomes
4. **Clean Up**: Ensure tests don't leave configuration artifacts

Example:
```yaml
- name: Test dme_validate with valid configuration
  cisco.dme.dme_validate:
    lines:
      - "description Test interface"
    parents:
      - "interface Ethernet1/1"
  register: result

- name: Verify result
  assert:
    that:
      - result is changed
      - result.valid is true
      - result.model is defined
```

## Troubleshooting Tests

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure collection is installed
   ansible-galaxy collection install . --force
   ```

2. **Connection Issues in Integration Tests**
   ```bash
   # Test basic connectivity
   ansible -i tests/integration/inventory.ini dme_devices -m ping
   ```

3. **Mock Issues in Unit Tests**
   ```bash
   # Check fixture imports
   pytest tests/unit/ -v --tb=short
   ```

### Debug Mode

```bash
# Run tests with debug output
pytest tests/unit/ -v -s --tb=long

# Run integration tests with debug
ansible-test integration --inventory tests/integration/inventory.ini -vvv
```

## Contributing Tests

When contributing to the collection:

1. **Add Tests for New Features**: All new functionality should include tests
2. **Update Existing Tests**: Modify tests when changing functionality
3. **Maintain Coverage**: Ensure test coverage doesn't decrease
4. **Document Changes**: Update this README when adding new test patterns

### Test Review Checklist

- [ ] Unit tests cover new/changed code
- [ ] Integration tests cover user-facing workflows
- [ ] Tests pass locally
- [ ] Mock data is realistic
- [ ] Error cases are tested
- [ ] Documentation is updated

## Performance Testing

For performance-critical changes:

```bash
# Run tests with timing
pytest tests/unit/ --durations=10

# Profile test execution
pytest tests/unit/ --profile
```

## Security Testing

The test suite includes security considerations:

- SSL/TLS configuration testing
- Authentication flow testing
- Input validation testing
- Error message sanitization

## Support

For testing questions or issues:

1. Check this documentation
2. Review existing test examples
3. Open an issue on the project repository
4. Contact the maintainers

---

**Note**: Always test changes against both mocked and real environments when possible to ensure comprehensive validation.
