"""Tests for FileMonitor"""

import pytest
import tempfile
import time
from pathlib import Path
from datetime import datetime, timedelta

from luminous_nix.mycelix.context.file_monitor import FileMonitor
from luminous_nix.mycelix.context.types import ProjectType


@pytest.fixture
def temp_project_dir():
    """Create temporary project directory with files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "test_project"
        project_path.mkdir()

        # Create some test files
        (project_path / "main.py").write_text("print('hello')")
        (project_path / "test.py").write_text("import unittest")
        (project_path / "README.md").write_text("# Test Project")
        (project_path / "package.json").write_text('{"name": "test"}')

        yield project_path


class TestFileMonitor:
    """Test FileMonitor functionality"""

    def test_initialization(self, temp_project_dir):
        """Test FileMonitor initialization"""
        monitor = FileMonitor(watch_paths=[temp_project_dir])

        assert monitor.watch_paths == [temp_project_dir]
        assert monitor.recent_window.total_seconds() == 30 * 60  # 30 minutes

    def test_detect_language_from_extension(self, temp_project_dir):
        """Test language detection from file extensions"""
        monitor = FileMonitor(watch_paths=[temp_project_dir])

        assert monitor._detect_language(Path("test.py")) == "python"
        assert monitor._detect_language(Path("main.rs")) == "rust"
        assert monitor._detect_language(Path("app.js")) == "javascript"
        assert monitor._detect_language(Path("app.ts")) == "typescript"
        assert monitor._detect_language(Path("config.nix")) == "nix"
        assert monitor._detect_language(Path("README.md")) == "markdown"
        assert monitor._detect_language(Path("unknown.xyz")) is None

    def test_detect_project_type_from_file(self, temp_project_dir):
        """Test project type detection from single file"""
        monitor = FileMonitor(watch_paths=[temp_project_dir])

        assert monitor._detect_project_type_from_file(Path("flake.nix")) == ProjectType.NIX
        assert monitor._detect_project_type_from_file(Path("Cargo.toml")) == ProjectType.RUST
        assert monitor._detect_project_type_from_file(Path("package.json")) == ProjectType.JAVASCRIPT
        assert monitor._detect_project_type_from_file(Path("setup.py")) == ProjectType.PYTHON
        assert monitor._detect_project_type_from_file(Path("index.html")) == ProjectType.WEB_DEV
        assert monitor._detect_project_type_from_file(Path("README.md")) == ProjectType.DOCUMENTATION

    def test_get_recent_files(self, temp_project_dir):
        """Test getting recently modified files"""
        monitor = FileMonitor(watch_paths=[temp_project_dir], recent_window_minutes=60)

        # Touch a file to update its mtime
        test_file = temp_project_dir / "main.py"
        test_file.touch()

        recent = monitor.get_recent_files(limit=10)

        assert len(recent) > 0
        assert any(f.path == test_file for f in recent)

    def test_get_active_files(self, temp_project_dir):
        """Test getting currently active files (very recent)"""
        monitor = FileMonitor(watch_paths=[temp_project_dir])

        # Touch a file to make it active
        test_file = temp_project_dir / "main.py"
        test_file.touch()

        # Small delay to ensure timestamp is updated
        time.sleep(0.1)

        active = monitor.get_active_files(threshold_minutes=5)

        # Should find the recently touched file
        assert any(f.path == test_file for f in active)

    def test_infer_project_type_python(self, temp_project_dir):
        """Test project type inference for Python project"""
        monitor = FileMonitor(watch_paths=[temp_project_dir])

        # Create Python project indicators
        (temp_project_dir / "main.py").touch()
        (temp_project_dir / "test.py").touch()
        (temp_project_dir / "pyproject.toml").touch()

        project_type = monitor.infer_project_type()

        assert project_type == ProjectType.PYTHON

    def test_infer_project_type_rust(self, temp_project_dir):
        """Test project type inference for Rust project"""
        monitor = FileMonitor(watch_paths=[temp_project_dir])

        # Create Rust project indicators
        (temp_project_dir / "main.rs").touch()
        (temp_project_dir / "Cargo.toml").touch()

        project_type = monitor.infer_project_type()

        assert project_type == ProjectType.RUST

    def test_infer_project_type_web(self, temp_project_dir):
        """Test project type inference for web project"""
        monitor = FileMonitor(watch_paths=[temp_project_dir])

        # Create web project indicators
        (temp_project_dir / "index.html").touch()
        (temp_project_dir / "style.css").touch()
        (temp_project_dir / "app.js").touch()

        project_type = monitor.infer_project_type()

        assert project_type == ProjectType.WEB_DEV

    def test_infer_project_type_unknown(self, temp_project_dir):
        """Test project type inference returns unknown when unclear"""
        monitor = FileMonitor(watch_paths=[temp_project_dir])

        # Create files with no clear project type
        (temp_project_dir / "random.txt").touch()
        (temp_project_dir / "notes.doc").touch()

        # Clear existing files that might hint at project type
        for f in temp_project_dir.glob("*.py"):
            f.unlink()
        for f in temp_project_dir.glob("*.json"):
            f.unlink()

        project_type = monitor.infer_project_type()

        # Should either be UNKNOWN or detect from remaining files
        assert project_type in [ProjectType.UNKNOWN, ProjectType.DOCUMENTATION]

    def test_get_language_distribution(self, temp_project_dir):
        """Test language distribution analysis"""
        monitor = FileMonitor(watch_paths=[temp_project_dir])

        # Create mix of files
        (temp_project_dir / "main.py").touch()
        (temp_project_dir / "test.py").touch()
        (temp_project_dir / "app.js").touch()
        (temp_project_dir / "README.md").touch()

        distribution = monitor.get_language_distribution()

        assert "python" in distribution
        assert "javascript" in distribution
        assert "markdown" in distribution

    def test_clear_cache(self, temp_project_dir):
        """Test clearing file cache"""
        monitor = FileMonitor(watch_paths=[temp_project_dir])

        # Get files to populate cache
        monitor.get_recent_files()

        assert len(monitor._file_cache) > 0

        # Clear cache
        monitor.clear_cache()

        assert len(monitor._file_cache) == 0
        assert monitor._last_scan is None
