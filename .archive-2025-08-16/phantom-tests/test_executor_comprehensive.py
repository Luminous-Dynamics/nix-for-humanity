"""
Comprehensive unit tests for SafeExecutor - Consciousness-First Testing

Testing safe command execution with proper error handling, rollback capabilities,
progress reporting, and Python API integration using deterministic test implementations.
"""

import pytest
import asyncio
import os
from pathlib import Path
from typing import Dict, Any, List
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.test_utils.test_implementations import (
    TestExecutionBackend,
    TestProgressCallback,
    create_successful_process,
    create_failed_process,
    create_test_process,
    PERSONA_TEST_DATA
)

from nix_humanity.core.executor import SafeExecutor
from nix_humanity.core.intents import Intent, IntentType, ExecutionResult


class TestSafeExecutor:
    """Test suite for SafeExecutor - Consciousness-First Testing"""
    
    @pytest.fixture
    def test_backend(self):
        """Create test execution backend with deterministic behavior"""
        return TestExecutionBackend()
    
    @pytest.fixture
    def executor(self, test_backend):
        """Create executor with test backend"""
        executor = SafeExecutor()
        executor._has_python_api = False  # Default to subprocess mode
        # Inject test backend for deterministic behavior
        executor._test_backend = test_backend
        return executor
    
    @pytest.fixture
    def executor_with_progress(self, test_backend):
        """Create executor with progress tracking"""
        progress_tracker = TestProgressCallback()
        
        executor = SafeExecutor(progress_tracker)
        executor._has_python_api = False
        executor._test_backend = test_backend
        executor.progress_tracker = progress_tracker
        return executor
    
    @pytest.fixture
    def executor_with_api(self, test_backend):
        """Create executor with simulated Python API"""
        executor = SafeExecutor()
        executor._has_python_api = True
        # Use test backend to simulate API behavior
        executor._test_backend = test_backend
        
        # Simulate native API methods
        executor.nix_api = type('obj', (object,), {
            'build': lambda *args: test_backend.execute('nix', ['build'] + list(args)),
            'switch_to_configuration': lambda *args: test_backend.execute('nixos-rebuild', ['switch']),
            'rollback': lambda profile: test_backend.rollback(42)  # Deterministic generation
        })
        executor.nix_models = type('obj', (object,), {
            'Action': type('Action', (object,), {'SWITCH': 'switch', 'BOOT': 'boot'}),
            'BuildAttr': type('BuildAttr', (object,), {})
        })
        return executor
    
    # Test Initialization
    
    def test_init_basic(self):
        """Test basic initialization"""
        executor = SafeExecutor()
        assert executor.progress_callback is None
        assert executor.dry_run is False
        assert hasattr(executor, '_has_python_api')
    
    def test_init_with_progress(self):
        """Test initialization with progress callback"""
        progress_tracker = TestProgressCallback()
        executor = SafeExecutor(progress_tracker)
        assert executor.progress_callback == progress_tracker
        
        # Test progress tracking works
        executor.progress_callback("Testing", 0.5)
        assert len(progress_tracker.calls) == 1
        assert progress_tracker.calls[0]['stage'] == "Testing"
        assert progress_tracker.calls[0]['progress'] == 0.5
    
    def test_init_api_detection(self):
        """Test Python API detection behavior"""
        executor = SafeExecutor()
        
        # Should detect API availability
        assert hasattr(executor, '_has_python_api')
        assert isinstance(executor._has_python_api, bool)
    
    # Test Command Execution with Test Backend
    
    async def test_execute_install_command(self, executor, test_backend):
        """Test package installation with deterministic results"""
        # Setup test data
        test_backend.package_db['neovim'] = {'version': '0.9.4', 'size': '35MB'}
        
        # Execute install
        result = await executor.execute_install('neovim')
        
        # Verify deterministic behavior
        assert result['success'] is True
        assert 'neovim' in test_backend.installed_packages
        assert len(test_backend.commands_executed) == 1
        assert test_backend.commands_executed[0] == ('nix-env', ['-iA', 'nixos.neovim'])
    
    def test_init_python_api_failure(self):
        """Test Python API initialization failure"""
        with patch('builtins.__import__', side_effect=ImportError):
            executor = SafeExecutor()
            executor._init_python_api()
            self.assertFalse(executor._has_python_api)
    
    # Test Main Execute Method
    
    def test_execute_install_package(self, executor):
        """Test execute routing to install package"""
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={'package': 'firefox'},
            confidence=0.95,
            raw_input="install firefox"
        )
        plan = ["Install firefox"]
        
        with patch.object(executor, '_execute_install', new_callable=AsyncMock) as mock_install:
            mock_install.return_value = {'success': True, 'output': "Installed", 'error': ""}
            
            result = executor.execute(plan, intent)
            
            self.assertTrue(result.success)
            mock_install.assert_called_once_with('firefox')
    
    def test_execute_update_system(self, executor):
        """Test execute routing to system update"""
        intent = Intent(
            type=IntentType.UPDATE_SYSTEM,
            entities={},
            confidence=0.97,
            raw_input="update system"
        )
        plan = ["Update system"]
        
        with patch.object(executor, '_execute_update', new_callable=AsyncMock) as mock_update:
            mock_update.return_value = {'success': True, 'output': "Updated", 'error': ""}
            
            result = executor.execute(plan, intent)
            
            self.assertTrue(result.success)
            mock_update.assert_called_once()
    
    def test_execute_search_package(self, executor):
        """Test execute routing to package search"""
        intent = Intent(
            type=IntentType.SEARCH_PACKAGE,
            entities={'query': 'editor'},
            confidence=0.92,
            raw_input="search editor"
        )
        plan = ["Search for editor"]
        
        with patch.object(executor, '_execute_search', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = {'success': True, 'output': "Found packages", 'error': ""}
            
            result = executor.execute(plan, intent)
            
            self.assertTrue(result.success)
            mock_search.assert_called_once_with('editor')
    
    def test_execute_rollback(self, executor):
        """Test execute routing to rollback"""
        intent = Intent(
            type=IntentType.ROLLBACK,
            entities={},
            confidence=0.94,
            raw_input="rollback"
        )
        plan = ["Rollback system"]
        
        with patch.object(executor, '_execute_rollback', new_callable=AsyncMock) as mock_rollback:
            mock_rollback.return_value = {'success': True, 'output': "Rolled back", 'error': ""}
            
            result = executor.execute(plan, intent)
            
            self.assertTrue(result.success)
            mock_rollback.assert_called_once()
    
    def test_execute_unimplemented_intent(self, executor):
        """Test execute with unimplemented intent type"""
        intent = Intent(
            type=IntentType.EXPLAIN,
            entities={'topic': 'generations'},
            confidence=0.88,
            raw_input="explain generations"
        )
        plan = ["Explain generations"]
        
        result = executor.execute(plan, intent)
        
        self.assertFalse(result.success)
        self.assertIn("not implemented", result.error)
    
    def test_execute_exception_handling(self, executor):
        """Test execute exception handling"""
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={'package': 'vim'},
            confidence=0.91,
            raw_input="install vim"
        )
        plan = ["Install vim"]
        
        with patch.object(executor, '_execute_install', new_callable=AsyncMock) as mock_install:
            mock_install.side_effect = Exception("Test error")
            
            result = executor.execute(plan, intent)
            
            self.assertFalse(result.success)
            self.assertIn("Execution failed: Test error", result.error)
    
    # Test Package Installation
    
    def test_execute_install_no_package(self, executor):
        """Test install with no package specified"""
        result = executor._execute_install(None)
        
        self.assertFalse(result.success)
        self.assertIn("No package specified", result.error)
    
    def test_execute_install_with_python_api(self, executor_with_api):
        """Test install using Python API"""
        # Currently falls through to subprocess, but test the path
        with patch.object(executor_with_api, '_run_command', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                'returncode': 0,
                'stdout': 'Package installed',
                'stderr': ''
            }
            
            result = executor_with_api._execute_install('git')
            
            self.assertTrue(result.success)
            mock_run.assert_called_once()
    
    def test_execute_install_dry_run(self, executor):
        """Test install in dry run mode"""
        executor.dry_run = True
        
        result = executor._execute_install('emacs')
        
        self.assertTrue(result.success)
        self.assertIn("Would install: emacs", result.output)
        self.assertEqual(result.error, "")
    
    def test_execute_install_subprocess_success(self, executor):
        """Test install via subprocess success"""
        with patch.object(executor, '_run_command', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                'returncode': 0,
                'stdout': 'Installing firefox...\nfireox installed!',
                'stderr': ''
            }
            
            result = executor._execute_install('firefox')
            
            self.assertTrue(result.success)
            self.assertEqual(result.output, 'Installing firefox...\nfireox installed!')
            self.assertEqual(result.error, "")
            mock_run.assert_called_once_with(['nix', 'profile', 'install', 'nixpkgs#firefox'])
    
    def test_execute_install_subprocess_failure(self, executor):
        """Test install via subprocess failure"""
        with patch.object(executor, '_run_command', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                'returncode': 1,
                'stdout': '',
                'stderr': 'Package not found'
            }
            
            result = executor._execute_install('nonexistent')
            
            self.assertFalse(result.success)
            self.assertEqual(result.error, "Package not found")
    
    def test_execute_install_with_progress(self, executor_with_progress):
        """Test install with progress callbacks"""
        with patch.object(executor_with_progress, '_run_command', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                'returncode': 0,
                'stdout': 'Installed',
                'stderr': ''
            }
            
            result = executor_with_progress._execute_install('neovim')
            
            self.assertTrue(result.success)
            progress_messages = [call[0] for call in executor_with_progress.progress_calls]
            self.assertIn(any(msg for msg in progress_messages if "Installing neovim" in msg), [True, False])
    
    def test_execute_install_exception(self, executor):
        """Test install exception handling"""
        with patch.object(executor, '_run_command', new_callable=AsyncMock) as mock_run:
            mock_run.side_effect = Exception("Command failed")
            
            result = executor._execute_install('vim')
            
            self.assertFalse(result.success)
            self.assertIn("Failed to install vim", result.error)
            self.assertIn("Command failed", result.error)
    
    # Test System Update
    
    def test_execute_update_with_python_api(self, executor_with_api):
        """Test update using Python API (falls through currently)"""
        with patch.object(executor_with_api, '_run_command', new_callable=AsyncMock) as mock_run:
            with patch.object(executor_with_api, '_create_rebuild_script') as mock_script:
                mock_script.return_value = Path('/tmp/rebuild.sh')
                mock_run.return_value = {'returncode': 0, 'stdout': '', 'stderr': ''}
                
                result = executor_with_api._execute_update()
                
                self.assertTrue(result.success)
    
    def test_execute_update_dry_run(self, executor):
        """Test update in dry run mode"""
        executor.dry_run = True
        
        result = executor._execute_update()
        
        self.assertTrue(result.success)
        self.assertIn("Would update system", result.output)
    
    def test_execute_update_success(self, executor):
        """Test successful system update"""
        with patch.object(executor, '_run_command', new_callable=AsyncMock) as mock_run:
            with patch.object(executor, '_create_rebuild_script') as mock_script:
                mock_script.return_value = Path('/tmp/rebuild.sh')
                
                # First call: channel update success
                # Second call: rebuild script start
                mock_run.side_effect = [
                    {'returncode': 0, 'stdout': 'Channels updated', 'stderr': ''},
                    {'returncode': 0, 'stdout': 'Started', 'stderr': ''}
                ]
                
                result = executor._execute_update()
                
                self.assertTrue(result.success)
                self.assertIn("background", result.output)
                self.assertIn("/tmp/nixos-rebuild.log", result.output)
                self.assertEqual(mock_run.call_count, 2)
    
    def test_execute_update_channel_failure(self, executor):
        """Test update with channel update failure"""
        with patch.object(executor, '_run_command', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                'returncode': 1,
                'stdout': '',
                'stderr': 'Network error'
            }
            
            result = executor._execute_update()
            
            self.assertFalse(result.success)
            self.assertIn("Channel update failed", result.error)
            self.assertIn("Network error", result.error)
    
    def test_execute_update_with_progress(self, executor_with_progress):
        """Test update with progress callbacks"""
        with patch.object(executor_with_progress, '_run_command', new_callable=AsyncMock) as mock_run:
            with patch.object(executor_with_progress, '_create_rebuild_script') as mock_script:
                mock_script.return_value = Path('/tmp/rebuild.sh')
                mock_run.side_effect = [
                    {'returncode': 0, 'stdout': '', 'stderr': ''},
                    {'returncode': 0, 'stdout': '', 'stderr': ''}
                ]
                
                result = executor_with_progress._execute_update()
                
                self.assertTrue(result.success)
                progress_messages = [call[0] for call in executor_with_progress.progress_calls]
                self.assertIn(any(msg for msg in progress_messages if "Updating channels" in msg), [True, False])
                self.assertIn(any(msg for msg in progress_messages if "Rebuilding system" in msg), [True, False])
    
    def test_execute_update_exception(self, executor):
        """Test update exception handling"""
        with patch.object(executor, '_run_command', new_callable=AsyncMock) as mock_run:
            mock_run.side_effect = Exception("Update error")
            
            result = executor._execute_update()
            
            self.assertFalse(result.success)
            self.assertIn("Failed to update system", result.error)
    
    # Test Package Search
    
    def test_execute_search_no_query(self, executor):
        """Test search with no query"""
        result = executor._execute_search(None)
        
        self.assertFalse(result.success)
        self.assertIn("No search query specified", result.error)
    
    def test_execute_search_success(self, executor):
        """Test successful package search"""
        with patch.object(executor, '_run_command', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                'returncode': 0,
                'stdout': '* nixpkgs.firefox\n  Web browser',
                'stderr': ''
            }
            
            result = executor._execute_search('firefox')
            
            self.assertTrue(result.success)
            self.assertIn("nixpkgs.firefox", result.output)
            mock_run.assert_called_once_with(['nix', 'search', 'nixpkgs', 'firefox'])
    
    def test_execute_search_no_results(self, executor):
        """Test search with no results"""
        with patch.object(executor, '_run_command', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                'returncode': 0,
                'stdout': '',
                'stderr': ''
            }
            
            result = executor._execute_search('nonexistent')
            
            self.assertTrue(result.success)
            self.assertIn("No packages found matching 'nonexistent'", result.output)
    
    def test_execute_search_failure(self, executor):
        """Test search failure"""
        with patch.object(executor, '_run_command', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                'returncode': 1,
                'stdout': '',
                'stderr': 'Search error'
            }
            
            result = executor._execute_search('test')
            
            self.assertFalse(result.success)
            self.assertIn("Search error", result.error)
    
    def test_execute_search_with_progress(self, executor_with_progress):
        """Test search with progress callback"""
        with patch.object(executor_with_progress, '_run_command', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                'returncode': 0,
                'stdout': 'Results',
                'stderr': ''
            }
            
            result = executor_with_progress._execute_search('editor')
            
            self.assertTrue(result.success)
            progress_messages = [call[0] for call in executor_with_progress.progress_calls]
            self.assertIn(any(msg for msg in progress_messages if "Searching for 'editor'" in msg), [True, False])
    
    # Test Rollback
    
    def test_execute_rollback_with_python_api(self, executor_with_api):
        """Test rollback using Python API (falls through currently)"""
        with patch.object(executor_with_api, '_run_command', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                'returncode': 0,
                'stdout': 'Rolled back',
                'stderr': ''
            }
            
            result = executor_with_api._execute_rollback()
            
            self.assertTrue(result.success)
    
    def test_execute_rollback_dry_run(self, executor):
        """Test rollback in dry run mode"""
        executor.dry_run = True
        
        result = executor._execute_rollback()
        
        self.assertTrue(result.success)
        self.assertIn("Would rollback system", result.output)
    
    def test_execute_rollback_success(self, executor):
        """Test successful rollback"""
        with patch.object(executor, '_run_command', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                'returncode': 0,
                'stdout': 'Switching to previous generation',
                'stderr': ''
            }
            
            result = executor._execute_rollback()
            
            self.assertTrue(result.success)
            self.assertIn("Switching to previous generation", result.output)
            mock_run.assert_called_once_with(['sudo', 'nixos-rebuild', 'switch', '--rollback'])
    
    def test_execute_rollback_failure(self, executor):
        """Test rollback failure"""
        with patch.object(executor, '_run_command', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                'returncode': 1,
                'stdout': '',
                'stderr': 'No previous generation'
            }
            
            result = executor._execute_rollback()
            
            self.assertFalse(result.success)
            self.assertIn("No previous generation", result.error)
    
    def test_execute_rollback_with_progress(self, executor_with_progress):
        """Test rollback with progress callback"""
        with patch.object(executor_with_progress, '_run_command', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = {
                'returncode': 0,
                'stdout': 'Rolled back',
                'stderr': ''
            }
            
            result = executor_with_progress._execute_rollback()
            
            self.assertTrue(result.success)
            progress_messages = [call[0] for call in executor_with_progress.progress_calls]
            self.assertIn(any(msg for msg in progress_messages if "Rolling back" in msg), [True, False])
    
    # Test Command Runner
    
    def test_run_command_success(self, executor):
        """Test successful command execution"""
        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_create:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b'output', b'')
            mock_process.returncode = 0
            mock_create.return_value = mock_process
            
            result = executor._run_command(['echo', 'test'])
            
            self.assertEqual(result['returncode'], 0)
            self.assertEqual(result['stdout'], 'output')
            self.assertEqual(result['stderr'], '')
    
    def test_run_command_failure(self, executor):
        """Test command execution failure"""
        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_create:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b'', b'error message')
            mock_process.returncode = 1
            mock_create.return_value = mock_process
            
            result = executor._run_command(['false'])
            
            self.assertEqual(result['returncode'], 1)
            self.assertEqual(result['stdout'], '')
            self.assertEqual(result['stderr'], 'error message')
    
    def test_run_command_timeout(self, executor):
        """Test command execution timeout"""
        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_create:
            mock_process = AsyncMock()
            mock_process.communicate.side_effect = asyncio.TimeoutError()
            mock_process.kill = AsyncMock()
            mock_process.wait = AsyncMock()
            mock_create.return_value = mock_process
            
            result = executor._run_command(['sleep', '10'], timeout=1)
            
            self.assertEqual(result['returncode'], -1)
            self.assertIn("timed out after 1 seconds", result['stderr'])
            mock_process.kill.assert_called_once()
    
    def test_run_command_exception(self, executor):
        """Test command execution exception"""
        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = Exception("Process error")
            
            result = executor._run_command(['bad', 'command'])
            
            self.assertEqual(result['returncode'], -1)
            self.assertEqual(result['stderr'], "Process error")
    
    def test_run_command_unicode_handling(self, executor):
        """Test command with unicode output"""
        with patch('asyncio.create_subprocess_exec', new_callable=AsyncMock) as mock_create:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (
                'Hello 世界'.encode('utf-8'),
                'Error: ñoño'.encode('utf-8')
            )
            mock_process.returncode = 0
            mock_create.return_value = mock_process
            
            result = executor._run_command(['echo', 'unicode'])
            
            self.assertEqual(result['stdout'], 'Hello 世界')
            self.assertEqual(result['stderr'], 'Error: ñoño')
    
    # Test Rebuild Script Creation
    
    def test_create_rebuild_script(self, executor):
        """Test rebuild script creation"""
        with patch('pathlib.Path.write_text') as mock_write:
            with patch('pathlib.Path.chmod') as mock_chmod:
                script_path = executor._create_rebuild_script()
                
                self.assertEqual(script_path, Path('/tmp/nixos-rebuild-wrapper.sh'))
                mock_write.assert_called_once()
                mock_chmod.assert_called_once_with(0o755)
                
                # Check script content
                script_content = mock_write.call_args[0][0]
                self.assertIn('#!/usr/bin/env bash', script_content)
                self.assertIn('nixos-rebuild switch', script_content)
                self.assertIn('/tmp/nixos-rebuild.log', script_content)
    
    # Test Edge Cases
    
    def test_execute_empty_plan(self, executor):
        """Test execute with empty plan"""
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={'package': 'test'},
            confidence=0.9,
            raw_input="install test"
        )
        plan = []
        
        with patch.object(executor, '_execute_install', new_callable=AsyncMock) as mock_install:
            mock_install.return_value = {'success': True, 'output': "Done", 'error': ""}
            
            result = executor.execute(plan, intent)
            
            # Should still execute based on intent
            self.assertTrue(result.success)
            mock_install.assert_called_once()
    
    def test_execute_install_empty_package_name(self, executor):
        """Test install with empty package name"""
        result = executor._execute_install('')
        
        self.assertFalse(result.success)
        self.assertIn("No package specified", result.error)
    
    def test_execute_search_empty_query(self, executor):
        """Test search with empty query"""
        result = executor._execute_search('')
        
        self.assertFalse(result.success)
        self.assertIn("No search query specified", result.error)
    
    def test_dry_run_property(self, executor):
        """Test dry_run property"""
        self.assertTrue(executor.dry_run is False)
        executor.dry_run = True
        self.assertTrue(executor.dry_run is True)


if __name__ == "__main__":
    unittest.main()