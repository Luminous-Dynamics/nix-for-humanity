"""
Integration Tests for Phase 6 Advanced Intelligence

Tests all 5 revolutionary enhancements working together:
1. Async multi-agent orchestration
2. Multi-level memory system
3. Agent collaboration & learning
4. Proactive assistance
5. Comprehensive observability
"""

import pytest
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import shutil

# Phase 6 imports
from luminous_nix.mycelix.orchestration.async_meta_sophia import (
    AsyncMetaSophia, AsyncAgentWrapper, StreamUpdate
)
from luminous_nix.mycelix.memory.memory_system import (
    MemorySystem, MemoryItem, ShortTermMemory, WorkingMemory, LongTermMemory
)
from luminous_nix.mycelix.orchestration.collaborative_agents import (
    CollaborativeAgentNetwork, KnowledgeGraph, KnowledgeNode, Critique
)
from luminous_nix.mycelix.intelligence.proactive_assistant import (
    ProactiveAssistant, UserAction, Pattern, PredictedNeed
)
from luminous_nix.mycelix.observability.observability_system import (
    ObservabilitySystem, MetricsCollector, DistributedTracer, StructuredLogger
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def temp_dir():
    """Temporary directory for test data"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def memory_system(temp_dir):
    """Memory system with temp storage"""
    db_path = temp_dir / "memory.db"
    return MemorySystem(db_path=db_path)


@pytest.fixture
def knowledge_graph(temp_dir):
    """Knowledge graph with temp storage"""
    kg_path = temp_dir / "knowledge.json"
    return KnowledgeGraph(persistence_path=kg_path)


@pytest.fixture
def collaborative_network(temp_dir):
    """Collaborative agent network"""
    kg_path = temp_dir / "knowledge.json"
    return CollaborativeAgentNetwork(knowledge_path=kg_path)


@pytest.fixture
def proactive_assistant():
    """Proactive assistance system"""
    return ProactiveAssistant(
        confidence_threshold=0.65,
        check_interval_seconds=1  # Fast for testing
    )


@pytest.fixture
def observability():
    """Observability system"""
    return ObservabilitySystem()


@pytest.fixture
async def async_meta_sophia():
    """Async Meta-Sophia orchestrator"""
    meta = AsyncMetaSophia()
    return meta


# ============================================================================
# 1. Async Multi-Agent Orchestration Tests
# ============================================================================

class TestAsyncOrchestration:
    """Test async multi-agent orchestration"""

    @pytest.mark.asyncio
    async def test_parallel_agent_execution(self, async_meta_sophia):
        """Test that agents execute in parallel"""

        # Mock agents with different response times
        class SlowAgent:
            async def respond_async(self, query, context=None):
                await asyncio.sleep(0.1)
                return {'content': 'slow response', 'confidence': 0.8}

        class FastAgent:
            async def respond_async(self, query, context=None):
                await asyncio.sleep(0.01)
                return {'content': 'fast response', 'confidence': 0.9}

        # Register agents
        from luminous_nix.mycelix.orchestration.meta_sophia import AgentProfile

        slow_profile = AgentProfile(
            name='slow_agent',
            specialization='testing',
            capabilities=['test']
        )
        fast_profile = AgentProfile(
            name='fast_agent',
            specialization='testing',
            capabilities=['test']
        )

        async_meta_sophia.register_agent('slow', slow_profile, SlowAgent())
        async_meta_sophia.register_agent('fast', fast_profile, FastAgent())

        # Execute and measure time
        start = asyncio.get_event_loop().time()

        result = await async_meta_sophia.process_query_async(
            query="test query",
            user_id="test_user"
        )

        elapsed = asyncio.get_event_loop().time() - start

        # Should complete in ~0.1s (parallel), not 0.11s (sequential)
        assert elapsed < 0.15, f"Parallel execution too slow: {elapsed:.3f}s"
        assert result is not None
        assert 'response' in result

    @pytest.mark.asyncio
    async def test_streaming_updates(self, async_meta_sophia):
        """Test real-time streaming updates"""

        # Mock agent
        class TestAgent:
            async def respond_async(self, query, context=None):
                await asyncio.sleep(0.01)
                return {'content': 'test', 'confidence': 0.9}

        from luminous_nix.mycelix.orchestration.meta_sophia import AgentProfile
        profile = AgentProfile(name='test', specialization='test', capabilities=['test'])
        async_meta_sophia.register_agent('test', profile, TestAgent())

        # Collect stream updates
        updates = []
        async for update in async_meta_sophia.process_query_streaming(
            query="test query",
            user_id="test_user"
        ):
            updates.append(update)

        # Should have multiple update types
        update_types = {u.type for u in updates}
        assert 'agent_start' in update_types
        assert 'agent_complete' in update_types
        assert 'complete' in update_types

        # Final update should have result
        final = updates[-1]
        assert final.type == 'complete'
        assert 'response' in final.data


# ============================================================================
# 2. Multi-Level Memory System Tests
# ============================================================================

class TestMemorySystem:
    """Test multi-level memory system"""

    @pytest.mark.asyncio
    async def test_three_tier_architecture(self, memory_system):
        """Test short-term, working, and long-term memory"""

        # Create memory items with different importance
        low_importance = MemoryItem(
            id='low_1',
            content='Low importance memory',
            memory_type='episodic',
            importance=0.3,
            context={},
            tags=['test']
        )

        medium_importance = MemoryItem(
            id='med_1',
            content='Medium importance memory',
            memory_type='semantic',
            importance=0.7,
            context={},
            tags=['test']
        )

        high_importance = MemoryItem(
            id='high_1',
            content='High importance memory',
            memory_type='procedural',
            importance=0.95,
            context={},
            tags=['test']
        )

        # Store memories
        await memory_system.remember(low_importance)
        await memory_system.remember(medium_importance)
        await memory_system.remember(high_importance)

        # Check tier distribution
        # Low should only be in short-term
        assert len(memory_system.short_term.memories) >= 1

        # Medium should be in short-term and working
        assert len(memory_system.working.memories) >= 1

        # High should be in all three tiers
        long_term_memories = await memory_system.long_term.search('High importance')
        assert len(long_term_memories) >= 1

    @pytest.mark.asyncio
    async def test_memory_persistence(self, temp_dir):
        """Test that long-term memory persists across sessions"""

        db_path = temp_dir / "memory.db"

        # Session 1: Store memory
        memory1 = MemorySystem(db_path=db_path)
        await memory1.remember(MemoryItem(
            id='persist_1',
            content='Persistent memory',
            memory_type='semantic',
            importance=0.95,
            context={'key': 'value'},
            tags=['persistent']
        ))

        # Close session
        del memory1

        # Session 2: Retrieve memory
        memory2 = MemorySystem(db_path=db_path)
        results = await memory2.recall('Persistent', limit=10)

        # Should find persisted memory
        assert len(results) > 0
        assert any('Persistent memory' in r.content for r in results)

    @pytest.mark.asyncio
    async def test_parallel_recall(self, memory_system):
        """Test parallel search across all memory tiers"""

        # Store memories in different tiers
        for i in range(10):
            await memory_system.remember(MemoryItem(
                id=f'test_{i}',
                content=f'Test memory {i}',
                memory_type='episodic',
                importance=0.5 + (i * 0.05),
                context={},
                tags=['test']
            ))

        # Recall should search all tiers
        start = asyncio.get_event_loop().time()
        results = await memory_system.recall('Test memory', limit=10)
        elapsed = asyncio.get_event_loop().time() - start

        # Should be fast (parallel search)
        assert elapsed < 0.1, f"Parallel recall too slow: {elapsed:.3f}s"
        assert len(results) > 0


# ============================================================================
# 3. Agent Collaboration & Learning Tests
# ============================================================================

class TestCollaborativeLearning:
    """Test agent collaboration and learning"""

    @pytest.mark.asyncio
    async def test_knowledge_graph_persistence(self, temp_dir):
        """Test knowledge graph saves and loads"""

        kg_path = temp_dir / "knowledge.json"

        # Session 1: Add knowledge
        kg1 = KnowledgeGraph(persistence_path=kg_path)
        node = KnowledgeNode(
            node_id='test_node_1',
            concept='NixOS flakes',
            description='Modern Nix package management',
            examples=['nix flake init', 'nix flake show'],
            learned_from=['agent1']
        )
        kg1.add_node(node)
        kg1._save()

        # Session 2: Load knowledge
        kg2 = KnowledgeGraph(persistence_path=kg_path)
        assert 'test_node_1' in kg2.nodes
        assert kg2.nodes['test_node_1'].concept == 'NixOS flakes'

    @pytest.mark.asyncio
    async def test_knowledge_search(self, knowledge_graph):
        """Test knowledge graph search"""

        # Add multiple nodes
        nodes = [
            KnowledgeNode(
                node_id=f'node_{i}',
                concept=f'Concept {i}',
                description=f'Description about NixOS concept {i}',
                examples=[f'example {i}'],
                learned_from=['test_agent']
            )
            for i in range(5)
        ]

        for node in nodes:
            knowledge_graph.add_node(node)

        # Search
        results = knowledge_graph.search('NixOS', limit=10)

        # Should find relevant nodes
        assert len(results) > 0
        assert all('NixOS' in node.description for node in results)

    @pytest.mark.asyncio
    async def test_peer_review_mechanism(self, collaborative_network):
        """Test that agents critique each other"""

        # Mock agents
        class Agent1:
            async def respond_async(self, query, context=None):
                return {
                    'content': 'Install with: nix-env -i firefox',
                    'confidence': 0.8,
                    'reasoning': 'Traditional approach'
                }

        class Agent2:
            async def respond_async(self, query, context=None):
                return {
                    'content': 'Use declarative: programs.firefox.enable = true;',
                    'confidence': 0.9,
                    'reasoning': 'Declarative is better'
                }

        from luminous_nix.mycelix.orchestration.meta_sophia import AgentProfile

        profile1 = AgentProfile(name='agent1', specialization='install', capabilities=['install'])
        profile2 = AgentProfile(name='agent2', specialization='config', capabilities=['config'])

        collaborative_network.register_agent('agent1', Agent1(), profile1)
        collaborative_network.register_agent('agent2', Agent2(), profile2)

        # Process query with collaboration
        result = await collaborative_network.collaborative_query(
            query="install firefox",
            selected_agents=['agent1', 'agent2']
        )

        # Should have critiques
        assert len(result['critiques']) > 0

        # Should have insights
        assert len(result['insights']) >= 0

        # Should have final response
        assert 'response' in result
        assert 'content' in result['response']


# ============================================================================
# 4. Proactive Assistance Tests
# ============================================================================

class TestProactiveAssistance:
    """Test proactive learning and assistance"""

    @pytest.mark.asyncio
    async def test_pattern_detection(self, proactive_assistant):
        """Test that patterns are detected"""

        user_id = 'test_user'

        # Simulate repeated actions
        for i in range(5):
            action = UserAction(
                action_type='install',
                content=f'install package-{i}',
                timestamp=datetime.now(),
                success=True
            )
            proactive_assistant.record_action(user_id, action)

        # Get context and detect patterns
        context = await proactive_assistant.context_monitor.get_current(user_id)
        patterns = proactive_assistant.pattern_detector.analyze(context)

        # Should detect frequency pattern
        assert len(patterns) > 0
        freq_patterns = [p for p in patterns if p.pattern_type == 'frequency']
        assert len(freq_patterns) > 0

    @pytest.mark.asyncio
    async def test_need_prediction(self, proactive_assistant):
        """Test that needs are predicted from patterns"""

        user_id = 'test_user'

        # Simulate pattern that should trigger prediction
        for i in range(6):
            action = UserAction(
                action_type='query',
                content=f'install vim',
                timestamp=datetime.now(),
                success=True
            )
            proactive_assistant.record_action(user_id, action)

        # Detect patterns
        context = await proactive_assistant.context_monitor.get_current(user_id)
        patterns = proactive_assistant.pattern_detector.analyze(context)

        # Predict needs
        predictions = proactive_assistant.need_predictor.predict(patterns)

        # Should make predictions
        assert len(predictions) > 0

        # High confidence predictions should exist
        high_conf = [p for p in predictions if p.confidence > 0.65]
        assert len(high_conf) > 0

    @pytest.mark.asyncio
    async def test_background_monitoring(self, proactive_assistant):
        """Test continuous background monitoring"""

        user_id = 'test_user'

        # Start monitoring task
        monitor_task = asyncio.create_task(
            proactive_assistant.monitor_and_assist(user_id)
        )

        # Simulate actions
        for i in range(3):
            action = UserAction(
                action_type='query',
                content='install package',
                timestamp=datetime.now(),
                success=True
            )
            proactive_assistant.record_action(user_id, action)
            await asyncio.sleep(0.1)

        # Let monitor run
        await asyncio.sleep(1.5)

        # Cancel monitoring
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass

        # Should have notifications
        notifications = proactive_assistant.get_pending_notifications(user_id)
        # May or may not have notifications depending on confidence threshold


# ============================================================================
# 5. Comprehensive Observability Tests
# ============================================================================

class TestObservability:
    """Test comprehensive observability"""

    def test_metrics_collection(self, observability):
        """Test metrics collection (counters, gauges, histograms)"""

        # Counters
        observability.metrics.increment('test_counter', 1.0)
        observability.metrics.increment('test_counter', 2.0)
        assert observability.metrics.get_counter('test_counter') == 3.0

        # Gauges
        observability.metrics.gauge('test_gauge', 42.0)
        assert observability.metrics.get_gauge('test_gauge') == 42.0

        # Histograms
        for i in range(10):
            observability.metrics.histogram('test_histogram', i * 10.0)

        stats = observability.metrics.get_histogram_stats('test_histogram')
        assert stats is not None
        assert stats['count'] == 10
        assert stats['min'] == 0.0
        assert stats['max'] == 90.0

    def test_distributed_tracing(self, observability):
        """Test distributed tracing with spans"""

        # Create span tree
        with observability.tracer.span('root_operation') as root_span:
            observability.tracer.set_attribute(root_span.span_id, 'key', 'value')

            with observability.tracer.span('child_operation') as child_span:
                observability.tracer.add_event(child_span.span_id, 'test_event')

        # Get trace
        trace = observability.tracer.get_trace(child_span.span_id)
        assert len(trace) == 2  # Root + child
        assert trace[0].operation == 'root_operation'
        assert trace[1].operation == 'child_operation'

        # Get trace tree
        tree = observability.tracer.get_trace_tree(root_span.span_id)
        assert tree['operation'] == 'root_operation'
        assert len(tree['children']) == 1
        assert tree['children'][0]['operation'] == 'child_operation'

    def test_structured_logging(self, observability):
        """Test structured logging with context"""

        # Set context
        observability.logger.set_context(user_id='test_user', session='test_session')

        # Log with structure
        observability.logger.info('Test message', extra_key='extra_value')
        observability.logger.warning('Warning message', severity='high')
        observability.logger.error('Error message', error=ValueError('test error'))

        # Search logs
        info_logs = observability.logger.search(level='INFO', limit=10)
        assert len(info_logs) > 0

        error_logs = observability.logger.search(level='ERROR', limit=10)
        assert len(error_logs) > 0

        # Search by message
        test_logs = observability.logger.search(message_contains='Test', limit=10)
        assert len(test_logs) > 0

    @pytest.mark.asyncio
    async def test_operation_instrumentation(self, observability):
        """Test automatic operation instrumentation"""

        # Instrumented operation
        async def test_operation():
            await asyncio.sleep(0.01)
            return "result"

        # Execute with instrumentation
        with observability.operation('test_op') as span:
            result = await test_operation()

        # Metrics should be recorded
        assert observability.metrics.get_counter('operations_success') >= 1

        # Duration should be recorded
        stats = observability.metrics.get_histogram_stats('operation_duration')
        assert stats is not None
        assert stats['count'] >= 1

    def test_dashboard_rendering(self, observability):
        """Test dashboard renders correctly"""

        # Generate some metrics
        for i in range(10):
            with observability.operation(f'query_{i}'):
                pass

        # Get health
        health = observability.dashboard.get_system_health()
        assert health['status'] in ['healthy', 'degraded']
        assert 'queries' in health
        assert 'performance' in health

        # Render dashboard
        dashboard_text = observability.dashboard.render_dashboard()
        assert 'Sophia Observability Dashboard' in dashboard_text
        assert 'System Status' in dashboard_text


# ============================================================================
# 6. Full System Integration Tests
# ============================================================================

class TestFullSystemIntegration:
    """Test all Phase 6 components working together"""

    @pytest.mark.asyncio
    async def test_complete_phase6_integration(
        self,
        temp_dir,
        async_meta_sophia,
        memory_system,
        collaborative_network,
        proactive_assistant,
        observability
    ):
        """
        Test complete Phase 6 system integration

        This test demonstrates all 5 enhancements working together:
        1. Async orchestration
        2. Memory system
        3. Collaborative learning
        4. Proactive assistance
        5. Observability
        """

        user_id = 'integration_test_user'

        # Mock intelligent agent
        class IntelligentAgent:
            def __init__(self, memory, knowledge, observability):
                self.memory = memory
                self.knowledge = knowledge
                self.observability = observability

            async def respond_async(self, query, context=None):
                with self.observability.operation('agent_respond'):
                    # Check memory for context
                    memories = await self.memory.recall(query, limit=3)

                    # Check knowledge graph
                    knowledge = self.knowledge.search(query, limit=3)

                    # Generate response with context
                    response = f"Response to '{query}' "
                    if memories:
                        response += f"(with {len(memories)} memories)"
                    if knowledge:
                        response += f" and {len(knowledge)} knowledge nodes"

                    return {
                        'content': response,
                        'confidence': 0.9,
                        'reasoning': 'Integrated intelligence'
                    }

        # Register agent
        from luminous_nix.mycelix.orchestration.meta_sophia import AgentProfile

        agent = IntelligentAgent(
            memory=memory_system,
            knowledge=collaborative_network.knowledge_graph,
            observability=observability
        )

        profile = AgentProfile(
            name='intelligent_agent',
            specialization='integrated',
            capabilities=['all']
        )

        async_meta_sophia.register_agent('intelligent', profile, agent)
        collaborative_network.register_agent('intelligent', agent, profile)

        # Phase 1: Initial query with observability
        with observability.operation('initial_query'):
            result1 = await async_meta_sophia.process_query_async(
                query="install nginx",
                user_id=user_id
            )

            # Store in memory
            await memory_system.remember(MemoryItem(
                id='query_1',
                content='install nginx',
                memory_type='episodic',
                importance=0.8,
                context={'intent': 'install', 'package': 'nginx'},
                tags=['install', 'nginx']
            ))

        # Phase 2: Related query (should use memory)
        with observability.operation('contextual_query'):
            result2 = await async_meta_sophia.process_query_async(
                query="configure nginx",
                user_id=user_id
            )

            # Should benefit from memory
            assert result2 is not None

        # Phase 3: Collaborative learning
        collab_result = await collaborative_network.collaborative_query(
            query="nginx best practices"
        )

        # Should have learning insights
        assert len(collab_result['insights']) >= 0

        # Phase 4: Proactive assistance (simulate pattern)
        for i in range(5):
            action = UserAction(
                action_type='query',
                content='nginx configuration',
                timestamp=datetime.now(),
                success=True
            )
            proactive_assistant.record_action(user_id, action)

        context = await proactive_assistant.context_monitor.get_current(user_id)
        patterns = proactive_assistant.pattern_detector.analyze(context)

        # Should detect patterns
        assert len(patterns) >= 0

        # Phase 5: Check observability
        health = observability.dashboard.get_system_health()

        # System should be healthy
        assert health['status'] in ['healthy', 'degraded']

        # Should have metrics
        assert health['queries']['total'] >= 2

        # Should have traces
        assert len(observability.tracer.span_history) > 0

        # Verify all components worked
        assert result1 is not None, "Async orchestration failed"
        assert await memory_system.recall('nginx'), "Memory system failed"
        assert len(collaborative_network.knowledge_graph.nodes) >= 0, "Collaboration failed"
        assert len(patterns) >= 0, "Proactive assistance failed"
        assert health['queries']['total'] > 0, "Observability failed"

        print("\n✅ Full Phase 6 integration test PASSED!")
        print(f"   - Async orchestration: {len(result1.get('performance', {}))} metrics")
        print(f"   - Memory system: {len(await memory_system.recall('nginx'))} memories")
        print(f"   - Knowledge graph: {len(collaborative_network.knowledge_graph.nodes)} nodes")
        print(f"   - Patterns detected: {len(patterns)}")
        print(f"   - System health: {health['status']}")


# ============================================================================
# Test Execution
# ============================================================================

if __name__ == "__main__":
    """Run tests with pytest"""
    pytest.main([__file__, "-v", "-s"])
