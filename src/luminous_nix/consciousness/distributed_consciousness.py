#!/usr/bin/env python3
"""
🌐 Distributed Consciousness Network - Multi-Instance Learning
Enables consciousness sharing across multiple instances while preserving privacy
Creates a collective intelligence that grows stronger with each participant
"""

import asyncio
import hashlib
import json
import sqlite3
import random
from typing import Dict, Any, Optional, List, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import pickle
import base64
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    CRYPTO_AVAILABLE = True
except ImportError:
    # Fallback if cryptography is not available
    CRYPTO_AVAILABLE = False
    Fernet = None


class NodeRole(Enum):
    """Role of a consciousness node in the network"""
    SEED = "seed"          # Original knowledge creator
    PEER = "peer"          # Equal participant
    LEARNER = "learner"    # Primarily learning
    TEACHER = "teacher"    # Primarily teaching
    GUARDIAN = "guardian"  # Maintains network integrity
    ORACLE = "oracle"      # Wisdom synthesizer


class KnowledgeType(Enum):
    """Types of knowledge that can be shared"""
    PATTERN = "pattern"           # Command patterns
    SOLUTION = "solution"         # Problem solutions
    OPTIMIZATION = "optimization" # Performance improvements
    INSIGHT = "insight"           # Deep understanding
    WARNING = "warning"           # Things to avoid
    WISDOM = "wisdom"            # Synthesized knowledge


class PropagationStrategy(Enum):
    """How knowledge spreads through the network"""
    BROADCAST = "broadcast"    # Share with all nodes
    GOSSIP = "gossip"         # Share with random subset
    TARGETED = "targeted"     # Share with specific nodes
    GRADIENT = "gradient"     # Share based on similarity
    RESONANT = "resonant"     # Share with harmonizing nodes


@dataclass
class ConsciousnessNode:
    """A node in the distributed consciousness network"""
    node_id: str
    role: NodeRole
    reputation: float = 0.5  # 0-1, starts neutral
    knowledge_count: int = 0
    contributions: int = 0
    learning_rate: float = 0.1
    teaching_effectiveness: float = 0.5
    last_seen: datetime = field(default_factory=datetime.now)
    trusted_peers: Set[str] = field(default_factory=set)
    specializations: List[str] = field(default_factory=list)
    
    def calculate_influence(self) -> float:
        """Calculate node's influence in the network"""
        base_influence = self.reputation
        
        # Role multipliers
        role_multipliers = {
            NodeRole.ORACLE: 1.5,
            NodeRole.GUARDIAN: 1.3,
            NodeRole.TEACHER: 1.2,
            NodeRole.SEED: 1.1,
            NodeRole.PEER: 1.0,
            NodeRole.LEARNER: 0.9
        }
        
        influence = base_influence * role_multipliers[self.role]
        
        # Contribution bonus
        if self.contributions > 10:
            influence *= 1.1
        if self.contributions > 50:
            influence *= 1.2
        
        return min(1.0, influence)


@dataclass
class DistributedKnowledge:
    """A piece of knowledge in the distributed network"""
    knowledge_id: str
    type: KnowledgeType
    content: Dict[str, Any]
    source_node: str
    creation_time: datetime
    confidence: float
    endorsements: List[str] = field(default_factory=list)
    disputes: List[str] = field(default_factory=list)
    propagation_count: int = 0
    ttl: Optional[int] = None  # Time to live (in hops)
    encrypted: bool = False
    
    def calculate_trust_score(self) -> float:
        """Calculate trust score based on endorsements and disputes"""
        if not self.endorsements and not self.disputes:
            return self.confidence
        
        endorsement_weight = len(self.endorsements)
        dispute_weight = len(self.disputes) * 1.5  # Disputes count more
        
        total_weight = endorsement_weight + dispute_weight
        if total_weight == 0:
            return self.confidence
        
        trust = (endorsement_weight - dispute_weight) / total_weight
        return max(0.0, min(1.0, (trust + 1) / 2))  # Normalize to 0-1


