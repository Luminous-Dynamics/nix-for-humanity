#!/usr/bin/env python3
"""
Tests for the Response system.
Following Living Documentation pattern - tests explain WHY they exist.
"""

import unittest
from unittest.mock import Mock, patch

from luminous_nix.core.responses import Response


class TestResponse(unittest.TestCase):
    """Test the Response dataclass and its behavior."""
    
    def test_response_creation_success(self):
        """
        Test creating a successful response.
        WHY: Responses are the primary output of our system - they must be reliable.
        """
        response = Response(
            success=True,
            text="Package firefox installed successfully",
            commands=["nix-env -iA nixos.firefox"],
            data={"package": "firefox", "version": "120.0"}
        )
        
        self.assertTrue(response.success)
        self.assertEqual(response.text, "Package firefox installed successfully")
        self.assertEqual(len(response.commands), 1)
        self.assertIn("package", response.data)
        
    def test_response_creation_failure(self):
        """
        Test creating a failure response.
        WHY: Error responses must convey clear information for debugging.
        """
        response = Response(
            success=False,
            text="Failed to install package",
            commands=[],
            data={
                "error": "Package not found",
                "suggestions": ["Try searching with: ask-nix search firefox"]
            }
        )
        
        self.assertFalse(response.success)
        self.assertEqual(response.text, "Failed to install package")
        self.assertEqual(len(response.commands), 0)
        self.assertIn("error", response.data)
        self.assertIn("suggestions", response.data)
        
    def test_response_with_empty_data(self):
        """
        Test response with minimal data.
        WHY: Not all responses need additional data - simple responses should work.
        """
        response = Response(
            success=True,
            text="System updated",
            commands=["nixos-rebuild switch"],
            data={}
        )
        
        self.assertTrue(response.success)
        self.assertEqual(response.data, {})
        
    def test_response_with_teaching_moment(self):
        """
        Test response that includes educational content.
        WHY: Following our Enhanced Error Teaching principle - errors should educate.
        """
        response = Response(
            success=False,
            text="Permission denied",
            commands=[],
            data={
                "error": "Cannot modify system configuration",
                "teaching": "This needs elevated privileges. Consider: sudo or configuration.nix",
                "learn_more": "https://nixos.org/manual/nixos/stable/#sec-configuration-file"
            }
        )
        
        self.assertFalse(response.success)
        self.assertIn("teaching", response.data)
        self.assertIn("elevated privileges", response.data["teaching"])
        
    def test_response_with_multiple_commands(self):
        """
        Test response with multiple commands executed.
        WHY: Complex operations may require multiple steps - we track them all.
        """
        response = Response(
            success=True,
            text="Development environment created",
            commands=[
                "nix-shell -p python3",
                "nix-shell -p nodejs",
                "nix-shell -p git"
            ],
            data={"environment": "web-dev"}
        )
        
        self.assertEqual(len(response.commands), 3)
        self.assertIn("python3", response.commands[0])
        
    def test_response_equality(self):
        """
        Test that identical responses are equal.
        WHY: Response comparison is needed for testing and caching.
        """
        response1 = Response(
            success=True,
            text="Test",
            commands=["cmd"],
            data={"key": "value"}
        )
        
        response2 = Response(
            success=True,
            text="Test",
            commands=["cmd"],
            data={"key": "value"}
        )
        
        self.assertEqual(response1, response2)
        
    def test_response_inequality(self):
        """
        Test that different responses are not equal.
        WHY: Ensure response comparison works correctly for different responses.
        """
        response1 = Response(
            success=True,
            text="Test 1",
            commands=["cmd1"],
            data={"key": "value1"}
        )
        
        response2 = Response(
            success=True,
            text="Test 2",
            commands=["cmd2"],
            data={"key": "value2"}
        )
        
        self.assertNotEqual(response1, response2)
        
    def test_response_with_progress_data(self):
        """
        Test response that includes progress information.
        WHY: Long-running operations need progress feedback.
        """
        response = Response(
            success=True,
            text="Building configuration...",
            commands=["nixos-rebuild switch"],
            data={
                "progress": 45,
                "stage": "downloading",
                "estimated_time": "2 minutes remaining"
            }
        )
        
        self.assertEqual(response.data["progress"], 45)
        self.assertEqual(response.data["stage"], "downloading")
        
    def test_response_with_warnings(self):
        """
        Test response that succeeded but has warnings.
        WHY: Operations can succeed with caveats - users need to know.
        """
        response = Response(
            success=True,
            text="Package installed with warnings",
            commands=["nix-env -iA nixos.package"],
            data={
                "warnings": [
                    "This package is marked as insecure",
                    "Consider using the newer version"
                ],
                "package": "old-package"
            }
        )
        
        self.assertTrue(response.success)
        self.assertIn("warnings", response.data)
        self.assertEqual(len(response.data["warnings"]), 2)


class TestResponsePatterns(unittest.TestCase):
    """Test common response patterns in our system."""
    
    def test_search_response_pattern(self):
        """
        Test the pattern for search result responses.
        WHY: Search responses have a specific structure users depend on.
        """
        response = Response(
            success=True,
            text="Found 3 packages matching 'editor'",
            commands=["nix search nixpkgs editor"],
            data={
                "results": [
                    {"name": "vim", "description": "Vi IMproved"},
                    {"name": "emacs", "description": "Extensible editor"},
                    {"name": "nano", "description": "Simple editor"}
                ],
                "count": 3,
                "query": "editor"
            }
        )
        
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(len(response.data["results"]), 3)
        self.assertEqual(response.data["query"], "editor")
        
    def test_generation_response_pattern(self):
        """
        Test the pattern for system generation responses.
        WHY: Generation management is critical for system recovery.
        """
        response = Response(
            success=True,
            text="Current generation: 42",
            commands=["nixos-rebuild list-generations"],
            data={
                "current": 42,
                "generations": [
                    {"number": 42, "date": "2024-01-15", "current": True},
                    {"number": 41, "date": "2024-01-14", "current": False},
                    {"number": 40, "date": "2024-01-13", "current": False}
                ],
                "total": 3
            }
        )
        
        self.assertEqual(response.data["current"], 42)
        self.assertEqual(response.data["total"], 3)
        self.assertTrue(response.data["generations"][0]["current"])
        
    def test_configuration_response_pattern(self):
        """
        Test the pattern for configuration generation responses.
        WHY: Generated configurations need specific formatting.
        """
        response = Response(
            success=True,
            text="Configuration generated",
            commands=[],
            data={
                "type": "configuration",
                "config": "{ pkgs, ... }: {\n  environment.systemPackages = with pkgs; [ vim ];\n}",
                "preview": True,
                "file_path": "/etc/nixos/configuration.nix"
            }
        )
        
        self.assertEqual(response.data["type"], "configuration")
        self.assertIn("environment.systemPackages", response.data["config"])
        self.assertTrue(response.data["preview"])


if __name__ == '__main__':
    unittest.main()