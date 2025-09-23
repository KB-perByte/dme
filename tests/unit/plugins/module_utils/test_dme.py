# -*- coding: utf-8 -*-
# Copyright 2025 Sagar Paul (@KB-perByte)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for module_utils.dme module."""

import pytest
from unittest.mock import MagicMock, patch, Mock
from ansible.module_utils.connection import ConnectionError

from ansible_collections.cisco.dme.plugins.module_utils.dme import (
    find_dict_in_list,
    DmeRequest,
    BASE_HEADERS,
)


class TestFindDictInList:
    """Test cases for find_dict_in_list utility function."""

    def test_find_dict_in_list_success(self):
        """Test successful dictionary lookup."""
        test_list = [
            {"name": "test1", "value": "value1"},
            {"name": "test2", "value": "value2"},
            {"name": "test3", "value": "value3"},
        ]

        result = find_dict_in_list(test_list, "name", "test2")
        assert result is not None
        dict_found, index = result
        assert dict_found["name"] == "test2"
        assert dict_found["value"] == "value2"
        assert index == 1

    def test_find_dict_in_list_not_found(self):
        """Test dictionary not found."""
        test_list = [
            {"name": "test1", "value": "value1"},
            {"name": "test2", "value": "value2"},
        ]

        result = find_dict_in_list(test_list, "name", "test3")
        assert result is None

    def test_find_dict_in_list_empty_list(self):
        """Test with empty list."""
        result = find_dict_in_list([], "name", "test")
        assert result is None

    def test_find_dict_in_list_not_list(self):
        """Test with non-list input."""
        result = find_dict_in_list("not a list", "name", "test")
        assert result is None

    def test_find_dict_in_list_text_comparison(self):
        """Test text comparison with whitespace."""
        test_list = [
            {"name": "  test1  ", "value": "value1"},
            {"name": "test2", "value": "value2"},
        ]

        result = find_dict_in_list(test_list, "name", "test1")
        assert result is not None
        dict_found, index = result
        assert dict_found["name"] == "  test1  "
        assert index == 0

    def test_find_dict_in_list_non_dict_items(self):
        """Test with list containing non-dictionary items."""
        test_list = [
            "not a dict",
            {"name": "test1", "value": "value1"},
            123,
            {"name": "test2", "value": "value2"},
        ]

        result = find_dict_in_list(test_list, "name", "test2")
        assert result is not None
        dict_found, index = result
        assert dict_found["name"] == "test2"
        assert index == 3

    def test_find_dict_in_list_missing_key(self):
        """Test with dictionaries missing the search key."""
        test_list = [{"other_key": "value1"}, {"name": "test2", "value": "value2"}]

        result = find_dict_in_list(test_list, "name", "test2")
        assert result is not None
        dict_found, index = result
        assert dict_found["name"] == "test2"
        assert index == 1


