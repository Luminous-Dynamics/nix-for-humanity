"""
File Monitor - Tracks file editing patterns

Monitors which files the user is editing to infer:
- Current project type
- Areas of focus
- Workflow patterns
"""

import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from collections import defaultdict

from .types import FileActivity, ProjectType

logger = logging.getLogger(__name__)


class FileMonitor:
    """
    Monitor file system activity to understand user context

    Features:
    - Detect recently edited files
    - Infer programming language
    - Identify project type
    - Track edit frequency
    """

    # File extension to language mapping
    LANGUAGE_MAP = {
        ".py": "python",
        ".rs": "rust",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".nix": "nix",
        ".html": "html",
        ".css": "css",
        ".md": "markdown",
        ".go": "go",
        ".c": "c",
        ".cpp": "cpp",
        ".java": "java",
    }

    # Project type detection patterns
    PROJECT_PATTERNS = {
        ProjectType.PYTHON: [".py", "pyproject.toml", "setup.py", "requirements.txt"],
        ProjectType.RUST: [".rs", "Cargo.toml", "Cargo.lock"],
        ProjectType.JAVASCRIPT: [".js", "package.json", "node_modules"],
        ProjectType.TYPESCRIPT: [".ts", "tsconfig.json"],
        ProjectType.WEB_DEV: [".html", ".css", ".js", "index.html"],
        ProjectType.NIX: [".nix", "flake.nix", "flake.lock"],
        ProjectType.SYSTEM_CONFIG: ["/etc/nixos/configuration.nix", ".config/"],
        ProjectType.DOCUMENTATION: [".md", ".rst", "docs/", "README"],
    }

    def __init__(
        self,
        watch_paths: Optional[List[Path]] = None,
        recent_window_minutes: int = 30
    ):
        """
        Initialize file monitor

        Args:
            watch_paths: Directories to monitor (default: current directory)
            recent_window_minutes: How recent is "recent" for file activity
        """
        self.watch_paths = watch_paths or [Path.cwd()]
        self.recent_window = timedelta(minutes=recent_window_minutes)
        self._file_cache: Dict[Path, FileActivity] = {}
        self._last_scan: Optional[datetime] = None

    def get_recent_files(self, limit: int = 20) -> List[FileActivity]:
        """
        Get recently edited files

        Args:
            limit: Maximum number of files to return

        Returns:
            List of FileActivity objects, sorted by recency
        """
        self._scan_files()

        # Filter to recent files
        cutoff = datetime.now() - self.recent_window
        recent = [
            f for f in self._file_cache.values()
            if f.last_modified >= cutoff
        ]

        # Sort by most recent first
        recent.sort(key=lambda f: f.last_modified, reverse=True)

        return recent[:limit]

    def get_active_files(self, threshold_minutes: int = 5) -> List[FileActivity]:
        """
        Get currently active files (very recently edited)

        Args:
            threshold_minutes: How recent to consider "active"

        Returns:
            List of currently active files
        """
        cutoff = datetime.now() - timedelta(minutes=threshold_minutes)
        return [
            f for f in self.get_recent_files()
            if f.last_modified >= cutoff
        ]

    def infer_project_type(self) -> Optional[ProjectType]:
        """
        Infer project type from recent files

        Returns:
            Most likely ProjectType, or None if unclear
        """
        recent = self.get_recent_files()
        if not recent:
            return None

        # Count evidence for each project type
        evidence: Dict[ProjectType, int] = defaultdict(int)

        for file_activity in recent:
            path = file_activity.path

            # Check against project patterns
            for project_type, patterns in self.PROJECT_PATTERNS.items():
                for pattern in patterns:
                    if pattern.startswith("/"):
                        # Absolute path pattern
                        if str(path).startswith(pattern):
                            evidence[project_type] += 5
                    elif "/" in pattern:
                        # Relative path pattern (contains directory)
                        if pattern in str(path):
                            evidence[project_type] += 3
                    else:
                        # File extension or name pattern
                        if str(path).endswith(pattern) or pattern in path.name:
                            evidence[project_type] += 1

        if not evidence:
            return ProjectType.UNKNOWN

        # Return project type with most evidence
        return max(evidence.items(), key=lambda x: x[1])[0]

    def _scan_files(self):
        """Scan watch paths for file modifications"""
        # Don't scan too frequently
        if self._last_scan:
            if datetime.now() - self._last_scan < timedelta(seconds=5):
                return

        for watch_path in self.watch_paths:
            if not watch_path.exists():
                continue

            # Walk directory tree
            try:
                for root, dirs, files in os.walk(watch_path):
                    # Skip hidden directories and common ignore patterns
                    dirs[:] = [
                        d for d in dirs
                        if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'target']
                    ]

                    for filename in files:
                        # Skip hidden files
                        if filename.startswith('.'):
                            continue

                        filepath = Path(root) / filename
                        self._update_file_activity(filepath)

            except (PermissionError, OSError) as e:
                logger.debug(f"Error scanning {watch_path}: {e}")

        self._last_scan = datetime.now()

    def _update_file_activity(self, filepath: Path):
        """Update activity record for a file"""
        try:
            stat = filepath.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime)

            # Only track if modified recently
            if datetime.now() - mtime > self.recent_window:
                return

            if filepath in self._file_cache:
                # Update existing record
                activity = self._file_cache[filepath]
                if mtime > activity.last_modified:
                    activity.last_modified = mtime
                    activity.edit_count += 1
            else:
                # Create new record
                language = self._detect_language(filepath)
                project_type = self._detect_project_type_from_file(filepath)

                activity = FileActivity(
                    path=filepath,
                    last_modified=mtime,
                    edit_count=1,
                    language=language,
                    project_type=project_type
                )
                self._file_cache[filepath] = activity

        except (OSError, PermissionError):
            pass

    def _detect_language(self, filepath: Path) -> Optional[str]:
        """Detect programming language from file extension"""
        return self.LANGUAGE_MAP.get(filepath.suffix)

    def _detect_project_type_from_file(self, filepath: Path) -> Optional[ProjectType]:
        """Quick project type detection from single file"""
        # Check special files
        if filepath.name == "flake.nix" or filepath.suffix == ".nix":
            return ProjectType.NIX
        elif filepath.name in ["Cargo.toml", "Cargo.lock"] or filepath.suffix == ".rs":
            return ProjectType.RUST
        elif filepath.name in ["package.json", "package-lock.json"]:
            return ProjectType.JAVASCRIPT
        elif filepath.name in ["pyproject.toml", "setup.py", "requirements.txt"] or filepath.suffix == ".py":
            return ProjectType.PYTHON
        elif filepath.suffix in [".html", ".css"] or filepath.name == "index.html":
            return ProjectType.WEB_DEV
        elif filepath.suffix == ".md" or "docs" in str(filepath):
            return ProjectType.DOCUMENTATION

        return None

    def get_language_distribution(self) -> Dict[str, int]:
        """
        Get distribution of programming languages in recent files

        Returns:
            Dictionary mapping language to file count
        """
        recent = self.get_recent_files()
        distribution: Dict[str, int] = defaultdict(int)

        for file_activity in recent:
            if file_activity.language:
                distribution[file_activity.language] += 1

        return dict(distribution)

    def clear_cache(self):
        """Clear the file activity cache"""
        self._file_cache.clear()
        self._last_scan = None
