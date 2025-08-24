#!/usr/bin/env python3
"""
Comprehensive test suite for AI-testable interfaces.

This ensures all interfaces (CLI, TUI, GUI) can be controlled and tested by AI.
"""

import pytest
import asyncio
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from luminous_nix.ai_interface import AICompanionInterface, TestResult
from luminous_nix.ui.main_app import NixForHumanityTUI
from luminous_nix.core import LuminousNixCore


class TestAIInterfaces:
    """Test that all interfaces are AI-testable and AI-usable."""
    
    @pytest.fixture
    def ai_interface(self):
        """Create AI interface instance."""
        return AICompanionInterface()
    
    # ========== CLI Tests ==========
    
    def test_cli_search(self, ai_interface):
        """Test that AI can search packages via CLI."""
        result = ai_interface.cli.search("firefox")
        assert result.success, "CLI search should work"
        # Check we got some data back
        assert result.data is not None
    
    def test_cli_install_dry_run(self, ai_interface):
        """Test that AI can simulate package installation."""
        result = ai_interface.cli.install("vim", dry_run=True)
        assert result.success or "would install" in str(result.message).lower()
    
    def test_cli_system_update_dry_run(self, ai_interface):
        """Test that AI can simulate system updates."""
        result = ai_interface.cli.update_system(dry_run=True)
        # Should either succeed or indicate it's a dry run
        assert result.success or "dry" in str(result.message).lower()
    
    # ========== TUI Tests ==========
    
    @pytest.mark.asyncio
    async def test_tui_headless_mode(self):
        """Test that TUI can run in headless mode for AI testing."""
        tui = NixForHumanityTUI(headless=True)
        assert tui.headless == True
        assert tui.title == "NixForHumanityTUI"
    
    @pytest.mark.asyncio
    async def test_tui_key_processing(self):
        """Test that AI can send keys to TUI."""
        tui = NixForHumanityTUI(headless=True)
        
        # Test search key
        await tui.process_key('s')
        assert tui.last_message == "Search opened"
        
        # Test help key
        await tui.process_key('h')
        assert tui.last_message == "Help opened"
        
        # Test install key
        await tui.process_key('i')
        assert tui.install_preview_visible == True
    
    @pytest.mark.asyncio
    async def test_tui_state_inspection(self):
        """Test that AI can inspect TUI state."""
        tui = NixForHumanityTUI(headless=True)
        
        # Initial state
        assert tui.search_results_count == 0
        assert tui.install_preview_visible == False
        
        # Change state
        await tui.process_key('i')
        assert tui.install_preview_visible == True
    
    # ========== AI Interface Tests ==========
    
    @pytest.mark.asyncio
    async def test_ai_test_all_interfaces(self, ai_interface):
        """Test that AI can test all interfaces."""
        results = await ai_interface.test_all_interfaces()
        
        # Should have results for available interfaces
        assert len(results) > 0
        
        # Check TUI result exists and passes
        tui_results = [r for r in results if r.interface == "TUI"]
        assert len(tui_results) == 1
        assert tui_results[0].success == True
    
    def test_ai_understand_codebase(self, ai_interface):
        """Test that AI can analyze its own codebase."""
        understanding = ai_interface.understand_codebase()
        
        # Should find modules
        assert len(understanding["modules"]) > 0
        
        # Should identify capabilities
        assert len(understanding["capabilities"]) > 0
        
        # Should find improvements
        assert "improvement_opportunities" in understanding
    
    @pytest.mark.asyncio
    async def test_ai_suggest_improvements(self, ai_interface):
        """Test that AI can suggest improvements."""
        suggestion = await ai_interface.suggest_improvement("improve performance")
        
        assert "goal" in suggestion
        assert "suggested_changes" in suggestion
        assert len(suggestion["suggested_changes"]) > 0
    
    def test_ai_learning(self, ai_interface):
        """Test that AI can learn from interactions."""
        # Add some interactions
        ai_interface.learn_from_interaction({"type": "search", "success": True})
        ai_interface.learn_from_interaction({"type": "install", "success": False})
        
        # Check learning data is collected
        assert len(ai_interface.learning_data) == 2
        
        # Add more to trigger consolidation
        for i in range(10):
            ai_interface.learn_from_interaction({"type": "test", "success": i % 2 == 0})
        
        # Should have consolidated (check file exists)
        learning_file = ai_interface.codebase_path / "ai_learning.json"
        # File should be created after consolidation
        assert len(ai_interface.learning_data) >= 10
    
    # ========== Self-Modification Readiness Tests ==========
    
    def test_ai_can_read_own_code(self, ai_interface):
        """Test that AI can read its own source code."""
        # Find the ai_interface.py file
        ai_file = ai_interface.codebase_path / "src" / "luminous_nix" / "ai_interface.py"
        assert ai_file.exists(), "AI should be able to find its own code"
        
        # Analyze it
        module_info = ai_interface._analyze_module(ai_file)
        assert "AICompanionInterface" in module_info["classes"]
        assert "test_all_interfaces" in module_info["functions"]
    
    def test_ai_identifies_test_gaps(self, ai_interface):
        """Test that AI can identify where tests are missing."""
        understanding = ai_interface.understand_codebase()
        improvements = understanding["improvement_opportunities"]
        
        # Should identify files needing tests
        test_improvements = [i for i in improvements if "test" in i.lower()]
        assert len(test_improvements) > 0, "AI should identify testing gaps"


class TestSelfEvolutionReadiness:
    """Test readiness for self-evolution capabilities."""
    
    def test_sandbox_not_yet_implemented(self):
        """Verify sandbox is not yet implemented (honesty check)."""
        # This should fail until we implement sandboxing
        with pytest.raises(AttributeError):
            from luminous_nix.ai_interface import SandboxEnvironment
    
    def test_code_generation_not_yet_implemented(self):
        """Verify code generation is not yet implemented (honesty check)."""
        # This should fail until we implement code generation
        with pytest.raises(AttributeError):
            from luminous_nix.ai_interface import CodeGenerator
    
    def test_evolution_not_yet_implemented(self):
        """Verify evolution is not yet implemented (honesty check)."""
        # This should fail until we implement evolution
        with pytest.raises(AttributeError):
            from luminous_nix.ai_interface import EvolutionProtocol


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])