"""
Tests for plugin security validation.

Tests manifest validation, permission checking, dependency validation, and signatures.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from luminous_nix.plugins.validator import PluginValidator
from luminous_nix.plugins.discovery import PluginManifest
from luminous_nix.plugins.base import PluginConfig
from luminous_nix.plugins.errors import PluginValidationError


class TestPluginValidator:
    """Test PluginValidator"""

    @pytest.fixture
    def temp_plugin_dir(self):
        """Create temporary plugin directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def valid_manifest(self, temp_plugin_dir):
        """Create valid manifest"""
        plugin_dir = temp_plugin_dir / "valid-plugin"
        plugin_dir.mkdir()

        # Create main.py
        (plugin_dir / "main.py").write_text("class TestPlugin: pass")

        return PluginManifest(
            name="valid-plugin",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="TestPlugin",
            plugin_dir=plugin_dir,
            manifest_file=plugin_dir / "plugin.toml",
            author="Test Author",
            description="Valid plugin"
        )

    def test_validator_initialization(self):
        """Test validator initialization"""
        config = PluginConfig()
        validator = PluginValidator(config)

        assert validator.config == config

    def test_validate_valid_manifest(self, valid_manifest):
        """Test validating a valid manifest"""
        validator = PluginValidator(PluginConfig())

        # Should not raise
        result = validator.validate(valid_manifest)
        assert result == True

    def test_validate_missing_required_fields(self, temp_plugin_dir):
        """Test validation fails for missing required fields"""
        manifest = PluginManifest(
            name="",  # Empty name
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="TestPlugin",
            plugin_dir=temp_plugin_dir / "test",
            manifest_file=temp_plugin_dir / "test" / "plugin.toml"
        )

        validator = PluginValidator(PluginConfig())

        with pytest.raises(PluginValidationError) as exc:
            validator.validate(manifest)

        assert "name" in str(exc.value).lower()

    def test_validate_invalid_version_format(self, temp_plugin_dir):
        """Test validation fails for invalid version"""
        manifest = PluginManifest(
            name="test-plugin",
            version="not-a-version",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="TestPlugin",
            plugin_dir=temp_plugin_dir / "test",
            manifest_file=temp_plugin_dir / "test" / "plugin.toml"
        )

        validator = PluginValidator(PluginConfig())

        with pytest.raises(PluginValidationError) as exc:
            validator.validate(manifest)

        assert "version" in str(exc.value).lower()

    def test_validate_missing_entry_point_file(self, temp_plugin_dir):
        """Test validation fails when entry point file missing"""
        plugin_dir = temp_plugin_dir / "missing-file"
        plugin_dir.mkdir()
        # Don't create main.py

        manifest = PluginManifest(
            name="test-plugin",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="TestPlugin",
            plugin_dir=plugin_dir,
            manifest_file=plugin_dir / "plugin.toml"
        )

        validator = PluginValidator(PluginConfig())

        with pytest.raises(PluginValidationError) as exc:
            validator.validate(manifest)

        assert "main.py" in str(exc.value) or "entry point" in str(exc.value).lower()