class TestDmeRequest:
    """Test cases for DmeRequest class."""

    def test_init_with_module(self, mock_module):
        """Test DmeRequest initialization with module."""
        with patch(
            "ansible_collections.cisco.dme.plugins.module_utils.dme.Connection"
        ) as mock_conn_class:
            mock_connection = MagicMock()
            mock_conn_class.return_value = mock_connection

            dme_request = DmeRequest(module=mock_module)

            assert dme_request.module == mock_module
            assert dme_request.connection == mock_connection
            assert dme_request.headers == BASE_HEADERS
            assert "validate_certs" in dme_request.not_rest_data_keys
            mock_conn_class.assert_called_once_with(mock_module._socket_path)

    def test_init_with_connection(self, mock_connection):
        """Test DmeRequest initialization with connection."""
        task_vars = {"test_var": "test_value"}

        dme_request = DmeRequest(connection=mock_connection, task_vars=task_vars)

        assert dme_request.module is None
        assert dme_request.connection == mock_connection
        assert dme_request.headers == BASE_HEADERS
        mock_connection.load_platform_plugins.assert_called_once_with("cisco.dme.dme")
        mock_connection.set_options.assert_called_once_with(var_options=task_vars)

    def test_init_with_connection_error(self, mock_connection):
        """Test DmeRequest initialization with connection error."""
        mock_connection.load_platform_plugins.side_effect = ConnectionError(
            "Connection failed"
        )

        with pytest.raises(ConnectionError):
            DmeRequest(connection=mock_connection)

    def test_init_with_custom_headers(self, mock_connection):
        """Test DmeRequest initialization with custom headers."""
        custom_headers = {"Custom-Header": "custom-value"}
        not_rest_keys = ["custom_key"]

        dme_request = DmeRequest(
            connection=mock_connection,
            headers=custom_headers,
            not_rest_data_keys=not_rest_keys,
        )

        assert dme_request.headers == custom_headers
        assert "custom_key" in dme_request.not_rest_data_keys
        assert "validate_certs" in dme_request.not_rest_data_keys

    def test_httpapi_error_handle_success(self, mock_connection):
        """Test successful HTTP API request handling."""
        mock_connection.send_request.return_value = (200, {"result": "success"})

        dme_request = DmeRequest(connection=mock_connection)
        code, response = dme_request._httpapi_error_handle("GET", "/test")

        assert code == 200
        assert response == {"result": "success"}
        mock_connection.send_request.assert_called_once_with("GET", "/test")

    def test_httpapi_error_handle_with_module_success(
        self, mock_module, mock_connection
    ):
        """Test successful HTTP API request handling with module."""
        mock_connection.send_request.return_value = (200, {"result": "success"})

        with patch(
            "ansible_collections.cisco.dme.plugins.module_utils.dme.Connection",
            return_value=mock_connection,
        ):
            dme_request = DmeRequest(module=mock_module)
            response = dme_request._httpapi_error_handle("GET", "/test")

            assert response == {"result": "success"}

    def test_httpapi_error_handle_connection_error(self, mock_module, mock_connection):
        """Test HTTP API request with connection error."""
        mock_connection.send_request.side_effect = ConnectionError("Connection failed")

        with patch(
            "ansible_collections.cisco.dme.plugins.module_utils.dme.Connection",
            return_value=mock_connection,
        ):
            dme_request = DmeRequest(module=mock_module)

            with pytest.raises(Exception, match="Module failed"):
                dme_request._httpapi_error_handle("GET", "/test")

            mock_module.fail_json.assert_called_once()

    def test_httpapi_error_handle_http_error(self, mock_connection):
        """Test HTTP API request with HTTP error."""
        mock_connection.send_request.return_value = (400, {"error": "Bad Request"})

        dme_request = DmeRequest(connection=mock_connection)
        code, response = dme_request._httpapi_error_handle("GET", "/test")

        assert code == 400
        assert response == {"error": "Bad Request"}

    def test_httpapi_error_handle_http_error_with_module(
        self, mock_module, mock_connection
    ):
        """Test HTTP API request with HTTP error and module."""
        mock_connection.send_request.return_value = (400, {"error": "Bad Request"})

        with patch(
            "ansible_collections.cisco.dme.plugins.module_utils.dme.Connection",
            return_value=mock_connection,
        ):
            dme_request = DmeRequest(module=mock_module)

            with pytest.raises(Exception, match="Module failed"):
                dme_request._httpapi_error_handle("GET", "/test")

            mock_module.fail_json.assert_called_once()

    def test_rpc_error_handle_success(self, mock_connection):
        """Test successful RPC request handling."""
        mock_connection.send_validate_request.return_value = (
            200,
            {"result": "success"},
        )

        dme_request = DmeRequest(connection=mock_connection)
        code, response = dme_request._rpc_error_handle("POST", "/ins")

        assert code == 200
        assert response == {"result": "success"}
        mock_connection.send_validate_request.assert_called_once_with("POST", "/ins")

    def test_rpc_error_handle_with_module_success(self, mock_module, mock_connection):
        """Test successful RPC request handling with module."""
        mock_connection.send_validate_request.return_value = (
            200,
            {"result": "success"},
        )

        with patch(
            "ansible_collections.cisco.dme.plugins.module_utils.dme.Connection",
            return_value=mock_connection,
        ):
            dme_request = DmeRequest(module=mock_module)
            response = dme_request._rpc_error_handle("POST", "/ins")

            assert response == {"result": "success"}

    def test_http_methods(self, mock_connection):
        """Test HTTP method wrappers."""
        mock_connection.send_request.return_value = (200, {"result": "success"})

        dme_request = DmeRequest(connection=mock_connection)

        # Test all HTTP methods
        methods = [
            (dme_request.get, "GET"),
            (dme_request.post, "POST"),
            (dme_request.put, "PUT"),
            (dme_request.patch, "PATCH"),
            (dme_request.delete, "DELETE"),
        ]

        for method_func, http_method in methods:
            mock_connection.send_request.reset_mock()
            code, response = method_func("/test", data={"test": "data"})

            assert code == 200
            assert response == {"result": "success"}
            mock_connection.send_request.assert_called_once_with(
                http_method, "/test", data={"test": "data"}
            )

    def test_rpc_get_method(self, mock_connection):
        """Test RPC GET method wrapper."""
        mock_connection.send_validate_request.return_value = (
            200,
            {"result": "success"},
        )

        dme_request = DmeRequest(connection=mock_connection)
        code, response = dme_request.rpc_get("/ins", data={"test": "data"})

        assert code == 200
        assert response == {"result": "success"}
        mock_connection.send_validate_request.assert_called_once_with(
            "POST", "/ins", data={"test": "data"}
        )

    def test_debug_logging(self, mock_module, mock_connection):
        """Test debug logging functionality."""
        mock_module._debug = True
        mock_connection.send_request.return_value = (200, {"result": "success"})

        with patch(
            "ansible_collections.cisco.dme.plugins.module_utils.dme.Connection",
            return_value=mock_connection,
        ):
            dme_request = DmeRequest(module=mock_module)
            dme_request._httpapi_error_handle("GET", "/test")

            mock_module.log.assert_called_once_with(
                "DME API GET /test returned code 200"
            )

    def test_certificate_error_handling(self, mock_module, mock_connection):
        """Test certificate error handling."""
        from ssl import CertificateError

        mock_connection.send_request.side_effect = CertificateError("Certificate error")

        with patch(
            "ansible_collections.cisco.dme.plugins.module_utils.dme.Connection",
            return_value=mock_connection,
        ):
            dme_request = DmeRequest(module=mock_module)

            with pytest.raises(Exception, match="Module failed"):
                dme_request._httpapi_error_handle("GET", "/test")

            # Check that fail_json was called with certificate error message
            args, kwargs = mock_module.fail_json.call_args
            assert "Certificate error" in kwargs["msg"]

    def test_value_error_handling(self, mock_module, mock_connection):
        """Test value error handling."""
        mock_connection.send_request.side_effect = ValueError("Invalid JSON")

        with patch(
            "ansible_collections.cisco.dme.plugins.module_utils.dme.Connection",
            return_value=mock_connection,
        ):
            dme_request = DmeRequest(module=mock_module)

            with pytest.raises(Exception, match="Module failed"):
                dme_request._httpapi_error_handle("GET", "/test")

            # Check that fail_json was called with value error message
            args, kwargs = mock_module.fail_json.call_args
            assert "Invalid response" in kwargs["msg"]

    def test_unexpected_error_handling(self, mock_module, mock_connection):
        """Test unexpected error handling."""
        mock_connection.send_request.side_effect = RuntimeError("Unexpected error")

        with patch(
            "ansible_collections.cisco.dme.plugins.module_utils.dme.Connection",
            return_value=mock_connection,
        ):
            dme_request = DmeRequest(module=mock_module)

            with pytest.raises(Exception, match="Module failed"):
                dme_request._httpapi_error_handle("GET", "/test")

            # Check that fail_json was called with unexpected error message
            args, kwargs = mock_module.fail_json.call_args
            assert "Unexpected error" in kwargs["msg"]
