# -*- coding: utf-8 -*-
# Copyright 2025 Sagar Paul (@KB-perByte)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Pytest configuration and shared fixtures for DME tests."""

import json
from unittest.mock import MagicMock, Mock
import pytest
from ansible.module_utils.connection import Connection
from .fixtures.dme_responses import (
    MOCK_LOGIN_RESPONSE,
    MOCK_LOGOUT_RESPONSE,
    MOCK_CLASS_RESPONSE,
    MOCK_MO_RESPONSE,
    MOCK_VALIDATION_SUCCESS_RESPONSE,
    MOCK_CONFIG_SUCCESS_RESPONSE,
)


@pytest.fixture
def mock_connection():
    """Create a mock connection for testing."""
    connection = MagicMock(spec=Connection)
    connection.socket_path = "/tmp/test_socket"
    connection._url = (
        "https://test-device.example.com"  # pylint: disable=protected-access
    )
    connection.get_options.return_value = {
        "host": "test-device.example.com",
        "port": 443,
        "remote_user": "admin",
        "password": "password",
        "validate_certs": False,
    }
    return connection


@pytest.fixture
def mock_module():
    """Create a mock Ansible module for testing."""
    module = MagicMock()
    module._socket_path = "/tmp/test_socket"  # pylint: disable=protected-access
    module._debug = False  # pylint: disable=protected-access
    module.fail_json = Mock(side_effect=Exception("Module failed"))
    module.log = Mock()
    return module


@pytest.fixture
def mock_task():
    """Create a mock Ansible task for testing."""
    task = MagicMock()
    task.action = "cisco.dme.dme_command"
    task.args = {}
    return task


@pytest.fixture
def mock_httpapi_responses():
    """Create mock HTTP API responses."""
    return {
        "login": (200, MOCK_LOGIN_RESPONSE),
        "logout": (200, MOCK_LOGOUT_RESPONSE),
        "class_query": (200, MOCK_CLASS_RESPONSE),
        "mo_query": (200, MOCK_MO_RESPONSE),
        "config": (200, MOCK_CONFIG_SUCCESS_RESPONSE),
    }


@pytest.fixture
def mock_validation_responses():
    """Create mock validation responses."""
    return {
        "success": (200, MOCK_VALIDATION_SUCCESS_RESPONSE),
    }


@pytest.fixture
def mock_ansible_env(monkeypatch):
    """Mock Ansible environment variables and imports."""
    # Mock the ssl import handling
    monkeypatch.setattr("ssl.CertificateError", Exception)

    # Mock requests for the httpapi plugin
    mock_requests = MagicMock()
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "jsonrpc": "2.0",
            "result": {"msg": json.dumps(MOCK_VALIDATION_SUCCESS_RESPONSE["dme_data"])},
            "id": 1,
        }
    ]
    mock_session.post.return_value = mock_response
    mock_requests.Session.return_value = mock_session
    mock_requests.packages.urllib3.disable_warnings = MagicMock()
    mock_requests.exceptions.RequestException = Exception

    monkeypatch.setattr("requests", mock_requests, raising=False)

    return mock_requests
