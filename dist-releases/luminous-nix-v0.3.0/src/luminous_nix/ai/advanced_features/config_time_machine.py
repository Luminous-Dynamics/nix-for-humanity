#!/usr/bin/env python3
"""
Configuration Time Machine - Browse and restore any past configuration state

This module provides the ability to:
- Browse configuration history with visual timeline
- Understand changes between any two points
- Restore to any previous state
- Create snapshots with annotations
- Track configuration evolution patterns
"""

import os
import json
import hashlib
import difflib
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.tree import Tree
# Timeline not available in all rich versions


class ChangeType(Enum):
    """Types of configuration changes"""
    PACKAGE_ADD = "package_add"
    PACKAGE_REMOVE = "package_remove"
    SERVICE_ENABLE = "service_enable"
    SERVICE_DISABLE = "service_disable"
    KERNEL_UPDATE = "kernel_update"
    BOOT_CONFIG = "boot_config"
    USER_CHANGE = "user_change"
    NETWORK_CONFIG = "network_config"
    HARDWARE_CONFIG = "hardware_config"
    CUSTOM_MODULE = "custom_module"
    OTHER = "other"


class RestoreStrategy(Enum):
    """Strategies for restoring configurations"""
    FULL = "full"              # Complete restoration
    SELECTIVE = "selective"      # Only specific aspects
    MERGE = "merge"             # Merge with current
    CHERRY_PICK = "cherry_pick"  # Pick specific changes


@dataclass
class ConfigSnapshot:
    """A point-in-time configuration snapshot"""
    generation: int
    timestamp: datetime
    hash: str
    path: Path
    size: int
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Change analysis
    changes_from_previous: List['ConfigChange'] = field(default_factory=list)
    risk_score: float = 0.0
    stability_score: float = 100.0
    
    # User annotations
    notes: Optional[str] = None
    is_milestone: bool = False
    is_backup: bool = False


@dataclass
class ConfigChange:
    """A specific change between configurations"""
    type: ChangeType
    category: str
    description: str
    details: Dict[str, Any]
    impact: str  # low, medium, high
    reversible: bool
    
    # For tracking specific changes
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    modified: Dict[str, Tuple[Any, Any]] = field(default_factory=dict)


@dataclass
class TimelineEvent:
    """An event in the configuration timeline"""
    timestamp: datetime
    generation: int
    event_type: str
    description: str
    icon: str
    color: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class RestorePoint:
    """A recommended restore point"""
    snapshot: ConfigSnapshot
    reason: str
    confidence: float
    benefits: List[str]
    risks: List[str]


