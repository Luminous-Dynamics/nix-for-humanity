#!/usr/bin/env python3
"""
Comprehensive tests for Nix flake management feature.
Tests natural language parsing, flake generation, and validation.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from luminous_nix.core.flake_manager import FlakeManager, FlakeTemplate


@pytest.mark.integration
class TestFlakeManager:
    """Test the flake management system."""

    def setup_method(self):
        """Setup test environment."""
        self.manager = FlakeManager()

    def test_parse_python_intent(self):
        """Test parsing Python project descriptions."""
        examples = [
            ("python web app with django", {
                "language": "python",
                "packages": ["django"],
                "frameworks": ["django"],
            }),
            ("python data science with pandas numpy jupyter", {
                "language": "python",
                "packages": ["pandas", "numpy", "jupyter"],
                "features": [],
            }),
            ("python testing project with pytest", {
                "language": "python",
                "packages": ["pytest"],
                "features": ["testing"],
            }),
        ]

        for description, expected in examples:
            intent = self.manager.parse_intent(description)
            assert intent["language"] == expected["language"]
            for pkg in expected["packages"]:
                assert pkg in intent["packages"]
            for framework in expected.get("frameworks", []):
                assert framework in intent["frameworks"]

    def test_parse_nodejs_intent(self):
        """Test parsing Node.js project descriptions."""
        examples = [
            ("nodejs api with express and typescript", {
                "language": "nodejs",
                "packages": ["express"],
                "frameworks": ["express"],
            }),
            ("react app with next.js", {
                "language": "nodejs",
                "packages": [],
                "frameworks": ["next"],
            }),
        ]

        for description, expected in examples:
            intent = self.manager.parse_intent(description)
            assert intent["language"] == expected["language"]
            for framework in expected.get("frameworks", []):
                assert framework in intent["frameworks"]

    def test_parse_rust_intent(self):
        """Test parsing Rust project descriptions."""
        intent = self.manager.parse_intent("rust cli tool with clap and serde")
        assert intent["language"] == "rust"
        assert "clap" in intent["packages"]
        assert "serde" in intent["packages"]

    def test_parse_go_intent(self):
        """Test parsing Go project descriptions."""
        intent = self.manager.parse_intent("go microservice with gin and docker")
        assert intent["language"] == "go"
        assert "gin" in intent["packages"]
        assert "docker" in intent["features"]
        assert "gin" in intent["frameworks"]

    def test_detect_features(self):
        """Test feature detection from descriptions."""
        examples = [
            ("project with testing and linting", ["testing", "linting"]),
            ("app with docker and database", ["docker", "database"]),
            ("code with debugging and formatting", ["debugging", "formatting"]),
        ]

        for description, expected_features in examples:
            intent = self.manager.parse_intent(description)
            for feature in expected_features:
                assert feature in intent["features"]

    def test_detect_tools(self):
        """Test tool detection from descriptions."""
        examples = [
            ("development with vscode and git", ["vscode", "git"]),
            ("project using vim and tmux", ["vim", "tmux"]),
        ]

        for description, expected_tools in examples:
            intent = self.manager.parse_intent(description)
            for tool in expected_tools:
                assert tool in intent["tools"]

    def test_generate_python_flake(self):
        """Test generating Python flake content."""
        intent = {
            "language": "python",
            "packages": ["django", "pytest"],
            "features": ["testing"],
            "tools": ["git"],
            "frameworks": ["django"],
        }

        flake_content = self.manager._generate_flake(intent)

        # Check basic structure
        assert "description = " in flake_content
        assert "inputs = {" in flake_content
        assert "outputs = " in flake_content
        assert "devShells.default" in flake_content

        # Check Python-specific content
        assert "python311" in flake_content
        assert "django" in flake_content
        assert "pytest" in flake_content

    def test_generate_nodejs_flake(self):
        """Test generating Node.js flake content."""
        intent = {
            "language": "nodejs",
            "packages": [],
            "features": [],
            "tools": [],
            "frameworks": ["express"],
        }

        flake_content = self.manager._generate_flake(intent)

        # Check Node.js-specific content
        assert "nodejs_" in flake_content
        assert "npm" in flake_content
        assert "Node.js development environment" in flake_content

    def test_create_flake_in_temp_dir(self):
        """Test creating a flake in a temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            intent = {
                "language": "python",
                "packages": ["flask"],
                "features": [],
                "tools": [],
                "frameworks": ["flask"],
            }

            success, message = self.manager.create_flake(intent, project_path)
            
            assert success
            assert "Created flake.nix" in message
            
            # Check that file was created
            flake_path = project_path / "flake.nix"
            assert flake_path.exists()
            
            # Check content
            with open(flake_path) as f:
                content = f.read()
            assert "flask" in content.lower()

    def test_create_flake_already_exists(self):
        """Test handling when flake already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            flake_path = project_path / "flake.nix"
            
            # Create existing flake
            flake_path.write_text("# Existing flake")
            
            intent = {"language": "python", "packages": [], "features": [], "tools": [], "frameworks": []}
            success, message = self.manager.create_flake(intent, project_path)
            
            assert not success
            assert "already exists" in message

    def test_detect_project_type(self):
        """Test detecting project type from files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # Test Python detection
            (project_path / "requirements.txt").touch()
            assert self.manager._detect_project_type(project_path) == "python"
            
            # Clean up
            (project_path / "requirements.txt").unlink()
            
            # Test Node.js detection
            (project_path / "package.json").touch()
            assert self.manager._detect_project_type(project_path) == "nodejs"
            
            # Clean up
            (project_path / "package.json").unlink()
            
            # Test Rust detection
            (project_path / "Cargo.toml").touch()
            assert self.manager._detect_project_type(project_path) == "rust"

    @patch("subprocess.run")
    def test_validate_flake(self, mock_run):
        """Test flake validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            flake_path = project_path / "flake.nix"
            
            # Test missing flake
            success, message = self.manager.validate_flake(project_path)
            assert not success
            assert "No flake.nix found" in message
            
            # Create flake
            flake_path.write_text("{}")
            
            # Test successful validation
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            success, message = self.manager.validate_flake(project_path)
            assert success
            assert "valid" in message.lower()
            
            # Test failed validation
            mock_run.return_value = MagicMock(returncode=1, stderr="syntax error")
            success, message = self.manager.validate_flake(project_path)
            assert not success
            assert "failed" in message.lower()

    def test_show_flake_info(self):
        """Test showing flake information."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            flake_path = project_path / "flake.nix"
            
            # Test missing flake
            info = self.manager.show_flake_info(project_path)
            assert "No flake.nix found" in info
            
            # Create test flake
            flake_content = """
            {
              description = "Test Python project";
              inputs = {
                nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
                flake-utils.url = "github:numtide/flake-utils";
              };
              outputs = { self, nixpkgs, flake-utils }:
                flake-utils.lib.eachDefaultSystem (system:
                  let
                    pkgs = nixpkgs.legacyPackages.${system};
                  in {
                    devShells.default = pkgs.mkShell {
                      buildInputs = with pkgs; [
                        python311
                        postgresql
                        docker
                      ];
                    };
                  });
            }
            """
            flake_path.write_text(flake_content)
            
            info = self.manager.show_flake_info(project_path)
            assert "Flake Information" in info
            assert "Test Python project" in info
            assert "nixpkgs" in info
            assert "Python" in info
            assert "PostgreSQL" in info
            assert "Docker" in info

    def test_convert_shell_nix_to_flake(self):
        """Test converting shell.nix to flake.nix."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            shell_nix = project_path / "shell.nix"
            
            # Create shell.nix
            shell_content = """
            { pkgs ? import <nixpkgs> {} }:
            pkgs.mkShell {
              buildInputs = with pkgs; [
                python311
                pytest
                black
                git
              ];
            }
            """
            shell_nix.write_text(shell_content)
            
            # Convert
            success, message = self.manager.convert_to_flake(project_path)
            assert success
            assert "Successfully converted" in message
            
            # Check that flake was created
            flake_path = project_path / "flake.nix"
            assert flake_path.exists()
            
            # Check content preservation
            with open(flake_path) as f:
                flake_content = f.read()
            # The detected packages should influence the flake
            assert "python" in flake_content.lower()

    def test_flake_templates(self):
        """Test that all language templates are valid."""
        templates = self.manager.templates
        
        # Check required languages
        assert "python" in templates
        assert "rust" in templates
        assert "nodejs" in templates
        assert "go" in templates
        
        # Check template structure
        for name, template in templates.items():
            assert isinstance(template, FlakeTemplate)
            assert template.name
            assert template.description
            assert template.inputs
            assert template.outputs
            assert isinstance(template.packages, list)
            assert isinstance(template.build_inputs, list)

    def test_complex_project_generation(self):
        """Test generating flakes for complex projects."""
        examples = [
            "python django web app with postgresql redis docker testing and vscode",
            "rust actix web server with diesel tokio and debugging tools",
            "nodejs react app with typescript jest prettier and docker",
            "go gin api with gorm mongodb and continuous integration",
        ]

        for description in examples:
            intent = self.manager.parse_intent(description)
            flake_content = self.manager._generate_flake(intent)
            
            # Basic validation
            assert "{" in flake_content
            assert "}" in flake_content
            assert "description" in flake_content
            assert "inputs" in flake_content
            assert "outputs" in flake_content
            assert intent["language"] in flake_content.lower()


@pytest.mark.integration
class TestFlakeIntegration:
    """Integration tests for flake management with CLI."""

    def setup_method(self):
        """Setup test environment."""
        self.manager = FlakeManager()

    def test_end_to_end_flake_creation(self):
        """Test complete flake creation workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # Simulate natural language input
            description = "python machine learning project with tensorflow pandas jupyter and testing"
            
            # Parse intent
            intent = self.manager.parse_intent(description)
            
            # Verify parsing
            assert intent["language"] == "python"
            assert "tensorflow" in intent["packages"]
            assert "pandas" in intent["packages"]
            assert "jupyter" in intent["packages"]
            assert "testing" in intent["features"]
            
            # Create flake
            success, message = self.manager.create_flake(intent, project_path)
            assert success
            
            # Verify file creation
            flake_path = project_path / "flake.nix"
            assert flake_path.exists()
            
            # Verify content
            with open(flake_path) as f:
                content = f.read()
            
            # Check for expected elements
            assert "machine learning" in content.lower() or "tensorflow" in content.lower()
            assert "pandas" in content
            assert "jupyter" in content

    def test_language_auto_detection(self):
        """Test automatic language detection from project files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # Create Python project indicator
            pyproject = project_path / "pyproject.toml"
            pyproject.write_text("[tool.poetry]\nname = 'test'\n")
            
            # Parse without specifying language
            intent = self.manager.parse_intent("create development environment with testing")
            
            # Language should be detected when creating flake
            success, message = self.manager.create_flake(intent, project_path)
            assert success
            
            # Check that Python was detected
            flake_path = project_path / "flake.nix"
            with open(flake_path) as f:
                content = f.read()
            assert "python" in content.lower()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-m", "integration"])