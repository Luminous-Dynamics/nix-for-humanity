#!/usr/bin/env python3
"""
Comprehensive tests for NixOS configuration generation.
Tests both natural language processing and configuration output.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from luminous_nix.core.config_generator import (
    ConfigSection,
    NixConfigGenerator,
    NixModule,
)


@pytest.mark.integration
class TestBasicConfigGenerator:
    """Test the basic template-based configuration generator."""

    def setup_method(self):
        """Setup test environment."""
        self.generator = NixConfigGenerator()

    def test_parse_desktop_intent(self):
        """Test parsing desktop environment requests."""
        intents = [
            ("I want GNOME desktop", ["desktop.gnome"]),
            ("Set up KDE Plasma", ["desktop.kde"]),
            ("Install a desktop with GNOME", ["desktop.gnome"]),
        ]

        for query, expected_modules in intents:
            intent = self.generator.parse_intent(query)
            assert intent["modules"] == expected_modules

    def test_parse_server_intent(self):
        """Test parsing server configuration requests."""
        intents = [
            ("Set up nginx web server", ["web.nginx"]),
            ("I need Apache", ["web.apache"]),
            ("Configure PostgreSQL database", ["db.postgresql"]),
            ("Install MySQL server", ["db.mysql"]),
        ]

        for query, expected_modules in intents:
            intent = self.generator.parse_intent(query)
            assert intent["modules"] == expected_modules

    def test_parse_development_intent(self):
        """Test parsing development environment requests."""
        intent = self.generator.parse_intent(
            "Set up development environment with Docker and VSCode"
        )
        assert "dev.docker" in intent["modules"]
        assert "dev.vscode" in intent["modules"]

    def test_parse_user_creation(self):
        """Test parsing user creation requests."""
        queries = [
            ("Add user john", "john", False),
            ("Create admin user alice", "alice", True),
            ("Add user bob with sudo access", "bob", True),
        ]

        for query, expected_name, expected_admin in queries:
            intent = self.generator.parse_intent(query)
            assert len(intent["users"]) == 1
            assert intent["users"][0]["name"] == expected_name
            assert intent["users"][0]["admin"] == expected_admin

    def test_parse_packages(self):
        """Test parsing package installation requests."""
        intent = self.generator.parse_intent(
            "Install firefox, git, and development tools"
        )
        assert "firefox" in intent["packages"]
        assert "git" in intent["packages"]
        # Development tools should expand to multiple packages
        assert "vim" in intent["packages"]
        assert "tmux" in intent["packages"]

    def test_conflict_detection(self):
        """Test that conflicting modules are detected."""
        # GNOME and KDE conflict
        conflicts = self.generator.check_conflicts(["desktop.gnome", "desktop.kde"])
        assert len(conflicts) == 1
        assert ("desktop.gnome", "desktop.kde") in conflicts

        # Nginx and Apache conflict
        conflicts = self.generator.check_conflicts(["web.nginx", "web.apache"])
        assert len(conflicts) == 1

    def test_generate_basic_config(self):
        """Test generating a basic configuration."""
        intent = {
            "modules": ["desktop.gnome"],
            "packages": ["firefox", "git"],
            "users": [{"name": "testuser", "admin": True}],
            "settings": {"hostname": "test-nixos"},
            "action": "generate",
        }

        config = self.generator.generate_config(intent)

        # Check that config contains expected elements
        assert "boot.loader" in config
        assert "services.xserver.desktopManager.gnome.enable = true" in config
        assert "firefox" in config
        assert "git" in config
        assert 'users.users.testuser' in config
        assert '"wheel"' in config  # Admin group
        assert 'networking.hostName = "test-nixos"' in config

    def test_generate_web_server_config(self):
        """Test generating a web server configuration."""
        intent = self.generator.parse_intent(
            "Create a web server with nginx and postgresql"
        )
        config = self.generator.generate_config(intent)

        assert "services.nginx.enable = true" in config
        assert "services.postgresql.enable = true" in config

    def test_config_formatting(self):
        """Test that configurations are properly formatted."""
        test_config = {
            "test.bool": True,
            "test.string": "value",
            "test.number": 42,
            "test.list": ["item1", "item2"],
            "test.package": "pkgs.firefox",
        }

        formatted = self.generator._format_config(test_config, indent=1)

        assert "  test.bool = true;" in formatted
        assert '  test.string = "value";' in formatted
        assert "  test.number = 42;" in formatted
        assert '  test.list = [ "item1" "item2" ];' in formatted
        assert "  test.package = pkgs.firefox;" in formatted

    def test_save_config_with_backup(self):
        """Test saving configuration with backup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test.nix"
            
            # Write initial config
            config_path.write_text("# Original config")
            
            # Save new config with backup
            success, msg = self.generator.save_config(
                "# New config", str(config_path), backup=True
            )
            
            assert success
            assert config_path.read_text() == "# New config"
            
            # Check that backup was created
            backups = list(Path(tmpdir).glob("*.bak.*"))
            assert len(backups) == 1

    @patch("subprocess.run")
    def test_validate_config(self, mock_run):
        """Test configuration validation."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        valid, msg = self.generator.validate_config("/tmp/test.nix")
        assert valid
        assert "valid" in msg.lower()

        # Test invalid config
        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="syntax error"
        )
        valid, msg = self.generator.validate_config("/tmp/test.nix")
        assert not valid
        assert "error" in msg.lower()

    def test_explain_config(self):
        """Test configuration explanation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.nix', delete=False) as f:
            f.write("""
            {
              boot.loader.systemd-boot.enable = true;
              services.xserver.desktopManager.gnome.enable = true;
              services.nginx.enable = true;
              services.openssh.enable = true;
              networking.firewall.enable = true;
              networking.hostName = "test-system";
            }
            """)
            f.flush()

            explanation = self.generator.explain_config(f.name)

            assert "UEFI boot" in explanation
            assert "GNOME desktop" in explanation
            assert "Nginx web server" in explanation
            assert "SSH remote access" in explanation
            assert "firewall enabled" in explanation
            assert "test-system" in explanation

            Path(f.name).unlink()

    def test_complex_config_generation(self):
        """Test generating complex configurations."""
        queries = [
            "Set up a development workstation with KDE, Docker, and VSCode",
            "Configure a secure web server with nginx, PostgreSQL, and firewall",
            "Create a minimal system with user john and SSH access",
        ]

        for query_text in queries:
            intent = self.generator.parse_intent(query_text)
            config = self.generator.generate_config(intent)

            # Basic validation - config should be non-empty and valid Nix
            assert config
            assert "{ config, pkgs, ... }:" in config
            assert "system.stateVersion" in config

    def test_module_database(self):
        """Test that module database is properly populated."""
        modules = self.generator._load_modules_database()

        # Check essential modules exist
        assert "boot.uefi" in modules
        assert "desktop.gnome" in modules
        assert "web.nginx" in modules
        assert "db.postgresql" in modules
        assert "dev.docker" in modules

        # Check module structure
        for name, module in modules.items():
            assert isinstance(module, NixModule)
            assert module.name
            assert module.config
            assert isinstance(module.config, dict)


