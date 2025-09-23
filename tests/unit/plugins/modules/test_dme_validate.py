# -*- coding: utf-8 -*-
# Copyright 2025 Sagar Paul (@KB-perByte)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for modules.dme_validate module."""

import pytest
from ansible_collections.cisco.dme.plugins.modules import dme_validate


class TestDmeValidateModule:
    """Test cases for DME validate module."""

    def test_module_documentation(self):
        """Test that module has proper documentation."""
        assert hasattr(dme_validate, "DOCUMENTATION")
        assert dme_validate.DOCUMENTATION is not None
        assert "module: dme_validate" in dme_validate.DOCUMENTATION
        assert "short_description:" in dme_validate.DOCUMENTATION
        assert "description:" in dme_validate.DOCUMENTATION
        assert "version_added:" in dme_validate.DOCUMENTATION
        assert "options:" in dme_validate.DOCUMENTATION
        assert "author:" in dme_validate.DOCUMENTATION

    def test_module_examples(self):
        """Test that module has examples."""
        assert hasattr(dme_validate, "EXAMPLES")
        assert dme_validate.EXAMPLES is not None
        assert "cisco.dme.dme_validate:" in dme_validate.EXAMPLES

    def test_module_return_documentation(self):
        """Test that module has return documentation."""
        assert hasattr(dme_validate, "RETURN")
        assert dme_validate.RETURN is not None
        assert "errors:" in dme_validate.RETURN
        assert "model:" in dme_validate.RETURN
        assert "valid:" in dme_validate.RETURN
        assert "changed:" in dme_validate.RETURN

    def test_module_options_structure(self):
        """Test that module documentation contains expected options."""
        doc = dme_validate.DOCUMENTATION
        assert "lines:" in doc
        assert "parents:" in doc
        assert "src:" in doc

    def test_module_metadata(self):
        """Test module metadata."""
        assert hasattr(dme_validate, "__metaclass__")
        assert dme_validate.__metaclass__ == type

    def test_module_imports(self):
        """Test that module has proper imports."""
        # The module should be importable without errors
        from ansible_collections.cisco.dme.plugins.modules import (
            dme_validate as imported_module,
        )

        assert imported_module is not None

    def test_documentation_yaml_structure(self):
        """Test that documentation follows YAML structure."""
        import yaml

        try:
            doc_dict = yaml.safe_load(dme_validate.DOCUMENTATION)
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
            examples_list = yaml.safe_load_all(dme_validate.EXAMPLES)
            examples = list(examples_list)
            assert len(examples) > 0
        except yaml.YAMLError as e:
            pytest.fail(f"Examples are not valid YAML: {e}")

    def test_return_yaml_structure(self):
        """Test that return documentation follows YAML structure."""
        import yaml

        try:
            return_dict = yaml.safe_load(dme_validate.RETURN)
            assert isinstance(return_dict, dict)
            assert "errors" in return_dict
            assert "model" in return_dict
            assert "valid" in return_dict
            assert "changed" in return_dict
        except yaml.YAMLError as e:
            pytest.fail(f"Return documentation is not valid YAML: {e}")

    def test_lines_option_structure(self):
        """Test that lines option is properly documented."""
        import yaml

        doc_dict = yaml.safe_load(dme_validate.DOCUMENTATION)
        lines_option = doc_dict["options"]["lines"]

        assert lines_option["type"] == "list"
        assert lines_option["elements"] == "str"
        assert "aliases" in lines_option
        assert "commands" in lines_option["aliases"]

    def test_parents_option_structure(self):
        """Test that parents option is properly documented."""
        import yaml

        doc_dict = yaml.safe_load(dme_validate.DOCUMENTATION)
        parents_option = doc_dict["options"]["parents"]

        assert parents_option["type"] == "list"
        assert parents_option["elements"] == "str"

    def test_src_option_structure(self):
        """Test that src option is properly documented."""
        import yaml

        doc_dict = yaml.safe_load(dme_validate.DOCUMENTATION)
        src_option = doc_dict["options"]["src"]

        assert src_option["type"] == "str"
        assert "mutually exclusive" in src_option["description"]

    def test_module_version_added(self):
        """Test that version_added is specified."""
        import yaml

        doc_dict = yaml.safe_load(dme_validate.DOCUMENTATION)
        assert "version_added" in doc_dict
        assert doc_dict["version_added"] == "1.0.0"

    def test_module_author(self):
        """Test that author is specified."""
        import yaml

        doc_dict = yaml.safe_load(dme_validate.DOCUMENTATION)
        assert "author" in doc_dict
        assert "Sagar Paul" in doc_dict["author"]
        assert "@KB-perByte" in doc_dict["author"]

    def test_examples_show_success_and_failure(self):
        """Test that examples show both success and failure cases."""
        examples = dme_validate.EXAMPLES
        # Should show successful validation
        assert "valid: true" in examples
        # Should show failed validation
        assert "valid: false" in examples
        assert "errors:" in examples

    def test_examples_contain_realistic_commands(self):
        """Test that examples contain realistic network commands."""
        examples = dme_validate.EXAMPLES
        assert "interface Ethernet" in examples
        assert "description" in examples
        assert "no speed" in examples
        assert "duplex full" in examples
        assert "mtu" in examples

    def test_examples_show_error_scenarios(self):
        """Test that examples show error scenarios."""
        examples = dme_validate.EXAMPLES
        assert "Intentional Mistake" in examples
        assert "idescription" in examples  # Invalid command
        assert "ip forwarding" in examples  # Another invalid command

    def test_return_documentation_completeness(self):
        """Test that return documentation is complete."""
        import yaml

        return_dict = yaml.safe_load(dme_validate.RETURN)

        expected_keys = ["errors", "model", "valid", "changed"]
        for key in expected_keys:
            assert key in return_dict
            assert "description" in return_dict[key]
            assert "returned" in return_dict[key]
            assert "type" in return_dict[key]
            assert "sample" in return_dict[key]

    def test_mutual_exclusivity_documented(self):
        """Test that mutual exclusivity is properly documented."""
        import yaml

        doc_dict = yaml.safe_load(dme_validate.DOCUMENTATION)
        src_desc = doc_dict["options"]["src"]["description"]
        assert "mutually exclusive" in src_desc
        assert "lines" in src_desc
        assert "parents" in src_desc

    def test_idempotency_mentioned(self):
        """Test that idempotency requirements are mentioned."""
        import yaml

        doc_dict = yaml.safe_load(dme_validate.DOCUMENTATION)
        lines_desc = doc_dict["options"]["lines"]["description"]
        assert "idempotency" in lines_desc

    def test_examples_show_dme_model_output(self):
        """Test that examples show DME model output structure."""
        examples = dme_validate.EXAMPLES
        assert "topSystem:" in examples
        assert "children:" in examples
        assert "aclEntity:" in examples or "interfaceEntity:" in examples
        assert "attributes:" in examples

    def test_module_short_description(self):
        """Test module short description is appropriate."""
        import yaml

        doc_dict = yaml.safe_load(dme_validate.DOCUMENTATION)
        short_desc = doc_dict["short_description"]
        assert "validate" in short_desc.lower()
        assert "convert" in short_desc.lower()
        assert "configuration" in short_desc.lower()

    def test_module_description_detail(self):
        """Test module description provides sufficient detail."""
        import yaml

        doc_dict = yaml.safe_load(dme_validate.DOCUMENTATION)
        description = doc_dict["description"]
        assert "validate" in description.lower()
        assert "converts" in description.lower()
        assert "configuration" in description.lower()

    def test_examples_show_register_usage(self):
        """Test that examples show how to register and use results."""
        examples = dme_validate.EXAMPLES
        assert "register:" in examples
        assert "result_validation" in examples

    def test_configuration_syntax_warning(self):
        """Test that configuration syntax warnings are present."""
        import yaml

        doc_dict = yaml.safe_load(dme_validate.DOCUMENTATION)
        lines_desc = doc_dict["options"]["lines"]["description"]
        assert "exact same commands" in lines_desc
        assert "device running-config" in lines_desc

    def test_file_path_handling_documented(self):
        """Test that file path handling is documented for src option."""
        import yaml

        doc_dict = yaml.safe_load(dme_validate.DOCUMENTATION)
        src_desc = doc_dict["options"]["src"]["description"]
        assert "full path" in src_desc
        assert "relative path" in src_desc
        assert "playbook" in src_desc or "role" in src_desc
