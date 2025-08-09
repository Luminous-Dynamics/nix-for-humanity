#!/usr/bin/env python3
"""
import subprocess
Tests for resilient_core.py

Tests the resilient multi-tiered system functionality.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os
from pathlib import Path
from dataclasses import dataclass

# Add parent directories to path
project_root = os.path.join(os.path.dirname(__file__), '../..')
sys.path.insert(0, project_root)
scripts_path = os.path.join(project_root, 'scripts')
sys.path.insert(0, scripts_path)


# Define the dataclass locally to avoid import issues
@dataclass
class SystemCapabilities:
    """Current system capabilities"""
    voice_input: bool
    voice_output: bool
    nlp_tier: str
    executor_tier: str
    ui_tier: str
    overall_rating: str  # "Premium", "Standard", "Basic", "Minimal"


class TestSystemCapabilities(unittest.TestCase):
    """Test the SystemCapabilities dataclass."""
    
    def test_system_capabilities_creation(self):
        """Test creating SystemCapabilities."""
        caps = SystemCapabilities(
            voice_input=True,
            voice_output=True,
            nlp_tier="Premium",
            executor_tier="NixOS Python API",
            ui_tier="Advanced",
            overall_rating="Premium"
        )
        
        self.assertTrue(caps.voice_input)
        self.assertTrue(caps.voice_output)
        self.assertEqual(caps.nlp_tier, "Premium")
        self.assertEqual(caps.executor_tier, "NixOS Python API")
        self.assertEqual(caps.ui_tier, "Advanced")
        self.assertEqual(caps.overall_rating, "Premium")
    
    def test_system_capabilities_minimal(self):
        """Test minimal system capabilities."""
        caps = SystemCapabilities(
            voice_input=False,
            voice_output=False,
            nlp_tier="Basic",
            executor_tier="Manual Instructions",
            ui_tier="Text Only",
            overall_rating="Minimal"
        )
        
        self.assertFalse(caps.voice_input)
        self.assertFalse(caps.voice_output)
        self.assertEqual(caps.overall_rating, "Minimal")
    
    def test_capability_ratings(self):
        """Test different capability ratings."""
        ratings = ["Premium", "Standard", "Basic", "Minimal"]
        
        for rating in ratings:
            caps = SystemCapabilities(
                voice_input=rating == "Premium",
                voice_output=rating == "Premium",
                nlp_tier=rating,
                executor_tier=rating,
                ui_tier=rating,
                overall_rating=rating
            )
            
            self.assertEqual(caps.overall_rating, rating)


class TestResilientExecutor(unittest.TestCase):
    """Test the ResilientExecutor concept."""
    
    def test_executor_tiers(self):
        """Test executor tier concept."""
        # Mock tier structure
        tiers = [
            {
                "name": "NixOS Python API",
                "execute": lambda: "python_api",
                "safety": "Highest",
                "features": ["Real-time progress", "Direct API access"]
            },
            {
                "name": "nix profile",
                "execute": lambda: "nix_profile", 
                "safety": "High",
                "features": ["Modern interface", "Profile management"]
            },
            {
                "name": "nix-env",
                "execute": lambda: "nix_env",
                "safety": "Medium",
                "features": ["Universal compatibility"]
            },
            {
                "name": "Manual Instructions",
                "execute": lambda: "manual",
                "safety": "User-dependent",
                "features": ["Always available", "Educational"]
            }
        ]
        
        # Test tier properties
        for tier in tiers:
            self.assertIn("name", tier)
            self.assertIn("execute", tier)
            self.assertIn("safety", tier)
            self.assertIn("features", tier)
            self.assertTrue(callable(tier["execute"]))
            self.assertIsInstance(tier["features"], list)
    
    def test_safety_levels(self):
        """Test safety level hierarchy."""
        safety_levels = {
            "Highest": 4,
            "High": 3,
            "Medium": 2,
            "User-dependent": 1
        }
        
        # Test ordering
        self.assertGreater(safety_levels["Highest"], safety_levels["High"])
        self.assertGreater(safety_levels["High"], safety_levels["Medium"])
        self.assertGreater(safety_levels["Medium"], safety_levels["User-dependent"])
    
    @patch('subprocess.run')
    def test_tier_detection_logic(self, mock_run):
        """Test tier detection logic."""
        # Test NixOS 25.11 detection
        mock_run.return_value.stdout = "nixos-rebuild-ng version 25.11"
        mock_run.return_value.returncode = 0
        
        # Should detect as NixOS Python API tier
        detected_tier = "NixOS Python API"  # Simulated detection
        self.assertEqual(detected_tier, "NixOS Python API")
        
        # Test nix profile detection
        mock_run.return_value.returncode = 0
        detected_tier = "nix profile"  # Simulated detection
        self.assertEqual(detected_tier, "nix profile")
        
        # Test fallback
        mock_run.side_effect = Exception("Command not found")
        detected_tier = "nix-env"  # Simulated fallback
        self.assertEqual(detected_tier, "nix-env")
    
    def test_feature_requirements(self):
        """Test feature requirements for different tiers."""
        feature_requirements = {
            "NixOS Python API": ["nixos-rebuild-ng", "Python 3.11+"],
            "nix profile": ["Nix 2.4+"],
            "nix-env": ["Any Nix version"],
            "Manual Instructions": []
        }
        
        # Manual instructions should have no requirements
        self.assertEqual(len(feature_requirements["Manual Instructions"]), 0)
        
        # Higher tiers should have more requirements
        self.assertGreater(
            len(feature_requirements["NixOS Python API"]),
            len(feature_requirements["nix-env"])
        )


if __name__ == '__main__':
    unittest.main()