"""
Advanced Causal Understanding for Luminous Nix
Deep system reasoning, root cause analysis, and wisdom generation
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Set, Union
from datetime import datetime, timedelta
from enum import Enum
import networkx as nx
import numpy as np
from collections import defaultdict, deque
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class CausalRelationType(Enum):
    """Types of causal relationships"""
    DIRECT = "direct"              # A directly causes B
    INDIRECT = "indirect"          # A causes B through C
    BIDIRECTIONAL = "bidirectional"  # A and B affect each other
    CONDITIONAL = "conditional"     # A causes B only if C
    TEMPORAL = "temporal"          # A causes B after time delay
    PROBABILISTIC = "probabilistic"  # A increases probability of B
    INHIBITORY = "inhibitory"      # A prevents B


class WisdomType(Enum):
    """Types of extracted wisdom"""
    PATTERN = "pattern"            # Recurring pattern
    PRINCIPLE = "principle"        # General principle
    HEURISTIC = "heuristic"       # Rule of thumb
    CORRELATION = "correlation"    # Statistical relationship
    CAUSATION = "causation"       # Causal relationship
    ANOMALY = "anomaly"           # Unusual pattern
    EVOLUTION = "evolution"       # How things change over time


@dataclass
class CausalNode:
    """Node in causal graph"""
    node_id: str
    node_type: str  # command, error, state, outcome
    description: str
    occurrence_count: int = 0
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_occurrence(self):
        """Update occurrence statistics"""
        self.occurrence_count += 1
        self.last_seen = datetime.now()


@dataclass
class CausalEdge:
    """Edge in causal graph representing relationship"""
    source: str
    target: str
    relation_type: CausalRelationType
    strength: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    time_lag_ms: Optional[int] = None
    condition: Optional[str] = None
    evidence_count: int = 0
    
    def update_strength(self, observation_weight: float = 0.1):
        """Update edge strength based on new observation"""
        self.strength = min(1.0, self.strength + observation_weight)
        self.evidence_count += 1
        self.confidence = min(1.0, self.evidence_count / 10.0)  # Confidence grows with evidence


@dataclass
class CausalPath:
    """Path through causal graph"""
    nodes: List[str]
    edges: List[CausalEdge]
    total_strength: float
    path_type: str  # direct, indirect, cyclic
    
    def explain(self, graph: 'CausalGraph') -> str:
        """Generate human-readable explanation of path"""
        explanations = []
        
        for i, edge in enumerate(self.edges):
            source_node = graph.get_node(edge.source)
            target_node = graph.get_node(edge.target)
            
            if edge.relation_type == CausalRelationType.DIRECT:
                explanations.append(
                    f"{source_node.description} directly causes {target_node.description}"
                )
            elif edge.relation_type == CausalRelationType.TEMPORAL:
                explanations.append(
                    f"{source_node.description} leads to {target_node.description} "
                    f"after {edge.time_lag_ms}ms"
                )
            elif edge.relation_type == CausalRelationType.CONDITIONAL:
                explanations.append(
                    f"{source_node.description} causes {target_node.description} "
                    f"when {edge.condition}"
                )
        
        return " → ".join(explanations)


@dataclass
class RootCause:
    """Identified root cause of an issue"""
    cause_id: str
    issue_id: str
    cause_node: CausalNode
    causal_paths: List[CausalPath]
    confidence: float
    explanation: str
    suggested_fixes: List[str]
    prevention_strategies: List[str]


@dataclass
class ExtractedWisdom:
    """Wisdom extracted from causal analysis"""
    wisdom_id: str
    wisdom_type: WisdomType
    statement: str
    confidence: float
    supporting_evidence: List[str]
    applicable_contexts: List[str]
    discovered_at: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    
    def apply(self) -> bool:
        """Apply this wisdom (track usage)"""
        self.usage_count += 1
        return True


class CausalGraph:
    """Causal graph for system understanding"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, CausalNode] = {}
        self.edges: Dict[Tuple[str, str], CausalEdge] = {}
        self.temporal_events: deque = deque(maxlen=1000)
        
    def add_node(self, node: CausalNode):
        """Add node to causal graph"""
        self.nodes[node.node_id] = node
        self.graph.add_node(node.node_id, data=node)
        
    def add_edge(self, edge: CausalEdge):
        """Add causal relationship"""
        key = (edge.source, edge.target)
        self.edges[key] = edge
        self.graph.add_edge(
            edge.source, 
            edge.target,
            weight=edge.strength,
            data=edge
        )
    
    def get_node(self, node_id: str) -> Optional[CausalNode]:
        """Get node by ID"""
        return self.nodes.get(node_id)
    
    def find_paths(self, source: str, target: str, max_length: int = 5) -> List[CausalPath]:
        """Find causal paths between nodes"""
        paths = []
        
        try:
            # Find all simple paths
            simple_paths = list(nx.all_simple_paths(
                self.graph, source, target, cutoff=max_length
            ))
            
            for node_path in simple_paths:
                edges = []
                total_strength = 1.0
                
                for i in range(len(node_path) - 1):
                    edge_key = (node_path[i], node_path[i+1])
                    if edge_key in self.edges:
                        edge = self.edges[edge_key]
                        edges.append(edge)
                        total_strength *= edge.strength
                
                path_type = "direct" if len(node_path) == 2 else "indirect"
                
                paths.append(CausalPath(
                    nodes=node_path,
                    edges=edges,
                    total_strength=total_strength,
                    path_type=path_type
                ))
            
        except nx.NetworkXNoPath:
            pass
        
        return sorted(paths, key=lambda p: p.total_strength, reverse=True)
    
    def find_cycles(self) -> List[List[str]]:
        """Find causal cycles in graph"""
        return list(nx.simple_cycles(self.graph))
    
    def calculate_importance(self, node_id: str) -> float:
        """Calculate importance of a node using PageRank"""
        try:
            pagerank = nx.pagerank(self.graph)
            return pagerank.get(node_id, 0.0)
        except:
            return 0.0


