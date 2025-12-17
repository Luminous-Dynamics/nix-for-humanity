"""
Agent Collaboration & Learning System
Agents teach each other and learn collectively

Features:
1. Peer review of responses
2. Cross-agent knowledge transfer
3. Shared knowledge graph
4. Emergent collective intelligence
"""

import asyncio
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging
import json
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class Critique:
    """A critique from one agent about another's response"""
    critic_id: str
    target_agent_id: str
    query: str
    response_content: str
    critique_type: str  # 'accuracy', 'completeness', 'clarity', 'efficiency'
    score: float  # 0-1
    suggestions: List[str]
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class LearningInsight:
    """An insight extracted from agent interactions"""
    insight_id: str
    insight_type: str  # 'pattern', 'antipattern', 'optimization', 'knowledge_gap'
    description: str
    evidence: List[str]  # References to supporting data
    confidence: float
    applicable_agents: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class KnowledgeNode:
    """A node in the shared knowledge graph"""
    node_id: str
    concept: str
    description: str
    examples: List[str]
    related_nodes: Set[str] = field(default_factory=set)
    learned_from: List[str] = field(default_factory=list)  # Agent IDs
    success_count: int = 0
    failure_count: int = 0
    confidence: float = 0.5


class KnowledgeGraph:
    """Shared knowledge graph for collective learning"""

    def __init__(self, persistence_path: Optional[Path] = None):
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: Dict[str, Set[str]] = defaultdict(set)  # node_id -> related_node_ids
        self.persistence_path = persistence_path

        if persistence_path and persistence_path.exists():
            self._load()

    def add_node(self, node: KnowledgeNode) -> None:
        """Add or update a knowledge node"""
        if node.node_id in self.nodes:
            # Update existing node
            existing = self.nodes[node.node_id]
            existing.examples.extend(node.examples)
            existing.learned_from.extend(node.learned_from)
            existing.related_nodes.update(node.related_nodes)
        else:
            self.nodes[node.node_id] = node

        # Update edges
        for related_id in node.related_nodes:
            self.edges[node.node_id].add(related_id)
            self.edges[related_id].add(node.node_id)  # Bidirectional

    def add_relationship(self, node_id1: str, node_id2: str) -> None:
        """Add a relationship between two nodes"""
        if node_id1 in self.nodes and node_id2 in self.nodes:
            self.edges[node_id1].add(node_id2)
            self.edges[node_id2].add(node_id1)

            self.nodes[node_id1].related_nodes.add(node_id2)
            self.nodes[node_id2].related_nodes.add(node_id1)

    def get_related(self, node_id: str, depth: int = 1) -> List[KnowledgeNode]:
        """Get related nodes up to a certain depth"""
        if node_id not in self.nodes:
            return []

        visited = {node_id}
        current_level = {node_id}
        result = []

        for _ in range(depth):
            next_level = set()
            for nid in current_level:
                for related_id in self.edges.get(nid, []):
                    if related_id not in visited:
                        visited.add(related_id)
                        next_level.add(related_id)
                        result.append(self.nodes[related_id])

            current_level = next_level
            if not current_level:
                break

        return result

    def search(self, query: str, limit: int = 10) -> List[KnowledgeNode]:
        """Search for relevant knowledge nodes"""
        query_lower = query.lower()

        scored_nodes = []
        for node in self.nodes.values():
            score = 0.0

            # Exact matches in concept
            if query_lower in node.concept.lower():
                score += 10.0

            # Matches in description
            if query_lower in node.description.lower():
                score += 5.0

            # Matches in examples
            for example in node.examples:
                if query_lower in example.lower():
                    score += 2.0

            # Factor in confidence and success rate
            if node.success_count + node.failure_count > 0:
                success_rate = node.success_count / (node.success_count + node.failure_count)
                score *= (1 + success_rate * node.confidence)

            if score > 0:
                scored_nodes.append((score, node))

        # Sort by score and return top results
        scored_nodes.sort(reverse=True, key=lambda x: x[0])
        return [node for _, node in scored_nodes[:limit]]

    def update_success(self, node_id: str, success: bool) -> None:
        """Update success/failure counts for a node"""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            if success:
                node.success_count += 1
            else:
                node.failure_count += 1

            # Update confidence based on track record
            total = node.success_count + node.failure_count
            if total > 0:
                node.confidence = node.success_count / total

    def _save(self) -> None:
        """Save knowledge graph to disk"""
        if not self.persistence_path:
            return

        data = {
            'nodes': [
                {
                    'node_id': node.node_id,
                    'concept': node.concept,
                    'description': node.description,
                    'examples': node.examples,
                    'related_nodes': list(node.related_nodes),
                    'learned_from': node.learned_from,
                    'success_count': node.success_count,
                    'failure_count': node.failure_count,
                    'confidence': node.confidence,
                }
                for node in self.nodes.values()
            ]
        }

        self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.persistence_path, 'w') as f:
            json.dump(data, f, indent=2)

    def _load(self) -> None:
        """Load knowledge graph from disk"""
        if not self.persistence_path or not self.persistence_path.exists():
            return

        with open(self.persistence_path, 'r') as f:
            data = json.load(f)

        for node_data in data.get('nodes', []):
            node = KnowledgeNode(
                node_id=node_data['node_id'],
                concept=node_data['concept'],
                description=node_data['description'],
                examples=node_data['examples'],
                related_nodes=set(node_data.get('related_nodes', [])),
                learned_from=node_data.get('learned_from', []),
                success_count=node_data.get('success_count', 0),
                failure_count=node_data.get('failure_count', 0),
                confidence=node_data.get('confidence', 0.5),
            )
            self.add_node(node)


