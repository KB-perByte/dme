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
	@echo "  changelog        - Generate changelog from fragments"
	@echo "  changelog-release - Create a new release with changelog"
	@echo "  changelog-deps   - Install changelog dependencies"

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

## Generate changelog from fragments
changelog:
	@if [ ! -d "changelogs/fragments" ] || [ -z "$$(ls -A changelogs/fragments 2>/dev/null)" ]; then \
		echo "No changelog fragments found. Nothing to generate."; \
	else \
		export PATH="$$HOME/.local/bin:$$PATH"; \
		python3 -m antsibull_changelog generate --reload-plugins; \
		echo "Changelog generated successfully."; \
	fi

## Create a new release with changelog (requires VERSION variable)
changelog-release:
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: VERSION variable is required. Usage: make changelog-release VERSION=1.2.3"; \
		exit 1; \
	fi
	@export PATH="$$HOME/.local/bin:$$PATH"; \
	python3 -m antsibull_changelog release --version $(VERSION)
	@echo "Release $(VERSION) created successfully."
	@echo "Don't forget to update galaxy.yml version and commit the changes."

## Install changelog dependencies
changelog-deps:
	pip install antsibull-changelog ansible-core

.PHONY: help check_black check_flake8 check_isort fix_black fix_isort lint_all collection-docs collection-lint test test-unit test-integration test-coverage test-deps changelog changelog-release changelog-deps