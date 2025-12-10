# -*- coding: utf-8 -*-
# Copyright 2025 Sagar Paul (@KB-perByte)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for modules.dme_config module."""

import pytest
from ansible_collections.cisco.dme.plugins.modules import dme_config


class TestDmeConfigModule:
    """Test cases for DME config module."""

    def test_module_documentation(self):
        """Test that module has proper documentation."""
        assert hasattr(dme_config, "DOCUMENTATION")
        assert dme_config.DOCUMENTATION is not None
        assert "module: dme_config" in dme_config.DOCUMENTATION
        assert "short_description:" in dme_config.DOCUMENTATION
        assert "description:" in dme_config.DOCUMENTATION
        assert "version_added:" in dme_config.DOCUMENTATION
        assert "options:" in dme_config.DOCUMENTATION
        assert "author:" in dme_config.DOCUMENTATION

    def test_module_examples(self):
        """Test that module has examples."""
        assert hasattr(dme_config, "EXAMPLES")
        assert dme_config.EXAMPLES is not None
        assert "cisco.dme.dme_config:" in dme_config.EXAMPLES

    def test_module_again_examples(self):
        """Test that module has examples."""
        assert hasattr(dme_config, "EXAMPLES")
        assert dme_config.EXAMPLES is not None
        assert "cisco.dme.dme_config:" in dme_config.EXAMPLES
    
    def test_module_return_documentation(self):
        """Test that module has return documentation."""
        assert hasattr(dme_config, "RETURN")
        assert dme_config.RETURN is not None
        assert "before:" in dme_config.RETURN
        assert "after:" in dme_config.RETURN

    def test_module_options_structure(self):
        """Test that module documentation contains expected options."""
        doc = dme_config.DOCUMENTATION
        assert "config:" in doc
        assert "required: true" in doc

    def test_module_metadata(self):
        """Test module metadata."""
        assert hasattr(dme_config, "__metaclass__")
        assert dme_config.__metaclass__ == type

    def test_module_imports(self):
        """Test that module has proper imports."""
        # The module should be importable without errors
        from ansible_collections.cisco.dme.plugins.modules import (
            dme_config as imported_module,
        )

        assert imported_module is not None

    def test_documentation_yaml_structure(self):
        """Test that documentation follows YAML structure."""
        import yaml

        try:
            doc_dict = yaml.safe_load(dme_config.DOCUMENTATION)
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
            examples_list = yaml.safe_load_all(dme_config.EXAMPLES)
            examples = list(examples_list)
            assert len(examples) > 0
        except yaml.YAMLError as e:
            pytest.fail(f"Examples are not valid YAML: {e}")

    def test_return_yaml_structure(self):
        """Test that return documentation follows YAML structure."""
        import yaml

        try:
            return_dict = yaml.safe_load(dme_config.RETURN)
            assert isinstance(return_dict, dict)
            assert "before" in return_dict
            assert "after" in return_dict
        except yaml.YAMLError as e:
            pytest.fail(f"Return documentation is not valid YAML: {e}")

    def test_config_option_required(self):
        """Test that config option is marked as required."""
        import yaml

        doc_dict = yaml.safe_load(dme_config.DOCUMENTATION)
        assert "config" in doc_dict["options"]
        config_option = doc_dict["options"]["config"]
        assert config_option["required"] is True
        assert config_option["type"] == "dict"

    def test_module_version_added(self):
        """Test that version_added is specified."""
        import yaml

        doc_dict = yaml.safe_load(dme_config.DOCUMENTATION)
        assert "version_added" in doc_dict
        assert doc_dict["version_added"] == "1.0.0"

    def test_module_author(self):
        """Test that author is specified."""
        import yaml

        doc_dict = yaml.safe_load(dme_config.DOCUMENTATION)
        assert "author" in doc_dict
        assert "Sagar Paul" in doc_dict["author"]
        assert "@KB-perByte" in doc_dict["author"]

    def test_examples_show_workflow(self):
        """Test that examples show the complete workflow."""
        examples = dme_config.EXAMPLES
        # Should show the complete workflow: command -> validate -> config
        assert "cisco.dme.dme_command:" in examples
        assert "cisco.dme.dme_validate:" in examples
        assert "cisco.dme.dme_config:" in examples
        assert "register: result_validation" in examples
        assert "result_validation.model" in examples

    def test_examples_contain_realistic_config(self):
        """Test that examples contain realistic DME configuration."""
        examples = dme_config.EXAMPLES
        assert "topSystem:" in examples
        assert "children:" in examples
        assert "interfaceEntity:" in examples
        assert "l1PhysIf:" in examples
        assert "attributes:" in examples

    def test_return_documentation_completeness(self):
        """Test that return documentation is complete."""
        import yaml

        return_dict = yaml.safe_load(dme_config.RETURN)

        for key in ["before", "after"]:
            assert key in return_dict
            assert "description" in return_dict[key]
            assert "returned" in return_dict[key]
            assert "type" in return_dict[key]
            assert "sample" in return_dict[key]

    def test_config_description_mentions_validation(self):
        """Test that config description mentions validation requirement."""
        import yaml

        doc_dict = yaml.safe_load(dme_config.DOCUMENTATION)
        config_desc = doc_dict["options"]["config"]["description"]
        assert "validate" in config_desc.lower()
        assert "dme_validate" in config_desc

    def test_examples_show_error_handling(self):
        """Test that examples show proper error handling patterns."""
        examples = dme_config.EXAMPLES
        # Should show validation before configuration
        assert "dme_validate:" in examples
        assert "dme_config:" in examples
        # The validate step should come before config step
        validate_pos = examples.find("dme_validate:")
        config_pos = examples.find("dme_config:")
        assert validate_pos < config_pos

    def test_module_short_description(self):
        """Test module short description is appropriate."""
        import yaml

        doc_dict = yaml.safe_load(dme_config.DOCUMENTATION)
        short_desc = doc_dict["short_description"]
        assert "configuration" in short_desc.lower()
        assert "dme" in short_desc.lower()

    def test_module_description_detail(self):
        """Test module description provides sufficient detail."""
        import yaml

        doc_dict = yaml.safe_load(dme_config.DOCUMENTATION)
        description = doc_dict["description"]
        assert "configuration" in description.lower()
        assert "dme" in description.lower()
        assert "model" in description.lower()
