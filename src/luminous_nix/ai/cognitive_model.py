"""
Cognitive Modeling - AI That Understands What You Understand

Revolutionary capability: Track user UNDERSTANDING, not just commands.
Build a model of what concepts the user knows, adapting teaching accordingly.

This transforms AI from command executor to genuine teacher.
"""

from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


class ConceptConfidence(Enum):
    """User's confidence level with a concept"""
    UNKNOWN = 0.0          # Never encountered
    AWARE = 0.25           # Heard of it
    BASIC = 0.50           # Basic understanding
    INTERMEDIATE = 0.75    # Comfortable using
    EXPERT = 1.0           # Deep understanding


class EvidenceType(Enum):
    """Types of evidence for understanding"""
    ASKED_ABOUT = "asked_about"           # Asked a question about concept
    USED_CORRECTLY = "used_correctly"     # Used concept correctly
    USED_INCORRECTLY = "used_incorrectly" # Misused concept
    EXPLAINED_WELL = "explained_well"     # Could explain to others
    STRUGGLED_WITH = "struggled_with"     # Had difficulty
    SUCCEEDED_WITH = "succeeded_with"     # Successfully completed task
    FAILED_WITH = "failed_with"           # Failed at task involving concept


@dataclass
class Evidence:
    """Evidence of user understanding (or lack thereof)"""
    type: EvidenceType
    concept_id: str
    query: str           # What user said/did
    timestamp: float     # When it happened
    impact: float        # -1.0 to 1.0 (negative = decreased confidence)


@dataclass
class Concept:
    """A NixOS concept to track"""
    id: str
    name: str
    description: str
    prerequisites: List[str] = field(default_factory=list)  # Must understand these first
    related: List[str] = field(default_factory=list)        # Related concepts
    keywords: List[str] = field(default_factory=list)       # Trigger words

    # User's understanding
    confidence: float = 0.0                    # 0.0-1.0
    evidence: List[Evidence] = field(default_factory=list)
    first_encountered: Optional[float] = None
    last_interaction: Optional[float] = None


@dataclass
class LearningOpportunity:
    """A teaching moment identified by the system"""
    concept: Concept
    trigger: str              # What triggered this opportunity
    readiness: float          # 0.0-1.0 (1.0 = ready to learn)
    teaching_approach: str    # How to teach this
    priority: int             # 1=high, 2=medium, 3=low


