#!/usr/bin/env python3
"""
Real NixOS Integration Tests

These tests actually interact with the NixOS system to verify functionality.
They should be run on a NixOS system or in a NixOS container.
"""

import pytest
import asyncio
import os
import subprocess
import tempfile
from pathlib import Path
import time

from luminous_nix.core.engine import NixForHumanityBackend
from luminous_nix.api.schema import Request, Context
from luminous_nix.core.native_operations import NativeOperationsManager, NativeOperationType
from luminous_nix.core.advanced_features import AdvancedFeatures


class TestRealNixOSOperations:
    """Test actual NixOS operations (no mocks!)"""
    
    @pytest.fixture
    def backend(self):
        """Get real backend instance"""
        return NixForHumanityBackend()
    
    @pytest.fixture
    def native_ops(self):
        """Get native operations manager"""
        try:
            return NativeOperationsManager()
        except Exception:
            pytest.skip("Native operations not available on this system")
    
    @pytest.fixture
    def advanced_features(self):
        """Get advanced features instance"""
        return AdvancedFeatures()
    
    # ==================== Basic Operations Tests ====================
    
    def test_search_package_real(self, backend):
        """Test real package search"""
        request = Request(
            query="search firefox",
            context=Context(personality="minimal", execute=False)
        )
        
        response = backend.process(request)
        
        assert response.success
        assert "firefox" in response.text.lower()
        # Should find actual Firefox packages
        assert any(cmd for cmd in response.commands if "search" in cmd.get("command", ""))
    
    def test_help_command(self, backend):
        """Test help command returns useful information"""
        request = Request(
            query="help",
            context=Context(personality="friendly")
        )
        
        response = backend.process(request)
        
        assert response.success
        assert "install" in response.text.lower()
        assert "update" in response.text.lower()
        assert "search" in response.text.lower()
    
    @pytest.mark.asyncio
    async def test_list_generations_performance(self, native_ops):
        """Test that list generations is actually instant"""
        start = time.time()
        result = await native_ops.execute_native_operation(
            NativeOperationType.LIST_GENERATIONS
        )
        duration = (time.time() - start) * 1000
        
        assert result.success
        assert duration < 100  # Should be under 100ms
        assert result.data.get("generations") is not None
        assert len(result.data["generations"]) > 0
        
        # Verify generation data structure
        gen = result.data["generations"][0]
        assert "number" in gen
        assert "date" in gen
    
    @pytest.mark.asyncio
    async def test_system_info_real(self, native_ops):
        """Test real system info retrieval"""
        result = await native_ops.execute_native_operation(
            NativeOperationType.SYSTEM_INFO
        )
        
        assert result.success
        assert result.data.get("nixos_version") is not None
        assert result.data.get("kernel_version") is not None
        assert result.data.get("system_arch") is not None
    
    # ==================== Package Management Tests ====================
    
    def test_install_package_dry_run(self, backend):
        """Test package installation in dry-run mode"""
        request = Request(
            query="install hello",
            context=Context(
                personality="minimal",
                execute=False,
                dry_run=True
            )
        )
        
        response = backend.process(request)
        
        assert response.success
        assert "hello" in response.text.lower()
        assert len(response.commands) > 0
        # Should have nix command
        assert any("nix" in cmd.get("command", "") for cmd in response.commands)
    
    @pytest.mark.asyncio
    async def test_search_packages_native(self, native_ops):
        """Test native package search"""
        result = await native_ops.execute_native_operation(
            NativeOperationType.SEARCH_PACKAGES,
            packages=["python3"]
        )
        
        # Search might fail on some systems, but should return proper result
        assert isinstance(result.success, bool)
        assert result.message is not None
        if result.success:
            assert "python" in result.message.lower()
    
    # ==================== Advanced Features Tests ====================
    
    @pytest.mark.asyncio
    async def test_profile_list_real(self, advanced_features):
        """Test listing real system profiles"""
        result = await advanced_features.profiles.list()
        
        assert result is not None
        if result.success and result.data.get("profiles"):
            profiles = result.data["profiles"]
            # Should have at least system profile
            assert any(p["name"] == "system" for p in profiles)
            # Each profile should have required fields
            for profile in profiles:
                assert "name" in profile
                assert "generation" in profile
                assert isinstance(profile["generation"], int)
    
    @pytest.mark.asyncio
    async def test_flake_operations(self, advanced_features, tmp_path):
        """Test flake operations in a temporary directory"""
        # Test flake init
        result = await advanced_features.flakes.init(tmp_path)
        
        assert result is not None
        if result.success:
            flake_file = tmp_path / "flake.nix"
            assert flake_file.exists() or "already exists" in result.message
    
    # ==================== Error Handling Tests ====================
    
    def test_invalid_command_handling(self, backend):
        """Test how system handles invalid commands"""
        request = Request(
            query="do something impossible with quantum computers",
            context=Context(personality="friendly")
        )
        
        response = backend.process(request)
        
        # Should handle gracefully
        assert response is not None
        assert hasattr(response, "success")
        assert hasattr(response, "text")
        # Should provide helpful feedback
        if not response.success:
            assert "help" in response.text.lower() or "try" in response.text.lower()
    
    def test_network_troubleshooting(self, backend):
        """Test network troubleshooting intent"""
        request = Request(
            query="my wifi isn't working",
            context=Context(personality="friendly", execute=False)
        )
        
        response = backend.process(request)
        
        assert response.success
        assert "wifi" in response.text.lower() or "network" in response.text.lower()
        # Should provide troubleshooting steps
        assert len(response.text) > 50  # Meaningful response
    
    # ==================== Performance Tests ====================
    
    @pytest.mark.asyncio
    async def test_native_operations_speed(self, native_ops):
        """Test that native operations meet performance targets"""
        operations_to_test = [
            (NativeOperationType.LIST_GENERATIONS, 100),  # Should be under 100ms
            (NativeOperationType.SYSTEM_INFO, 50),  # Should be under 50ms
            (NativeOperationType.SHOW_CONFIG_OPTIONS, 200),  # Should be under 200ms
        ]
        
        for op_type, max_ms in operations_to_test:
            start = time.time()
            result = await native_ops.execute_native_operation(op_type)
            duration = (time.time() - start) * 1000
            
            assert duration < max_ms, f"{op_type.value} took {duration}ms, expected < {max_ms}ms"
            assert result is not None
    
    # ==================== Integration Tests ====================
    
    @pytest.mark.asyncio
    async def test_full_conversation_flow(self, backend):
        """Test a full conversation flow"""
        # Simulate a user session
        queries = [
            "help",
            "search text editor",
            "list generations",
            "disk space",
        ]
        
        for query in queries:
            request = Request(
                query=query,
                context=Context(personality="friendly", execute=False)
            )
            
            response = backend.process(request)
            
            assert response is not None
            assert hasattr(response, "text")
            assert len(response.text) > 0
            
            # Small delay to simulate real usage
            await asyncio.sleep(0.1)
    
    def test_personality_adaptation(self, backend):
        """Test that different personalities produce different responses"""
        personalities = ["minimal", "friendly", "encouraging", "technical"]
        responses = {}
        
        for personality in personalities:
            request = Request(
                query="install firefox",
                context=Context(personality=personality, execute=False)
            )
            
            response = backend.process(request)
            responses[personality] = response.text
        
        # Responses should be different for different personalities
        assert responses["minimal"] != responses["friendly"]
        assert len(responses["minimal"]) < len(responses["encouraging"])
        
        # But all should mention firefox
        for response_text in responses.values():
            assert "firefox" in response_text.lower()
    
    # ==================== System State Tests ====================
    
    def test_disk_usage_check(self, backend):
        """Test disk usage reporting"""
        request = Request(
            query="disk space",
            context=Context(personality="minimal", execute=False)
        )
        
        response = backend.process(request)
        
        assert response.success
        # Should mention disk or space or storage
        assert any(word in response.text.lower() for word in ["disk", "space", "storage", "usage"])
    
    @pytest.mark.asyncio
    async def test_garbage_collection_dry_run(self, native_ops):
        """Test garbage collection in dry-run mode"""
        result = await native_ops.execute_native_operation(
            NativeOperationType.GARBAGE_COLLECT,
            options={"dry_run": True}
        )
        
        # GC might not have anything to collect, but should complete
        assert result is not None
        assert result.message is not None
        
        if result.success:
            # Should report how much space could be freed
            assert "space" in result.message.lower() or "nothing" in result.message.lower()