class ConfigTimeMachine:
    """
    Configuration Time Machine for NixOS
    
    Features:
    - Visual timeline of all configurations
    - Diff analysis between any two points
    - Intelligent restore recommendations
    - Change pattern recognition
    - Snapshot management with annotations
    """
    
    def __init__(self, config_dir: str = "/etc/nixos"):
        """Initialize the Time Machine"""
        self.config_dir = Path(config_dir)
        self.generations_dir = Path("/nix/var/nix/profiles")
        self.console = Console()
        
        # Cache for analyzed snapshots
        self.snapshots: Dict[int, ConfigSnapshot] = {}
        self.timeline: List[TimelineEvent] = []
        
        # Analysis cache
        self._change_cache: Dict[str, List[ConfigChange]] = {}
        self._pattern_cache: Dict[str, Any] = {}
        
        # Load initial data
        self._load_snapshots()
        self._build_timeline()
    
    def _load_snapshots(self):
        """Load all available configuration snapshots"""
        try:
            # Get NixOS generations
            result = subprocess.run(
                ["nix-env", "--list-generations", "-p", "/nix/var/nix/profiles/system"],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.strip().split('\n'):
                if line:
                    self._parse_generation_line(line)
                    
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not load generations: {e}[/yellow]")
    
    def _parse_generation_line(self, line: str):
        """Parse a generation line from nix-env"""
        # Format: "  42   2024-01-15 10:30:00   (current)"
        parts = line.strip().split(None, 3)
        
        if len(parts) >= 3:
            try:
                gen_num = int(parts[0])
                date_str = f"{parts[1]} {parts[2]}"
                timestamp = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                
                # Check if this is the current generation
                is_current = "(current)" in line
                
                # Create snapshot
                snapshot = ConfigSnapshot(
                    generation=gen_num,
                    timestamp=timestamp,
                    hash=self._calculate_config_hash(gen_num),
                    path=self.generations_dir / f"system-{gen_num}-link",
                    size=self._get_generation_size(gen_num),
                    description=f"Generation {gen_num}",
                    metadata={"is_current": is_current}
                )
                
                # Analyze changes if not the first generation
                if gen_num > 1 and (gen_num - 1) in self.snapshots:
                    snapshot.changes_from_previous = self._analyze_changes(
                        self.snapshots[gen_num - 1],
                        snapshot
                    )
                
                self.snapshots[gen_num] = snapshot
                
            except (ValueError, IndexError):
                pass
    
    def _calculate_config_hash(self, generation: int) -> str:
        """Calculate hash of a configuration"""
        config_path = self.generations_dir / f"system-{generation}-link" / "etc/nixos/configuration.nix"
        
        if config_path.exists():
            with open(config_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()[:16]
        
        return f"gen-{generation}"
    
    def _get_generation_size(self, generation: int) -> int:
        """Get the size of a generation"""
        gen_path = self.generations_dir / f"system-{generation}-link"
        
        if gen_path.exists():
            try:
                result = subprocess.run(
                    ["du", "-sb", str(gen_path)],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return int(result.stdout.split()[0])
            except:
                pass
        
        return 0
    
    def _analyze_changes(self, old_snapshot: ConfigSnapshot, 
                         new_snapshot: ConfigSnapshot) -> List[ConfigChange]:
        """Analyze changes between two snapshots"""
        
        cache_key = f"{old_snapshot.generation}-{new_snapshot.generation}"
        if cache_key in self._change_cache:
            return self._change_cache[cache_key]
        
        changes = []
        
        # Compare configuration files
        old_config = self._read_config(old_snapshot.generation)
        new_config = self._read_config(new_snapshot.generation)
        
        if old_config and new_config:
            # Analyze package changes
            old_packages = self._extract_packages(old_config)
            new_packages = self._extract_packages(new_config)
            
            added_packages = new_packages - old_packages
            removed_packages = old_packages - new_packages
            
            if added_packages:
                changes.append(ConfigChange(
                    type=ChangeType.PACKAGE_ADD,
                    category="packages",
                    description=f"Added {len(added_packages)} packages",
                    details={"packages": list(added_packages)},
                    impact="low" if len(added_packages) < 5 else "medium",
                    reversible=True,
                    added=list(added_packages)
                ))
            
            if removed_packages:
                changes.append(ConfigChange(
                    type=ChangeType.PACKAGE_REMOVE,
                    category="packages",
                    description=f"Removed {len(removed_packages)} packages",
                    details={"packages": list(removed_packages)},
                    impact="low" if len(removed_packages) < 5 else "medium",
                    reversible=True,
                    removed=list(removed_packages)
                ))
            
            # Analyze service changes
            old_services = self._extract_services(old_config)
            new_services = self._extract_services(new_config)
            
            enabled_services = new_services - old_services
            disabled_services = old_services - new_services
            
            if enabled_services:
                changes.append(ConfigChange(
                    type=ChangeType.SERVICE_ENABLE,
                    category="services",
                    description=f"Enabled {len(enabled_services)} services",
                    details={"services": list(enabled_services)},
                    impact="medium",
                    reversible=True,
                    added=list(enabled_services)
                ))
            
            if disabled_services:
                changes.append(ConfigChange(
                    type=ChangeType.SERVICE_DISABLE,
                    category="services",
                    description=f"Disabled {len(disabled_services)} services",
                    details={"services": list(disabled_services)},
                    impact="medium",
                    reversible=True,
                    removed=list(disabled_services)
                ))
        
        self._change_cache[cache_key] = changes
        return changes
    
    def _read_config(self, generation: int) -> Optional[str]:
        """Read configuration for a generation"""
        config_path = self.generations_dir / f"system-{generation}-link" / "etc/nixos/configuration.nix"
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return f.read()
            except:
                pass
        
        return None
    
    def _extract_packages(self, config: str) -> set:
        """Extract package names from configuration"""
        packages = set()
        
        # Simple extraction - would need more sophisticated parsing
        import re
        
        # Look for environment.systemPackages patterns
        pattern = r'environment\.systemPackages\s*=\s*with\s+pkgs;\s*\[(.*?)\]'
        matches = re.findall(pattern, config, re.DOTALL)
        
        for match in matches:
            # Extract package names
            pkg_names = re.findall(r'\b(\w+)\b', match)
            packages.update(pkg_names)
        
        return packages
    
    def _extract_services(self, config: str) -> set:
        """Extract enabled services from configuration"""
        services = set()
        
        import re
        
        # Look for services.*.enable = true patterns
        pattern = r'services\.(\w+)\.enable\s*=\s*true'
        matches = re.findall(pattern, config)
        services.update(matches)
        
        return services
    
    def _build_timeline(self):
        """Build the configuration timeline"""
        self.timeline = []
        
        for gen_num, snapshot in sorted(self.snapshots.items()):
            # Determine event type and styling
            if snapshot.metadata.get("is_current"):
                event_type = "current"
                icon = "🟢"
                color = "green"
            elif snapshot.is_milestone:
                event_type = "milestone"
                icon = "⭐"
                color = "yellow"
            elif snapshot.is_backup:
                event_type = "backup"
                icon = "💾"
                color = "blue"
            else:
                event_type = "normal"
                icon = "⚪"
                color = "white"
            
            # Create description
            description = snapshot.description or f"Generation {gen_num}"
            if snapshot.changes_from_previous:
                change_summary = self._summarize_changes(snapshot.changes_from_previous)
                description += f" - {change_summary}"
            
            event = TimelineEvent(
                timestamp=snapshot.timestamp,
                generation=gen_num,
                event_type=event_type,
                description=description,
                icon=icon,
                color=color,
                details={
                    "size": snapshot.size,
                    "hash": snapshot.hash,
                    "changes": len(snapshot.changes_from_previous)
                }
            )
            
            self.timeline.append(event)
    
    def _summarize_changes(self, changes: List[ConfigChange]) -> str:
        """Create a summary of changes"""
        if not changes:
            return "No changes"
        
        summaries = []
        
        # Count by type
        type_counts = {}
        for change in changes:
            type_counts[change.type] = type_counts.get(change.type, 0) + 1
        
        # Create summaries
        for change_type, count in type_counts.items():
            if change_type == ChangeType.PACKAGE_ADD:
                summaries.append(f"+{count} packages")
            elif change_type == ChangeType.PACKAGE_REMOVE:
                summaries.append(f"-{count} packages")
            elif change_type == ChangeType.SERVICE_ENABLE:
                summaries.append(f"enabled {count} services")
            elif change_type == ChangeType.SERVICE_DISABLE:
                summaries.append(f"disabled {count} services")
        
        return ", ".join(summaries) if summaries else "Minor changes"
    
    def browse_timeline(self, limit: int = 20) -> List[TimelineEvent]:
        """Browse the configuration timeline"""
        return self.timeline[-limit:]
    
    def get_snapshot(self, generation: int) -> Optional[ConfigSnapshot]:
        """Get a specific snapshot"""
        return self.snapshots.get(generation)
    
    def diff_configurations(self, gen1: int, gen2: int) -> List[str]:
        """Get diff between two configurations"""
        config1 = self._read_config(gen1)
        config2 = self._read_config(gen2)
        
        if not config1 or not config2:
            return ["Could not read configurations"]
        
        # Create unified diff
        diff = difflib.unified_diff(
            config1.splitlines(keepends=True),
            config2.splitlines(keepends=True),
            fromfile=f"Generation {gen1}",
            tofile=f"Generation {gen2}",
            n=3
        )
        
        return list(diff)
    
    def find_similar_configurations(self, target_gen: int, 
                                   threshold: float = 0.8) -> List[Tuple[int, float]]:
        """Find configurations similar to a target"""
        target = self.snapshots.get(target_gen)
        if not target:
            return []
        
        similar = []
        target_config = self._read_config(target_gen)
        
        if not target_config:
            return []
        
        for gen_num, snapshot in self.snapshots.items():
            if gen_num == target_gen:
                continue
            
            other_config = self._read_config(gen_num)
            if other_config:
                # Calculate similarity
                similarity = self._calculate_similarity(target_config, other_config)
                
                if similarity >= threshold:
                    similar.append((gen_num, similarity))
        
        return sorted(similar, key=lambda x: x[1], reverse=True)
    
    def _calculate_similarity(self, config1: str, config2: str) -> float:
        """Calculate similarity between two configurations"""
        # Simple line-based similarity
        lines1 = set(config1.strip().split('\n'))
        lines2 = set(config2.strip().split('\n'))
        
        if not lines1 or not lines2:
            return 0.0
        
        intersection = len(lines1 & lines2)
        union = len(lines1 | lines2)
        
        return intersection / union if union > 0 else 0.0
    
    def recommend_restore_points(self, criteria: Optional[Dict[str, Any]] = None) -> List[RestorePoint]:
        """Recommend restore points based on criteria"""
        recommendations = []
        
        current_gen = max(self.snapshots.keys())
        
        for gen_num, snapshot in self.snapshots.items():
            if gen_num == current_gen:
                continue
            
            # Score this snapshot
            score = 0.0
            benefits = []
            risks = []
            reason = ""
            
            # Stability scoring
            if snapshot.stability_score > 90:
                score += 0.3
                benefits.append("High stability")
            
            # Low risk scoring
            if snapshot.risk_score < 20:
                score += 0.2
                benefits.append("Low risk")
            
            # Milestone bonus
            if snapshot.is_milestone:
                score += 0.2
                benefits.append("Marked as milestone")
                reason = "Milestone configuration"
            
            # Age penalty (prefer recent)
            age_days = (datetime.now() - snapshot.timestamp).days
            if age_days < 7:
                score += 0.2
                benefits.append("Recent configuration")
            elif age_days > 30:
                score -= 0.1
                risks.append("Older configuration")
            
            # Check specific criteria
            if criteria:
                if criteria.get("stable") and snapshot.stability_score > 95:
                    score += 0.3
                    reason = "Highly stable configuration"
                
                if criteria.get("minimal") and len(snapshot.changes_from_previous) < 3:
                    score += 0.2
                    reason = "Minimal configuration"
            
            if score > 0.5:
                recommendations.append(RestorePoint(
                    snapshot=snapshot,
                    reason=reason or "Good restore candidate",
                    confidence=min(score, 1.0),
                    benefits=benefits,
                    risks=risks
                ))
        
        return sorted(recommendations, key=lambda x: x.confidence, reverse=True)[:5]
    
    def create_snapshot(self, description: str, tags: List[str] = None,
                       is_milestone: bool = False) -> ConfigSnapshot:
        """Create a new snapshot with annotations"""
        
        # Get current generation
        current_gen = max(self.snapshots.keys())
        snapshot = self.snapshots[current_gen]
        
        # Update with user data
        snapshot.description = description
        snapshot.tags = tags or []
        snapshot.is_milestone = is_milestone
        snapshot.notes = f"Created by user at {datetime.now()}"
        
        # Save metadata
        self._save_snapshot_metadata(snapshot)
        
        return snapshot
    
    def _save_snapshot_metadata(self, snapshot: ConfigSnapshot):
        """Save snapshot metadata to disk"""
        metadata_dir = Path.home() / ".config/luminous-nix/snapshots"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        
        metadata_file = metadata_dir / f"gen-{snapshot.generation}.json"
        
        metadata = {
            "generation": snapshot.generation,
            "timestamp": snapshot.timestamp.isoformat(),
            "description": snapshot.description,
            "tags": snapshot.tags,
            "is_milestone": snapshot.is_milestone,
            "is_backup": snapshot.is_backup,
            "notes": snapshot.notes
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def restore_configuration(self, generation: int, 
                             strategy: RestoreStrategy = RestoreStrategy.FULL,
                             dry_run: bool = True) -> Dict[str, Any]:
        """Restore to a specific configuration"""
        
        if generation not in self.snapshots:
            return {
                "success": False,
                "error": f"Generation {generation} not found"
            }
        
        snapshot = self.snapshots[generation]
        
        if strategy == RestoreStrategy.FULL:
            # Full system restoration
            if dry_run:
                return {
                    "success": True,
                    "action": "would_restore",
                    "generation": generation,
                    "command": f"sudo nixos-rebuild switch --rollback {generation}",
                    "changes": len(snapshot.changes_from_previous)
                }
            else:
                try:
                    result = subprocess.run(
                        ["sudo", "nixos-rebuild", "switch", "--rollback", str(generation)],
                        capture_output=True,
                        text=True
                    )
                    
                    return {
                        "success": result.returncode == 0,
                        "generation": generation,
                        "output": result.stdout,
                        "error": result.stderr if result.returncode != 0 else None
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "error": str(e)
                    }
        
        elif strategy == RestoreStrategy.SELECTIVE:
            # Selective restoration (packages only, services only, etc.)
            return {
                "success": True,
                "action": "selective_restore",
                "generation": generation,
                "note": "Selective restore requires manual configuration editing"
            }
        
        elif strategy == RestoreStrategy.MERGE:
            # Merge with current configuration
            return {
                "success": True,
                "action": "merge",
                "generation": generation,
                "note": "Merge requires manual conflict resolution"
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown strategy: {strategy}"
            }
    
    def analyze_evolution_patterns(self) -> Dict[str, Any]:
        """Analyze configuration evolution patterns"""
        
        if not self.snapshots:
            return {}
        
        patterns = {
            "total_generations": len(self.snapshots),
            "time_span": None,
            "change_frequency": None,
            "most_changed": {},
            "stability_periods": [],
            "growth_rate": None
        }
        
        # Calculate time span
        timestamps = [s.timestamp for s in self.snapshots.values()]
        if timestamps:
            patterns["time_span"] = (max(timestamps) - min(timestamps)).days
        
        # Analyze change frequency
        changes_per_week = {}
        for snapshot in self.snapshots.values():
            week = snapshot.timestamp.isocalendar()[1]
            year = snapshot.timestamp.year
            key = f"{year}-W{week:02d}"
            changes_per_week[key] = changes_per_week.get(key, 0) + len(snapshot.changes_from_previous)
        
        if changes_per_week:
            patterns["change_frequency"] = sum(changes_per_week.values()) / len(changes_per_week)
        
        # Find most changed categories
        category_counts = {}
        for snapshot in self.snapshots.values():
            for change in snapshot.changes_from_previous:
                category_counts[change.category] = category_counts.get(change.category, 0) + 1
        
        patterns["most_changed"] = dict(sorted(
            category_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5])
        
        # Identify stability periods (no changes for >7 days)
        last_change = None
        for snapshot in sorted(self.snapshots.values(), key=lambda x: x.timestamp):
            if not snapshot.changes_from_previous:
                if last_change and (snapshot.timestamp - last_change).days > 7:
                    patterns["stability_periods"].append({
                        "start": last_change,
                        "end": snapshot.timestamp,
                        "duration_days": (snapshot.timestamp - last_change).days
                    })
            else:
                last_change = snapshot.timestamp
        
        # Calculate growth rate (size over time)
        sizes = [(s.timestamp, s.size) for s in self.snapshots.values() if s.size > 0]
        if len(sizes) > 1:
            first_size = sizes[0][1]
            last_size = sizes[-1][1]
            days = (sizes[-1][0] - sizes[0][0]).days
            
            if days > 0:
                patterns["growth_rate"] = (last_size - first_size) / days  # bytes per day
        
        return patterns
    
    def visualize_timeline(self) -> Panel:
        """Create a visual timeline of configurations"""
        
        tree = Tree("[bold cyan]Configuration Timeline[/bold cyan]")
        
        # Group by month
        by_month = {}
        for event in self.timeline[-30:]:  # Last 30 events
            month_key = event.timestamp.strftime("%Y-%m")
            if month_key not in by_month:
                by_month[month_key] = []
            by_month[month_key].append(event)
        
        for month, events in sorted(by_month.items(), reverse=True):
            month_date = datetime.strptime(month, "%Y-%m")
            month_branch = tree.add(f"[yellow]{month_date.strftime('%B %Y')}[/yellow]")
            
            for event in sorted(events, key=lambda x: x.timestamp, reverse=True):
                # Format event
                time_str = event.timestamp.strftime("%d %H:%M")
                
                # Style based on type
                if event.event_type == "current":
                    style = "bold green"
                elif event.event_type == "milestone":
                    style = "bold yellow"
                else:
                    style = "white"
                
                event_text = f"{event.icon} [{style}]Gen {event.generation}[/{style}] - {time_str}"
                
                if event.details and event.details.get("changes"):
                    event_text += f" [dim]({event.details['changes']} changes)[/dim]"
                
                event_node = month_branch.add(event_text)
                
                if event.description and event.description != f"Generation {event.generation}":
                    event_node.add(f"[dim]{event.description}[/dim]")
        
        return Panel(tree, title="📅 Configuration History", border_style="blue")