class CollaborativeAgentNetwork:
    """
    Agents that learn from each other through peer review and knowledge sharing

    Key Features:
    - Agents critique each other's responses
    - Successful patterns shared via knowledge graph
    - Collective intelligence emerges from interactions
    - Self-improving system
    """

    def __init__(
        self,
        knowledge_path: Optional[Path] = None,
        enable_peer_review: bool = True,
        enable_knowledge_sharing: bool = True,
    ):
        self.agents: Dict[str, any] = {}  # agent_id -> agent instance
        self.agent_profiles: Dict[str, any] = {}  # agent_id -> AgentProfile

        # Collaborative learning components
        self.knowledge_graph = KnowledgeGraph(knowledge_path)
        self.learning_events: List[LearningInsight] = []
        self.critiques: List[Critique] = []

        # Configuration
        self.enable_peer_review = enable_peer_review
        self.enable_knowledge_sharing = enable_knowledge_sharing

        # Performance tracking
        self.agent_performance: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {'accuracy': 0.5, 'helpfulness': 0.5, 'queries_handled': 0}
        )

    def register_agent(self, agent_id: str, agent_instance, profile) -> None:
        """Register an agent in the collaborative network"""
        self.agents[agent_id] = agent_instance
        self.agent_profiles[agent_id] = profile

        logger.info(f"Registered agent '{agent_id}' in collaborative network")

    async def collaborative_query(
        self,
        query: str,
        selected_agents: Optional[List[str]] = None
    ) -> Dict:
        """
        Process query with agent collaboration

        Flow:
        1. Get initial responses from agents
        2. Agents critique each other (peer review)
        3. Extract learning insights
        4. Update knowledge graph
        5. Generate refined consensus response
        """

        start_time = datetime.now()

        # Select agents (all if not specified)
        agent_ids = selected_agents or list(self.agents.keys())

        # Step 1: Get initial responses in parallel
        logger.info(f"Getting initial responses from {len(agent_ids)} agents")
        responses = await self._parallel_responses(query, agent_ids)

        # Step 2: Peer review (if enabled)
        critiques = []
        if self.enable_peer_review and len(responses) > 1:
            logger.info("Conducting peer review")
            critiques = await self._cross_critique(responses, query)
            self.critiques.extend(critiques)

        # Step 3: Extract learning insights
        insights = await self._extract_insights(responses, critiques, query)
        self.learning_events.extend(insights)

        # Step 4: Update knowledge graph
        if self.enable_knowledge_sharing:
            await self._update_knowledge(responses, insights, query)

        # Step 5: Synthesize with learning
        final_response = await self._synthesize_with_learning(
            responses, critiques, insights, query
        )

        # Update performance metrics
        duration = (datetime.now() - start_time).total_seconds()

        return {
            'response': final_response,
            'agent_responses': responses,
            'critiques': critiques,
            'insights': insights,
            'performance': {
                'duration_seconds': duration,
                'agents_used': len(responses),
                'critiques_generated': len(critiques),
                'insights_extracted': len(insights),
            }
        }

    async def _parallel_responses(
        self,
        query: str,
        agent_ids: List[str]
    ) -> List[Dict]:
        """Get responses from multiple agents in parallel"""

        tasks = []
        for agent_id in agent_ids:
            if agent_id not in self.agents:
                continue

            agent = self.agents[agent_id]

            # Enrich query with relevant knowledge
            if self.enable_knowledge_sharing:
                relevant_knowledge = self.knowledge_graph.search(query, limit=5)
                context = {
                    'shared_knowledge': [
                        {'concept': node.concept, 'description': node.description}
                        for node in relevant_knowledge
                    ]
                }
            else:
                context = {}

            # Create async task for agent response
            task = asyncio.create_task(
                self._agent_respond(agent, query, context)
            )
            tasks.append((agent_id, task))

        # Wait for all responses
        responses = []
        for agent_id, task in tasks:
            try:
                response = await asyncio.wait_for(task, timeout=30.0)
                responses.append({
                    'agent_id': agent_id,
                    'content': response.get('content', ''),
                    'confidence': response.get('confidence', 0.5),
                    'reasoning': response.get('reasoning', ''),
                })
            except asyncio.TimeoutError:
                logger.warning(f"Agent {agent_id} timed out")
            except Exception as e:
                logger.error(f"Agent {agent_id} error: {e}")

        return responses

    async def _agent_respond(self, agent, query: str, context: Dict) -> Dict:
        """Get response from a single agent"""
        loop = asyncio.get_event_loop()

        try:
            # Assume agent has a respond method
            if hasattr(agent, 'respond_async'):
                response = await agent.respond_async(query, context)
            else:
                response = await loop.run_in_executor(
                    None,
                    agent.respond,
                    query,
                    context
                )

            return response
        except Exception as e:
            logger.error(f"Agent response error: {e}")
            return {
                'content': f"Error: {str(e)}",
                'confidence': 0.0,
                'error': True
            }

    async def _cross_critique(
        self,
        responses: List[Dict],
        query: str
    ) -> List[Critique]:
        """Each agent critiques other agents' responses"""

        critiques = []

        # Each agent critiques every other agent
        for i, response_i in enumerate(responses):
            agent_id_i = response_i['agent_id']

            for j, response_j in enumerate(responses):
                if i == j:
                    continue  # Don't critique yourself

                agent_id_j = response_j['agent_id']

                # Generate critique
                critique = await self._generate_critique(
                    critic_id=agent_id_i,
                    target_agent_id=agent_id_j,
                    query=query,
                    response=response_j,
                    critic_response=response_i
                )

                if critique:
                    critiques.append(critique)

        return critiques

    async def _generate_critique(
        self,
        critic_id: str,
        target_agent_id: str,
        query: str,
        response: Dict,
        critic_response: Dict
    ) -> Optional[Critique]:
        """Generate a critique from one agent about another"""

        try:
            # Analyze response for different aspects
            content = response.get('content', '')
            confidence = response.get('confidence', 0.5)

            # Simple heuristic-based critique (can be enhanced with LLM)
            scores = {
                'completeness': self._score_completeness(content, query),
                'clarity': self._score_clarity(content),
                'confidence_calibration': confidence,
            }

            avg_score = sum(scores.values()) / len(scores)

            # Generate suggestions
            suggestions = []
            if scores['completeness'] < 0.7:
                suggestions.append("Response could be more comprehensive")
            if scores['clarity'] < 0.7:
                suggestions.append("Response could be clearer or better structured")
            if confidence < 0.5:
                suggestions.append("Agent seems uncertain - may need more training")

            critique = Critique(
                critic_id=critic_id,
                target_agent_id=target_agent_id,
                query=query,
                response_content=content,
                critique_type='comprehensive',
                score=avg_score,
                suggestions=suggestions,
                reasoning=f"Evaluated on completeness, clarity, and confidence"
            )

            return critique

        except Exception as e:
            logger.error(f"Critique generation error: {e}")
            return None

    def _score_completeness(self, content: str, query: str) -> float:
        """Score response completeness (simple heuristic)"""
        if not content:
            return 0.0

        # Length-based heuristic (can be improved)
        words = len(content.split())

        if words < 10:
            return 0.3
        elif words < 30:
            return 0.6
        elif words < 100:
            return 0.8
        else:
            return 0.9

    def _score_clarity(self, content: str) -> float:
        """Score response clarity (simple heuristic)"""
        if not content:
            return 0.0

        # Structure-based heuristic
        has_sentences = '.' in content or '!' in content or '?' in content
        has_structure = '\n' in content or '1.' in content or '-' in content

        score = 0.5
        if has_sentences:
            score += 0.25
        if has_structure:
            score += 0.25

        return min(score, 1.0)

    async def _extract_insights(
        self,
        responses: List[Dict],
        critiques: List[Critique],
        query: str
    ) -> List[LearningInsight]:
        """Extract learning insights from agent interactions"""

        insights = []

        # Insight 1: High agreement patterns
        if len(responses) > 2:
            # Check if multiple agents agree
            content_map = defaultdict(list)
            for resp in responses:
                content_hash = resp['content'][:100]  # Simple similarity
                content_map[content_hash].append(resp['agent_id'])

            for content_hash, agent_ids in content_map.items():
                if len(agent_ids) >= 2:
                    insight = LearningInsight(
                        insight_id=f"consensus_{datetime.now().timestamp()}",
                        insight_type='pattern',
                        description=f"Multiple agents agree on response to: {query[:50]}",
                        evidence=[f"Agents: {', '.join(agent_ids)}"],
                        confidence=len(agent_ids) / len(responses),
                        applicable_agents=agent_ids
                    )
                    insights.append(insight)

        # Insight 2: Common critique patterns
        if critiques:
            critique_types = defaultdict(int)
            for critique in critiques:
                for suggestion in critique.suggestions:
                    critique_types[suggestion] += 1

            for suggestion, count in critique_types.items():
                if count >= 2:
                    insight = LearningInsight(
                        insight_id=f"critique_{datetime.now().timestamp()}",
                        insight_type='knowledge_gap',
                        description=suggestion,
                        evidence=[f"Mentioned in {count} critiques"],
                        confidence=count / len(critiques),
                        applicable_agents=list(self.agents.keys())
                    )
                    insights.append(insight)

        return insights

    async def _update_knowledge(
        self,
        responses: List[Dict],
        insights: List[LearningInsight],
        query: str
    ) -> None:
        """Update shared knowledge graph based on interactions"""

        try:
            # Create knowledge nodes from high-confidence responses
            for response in responses:
                if response.get('confidence', 0) > 0.7:
                    node = KnowledgeNode(
                        node_id=f"node_{datetime.now().timestamp()}",
                        concept=query[:100],
                        description=response['content'][:500],
                        examples=[query],
                        learned_from=[response['agent_id']]
                    )
                    self.knowledge_graph.add_node(node)

            # Add insights as knowledge
            for insight in insights:
                if insight.confidence > 0.6:
                    node = KnowledgeNode(
                        node_id=insight.insight_id,
                        concept=insight.insight_type,
                        description=insight.description,
                        examples=insight.evidence,
                        learned_from=insight.applicable_agents
                    )
                    self.knowledge_graph.add_node(node)

            # Persist knowledge
            self.knowledge_graph._save()

        except Exception as e:
            logger.error(f"Knowledge update error: {e}")

    async def _synthesize_with_learning(
        self,
        responses: List[Dict],
        critiques: List[Critique],
        insights: List[LearningInsight],
        query: str
    ) -> Dict:
        """Synthesize final response incorporating learning"""

        if not responses:
            return {
                'content': 'No responses available',
                'confidence': 0.0
            }

        # Weight responses by confidence and critique scores
        weighted_responses = []
        for response in responses:
            agent_id = response['agent_id']

            # Base confidence
            weight = response.get('confidence', 0.5)

            # Adjust by critique scores
            agent_critiques = [c for c in critiques if c.target_agent_id == agent_id]
            if agent_critiques:
                avg_critique_score = sum(c.score for c in agent_critiques) / len(agent_critiques)
                weight = (weight + avg_critique_score) / 2

            weighted_responses.append((weight, response))

        # Sort by weight
        weighted_responses.sort(reverse=True, key=lambda x: x[0])

        # Best response
        best_weight, best_response = weighted_responses[0]

        # Combine insights
        learning_summary = []
        for insight in insights:
            if insight.confidence > 0.5:
                learning_summary.append(insight.description)

        return {
            'content': best_response['content'],
            'confidence': best_weight,
            'agent_id': best_response['agent_id'],
            'learning_insights': learning_summary,
            'collective_intelligence': {
                'agents_contributed': len(responses),
                'critiques_considered': len(critiques),
                'insights_generated': len(insights),
            }
        }


# Example usage
async def example_collaborative_learning():
    """Demonstrate collaborative agent learning"""

    from pathlib import Path

    # Create collaborative network
    network = CollaborativeAgentNetwork(
        knowledge_path=Path("~/.luminous-nix/collaborative_knowledge.json").expanduser(),
        enable_peer_review=True,
        enable_knowledge_sharing=True
    )

    # TODO: Register actual agents
    # network.register_agent('agent1', agent1_instance, profile1)
    # network.register_agent('agent2', agent2_instance, profile2)

    # Process query collaboratively
    query = "install and configure nginx as reverse proxy"

    result = await network.collaborative_query(query)

    print("🤝 Collaborative Response:")
    print(f"   Content: {result['response']['content'][:200]}...")
    print(f"   Confidence: {result['response']['confidence']:.2%}")
    print(f"   Agents: {result['performance']['agents_used']}")
    print(f"   Critiques: {result['performance']['critiques_generated']}")
    print(f"   Insights: {result['performance']['insights_extracted']}")

    if result['response'].get('learning_insights'):
        print("\n💡 Learning Insights:")
        for insight in result['response']['learning_insights']:
            print(f"   - {insight}")


if __name__ == "__main__":
    asyncio.run(example_collaborative_learning())