class CognitiveModel:
    """
    Models user's understanding of NixOS concepts.

    Philosophy: Track UNDERSTANDING, not commands. Adapt teaching to
    what the user already knows and is ready to learn next.
    """

    def __init__(self, profile_path: Optional[Path] = None):
        """Initialize cognitive model"""
        self.profile_path = profile_path or Path.home() / ".luminous-nix" / "cognitive_model.json"

        # Define NixOS concept graph
        self.concepts: Dict[str, Concept] = self._build_concept_graph()

        # Load existing cognitive model if available
        self._load_model()

    def _build_concept_graph(self) -> Dict[str, Concept]:
        """
        Build graph of 20 core NixOS concepts to track.

        These are the fundamental concepts users need to understand
        to be effective with NixOS.
        """
        concepts = {}

        # 1. Declarative Configuration
        concepts['declarative'] = Concept(
            id='declarative',
            name='Declarative Configuration',
            description='NixOS describes desired state, not steps to achieve it',
            prerequisites=[],  # Foundational concept
            related=['imperative', 'generations', 'reproducible'],
            keywords=['declarative', 'describe', 'state', 'configuration.nix']
        )

        # 2. Imperative vs Declarative
        concepts['imperative'] = Concept(
            id='imperative',
            name='Imperative vs Declarative',
            description='Understanding the difference between "do this" and "make it like this"',
            prerequisites=[],
            related=['declarative'],
            keywords=['imperative', 'command', 'vs', 'difference']
        )

        # 3. Generations
        concepts['generations'] = Concept(
            id='generations',
            name='System Generations',
            description='Each rebuild creates a new generation - rollback safety net',
            prerequisites=['declarative'],
            related=['rollback', 'reproducible'],
            keywords=['generation', 'rollback', 'previous', 'boot menu']
        )

        # 4. Reproducibility
        concepts['reproducible'] = Concept(
            id='reproducible',
            name='Reproducibility',
            description='Same config = same system, always',
            prerequisites=['declarative'],
            related=['flakes', 'deterministic'],
            keywords=['reproducible', 'deterministic', 'same', 'consistent']
        )

        # 5. Nix Expression Language
        concepts['nix_lang'] = Concept(
            id='nix_lang',
            name='Nix Expression Language',
            description='Functional programming language for package definitions',
            prerequisites=[],
            related=['derivation', 'packages'],
            keywords=['nix expression', 'language', 'functional', 'lambda']
        )

        # 6. Packages
        concepts['packages'] = Concept(
            id='packages',
            name='Package Management',
            description='How NixOS manages software packages',
            prerequisites=['nix_lang'],
            related=['nixpkgs', 'derivation'],
            keywords=['package', 'install', 'nixpkgs', 'search']
        )

        # 7. Derivations
        concepts['derivation'] = Concept(
            id='derivation',
            name='Derivations',
            description='Build recipes that produce packages',
            prerequisites=['nix_lang', 'packages'],
            related=['store', 'build'],
            keywords=['derivation', 'drv', 'build', 'recipe']
        )

        # 8. Nix Store
        concepts['store'] = Concept(
            id='store',
            name='Nix Store',
            description='/nix/store - immutable package storage',
            prerequisites=['packages'],
            related=['derivation', 'hash'],
            keywords=['store', '/nix/store', 'immutable', 'hash']
        )

        # 9. Channels
        concepts['channels'] = Concept(
            id='channels',
            name='Channels',
            description='Traditional way to get package versions (being replaced by flakes)',
            prerequisites=['packages'],
            related=['flakes', 'unstable', 'stable'],
            keywords=['channel', 'nixos-', 'unstable', 'stable']
        )

        # 10. Flakes
        concepts['flakes'] = Concept(
            id='flakes',
            name='Flakes',
            description='Modern, reproducible way to manage dependencies with lock files',
            prerequisites=['reproducible', 'packages'],
            related=['channels', 'inputs', 'outputs'],
            keywords=['flake', 'flake.nix', 'flake.lock', 'inputs', 'outputs']
        )

        # 11. NixOS Modules
        concepts['modules'] = Concept(
            id='modules',
            name='NixOS Modules',
            description='Composable configuration units',
            prerequisites=['declarative'],
            related=['options', 'services'],
            keywords=['module', 'imports', 'config', 'options']
        )

        # 12. Options
        concepts['options'] = Concept(
            id='options',
            name='Configuration Options',
            description='Available settings you can configure',
            prerequisites=['modules'],
            related=['services', 'enable'],
            keywords=['options', 'enable', 'configure', 'set']
        )

        # 13. Services
        concepts['services'] = Concept(
            id='services',
            name='System Services',
            description='Background processes (nginx, postgresql, etc.)',
            prerequisites=['options'],
            related=['systemd', 'enable'],
            keywords=['service', 'services.', 'systemd', 'daemon']
        )

        # 14. Home Manager
        concepts['home_manager'] = Concept(
            id='home_manager',
            name='Home Manager',
            description='Declarative user environment configuration',
            prerequisites=['declarative', 'modules'],
            related=['dotfiles', 'user'],
            keywords=['home-manager', 'home.', 'dotfiles', 'user config']
        )

        # 15. NixOS Rebuild
        concepts['rebuild'] = Concept(
            id='rebuild',
            name='nixos-rebuild',
            description='Command to apply configuration changes',
            prerequisites=['declarative', 'generations'],
            related=['switch', 'boot', 'test'],
            keywords=['rebuild', 'switch', 'boot', 'test', 'apply']
        )

        # 16. Development Shells
        concepts['dev_shell'] = Concept(
            id='dev_shell',
            name='Development Shells',
            description='Isolated development environments with nix-shell or nix develop',
            prerequisites=['packages', 'flakes'],
            related=['shell.nix', 'dependencies'],
            keywords=['nix-shell', 'nix develop', 'shell.nix', 'dev environment']
        )

        # 17. Overlays
        concepts['overlays'] = Concept(
            id='overlays',
            name='Overlays',
            description='Modify or extend nixpkgs',
            prerequisites=['packages', 'nix_lang'],
            related=['nixpkgs', 'override'],
            keywords=['overlay', 'override', 'modify package']
        )

        # 18. Garbage Collection
        concepts['gc'] = Concept(
            id='gc',
            name='Garbage Collection',
            description='Clean up old generations and unused packages',
            prerequisites=['generations', 'store'],
            related=['disk space', 'cleanup'],
            keywords=['garbage', 'collect', 'gc', 'cleanup', 'disk']
        )

        # 19. System Configuration
        concepts['system_config'] = Concept(
            id='system_config',
            name='System-Wide Configuration',
            description='Hardware, networking, users, services in configuration.nix',
            prerequisites=['declarative', 'modules'],
            related=['configuration.nix', 'hardware'],
            keywords=['configuration.nix', 'system', 'hardware', 'networking']
        )

        # 20. Rollback
        concepts['rollback'] = Concept(
            id='rollback',
            name='Rollback & Recovery',
            description='Boot into previous generation if something breaks',
            prerequisites=['generations'],
            related=['boot menu', 'recovery'],
            keywords=['rollback', 'previous', 'boot menu', 'recovery', 'undo']
        )

        return concepts

    def record_interaction(self, query: str, success: bool = True) -> List[LearningOpportunity]:
        """
        Record user interaction and update cognitive model.

        Args:
            query: What the user said/did
            success: Whether the interaction was successful

        Returns:
            List of learning opportunities identified
        """
        import time
        timestamp = time.time()
        query_lower = query.lower()

        opportunities = []

        # Detect which concepts are involved in this query
        involved_concepts = self._detect_concepts(query_lower)

        for concept_id in involved_concepts:
            concept = self.concepts[concept_id]

            # Record evidence
            if success:
                evidence_type = EvidenceType.USED_CORRECTLY
                impact = 0.15  # Positive impact
            else:
                evidence_type = EvidenceType.STRUGGLED_WITH
                impact = -0.05  # Small negative impact

            evidence = Evidence(
                type=evidence_type,
                concept_id=concept_id,
                query=query,
                timestamp=timestamp,
                impact=impact
            )

            concept.evidence.append(evidence)

            # Update confidence (Bayesian-ish update)
            concept.confidence = max(0.0, min(1.0, concept.confidence + impact))

            # Track first encounter and last interaction
            if concept.first_encountered is None:
                concept.first_encountered = timestamp
            concept.last_interaction = timestamp

        # Identify learning opportunities
        opportunities = self._identify_learning_opportunities(query_lower, involved_concepts)

        # Save updated model
        self._save_model()

        return opportunities

    def _detect_concepts(self, query: str) -> Set[str]:
        """Detect which concepts are mentioned in query"""
        detected = set()

        for concept_id, concept in self.concepts.items():
            # Check if any keywords match
            for keyword in concept.keywords:
                if keyword.lower() in query:
                    detected.add(concept_id)
                    break

        return detected

    def _identify_learning_opportunities(self, query: str, involved_concepts: Set[str]) -> List[LearningOpportunity]:
        """
        Identify concepts user is ready to learn.

        Logic:
        - Prerequisites met (confidence > 0.5)
        - User showed interest (mentioned in query or related concepts)
        - Haven't learned yet (confidence < 0.5)
        """
        opportunities = []

        for concept_id, concept in self.concepts.items():
            # Skip if already understood
            if concept.confidence >= 0.5:
                continue

            # Check if prerequisites are met
            prereq_met = all(
                self.concepts[prereq].confidence >= 0.5
                for prereq in concept.prerequisites
            )

            if not prereq_met:
                continue

            # Check if related to what user is doing
            is_related = (
                concept_id in involved_concepts or
                any(rel in involved_concepts for rel in concept.related)
            )

            if is_related:
                readiness = self._calculate_readiness(concept)

                opportunity = LearningOpportunity(
                    concept=concept,
                    trigger=query,
                    readiness=readiness,
                    teaching_approach=self._suggest_teaching_approach(concept),
                    priority=1 if readiness > 0.7 else 2 if readiness > 0.4 else 3
                )

                opportunities.append(opportunity)

        # Sort by readiness (highest first)
        opportunities.sort(key=lambda o: o.readiness, reverse=True)

        return opportunities[:3]  # Top 3 opportunities

    def _calculate_readiness(self, concept: Concept) -> float:
        """
        Calculate how ready user is to learn this concept.

        Factors:
        - Prerequisites met (required)
        - Related concepts understood (helpful)
        - Recent interest (timely)
        """
        # Check prerequisites (must be met)
        prereq_confidence = sum(
            self.concepts[prereq].confidence
            for prereq in concept.prerequisites
        ) / max(len(concept.prerequisites), 1)

        if prereq_confidence < 0.5:
            return 0.0  # Not ready if prerequisites not met

        # Check related concepts
        related_confidence = sum(
            self.concepts[rel].confidence
            for rel in concept.related
            if rel in self.concepts
        ) / max(len(concept.related), 1)

        # Calculate readiness score
        readiness = (
            prereq_confidence * 0.6 +  # Prerequisites are most important
            related_confidence * 0.3 +  # Related concepts help
            0.1                         # Base readiness
        )

        return min(1.0, readiness)

    def _suggest_teaching_approach(self, concept: Concept) -> str:
        """Suggest how to teach this concept based on user's level"""

        # Count how many concepts user knows
        known_count = sum(1 for c in self.concepts.values() if c.confidence >= 0.5)

        if known_count < 5:
            # Beginner - need lots of context
            return f"Start with basics of {concept.name}. Use analogies to familiar concepts. Provide step-by-step guidance."
        elif known_count < 10:
            # Intermediate - can handle more detail
            return f"Explain {concept.name} with examples. Connect to what they already know. Provide practical use cases."
        else:
            # Advanced - prefer concise, technical
            return f"Give concise explanation of {concept.name}. Focus on practical application and edge cases."

    def get_knowledge_summary(self) -> Dict[str, any]:
        """Get summary of user's knowledge"""

        # Categorize by confidence
        expert = [c for c in self.concepts.values() if c.confidence >= 0.75]
        intermediate = [c for c in self.concepts.values() if 0.5 <= c.confidence < 0.75]
        basic = [c for c in self.concepts.values() if 0.25 <= c.confidence < 0.5]
        unknown = [c for c in self.concepts.values() if c.confidence < 0.25]

        return {
            'total_concepts': len(self.concepts),
            'expert': len(expert),
            'intermediate': len(intermediate),
            'basic': len(basic),
            'unknown': len(unknown),
            'overall_confidence': sum(c.confidence for c in self.concepts.values()) / len(self.concepts),
            'expert_concepts': [c.name for c in expert],
            'intermediate_concepts': [c.name for c in intermediate],
            'basic_concepts': [c.name for c in basic],
            'ready_to_learn': [c.name for c in unknown if self._calculate_readiness(c) > 0.5]
        }

    def _save_model(self):
        """Save cognitive model to disk"""
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to JSON-serializable format
        data = {
            'concepts': {
                cid: {
                    'confidence': c.confidence,
                    'evidence': [
                        {
                            'type': e.type.value,
                            'query': e.query,
                            'timestamp': e.timestamp,
                            'impact': e.impact
                        }
                        for e in c.evidence
                    ],
                    'first_encountered': c.first_encountered,
                    'last_interaction': c.last_interaction
                }
                for cid, c in self.concepts.items()
            }
        }

        with open(self.profile_path, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_model(self):
        """Load existing cognitive model"""
        if not self.profile_path.exists():
            return

        try:
            with open(self.profile_path) as f:
                data = json.load(f)

            # Restore concept state
            for cid, cdata in data.get('concepts', {}).items():
                if cid in self.concepts:
                    concept = self.concepts[cid]
                    concept.confidence = cdata.get('confidence', 0.0)
                    concept.first_encountered = cdata.get('first_encountered')
                    concept.last_interaction = cdata.get('last_interaction')

                    # Restore evidence
                    for edata in cdata.get('evidence', []):
                        evidence = Evidence(
                            type=EvidenceType(edata['type']),
                            concept_id=cid,
                            query=edata['query'],
                            timestamp=edata['timestamp'],
                            impact=edata['impact']
                        )
                        concept.evidence.append(evidence)
        except Exception as e:
            print(f"Warning: Could not load cognitive model: {e}")


def get_cognitive_model() -> CognitiveModel:
    """Get singleton instance of cognitive model"""
    global _cognitive_model

    if _cognitive_model is None:
        _cognitive_model = CognitiveModel()

    return _cognitive_model


# Singleton
_cognitive_model: Optional[CognitiveModel] = None
