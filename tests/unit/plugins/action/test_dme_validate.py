# -*- coding: utf-8 -*-
# Copyright 2025 Sagar Paul (@KB-perByte)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for action.dme_validate plugin."""

import pytest
from unittest.mock import MagicMock, patch
from ansible.plugins.action import ActionBase

from ansible_collections.cisco.dme.plugins.action.dme_validate import ActionModule
from ansible_collections.cisco.dme.tests.unit.fixtures.dme_responses import (
    MOCK_VALIDATION_SUCCESS_RESPONSE,
    MOCK_VALIDATION_ERROR_RESPONSE,
)


class TestDmeValidateAction:
    """Test cases for DME validate action plugin."""

    @pytest.fixture
    def action_module(self, mock_task):
        """Create ActionModule instance for testing."""
        action = ActionModule(
            task=mock_task,
            connection=MagicMock(),
            play_context=MagicMock(),
            loader=MagicMock(),
            templar=MagicMock(),
            shared_loader_obj=MagicMock(),
        )
        action._task = mock_task
        action._connection = MagicMock()
        action._connection.socket_path = "/tmp/test_socket"
        return action

    def test_init(self, action_module):
        """Test ActionModule initialization."""
        assert action_module._result is None
        assert action_module._supports_async is True
        assert action_module.api_object == "/ins"

    def test_parse_config_block_basic(self, action_module):
        """Test basic configuration block parsing."""
        config_text = """interface Ethernet1/1
description Test interface
no shutdown
ip address 192.168.1.1/24"""

        result = action_module.parse_config_block(config_text)

        expected = [
            "interface Ethernet1/1",
            "description Test interface",
            "no shutdown",
            "ip address 192.168.1.1/24",
        ]
        assert result == expected

    def test_parse_config_block_with_comments(self, action_module):
        """Test configuration parsing with comments."""
        config_text = """interface Ethernet1/1
! This is a comment
description Test interface
! Another comment
no shutdown"""

        result = action_module.parse_config_block(config_text)

        expected = [
            "interface Ethernet1/1",
            "description Test interface",
            "no shutdown",
        ]
        assert result == expected

    def test_parse_config_block_with_empty_lines(self, action_module):
        """Test configuration parsing with empty lines."""
        config_text = """interface Ethernet1/1

description Test interface


no shutdown

"""

        result = action_module.parse_config_block(config_text)

        expected = [
            "interface Ethernet1/1",
            "description Test interface",
            "no shutdown",
        ]
        assert result == expected

    def test_parse_config_block_empty(self, action_module):
        """Test parsing empty configuration."""
        result = action_module.parse_config_block("")
        assert result == []

        result = action_module.parse_config_block(None)
        assert result == []

    def test_parse_config_block_whitespace_handling(self, action_module):
        """Test parsing with various whitespace scenarios."""
        config_text = """  interface Ethernet1/1
    description Test interface
no shutdown"""

        result = action_module.parse_config_block(config_text)

        expected = [
            "  interface Ethernet1/1",
            "    description Test interface",
            "no shutdown",
        ]
        assert result == expected

    def test_config_to_jsonrpc_payload_basic(self, action_module):
        """Test basic JSON-RPC payload generation."""
        config_lines = [
            "interface Ethernet1/1",
            "description Test interface",
            "no shutdown",
        ]

        result = action_module.config_to_jsonrpc_payload(config_lines)

        expected = [
            {
                "jsonrpc": "2.0",
                "method": "cli_rest",
                "option": "default",
                "params": {"cmd": "interface Ethernet1/1", "version": 1},
                "id": 1,
            },
            {
                "jsonrpc": "2.0",
                "method": "cli_rest",
                "option": "default",
                "params": {"cmd": "description Test interface", "version": 1},
                "id": 2,
            },
            {
                "jsonrpc": "2.0",
                "method": "cli_rest",
                "option": "default",
                "params": {"cmd": "no shutdown", "version": 1},
                "id": 3,
            },
        ]

        assert result == expected

    def test_config_to_jsonrpc_payload_custom_start_id(self, action_module):
        """Test JSON-RPC payload generation with custom start ID."""
        config_lines = ["show version", "show interface"]

        result = action_module.config_to_jsonrpc_payload(config_lines, start_id=10)

        assert result[0]["id"] == 10
        assert result[1]["id"] == 11

    def test_config_to_jsonrpc_payload_empty(self, action_module):
        """Test JSON-RPC payload generation with empty input."""
        result = action_module.config_to_jsonrpc_payload([])
        assert result == []

        result = action_module.config_to_jsonrpc_payload(None)
        assert result == []

    def test_config_to_jsonrpc_payload_skip_empty_commands(self, action_module):
        """Test JSON-RPC payload generation skips empty commands."""
        config_lines = [
            "interface Ethernet1/1",
            "",
            "   ",
            "description Test interface",
        ]

        result = action_module.config_to_jsonrpc_payload(config_lines)

        assert len(result) == 2
        assert result[0]["params"]["cmd"] == "interface Ethernet1/1"
        assert result[1]["params"]["cmd"] == "description Test interface"

    def test_configure_module_rpc_success(self, action_module):
        """Test successful RPC configuration."""
        mock_dme_request = MagicMock()
        mock_dme_request.rpc_get.return_value = (200, MOCK_VALIDATION_SUCCESS_RESPONSE)

        payload = [
            {
                "jsonrpc": "2.0",
                "method": "cli_rest",
                "params": {"cmd": "show version"},
                "id": 1,
            }
        ]

        api_response, code = action_module.configure_module_rpc(
            mock_dme_request, payload
        )

        assert api_response == MOCK_VALIDATION_SUCCESS_RESPONSE
        assert code == 200
        mock_dme_request.rpc_get.assert_called_once_with(
            action_module.api_object, data=payload
        )

    def test_configure_module_rpc_empty_payload(self, action_module):
        """Test RPC configuration with empty payload."""
        mock_dme_request = MagicMock()

        with pytest.raises(ValueError, match="RPC payload is required"):
            action_module.configure_module_rpc(mock_dme_request, None)

    @patch("ansible_collections.cisco.dme.plugins.action.dme_validate.Connection")
    @patch("ansible_collections.cisco.dme.plugins.action.dme_validate.DmeRequest")
    def test_run_with_lines_success(
        self, mock_dme_request_class, mock_connection_class, action_module
    ):
        """Test successful run with lines parameter."""
        # Setup mocks
        mock_connection = MagicMock()
        mock_connection_class.return_value = mock_connection

        mock_dme_request = MagicMock()
        mock_dme_request_class.return_value = mock_dme_request
        mock_dme_request.rpc_get.return_value = (200, MOCK_VALIDATION_SUCCESS_RESPONSE)

        # Setup task args
        action_module._task.args = {
            "lines": ["description Test interface", "no shutdown"],
            "parents": ["interface Ethernet1/1"],
        }

        # Mock parent run method
        with patch.object(ActionBase, "run", return_value={}):
            with patch.object(action_module, "_check_argspec"):
                result = action_module.run()

        # Verify results
        assert result["changed"] is True
        assert result["valid"] is True
        assert result["model"] == MOCK_VALIDATION_SUCCESS_RESPONSE["dme_data"]
        assert "errors" not in result

    @patch("ansible_collections.cisco.dme.plugins.action.dme_validate.Connection")
    @patch("ansible_collections.cisco.dme.plugins.action.dme_validate.DmeRequest")
    def test_run_with_validation_errors(
        self, mock_dme_request_class, mock_connection_class, action_module
    ):
        """Test run with validation errors."""
        # Setup mocks
        mock_connection = MagicMock()
        mock_connection_class.return_value = mock_connection

        mock_dme_request = MagicMock()
        mock_dme_request_class.return_value = mock_dme_request
        mock_dme_request.rpc_get.return_value = (200, MOCK_VALIDATION_ERROR_RESPONSE)

        # Setup task args with intentional error
        action_module._task.args = {
            "lines": ["idescription Invalid command", "no shutdown"],
            "parents": ["interface Ethernet1/1"],
        }

        # Mock parent run method
        with patch.object(ActionBase, "run", return_value={}):
            with patch.object(action_module, "_check_argspec"):
                result = action_module.run()

        # Verify results
        assert result["changed"] is True
        assert result["valid"] is False
        assert result["model"] == MOCK_VALIDATION_ERROR_RESPONSE["dme_data"]
        assert "errors" in result
        assert 0 in result["errors"]  # First command had an error

    @patch("ansible_collections.cisco.dme.plugins.action.dme_validate.Connection")
    @patch("ansible_collections.cisco.dme.plugins.action.dme_validate.DmeRequest")
    def test_run_with_string_parents(
        self, mock_dme_request_class, mock_connection_class, action_module
    ):
        """Test run with parents as string instead of list."""
        # Setup mocks
        mock_connection = MagicMock()
        mock_connection_class.return_value = mock_connection

        mock_dme_request = MagicMock()
        mock_dme_request_class.return_value = mock_dme_request
        mock_dme_request.rpc_get.return_value = (200, MOCK_VALIDATION_SUCCESS_RESPONSE)

        # Setup task args with string parents
        action_module._task.args = {
            "lines": ["description Test interface"],
            "parents": "interface Ethernet1/1",  # String instead of list
        }

        # Mock parent run method
        with patch.object(ActionBase, "run", return_value={}):
            with patch.object(action_module, "_check_argspec"):
                result = action_module.run()

        # Verify it still works
        assert result["changed"] is True
        assert result["valid"] is True

    @patch("ansible_collections.cisco.dme.plugins.action.dme_validate.Connection")
    @patch("ansible_collections.cisco.dme.plugins.action.dme_validate.DmeRequest")
    def test_run_with_string_lines(
        self, mock_dme_request_class, mock_connection_class, action_module
    ):
        """Test run with lines as string instead of list."""
        # Setup mocks
        mock_connection = MagicMock()
        mock_connection_class.return_value = mock_connection

        mock_dme_request = MagicMock()
        mock_dme_request_class.return_value = mock_dme_request
        mock_dme_request.rpc_get.return_value = (200, MOCK_VALIDATION_SUCCESS_RESPONSE)

        # Setup task args with string lines
        action_module._task.args = {
            "lines": "description Test interface",  # String instead of list
            "parents": ["interface Ethernet1/1"],
        }

        # Mock parent run method
        with patch.object(ActionBase, "run", return_value={}):
            with patch.object(action_module, "_check_argspec"):
                result = action_module.run()

        # Verify it still works
        assert result["changed"] is True
        assert result["valid"] is True

    @patch("ansible_collections.cisco.dme.plugins.action.dme_validate.Connection")
    @patch("ansible_collections.cisco.dme.plugins.action.dme_validate.DmeRequest")
    def test_run_without_lines_or_src(
        self, mock_dme_request_class, mock_connection_class, action_module
    ):
        """Test run without lines or src parameters."""
        # Setup mocks
        mock_connection = MagicMock()
        mock_connection_class.return_value = mock_connection

        mock_dme_request = MagicMock()
        mock_dme_request_class.return_value = mock_dme_request

        # Setup task args without lines or src
        action_module._task.args = {}

        # Mock parent run method
        with patch.object(ActionBase, "run", return_value={}):
            with patch.object(action_module, "_check_argspec"):
                result = action_module.run()

        # Verify it doesn't call RPC
        assert result["changed"] is False
        mock_dme_request.rpc_get.assert_not_called()

    def test_check_argspec_valid(self, action_module):
        """Test argument specification validation with valid args."""
        action_module._task.args = {
            "lines": ["description Test interface"],
            "parents": ["interface Ethernet1/1"],
        }
        action_module._result = {}

        with patch(
            "ansible_collections.cisco.dme.plugins.action.dme_validate.AnsibleArgSpecValidator"
        ) as mock_validator:
            mock_validator.return_value.validate.return_value = (
                True,
                [],
                action_module._task.args,
            )

            action_module._check_argspec()

            assert not action_module._result.get("failed", False)

    def test_check_argspec_invalid(self, action_module):
        """Test argument specification validation with invalid args."""
        action_module._task.args = {"invalid": "args"}
        action_module._result = {}

        with patch(
            "ansible_collections.cisco.dme.plugins.action.dme_validate.AnsibleArgSpecValidator"
        ) as mock_validator:
            mock_validator.return_value.validate.return_value = (
                False,
                ["Invalid arguments"],
                {},
            )

            action_module._check_argspec()

            assert action_module._result["failed"] is True
            assert action_module._result["msg"] == ["Invalid arguments"]

    def test_supports_check_mode(self, action_module):
        """Test that check mode is not supported."""
        with patch.object(ActionBase, "run", return_value={}):
            with patch.object(action_module, "_check_argspec"):
                action_module.run()

        assert action_module._supports_check_mode is False

    def test_error_mapping(self, action_module):
        """Test error mapping functionality."""
        # Test the error mapping logic specifically
        config_raw = "interface Ethernet1/1\nidescription Invalid\nno shutdown\n"
        error_map = {0: "", 1: ""}  # Errors on first two commands

        # Simulate the error mapping process
        config_list = config_raw.split("\n")
        new_err_map = {}
        for idx, cmd in error_map.items():
            new_err_map[idx] = config_list[idx]

        expected_errors = {0: "interface Ethernet1/1", 1: "idescription Invalid"}

        assert new_err_map == expected_errors

    @patch("ansible_collections.cisco.dme.plugins.action.dme_validate.Connection")
    @patch("ansible_collections.cisco.dme.plugins.action.dme_validate.DmeRequest")
    def test_run_with_complex_config(
        self, mock_dme_request_class, mock_connection_class, action_module
    ):
        """Test run with complex multi-line configuration."""
        # Setup mocks
        mock_connection = MagicMock()
        mock_connection_class.return_value = mock_connection

        mock_dme_request = MagicMock()
        mock_dme_request_class.return_value = mock_dme_request
        mock_dme_request.rpc_get.return_value = (200, MOCK_VALIDATION_SUCCESS_RESPONSE)

        # Setup complex configuration
        action_module._task.args = {
            "lines": [
                "description Complex interface configuration",
                "switchport mode trunk",
                "switchport trunk allowed vlan 100,200,300",
                "spanning-tree port type edge trunk",
                "no shutdown",
            ],
            "parents": ["interface Ethernet1/1"],
        }

        # Mock parent run method
        with patch.object(ActionBase, "run", return_value={}):
            with patch.object(action_module, "_check_argspec"):
                result = action_module.run()

        # Verify the complex configuration was processed
        assert result["changed"] is True
        assert result["valid"] is True

        # Verify RPC was called with correct payload structure
        call_args = mock_dme_request.rpc_get.call_args
        payload = call_args[1]["data"]

        # Should have 6 commands total (1 parent + 5 lines)
        assert len(payload) == 6
        assert payload[0]["params"]["cmd"] == "interface Ethernet1/1"
        assert (
            payload[1]["params"]["cmd"] == "description Complex interface configuration"
        )
