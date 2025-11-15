#!/usr/bin/env python3
"""
Advanced Features CLI - Phase 1 Integration
Integrates Rollback Intelligence, Storage Optimizer, and Security Auditor
"""

import sys
import os
import argparse
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import Phase 1 features
from luminous_nix.ai.advanced_features.rollback_intelligence import RollbackIntelligence
from luminous_nix.ai.advanced_features.storage_optimizer import StorageOptimizer
from luminous_nix.ai.advanced_features.security_auditor import SecurityAuditor, Severity


# ANSI colors for output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def format_size(size_gb: float) -> str:
    """Format size in GB to human readable"""
    if size_gb >= 1:
        return f"{size_gb:.1f}GB"
    else:
        return f"{size_gb*1024:.0f}MB"


def format_severity(severity: Severity) -> str:
    """Format severity with color"""
    colors = {
        Severity.CRITICAL: Colors.RED,
        Severity.HIGH: Colors.YELLOW,
        Severity.MEDIUM: Colors.BLUE,
        Severity.LOW: Colors.GREEN,
    }
    return f"{colors.get(severity, '')}{severity.value.upper()}{Colors.ENDC}"


class AdvancedFeaturesCLI:
    """CLI handler for advanced HRM-powered features"""

    def __init__(self):
        self.rollback = RollbackIntelligence()
        self.storage = StorageOptimizer()
        self.security = SecurityAuditor()

        # Check for verbose mode
        self.verbose = int(os.environ.get("LUMINOUS_VERBOSE", "0")) > 0
        self.json_output = os.environ.get("LUMINOUS_JSON", "false").lower() == "true"
        self.dry_run = os.environ.get("LUMINOUS_DRY_RUN", "false").lower() == "true"

    # ==================== ROLLBACK INTELLIGENCE ====================

    def handle_rollback(self, args: List[str]) -> int:
        """Handle rollback-related commands"""
        if not args or args[0] == "help":
            return self.rollback_help()

        subcommand = args[0]

        if subcommand == "analyze":
            symptoms = " ".join(args[1:]) if len(args) > 1 else None
            return self.rollback_analyze(symptoms)
        elif subcommand == "check":
            if len(args) < 2:
                print(f"{Colors.RED}Error: Generation number required{Colors.ENDC}")
                return 1
            try:
                generation = int(args[1])
                return self.rollback_check(generation)
            except ValueError:
                print(f"{Colors.RED}Error: Invalid generation number{Colors.ENDC}")
                return 1
        elif subcommand == "find-working":
            if len(args) < 2:
                print(f"{Colors.RED}Error: Component name required{Colors.ENDC}")
                return 1
            component = args[1]
            return self.rollback_find_working(component)
        elif subcommand == "summary":
            generation = int(args[1]) if len(args) > 1 else None
            return self.rollback_summary(generation)
        else:
            print(f"{Colors.RED}Unknown rollback command: {subcommand}{Colors.ENDC}")
            return self.rollback_help()

    def rollback_analyze(self, symptoms: Optional[str]) -> int:
        """Analyze system failure and recommend rollback"""
        if not self.json_output:
            print(
                f"{Colors.HEADER}🔄 Analyzing System for Safe Rollback...{Colors.ENDC}"
            )

        analysis = self.rollback.analyze_system_failure(symptoms)

        if self.json_output:
            print(
                json.dumps(
                    {
                        "current_generation": analysis.current_generation,
                        "recommended_generation": analysis.recommended_generation,
                        "confidence": analysis.confidence,
                        "reason": analysis.reason,
                        "risk_level": analysis.risk_level,
                        "command": analysis.rollback_command,
                        "changes": analysis.changes_detected[:5],
                    }
                )
            )
        else:
            print(
                f"\n{Colors.BOLD}Current Generation:{Colors.ENDC} {analysis.current_generation}"
            )
            print(
                f"{Colors.BOLD}Recommended Rollback:{Colors.ENDC} Generation {analysis.recommended_generation}"
            )
            print(f"{Colors.BOLD}Confidence:{Colors.ENDC} {analysis.confidence:.0%}")
            print(f"{Colors.BOLD}Risk Level:{Colors.ENDC} {analysis.risk_level}")
            print(f"{Colors.BOLD}Reason:{Colors.ENDC} {analysis.reason}")

            if analysis.changes_detected:
                print(f"\n{Colors.BOLD}Breaking Changes Detected:{Colors.ENDC}")
                for change in analysis.changes_detected[:5]:
                    print(f"  • {change}")

            print(f"\n{Colors.GREEN}Rollback Command:{Colors.ENDC}")
            print(f"  {analysis.rollback_command}")

            if analysis.alternative_generations:
                print(f"\n{Colors.BOLD}Alternative Options:{Colors.ENDC}")
                for gen, reason in analysis.alternative_generations[:3]:
                    print(f"  • Generation {gen}: {reason}")

        return 0

    def rollback_check(self, generation: int) -> int:
        """Check safety of a specific generation"""
        if not self.json_output:
            print(
                f"{Colors.HEADER}🔍 Checking Generation {generation} Safety...{Colors.ENDC}"
            )

        safety = self.rollback.analyze_generation_safety(generation)

        if self.json_output:
            print(json.dumps(safety))
        else:
            score = safety["safety_score"]
            safe = safety["safe_to_rollback"]

            print(f"\n{Colors.BOLD}Generation:{Colors.ENDC} {generation}")
            print(f"{Colors.BOLD}Safety Score:{Colors.ENDC} {score:.2f}/1.0")
            print(
                f"{Colors.BOLD}Safe to Rollback:{Colors.ENDC} {'✅ Yes' if safe else '❌ No'}"
            )
            print(
                f"{Colors.BOLD}Recommendation:{Colors.ENDC} {safety.get('recommendation', 'N/A')}"
            )

            if safety.get("breaking_changes"):
                print(f"\n{Colors.BOLD}Breaking Changes:{Colors.ENDC}")
                for change in safety["breaking_changes"][:5]:
                    print(f"  • {change}")

            if safety.get("safe_changes"):
                print(f"\n{Colors.BOLD}Safe Changes:{Colors.ENDC}")
                for change in safety["safe_changes"][:5]:
                    print(f"  • {change}")

        return 0 if safety.get("safe_to_rollback", False) else 1

    def rollback_find_working(self, component: str) -> int:
        """Find last working generation for a component"""
        if not self.json_output:
            print(
                f"{Colors.HEADER}🔎 Finding Last Working Generation for '{component}'...{Colors.ENDC}"
            )

        generation = self.rollback.find_last_working_generation(component)

        if self.json_output:
            print(json.dumps({"component": component, "last_working": generation}))
        else:
            if generation is not None:
                print(f"\n{Colors.GREEN}✅ Found: Generation {generation}{Colors.ENDC}")
                print(f"\nRollback command:")
                print(f"  sudo nixos-rebuild switch --rollback-to {generation}")
            else:
                print(
                    f"\n{Colors.YELLOW}⚠️ No previous working generation found{Colors.ENDC}"
                )
                print(f"Component '{component}' may not have changed recently")

        return 0 if generation is not None else 1

    def rollback_summary(self, generation: Optional[int]) -> int:
        """Get summary of what changed in a generation"""
        if generation is None:
            print(f"{Colors.RED}Error: Generation number required{Colors.ENDC}")
            return 1

        summary = self.rollback.get_generation_summary(generation)

        if self.json_output:
            print(json.dumps({"generation": generation, "summary": summary}))
        else:
            print(f"\n{Colors.BOLD}Generation {generation} Summary:{Colors.ENDC}")
            print(f"  {summary}")

        return 0

    def rollback_help(self) -> int:
        """Show rollback command help"""
        print(f"{Colors.HEADER}🔄 Rollback Intelligence Commands{Colors.ENDC}")
        print("\nUsage: luminous-nix rollback <command> [options]")
        print("\nCommands:")
        print("  analyze [symptoms]     - Find safe rollback point")
        print("  check <generation>     - Check if generation is safe")
        print("  find-working <comp>    - Find last working generation for component")
        print("  summary <generation>   - Show what changed in generation")
        print("  help                   - Show this help")
        print("\nExamples:")
        print("  luminous-nix rollback analyze 'system won't boot'")
        print("  luminous-nix rollback check 42")
        print("  luminous-nix rollback find-working nvidia")
        return 0

    # ==================== STORAGE OPTIMIZER ====================

    def handle_storage(self, args: List[str]) -> int:
        """Handle storage-related commands"""
        if not args or args[0] == "help":
            return self.storage_help()

        subcommand = args[0]

        if subcommand == "analyze":
            aggressive = "--aggressive" in args
            return self.storage_analyze(aggressive)
        elif subcommand == "cleanup":
            aggressive = "--aggressive" in args
            return self.storage_cleanup(aggressive)
        elif subcommand == "optimize":
            target = 10.0  # Default target
            for arg in args[1:]:
                try:
                    target = float(arg)
                    break
                except ValueError:
                    pass
            return self.storage_optimize(target)
        elif subcommand == "large":
            min_size = 100  # Default 100MB
            for arg in args[1:]:
                try:
                    min_size = int(arg)
                    break
                except ValueError:
                    pass
            return self.storage_find_large(min_size)
        else:
            print(f"{Colors.RED}Unknown storage command: {subcommand}{Colors.ENDC}")
            return self.storage_help()

    def storage_analyze(self, aggressive: bool) -> int:
        """Analyze storage usage"""
        if not self.json_output:
            mode = "aggressive" if aggressive else "safe"
            print(f"{Colors.HEADER}💾 Analyzing Storage ({mode} mode)...{Colors.ENDC}")

        analysis = self.storage.analyze_storage(aggressive)

        if self.json_output:
            print(
                json.dumps(
                    {
                        "total_size_gb": analysis.total_store_size_gb,
                        "reclaimable_gb": analysis.reclaimable_gb,
                        "safe_gb": analysis.safe_to_remove_gb,
                        "risky_gb": analysis.risky_to_remove_gb,
                        "confidence": analysis.confidence,
                        "estimated_time": analysis.estimated_time_minutes,
                    }
                )
            )
        else:
            print(
                f"\n{Colors.BOLD}Nix Store Size:{Colors.ENDC} {format_size(analysis.total_store_size_gb)}"
            )
            print(
                f"{Colors.BOLD}Reclaimable Space:{Colors.ENDC} {format_size(analysis.reclaimable_gb)}"
            )
            print(f"  • Safe to remove: {format_size(analysis.safe_to_remove_gb)}")
            print(f"  • Risky to remove: {format_size(analysis.risky_to_remove_gb)}")
            print(f"{Colors.BOLD}Confidence:{Colors.ENDC} {analysis.confidence:.0%}")
            print(
                f"{Colors.BOLD}Estimated Time:{Colors.ENDC} {analysis.estimated_time_minutes:.0f} minutes"
            )

            if analysis.breakdown:
                print(f"\n{Colors.BOLD}Breakdown by Category:{Colors.ENDC}")
                for category, size in analysis.breakdown.items():
                    if size > 0:
                        print(f"  • {category}: {format_size(size)}")

            if analysis.old_generations:
                print(
                    f"\n{Colors.BOLD}Old Generations ({len(analysis.old_generations)}):{Colors.ENDC}"
                )
                for gen in analysis.old_generations[:5]:
                    print(f"  • Generation {gen['number']} ({gen['date']})")

            if analysis.cleanup_commands:
                print(f"\n{Colors.GREEN}Cleanup Commands:{Colors.ENDC}")
                for cmd in analysis.cleanup_commands:
                    if cmd.startswith("#"):
                        print(f"  {cmd}")
                    else:
                        print(f"  $ {cmd}")

        return 0

    def storage_cleanup(self, aggressive: bool) -> int:
        """Perform storage cleanup"""
        if self.dry_run:
            print(
                f"{Colors.YELLOW}DRY RUN - Commands will be shown but not executed{Colors.ENDC}"
            )

        analysis = self.storage.analyze_storage(aggressive)

        if not self.json_output:
            print(
                f"\n{Colors.BOLD}Ready to free {format_size(analysis.reclaimable_gb)}{Colors.ENDC}"
            )

            if not self.dry_run:
                response = input(
                    f"\n{Colors.YELLOW}Proceed with cleanup? [y/N]: {Colors.ENDC}"
                )
                if response.lower() != "y":
                    print("Cleanup cancelled")
                    return 1

        # Execute or show commands
        for cmd in analysis.cleanup_commands:
            if cmd.startswith("#"):
                if not self.json_output:
                    print(f"\n{cmd}")
            else:
                if self.dry_run or self.json_output:
                    print(f"$ {cmd}")
                else:
                    print(f"$ {cmd}")
                    os.system(cmd)

        if not self.dry_run and not self.json_output:
            print(f"\n{Colors.GREEN}✅ Cleanup complete!{Colors.ENDC}")

        return 0

    def storage_optimize(self, target_gb: float) -> int:
        """Optimize to free specific amount of space"""
        if not self.json_output:
            print(
                f"{Colors.HEADER}💾 Optimizing to Free {format_size(target_gb)}...{Colors.ENDC}"
            )

        plan = self.storage.optimize_store(target_gb)

        if self.json_output:
            print(json.dumps(plan))
        else:
            can_achieve = plan.get("can_achieve", False)
            available = plan.get("available_gb", 0)

            if can_achieve:
                print(
                    f"\n{Colors.GREEN}✅ Can free {format_size(target_gb)}{Colors.ENDC}"
                )
            else:
                print(
                    f"\n{Colors.YELLOW}⚠️ Can only free {format_size(available)}{Colors.ENDC}"
                )

            if plan.get("steps"):
                print(f"\n{Colors.BOLD}Optimization Steps:{Colors.ENDC}")
                for step in plan["steps"]:
                    risk = step.get("risk", "unknown")
                    risk_color = (
                        Colors.GREEN
                        if risk == "none"
                        else Colors.YELLOW
                        if risk == "low"
                        else Colors.RED
                    )
                    print(
                        f"  • {step['action']}: {format_size(step['space_gb'])} ({risk_color}{risk} risk{Colors.ENDC})"
                    )
                    print(f"    Command: {step['command']}")

        return 0 if plan.get("can_achieve", False) else 1

    def storage_find_large(self, min_size_mb: int) -> int:
        """Find large packages"""
        if not self.json_output:
            print(
                f"{Colors.HEADER}🔍 Finding Packages Larger Than {min_size_mb}MB...{Colors.ENDC}"
            )

        packages = self.storage.find_large_packages(min_size_mb)

        if self.json_output:
            print(json.dumps(packages))
        else:
            if packages:
                print(
                    f"\n{Colors.BOLD}Found {len(packages)} Large Packages:{Colors.ENDC}"
                )
                for pkg in packages:
                    print(f"  • {pkg['name']}: {pkg['size_mb']}MB")
            else:
                print(
                    f"\n{Colors.YELLOW}No packages larger than {min_size_mb}MB found{Colors.ENDC}"
                )

        return 0

    def storage_help(self) -> int:
        """Show storage command help"""
        print(f"{Colors.HEADER}💾 Storage Optimization Commands{Colors.ENDC}")
        print("\nUsage: luminous-nix storage <command> [options]")
        print("\nCommands:")
        print("  analyze [--aggressive]  - Analyze storage usage")
        print("  cleanup [--aggressive]  - Clean up storage safely")
        print("  optimize <GB>          - Free specific amount of space")
        print("  large [min_MB]         - Find large packages")
        print("  help                   - Show this help")
        print("\nExamples:")
        print("  luminous-nix storage analyze")
        print("  luminous-nix storage cleanup --aggressive")
        print("  luminous-nix storage optimize 10")
        print("  luminous-nix storage large 500")
        return 0

    # ==================== SECURITY AUDITOR ====================

    def handle_security(self, args: List[str]) -> int:
        """Handle security-related commands"""
        if not args or args[0] == "help":
            return self.security_help()

        subcommand = args[0]

        if subcommand == "audit":
            deep = "--deep" in args
            return self.security_audit(deep)
        elif subcommand == "check":
            if len(args) < 2:
                print(f"{Colors.RED}Error: Package name required{Colors.ENDC}")
                return 1
            package = args[1]
            return self.security_check(package)
        elif subcommand == "harden":
            return self.security_harden()
        elif subcommand == "updates":
            return self.security_updates()
        else:
            print(f"{Colors.RED}Unknown security command: {subcommand}{Colors.ENDC}")
            return self.security_help()

    def security_audit(self, deep: bool) -> int:
        """Perform security audit"""
        if not self.json_output:
            scan_type = "deep" if deep else "standard"
            print(
                f"{Colors.HEADER}🔐 Running Security Audit ({scan_type})...{Colors.ENDC}"
            )

        audit = self.security.audit_system(deep_scan=deep)

        if self.json_output:
            print(
                json.dumps(
                    {
                        "scan_date": audit.scan_date.isoformat(),
                        "packages_scanned": audit.total_packages_scanned,
                        "critical": audit.critical_count,
                        "high": audit.high_count,
                        "medium": audit.medium_count,
                        "low": audit.low_count,
                        "security_score": audit.security_score,
                        "risk_level": audit.risk_level,
                    }
                )
            )
        else:
            # Score color based on level
            score = audit.security_score
            if score >= 80:
                score_color = Colors.GREEN
            elif score >= 60:
                score_color = Colors.YELLOW
            else:
                score_color = Colors.RED

            print(
                f"\n{Colors.BOLD}Security Score:{Colors.ENDC} {score_color}{score:.0f}/100{Colors.ENDC}"
            )
            print(f"{Colors.BOLD}Risk Level:{Colors.ENDC} {audit.risk_level.upper()}")
            print(
                f"{Colors.BOLD}Packages Scanned:{Colors.ENDC} {audit.total_packages_scanned}"
            )

            # Vulnerability summary
            total_vulns = (
                audit.critical_count
                + audit.high_count
                + audit.medium_count
                + audit.low_count
            )
            if total_vulns > 0:
                print(
                    f"\n{Colors.BOLD}Vulnerabilities Found ({total_vulns}):{Colors.ENDC}"
                )
                if audit.critical_count > 0:
                    print(
                        f"  • {Colors.RED}Critical: {audit.critical_count}{Colors.ENDC}"
                    )
                if audit.high_count > 0:
                    print(f"  • {Colors.YELLOW}High: {audit.high_count}{Colors.ENDC}")
                if audit.medium_count > 0:
                    print(f"  • {Colors.BLUE}Medium: {audit.medium_count}{Colors.ENDC}")
                if audit.low_count > 0:
                    print(f"  • {Colors.GREEN}Low: {audit.low_count}{Colors.ENDC}")

                # Show top vulnerabilities
                if audit.vulnerabilities_found:
                    print(f"\n{Colors.BOLD}Top Issues:{Colors.ENDC}")
                    for vuln in audit.vulnerabilities_found[:5]:
                        print(
                            f"  • {vuln.cve_id}: {vuln.package} ({format_severity(vuln.severity)})"
                        )
                        print(f"    {vuln.description}")
            else:
                print(f"\n{Colors.GREEN}✅ No vulnerabilities found!{Colors.ENDC}")

            # Configuration status
            print(f"\n{Colors.BOLD}Security Configuration:{Colors.ENDC}")
            configs = [
                ("Firewall", audit.firewall_enabled),
                ("Auto-Updates", audit.auto_updates_enabled),
                ("Secure Boot", audit.secure_boot),
                ("Disk Encryption", audit.encrypted_root),
            ]
            for name, enabled in configs:
                status = (
                    f"{Colors.GREEN}✅{Colors.ENDC}"
                    if enabled
                    else f"{Colors.RED}❌{Colors.ENDC}"
                )
                print(f"  • {name}: {status}")

            # Immediate actions
            if audit.immediate_actions:
                print(
                    f"\n{Colors.RED}{Colors.BOLD}Immediate Actions Required:{Colors.ENDC}"
                )
                for action in audit.immediate_actions[:5]:
                    print(f"  ! {action}")

            # Configuration fixes
            if audit.configuration_fixes:
                print(f"\n{Colors.YELLOW}Recommended Configuration:{Colors.ENDC}")
                print("```nix")
                for fix in audit.configuration_fixes[:5]:
                    print(f"  {fix}")
                print("```")

        return 0 if audit.security_score >= 60 else 1

    def security_check(self, package: str) -> int:
        """Check security of specific package"""
        if not self.json_output:
            print(f"{Colors.HEADER}🔍 Checking Security of '{package}'...{Colors.ENDC}")

        vulnerabilities = self.security.check_package_security(package)

        if self.json_output:
            print(
                json.dumps(
                    [
                        {
                            "cve_id": v.cve_id,
                            "severity": v.severity.value,
                            "description": v.description,
                            "fixed_version": v.fixed_version,
                            "patch_available": v.patch_available,
                        }
                        for v in vulnerabilities
                    ]
                )
            )
        else:
            if vulnerabilities:
                print(
                    f"\n{Colors.RED}⚠️ {len(vulnerabilities)} vulnerabilities found:{Colors.ENDC}"
                )
                for vuln in vulnerabilities:
                    print(f"\n  {vuln.cve_id} ({format_severity(vuln.severity)})")
                    print(f"    {vuln.description}")
                    if vuln.fixed_version:
                        print(
                            f"    {Colors.GREEN}Fix: Update to {vuln.fixed_version}{Colors.ENDC}"
                        )
                    elif vuln.workaround:
                        print(
                            f"    {Colors.YELLOW}Workaround: {vuln.workaround}{Colors.ENDC}"
                        )
            else:
                print(f"\n{Colors.GREEN}✅ No known vulnerabilities{Colors.ENDC}")

        return 0 if not vulnerabilities else 1

    def security_harden(self) -> int:
        """Get hardening recommendations"""
        if not self.json_output:
            print(
                f"{Colors.HEADER}🛡️ Generating Hardening Configuration...{Colors.ENDC}"
            )

        hardening = self.security.suggest_hardening()

        if self.json_output:
            print(json.dumps(hardening))
        else:
            print(f"\n{Colors.BOLD}System Hardening Configuration:{Colors.ENDC}")
            print("\n```nix")
            print(hardening["configuration"])
            print("```")

            if hardening.get("impact"):
                print(f"\n{Colors.BOLD}Impact Assessment:{Colors.ENDC}")
                for aspect, impact in hardening["impact"].items():
                    color = (
                        Colors.GREEN
                        if impact == "minimal"
                        else Colors.YELLOW
                        if impact == "moderate"
                        else Colors.RED
                    )
                    print(f"  • {aspect.capitalize()}: {color}{impact}{Colors.ENDC}")

            if hardening.get("priority"):
                print(f"\n{Colors.BOLD}Priority Actions:{Colors.ENDC}")
                for i, action in enumerate(hardening["priority"][:5], 1):
                    print(f"  {i}. {action}")

        return 0

    def security_updates(self) -> int:
        """Check for security updates"""
        if not self.json_output:
            print(f"{Colors.HEADER}🔄 Checking for Security Updates...{Colors.ENDC}")

        updates = self.security.track_security_updates()

        if self.json_output:
            print(json.dumps(updates))
        else:
            if updates:
                print(
                    f"\n{Colors.YELLOW}⚠️ {len(updates)} security updates available:{Colors.ENDC}"
                )
                for update in updates[:10]:
                    print(
                        f"  • {update.get('package', 'Unknown')}: {update.get('version', 'N/A')}"
                    )

                print(f"\n{Colors.GREEN}Apply updates:{Colors.ENDC}")
                print("  sudo nixos-rebuild switch --upgrade")
            else:
                print(f"\n{Colors.GREEN}✅ System appears up to date{Colors.ENDC}")

        return 0

    def security_help(self) -> int:
        """Show security command help"""
        print(f"{Colors.HEADER}🔐 Security Audit Commands{Colors.ENDC}")
        print("\nUsage: luminous-nix security <command> [options]")
        print("\nCommands:")
        print("  audit [--deep]         - Run security audit")
        print("  check <package>        - Check package for CVEs")
        print("  harden                 - Get hardening configuration")
        print("  updates                - Check for security updates")
        print("  help                   - Show this help")
        print("\nExamples:")
        print("  luminous-nix security audit")
        print("  luminous-nix security check openssl")
        print("  luminous-nix security harden")
        return 0


def main():
    """Main entry point for advanced features CLI"""
    cli = AdvancedFeaturesCLI()

    # Parse command line arguments
    args = sys.argv[1:]

    if not args or args[0] == "help":
        print(f"{Colors.HEADER}🚀 Luminous Nix Advanced Features (Phase 1){Colors.ENDC}")
        print("\nAvailable commands:")
        print("  rollback   - Intelligent rollback analysis")
        print("  storage    - Storage optimization")
        print("  security   - Security auditing")
        print("\nUse 'luminous-nix <command> help' for command-specific help")
        return 0

    command = args[0]
    command_args = args[1:] if len(args) > 1 else []

    try:
        if command == "rollback":
            return cli.handle_rollback(command_args)
        elif command == "storage":
            return cli.handle_storage(command_args)
        elif command == "security":
            return cli.handle_security(command_args)
        else:
            print(f"{Colors.RED}Unknown command: {command}{Colors.ENDC}")
            print("Use 'luminous-nix help' for available commands")
            return 1
    except Exception as e:
        if cli.verbose:
            import traceback

            traceback.print_exc()
        else:
            print(f"{Colors.RED}Error: {e}{Colors.ENDC}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
