#!/usr/bin/env python3
"""Test all Phase 2 integrations"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_integrated_backend():
    """Test integrated backend"""
    try:
        from luminous_nix.core.integrated_backend import get_integrated_backend
        backend = get_integrated_backend()
        print("✅ Integrated backend works")
        return True
    except Exception as e:
        print(f"❌ Integrated backend failed: {e}")
        return False

def test_ai_orchestrator():
    """Test AI orchestrator"""
    try:
        from luminous_nix.core.ai_orchestrator import get_ai_orchestrator
        ai = get_ai_orchestrator()
        
        # Test basic query understanding
        response = ai.understand_query("install firefox")
        print(f"✅ AI orchestrator works (using {response.source})")
        return True
    except Exception as e:
        print(f"❌ AI orchestrator failed: {e}")
        return False

def test_tui_import():
    """Test TUI can be imported"""
    try:
        from luminous_nix.ui.main_app import LuminousNixTUI
        print("✅ TUI imports successfully")
        return True
    except Exception as e:
        print(f"❌ TUI import failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Phase 2 integrations...")
    print("-" * 40)
    
    results = []
    results.append(test_integrated_backend())
    results.append(test_ai_orchestrator())
    results.append(test_tui_import())
    
    print("-" * 40)
    if all(results):
        print("✅ All integrations working!")
        sys.exit(0)
    else:
        print("❌ Some integrations failed")
        sys.exit(1)