class RootCauseAnalyzer:
    """Analyzes issues to find root causes"""
    
    def __init__(self, causal_graph: CausalGraph):
        self.graph = causal_graph
        self.analysis_history: List[RootCause] = []
        
    def analyze_issue(self, issue_description: str, 
                      issue_node_id: str,
                      context: Dict[str, Any] = None) -> List[RootCause]:
        """Analyze an issue to find root causes"""
        root_causes = []
        
        # Get issue node
        issue_node = self.graph.get_node(issue_node_id)
        if not issue_node:
            return root_causes
        
        # Find all predecessors (potential causes)
        predecessors = list(self.graph.graph.predecessors(issue_node_id))
        
        for pred_id in predecessors:
            pred_node = self.graph.get_node(pred_id)
            if not pred_node:
                continue
            
            # Find causal paths
            paths = self.graph.find_paths(pred_id, issue_node_id)
            
            if paths:
                # Calculate confidence based on path strength and evidence
                confidence = self._calculate_confidence(paths)
                
                # Generate explanation
                explanation = self._generate_explanation(pred_node, issue_node, paths)
                
                # Suggest fixes
                fixes = self._suggest_fixes(pred_node, issue_node, context)
                
                # Prevention strategies
                prevention = self._suggest_prevention(pred_node, issue_node, paths)
                
                root_cause = RootCause(
                    cause_id=f"rc_{datetime.now().timestamp()}",
                    issue_id=issue_node_id,
                    cause_node=pred_node,
                    causal_paths=paths,
                    confidence=confidence,
                    explanation=explanation,
                    suggested_fixes=fixes,
                    prevention_strategies=prevention
                )
                
                root_causes.append(root_cause)
                self.analysis_history.append(root_cause)
        
        # Sort by confidence
        return sorted(root_causes, key=lambda rc: rc.confidence, reverse=True)
    
    def _calculate_confidence(self, paths: List[CausalPath]) -> float:
        """Calculate confidence in root cause"""
        if not paths:
            return 0.0
        
        # Weighted average of path strengths
        total_weight = sum(p.total_strength for p in paths)
        avg_strength = total_weight / len(paths)
        
        # Bonus for multiple paths
        path_bonus = min(0.2, len(paths) * 0.05)
        
        return min(1.0, avg_strength + path_bonus)
    
    def _generate_explanation(self, cause: CausalNode, effect: CausalNode, 
                             paths: List[CausalPath]) -> str:
        """Generate human-readable explanation"""
        if len(paths) == 1 and paths[0].path_type == "direct":
            return f"{cause.description} directly causes {effect.description}"
        elif len(paths) == 1:
            return paths[0].explain(self.graph)
        else:
            return (f"{cause.description} causes {effect.description} through "
                   f"{len(paths)} different causal paths")
    
    def _suggest_fixes(self, cause: CausalNode, effect: CausalNode,
                      context: Dict[str, Any] = None) -> List[str]:
        """Suggest fixes based on root cause"""
        fixes = []
        
        # Type-specific fixes
        if cause.node_type == "command":
            fixes.append(f"Modify or avoid command: {cause.description}")
        elif cause.node_type == "state":
            fixes.append(f"Change system state: resolve {cause.description}")
        elif cause.node_type == "error":
            fixes.append(f"Handle error: {cause.description}")
        
        # Context-specific fixes
        if context:
            if context.get("user_level") == "beginner":
                fixes.append("Use guided mode with safety checks")
            if context.get("frequency") == "recurring":
                fixes.append("Create automated solution or alias")
        
        return fixes
    
    def _suggest_prevention(self, cause: CausalNode, effect: CausalNode,
                           paths: List[CausalPath]) -> List[str]:
        """Suggest prevention strategies"""
        strategies = []
        
        # Check for temporal patterns
        temporal_edges = [e for p in paths for e in p.edges 
                         if e.relation_type == CausalRelationType.TEMPORAL]
        if temporal_edges:
            strategies.append("Add delays or timeouts to prevent race conditions")
        
        # Check for conditional patterns
        conditional_edges = [e for p in paths for e in p.edges 
                           if e.relation_type == CausalRelationType.CONDITIONAL]
        if conditional_edges:
            conditions = set(e.condition for e in conditional_edges if e.condition)
            strategies.append(f"Check conditions before execution: {', '.join(conditions)}")
        
        # General strategies
        strategies.append(f"Add validation to prevent: {cause.description}")
        strategies.append(f"Monitor for early signs of: {cause.description}")
        
        return strategies


