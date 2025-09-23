# -*- coding: utf-8 -*-
# Copyright 2025 Sagar Paul (@KB-perByte)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for action.dme_config plugin."""

from unittest.mock import MagicMock, patch

import pytest
from ansible.plugins.action import ActionBase
from ansible_collections.cisco.dme.plugins.action.dme_config import ActionModule
from ansible_collections.cisco.dme.tests.unit.fixtures.dme_responses import (
    MOCK_CONFIG_SUCCESS_RESPONSE,
)


class TestDmeConfigAction:
    """Test cases for DME config action plugin."""

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
        assert action_module.api_object == "/api/mo/sys.json"

    def test_check_argspec_valid(self, action_module):
        """Test argument specification validation with valid args."""
        action_module._task.args = {
            "config": {
                "topSystem": {
                    "children": [
                        {
                            "interfaceEntity": {
                                "children": [
                                    {
                                        "l1PhysIf": {
                                            "attributes": {
                                                "descr": "Test description",
                                                "id": "eth1/2",
                                            },
                                        },
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
        }
        action_module._result = {}

        with patch(
            "ansible_collections.cisco.dme.plugins.action.dme_config.AnsibleArgSpecValidator",
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
            "ansible_collections.cisco.dme.plugins.action.dme_config.AnsibleArgSpecValidator",
        ) as mock_validator:
            mock_validator.return_value.validate.return_value = (
                False,
                ["Missing required parameter: config"],
                {},
            )

            action_module._check_argspec()

            assert action_module._result["failed"] is True
            assert action_module._result["msg"] == [
                "Missing required parameter: config",
            ]

    def test_configure_module_api_success(self, action_module):
        """Test successful configuration API call."""
        mock_dme_request = MagicMock()
        mock_dme_request.post.return_value = (200, MOCK_CONFIG_SUCCESS_RESPONSE)

        payload = {
            "topSystem": {
                "children": [
                    {
                        "interfaceEntity": {
                            "children": [
                                {
                                    "l1PhysIf": {
                                        "attributes": {
                                            "descr": "Test description",
                                            "id": "eth1/2",
                                        },
                                    },
                                },
                            ],
                        },
                    },
                ],
            },
        }

        api_response, changed = action_module.configure_module_api(
            mock_dme_request,
            payload,
        )

        assert api_response == MOCK_CONFIG_SUCCESS_RESPONSE
        assert changed is True
        mock_dme_request.post.assert_called_once_with(
            action_module.api_object,
            data=payload,
        )

    def test_configure_module_api_empty_payload(self, action_module):
        """Test configuration API call with empty payload."""
        mock_dme_request = MagicMock()

        with pytest.raises(ValueError, match="Configuration payload is required"):
            action_module.configure_module_api(mock_dme_request, None)

    def test_configure_module_api_empty_dict_payload(self, action_module):
        """Test configuration API call with empty dictionary payload."""
        mock_dme_request = MagicMock()

        with pytest.raises(ValueError, match="Configuration payload is required"):
            action_module.configure_module_api(mock_dme_request, {})

    @patch("ansible_collections.cisco.dme.plugins.action.dme_config.Connection")
    @patch("ansible_collections.cisco.dme.plugins.action.dme_config.DmeRequest")
    def test_run_success(
        self,
        mock_dme_request_class,
        mock_connection_class,
        action_module,
    ):
        """Test successful run method execution."""
        # Setup mocks
        mock_connection = MagicMock()
        mock_connection_class.return_value = mock_connection

        mock_dme_request = MagicMock()
        mock_dme_request_class.return_value = mock_dme_request
        mock_dme_request.post.return_value = (200, MOCK_CONFIG_SUCCESS_RESPONSE)

        # Setup task args
        config_payload = {
            "topSystem": {
                "children": [
                    {
                        "interfaceEntity": {
                            "children": [
                                {
                                    "l1PhysIf": {
                                        "attributes": {
                                            "descr": "Test description",
                                            "id": "eth1/2",
                                        },
                                    },
                                },
                            ],
                        },
                    },
                ],
            },
        }
        action_module._task.args = {"config": config_payload}

        # Mock parent run method
        with patch.object(ActionBase, "run", return_value={}):
            with patch.object(action_module, "_check_argspec"):
                result = action_module.run(task_vars={"test": "vars"})

        # Verify results
        assert result["changed"] is True
        assert result["dme_response"] == MOCK_CONFIG_SUCCESS_RESPONSE
        assert not result.get("failed", False)

        # Verify DmeRequest was created properly
        mock_dme_request_class.assert_called_once_with(
            connection=mock_connection,
            task_vars={"test": "vars"},
        )
        mock_dme_request.post.assert_called_once_with(
            "/api/mo/sys.json",
            data=config_payload,
        )

    @patch("ansible_collections.cisco.dme.plugins.action.dme_config.Connection")
    @patch("ansible_collections.cisco.dme.plugins.action.dme_config.DmeRequest")
    def test_run_no_config(
        self,
        mock_dme_request_class,
        mock_connection_class,
        action_module,
    ):
        """Test run method without config parameter."""
        # Setup mocks
        mock_connection = MagicMock()
        mock_connection_class.return_value = mock_connection

        mock_dme_request = MagicMock()
        mock_dme_request_class.return_value = mock_dme_request

        # Setup task args without config
        action_module._task.args = {}

        # Mock parent run method
        with patch.object(ActionBase, "run", return_value={}):
            with patch.object(action_module, "_check_argspec"):
                result = action_module.run()

        # Verify results - should not call configure_module_api
        assert result["changed"] is False
        assert "dme_response" not in result
        mock_dme_request.post.assert_not_called()

    @patch("ansible_collections.cisco.dme.plugins.action.dme_config.Connection")
    @patch("ansible_collections.cisco.dme.plugins.action.dme_config.DmeRequest")
    def test_run_with_argspec_failure(
        self,
        mock_dme_request_class,
        mock_connection_class,
        action_module,
    ):
        """Test run method when argument specification validation fails."""
        action_module._task.args = {"invalid": "args"}

        # Mock parent run method
        with patch.object(ActionBase, "run", return_value={}):
            with patch.object(action_module, "_check_argspec") as mock_check:
                mock_check.side_effect = lambda: setattr(
                    action_module,
                    "_result",
                    {"failed": True, "msg": "Invalid args"},
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

    def test_api_object_constant(self, action_module):
        """Test that API object is correctly set to sys endpoint."""
        assert action_module.api_object == "/api/mo/sys.json"

    @patch("ansible_collections.cisco.dme.plugins.action.dme_config.Connection")
    @patch("ansible_collections.cisco.dme.plugins.action.dme_config.DmeRequest")
    def test_run_with_complex_config(
        self,
        mock_dme_request_class,
        mock_connection_class,
        action_module,
    ):
        """Test run method with complex configuration payload."""
        # Setup mocks
        mock_connection = MagicMock()
        mock_connection_class.return_value = mock_connection

        mock_dme_request = MagicMock()
        mock_dme_request_class.return_value = mock_dme_request
        mock_dme_request.post.return_value = (200, MOCK_CONFIG_SUCCESS_RESPONSE)

        # Setup complex configuration
        complex_config = {
            "topSystem": {
                "children": [
                    {
                        "interfaceEntity": {
                            "children": [
                                {
                                    "l1PhysIf": {
                                        "attributes": {
                                            "descr": "Test interface",
                                            "id": "eth1/1",
                                            "adminSt": "up",
                                            "speed": "10000",
                                            "mtu": "9000",
                                        },
                                    },
                                },
                                {
                                    "l1PhysIf": {
                                        "attributes": {
                                            "descr": "Another test interface",
                                            "id": "eth1/2",
                                            "adminSt": "down",
                                        },
                                    },
                                },
                            ],
                        },
                    },
                    {
                        "bgpEntity": {
                            "children": [
                                {
                                    "bgpInst": {
                                        "attributes": {
                                            "adminSt": "enabled",
                                            "asn": "65001",
                                        },
                                    },
                                },
                            ],
                        },
                    },
                ],
            },
        }

        action_module._task.args = {"config": complex_config}

        # Mock parent run method
        with patch.object(ActionBase, "run", return_value={}):
            with patch.object(action_module, "_check_argspec"):
                result = action_module.run()

        # Verify the complex config was passed correctly
        assert result["changed"] is True
        mock_dme_request.post.assert_called_once_with(
            "/api/mo/sys.json",
            data=complex_config,
        )

    def test_configure_module_api_with_list_payload(self, action_module):
        """Test configuration API call with list payload (should still work)."""
        mock_dme_request = MagicMock()
        mock_dme_request.post.return_value = (200, MOCK_CONFIG_SUCCESS_RESPONSE)

        # Some configurations might be passed as lists
        payload = [
            {
                "topSystem": {
                    "children": [
                        {
                            "interfaceEntity": {
                                "children": [
                                    {
                                        "l1PhysIf": {
                                            "attributes": {
                                                "descr": "Test description",
                                                "id": "eth1/2",
                                            },
                                        },
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
        ]

        api_response, changed = action_module.configure_module_api(
            mock_dme_request,
            payload,
        )

        assert api_response == MOCK_CONFIG_SUCCESS_RESPONSE
        assert changed is True
        mock_dme_request.post.assert_called_once_with(
            action_module.api_object,
            data=payload,
        )