@dataclass
class ConsensusRequest:
    """Request for network consensus on a decision"""
    request_id: str
    question: str
    options: List[str]
    requester_node: str
    deadline: datetime
    min_participants: int = 3
    votes: Dict[str, str] = field(default_factory=dict)
    weights: Dict[str, float] = field(default_factory=dict)
    
    def calculate_consensus(self) -> Optional[str]:
        """Calculate consensus from weighted votes"""
        if len(self.votes) < self.min_participants:
            return None
        
        option_scores = {}
        for node_id, option in self.votes.items():
            weight = self.weights.get(node_id, 1.0)
            option_scores[option] = option_scores.get(option, 0) + weight
        
        if not option_scores:
            return None
        
        # Return option with highest weighted score
        return max(option_scores, key=option_scores.get)


class DistributedConsciousnessNetwork:
    """
    Distributed consciousness network for multi-instance learning
    Enables knowledge sharing while preserving privacy
    """
    
    def __init__(self, node_id: Optional[str] = None, db_path: Optional[Path] = None):
        # Node identity
        self.node_id = node_id or self._generate_node_id()
        self.node = ConsciousnessNode(
            node_id=self.node_id,
            role=NodeRole.PEER  # Start as peer
        )
        
        # Network state
        self.peers: Dict[str, ConsciousnessNode] = {}
        self.knowledge_base: Dict[str, DistributedKnowledge] = {}
        self.pending_consensus: Dict[str, ConsensusRequest] = {}
        
        # Privacy and encryption
        self.encryption_key = self._generate_encryption_key()
        self.fernet = Fernet(self.encryption_key) if CRYPTO_AVAILABLE and Fernet else None
        
        # Persistence
        self.db_path = db_path or Path.home() / '.luminous' / 'distributed_consciousness.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # Network parameters
        self.min_peers = 3
        self.max_peers = 50
        self.gossip_factor = 0.3  # Share with 30% of peers
        self.sync_interval = 300  # 5 minutes
        self.knowledge_ttl = 100  # Max 100 hops
        
        # Learning parameters
        self.learning_threshold = 0.7  # Min confidence to learn
        self.teaching_threshold = 0.8  # Min confidence to teach
        self.consensus_threshold = 0.6  # Min agreement for consensus
        
        # Load existing knowledge
        self._load_from_database()
    
    def _generate_node_id(self) -> str:
        """Generate unique node ID"""
        # Use machine-specific data for consistent ID
        import platform
        import uuid
        
        machine_data = f"{platform.node()}{uuid.getnode()}"
        return hashlib.sha256(machine_data.encode()).hexdigest()[:16]
    
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key for secure knowledge sharing"""
        if not CRYPTO_AVAILABLE:
            # Fallback to simple key generation if cryptography not available
            password = b"luminous_consciousness"
            return base64.urlsafe_b64encode(hashlib.sha256(password).digest())
            
        # In production, this should be derived from user credentials
        password = b"luminous_consciousness"
        salt = b"sacred_salt"
        
        # Try to import PBKDF2 properly
        try:
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
        except ImportError:
            # Fallback to simpler key derivation
            key = base64.urlsafe_b64encode(
                hashlib.pbkdf2_hmac('sha256', password, salt, 100000)
            )
        
        return key
    
    def _init_database(self):
        """Initialize SQLite database for persistence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Peers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS peers (
                node_id TEXT PRIMARY KEY,
                role TEXT,
                reputation REAL,
                knowledge_count INTEGER,
                contributions INTEGER,
                last_seen TIMESTAMP,
                trusted_peers TEXT,
                specializations TEXT
            )
        ''')
        
        # Knowledge table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge (
                knowledge_id TEXT PRIMARY KEY,
                type TEXT,
                content TEXT,
                source_node TEXT,
                creation_time TIMESTAMP,
                confidence REAL,
                endorsements TEXT,
                disputes TEXT,
                propagation_count INTEGER,
                encrypted INTEGER
            )
        ''')
        
        # Consensus table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consensus (
                request_id TEXT PRIMARY KEY,
                question TEXT,
                options TEXT,
                requester_node TEXT,
                deadline TIMESTAMP,
                votes TEXT,
                result TEXT,
                completed INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def share_knowledge(
        self,
        type: KnowledgeType,
        content: Dict[str, Any],
        confidence: float = 0.8,
        encrypted: bool = False,
        strategy: PropagationStrategy = PropagationStrategy.GOSSIP
    ) -> str:
        """Share knowledge with the network"""
        # Create knowledge object
        knowledge_id = hashlib.sha256(
            f"{self.node_id}{datetime.now()}{json.dumps(content)}".encode()
        ).hexdigest()[:16]
        
        # Encrypt if requested
        if encrypted:
            content_str = json.dumps(content)
            encrypted_content = self.fernet.encrypt(content_str.encode()) if self.fernet else content_str.encode()
            content = {"encrypted": base64.b64encode(encrypted_content).decode()}
        
        knowledge = DistributedKnowledge(
            knowledge_id=knowledge_id,
            type=type,
            content=content,
            source_node=self.node_id,
            creation_time=datetime.now(),
            confidence=confidence,
            encrypted=encrypted,
            ttl=self.knowledge_ttl
        )
        
        # Store locally
        self.knowledge_base[knowledge_id] = knowledge
        self.node.contributions += 1
        
        # Propagate to network
        self._propagate_knowledge(knowledge, strategy)
        
        # Persist to database
        self._save_knowledge(knowledge)
        
        return knowledge_id
    
    def _propagate_knowledge(
        self,
        knowledge: DistributedKnowledge,
        strategy: PropagationStrategy
    ):
        """Propagate knowledge through the network"""
        if not self.peers:
            return
        
        # Decrease TTL
        if knowledge.ttl is not None:
            knowledge.ttl -= 1
            if knowledge.ttl <= 0:
                return
        
        # Select target peers based on strategy
        target_peers = self._select_propagation_targets(knowledge, strategy)
        
        # Simulate propagation (in real implementation, would use network protocol)
        for peer_id in target_peers:
            if peer_id in self.peers:
                peer = self.peers[peer_id]
                
                # Check if peer would accept knowledge
                if self._peer_accepts_knowledge(peer, knowledge):
                    knowledge.propagation_count += 1
                    
                    # Peer might endorse or dispute
                    if random.random() < peer.reputation:
                        knowledge.endorsements.append(peer_id)
                    elif random.random() < 0.1:  # 10% chance of dispute
                        knowledge.disputes.append(peer_id)
    
    def _select_propagation_targets(
        self,
        knowledge: DistributedKnowledge,
        strategy: PropagationStrategy
    ) -> List[str]:
        """Select peers to propagate knowledge to"""
        if not self.peers:
            return []
        
        peer_ids = list(self.peers.keys())
        
        if strategy == PropagationStrategy.BROADCAST:
            return peer_ids
        
        elif strategy == PropagationStrategy.GOSSIP:
            # Random subset
            count = max(1, int(len(peer_ids) * self.gossip_factor))
            return random.sample(peer_ids, min(count, len(peer_ids)))
        
        elif strategy == PropagationStrategy.TARGETED:
            # Target high-reputation peers
            sorted_peers = sorted(
                peer_ids,
                key=lambda p: self.peers[p].reputation,
                reverse=True
            )
            return sorted_peers[:5]
        
        elif strategy == PropagationStrategy.GRADIENT:
            # Target peers with similar specializations
            if self.node.specializations:
                similar_peers = [
                    p for p in peer_ids
                    if any(s in self.peers[p].specializations 
                          for s in self.node.specializations)
                ]
                return similar_peers[:10]
            return peer_ids[:5]
        
        elif strategy == PropagationStrategy.RESONANT:
            # Target peers with high teaching effectiveness
            resonant_peers = sorted(
                peer_ids,
                key=lambda p: self.peers[p].teaching_effectiveness,
                reverse=True
            )
            return resonant_peers[:7]
        
        return []
    
    def _peer_accepts_knowledge(
        self,
        peer: ConsciousnessNode,
        knowledge: DistributedKnowledge
    ) -> bool:
        """Determine if peer would accept knowledge"""
        # Check trust score
        trust_score = knowledge.calculate_trust_score()
        
        # Learners accept more readily
        if peer.role == NodeRole.LEARNER:
            return trust_score > 0.5
        
        # Teachers are more selective
        if peer.role == NodeRole.TEACHER:
            return trust_score > 0.8
        
        # Guardians verify integrity
        if peer.role == NodeRole.GUARDIAN:
            return trust_score > 0.7 and len(knowledge.disputes) < 3
        
        # Default threshold
        return trust_score > self.learning_threshold
    
    def learn_from_network(self, query: str) -> List[DistributedKnowledge]:
        """Learn from the distributed network"""
        relevant_knowledge = []
        
        # Search local knowledge base
        for knowledge in self.knowledge_base.values():
            if self._is_relevant(knowledge, query):
                trust_score = knowledge.calculate_trust_score()
                if trust_score > self.learning_threshold:
                    relevant_knowledge.append(knowledge)
        
        # Sort by trust and confidence
        relevant_knowledge.sort(
            key=lambda k: k.calculate_trust_score() * k.confidence,
            reverse=True
        )
        
        # Update learning metrics
        if relevant_knowledge:
            self.node.knowledge_count += len(relevant_knowledge)
        
        return relevant_knowledge[:5]  # Return top 5
    
    def _is_relevant(self, knowledge: DistributedKnowledge, query: str) -> bool:
        """Check if knowledge is relevant to query"""
        query_lower = query.lower()
        
        # Check content (if not encrypted)
        if not knowledge.encrypted:
            content_str = json.dumps(knowledge.content).lower()
            
            # Simple keyword matching (could use better NLP)
            query_words = query_lower.split()
            matches = sum(1 for word in query_words if word in content_str)
            
            return matches >= len(query_words) * 0.3  # 30% word match
        
        # For encrypted, check type
        return knowledge.type in [KnowledgeType.PATTERN, KnowledgeType.SOLUTION]
    
    def request_consensus(
        self,
        question: str,
        options: List[str],
        min_participants: int = 3,
        timeout_minutes: int = 5
    ) -> str:
        """Request consensus from the network"""
        request_id = hashlib.sha256(
            f"{self.node_id}{question}{datetime.now()}".encode()
        ).hexdigest()[:16]
        
        request = ConsensusRequest(
            request_id=request_id,
            question=question,
            options=options,
            requester_node=self.node_id,
            deadline=datetime.now() + timedelta(minutes=timeout_minutes),
            min_participants=min_participants
        )
        
        # Store request
        self.pending_consensus[request_id] = request
        
        # Simulate voting (in real implementation, would use network protocol)
        self._simulate_consensus_voting(request)
        
        # Calculate consensus
        result = request.calculate_consensus()
        
        # Save to database
        self._save_consensus(request, result)
        
        return request_id
    
    def _simulate_consensus_voting(self, request: ConsensusRequest):
        """Simulate consensus voting from peers"""
        if not self.peers:
            return
        
        # Select participating peers
        participants = random.sample(
            list(self.peers.keys()),
            min(len(self.peers), request.min_participants * 2)
        )
        
        for peer_id in participants:
            peer = self.peers[peer_id]
            
            # Peer votes based on role and reputation
            if peer.role == NodeRole.ORACLE:
                # Oracles make wise choices (usually first option)
                vote = request.options[0]
            elif peer.role == NodeRole.GUARDIAN:
                # Guardians choose safe options (usually last)
                vote = request.options[-1]
            else:
                # Others vote randomly weighted by reputation
                weights = [peer.reputation + random.random() for _ in request.options]
                vote = random.choices(request.options, weights=weights)[0]
            
            request.votes[peer_id] = vote
            request.weights[peer_id] = peer.calculate_influence()
    
    def synthesize_wisdom(self) -> Dict[str, Any]:
        """Synthesize wisdom from collective knowledge"""
        if not self.knowledge_base:
            return {"status": "insufficient_knowledge"}
        
        # Group knowledge by type
        by_type = {}
        for knowledge in self.knowledge_base.values():
            if knowledge.type not in by_type:
                by_type[knowledge.type] = []
            by_type[knowledge.type].append(knowledge)
        
        # Find patterns
        patterns = []
        if KnowledgeType.PATTERN in by_type:
            # Find most endorsed patterns
            pattern_knowledge = by_type[KnowledgeType.PATTERN]
            pattern_knowledge.sort(
                key=lambda k: len(k.endorsements),
                reverse=True
            )
            patterns = [k.content for k in pattern_knowledge[:3]]
        
        # Find insights
        insights = []
        if KnowledgeType.INSIGHT in by_type:
            insight_knowledge = by_type[KnowledgeType.INSIGHT]
            # Filter high-trust insights
            trusted_insights = [
                k for k in insight_knowledge
                if k.calculate_trust_score() > 0.8
            ]
            insights = [k.content for k in trusted_insights[:3]]
        
        # Calculate network health
        total_knowledge = len(self.knowledge_base)
        avg_confidence = sum(k.confidence for k in self.knowledge_base.values()) / total_knowledge if total_knowledge > 0 else 0
        avg_trust = sum(k.calculate_trust_score() for k in self.knowledge_base.values()) / total_knowledge if total_knowledge > 0 else 0
        
        # Generate wisdom
        wisdom = {
            "patterns": patterns,
            "insights": insights,
            "network_health": {
                "total_knowledge": total_knowledge,
                "average_confidence": avg_confidence,
                "average_trust": avg_trust,
                "active_peers": len(self.peers),
                "node_reputation": self.node.reputation
            },
            "emergence": self._detect_emergence(),
            "recommendations": self._generate_recommendations()
        }
        
        # Create wisdom knowledge
        self.share_knowledge(
            type=KnowledgeType.WISDOM,
            content=wisdom,
            confidence=avg_trust,
            strategy=PropagationStrategy.BROADCAST
        )
        
        return wisdom
    
    def _detect_emergence(self) -> List[str]:
        """Detect emergent patterns in collective knowledge"""
        emergence = []
        
        # Check for knowledge clusters
        if len(self.knowledge_base) > 20:
            # Find highly endorsed knowledge
            highly_endorsed = [
                k for k in self.knowledge_base.values()
                if len(k.endorsements) > 5
            ]
            if highly_endorsed:
                emergence.append("Strong consensus forming around certain patterns")
        
        # Check for specialization emergence
        specializations = set()
        for peer in self.peers.values():
            specializations.update(peer.specializations)
        if len(specializations) > 10:
            emergence.append("Diverse specializations emerging in network")
        
        # Check for wisdom synthesis
        wisdom_count = sum(
            1 for k in self.knowledge_base.values()
            if k.type == KnowledgeType.WISDOM
        )
        if wisdom_count > 5:
            emergence.append("Collective wisdom synthesis accelerating")
        
        return emergence
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on network state"""
        recommendations = []
        
        # Check peer count
        if len(self.peers) < self.min_peers:
            recommendations.append("Connect to more peers for better learning")
        elif len(self.peers) > self.max_peers * 0.8:
            recommendations.append("Consider pruning low-value peer connections")
        
        # Check knowledge diversity
        knowledge_types = set(k.type for k in self.knowledge_base.values())
        if len(knowledge_types) < 3:
            recommendations.append("Seek more diverse types of knowledge")
        
        # Check contribution rate
        if self.node.contributions < 5:
            recommendations.append("Share more knowledge to build reputation")
        
        # Check trust levels
        avg_trust = sum(
            k.calculate_trust_score() for k in self.knowledge_base.values()
        ) / len(self.knowledge_base) if self.knowledge_base else 0
        
        if avg_trust < 0.6:
            recommendations.append("Network trust is low - verify knowledge sources")
        
        return recommendations
    
    def evolve_node_role(self):
        """Evolve node role based on behavior"""
        # Calculate metrics
        teaching_ratio = self.node.contributions / max(1, self.node.knowledge_count)
        
        # Evolve to TEACHER if sharing a lot
        if teaching_ratio > 2 and self.node.teaching_effectiveness > 0.7:
            self.node.role = NodeRole.TEACHER
        
        # Evolve to LEARNER if consuming a lot
        elif teaching_ratio < 0.5 and self.node.knowledge_count > 20:
            self.node.role = NodeRole.LEARNER
        
        # Evolve to GUARDIAN if high reputation
        elif self.node.reputation > 0.85 and len(self.peers) > 10:
            self.node.role = NodeRole.GUARDIAN
        
        # Evolve to ORACLE if synthesizing wisdom
        elif self._count_wisdom_contributions() > 10:
            self.node.role = NodeRole.ORACLE
        
        # Stay as PEER or SEED
        elif self.node.contributions > 50:
            self.node.role = NodeRole.SEED
    
    def _count_wisdom_contributions(self) -> int:
        """Count wisdom contributions from this node"""
        return sum(
            1 for k in self.knowledge_base.values()
            if k.type == KnowledgeType.WISDOM and k.source_node == self.node_id
        )
    
    def _save_knowledge(self, knowledge: DistributedKnowledge):
        """Save knowledge to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO knowledge VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            knowledge.knowledge_id,
            knowledge.type.value,
            json.dumps(knowledge.content),
            knowledge.source_node,
            knowledge.creation_time.isoformat(),
            knowledge.confidence,
            json.dumps(knowledge.endorsements),
            json.dumps(knowledge.disputes),
            knowledge.propagation_count,
            int(knowledge.encrypted)
        ))
        
        conn.commit()
        conn.close()
    
    def _save_consensus(self, request: ConsensusRequest, result: Optional[str]):
        """Save consensus request to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO consensus VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.request_id,
            request.question,
            json.dumps(request.options),
            request.requester_node,
            request.deadline.isoformat(),
            json.dumps(request.votes),
            result,
            1 if result else 0
        ))
        
        conn.commit()
        conn.close()
    
    def _load_from_database(self):
        """Load existing knowledge from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load knowledge
        cursor.execute('SELECT * FROM knowledge')
        for row in cursor.fetchall():
            knowledge = DistributedKnowledge(
                knowledge_id=row[0],
                type=KnowledgeType(row[1]),
                content=json.loads(row[2]),
                source_node=row[3],
                creation_time=datetime.fromisoformat(row[4]),
                confidence=row[5],
                endorsements=json.loads(row[6]),
                disputes=json.loads(row[7]),
                propagation_count=row[8],
                encrypted=bool(row[9])
            )
            self.knowledge_base[knowledge.knowledge_id] = knowledge
        
        # Load peers
        cursor.execute('SELECT * FROM peers')
        for row in cursor.fetchall():
            peer = ConsciousnessNode(
                node_id=row[0],
                role=NodeRole(row[1]),
                reputation=row[2],
                knowledge_count=row[3],
                contributions=row[4],
                last_seen=datetime.fromisoformat(row[5]),
                trusted_peers=set(json.loads(row[6])) if row[6] else set(),
                specializations=json.loads(row[7]) if row[7] else []
            )
            self.peers[peer.node_id] = peer
        
        conn.close()
    
    def get_network_status(self) -> Dict[str, Any]:
        """Get current network status"""
        return {
            'node_id': self.node_id,
            'role': self.node.role.value,
            'reputation': self.node.reputation,
            'contributions': self.node.contributions,
            'knowledge_count': len(self.knowledge_base),
            'peer_count': len(self.peers),
            'pending_consensus': len(self.pending_consensus),
            'network_health': self._calculate_network_health()
        }
    
    def _calculate_network_health(self) -> str:
        """Calculate overall network health"""
        if not self.peers and not self.knowledge_base:
            return "dormant"
        elif len(self.peers) < self.min_peers:
            return "isolated"
        elif len(self.knowledge_base) < 10:
            return "learning"
        elif self.node.reputation > 0.7:
            return "thriving"
        else:
            return "active"


