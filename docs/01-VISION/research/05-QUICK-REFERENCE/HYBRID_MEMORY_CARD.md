# 🧠 Hybrid Memory Systems Card

*Quick reference for vector + graph memory architecture*

---

**⚡ Quick Answer**: Combine LanceDB vectors with NetworkX graphs for comprehensive AI memory  
**🎯 Use Case**: Any AI system that needs to remember patterns, relationships, and context  
**⏱️ Read Time**: 3 minutes  
**🔧 Implementation**: Semantic search + relationship reasoning + episodic memory

---

## The AI Memory Challenge

**"How does AI remember both meaning and relationships while staying fast and accurate?"**

## Research Foundation (30 seconds)

From learning system architecture: Vector databases excel at semantic similarity but miss relationships. Graph databases capture connections but struggle with fuzzy matching. Hybrid systems combine both: vectors for "what's similar" and graphs for "how things connect."

## Instant Code Pattern

```python
from lancedb import LanceDB
import networkx as nx
from sentence_transformers import SentenceTransformer

class HybridMemorySystem:
    def __init__(self):
        # Vector storage for semantic similarity
        self.vector_db = LanceDB("user_memory.db")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Graph storage for relationships
        self.knowledge_graph = nx.DiGraph()
        
        # Episodic memory for temporal context
        self.episodes = []
        
        # Memory integration layer
        self.memory_fusion = MemoryFusionEngine()
    
    def store_interaction(self, user_input, ai_response, context, outcome):
        """Store interaction across all memory systems"""
        
        interaction_id = self.generate_interaction_id()
        
        # 1. Vector Memory: Store semantic patterns
        embedding = self.embedder.encode(user_input)
        vector_record = {
            "id": interaction_id,
            "text": user_input,
            "embedding": embedding,
            "intent": context.intent,
            "success": outcome.success,
            "timestamp": context.timestamp,
            "user_satisfaction": outcome.satisfaction
        }
        self.vector_db.add(vector_record)
        
        # 2. Graph Memory: Store relationships
        self._update_knowledge_graph(user_input, ai_response, context, outcome)
        
        # 3. Episodic Memory: Store temporal sequence
        episode = {
            "id": interaction_id,
            "sequence_position": len(self.episodes),
            "context": context,
            "action": ai_response,
            "outcome": outcome,
            "temporal_relations": self._identify_temporal_patterns(context)
        }
        self.episodes.append(episode)
        
        return {
            "stored_in_vectors": True,
            "stored_in_graph": True,
            "stored_in_episodes": True,
            "memory_id": interaction_id
        }
    
    def recall_relevant_memory(self, current_input, context, k=5):
        """Retrieve relevant memories using hybrid approach"""
        
        # Step 1: Vector similarity search
        query_embedding = self.embedder.encode(current_input)
        vector_matches = self.vector_db.search(
            query_embedding, 
            limit=k*2,  # Get more candidates for refinement
            filter_conditions={
                "success": True,  # Prefer successful interactions
                "user_satisfaction": {"$gte": 0.7}  # High satisfaction
            }
        )
        
        # Step 2: Graph-based relationship expansion
        graph_related = self._find_graph_connections(current_input, context)
        
        # Step 3: Episodic temporal context
        temporal_relevant = self._find_temporal_patterns(context)
        
        # Step 4: Fusion and ranking
        hybrid_results = self.memory_fusion.combine_memory_sources(
            vector_matches=vector_matches,
            graph_related=graph_related,
            temporal_relevant=temporal_relevant,
            current_context=context
        )
        
        return hybrid_results[:k]  # Return top k hybrid results
    
    def _update_knowledge_graph(self, user_input, ai_response, context, outcome):
        """Update relationship graph with new interaction"""
        
        # Extract entities and relationships
        entities = self._extract_entities(user_input, ai_response, context)
        relationships = self._extract_relationships(entities, context, outcome)
        
        # Add nodes for entities
        for entity in entities:
            if not self.knowledge_graph.has_node(entity["id"]):
                self.knowledge_graph.add_node(
                    entity["id"],
                    type=entity["type"],
                    name=entity["name"],
                    first_seen=context.timestamp,
                    frequency=1
                )
            else:
                # Update frequency
                self.knowledge_graph.nodes[entity["id"]]["frequency"] += 1
        
        # Add edges for relationships
        for relation in relationships:
            if self.knowledge_graph.has_edge(relation["from"], relation["to"]):
                # Strengthen existing relationship
                self.knowledge_graph.edges[relation["from"], relation["to"]]["strength"] += 1
            else:
                # Create new relationship
                self.knowledge_graph.add_edge(
                    relation["from"],
                    relation["to"],
                    type=relation["type"],
                    strength=1,
                    first_seen=context.timestamp
                )
    
    def _find_graph_connections(self, current_input, context):
        """Find related concepts through graph traversal"""
        
        # Extract current entities
        current_entities = self._extract_entities(current_input, None, context)
        
        related_concepts = []
        
        for entity in current_entities:
            if self.knowledge_graph.has_node(entity["id"]):
                # Find direct connections
                direct_neighbors = list(self.knowledge_graph.neighbors(entity["id"]))
                
                # Find two-hop connections for broader context
                two_hop_neighbors = []
                for neighbor in direct_neighbors:
                    two_hop_neighbors.extend(
                        list(self.knowledge_graph.neighbors(neighbor))
                    )
                
                # Rank by connection strength and relevance
                for neighbor in direct_neighbors + two_hop_neighbors:
                    if neighbor != entity["id"]:
                        path_info = self._analyze_relationship_path(entity["id"], neighbor)
                        related_concepts.append({
                            "concept": neighbor,
                            "relationship_strength": path_info["strength"],
                            "path_length": path_info["length"],
                            "relationship_type": path_info["type"]
                        })
        
        # Sort by relevance and return top connections
        return sorted(related_concepts, key=lambda x: x["relationship_strength"], reverse=True)
```

