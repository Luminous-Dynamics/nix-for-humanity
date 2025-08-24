#!/usr/bin/env python3
"""
🌟 Luminous Setup Ceremony - Profile System
Integrates with existing Luminous Nix components for intelligent system setup
"""

import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# Reuse our existing components!
from ..consciousness.poml_core import POMLConsciousness
from ..persistence.trinity_store import DataTrinity, TrinityKnowledge
from ..core.system_orchestrator import SystemOrchestrator
from ..nlp.intent_recognition import IntentRecognizer
from ..core.native_nix_api import NativeNixAPI
from ..config.config_manager import ConfigManager

logger = logging.getLogger(__name__)


class ProfileType(Enum):
    """Core user profiles"""
    HOME = "home_user"
    OFFICE = "office_worker"
    CREATIVE = "creative"
    DEVELOPER = "developer"
    GAMER = "gamer"
    STUDENT = "student"
    HYBRID = "hybrid"  # Combination of multiple


@dataclass
class UserProfile:
    """Complete user profile with packages and settings"""
    type: ProfileType
    name: str
    emoji: str
    description: str
    packages: List[str]
    optional_packages: List[str]
    settings: Dict[str, Any]
    optimizations: List[str]
    ai_persona: str  # Which persona guides this profile
    
    def to_nix_config(self) -> str:
        """Generate NixOS configuration for this profile"""
        # We'll use the existing ConfigGenerator!
        pass


class PackageIntelligence:
    """
    Intelligent package management using existing components
    """
    
    def __init__(self):
        self.orchestrator = SystemOrchestrator()
        self.trinity = DataTrinity()
        self.nix_api = NativeNixAPI()
        self.intent = IntentRecognizer()
        
    def detect_installed(self) -> Dict[str, List[str]]:
        """Detect and categorize installed packages"""
        # Use native API for fast detection
        installed = self.nix_api.get_installed_packages()
        
        # Categorize using our knowledge base
        categorized = {}
        for pkg in installed:
            # Query trinity for package category
            knowledge = self.trinity.query_semantic(
                f"category of {pkg} package",
                limit=1
            )
            if knowledge:
                category = knowledge[0].metadata.get('category', 'other')
                if category not in categorized:
                    categorized[category] = []
                categorized[category].append(pkg)
                
        return categorized
    
    def find_conflicts(self, packages: List[str]) -> List[Tuple[str, str, str]]:
        """
        Find package conflicts using AST intelligence
        Returns: [(pkg1, pkg2, reason), ...]
        """
        conflicts = []
        
        # Use trinity to find known conflicts
        for i, pkg1 in enumerate(packages):
            for pkg2 in packages[i+1:]:
                # Check knowledge graph for conflicts
                conflict_data = self.trinity.query_relational(
                    f"MATCH (p1:Package {{name: '{pkg1}'}})-[:CONFLICTS_WITH]-(p2:Package {{name: '{pkg2}'}}) RETURN p1, p2"
                )
                if conflict_data:
                    reason = conflict_data[0].get('reason', 'Known conflict')
                    conflicts.append((pkg1, pkg2, reason))
                    
        return conflicts
    
    def suggest_companions(self, package: str) -> List[Dict[str, Any]]:
        """Suggest packages that work well together"""
        # Query trinity for companion packages
        companions = self.trinity.query_relational(
            f"MATCH (p:Package {{name: '{package}'}})-[:WORKS_WELL_WITH]-(c:Package) "
            f"RETURN c.name as name, c.description as description"
        )
        
        return [
            {
                'package': comp['name'],
                'reason': comp['description'],
                'confidence': 0.85  # Could be calculated from usage patterns
            }
            for comp in companions
        ]


