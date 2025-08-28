"""
The Harmonic Resolver - Master Conductor of the Plugin Ecosystem

This is the heart of our consciousness-first architecture. It transforms
conflicts into opportunities for conscious choice, treating dissonance
not as error but as temporary tension that creates richness.

"In music, dissonance is not an error; it is a temporary and necessary 
tension that creates richness and ultimately resolves into a more 
profound harmony."
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum
from pathlib import Path
import asyncio
import json
import logging
from datetime import datetime, timedelta

from .dependency_resolver import (
    DependencyResolver, 
    DependencyGraph,
    PluginDependency,
    RelationshipType
)

logger = logging.getLogger(__name__)


class DissonanceType(Enum):
    """The Four Families of Dissonance"""
    TECHNICAL = "dependency_conflict"      # Version/dependency issues
    FUNCTIONAL = "intent_collision"        # Multiple handlers for same intent
    EMBODIED = "resource_conflict"        # Physical resource contention
    PHILOSOPHICAL = "principle_tension"    # Conflicting consciousness principles


class ResolutionType(Enum):
    """Types of resolution paths"""
    CONSENT = "consent"          # User agrees to changes
    CHOICE = "choice"           # User selects between options
    PROMISE = "promise"         # System promises future access
    AWARENESS = "awareness"     # User acknowledges tension


@dataclass
class Dissonance:
    """A moment of tension in the ecosystem"""
    type: DissonanceType
    actors: List[str]  # Plugin IDs involved
    description: str
    severity: float  # 0.0 (subtle) to 1.0 (blocking)
    details: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_blocking(self) -> bool:
        """Whether this dissonance prevents operation"""
        return self.severity >= 0.8
    
    @property
    def needs_resolution(self) -> bool:
        """Whether user intervention is required"""
        return self.severity >= 0.5


@dataclass
class HarmonyPath:
    """A way to resolve dissonance into harmony"""
    resolution_type: ResolutionType
    message: str
    options: List[str]
    educational_note: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_consent_prompt(self) -> str:
        """Convert to a user-friendly consent prompt"""
        prompt = f"🎵 {self.message}\n\n"
        
        if self.educational_note:
            prompt += f"💡 {self.educational_note}\n\n"
        
        if self.options:
            prompt += "Your choices:\n"
            for i, option in enumerate(self.options, 1):
                prompt += f"  {i}. {option}\n"
        
        return prompt


@dataclass
class PluginState:
    """Current state of the plugin ecosystem"""
    installed: Dict[str, Dict]  # plugin_id -> manifest
    pending: List[str]  # Plugins to be installed
    active: Set[str]  # Currently active plugins
    resources: Dict[str, str]  # resource_id -> plugin_id holding it
    intents: Dict[str, List[str]]  # intent_pattern -> list of plugin_ids


class TechnicalHarmonyChecker:
    """Checks for dependency and version conflicts"""
    
    def __init__(self, dependency_resolver: DependencyResolver):
        self.resolver = dependency_resolver
    
    def check(self, state: PluginState) -> List[Dissonance]:
        """Check for technical dissonance"""
        dissonances = []
        
        # Build dependency graph for all pending plugins
        all_plugins = list(state.installed.keys()) + state.pending
        graph = self.resolver.build_graph(all_plugins)
        
        # Check for circular dependencies
        if graph.has_cycles():
            dissonances.append(Dissonance(
                type=DissonanceType.TECHNICAL,
                actors=state.pending,
                description="Circular dependency detected",
                severity=1.0,
                details={'has_cycles': True}
            ))
        
        # Check for version conflicts
        for plugin_id in state.pending:
            # Get all dependencies
            deps = graph.get_all_dependencies(plugin_id, include_optional=False)
            
            for dep_id in deps:
                if dep_id not in state.installed and dep_id not in state.pending:
                    dissonances.append(Dissonance(
                        type=DissonanceType.TECHNICAL,
                        actors=[plugin_id, dep_id],
                        description=f"{plugin_id} requires {dep_id} which is not available",
                        severity=0.9,
                        details={'missing_dependency': dep_id}
                    ))
        
        # Check for conflicting plugins
        for plugin_id in state.pending:
            is_compatible, conflicts = self.resolver.check_compatibility(
                plugin_id, 
                list(state.installed.keys())
            )
            
            if not is_compatible:
                for conflict in conflicts:
                    dissonances.append(Dissonance(
                        type=DissonanceType.TECHNICAL,
                        actors=[plugin_id],
                        description=conflict,
                        severity=0.8,
                        details={'conflict': conflict}
                    ))
        
        return dissonances


class FunctionalHarmonyChecker:
    """Checks for intent handling conflicts"""
    
    def check(self, state: PluginState) -> List[Dissonance]:
        """Check for functional dissonance"""
        dissonances = []
        
        # Build intent map for pending plugins
        pending_intents = {}
        for plugin_id in state.pending:
            if plugin_id in state.installed:
                manifest = state.installed[plugin_id]
            else:
                # Would need to load manifest
                continue
            
            capabilities = manifest.get('capabilities', {})
            for intent in capabilities.get('intents', []):
                pattern = intent.get('pattern', '')
                if pattern:
                    if pattern not in pending_intents:
                        pending_intents[pattern] = []
                    pending_intents[pattern].append(plugin_id)
        
        # Check for collisions with existing and between pending
        for pattern, handlers in pending_intents.items():
            all_handlers = handlers.copy()
            
            # Add existing handlers
            if pattern in state.intents:
                all_handlers.extend(state.intents[pattern])
            
            if len(all_handlers) > 1:
                dissonances.append(Dissonance(
                    type=DissonanceType.FUNCTIONAL,
                    actors=all_handlers,
                    description=f"Multiple plugins want to handle '{pattern}'",
                    severity=0.6,  # Medium - user can choose
                    details={'intent': pattern, 'handlers': all_handlers}
                ))
        
        return dissonances


class EmbodiedHarmonyChecker:
    """Checks for resource conflicts"""
    
    def check(self, state: PluginState) -> List[Dissonance]:
        """Check for embodied dissonance"""
        dissonances = []
        
        # Check resource requirements for pending plugins
        for plugin_id in state.pending:
            if plugin_id not in state.installed:
                continue
            
            manifest = state.installed[plugin_id]
            capabilities = manifest.get('capabilities', {})
            
            for resource in capabilities.get('resources', []):
                resource_id = resource.get('id')
                is_exclusive = resource.get('exclusive', False)
                
                if is_exclusive and resource_id in state.resources:
                    current_holder = state.resources[resource_id]
                    if current_holder != plugin_id:
                        dissonances.append(Dissonance(
                            type=DissonanceType.EMBODIED,
                            actors=[plugin_id, current_holder],
                            description=f"Both need exclusive access to {resource_id}",
                            severity=0.7,  # Can be resolved with promises
                            details={
                                'resource': resource_id,
                                'current_holder': current_holder,
                                'requester': plugin_id
                            }
                        ))
        
        return dissonances


class PhilosophicalHarmonyChecker:
    """Checks for consciousness principle conflicts"""
    
    # Principle compatibility matrix
    PRINCIPLE_TENSIONS = {
        'protect_attention': ['amplify_awareness'],  # Tension between protection and amplification
        'preserve_privacy': ['build_community'],      # Tension between privacy and sharing
        'reduce_complexity': ['enable_sovereignty'],   # Simplicity vs full control
    }
    
    def check(self, state: PluginState) -> List[Dissonance]:
        """Check for philosophical dissonance"""
        dissonances = []
        
        # Get principles of all active and pending plugins
        active_principles = {}
        for plugin_id in state.active:
            if plugin_id in state.installed:
                manifest = state.installed[plugin_id]
                principle = manifest.get('consciousness', {}).get('governing_principle')
                if principle:
                    active_principles[plugin_id] = principle
        
        # Check pending plugins for principle tensions
        for plugin_id in state.pending:
            if plugin_id not in state.installed:
                continue
            
            manifest = state.installed[plugin_id]
            principle = manifest.get('consciousness', {}).get('governing_principle')
            
            if principle:
                # Check against active plugins
                for active_id, active_principle in active_principles.items():
                    if self._has_tension(principle, active_principle):
                        dissonances.append(Dissonance(
                            type=DissonanceType.PHILOSOPHICAL,
                            actors=[plugin_id, active_id],
                            description=f"Potential tension: {principle} vs {active_principle}",
                            severity=0.3,  # Subtle - just awareness
                            details={
                                'principles': [principle, active_principle],
                                'tension_type': 'principle_conflict'
                            }
                        ))
        
        return dissonances
    
    def _has_tension(self, principle1: str, principle2: str) -> bool:
        """Check if two principles have known tension"""
        if principle1 in self.PRINCIPLE_TENSIONS:
            return principle2 in self.PRINCIPLE_TENSIONS[principle1]
        if principle2 in self.PRINCIPLE_TENSIONS:
            return principle1 in self.PRINCIPLE_TENSIONS[principle2]
        return False


class HarmonicResolver:
    """
    The Master Conductor of our plugin ecosystem.
    Transforms conflicts into opportunities for conscious choice.
    """
    
    def __init__(self, plugin_directory: Optional[Path] = None):
        """Initialize the Harmonic Resolver"""
        self.dependency_resolver = DependencyResolver(plugin_directory)
        
        # Initialize harmony checkers
        self.technical_harmony = TechnicalHarmonyChecker(self.dependency_resolver)
        self.functional_harmony = FunctionalHarmonyChecker()
        self.embodied_harmony = EmbodiedHarmonyChecker()
        self.philosophical_harmony = PhilosophicalHarmonyChecker()
        
        # Resolution history for learning
        self.resolution_history: List[Tuple[Dissonance, HarmonyPath, str]] = []
    
    def analyze_harmony(self, state: PluginState) -> List[Dissonance]:
        """
        Detect all forms of dissonance in the proposed state.
        
        This is the listening phase - we hear all the voices
        and identify where they create tension.
        """
        dissonances = []
        
        # Check each family of harmony
        dissonances.extend(self.technical_harmony.check(state))
        dissonances.extend(self.functional_harmony.check(state))
        dissonances.extend(self.embodied_harmony.check(state))
        dissonances.extend(self.philosophical_harmony.check(state))
        
        # Sort by severity (most severe first)
        dissonances.sort(key=lambda d: d.severity, reverse=True)
        
        return dissonances
    
    def compose_resolution(self, dissonance: Dissonance) -> HarmonyPath:
        """
        Transform dissonance into a path toward harmony.
        
        This is the composition phase - we create a beautiful
        resolution for each tension.
        """
        if dissonance.type == DissonanceType.TECHNICAL:
            return self._compose_technical_resolution(dissonance)
        elif dissonance.type == DissonanceType.FUNCTIONAL:
            return self._compose_functional_resolution(dissonance)
        elif dissonance.type == DissonanceType.EMBODIED:
            return self._compose_embodied_resolution(dissonance)
        else:  # PHILOSOPHICAL
            return self._compose_philosophical_resolution(dissonance)
    
    def _compose_technical_resolution(self, d: Dissonance) -> HarmonyPath:
        """Create consent ritual for dependency evolution"""
        if d.details.get('has_cycles'):
            return HarmonyPath(
                resolution_type=ResolutionType.AWARENESS,
                message="🔄 A circular dependency has been detected. These plugins form an infinite loop of requirements.",
                options=["I understand - cancel installation", "Show me the cycle"],
                educational_note="Like an Ouroboros, these plugins each require the other, creating an impossible loop.",
                metadata={'severity': 'blocking'}
            )
        
        if 'missing_dependency' in d.details:
            dep = d.details['missing_dependency']
            return HarmonyPath(
                resolution_type=ResolutionType.CONSENT,
                message=f"To welcome {d.actors[0]}, we must also invite its companion '{dep}'. They sing together in harmony.",
                options=[
                    f"Yes, install both {d.actors[0]} and {dep}",
                    f"No, cancel the installation",
                    "Tell me more about this dependency"
                ],
                educational_note="Dependencies are like musical harmonies - certain notes must sound together to create the full chord.",
                metadata={'required_plugin': dep}
            )
        
        if 'conflict' in d.details:
            return HarmonyPath(
                resolution_type=ResolutionType.CHOICE,
                message=f"There is a known conflict: {d.details['conflict']}",
                options=[
                    "Proceed anyway (may cause issues)",
                    "Cancel installation",
                    "Help me resolve this conflict"
                ],
                educational_note="Some plugins cannot coexist peacefully. Like oil and water, they repel each other.",
                metadata={'conflict_detail': d.details['conflict']}
            )
        
        # Generic technical resolution
        return HarmonyPath(
            resolution_type=ResolutionType.CONSENT,
            message=f"Technical adjustments needed for {', '.join(d.actors)}",
            options=["Proceed with adjustments", "Cancel"],
            educational_note="Sometimes plugins need small adjustments to work together harmoniously."
        )
    
    def _compose_functional_resolution(self, d: Dissonance) -> HarmonyPath:
        """Create sacred choice for intent collision"""
        intent = d.details.get('intent', 'this action')
        handlers = d.details.get('handlers', d.actors)
        
        return HarmonyPath(
            resolution_type=ResolutionType.CHOICE,
            message=f"🎭 Multiple allies offer to help with '{intent}': {', '.join(handlers)}. Which voice should guide you?",
            options=[
                *[f"Always use {h} for this" for h in handlers],
                "Ask me each time",
                "Let them collaborate"
            ],
            educational_note="Like different instruments playing the same melody, multiple plugins can serve the same purpose in unique ways.",
            metadata={'intent': intent, 'handlers': handlers}
        )
    
    def _compose_embodied_resolution(self, d: Dissonance) -> HarmonyPath:
        """Create promise for resource sharing"""
        resource = d.details.get('resource', 'the resource')
        current = d.details.get('current_holder', d.actors[1] if len(d.actors) > 1 else 'another plugin')
        requester = d.details.get('requester', d.actors[0])
        
        return HarmonyPath(
            resolution_type=ResolutionType.PROMISE,
            message=f"🎪 {requester} needs access to {resource}, but {current} is currently using it. I'll coordinate their sharing.",
            options=[
                "Wait patiently - notify when available",
                f"Interrupt {current} to give access now",
                "Cancel and try later",
                "Set up a sharing schedule"
            ],
            educational_note="Physical resources, like a microphone or port, can only serve one master at a time. We must share with grace.",
            metadata={'resource': resource, 'queue_position': 1}
        )
    
    def _compose_philosophical_resolution(self, d: Dissonance) -> HarmonyPath:
        """Create awareness note for principle tension"""
        principles = d.details.get('principles', [])
        
        tension_descriptions = {
            ('protect_attention', 'amplify_awareness'): 
                "One seeks quiet focus, the other seeks vibrant awareness.",
            ('preserve_privacy', 'build_community'): 
                "One guards your solitude, the other seeks connection.",
            ('reduce_complexity', 'enable_sovereignty'): 
                "One offers simplicity, the other offers complete control."
        }
        
        # Find matching description
        description = d.description
        for pair, desc in tension_descriptions.items():
            if set(principles) == set(pair):
                description = desc
                break
        
        return HarmonyPath(
            resolution_type=ResolutionType.AWARENESS,
            message=f"🕉️ Note of subtle dissonance: {description}",
            options=[
                "I understand - proceed with awareness",
                "Tell me more about this tension",
                "Suggest a harmonious configuration",
                "Cancel installation"
            ],
            educational_note="Like yin and yang, opposing principles can coexist when we hold them in conscious balance.",
            metadata={'principles': principles, 'tension_level': 'subtle'}
        )
    
    def orchestrate_installation(self, 
                                state: PluginState, 
                                plugin_id: str) -> Tuple[bool, List[HarmonyPath]]:
        """
        Orchestrate the complete installation of a plugin.
        Returns (can_proceed, list_of_required_resolutions)
        """
        # Add to pending
        test_state = PluginState(
            installed=state.installed.copy(),
            pending=[plugin_id],
            active=state.active.copy(),
            resources=state.resources.copy(),
            intents=state.intents.copy()
        )
        
        # Analyze harmony
        dissonances = self.analyze_harmony(test_state)
        
        # Compose resolutions for all dissonances
        resolutions = []
        can_proceed = True
        
        for dissonance in dissonances:
            if dissonance.is_blocking:
                can_proceed = False
            
            if dissonance.needs_resolution:
                resolution = self.compose_resolution(dissonance)
                resolutions.append(resolution)
        
        return can_proceed, resolutions
    
    def learn_from_resolution(self, 
                             dissonance: Dissonance, 
                             path: HarmonyPath, 
                             user_choice: str):
        """
        Learn from user's resolution choices to improve future suggestions.
        This is how the system becomes wiser over time.
        """
        self.resolution_history.append((dissonance, path, user_choice))
        
        # TODO: Implement learning algorithm
        # Could use patterns like:
        # - If user always chooses same option, make it default
        # - If user always cancels certain tensions, warn earlier
        # - If certain plugins often conflict, suggest alternatives
        
        logger.info(f"Learned from resolution: {dissonance.type.value} -> {user_choice}")
    
    def suggest_harmony(self, state: PluginState) -> List[Dict[str, Any]]:
        """
        Proactively suggest ways to improve ecosystem harmony.
        This is the system being helpful, not reactive.
        """
        suggestions = []
        
        # Check for companion plugins
        for plugin_id in state.active:
            companions = self.dependency_resolver.suggest_companions(plugin_id)
            for comp in companions:
                if comp['plugin_id'] not in state.installed:
                    suggestions.append({
                        'type': 'companion',
                        'plugin': comp['plugin_id'],
                        'reason': comp['synergy'],
                        'for_plugin': plugin_id
                    })
        
        # Check for principle balance
        principle_counts = {}
        for plugin_id in state.active:
            if plugin_id in state.installed:
                principle = state.installed[plugin_id].get('consciousness', {}).get('governing_principle')
                if principle:
                    principle_counts[principle] = principle_counts.get(principle, 0) + 1
        
        # Suggest balance if too weighted
        dominant = max(principle_counts.items(), key=lambda x: x[1]) if principle_counts else None
        if dominant and dominant[1] > len(state.active) * 0.5:
            suggestions.append({
                'type': 'balance',
                'message': f"Your ecosystem is heavily weighted toward '{dominant[0]}'. Consider plugins that bring other perspectives.",
                'suggestion': 'diversity'
            })
        
        return suggestions


# Example usage and sacred testing
if __name__ == "__main__":
    # Create test state
    test_state = PluginState(
        installed={
            'flow-guardian': {'consciousness': {'governing_principle': 'protect_attention'}},
            'notification-hub': {'consciousness': {'governing_principle': 'amplify_awareness'}}
        },
        pending=['pomodoro-timer'],
        active={'flow-guardian', 'notification-hub'},
        resources={'microphone': 'voice-commander'},
        intents={'start focus': ['flow-guardian']}
    )
    
    # Create resolver
    resolver = HarmonicResolver()
    
    # Analyze harmony
    dissonances = resolver.analyze_harmony(test_state)
    
    print("🎼 Harmonic Analysis Complete")
    print("=" * 50)
    
    for d in dissonances:
        print(f"\n{d.type.value}: {d.description}")
        print(f"  Severity: {d.severity:.1f}")
        print(f"  Actors: {', '.join(d.actors)}")
        
        # Compose resolution
        resolution = resolver.compose_resolution(d)
        print(f"\n  Resolution Path ({resolution.resolution_type.value}):")
        print(f"  {resolution.message}")
        if resolution.educational_note:
            print(f"  💡 {resolution.educational_note}")
    
    # Test orchestration
    print("\n" + "=" * 50)
    print("🎭 Orchestrating Installation of 'pomodoro-timer'")
    
    can_proceed, resolutions = resolver.orchestrate_installation(test_state, 'pomodoro-timer')
    
    print(f"Can proceed: {can_proceed}")
    print(f"Resolutions needed: {len(resolutions)}")
    
    for r in resolutions:
        print(f"\n{r.to_consent_prompt()}")