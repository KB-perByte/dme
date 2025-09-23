# Default files to check for syntax
CHECK_SYNTAX_FILES ?= plugins/ tests/

# Help target
help:
	@echo "Available targets:"
	@echo "  check_black      - Run black syntax check"
	@echo "  check_flake8     - Run flake8 syntax check"
	@echo "  check_isort      - Run isort syntax check"
	@echo "  fix_black        - Run black to fix formatting"
	@echo "  fix_isort        - Run isort to fix import sorting"
	@echo "  lint_all         - Run all linting checks"
	@echo "  collection-docs  - Generate collection documentation"
	@echo "  collection-lint  - Run ansible-lint on the collection"
	@echo "  test             - Run all tests"
	@echo "  test-unit        - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-coverage    - Run tests with coverage report"

## Run black syntax check
check_black:
	tox -e black -- --check $(CHECK_SYNTAX_FILES)

## Run flake8 syntax check
check_flake8:
	tox -e flake8 -- $(CHECK_SYNTAX_FILES)

## Run isort syntax check
check_isort:
	tox -e isort -- --check $(CHECK_SYNTAX_FILES)

## Run black to fix formatting
fix_black:
	tox -e black -- $(CHECK_SYNTAX_FILES)

## Run isort to fix import sorting
fix_isort:
	tox -e isort -- $(CHECK_SYNTAX_FILES)

## Run all linting checks
lint_all: check_black check_flake8 check_isort

## Generate collection documentation
collection-docs:
	ansible-doc --list cisco.dme

## Run ansible-lint on the collection
collection-lint:
	ansible-lint

## Run all tests
test:
	./tests/run_tests.sh --all

## Run unit tests only
test-unit:
	./tests/run_tests.sh --unit-only

## Run integration tests only
test-integration:
	./tests/run_tests.sh --integration-only

## Run tests with coverage report
test-coverage:
	./tests/run_tests.sh --unit-only --coverage

## Install test dependencies
test-deps:
	pip install -r tests/requirements.txt

.PHONY: help check_black check_flake8 check_isort fix_black fix_isort lint_all collection-docs collection-lint test test-unit test-integration test-coverage test-deps