=======================
Cisco.Dme Release Notes
=======================

.. contents:: Topics

v1.0.0
======

Release Summary
---------------

Initial release of the Cisco DME collection providing modules and plugins
for managing Cisco appliances supporting Data Management Engine (DME).

Major Changes
-------------

- Added dme HttpApi connection plugin for Cisco DME REST API
- Complete module utilities for DME API interaction
- Comprehensive action plugins for all modules
- Full documentation and examples for all modules
- Initial release with dme_command, dme_config, and dme_validate modules

Minor Changes
-------------

- Added comprehensive error handling and authentication
- Added comprehensive unit test suite for all modules and plugins
- Added support for JSON-RPC validation requests
- Added test fixtures and mock data for consistent testing
- Added testing documentation and troubleshooting guides
- Created automated test execution scripts and Makefile targets
- Created integration test framework with mock DME endpoints
- Implemented CSRF token generation for secure API calls
- Implemented pytest configuration with coverage reporting
- Included SSL verification configuration options

New Plugins
-----------

Httpapi
~~~~~~~

- cisco.dme.dme - HttpApi Plugin for Cisco Nxos Data Management Engine (DME).

New Modules
-----------

- cisco.dme.dme_command - Fetch arbitrary DME model based on node class.
- cisco.dme.dme_config - A configuration module for configuration using DME model.
- cisco.dme.dme_validate - Validate and convert configuration on DME managed devices.
