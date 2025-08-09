#!/usr/bin/env python3
"""
Comprehensive unit tests for NixOSIntegration module
Tests the bridge between high-level intents and NixOS operations
"""

import unittest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path
import sys
import tempfile
import json

# Add backend to path for imports
test_dir = Path(__file__).parent
backend_path = test_dir.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from nix_humanity.core.nix_integration import (
    NixOSIntegration,
    update_system,
    rollback_system,
    install_package
)


class TestNixOSIntegration(unittest.TestCase):
    """Test suite for NixOSIntegration class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock the NativeNixBackend import
        self.mock_backend_patcher = patch('core.nix_integration.NativeNixBackend')
        self.mock_backend_class = self.mock_backend_patcher.start()
        
        # Create mock backend instance
        self.mock_backend = Mock()
        self.mock_backend_class.return_value = self.mock_backend
        
        # Mock NATIVE_API_AVAILABLE
        self.native_api_patcher = patch('core.nix_integration.NATIVE_API_AVAILABLE', True)
        self.native_api_patcher.start()
        
        # Create integration instance
        self.integration = NixOSIntegration()
        
    def tearDown(self):
        """Clean up patches"""
        self.mock_backend_patcher.stop()
        self.native_api_patcher.stop()
        
    def test_initialization(self):
        """Test NixOSIntegration initialization"""
        # Verify backend was created
        self.mock_backend_class.assert_called_once()
        
        # Verify initial state
        self.assertEqual(self.integration.operation_count, 0)
        self.assertTrue(self.integration.using_native_api)
        
    def test_initialization_with_progress_callback(self):
        """Test initialization with progress callback"""
        # Create new instance with callback
        callback = Mock()
        integration = NixOSIntegration(progress_callback=callback)
        
        # Verify callback was set
        self.mock_backend.set_progress_callback.assert_called_with(callback)
        
    def test_get_status(self):
        """Test getting integration status"""
        # Set operation count
        self.integration.operation_count = 5
        
        # Get status
        status = self.integration.get_status()
        
        # Verify status
        self.assertEqual(status["native_api_available"], True)
        self.assertEqual(status["operations_completed"], 5)
        self.assertEqual(status["backend"], "native")
        self.assertEqual(status["performance_boost"], "10x")
        
    def test_get_status_subprocess_mode(self):
        """Test status when native API is not available"""
        self.integration.using_native_api = False
        
        status = self.integration.get_status()
        
        self.assertEqual(status["backend"], "subprocess")
        self.assertEqual(status["performance_boost"], "1x")
        
    def test_execute_intent_update_system(self):
        """Test executing update_system intent"""
        # Mock the backend execute method
        mock_result = Mock()
        mock_result.success = True
        mock_result.message = "System updated successfully"
        mock_result.data = {"updated_packages": 5}
        mock_result.error = None
        
        self.mock_backend.execute = AsyncMock(return_value=mock_result)
        
        # Execute intent
        result = self.integration.execute_intent(
            "update_system",
            {"dry_run": False}
        )
        
        # Verify backend was called correctly
        self.mock_backend.execute.assert_called_once()
        call_args = self.mock_backend.execute.call_args[0][0]
        self.assertEqual(call_args.type.value, "update_system")  # OperationType.UPDATE
        self.assertFalse(call_args.dry_run)
        
        # Verify result
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "System updated successfully")
        self.assertEqual(result["intent"], "update_system")
        self.assertTrue(result["native_api"])
        
        # Verify educational context
        self.assertIn("education", result)
        self.assertIn("what_happened", result["education"])
        self.assertIn("reproducibility", result["education"]["why_it_matters"])
        
        # Verify operation count increased
        self.assertEqual(self.integration.operation_count, 1)
        
    def test_execute_intent_rollback_system(self):
        """Test executing rollback_system intent"""
        mock_result = Mock()
        mock_result.success = True
        mock_result.message = "Rolled back to generation 42"
        mock_result.data = {"generation": 42}
        mock_result.error = None
        
        self.mock_backend.execute = AsyncMock(return_value=mock_result)
        
        result = self.integration.execute_intent("rollback_system", {})
        
        # Verify operation type
        call_args = self.mock_backend.execute.call_args[0][0]
        self.assertEqual(call_args.type.value, "rollback")
        
        # Verify educational context for rollback
        self.assertIn("education", result)
        self.assertIn("instant and safe", result["education"]["why_it_matters"])
        
    def test_execute_intent_install_package(self):
        """Test executing install_package intent"""
        mock_result = Mock()
        mock_result.success = True
        mock_result.message = "Instructions generated for firefox"
        mock_result.data = {"config_snippet": "environment.systemPackages = [ pkgs.firefox ];"}
        mock_result.error = None
        
        self.mock_backend.execute = AsyncMock(return_value=mock_result)
        
        result = self.integration.execute_intent(
            "install_package",
            {"package": "firefox"}
        )
        
        # Verify package was passed correctly
        call_args = self.mock_backend.execute.call_args[0][0]
        self.assertEqual(call_args.type.value, "install_package")
        self.assertEqual(call_args.packages, ["firefox"])
        
        # Verify educational context
        self.assertIn("declarative configuration", result["education"]["why_it_matters"])
        
    def test_execute_intent_with_multiple_packages(self):
        """Test executing intent with multiple packages"""
        mock_result = Mock()
        mock_result.success = True
        mock_result.message = "Success"
        mock_result.data = {}
        mock_result.error = None
        
        self.mock_backend.execute = AsyncMock(return_value=mock_result)
        
        self.integration.execute_intent(
            "install_package",
            {"packages": ["vim", "emacs", "neovim"]}
        )
        
        call_args = self.mock_backend.execute.call_args[0][0]
        self.assertEqual(call_args.packages, ["vim", "emacs", "neovim"])
        
    def test_execute_intent_with_error(self):
        """Test handling errors during execution"""
        # Mock backend raising exception
        self.mock_backend.execute = AsyncMock(
            side_effect=Exception("Network connection failed")
        )
        
        result = self.integration.execute_intent(
            "update_system",
            {"dry_run": False}
        )
        
        # Verify error handling
        self.assertFalse(result["success"])
        self.assertIn("Network connection failed", result["message"])
        self.assertIn("Network connection failed", result["error"])
        self.assertIn("suggestion", result)
        self.assertIn("internet connection", result["suggestion"])
        
    def test_execute_intent_with_backend_error(self):
        """Test handling backend error results"""
        mock_result = Mock()
        mock_result.success = False
        mock_result.message = "Build failed"
        mock_result.data = {}
        mock_result.error = "error: attribute 'firefx' missing"
        
        self.mock_backend.execute = AsyncMock(return_value=mock_result)
        
        result = self.integration.execute_intent(
            "install_package",
            {"package": "firefx"}  # Typo
        )
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertIn("suggestion", result)
        
    def test_map_intent_to_operation(self):
        """Test mapping various intents to operations"""
        test_cases = [
            ("update_system", {}, "update_system"),
            ("rollback_system", {}, "rollback"),
            ("install_package", {"package": "vim"}, "install_package"),
            ("remove_package", {"package": "vim"}, "remove"),
            ("search_package", {"package": "firefox"}, "search_package"),
            ("build_system", {}, "build"),
            ("test_configuration", {}, "test"),
            ("list_generations", {}, "list_generations"),
            ("unknown_intent", {}, "build"),  # Default
        ]
        
        for intent, params, expected_type in test_cases:
            operation = self.integration._map_intent_to_operation(intent, params)
            self.assertEqual(operation.type.value, expected_type)
            
    def test_map_intent_with_dry_run(self):
        """Test dry run parameter mapping"""
        operation = self.integration._map_intent_to_operation(
            "update_system",
            {"dry_run": True}
        )
        
        self.assertTrue(operation.dry_run)
        
    def test_map_intent_with_options(self):
        """Test custom options mapping"""
        options = {"verbose": True, "show-trace": True}
        operation = self.integration._map_intent_to_operation(
            "build_system",
            {"options": options}
        )
        
        self.assertEqual(operation.options, options)
        
    def test_get_error_suggestion_permission(self):
        """Test error suggestion for permission errors"""
        suggestion = self.integration._get_error_suggestion(
            "Permission denied: cannot write to /etc/nixos"
        )
        
        self.assertIn("root privileges", suggestion)
        self.assertIn("sudo", suggestion)
        
    def test_get_error_suggestion_file_not_found(self):
        """Test error suggestion for file not found"""
        suggestion = self.integration._get_error_suggestion(
            "error: no such file or directory: configuration.nix"
        )
        
        self.assertIn("configuration.nix", suggestion)
        self.assertIn("exists", suggestion)
        
    def test_get_error_suggestion_build_failed(self):
        """Test error suggestion for build failures"""
        suggestion = self.integration._get_error_suggestion(
            "error: build failed with exit code 1"
        )
        
        self.assertIn("syntax errors", suggestion)
        self.assertIn("nixos-rebuild build", suggestion)
        
    def test_get_error_suggestion_network(self):
        """Test error suggestion for network issues"""
        suggestion = self.integration._get_error_suggestion(
            "error: unable to download 'https://cache.nixos.org/...': Network is unreachable"
        )
        
        self.assertIn("internet connection", suggestion)
        
    def test_get_error_suggestion_disk_space(self):
        """Test error suggestion for disk space issues"""
        suggestion = self.integration._get_error_suggestion(
            "error: writing to file: No space left on device"
        )
        
        self.assertIn("disk space", suggestion.lower())
        self.assertIn("nix-collect-garbage", suggestion)
        
    def test_get_error_suggestion_generic(self):
        """Test generic error suggestion"""
        suggestion = self.integration._get_error_suggestion(
            "some unknown error occurred"
        )
        
        self.assertIn("NixOS manual", suggestion)
        self.assertIn("community", suggestion)
        
    def test_get_system_info_success(self):
        """Test getting system information successfully"""
        # Mock generations result
        mock_result = Mock()
        mock_result.success = True
        mock_result.data = {
            "generations": [
                {"generation": 40, "date": "2024-01-01", "current": False},
                {"generation": 41, "date": "2024-01-02", "current": False},
                {"generation": 42, "date": "2024-01-03", "current": True},
            ]
        }
        
        self.mock_backend.execute = AsyncMock(return_value=mock_result)
        
        # Mock NixOS version reading
        with patch('builtins.open', unittest.mock.mock_open(
            read_data='VERSION="24.05 (Uakari)"'
        )):
            info = self.integration.get_system_info()
        
        self.assertEqual(info["nixos_version"], "24.05 (Uakari)")
        self.assertEqual(info["total_generations"], 3)
        self.assertEqual(info["current_generation"]["generation"], 42)
        self.assertTrue(info["native_api"])
        
    def test_get_system_info_no_current_generation(self):
        """Test system info when no current generation is marked"""
        mock_result = Mock()
        mock_result.success = True
        mock_result.data = {
            "generations": [
                {"generation": 40, "date": "2024-01-01", "current": False},
                {"generation": 41, "date": "2024-01-02", "current": False},
            ]
        }
        
        self.mock_backend.execute = AsyncMock(return_value=mock_result)
        
        info = self.integration.get_system_info()
        
        self.assertIsNone(info["current_generation"])
        self.assertEqual(info["total_generations"], 2)
        
    def test_get_system_info_error(self):
        """Test handling errors when getting system info"""
        self.mock_backend.execute = AsyncMock(
            side_effect=Exception("Failed to list generations")
        )
        
        info = self.integration.get_system_info()
        
        self.assertIn("error", info)
        self.assertIn("Failed to list generations", info["error"])
        self.assertTrue(info["native_api"])
        
    def test_get_nixos_version(self):
        """Test reading NixOS version from os-release"""
        with patch('builtins.open', unittest.mock.mock_open(
            read_data='NAME="NixOS"\nVERSION="24.05 (Uakari)"'
        )):
            version = self.integration._get_nixos_version()
            self.assertEqual(version, "24.05 (Uakari)")
            
    def test_get_nixos_version_file_not_found(self):
        """Test handling missing os-release file"""
        with patch('builtins.open', side_effect=FileNotFoundError()):
            version = self.integration._get_nixos_version()
            self.assertEqual(version, "Unknown")
            
    def test_get_nixos_version_malformed(self):
        """Test handling malformed os-release file"""
        with patch('builtins.open', unittest.mock.mock_open(
            read_data='NAME=NixOS'
        )):
            version = self.integration._get_nixos_version()
            self.assertEqual(version, "Unknown")  # No VERSION field


class TestConvenienceFunctions(unittest.TestCase):
    """Test the convenience functions"""
    
    def setUp(self):
        """Set up for integration tests"""
        self.mock_backend_patcher = patch('core.nix_integration.NativeNixBackend')
        self.mock_backend_class = self.mock_backend_patcher.start()
        self.mock_backend = Mock()
        self.mock_backend_class.return_value = self.mock_backend
        
        self.native_api_patcher = patch('core.nix_integration.NATIVE_API_AVAILABLE', True)
        self.native_api_patcher.start()
        
    def tearDown(self):
        """Clean up patches"""
        self.mock_backend_patcher.stop()
        self.native_api_patcher.stop()
        
    def test_full_update_workflow(self):
        """Test a complete system update workflow"""
        integration = NixOSIntegration()
        
        # Step 1: Check system info
        mock_info_result = Mock()
        mock_info_result.success = True
        mock_info_result.data = {
            "generations": [
                {"generation": 42, "date": "2024-01-03", "current": True}
            ]
        }
        
        # Step 2: Do dry run
        mock_dry_result = Mock()
        mock_dry_result.success = True
        mock_dry_result.message = "Would update 5 packages"
        mock_dry_result.data = {"packages_to_update": 5}
        mock_dry_result.error = None
        
        # Step 3: Actual update
        mock_update_result = Mock()
        mock_update_result.success = True
        mock_update_result.message = "System updated"
        mock_update_result.data = {"new_generation": 43}
        mock_update_result.error = None
        
        # Set up mock returns in order
        self.mock_backend.execute = AsyncMock(
            side_effect=[mock_info_result, mock_dry_result, mock_update_result]
        )
        
        # Execute workflow
        info = integration.get_system_info()
        self.assertEqual(info["current_generation"]["generation"], 42)
        
        dry_result = integration.execute_intent(
            "update_system",
            {"dry_run": True}
        )
        self.assertTrue(dry_result["success"])
        
        update_result = integration.execute_intent(
            "update_system",
            {"dry_run": False}
        )
        self.assertTrue(update_result["success"])
        
        # Verify operation count
        self.assertEqual(integration.operation_count, 2)  # dry run + actual
        
    def test_error_recovery_workflow(self):
        """Test error recovery workflow"""
        integration = NixOSIntegration()
        
        # First attempt fails
        self.mock_backend.execute = AsyncMock(
            side_effect=Exception("Network unreachable")
        )
        
        result1 = integration.execute_intent("update_system", {})
        self.assertFalse(result1["success"])
        self.assertIn("internet connection", result1["suggestion"])
        
        # User fixes network, second attempt succeeds
        mock_success = Mock()
        mock_success.success = True
        mock_success.message = "Success"
        mock_success.data = {}
        mock_success.error = None
        
        self.mock_backend.execute = AsyncMock(return_value=mock_success)
        
        result2 = integration.execute_intent("update_system", {})
        self.assertTrue(result2["success"])


if __name__ == "__main__":
    # Run async tests properly
    unittest.main()