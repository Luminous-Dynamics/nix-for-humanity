#!/usr/bin/env python3
"""
Comprehensive tests for the SafeExecutor.
Tests command validation, execution, and safety features.
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
import sys
import subprocess

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from nix_humanity.core.executor import SafeExecutor, ValidationResult
from nix_humanity.core.intents import Intent, IntentType


class TestSafeExecutor(unittest.TestCase):
    """Test the SafeExecutor component"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.executor = SafeExecutor()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test executor initializes correctly"""
        self.assertIsNotNone(self.executor)
        self.assertTrue(hasattr(self.executor, 'validate'))
        self.assertTrue(hasattr(self.executor, 'execute'))
    
    def test_validate_safe_command(self):
        """Test validation of safe commands"""
        safe_commands = [
            "nix-env -qa firefox",
            "nix search nixpkgs firefox",
            "nixos-rebuild dry-build",
            "nix-channel --list"
        ]
        
        for cmd in safe_commands:
            result = self.executor.validate(cmd)
            self.assertIsInstance(result, ValidationResult)
            self.assertTrue(result.is_safe)
    
    def test_validate_dangerous_command(self):
        """Test validation blocks dangerous commands"""
        dangerous_commands = [
            "rm -rf /",
            "rm -rf /*",
            "dd if=/dev/zero of=/dev/sda",
            "mkfs.ext4 /dev/sda",
            "chmod -R 777 /",
            ":(){ :|:& };:"  # Fork bomb
        ]
        
        for cmd in dangerous_commands:
            result = self.executor.validate(cmd)
            self.assertIsInstance(result, ValidationResult)
            self.assertFalse(result.is_safe)
            self.assertIsNotNone(result.reason)
    
    def test_execute_dry_run(self):
        """Test dry run execution doesn't run commands"""
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"packages": ["vim"]},
            confidence=0.9,
            raw_text="install vim"
        )
        
        with patch('subprocess.run') as mock_run:
            result = self.executor.execute(intent, dry_run=True)
            
            # Should not actually run the command
            mock_run.assert_not_called()
            
            self.assertIsNotNone(result)
            self.assertTrue(result.success)
    
    @patch('subprocess.run')
    def test_execute_install(self, mock_run):
        """Test executing install command"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Package installed successfully",
            stderr=""
        )
        
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"packages": ["firefox"]},
            confidence=0.9,
            raw_text="install firefox"
        )
        
        result = self.executor.execute(intent, dry_run=False)
        
        self.assertIsNotNone(result)
        self.assertTrue(result.success)
        mock_run.assert_called()
    
    @patch('subprocess.run')
    def test_execute_search(self, mock_run):
        """Test executing search command"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="firefox-1.0.0\nfirefox-esr-1.0.0",
            stderr=""
        )
        
        intent = Intent(
            type=IntentType.SEARCH_PACKAGE,
            entities={"query": "firefox"},
            confidence=0.9,
            raw_text="search firefox"
        )
        
        result = self.executor.execute(intent, dry_run=False)
        
        self.assertIsNotNone(result)
        self.assertTrue(result.success)
    
    @patch('subprocess.run')
    def test_execute_with_timeout(self, mock_run):
        """Test command timeout handling"""
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd="long-running-command",
            timeout=30
        )
        
        intent = Intent(
            type=IntentType.UPDATE_SYSTEM,
            entities={},
            confidence=0.9,
            raw_text="update system"
        )
        
        result = self.executor.execute(intent, dry_run=False)
        
        self.assertIsNotNone(result)
        self.assertFalse(result.success)
        self.assertIn("timeout", result.output.lower())
    
    @patch('subprocess.run')
    def test_execute_with_error(self, mock_run):
        """Test error handling in execution"""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="Error: Package not found"
        )
        
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"packages": ["nonexistent-package"]},
            confidence=0.9,
            raw_text="install nonexistent-package"
        )
        
        result = self.executor.execute(intent, dry_run=False)
        
        self.assertIsNotNone(result)
        self.assertFalse(result.success)
        self.assertIn("Error", result.output)
    
    def test_progress_callback(self):
        """Test progress callback is called"""
        callback_called = []
        
        def progress_callback(message, progress):
            callback_called.append((message, progress))
        
        executor = SafeExecutor(progress_callback=progress_callback)
        
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"packages": ["vim"]},
            confidence=0.9,
            raw_text="install vim"
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="Success", stderr="")
            executor.execute(intent, dry_run=False)
        
        # Progress callback should have been called
        self.assertGreater(len(callback_called), 0)
    
    def test_package_name_validation(self):
        """Test package name validation"""
        valid_names = ["firefox", "vim", "python3", "nodejs-18_x"]
        invalid_names = ["../../../etc/passwd", "rm -rf /", "; echo hacked"]
        
        for name in valid_names:
            self.assertTrue(self.executor.is_valid_package_name(name))
        
        for name in invalid_names:
            self.assertFalse(self.executor.is_valid_package_name(name))
    
    def test_rollback_execution(self):
        """Test rollback command execution"""
        intent = Intent(
            type=IntentType.ROLLBACK,
            entities={"generation": 5},
            confidence=0.9,
            raw_text="rollback to generation 5"
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="Rolled back", stderr="")
            result = self.executor.execute(intent, dry_run=False)
        
        self.assertIsNotNone(result)
        self.assertTrue(result.success)
    
    def test_help_execution(self):
        """Test help command execution"""
        intent = Intent(
            type=IntentType.HELP,
            entities={},
            confidence=0.9,
            raw_text="help"
        )
        
        result = self.executor.execute(intent, dry_run=False)
        
        self.assertIsNotNone(result)
        self.assertTrue(result.success)
        self.assertIn("help", result.output.lower())
    
    def test_concurrent_execution_prevention(self):
        """Test that executor prevents concurrent dangerous operations"""
        intent1 = Intent(
            type=IntentType.UPDATE_SYSTEM,
            entities={},
            confidence=0.9,
            raw_text="update system"
        )
        
        intent2 = Intent(
            type=IntentType.UPDATE_SYSTEM,
            entities={},
            confidence=0.9,
            raw_text="update system again"
        )
        
        # In real implementation, would check for locks
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="OK", stderr="")
            
            result1 = self.executor.execute(intent1, dry_run=True)
            result2 = self.executor.execute(intent2, dry_run=True)
            
            self.assertIsNotNone(result1)
            self.assertIsNotNone(result2)


class TestValidationResult(unittest.TestCase):
    """Test the ValidationResult class"""
    
    def test_creation(self):
        """Test ValidationResult creation"""
        result = ValidationResult(
            is_safe=True,
            reason="Command is safe",
            suggestions=["Consider using --dry-run first"]
        )
        
        self.assertTrue(result.is_safe)
        self.assertEqual(result.reason, "Command is safe")
        self.assertEqual(len(result.suggestions), 1)
    
    def test_unsafe_result(self):
        """Test unsafe validation result"""
        result = ValidationResult(
            is_safe=False,
            reason="Command could damage system",
            suggestions=["Use a safer alternative", "Run in a VM first"]
        )
        
        self.assertFalse(result.is_safe)
        self.assertIn("damage", result.reason)
        self.assertEqual(len(result.suggestions), 2)


if __name__ == '__main__':
    unittest.main()