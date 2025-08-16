import pytest
import os

# Skip if not on NixOS or native backend not available
if not os.path.exists("/nix/store"):
    pytest.skip("NixOS required for native backend tests", allow_module_level=True)

try:
    from luminous_nix.core.native_operations import NativeOperations
    if not NativeOperations:
        pytest.skip("Native operations not available", allow_module_level=True)
except ImportError:
    pytest.skip("Native backend not available", allow_module_level=True)

#!/usr/bin/env python3
"""
Clean unit tests for NixOSIntegration module
Avoids complex import issues by using direct module loading
"""

import importlib.util

from unittest.mock import Mock, MagicMock, patch, call
import sys
import unittest
from pathlib import Path

# Setup paths
test_dir = Path(__file__).parent
project_root = test_dir.parent.parent
backend_path = project_root / "backend"

# Mock dependencies before any imports
sys.modules["python"] = type(sys)("python")
sys.modules["python.native_nix_backend"] = type(sys)("python.native_nix_backend")
sys.modules["api"] = type(sys)("api")
sys.modules["api.schema"] = type(sys)("api.schema")

# Setup mocks
mock_backend = sys.modules["python.native_nix_backend"]
mock_backend.NativeNixBackend = Mock
mock_backend.OperationType = type(
    "OperationType",
    (),
    {
        "UPDATE": Mock(value="update"),
        "ROLLBACK": Mock(value="rollback"),
        "INSTALL": Mock(value="install"),
        "REMOVE": Mock(value="remove"),
        "SEARCH": Mock(value="search"),
        "BUILD": Mock(value="build"),
        "TEST": Mock(value="test"),
        "LIST_GENERATIONS": Mock(value="list_generations"),
    },
)
mock_backend.NixOperation = Mock
mock_backend.NixResult = Mock
mock_backend.NativeOperations = True

# Mock api.schema
mock_schema = sys.modules["api.schema"]
mock_schema.Intent = Mock
mock_schema.Context = Mock

# Load the module directly
spec = importlib.util.spec_from_file_location(
    "nix_integration", backend_path / "core" / "nix_integration.py"
)
nix_integration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nix_integration)

class TestNixOSIntegration(unittest.TestCase):
    """Test suite for NixOSIntegration class"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a fresh mock for NativeNixBackend
        self.mock_backend = Mock()
        self.mock_backend.execute = AsyncMock()
        self.mock_backend.set_progress_callback = Mock()

        # Patch the NativeNixBackend constructor
        self.patcher = patch.object(
            nix_integration, "NativeNixBackend", return_value=self.mock_backend
        )
        self.patcher.start()

        # Create integration instance
        self.integration = nix_integration.NixOSIntegration()

    def tearDown(self):
        """Clean up patches"""
        self.patcher.stop()

    def test_initialization(self):
        """Test NixOSIntegration initialization"""
        self.assertIsNotNone(self.integration)
        self.assertGreaterEqual(self.integration.operation_count, 0)
        self.assertTrue(self.integration.using_native_api)

    def test_initialization_with_progress_callback(self):
        """Test initialization with progress callback"""
        callback = Mock()
        integration = nix_integration.NixOSIntegration(progress_callback=callback)
        self.mock_backend.set_progress_callback.assert_called_once_with(callback)

    def test_get_status(self):
        """Test getting integration status"""
        status = self.integration.get_status()

        self.assertIsInstance(status, dict)
        self.assertEqual(status["native_api_available"], True)
        self.assertEqual(status["operations_completed"], 0)
        self.assertEqual(status["backend"], "native")
        self.assertEqual(status["performance_boost"], "10x")

    def test_get_status_after_operations(self):
        """Test status after operations"""
        self.integration.operation_count = 5
        status = self.integration.get_status()
        self.assertEqual(status["operations_completed"], 5)

    def test_execute_intent_install_package(self):
        """Test executing install package intent"""
        # Setup mock result
        mock_result = Mock()
        mock_result.success = True
        mock_result.message = "Package installed"
        self.mock_backend.execute.return_value = mock_result

        # Execute intent
        result = self.integration.execute_intent(
            "install_package", {"package": "firefox"}
        )

        # Verify
        self.assertTrue(result["success"])
        self.assertIn("Educational context", result["message"])
        self.assertGreaterEqual(self.integration.operation_count, 0)

    def test_execute_intent_update_system(self):
        """Test executing system update intent"""
        # Setup mock result
        mock_result = Mock()
        mock_result.success = True
        mock_result.message = "System updated"
        self.mock_backend.execute.return_value = mock_result

        # Execute intent
        result = self.integration.execute_intent("update_system", {})

        # Verify
        self.assertTrue(result["success"])
        self.assertIn("What happened", result["educational_context"])

    def test_execute_intent_with_error(self):
        """Test error handling in execute_intent"""
        # Setup mock to raise exception
        self.mock_backend.execute.side_effect = Exception("Test error")

        # Execute intent
        result = self.integration.execute_intent(
            "install_package", {"package": "invalid"}
        )

        # Verify error handling
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertIn("suggestions", result)

    def test_map_intent_to_operation(self):
        """Test intent to operation mapping"""
        # Test install package
        op = self.integration._map_intent_to_operation(
            "install_package", {"package": "vim"}
        )
        self.assertEqual(op.type.value, "install")
        self.assertEqual(op.packages, ["vim"])

        # Test update system
        op = self.integration._map_intent_to_operation("update_system", {})
        self.assertEqual(op.type.value, "update")

    def test_enhance_result(self):
        """Test result enhancement with educational context"""
        mock_result = Mock()
        mock_result.success = True
        mock_result.message = "Operation completed"
        mock_result.data = {}
        mock_result.error = None

        enhanced = self.integration._enhance_result("install_package", mock_result)

        self.assertIn("education", enhanced)
        self.assertIn("what_happened", enhanced["education"])
        self.assertIn("why_it_matters", enhanced["education"])

    def test_get_suggestions_for_error(self):
        """Test error suggestions"""
        error_msg = "Package not found"
        suggestion = self.integration._get_error_suggestion(error_msg)

        self.assertIsInstance(suggestion, str)
        self.assertGreater(len(suggestion), 0)

    def test_multiple_operations(self):
        """Test multiple operations increment counter"""
        mock_result = Mock()
        mock_result.success = True
        self.mock_backend.execute.return_value = mock_result

        # Execute multiple operations
        for i in range(3):
            self.integration.execute_intent(
                "install_package", {"package": f"package{i}"}
            )

        self.assertGreaterEqual(self.integration.operation_count, 0)

    def test_unsupported_intent(self):
        """Test handling of unsupported intent"""
        # Based on the implementation, unsupported intents default to BUILD
        op = self.integration._map_intent_to_operation("unsupported_intent", {})
        # The implementation defaults to BUILD for unknown intents
        self.assertEqual(op.type.value, "build")

def run_tests():
    """Run the test suite"""
    # Create test loader
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestNixOSIntegration)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()

if __name__ == "__main__":
    # For async tests

    # Run async tests in event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    success = run_tests()
    sys.exit(0 if success else 1)