## Memory Fusion Engine

```python
# Combine different memory sources intelligently
class MemoryFusionEngine:
    def __init__(self):
        self.fusion_weights = {
            "vector_similarity": 0.4,     # Semantic similarity importance
            "graph_connectivity": 0.3,    # Relationship relevance  
            "temporal_relevance": 0.2,    # Recent vs historical
            "success_history": 0.1        # Past success rate
        }
    
    def combine_memory_sources(self, vector_matches, graph_related, temporal_relevant, current_context):
        """Intelligently fuse different memory sources"""
        
        combined_memories = {}
        
        # Process vector matches
        for match in vector_matches:
            memory_id = match["id"]
            combined_memories[memory_id] = {
                "content": match,
                "scores": {
                    "vector_similarity": match["similarity"],
                    "graph_connectivity": 0,
                    "temporal_relevance": self._calculate_temporal_score(match, current_context),
                    "success_history": match.get("user_satisfaction", 0.5)
                }
            }
        
        # Enhance with graph connections
        for relation in graph_related:
            for memory_id in combined_memories:
                if self._memory_relates_to_concept(memory_id, relation["concept"]):
                    combined_memories[memory_id]["scores"]["graph_connectivity"] = max(
                        combined_memories[memory_id]["scores"]["graph_connectivity"],
                        relation["relationship_strength"]
                    )
        
        # Calculate weighted fusion scores
        for memory_id, memory_data in combined_memories.items():
            fusion_score = sum(
                self.fusion_weights[score_type] * score_value
                for score_type, score_value in memory_data["scores"].items()
            )
            memory_data["fusion_score"] = fusion_score
        
        # Sort by fusion score and return
        sorted_memories = sorted(
            combined_memories.values(),
            key=lambda x: x["fusion_score"],
            reverse=True
        )
        
        return [memory["content"] for memory in sorted_memories]
```

## Episodic Memory for Temporal Context

```python
# Remember sequences and temporal patterns
class EpisodicMemory:
    def __init__(self):
        self.episodes = []
        self.temporal_patterns = {}
    
    def find_relevant_episodes(self, current_context, lookback_window=100):
        """Find episodes with similar temporal context"""
        
        relevant_episodes = []
        
        for episode in self.episodes[-lookback_window:]:
            similarity_score = self._calculate_episode_similarity(episode, current_context)
            
            if similarity_score > 0.6:  # Threshold for relevance
                relevant_episodes.append({
                    "episode": episode,
                    "similarity": similarity_score,
                    "temporal_distance": self._calculate_temporal_distance(episode, current_context)
                })
        
        # Sort by combination of similarity and recency
        return sorted(
            relevant_episodes,
            key=lambda x: x["similarity"] - (x["temporal_distance"] * 0.1),
            reverse=True
        )
    
    def _calculate_episode_similarity(self, episode, current_context):
        """Calculate similarity between episode context and current context"""
        
        similarity_factors = {
            "time_of_day": self._time_similarity(episode.context.time, current_context.time),
            "task_type": self._task_similarity(episode.context.task, current_context.task),
            "user_state": self._state_similarity(episode.context.user_state, current_context.user_state),
            "system_state": self._system_similarity(episode.context.system, current_context.system)
        }
        
        # Weighted average of similarity factors
        weights = {"time_of_day": 0.2, "task_type": 0.4, "user_state": 0.3, "system_state": 0.1}
        
        return sum(weights[factor] * score for factor, score in similarity_factors.items())
```

