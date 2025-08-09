#!/usr/bin/env python3
"""
Quick test runner for CLI Adapter tests
Bypasses Nix environment setup for rapid testing
"""

import sys
import os
from pathlib import Path

# Add both src and backend to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
backend_path = project_root / "backend"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(backend_path))

# Set environment for testing
pythonpath = f"{src_path}:{backend_path}"
os.environ['PYTHONPATH'] = pythonpath
os.environ['NIX_FOR_HUMANITY_TEST_MODE'] = 'true'

try:
    # Import test modules
    print("🧪 Importing test framework...")
    from tests.fixtures.sacred_test_base import ConsciousnessTestBackend
    from tests.fixtures.sacred_test_base import SacredTestBase
    from tests.utils.async_test_runner import AsyncTestCase
    
    print("🚀 Importing CLI Adapter...")
    from nix_for_humanity.adapters.cli_adapter import CLIAdapter
    from nix_for_humanity.core.interface import Query, Response, Intent, IntentType
    from nix_for_humanity.core.types import Command
    
    print("✅ All imports successful!")
    print("\n📊 CLI Adapter Analysis:")
    print(f"   Module: {CLIAdapter.__module__}")
    print(f"   File: {CLIAdapter.__module__.replace('.', '/')}.py")
    print(f"   Methods: {[m for m in dir(CLIAdapter) if not m.startswith('_')]}")
    
    # Test basic initialization
    print("\n🔧 Testing basic initialization...")
    adapter = CLIAdapter()
    print(f"   Session ID: {adapter.session_id}")
    print(f"   Core initialized: {adapter.core is not None}")
    print(f"   Visual mode: {adapter.visual_mode}")
    
    print("\n✅ CLI Adapter basic functionality verified!")
    print("🎯 Ready to run comprehensive test suite")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)