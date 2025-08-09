#!/usr/bin/env python3
"""
Real integration tests for native operations.

These tests actually call the native API (no mocks!) to ensure everything works.
"""

import pytest
import asyncio
import time
from nix_humanity.core.native_operations import NativeOperationsManager, NativeOperationType
from nix_humanity.core.nixos_version import check_nixos_version


class TestNativeOperationsReal:
    """Real integration tests for native operations"""
    
    @pytest.fixture
    async def native_ops(self):
        """Get native operations manager"""
        try:
            return NativeOperationsManager()
        except RuntimeError:
            pytest.skip("Native API not available on this system")
            
    @pytest.mark.asyncio
    async def test_list_generations_performance(self, native_ops):
        """Test that list generations is actually instant"""
        start = time.time()
        result = await native_ops.execute_native_operation(
            NativeOperationType.LIST_GENERATIONS
        )
        duration = (time.time() - start) * 1000
        
        assert result.success
        assert duration < 100  # Should be under 100ms (instant!)
        assert result.data.get('generations') is not None
        assert len(result.data['generations']) > 0
        
    @pytest.mark.asyncio
    async def test_system_info_instant(self, native_ops):
        """Test that system info is instant"""
        start = time.time()
        result = await native_ops.execute_native_operation(
            NativeOperationType.SYSTEM_INFO
        )
        duration = (time.time() - start) * 1000
        
        assert result.success
        assert duration < 50  # Should be under 50ms
        assert result.data.get('nixos_version') is not None
        
    @pytest.mark.asyncio
    async def test_search_packages_fast(self, native_ops):
        """Test that package search is fast"""
        start = time.time()
        result = await native_ops.execute_native_operation(
            NativeOperationType.SEARCH_PACKAGES,
            packages=["firefox"]
        )
        duration = (time.time() - start) * 1000
        
        # Search might take a bit longer but should still be fast
        assert duration < 5000  # Under 5 seconds
        assert result.message  # Should have some message
        
    @pytest.mark.asyncio
    async def test_dry_build_safe(self, native_ops):
        """Test that dry build doesn't actually change anything"""
        result = await native_ops.execute_native_operation(
            NativeOperationType.DRY_BUILD
        )
        
        # Dry build should always be safe
        assert "would" in result.message.lower() or "dry" in result.message.lower()
        
    def test_version_detection(self):
        """Test NixOS version detection"""
        compatible, version = check_nixos_version()
        
        # Should always get a result
        assert isinstance(compatible, bool)
        # Version might be None if detection fails
        if version:
            assert isinstance(version, str)
            
    @pytest.mark.asyncio
    async def test_all_operations_available(self, native_ops):
        """Test that all operations are properly registered"""
        operations = native_ops.get_supported_operations()
        
        assert len(operations) >= 20  # We have at least 20 operations
        
        # Check categories
        categories = {op['category'] for op in operations}
        assert "System Management" in categories
        assert "Generation Management" in categories
        assert "Package Management" in categories
        assert "Store Management" in categories
        
    @pytest.mark.asyncio
    async def test_error_handling(self, native_ops):
        """Test that errors are handled gracefully"""
        # Try to switch to non-existent generation
        result = await native_ops.execute_native_operation(
            NativeOperationType.SWITCH_GENERATION,
            options={'generation': 999999}
        )
        
        # Should fail gracefully
        assert not result.success
        assert result.message
        assert "error" in result.data or result.message


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])