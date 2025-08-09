#!/usr/bin/env python3
"""
Test the Native Python-Nix Backend Integration
This verifies that our direct nixos-rebuild-ng API integration works correctly
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from core.backend import NixForHumanityBackend, create_backend
from api.schema import Request, Response


def progress_callback(message: str, progress: float):
    """Display progress updates"""
    bar_length = 40
    filled_length = int(bar_length * progress)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    print(f"\r[{bar}] {progress:.0%} - {message}", end='', flush=True)
    if progress >= 1.0:
        print()  # New line when complete


async def test_native_backend():
    """Test the native backend integration"""
    print("🧪 Testing Native Python-Nix Backend Integration\n")
    
    # Enable native backend
    os.environ['NIX_HUMANITY_PYTHON_BACKEND'] = 'true'
    
    # Create backend with progress callback
    backend = create_backend(progress_callback)
    
    # Test 1: System information query (should use traditional backend)
    print("Test 1: General query (traditional backend)")
    request = Request(
        query="What is NixOS?",
        context={"personality": "minimal"}
    )
    
    response = backend.process(request)
    print(f"Success: {response.success}")
    print(f"Response: {response.text[:100]}...")
    print()
    
    # Test 2: Update system query (should use native backend)
    print("\nTest 2: System update query (native backend)")
    request = Request(
        query="update my system",
        context={"dry_run": True}
    )
    
    response = await backend.process_request(request)
    print(f"Success: {response.success}")
    print(f"Plan: {response.plan}")
    print(f"Explanation: {response.explanation}")
    
    # Check if native API was used
    if hasattr(response, 'data') and response.data.get('education'):
        print("\n✅ Native API integration successful!")
        print(f"Educational context: {response.data['education']}")
    
    # Test 3: Install package query
    print("\n\nTest 3: Install package query (native backend)")
    request = Request(
        query="install firefox",
        context={"execute": False}
    )
    
    response = await backend.process_request(request)
    print(f"Success: {response.success}")
    print(f"Explanation: {response.explanation}")
    
    # Test 4: Rollback query
    print("\n\nTest 4: Rollback query (native backend)")
    request = Request(
        query="rollback to previous generation",
        context={"dry_run": True}
    )
    
    response = await backend.process_request(request)
    print(f"Success: {response.success}")
    print(f"Plan: {response.plan}")
    
    # Test 5: Check native API availability
    print("\n\n🔍 Checking Native API Status:")
    from backend.core.nix_integration import NixOSIntegration
    integration = NixOSIntegration()
    status = integration.get_status()
    
    print(f"Native API Available: {status['native_api_available']}")
    print(f"Backend Type: {status['backend']}")
    print(f"Performance Boost: {status['performance_boost']}")
    
    # Test 6: Get system info
    print("\n\n📊 System Information:")
    sys_info = await integration.get_system_info()
    
    print(f"NixOS Version: {sys_info.get('nixos_version', 'Unknown')}")
    print(f"Using Flakes: {sys_info.get('using_flakes', False)}")
    print(f"Total Generations: {sys_info.get('total_generations', 0)}")
    print(f"Native API: {sys_info.get('native_api', False)}")
    
    print("\n\n✨ All tests complete!")


async def test_error_handling():
    """Test error handling in native backend"""
    print("\n\n🔥 Testing Error Handling:\n")
    
    os.environ['NIX_HUMANITY_PYTHON_BACKEND'] = 'true'
    backend = create_backend()
    
    # Test with invalid query
    request = Request(
        query="do something invalid",
        context={}
    )
    
    response = await backend.process_request(request)
    print(f"Handled invalid query: {response.success}")
    print(f"Error explanation: {response.explanation}")


async def main():
    """Run all tests"""
    try:
        # First check if we can import the native API
        print("🔍 Checking for nixos-rebuild-ng API...\n")
        
        try:
            from backend.python.native_nix_backend import NATIVE_API_AVAILABLE
            print(f"Native API Available: {NATIVE_API_AVAILABLE}")
            
            if not NATIVE_API_AVAILABLE:
                print("\n⚠️  Native API not available - using fallback mode")
                print("This is expected if nixos-rebuild-ng is not installed")
                
        except ImportError as e:
            print(f"Could not import native backend: {e}")
            
        # Run tests
        await test_native_backend()
        await test_error_handling()
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())