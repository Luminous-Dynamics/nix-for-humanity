"""
Plugin discovery system.

Finds plugins in configured locations and parses their manifests.
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass
try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for older Python

from .base import PluginMetadata, PluginConfig
from .errors import PluginValidationError


@dataclass
class PluginManifest:
    """Parsed plugin manifest from plugin.toml"""
    # Core identifiers
    name: str
    version: str
    api_version: str

    # Entry points
    entry_point_module: str
    entry_point_class: str

    # Paths
    plugin_dir: Path
    manifest_file: Path

    # Metadata
    author: Optional[str] = None
    description: Optional[str] = None
    email: Optional[str] = None
    homepage: Optional[str] = None
    license: Optional[str] = None

    # Capabilities
    operation_types: List[str] = None
    hooks: List[str] = None

    # Requirements
    requires_permissions: List[str] = None
    dependencies: List[str] = None
    requires_nix_version: Optional[str] = None

    # Security
    signature: Optional[str] = None

    # Additional manifest data
    raw_manifest: Optional[Dict] = None

    def __post_init__(self):
        """Initialize list fields"""
        if self.operation_types is None:
            self.operation_types = []
        if self.hooks is None:
            self.hooks = []
        if self.requires_permissions is None:
            self.requires_permissions = []
        if self.dependencies is None:
            self.dependencies = []


class PluginDiscovery:
    """
    Discovers plugins in configured locations.

    Searches for plugin.toml files and parses them into PluginManifest objects.
    """

    def __init__(self, config: PluginConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._cache: Dict[str, PluginManifest] = {}
        self._discovered: bool = False  # Track if discovery has been done

    def discover_all(self) -> List[PluginManifest]:
        """
        Discover all plugins in configured paths.

        Returns cached results if discovery has already been done.
        Call clear_cache() to force re-discovery.

        Returns:
            List of discovered plugin manifests
        """
        # Return cached results if already discovered
        if self._discovered:
            return list(self._cache.values())

        manifests = []

        for plugin_path in self.config.plugin_paths:
            if not plugin_path.exists():
                self.logger.debug(f"Plugin path does not exist: {plugin_path}")
                continue

            if not plugin_path.is_dir():
                self.logger.warning(f"Plugin path is not a directory: {plugin_path}")
                continue

            # Find all plugin directories (contain plugin.toml)
            for plugin_dir in plugin_path.iterdir():
                if not plugin_dir.is_dir():
                    continue

                # Skip hidden directories (starting with '.')
                if plugin_dir.name.startswith('.'):
                    continue

                manifest_file = plugin_dir / "plugin.toml"
                if not manifest_file.exists():
                    continue

                try:
                    manifest = self._parse_manifest(manifest_file, plugin_dir)
                    manifests.append(manifest)
                    # Cache this manifest (later paths override earlier ones for priority)
                    self._cache[manifest.name] = manifest
                    self.logger.debug(f"Discovered plugin: {manifest.name}")
                except Exception as e:
                    self.logger.error(f"Failed to parse manifest {manifest_file}: {e}")

        self._discovered = True
        self.logger.info(f"Discovered {len(manifests)} plugins")
        return manifests

    def find_plugin(self, name: str) -> Optional[PluginManifest]:
        """
        Find a specific plugin by name.

        Searches by the plugin's manifest name, not directory name.

        Args:
            name: Plugin name to find (from manifest)

        Returns:
            Plugin manifest if found

        Raises:
            PluginNotFoundError: If plugin not found
        """
        from .errors import PluginNotFoundError

        # Check cache first
        if name in self._cache:
            return self._cache[name]

        # Search all plugin directories by parsing manifests
        # Later paths have higher priority, so search all paths
        found_manifest = None

        for plugin_path in self.config.plugin_paths:
            if not plugin_path.exists():
                continue

            if not plugin_path.is_dir():
                continue

            # Check each directory for a plugin
            for plugin_dir in plugin_path.iterdir():
                if not plugin_dir.is_dir():
                    continue

                # Skip hidden directories (starting with '.')
                if plugin_dir.name.startswith('.'):
                    continue

                manifest_file = plugin_dir / "plugin.toml"
                if not manifest_file.exists():
                    continue

                try:
                    manifest = self._parse_manifest(manifest_file, plugin_dir)
                    # Cache this manifest (later paths override earlier ones)
                    self._cache[manifest.name] = manifest

                    # Check if this is the one we're looking for
                    if manifest.name == name:
                        found_manifest = manifest
                        # Don't return yet - continue to check higher priority paths
                except Exception as e:
                    self.logger.error(f"Failed to parse manifest {manifest_file}: {e}")
                    continue

        # Return the highest priority match (from last path searched)
        if found_manifest:
            return found_manifest

        # Not found
        raise PluginNotFoundError(f"Plugin '{name}' not found")

    def _parse_manifest(self, manifest_file: Path, plugin_dir: Path) -> PluginManifest:
        """
        Parse a plugin.toml manifest file.

        Args:
            manifest_file: Path to plugin.toml
            plugin_dir: Plugin directory

        Returns:
            Parsed plugin manifest

        Raises:
            PluginValidationError: If manifest is invalid
        """
        try:
            with open(manifest_file, 'rb') as f:
                data = tomllib.load(f)
        except Exception as e:
            raise PluginValidationError(f"Failed to parse TOML: {e}")

        # Validate required sections
        if 'plugin' not in data:
            raise PluginValidationError("Missing [plugin] section")

        plugin_section = data['plugin']

        # Required fields
        required_fields = ['name', 'version', 'api_version']
        for field in required_fields:
            if field not in plugin_section:
                raise PluginValidationError(f"Missing required field: {field}")

        # Entry points
        if 'entry_points' not in data.get('plugin', {}):
            raise PluginValidationError("Missing [plugin.entry_points] section")

        entry_points = data['plugin']['entry_points']
        if 'module' not in entry_points or 'class' not in entry_points:
            raise PluginValidationError("Missing entry point module or class")

        # Get metadata section if it exists
        metadata_section = data.get('plugin', {}).get('metadata', {})

        # Build manifest with flat structure
        manifest = PluginManifest(
            # Core identifiers
            name=plugin_section['name'],
            version=plugin_section['version'],
            api_version=plugin_section['api_version'],

            # Entry points
            entry_point_module=entry_points['module'],
            entry_point_class=entry_points['class'],

            # Paths
            plugin_dir=plugin_dir,
            manifest_file=manifest_file,

            # Metadata (prefer metadata section, fall back to plugin section)
            author=metadata_section.get('author') or plugin_section.get('author'),
            description=metadata_section.get('description') or plugin_section.get('description'),
            email=metadata_section.get('email') or plugin_section.get('email'),
            homepage=metadata_section.get('homepage') or plugin_section.get('homepage'),
            license=metadata_section.get('license') or plugin_section.get('license'),

            # Capabilities
            operation_types=data.get('plugin', {}).get('provides', {}).get('operation_types', []),
            hooks=data.get('plugin', {}).get('provides', {}).get('hooks', []),

            # Requirements
            requires_permissions=data.get('plugin', {}).get('permissions', {}).get('required', []) or data.get('plugin', {}).get('requires', {}).get('permissions', []),
            dependencies=data.get('plugin', {}).get('requirements', {}).get('dependencies', []) or data.get('plugin', {}).get('requires', {}).get('dependencies', []),
            requires_nix_version=data.get('plugin', {}).get('requirements', {}).get('nix_version') or data.get('plugin', {}).get('requires', {}).get('nix_version'),

            # Security
            signature=data.get('plugin', {}).get('signature'),

            # Raw data
            raw_manifest=data
        )

        return manifest

    def clear_cache(self):
        """Clear the discovery cache and reset discovery state"""
        self._cache.clear()
        self._discovered = False


# Export
__all__ = ['PluginDiscovery', 'PluginManifest']
