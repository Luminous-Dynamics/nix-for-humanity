#!/usr/bin/env python3
"""
import subprocess
Tests for SafeExecutor - command execution module

Tests the safe execution of NixOS commands with security validation,
rollback support, and progress reporting.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, AsyncMock, call
import asyncio
import sys
import os

# Add parent directories to path
project_root = os.path.join(os.path.dirname(__file__), '../..')
sys.path.insert(0, project_root)
backend_path = os.path.join(project_root, 'nix_humanity')
sys.path.insert(0, backend_path)

# Mock the imports that might not be available
sys.modules['nix_humanity.python'] = MagicMock()
sys.modules['nix_humanity.python.native_nix_backend'] = MagicMock()

# Import after mocking
from nix_humanity.core.executor import SafeExecutor, ValidationResult
from nix_humanity.core.intents import Intent, IntentType
from nix_humanity.api.schema import Result


class TestValidationResult(unittest.TestCase):
    """Test the ValidationResult class."""
    
    def test_validation_result_creation(self):
        """Test creating ValidationResult objects."""
        # Valid result
        result = ValidationResult(valid=True, reason="All checks passed")
        self.assertTrue(result.valid)
        self.assertEqual(result.reason, "All checks passed")
        
        # Invalid result
        result = ValidationResult(valid=False, reason="Dangerous pattern detected")
        self.assertFalse(result.valid)
        self.assertEqual(result.reason, "Dangerous pattern detected")


class TestSafeExecutor(unittest.TestCase):
    """Test the SafeExecutor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.progress_callback = Mock()
        
        # Mock the Python API module
        self.native_backend_mock = MagicMock()
        self.native_backend_mock.execute = AsyncMock()
        
        # Create executor
        with patch('backend.core.executor.SafeExecutor._init_python_api'):
            self.executor = SafeExecutor(progress_callback=self.progress_callback)
            self.executor._has_python_api = False
            self.executor.native_backend = None
    
    def test_init(self):
        """Test SafeExecutor initialization."""
        with patch('backend.core.executor.SafeExecutor._init_python_api') as mock_init:
            executor = SafeExecutor()
            self.assertIsNone(executor.progress_callback)
            self.assertFalse(executor.dry_run)
            mock_init.assert_called_once()
        
        # With progress callback
        callback = Mock()
        with patch('backend.core.executor.SafeExecutor._init_python_api'):
            executor = SafeExecutor(progress_callback=callback)
            self.assertEqual(executor.progress_callback, callback)
    
    def test_get_operation_type(self):
        """Test mapping intent to operation type."""
        test_cases = [
            (IntentType.INSTALL_PACKAGE, 'install-package'),
            (IntentType.UPDATE_SYSTEM, 'modify-configuration'),
            (IntentType.CONFIGURE, 'modify-configuration'),
            (IntentType.ROLLBACK, 'modify-configuration'),
            (IntentType.SEARCH_PACKAGE, 'read-file'),
            (IntentType.EXPLAIN, 'read-file'),
            (IntentType.HELP, 'read-file'),
            (IntentType.REMOVE_PACKAGE, 'remove-package'),
            (IntentType.UNKNOWN, 'unknown'),
        ]
        
        for intent_type, expected_op in test_cases:
            intent = Intent(
                type=intent_type,
                entities={},
                confidence=1.0,
                raw_text="test"
            )
            result = self.executor._get_operation_type(intent)
            self.assertEqual(result, expected_op)
    
    def test_progress_wrapper(self):
        """Test progress callback wrapper."""
        self.executor._progress_wrapper("Installing package", 0.5)
        self.progress_callback.assert_called_once_with("Installing package", 0.5)
        
        # Test without callback
        executor = SafeExecutor()
        # Should not raise error
        executor._progress_wrapper("Test", 0.1)
    
    @patch('backend.core.executor.SafeExecutor._run_command')
    async def test_execute_help(self, mock_run):
        """Test executing help command."""
        intent = Intent(
            type=IntentType.HELP,
            entities={},
            confidence=1.0,
            raw_text="help"
        )
        
        result = await self.executor.execute([], intent)
        
        self.assertTrue(result.success)
        self.assertIn("Available commands", result.output)
        self.assertIn("Install packages", result.output)
        self.assertEqual(result.error, "")
    
    @patch('backend.core.executor.SafeExecutor._run_command')
    async def test_execute_search(self, mock_run):
        """Test executing package search."""
        mock_run.return_value = {
            'returncode': 0,
            'stdout': 'firefox - Web browser',
            'stderr': ''
        }
        
        intent = Intent(
            type=IntentType.SEARCH_PACKAGE,
            entities={'query': 'firefox'},
            confidence=1.0,
            raw_text="search firefox"
        )
        
        result = await self.executor.execute([], intent)
        
        self.assertTrue(result.success)
        self.assertEqual(result.output, 'firefox - Web browser')
        self.assertEqual(result.error, "")
        
        # Verify command
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd, ['nix', 'search', 'nixpkgs', 'firefox'])
    
    @patch('backend.core.executor.SafeExecutor._run_command')
    async def test_execute_search_no_query(self, mock_run):
        """Test search with no query specified."""
        intent = Intent(
            type=IntentType.SEARCH_PACKAGE,
            entities={},
            confidence=1.0,
            raw_text="search_package"
        )
        
        result = await self.executor.execute([], intent)
        
        self.assertFalse(result.success)
        self.assertEqual(result.error, "No search query specified")
        mock_run.assert_not_called()
    
    def test_validate_package_name(self):
        """Test package name validation."""
        # Valid packages
        valid_packages = [
            'firefox',
            'google-chrome',
            'python3',
            'lib-test',
            'package_name',
            'pkg123'
        ]
        
        for pkg in valid_packages:
            self.assertTrue(
                self.executor._validate_package_name(pkg),
                f"Package '{pkg}' should be valid"
            )
        
        # Invalid packages
        invalid_packages = [
            None,
            '',
            'a' * 101,  # Too long
            '../etc/passwd',  # Path traversal
            'pkg;rm -rf /',  # Shell injection
            '.hidden',  # Starts with dot
            '-flag',  # Starts with dash
            'sudo',  # Special name
            '..',  # Special name
            'pkg$var',  # Shell variable
        ]
        
        for pkg in invalid_packages:
            self.assertFalse(
                self.executor._validate_package_name(pkg),
                f"Package '{pkg}' should be invalid"
            )
    
    def test_validate_search_query(self):
        """Test search query validation."""
        # Valid queries
        valid_queries = [
            'firefox',
            'text editor',
            'python development',
            'web-browser'
        ]
        
        for query in valid_queries:
            self.assertTrue(
                self.executor._validate_search_query(query),
                f"Query '{query}' should be valid"
            )
        
        # Invalid queries
        invalid_queries = [
            None,
            '',
            'a' * 201,  # Too long
            'search; rm -rf /',  # Shell injection
            'query | cat /etc/passwd',  # Pipe
            'search`whoami`',  # Command substitution
            '<script>alert(1)</script>',  # XSS attempt
        ]
        
        for query in invalid_queries:
            self.assertFalse(
                self.executor._validate_search_query(query),
                f"Query '{query}' should be invalid"
            )
    
    def test_validate_command_args(self):
        """Test command argument validation."""
        # Valid commands
        valid_commands = [
            ['nix', 'search', 'firefox'],
            ['sudo', 'nixos-rebuild', 'switch'],
            ['nix-env', '-i', 'package'],
            ['nix-channel', '--update'],
        ]
        
        for cmd in valid_commands:
            self.assertTrue(
                self.executor._validate_command_args(cmd),
                f"Command {cmd} should be valid"
            )
        
        # Invalid commands
        invalid_commands = [
            None,
            [],
            ['rm', '-rf', '/'],  # Not whitelisted
            ['nix', 'search; rm -rf /'],  # Shell injection
            ['wget', 'http://example.com'],  # Not whitelisted
            ['curl', 'http://example.com'],  # Not whitelisted
        ]
        
        for cmd in invalid_commands:
            self.assertFalse(
                self.executor._validate_command_args(cmd),
                f"Command {cmd} should be invalid"
            )
    
    def test_validate_execution_request(self):
        """Test comprehensive execution request validation."""
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={'package': 'firefox'},
            confidence=1.0,
            raw_text="install firefox"
        )
        
        # Valid request
        result = self.executor._validate_execution_request(['install firefox'], intent)
        self.assertTrue(result.valid)
        self.assertEqual(result.reason, "Validation passed")
        
        # Too many actions
        long_plan = [f"action{i}" for i in range(25)]
        result = self.executor._validate_execution_request(long_plan, intent)
        self.assertFalse(result.valid)
        self.assertIn("too complex", result.reason)
        
        # Invalid action type
        result = self.executor._validate_execution_request([123], intent)
        self.assertFalse(result.valid)
        self.assertIn("Invalid action type", result.reason)
        
        # Dangerous pattern
        result = self.executor._validate_execution_request(['rm -rf /'], intent)
        self.assertFalse(result.valid)
        self.assertIn("Unsafe pattern", result.reason)
    
    def test_create_rebuild_script(self):
        """Test creating rebuild script for background execution."""
        script_path = self.executor._create_rebuild_script()
        
        self.assertTrue(script_path.exists())
        self.assertEqual(script_path.name, 'nixos-rebuild-wrapper.sh')
        
        # Check script content
        content = script_path.read_text()
        self.assertIn("nixos-rebuild switch", content)
        self.assertIn("/tmp/nixos-rebuild.log", content)
        
        # Check permissions
        stat_info = script_path.stat()
        self.assertEqual(stat_info.st_mode & 0o777, 0o755)
        
        # Cleanup
        script_path.unlink()
    
    @patch('backend.core.executor.SafeExecutor._run_command')
    async def test_execute_install_dry_run(self, mock_run):
        """Test install in dry run mode."""
        self.executor.dry_run = True
        
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={'package': 'firefox'},
            confidence=1.0,
            raw_text="install firefox"
        )
        
        result = await self.executor.execute([], intent)
        
        self.assertTrue(result.success)
        self.assertEqual(result.output, "Would install: firefox")
        self.assertEqual(result.error, "")
        mock_run.assert_not_called()
    
    @patch('backend.core.executor.SafeExecutor._run_command')
    @patch('backend.core.executor.InputValidator.validate_input')
    @patch('backend.core.executor.PermissionChecker.check_operation_permission')
    async def test_execute_install_validation_fail(self, mock_perm, mock_validate, mock_run):
        """Test install with validation failure."""
        # Setup mocks
        mock_perm.return_value = {'allowed': True}
        mock_validate.return_value = {
            'valid': False,
            'reason': 'Invalid package name',
            'suggestions': ['Use alphanumeric characters only']
        }
        
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={'package': 'bad;package'},
            confidence=1.0,
            raw_text="install bad;package"
        )
        
        result = await self.executor.execute([], intent)
        
        self.assertFalse(result.success)
        self.assertEqual(result.error, 'Invalid package name')
        self.assertEqual(result.details, ['Use alphanumeric characters only'])
        mock_run.assert_not_called()
    
    @patch('backend.core.executor.SafeExecutor._run_command')
    @patch('backend.core.executor.PermissionChecker.check_operation_permission')
    async def test_execute_permission_denied(self, mock_perm, mock_run):
        """Test execution with permission denied."""
        mock_perm.return_value = {
            'allowed': False,
            'reason': 'User not in wheel group',
            'suggestions': ['Add user to wheel group']
        }
        
        intent = Intent(
            type=IntentType.UPDATE_SYSTEM,
            entities={},
            confidence=1.0,
            raw_text="update system"
        )
        
        result = await self.executor.execute([], intent)
        
        self.assertFalse(result.success)
        self.assertEqual(result.error, "Permission denied: User not in wheel group")
        self.assertEqual(result.details, ['Add user to wheel group'])
        mock_run.assert_not_called()
    
    @patch('backend.core.executor.asyncio.create_subprocess_exec')
    async def test_run_command_timeout(self, mock_subprocess):
        """Test command execution with timeout."""
        # Create mock process
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock()
        mock_process.kill = Mock()
        mock_process.wait = AsyncMock()
        
        # Make communicate timeout
        mock_process.communicate.side_effect = asyncio.TimeoutError()
        mock_subprocess.return_value = mock_process
        
        result = await self.executor._run_command(['sleep', '10'], timeout=1)
        
        self.assertEqual(result['returncode'], -1)
        self.assertIn('timed out', result['stderr'])
        mock_process.kill.assert_called_once()
    
    @patch('backend.core.executor.CommandValidator.validate_nix_command')
    async def test_run_command_security_block(self, mock_validate):
        """Test command blocked by security validation."""
        mock_validate.return_value = (
            False,
            'Dangerous command detected',
            {'reason': 'Shell injection attempt'}
        )
        
        result = await self.executor._run_command(['nix', 'eval', '--impure'])
        
        self.assertEqual(result['returncode'], -1)
        self.assertIn('Command blocked', result['stderr'])
        self.assertIn('Dangerous command', result['stderr'])


class TestSafeExecutorAsync(unittest.TestCase):
    """Test async functionality of SafeExecutor."""
    
    def setUp(self):
        """Set up test fixtures."""
        with patch('backend.core.executor.SafeExecutor._init_python_api'):
            self.executor = SafeExecutor()
            self.executor._has_python_api = False
    
    def test_async_execution(self):
        """Test that execute is properly async."""
        intent = Intent(
            type=IntentType.HELP,
            entities={},
            confidence=1.0,
            raw_text="help"
        )
        
        # Should return a coroutine
        coro = self.executor.execute([], intent)
        self.assertTrue(asyncio.iscoroutine(coro))
        
        # Clean up
        coro.close()


def run_async_test(coro):
    """Helper to run async tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


if __name__ == '__main__':
    unittest.main()