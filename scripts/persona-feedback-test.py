#!/usr/bin/env python3
"""
from typing import Dict, List
Comprehensive Persona Testing Script for Nix for Humanity

This script simulates feedback gathering from all 10 personas, testing real functionality
and generating actionable insights for system improvement.
"""

import subprocess
import json
import time
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# Ensure we can import from scripts directory
sys.path.insert(0, str(Path(__file__).parent))

try:
    from feedback_collector import FeedbackCollector
except ImportError:
    print("Warning: FeedbackCollector not available, using mock implementation")
    class FeedbackCollector:
        def __init__(self): pass
        def collect_explicit_feedback(self, **kwargs): pass

@dataclass
class Persona:
    """Represents a user persona with their specific characteristics"""
    name: str
    age: int
    description: str
    key_traits: List[str]
    test_scenarios: List[Dict[str, Any]]
    success_metrics: Dict[str, Any]
    preferred_style: str

@dataclass
class TestResult:
    """Results from testing a scenario"""
    persona: str
    scenario: str
    command: str
    success: bool
    response_time: float
    response: str
    metrics: Dict[str, Any]
    feedback: str

class PersonaFeedbackTester:
    """Tests ask-nix with all 10 personas and collects feedback"""
    
    def __init__(self):
        self.feedback_collector = FeedbackCollector()
        self.results: List[TestResult] = []
        self.ask_nix_path = self._find_ask_nix()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Define all 10 personas
        self.personas = self._define_personas()
    
    def _find_ask_nix(self) -> str:
        """Find the ask-nix executable"""
        # Try relative path first
        local_path = Path(__file__).parent.parent / "bin" / "ask-nix"
        if local_path.exists():
            return str(local_path)
        
        # Try which command
        try:
            result = subprocess.run(['which', 'ask-nix'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        
        # Default
        return "ask-nix"
    
    def _define_personas(self) -> List[Persona]:
        """Define all 10 core personas with their test scenarios"""
        return [
            Persona(
                name="Grandma Rose",
                age=75,
                description="Voice-first, zero technical terms",
                key_traits=["non-technical", "voice-preferred", "patient", "needs-clear-guidance"],
                test_scenarios=[
                    {
                        "scenario": "Install a web browser",
                        "command": "I want to look at pictures of my grandchildren on the internet",
                        "expected_behavior": "Simple, non-technical explanation"
                    },
                    {
                        "scenario": "Fix internet connection",
                        "command": "The internet stopped working",
                        "expected_behavior": "Step-by-step troubleshooting"
                    }
                ],
                success_metrics={
                    "max_technical_terms": 0,
                    "requires_voice": True,
                    "step_by_step": True,
                    "max_response_time": 3.0
                },
                preferred_style="--friendly"
            ),
            
            Persona(
                name="Maya",
                age=16,
                description="ADHD - Fast, focused, minimal distractions",
                key_traits=["adhd", "impatient", "needs-speed", "minimal-text"],
                test_scenarios=[
                    {
                        "scenario": "Quick package install",
                        "command": "firefox now",
                        "expected_behavior": "Instant action, minimal text"
                    },
                    {
                        "scenario": "System update",
                        "command": "update",
                        "expected_behavior": "Quick confirmation and progress"
                    }
                ],
                success_metrics={
                    "max_response_time": 0.5,
                    "max_word_count": 50,
                    "action_oriented": True,
                    "visual_progress": True
                },
                preferred_style="--minimal"
            ),
            
            Persona(
                name="David",
                age=42,
                description="Tired Parent - Stress-free, reliable",
                key_traits=["exhausted", "low-patience", "needs-reliability", "error-recovery"],
                test_scenarios=[
                    {
                        "scenario": "Fix broken system",
                        "command": "something broke and I don't know what",
                        "expected_behavior": "Calm reassurance and automatic fixes"
                    },
                    {
                        "scenario": "Install educational software",
                        "command": "need something for kids homework",
                        "expected_behavior": "Smart suggestions"
                    }
                ],
                success_metrics={
                    "stress_free": True,
                    "automatic_recovery": True,
                    "no_jargon": True,
                    "max_steps": 3
                },
                preferred_style="--encouraging"
            ),
            
            Persona(
                name="Dr. Sarah",
                age=35,
                description="Researcher - Efficient, precise",
                key_traits=["technical", "efficient", "precise", "power-user"],
                test_scenarios=[
                    {
                        "scenario": "Complex package management",
                        "command": "install tensorflow with cuda support",
                        "expected_behavior": "Technical details, options"
                    },
                    {
                        "scenario": "System optimization",
                        "command": "optimize build times",
                        "expected_behavior": "Advanced configuration"
                    }
                ],
                success_metrics={
                    "technical_accuracy": True,
                    "detailed_options": True,
                    "performance_metrics": True,
                    "batch_operations": True
                },
                preferred_style="--technical"
            ),
            
            Persona(
                name="Alex",
                age=28,
                description="Blind Developer - 100% accessible",
                key_traits=["blind", "screen-reader", "keyboard-only", "audio-feedback"],
                test_scenarios=[
                    {
                        "scenario": "Navigate options",
                        "command": "show me installation options for nodejs",
                        "expected_behavior": "Screen-reader friendly output"
                    },
                    {
                        "scenario": "Debug error",
                        "command": "explain this error message",
                        "expected_behavior": "Clear audio-friendly description"
                    }
                ],
                success_metrics={
                    "screen_reader_compatible": True,
                    "keyboard_navigable": True,
                    "clear_structure": True,
                    "no_visual_only": True
                },
                preferred_style="--accessible"
            ),
            
            Persona(
                name="Carlos",
                age=52,
                description="Career Switcher - Learning support",
                key_traits=["learning", "patient", "needs-context", "appreciates-education"],
                test_scenarios=[
                    {
                        "scenario": "Learn about packages",
                        "command": "what is a package manager",
                        "expected_behavior": "Educational explanation"
                    },
                    {
                        "scenario": "First installation",
                        "command": "how do I install my first program",
                        "expected_behavior": "Guided tutorial"
                    }
                ],
                success_metrics={
                    "educational": True,
                    "patient_explanations": True,
                    "learning_mode": True,
                    "progress_tracking": True
                },
                preferred_style="--encouraging"
            ),
            
            Persona(
                name="Priya",
                age=34,
                description="Single Mom - Quick, context-aware",
                key_traits=["busy", "interrupted", "needs-context", "multitasking"],
                test_scenarios=[
                    {
                        "scenario": "Quick task between interruptions",
                        "command": "install zoom for work meeting",
                        "expected_behavior": "Quick, resumable action"
                    },
                    {
                        "scenario": "Context switching",
                        "command": "what was I doing",
                        "expected_behavior": "Remember context"
                    }
                ],
                success_metrics={
                    "context_aware": True,
                    "resumable": True,
                    "quick_actions": True,
                    "interrupt_friendly": True
                },
                preferred_style="--friendly"
            ),
            
            Persona(
                name="Jamie",
                age=19,
                description="Privacy Advocate - Transparent",
                key_traits=["privacy-focused", "skeptical", "needs-transparency", "security-conscious"],
                test_scenarios=[
                    {
                        "scenario": "Privacy check",
                        "command": "what data are you collecting",
                        "expected_behavior": "Full transparency"
                    },
                    {
                        "scenario": "Secure installation",
                        "command": "install tor browser",
                        "expected_behavior": "Security information"
                    }
                ],
                success_metrics={
                    "transparent": True,
                    "privacy_respecting": True,
                    "explains_actions": True,
                    "no_hidden_data": True
                },
                preferred_style="--technical"
            ),
            
            Persona(
                name="Viktor",
                age=67,
                description="ESL - Clear communication",
                key_traits=["esl", "needs-simple-english", "patient", "visual-aids"],
                test_scenarios=[
                    {
                        "scenario": "Basic installation",
                        "command": "i want program for write document",
                        "expected_behavior": "Understand broken English"
                    },
                    {
                        "scenario": "Error help",
                        "command": "computer say error, not understand",
                        "expected_behavior": "Simple explanations"
                    }
                ],
                success_metrics={
                    "simple_language": True,
                    "understands_broken_english": True,
                    "visual_aids": True,
                    "patient": True
                },
                preferred_style="--friendly"
            ),
            
            Persona(
                name="Luna",
                age=14,
                description="Autistic - Predictable",
                key_traits=["autistic", "needs-predictability", "routine-oriented", "clear-patterns"],
                test_scenarios=[
                    {
                        "scenario": "Routine task",
                        "command": "update like always",
                        "expected_behavior": "Consistent behavior"
                    },
                    {
                        "scenario": "New installation",
                        "command": "install minecraft",
                        "expected_behavior": "Clear, predictable steps"
                    }
                ],
                success_metrics={
                    "predictable": True,
                    "consistent_ui": True,
                    "clear_patterns": True,
                    "no_surprises": True
                },
                preferred_style="--minimal"
            )
        ]
    
    def run_test_scenario(self, persona: Persona, scenario: Dict[str, Any]) -> TestResult:
        """Run a single test scenario for a persona"""
        command = scenario["command"]
        
        # Build the ask-nix command with appropriate style
        cmd_args = [self.ask_nix_path]
        if persona.preferred_style and persona.preferred_style != "--accessible":
            # Note: --accessible might not exist yet, skip if not available
            cmd_args.append(persona.preferred_style)
        cmd_args.append(command)
        
        # Time the execution
        start_time = time.time()
        
        try:
            # Run the actual command
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, "NO_FEEDBACK": "1"}  # Disable interactive feedback for testing
            )
            
            response_time = time.time() - start_time
            response = result.stdout if result.returncode == 0 else result.stderr
            success = result.returncode == 0
            
        except subprocess.TimeoutExpired:
            response_time = 10.0
            response = "Command timed out"
            success = False
        except Exception as e:
            response_time = time.time() - start_time
            response = f"Error: {str(e)}"
            success = False
        
        # Evaluate against persona success metrics
        metrics = self._evaluate_response(persona, scenario, response, response_time)
        
        # Generate feedback
        feedback = self._generate_feedback(persona, scenario, response, metrics)
        
        return TestResult(
            persona=persona.name,
            scenario=scenario["scenario"],
            command=command,
            success=success,
            response_time=response_time,
            response=response,
            metrics=metrics,
            feedback=feedback
        )
    
    def _evaluate_response(self, persona: Persona, scenario: Dict[str, Any], 
                          response: str, response_time: float) -> Dict[str, Any]:
        """Evaluate response against persona success metrics"""
        metrics = {}
        
        # Response time check
        if "max_response_time" in persona.success_metrics:
            metrics["response_time_ok"] = response_time <= persona.success_metrics["max_response_time"]
        
        # Word count check  
        if "max_word_count" in persona.success_metrics:
            word_count = len(response.split())
            metrics["word_count"] = word_count
            metrics["word_count_ok"] = word_count <= persona.success_metrics["max_word_count"]
        
        # Technical terms check
        if "max_technical_terms" in persona.success_metrics:
            technical_terms = ["nixos", "package", "configuration", "flake", "derivation", 
                             "systemd", "profile", "generation", "channel", "nix-env"]
            term_count = sum(1 for term in technical_terms if term.lower() in response.lower())
            metrics["technical_terms"] = term_count
            metrics["technical_terms_ok"] = term_count <= persona.success_metrics["max_technical_terms"]
        
        # Simple language check (for Viktor)
        if "simple_language" in persona.success_metrics:
            complex_words = len([w for w in response.split() if len(w) > 10])
            metrics["simple_language_ok"] = complex_words < 5
        
        # Screen reader compatibility (basic check)
        if "screen_reader_compatible" in persona.success_metrics:
            # Check for good structure markers
            has_headers = any(marker in response for marker in ["#", "**", "Step", "Option"])
            no_ascii_art = not any(char in response for char in ["╔", "║", "╗", "╚", "═", "╝"])
            metrics["screen_reader_ok"] = has_headers and no_ascii_art
        
        # Action-oriented check (for Maya)
        if "action_oriented" in persona.success_metrics:
            action_words = ["run", "type", "execute", "install", "quick", "now", "done"]
            has_actions = any(word in response.lower() for word in action_words)
            metrics["action_oriented_ok"] = has_actions
        
        return metrics
    
    def _generate_feedback(self, persona: Persona, scenario: Dict[str, Any],
                          response: str, metrics: Dict[str, Any]) -> str:
        """Generate persona-specific feedback"""
        feedback_parts = []
        
        # Check if response meets persona needs
        all_metrics_ok = all(v for k, v in metrics.items() if k.endswith("_ok"))
        
        if all_metrics_ok:
            feedback_parts.append(f"✅ Response meets {persona.name}'s needs well")
        else:
            feedback_parts.append(f"❌ Response could be improved for {persona.name}")
        
        # Specific feedback based on failed metrics
        if metrics.get("response_time_ok") is False:
            feedback_parts.append(f"- Response too slow ({metrics.get('response_time', 0):.1f}s)")
        
        if metrics.get("word_count_ok") is False:
            feedback_parts.append(f"- Too verbose ({metrics.get('word_count', 0)} words)")
        
        if metrics.get("technical_terms_ok") is False:
            feedback_parts.append(f"- Too technical ({metrics.get('technical_terms', 0)} technical terms)")
        
        if metrics.get("simple_language_ok") is False:
            feedback_parts.append("- Language too complex for ESL user")
        
        if metrics.get("screen_reader_ok") is False:
            feedback_parts.append("- Not optimized for screen readers")
        
        if metrics.get("action_oriented_ok") is False:
            feedback_parts.append("- Needs more action-oriented language")
        
        # Add scenario-specific observations
        if len(response) < 50:
            feedback_parts.append("- Response might be too terse")
        elif len(response) > 1000:
            feedback_parts.append("- Response might be overwhelming")
        
        return "\n".join(feedback_parts)
    
    def test_all_personas(self):
        """Run tests for all personas"""
        print("🎭 Nix for Humanity - Comprehensive Persona Testing")
        print("=" * 60)
        print(f"Session ID: {self.session_id}")
        print(f"Testing with: {self.ask_nix_path}")
        print("=" * 60)
        
        for persona in self.personas:
            print(f"\n👤 Testing {persona.name} ({persona.age}, {persona.description})")
            print("-" * 40)
            
            for scenario in persona.test_scenarios:
                print(f"\n📝 Scenario: {scenario['scenario']}")
                print(f"💬 Command: {scenario['command']}")
                
                # Run the test
                result = self.run_test_scenario(persona, scenario)
                self.results.append(result)
                
                # Display results
                print(f"⏱️  Response Time: {result.response_time:.2f}s")
                print(f"✓  Success: {result.success}")
                print(f"\n📊 Metrics:")
                for metric, value in result.metrics.items():
                    if not metric.endswith("_ok"):
                        status = "✅" if result.metrics.get(f"{metric}_ok", True) else "❌"
                        print(f"   {status} {metric}: {value}")
                
                print(f"\n💭 Feedback:\n{result.feedback}")
                
                # Show truncated response
                if len(result.response) > 200:
                    print(f"\n📄 Response (truncated):\n{result.response[:200]}...")
                else:
                    print(f"\n📄 Response:\n{result.response}")
                
                # Small delay between tests
                time.sleep(0.5)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive feedback report"""
        report = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.results),
            "personas_tested": len(self.personas),
            "overall_success_rate": sum(1 for r in self.results if r.success) / len(self.results) if self.results else 0,
            "persona_results": {},
            "key_insights": [],
            "actionable_improvements": []
        }
        
        # Analyze per-persona results
        for persona in self.personas:
            persona_results = [r for r in self.results if r.persona == persona.name]
            if persona_results:
                success_rate = sum(1 for r in persona_results if r.success) / len(persona_results)
                avg_response_time = sum(r.response_time for r in persona_results) / len(persona_results)
                
                # Check if persona needs are met
                all_metrics = {}
                for result in persona_results:
                    for metric, value in result.metrics.items():
                        if metric.endswith("_ok"):
                            if metric not in all_metrics:
                                all_metrics[metric] = []
                            all_metrics[metric].append(value)
                
                needs_met_rate = sum(sum(values) / len(values) for values in all_metrics.values()) / len(all_metrics) if all_metrics else 0
                
                report["persona_results"][persona.name] = {
                    "success_rate": success_rate,
                    "avg_response_time": avg_response_time,
                    "needs_met_rate": needs_met_rate,
                    "key_issues": [r.feedback for r in persona_results if not r.success]
                }
        
        # Generate key insights
        self._generate_insights(report)
        
        # Generate actionable improvements
        self._generate_improvements(report)
        
        return report
    
    def _generate_insights(self, report: Dict[str, Any]):
        """Generate key insights from test results"""
        insights = []
        
        # Overall performance
        if report["overall_success_rate"] < 0.8:
            insights.append("⚠️ Overall success rate below 80% - system needs reliability improvements")
        
        # Persona-specific insights
        for persona_name, results in report["persona_results"].items():
            if results["success_rate"] < 0.5:
                insights.append(f"🚨 {persona_name}: Critical issues - only {results['success_rate']:.0%} success rate")
            elif results["needs_met_rate"] < 0.7:
                insights.append(f"⚠️ {persona_name}: Needs not fully met ({results['needs_met_rate']:.0%})")
            
            if results["avg_response_time"] > 3.0:
                insights.append(f"🐌 {persona_name}: Slow responses ({results['avg_response_time']:.1f}s average)")
        
        # Cross-persona patterns
        technical_personas = ["Dr. Sarah", "Alex", "Jamie"]
        non_technical_personas = ["Grandma Rose", "Viktor", "Luna"]
        
        tech_success = sum(report["persona_results"].get(p, {}).get("success_rate", 0) for p in technical_personas) / len(technical_personas)
        non_tech_success = sum(report["persona_results"].get(p, {}).get("success_rate", 0) for p in non_technical_personas) / len(non_technical_personas)
        
        if tech_success > non_tech_success + 0.2:
            insights.append("📊 System performs better for technical users - needs accessibility improvements")
        elif non_tech_success > tech_success + 0.2:
            insights.append("📊 System performs better for non-technical users - needs power user features")
        
        report["key_insights"] = insights
    
    def _generate_improvements(self, report: Dict[str, Any]):
        """Generate actionable improvement recommendations"""
        improvements = []
        
        # Based on common failures
        response_time_issues = sum(1 for r in self.results if r.metrics.get("response_time_ok") is False)
        if response_time_issues > len(self.results) * 0.2:
            improvements.append({
                "priority": "HIGH",
                "area": "Performance",
                "action": "Optimize response generation - consider caching common queries",
                "affects": ["Maya (ADHD)", "Priya (Single Mom)"]
            })
        
        technical_term_issues = sum(1 for r in self.results if r.metrics.get("technical_terms_ok") is False)
        if technical_term_issues > len(self.results) * 0.3:
            improvements.append({
                "priority": "HIGH", 
                "area": "Language Simplification",
                "action": "Implement automatic technical term translation for non-technical personas",
                "affects": ["Grandma Rose", "Viktor (ESL)", "David (Tired Parent)"]
            })
        
        # Screen reader issues
        screen_reader_issues = sum(1 for r in self.results if r.metrics.get("screen_reader_ok") is False)
        if screen_reader_issues > 0:
            improvements.append({
                "priority": "CRITICAL",
                "area": "Accessibility",
                "action": "Ensure all output is screen-reader compatible - remove ASCII art, add structure",
                "affects": ["Alex (Blind Developer)"]
            })
        
        # Based on persona-specific needs
        for persona_name, results in report["persona_results"].items():
            if results["needs_met_rate"] < 0.5:
                if persona_name == "Grandma Rose":
                    improvements.append({
                        "priority": "HIGH",
                        "area": "Voice Interface",
                        "action": "Prioritize voice interface development for non-technical users",
                        "affects": [persona_name]
                    })
                elif persona_name == "Maya":
                    improvements.append({
                        "priority": "MEDIUM",
                        "area": "Speed Optimization",
                        "action": "Implement instant response mode with progressive updates",
                        "affects": [persona_name]
                    })
                elif persona_name == "Carlos":
                    improvements.append({
                        "priority": "MEDIUM",
                        "area": "Learning Mode",
                        "action": "Enhance learning mode with interactive tutorials",
                        "affects": [persona_name]
                    })
        
        report["actionable_improvements"] = improvements
    
    def save_report(self, report: Dict[str, Any]):
        """Save report to file"""
        report_dir = Path(__file__).parent.parent / "test-results" / "persona-feedback"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"persona-feedback-{self.session_id}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Also save human-readable summary
        summary_file = report_dir / f"persona-feedback-{self.session_id}.md"
        with open(summary_file, 'w') as f:
            f.write(self._format_report_markdown(report))
        
        print(f"\n📁 Reports saved to:")
        print(f"   JSON: {report_file}")
        print(f"   Markdown: {summary_file}")
    
    def _format_report_markdown(self, report: Dict[str, Any]) -> str:
        """Format report as readable markdown"""
        md = f"""# Nix for Humanity - Persona Feedback Report

