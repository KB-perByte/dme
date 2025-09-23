# -*- coding: utf-8 -*-
# Copyright 2025 Sagar Paul (@KB-perByte)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for modules.dme_command module."""

import pytest
from ansible_collections.cisco.dme.plugins.modules import dme_command


class TestDmeCommandModule:
    """Test cases for DME command module."""

    def test_module_documentation(self):
        """Test that module has proper documentation."""
        assert hasattr(dme_command, "DOCUMENTATION")
        assert dme_command.DOCUMENTATION is not None
        assert "module: dme_command" in dme_command.DOCUMENTATION
        assert "short_description:" in dme_command.DOCUMENTATION
        assert "description:" in dme_command.DOCUMENTATION
        assert "version_added:" in dme_command.DOCUMENTATION
        assert "options:" in dme_command.DOCUMENTATION
        assert "author:" in dme_command.DOCUMENTATION

    def test_module_examples(self):
        """Test that module has examples."""
        assert hasattr(dme_command, "EXAMPLES")
        assert dme_command.EXAMPLES is not None
        assert "cisco.dme.dme_command:" in dme_command.EXAMPLES

    # def test_module_return_documentation(self):
    #     """Test that module has return documentation."""
    #     # Note: The current module doesn't have RETURN documentation
    #     # This test documents the current state
    #     assert not hasattr(dme_command, "RETURN")

    def test_module_options_structure(self):
        """Test that module documentation contains expected options."""
        doc = dme_command.DOCUMENTATION
        assert "read_class:" in doc
        assert "read_dn:" in doc
        assert "entry:" in doc
        assert "rsp_prop_include:" in doc

    def test_module_metadata(self):
        """Test module metadata."""
        assert hasattr(dme_command, "__metaclass__")
        assert dme_command.__metaclass__ == type

    def test_module_imports(self):
        """Test that module has proper imports."""
        # The module should be importable without errors
        from ansible_collections.cisco.dme.plugins.modules import (
            dme_command as imported_module,
        )

        assert imported_module is not None

    def test_documentation_yaml_structure(self):
        """Test that documentation follows YAML structure."""
        import yaml

        try:
            doc_dict = yaml.safe_load(dme_command.DOCUMENTATION)
            assert isinstance(doc_dict, dict)
            assert "module" in doc_dict
            assert "short_description" in doc_dict
            assert "description" in doc_dict
            assert "version_added" in doc_dict
            assert "options" in doc_dict
            assert "author" in doc_dict
        except yaml.YAMLError as e:
            pytest.fail(f"Documentation is not valid YAML: {e}")

    def test_examples_yaml_structure(self):
        """Test that examples follow YAML structure."""
        import yaml

        try:
            # Examples should be valid YAML
            examples_list = yaml.safe_load_all(dme_command.EXAMPLES)
            examples = list(examples_list)
            assert len(examples) > 0
        except yaml.YAMLError as e:
            pytest.fail(f"Examples are not valid YAML: {e}")

    def test_module_options_read_class(self):
        """Test read_class option documentation."""
        doc = dme_command.DOCUMENTATION
        assert "read_class:" in doc
        assert "description:" in doc
        assert "type: dict" in doc
        assert "suboptions:" in doc
        assert "entry:" in doc

    def test_module_options_read_dn(self):
        """Test read_dn option documentation."""
        doc = dme_command.DOCUMENTATION
        assert "read_dn:" in doc
        assert "description:" in doc
        assert "type: dict" in doc
        assert "suboptions:" in doc
        assert "entry:" in doc

    def test_module_suboptions(self):
        """Test that suboptions are properly documented."""
        doc = dme_command.DOCUMENTATION
        # Check for common suboptions
        assert "rsp_prop_include:" in doc
        assert "config-only" in doc
        assert "rsp_subtree:" in doc
        assert "full" in doc
        assert "query_target:" in doc
        assert "subtree" in doc
        assert "target_subtree_class:" in doc
        assert "topSystem" in doc

    def test_module_version_added(self):
        """Test that version_added is specified."""
        import yaml

        doc_dict = yaml.safe_load(dme_command.DOCUMENTATION)
        assert "version_added" in doc_dict
        assert doc_dict["version_added"] == "1.0.0"

    def test_module_author(self):
        """Test that author is specified."""
        import yaml

        doc_dict = yaml.safe_load(dme_command.DOCUMENTATION)
        assert "author" in doc_dict
        assert "Sagar Paul" in doc_dict["author"]
        assert "@KB-perByte" in doc_dict["author"]

    def test_module_choices_validation(self):
        """Test that choices are properly defined for options."""
        import yaml

        doc_dict = yaml.safe_load(dme_command.DOCUMENTATION)

        # Check rsp_prop_include choices
        read_class_options = doc_dict["options"]["read_class"]["suboptions"]
        assert "choices" in read_class_options["rsp_prop_include"]
        assert "config-only" in read_class_options["rsp_prop_include"]["choices"]

        read_dn_options = doc_dict["options"]["read_dn"]["suboptions"]
        assert "choices" in read_dn_options["rsp_prop_include"]
        assert "config-only" in read_dn_options["rsp_prop_include"]["choices"]

    def test_examples_contain_required_elements(self):
        """Test that examples contain required elements."""
        examples = dme_command.EXAMPLES
        assert "cisco.dme.dme_command:" in examples
        assert "read_class:" in examples
        assert "read_dn:" in examples
        assert "entry:" in examples
        assert "rsp_prop_include:" in examples

    def test_examples_show_realistic_usage(self):
        """Test that examples show realistic usage patterns."""
        examples = dme_command.EXAMPLES
        # Check for realistic DME class names
        assert "ipv4aclACL" in examples
        # Check for realistic DN paths
        assert "sys/intf/phys-[eth1/1]" in examples
        # Check for realistic response options
        assert "config-only" in examples
        assert "full" in examples
