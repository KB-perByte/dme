# -*- coding: utf-8 -*-
# Copyright 2025 Sagar Paul (@KB-perByte)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for action.dme_command plugin."""

import pytest
from unittest.mock import MagicMock, patch, Mock
from ansible.plugins.action import ActionBase

from ansible_collections.cisco.dme.plugins.action.dme_command import ActionModule
from ansible_collections.cisco.dme.tests.unit.fixtures.dme_responses import (
    MOCK_CLASS_RESPONSE,
    MOCK_MO_RESPONSE,
)


class TestDmeCommandAction:
    """Test cases for DME command action plugin."""

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
        assert action_module.api_object == ""
        assert action_module.api_object_search == ""
        assert action_module.module_class_return == "class"
        assert action_module.module_mo_return == "mo"

    def test_check_argspec_valid(self, action_module):
        """Test argument specification validation with valid args."""
        action_module._task.args = {"read_class": {"entry": "ipv4aclACL"}}
        action_module._result = {}

        with patch(
            "ansible_collections.cisco.dme.plugins.action.dme_command.AnsibleArgSpecValidator"
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
            "ansible_collections.cisco.dme.plugins.action.dme_command.AnsibleArgSpecValidator"
        ) as mock_validator:
            mock_validator.return_value.validate.return_value = (
                False,
                ["Error message"],
                {},
            )

            action_module._check_argspec()

            assert action_module._result["failed"] is True
            assert action_module._result["msg"] == ["Error message"]

    def test_configure_class_api_success(self, action_module):
        """Test successful class API configuration."""
        mock_dme_request = MagicMock()
        mock_dme_request.get.return_value = (200, MOCK_CLASS_RESPONSE)

        read_class = {"entry": "ipv4aclACL", "rsp_prop_include": "config-only"}

        api_response, code = action_module.configure_class_api(
            mock_dme_request, read_class
        )

        assert api_response == MOCK_CLASS_RESPONSE
        assert code == 200
        assert (
            action_module.api_object
            == "/api/node/class/ipv4aclACL.json?rsp-prop-include=config-only"
        )
        mock_dme_request.get.assert_called_once_with(action_module.api_object, data="")

    def test_configure_class_api_without_rsp_prop_include(self, action_module):
        """Test class API configuration without rsp_prop_include."""
        mock_dme_request = MagicMock()
        mock_dme_request.get.return_value = (200, MOCK_CLASS_RESPONSE)

        read_class = {"entry": "ipv4aclACL"}

        api_response, code = action_module.configure_class_api(
            mock_dme_request, read_class
        )

        assert api_response == MOCK_CLASS_RESPONSE
        assert code == 200
        assert action_module.api_object == "/api/node/class/ipv4aclACL.json"

    def test_configure_class_api_missing_entry(self, action_module):
        """Test class API configuration with missing entry."""
        mock_dme_request = MagicMock()
        read_class = {}

        with pytest.raises(ValueError, match="Class entry is required"):
            action_module.configure_class_api(mock_dme_request, read_class)

    def test_configure_mo_api_success(self, action_module):
        """Test successful managed object API configuration."""
        mock_dme_request = MagicMock()
        mock_dme_request.get.return_value = (200, MOCK_MO_RESPONSE)

        read_dn = {
            "entry": "sys/intf/phys-[eth1/1]",
            "rsp_prop_include": "config-only",
            "rsp_subtree": "full",
            "query_target": "subtree",
            "target_subtree_class": "topSystem",
        }

        api_response, code = action_module.configure_mo_api(mock_dme_request, read_dn)

        assert api_response == MOCK_MO_RESPONSE
        assert code == 200
        expected_url = "/api/mo/sys/intf/phys-[eth1/1].json?rsp-prop-include=config-only&rsp-subtree=full&query-target=subtree&target-subtree-class=topSystem"
        assert action_module.api_object == expected_url
        mock_dme_request.get.assert_called_once_with(action_module.api_object, data="")

    def test_configure_mo_api_minimal(self, action_module):
        """Test managed object API configuration with minimal parameters."""
        mock_dme_request = MagicMock()
        mock_dme_request.get.return_value = (200, MOCK_MO_RESPONSE)

        read_dn = {"entry": "sys/intf/phys-[eth1/1]"}

        api_response, code = action_module.configure_mo_api(mock_dme_request, read_dn)

        assert api_response == MOCK_MO_RESPONSE
        assert code == 200
        assert action_module.api_object == "/api/mo/sys/intf/phys-[eth1/1].json"

    def test_configure_mo_api_missing_entry(self, action_module):
        """Test managed object API configuration with missing entry."""
        mock_dme_request = MagicMock()
        read_dn = {}

        with pytest.raises(ValueError, match="DN entry is required"):
            action_module.configure_mo_api(mock_dme_request, read_dn)

    def test_configure_mo_api_single_param(self, action_module):
        """Test managed object API configuration with single parameter."""
        mock_dme_request = MagicMock()
        mock_dme_request.get.return_value = (200, MOCK_MO_RESPONSE)

        read_dn = {"entry": "sys/intf/phys-[eth1/1]", "rsp_prop_include": "config-only"}

        api_response, code = action_module.configure_mo_api(mock_dme_request, read_dn)

        expected_url = (
            "/api/mo/sys/intf/phys-[eth1/1].json?rsp-prop-include=config-only"
        )
        assert action_module.api_object == expected_url

    @patch("ansible_collections.cisco.dme.plugins.action.dme_command.Connection")
    @patch("ansible_collections.cisco.dme.plugins.action.dme_command.DmeRequest")
    def test_run_with_read_class(
        self, mock_dme_request_class, mock_connection_class, action_module
    ):
        """Test run method with read_class parameter."""
        # Setup mocks
        mock_connection = MagicMock()
        mock_connection_class.return_value = mock_connection

        mock_dme_request = MagicMock()
        mock_dme_request_class.return_value = mock_dme_request
        mock_dme_request.get.return_value = (200, MOCK_CLASS_RESPONSE)

        # Setup task args
        action_module._task.args = {
            "read_class": {"entry": "ipv4aclACL", "rsp_prop_include": "config-only"}
        }

        # Mock parent run method
        with patch.object(ActionBase, "run", return_value={}):
            with patch.object(action_module, "_check_argspec"):
                result = action_module.run(task_vars={"test": "vars"})

        # Verify results
        assert result["changed"] == 200  # This is the HTTP code from the mock
        assert result["class"] == MOCK_CLASS_RESPONSE
        assert not result.get("failed", False)

        # Verify DmeRequest was created properly
        mock_dme_request_class.assert_called_once_with(
            connection=mock_connection, task_vars={"test": "vars"}
        )

    @patch("ansible_collections.cisco.dme.plugins.action.dme_command.Connection")
    @patch("ansible_collections.cisco.dme.plugins.action.dme_command.DmeRequest")
    def test_run_with_read_dn(
        self, mock_dme_request_class, mock_connection_class, action_module
    ):
        """Test run method with read_dn parameter."""
        # Setup mocks
        mock_connection = MagicMock()
        mock_connection_class.return_value = mock_connection

        mock_dme_request = MagicMock()
        mock_dme_request_class.return_value = mock_dme_request
        mock_dme_request.get.return_value = (200, MOCK_MO_RESPONSE)

        # Setup task args
        action_module._task.args = {
            "read_dn": {"entry": "sys/intf/phys-[eth1/1]", "rsp_subtree": "full"}
        }

        # Mock parent run method
        with patch.object(ActionBase, "run", return_value={}):
            with patch.object(action_module, "_check_argspec"):
                result = action_module.run(task_vars={"test": "vars"})

        # Verify results
        assert result["changed"] == 200
        assert result["mo"] == MOCK_MO_RESPONSE
        assert not result.get("failed", False)

    @patch("ansible_collections.cisco.dme.plugins.action.dme_command.Connection")
    @patch("ansible_collections.cisco.dme.plugins.action.dme_command.DmeRequest")
    def test_run_with_both_parameters(
        self, mock_dme_request_class, mock_connection_class, action_module
    ):
        """Test run method with both read_class and read_dn parameters."""
        # Setup mocks
        mock_connection = MagicMock()
        mock_connection_class.return_value = mock_connection

        mock_dme_request = MagicMock()
        mock_dme_request_class.return_value = mock_dme_request
        mock_dme_request.get.side_effect = [
            (200, MOCK_CLASS_RESPONSE),
            (200, MOCK_MO_RESPONSE),
        ]

        # Setup task args
        action_module._task.args = {
            "read_class": {"entry": "ipv4aclACL"},
            "read_dn": {"entry": "sys/intf/phys-[eth1/1]"},
        }

        # Mock parent run method
        with patch.object(ActionBase, "run", return_value={}):
            with patch.object(action_module, "_check_argspec"):
                result = action_module.run()

        # Verify results
        assert result["class"] == MOCK_CLASS_RESPONSE
        assert result["mo"] == MOCK_MO_RESPONSE
        assert mock_dme_request.get.call_count == 2

    @patch("ansible_collections.cisco.dme.plugins.action.dme_command.Connection")
    @patch("ansible_collections.cisco.dme.plugins.action.dme_command.DmeRequest")
    def test_run_with_argspec_failure(
        self, mock_dme_request_class, mock_connection_class, action_module
    ):
        """Test run method when argument specification validation fails."""
        action_module._task.args = {"invalid": "args"}

        # Mock parent run method
        with patch.object(ActionBase, "run", return_value={}):
            with patch.object(action_module, "_check_argspec") as mock_check:
                mock_check.side_effect = lambda: setattr(
                    action_module, "_result", {"failed": True, "msg": "Invalid args"}
                )

                result = action_module.run()

        # Verify that the method returns early on argspec failure
        assert result["failed"] is True
        assert result["msg"] == "Invalid args"
        mock_dme_request_class.assert_not_called()

    # def test_supports_check_mode(self, action_module):
    #     """Test that check mode is not supported."""
    #     with patch.object(ActionBase, "run", return_value={}):
    #         with patch.object(action_module, "_check_argspec"):
    #             action_module.run()

    #     assert action_module._supports_check_mode is False

    def test_api_object_construction_edge_cases(self, action_module):
        """Test API object construction with edge cases."""
        mock_dme_request = MagicMock()
        mock_dme_request.get.return_value = (200, MOCK_MO_RESPONSE)

        # Test with empty string values (should be handled gracefully)
        read_dn = {
            "entry": "sys/intf/phys-[eth1/1]",
            "rsp_prop_include": "",
            "rsp_subtree": "full",
            "query_target": "",
            "target_subtree_class": "topSystem",
        }

        api_response, code = action_module.configure_mo_api(mock_dme_request, read_dn)

        # Empty parameters should not be included in URL
        expected_url = "/api/mo/sys/intf/phys-[eth1/1].json?rsp-subtree=full&target-subtree-class=topSystem"
        assert action_module.api_object == expected_url
