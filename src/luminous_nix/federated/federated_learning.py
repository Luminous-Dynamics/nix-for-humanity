"""
Federated Learning Network for Luminous Nix
Privacy-preserving collective intelligence through democratic model evolution
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json
import numpy as np
from pathlib import Path
import logging
import asyncio
from collections import defaultdict

logger = logging.getLogger(__name__)


class PrivacyLevel(Enum):
    """Privacy levels for federated learning"""
    PUBLIC = "public"           # Share everything
    DIFFERENTIAL = "differential"  # Add noise for privacy
    ENCRYPTED = "encrypted"      # Homomorphic encryption
    LOCAL_ONLY = "local_only"    # Don't share


class ModelType(Enum):
    """Types of models in federated network"""
    INTENT_RECOGNITION = "intent_recognition"
    ERROR_PATTERNS = "error_patterns"
    UI_PREFERENCES = "ui_preferences"
    LEARNING_PATHS = "learning_paths"
    COMMAND_PREDICTION = "command_prediction"
    PERSONA_EVOLUTION = "persona_evolution"


class VoteType(Enum):
    """Democratic voting mechanisms"""
    SIMPLE_MAJORITY = "simple_majority"      # >50%
    SUPER_MAJORITY = "super_majority"        # >66%
    CONSENSUS = "consensus"                  # >90%
    WEIGHTED = "weighted"                    # Based on contribution


@dataclass
class ModelUpdate:
    """Represents a model update from a participant"""
    participant_id: str
    model_type: ModelType
    timestamp: datetime
    weights: Dict[str, np.ndarray]
    metrics: Dict[str, float]
    privacy_level: PrivacyLevel
    contribution_score: float = 0.0
    signature: Optional[str] = None
    
    def apply_differential_privacy(self, epsilon: float = 1.0):
        """Apply differential privacy noise to weights"""
        for key, weight in self.weights.items():
            noise = np.random.laplace(0, 1/epsilon, weight.shape)
            self.weights[key] = weight + noise
    
    def compute_signature(self) -> str:
        """Compute cryptographic signature of update"""
        data = json.dumps({
            'participant': self.participant_id,
            'type': self.model_type.value,
            'timestamp': self.timestamp.isoformat(),
            'weights_hash': self._hash_weights()
        }, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _hash_weights(self) -> str:
        """Create hash of weight values"""
        weight_data = ""
        for key in sorted(self.weights.keys()):
            weight_data += f"{key}:{self.weights[key].sum():.6f};"
        return hashlib.md5(weight_data.encode()).hexdigest()


@dataclass
class CollectiveDecision:
    """Represents a democratic decision in the network"""
    decision_id: str
    proposal: str
    proposer_id: str
    vote_type: VoteType
    created_at: datetime
    expires_at: datetime
    votes: Dict[str, bool] = field(default_factory=dict)
    weights: Dict[str, float] = field(default_factory=dict)
    status: str = "pending"  # pending, approved, rejected, expired
    implementation: Optional[Dict[str, Any]] = None
    
    def add_vote(self, participant_id: str, vote: bool, weight: float = 1.0):
        """Add a vote to the decision"""
        self.votes[participant_id] = vote
        self.weights[participant_id] = weight
    
    def calculate_result(self) -> Tuple[bool, float]:
        """Calculate voting result based on vote type"""
        if not self.votes:
            return False, 0.0
        
        if self.vote_type == VoteType.WEIGHTED:
            total_weight = sum(self.weights.values())
            positive_weight = sum(w for p, w in self.weights.items() 
                                if self.votes.get(p, False))
            approval_rate = positive_weight / total_weight if total_weight > 0 else 0
        else:
            positive_votes = sum(1 for v in self.votes.values() if v)
            approval_rate = positive_votes / len(self.votes)
        
        thresholds = {
            VoteType.SIMPLE_MAJORITY: 0.5,
            VoteType.SUPER_MAJORITY: 0.66,
            VoteType.CONSENSUS: 0.9,
            VoteType.WEIGHTED: 0.5
        }
        
        threshold = thresholds.get(self.vote_type, 0.5)
        return approval_rate > threshold, approval_rate


@dataclass
class NetworkParticipant:
    """Represents a participant in federated network"""
    participant_id: str
    joined_at: datetime
    contribution_score: float = 0.0
    models_shared: int = 0
    votes_cast: int = 0
    privacy_preference: PrivacyLevel = PrivacyLevel.DIFFERENTIAL
    trusted_peers: Set[str] = field(default_factory=set)
    reputation: float = 1.0  # 0.0 to 1.0
    last_active: datetime = field(default_factory=datetime.now)
    
    def update_reputation(self, delta: float):
        """Update participant reputation"""
        self.reputation = max(0.0, min(1.0, self.reputation + delta))
        
    def calculate_voting_weight(self) -> float:
        """Calculate voting weight based on contribution and reputation"""
        base_weight = 1.0
        contribution_bonus = min(self.contribution_score / 100, 1.0)
        reputation_multiplier = self.reputation
        return base_weight * (1 + contribution_bonus) * reputation_multiplier


class FederatedLearningNetwork:
    """
    Main federated learning coordinator
    Manages privacy-preserving model sharing and collective intelligence
    """
    
    def __init__(self, 
                 participant_id: str,
                 storage_path: Path = Path("~/.luminous-nix/federated"),
                 privacy_level: PrivacyLevel = PrivacyLevel.DIFFERENTIAL):
        self.participant_id = participant_id
        self.storage_path = storage_path.expanduser()
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.privacy_level = privacy_level
        
        # Network state
        self.participants: Dict[str, NetworkParticipant] = {}
        self.model_updates: Dict[ModelType, List[ModelUpdate]] = defaultdict(list)
        self.decisions: Dict[str, CollectiveDecision] = {}
        self.local_models: Dict[ModelType, Any] = {}
        
        # Configuration
        self.min_participants = 3  # Minimum for federated averaging
        self.update_frequency = timedelta(hours=6)
        self.decision_timeout = timedelta(days=3)
        self.differential_epsilon = 1.0  # Privacy budget
        
        # Metrics
        self.metrics = {
            'updates_shared': 0,
            'updates_received': 0,
            'decisions_participated': 0,
            'collective_improvements': 0
        }
        
        # Initialize self as participant
        self.self_participant = NetworkParticipant(
            participant_id=participant_id,
            joined_at=datetime.now(),
            privacy_preference=privacy_level
        )
        self.participants[participant_id] = self.self_participant
        
    async def share_model_update(self, 
                                model_type: ModelType,
                                weights: Dict[str, np.ndarray],
                                metrics: Dict[str, float]) -> ModelUpdate:
        """Share a model update with the network"""
        update = ModelUpdate(
            participant_id=self.participant_id,
            model_type=model_type,
            timestamp=datetime.now(),
            weights=weights.copy(),
            metrics=metrics,
            privacy_level=self.privacy_level
        )
        
        # Apply privacy preservation
        if self.privacy_level == PrivacyLevel.DIFFERENTIAL:
            update.apply_differential_privacy(self.differential_epsilon)
        elif self.privacy_level == PrivacyLevel.ENCRYPTED:
            # TODO: Implement homomorphic encryption
            pass
        
        # Sign the update
        update.signature = update.compute_signature()
        
        # Store locally
        self.model_updates[model_type].append(update)
        
        # Update metrics
        self.metrics['updates_shared'] += 1
        self.self_participant.models_shared += 1
        self.self_participant.contribution_score += 1.0
        
        logger.info(f"Shared {model_type.value} model update with network")
        
        # Broadcast to network (simulated)
        await self._broadcast_update(update)
        
        return update
    
    async def receive_model_update(self, update: ModelUpdate) -> bool:
        """Receive and validate a model update from network"""
        # Validate signature
        if update.signature != update.compute_signature():
            logger.warning(f"Invalid signature from {update.participant_id}")
            return False
        
        # Check participant reputation
        participant = self.participants.get(update.participant_id)
        if participant and participant.reputation < 0.3:
            logger.warning(f"Low reputation participant {update.participant_id}")
            return False
        
        # Store update
        self.model_updates[update.model_type].append(update)
        self.metrics['updates_received'] += 1
        
        # Update participant stats
        if participant:
            participant.last_active = datetime.now()
            participant.contribution_score += 0.5
        
        logger.info(f"Received {update.model_type.value} update from {update.participant_id}")
        
        # Check if we should aggregate
        if len(self.model_updates[update.model_type]) >= self.min_participants:
            await self.aggregate_models(update.model_type)
        
        return True
    
    async def aggregate_models(self, model_type: ModelType) -> Optional[Dict[str, np.ndarray]]:
        """Aggregate model updates using federated averaging"""
        updates = self.model_updates[model_type]
        
        if len(updates) < self.min_participants:
            logger.info(f"Not enough participants for {model_type.value} aggregation")
            return None
        
        # Filter by recency (last 24 hours)
        cutoff = datetime.now() - timedelta(hours=24)
        recent_updates = [u for u in updates if u.timestamp > cutoff]
        
        if not recent_updates:
            return None
        
        logger.info(f"Aggregating {len(recent_updates)} updates for {model_type.value}")
        
        # Weighted federated averaging
        aggregated = {}
        total_weight = 0.0
        
        for update in recent_updates:
            participant = self.participants.get(update.participant_id)
            weight = participant.reputation if participant else 1.0
            
            for key, values in update.weights.items():
                if key not in aggregated:
                    aggregated[key] = np.zeros_like(values)
                aggregated[key] += values * weight
            
            total_weight += weight
        
        # Normalize by total weight
        for key in aggregated:
            aggregated[key] /= total_weight
        
        # Store aggregated model
        self.local_models[model_type] = aggregated
        self.metrics['collective_improvements'] += 1
        
        # Clear old updates
        self.model_updates[model_type] = recent_updates[-10:]  # Keep last 10
        
        return aggregated
    
    async def propose_decision(self, 
                              proposal: str,
                              vote_type: VoteType = VoteType.SIMPLE_MAJORITY,
                              implementation: Optional[Dict[str, Any]] = None) -> CollectiveDecision:
        """Propose a democratic decision to the network"""
        decision = CollectiveDecision(
            decision_id=hashlib.md5(f"{proposal}{datetime.now()}".encode()).hexdigest()[:8],
            proposal=proposal,
            proposer_id=self.participant_id,
            vote_type=vote_type,
            created_at=datetime.now(),
            expires_at=datetime.now() + self.decision_timeout,
            implementation=implementation
        )
        
        self.decisions[decision.decision_id] = decision
        
        # Auto-vote yes as proposer
        decision.add_vote(
            self.participant_id, 
            True, 
            self.self_participant.calculate_voting_weight()
        )
        
        logger.info(f"Proposed decision: {proposal}")
        
        # Broadcast to network
        await self._broadcast_decision(decision)
        
        return decision
    
    async def vote_on_decision(self, decision_id: str, vote: bool) -> bool:
        """Vote on a collective decision"""
        decision = self.decisions.get(decision_id)
        if not decision:
            logger.warning(f"Decision {decision_id} not found")
            return False
        
        if decision.expires_at < datetime.now():
            decision.status = "expired"
            logger.warning(f"Decision {decision_id} has expired")
            return False
        
        # Add vote
        decision.add_vote(
            self.participant_id,
            vote,
            self.self_participant.calculate_voting_weight()
        )
        
        self.self_participant.votes_cast += 1
        self.metrics['decisions_participated'] += 1
        
        # Check if decision reached threshold
        approved, approval_rate = decision.calculate_result()
        
        if approved:
            decision.status = "approved"
            logger.info(f"Decision {decision_id} approved with {approval_rate:.1%} support")
            
            # Execute implementation if provided
            if decision.implementation:
                await self._execute_decision(decision)
        
        return True
    
    async def get_collective_wisdom(self, query_type: str) -> Dict[str, Any]:
        """Get aggregated wisdom from the network"""
        wisdom = {
            'query_type': query_type,
            'participants': len(self.participants),
            'timestamp': datetime.now().isoformat()
        }
        
        if query_type == "error_patterns":
            # Aggregate common error patterns
            error_patterns = defaultdict(int)
            for updates in self.model_updates[ModelType.ERROR_PATTERNS]:
                for pattern, count in updates.metrics.items():
                    error_patterns[pattern] += count
            
            wisdom['top_errors'] = dict(sorted(
                error_patterns.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10])
            
        elif query_type == "ui_preferences":
            # Aggregate UI complexity preferences
            preferences = defaultdict(list)
            for updates in self.model_updates[ModelType.UI_PREFERENCES]:
                for pref, value in updates.metrics.items():
                    preferences[pref].append(value)
            
            wisdom['average_preferences'] = {
                k: sum(v) / len(v) for k, v in preferences.items()
            }
            
        elif query_type == "learning_paths":
            # Aggregate successful learning paths
            paths = defaultdict(float)
            for updates in self.model_updates[ModelType.LEARNING_PATHS]:
                for path, success in updates.metrics.items():
                    paths[path] += success
            
            wisdom['successful_paths'] = dict(sorted(
                paths.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5])
        
        return wisdom
    
    async def sync_with_network(self) -> Dict[str, Any]:
        """Synchronize with federated network"""
        sync_result = {
            'timestamp': datetime.now().isoformat(),
            'participants_online': 0,
            'updates_synced': 0,
            'decisions_synced': 0
        }
        
        # Simulate network discovery
        # In production, this would use P2P discovery or central registry
        online_participants = await self._discover_participants()
        sync_result['participants_online'] = len(online_participants)
        
        # Exchange model updates
        for participant_id in online_participants:
            if participant_id != self.participant_id:
                updates = await self._fetch_updates_from(participant_id)
                for update in updates:
                    await self.receive_model_update(update)
                    sync_result['updates_synced'] += 1
        
        # Sync decisions
        decisions = await self._fetch_decisions()
        for decision in decisions:
            if decision.decision_id not in self.decisions:
                self.decisions[decision.decision_id] = decision
                sync_result['decisions_synced'] += 1
        
        logger.info(f"Network sync complete: {sync_result}")
        return sync_result
    
    def get_network_status(self) -> Dict[str, Any]:
        """Get current network status and statistics"""
        return {
            'participant_id': self.participant_id,
            'privacy_level': self.privacy_level.value,
            'network_size': len(self.participants),
            'contribution_score': self.self_participant.contribution_score,
            'reputation': self.self_participant.reputation,
            'models_shared': self.self_participant.models_shared,
            'votes_cast': self.self_participant.votes_cast,
            'pending_decisions': sum(1 for d in self.decisions.values() 
                                   if d.status == "pending"),
            'model_types_active': list(self.local_models.keys()),
            'metrics': self.metrics
        }
    
    # Private helper methods
    
    async def _broadcast_update(self, update: ModelUpdate):
        """Broadcast model update to network (simulated)"""
        # In production: P2P broadcast or publish to distributed ledger
        await asyncio.sleep(0.1)  # Simulate network delay
        
    async def _broadcast_decision(self, decision: CollectiveDecision):
        """Broadcast decision proposal to network"""
        await asyncio.sleep(0.1)  # Simulate network delay
        
    async def _execute_decision(self, decision: CollectiveDecision):
        """Execute an approved collective decision"""
        if not decision.implementation:
            return
        
        impl = decision.implementation
        if impl.get('type') == 'feature_flag':
            # Enable/disable feature based on vote
            feature = impl.get('feature')
            enabled = impl.get('enabled', True)
            logger.info(f"Setting feature {feature} to {enabled}")
            
        elif impl.get('type') == 'parameter_update':
            # Update system parameters
            param = impl.get('parameter')
            value = impl.get('value')
            logger.info(f"Updating {param} to {value}")
    
    async def _discover_participants(self) -> List[str]:
        """Discover active network participants (simulated)"""
        # In production: Use DHT, mDNS, or registry service
        # For now, return simulated participants
        return [self.participant_id]  # Only self in demo
    
    async def _fetch_updates_from(self, participant_id: str) -> List[ModelUpdate]:
        """Fetch model updates from a participant (simulated)"""
        return []  # Empty in demo
    
    async def _fetch_decisions(self) -> List[CollectiveDecision]:
        """Fetch pending decisions from network (simulated)"""
        return []  # Empty in demo


class ConstitutionalGovernance:
    """
    Ensures federated learning respects sacred boundaries
    Implements consciousness-first principles in collective intelligence
    """
    
    def __init__(self):
        self.sacred_boundaries = [
            "Preserve human agency and autonomy",
            "Respect privacy and data sovereignty",
            "Acknowledge uncertainty and limitations",
            "Build trust through vulnerability",
            "Protect flow states and cognitive rhythms"
        ]
        
        self.violation_history: List[Dict[str, Any]] = []
        
    def validate_model_update(self, update: ModelUpdate) -> Tuple[bool, Optional[str]]:
        """Validate model update against sacred boundaries"""
        # Check privacy preservation
        if update.privacy_level == PrivacyLevel.PUBLIC:
            if self._contains_personal_data(update.weights):
                return False, "Public sharing of potential personal data violates privacy sovereignty"
        
        # Check for manipulation patterns
        if self._detects_manipulation(update.metrics):
            return False, "Model appears to optimize for engagement over consciousness"
        
        # Check for cognitive overload
        if self._causes_overload(update.metrics):
            return False, "Model may fragment attention rather than amplify awareness"
        
        return True, None
    
    def validate_decision(self, decision: CollectiveDecision) -> Tuple[bool, Optional[str]]:
        """Validate collective decision against sacred principles"""
        proposal = decision.proposal.lower()
        
        # Check for agency preservation
        if any(word in proposal for word in ['force', 'require', 'mandatory']):
            return False, "Decision may violate user agency and autonomy"
        
        # Check for transparency
        if 'hidden' in proposal or 'secret' in proposal:
            return False, "Decision lacks transparency required for trust"
        
        # Check democratic process
        if decision.vote_type == VoteType.SIMPLE_MAJORITY:
            if 'fundamental' in proposal or 'core' in proposal:
                return False, "Fundamental changes require super-majority or consensus"
        
        return True, None
    
    def record_violation(self, violation_type: str, details: Dict[str, Any]):
        """Record a boundary violation for learning"""
        self.violation_history.append({
            'timestamp': datetime.now().isoformat(),
            'type': violation_type,
            'details': details
        })
    
    def _contains_personal_data(self, weights: Dict[str, np.ndarray]) -> bool:
        """Check if weights might contain personal information"""
        # Heuristic: High-dimensional sparse weights might encode personal patterns
        for key, weight in weights.items():
            if weight.size > 1000 and np.count_nonzero(weight) < weight.size * 0.1:
                return True
        return False
    
    def _detects_manipulation(self, metrics: Dict[str, float]) -> bool:
        """Check if model optimizes for engagement over wellbeing"""
        engagement_metrics = ['clicks', 'time_spent', 'interactions']
        wellbeing_metrics = ['satisfaction', 'calm', 'focus', 'clarity']
        
        engagement_score = sum(metrics.get(m, 0) for m in engagement_metrics)
        wellbeing_score = sum(metrics.get(m, 0) for m in wellbeing_metrics)
        
        return engagement_score > wellbeing_score * 2
    
    def _causes_overload(self, metrics: Dict[str, float]) -> bool:
        """Check if model might cause cognitive overload"""
        overload_indicators = ['complexity', 'options_shown', 'notifications']
        
        for indicator in overload_indicators:
            if metrics.get(indicator, 0) > 0.8:  # Normalized to 0-1
                return True
        return False


# Example usage
async def demo_federated_learning():
    """Demonstrate federated learning capabilities"""
    
    # Initialize network
    network = FederatedLearningNetwork(
        participant_id="user_123",
        privacy_level=PrivacyLevel.DIFFERENTIAL
    )
    
    # Share a model update
    weights = {
        'intent_layer': np.random.randn(100, 50),
        'output_layer': np.random.randn(50, 10)
    }
    metrics = {
        'accuracy': 0.92,
        'loss': 0.15,
        'satisfaction': 0.85
    }
    
    update = await network.share_model_update(
        ModelType.INTENT_RECOGNITION,
        weights,
        metrics
    )
    
    print(f"Shared update: {update.signature[:8]}...")
    
    # Propose a democratic decision
    decision = await network.propose_decision(
        "Enable proactive error prevention by default for new users",
        VoteType.SUPER_MAJORITY,
        implementation={
            'type': 'feature_flag',
            'feature': 'proactive_error_prevention',
            'enabled': True
        }
    )
    
    print(f"Proposed decision: {decision.decision_id}")
    
    # Get collective wisdom
    wisdom = await network.get_collective_wisdom("error_patterns")
    print(f"Collective wisdom: {wisdom}")
    
    # Check network status
    status = network.get_network_status()
    print(f"Network status: {status}")
    
    # Constitutional validation
    governance = ConstitutionalGovernance()
    valid, reason = governance.validate_model_update(update)
    print(f"Update validation: {valid} - {reason}")


if __name__ == "__main__":
    asyncio.run(demo_federated_learning())