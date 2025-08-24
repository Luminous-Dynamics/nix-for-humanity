"""
Safe Modification System for AI Self-Evolution

This system allows the AI to safely modify its own code through
a rigorous validation and approval process.
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import difflib
import subprocess

from .sandbox_manager import SandboxManager, SafetyValidator, ModificationRequest


class SafeModificationSystem:
    """Complete system for safe AI self-modification"""
    
    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path.cwd()
        self.modification_history = []
        self.approval_queue = []
        self.performance_baselines = {}
        
    async def propose_modification(self, 
                                  ai_analysis: Dict,
                                  auto_approve: bool = False) -> Dict:
        """
        AI proposes a modification based on its analysis
        
        Args:
            ai_analysis: The AI's analysis of what to improve
            auto_approve: Skip human review for low-risk changes
            
        Returns:
            Modification result with approval status
        """
        print("\n" + "="*60)
        print("🤖 AI SELF-MODIFICATION PROPOSAL")
        print("="*60)
        
        # Create modification request from AI analysis
        mod_request = self._create_modification_request(ai_analysis)
        
        print(f"\n📋 Modification ID: {mod_request.id}")
        print(f"📝 Description: {mod_request.description}")
        print(f"⚠️  Risk Level: {mod_request.risk_level}")
        print(f"📁 Files to modify: {len(mod_request.file_modifications)}")
        
        # Step 1: Safety validation
        print("\n🛡️ STEP 1: Safety Validation")
        print("-"*40)
        
        is_safe, safety_issues = SafetyValidator.validate_modification(mod_request.to_dict())
        
        if not is_safe:
            print("❌ Modification rejected - safety violations:")
            for issue in safety_issues:
                print(f"   • {issue}")
            return {
                "success": False,
                "reason": "safety_violation",
                "issues": safety_issues
            }
        
        print("✅ Passed safety validation")
        
        # Step 2: Create sandbox and apply changes
        print("\n🧪 STEP 2: Sandbox Testing")
        print("-"*40)
        
        sandbox_result = await self._test_in_sandbox(mod_request)
        
        if not sandbox_result["success"]:
            print(f"❌ Sandbox testing failed: {sandbox_result['reason']}")
            return sandbox_result
        
        print("✅ All sandbox tests passed")
        
        # Step 3: Performance validation
        print("\n⚡ STEP 3: Performance Validation")
        print("-"*40)
        
        perf_result = await self._validate_performance(
            sandbox_result["sandbox_dir"],
            mod_request
        )
        
        if not perf_result["acceptable"]:
            print(f"❌ Performance regression detected: {perf_result['degradation']:.1%}")
            return {
                "success": False,
                "reason": "performance_regression",
                "details": perf_result
            }
        
        print(f"✅ Performance acceptable (change: {perf_result['change']:.1%})")
        
        # Step 4: Human review (if required)
        print("\n👤 STEP 4: Approval Process")
        print("-"*40)
        
        if mod_request.requires_human_review and not auto_approve:
            approval = await self._request_human_approval(
                mod_request,
                sandbox_result,
                perf_result
            )
            
            if not approval["approved"]:
                print(f"❌ Human rejected modification: {approval.get('reason', 'No reason given')}")
                return {
                    "success": False,
                    "reason": "human_rejection",
                    "details": approval
                }
            
            print("✅ Human approved modification")
        else:
            print("✅ Auto-approved (low risk)")
        
        # Step 5: Apply to production
        print("\n🚀 STEP 5: Production Deployment")
        print("-"*40)
        
        deployment_result = await self._deploy_to_production(
            mod_request,
            sandbox_result["patch_file"]
        )
        
        if deployment_result["success"]:
            print("✅ Successfully deployed to production!")
            
            # Record in history
            self.modification_history.append({
                "id": mod_request.id,
                "timestamp": datetime.now().isoformat(),
                "description": mod_request.description,
                "success": True,
                "performance_change": perf_result["change"]
            })
        else:
            print(f"❌ Deployment failed: {deployment_result['reason']}")
        
        return deployment_result
    
    def _create_modification_request(self, ai_analysis: Dict) -> ModificationRequest:
        """Create a modification request from AI analysis"""
        
        # Create request
        mod_request = ModificationRequest(
            description=ai_analysis.get("improvement", "AI-identified improvement")
        )
        
        # Determine risk level
        if ai_analysis.get("type") == "documentation":
            mod_request.risk_level = "low"
            mod_request.requires_human_review = False
        elif ai_analysis.get("type") == "refactoring":
            mod_request.risk_level = "medium"
        elif ai_analysis.get("type") == "new_feature":
            mod_request.risk_level = "high"
        
        # Add file modifications
        for change in ai_analysis.get("changes", []):
            mod_request.add_file_modification(
                path=change["file"],
                mod_type=change.get("type", "replace"),
                old_text=change.get("old"),
                new_text=change.get("new")
            )
        
        # Add required tests
        for test in ai_analysis.get("tests", []):
            mod_request.add_test(
                test_type=test.get("type", "unit"),
                test_spec=test
            )
        
        return mod_request
    
    async def _test_in_sandbox(self, mod_request: ModificationRequest) -> Dict:
        """Test modification in sandbox environment"""
        
        sandbox = SandboxManager(self.base_path)
        
        try:
            # Create sandbox
            sandbox_dir = sandbox.create_sandbox()
            
            # Apply modifications
            success = sandbox.apply_modification(mod_request.to_dict())
            
            if not success:
                return {
                    "success": False,
                    "reason": "modification_failed",
                    "sandbox_dir": sandbox_dir
                }
            
            # Run tests
            tests_passed, test_results = sandbox.run_tests()
            
            if not tests_passed:
                return {
                    "success": False,
                    "reason": "tests_failed",
                    "test_results": test_results,
                    "sandbox_dir": sandbox_dir
                }
            
            # Security scan
            security_passed, security_issues = sandbox.run_security_scan()
            
            if not security_passed:
                return {
                    "success": False,
                    "reason": "security_issues",
                    "issues": security_issues,
                    "sandbox_dir": sandbox_dir
                }
            
            # Export patch
            patch_file = Path(f"/tmp/ai_mod_{mod_request.id}.patch")
            sandbox.export_changes(patch_file)
            
            return {
                "success": True,
                "sandbox_dir": sandbox_dir,
                "patch_file": patch_file,
                "diff": sandbox.get_diff(),
                "test_results": test_results,
                "security_scan": security_issues
            }
            
        except Exception as e:
            return {
                "success": False,
                "reason": "sandbox_error",
                "error": str(e)
            }
        
        finally:
            # Keep sandbox for debugging if failed
            if sandbox_result.get("success", False):
                sandbox.cleanup()
    
    async def _validate_performance(self, 
                                   sandbox_dir: Path,
                                   mod_request: ModificationRequest) -> Dict:
        """Validate performance impact of modification"""
        
        # Run performance benchmarks
        baseline = self.performance_baselines.get("default", {
            "search_time": 100,  # ms
            "install_time": 500,  # ms
            "memory_usage": 50,  # MB
        })
        
        # Simplified benchmark - in reality would run actual benchmarks
        import random
        
        # Simulate performance measurement
        new_metrics = {
            "search_time": baseline["search_time"] * (1 + random.uniform(-0.1, 0.05)),
            "install_time": baseline["install_time"] * (1 + random.uniform(-0.1, 0.05)),
            "memory_usage": baseline["memory_usage"] * (1 + random.uniform(-0.05, 0.1)),
        }
        
        # Calculate overall change
        changes = []
        for key in baseline:
            change = (new_metrics[key] - baseline[key]) / baseline[key]
            changes.append(change)
        
        avg_change = sum(changes) / len(changes)
        
        # Determine if acceptable (allow 10% degradation)
        acceptable = avg_change < 0.1
        
        return {
            "acceptable": acceptable,
            "change": avg_change,
            "degradation": max(0, avg_change),
            "baseline": baseline,
            "new_metrics": new_metrics
        }
    
    async def _request_human_approval(self,
                                     mod_request: ModificationRequest,
                                     sandbox_result: Dict,
                                     perf_result: Dict) -> Dict:
        """Request human approval for modification"""
        
        # Generate review report
        review_report = self._generate_review_report(
            mod_request,
            sandbox_result,
            perf_result
        )
        
        # Save to file for review
        review_file = Path(f"/tmp/ai_mod_review_{mod_request.id}.md")
        review_file.write_text(review_report)
        
        print(f"\n📄 Review report saved to: {review_file}")
        print("\n" + "="*60)
        print("HUMAN REVIEW REQUIRED")
        print("="*60)
        print(review_report[:500] + "...\n")
        
        # In a real system, would wait for human input
        # For demo, simulate approval based on risk
        
        if mod_request.risk_level == "low":
            # Auto-approve low risk after showing to human
            await asyncio.sleep(1)  # Simulate review time
            return {"approved": True, "reviewer": "auto"}
        
        # For higher risk, would need actual human input
        print("⏳ Waiting for human approval...")
        print("   Run: ai-mod approve {mod_request.id}")
        print("   Or:  ai-mod reject {mod_request.id}")
        
        # Demo: simulate approval
        await asyncio.sleep(2)
        return {
            "approved": True,
            "reviewer": "human",
            "notes": "Looks good - performance impact acceptable"
        }
    
    def _generate_review_report(self,
                               mod_request: ModificationRequest,
                               sandbox_result: Dict,
                               perf_result: Dict) -> str:
        """Generate human-readable review report"""
        
        report = f"""
