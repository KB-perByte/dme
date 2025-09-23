# Quick Testing Guide

## Quick Start

### Run Unit Tests
```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=plugins --cov-report=html
```

### Run Integration Tests
```bash
# Update inventory with your device details
cp tests/integration/inventory.ini.example tests/integration/inventory.ini
# Edit inventory.ini with your device IP and credentials

# Run integration tests
ansible-test integration --inventory tests/integration/inventory.ini
```

### Use Test Runner Script
```bash
# Run unit tests only (default)
./tests/run_tests.sh

# Run all tests with coverage
./tests/run_tests.sh --all --coverage

# Run with verbose output
./tests/run_tests.sh --verbose

# Show help
./tests/run_tests.sh --help
```

## Test Categories

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test complete workflows against real or mock devices
- **Mock Tests**: Test with simulated device responses

## Key Test Files

- `tests/unit/conftest.py` - Shared test fixtures
- `tests/unit/fixtures/dme_responses.py` - Mock API responses
- `tests/integration/inventory.ini` - Test device inventory
- `tests/requirements.txt` - Test dependencies

## Common Issues

1. **Import Errors**: Run `ansible-galaxy collection install . --force`
2. **Connection Issues**: Check inventory.ini and device connectivity
3. **Missing Dependencies**: Run `pip install -r tests/requirements.txt`

For detailed information, see [tests/README.md](README.md).