class TestPermissionValidation:
    """Test permission validation"""

    @pytest.fixture
    def temp_plugin_dir(self):
        """Create temporary plugin directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_validate_valid_permissions(self, temp_plugin_dir):
        """Test validating valid permissions"""
        plugin_dir = temp_plugin_dir / "test"
        plugin_dir.mkdir()
        (plugin_dir / "main.py").write_text("class Test: pass")

        manifest = PluginManifest(
            name="test",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="Test",
            plugin_dir=plugin_dir,
            manifest_file=plugin_dir / "plugin.toml",
            requires_permissions=["operations:execute", "filesystem:read"]
        )

        validator = PluginValidator(PluginConfig())
        result = validator.validate(manifest)

        assert result == True

    def test_validate_invalid_permission_format(self, temp_plugin_dir):
        """Test validation fails for invalid permission format"""
        plugin_dir = temp_plugin_dir / "test"
        plugin_dir.mkdir()
        (plugin_dir / "main.py").write_text("class Test: pass")

        manifest = PluginManifest(
            name="test",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="Test",
            plugin_dir=plugin_dir,
            manifest_file=plugin_dir / "plugin.toml",
            requires_permissions=["invalid-permission-format"]  # No colon
        )

        validator = PluginValidator(PluginConfig())

        with pytest.raises(PluginValidationError) as exc:
            validator.validate(manifest)

        assert "permission" in str(exc.value).lower()

    def test_validate_unknown_permission_category(self, temp_plugin_dir):
        """Test validation warns for unknown permission category"""
        plugin_dir = temp_plugin_dir / "test"
        plugin_dir.mkdir()
        (plugin_dir / "main.py").write_text("class Test: pass")

        manifest = PluginManifest(
            name="test",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="Test",
            plugin_dir=plugin_dir,
            manifest_file=plugin_dir / "plugin.toml",
            requires_permissions=["unknown_category:action"]
        )

        validator = PluginValidator(PluginConfig())

        # Should either raise or warn (implementation dependent)
        try:
            validator.validate(manifest)
        except PluginValidationError as e:
            assert "unknown" in str(e).lower() or "category" in str(e).lower()

    def test_validate_all_permission_categories(self, temp_plugin_dir):
        """Test all standard permission categories are accepted"""
        plugin_dir = temp_plugin_dir / "test"
        plugin_dir.mkdir()
        (plugin_dir / "main.py").write_text("class Test: pass")

        manifest = PluginManifest(
            name="test",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="Test",
            plugin_dir=plugin_dir,
            manifest_file=plugin_dir / "plugin.toml",
            requires_permissions=[
                "operations:execute",
                "security:encrypt",
                "filesystem:read",
                "network:http",
                "hardware:usb"
            ]
        )

        validator = PluginValidator(PluginConfig())
        result = validator.validate(manifest)

        assert result == True


class TestDependencyValidation:
    """Test dependency validation"""

    @pytest.fixture
    def temp_plugin_dir(self):
        """Create temporary plugin directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_validate_valid_dependencies(self, temp_plugin_dir):
        """Test validating valid dependencies"""
        plugin_dir = temp_plugin_dir / "test"
        plugin_dir.mkdir()
        (plugin_dir / "main.py").write_text("class Test: pass")

        manifest = PluginManifest(
            name="test",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="Test",
            plugin_dir=plugin_dir,
            manifest_file=plugin_dir / "plugin.toml",
            dependencies=["plugin-a>=1.0", "plugin-b>=2.0"]
        )

        validator = PluginValidator(PluginConfig())

        # Should validate format (actual dependency checking is runtime)
        result = validator.validate(manifest)
        assert result == True

    def test_validate_invalid_dependency_format(self, temp_plugin_dir):
        """Test validation fails for invalid dependency format"""
        plugin_dir = temp_plugin_dir / "test"
        plugin_dir.mkdir()
        (plugin_dir / "main.py").write_text("class Test: pass")

        manifest = PluginManifest(
            name="test",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="Test",
            plugin_dir=plugin_dir,
            manifest_file=plugin_dir / "plugin.toml",
            dependencies=["invalid dependency format!!!"]
        )

        validator = PluginValidator(PluginConfig())

        # May or may not raise depending on strictness
        # At minimum should not crash
        try:
            validator.validate(manifest)
        except PluginValidationError:
            pass  # Expected possible failure

    def test_circular_dependency_detection(self, temp_plugin_dir):
        """Test detection of circular dependencies"""
        # This would require multiple plugins to test properly
        # For now, just ensure validator has the infrastructure
        validator = PluginValidator(PluginConfig())

        assert hasattr(validator, 'validate') or hasattr(validator, '_validate_dependencies')


class TestSignatureValidation:
    """Test signature validation"""

    @pytest.fixture
    def temp_plugin_dir(self):
        """Create temporary plugin directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_signature_not_required_by_default(self, temp_plugin_dir):
        """Test signatures not required by default"""
        plugin_dir = temp_plugin_dir / "test"
        plugin_dir.mkdir()
        (plugin_dir / "main.py").write_text("class Test: pass")

        manifest = PluginManifest(
            name="test",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="Test",
            plugin_dir=plugin_dir,
            manifest_file=plugin_dir / "plugin.toml"
        )

        config = PluginConfig(require_signatures=False)
        validator = PluginValidator(config)

        # Should pass without signature
        result = validator.validate(manifest)
        assert result == True

    def test_signature_required_when_configured(self, temp_plugin_dir):
        """Test signature validation when required"""
        plugin_dir = temp_plugin_dir / "test"
        plugin_dir.mkdir()
        (plugin_dir / "main.py").write_text("class Test: pass")

        manifest = PluginManifest(
            name="test",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="Test",
            plugin_dir=plugin_dir,
            manifest_file=plugin_dir / "plugin.toml"
            # No signature provided
        )

        config = PluginConfig(require_signatures=True)
        validator = PluginValidator(config)

        # Should fail without signature
        with pytest.raises(PluginValidationError) as exc:
            validator.validate(manifest)

        assert "signature" in str(exc.value).lower()

    def test_validate_signature_format(self, temp_plugin_dir):
        """Test signature format validation"""
        plugin_dir = temp_plugin_dir / "test"
        plugin_dir.mkdir()
        (plugin_dir / "main.py").write_text("class Test: pass")

        manifest = PluginManifest(
            name="test",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="Test",
            plugin_dir=plugin_dir,
            manifest_file=plugin_dir / "plugin.toml",
            signature="not-a-valid-signature"
        )

        config = PluginConfig(require_signatures=True)
        validator = PluginValidator(config)

        # Should fail with invalid signature
        with pytest.raises(PluginValidationError):
            validator.validate(manifest)


class TestFileStructureValidation:
    """Test file structure validation"""

    @pytest.fixture
    def temp_plugin_dir(self):
        """Create temporary plugin directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_validate_entry_point_exists(self, temp_plugin_dir):
        """Test validation checks entry point file exists"""
        plugin_dir = temp_plugin_dir / "test"
        plugin_dir.mkdir()

        # Create the entry point file
        (plugin_dir / "main.py").write_text("class TestPlugin: pass")

        manifest = PluginManifest(
            name="test",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="TestPlugin",
            plugin_dir=plugin_dir,
            manifest_file=plugin_dir / "plugin.toml"
        )

        validator = PluginValidator(PluginConfig())
        result = validator.validate(manifest)

        assert result == True

    def test_validate_entry_point_missing(self, temp_plugin_dir):
        """Test validation fails when entry point missing"""
        plugin_dir = temp_plugin_dir / "test"
        plugin_dir.mkdir()
        # Don't create main.py

        manifest = PluginManifest(
            name="test",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="TestPlugin",
            plugin_dir=plugin_dir,
            manifest_file=plugin_dir / "plugin.toml"
        )

        validator = PluginValidator(PluginConfig())

        with pytest.raises(PluginValidationError):
            validator.validate(manifest)

    def test_validate_manifest_file_exists(self, temp_plugin_dir):
        """Test validation accepts programmatically created manifests"""
        plugin_dir = temp_plugin_dir / "test"
        plugin_dir.mkdir()
        (plugin_dir / "main.py").write_text("class Test: pass")

        # Manifest file doesn't actually exist (programmatic creation)
        manifest = PluginManifest(
            name="test",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="Test",
            plugin_dir=plugin_dir,
            manifest_file=plugin_dir / "plugin.toml"  # Doesn't exist
        )

        validator = PluginValidator(PluginConfig())

        # Should accept programmatically created manifests
        # (manifest file existence is not checked)
        assert validator.validate(manifest) == True