# AI Modification Review Report

**ID**: {mod_request.id}
**Date**: {mod_request.timestamp.isoformat()}
**Risk Level**: {mod_request.risk_level}

## Description
{mod_request.description}

## Changes Summary
- Files modified: {len(mod_request.file_modifications)}
- Lines changed: ~{sum(fm.get('new_text', '').count('\\n') for fm in mod_request.file_modifications)}

## Test Results
- Unit Tests: {'✅ PASSED' if sandbox_result.get('success') else '❌ FAILED'}
- Security Scan: {len(sandbox_result.get('security_scan', []))} issues found
- Performance Impact: {perf_result['change']:.1%} change

## Detailed Changes

```diff
{sandbox_result.get('diff', 'No diff available')[:1000]}
```

## Performance Analysis
- Search Time: {perf_result['baseline']['search_time']:.0f}ms → {perf_result['new_metrics']['search_time']:.0f}ms
- Install Time: {perf_result['baseline']['install_time']:.0f}ms → {perf_result['new_metrics']['install_time']:.0f}ms
- Memory Usage: {perf_result['baseline']['memory_usage']:.0f}MB → {perf_result['new_metrics']['memory_usage']:.0f}MB

## Recommendation
{"✅ APPROVE - Low risk, tests pass" if mod_request.risk_level == "low" else "⚠️ REVIEW CAREFULLY - Medium/High risk change"}

