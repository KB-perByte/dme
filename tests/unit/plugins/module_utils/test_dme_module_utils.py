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