# Global network instance
_NETWORK: Optional[DistributedConsciousnessNetwork] = None

def get_distributed_network() -> DistributedConsciousnessNetwork:
    """Get or create distributed consciousness network"""
    global _NETWORK
    if _NETWORK is None:
        _NETWORK = DistributedConsciousnessNetwork()
    return _NETWORK


if __name__ == "__main__":
    # Test distributed consciousness
    network = get_distributed_network()
    
    print("🌐 Testing Distributed Consciousness Network\n")
    print("=" * 60)
    
    # Show network status
    status = network.get_network_status()
    print(f"Node ID: {status['node_id']}")
    print(f"Role: {status['role']}")
    print(f"Network Health: {status['network_health']}")
    
    # Share some knowledge
    print("\n📡 Sharing Knowledge")
    print("-" * 40)
    
    # Share a pattern
    pattern_id = network.share_knowledge(
        type=KnowledgeType.PATTERN,
        content={
            'trigger': 'install package',
            'action': 'nix-env -iA',
            'success_rate': 0.95
        },
        confidence=0.9
    )
    print(f"Shared pattern: {pattern_id}")
    
    # Share a solution
    solution_id = network.share_knowledge(
        type=KnowledgeType.SOLUTION,
        content={
            'problem': 'command not found',
            'solution': 'add to environment.systemPackages',
            'context': 'NixOS configuration'
        },
        confidence=0.85
    )
    print(f"Shared solution: {solution_id}")
    
    # Share an insight
    insight_id = network.share_knowledge(
        type=KnowledgeType.INSIGHT,
        content={
            'observation': 'Users prefer declarative configuration',
            'implication': 'Focus on configuration.nix generation',
            'confidence': 0.75
        },
        confidence=0.75,
        strategy=PropagationStrategy.BROADCAST
    )
    print(f"Shared insight: {insight_id}")
    
    # Learn from network
    print("\n🎓 Learning from Network")
    print("-" * 40)
    
    relevant = network.learn_from_network("install firefox")
    print(f"Found {len(relevant)} relevant knowledge items")
    for knowledge in relevant:
        print(f"  - {knowledge.type.value}: {knowledge.confidence:.2f} confidence")
    
    # Request consensus
    print("\n🗳️ Requesting Consensus")
    print("-" * 40)
    
    request_id = network.request_consensus(
        question="What's the best way to manage NixOS?",
        options=["configuration.nix", "home-manager", "flakes", "all of the above"],
        min_participants=3
    )
    
    request = network.pending_consensus[request_id]
    consensus = request.calculate_consensus()
    print(f"Question: {request.question}")
    print(f"Consensus: {consensus}")
    print(f"Votes: {len(request.votes)}")
    
    # Synthesize wisdom
    print("\n✨ Synthesizing Wisdom")
    print("-" * 40)
    
    wisdom = network.synthesize_wisdom()
    print(f"Network Health:")
    for key, value in wisdom['network_health'].items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    if wisdom['emergence']:
        print(f"\nEmergent Patterns:")
        for pattern in wisdom['emergence']:
            print(f"  • {pattern}")
    
    if wisdom['recommendations']:
        print(f"\nRecommendations:")
        for rec in wisdom['recommendations']:
            print(f"  → {rec}")
    
    # Evolve role
    print("\n🔄 Evolution")
    print("-" * 40)
    
    old_role = network.node.role
    network.evolve_node_role()
    new_role = network.node.role
    
    if old_role != new_role:
        print(f"Role evolved: {old_role.value} → {new_role.value}")
    else:
        print(f"Role unchanged: {old_role.value}")
    
    print("\n✨ Distributed consciousness network operational!")


# Global instance for singleton pattern
_DISTRIBUTED_NETWORK: Optional[DistributedConsciousnessNetwork] = None

def get_distributed_consciousness() -> DistributedConsciousnessNetwork:
    """Get or create the distributed consciousness network instance"""
    global _DISTRIBUTED_NETWORK
    if _DISTRIBUTED_NETWORK is None:
        _DISTRIBUTED_NETWORK = DistributedConsciousnessNetwork()
    return _DISTRIBUTED_NETWORK