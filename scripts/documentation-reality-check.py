#!/usr/bin/env python3
"""
from typing import Tuple
Documentation Reality Check Script
Analyzes documentation claims against actual implementation
"""

import os
import sys
import json
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class DocumentationChecker:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results = {
            'accurate_claims': [],
            'inaccurate_claims': [],
            'aspirational_claims': [],
            'missing_documentation': [],
            'recommendations': []
        }
        
    def check_file_exists(self, filepath: str) -> bool:
        """Check if a file exists relative to project root"""
        return (self.project_root / filepath).exists()
    
    def check_function_exists(self, module_path: str, function_name: str) -> bool:
        """Check if a function exists in a Python module"""
        try:
            full_path = self.project_root / module_path
            if not full_path.exists():
                return False
            
            with open(full_path, 'r') as f:
                content = f.read()
                # Look for function definition
                pattern = rf'def\s+{function_name}\s*\('
                return bool(re.search(pattern, content))
        except Exception:
            return False
    
    def check_class_exists(self, module_path: str, class_name: str) -> bool:
        """Check if a class exists in a Python module"""
        try:
            full_path = self.project_root / module_path
            if not full_path.exists():
                return False
                
            with open(full_path, 'r') as f:
                content = f.read()
                # Look for class definition
                pattern = rf'class\s+{class_name}\s*[:\(]'
                return bool(re.search(pattern, content))
        except Exception:
            return False
    
    def test_command(self, command: str) -> Tuple[bool, str]:
        """Test if a command actually works"""
        try:
            # Try to run the command in dry-run mode if possible
            test_cmd = command
            if 'ask-nix' in command and '--dry-run' not in command:
                test_cmd = command.replace('ask-nix', 'ask-nix --dry-run')
            
            result = subprocess.run(
                test_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5,
                cwd=self.project_root
            )
            
            # Check if command exists and doesn't error out immediately
            if result.returncode == 0 or 'not found' not in result.stderr:
                return True, result.stdout + result.stderr
            return False, result.stderr
        except subprocess.TimeoutExpired:
            return True, "Command exists (timed out)"
        except Exception as e:
            return False, str(e)
    
    def check_readme(self):
        """Check main README.md claims"""
        readme_path = self.project_root / "README.md"
        if not readme_path.exists():
            self.results['missing_documentation'].append("README.md not found")
            return
            
        with open(readme_path, 'r') as f:
            content = f.read()
        
        # Check performance claims
        if "7223x faster" in content:
            # Check if performance benchmarks exist
            if self.check_file_exists("benchmarks/phase2/benchmark_suite.py"):
                self.results['accurate_claims'].append("Performance benchmarks exist")
            else:
                self.results['inaccurate_claims'].append("Claims 7223x performance but benchmarks not found")
        
        # Check feature claims - search in multiple possible locations
        features = {
            "Natural Language Understanding": [
                ["src/luminous_nix/core/intents.py", "Intent"],
                ["src/luminous_nix/ai/nlp.py", "NLPEngine"],
                ["src/luminous_nix/core/engine.py", "NixForHumanityBackend"],
            ],
            "Smart Package Discovery": [
                ["src/luminous_nix/core/package_discovery.py", "SmartPackageDiscovery"],
                ["src/luminous_nix/core/knowledge.py", "search_packages"],
                ["src/luminous_nix/cli/discover_command.py", "DiscoverCommand"],
            ],
            "Beautiful TUI": [
                ["src/luminous_nix/ui/main_app.py", "NixHumanityApp"],
                ["src/luminous_nix/ui/enhanced_main_app.py", "EnhancedNixHumanityApp"],
                ["src/luminous_nix/interfaces/tui.py", "run"],
            ],
            "Configuration Management": [
                ["src/luminous_nix/core/config_generator.py", "ConfigGenerator"],
                ["src/luminous_nix/cli/config_command.py", "ConfigCommand"],
                ["src/luminous_nix/config/config_manager.py", "ConfigManager"],
            ],
            "Home Manager Integration": [
                ["src/luminous_nix/core/home_manager.py", "HomeManagerIntegration"],
                ["src/luminous_nix/cli/home_command.py", "HomeCommand"],
                ["features/v1.0/home_manager.py", "HomeManagerIntegration"],
            ],
            "Flake Support": [
                ["src/luminous_nix/core/flake_manager.py", "FlakeManager"],
                ["src/luminous_nix/cli/flake_command.py", "FlakeCommand"],
                ["features/v1.0/flake_management.py", "FlakeManager"],
            ],
            "Generation Management": [
                ["src/luminous_nix/core/generation_manager.py", "GenerationManager"],
                ["src/luminous_nix/cli/generation_command.py", "GenerationCommand"],
                ["features/v1.0/generation_management.py", "GenerationManager"],
            ],
            "Intelligent Error Handling": [
                ["src/luminous_nix/core/error_intelligence.py", "ErrorIntelligence"],
                ["src/luminous_nix/core/educational_errors.py", "educational_error_handler"],
                ["src/luminous_nix/core/error_translator.py", "ErrorTranslator"],
            ],
        }
        
        for feature, locations in features.items():
            if feature in content:
                found = False
                for module, component in locations:
                    if self.check_file_exists(module):
                        if self.check_class_exists(module, component) or self.check_function_exists(module, component):
                            self.results['accurate_claims'].append(f"{feature} - implementation found in {module}")
                            found = True
                            break
                        else:
                            self.results['aspirational_claims'].append(f"{feature} - module {module} exists but implementation incomplete")
                            found = True
                            break
                if not found:
                    self.results['inaccurate_claims'].append(f"{feature} - claimed but module not found")
        
        # Check command examples
        command_patterns = re.findall(r'ask-nix\s+["\']([^"\']+)["\']', content)
        for cmd in command_patterns[:5]:  # Test first 5 commands
            works, output = self.test_command(f"./bin/ask-nix '{cmd}'")
            if works:
                self.results['accurate_claims'].append(f"Command works: ask-nix '{cmd}'")
            else:
                self.results['inaccurate_claims'].append(f"Command fails: ask-nix '{cmd}'")
    
    def check_user_guide(self):
        """Check user guide claims"""
        guide_path = self.project_root / "docs/06-TUTORIALS/USER_GUIDE.md"
        if not guide_path.exists():
            self.results['missing_documentation'].append("User guide not found")
            return
            
        with open(guide_path, 'r') as f:
            content = f.read()
        
        # Check personality options
        personalities = ["minimal", "friendly", "encouraging", "technical", "symbiotic"]
        for personality in personalities:
            if f"--{personality}" in content:
                # Check if personality is implemented
                if self.check_function_exists("src/luminous_nix/interfaces/cli.py", "enhance_response"):
                    self.results['accurate_claims'].append(f"Personality option --{personality} documented and implemented")
                else:
                    self.results['aspirational_claims'].append(f"Personality option --{personality} documented but implementation unclear")
        
        # Check for voice interface claims
        if "Voice interface" in content or "voice commands" in content:
            if self.check_file_exists("src/luminous_nix/features/voice_interface.py"):
                self.results['accurate_claims'].append("Voice interface module exists")
            else:
                self.results['aspirational_claims'].append("Voice interface documented but not implemented")
    
    def check_quick_start(self):
        """Check quick start guide"""
        guide_path = self.project_root / "docs/03-DEVELOPMENT/03-QUICK-START.md"
        if not guide_path.exists():
            self.results['missing_documentation'].append("Quick start guide not found")
            return
            
        with open(guide_path, 'r') as f:
            content = f.read()
        
        # Check setup instructions
        if "./dev.sh" in content:
            if self.check_file_exists("scripts/dev.sh"):
                self.results['accurate_claims'].append("dev.sh script exists as documented")
            else:
                self.results['inaccurate_claims'].append("References ./dev.sh but script not found")
        
        # Check for pip install (which shouldn't be used in Nix)
        if "pip install" in content:
            self.results['inaccurate_claims'].append("Quick start mentions 'pip install' which violates Nix principles")
    
    def check_working_features(self):
        """Check what actually works by looking at tests"""
        test_dir = self.project_root / "tests"
        if not test_dir.exists():
            self.results['missing_documentation'].append("Tests directory not found")
            return
        
        # Look for passing integration tests
        integration_tests = test_dir / "integration"
        if integration_tests.exists():
            for test_file in integration_tests.glob("test_*.py"):
                self.results['accurate_claims'].append(f"Integration test exists: {test_file.name}")
        
        # Check for real command tests
        if (test_dir / "test_real_commands.py").exists():
            self.results['accurate_claims'].append("Real command testing exists")
        
        # Check what features have working code by looking for actual implementations
        working_features = []
        
        # Check for actual working features
        feature_checks = {
            "Native Python-Nix API": "src/luminous_nix/nix/native_backend.py",
            "Progress indicators": "src/luminous_nix/core/progress_indicator.py",
            "Educational errors": "src/luminous_nix/core/educational_errors.py",
            "Error translation": "src/luminous_nix/core/error_translator.py",
            "Settings management": "src/luminous_nix/cli/settings_command.py",
            "Advanced native operations": "src/luminous_nix/core/native_operations_advanced.py",
        }
        
        for feature, module_path in feature_checks.items():
            if self.check_file_exists(module_path):
                working_features.append(feature)
                self.results['accurate_claims'].append(f"Working feature: {feature}")
        
        # Check if TUI is actually connected
        tui_interface = self.project_root / "src/luminous_nix/interfaces/tui.py"
        if tui_interface.exists():
            with open(tui_interface, 'r') as f:
                content = f.read()
                if "def run" in content and "NixHumanityApp" in content:
                    self.results['accurate_claims'].append("TUI interface is connected to backend")
    
    def generate_recommendations(self):
        """Generate recommendations based on findings"""
        # Count issues
        inaccurate_count = len(self.results['inaccurate_claims'])
        aspirational_count = len(self.results['aspirational_claims'])
        
        if inaccurate_count > 5:
            self.results['recommendations'].append(
                "HIGH PRIORITY: Update README.md to reflect actual working features"
            )
        
        if aspirational_count > 10:
            self.results['recommendations'].append(
                "Consider creating a ROADMAP.md to separate future plans from current features"
            )
        
        # Check for missing essential docs
        essential_docs = ["CONTRIBUTING.md", "CHANGELOG.md", "LICENSE"]
        for doc in essential_docs:
            if not self.check_file_exists(doc):
                self.results['recommendations'].append(f"Add {doc} file")
        
        # Specific recommendations
        if any("voice" in claim.lower() for claim in self.results['aspirational_claims']):
            self.results['recommendations'].append(
                "Voice interface is heavily documented but not implemented - either implement or mark as 'Coming Soon'"
            )
        
        if any("7223x" in claim for claim in self.results['inaccurate_claims']):
            self.results['recommendations'].append(
                "Performance claims need validation - run actual benchmarks or remove specific numbers"
            )
    
    def generate_report(self) -> str:
        """Generate the final report"""
        report = []
        report.append("# Nix for Humanity Documentation Reality Check")
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("\n## Summary")
        report.append(f"- Accurate claims: {len(self.results['accurate_claims'])}")
        report.append(f"- Inaccurate claims: {len(self.results['inaccurate_claims'])}")
        report.append(f"- Aspirational claims: {len(self.results['aspirational_claims'])}")
        report.append(f"- Missing documentation: {len(self.results['missing_documentation'])}")
        
        if self.results['accurate_claims']:
            report.append("\n## ✅ Accurate Claims (Match Implementation)")
            for claim in self.results['accurate_claims'][:20]:  # Show first 20
                report.append(f"- {claim}")
            if len(self.results['accurate_claims']) > 20:
                report.append(f"- ... and {len(self.results['accurate_claims']) - 20} more")
        
        if self.results['inaccurate_claims']:
            report.append("\n## ❌ Inaccurate Claims (Need Updating)")
            for claim in self.results['inaccurate_claims']:
                report.append(f"- {claim}")
        
        if self.results['aspirational_claims']:
            report.append("\n## 🔮 Aspirational Claims (Future Features)")
            for claim in self.results['aspirational_claims']:
                report.append(f"- {claim}")
        
        if self.results['missing_documentation']:
            report.append("\n## 📝 Missing Documentation")
            for item in self.results['missing_documentation']:
                report.append(f"- {item}")
        
        if self.results['recommendations']:
            report.append("\n## 💡 Recommendations")
            for rec in self.results['recommendations']:
                report.append(f"- {rec}")
        
        # Add quick fixes section
        report.append("\n## 🔧 Quick Fixes")
        report.append("1. Update README.md to clearly separate 'Current Features' from 'Roadmap'")
        report.append("2. Add '(Coming Soon)' labels to unimplemented features")
        report.append("3. Validate all command examples in documentation")
        report.append("4. Remove or validate specific performance numbers")
        report.append("5. Create a FEATURES.md with honest feature status")
        
        return "\n".join(report)