**Session ID:** {report['session_id']}  
**Timestamp:** {report['timestamp']}  
**Total Tests:** {report['total_tests']}  
**Overall Success Rate:** {report['overall_success_rate']:.1%}

## Executive Summary

### Key Insights
"""
        for insight in report['key_insights']:
            md += f"- {insight}\n"
        
        md += "\n### Actionable Improvements\n"
        for improvement in report['actionable_improvements']:
            md += f"\n#### {improvement['priority']} Priority: {improvement['area']}\n"
            md += f"**Action:** {improvement['action']}\n"
            md += f"**Affects:** {', '.join(improvement['affects'])}\n"
        
        md += "\n## Persona-by-Persona Results\n"
        for persona_name, results in report['persona_results'].items():
            md += f"\n### {persona_name}\n"
            md += f"- **Success Rate:** {results['success_rate']:.1%}\n"
            md += f"- **Avg Response Time:** {results['avg_response_time']:.2f}s\n"
            md += f"- **Needs Met:** {results['needs_met_rate']:.1%}\n"
            
            if results['key_issues']:
                md += f"- **Issues:**\n"
                for issue in results['key_issues']:
                    md += f"  - {issue}\n"
        
        md += "\n## Detailed Test Results\n"
        for result in self.results:
            md += f"\n### {result.persona} - {result.scenario}\n"
            md += f"**Command:** `{result.command}`\n"
            md += f"**Success:** {'✅' if result.success else '❌'}\n"
            md += f"**Response Time:** {result.response_time:.2f}s\n"
            md += f"**Feedback:**\n{result.feedback}\n"
        
        return md


def main():
    """Run the persona feedback testing"""
    tester = PersonaFeedbackTester()
    
    print("🚀 Starting Nix for Humanity Persona Testing")
    print("This will test real functionality with all 10 personas\n")
    
    # Check if ask-nix exists
    if not Path(tester.ask_nix_path).exists() and not subprocess.run(['which', tester.ask_nix_path], capture_output=True).returncode == 0:
        print(f"❌ Error: ask-nix not found at {tester.ask_nix_path}")
        print("Please ensure ask-nix is installed and in your PATH")
        return 1
    
    try:
        # Run all tests
        tester.test_all_personas()
        
        # Generate report
        print("\n" + "=" * 60)
        print("📊 Generating Comprehensive Report...")
        report = tester.generate_report()
        
        # Display summary
        print(f"\n🎯 Overall Success Rate: {report['overall_success_rate']:.1%}")
        print(f"\n🔍 Key Insights:")
        for insight in report['key_insights'][:5]:  # Top 5 insights
            print(f"   {insight}")
        
        print(f"\n🔧 Top Improvements Needed:")
        for improvement in report['actionable_improvements'][:3]:  # Top 3 improvements
            print(f"   [{improvement['priority']}] {improvement['area']}: {improvement['action']}")
        
        # Save report
        tester.save_report(report)
        
        print("\n✅ Testing complete! Check the reports for detailed analysis.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())