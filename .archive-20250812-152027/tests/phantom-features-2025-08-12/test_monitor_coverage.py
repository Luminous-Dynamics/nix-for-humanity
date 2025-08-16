#!/usr/bin/env python3
"""
import subprocess
Tests for monitor_coverage.py

Tests the coverage monitoring functionality.
"""

import json
import os
import shutil
import sqlite3

from unittest.mock import Mock, MagicMock, patch, call
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent directories to path
project_root = os.path.join(os.path.dirname(__file__), "../..")
sys.path.insert(0, project_root)
scripts_path = os.path.join(project_root, "scripts")
sys.path.insert(0, scripts_path)

# Import the module to test
from monitor_coverage import (
    CORE_FEATURE_THRESHOLD,
    CRITICAL_PATH_THRESHOLD,
    CoverageMonitor,
)

class TestCoverageMonitor(unittest.TestCase):
    """Test the CoverageMonitor class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test database
        self.test_dir = tempfile.mkdtemp()
        self.test_project_root = Path(self.test_dir)

        # Create monitor instance
        self.monitor = CoverageMonitor(self.test_project_root)

    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)

    def test_init(self):
        """Test CoverageMonitor initialization."""
        # Check that monitor was initialized
        self.assertEqual(self.monitor.project_root, self.test_project_root)
        self.assertTrue(self.monitor.db_path.exists())

        # Check database path
        expected_db_path = (
            self.test_project_root / ".coverage_monitor" / "coverage_history.db"
        )
        self.assertEqual(self.monitor.db_path, expected_db_path)

    def test_database_creation(self):
        """Test that database tables are created correctly."""
        # Connect to database
        with sqlite3.connect(self.monitor.db_path) as conn:
            # Check coverage_history table
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='coverage_history'"
            )
            self.assertIsNotNone(cursor.fetchone())

            # Check coverage_gaps table
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='coverage_gaps'"
            )
            self.assertIsNotNone(cursor.fetchone())

    def test_thresholds(self):
        """Test that coverage thresholds are set correctly."""
        self.assertEqual(CRITICAL_PATH_THRESHOLD, 95.0)
        self.assertEqual(CORE_FEATURE_THRESHOLD, 90.0)

    @patch("subprocess.run")
    def test_run_coverage_success(self, mock_run):
        """Test successful coverage run."""
        # Mock successful subprocess run
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Coverage: 85%"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        # Run coverage
        result = self.monitor.run_coverage()

        # Verify subprocess was called correctly
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        self.assertIn("-m", call_args)
        self.assertIn("pytest", call_args)
        self.assertIn("--cov=nix_humanity", call_args)

    @patch("subprocess.run")
    def test_run_coverage_failure(self, mock_run):
        """Test failed coverage run."""
        # Mock failed subprocess run
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Test failed"
        mock_run.return_value = mock_result

        # Run coverage
        result = self.monitor.run_coverage()

        # Should return None on failure
        self.assertIsNone(result)

    def test_critical_paths(self):
        """Test critical path definitions."""
        from monitor_coverage import CRITICAL_PATHS

        # Check that critical paths are defined
        self.assertIsInstance(CRITICAL_PATHS, list)
        self.assertGreater(len(CRITICAL_PATHS), 0)

        # Check some expected paths
        expected_paths = [
            "nix_humanity/nlp/",
            "nix_humanity/executor/",
            "nix_humanity/safety/",
        ]

        for path in expected_paths:
            self.assertIn(path, CRITICAL_PATHS)

    def test_core_features(self):
        """Test core feature definitions."""
        from monitor_coverage import CORE_FEATURES

        # Check that core features are defined
        self.assertIsInstance(CORE_FEATURES, list)
        self.assertGreater(len(CORE_FEATURES), 0)

        # Check some expected features
        expected_features = [
            "nix_humanity/learning/",
            "nix_humanity/context/",
            "nix_humanity/personality/",
        ]

        for feature in expected_features:
            self.assertIn(feature, CORE_FEATURES)

    def test_ui_components(self):
        """Test UI component definitions."""
        from monitor_coverage import UI_COMPONENTS

        # Check that UI components are defined
        self.assertIsInstance(UI_COMPONENTS, list)
        self.assertGreater(len(UI_COMPONENTS), 0)

        # Check some expected components
        expected_components = ["nix_humanity/cli/", "nix_humanity/tui/"]

        for component in expected_components:
            self.assertIn(component, UI_COMPONENTS)

    def test_database_insert(self):
        """Test inserting coverage data into database."""
        # Insert test data
        test_data = {
            "overall": 85.5,
            "critical": 96.0,
            "core": 91.0,
            "ui": 82.0,
            "details": {"test": "data"},
            "commit": "abc123",
        }

        with sqlite3.connect(self.monitor.db_path) as conn:
            conn.execute(
                """
                INSERT INTO coverage_history
                (overall_coverage, critical_coverage, core_coverage, ui_coverage, details, commit_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    test_data["overall"],
                    test_data["critical"],
                    test_data["core"],
                    test_data["ui"],
                    json.dumps(test_data["details"]),
                    test_data["commit"],
                ),
            )

        # Verify data was inserted
        with sqlite3.connect(self.monitor.db_path) as conn:
            cursor = conn.execute("SELECT * FROM coverage_history")
            row = cursor.fetchone()

            self.assertIsNotNone(row)
            self.assertEqual(row[2], test_data["overall"])  # overall_coverage
            self.assertEqual(row[3], test_data["critical"])  # critical_coverage

    def test_coverage_gaps_insert(self):
        """Test inserting coverage gap data."""
        # Insert test gap data
        test_gap = {
            "file": "test_file.py",
            "coverage": 65.0,
            "missing": "10-15, 20-25",
            "category": "core",
        }

        with sqlite3.connect(self.monitor.db_path) as conn:
            conn.execute(
                """
                INSERT INTO coverage_gaps
                (file_path, coverage_percent, missing_lines, category)
                VALUES (?, ?, ?, ?)
            """,
                (
                    test_gap["file"],
                    test_gap["coverage"],
                    test_gap["missing"],
                    test_gap["category"],
                ),
            )

        # Verify data was inserted
        with sqlite3.connect(self.monitor.db_path) as conn:
            cursor = conn.execute("SELECT * FROM coverage_gaps")
            row = cursor.fetchone()

            self.assertIsNotNone(row)
            self.assertEqual(row[2], test_gap["file"])  # file_path
            self.assertEqual(row[3], test_gap["coverage"])  # coverage_percent

if __name__ == "__main__":
    unittest.main()
