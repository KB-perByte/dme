# Cisco\.Dme Release Notes

**Topics**

- <a href="#v1-0-0">v1\.0\.0</a>
    - <a href="#release-summary">Release Summary</a>
    - <a href="#major-changes">Major Changes</a>
    - <a href="#minor-changes">Minor Changes</a>
    - <a href="#new-plugins">New Plugins</a>
        - <a href="#httpapi">Httpapi</a>
    - <a href="#new-modules">New Modules</a>

<a id="v1-0-0"></a>
## v1\.0\.0

<a id="release-summary"></a>
### Release Summary

Initial release of the Cisco DME collection providing modules and plugins
for managing Cisco appliances supporting Data Management Engine \(DME\)\.

<a id="major-changes"></a>
### Major Changes

* Added dme HttpApi connection plugin for Cisco DME REST API
* Complete module utilities for DME API interaction
* Comprehensive action plugins for all modules
* Full documentation and examples for all modules
* Initial release with dme\_command\, dme\_config\, and dme\_validate modules

<a id="minor-changes"></a>
### Minor Changes

* Added comprehensive error handling and authentication
* Added comprehensive unit test suite for all modules and plugins
* Added support for JSON\-RPC validation requests
* Added test fixtures and mock data for consistent testing
* Added testing documentation and troubleshooting guides
* Created automated test execution scripts and Makefile targets
* Created integration test framework with mock DME endpoints
* Implemented CSRF token generation for secure API calls
* Implemented pytest configuration with coverage reporting
* Included SSL verification configuration options

<a id="new-plugins"></a>
### New Plugins

<a id="httpapi"></a>
#### Httpapi

* cisco\.dme\.dme \- HttpApi Plugin for Cisco Nxos Data Management Engine \(DME\)\.

<a id="new-modules"></a>
### New Modules

* cisco\.dme\.dme\_command \- Fetch arbitrary DME model based on node class\.
* cisco\.dme\.dme\_config \- A configuration module for configuration using DME model\.
* cisco\.dme\.dme\_validate \- Validate and convert configuration on DME managed devices\.
