#!/usr/bin/env python3
"""
Performance Profiler - Identify and fix performance bottlenecks
Intelligent performance analysis and optimization recommendations
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PerformanceIssue(Enum):
    """Types of performance issues"""

    SLOW_BOOT = "slow_boot"
    HIGH_MEMORY = "high_memory"
    SLOW_REBUILD = "slow_rebuild"
    CACHE_MISS = "cache_miss"
    NETWORK_LAG = "network_lag"
    DISK_IO = "disk_io"
    CPU_BOUND = "cpu_bound"
    DERIVATION_SIZE = "derivation_size"


@dataclass
class PerformanceMetrics:
    """System performance metrics"""

    boot_time_seconds: float
    rebuild_time_seconds: float
    memory_usage_gb: float
    disk_usage_gb: float
    cpu_usage_percent: float

    cache_hit_rate: float
    derivation_count: int
    closure_size_gb: float

    network_downloads_mb: float
    compile_time_seconds: float


@dataclass
class PerformanceAnalysis:
    """Performance analysis results"""

    metrics: PerformanceMetrics

    # Issues found
    issues: List[Tuple[PerformanceIssue, float]]  # (issue, severity 0-1)
    bottlenecks: List[str]

    # Optimization recommendations
    quick_wins: List[Dict[str, Any]]  # Easy optimizations
    major_improvements: List[Dict[str, Any]]  # Significant but complex
    configuration_changes: List[str]  # Nix config changes

    # Performance predictions
    potential_speedup: float  # Percentage improvement possible
    estimated_boot_reduction: float  # Seconds
    estimated_memory_savings: float  # GB

    confidence: float


class PerformanceProfiler:
    """
    Intelligent performance profiling using HRM
    Identifies bottlenecks and suggests optimizations
    """

    def __init__(self):
        # Performance thresholds
        self.thresholds = {
            "boot_time": 30.0,  # seconds
            "rebuild_time": 300.0,  # 5 minutes
            "memory_usage": 4.0,  # GB
            "cache_hit_rate": 0.7,  # 70%
            "cpu_usage": 80.0,  # percent
        }

        # Optimization strategies
        self.optimizations = {
            PerformanceIssue.SLOW_BOOT: self._optimize_boot,
            PerformanceIssue.HIGH_MEMORY: self._optimize_memory,
            PerformanceIssue.SLOW_REBUILD: self._optimize_rebuild,
            PerformanceIssue.CACHE_MISS: self._optimize_cache,
            PerformanceIssue.DISK_IO: self._optimize_disk,
        }

    def profile_system(self) -> PerformanceAnalysis:
        """
        Profile system performance and identify issues

        Returns:
            PerformanceAnalysis with metrics and recommendations
        """
        try:
            # Collect metrics
            metrics = self._collect_metrics()

            # Identify issues
            issues = self._identify_issues(metrics)

            # Find bottlenecks
            bottlenecks = self._find_bottlenecks(metrics, issues)

            # Generate optimizations
            quick_wins = self._generate_quick_wins(issues)
            major_improvements = self._generate_major_improvements(issues, metrics)
            config_changes = self._generate_config_changes(issues, metrics)

            # Calculate potential improvements
            speedup = self._calculate_speedup_potential(
                issues, quick_wins, major_improvements
            )
            boot_reduction = self._estimate_boot_reduction(metrics, quick_wins)
            memory_savings = self._estimate_memory_savings(metrics, quick_wins)

            return PerformanceAnalysis(
                metrics=metrics,
                issues=issues,
                bottlenecks=bottlenecks,
                quick_wins=quick_wins,
                major_improvements=major_improvements,
                configuration_changes=config_changes,
                potential_speedup=speedup,
                estimated_boot_reduction=boot_reduction,
                estimated_memory_savings=memory_savings,
                confidence=0.85,
            )

        except Exception as e:
            logger.error(f"Performance profiling failed: {e}")
            return self._create_fallback_analysis(str(e))

    def optimize_boot_time(self) -> Dict[str, Any]:
        """Specifically optimize boot time"""
        try:
            metrics = self._collect_metrics()

            optimizations = {
                "current_boot_time": metrics.boot_time_seconds,
                "optimizations": [],
            }

            # Check for common boot issues
            if metrics.boot_time_seconds > 30:
                optimizations["optimizations"].append(
                    {
                        "action": "Enable systemd-boot",
                        "config": "boot.loader.systemd-boot.enable = true;",
                        "impact": "Save 5-10 seconds",
                        "difficulty": "easy",
                    }
                )

            # Check for unnecessary services
            unnecessary_services = self._detect_unnecessary_services()
            if unnecessary_services:
                optimizations["optimizations"].append(
                    {
                        "action": "Disable unnecessary services",
                        "services": unnecessary_services,
                        "impact": f"Save {len(unnecessary_services) * 2} seconds",
                        "difficulty": "easy",
                    }
                )

            # Check kernel modules
            unused_modules = self._detect_unused_kernel_modules()
            if unused_modules:
                optimizations["optimizations"].append(
                    {
                        "action": "Blacklist unused kernel modules",
                        "modules": unused_modules[:5],
                        "config": f"boot.blacklistedKernelModules = {unused_modules[:5]};",
                        "impact": "Save 3-5 seconds",
                        "difficulty": "moderate",
                    }
                )

            # Parallel boot optimization
            optimizations["optimizations"].append(
                {
                    "action": "Enable parallel service startup",
                    "config": 'systemd.services.<service>.wantedBy = [ "multi-user.target" ];',
                    "impact": "Save 5-15 seconds",
                    "difficulty": "moderate",
                }
            )

            optimizations["estimated_final_boot_time"] = max(
                10, metrics.boot_time_seconds - 20
            )

            return optimizations

        except Exception as e:
            logger.error(f"Boot optimization failed: {e}")
            return {"error": str(e)}

    def optimize_rebuild_time(self) -> Dict[str, Any]:
        """Optimize NixOS rebuild time"""
        try:
            metrics = self._collect_metrics()

            optimizations = {
                "current_rebuild_time": metrics.rebuild_time_seconds,
                "optimizations": [],
            }

            # Enable binary caches
            optimizations["optimizations"].append(
                {
                    "action": "Add binary caches",
                    "config": """nix.settings = {
  substituters = [
    "https://cache.nixos.org"
    "https://nix-community.cachix.org"
  ];
  trusted-public-keys = [
    "cache.nixos.org-1:..."
    "nix-community.cachix.org-1:..."
  ];
};""",
                    "impact": "Save 50-80% rebuild time",
                    "difficulty": "easy",
                }
            )

            # Optimize evaluation
            if metrics.derivation_count > 1000:
                optimizations["optimizations"].append(
                    {
                        "action": "Reduce derivation count",
                        "suggestion": "Use buildEnv to combine packages",
                        "impact": "Save 10-20% evaluation time",
                        "difficulty": "moderate",
                    }
                )

            # Distributed builds
            optimizations["optimizations"].append(
                {
                    "action": "Enable distributed builds",
                    "config": "nix.distributedBuilds = true;",
                    "impact": "Parallel builds on multiple machines",
                    "difficulty": "complex",
                }
            )

            # Incremental builds
            optimizations["optimizations"].append(
                {
                    "action": "Use ccache for C/C++ builds",
                    "config": "programs.ccache.enable = true;",
                    "impact": "Save 30-50% on repeated builds",
                    "difficulty": "easy",
                }
            )

            return optimizations

        except Exception as e:
            logger.error(f"Rebuild optimization failed: {e}")
            return {"error": str(e)}

    def analyze_resource_usage(self) -> Dict[str, Any]:
        """Analyze system resource usage"""
        try:
            metrics = self._collect_metrics()

            analysis = {
                "memory": {
                    "current_usage_gb": metrics.memory_usage_gb,
                    "status": "high" if metrics.memory_usage_gb > 4.0 else "normal",
                    "top_consumers": self._get_top_memory_consumers(),
                },
                "cpu": {
                    "average_usage": metrics.cpu_usage_percent,
                    "status": "high" if metrics.cpu_usage_percent > 80 else "normal",
                    "top_processes": self._get_top_cpu_processes(),
                },
                "disk": {
                    "usage_gb": metrics.disk_usage_gb,
                    "closure_size_gb": metrics.closure_size_gb,
                    "largest_packages": self._get_largest_packages(),
                },
                "recommendations": [],
            }

            # Memory recommendations
            if metrics.memory_usage_gb > 4.0:
                analysis["recommendations"].append(
                    {
                        "resource": "memory",
                        "action": "Reduce service memory usage",
                        "config": 'systemd.services.<service>.serviceConfig.MemoryMax = "512M";',
                    }
                )

            # CPU recommendations
            if metrics.cpu_usage_percent > 80:
                analysis["recommendations"].append(
                    {
                        "resource": "cpu",
                        "action": "Enable CPU frequency scaling",
                        "config": 'powerManagement.cpuFreqGovernor = "ondemand";',
                    }
                )

            return analysis

        except Exception as e:
            logger.error(f"Resource analysis failed: {e}")
            return {"error": str(e)}

    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect system performance metrics"""
        # In production, would collect real metrics
        # For demo, return simulated data
        return PerformanceMetrics(
            boot_time_seconds=45.0,
            rebuild_time_seconds=420.0,
            memory_usage_gb=5.2,
            disk_usage_gb=25.0,
            cpu_usage_percent=65.0,
            cache_hit_rate=0.45,
            derivation_count=1500,
            closure_size_gb=8.5,
            network_downloads_mb=250.0,
            compile_time_seconds=180.0,
        )

    def _identify_issues(
        self, metrics: PerformanceMetrics
    ) -> List[Tuple[PerformanceIssue, float]]:
        """Identify performance issues from metrics"""
        issues = []

        # Check boot time
        if metrics.boot_time_seconds > self.thresholds["boot_time"]:
            severity = min(1.0, (metrics.boot_time_seconds - 30) / 30)
            issues.append((PerformanceIssue.SLOW_BOOT, severity))

        # Check rebuild time
        if metrics.rebuild_time_seconds > self.thresholds["rebuild_time"]:
            severity = min(1.0, (metrics.rebuild_time_seconds - 300) / 300)
            issues.append((PerformanceIssue.SLOW_REBUILD, severity))

        # Check memory usage
        if metrics.memory_usage_gb > self.thresholds["memory_usage"]:
            severity = min(1.0, (metrics.memory_usage_gb - 4.0) / 4.0)
            issues.append((PerformanceIssue.HIGH_MEMORY, severity))

        # Check cache hit rate
        if metrics.cache_hit_rate < self.thresholds["cache_hit_rate"]:
            severity = 1.0 - metrics.cache_hit_rate
            issues.append((PerformanceIssue.CACHE_MISS, severity))

        # Check CPU usage
        if metrics.cpu_usage_percent > self.thresholds["cpu_usage"]:
            severity = min(1.0, (metrics.cpu_usage_percent - 80) / 20)
            issues.append((PerformanceIssue.CPU_BOUND, severity))

        # Check derivation size
        if metrics.derivation_count > 1000:
            severity = min(1.0, (metrics.derivation_count - 1000) / 1000)
            issues.append((PerformanceIssue.DERIVATION_SIZE, severity))

        return sorted(issues, key=lambda x: x[1], reverse=True)

    def _find_bottlenecks(
        self, metrics: PerformanceMetrics, issues: List[Tuple[PerformanceIssue, float]]
    ) -> List[str]:
        """Find performance bottlenecks"""
        bottlenecks = []

        if metrics.boot_time_seconds > 30:
            bottlenecks.append("Slow boot time - likely due to unnecessary services")

        if metrics.cache_hit_rate < 0.5:
            bottlenecks.append("Poor cache utilization - rebuilding too much")

        if metrics.memory_usage_gb > 6:
            bottlenecks.append("High memory usage - possible memory leaks")

        if metrics.derivation_count > 2000:
            bottlenecks.append("Too many derivations - configuration too complex")

        return bottlenecks

    def _generate_quick_wins(
        self, issues: List[Tuple[PerformanceIssue, float]]
    ) -> List[Dict[str, Any]]:
        """Generate quick optimization wins"""
        quick_wins = []

        for issue, severity in issues:
            if issue == PerformanceIssue.CACHE_MISS:
                quick_wins.append(
                    {
                        "action": "Enable binary caches",
                        "command": 'nix.settings.substituters = [ "https://cache.nixos.org" ];',
                        "time_to_implement": "5 minutes",
                        "impact": "High",
                        "speedup": "2-5x for rebuilds",
                    }
                )

            elif issue == PerformanceIssue.SLOW_BOOT:
                quick_wins.append(
                    {
                        "action": "Disable plymouth boot splash",
                        "command": "boot.plymouth.enable = false;",
                        "time_to_implement": "2 minutes",
                        "impact": "Medium",
                        "speedup": "Save 3-5 seconds",
                    }
                )

            elif issue == PerformanceIssue.HIGH_MEMORY:
                quick_wins.append(
                    {
                        "action": "Enable zram swap",
                        "command": "zramSwap.enable = true;",
                        "time_to_implement": "2 minutes",
                        "impact": "Medium",
                        "speedup": "Reduce memory pressure",
                    }
                )

        return quick_wins[:3]  # Top 3 quick wins

    def _generate_major_improvements(
        self, issues: List[Tuple[PerformanceIssue, float]], metrics: PerformanceMetrics
    ) -> List[Dict[str, Any]]:
        """Generate major improvement recommendations"""
        improvements = []

        if metrics.rebuild_time_seconds > 600:
            improvements.append(
                {
                    "action": "Set up distributed build cluster",
                    "description": "Use multiple machines for building",
                    "time_to_implement": "2-4 hours",
                    "impact": "Very High",
                    "speedup": "3-10x for large builds",
                    "complexity": "high",
                }
            )

        if metrics.derivation_count > 1500:
            improvements.append(
                {
                    "action": "Modularize configuration",
                    "description": "Split configuration into focused modules",
                    "time_to_implement": "4-8 hours",
                    "impact": "High",
                    "speedup": "20-30% faster evaluation",
                    "complexity": "moderate",
                }
            )

        return improvements

    def _generate_config_changes(
        self, issues: List[Tuple[PerformanceIssue, float]], metrics: PerformanceMetrics
    ) -> List[str]:
        """Generate Nix configuration changes"""
        changes = []

        # Always recommend these optimizations
        changes.append("nix.settings.auto-optimise-store = true;")
        changes.append("nix.gc.automatic = true;")
        changes.append('nix.gc.dates = "weekly";')

        if metrics.cache_hit_rate < 0.7:
            changes.append("nix.settings.keep-outputs = true;")
            changes.append("nix.settings.keep-derivations = true;")

        if metrics.boot_time_seconds > 30:
            changes.append("boot.initrd.verbose = false;")
            changes.append("boot.loader.timeout = 1;")

        return changes

    def _calculate_speedup_potential(
        self,
        issues: List[Tuple[PerformanceIssue, float]],
        quick_wins: List[Dict],
        major_improvements: List[Dict],
    ) -> float:
        """Calculate potential speedup percentage"""
        total_speedup = 0.0

        # Quick wins typically give 10-30% improvement
        total_speedup += len(quick_wins) * 15

        # Major improvements can give 30-70% improvement
        total_speedup += len(major_improvements) * 40

        # Cap at realistic 80% improvement
        return min(80.0, total_speedup)

    def _estimate_boot_reduction(
        self, metrics: PerformanceMetrics, quick_wins: List[Dict]
    ) -> float:
        """Estimate boot time reduction in seconds"""
        reduction = 0.0

        for win in quick_wins:
            if "boot" in win.get("action", "").lower():
                reduction += 5.0  # Each boot optimization saves ~5 seconds

        return min(reduction, metrics.boot_time_seconds * 0.5)  # Max 50% reduction

    def _estimate_memory_savings(
        self, metrics: PerformanceMetrics, quick_wins: List[Dict]
    ) -> float:
        """Estimate memory savings in GB"""
        savings = 0.0

        for win in quick_wins:
            if "memory" in win.get("action", "").lower() or "zram" in win.get(
                "command", ""
            ):
                savings += 1.0  # Each memory optimization saves ~1GB

        return min(savings, metrics.memory_usage_gb * 0.3)  # Max 30% reduction

    def _optimize_boot(self, metrics: PerformanceMetrics) -> List[str]:
        """Optimize boot time"""
        return [
            "boot.loader.timeout = 1;",
            "boot.plymouth.enable = false;",
            "systemd.services.NetworkManager-wait-online.enable = false;",
        ]

    def _optimize_memory(self, metrics: PerformanceMetrics) -> List[str]:
        """Optimize memory usage"""
        return ["zramSwap.enable = true;", 'boot.kernel.sysctl."vm.swappiness" = 10;']

    def _optimize_rebuild(self, metrics: PerformanceMetrics) -> List[str]:
        """Optimize rebuild time"""
        return [
            'nix.settings.max-jobs = "auto";',
            "nix.settings.cores = 0;",  # Use all cores
        ]

    def _optimize_cache(self, metrics: PerformanceMetrics) -> List[str]:
        """Optimize cache usage"""
        return [
            "nix.settings.keep-outputs = true;",
            "nix.settings.keep-derivations = true;",
        ]

    def _optimize_disk(self, metrics: PerformanceMetrics) -> List[str]:
        """Optimize disk I/O"""
        return [
            "nix.settings.auto-optimise-store = true;",
            "services.fstrim.enable = true;",  # For SSDs
        ]

    def _detect_unnecessary_services(self) -> List[str]:
        """Detect services that could be disabled"""
        # In production, would check actual services
        return ["bluetooth", "cups", "avahi"]

    def _detect_unused_kernel_modules(self) -> List[str]:
        """Detect unused kernel modules"""
        # In production, would check loaded modules
        return ["btusb", "bluetooth", "pcspkr"]

    def _get_top_memory_consumers(self) -> List[Dict[str, Any]]:
        """Get top memory consuming processes"""
        # Simulated data
        return [
            {"name": "firefox", "memory_mb": 1500},
            {"name": "vscode", "memory_mb": 800},
            {"name": "nix-daemon", "memory_mb": 400},
        ]

    def _get_top_cpu_processes(self) -> List[Dict[str, Any]]:
        """Get top CPU consuming processes"""
        # Simulated data
        return [
            {"name": "nix-build", "cpu_percent": 45},
            {"name": "cc1plus", "cpu_percent": 30},
            {"name": "firefox", "cpu_percent": 15},
        ]

    def _get_largest_packages(self) -> List[Dict[str, str]]:
        """Get largest installed packages"""
        # Simulated data
        return [
            {"name": "libreoffice", "size": "800MB"},
            {"name": "texlive-full", "size": "2.8GB"},
            {"name": "chromium", "size": "450MB"},
        ]

    def _create_fallback_analysis(self, error: str) -> PerformanceAnalysis:
        """Create fallback analysis on error"""
        return PerformanceAnalysis(
            metrics=PerformanceMetrics(
                boot_time_seconds=0.0,
                rebuild_time_seconds=0.0,
                memory_usage_gb=0.0,
                disk_usage_gb=0.0,
                cpu_usage_percent=0.0,
                cache_hit_rate=0.0,
                derivation_count=0,
                closure_size_gb=0.0,
                network_downloads_mb=0.0,
                compile_time_seconds=0.0,
            ),
            issues=[],
            bottlenecks=[f"Error: {error}"],
            quick_wins=[],
            major_improvements=[],
            configuration_changes=[],
            potential_speedup=0.0,
            estimated_boot_reduction=0.0,
            estimated_memory_savings=0.0,
            confidence=0.0,
        )