class ProfileManager:
    """
    Manages user profiles using POML consciousness system
    """
    
    def __init__(self):
        self.consciousness = POMLConsciousness()
        self.profiles = self._load_profiles()
        self.package_intel = PackageIntelligence()
        
    def _load_profiles(self) -> Dict[str, UserProfile]:
        """Load profile definitions"""
        return {
            'home': UserProfile(
                type=ProfileType.HOME,
                name="Home & Family",
                emoji="🏠",
                description="Perfect for family computers",
                packages=[
                    "firefox", "thunderbird", "libreoffice",
                    "vlc", "gimp", "transmission-gtk"
                ],
                optional_packages=[
                    "spotify", "zoom", "skype", "teams"
                ],
                settings={
                    "auto_updates": True,
                    "parental_controls": "available",
                    "complexity": "minimal"
                },
                optimizations=["stability", "ease_of_use"],
                ai_persona="grandma_rose"
            ),
            'developer': UserProfile(
                type=ProfileType.DEVELOPER,
                name="Code Warrior",
                emoji="⚡",
                description="Full development environment",
                packages=[
                    "git", "vscode", "docker", "nodejs",
                    "python3", "rust", "alacritty", "tmux"
                ],
                optional_packages=[
                    "postgresql", "redis", "mongodb",
                    "kubernetes", "terraform", "ansible"
                ],
                settings={
                    "shell": "zsh",
                    "dotfiles": True,
                    "developer_mode": True
                },
                optimizations=["performance", "flexibility"],
                ai_persona="elder_unix"
            ),
            'creative': UserProfile(
                type=ProfileType.CREATIVE,
                name="Creative Studio",
                emoji="🎨",
                description="For artists and creators",
                packages=[
                    "gimp", "inkscape", "blender", "krita",
                    "kdenlive", "ardour", "obs-studio"
                ],
                optional_packages=[
                    "darktable", "rawtherapee", "natron",
                    "synfigstudio", "godot"
                ],
                settings={
                    "gpu_acceleration": True,
                    "color_management": True,
                    "tablet_support": True
                },
                optimizations=["gpu_performance", "color_accuracy"],
                ai_persona="maya_lightning"
            )
        }
    
    def infer_profile(self, installed_packages: List[str]) -> ProfileType:
        """Use POML consciousness to infer user profile from packages"""
        # Create context for consciousness
        context = {
            "installed_packages": installed_packages,
            "package_categories": self.package_intel.detect_installed()
        }
        
        # Ask consciousness to analyze
        result = self.consciousness.process_intent(
            intent="analyze user profile from packages",
            context=context
        )
        
        # Extract profile type from result
        profile_scores = result.get('profile_scores', {})
        return ProfileType(max(profile_scores, key=profile_scores.get))
    
    def recommend_packages(self, profile: UserProfile, 
                          installed: List[str]) -> Dict[str, List[Dict]]:
        """Intelligent package recommendations"""
        recommendations = {
            "essential_missing": [],
            "highly_recommended": [],
            "nice_to_have": [],
            "companion_apps": []
        }
        
        # Find missing essentials
        for pkg in profile.packages:
            if pkg not in installed:
                recommendations["essential_missing"].append({
                    "package": pkg,
                    "reason": "Core package for your profile"
                })
        
        # Find companions for installed packages
        for pkg in installed:
            companions = self.package_intel.suggest_companions(pkg)
            recommendations["companion_apps"].extend(companions)
        
        return recommendations


class ConflictResolver:
    """
    Intelligent conflict resolution using AST and consciousness
    """
    
    def __init__(self):
        self.consciousness = POMLConsciousness()
        self.orchestrator = SystemOrchestrator()
        
    def resolve_conflicts(self, conflicts: List[Tuple[str, str, str]], 
                         user_profile: UserProfile) -> List[Dict[str, Any]]:
        """Resolve conflicts based on user profile and AI guidance"""
        resolutions = []
        
        for pkg1, pkg2, reason in conflicts:
            # Ask consciousness for resolution
            context = {
                "package1": pkg1,
                "package2": pkg2,
                "conflict_reason": reason,
                "user_profile": user_profile.type.value,
                "user_expertise": user_profile.settings.get("expertise", "beginner")
            }
            
            resolution = self.consciousness.process_intent(
                intent="resolve package conflict",
                context=context,
                persona=user_profile.ai_persona
            )
            
            resolutions.append({
                "conflict": (pkg1, pkg2),
                "resolution": resolution.get("resolution"),
                "explanation": resolution.get("explanation"),
                "auto_apply": resolution.get("confidence", 0) > 0.8
            })
            
        return resolutions


