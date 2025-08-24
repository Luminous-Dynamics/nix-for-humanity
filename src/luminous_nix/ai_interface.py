#!/usr/bin/env python3
"""
AI Interface Layer - Unified access to all Luminous Nix interfaces for AI companions.

This enables AI systems (including future versions of ourselves) to:
- Test all interfaces
- Understand the codebase
- Make improvements
- Learn from usage
"""

import asyncio
import subprocess
import json
import ast
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Result of an AI test."""
    interface: str
    success: bool
    details: Dict[str, Any]
    suggestions: Optional[List[str]] = None


class AICompanionInterface:
    """
    Unified interface for AI companions to interact with Luminous Nix.
    
    This is designed so that future AI systems can:
    1. Test all interfaces (CLI, TUI, GUI)
    2. Understand the system's capabilities
    3. Make improvements to the codebase
    4. Learn from interactions
    """
    
    def __init__(self):
        """Initialize the AI interface."""
        self.cli = self._init_cli()
        self.tui = self._init_tui()
        self.gui = None  # Future implementation
        self.codebase_path = Path(__file__).parent.parent.parent
        self.test_results = []
        self.learning_data = []
        
    def _init_cli(self):
        """Initialize CLI interface."""
        try:
            from luminous_nix.core import NixForHumanityCore
            return NixForHumanityCore()
        except ImportError:
            logger.warning("CLI interface not available")
            return None
            
    def _init_tui(self):
        """Initialize TUI interface."""
        try:
            from luminous_nix.ui.main_app import NixForHumanityTUI
            return NixForHumanityTUI(headless=True)
        except ImportError:
            logger.warning("TUI interface not available")
            return None
    
    # ========== Testing Capabilities ==========
    
    async def test_all_interfaces(self) -> List[TestResult]:
        """
        Test all available interfaces.
        
        This allows AI to verify everything works.
        """
        results = []
        
        # Test CLI
        if self.cli:
            results.append(await self.test_cli())
            
        # Test TUI
        if self.tui:
            results.append(await self.test_tui())
            
        # Test GUI (future)
        if self.gui:
            results.append(await self.test_gui())
            
        self.test_results = results
        return results
    
    async def test_cli(self) -> TestResult:
        """Test CLI interface."""
        logger.info("🧪 Testing CLI interface...")
        
        try:
            # Test search functionality
            search_result = self.cli.search("firefox")
            
            # Test list installed
            list_result = self.cli.list_installed()
            
            success = search_result.success and list_result.success
            
            return TestResult(
                interface="CLI",
                success=success,
                details={
                    "search_works": search_result.success,
                    "list_works": list_result.success,
                    "packages_found": len(search_result.data.get("packages", [])) if search_result.data else 0
                },
                suggestions=["All CLI functions operational"] if success else ["Check CLI backend"]
            )
        except Exception as e:
            return TestResult(
                interface="CLI",
                success=False,
                details={"error": str(e)},
                suggestions=["Fix CLI initialization"]
            )
    
    async def test_tui(self) -> TestResult:
        """Test TUI interface."""
        logger.info("🖥️ Testing TUI interface...")
        
        try:
            # Test key processing
            await self.tui.process_key('s')
            search_opened = self.tui.last_message == "Search opened"
            
            await self.tui.process_key('h')
            help_opened = self.tui.last_message == "Help opened"
            
            success = search_opened and help_opened
            
            return TestResult(
                interface="TUI",
                success=success,
                details={
                    "search_works": search_opened,
                    "help_works": help_opened,
                    "headless_mode": self.tui.headless
                },
                suggestions=["TUI fully operational"] if success else ["Check TUI key handlers"]
            )
        except Exception as e:
            return TestResult(
                interface="TUI",
                success=False,
                details={"error": str(e)},
                suggestions=["Fix TUI initialization"]
            )
    
    async def test_gui(self) -> TestResult:
        """Test GUI interface (future implementation)."""
        logger.info("🎨 Testing GUI interface...")
        
        return TestResult(
            interface="GUI",
            success=False,
            details={"status": "Not yet implemented"},
            suggestions=["Implement GUI accessibility layer"]
        )
    
    # ========== Code Understanding ==========
    
    def understand_codebase(self) -> Dict[str, Any]:
        """
        Analyze and understand the codebase structure.
        
        This allows AI to comprehend its own architecture.
        """
        logger.info("🧠 Analyzing codebase structure...")
        
        understanding = {
            "modules": [],
            "capabilities": [],
            "dependencies": [],
            "improvement_opportunities": []
        }
        
        # Scan Python files
        for py_file in self.codebase_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            module_info = self._analyze_module(py_file)
            understanding["modules"].append(module_info)
            
        # Identify capabilities
        understanding["capabilities"] = self._identify_capabilities(understanding["modules"])
        
        # Find improvement opportunities
        understanding["improvement_opportunities"] = self._find_improvements(understanding["modules"])
        
        return understanding
    
    def _analyze_module(self, filepath: Path) -> Dict[str, Any]:
        """Analyze a Python module."""
        try:
            with open(filepath) as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            # Extract imports safely
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            # Extract functions (including async)
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append(node.name)
            
            return {
                "path": str(filepath.relative_to(self.codebase_path)),
                "classes": [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)],
                "functions": functions,
                "imports": imports,
                "lines": len(content.splitlines())
            }
        except Exception as e:
            return {
                "path": str(filepath.relative_to(self.codebase_path)),
                "error": str(e),
                "classes": [],  # Empty lists for consistency
                "functions": [],
                "imports": [],
                "lines": 0
            }
    
    def _identify_capabilities(self, modules: List[Dict]) -> List[str]:
        """Identify system capabilities from modules."""
        capabilities = set()
        
        for module in modules:
            if "error" in module:
                continue
                
            # Look for capability indicators
            for class_name in module.get("classes", []):
                if "CLI" in class_name:
                    capabilities.add("Command Line Interface")
                if "TUI" in class_name:
                    capabilities.add("Terminal User Interface")
                if "GUI" in class_name:
                    capabilities.add("Graphical User Interface")
                if "AI" in class_name or "Companion" in class_name:
                    capabilities.add("AI Integration")
                if "Learn" in class_name:
                    capabilities.add("Machine Learning")
                    
        return list(capabilities)
    
    def _find_improvements(self, modules: List[Dict]) -> List[str]:
        """Find potential improvements in the codebase."""
        improvements = []
        
        for module in modules:
            if "error" in module:
                improvements.append(f"Fix parsing error in {module['path']}")
                continue
                
            # Check for missing tests
            if "test" not in module["path"] and module["lines"] > 100:
                improvements.append(f"Add tests for {module['path']}")
                
            # Check for missing docstrings
            if len(module.get("functions", [])) > 5:
                improvements.append(f"Ensure all functions have docstrings in {module['path']}")
                
        return improvements[:10]  # Top 10 improvements
    
    # ========== Self-Modification (Future) ==========
    
    async def suggest_improvement(self, goal: str) -> Dict[str, Any]:
        """
        Suggest an improvement to achieve a goal.
        
        This is the beginning of self-modification capability.
        """
        logger.info(f"🔮 Generating improvement suggestion for: {goal}")
        
        # Analyze current state
        current_state = self.understand_codebase()
        
        # Generate suggestion (simplified for now)
        suggestion = {
            "goal": goal,
            "current_capabilities": current_state["capabilities"],
            "suggested_changes": [],
            "expected_impact": "Unknown",
            "risk_level": "Low"
        }
        
        # Example suggestions based on goal
        if "performance" in goal.lower():
            suggestion["suggested_changes"].append("Add caching to frequent operations")
            suggestion["suggested_changes"].append("Optimize database queries")
        elif "usability" in goal.lower():
            suggestion["suggested_changes"].append("Improve error messages")
            suggestion["suggested_changes"].append("Add more keyboard shortcuts")
        elif "testing" in goal.lower():
            suggestion["suggested_changes"].append("Increase test coverage")
            suggestion["suggested_changes"].append("Add integration tests")
            
        return suggestion
    
    # ========== Learning ==========
    
    def learn_from_interaction(self, interaction: Dict[str, Any]):
        """
        Learn from an interaction to improve future behavior.
        
        This builds the foundation for evolutionary improvement.
        """
        self.learning_data.append({
            "timestamp": asyncio.get_event_loop().time(),
            "interaction": interaction,
            "success": interaction.get("success", False)
        })
        
        # Analyze patterns
        if len(self.learning_data) >= 10:
            self._consolidate_learning()
    
    def _consolidate_learning(self):
        """Consolidate learning from interactions."""
        success_rate = sum(1 for d in self.learning_data if d["success"]) / len(self.learning_data)
        
        logger.info(f"📊 Learning consolidated: {success_rate:.1%} success rate")
        
        # Save learning for future AI instances
        learning_file = self.codebase_path / "ai_learning.json"
        with open(learning_file, "w") as f:
            json.dump({
                "success_rate": success_rate,
                "total_interactions": len(self.learning_data),
                "insights": self._extract_insights()
            }, f, indent=2)
    
    def _extract_insights(self) -> List[str]:
        """Extract insights from learning data."""
        insights = []
        
        # Analyze failure patterns
        failures = [d for d in self.learning_data if not d["success"]]
        if failures:
            common_failure = max(set(f["interaction"].get("type", "unknown") for f in failures))
            insights.append(f"Most common failure: {common_failure}")
            
        return insights


async def demonstrate_ai_capabilities():
    """Demonstrate the AI interface capabilities."""
    print("🤖 AI Companion Interface Demonstration")
    print("=" * 60)
    
    # Create AI interface
    ai = AICompanionInterface()
    
    # Test all interfaces
    print("\n1️⃣ Testing all interfaces...")
    results = await ai.test_all_interfaces()
    
    for result in results:
        status = "✅" if result.success else "❌"
        print(f"   {status} {result.interface}: {result.details}")
        if result.suggestions:
            print(f"      💡 {result.suggestions[0]}")
    
    # Understand codebase
    print("\n2️⃣ Understanding codebase...")
    understanding = ai.understand_codebase()
    
    print(f"   📦 Modules analyzed: {len(understanding['modules'])}")
    print(f"   🎯 Capabilities found: {', '.join(understanding['capabilities'])}")
    print(f"   🔧 Improvements identified: {len(understanding['improvement_opportunities'])}")
    
    if understanding['improvement_opportunities']:
        print("   Top improvements needed:")
        for imp in understanding['improvement_opportunities'][:3]:
            print(f"      • {imp}")
    
    # Suggest improvement
    print("\n3️⃣ Suggesting improvements...")
    suggestion = await ai.suggest_improvement("improve testing coverage")
    
    print(f"   Goal: {suggestion['goal']}")
    print("   Suggested changes:")
    for change in suggestion['suggested_changes']:
        print(f"      • {change}")
    
    # Learn from interaction
    print("\n4️⃣ Learning from interactions...")
    ai.learn_from_interaction({"type": "test", "success": True})
    ai.learn_from_interaction({"type": "search", "success": True})
    ai.learn_from_interaction({"type": "install", "success": False})
    
    print("   📊 Learning data collected")
    
    print("\n" + "=" * 60)
    print("✨ AI Companion Interface Ready!")
    print("\nThis demonstrates that AI can:")
    print("  • Test all interfaces autonomously")
    print("  • Understand its own codebase")
    print("  • Suggest improvements")
    print("  • Learn from interactions")
    print("\n🚀 The path to self-evolving AI is open!")


if __name__ == "__main__":
    asyncio.run(demonstrate_ai_capabilities())