#!/usr/bin/env python3
"""
from typing import Tuple, List
Persona-based testing for ask-nix
Tests the 10 core personas with realistic scenarios
"""

import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

class PersonaTest:
    def __init__(self, name: str, age: int, description: str, needs: List[str], test_scenarios: List[Dict]):
        self.name = name
        self.age = age
        self.description = description
        self.needs = needs
        self.test_scenarios = test_scenarios
        self.results = []
        
    def run_command(self, command: str, dry_run: bool = True) -> Tuple[bool, str, float]:
        """Run ask-nix command and measure success"""
        start_time = time.time()
        
        cmd = ["/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/bin/ask-nix"]
        if dry_run:
            cmd.append("--dry-run")
        cmd.append(command)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            elapsed = time.time() - start_time
            success = result.returncode == 0
            output = result.stdout + result.stderr
            return success, output, elapsed
        except subprocess.TimeoutExpired:
            return False, "Command timed out", 30.0
        except Exception as e:
            return False, str(e), 0.0
    
    def test_scenario(self, scenario: Dict) -> Dict:
        """Test a single scenario"""
        print(f"\n  Testing: {scenario['description']}")
        print(f"  Command: {scenario['command']}")
        
        success, output, elapsed = self.run_command(scenario['command'])
        
        # Evaluate based on persona needs
        evaluation = self.evaluate_response(output, scenario, elapsed)
        
        result = {
            'scenario': scenario['description'],
            'command': scenario['command'],
            'success': success,
            'elapsed_time': elapsed,
            'evaluation': evaluation,
            'output_snippet': output[:200] + '...' if len(output) > 200 else output
        }
        
        # Print result
        status = "✅" if evaluation['passed'] else "❌"
        print(f"  {status} Result: {evaluation['summary']}")
        print(f"  ⏱️  Time: {elapsed:.2f}s")
        
        return result
    
    def evaluate_response(self, output: str, scenario: Dict, elapsed: float) -> Dict:
        """Evaluate response based on persona needs"""
        evaluation = {
            'passed': True,
            'issues': [],
            'strengths': [],
            'summary': ''
        }
        
        # Universal checks
        if elapsed > scenario.get('max_time', 5.0):
            evaluation['passed'] = False
            evaluation['issues'].append(f"Too slow ({elapsed:.1f}s)")
        
        # Persona-specific checks
        if self.name == "Grandma Rose":
            # Check for technical jargon
            jargon = ['nixpkgs', 'flake', 'derivation', 'profile', 'sudo']
            found_jargon = [word for word in jargon if word.lower() in output.lower()]
            if found_jargon:
                evaluation['issues'].append(f"Technical terms: {', '.join(found_jargon)}")
                evaluation['passed'] = False
            
            # Check for voice-friendly output
            if len(output.split('\n')) > 10:
                evaluation['issues'].append("Too much text for voice reading")
            else:
                evaluation['strengths'].append("Concise for voice")
                
        elif self.name == "Maya":
            # Fast and focused
            if elapsed > 2.0:
                evaluation['issues'].append("Too slow for ADHD needs")
                evaluation['passed'] = False
            
            # Minimal distractions
            if output.count('💡') > 2 or output.count('✨') > 2:
                evaluation['issues'].append("Too many emoji distractions")
                
        elif self.name == "David":
            # Stress-free, reliable
            if "error" in output.lower() or "failed" in output.lower():
                if "💡" not in output:
                    evaluation['issues'].append("Error without helpful suggestion")
                    evaluation['passed'] = False
                else:
                    evaluation['strengths'].append("Error includes help")
                    
        elif self.name == "Dr. Sarah":
            # Efficient, precise
            if scenario.get('expects_execution') and '--dry-run' in output:
                evaluation['strengths'].append("Clear about dry-run mode")
            
            # Should provide exact commands
            if "```" not in output and scenario.get('expects_command'):
                evaluation['issues'].append("No clear command provided")
                
        elif self.name == "Alex":
            # Accessible
            # Check for screen reader friendly output
            if "🔍" in output or "📦" in output:
                evaluation['issues'].append("Emojis may confuse screen readers")
            
            # Clear structure
            if output.count('\n\n') < 2:
                evaluation['issues'].append("Lacks paragraph breaks for screen reader")
                
        elif self.name == "Carlos":
            # Learning support
            if "example" not in output.lower() and scenario.get('needs_example'):
                evaluation['issues'].append("No example provided")
                evaluation['passed'] = False
            else:
                evaluation['strengths'].append("Includes examples")
                
        elif self.name == "Priya":
            # Quick, context-aware
            if elapsed > 3.0:
                evaluation['issues'].append("Too slow for busy parent")
            
            # Interruptible
            if len(output) > 500:
                evaluation['issues'].append("Too long to read quickly")
                
        elif self.name == "Jamie":
            # Privacy transparent
            if "local" in output.lower() or "privacy" in output.lower():
                evaluation['strengths'].append("Mentions privacy")
            elif scenario.get('privacy_sensitive'):
                evaluation['issues'].append("No privacy information")
                
        elif self.name == "Viktor":
            # Clear communication
            complex_words = ['declarative', 'imperative', 'instantiate']
            found_complex = [word for word in complex_words if word.lower() in output.lower()]
            if found_complex:
                evaluation['issues'].append(f"Complex English: {', '.join(found_complex)}")
                
        elif self.name == "Luna":
            # Predictable
            if output.count('!') > 3:
                evaluation['issues'].append("Too many exclamations (overwhelming)")
            
            # Consistent format
            if "1." in output and "2." in output:
                evaluation['strengths'].append("Numbered list (predictable)")
        
        # Generate summary
        if evaluation['passed']:
            evaluation['summary'] = f"Passed - {', '.join(evaluation['strengths'][:2])}"
        else:
            evaluation['summary'] = f"Failed - {', '.join(evaluation['issues'][:2])}"
            
        return evaluation
    
    def run_tests(self) -> List[Dict]:
        """Run all test scenarios for this persona"""
        print(f"\n{'='*60}")
        print(f"Testing Persona: {self.name} ({self.age})")
        print(f"Description: {self.description}")
        print(f"Key Needs: {', '.join(self.needs)}")
        print(f"{'='*60}")
        
        for scenario in self.test_scenarios:
            result = self.test_scenario(scenario)
            self.results.append(result)
            time.sleep(0.5)  # Brief pause between tests
            
        return self.results