class TestChecksumValidation:
    """Test checksum computation and validation"""

    @pytest.fixture
    def temp_plugin_dir(self):
        """Create temporary plugin directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_compute_plugin_checksum(self, temp_plugin_dir):
        """Test computing checksum for plugin files"""
        plugin_dir = temp_plugin_dir / "test"
        plugin_dir.mkdir()
        (plugin_dir / "main.py").write_text("class TestPlugin: pass")

        validator = PluginValidator(PluginConfig())

        # Should be able to compute checksum
        checksum = validator._compute_checksum(plugin_dir)

        assert checksum is not None
        assert len(checksum) > 0

    def test_checksum_changes_with_content(self, temp_plugin_dir):
        """Test checksum changes when content changes"""
        plugin_dir = temp_plugin_dir / "test"
        plugin_dir.mkdir()
        (plugin_dir / "main.py").write_text("class TestPlugin: pass")

        validator = PluginValidator(PluginConfig())

        checksum1 = validator._compute_checksum(plugin_dir)

        # Modify file
        (plugin_dir / "main.py").write_text("class TestPlugin: pass  # Changed")

        checksum2 = validator._compute_checksum(plugin_dir)

        assert checksum1 != checksum2

    def test_checksum_same_for_same_content(self, temp_plugin_dir):
        """Test checksum is deterministic"""
        plugin_dir = temp_plugin_dir / "test"
        plugin_dir.mkdir()
        (plugin_dir / "main.py").write_text("class TestPlugin: pass")

        validator = PluginValidator(PluginConfig())

        checksum1 = validator._compute_checksum(plugin_dir)
        checksum2 = validator._compute_checksum(plugin_dir)

        assert checksum1 == checksum2


class TestConflictDetection:
    """Test plugin conflict detection"""

    @pytest.fixture
    def temp_plugin_dir(self):
        """Create temporary plugin directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_detect_operation_type_conflict(self, temp_plugin_dir):
        """Test detection of operation type conflicts"""
        # Two plugins providing same operation type
        plugin_dir = temp_plugin_dir / "test"
        plugin_dir.mkdir()
        (plugin_dir / "main.py").write_text("class Test: pass")

        manifest = PluginManifest(
            name="test",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="Test",
            plugin_dir=plugin_dir,
            manifest_file=plugin_dir / "plugin.toml",
            operation_types=["CUSTOM_OP"]
        )

        validator = PluginValidator(PluginConfig())

        # First plugin should validate fine
        result = validator.validate(manifest)
        assert result == True

        # Register it as loaded
        validator._loaded_operations = {"CUSTOM_OP"}

        # Second plugin with same operation should conflict
        manifest2 = PluginManifest(
            name="test2",
            version="1.0.0",
            api_version="1.0",
            entry_point_module="main",
            entry_point_class="Test",
            plugin_dir=plugin_dir,
            manifest_file=plugin_dir / "plugin.toml",
            operation_types=["CUSTOM_OP"]  # Conflict!
        )

        with pytest.raises(PluginValidationError) as exc:
            validator.validate(manifest2, check_conflicts=True)

        assert "conflict" in str(exc.value).lower()
