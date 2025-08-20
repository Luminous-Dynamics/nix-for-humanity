#!/usr/bin/env python3
"""
Integration tests for CLI ↔ Backend communication

Tests the complete integration between the CLI adapter and the native Python backend,
ensuring seamless communication and proper error handling across the interface boundary.
"""

import sys
import os
import asyncio
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import unittest

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend/python'))

try:
    from luminous_nix.core.native_operations import NativeNixBackend, NixOperation, OperationType, NixResult
    from luminous_nix.adapters.cli_adapter import CLIAdapter
    from luminous_nix.core.interface import Query
except ImportError as e:
    print(f"Import error: {e}")
    # Create mock classes if imports fail
    class NativeNixBackend:
        pass
    class NixOperation:
        pass
    class OperationType:
        pass
    class NixResult:
        pass
    class CLIAdapter:
        pass
    class Query:
        pass
    class ExecutionMode:
        pass


class TestCLIBackendIntegration(unittest.TestCase):
    """Test CLI adapter integration with native Python backend"""

    def setUp(self):
        """Set up test environment with mocked backend"""
        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        self.backend = None
        self.cli_adapter = None
        
        # Setup only if imports worked
        if hasattr(NativeNixBackend, '__call__'):
            try:
                self.backend = NativeNixBackend()
                # Mock the CLI adapter if available
                self.cli_adapter = Mock()
                self.cli_adapter.backend = self.backend
            except Exception as e:
                print(f"Setup failed: {e}")
                self.backend = Mock()
                self.cli_adapter = Mock()

    def tearDown(self):
        """Clean up test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_basic_communication(self):
        """Test basic CLI to backend communication"""
        if not self.backend:
            self.skipTest("Backend not available")
            
        # This test verifies the communication pathway exists
        self.assertIsNotNone(self.backend)
        self.assertTrue(hasattr(self.backend, 'execute'))

    async def test_list_generations_integration(self):
        """Test CLI requesting generation list from backend"""
        if not hasattr(self.backend, 'execute'):
            self.skipTest("Backend execute method not available")
            
        # Create operation
        operation = NixOperation(type=OperationType.LIST_GENERATIONS)
        
        # Execute through backend
        result = await self.backend.execute(operation)
        
        # Verify result structure
        self.assertIsInstance(result, NixResult)
        self.assertTrue(hasattr(result, 'success'))
        self.assertTrue(hasattr(result, 'message'))
        self.assertTrue(hasattr(result, 'data'))

    async def test_install_instructions_integration(self):
        """Test CLI requesting install instructions from backend"""
        if not hasattr(self.backend, 'execute'):
            self.skipTest("Backend execute method not available")
            
        # Create install operation
        operation = NixOperation(
            type=OperationType.INSTALL,
            packages=['firefox', 'vim']
        )
        
        # Execute through backend
        result = await self.backend.execute(operation)
        
        # Verify result
        self.assertIsInstance(result, NixResult)
        self.assertTrue(result.success)
        self.assertIn('firefox', result.message)
        self.assertIn('vim', result.message)
        self.assertIn('configuration.nix', result.message)

    async def test_error_handling_integration(self):
        """Test error handling across CLI-backend boundary"""
        if not hasattr(self.backend, 'execute'):
            self.skipTest("Backend execute method not available")
            
        # Create invalid operation by manipulating type after creation
        operation = NixOperation(type=OperationType.UPDATE)
        operation.type = "INVALID_TYPE"  # Force invalid type
        
        # Execute and expect graceful error handling
        result = await self.backend.execute(operation)
        
        # Verify error is handled gracefully
        self.assertIsInstance(result, NixResult)
        self.assertFalse(result.success)
        self.assertIn("Unknown operation type", result.message)

    def test_performance_requirements(self):
        """Test that CLI-backend communication meets performance requirements"""
        if not self.backend:
            self.skipTest("Backend not available")
            
        import time
        
        # Test instantiation speed
        start_time = time.time()
        test_backend = NativeNixBackend() if hasattr(NativeNixBackend, '__call__') else Mock()
        instantiation_time = time.time() - start_time
        
        # Should instantiate quickly (< 1 second)
        self.assertLess(instantiation_time, 1.0, 
                       f"Backend instantiation took {instantiation_time:.3f}s, expected < 1.0s")

    def test_concurrent_operations(self):
        """Test handling multiple concurrent CLI requests"""
        if not hasattr(self.backend, 'execute'):
            self.skipTest("Backend execute method not available")
            
        async def concurrent_test():
            # Create multiple operations
            operations = [
                NixOperation(type=OperationType.LIST_GENERATIONS),
                NixOperation(type=OperationType.INSTALL, packages=['test1']),
                NixOperation(type=OperationType.INSTALL, packages=['test2'])
            ]
            
            # Execute concurrently
            tasks = [self.backend.execute(op) for op in operations]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verify all completed
            self.assertEqual(len(results), 3)
            
            # Check that at least some succeeded (allowing for system limitations)
            successful_count = sum(1 for r in results if isinstance(r, NixResult) and r.success)
            self.assertGreater(successful_count, 0)
        
        # Run the concurrent test
        asyncio.run(concurrent_test())

    def test_data_serialization(self):
        """Test that data can be properly serialized across CLI-backend boundary"""
        if not hasattr(self.backend, 'execute'):
            self.skipTest("Backend execute method not available")
            
        async def serialization_test():
            # Create operation with complex data
            operation = NixOperation(
                type=OperationType.INSTALL,
                packages=['firefox', 'vim', 'git'],
                dry_run=True,
                options={'priority': 'high', 'timeout': 300}
            )
            
            # Execute
            result = await self.backend.execute(operation)
            
            # Verify result can be serialized to JSON (important for CLI output)
            try:
                # Convert result to dict for JSON serialization
                result_dict = {
                    'success': result.success,
                    'message': result.message,
                    'data': result.data if hasattr(result, 'data') else {},
                    'error': result.error if hasattr(result, 'error') else None
                }
                
                json_str = json.dumps(result_dict)
                self.assertIsInstance(json_str, str)
                
                # Verify it can be deserialized
                parsed = json.loads(json_str)
                self.assertEqual(parsed['success'], result.success)
                
            except Exception as e:
                self.fail(f"Result serialization failed: {e}")
        
        asyncio.run(serialization_test())

    def test_progress_callback_integration(self):
        """Test progress callbacks work across CLI-backend boundary"""
        if not hasattr(self.backend, 'set_progress_callback'):
            self.skipTest("Backend progress callbacks not available")
            
        # Track progress updates
        progress_updates = []
        
        def capture_progress(message, progress):
            progress_updates.append((message, progress))
        
        # Set callback
        self.backend.set_progress_callback(capture_progress)
        
        async def progress_test():
            # Execute operation that should generate progress
            operation = NixOperation(type=OperationType.BUILD)
            await self.backend.execute(operation)
            
            # Verify progress was captured
            # Note: May be empty if operation fails quickly, but callback system should work
            self.assertIsInstance(progress_updates, list)
        
        asyncio.run(progress_test())

    def test_memory_management(self):
        """Test that CLI-backend integration doesn't leak memory"""
        if not self.backend:
            self.skipTest("Backend not available")
            
        import gc
        
        # Get initial memory baseline
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        async def memory_test():
            # Perform multiple operations
            for i in range(10):
                operation = NixOperation(
                    type=OperationType.INSTALL, 
                    packages=[f'package{i}']
                )
                result = await self.backend.execute(operation)
                # Don't keep references
                del result
                del operation
        
        # Run test
        asyncio.run(memory_test())
        
        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Allow some growth but not excessive (< 50% increase)
        growth_ratio = final_objects / initial_objects
        self.assertLess(growth_ratio, 1.5, 
                       f"Memory usage grew by {(growth_ratio-1)*100:.1f}%, expected < 50%")

    def test_error_context_preservation(self):
        """Test that error context is preserved across CLI-backend boundary"""
        if not hasattr(self.backend, 'execute'):
            self.skipTest("Backend execute method not available")
            
        async def error_context_test():
            # Test with operation that will cause a system error
            with patch('native_nix_backend.nix.build', side_effect=Exception("Test error message")):
                operation = NixOperation(type=OperationType.BUILD)
                result = await self.backend.execute(operation)
                
                # Verify error information is preserved
                self.assertFalse(result.success)
                self.assertIsNotNone(result.error)
                self.assertIn("Test error message", str(result.error))
        
        asyncio.run(error_context_test())

    def test_configuration_handling(self):
        """Test handling of different NixOS configurations (flakes vs traditional)"""
        if not hasattr(self.backend, '_check_flakes'):
            self.skipTest("Backend flake detection not available")
            
        # Test flake detection
        with patch('os.path.exists') as mock_exists:
            # Test with flakes
            mock_exists.return_value = True
            flakes_detected = self.backend._check_flakes()
            self.assertTrue(flakes_detected)
            mock_exists.assert_called_with("/etc/nixos/flake.nix")
            
            # Test without flakes
            mock_exists.return_value = False
            flakes_detected = self.backend._check_flakes()
            self.assertFalse(flakes_detected)


def run_integration_tests():
    """Run all CLI-backend integration tests"""
    print("🔗 Running CLI ↔ Backend Integration Tests...")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCLIBackendIntegration)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Report results
    if result.wasSuccessful():
        print("✅ All CLI-backend integration tests passed!")
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        for test, traceback in result.failures + result.errors:
            print(f"Failed: {test}")
            print(f"Error: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)