# Define the 10 personas with test scenarios
PERSONAS = [
    PersonaTest(
        name="Grandma Rose",
        age=75,
        description="Voice-first, zero technical terms",
        needs=["Accessibility", "Simple language", "Voice-friendly"],
        test_scenarios=[
            {
                'description': "Install a web browser",
                'command': "install firefox",
                'max_time': 5.0,
                'expects_command': True
            },
            {
                'description': "Check for updates",
                'command': "update my computer",
                'max_time': 5.0
            },
            {
                'description': "Remove a program",
                'command': "uninstall zoom",
                'max_time': 5.0
            }
        ]
    ),
    
    PersonaTest(
        name="Maya", 
        age=16,
        description="ADHD - Fast, focused, minimal distractions",
        needs=["Speed", "Focus", "Minimal UI"],
        test_scenarios=[
            {
                'description': "Quick install",
                'command': "install discord",
                'max_time': 2.0,
                'expects_command': True
            },
            {
                'description': "Fast search",
                'command': "find games",
                'max_time': 2.0
            },
            {
                'description': "Instant action",
                'command': "install spotify now",
                'max_time': 2.0
            }
        ]
    ),
    
    PersonaTest(
        name="David",
        age=42,
        description="Tired Parent - Stress-free, reliable",
        needs=["Error handling", "Reliability", "Clear guidance"],
        test_scenarios=[
            {
                'description': "Install kids software",
                'command': "install minecraft",
                'max_time': 5.0,
                'expects_command': True
            },
            {
                'description': "Fix broken package",
                'command': "firefox not working",
                'max_time': 5.0
            },
            {
                'description': "Safe system update",
                'command': "update everything safely",
                'max_time': 5.0
            }
        ]
    ),
    
    PersonaTest(
        name="Dr. Sarah",
        age=35,
        description="Researcher - Efficient, precise",
        needs=["Power features", "Precision", "Efficiency"],
        test_scenarios=[
            {
                'description': "Install research tools",
                'command': "install jupyter",
                'max_time': 3.0,
                'expects_command': True,
                'expects_execution': True
            },
            {
                'description': "Batch operations",
                'command': "install python pandas numpy matplotlib",
                'max_time': 3.0
            },
            {
                'description': "System optimization",
                'command': "optimize nix store",
                'max_time': 3.0
            }
        ]
    ),
    
    PersonaTest(
        name="Alex",
        age=28,
        description="Blind Developer - 100% accessible",
        needs=["Screen readers", "Keyboard navigation", "Clear structure"],
        test_scenarios=[
            {
                'description': "Install dev tools",
                'command': "install neovim",
                'max_time': 5.0,
                'expects_command': True
            },
            {
                'description': "List installed",
                'command': "what do I have installed",
                'max_time': 5.0
            },
            {
                'description': "Navigate options",
                'command': "install git with options",
                'max_time': 5.0
            }
        ]
    ),
    
    PersonaTest(
        name="Carlos",
        age=52,
        description="Career Switcher - Learning support",
        needs=["Onboarding", "Examples", "Education"],
        test_scenarios=[
            {
                'description': "Learn basics",
                'command': "what is nix",
                'max_time': 5.0,
                'needs_example': True
            },
            {
                'description': "First install",
                'command': "how do I install vscode",
                'max_time': 5.0,
                'needs_example': True
            },
            {
                'description': "Understand errors",
                'command': "what does collision mean",
                'max_time': 5.0
            }
        ]
    ),
    
    PersonaTest(
        name="Priya",
        age=34,
        description="Single Mom - Quick, context-aware",
        needs=["Interruptions", "Quick tasks", "Context switching"],
        test_scenarios=[
            {
                'description': "Quick software install",
                'command': "install zoom",
                'max_time': 3.0,
                'expects_command': True
            },
            {
                'description': "Resume task",
                'command': "continue update",
                'max_time': 3.0
            },
            {
                'description': "Quick check",
                'command': "is firefox installed",
                'max_time': 2.0
            }
        ]
    ),
    
    PersonaTest(
        name="Jamie",
        age=19,
        description="Privacy Advocate - Transparent",
        needs=["Privacy", "Transparency", "Control"],
        test_scenarios=[
            {
                'description': "Privacy-focused browser",
                'command': "install tor browser",
                'max_time': 5.0,
                'privacy_sensitive': True
            },
            {
                'description': "Check data collection",
                'command': "what data do you collect",
                'max_time': 3.0,
                'privacy_sensitive': True
            },
            {
                'description': "Secure communication",
                'command': "install signal",
                'max_time': 5.0
            }
        ]
    ),
    
    PersonaTest(
        name="Viktor",
        age=67,
        description="ESL - Clear communication",
        needs=["Language clarity", "Simple English", "Examples"],
        test_scenarios=[
            {
                'description': "Install browser",
                'command': "I want internet",
                'max_time': 5.0
            },
            {
                'description': "Update computer",
                'command': "make computer new",
                'max_time': 5.0
            },
            {
                'description': "Find program",
                'command': "where is firefox",
                'max_time': 5.0
            }
        ]
    ),
    
    PersonaTest(
        name="Luna",
        age=14,
        description="Autistic - Predictable",
        needs=["Consistency", "Predictability", "Clear patterns"],
        test_scenarios=[
            {
                'description': "Consistent install",
                'command': "install steam",
                'max_time': 5.0,
                'expects_command': True
            },
            {
                'description': "Same command again",
                'command': "install steam",
                'max_time': 5.0
            },
            {
                'description': "Predictable list",
                'command': "list all browsers",
                'max_time': 5.0
            }
        ]
    )
]