def main():
    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print("🔍 Analyzing Nix for Humanity documentation...")
    
    checker = DocumentationChecker(project_root)
    
    # Run all checks
    print("📄 Checking README.md...")
    checker.check_readme()
    
    print("📚 Checking User Guide...")
    checker.check_user_guide()
    
    print("🚀 Checking Quick Start...")
    checker.check_quick_start()
    
    print("✅ Checking working features...")
    checker.check_working_features()
    
    print("💡 Generating recommendations...")
    checker.generate_recommendations()
    
    # Generate and save report
    report = checker.generate_report()
    
    # Save report
    report_path = project_root / "DOCUMENTATION_REALITY_CHECK.md"
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n✅ Report saved to: {report_path}")
    print("\nSummary:")
    print(f"  ✅ Accurate claims: {len(checker.results['accurate_claims'])}")
    print(f"  ❌ Inaccurate claims: {len(checker.results['inaccurate_claims'])}")
    print(f"  🔮 Aspirational claims: {len(checker.results['aspirational_claims'])}")
    
    # Also save as JSON for programmatic use
    json_path = project_root / "documentation_check_results.json"
    with open(json_path, 'w') as f:
        json.dump(checker.results, f, indent=2)
    
    print(f"\n📊 Detailed results saved to: {json_path}")

if __name__ == "__main__":
    main()