@pytest.mark.integration
class TestConfigGenerationIntegration:
    """Integration tests for configuration generation with core system."""

    def setup_method(self):
        """Setup test environment."""
        from luminous_nix.core.luminous_core import LuminousNixCore, Query

        self.core = LuminousNixCore()
        self.generator = NixConfigGenerator()
        self.Query = Query  # Store the class for use in tests

    def test_config_generation_through_core(self):
        """Test configuration generation through the core system."""
        query = self.Query(text="generate config for web server with nginx", dry_run=True)

        # This tests that the core can handle config generation requests
        response = self.core.process_query(query)

        # The response should indicate config generation capability
        assert response is not None
        # Depending on implementation, check for success or appropriate response

    def test_incremental_config_updates(self):
        """Test incrementally updating configurations."""
        # Start with basic config
        intent1 = self.generator.parse_intent("Create basic system")
        config1 = self.generator.generate_config(intent1)

        # Add a service
        intent2 = self.generator.parse_intent("Add nginx to the system")
        intent2["action"] = "modify"
        config2 = self.generator.generate_config(intent2)

        # Configs should be different
        assert config1 != config2

    def test_config_templates(self):
        """Test that all templates are valid."""
        templates = self.generator._load_templates()

        assert "base" in templates
        assert "user" in templates
        assert "service_section" in templates

        # Base template should have placeholders
        base = templates["base"]
        assert "{hostname}" in base
        assert "{timezone}" in base
        assert "{packages}" in base
        assert "{services}" in base


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "-m", "integration"])