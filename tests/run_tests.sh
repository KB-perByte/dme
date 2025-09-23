#!/bin/bash
# Test runner script for Cisco DME Collection
# Copyright 2025 Sagar Paul (@KB-perByte)
# GNU General Public License v3.0+

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COLLECTION_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}Cisco DME Collection Test Runner${NC}"
echo "=================================="

# Check if we're in the right directory
if [[ ! -f "$COLLECTION_ROOT/galaxy.yml" ]]; then
    echo -e "${RED}Error: Not in collection root directory${NC}"
    exit 1
fi

# Function to print section headers
print_section() {
    echo
    echo -e "${YELLOW}$1${NC}"
    echo "$(printf '%.0s-' $(seq 1 ${#1}))"
}

# Function to run command with error handling
run_command() {
    local cmd="$1"
    local description="$2"

    echo "Running: $description"
    if eval "$cmd"; then
        echo -e "${GREEN}✓ $description completed successfully${NC}"
        return 0
    else
        echo -e "${RED}✗ $description failed${NC}"
        return 1
    fi
}

# Parse command line arguments
UNIT_TESTS=true
INTEGRATION_TESTS=false
COVERAGE=false
VERBOSE=false
LINT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --unit-only)
            UNIT_TESTS=true
            INTEGRATION_TESTS=false
            shift
            ;;
        --integration-only)
            UNIT_TESTS=false
            INTEGRATION_TESTS=true
            shift
            ;;
        --all)
            UNIT_TESTS=true
            INTEGRATION_TESTS=true
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --lint)
            LINT=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --unit-only       Run only unit tests (default)"
            echo "  --integration-only Run only integration tests"
            echo "  --all             Run both unit and integration tests"
            echo "  --coverage        Generate coverage report"
            echo "  --verbose, -v     Verbose output"
            echo "  --lint            Run linting checks"
            echo "  --help, -h        Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Change to collection root
cd "$COLLECTION_ROOT"

print_section "Environment Setup"

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python version: $python_version"

# Verify test structure
echo "Verifying test structure..."
if python3 tests/verify_test_structure.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Test structure verified${NC}"
else
    echo -e "${YELLOW}⚠ Test structure verification failed, but continuing...${NC}"
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}pytest not found, installing test requirements...${NC}"
    run_command "pip install -r tests/requirements.txt" "Installing test requirements"
fi

# Install collection dependencies
if [[ -f "requirements.yml" ]]; then
    run_command "ansible-galaxy collection install -r requirements.yml" "Installing collection dependencies"
fi

# Install the collection itself for testing
run_command "ansible-galaxy collection install . --force" "Installing collection for testing"

# Linting (if requested)
if [[ "$LINT" == "true" ]]; then
    print_section "Linting"

    if command -v flake8 &> /dev/null; then
        run_command "flake8 plugins/ --max-line-length=88 --extend-ignore=E203,W503" "Running flake8"
    else
        echo -e "${YELLOW}flake8 not found, skipping linting${NC}"
    fi

    if command -v pylint &> /dev/null; then
        run_command "pylint plugins/" "Running pylint"
    else
        echo -e "${YELLOW}pylint not found, skipping pylint${NC}"
    fi
fi

# Unit Tests
if [[ "$UNIT_TESTS" == "true" ]]; then
    print_section "Unit Tests"

    pytest_args="tests/unit/"

    if [[ "$VERBOSE" == "true" ]]; then
        pytest_args="$pytest_args -v"
    fi

    if [[ "$COVERAGE" == "true" ]]; then
        pytest_args="$pytest_args --cov=plugins --cov-report=term-missing --cov-report=html"
    fi

    run_command "pytest $pytest_args" "Running unit tests"

    if [[ "$COVERAGE" == "true" ]]; then
        echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
    fi
fi

# Integration Tests
if [[ "$INTEGRATION_TESTS" == "true" ]]; then
    print_section "Integration Tests"

    # Check if inventory exists
    if [[ ! -f "tests/integration/inventory.ini" ]]; then
        echo -e "${YELLOW}Integration inventory not found, creating default...${NC}"
        cp tests/integration/inventory.ini.example tests/integration/inventory.ini 2>/dev/null || true
    fi

    # Check if we can connect to test devices
    echo "Checking connectivity to test devices..."
    if ansible -i tests/integration/inventory.ini dme_devices -m ping &>/dev/null; then
        echo -e "${GREEN}✓ Test devices are reachable${NC}"

        # Run integration tests
        integration_args=""
        if [[ "$VERBOSE" == "true" ]]; then
            integration_args="-v"
        fi

        run_command "ansible-test integration --inventory tests/integration/inventory.ini $integration_args" "Running integration tests"
    else
        echo -e "${YELLOW}⚠ Test devices not reachable, skipping integration tests${NC}"
        echo "To run integration tests:"
        echo "1. Update tests/integration/inventory.ini with your device details"
        echo "2. Ensure network connectivity to the devices"
        echo "3. Verify credentials are correct"
    fi
fi

print_section "Test Summary"

echo -e "${GREEN}✓ Test execution completed${NC}"

if [[ "$UNIT_TESTS" == "true" ]]; then
    echo "• Unit tests: Executed"
fi

if [[ "$INTEGRATION_TESTS" == "true" ]]; then
    echo "• Integration tests: Executed"
fi

if [[ "$COVERAGE" == "true" ]]; then
    echo "• Coverage report: Generated in htmlcov/"
fi

echo
echo "For more testing options, see tests/README.md"
