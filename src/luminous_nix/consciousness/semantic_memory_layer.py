#!/usr/bin/env python3
"""
🧠 Semantic Memory Layer - The Living Knowledge Graph

This implements the semantic memory capabilities that allow the system to:
- Learn from every interaction
- Build associations between concepts
- Recognize patterns across time
- Develop deep understanding of user needs
"""

import json
import logging
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
import math
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


@dataclass
class MemoryNode:
    """A single memory in the semantic graph"""
    id: str
    content: str
    timestamp: datetime
    node_type: str  # command, error, success, learning, insight
    embedding: Optional[List[float]] = None
    connections: Dict[str, float] = field(default_factory=dict)  # id -> strength
    activation: float = 1.0  # Current activation level
    importance: float = 0.5  # Long-term importance
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def decay(self, time_passed: timedelta, decay_rate: float = 0.1):
        """Apply temporal decay to activation"""
        hours_passed = time_passed.total_seconds() / 3600
        self.activation *= math.exp(-decay_rate * hours_passed)
        
    def strengthen(self, amount: float = 0.1):
        """Strengthen this memory"""
        self.activation = min(1.0, self.activation + amount)
        self.importance = min(1.0, self.importance + amount * 0.5)


@dataclass
class Pattern:
    """A recognized pattern in user behavior"""
    id: str
    pattern_type: str  # sequence, preference, error_recovery, workflow
    nodes: List[str]  # Memory node IDs in this pattern
    frequency: int = 1
    last_seen: datetime = field(default_factory=datetime.now)
    confidence: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def reinforce(self):
        """Reinforce this pattern when seen again"""
        self.frequency += 1
        self.confidence = min(1.0, self.confidence + 0.05)
        self.last_seen = datetime.now()


