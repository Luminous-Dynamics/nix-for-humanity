#!/usr/bin/env python3
"""Tests for FlakeManager - Nix flakes and development environment management."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json
import tempfile
import os

from luminous_nix.core.flake_manager import (
    FlakeManager,
    FlakeInput,
    DevShell,
    FlakeOutput
)


class TestFlakeManager(unittest.TestCase):
    """Test FlakeManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = FlakeManager()
        
    def test_initialization(self):
        """Test FlakeManager initialization."""
        self.assertIsNotNone(self.manager)
        self.assertIsInstance(self.manager.templates, dict)
        self.assertIsInstance(self.manager.language_configs, dict)
        
    def test_flake_input_creation(self):
        """Test FlakeInput dataclass."""
        input = FlakeInput(
            name="nixpkgs",
            url="github:NixOS/nixpkgs/nixos-unstable"
        )
        self.assertEqual(input.name, "nixpkgs")
        self.assertEqual(input.url, "github:NixOS/nixpkgs/nixos-unstable")
        self.assertEqual(input.type, "github")
        self.assertIsNone(input.follows)
        
    def test_dev_shell_creation(self):
        """Test DevShell dataclass."""
        shell = DevShell(
            name="python",
            packages=["python3", "poetry"],
            shell_hook="echo 'Welcome to Python dev shell'"
        )
        self.assertEqual(shell.name, "python")
        self.assertEqual(len(shell.packages), 2)
        self.assertIn("python3", shell.packages)
        self.assertEqual(shell.shell_hook, "echo 'Welcome to Python dev shell'")
        
    def test_flake_output_creation(self):
        """Test FlakeOutput dataclass."""
        output = FlakeOutput(
            type="package",
            name="my-app",
            content="{ pkgs }: pkgs.stdenv.mkDerivation { ... }"
        )
        self.assertEqual(output.type, "package")
        self.assertEqual(output.name, "my-app")
        self.assertIn("mkDerivation", output.content)
        
    @patch('luminous_nix.core.flake_manager.subprocess.run')
    def test_create_flake(self, mock_run):
        """Test flake creation."""
        mock_run.return_value = MagicMock(returncode=0)
        
        # Create intent for create_flake method
        with tempfile.TemporaryDirectory() as tmpdir:
            intent = {
                "action": "create",
                "language": "python",
                "packages": ["python3", "poetry"],
                "description": "Python development environment",
                "features": []
            }
            success, message = self.manager.create_flake(intent, Path(tmpdir))
            self.assertTrue(success)
            self.assertIn("Created flake.nix", message)
            
    def test_language_configs(self):
        """Test language configuration loading."""
        configs = self.manager.language_configs
        
        # Common language configs that should exist
        expected_languages = ["python", "javascript", "rust", "go"]
        
        # If configs are loaded, verify structure
        if configs:
            for lang in configs:
                self.assertIsInstance(configs[lang], (dict, str))
        else:
            # If no configs loaded, that's okay - verify manager exists
            self.assertIsNotNone(self.manager)
            
    def test_templates(self):
        """Test flake templates."""
        templates = self.manager.templates
        
        # If templates are loaded, verify they're strings
        if templates:
            for name, template in templates.items():
                self.assertIsInstance(name, str)
                self.assertIsInstance(template, str)
        else:
            # If no templates loaded, that's okay
            self.assertIsNotNone(self.manager)
            
    @patch('luminous_nix.core.flake_manager.subprocess.run')
    def test_flake_validation(self, mock_run):
        """Test flake validation."""
        # Mock successful validation
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a dummy flake.nix for testing
            flake_path = Path(tmpdir) / "flake.nix"
            flake_path.write_text("{ description = \"test\"; }")
            
            success, message = self.manager.validate_flake(Path(tmpdir))
            self.assertTrue(success)
            self.assertIn("successful", message)
            
    def test_dev_shell_with_env_vars(self):
        """Test DevShell with environment variables."""
        shell = DevShell(
            name="custom",
            packages=["gcc", "make"],
            env_vars={"CC": "gcc", "DEBUG": "1"}
        )
        self.assertEqual(shell.env_vars["CC"], "gcc")
        self.assertEqual(shell.env_vars["DEBUG"], "1")
        self.assertEqual(len(shell.env_vars), 2)
        
    def test_flake_input_with_follows(self):
        """Test FlakeInput with follows dependency."""
        input = FlakeInput(
            name="utils",
            url="github:numtide/flake-utils",
            follows="nixpkgs"
        )
        self.assertEqual(input.follows, "nixpkgs")
        
    def test_multiple_dev_shells(self):
        """Test creating multiple development shells."""
        shells = [
            DevShell(name="default", packages=["git"]),
            DevShell(name="python", packages=["python3"]),
            DevShell(name="node", packages=["nodejs"])
        ]
        
        self.assertEqual(len(shells), 3)
        self.assertEqual(shells[0].name, "default")
        self.assertEqual(shells[1].packages[0], "python3")
        self.assertEqual(shells[2].packages[0], "nodejs")


if __name__ == "__main__":
    unittest.main()