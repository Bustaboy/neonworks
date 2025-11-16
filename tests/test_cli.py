"""
Comprehensive tests for CLI module

Tests command-line interface functionality and project management.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# ===========================
# CLI Template Tests
# ===========================


class TestCLITemplates:
    """Test CLI template functionality"""

    def test_templates_defined(self):
        """Test that templates are properly defined"""
        # Import templates
        from neonworks import cli

        TEMPLATES = cli.TEMPLATES

        assert "basic_game" in TEMPLATES
        assert "turn_based_rpg" in TEMPLATES

    def test_template_structure(self):
        """Test template data structure"""
        from neonworks import cli

        TEMPLATES = cli.TEMPLATES

        for template_id, template in TEMPLATES.items():
            assert "name" in template
            assert "description" in template
            assert "settings" in template
            assert isinstance(template["settings"], dict)

    def test_template_settings(self):
        """Test template settings are valid"""
        from neonworks import cli

        TEMPLATES = cli.TEMPLATES

        basic_template = TEMPLATES["basic_game"]
        settings = basic_template["settings"]

        assert "window_title" in settings
        assert "window_width" in settings
        assert "window_height" in settings
        assert settings["window_width"] > 0
        assert settings["window_height"] > 0


# ===========================
# CLI Command Tests
# ===========================


class TestCLICommands:
    """Test CLI command functionality"""

    def test_cli_module_imports(self):
        """Test that CLI module can be imported"""
        from neonworks import cli

        assert cli is not None

    def test_templates_constant(self):
        """Test TEMPLATES constant exists"""
        from neonworks import cli

        TEMPLATES = cli.TEMPLATES
        assert isinstance(TEMPLATES, dict)
        assert len(TEMPLATES) > 0

    def test_lazy_import_functions_exist(self):
        """Test lazy import functions are defined"""
        from neonworks import cli

        assert hasattr(cli, "lazy_import_project_module")
        assert hasattr(cli, "lazy_import_validation_module")

    def test_template_basic_game(self):
        """Test basic_game template configuration"""
        from neonworks import cli

        TEMPLATES = cli.TEMPLATES

        template = TEMPLATES["basic_game"]

        assert template["name"] == "Basic Game"
        assert isinstance(template["description"], str)
        assert not template["settings"]["enable_base_building"]
        assert not template["settings"]["enable_survival"]

    def test_template_turn_based_rpg(self):
        """Test turn_based_rpg template configuration"""
        from neonworks import cli

        TEMPLATES = cli.TEMPLATES

        template = TEMPLATES["turn_based_rpg"]

        assert template["name"] == "Turn-Based RPG"
        assert template["settings"]["enable_turn_based"]


# ===========================
# CLI Integration Tests
# ===========================


class TestCLIIntegration:
    """Integration tests for CLI"""

    def test_cli_script_structure(self):
        """Test CLI script has proper structure"""
        cli_path = Path(__file__).parent.parent / "cli.py"

        assert cli_path.exists()

        # Read file and check for main components
        content = cli_path.read_text(encoding="utf-8")

        assert "argparse" in content
        assert "TEMPLATES" in content
        assert "__main__" in content

    def test_all_templates_have_required_fields(self):
        """Test all templates have required configuration"""
        from neonworks import cli

        TEMPLATES = cli.TEMPLATES

        required_settings = [
            "window_title",
            "window_width",
            "window_height",
            "tile_size",
            "grid_width",
            "grid_height",
        ]

        for template_id, template in TEMPLATES.items():
            settings = template["settings"]

            for required_field in required_settings:
                assert (
                    required_field in settings
                ), f"Template {template_id} missing {required_field}"


# ===========================
# Export CLI Tests
# ===========================


class TestExportCLI:
    """Test export CLI functionality"""

    def test_export_cli_exists(self):
        """Test export_cli module exists"""
        export_cli_path = Path(__file__).parent.parent / "export_cli.py"

        assert export_cli_path.exists()

    def test_export_cli_imports(self):
        """Test export_cli can be imported"""
        from neonworks import export_cli

        assert export_cli is not None


# ===========================
# License CLI Tests
# ===========================


class TestLicenseCLI:
    """Test license CLI functionality"""

    def test_license_cli_exists(self):
        """Test license_cli module exists"""
        license_cli_path = Path(__file__).parent.parent / "license_cli.py"

        assert license_cli_path.exists()

    def test_license_cli_imports(self):
        """Test license_cli can be imported"""
        from neonworks import license_cli

        assert license_cli is not None


# ===========================
# Main CLI Tests
# ===========================


class TestMainCLI:
    """Test main CLI functionality"""

    def test_main_cli_exists(self):
        """Test main.py exists"""
        main_path = Path(__file__).parent.parent / "main.py"

        assert main_path.exists()

    def test_main_cli_has_entry_point(self):
        """Test main.py has entry point"""
        main_path = Path(__file__).parent.parent / "main.py"
        content = main_path.read_text(encoding="utf-8")

        assert "__main__" in content or "def main" in content
