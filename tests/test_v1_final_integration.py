#!/usr/bin/env python3
"""
Final Integration Test for Nix for Humanity v1.0

Validates all 10 core features work together seamlessly:
1. Natural Language Understanding
2. Smart Package Discovery
3. Native Python-Nix API
4. Beautiful TUI
5. Configuration Management
6. Home Manager Integration
7. Flake Support
8. Generation Management
9. Intelligent Error Handling
10. Settings & Profiles
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

# Import v1.0 components
from nix_humanity.core import NixForHumanityBackend
from nix_humanity.api import Request, Response

class V1IntegrationTest:
    """Complete integration test for v1.0"""
    
    def __init__(self):
        self.backend = NixForHumanityBackend()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "features": {},
            "performance": {},
            "overall_success": True
        }
    
    def test_feature_1_natural_language(self):
        """Test natural language understanding across various inputs"""
        print("\n🧪 Feature 1: Natural Language Understanding")
        print("-" * 50)
        
        test_queries = [
            ("install firefox please", "Polite request"),
            ("how do I update my system?", "Question format"),
            ("I need python", "Informal request"),
            ("show me my network settings", "Complex request"),
            ("what packages do I have?", "Status query")
        ]
        
        success_count = 0
        total_time = 0
        
        for query, description in test_queries:
            start = time.time()
            try:
                request = Request(query=query, context={'personality': 'minimal'})
                response = self.backend.process(request)
                elapsed = time.time() - start
                total_time += elapsed
                
                if response.success:
                    print(f"✅ {description}: Understood correctly ({elapsed:.3f}s)")
                    success_count += 1
                else:
                    print(f"❌ {description}: Failed to understand")
                    
            except Exception as e:
                print(f"❌ {description}: Error - {e}")
        
        feature_success = success_count == len(test_queries)
        self.results["features"]["natural_language"] = {
            "success": feature_success,
            "tests_passed": f"{success_count}/{len(test_queries)}",
            "avg_time": total_time / len(test_queries)
        }
        
        return feature_success
    
    def test_feature_2_smart_discovery(self):
        """Test smart package discovery with fuzzy matching"""
        print("\n🧪 Feature 2: Smart Package Discovery")
        print("-" * 50)
        
        test_searches = [
            ("browser", ["firefox", "chromium"]),
            ("editor", ["vim", "emacs", "vscode"]),
            ("pythn", ["python"]),  # Typo test
            ("development", ["git", "gcc", "make"])
        ]
        
        success_count = 0
        
        for search_term, expected_results in test_searches:
            try:
                request = Request(query=f"search {search_term}", context={})
                response = self.backend.process(request)
                
                if response.success:
                    # Check if any expected result is mentioned in response
                    found_any = any(pkg in response.text.lower() for pkg in expected_results)
                    if found_any:
                        print(f"✅ '{search_term}': Found relevant packages")
                        success_count += 1
                    else:
                        print(f"❌ '{search_term}': No relevant packages found")
                else:
                    print(f"❌ '{search_term}': Search failed")
                    
            except Exception as e:
                print(f"❌ '{search_term}': Error - {e}")
        
        feature_success = success_count >= len(test_searches) * 0.75  # 75% success rate
        self.results["features"]["smart_discovery"] = {
            "success": feature_success,
            "tests_passed": f"{success_count}/{len(test_searches)}"
        }
        
        return feature_success
    
    def test_feature_3_native_api(self):
        """Test native Python-Nix API performance"""
        print("\n🧪 Feature 3: Native Python-Nix API")
        print("-" * 50)
        
        # Test operations that should be fast with native API
        operations = [
            ("list generations", "show generations"),
            ("check status", "status"),
            ("garbage collection info", "garbage collect --dry-run")
        ]
        
        all_fast = True
        times = []
        
        for operation, query in operations:
            start = time.time()
            try:
                request = Request(query=query, context={})
                response = self.backend.process(request)
                elapsed = time.time() - start
                times.append(elapsed)
                
                if elapsed < 0.1:  # Should be very fast with native API
                    print(f"✅ {operation}: {elapsed:.3f}s (native speed)")
                else:
                    print(f"⚠️  {operation}: {elapsed:.3f}s (slower than expected)")
                    all_fast = False
                    
            except Exception as e:
                print(f"❌ {operation}: Error - {e}")
                all_fast = False
        
        avg_time = sum(times) / len(times) if times else 999
        self.results["features"]["native_api"] = {
            "success": all_fast,
            "avg_time": avg_time,
            "all_under_100ms": all_fast
        }
        
        return all_fast
    
    def test_feature_4_tui_availability(self):
        """Test TUI components are available"""
        print("\n🧪 Feature 4: Beautiful TUI")
        print("-" * 50)
        
        try:
            # Check if TUI files exist
            tui_files = [
                "tui/main.py",
                "tui/components/__init__.py",
                "tui/themes/__init__.py"
            ]
            
            missing_files = []
            for file in tui_files:
                if not Path(file).exists():
                    missing_files.append(file)
            
            if missing_files:
                print(f"⚠️  TUI files missing: {missing_files}")
                success = False
            else:
                print("✅ TUI components present")
                
                # Try to import TUI
                try:
                    from tui.main import NixHumanityTUI
                    print("✅ TUI imports successfully")
                    success = True
                except ImportError as e:
                    print(f"⚠️  TUI import failed: {e}")
                    success = False
            
        except Exception as e:
            print(f"❌ TUI test error: {e}")
            success = False
        
        self.results["features"]["tui"] = {"success": success}
        return success
    
    def test_feature_5_config_management(self):
        """Test configuration management capabilities"""
        print("\n🧪 Feature 5: Configuration Management")
        print("-" * 50)
        
        # Test configuration-related queries
        config_tests = [
            "show configuration",
            "how to edit configuration",
            "validate my config"
        ]
        
        success_count = 0
        
        for query in config_tests:
            try:
                request = Request(query=query, context={})
                response = self.backend.process(request)
                
                if response.success and "configuration" in response.text.lower():
                    print(f"✅ '{query}': Handled correctly")
                    success_count += 1
                else:
                    print(f"❌ '{query}': Failed")
                    
            except Exception as e:
                print(f"❌ '{query}': Error - {e}")
        
        feature_success = success_count == len(config_tests)
        self.results["features"]["config_management"] = {
            "success": feature_success,
            "tests_passed": f"{success_count}/{len(config_tests)}"
        }
        
        return feature_success
    
    def test_feature_6_home_manager(self):
        """Test Home Manager integration"""
        print("\n🧪 Feature 6: Home Manager Integration")
        print("-" * 50)
        
        queries = [
            "install firefox for my user",
            "home manager status",
            "user packages"
        ]
        
        handled_count = 0
        
        for query in queries:
            try:
                request = Request(query=query, context={})
                response = self.backend.process(request)
                
                # Check if response mentions home-manager or user-specific
                if "home" in response.text.lower() or "user" in response.text.lower():
                    print(f"✅ '{query}': Home Manager aware")
                    handled_count += 1
                else:
                    print(f"⚠️  '{query}': Generic response")
                    
            except Exception as e:
                print(f"❌ '{query}': Error - {e}")
        
        feature_success = handled_count >= 2  # At least 2/3 should be home-manager aware
        self.results["features"]["home_manager"] = {
            "success": feature_success,
            "awareness_count": f"{handled_count}/{len(queries)}"
        }
        
        return feature_success
    
    def test_feature_7_flake_support(self):
        """Test flake support"""
        print("\n🧪 Feature 7: Flake Support")
        print("-" * 50)
        
        flake_queries = [
            "update flake",
            "flake template",
            "use flakes"
        ]
        
        success_count = 0
        
        for query in flake_queries:
            try:
                request = Request(query=query, context={})
                response = self.backend.process(request)
                
                if response.success and "flake" in response.text.lower():
                    print(f"✅ '{query}': Flake support recognized")
                    success_count += 1
                else:
                    print(f"❌ '{query}': No flake support")
                    
            except Exception as e:
                print(f"❌ '{query}': Error - {e}")
        
        feature_success = success_count >= 2
        self.results["features"]["flake_support"] = {
            "success": feature_success,
            "tests_passed": f"{success_count}/{len(flake_queries)}"
        }
        
        return feature_success
    
    def test_feature_8_generation_management(self):
        """Test generation management"""
        print("\n🧪 Feature 8: Generation Management")
        print("-" * 50)
        
        # Test generation operations
        gen_operations = [
            ("list generations", 0.1),
            ("current generation", 0.1),
            ("rollback", 0.5)
        ]
        
        all_success = True
        
        for query, time_limit in gen_operations:
            start = time.time()
            try:
                request = Request(query=query, context={})
                response = self.backend.process(request)
                elapsed = time.time() - start
                
                if response.success and elapsed < time_limit:
                    print(f"✅ '{query}': Success in {elapsed:.3f}s")
                else:
                    print(f"❌ '{query}': Failed or too slow ({elapsed:.3f}s)")
                    all_success = False
                    
            except Exception as e:
                print(f"❌ '{query}': Error - {e}")
                all_success = False
        
        self.results["features"]["generation_management"] = {"success": all_success}
        return all_success
    
    def test_feature_9_error_handling(self):
        """Test intelligent error handling"""
        print("\n🧪 Feature 9: Intelligent Error Handling")
        print("-" * 50)
        
        # Test various error scenarios
        error_tests = [
            ("install nonexistentpackage123456", "package not found"),
            ("remove systemd", "permission"),
            ("invalid command syntax!!!", "syntax")
        ]
        
        educational_count = 0
        
        for query, expected_error in error_tests:
            try:
                request = Request(query=query, context={})
                response = self.backend.process(request)
                
                # Check if error is educational
                if not response.success:
                    # Look for educational markers
                    if any(marker in response.text for marker in ["🎓", "Understanding", "Learn"]):
                        print(f"✅ '{expected_error}': Educational error message")
                        educational_count += 1
                    else:
                        print(f"⚠️  '{expected_error}': Basic error message")
                else:
                    print(f"❌ '{expected_error}': Should have failed")
                    
            except Exception as e:
                # Even exceptions should be handled gracefully
                if "🎓" in str(e):
                    print(f"✅ '{expected_error}': Educational exception")
                    educational_count += 1
                else:
                    print(f"❌ '{expected_error}': Unhandled exception")
        
        feature_success = educational_count >= 2
        self.results["features"]["error_handling"] = {
            "success": feature_success,
            "educational_errors": f"{educational_count}/{len(error_tests)}"
        }
        
        return feature_success
    
    def test_feature_10_settings_profiles(self):
        """Test settings and profiles"""
        print("\n🧪 Feature 10: Settings & Profiles")
        print("-" * 50)
        
        # Test different personality styles
        personalities = ["minimal", "friendly", "encouraging", "technical"]
        
        success_count = 0
        
        for personality in personalities:
            try:
                request = Request(
                    query="help",
                    context={'personality': personality}
                )
                response = self.backend.process(request)
                
                if response.success:
                    print(f"✅ '{personality}' personality: Works correctly")
                    success_count += 1
                else:
                    print(f"❌ '{personality}' personality: Failed")
                    
            except Exception as e:
                print(f"❌ '{personality}' personality: Error - {e}")
        
        feature_success = success_count >= 3
        self.results["features"]["settings_profiles"] = {
            "success": feature_success,
            "personalities_working": f"{success_count}/{len(personalities)}"
        }
        
        return feature_success
    
    def test_complete_user_journey(self):
        """Test a complete user journey using multiple features"""
        print("\n🧪 Complete User Journey Test")
        print("-" * 50)
        
        journey_steps = [
            ("Hi, I'm new to NixOS", "Greeting"),
            ("What can you help me with?", "Capabilities"),
            ("I want to install a web browser", "Package discovery"),
            ("search firefox", "Package search"),
            ("install firefox", "Package installation"),
            ("show my generations", "Generation check"),
            ("help with configuration", "Config guidance")
        ]
        
        journey_success = True
        total_time = 0
        
        for step, description in journey_steps:
            start = time.time()
            try:
                request = Request(query=step, context={'personality': 'friendly'})
                response = self.backend.process(request)
                elapsed = time.time() - start
                total_time += elapsed
                
                if response.success:
                    print(f"✅ {description}: Completed ({elapsed:.3f}s)")
                else:
                    print(f"❌ {description}: Failed")
                    journey_success = False
                    
            except Exception as e:
                print(f"❌ {description}: Error - {e}")
                journey_success = False
        
        self.results["user_journey"] = {
            "success": journey_success,
            "total_time": total_time,
            "avg_step_time": total_time / len(journey_steps)
        }
        
        return journey_success
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Nix for Humanity v1.0 Final Integration Test")
        print("=" * 60)
        
        # Test all 10 features
        feature_results = [
            self.test_feature_1_natural_language(),
            self.test_feature_2_smart_discovery(),
            self.test_feature_3_native_api(),
            self.test_feature_4_tui_availability(),
            self.test_feature_5_config_management(),
            self.test_feature_6_home_manager(),
            self.test_feature_7_flake_support(),
            self.test_feature_8_generation_management(),
            self.test_feature_9_error_handling(),
            self.test_feature_10_settings_profiles()
        ]
        
        # Test complete user journey
        journey_success = self.test_complete_user_journey()
        
        # Calculate overall success
        features_passed = sum(feature_results)
        total_features = len(feature_results)
        
        self.results["summary"] = {
            "features_passed": f"{features_passed}/{total_features}",
            "user_journey_passed": journey_success,
            "overall_success": features_passed == total_features and journey_success
        }
        
        # Performance summary
        print("\n📊 Performance Summary")
        print("-" * 50)
        
        if "natural_language" in self.results["features"]:
            avg_response = self.results["features"]["natural_language"]["avg_time"]
            print(f"Average response time: {avg_response:.3f}s")
            
            if avg_response < 0.1:
                print("✅ Excellent performance (<100ms)")
            elif avg_response < 0.5:
                print("✅ Good performance (<500ms)")
            else:
                print("⚠️  Performance needs optimization")
        
        # Final report
        print("\n" + "=" * 60)
        print("📋 FINAL INTEGRATION TEST REPORT")
        print("=" * 60)
        print(f"Features Passed: {features_passed}/{total_features}")
        print(f"User Journey: {'PASSED' if journey_success else 'FAILED'}")
        print(f"Overall Result: {'✅ READY FOR RELEASE' if self.results['overall_success'] else '❌ NEEDS WORK'}")
        
        # Save detailed results
        with open("v1_integration_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print("\nDetailed results saved to: v1_integration_test_results.json")
        
        return self.results['overall_success']

def main():
    """Run the integration test"""
    test = V1IntegrationTest()
    success = test.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()