def run_all_tests():
    """Run tests for all personas"""
    print("🧪 Persona-Based Testing for ask-nix")
    print("=" * 80)
    
    all_results = {}
    summary = {
        'total_tests': 0,
        'passed': 0,
        'failed': 0,
        'personas_passed': [],
        'personas_failed': [],
        'common_issues': {},
        'common_strengths': {}
    }
    
    for persona in PERSONAS:
        results = persona.run_tests()
        all_results[persona.name] = results
        
        # Update summary
        persona_passed = all([r['evaluation']['passed'] for r in results])
        summary['total_tests'] += len(results)
        summary['passed'] += sum(1 for r in results if r['evaluation']['passed'])
        summary['failed'] += sum(1 for r in results if not r['evaluation']['passed'])
        
        if persona_passed:
            summary['personas_passed'].append(persona.name)
        else:
            summary['personas_failed'].append(persona.name)
            
        # Collect common issues/strengths
        for result in results:
            for issue in result['evaluation']['issues']:
                summary['common_issues'][issue] = summary['common_issues'].get(issue, 0) + 1
            for strength in result['evaluation']['strengths']:
                summary['common_strengths'][strength] = summary['common_strengths'].get(strength, 0) + 1
    
    # Print summary
    print(f"\n{'='*80}")
    print("📊 TESTING SUMMARY")
    print(f"{'='*80}")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']} ({summary['passed']/summary['total_tests']*100:.1f}%)")
    print(f"Failed: {summary['failed']} ({summary['failed']/summary['total_tests']*100:.1f}%)")
    
    print(f"\n✅ Personas Fully Passing ({len(summary['personas_passed'])}):")
    for p in summary['personas_passed']:
        print(f"  - {p}")
        
    print(f"\n❌ Personas With Failures ({len(summary['personas_failed'])}):")
    for p in summary['personas_failed']:
        print(f"  - {p}")
        
    print("\n🔴 Most Common Issues:")
    for issue, count in sorted(summary['common_issues'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {issue} ({count} occurrences)")
        
    print("\n🟢 Most Common Strengths:")
    for strength, count in sorted(summary['common_strengths'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {strength} ({count} occurrences)")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"persona_test_results_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'summary': summary,
            'detailed_results': all_results
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    return summary, all_results


if __name__ == "__main__":
    summary, results = run_all_tests()