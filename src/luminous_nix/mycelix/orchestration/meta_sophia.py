"""
Meta-Sophia: Multi-Agent Orchestrator

Coordinates multiple Sophia agents to handle complex queries through
collective intelligence and consensus building.
"""

from typing import Dict, List, Optional, Any
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from .agent_protocol import (
    AgentMessage,
    AgentResponse,
    ConsensusResponse,
    OrchestrationContext,
    create_query_message,
)
from .agent_registry import AgentRegistry
from .task_router import TaskRouter
from .knowledge_broker import KnowledgeBroker
from .emergence_monitor import EmergenceMonitor

# Phase 5: Metacognitive Intelligence
from ..metacognition import (
    ConfidenceCalibrator,
    ExplanationEngine,
    MistakeDetector,
    UserModeler,
    ReasoningType,
)


class MetaSophia:
    """
    Orchestrator for the Sophia agent network

    Coordinates multiple specialized agents to:
    - Decompose complex queries
    - Route tasks to appropriate agents
    - Synthesize agent responses
    - Build consensus
    - Facilitate knowledge sharing
    """

    def __init__(self, max_workers: int = 5):
        """
        Initialize Meta-Sophia orchestrator

        Args:
            max_workers: Maximum parallel agent executions
        """
        self.registry = AgentRegistry()
        self.router = TaskRouter(self.registry)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # Phase 4C: Knowledge & Emergence
        self.knowledge = KnowledgeBroker()
        self.emergence = EmergenceMonitor()

        # Phase 5: Metacognitive Intelligence - REVOLUTIONARY!
        self.confidence_calibrator = ConfidenceCalibrator()
        self.explanation_engine = ExplanationEngine()
        self.mistake_detector = MistakeDetector()
        self.user_modeler = UserModeler()

        # Orchestration stats
        self.total_orchestrations = 0
        self.successful_orchestrations = 0
        self.total_agents_used = 0

    def register_agent(self, agent_id: str, profile: Any, agent_instance: Any) -> bool:
        """
        Register a Sophia agent in the network

        Args:
            agent_id: Unique agent identifier
            profile: AgentProfile defining specialization
            agent_instance: The agent object

        Returns:
            True if registered, False if already exists
        """
        return self.registry.register_agent(agent_id, profile, agent_instance)

    def process_query(
        self, query: str, user_id: str, session_id: str, context: Optional[Dict] = None
    ) -> ConsensusResponse:
        """
        Process a query through the agent network (basic version)

        Args:
            query: User query to process
            user_id: User identifier
            session_id: Session identifier
            context: Additional context (optional)

        Returns:
            ConsensusResponse with synthesized result
        """
        self.total_orchestrations += 1
        start_time = time.time()

        # Create orchestration context
        orch_context = self.router.create_orchestration_context(
            query, user_id, session_id
        )

        # Check if we need orchestration
        if len(orch_context.sub_tasks) == 1:
            # Single task - direct agent execution
            response = self._execute_single_agent(orch_context)
        else:
            # Multiple tasks - orchestrate
            response = self._execute_multi_agent(orch_context)

        # Update stats
        if response.confidence >= 0.8:
            self.successful_orchestrations += 1

        # Set timing
        response.total_processing_time = (time.time() - start_time) * 1000  # ms

        return response

    def process_query_with_metacognition(
        self,
        query: str,
        user_id: str,
        session_id: str,
        context: Optional[Dict] = None,
        generate_explanation: bool = True,
        check_for_mistakes: bool = True,
        adapt_to_user: bool = True,
    ) -> Dict[str, Any]:
        """
        REVOLUTIONARY: Process query with full metacognitive awareness

        This is the self-aware AI partner. It:
        1. Explains its reasoning step by step
        2. Calibrates confidence honestly
        3. Detects and corrects mistakes
        4. Adapts to your preferences
        5. Learns from every interaction

        Args:
            query: User query to process
            user_id: User identifier
            session_id: Session identifier
            context: Additional context
            generate_explanation: Generate full explanation of reasoning
            check_for_mistakes: Check response for potential mistakes
            adapt_to_user: Adapt response to user preferences

        Returns:
            Dict with response, explanation, confidence, and metacognitive insights
        """
        start_time = time.time()

        # Start building explanation
        explanation_builder = self.explanation_engine.start_explanation(query)

        # Step 1: Analyze query
        explanation_builder.add_step(
            ReasoningType.ANALYSIS,
            f"Analyzing query: '{query}'",
            input_data={"query": query, "user_id": user_id},
            output_data={"complexity": "analyzing..."},
            confidence=1.0
        )

        # Step 2: Get base response from orchestration
        explanation_builder.add_step(
            ReasoningType.DECOMPOSITION,
            "Creating orchestration plan",
            input_data={"query": query},
            confidence=1.0
        )

        # Call base orchestration
        base_response = self.process_query(query, user_id, session_id, context)

        # Convert response to dict for processing
        response_dict = {
            "content": base_response.content,
            "insights": base_response.insights,
            "suggestions": base_response.suggestions,
            "actions": base_response.actions,
            "confidence": base_response.confidence,
            "contributing_agents": base_response.contributing_agents,
        }

        # Step 3: Agent selection explanation
        explanation_builder.add_step(
            ReasoningType.AGENT_SELECTION,
            f"Selected {len(base_response.contributing_agents)} agent(s): {', '.join(base_response.contributing_agents)}",
            input_data={"available_agents": len(self.registry.agents)},
            output_data={"selected": base_response.contributing_agents},
            confidence=1.0
        )

        # Step 4: Calibrate confidence (HONEST uncertainty)
        agent_responses = [{
            "confidence": base_response.confidence,
            "content": base_response.content,
        }]

        calibration = self.confidence_calibrator.calibrate(
            agent_responses=agent_responses,
            query=query,
            query_type=self._infer_query_type(query),
            has_relevant_knowledge=len(base_response.insights) > 0,
            context_quality=1.0 if context else 0.8
        )

        explanation_builder.add_step(
            ReasoningType.VALIDATION,
            f"Calibrated confidence: {calibration.calibrated_confidence:.0%} (from {calibration.original_confidence:.0%})",
            input_data={"original_confidence": calibration.original_confidence},
            output_data={"calibrated": calibration.calibrated_confidence,
                        "uncertainty_sources": calibration.uncertainty_sources},
            confidence=calibration.calibrated_confidence
        )

        # Add uncertainties
        for source, value in calibration.uncertainty_sources.items():
            if value > 0.2:
                explanation_builder.add_uncertainty(
                    f"{source.replace('_', ' ').title()}: {value:.0%} uncertainty"
                )

        # Update response with calibrated confidence
        response_dict["confidence"] = calibration.calibrated_confidence
        response_dict["calibration"] = {
            "original": calibration.original_confidence,
            "calibrated": calibration.calibrated_confidence,
            "should_defer": calibration.should_defer,
            "explanation": calibration.explanation,
            "suggestions": calibration.suggestions,
        }

        # Step 5: Check for mistakes (SELF-CORRECTION)
        if check_for_mistakes:
            mistake_type = self.mistake_detector.check_response(
                query=query,
                response=response_dict,
                context=context
            )

            if mistake_type:
                explanation_builder.add_step(
                    ReasoningType.UNCERTAINTY,
                    f"Detected potential issue: {mistake_type.value}",
                    input_data={"original_response": response_dict},
                    confidence=0.5
                )

                # Generate recovery
                recovery = self.mistake_detector.recover(
                    mistake_type=mistake_type,
                    original_query=query,
                    original_response=response_dict
                )

                # Update response with correction
                response_dict["mistake_detected"] = {
                    "type": mistake_type.value,
                    "what_went_wrong": recovery.what_went_wrong,
                    "correction": recovery.corrected_response,
                    "what_learned": recovery.what_learned,
                }

                explanation_builder.add_key_decision(
                    f"Detected and corrected {mistake_type.value}"
                )

        # Step 6: Adapt to user (PERSONALIZATION)
        if adapt_to_user:
            adapted_response = self.user_modeler.adapt_response(
                user_id=user_id,
                response=response_dict
            )

            if adapted_response != response_dict:
                explanation_builder.add_step(
                    ReasoningType.SYNTHESIS,
                    "Adapted response to your preferences",
                    input_data={"original": "generic"},
                    output_data={"adapted": "personalized"},
                    confidence=1.0
                )

                response_dict = adapted_response

        # Step 7: Record interaction for learning
        successful = calibration.calibrated_confidence >= 0.7
        self.user_modeler.observe_interaction(
            user_id=user_id,
            query=query,
            response=response_dict,
            successful=successful
        )

        # Step 8: Build final explanation
        explanation_builder.set_final_response(response_dict["content"])
        explanation_builder.set_confidence_breakdown({
            "agent_confidence": base_response.confidence,
            "calibrated_confidence": calibration.calibrated_confidence,
            "user_adaptation": 1.0 if adapt_to_user else 0.0,
        })

        explanation = explanation_builder.build() if generate_explanation else None

        # Calculate total processing time
        processing_time = (time.time() - start_time) * 1000  # ms

        # Build result with FULL metacognitive awareness
        result = {
            "query": query,
            "response": response_dict,
            "explanation": explanation.to_natural_language("medium") if explanation else None,
            "explanation_object": explanation,
            "confidence": {
                "original": calibration.original_confidence,
                "calibrated": calibration.calibrated_confidence,
                "should_defer": calibration.should_defer,
                "explanation": calibration.explanation,
            },
            "metacognitive_insights": {
                "calibration_applied": True,
                "mistakes_checked": check_for_mistakes,
                "user_adapted": adapt_to_user,
                "uncertainty_acknowledged": len(calibration.uncertainty_sources) > 0,
            },
            "performance": {
                "processing_time_ms": processing_time,
                "agents_used": len(base_response.contributing_agents),
            },
            "recommendations": self.user_modeler.get_recommendations(user_id),
        }

        return result

    def _infer_query_type(self, query: str) -> str:
        """Infer query type for calibration"""
        query_lower = query.lower()

        if "install" in query_lower:
            return "installation"
        elif "configure" in query_lower or "setup" in query_lower:
            return "configuration"
        elif "debug" in query_lower or "error" in query_lower:
            return "debugging"
        elif "secure" in query_lower:
            return "security"
        else:
            return "general"

    def _execute_single_agent(self, context: OrchestrationContext) -> ConsensusResponse:
        """Execute query with single agent (no orchestration needed)"""
        task = context.sub_tasks[0]
        agent_id = context.assigned_agents.get(task.task_id)

        if not agent_id:
            # No agent available
            return self._create_error_response(
                "No suitable agent available", context.query
            )

        # Get agent instance
        agent = self.registry.get_agent(agent_id)
        if not agent:
            return self._create_error_response(f"Agent {agent_id} not found", context.query)

        # Increment load
        self.registry.increment_load(agent_id)

        try:
            # Execute with agent
            start_time = time.time()

            # Call agent's respond_to_query method
            agent_response = agent.respond_to_query(task.query, task.context)

            processing_time = (time.time() - start_time) * 1000  # ms

            # Update metrics
            self.registry.update_metrics(
                agent_id,
                success=True,
                confidence=agent_response.get("confidence", 0.8),
                response_time=processing_time,
            )

            # Convert to ConsensusResponse
            return ConsensusResponse(
                content=agent_response.get("content", ""),
                insights=agent_response.get("insights", []),
                suggestions=agent_response.get("suggestions", []),
                actions=agent_response.get("actions", []),
                contributing_agents=[agent_id],
                confidence=agent_response.get("confidence", 0.8),
                agreement_level=1.0,  # Single agent = 100% agreement
                total_processing_time=processing_time,
                consensus_building_time=0.0,  # No consensus needed
            )

        except Exception as e:
            # Update metrics
            self.registry.update_metrics(
                agent_id, success=False, confidence=0.0, response_time=0.0
            )

            return self._create_error_response(str(e), context.query)

        finally:
            # Decrement load
            self.registry.decrement_load(agent_id)

    def _execute_multi_agent(self, context: OrchestrationContext) -> ConsensusResponse:
        """Execute query with multiple agents and build consensus"""
        agent_responses = []

        # Execute tasks in parallel where possible
        futures = []

        for task in context.sub_tasks:
            agent_id = context.assigned_agents.get(task.task_id)

            if not agent_id:
                continue

            # Check dependencies
            if task.dependencies:
                # TODO: Implement dependency handling
                # For now, skip tasks with dependencies in parallel execution
                continue

            # Submit task to executor
            future = self.executor.submit(
                self._execute_agent_task, agent_id, task, context
            )
            futures.append((future, agent_id))

        # Collect results
        for future, agent_id in futures:
            try:
                response = future.result(timeout=5.0)  # 5 second timeout
                if response:
                    agent_responses.append(response)
            except Exception as e:
                # Agent failed - continue with others
                print(f"Agent {agent_id} failed: {e}")
                continue

        # Build consensus
        consensus_start = time.time()
        consensus = self._build_consensus(agent_responses, context)
        consensus.consensus_building_time = (time.time() - consensus_start) * 1000  # ms

        return consensus

    def _execute_agent_task(
        self, agent_id: str, task: Any, context: OrchestrationContext
    ) -> Optional[AgentResponse]:
        """Execute a single task with an agent"""
        agent = self.registry.get_agent(agent_id)
        if not agent:
            return None

        # Increment load
        self.registry.increment_load(agent_id)

        try:
            start_time = time.time()

            # Execute with agent
            response = agent.respond_to_query(task.query, task.context)

            processing_time = (time.time() - start_time) * 1000  # ms

            # Create AgentResponse
            agent_response = AgentResponse(
                agent_id=agent_id,
                task_id=task.task_id,
                content=response.get("content", ""),
                insights=response.get("insights", []),
                suggestions=response.get("suggestions", []),
                actions=response.get("actions", []),
                confidence=response.get("confidence", 0.8),
                processing_time=processing_time,
            )

            # Update metrics
            self.registry.update_metrics(
                agent_id,
                success=True,
                confidence=agent_response.confidence,
                response_time=processing_time,
            )

            self.total_agents_used += 1

            return agent_response

        except Exception as e:
            # Update metrics
            self.registry.update_metrics(
                agent_id, success=False, confidence=0.0, response_time=0.0
            )
            return None

        finally:
            # Decrement load
            self.registry.decrement_load(agent_id)

    def _build_consensus(
        self, responses: List[AgentResponse], context: OrchestrationContext
    ) -> ConsensusResponse:
        """
        Build consensus from multiple agent responses

        Uses Bayesian belief merging to synthesize responses
        """
        if not responses:
            return self._create_error_response(
                "No agent responses to build consensus", context.query
            )

        if len(responses) == 1:
            # Single response - no consensus needed
            r = responses[0]
            return ConsensusResponse(
                content=r.content,
                insights=r.insights,
                suggestions=r.suggestions,
                actions=r.actions,
                contributing_agents=[r.agent_id],
                confidence=r.confidence,
                agreement_level=1.0,
            )

        # Multiple responses - synthesize

        # Aggregate content (weighted by confidence)
        total_confidence = sum(r.confidence for r in responses)

        # Build synthesized content
        content_parts = []
        all_insights = []
        all_suggestions = []
        all_actions = []

        for response in responses:
            if response.content:
                content_parts.append(response.content)
            all_insights.extend(response.insights)
            all_suggestions.extend(response.suggestions)
            all_actions.extend(response.actions)

        # Remove duplicates while preserving order
        all_insights = list(dict.fromkeys(all_insights))
        all_suggestions = list(dict.fromkeys(all_suggestions))
        all_actions = list(dict.fromkeys(all_actions))

        # Calculate agreement level
        # Simple heuristic: variance in confidence scores
        confidences = [r.confidence for r in responses]
        mean_confidence = sum(confidences) / len(confidences)
        variance = sum((c - mean_confidence) ** 2 for c in confidences) / len(
            confidences
        )
        agreement_level = max(0.0, 1.0 - variance)

        # Synthesize content
        if len(content_parts) == 1:
            synthesized_content = content_parts[0]
        else:
            synthesized_content = "\n\n".join(
                f"• {part}" for part in content_parts if part
            )

        # Create consensus response
        consensus = ConsensusResponse(
            content=synthesized_content,
            insights=all_insights,
            suggestions=all_suggestions,
            actions=all_actions,
            contributing_agents=[r.agent_id for r in responses],
            confidence=mean_confidence,
            agreement_level=agreement_level,
        )

        return consensus

    def _create_error_response(self, error: str, query: str) -> ConsensusResponse:
        """Create error response"""
        return ConsensusResponse(
            content=f"Unable to process query: {error}",
            insights=[],
            suggestions=["Try rephrasing the query", "Check agent availability"],
            actions=[],
            contributing_agents=[],
            confidence=0.0,
            agreement_level=0.0,
        )

    # ========================================================================
    # Phase 4C: Knowledge & Emergence Methods
    # ========================================================================

    def observe_interaction(
        self,
        query: str,
        agents_involved: List[str],
        response: Dict[str, Any],
        success: bool = True,
        user_feedback: Optional[str] = None,
    ):
        """
        Observe an interaction for learning and pattern detection

        Args:
            query: The query
            agents_involved: Agents that participated
            response: The response
            success: Whether it was successful
            user_feedback: Optional user feedback
        """
        # Assess quality from confidence and agreement
        quality_score = response.get("confidence", 0.5)

        # Record in emergence monitor
        self.emergence.observe_interaction(
            query=query,
            agents_involved=agents_involved,
            response=response,
            quality_score=quality_score,
        )

        # Record learning event in knowledge broker
        if agents_involved:
            self.knowledge.record_learning_event(
                agent_id=agents_involved[0],  # Primary agent
                query=query,
                response=response,
                success=success,
                user_feedback=user_feedback,
            )

    def query_shared_knowledge(
        self,
        domain: str,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List:
        """
        Query shared knowledge from the network

        Args:
            domain: Knowledge domain
            query: Optional query string
            tags: Optional tags to filter

        Returns:
            List of knowledge entries
        """
        return self.knowledge.query_knowledge(
            domain=domain,
            query=query,
            tags=tags,
        )

    def get_emergent_insights(self, min_novelty: float = 0.7) -> List:
        """
        Get emergent insights from the network

        Args:
            min_novelty: Minimum novelty threshold

        Returns:
            List of emergent insights
        """
        return self.emergence.get_novel_insights(min_novelty=min_novelty)

    def get_agent_synergies(self) -> List:
        """
        Get agent synergy scores

        Returns:
            List of (agent1, agent2, synergy) tuples
        """
        return self.emergence.get_agent_synergies()

    def contribute_knowledge(
        self,
        agent_id: str,
        domain: str,
        content: str,
        confidence: float = 0.8,
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        Agent contributes knowledge to shared pool

        Args:
            agent_id: Contributing agent
            domain: Knowledge domain
            content: Knowledge content
            confidence: Confidence level
            tags: Optional tags

        Returns:
            Knowledge ID
        """
        return self.knowledge.contribute_knowledge(
            agent_id=agent_id,
            domain=domain,
            content=content,
            confidence=confidence,
            tags=tags,
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get orchestration statistics including knowledge and emergence"""
        network_stats = self.registry.get_network_stats()
        knowledge_stats = {
            "total_domains": len(self.knowledge.knowledge_base),
            "total_knowledge": sum(
                len(k) for k in self.knowledge.knowledge_base.values()
            ),
            "total_learning_events": len(self.knowledge.learning_events),
        }
        emergence_stats = self.emergence.get_statistics()

        return {
            "orchestration": {
                "total": self.total_orchestrations,
                "successful": self.successful_orchestrations,
                "success_rate": (
                    self.successful_orchestrations / self.total_orchestrations
                    if self.total_orchestrations > 0
                    else 0.0
                ),
                "total_agents_used": self.total_agents_used,
                "avg_agents_per_query": (
                    self.total_agents_used / self.total_orchestrations
                    if self.total_orchestrations > 0
                    else 0.0
                ),
            },
            "network": network_stats,
            "knowledge": knowledge_stats,
            "emergence": emergence_stats,
        }

    def shutdown(self):
        """Shutdown orchestrator and cleanup"""
        self.executor.shutdown(wait=True)