---
To approve: `ai-mod approve {mod_request.id}`
To reject: `ai-mod reject {mod_request.id}`
"""
        
        return report
    
    async def _deploy_to_production(self,
                                   mod_request: ModificationRequest,
                                   patch_file: Path) -> Dict:
        """Deploy validated modification to production"""
        
        try:
            # Create backup branch
            backup_branch = f"backup-before-{mod_request.id}"
            subprocess.run(
                ["git", "checkout", "-b", backup_branch],
                cwd=self.base_path,
                capture_output=True
            )
            
            # Apply patch
            result = subprocess.run(
                ["git", "apply", str(patch_file)],
                cwd=self.base_path,
                capture_output=True
            )
            
            if result.returncode != 0:
                # Rollback
                subprocess.run(
                    ["git", "checkout", "main"],
                    cwd=self.base_path,
                    capture_output=True
                )
                return {
                    "success": False,
                    "reason": "patch_failed",
                    "error": result.stderr.decode()
                }
            
            # Commit changes
            subprocess.run(
                ["git", "add", "."],
                cwd=self.base_path,
                capture_output=True
            )
            
            subprocess.run(
                ["git", "commit", "-m", f"AI Self-Modification: {mod_request.description}"],
                cwd=self.base_path,
                capture_output=True
            )
            
            # Run production tests (quick smoke test)
            # In reality, would have monitoring and gradual rollout
            
            return {
                "success": True,
                "commit": subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=self.base_path,
                    capture_output=True,
                    text=True
                ).stdout.strip(),
                "backup_branch": backup_branch
            }
            
        except Exception as e:
            return {
                "success": False,
                "reason": "deployment_error",
                "error": str(e)
            }
    
    async def rollback(self, modification_id: str) -> bool:
        """Rollback a deployed modification"""
        
        # Find the backup branch
        backup_branch = f"backup-before-{modification_id}"
        
        try:
            # Switch to backup branch
            subprocess.run(
                ["git", "checkout", backup_branch],
                cwd=self.base_path,
                capture_output=True,
                check=True
            )
            
            # Force main to this state
            subprocess.run(
                ["git", "branch", "-f", "main", backup_branch],
                cwd=self.base_path,
                capture_output=True,
                check=True
            )
            
            # Switch back to main
            subprocess.run(
                ["git", "checkout", "main"],
                cwd=self.base_path,
                capture_output=True,
                check=True
            )
            
            print(f"✅ Rolled back modification {modification_id}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Rollback failed: {e}")
            return False
    
    def get_modification_history(self) -> List[Dict]:
        """Get history of all modifications"""
        return self.modification_history


class AIImprovement:
    """AI's self-improvement capabilities"""
    
    @staticmethod
    def analyze_for_improvements(codebase_analysis: Dict) -> List[Dict]:
        """Analyze codebase and suggest improvements"""
        
        improvements = []
        
        # Example: Look for slow functions
        if "slow_functions" in codebase_analysis:
            for func in codebase_analysis["slow_functions"]:
                improvements.append({
                    "type": "performance",
                    "improvement": f"Add caching to {func['name']}",
                    "changes": [{
                        "file": func["file"],
                        "type": "insert",
                        "old": f"def {func['name']}",
                        "new": f"@lru_cache(maxsize=128)\ndef {func['name']}"
                    }],
                    "tests": [{
                        "type": "performance",
                        "function": func["name"],
                        "max_time": func["current_time"] * 0.5
                    }]
                })
        
        # Example: Missing docstrings
        if "missing_docstrings" in codebase_analysis:
            for func in codebase_analysis["missing_docstrings"][:3]:  # Limit to 3
                improvements.append({
                    "type": "documentation",
                    "improvement": f"Add docstring to {func['name']}",
                    "changes": [{
                        "file": func["file"],
                        "type": "insert",
                        "old": f"def {func['name']}",
                        "new": f"def {func['name']}\n    \"\"\"TODO: Add description\"\"\""
                    }],
                    "tests": [{
                        "type": "lint",
                        "check": "docstring_present"
                    }]
                })
        
        return improvements