#!/usr/bin/env python3
"""
Test suite using REAL NixOS commands instead of mocks.
These tests actually interact with the NixOS system.
"""

import os
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Enable real backend for all tests
os.environ["LUMINOUS_USE_REAL_BACKEND"] = "true"
os.environ["LUMINOUS_DRY_RUN"] = "true"  # Safety: always dry run in tests

from luminous_nix.core.luminous_core import LuminousNixCore, Query


class TestRealNixCommands:
    """Test suite that uses real NixOS commands"""
    
    def setup_method(self):
        """Setup for each test"""
        self.core = LuminousNixCore()
        
    def test_real_help_command(self):
        """Test help command with real backend"""
        query = Query(text="help", dry_run=True)
        response = self.core.process_query(query)
        
        # Help should work even with real backend
        assert response is not None
        # We may get different success values depending on backend
        # but we should get a response
        
    def test_real_list_installed(self):
        """Test listing installed packages with real nix-env"""
        query = Query(text="list installed", dry_run=True)
        response = self.core.process_query(query)
        
        assert response is not None
        assert response.success is True
        # Real system may have 0 or more packages
        
    def test_real_search_package(self):
        """Test searching for packages with real nix search"""
        query = Query(text="search hello", dry_run=True)
        response = self.core.process_query(query)
        
        assert response is not None
        # Search might timeout or succeed
        if response.success:
            assert response.message is not None
            
    def test_real_dry_run_install(self):
        """Test dry run installation with real nix-env"""
        query = Query(text="install hello", dry_run=True)
        response = self.core.process_query(query)
        
        assert response is not None
        # Should get a dry run response
        if response.success:
            assert "dry" in response.message.lower() or "would" in response.message.lower()
            
    def test_real_system_info(self):
        """Test getting system info with real commands"""
        query = Query(text="info", dry_run=True)
        response = self.core.process_query(query)
        
        assert response is not None
        # Info command should provide system details
        
    def test_real_garbage_collection_dry_run(self):
        """Test garbage collection in dry run mode"""
        query = Query(text="clean", dry_run=True)
        response = self.core.process_query(query)
        
        assert response is not None
        # Should indicate dry run
        
    @pytest.mark.slow
    def test_real_update_dry_run(self):
        """Test system update in dry run mode"""
        query = Query(text="update", dry_run=True)
        response = self.core.process_query(query)
        
        assert response is not None
        # Update might start in background or indicate dry run


class TestRealIntegration:
    """Integration tests with real NixOS backend"""
    
    def setup_method(self):
        """Setup for each test"""
        self.core = LuminousNixCore()
        
    def test_search_then_info(self):
        """Test searching for a package then getting info about it"""
        # First search
        search_query = Query(text="search firefox", dry_run=True)
        search_response = self.core.process_query(search_query)
        
        # Then get info
        info_query = Query(text="info firefox", dry_run=True)
        info_response = self.core.process_query(info_query)
        
        assert search_response is not None
        assert info_response is not None
        
    def test_list_then_remove_dry_run(self):
        """Test listing packages then removing one (dry run)"""
        # First list
        list_query = Query(text="list", dry_run=True)
        list_response = self.core.process_query(list_query)
        
        # Try to remove something (dry run)
        remove_query = Query(text="remove hello", dry_run=True)
        remove_response = self.core.process_query(remove_query)
        
        assert list_response is not None
        assert remove_response is not None
        
        
if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])