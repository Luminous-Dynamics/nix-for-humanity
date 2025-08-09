#!/usr/bin/env python3
"""
from typing import List
Test Harness: Validate Legacy vs Headless Engine Compatibility
Ensures both engines produce equivalent results for the same queries
"""

import os
import sys
import json
import difflib
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime

# Add scripts directory to path
script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))
sys.path.insert(0, script_dir)

@dataclass
class TestResult:
    """Result of a single compatibility test"""
    query: str
    passed: bool
    legacy_response: Dict
    headless_response: Dict
    differences: List[str]
    execution_time_legacy: float
    execution_time_headless: float

class EngineCompatibilityTester:
    """Test harness to ensure both engines produce compatible results"""
    
    def __init__(self):
        self.test_queries = [
            # Basic queries
            "install firefox",
            "how do I update my system?",
            "my wifi stopped working",
            "what's a generation?",
            "rollback to previous configuration",
            
            # Complex queries
            "install firefox and vscode then update system",
            "help me set up a development environment with python and nodejs",
            "I'm getting an error: attribute 'firefox' missing",
            
            # Edge cases
            "plz can u get me the fierfox broswer",  # Typos
            "INSTALL FIREFOX!!!",  # Caps and punctuation
            "firefox install how",  # Word order
            "",  # Empty query
            "help",  # Single word
        ]
        
        self.results: List[TestResult] = []
    
    def run_tests(self) -> None:
        """Run compatibility tests on all queries"""
        print("🧪 Engine Compatibility Test Suite")
        print("=" * 70)
        
        # Initialize both engines
        legacy_engine = self._create_legacy_engine()
        headless_engine = self._create_headless_engine()
        
        if not headless_engine:
            print("❌ Headless engine not available. Cannot run compatibility tests.")
            return
        
        # Test each query
        for i, query in enumerate(self.test_queries, 1):
            print(f"\nTest {i}/{len(self.test_queries)}: '{query[:50]}...'")
            result = self._test_query(query, legacy_engine, headless_engine)
            self.results.append(result)
            
            if result.passed:
                print(f"✅ PASSED ({result.execution_time_legacy:.3f}s vs {result.execution_time_headless:.3f}s)")
            else:
                print(f"❌ FAILED - {len(result.differences)} differences found")
    
    def _create_legacy_engine(self):
        """Create legacy engine instance"""
        from nix_knowledge_engine import NixOSKnowledgeEngine
        return NixOSKnowledgeEngine()
    
    def _create_headless_engine(self):
        """Create headless engine instance"""
        try:
            from core.headless_engine import HeadlessEngine, Context
            from adapters.cli_adapter import CLIAdapter
            return CLIAdapter(use_server=False)
        except ImportError:
            return None
    
    def _test_query(self, query: str, legacy_engine, headless_engine) -> TestResult:
        """Test a single query on both engines"""
        import time
        
        # Test legacy engine
        start = time.time()
        legacy_response = self._process_legacy(query, legacy_engine)
        legacy_time = time.time() - start
        
        # Test headless engine
        start = time.time()
        headless_response = self._process_headless(query, headless_engine)
        headless_time = time.time() - start
        
        # Compare results
        differences = self._compare_responses(legacy_response, headless_response)
        
        return TestResult(
            query=query,
            passed=len(differences) == 0,
            legacy_response=legacy_response,
            headless_response=headless_response,
            differences=differences,
            execution_time_legacy=legacy_time,
            execution_time_headless=headless_time
        )
    
    def _process_legacy(self, query: str, engine) -> Dict:
        """Process query with legacy engine"""
        try:
            intent = engine.extract_intent(query)
            solution = engine.get_solution(intent)
            response_text = engine.format_response(intent, solution)
            
            return {
                'success': True,
                'intent_action': intent.get('action', 'unknown'),
                'intent_package': intent.get('package'),
                'solution_found': solution.get('found', False),
                'response_length': len(response_text),
                'response_preview': response_text[:100],
                'has_methods': bool(solution.get('methods')),
                'method_count': len(solution.get('methods', []))
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _process_headless(self, query: str, adapter) -> Dict:
        """Process query with headless engine"""
        try:
            from core.headless_engine import Context
            
            context = Context(
                personality='friendly',
                collect_feedback=False
            )
            
            response = adapter.process_query(query, context)
            
            return {
                'success': True,
                'intent_action': response.get('intent', {}).get('action', 'unknown'),
                'intent_package': response.get('intent', {}).get('package'),
                'solution_found': response.get('confidence', 0) > 0.5,
                'response_length': len(response.get('text', '')),
                'response_preview': response.get('text', '')[:100],
                'has_methods': bool(response.get('commands')),
                'method_count': len(response.get('commands', []))
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _compare_responses(self, legacy: Dict, headless: Dict) -> List[str]:
        """Compare two responses and return differences"""
        differences = []
        
        # Key compatibility checks
        checks = [
            ('success', lambda l, h: l['success'] == h['success']),
            ('intent_action', lambda l, h: l.get('intent_action') == h.get('intent_action')),
            ('solution_found', lambda l, h: l.get('solution_found') == h.get('solution_found')),
            ('has_methods', lambda l, h: l.get('has_methods') == h.get('has_methods')),
        ]
        
        for check_name, check_func in checks:
            try:
                if not check_func(legacy, headless):
                    differences.append(
                        f"{check_name}: legacy={legacy.get(check_name)} vs headless={headless.get(check_name)}"
                    )
            except Exception as e:
                differences.append(f"{check_name}: comparison error: {e}")
        
        # Allow some variation in response length (±20%)
        if legacy.get('response_length', 0) > 0:
            ratio = headless.get('response_length', 0) / legacy.get('response_length', 1)
            if ratio < 0.8 or ratio > 1.2:
                differences.append(
                    f"response_length: significant difference ({legacy.get('response_length')} vs {headless.get('response_length')})"
                )
        
        return differences
    
    def generate_report(self) -> None:
        """Generate compatibility test report"""
        if not self.results:
            print("\n❌ No test results to report")
            return
        
        print("\n" + "=" * 70)
        print("📊 COMPATIBILITY TEST REPORT")
        print("=" * 70)
        
        # Summary stats
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        
        print(f"\nSummary:")
        print(f"  Total Tests: {total}")
        print(f"  Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"  Failed: {failed} ({failed/total*100:.1f}%)")
        
        # Performance comparison
        avg_legacy_time = sum(r.execution_time_legacy for r in self.results) / total
        avg_headless_time = sum(r.execution_time_headless for r in self.results) / total
        
        print(f"\nPerformance:")
        print(f"  Avg Legacy Time: {avg_legacy_time:.3f}s")
        print(f"  Avg Headless Time: {avg_headless_time:.3f}s")
        print(f"  Speedup: {avg_legacy_time/avg_headless_time:.2f}x")
        
        # Failed tests details
        if failed > 0:
            print(f"\n❌ Failed Tests:")
            for r in self.results:
                if not r.passed:
                    print(f"\n  Query: '{r.query}'")
                    for diff in r.differences:
                        print(f"    - {diff}")
        
        # Save detailed report
        self._save_detailed_report()
    
    def _save_detailed_report(self):
        """Save detailed report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"/tmp/nix_engine_compatibility_report_{timestamp}.json"
        
        report_data = {
            'timestamp': timestamp,
            'summary': {
                'total_tests': len(self.results),
                'passed': sum(1 for r in self.results if r.passed),
                'failed': sum(1 for r in self.results if not r.passed)
            },
            'results': [
                {
                    'query': r.query,
                    'passed': r.passed,
                    'differences': r.differences,
                    'execution_times': {
                        'legacy': r.execution_time_legacy,
                        'headless': r.execution_time_headless
                    },
                    'responses': {
                        'legacy': r.legacy_response,
                        'headless': r.headless_response
                    }
                }
                for r in self.results
            ]
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")


def main():
    """Run compatibility tests"""
    tester = EngineCompatibilityTester()
    
    # Run tests
    tester.run_tests()
    
    # Generate report
    tester.generate_report()
    
    # Return exit code based on results
    if tester.results:
        failed_count = sum(1 for r in tester.results if not r.passed)
        sys.exit(failed_count)  # 0 if all passed


if __name__ == "__main__":
    main()