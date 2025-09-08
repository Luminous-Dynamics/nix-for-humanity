#!/usr/bin/env python3
"""
AI-Powered Configuration Optimizer - Automatic configuration improvements

This module uses AI to analyze and optimize NixOS configurations:
- Performance optimization
- Security hardening
- Resource efficiency
- Dependency cleanup
- Best practice enforcement
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

# Import our AI capabilities
from ..ollama_integration import ollama_client
# HRM is optional - fallback to basic reasoning if not available
try:
    from ..hrm_reasoner import HRMReasoner as HierarchicalReasoningMachine
except ImportError:
    HierarchicalReasoningMachine = None
    
try:
    from ...poml.processors.poml_processor_v2 import POMLProcessor
except ImportError:
    POMLProcessor = None


class OptimizationType(Enum):
    """Types of optimizations"""
    PERFORMANCE = "performance"
    SECURITY = "security"
    RESOURCES = "resources"
    DEPENDENCIES = "dependencies"
    BEST_PRACTICES = "best_practices"
    BOOT_TIME = "boot_time"
    NETWORK = "network"
    STORAGE = "storage"


class OptimizationLevel(Enum):
    """Optimization aggressiveness levels"""
    SAFE = "safe"           # Only guaranteed safe changes
    BALANCED = "balanced"   # Reasonable risk/reward
    AGGRESSIVE = "aggressive"  # Maximum optimization
    CUSTOM = "custom"       # User-defined rules


@dataclass
class OptimizationRule:
    """A specific optimization rule"""
    id: str
    type: OptimizationType
    name: str
    description: str
    pattern: str  # Regex pattern to match
    replacement: str  # Replacement pattern
    impact: str  # low, medium, high
    risk: str    # low, medium, high
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    def applies_to(self, config: str) -> bool:
        """Check if this rule applies to the config"""
        if self.conditions:
            # Check conditions (simplified)
            for key, value in self.conditions.items():
                if key == "has_package" and value not in config:
                    return False
                elif key == "missing_package" and value in config:
                    return False
        
        return bool(re.search(self.pattern, config))


@dataclass
class OptimizationSuggestion:
    """A suggested optimization"""
    rule: OptimizationRule
    location: str  # Where in the config
    current_value: str
    suggested_value: str
    explanation: str
    confidence: float
    estimated_impact: Dict[str, Any]


@dataclass
class OptimizationPlan:
    """Complete optimization plan"""
    suggestions: List[OptimizationSuggestion]
    total_impact: Dict[str, Any]
    risk_assessment: str
    estimated_improvement: Dict[str, float]
    ai_analysis: Optional[str] = None
    
    def filter_by_type(self, opt_type: OptimizationType) -> List[OptimizationSuggestion]:
        """Get suggestions of a specific type"""
        return [s for s in self.suggestions if s.rule.type == opt_type]
    
    def filter_by_risk(self, max_risk: str) -> List[OptimizationSuggestion]:
        """Get suggestions below a risk threshold"""
        risk_levels = {"low": 1, "medium": 2, "high": 3}
        max_level = risk_levels.get(max_risk, 3)
        
        return [s for s in self.suggestions 
                if risk_levels.get(s.rule.risk, 3) <= max_level]


class ConfigOptimizer:
    """
    AI-Powered Configuration Optimizer
    
    Features:
    - Automatic detection of optimization opportunities
    - AI-driven suggestions for improvements
    - Risk assessment for each change
    - Performance impact estimation
    - Best practice enforcement
    """
    
    def __init__(self):
        """Initialize the optimizer"""
        self.console = Console()
        self.hrm = HierarchicalReasoningMachine() if HierarchicalReasoningMachine else None
        self.poml_processor = POMLProcessor() if POMLProcessor else None
        
        # Load optimization rules
        self.rules = self._load_optimization_rules()
        
        # Cache for analysis results
        self._analysis_cache: Dict[str, Any] = {}
        
        # Performance baselines
        self.baselines = self._load_baselines()
    
    def _load_optimization_rules(self) -> List[OptimizationRule]:
        """Load optimization rules"""
        rules = []
        
        # Performance optimizations
        rules.append(OptimizationRule(
            id="perf_001",
            type=OptimizationType.PERFORMANCE,
            name="Enable CPU microcode updates",
            description="Ensure CPU microcode is updated for performance and security",
            pattern=r"# hardware\.cpu\..*microcode",
            replacement="hardware.cpu.intel.updateMicrocode = true;",
            impact="medium",
            risk="low"
        ))
        
        rules.append(OptimizationRule(
            id="perf_002",
            type=OptimizationType.PERFORMANCE,
            name="Enable kernel huge pages",
            description="Enable transparent huge pages for better memory performance",
            pattern=r"^((?!boot\.kernel\.sysctl.*transparent_hugepage).)*$",
            replacement='boot.kernel.sysctl."vm.transparent_hugepage" = "always";',
            impact="medium",
            risk="low"
        ))
        
        rules.append(OptimizationRule(
            id="perf_003",
            type=OptimizationType.BOOT_TIME,
            name="Enable systemd-boot",
            description="Use systemd-boot for faster boot times",
            pattern=r"boot\.loader\.grub\.enable\s*=\s*true",
            replacement="boot.loader.systemd-boot.enable = true;",
            impact="high",
            risk="medium",
            conditions={"not_efi": False}
        ))
        
        # Security optimizations
        rules.append(OptimizationRule(
            id="sec_001",
            type=OptimizationType.SECURITY,
            name="Enable firewall",
            description="Enable the NixOS firewall for better security",
            pattern=r"^((?!networking\.firewall\.enable).)*$",
            replacement="networking.firewall.enable = true;",
            impact="high",
            risk="low"
        ))
        
        rules.append(OptimizationRule(
            id="sec_002",
            type=OptimizationType.SECURITY,
            name="Disable root SSH",
            description="Disable root login via SSH",
            pattern=r"services\.openssh\.permitRootLogin\s*=\s*\"yes\"",
            replacement='services.openssh.permitRootLogin = "no";',
            impact="high",
            risk="low"
        ))
        
        rules.append(OptimizationRule(
            id="sec_003",
            type=OptimizationType.SECURITY,
            name="Enable fail2ban",
            description="Enable fail2ban to prevent brute force attacks",
            pattern=r"^((?!services\.fail2ban\.enable).)*$",
            replacement="services.fail2ban.enable = true;",
            impact="high",
            risk="low",
            conditions={"has_package": "openssh"}
        ))
        
        # Resource optimizations
        rules.append(OptimizationRule(
            id="res_001",
            type=OptimizationType.RESOURCES,
            name="Enable zram swap",
            description="Use compressed RAM for swap to improve performance",
            pattern=r"^((?!zramSwap\.enable).)*$",
            replacement="zramSwap.enable = true;",
            impact="medium",
            risk="low"
        ))
        
        rules.append(OptimizationRule(
            id="res_002",
            type=OptimizationType.RESOURCES,
            name="Optimize journald",
            description="Limit systemd journal size to save disk space",
            pattern=r"^((?!services\.journald\.extraConfig).)*$",
            replacement='services.journald.extraConfig = "SystemMaxUse=100M";',
            impact="low",
            risk="low"
        ))
        
        # Dependency optimizations
        rules.append(OptimizationRule(
            id="dep_001",
            type=OptimizationType.DEPENDENCIES,
            name="Remove duplicate packages",
            description="Remove packages that are already dependencies of others",
            pattern=r"(\w+).*\n.*\1",  # Simplified duplicate detection
            replacement="",  # Will be handled specially
            impact="low",
            risk="low"
        ))
        
        rules.append(OptimizationRule(
            id="dep_002",
            type=OptimizationType.DEPENDENCIES,
            name="Use package groups",
            description="Replace individual packages with meta packages",
            pattern=r"firefox\s+thunderbird",
            replacement="firefox thunderbird",  # Example
            impact="low",
            risk="low"
        ))
        
        # Best practices
        rules.append(OptimizationRule(
            id="bp_001",
            type=OptimizationType.BEST_PRACTICES,
            name="Use attribute sets",
            description="Use attribute sets for better organization",
            pattern=r"services\.(\w+)\.enable = true;\s*services\.\1\.",
            replacement="services.\\1 = { enable = true; ",
            impact="low",
            risk="low"
        ))
        
        rules.append(OptimizationRule(
            id="bp_002",
            type=OptimizationType.BEST_PRACTICES,
            name="Pin nixpkgs version",
            description="Pin nixpkgs to a specific version for reproducibility",
            pattern=r"^((?!nixpkgs\.url).)*$",
            replacement='# Consider pinning: nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";',
            impact="medium",
            risk="low"
        ))
        
        # Network optimizations
        rules.append(OptimizationRule(
            id="net_001",
            type=OptimizationType.NETWORK,
            name="Enable BBR congestion control",
            description="Use BBR for better network performance",
            pattern=r"^((?!boot\.kernel\.sysctl.*tcp_congestion_control).)*$",
            replacement='boot.kernel.sysctl."net.ipv4.tcp_congestion_control" = "bbr";',
            impact="medium",
            risk="low"
        ))
        
        # Storage optimizations  
        rules.append(OptimizationRule(
            id="stor_001",
            type=OptimizationType.STORAGE,
            name="Enable periodic trim",
            description="Enable periodic SSD trim for better performance",
            pattern=r"^((?!services\.fstrim\.enable).)*$",
            replacement="services.fstrim.enable = true;",
            impact="medium",
            risk="low",
            conditions={"has_ssd": True}
        ))
        
        return rules
    
    def _load_baselines(self) -> Dict[str, Any]:
        """Load performance baselines"""
        return {
            "boot_time": 30.0,  # seconds
            "memory_usage": 2048,  # MB
            "disk_usage": 10240,  # MB
            "service_count": 50,
            "package_count": 500
        }
    
    def analyze_configuration(self, config_path: str = "/etc/nixos/configuration.nix",
                             level: OptimizationLevel = OptimizationLevel.BALANCED) -> OptimizationPlan:
        """Analyze a configuration and suggest optimizations"""
        
        # Read configuration
        try:
            with open(config_path, 'r') as f:
                config_content = f.read()
        except Exception as e:
            self.console.print(f"[red]Error reading config: {e}[/red]")
            return OptimizationPlan([], {}, "error", {})
        
        suggestions = []
        
        # Apply rules based on level
        applicable_rules = self._filter_rules_by_level(level)
        
        for rule in applicable_rules:
            if rule.applies_to(config_content):
                # Find specific locations
                matches = re.finditer(rule.pattern, config_content)
                
                for match in matches:
                    suggestion = self._create_suggestion(rule, match, config_content)
                    if suggestion:
                        suggestions.append(suggestion)
        
        # Get AI analysis if available
        ai_analysis = None
        if ollama_client and ollama_client.is_available():
            ai_analysis = self._get_ai_analysis(config_content, suggestions)
        
        # Calculate total impact
        total_impact = self._calculate_total_impact(suggestions)
        
        # Risk assessment
        risk_assessment = self._assess_risk(suggestions)
        
        # Estimate improvements
        estimated_improvement = self._estimate_improvements(suggestions)
        
        return OptimizationPlan(
            suggestions=suggestions,
            total_impact=total_impact,
            risk_assessment=risk_assessment,
            estimated_improvement=estimated_improvement,
            ai_analysis=ai_analysis
        )
    
    def _filter_rules_by_level(self, level: OptimizationLevel) -> List[OptimizationRule]:
        """Filter rules based on optimization level"""
        
        if level == OptimizationLevel.SAFE:
            return [r for r in self.rules if r.risk == "low"]
        elif level == OptimizationLevel.BALANCED:
            return [r for r in self.rules if r.risk in ["low", "medium"]]
        elif level == OptimizationLevel.AGGRESSIVE:
            return self.rules
        else:
            return self.rules  # Custom uses all rules
    
    def _create_suggestion(self, rule: OptimizationRule, match, 
                          config: str) -> Optional[OptimizationSuggestion]:
        """Create an optimization suggestion"""
        
        try:
            current_value = match.group(0)
            
            # Special handling for certain rules
            if rule.id == "dep_001":
                # Duplicate detection needs special logic
                return None
            
            suggested_value = re.sub(rule.pattern, rule.replacement, current_value)
            
            # Generate explanation
            explanation = self._generate_explanation(rule, current_value, suggested_value)
            
            # Calculate confidence
            confidence = self._calculate_confidence(rule, config)
            
            # Estimate impact
            estimated_impact = self._estimate_impact(rule)
            
            return OptimizationSuggestion(
                rule=rule,
                location=f"Line {config[:match.start()].count(chr(10)) + 1}",
                current_value=current_value[:100],  # Truncate for display
                suggested_value=suggested_value[:100],
                explanation=explanation,
                confidence=confidence,
                estimated_impact=estimated_impact
            )
            
        except Exception:
            return None
    
    def _generate_explanation(self, rule: OptimizationRule, 
                             current: str, suggested: str) -> str:
        """Generate explanation for a suggestion"""
        
        base_explanation = rule.description
        
        # Add specific details
        if rule.type == OptimizationType.PERFORMANCE:
            base_explanation += " This can improve system performance."
        elif rule.type == OptimizationType.SECURITY:
            base_explanation += " This enhances system security."
        elif rule.type == OptimizationType.RESOURCES:
            base_explanation += " This optimizes resource usage."
        
        return base_explanation
    
    def _calculate_confidence(self, rule: OptimizationRule, config: str) -> float:
        """Calculate confidence in a suggestion"""
        
        confidence = 0.7  # Base confidence
        
        # Adjust based on risk
        if rule.risk == "low":
            confidence += 0.2
        elif rule.risk == "high":
            confidence -= 0.2
        
        # Adjust based on conditions
        if rule.conditions:
            conditions_met = sum(1 for k, v in rule.conditions.items() 
                               if self._check_condition(k, v, config))
            confidence += (conditions_met / len(rule.conditions)) * 0.1
        
        return min(max(confidence, 0.0), 1.0)
    
    def _check_condition(self, key: str, value: Any, config: str) -> bool:
        """Check if a condition is met"""
        
        if key == "has_package":
            return value in config
        elif key == "missing_package":
            return value not in config
        elif key == "has_ssd":
            # Check if system has SSD (simplified)
            return True  # Assume SSD for now
        elif key == "not_efi":
            # Check if system uses EFI
            return Path("/sys/firmware/efi").exists()
        
        return False
    
    def _estimate_impact(self, rule: OptimizationRule) -> Dict[str, Any]:
        """Estimate impact of applying a rule"""
        
        impact = {
            "performance": 0,
            "security": 0,
            "resources": 0,
            "maintainability": 0
        }
        
        # Map rule type to impact
        if rule.type == OptimizationType.PERFORMANCE:
            impact["performance"] = {"low": 5, "medium": 15, "high": 30}.get(rule.impact, 0)
        elif rule.type == OptimizationType.SECURITY:
            impact["security"] = {"low": 10, "medium": 25, "high": 50}.get(rule.impact, 0)
        elif rule.type == OptimizationType.RESOURCES:
            impact["resources"] = {"low": 5, "medium": 10, "high": 20}.get(rule.impact, 0)
        elif rule.type == OptimizationType.BEST_PRACTICES:
            impact["maintainability"] = {"low": 5, "medium": 10, "high": 15}.get(rule.impact, 0)
        
        return impact
    
    def _calculate_total_impact(self, suggestions: List[OptimizationSuggestion]) -> Dict[str, Any]:
        """Calculate total impact of all suggestions"""
        
        total = {
            "performance": 0,
            "security": 0,
            "resources": 0,
            "maintainability": 0,
            "changes": len(suggestions)
        }
        
        for suggestion in suggestions:
            for key, value in suggestion.estimated_impact.items():
                if key in total:
                    total[key] += value
        
        return total
    
    def _assess_risk(self, suggestions: List[OptimizationSuggestion]) -> str:
        """Assess overall risk of applying suggestions"""
        
        if not suggestions:
            return "none"
        
        risk_scores = {"low": 1, "medium": 2, "high": 3}
        
        total_risk = sum(risk_scores.get(s.rule.risk, 2) for s in suggestions)
        avg_risk = total_risk / len(suggestions)
        
        if avg_risk < 1.5:
            return "low"
        elif avg_risk < 2.5:
            return "medium"
        else:
            return "high"
    
    def _estimate_improvements(self, suggestions: List[OptimizationSuggestion]) -> Dict[str, float]:
        """Estimate percentage improvements"""
        
        improvements = {}
        
        # Count suggestions by type
        type_counts = {}
        for s in suggestions:
            type_counts[s.rule.type] = type_counts.get(s.rule.type, 0) + 1
        
        # Estimate improvements
        if OptimizationType.PERFORMANCE in type_counts:
            improvements["boot_time"] = min(type_counts[OptimizationType.PERFORMANCE] * 5, 30)
        
        if OptimizationType.RESOURCES in type_counts:
            improvements["memory_usage"] = min(type_counts[OptimizationType.RESOURCES] * 3, 20)
        
        if OptimizationType.SECURITY in type_counts:
            improvements["security_score"] = min(type_counts[OptimizationType.SECURITY] * 10, 50)
        
        return improvements
    
    def _get_ai_analysis(self, config: str, suggestions: List[OptimizationSuggestion]) -> str:
        """Get AI analysis of the configuration"""
        
        # Use POML template for analysis
        template_path = Path(__file__).parent.parent.parent / "poml/templates/config_optimizer.poml"
        
        if template_path.exists():
            try:
                # Process POML template
                variables = {
                    "config_snippet": config[:1000],  # First 1000 chars
                    "suggestion_count": len(suggestions),
                    "optimization_types": list(set(s.rule.type.value for s in suggestions))
                }
                
                prompt = self.poml_processor.process_template(str(template_path), variables)
                
                # Get AI response
                response = ollama_client.generate(prompt, model="mistral")
                return response.get("response", "")
                
            except Exception:
                pass
        
        # Fallback to HRM if available
        if self.hrm:
            try:
                analysis = self.hrm.reason_about_problem(
                    f"Analyze this NixOS configuration and suggest improvements: {config[:500]}",
                    context={"suggestions": len(suggestions)}
                )
                
                return analysis.conclusion
                
            except Exception:
                return ""
        
        return ""
    
    def apply_optimizations(self, config_path: str, plan: OptimizationPlan,
                           selections: Optional[List[int]] = None,
                           backup: bool = True) -> Dict[str, Any]:
        """Apply selected optimizations to configuration"""
        
        # Read current config
        try:
            with open(config_path, 'r') as f:
                config_content = f.read()
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        # Backup if requested
        if backup:
            backup_path = f"{config_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                with open(backup_path, 'w') as f:
                    f.write(config_content)
            except Exception as e:
                return {"success": False, "error": f"Backup failed: {e}"}
        
        # Select suggestions to apply
        if selections:
            suggestions_to_apply = [plan.suggestions[i] for i in selections 
                                   if i < len(plan.suggestions)]
        else:
            # Apply all low-risk suggestions by default
            suggestions_to_apply = plan.filter_by_risk("low")
        
        # Apply suggestions
        modified_config = config_content
        applied = []
        
        for suggestion in suggestions_to_apply:
            try:
                # Apply the replacement
                modified_config = re.sub(
                    suggestion.rule.pattern,
                    suggestion.rule.replacement,
                    modified_config,
                    count=1
                )
                applied.append(suggestion.rule.name)
            except Exception:
                continue
        
        # Write modified config
        try:
            with open(config_path, 'w') as f:
                f.write(modified_config)
        except Exception as e:
            return {"success": False, "error": f"Write failed: {e}"}
        
        return {
            "success": True,
            "applied": applied,
            "backup": backup_path if backup else None
        }
    
    def benchmark_configuration(self, config_path: str) -> Dict[str, Any]:
        """Benchmark current configuration"""
        
        benchmarks = {}
        
        try:
            # Boot time
            result = subprocess.run(
                ["systemd-analyze", "time"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                # Parse boot time from output
                import re
                match = re.search(r"= ([\d.]+)s", result.stdout)
                if match:
                    benchmarks["boot_time"] = float(match.group(1))
            
            # Memory usage
            with open("/proc/meminfo") as f:
                meminfo = f.read()
                total = int(re.search(r"MemTotal:\s+(\d+)", meminfo).group(1)) / 1024
                available = int(re.search(r"MemAvailable:\s+(\d+)", meminfo).group(1)) / 1024
                benchmarks["memory_used_mb"] = total - available
            
            # Package count
            result = subprocess.run(
                ["nix-env", "-q", "--installed"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                benchmarks["package_count"] = len(result.stdout.strip().split('\n'))
            
            # Service count
            result = subprocess.run(
                ["systemctl", "list-units", "--state=running", "--no-legend"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                benchmarks["service_count"] = len(result.stdout.strip().split('\n'))
            
        except Exception:
            pass
        
        return benchmarks
    
    def generate_report(self, plan: OptimizationPlan) -> Panel:
        """Generate optimization report"""
        
        # Create summary table
        summary_table = Table(title="Optimization Summary", show_header=True)
        summary_table.add_column("Category", style="cyan")
        summary_table.add_column("Count", justify="right")
        summary_table.add_column("Impact", style="yellow")
        
        # Count by type
        by_type = {}
        for suggestion in plan.suggestions:
            opt_type = suggestion.rule.type
            if opt_type not in by_type:
                by_type[opt_type] = []
            by_type[opt_type].append(suggestion)
        
        for opt_type, suggestions in by_type.items():
            impact = sum(s.estimated_impact.get(opt_type.value, 0) for s in suggestions)
            summary_table.add_row(
                opt_type.value.replace("_", " ").title(),
                str(len(suggestions)),
                f"+{impact}%" if impact > 0 else "—"
            )
        
        # Risk assessment
        risk_color = {
            "low": "green",
            "medium": "yellow",
            "high": "red"
        }.get(plan.risk_assessment, "white")
        
        # Improvement estimates
        improvement_text = []
        for metric, value in plan.estimated_improvement.items():
            improvement_text.append(f"  • {metric.replace('_', ' ').title()}: {value:.0f}% improvement")
        
        # Build report
        report_content = [
            summary_table,
            "",
            f"[bold]Overall Risk:[/bold] [{risk_color}]{plan.risk_assessment.upper()}[/{risk_color}]",
            "",
            "[bold]Expected Improvements:[/bold]",
            "\n".join(improvement_text) if improvement_text else "  No significant improvements estimated"
        ]
        
        if plan.ai_analysis:
            report_content.extend([
                "",
                "[bold]AI Analysis:[/bold]",
                plan.ai_analysis[:500]  # Truncate long analysis
            ])
        
        return Panel(
            "\n".join(str(item) for item in report_content),
            title="[cyan]Configuration Optimization Report[/cyan]",
            border_style="blue"
        )