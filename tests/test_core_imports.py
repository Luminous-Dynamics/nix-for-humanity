"""Test that core modules import successfully"""

def test_executor_imports():
    """Test SafeExecutor imports"""
    from luminous_nix.core.executor import SafeExecutor
    assert SafeExecutor is not None

def test_cache_imports():
    """Test CacheService imports"""
    from luminous_nix.services.cache import CacheService
    assert CacheService is not None

def test_search_imports():
    """Test SearchService imports"""
    from luminous_nix.services.search import SearchService
    assert SearchService is not None

def test_native_api_imports():
    """Test NativeNixAPI imports"""
    from luminous_nix.core.native_nix_api import NativeNixAPI
    assert NativeNixAPI is not None

def test_json_optimizer_imports():
    """Test JSONOptimizedNix imports"""
    from luminous_nix.core.json_optimized_nix import JSONOptimizedNix
    assert JSONOptimizedNix is not None
