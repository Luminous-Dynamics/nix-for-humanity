#!/usr/bin/env python3
"""
Launch Readiness Assessment - Honest evaluation of what's ready for launch.
Part of "Foundation Building" - knowing exactly where we stand.
"""

import subprocess
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class LaunchReadinessAssessment:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "readiness_score": 0,
            "critical_features": {},
            "nice_to_haves": {},
            "blockers": [],
            "quick_wins": [],
            "recommendation": ""
        }
        
    def run_assessment(self):
        """Run comprehensive launch readiness check."""
        print("""
╔══════════════════════════════════════════════════════╗
║  🚀 LAUNCH READINESS ASSESSMENT - The Honest Truth    ║
╚══════════════════════════════════════════════════════╝
        """)
        
        # Test critical features
        self.test_critical_features()
        
        # Test nice-to-haves
        self.test_nice_to_haves()
        
        # Calculate readiness
        self.calculate_readiness()
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Show results
        self.display_results()
        
    def test_critical_features(self):
        """Test features that MUST work for launch."""
        print("\n🔴 Testing Critical Features...")
        print("-" * 40)
        
        critical_tests = {
            "basic_install": self.test_basic_install,
            "search_packages": self.test_search,
            "error_handling": self.test_error_handling,
            "help_system": self.test_help,
            "performance": self.test_performance
        }
        
        for name, test_func in critical_tests.items():
            result = test_func()
            self.results["critical_features"][name] = result
            
            if result["working"]:
                print(f"✅ {name}: WORKING")
            else:
                print(f"❌ {name}: BROKEN - {result['issue']}")
                self.results["blockers"].append({
                    "feature": name,
                    "issue": result["issue"],
                    "severity": "CRITICAL"
                })
                
    def test_nice_to_haves(self):
        """Test features that would be nice but not essential."""
        print("\n🟡 Testing Nice-to-Have Features...")
        print("-" * 40)
        
        nice_tests = {
            "tui_interface": self.test_tui,
            "voice_interface": self.test_voice,
            "learning_system": self.test_learning,
            "personas": self.test_personas,
            "advanced_search": self.test_advanced_search
        }
        
        for name, test_func in nice_tests.items():
            result = test_func()
            self.results["nice_to_haves"][name] = result
            
            if result["working"]:
                print(f"✅ {name}: WORKING")
            else:
                print(f"⚠️  {name}: Not ready - {result['issue']}")
                
    def test_basic_install(self) -> Dict:
        """Test if basic package installation works."""
        try:
            # Test dry-run install
            result = subprocess.run(
                ["./bin/ask-nix", "--dry-run", "install", "firefox"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd="/srv/luminous-dynamics/11-meta-consciousness/luminous-nix"
            )
            
            if result.returncode == 0:
                return {"working": True, "performance": "Good"}
            else:
                return {
                    "working": False, 
                    "issue": f"Exit code {result.returncode}",
                    "error": result.stderr[:100]
                }
                
        except subprocess.TimeoutExpired:
            return {"working": False, "issue": "Timeout after 5 seconds"}
        except Exception as e:
            return {"working": False, "issue": str(e)}
            
    def test_search(self) -> Dict:
        """Test package search functionality."""
        try:
            result = subprocess.run(
                ["./bin/ask-nix", "search", "editor"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd="/srv/luminous-dynamics/11-meta-consciousness/luminous-nix"
            )
            
            if result.returncode == 0 and len(result.stdout) > 10:
                return {"working": True, "results": "Found packages"}
            else:
                return {"working": False, "issue": "No results or error"}
                
        except:
            return {"working": False, "issue": "Search failed"}
            
    def test_error_handling(self) -> Dict:
        """Test if errors are handled gracefully."""
        try:
            # Intentional typo
            result = subprocess.run(
                ["./bin/ask-nix", "install", "fierfox"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd="/srv/luminous-dynamics/11-meta-consciousness/luminous-nix"
            )
            
            # Check if it suggests correction
            if "firefox" in result.stdout.lower() or "did you mean" in result.stdout.lower():
                return {"working": True, "feature": "Smart corrections"}
            elif result.returncode != 0 and not "Traceback" in result.stderr:
                return {"working": True, "feature": "No crashes"}
            else:
                return {"working": False, "issue": "Crashes on typos"}
                
        except:
            return {"working": False, "issue": "Error handling broken"}
            
    def test_help(self) -> Dict:
        """Test help system."""
        try:
            result = subprocess.run(
                ["./bin/ask-nix", "help"],
                capture_output=True,
                text=True,
                timeout=2,
                cwd="/srv/luminous-dynamics/11-meta-consciousness/luminous-nix"
            )
            
            if result.returncode == 0 and len(result.stdout) > 50:
                return {"working": True, "quality": "Good"}
            else:
                return {"working": False, "issue": "Help not helpful"}
                
        except:
            return {"working": False, "issue": "Help system broken"}
            
    def test_performance(self) -> Dict:
        """Test response times."""
        try:
            start = time.time()
            result = subprocess.run(
                ["./bin/ask-nix", "--version"],
                capture_output=True,
                text=True,
                timeout=2,
                cwd="/srv/luminous-dynamics/11-meta-consciousness/luminous-nix"
            )
            elapsed = time.time() - start
            
            if elapsed < 0.5:
                return {"working": True, "speed": "Fast"}
            elif elapsed < 2:
                return {"working": True, "speed": "Acceptable"}
            else:
                return {"working": False, "issue": f"Too slow: {elapsed:.1f}s"}
                
        except:
            return {"working": False, "issue": "Performance test failed"}
            
    def test_tui(self) -> Dict:
        """Test TUI interface."""
        # Can't really test interactive TUI automatically
        tui_path = Path("/srv/luminous-dynamics/11-meta-consciousness/luminous-nix/bin/nix-tui")
        if tui_path.exists():
            return {"working": True, "status": "Executable exists"}
        else:
            return {"working": False, "issue": "TUI not found"}
            
    def test_voice(self) -> Dict:
        """Test voice interface."""
        voice_path = Path("/srv/luminous-dynamics/11-meta-consciousness/luminous-nix/src/luminous_nix/voice")
        if voice_path.exists():
            return {"working": False, "issue": "Code exists but not integrated"}
        else:
            return {"working": False, "issue": "Not implemented"}
            
    def test_learning(self) -> Dict:
        """Test learning system."""
        memory_path = Path.home() / ".luminous-nix" / "memory"
        if memory_path.exists():
            return {"working": False, "issue": "Partially implemented"}
        else:
            return {"working": False, "issue": "Not active"}
            
    def test_personas(self) -> Dict:
        """Test persona system."""
        try:
            # Test if grandma mode works
            result = subprocess.run(
                ["./bin/ask-nix", "--persona", "grandma", "help"],
                capture_output=True,
                text=True,
                timeout=3,
                cwd="/srv/luminous-dynamics/11-meta-consciousness/luminous-nix"
            )
            
            if "--persona" in result.stderr or "unrecognized" in result.stderr:
                return {"working": False, "issue": "Not implemented"}
            else:
                return {"working": True, "status": "Basic personas"}
                
        except:
            return {"working": False, "issue": "Persona system not ready"}
            
    def test_advanced_search(self) -> Dict:
        """Test advanced search features."""
        return {"working": False, "issue": "Basic search only"}
        
    def calculate_readiness(self):
        """Calculate overall readiness score."""
        critical_working = sum(
            1 for r in self.results["critical_features"].values() 
            if r.get("working", False)
        )
        critical_total = len(self.results["critical_features"])
        
        nice_working = sum(
            1 for r in self.results["nice_to_haves"].values()
            if r.get("working", False)
        )
        nice_total = len(self.results["nice_to_haves"])
        
        # Critical features are 80% of score, nice-to-haves are 20%
        critical_score = (critical_working / critical_total * 80) if critical_total > 0 else 0
        nice_score = (nice_working / nice_total * 20) if nice_total > 0 else 0
        
        self.results["readiness_score"] = critical_score + nice_score
        
        # Identify quick wins
        if not self.results["critical_features"].get("error_handling", {}).get("working"):
            self.results["quick_wins"].append("Add try/catch blocks everywhere")
        if not self.results["critical_features"].get("help_system", {}).get("working"):
            self.results["quick_wins"].append("Write better help text")
        if not self.results["critical_features"].get("performance", {}).get("working"):
            self.results["quick_wins"].append("Add caching layer")
            
    def generate_recommendations(self):
        """Generate launch recommendations."""
        score = self.results["readiness_score"]
        
        if score < 50:
            self.results["recommendation"] = """
🔴 NOT READY FOR LAUNCH

Critical issues must be fixed first:
- Core functionality is broken
- Too many crashes and timeouts
- Poor user experience

Recommended: 2-3 weeks of intensive fixes
"""
        elif score < 70:
            self.results["recommendation"] = """
🟡 COULD LAUNCH WITH WARNINGS

You could do a "beta" launch but expect:
- High support burden
- Frustrated early users
- Reputation risk

Recommended: 1 week of critical fixes
"""
        elif score < 85:
            self.results["recommendation"] = """
🟢 READY FOR SOFT LAUNCH

Good enough for friendly audiences:
- Private beta with supporters
- Soft launch in niche communities
- Gather feedback before HN

Recommended: Polish for 3-5 days
"""
        else:
            self.results["recommendation"] = """
✅ READY FOR PUBLIC LAUNCH

Ship it! You're ready for:
- Hacker News launch
- Product Hunt feature
- Broad public release

Recommended: Launch this week!
"""

    def display_results(self):
        """Display assessment results."""
        print("\n" + "=" * 50)
        print("📊 LAUNCH READINESS RESULTS")
        print("=" * 50)
        
        # Overall score
        score = self.results["readiness_score"]
        print(f"\n🎯 Overall Readiness: {score:.0f}%")
        
        # Progress bar
        bar_length = 40
        filled = int(bar_length * score / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"[{bar}]")
        
        # Critical features status
        critical_working = sum(
            1 for r in self.results["critical_features"].values()
            if r.get("working", False)
        )
        critical_total = len(self.results["critical_features"])
        print(f"\n🔴 Critical Features: {critical_working}/{critical_total} working")
        
        # Nice-to-haves status
        nice_working = sum(
            1 for r in self.results["nice_to_haves"].values()
            if r.get("working", False)
        )
        nice_total = len(self.results["nice_to_haves"])
        print(f"🟡 Nice-to-Haves: {nice_working}/{nice_total} working")
        
        # Blockers
        if self.results["blockers"]:
            print(f"\n🚫 Critical Blockers ({len(self.results['blockers'])}):")
            for blocker in self.results["blockers"][:3]:
                print(f"  • {blocker['feature']}: {blocker['issue']}")
        
        # Quick wins
        if self.results["quick_wins"]:
            print(f"\n💡 Quick Wins to Improve Score:")
            for win in self.results["quick_wins"][:3]:
                print(f"  • {win}")
        
        # Recommendation
        print(self.results["recommendation"])
        
        # Save full report
        report_path = Path("launch_readiness_report.json")
        with open(report_path, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 Full report: {report_path}")
        
def main():
    """Run the assessment."""
    assessment = LaunchReadinessAssessment()
    assessment.run_assessment()
    
    # Return exit code based on readiness
    if assessment.results["readiness_score"] < 50:
        return 1  # Not ready
    else:
        return 0  # Ready enough
        
if __name__ == "__main__":
    import sys
    sys.exit(main())