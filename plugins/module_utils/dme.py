#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (c) 2025 Sagar Paul (@KB-perByte)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type
try:
    from ssl import CertificateError
except ImportError:
    from backports.ssl_match_hostname import CertificateError

from ansible.module_utils._text import to_text
from ansible.module_utils.connection import Connection, ConnectionError

BASE_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def find_dict_in_list(some_list, key, value):
    """
    Find a dictionary in a list based on a key-value pair.

    Args:
        some_list: List of dictionaries to search through
        key: Key to search for in each dictionary
        value: Value to match against the key

    Returns:
        Tuple of (dict, index) if found, None otherwise
    """
    if not isinstance(some_list, list):
        return None

    text_type = False
    try:
        to_text(value)
        text_type = True
    except (TypeError, AttributeError):
        pass

    for index, some_dict in enumerate(some_list):
        if not isinstance(some_dict, dict) or key not in some_dict:
            continue

        if text_type:
            try:
                if to_text(some_dict[key]).strip() == to_text(value).strip():
                    return some_dict, index
            except (TypeError, AttributeError):
                continue
        else:
            if some_dict[key] == value:
                return some_dict, index

    return None


class DmeRequest(object):
    """
    DME Request handler for Cisco devices.

    This class provides a unified interface for making HTTP and JSON-RPC
    requests to Cisco devices supporting the Data Management Engine (DME).

    Args:
        module: Ansible module instance for error handling
        connection: Existing connection instance to reuse
        headers: Custom headers for requests
        not_rest_data_keys: Keys to exclude from REST data processing
        task_vars: Task variables from Ansible execution context
    """

    def __init__(
        self,
        module=None,
        connection=None,
        headers=None,
        not_rest_data_keys=None,
        task_vars=None,
    ):
        self.module = module

        if module:
            self.connection = Connection(self.module._socket_path)
        elif connection:
            self.connection = connection
            try:
                self.connection.load_platform_plugins(
                    "cisco.dme.dme",
                )
                self.connection.set_options(var_options=task_vars)
            except ConnectionError:
                raise

        if not_rest_data_keys:
            self.not_rest_data_keys = not_rest_data_keys
        else:
            self.not_rest_data_keys = []
        self.not_rest_data_keys.append("validate_certs")
        self.headers = headers if headers else BASE_HEADERS

    def _httpapi_error_handle(self, method, uri, **kwargs):
        """
        Handle HTTP API requests with proper error handling and logging.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            uri: API endpoint URI
            **kwargs: Additional parameters for the request

        Returns:
            Response data or tuple of (code, response) depending on context

        Raises:
            AnsibleModule.fail_json: On various error conditions
        """
        code = 99999
        response = {}

        try:
            code, response = self.connection.send_request(
                method,
                uri,
                **kwargs,
            )

            # Log successful requests in debug mode
            if self.module and hasattr(self.module, "_debug") and self.module._debug:
                self.module.log(f"DME API {method} {uri} returned code {code}")

        except ConnectionError as e:
            error_msg = (
                f"Connection error occurred while calling {method} {uri}: {str(e)}"
            )
            if self.module:
                self.module.fail_json(msg=error_msg)
            else:
                raise ConnectionError(error_msg)

        except CertificateError as e:
            error_msg = (
                f"Certificate error occurred while calling {method} {uri}: {str(e)}"
            )
            if self.module:
                self.module.fail_json(msg=error_msg)
            else:
                raise CertificateError(error_msg)

        except ValueError as e:
            error_msg = f"Invalid response received from {method} {uri}: {str(e)}"
            if self.module:
                self.module.fail_json(msg=error_msg)
            else:
                raise ValueError(error_msg)
        except Exception as e:
            error_msg = (
                f"Unexpected error occurred while calling {method} {uri}: {str(e)}"
            )
            if self.module:
                self.module.fail_json(msg=error_msg)
            else:
                raise Exception(error_msg)

        # Check for HTTP error codes
        if code >= 400:
            error_msg = f"HTTP error {code} received from {method} {uri}"
            if isinstance(response, dict) and "error" in response:
                error_msg += f": {response['error']}"
            if self.module:
                self.module.fail_json(msg=error_msg, http_code=code, response=response)

        if self.module:
            return response
        else:
            return code, response

    def _rpc_error_handle(self, method, uri, **kwargs):
        """
        Handle JSON-RPC requests with proper error handling and logging.

        Args:
            method: HTTP method (typically POST for RPC)
            uri: RPC endpoint URI
            **kwargs: Additional parameters for the request

        Returns:
            Response data or tuple of (code, response) depending on context

        Raises:
            AnsibleModule.fail_json: On various error conditions
        """
        code = 99999
        response = {}

        try:
            code, response = self.connection.send_validate_request(
                method,
                uri,
                **kwargs,
            )

            # Log successful RPC requests in debug mode
            if self.module and hasattr(self.module, "_debug") and self.module._debug:
                self.module.log(f"DME RPC {method} {uri} returned code {code}")

        except ConnectionError as e:
            error_msg = (
                f"Connection error occurred during RPC call {method} {uri}: {str(e)}"
            )
            if self.module:
                self.module.fail_json(msg=error_msg)
            else:
                raise ConnectionError(error_msg)

        except CertificateError as e:
            error_msg = (
                f"Certificate error occurred during RPC call {method} {uri}: {str(e)}"
            )
            if self.module:
                self.module.fail_json(msg=error_msg)
            else:
                raise CertificateError(error_msg)

        except ValueError as e:
            error_msg = f"Invalid RPC response received from {method} {uri}: {str(e)}"
            if self.module:
                self.module.fail_json(msg=error_msg)
            else:
                raise ValueError(error_msg)
        except Exception as e:
            error_msg = (
                f"Unexpected error occurred during RPC call {method} {uri}: {str(e)}"
            )
            if self.module:
                self.module.fail_json(msg=error_msg)
            else:
                raise Exception(error_msg)

        # Check for RPC-specific error codes
        if code >= 400:
            error_msg = f"RPC error {code} received from {method} {uri}"
            if isinstance(response, dict) and "error" in response:
                error_msg += f": {response['error']}"
            if self.module:
                self.module.fail_json(msg=error_msg, http_code=code, response=response)

        if self.module:
            return response
        else:
            return code, response

    def get(self, url, **kwargs):
        """Send HTTP GET request to DME API."""
        return self._httpapi_error_handle("GET", url, **kwargs)

    def put(self, url, **kwargs):
        """Send HTTP PUT request to DME API."""
        return self._httpapi_error_handle("PUT", url, **kwargs)

    def post(self, url, **kwargs):
        """Send HTTP POST request to DME API."""
        return self._httpapi_error_handle("POST", url, **kwargs)

    def patch(self, url, **kwargs):
        """Send HTTP PATCH request to DME API."""
        return self._httpapi_error_handle("PATCH", url, **kwargs)

    def delete(self, url, **kwargs):
        """Send HTTP DELETE request to DME API."""
        return self._httpapi_error_handle("DELETE", url, **kwargs)

    def rpc_get(self, url, **kwargs):
        """Send JSON-RPC request to DME validation endpoint."""
        return self._rpc_error_handle("POST", url, **kwargs)
