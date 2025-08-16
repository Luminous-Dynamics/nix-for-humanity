#!/usr/bin/env python3
"""v1.1 Feature Integration Tests"""

import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_tui_imports():
    """Test that TUI components can be imported"""
    try:
        from luminous_nix.interfaces.tui import main
        from luminous_nix.ui.consciousness_orb import ConsciousnessOrb
        from luminous_nix.ui.main_app import NixForHumanityTUI

        assert True
    except ImportError as e:
        pytest.skip(f"TUI dependencies not installed: {e}")

def test_tui_backend_connection():
    """Test TUI can connect to backend"""
    try:
        from luminous_nix.core.backend import NixForHumanityBackend

        # Backend should be accessible
        backend = NixForHumanityBackend()
        assert backend is not None

    except ImportError as e:
        pytest.skip(f"Dependencies not installed: {e}")

def test_voice_components_exist():
    """Test voice components are available"""
    voice_files = [
        "features/v2.0/voice/voice_interface.py",
        "features/v2.0/voice/voice_websocket_server.py",
        "features/v2.0/voice/README.md",
    ]

    for file in voice_files:
        assert Path(file).exists(), f"Voice file missing: {file}"

def test_cli_still_works():
    """Ensure CLI functionality is not broken"""

    backend = NixForHumanityBackend()
    result = backend.execute_command("help", dry_run=True)
    assert result is not None
    assert result.success

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