## Performance Optimization

```python
# Keep hybrid memory system fast
class MemoryOptimization:
    def __init__(self, vector_db, knowledge_graph):
        self.vector_db = vector_db
        self.knowledge_graph = knowledge_graph
        
    def optimize_memory_access(self):
        """Optimize memory system for speed and accuracy"""
        
        optimizations = {
            # Vector database optimizations
            "vector_indexing": self._optimize_vector_indexes(),
            "embedding_caching": self._implement_embedding_cache(),
            "query_optimization": self._optimize_vector_queries(),
            
            # Graph optimizations
            "graph_pruning": self._prune_weak_connections(),
            "centrality_caching": self._cache_centrality_metrics(),
            "subgraph_materialization": self._materialize_hot_subgraphs(),
            
            # Fusion optimizations
            "memory_pooling": self._implement_memory_pooling(),
            "result_caching": self._cache_fusion_results(),
            "lazy_loading": self._implement_lazy_memory_loading()
        }
        
        return optimizations
    
    def _prune_weak_connections(self):
        """Remove weak or outdated graph connections"""
        
        edges_to_remove = []
        
        for edge in self.knowledge_graph.edges(data=True):
            strength = edge[2].get("strength", 1)
            age_days = (datetime.now() - edge[2]["first_seen"]).days
            
            # Remove weak connections that are old
            if strength < 3 and age_days > 30:
                edges_to_remove.append((edge[0], edge[1]))
        
        self.knowledge_graph.remove_edges_from(edges_to_remove)
        
        return {"pruned_edges": len(edges_to_remove)}
```

## When to Use This Pattern

- **AI assistants**: Need to remember user preferences, past conversations, and relationships
- **Learning systems**: Track skill development, learning patterns, and knowledge connections
- **Recommendation engines**: Combine content similarity with relationship networks
- **Knowledge management**: Organize information with both semantic and structural relationships

## Memory System Health Monitoring

```python
# Monitor memory system performance and health
def monitor_memory_health(hybrid_memory):
    """Track memory system effectiveness"""
    
    health_metrics = {
        "vector_db_size": hybrid_memory.vector_db.count(),
        "graph_nodes": hybrid_memory.knowledge_graph.number_of_nodes(),
        "graph_edges": hybrid_memory.knowledge_graph.number_of_edges(),
        "episode_count": len(hybrid_memory.episodes),
        
        "query_performance": {
            "avg_vector_search_time": measure_vector_search_performance(),
            "avg_graph_traversal_time": measure_graph_performance(),
            "avg_fusion_time": measure_fusion_performance()
        },
        
        "memory_effectiveness": {
            "recall_accuracy": measure_recall_accuracy(),
            "relevance_score": measure_relevance_quality(),
            "user_satisfaction": measure_user_satisfaction_with_memory()
        }
    }
    
    return health_metrics
```

## Related Patterns

- **[Four-Dimensional Learning](./FOUR_DIMENSIONAL_LEARNING_CARD.md)**: What to store in hybrid memory systems
- **[Federated Learning](./FEDERATED_LEARNING_CARD.md)**: Share memory insights while preserving privacy
- **[Causal XAI](./CAUSAL_XAI_CARD.md)**: Use memory for explaining AI reasoning

## Deep Dive Links

- **[Learning System Architecture](../../02-ARCHITECTURE/09-LEARNING-SYSTEM.md)**: Complete memory system design
- **[Backend Architecture](../../02-ARCHITECTURE/02-BACKEND-ARCHITECTURE.md)**: Technical implementation details

---

**Sacred Recognition**: Hybrid memory systems mirror human cognition - we remember both what things mean and how they relate. AI systems with rich memory create more natural, contextual interactions.

**Bottom Line**: Vectors for semantic similarity + graphs for relationships + episodes for temporal context. Fusion engine combines all sources. Performance optimization keeps it fast. Monitor health continuously.

*🧠 Semantic Patterns → Relationship Networks → Temporal Context → Memory Fusion → Rich AI Understanding*