class WisdomExtractor:
    """Extracts wisdom and principles from causal patterns"""
    
    def __init__(self, causal_graph: CausalGraph):
        self.graph = causal_graph
        self.wisdom_base: Dict[str, ExtractedWisdom] = {}
        self.pattern_buffer: deque = deque(maxlen=100)
        
    def observe_pattern(self, pattern: Dict[str, Any]):
        """Observe a pattern for wisdom extraction"""
        self.pattern_buffer.append({
            'pattern': pattern,
            'timestamp': datetime.now()
        })
        
        # Try to extract wisdom if enough patterns
        if len(self.pattern_buffer) >= 10:
            self.extract_wisdom()
    
    def extract_wisdom(self) -> List[ExtractedWisdom]:
        """Extract wisdom from observed patterns"""
        wisdom_list = []
        
        # Analyze pattern buffer
        patterns = [p['pattern'] for p in self.pattern_buffer]
        
        # Extract different types of wisdom
        wisdom_list.extend(self._extract_recurring_patterns(patterns))
        wisdom_list.extend(self._extract_principles(patterns))
        wisdom_list.extend(self._extract_anomalies(patterns))
        wisdom_list.extend(self._extract_evolution(patterns))
        
        # Store new wisdom
        for wisdom in wisdom_list:
            if wisdom.wisdom_id not in self.wisdom_base:
                self.wisdom_base[wisdom.wisdom_id] = wisdom
                logger.info(f"New wisdom discovered: {wisdom.statement}")
        
        return wisdom_list
    
    def _extract_recurring_patterns(self, patterns: List[Dict]) -> List[ExtractedWisdom]:
        """Extract recurring patterns"""
        wisdom_list = []
        
        # Count pattern occurrences
        pattern_counts = defaultdict(int)
        for p in patterns:
            pattern_key = json.dumps(p.get('type', ''), sort_keys=True)
            pattern_counts[pattern_key] += 1
        
        # Find patterns that occur frequently
        for pattern_key, count in pattern_counts.items():
            if count >= 5:  # Threshold for "recurring"
                wisdom = ExtractedWisdom(
                    wisdom_id=f"pattern_{hash(pattern_key)}",
                    wisdom_type=WisdomType.PATTERN,
                    statement=f"Pattern '{pattern_key}' occurs frequently ({count} times)",
                    confidence=count / len(patterns),
                    supporting_evidence=[f"Observed {count} times in recent history"],
                    applicable_contexts=["pattern_recognition", "prediction"]
                )
                wisdom_list.append(wisdom)
        
        return wisdom_list
    
    def _extract_principles(self, patterns: List[Dict]) -> List[ExtractedWisdom]:
        """Extract general principles from patterns"""
        wisdom_list = []
        
        # Analyze cause-effect relationships
        cause_effect_pairs = defaultdict(list)
        for p in patterns:
            if 'cause' in p and 'effect' in p:
                cause_effect_pairs[p['cause']].append(p['effect'])
        
        # Find consistent cause-effect relationships
        for cause, effects in cause_effect_pairs.items():
            if len(effects) >= 3:
                most_common_effect = max(set(effects), key=effects.count)
                consistency = effects.count(most_common_effect) / len(effects)
                
                if consistency > 0.7:  # High consistency
                    wisdom = ExtractedWisdom(
                        wisdom_id=f"principle_{hash(cause)}",
                        wisdom_type=WisdomType.PRINCIPLE,
                        statement=f"{cause} consistently leads to {most_common_effect}",
                        confidence=consistency,
                        supporting_evidence=[f"Observed in {len(effects)} cases"],
                        applicable_contexts=["causation", "prediction"]
                    )
                    wisdom_list.append(wisdom)
        
        return wisdom_list
    
    def _extract_anomalies(self, patterns: List[Dict]) -> List[ExtractedWisdom]:
        """Extract anomalies and unusual patterns"""
        wisdom_list = []
        
        # Find patterns that occur only once
        pattern_counts = defaultdict(int)
        for p in patterns:
            pattern_key = json.dumps(p, sort_keys=True)
            pattern_counts[pattern_key] += 1
        
        unique_patterns = [p for p, count in pattern_counts.items() if count == 1]
        
        for pattern_str in unique_patterns[:3]:  # Top 3 anomalies
            pattern = json.loads(pattern_str)
            wisdom = ExtractedWisdom(
                wisdom_id=f"anomaly_{hash(pattern_str)}",
                wisdom_type=WisdomType.ANOMALY,
                statement=f"Unusual pattern detected: {pattern.get('type', 'unknown')}",
                confidence=0.5,  # Low confidence for anomalies
                supporting_evidence=["Unique occurrence in recent history"],
                applicable_contexts=["anomaly_detection", "investigation"]
            )
            wisdom_list.append(wisdom)
        
        return wisdom_list
    
    def _extract_evolution(self, patterns: List[Dict]) -> List[ExtractedWisdom]:
        """Extract how things evolve over time"""
        wisdom_list = []
        
        # Group patterns by time windows
        time_windows = defaultdict(list)
        for p in self.pattern_buffer:
            window = p['timestamp'].hour // 6  # 6-hour windows
            time_windows[window].append(p['pattern'])
        
        if len(time_windows) >= 2:
            # Compare early vs late patterns
            early_window = min(time_windows.keys())
            late_window = max(time_windows.keys())
            
            early_patterns = time_windows[early_window]
            late_patterns = time_windows[late_window]
            
            # Find evolution
            early_types = set(p.get('type') for p in early_patterns)
            late_types = set(p.get('type') for p in late_patterns)
            
            new_types = late_types - early_types
            if new_types:
                wisdom = ExtractedWisdom(
                    wisdom_id=f"evolution_{hash(str(new_types))}",
                    wisdom_type=WisdomType.EVOLUTION,
                    statement=f"System evolving: new patterns {new_types} emerging",
                    confidence=0.7,
                    supporting_evidence=["Temporal analysis shows change"],
                    applicable_contexts=["adaptation", "learning"]
                )
                wisdom_list.append(wisdom)
        
        return wisdom_list
    
    def apply_wisdom(self, context: Dict[str, Any]) -> List[ExtractedWisdom]:
        """Apply relevant wisdom to current context"""
        applicable_wisdom = []
        
        for wisdom in self.wisdom_base.values():
            # Check if wisdom applies to context
            context_match = any(
                ctx in context.get('type', '') 
                for ctx in wisdom.applicable_contexts
            )
            
            if context_match and wisdom.confidence > 0.6:
                applicable_wisdom.append(wisdom)
                wisdom.apply()  # Track usage
        
        return sorted(applicable_wisdom, key=lambda w: w.confidence, reverse=True)