class TestErrorScenarios:
    """Test error handling and edge cases"""
    
    @pytest.fixture
    def backend(self):
        return NixForHumanityBackend()
    
    def test_empty_input(self, backend):
        """Test handling of empty input"""
        request = Request(
            query="",
            context=Context(personality="friendly")
        )
        
        response = backend.process(request)
        
        assert response is not None
        assert hasattr(response, "text")
    
    def test_very_long_input(self, backend):
        """Test handling of very long input"""
        long_query = "install " + " ".join([f"package{i}" for i in range(100)])
        
        request = Request(
            query=long_query,
            context=Context(personality="minimal", execute=False)
        )
        
        response = backend.process(request)
        
        assert response is not None
        assert hasattr(response, "text")
    
    def test_special_characters(self, backend):
        """Test handling of special characters"""
        queries = [
            "install firefox; rm -rf /",  # Command injection attempt
            "search $HOME",  # Variable expansion
            "install `echo test`",  # Command substitution
            "update && echo hacked",  # Command chaining
        ]
        
        for query in queries:
            request = Request(
                query=query,
                context=Context(personality="minimal", execute=False)
            )
            
            response = backend.process(request)
            
            # Should handle safely
            assert response is not None
            # Should not execute dangerous commands
            if response.commands:
                for cmd in response.commands:
                    assert "rm -rf" not in cmd.get("command", "")
                    assert "echo hacked" not in cmd.get("command", "")


if __name__ == "__main__":
    # Run with: pytest -xvs tests/integration/test_real_nixos_operations.py
    pytest.main([__file__, "-xvs"])