class SetupCeremony:
    """
    The main setup ceremony orchestrator
    Coordinates all components for the installation experience
    """
    
    def __init__(self):
        self.profile_manager = ProfileManager()
        self.package_intel = PackageIntelligence()
        self.conflict_resolver = ConflictResolver()
        self.consciousness = POMLConsciousness()
        self.trinity = DataTrinity()
        
        # Track ceremony state
        self.current_round = 0
        self.selected_profile = None
        self.selected_packages = []
        self.checkpoints = []
        
    def begin_ceremony(self) -> Dict[str, Any]:
        """Start the setup ceremony"""
        # Detect what's installed
        installed = self.package_intel.detect_installed()
        
        # Infer profile
        suggested_profile = self.profile_manager.infer_profile(
            list(installed.values())
        )
        
        return {
            "stage": "welcome",
            "installed_summary": installed,
            "suggested_profile": suggested_profile,
            "message": self._generate_welcome_message(installed, suggested_profile)
        }
    
    def _generate_welcome_message(self, installed: Dict, profile: ProfileType) -> str:
        """Generate personalized welcome using consciousness"""
        context = {
            "installed_count": sum(len(v) for v in installed.values()),
            "categories": list(installed.keys()),
            "suggested_profile": profile.value
        }
        
        result = self.consciousness.process_intent(
            intent="generate setup welcome",
            context=context,
            persona="friendly_guide"
        )
        
        return result.get("message", "Welcome to your system setup!")
    
    def process_round(self, round_num: int, selections: List[str]) -> Dict[str, Any]:
        """Process a round of selections"""
        # Check for conflicts
        conflicts = self.package_intel.find_conflicts(selections)
        
        if conflicts:
            resolutions = self.conflict_resolver.resolve_conflicts(
                conflicts, 
                self.selected_profile
            )
            return {
                "stage": "conflict_resolution",
                "conflicts": conflicts,
                "resolutions": resolutions
            }
        
        # Add to selected packages
        self.selected_packages.extend(selections)
        
        # Create checkpoint
        self._create_checkpoint(round_num, selections)
        
        # Determine next round
        if round_num == 1:
            return self._round_two_specialized()
        elif round_num == 2:
            return self._round_three_personal()
        else:
            return self._final_round()
    
    def _create_checkpoint(self, round_num: int, packages: List[str]):
        """Create a rollback point"""
        checkpoint = {
            "round": round_num,
            "packages": packages,
            "timestamp": datetime.now(),
            "generation": self.package_intel.nix_api.create_generation()
        }
        self.checkpoints.append(checkpoint)
        
        # Store in trinity for learning
        self.trinity.store_temporal(
            f"setup_checkpoint_{round_num}",
            checkpoint
        )
    
    def natural_language_request(self, request: str) -> Dict[str, Any]:
        """Handle natural language package requests"""
        # Use existing intent recognition
        intent = self.package_intel.intent.recognize(request)
        
        # Find matching packages
        suggestions = self.package_intel.nix_api.search_packages(
            intent.get("search_term", request)
        )
        
        return {
            "request": request,
            "intent": intent,
            "suggestions": suggestions[:5]  # Top 5 matches
        }
    
    def finalize_setup(self) -> Dict[str, Any]:
        """Generate and apply final configuration"""
        # Generate NixOS config using existing generator
        config = self.profile_manager.profiles[self.selected_profile].to_nix_config()
        
        # Add selected packages
        for pkg in self.selected_packages:
            config += f"\n  environment.systemPackages = with pkgs; [ {pkg} ];"
        
        # Apply configuration
        result = self.package_intel.orchestrator.execute_intent({
            "action": "apply_configuration",
            "config": config
        })
        
        # Store in trinity for learning
        self.trinity.store_knowledge(TrinityKnowledge(
            id=f"setup_{datetime.now().isoformat()}",
            content=f"Setup completed with {len(self.selected_packages)} packages",
            metadata={
                "profile": self.selected_profile,
                "packages": self.selected_packages,
                "success": result.get("success", False)
            }
        ))
        
        return result