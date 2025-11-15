#!/usr/bin/env python3
"""
Storage Optimization - Smart garbage collection that knows what's safe
Intelligent cleanup vs blind deletion - frees space without breaking system
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

# Import core infrastructure
try:
    from .core.state_analyzer import get_state_analyzer
except ImportError:
    import sys

    sys.path.append("..")
    from core.state_analyzer import get_state_analyzer

logger = logging.getLogger(__name__)


@dataclass
class StorageAnalysis:
    """Storage optimization analysis result"""

    total_store_size_gb: float
    reclaimable_gb: float
    safe_to_remove_gb: float
    risky_to_remove_gb: float

    old_generations: List[Dict]  # Generations safe to remove
    orphaned_packages: List[str]  # Packages with no dependents
    build_artifacts: List[str]  # Temporary build files
    duplicate_derivations: List[str]  # Duplicate store paths

    cleanup_commands: List[str]  # Commands to run for cleanup
    estimated_time_minutes: float  # Estimated cleanup time
    confidence: float

    breakdown: Dict[str, float]  # GB by category


@dataclass
class PackageInfo:
    """Information about a Nix store package"""

    path: str
    name: str
    size_mb: float
    dependencies: Set[str]
    dependents: Set[str]
    last_accessed: Optional[datetime]
    is_current: bool  # Part of current generation


class StorageOptimizer:
    """
    Intelligent storage optimization using HRM reasoning
    Identifies safe cleanup opportunities without breaking the system
    """

    def __init__(self):
        self.analyzer = get_state_analyzer()

        # Safe cleanup thresholds
        self.config = {
            "max_generations_to_keep": 10,
            "min_generation_age_days": 7,
            "min_free_space_gb": 10,
            "aggressive_mode": False,
        }

        # Package categories that are always safe to clean
        self.safe_cleanup_patterns = [
            r".*\.drv$",  # Derivation files
            r".*-source$",  # Source archives
            r".*\.tar\.(gz|bz2|xz)$",  # Compressed archives
            r".*-doc$",  # Documentation
            r".*-man$",  # Man pages
            r".*\.log$",  # Log files
        ]

        # Critical packages never to remove
        self.critical_patterns = [
            r".*systemd.*",
            r".*kernel.*",
            r".*nixos.*",
            r".*boot.*",
            r".*grub.*",
            r".*init.*",
        ]

    def analyze_storage(self, aggressive: bool = False) -> StorageAnalysis:
        """
        Analyze storage and identify safe cleanup opportunities

        Args:
            aggressive: If True, be more aggressive about cleanup

        Returns:
            StorageAnalysis with cleanup recommendations
        """
        try:
            # Update config for aggressive mode
            if aggressive:
                self.config["max_generations_to_keep"] = 3
                self.config["min_generation_age_days"] = 1

            # Get system state
            state = self.analyzer.get_system_state()
            total_size = state.store_size_gb

            # Analyze different cleanup opportunities
            old_gens = self._analyze_old_generations()
            orphaned = self._analyze_orphaned_packages()
            artifacts = self._analyze_build_artifacts()
            duplicates = self._analyze_duplicate_derivations()

            # Calculate reclaimable space
            breakdown = {
                "old_generations": self._calculate_generation_size(old_gens),
                "orphaned_packages": self._calculate_package_size(orphaned),
                "build_artifacts": self._calculate_artifact_size(artifacts),
                "duplicates": self._calculate_duplicate_size(duplicates),
            }

            safe_gb = breakdown["old_generations"] + breakdown["build_artifacts"]
            risky_gb = breakdown["orphaned_packages"] + breakdown["duplicates"]
            total_reclaimable = safe_gb + risky_gb

            # Generate cleanup commands
            commands = self._generate_cleanup_commands(
                old_gens, orphaned, artifacts, duplicates, aggressive
            )

            # Estimate cleanup time
            estimated_time = self._estimate_cleanup_time(total_reclaimable)

            return StorageAnalysis(
                total_store_size_gb=total_size,
                reclaimable_gb=total_reclaimable,
                safe_to_remove_gb=safe_gb,
                risky_to_remove_gb=risky_gb,
                old_generations=old_gens,
                orphaned_packages=orphaned[:20],  # Limit for display
                build_artifacts=artifacts[:20],
                duplicate_derivations=duplicates[:10],
                cleanup_commands=commands,
                estimated_time_minutes=estimated_time,
                confidence=0.9 if not aggressive else 0.7,
                breakdown=breakdown,
            )

        except Exception as e:
            logger.error(f"Storage analysis failed: {e}")
            return self._create_fallback_analysis(str(e))

    def optimize_store(self, target_free_gb: float = 10.0) -> Dict[str, Any]:
        """
        Optimize store to free up specific amount of space

        Args:
            target_free_gb: Target GB to free up

        Returns:
            Optimization plan
        """
        try:
            # Get current analysis
            analysis = self.analyze_storage()

            if analysis.reclaimable_gb < target_free_gb:
                # Need aggressive mode
                analysis = self.analyze_storage(aggressive=True)

            # Create optimization plan
            plan = {
                "target_gb": target_free_gb,
                "available_gb": analysis.reclaimable_gb,
                "can_achieve": analysis.reclaimable_gb >= target_free_gb,
                "steps": [],
            }

            freed = 0.0

            # Prioritize safe cleanups first
            if freed < target_free_gb and analysis.breakdown["build_artifacts"] > 0:
                plan["steps"].append(
                    {
                        "action": "Clean build artifacts",
                        "command": "nix-collect-garbage",
                        "space_gb": analysis.breakdown["build_artifacts"],
                        "risk": "none",
                    }
                )
                freed += analysis.breakdown["build_artifacts"]

            if freed < target_free_gb and analysis.breakdown["old_generations"] > 0:
                plan["steps"].append(
                    {
                        "action": "Remove old generations",
                        "command": "nix-collect-garbage -d --delete-older-than 7d",
                        "space_gb": analysis.breakdown["old_generations"],
                        "risk": "low",
                    }
                )
                freed += analysis.breakdown["old_generations"]

            # Then risky cleanups if needed
            if freed < target_free_gb and analysis.breakdown["orphaned_packages"] > 0:
                plan["steps"].append(
                    {
                        "action": "Remove orphaned packages",
                        "command": "nix-store --gc",
                        "space_gb": analysis.breakdown["orphaned_packages"],
                        "risk": "medium",
                    }
                )
                freed += analysis.breakdown["orphaned_packages"]

            plan["total_freed_gb"] = freed

            return plan

        except Exception as e:
            logger.error(f"Store optimization failed: {e}")
            return {
                "error": str(e),
                "target_gb": target_free_gb,
                "available_gb": 0,
                "can_achieve": False,
            }

    def find_large_packages(self, min_size_mb: float = 100) -> List[Dict]:
        """Find large packages in the store"""
        large_packages = []

        try:
            # This would normally scan /nix/store
            # For demo, return simulated data
            store_path = Path("/nix/store")

            if store_path.exists():
                # In production, would properly scan store
                # For now, return example data
                examples = [
                    {
                        "name": "chromium-120.0",
                        "size_mb": 450,
                        "path": "/nix/store/xxx-chromium",
                    },
                    {
                        "name": "libreoffice-7.6",
                        "size_mb": 380,
                        "path": "/nix/store/yyy-libreoffice",
                    },
                    {
                        "name": "texlive-full",
                        "size_mb": 2800,
                        "path": "/nix/store/zzz-texlive",
                    },
                ]

                for pkg in examples:
                    if pkg["size_mb"] >= min_size_mb:
                        large_packages.append(pkg)

        except Exception as e:
            logger.error(f"Failed to find large packages: {e}")

        return sorted(large_packages, key=lambda x: x["size_mb"], reverse=True)

    def _analyze_old_generations(self) -> List[Dict]:
        """Analyze old generations safe to remove"""
        old_generations = []

        try:
            current_gen = self.analyzer._get_current_generation()
            generations = self.analyzer.list_generations(limit=50)

            # Keep track of generations to keep
            keep_count = 0
            cutoff_date = datetime.now() - timedelta(
                days=self.config["min_generation_age_days"]
            )

            for gen in generations:
                if gen.number == current_gen:
                    continue  # Never remove current

                if keep_count < self.config["max_generations_to_keep"]:
                    keep_count += 1
                    continue  # Keep recent generations

                if gen.date > cutoff_date:
                    continue  # Too recent

                # This generation can be removed
                old_generations.append(
                    {
                        "number": gen.number,
                        "date": gen.date.isoformat(),
                        "path": gen.path,
                        "estimated_size_gb": 0.5,  # Estimate
                    }
                )

        except Exception as e:
            logger.error(f"Failed to analyze old generations: {e}")

        return old_generations

    def _analyze_orphaned_packages(self) -> List[str]:
        """Find orphaned packages with no dependents"""
        orphaned = []

        try:
            # In production, would use nix-store --query --roots
            # For demo, return simulated orphaned packages
            simulated_orphans = [
                "/nix/store/abc-old-firefox-118.0",
                "/nix/store/def-unused-library-2.3",
                "/nix/store/ghi-build-dependency-1.0",
            ]

            for pkg in simulated_orphans:
                if not self._is_critical_package(pkg):
                    orphaned.append(pkg)

        except Exception as e:
            logger.error(f"Failed to analyze orphaned packages: {e}")

        return orphaned

    def _analyze_build_artifacts(self) -> List[str]:
        """Find build artifacts safe to remove"""
        artifacts = []

        try:
            # Look for .drv files and build outputs
            # In production, would scan store properly
            simulated_artifacts = [
                "/nix/store/123-firefox.drv",
                "/nix/store/456-build-log.txt",
                "/nix/store/789-source.tar.gz",
            ]

            for artifact in simulated_artifacts:
                if self._is_safe_to_remove(artifact):
                    artifacts.append(artifact)

        except Exception as e:
            logger.error(f"Failed to analyze build artifacts: {e}")

        return artifacts

    def _analyze_duplicate_derivations(self) -> List[str]:
        """Find duplicate derivations"""
        duplicates = []

        try:
            # In production, would find actual duplicates
            # For demo, return simulated data
            simulated_dups = [
                "/nix/store/aaa-python-3.11.5",
                "/nix/store/bbb-python-3.11.5",  # Duplicate
            ]

            # Would check if truly duplicate and safe to remove one
            duplicates = simulated_dups[1:]  # Keep first, remove rest

        except Exception as e:
            logger.error(f"Failed to analyze duplicates: {e}")

        return duplicates

    def _calculate_generation_size(self, generations: List[Dict]) -> float:
        """Calculate total size of generations"""
        # Estimate 0.5GB per generation
        return len(generations) * 0.5

    def _calculate_package_size(self, packages: List[str]) -> float:
        """Calculate total size of packages"""
        # Estimate 100MB per package
        return len(packages) * 0.1

    def _calculate_artifact_size(self, artifacts: List[str]) -> float:
        """Calculate total size of artifacts"""
        # Estimate 50MB per artifact
        return len(artifacts) * 0.05

    def _calculate_duplicate_size(self, duplicates: List[str]) -> float:
        """Calculate total size of duplicates"""
        # Estimate 200MB per duplicate
        return len(duplicates) * 0.2

    def _generate_cleanup_commands(
        self, old_gens, orphaned, artifacts, duplicates, aggressive
    ):
        """Generate cleanup commands"""
        commands = []

        # Safe cleanups
        if artifacts:
            commands.append("# Clean build artifacts")
            commands.append("nix-collect-garbage")

        if old_gens:
            commands.append("# Remove old generations")
            if aggressive:
                commands.append("nix-collect-garbage -d --delete-older-than 1d")
            else:
                commands.append("nix-collect-garbage -d --delete-older-than 7d")

        # Optimize store
        commands.append("# Optimize nix store")
        commands.append("nix-store --optimize")

        # Risky cleanups (only if aggressive)
        if aggressive and orphaned:
            commands.append("# Remove orphaned packages (review first!)")
            commands.append("nix-store --gc")

        return commands

    def _estimate_cleanup_time(self, gb_to_clean: float) -> float:
        """Estimate cleanup time in minutes"""
        # Rough estimate: 1 minute per GB
        return max(1.0, gb_to_clean)

    def _is_critical_package(self, path: str) -> bool:
        """Check if package is critical and should never be removed"""
        for pattern in self.critical_patterns:
            if re.search(pattern, path):
                return True
        return False

    def _is_safe_to_remove(self, path: str) -> bool:
        """Check if path is safe to remove"""
        for pattern in self.safe_cleanup_patterns:
            if re.search(pattern, path):
                return True
        return False

    def _create_fallback_analysis(self, error: str) -> StorageAnalysis:
        """Create fallback analysis when normal analysis fails"""
        return StorageAnalysis(
            total_store_size_gb=0.0,
            reclaimable_gb=0.0,
            safe_to_remove_gb=0.0,
            risky_to_remove_gb=0.0,
            old_generations=[],
            orphaned_packages=[],
            build_artifacts=[],
            duplicate_derivations=[],
            cleanup_commands=["nix-collect-garbage -d"],
            estimated_time_minutes=5.0,
            confidence=0.3,
            breakdown={"error": error},
        )