class SemanticMemoryLayer:
    """
    The semantic memory system that creates a living knowledge graph.
    Memories form connections, patterns emerge, and understanding deepens.
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path.home() / ".luminous-nix" / "semantic-memory"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Memory storage
        self.memories: Dict[str, MemoryNode] = {}
        self.patterns: Dict[str, Pattern] = {}
        self.concept_map: Dict[str, List[str]] = defaultdict(list)  # concept -> memory_ids
        
        # Learning parameters
        self.activation_threshold = 0.1  # Memories below this are pruned
        self.connection_threshold = 0.3  # Connection strength threshold
        self.pattern_min_frequency = 2  # Min frequency to keep pattern
        
        # Load existing memories
        self._load_memories()
        
        logger.info("🧠 Semantic Memory Layer initialized")
    
    def remember(self, content: str, node_type: str, metadata: Dict[str, Any] = None) -> MemoryNode:
        """
        Create a new memory and connect it to related memories.
        """
        # Generate ID from content hash
        memory_id = hashlib.md5(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        # Create memory node
        memory = MemoryNode(
            id=memory_id,
            content=content,
            timestamp=datetime.now(),
            node_type=node_type,
            metadata=metadata or {}
        )
        
        # Find and create connections to related memories
        self._create_connections(memory)
        
        # Store memory
        self.memories[memory_id] = memory
        
        # Extract and index concepts
        self._index_concepts(memory)
        
        # Look for patterns
        self._detect_patterns(memory)
        
        # Save state
        self._save_memories()
        
        logger.debug(f"💭 Remembered: {node_type} - {content[:50]}...")
        return memory
    
    def recall(self, query: str, context: Dict[str, Any] = None) -> List[MemoryNode]:
        """
        Recall memories related to a query using spreading activation.
        """
        # Find seed memories matching query
        seed_memories = self._find_seed_memories(query, context)
        
        if not seed_memories:
            return []
        
        # Spread activation through the network
        activated = self._spread_activation(seed_memories)
        
        # Return memories above threshold, sorted by activation
        results = [
            mem for mem in activated.values()
            if mem.activation > self.activation_threshold
        ]
        results.sort(key=lambda m: m.activation, reverse=True)
        
        return results[:10]  # Top 10 most relevant
    
    def _find_seed_memories(self, query: str, context: Dict[str, Any] = None) -> List[MemoryNode]:
        """Find initial memories matching the query"""
        seeds = []
        query_lower = query.lower()
        
        for memory in self.memories.values():
            relevance = 0.0
            
            # Content matching
            if query_lower in memory.content.lower():
                relevance += 0.5
            
            # Concept matching
            query_concepts = self._extract_concepts(query)
            memory_concepts = self._extract_concepts(memory.content)
            overlap = len(set(query_concepts) & set(memory_concepts))
            relevance += overlap * 0.2
            
            # Context matching
            if context and memory.metadata:
                if context.get("persona") == memory.metadata.get("persona"):
                    relevance += 0.2
                if context.get("task_type") == memory.metadata.get("task_type"):
                    relevance += 0.1
            
            if relevance > 0:
                memory.activation = relevance
                seeds.append(memory)
        
        return seeds
    
    def _spread_activation(self, seeds: List[MemoryNode], iterations: int = 3) -> Dict[str, MemoryNode]:
        """
        Spread activation through the memory network.
        This simulates how thinking of one thing reminds us of related things.
        """
        activated = {mem.id: mem for mem in seeds}
        
        for _ in range(iterations):
            new_activations = {}
            
            for mem_id, memory in activated.items():
                # Spread to connected memories
                for connected_id, strength in memory.connections.items():
                    if connected_id in self.memories:
                        connected = self.memories[connected_id]
                        
                        # Calculate activation to spread
                        spread = memory.activation * strength * 0.7  # Decay factor
                        
                        if connected_id in new_activations:
                            new_activations[connected_id].activation += spread
                        else:
                            connected.activation = spread
                            new_activations[connected_id] = connected
            
            # Merge new activations
            for mem_id, memory in new_activations.items():
                if mem_id not in activated or memory.activation > activated[mem_id].activation:
                    activated[mem_id] = memory
        
        return activated
    
    def _create_connections(self, new_memory: MemoryNode):
        """Create connections between new memory and existing memories"""
        new_concepts = self._extract_concepts(new_memory.content)
        
        for existing_id, existing in self.memories.items():
            # Skip if same memory
            if existing_id == new_memory.id:
                continue
            
            # Calculate connection strength
            existing_concepts = self._extract_concepts(existing.content)
            overlap = len(set(new_concepts) & set(existing_concepts))
            
            if overlap > 0:
                # Base strength on concept overlap
                strength = min(1.0, overlap * 0.3)
                
                # Boost for same type
                if new_memory.node_type == existing.node_type:
                    strength *= 1.2
                
                # Boost for temporal proximity
                time_diff = abs((new_memory.timestamp - existing.timestamp).total_seconds())
                if time_diff < 300:  # Within 5 minutes
                    strength *= 1.5
                elif time_diff < 3600:  # Within 1 hour
                    strength *= 1.2
                
                # Create bidirectional connection
                if strength > self.connection_threshold:
                    new_memory.connections[existing_id] = min(1.0, strength)
                    existing.connections[new_memory.id] = min(1.0, strength)
    
    def _index_concepts(self, memory: MemoryNode):
        """Index memory by concepts for fast retrieval"""
        concepts = self._extract_concepts(memory.content)
        for concept in concepts:
            self.concept_map[concept].append(memory.id)
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text"""
        # Simple concept extraction - can be enhanced with NLP
        words = text.lower().split()
        
        # Filter stop words and short words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 
                     'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                     'would', 'should', 'could', 'may', 'might', 'must', 'can',
                     'shall', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
                     'from', 'about', 'into', 'through', 'during', 'before', 'after'}
        
        concepts = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Add bigrams for compound concepts
        for i in range(len(words) - 1):
            if words[i] not in stop_words and words[i+1] not in stop_words:
                concepts.append(f"{words[i]}_{words[i+1]}")
        
        return concepts[:10]  # Limit to top 10 concepts
    
    def _detect_patterns(self, new_memory: MemoryNode):
        """Detect patterns in memory sequences"""
        # Look for sequences ending with this memory
        recent_memories = sorted(
            self.memories.values(),
            key=lambda m: m.timestamp,
            reverse=True
        )[:20]  # Last 20 memories
        
        # Check for command sequences
        if new_memory.node_type == "command":
            self._detect_command_sequence(new_memory, recent_memories)
        
        # Check for error-recovery patterns
        if new_memory.node_type == "success":
            self._detect_error_recovery(new_memory, recent_memories)
    
    def _detect_command_sequence(self, new_memory: MemoryNode, recent: List[MemoryNode]):
        """Detect repeated command sequences"""
        # Get recent commands
        recent_commands = [m for m in recent if m.node_type == "command"][-5:]
        
        if len(recent_commands) < 2:
            return
        
        # Create sequence signature
        sequence = [m.content for m in recent_commands]
        sequence_hash = hashlib.md5(str(sequence).encode()).hexdigest()[:16]
        
        # Check if pattern exists
        if sequence_hash in self.patterns:
            pattern = self.patterns[sequence_hash]
            pattern.reinforce()
            logger.info(f"🔄 Reinforced pattern: {pattern.pattern_type} (freq: {pattern.frequency})")
        else:
            # Create new pattern
            pattern = Pattern(
                id=sequence_hash,
                pattern_type="command_sequence",
                nodes=[m.id for m in recent_commands],
                metadata={"commands": sequence}
            )
            self.patterns[sequence_hash] = pattern
            logger.info(f"🎯 New pattern detected: command sequence")
    
    def _detect_error_recovery(self, success_memory: MemoryNode, recent: List[MemoryNode]):
        """Detect error recovery patterns"""
        # Look for recent errors
        for i, memory in enumerate(recent):
            if memory.node_type == "error" and i > 0:
                # Found error, check if we recovered from it
                recovery_sequence = recent[i::-1]  # From error to now
                
                if len(recovery_sequence) > 1:
                    pattern_id = f"recovery_{memory.id}_{success_memory.id}"
                    
                    pattern = Pattern(
                        id=pattern_id,
                        pattern_type="error_recovery",
                        nodes=[m.id for m in recovery_sequence],
                        metadata={
                            "error": memory.content,
                            "resolution": success_memory.content
                        }
                    )
                    self.patterns[pattern_id] = pattern
                    logger.info(f"💪 Learned error recovery pattern")
                    break
    
    def get_insights(self) -> Dict[str, Any]:
        """Get insights about the memory system"""
        # Calculate statistics
        total_memories = len(self.memories)
        memory_types = Counter(m.node_type for m in self.memories.values())
        total_connections = sum(len(m.connections) for m in self.memories.values()) // 2
        
        # Find strongest connections
        strongest_connections = []
        for memory in self.memories.values():
            for connected_id, strength in memory.connections.items():
                if strength > 0.7:
                    strongest_connections.append({
                        "from": memory.content[:30],
                        "to": self.memories[connected_id].content[:30] if connected_id in self.memories else "unknown",
                        "strength": strength
                    })
        
        # Pattern statistics
        pattern_types = Counter(p.pattern_type for p in self.patterns.values())
        frequent_patterns = [
            {
                "type": p.pattern_type,
                "frequency": p.frequency,
                "last_seen": p.last_seen.isoformat()
            }
            for p in sorted(self.patterns.values(), key=lambda x: x.frequency, reverse=True)[:5]
        ]
        
        return {
            "total_memories": total_memories,
            "memory_types": dict(memory_types),
            "total_connections": total_connections,
            "avg_connections_per_memory": total_connections / max(1, total_memories),
            "total_patterns": len(self.patterns),
            "pattern_types": dict(pattern_types),
            "frequent_patterns": frequent_patterns,
            "strongest_connections": strongest_connections[:5],
            "total_concepts": len(self.concept_map),
            "memory_health": self._calculate_health()
        }
    
    def _calculate_health(self) -> str:
        """Calculate the health of the memory system"""
        if len(self.memories) < 10:
            return "nascent"  # Just beginning
        elif len(self.memories) < 50:
            return "growing"  # Building connections
        elif len(self.patterns) < 5:
            return "learning"  # Recognizing patterns
        elif len(self.patterns) < 20:
            return "adapting"  # Developing understanding
        else:
            return "thriving"  # Rich memory network
    
    def consolidate(self):
        """
        Consolidate memories - strengthen important ones, forget unimportant ones.
        This is like sleep for the memory system.
        """
        now = datetime.now()
        to_remove = []
        
        for mem_id, memory in self.memories.items():
            # Apply decay
            time_passed = now - memory.timestamp
            memory.decay(time_passed)
            
            # Mark for removal if below threshold
            if memory.activation < self.activation_threshold and memory.importance < 0.3:
                to_remove.append(mem_id)
        
        # Remove weak memories
        for mem_id in to_remove:
            # Remove connections to this memory
            for other in self.memories.values():
                if mem_id in other.connections:
                    del other.connections[mem_id]
            
            # Remove from concept map
            for concept, mem_ids in self.concept_map.items():
                if mem_id in mem_ids:
                    mem_ids.remove(mem_id)
            
            # Remove memory
            del self.memories[mem_id]
        
        if to_remove:
            logger.info(f"🧹 Consolidated: removed {len(to_remove)} weak memories")
        
        # Save consolidated state
        self._save_memories()
    
    def _save_memories(self):
        """Save memories to disk"""
        try:
            # Save memories
            memories_file = self.data_dir / "memories.json"
            memories_data = {
                mem_id: {
                    "content": mem.content,
                    "timestamp": mem.timestamp.isoformat(),
                    "node_type": mem.node_type,
                    "connections": mem.connections,
                    "activation": mem.activation,
                    "importance": mem.importance,
                    "metadata": mem.metadata
                }
                for mem_id, mem in self.memories.items()
            }
            
            with open(memories_file, 'w') as f:
                json.dump(memories_data, f, indent=2)
            
            # Save patterns
            patterns_file = self.data_dir / "patterns.json"
            patterns_data = {
                pat_id: {
                    "pattern_type": pat.pattern_type,
                    "nodes": pat.nodes,
                    "frequency": pat.frequency,
                    "last_seen": pat.last_seen.isoformat(),
                    "confidence": pat.confidence,
                    "metadata": pat.metadata
                }
                for pat_id, pat in self.patterns.items()
            }
            
            with open(patterns_file, 'w') as f:
                json.dump(patterns_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save memories: {e}")
    
    def _load_memories(self):
        """Load memories from disk"""
        try:
            # Load memories
            memories_file = self.data_dir / "memories.json"
            if memories_file.exists():
                with open(memories_file, 'r') as f:
                    memories_data = json.load(f)
                
                for mem_id, data in memories_data.items():
                    memory = MemoryNode(
                        id=mem_id,
                        content=data["content"],
                        timestamp=datetime.fromisoformat(data["timestamp"]),
                        node_type=data["node_type"],
                        connections=data.get("connections", {}),
                        activation=data.get("activation", 0.5),
                        importance=data.get("importance", 0.5),
                        metadata=data.get("metadata", {})
                    )
                    self.memories[mem_id] = memory
                    self._index_concepts(memory)
                
                logger.info(f"📚 Loaded {len(self.memories)} memories")
            
            # Load patterns
            patterns_file = self.data_dir / "patterns.json"
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    patterns_data = json.load(f)
                
                for pat_id, data in patterns_data.items():
                    pattern = Pattern(
                        id=pat_id,
                        pattern_type=data["pattern_type"],
                        nodes=data["nodes"],
                        frequency=data.get("frequency", 1),
                        last_seen=datetime.fromisoformat(data["last_seen"]),
                        confidence=data.get("confidence", 0.5),
                        metadata=data.get("metadata", {})
                    )
                    self.patterns[pat_id] = pattern
                
                logger.info(f"🎯 Loaded {len(self.patterns)} patterns")
                
        except Exception as e:
            logger.warning(f"Could not load memories: {e}")


def create_semantic_memory() -> SemanticMemoryLayer:
    """Factory function to create semantic memory system"""
    return SemanticMemoryLayer()