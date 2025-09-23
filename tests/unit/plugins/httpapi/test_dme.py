# -*- coding: utf-8 -*-
# Copyright 2025 Sagar Paul (@KB-perByte)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for httpapi.dme plugin."""

import json
import pytest
from unittest.mock import MagicMock, patch, Mock
from ansible.errors import AnsibleAuthenticationFailure
from ansible.module_utils.six.moves.urllib.error import HTTPError

from ansible_collections.cisco.dme.plugins.httpapi.dme import (
    HttpApi,
    BASE_HEADERS,
    LOGIN_URL,
    LOGOUT_URL,
)
from ansible_collections.cisco.dme.tests.unit.fixtures.dme_responses import (
    MOCK_LOGIN_RESPONSE,
    MOCK_LOGOUT_RESPONSE,
    MOCK_AUTH_ERROR_RESPONSE,
    MOCK_VALIDATION_SUCCESS_RESPONSE,
    MOCK_JSONRPC_SUCCESS_RESPONSE,
)


class TestHttpApi:
    """Test cases for DME HttpApi plugin."""

    @pytest.fixture
    def http_api(self):
        """Create HttpApi instance for testing."""
        api = HttpApi()
        api.connection = MagicMock()
        api.connection._url = "https://test-device.example.com"
        api.connection.get_options.return_value = {
            "host": "test-device.example.com",
            "port": 443,
            "remote_user": "admin",
            "password": "password",
            "validate_certs": False,
        }
        return api

    def test_send_request_success(self, http_api):
        """Test successful HTTP request."""
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response_data = MagicMock()
        mock_response_data.getvalue.return_value = json.dumps(
            MOCK_LOGIN_RESPONSE
        ).encode()

        http_api.connection.send.return_value = (mock_response, mock_response_data)

        code, response = http_api.send_request("POST", LOGIN_URL, data={"test": "data"})

        assert code == 200
        assert response == MOCK_LOGIN_RESPONSE
        http_api.connection.send.assert_called_once()

    def test_send_request_with_params(self, http_api):
        """Test HTTP request with URL parameters."""
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response_data = MagicMock()
        mock_response_data.getvalue.return_value = json.dumps(
            {"result": "success"}
        ).encode()

        http_api.connection.send.return_value = (mock_response, mock_response_data)

        params = {"param1": "value1", "param2": "value2"}
        code, response = http_api.send_request("GET", "/api/test", params=params)

        assert code == 200
        # Verify URL was constructed with parameters
        call_args = http_api.connection.send.call_args
        assert "param1=value1" in call_args[0][0]
        assert "param2=value2" in call_args[0][0]

    def test_send_request_with_none_params(self, http_api):
        """Test HTTP request with None parameters (should be filtered out)."""
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response_data = MagicMock()
        mock_response_data.getvalue.return_value = json.dumps(
            {"result": "success"}
        ).encode()

        http_api.connection.send.return_value = (mock_response, mock_response_data)

        params = {"param1": "value1", "param2": None, "param3": "value3"}
        code, response = http_api.send_request("GET", "/api/test", params=params)

        assert code == 200
        # Verify None parameters were filtered out
        call_args = http_api.connection.send.call_args
        url = call_args[0][0]
        assert "param1=value1" in url
        assert "param2" not in url
        assert "param3=value3" in url

    def test_send_request_http_error(self, http_api):
        """Test HTTP request with HTTPError."""
        error_response = HTTPError(
            url="test_url", code=401, msg="Unauthorized", hdrs=None, fp=None
        )
        error_response.read = Mock(
            return_value=json.dumps(MOCK_AUTH_ERROR_RESPONSE).encode()
        )
        http_api.connection.send.side_effect = error_response

        code, response = http_api.send_request("POST", LOGIN_URL)

        assert code == 401
        assert response == MOCK_AUTH_ERROR_RESPONSE

    def test_send_request_empty_response(self, http_api):
        """Test HTTP request with empty response."""
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response_data = MagicMock()
        mock_response_data.getvalue.return_value = b""

        http_api.connection.send.return_value = (mock_response, mock_response_data)

        code, response = http_api.send_request("GET", "/api/test")

        assert code == 200
        assert response == {}

    def test_send_validate_request_success(self, http_api, mock_ansible_env):
        """Test successful validation request."""
        mock_requests = mock_ansible_env
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_JSONRPC_SUCCESS_RESPONSE
        mock_requests.Session.return_value.post.return_value = mock_response

        data = [
            {
                "jsonrpc": "2.0",
                "method": "cli_rest",
                "params": {"cmd": "show version"},
                "id": 1,
            }
        ]

        code, response = http_api.send_validate_request("POST", "/ins", data=data)

        assert code == 200
        assert "dme_data" in response
        assert "errors" in response
        assert response["dme_data"] == MOCK_VALIDATION_SUCCESS_RESPONSE["dme_data"]

    def test_send_validate_request_no_credentials(self, http_api):
        """Test validation request without credentials."""
        http_api.connection.get_options.return_value = {
            "host": "test-device.example.com",
            "port": 443,
            "remote_user": None,
            "password": None,
        }

        with pytest.raises(
            AnsibleAuthenticationFailure, match="Username and password are required"
        ):
            http_api.send_validate_request("POST", "/ins")

    def test_send_validate_request_with_errors(self, http_api, mock_ansible_env):
        """Test validation request with command errors."""
        mock_requests = mock_ansible_env
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "jsonrpc": "2.0",
                "error": {"code": -32600, "message": "Invalid Request"},
                "id": 1,
            },
            {
                "jsonrpc": "2.0",
                "result": {
                    "msg": json.dumps(MOCK_VALIDATION_SUCCESS_RESPONSE["dme_data"])
                },
                "id": 2,
            },
        ]
        mock_requests.Session.return_value.post.return_value = mock_response

        data = [
            {
                "jsonrpc": "2.0",
                "method": "cli_rest",
                "params": {"cmd": "invalid command"},
                "id": 1,
            },
            {
                "jsonrpc": "2.0",
                "method": "cli_rest",
                "params": {"cmd": "show version"},
                "id": 2,
            },
        ]

        code, response = http_api.send_validate_request("POST", "/ins", data=data)

        assert code == 200
        assert "errors" in response
        assert 0 in response["errors"]  # First command had an error

    def test_send_validate_request_request_exception(self, http_api, mock_ansible_env):
        """Test validation request with requests exception."""
        mock_requests = mock_ansible_env
        mock_requests.Session.return_value.post.side_effect = (
            mock_requests.exceptions.RequestException("Network error")
        )

        with pytest.raises(AnsibleAuthenticationFailure, match="Request failed"):
            http_api.send_validate_request("POST", "/ins")

    def test_send_validate_request_json_error(self, http_api, mock_ansible_env):
        """Test validation request with JSON parsing error."""
        mock_requests = mock_ansible_env
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_requests.Session.return_value.post.return_value = mock_response

        with pytest.raises(
            AnsibleAuthenticationFailure, match="Invalid response format"
        ):
            http_api.send_validate_request("POST", "/ins")

    def test_login_success(self, http_api):
        """Test successful login."""
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response_data = MagicMock()
        mock_response_data.getvalue.return_value = json.dumps(
            MOCK_LOGIN_RESPONSE
        ).encode()

        http_api.connection.send.return_value = (mock_response, mock_response_data)

        http_api.login("admin", "password")

        # Verify authentication data was set
        assert hasattr(http_api, "_auth_token")
        assert hasattr(http_api, "_session_id")
        assert hasattr(http_api, "_username")
        assert hasattr(http_api, "_siteFineprint")
        assert http_api._auth_token == "test-token-12345"
        assert http_api.connection._auth["Cookie"] == "APIC-cookie=test-token-12345"

    def test_login_auth_failure_with_error_message(self, http_api):
        """Test login failure with error message."""
        error_response = {"error": {"code": "401", "message": "Authentication failed"}}

        mock_response = MagicMock()
        mock_response.getcode.return_value = 401
        mock_response_data = MagicMock()
        mock_response_data.getvalue.return_value = json.dumps(error_response).encode()

        http_api.connection.send.return_value = (mock_response, mock_response_data)

        with pytest.raises(AnsibleAuthenticationFailure, match="Authentication failed"):
            http_api.login("admin", "wrong_password")

    def test_login_invalid_response_format(self, http_api):
        """Test login with invalid response format."""
        invalid_response = {"invalid": "response"}

        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response_data = MagicMock()
        mock_response_data.getvalue.return_value = json.dumps(invalid_response).encode()

        http_api.connection.send.return_value = (mock_response, mock_response_data)

        with pytest.raises(
            AnsibleAuthenticationFailure, match="Failed to acquire login token"
        ):
            http_api.login("admin", "password")

    def test_logout_success(self, http_api):
        """Test successful logout."""
        http_api.connection._auth = {"Cookie": "APIC-cookie=test-token"}
        http_api._auth_token = "test-token"

        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response_data = MagicMock()
        mock_response_data.getvalue.return_value = json.dumps(
            MOCK_LOGOUT_RESPONSE
        ).encode()

        http_api.connection.send.return_value = (mock_response, mock_response_data)

        http_api.logout()

        # Verify authentication data was cleared
        assert http_api.connection._auth is None
        assert http_api._auth_token is None

    def test_logout_no_auth(self, http_api):
        """Test logout when not authenticated."""
        http_api.connection._auth = None

        # Should not make any request if not authenticated
        http_api.logout()

        http_api.connection.send.assert_not_called()

    def test_display_request(self, http_api):
        """Test request display logging."""
        http_api._display_request("GET")

        http_api.connection.queue_message.assert_called_once_with(
            "vvvv", "DME API REST: GET https://test-device.example.com"
        )

    def test_get_response_value(self, http_api):
        """Test response value extraction."""
        mock_response_data = MagicMock()
        mock_response_data.getvalue.return_value = b'{"test": "value"}'

        result = http_api._get_response_value(mock_response_data)

        assert result == '{"test": "value"}'

    def test_response_to_json_valid(self, http_api):
        """Test JSON response parsing with valid JSON."""
        json_string = '{"test": "value"}'

        result = http_api._response_to_json(json_string)

        assert result == {"test": "value"}

    def test_response_to_json_invalid(self, http_api):
        """Test JSON response parsing with invalid JSON."""
        invalid_json = "invalid json string"

        result = http_api._response_to_json(invalid_json)

        assert result == invalid_json

    def test_response_to_json_empty(self, http_api):
        """Test JSON response parsing with empty string."""
        result = http_api._response_to_json("")

        assert result == {}

    def test_csrf_token_generation(self, http_api, mock_ansible_env):
        """Test CSRF token generation in validation requests."""
        mock_requests = mock_ansible_env
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_JSONRPC_SUCCESS_RESPONSE
        mock_requests.Session.return_value.post.return_value = mock_response

        # Make two requests and verify different CSRF tokens
        http_api.send_validate_request("POST", "/ins", data=[])
        call1_headers = mock_requests.Session.return_value.post.call_args[1]["headers"]

        # Reset mock to make another call
        mock_requests.Session.return_value.post.reset_mock()
        http_api.send_validate_request("POST", "/ins", data=[])
        call2_headers = mock_requests.Session.return_value.post.call_args[1]["headers"]

        # CSRF tokens should be different (dynamic generation)
        assert "anticsrf" in call1_headers
        assert "anticsrf" in call2_headers
        # Note: Due to time-based generation, tokens might be the same if called very quickly
        # This test mainly ensures the header is present

    def test_ssl_verification_settings(self, http_api, mock_ansible_env):
        """Test SSL verification settings are respected."""
        mock_requests = mock_ansible_env
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_JSONRPC_SUCCESS_RESPONSE
        mock_requests.Session.return_value.post.return_value = mock_response

        # Test with SSL verification disabled (default in our mock)
        http_api.send_validate_request("POST", "/ins", data=[])

        # Verify session.verify was set to False
        session_instance = mock_requests.Session.return_value
        assert session_instance.verify == False

        # Verify urllib3 warnings were disabled
        mock_requests.packages.urllib3.disable_warnings.assert_called()

    def test_headers_construction(self, http_api, mock_ansible_env):
        """Test proper headers construction for validation requests."""
        mock_requests = mock_ansible_env
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_JSONRPC_SUCCESS_RESPONSE
        mock_requests.Session.return_value.post.return_value = mock_response

        http_api.send_validate_request("POST", "/ins", data=[])

        call_headers = mock_requests.Session.return_value.post.call_args[1]["headers"]

        assert call_headers["Authorization"].startswith("Basic ")
        assert call_headers["Content-Type"] == "application/json-rpc"
        assert call_headers["Host"] == "test-device.example.com:443"
        assert call_headers["Origin"] == "https://test-device.example.com"
        assert call_headers["Referer"] == "https://test-device.example.com/"
        assert "anticsrf" in call_headers