class AdvancedCausalReasoning:
    """
    Main system for advanced causal understanding
    Combines graph analysis, root cause analysis, and wisdom extraction
    """
    
    def __init__(self):
        self.causal_graph = CausalGraph()
        self.root_cause_analyzer = RootCauseAnalyzer(self.causal_graph)
        self.wisdom_extractor = WisdomExtractor(self.causal_graph)
        
        # Event tracking
        self.event_buffer: deque = deque(maxlen=1000)
        self.learning_enabled = True
        
        # Initialize with basic causal knowledge
        self._initialize_base_knowledge()
    
    def _initialize_base_knowledge(self):
        """Initialize with basic NixOS causal relationships"""
        # Common command-error relationships
        self._add_causal_relationship(
            "sudo_missing", "permission_denied",
            CausalRelationType.DIRECT, 0.95
        )
        
        self._add_causal_relationship(
            "package_not_found", "installation_failure",
            CausalRelationType.DIRECT, 0.90
        )
        
        self._add_causal_relationship(
            "network_down", "download_failure",
            CausalRelationType.DIRECT, 0.85
        )
        
        self._add_causal_relationship(
            "disk_full", "write_failure",
            CausalRelationType.DIRECT, 0.95
        )
        
        # Temporal relationships
        self._add_causal_relationship(
            "system_update", "configuration_change",
            CausalRelationType.TEMPORAL, 0.70,
            time_lag_ms=5000
        )
        
        # Conditional relationships
        self._add_causal_relationship(
            "flake_enabled", "improved_reproducibility",
            CausalRelationType.CONDITIONAL, 0.80,
            condition="nix.conf contains 'experimental-features = flakes'"
        )
    
    def _add_causal_relationship(self, source: str, target: str,
                                relation_type: CausalRelationType,
                                strength: float,
                                time_lag_ms: Optional[int] = None,
                                condition: Optional[str] = None):
        """Helper to add causal relationship"""
        # Add nodes if not exist
        if source not in self.causal_graph.nodes:
            self.causal_graph.add_node(CausalNode(
                node_id=source,
                node_type="cause",
                description=source.replace('_', ' ').title()
            ))
        
        if target not in self.causal_graph.nodes:
            self.causal_graph.add_node(CausalNode(
                node_id=target,
                node_type="effect",
                description=target.replace('_', ' ').title()
            ))
        
        # Add edge
        edge = CausalEdge(
            source=source,
            target=target,
            relation_type=relation_type,
            strength=strength,
            confidence=0.8,  # Initial confidence
            time_lag_ms=time_lag_ms,
            condition=condition
        )
        self.causal_graph.add_edge(edge)
    
    def observe_event(self, event: Dict[str, Any]):
        """Observe an event for causal learning"""
        self.event_buffer.append({
            'event': event,
            'timestamp': datetime.now()
        })
        
        # Extract causal relationships
        if self.learning_enabled:
            self._learn_from_event(event)
        
        # Extract wisdom
        self.wisdom_extractor.observe_pattern(event)
    
    def _learn_from_event(self, event: Dict[str, Any]):
        """Learn causal relationships from event"""
        event_type = event.get('type')
        
        if event_type == 'command_execution':
            command = event.get('command')
            result = event.get('result')
            
            # Learn command-result relationship
            if command and result:
                node_id_cmd = f"cmd_{hash(command)}"
                node_id_result = f"result_{result}"
                
                # Add nodes
                if node_id_cmd not in self.causal_graph.nodes:
                    self.causal_graph.add_node(CausalNode(
                        node_id=node_id_cmd,
                        node_type="command",
                        description=command
                    ))
                
                if node_id_result not in self.causal_graph.nodes:
                    self.causal_graph.add_node(CausalNode(
                        node_id=node_id_result,
                        node_type="outcome",
                        description=result
                    ))
                
                # Add or strengthen edge
                edge_key = (node_id_cmd, node_id_result)
                if edge_key in self.causal_graph.edges:
                    self.causal_graph.edges[edge_key].update_strength()
                else:
                    edge = CausalEdge(
                        source=node_id_cmd,
                        target=node_id_result,
                        relation_type=CausalRelationType.PROBABILISTIC,
                        strength=0.1,
                        confidence=0.1
                    )
                    self.causal_graph.add_edge(edge)
    
    def analyze_issue(self, issue: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze an issue using causal reasoning"""
        # Create issue node
        issue_node_id = f"issue_{hash(issue)}"
        if issue_node_id not in self.causal_graph.nodes:
            self.causal_graph.add_node(CausalNode(
                node_id=issue_node_id,
                node_type="error",
                description=issue
            ))
        
        # Find root causes
        root_causes = self.root_cause_analyzer.analyze_issue(
            issue, issue_node_id, context
        )
        
        # Apply wisdom
        applicable_wisdom = self.wisdom_extractor.apply_wisdom({
            'type': 'issue_analysis',
            'issue': issue,
            'context': context
        })
        
        # Generate comprehensive analysis
        return {
            'issue': issue,
            'root_causes': [
                {
                    'cause': rc.cause_node.description,
                    'confidence': rc.confidence,
                    'explanation': rc.explanation,
                    'fixes': rc.suggested_fixes,
                    'prevention': rc.prevention_strategies
                }
                for rc in root_causes[:3]  # Top 3 causes
            ],
            'wisdom_applied': [
                {
                    'statement': w.statement,
                    'type': w.wisdom_type.value,
                    'confidence': w.confidence
                }
                for w in applicable_wisdom
            ],
            'causal_graph_stats': {
                'nodes': len(self.causal_graph.nodes),
                'edges': len(self.causal_graph.edges),
                'cycles': len(self.causal_graph.find_cycles())
            }
        }
    
    def explain_why(self, question: str) -> str:
        """Answer 'why' questions using causal reasoning"""
        # Parse question to extract entities
        # Simplified parsing - in production use NLP
        
        if "why did" in question.lower():
            # Extract what happened
            parts = question.lower().split("why did")[1].strip()
            
            # Find relevant nodes
            relevant_nodes = [
                node for node_id, node in self.causal_graph.nodes.items()
                if any(word in node.description.lower() for word in parts.split())
            ]
            
            if relevant_nodes:
                # Find causes for the most relevant node
                target_node = relevant_nodes[0]
                causes = self.root_cause_analyzer.analyze_issue(
                    target_node.description,
                    target_node.node_id
                )
                
                if causes:
                    top_cause = causes[0]
                    return (f"Based on causal analysis: {top_cause.explanation}. "
                           f"Confidence: {top_cause.confidence:.1%}")
        
        return "I need more data to establish causal relationships for this question."
    
    def get_wisdom_summary(self) -> Dict[str, Any]:
        """Get summary of extracted wisdom"""
        wisdom_by_type = defaultdict(list)
        
        for wisdom in self.wisdom_extractor.wisdom_base.values():
            wisdom_by_type[wisdom.wisdom_type.value].append({
                'statement': wisdom.statement,
                'confidence': wisdom.confidence,
                'usage_count': wisdom.usage_count,
                'discovered': wisdom.discovered_at.isoformat()
            })
        
        return {
            'total_wisdom': len(self.wisdom_extractor.wisdom_base),
            'by_type': dict(wisdom_by_type),
            'most_used': sorted(
                self.wisdom_extractor.wisdom_base.values(),
                key=lambda w: w.usage_count,
                reverse=True
            )[:5]
        }


# Demo
def demo_causal_reasoning():
    """Demonstrate advanced causal reasoning"""
    
    reasoning = AdvancedCausalReasoning()
    
    # Observe some events
    events = [
        {'type': 'command_execution', 'command': 'nixos-rebuild switch', 
         'result': 'permission_denied'},
        {'type': 'command_execution', 'command': 'sudo nixos-rebuild switch',
         'result': 'success'},
        {'type': 'error', 'error': 'disk_full', 'component': 'nix-store'},
        {'type': 'command_execution', 'command': 'nix-collect-garbage',
         'result': 'freed_10gb'},
    ]
    
    for event in events:
        reasoning.observe_event(event)
    
    # Analyze an issue
    analysis = reasoning.analyze_issue(
        "nixos-rebuild failed with permission denied",
        context={'user_level': 'beginner'}
    )
    
    print("Issue Analysis:")
    print(json.dumps(analysis, indent=2, default=str))
    
    # Answer a why question
    answer = reasoning.explain_why("Why did nixos-rebuild fail?")
    print(f"\nQ: Why did nixos-rebuild fail?\nA: {answer}")
    
    # Get wisdom summary
    wisdom = reasoning.get_wisdom_summary()
    print(f"\nWisdom Summary: {json.dumps(wisdom, indent=2, default=str)}")


if __name__ == "__main__":
    demo_causal_reasoning()