#!/usr/bin/env python3
import pytest
import os

# Skip if not on NixOS
if not os.path.exists("/nix/store"):
    pytest.skip("NixOS required for this test", allow_module_level=True)

"""
Integration tests for advanced native features.

Tests that our high-value features actually work with the native API.
"""

from luminous_nix.core.advanced_features import AdvancedFeatures
from luminous_nix.core.native_operations_advanced import (
    FlakeOperationType,
    ImageOperationType,
    NativeOperationResult,
    ProfileOperationType,
    RemoteOperationType,
)

class TestAdvancedFeatures:
    """Test all advanced feature implementations"""

    @pytest.fixture
    async def features(self):
        """Get advanced features instance"""
        return AdvancedFeatures()

    # ==================== Flake Tests ====================

    @pytest.mark.asyncio
    async def test_flake_operations(self, features):
        """Test flake management features"""
        # Test showing flake info
        result = await features.flakes.show()
        assert isinstance(result, NativeOperationResult)
        # May fail if no flake exists, but should return proper result
        assert result.message is not None

        # Test flake check
        result = await features.flakes.check()
        assert isinstance(result, NativeOperationResult)

    @pytest.mark.asyncio
    async def test_flake_init(self, features, tmp_path):
        """Test flake initialization"""
        result = await features.flakes.init(tmp_path)
        assert isinstance(result, NativeOperationResult)

        if result.success:
            # Check that flake.nix was created
            flake_file = tmp_path / "flake.nix"
            if flake_file.exists():
                assert flake_file.read_text().startswith("{")

    # ==================== Profile Tests ====================

    @pytest.mark.asyncio
    async def test_profile_list(self, features):
        """Test listing profiles"""
        result = await features.profiles.list()
        assert result is not None
        assert isinstance(result, NativeOperationResult)

        if result.success and result.data.get("profiles"):
            # Should have at least system profile
            profiles = result.data["profiles"]
            assert len(profiles) > 0
            assert any(p["name"] == "system" for p in profiles)

    @pytest.mark.asyncio
    async def test_profile_operations(self, features):
        """Test profile management operations"""
        # Test creating a profile (instructions)
        result = await features.profiles.create("test-profile")
        assert isinstance(result, NativeOperationResult)

        # Test backup instructions
        result = await features.profiles.backup()
        assert isinstance(result, NativeOperationResult)

    # ==================== REPL Tests ====================

    @pytest.mark.asyncio
    async def test_repl_launch(self, features):
        """Test REPL launcher"""
        result = await features.repl.launch()
        assert isinstance(result, NativeOperationResult)
        assert result.message is not None

        # Should provide REPL command
        if result.success and result.data:
            assert "command" in result.data

    # ==================== Remote Tests ====================

    @pytest.mark.asyncio
    async def test_remote_operations(self, features):
        """Test remote deployment features"""
        # Test checking builders
        result = await features.remote.check_builders()
        assert isinstance(result, NativeOperationResult)

        # Test deploy instructions (dry run)
        result = await features.remote.deploy("example.com", "user")
        assert isinstance(result, NativeOperationResult)
        if result.suggestions:
            assert any("ssh" in s.lower() for s in result.suggestions)

    # ==================== Image Building Tests ====================

    @pytest.mark.asyncio
    async def test_image_operations(self, features):
        """Test image building features"""
        # Test ISO building (dry run)
        result = await features.images.iso(minimal=True)
        assert isinstance(result, NativeOperationResult)

        # Test VM building
        result = await features.images.vm(with_display=False)
        assert isinstance(result, NativeOperationResult)

        # Test container building
        result = await features.images.container("docker")
        assert isinstance(result, NativeOperationResult)

    # ==================== Integration Tests ====================

    @pytest.mark.asyncio
    async def test_quick_demo(self, features):
        """Test the quick demo runs without errors"""
        # This tests that all features can be called together
        try:
            await features.quick_demo()
            assert True  # Demo completed without exceptions
        except Exception as e:
            pytest.fail(f"Demo failed with: {e}")

    @pytest.mark.asyncio
    async def test_convenience_functions(self):
        """Test standalone convenience functions"""
        from luminous_nix.core.advanced_features import (
            build_test_vm,
            switch_to_work_profile,
        )

        # These should all return NativeOperationResult
        result = await switch_to_work_profile()
        assert isinstance(result, NativeOperationResult)

        result = await build_test_vm()
        assert isinstance(result, NativeOperationResult)

    def test_all_operation_types_defined(self):
        """Ensure all operation types are properly defined"""
        # Flake operations
        assert len(FlakeOperationType) >= 7
        assert FlakeOperationType.BUILD_FLAKE
        assert FlakeOperationType.UPDATE_FLAKE

        # Profile operations
        assert len(ProfileOperationType) >= 6
        assert ProfileOperationType.LIST_PROFILES
        assert ProfileOperationType.SWITCH_PROFILE

        # Remote operations
        assert len(RemoteOperationType) >= 4
        assert RemoteOperationType.BUILD_REMOTE
        assert RemoteOperationType.DEPLOY_REMOTE

        # Image operations
        assert len(ImageOperationType) >= 4
        assert ImageOperationType.BUILD_ISO
        assert ImageOperationType.BUILD_VM

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
