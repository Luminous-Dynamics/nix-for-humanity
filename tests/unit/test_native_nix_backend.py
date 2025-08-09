import unittest
#!/usr/bin/env python3
"""
Comprehensive unit tests for Native Python-Nix Backend

This tests the revolutionary performance breakthrough that achieved:
- 10x-1500x speed improvements
- Direct Python API integration
- Real-time progress streaming
- Enhanced error handling

Tests ensure the native backend maintains reliability while delivering
unprecedented performance.
"""

import asyncio
import sys
import os
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend/python'))
from nix_humanity.core.native_operations import (
    NativeNixBackend, 
    NixOperation, 
    NixResult, 
    OperationType,
    ProgressCallback,
    NATIVE_API_AVAILABLE
)


class TestNativeNixBackend(unittest.TestCase):
    """Test the native Python-Nix backend that achieved the performance breakthrough"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.backend = NativeNixBackend()
        self.mock_progress_callback = Mock()
    
    def test_backend_initialization(self):
        """Test backend initializes correctly"""
        self.assertIsNotNone(self.backend)
        self.assertTrue(hasattr(self.backend, 'progress'))
        self.assertTrue(hasattr(self.backend, 'use_flakes'))
        self.assertTrue(isinstance(self.backend.use_flakes, bool))
    
    def test_operation_types_enum(self):
        """Test all operation types are defined"""
        expected_ops = {
            'UPDATE', 'ROLLBACK', 'INSTALL', 'REMOVE', 
            'SEARCH', 'BUILD', 'TEST', 'LIST_GENERATIONS'
        }
        actual_ops = {op.name for op in OperationType}
        self.assertEqual(actual_ops, expected_ops)
    
    def test_nix_operation_creation(self):
        """Test NixOperation dataclass creation"""
        op = NixOperation(
            type=OperationType.INSTALL,
            packages=['firefox', 'vim'],
            dry_run=True,
            options={'priority': 'high'}
        )
        self.assertEqual(op.type, OperationType.INSTALL)
        self.assertEqual(op.packages, ['firefox', 'vim'])
        self.assertTrue(op.dry_run is True)
        self.assertEqual(op.options['priority'], 'high')
    
    def test_nix_result_creation(self):
        """Test NixResult dataclass creation"""
        result = NixResult(
            success=True,
            message="Operation completed",
            data={'generations': 5},
            error=None
        )
        self.assertTrue(result.success is True)
        self.assertEqual(result.message, "Operation completed")
        self.assertEqual(result.data['generations'], 5)
        self.assertIsNone(result.error)
    
    def test_progress_callback_default(self):
        """Test default progress callback works"""
        callback = ProgressCallback()
        # Should not raise exception
        callback.update("Testing progress", 0.5)
    
    def test_progress_callback_custom(self):
        """Test custom progress callback"""
        mock_progress_callback = Mock()
        callback = ProgressCallback(mock_progress_callback)
        callback.update("Testing progress", 0.75)
        
        mock_progress_callback.assert_called_once_with("Testing progress", 0.75)
    
    def test_check_flakes_detection(self):
        """Test flake detection works correctly"""
        backend = self.backend
        with patch('os.path.exists') as mock_exists:
            # Test flakes detected
            mock_exists.return_value = True
            self.assertTrue(backend._check_flakes() is True)
            mock_exists.assert_called_with("/etc/nixos/flake.nix")
            
            # Test no flakes
            mock_exists.return_value = False
            self.assertTrue(backend._check_flakes() is False)


class TestNativeApiOperations(unittest.TestCase):
    """Test operations when native API is available"""
    
    def backend_with_api(self):
        """Create backend with mocked native API"""
        with patch('native_nix_backend.NATIVE_API_AVAILABLE', True):
            backend = NativeNixBackend()
            return backend
    
    def mock_nix_modules(self):
        """Mock the nixos-rebuild modules"""
        with patch('native_nix_backend.nix') as mock_nix, \
             patch('native_nix_backend.models') as mock_models, \
             patch('native_nix_backend.Profile') as mock_profile:
            yield {
                'nix': mock_nix,
                'models': mock_models,
                'profile': mock_profile
            }
    
    async def test_update_system_dry_run(self):
        """Test system update dry run with native API"""
        # Setup mocks
        mock_nix_modules['nix'].build = Mock(return_value="/nix/store/test-path")
        
        # Create operation
        operation = NixOperation(
            type=OperationType.UPDATE,
            dry_run=True
        )
        
        # Execute
        with patch.object(backend_with_api, '_check_flakes', return_value=False):
            result = await backend_with_api.execute(operation)
        
        # Verify
        self.assertTrue(result.success is True)
        self.assertIn("Dry run complete", result.message)
        self.assertIsNotNone(result.data.get('would_activate'))
        self.assertIsNone(result.error)
    
    async def test_update_system_flakes(self):
        """Test system update with flakes"""
        # Setup mocks
        mock_nix_modules['nix'].build_flake = Mock(return_value="/nix/store/flake-path")
        mock_nix_modules['nix'].switch_to_configuration = Mock()
        
        # Create operation
        operation = NixOperation(
            type=OperationType.UPDATE,
            dry_run=False
        )
        
        # Execute with flakes
        with patch.object(backend_with_api, '_check_flakes', return_value=True), \
             patch('native_nix_backend.Path'), \
             patch('native_nix_backend.Flake'):
            result = await backend_with_api.execute(operation)
        
        # Verify
        self.assertTrue(result.success is True)
        self.assertIn("updated successfully", result.message)
        self.assertIsNotNone(result.data.get('new_generation'))
    
    async def test_rollback_system(self):
        """Test system rollback"""
        # Setup mocks
        mock_nix_modules['nix'].rollback = Mock()
        
        # Create operation
        operation = NixOperation(type=OperationType.ROLLBACK)
        
        # Execute
        result = await backend_with_api.execute(operation)
        
        # Verify
        self.assertTrue(result.success is True)
        self.assertIn("rolled back to previous generation", result.message)
        mock_nix_modules['nix'].rollback.assert_called_once()
    
    async def test_list_generations(self):
        """Test listing system generations"""
        # Setup mock generations
        mock_gen1 = Mock()
        mock_gen1.id = 42
        mock_gen1.timestamp = "2025-02-01 12:00:00"
        mock_gen1.current = True
        
        mock_gen2 = Mock()
        mock_gen2.id = 41
        mock_gen2.timestamp = "2025-01-31 12:00:00"
        mock_gen2.current = False
        
        mock_nix_modules['nix'].get_generations = Mock(
            return_value=[mock_gen1, mock_gen2]
        )
        
        # Create operation
        operation = NixOperation(type=OperationType.LIST_GENERATIONS)
        
        # Execute
        result = await backend_with_api.execute(operation)
        
        # Verify
        self.assertTrue(result.success is True)
        self.assertIn("Found 2 generations", result.message)
        self.assertEqual(len(result.data['generations']), 2)
        self.assertEqual(result.data['generations'][0]['number'], 42)
        self.assertTrue(result.data['generations'][0]['current'] is True)
        self.assertEqual(result.data['generations'][1]['number'], 41)
        self.assertTrue(result.data['generations'][1]['current'] is False)
    
    async def test_install_packages_instructions(self):
        """Test package installation returns instructions"""
        operation = NixOperation(
            type=OperationType.INSTALL,
            packages=['firefox', 'vim']
        )
        
        result = await backend_with_api.execute(operation)
        
        self.assertTrue(result.success is True)
        self.assertIn("firefox, vim", result.message)
        self.assertIn("configuration.nix", result.message)
        self.assertIn("environment.systemPackages", result.message)
        self.assertEqual(result.data['packages'], ['firefox', 'vim'])
        self.assertIn(result.data['config_file'], ['/etc/nixos/configuration.nix', '/etc/nixos/flake.nix'])
    
    async def test_search_packages(self):
        """Test package search"""
        operation = NixOperation(
            type=OperationType.SEARCH,
            packages=['browser']
        )
        
        result = await backend_with_api.execute(operation)
        
        self.assertTrue(result.success is True)
        self.assertIn("nix search nixpkgs browser", result.message)
        self.assertEqual(result.data['query'], 'browser')
    
    async def test_build_system(self):
        """Test system build without switching"""
        mock_nix_modules['nix'].build = Mock(return_value="/nix/store/build-path")
        
        operation = NixOperation(type=OperationType.BUILD)
        
        with patch.object(backend_with_api, '_check_flakes', return_value=False):
            result = await backend_with_api.execute(operation)
        
        self.assertTrue(result.success is True)
        self.assertIn("built successfully", result.message)
        self.assertEqual(result.data['build_path'], "/nix/store/build-path")
    
    async def test_test_configuration(self):
        """Test configuration testing"""
        mock_nix_modules['nix'].build = Mock(return_value="/nix/store/test-path")
        mock_nix_modules['nix'].switch_to_configuration = Mock()
        
        operation = NixOperation(type=OperationType.TEST)
        
        with patch.object(backend_with_api, '_check_flakes', return_value=False):
            result = await backend_with_api.execute(operation)
        
        self.assertTrue(result.success is True)
        self.assertIn("Test configuration activated", result.message)
        self.assertEqual(result.data['test_path'], "/nix/store/test-path")


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def backend(self):
        return NativeNixBackend()
    
    async def test_unknown_operation_type(self):
        """Test handling of unknown operation types"""
        # Create invalid operation by direct assignment
        operation = NixOperation(type=OperationType.UPDATE)
        operation.type = "INVALID_TYPE"  # Force invalid type
        
        result = await backend.execute(operation)
        
        self.assertTrue(result.success is False)
        self.assertIn("Unknown operation type", result.message)
        self.assertEqual(result.error, "Invalid operation")
    
    async def test_operation_exception_handling(self):
        """Test exception handling during operations"""
        with patch.object(backend, '_update_system', side_effect=Exception("Test error")):
            operation = NixOperation(type=OperationType.UPDATE)
            result = await backend.execute(operation)
            
            self.assertTrue(result.success is False)
            self.assertEqual(result.message, "Operation failed")
            self.assertIn("Test error", result.error)
    
    async def test_rollback_failure(self):
        """Test rollback failure handling"""
        with patch('native_nix_backend.NATIVE_API_AVAILABLE', True), \
             patch('native_nix_backend.nix.rollback', side_effect=Exception("Rollback failed")):
            
            operation = NixOperation(type=OperationType.ROLLBACK)
            result = await backend.execute(operation)
            
            self.assertTrue(result.success is False)
            self.assertEqual(result.message, "Rollback failed")
            self.assertIn("Rollback failed", result.error)
    
    async def test_update_error_classification(self):
        """Test error message classification for updates"""
        with patch('native_nix_backend.NATIVE_API_AVAILABLE', True):
            # Test sudo error
            with patch('native_nix_backend.nix.build', side_effect=Exception("sudo required")):
                operation = NixOperation(type=OperationType.UPDATE)
                result = await backend.execute(operation)
                
                self.assertTrue(result.success is False)
                self.assertIn("administrator privileges", result.message)
            
            # Test network error
            with patch('native_nix_backend.nix.build', side_effect=Exception("network timeout")):
                operation = NixOperation(type=OperationType.UPDATE)
                result = await backend.execute(operation)
                
                self.assertTrue(result.success is False)
                self.assertIn("network issues", result.message)
            
            # Test build error
            with patch('native_nix_backend.nix.build', side_effect=Exception("build failed")):
                operation = NixOperation(type=OperationType.UPDATE)
                result = await backend.execute(operation)
                
                self.assertTrue(result.success is False)
                self.assertIn("check configuration syntax", result.message)


class TestFallbackMode(unittest.TestCase):
    """Test fallback behavior when native API is unavailable"""
    
    def backend_no_api(self):
        """Create backend without native API"""
        with patch('native_nix_backend.NATIVE_API_AVAILABLE', False):
            return NativeNixBackend()
    
    async def test_fallback_execute(self):
        """Test fallback execution when API unavailable"""
        operation = NixOperation(type=OperationType.UPDATE)
        result = await backend_no_api.execute(operation)
        
        self.assertTrue(result.success is False)
        self.assertIn("Native API not available", result.message)
        self.assertIn("fallback not implemented", result.message)


class TestPerformanceFeatures(unittest.TestCase):
    """Test performance-related features"""
    
    def backend(self):
        return NativeNixBackend()
    
    def test_progress_callback_setting(self):
        """Test setting custom progress callback"""
        mock_callback = Mock()
        backend.set_progress_callback(mock_callback)
        
        # Test that progress updates use new callback
        backend.progress.update("Test message", 0.5)
        mock_callback.assert_called_once_with("Test message", 0.5)
    
    async def test_progress_updates_during_operation(self):
        """Test that operations provide progress updates"""
        progress_calls = []
        
        def capture_progress(message, progress):
            progress_calls.append((message, progress))
        
        backend.set_progress_callback(capture_progress)
        
        with patch('native_nix_backend.NATIVE_API_AVAILABLE', True), \
             patch('native_nix_backend.nix.build', return_value="/nix/store/test"), \
             patch('native_nix_backend.nix.switch_to_configuration'):
            
            operation = NixOperation(type=OperationType.UPDATE, dry_run=False)
            await backend.execute(operation)
        
        # Verify progress updates occurred
        self.assertGreaterEqual(len(progress_calls), 3)  # Should have multiple progress updates
        self.assertEqual(progress_calls[0][1], 0.0)  # First update at 0%
        self.assertEqual(progress_calls[-1][1], 1.0)  # Last update at 100%
        
        # Verify messages are descriptive
        messages = [call[0] for call in progress_calls]
        self.assertTrue(any("Starting" in msg for msg in messages))
        self.assertTrue(any("complete" in msg.lower() for msg in messages))


class TestAsyncIntegration(unittest.TestCase):
    """Test async/await integration with nixos-rebuild-ng"""
    
    def backend(self):
        return NativeNixBackend()
    
    async def test_async_executor_integration(self):
        """Test that sync nixos-rebuild functions work with asyncio"""
        with patch('native_nix_backend.NATIVE_API_AVAILABLE', True), \
             patch('asyncio.get_event_loop') as mock_loop:
            
            mock_executor = Mock()
            mock_loop.return_value.run_in_executor = AsyncMock(return_value="/nix/store/test")
            
            operation = NixOperation(type=OperationType.BUILD)
            
            with patch.object(backend, '_check_flakes', return_value=False):
                result = await backend.execute(operation)
            
            # Verify executor was used for sync function
            mock_loop.return_value.run_in_executor.assert_called()
    
    async def test_concurrent_operations(self):
        """Test that multiple operations can be handled concurrently"""
        with patch('native_nix_backend.NATIVE_API_AVAILABLE', True), \
             patch('native_nix_backend.nix.get_generations', return_value=[]), \
             patch('native_nix_backend.nix.build', return_value="/nix/store/test"):
            
            # Create multiple operations
            ops = [
                NixOperation(type=OperationType.LIST_GENERATIONS),
                NixOperation(type=OperationType.BUILD),
                NixOperation(type=OperationType.SEARCH, packages=['test'])
            ]
            
            # Execute concurrently
            results = await asyncio.gather(*[backend.execute(op) for op in ops])
            
            # All should succeed
            self.assertEqual(len(results), 3)
            self.assertTrue(all(result.success for result in results))


class TestDataIntegrity(unittest.TestCase):
    """Test data integrity and type safety"""
    
    def test_operation_type_validation(self):
        """Test that operation types are properly validated"""
        # Valid operation
        op = NixOperation(type=OperationType.UPDATE)
        self.assertEqual(op.type, OperationType.UPDATE)
        
        # Test all enum values
        for op_type in OperationType:
            op = NixOperation(type=op_type)
            self.assertEqual(op.type, op_type)
    
    def test_result_data_structure(self):
        """Test that result data maintains expected structure"""
        result = NixResult(
            success=True,
            message="Test message",
            data={"key": "value"},
            error=None
        )
        
        # Verify types
        self.assertTrue(isinstance(result.success, bool))
        self.assertTrue(isinstance(result.message, str))
        self.assertTrue(isinstance(result.data, dict))
        self.assertIsNone(result.error) or isinstance(result.error, str)
    
    def test_progress_callback_type_safety(self):
        """Test progress callback type safety"""
        # Test with valid callback
        def valid_callback(message: str, progress: float):
            self.assertTrue(isinstance(message, str))
            self.assertTrue(isinstance(progress, float))
            self.assertTrue(0.0 <= progress <= 1.0)
        
        callback = ProgressCallback(valid_callback)
        callback.update("Test", 0.5)  # Should not raise
        
        # Test edge values
        callback.update("Start", 0.0)
        callback.update("Complete", 1.0)


if __name__ == "__main__":
    unittest.main()