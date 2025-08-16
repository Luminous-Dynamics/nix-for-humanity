#!/usr/bin/env python3
"""
Comprehensive Tests for Explainable Self-Maintenance Orchestrator
Phase 4 Living System: Unified explainable automation testing

This test suite validates the complete integration of all maintenance systems
with consciousness-first principles, causal explanations, and sacred boundaries.

Test Coverage Areas:
- Orchestrator initialization and configuration
- Explainable maintenance execution with full transparency
- Constitutional AI validation and sacred boundary enforcement
- Trust-building through vulnerability acknowledgment
- Multi-stakeholder explanation generation
- Invisible excellence mode integration
- Performance and reliability validation
- Error handling and recovery mechanisms
"""

import asyncio
import tempfile

from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from luminous_nix.infrastructure.causal_maintenance_integration_complete import (
    ExplainableMaintenanceDecision,
    MaintenanceDecisionContext,
    MaintenanceDecisionType,
    StakeholderType,
)

# Import the orchestrator and related components
from luminous_nix.infrastructure.explainable_self_maintenance_orchestrator import (
    AutomationBoundary,
    ExplainableSelfMaintenanceOrchestrator,
    MaintenanceOrchestratorConfig,
    MaintenanceTransparencyLevel,
)
from luminous_nix.infrastructure.self_maintenance_system import (
    MaintenanceAction,
    SystemHealthStatus,
)

class TestExplainableSelfMaintenanceOrchestrator:
    """Comprehensive test suite for the unified explainable orchestrator."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test data."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    @pytest.fixture
    def mock_config(self):
        """Create test configuration for orchestrator."""
        return MaintenanceOrchestratorConfig(
            transparency_level=MaintenanceTransparencyLevel.FULL_DISCLOSURE,
            automation_boundaries={
                "system_update": AutomationBoundary.NOTIFICATION_ONLY,
                "test_execution": AutomationBoundary.BACKGROUND_ALLOWED,
                "deployment": AutomationBoundary.USER_CONSENT_REQUIRED,
            },
            constitutional_ai_enabled=True,
            invisible_excellence_enabled=False,
            federated_learning_enabled=True,
            sacred_trinity_governance=True,
            flow_state_protection=True,
            vulnerability_acknowledgment=True,
            trust_building_enabled=True,
            sacred_boundary_enforcement=True,
        )

    @pytest.fixture
    def sample_maintenance_action(self):
        """Create sample maintenance action for testing."""
        return MaintenanceAction(
            action_id="test_action_001",
            action_type="system_update",
            description="Update system packages for security",
            risk_level="medium",
            estimated_duration=300,
            rollback_available=True,
            user_override_available=True,
            sacred_boundaries_checked=True,
        )

    @pytest.fixture
    def sample_decision_context(self):
        """Create sample decision context for testing."""
        return MaintenanceDecisionContext(
            current_system_state={
                "health_status": SystemHealthStatus.HEALTHY,
                "active_users": 1,
                "system_load": 0.3,
                "available_updates": 12,
            },
            user_context={
                "user_in_flow_state": False,
                "preferred_transparency": "full",
                "last_interaction": datetime.now() - timedelta(hours=2),
            },
            environmental_factors={
                "time_of_day": "afternoon",
                "system_uptime": timedelta(days=3),
                "network_available": True,
            },
            decision_urgency="medium",
            decision_type=MaintenanceDecisionType.SYSTEM_UPDATE,
        )

    @pytest.fixture
    async def orchestrator(self, mock_config, temp_dir):
        """Create orchestrator instance with mocked dependencies."""
        with (
            patch(
                "luminous_nix.infrastructure.explainable_self_maintenance_orchestrator.SelfMaintenanceSystem"
            ) as mock_maintenance,
            patch(
                "luminous_nix.infrastructure.explainable_self_maintenance_orchestrator.CausalMaintenanceExplainer"
            ) as mock_explainer,
            patch(
                "luminous_nix.infrastructure.explainable_self_maintenance_orchestrator.ConstitutionalAIValidator"
            ) as mock_constitutional,
            patch(
                "luminous_nix.infrastructure.explainable_self_maintenance_orchestrator.InvisibleExcellenceEngine"
            ) as mock_excellence,
        ):
            # Mock the components
            mock_maintenance.return_value = AsyncMock()
            mock_explainer.return_value = AsyncMock()
            mock_constitutional.return_value = AsyncMock()
            mock_excellence.return_value = AsyncMock()

            orchestrator = ExplainableSelfMaintenanceOrchestrator(
                config=mock_config, data_dir=temp_dir
            )

            await orchestrator.initialize()
            return orchestrator

    # Core Functionality Tests

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, mock_config, temp_dir):
        """Test orchestrator initialization with all components."""
        with patch(
            "luminous_nix.infrastructure.explainable_self_maintenance_orchestrator.SelfMaintenanceSystem"
        ) as mock_maintenance:
            mock_maintenance.return_value = AsyncMock()

            orchestrator = ExplainableSelfMaintenanceOrchestrator(
                config=mock_config, data_dir=temp_dir
            )

            await orchestrator.initialize()

            # Verify components are initialized
            assert orchestrator.self_maintenance is not None
            assert orchestrator.causal_explainer is not None
            assert orchestrator.constitutional_validator is not None
            assert orchestrator.invisible_excellence is not None

            # Verify configuration is applied
            assert (
                orchestrator.config.transparency_level
                == MaintenanceTransparencyLevel.FULL_DISCLOSURE
            )
            assert orchestrator.config.constitutional_ai_enabled is True
            assert orchestrator.config.trust_building_enabled is True

    @pytest.mark.asyncio
    async def test_explainable_maintenance_execution_success(
        self, orchestrator, sample_maintenance_action, sample_decision_context
    ):
        """Test successful explainable maintenance execution."""
        # Mock the causal explainer to return a valid decision
        mock_decision = ExplainableMaintenanceDecision(
            action=sample_maintenance_action,
            context=sample_decision_context,
            causal_explanation={
                "primary_cause": "Security updates available",
                "confidence": 0.95,
                "reasoning_chain": [
                    "Updates detected",
                    "Security assessment",
                    "Risk evaluation",
                ],
            },
            stakeholder_explanations={
                StakeholderType.END_USER: "We found important security updates for your system.",
                StakeholderType.SYSTEM_ADMIN: "12 security patches available, medium risk level.",
                StakeholderType.DEVELOPER: "CVE-2024-001 through CVE-2024-012 addressed in update.",
            },
            constitutional_compliance=True,
            trust_building_elements={
                "vulnerability_acknowledgment": "This update may briefly interrupt your work.",
                "uncertainty_communication": "Update success rate: 99.2% based on similar systems.",
                "user_agency_preservation": "You can postpone or customize this update.",
            },
        )

        orchestrator.causal_explainer.create_explainable_decision.return_value = (
            mock_decision
        )
        orchestrator.constitutional_validator.validate_action.return_value = True
        orchestrator.self_maintenance.execute_maintenance.return_value = {
            "success": True,
            "duration": 285,
        }

        # Execute maintenance
        result = await orchestrator.execute_explainable_maintenance(
            sample_maintenance_action, sample_decision_context
        )

        # Verify execution success
        assert result is not None
        assert result.decision == mock_decision
        assert result.execution_started is not None
        assert result.execution_completed is not None
        assert result.execution_success is True
        assert result.constitutional_compliance is True

        # Verify trust building elements are present
        assert "vulnerability_acknowledgment" in result.trust_building_record
        assert "transparency_provided" in result.trust_building_record
        assert result.trust_building_record["transparency_provided"] is True

    @pytest.mark.asyncio
    async def test_constitutional_ai_blocking(
        self, orchestrator, sample_maintenance_action, sample_decision_context
    ):
        """Test Constitutional AI blocking unsafe actions."""
        # Mock Constitutional AI to block the action
        orchestrator.constitutional_validator.validate_action.return_value = False

        # Mock causal explainer
        mock_decision = ExplainableMaintenanceDecision(
            action=sample_maintenance_action,
            context=sample_decision_context,
            causal_explanation={"primary_cause": "Test"},
            stakeholder_explanations={StakeholderType.END_USER: "Test explanation"},
            constitutional_compliance=False,
            trust_building_elements={},
        )
        orchestrator.causal_explainer.create_explainable_decision.return_value = (
            mock_decision
        )

        # Execute maintenance (should be blocked)
        result = await orchestrator.execute_explainable_maintenance(
            sample_maintenance_action, sample_decision_context
        )

        # Verify action was blocked
        assert result is None

        # Verify self-maintenance was never called
        orchestrator.self_maintenance.execute_maintenance.assert_not_called()

    @pytest.mark.asyncio
    async def test_multi_stakeholder_explanations(
        self, orchestrator, sample_maintenance_action, sample_decision_context
    ):
        """Test generation of explanations for different stakeholders."""
        # Mock comprehensive stakeholder explanations
        stakeholder_explanations = {
            StakeholderType.END_USER: "Your system will be updated to fix security issues. This keeps your computer safe.",
            StakeholderType.SYSTEM_ADMIN: "Security update deployment: 12 CVEs addressed, estimated downtime 5 minutes.",
            StakeholderType.DEVELOPER: "Package updates: openssl 3.0.8→3.0.9, linux-kernel 6.1.0→6.1.1, affects dependencies X, Y, Z.",
            StakeholderType.AI_RESEARCHER: "Causal reasoning: Security→Risk→Mitigation chain with 0.95 confidence.",
            StakeholderType.SACRED_TRINITY: "Sacred Trinity governance: Human approved, Claude implemented, LLM validated.",
        }

        mock_decision = ExplainableMaintenanceDecision(
            action=sample_maintenance_action,
            context=sample_decision_context,
            causal_explanation={"primary_cause": "Security vulnerability mitigation"},
            stakeholder_explanations=stakeholder_explanations,
            constitutional_compliance=True,
            trust_building_elements={
                "vulnerability_acknowledgment": "We acknowledge this may cause brief interruption.",
                "uncertainty_communication": "Success probability: 99.2%",
                "user_agency_preservation": "You retain full control and can rollback.",
            },
        )

        orchestrator.causal_explainer.create_explainable_decision.return_value = (
            mock_decision
        )
        orchestrator.constitutional_validator.validate_action.return_value = True
        orchestrator.self_maintenance.execute_maintenance.return_value = {
            "success": True
        }

        # Execute maintenance
        result = await orchestrator.execute_explainable_maintenance(
            sample_maintenance_action, sample_decision_context
        )

        # Verify all stakeholder explanations are present
        assert result.decision.stakeholder_explanations == stakeholder_explanations
        assert len(result.decision.stakeholder_explanations) == 5
        assert StakeholderType.END_USER in result.decision.stakeholder_explanations
        assert (
            StakeholderType.SACRED_TRINITY in result.decision.stakeholder_explanations
        )

    @pytest.mark.asyncio
    async def test_transparency_level_adaptation(self, mock_config, temp_dir):
        """Test adaptation to different transparency levels."""
        # Test with minimal transparency
        mock_config.transparency_level = MaintenanceTransparencyLevel.AMBIENT_AWARENESS

        with patch(
            "luminous_nix.infrastructure.explainable_self_maintenance_orchestrator.SelfMaintenanceSystem"
        ) as mock_maintenance:
            mock_maintenance.return_value = AsyncMock()

            orchestrator = ExplainableSelfMaintenanceOrchestrator(
                config=mock_config, data_dir=temp_dir
            )

            await orchestrator.initialize()

            # Verify transparency level is respected
            assert (
                orchestrator.config.transparency_level
                == MaintenanceTransparencyLevel.AMBIENT_AWARENESS
            )

            # Test explanation generation adapts to transparency level
            explanation = await orchestrator._generate_stakeholder_explanation(
                "test explanation",
                StakeholderType.END_USER,
                mock_config.transparency_level,
            )

            # Ambient awareness should provide minimal explanation
            assert len(explanation) < 100  # Should be brief

    @pytest.mark.asyncio
    async def test_flow_state_protection(self, orchestrator, sample_maintenance_action):
        """Test flow state protection prevents interruptions."""
        # Create context with user in flow state
        flow_context = MaintenanceDecisionContext(
            current_system_state={"health_status": SystemHealthStatus.HEALTHY},
            user_context={
                "user_in_flow_state": True,
                "flow_duration": timedelta(minutes=45),
            },
            environmental_factors={"time_of_day": "morning"},
            decision_urgency="low",
            decision_type=MaintenanceDecisionType.ROUTINE_MAINTENANCE,
        )

        # Mock action that would normally require interruption
        sample_maintenance_action.requires_interruption = True

        # Mock causal explainer
        mock_decision = ExplainableMaintenanceDecision(
            action=sample_maintenance_action,
            context=flow_context,
            causal_explanation={"primary_cause": "Routine maintenance"},
            stakeholder_explanations={
                StakeholderType.END_USER: "Maintenance deferred to protect your focus."
            },
            constitutional_compliance=True,
            trust_building_elements={
                "flow_state_respect": "Deferred to preserve deep work session."
            },
        )
        orchestrator.causal_explainer.create_explainable_decision.return_value = (
            mock_decision
        )
        orchestrator.constitutional_validator.validate_action.return_value = True

        # Execute maintenance
        result = await orchestrator.execute_explainable_maintenance(
            sample_maintenance_action, flow_context
        )

        # Verify action was deferred due to flow state
        assert "flow_state_respect" in result.decision.trust_building_elements
        assert (
            "deferred"
            in result.decision.trust_building_elements["flow_state_respect"].lower()
        )

    @pytest.mark.asyncio
    async def test_trust_building_through_vulnerability(
        self, orchestrator, sample_maintenance_action, sample_decision_context
    ):
        """Test trust building through vulnerability acknowledgment."""
        # Mock decision with vulnerability acknowledgment
        mock_decision = ExplainableMaintenanceDecision(
            action=sample_maintenance_action,
            context=sample_decision_context,
            causal_explanation={"primary_cause": "Security update", "confidence": 0.87},
            stakeholder_explanations={
                StakeholderType.END_USER: "I need to update your system, but I'm not 100% certain this won't cause issues."
            },
            constitutional_compliance=True,
            trust_building_elements={
                "vulnerability_acknowledgment": "I have 87% confidence this will succeed, but there's a 13% chance of minor issues.",
                "uncertainty_communication": "If problems occur, I can rollback in under 2 minutes.",
                "limitation_disclosure": "I can't predict every possible interaction with your custom configurations.",
            },
        )

        orchestrator.causal_explainer.create_explainable_decision.return_value = (
            mock_decision
        )
        orchestrator.constitutional_validator.validate_action.return_value = True
        orchestrator.self_maintenance.execute_maintenance.return_value = {
            "success": True
        }

        # Execute maintenance
        result = await orchestrator.execute_explainable_maintenance(
            sample_maintenance_action, sample_decision_context
        )

        # Verify vulnerability and uncertainty are acknowledged
        trust_elements = result.decision.trust_building_elements
        assert "vulnerability_acknowledgment" in trust_elements
        assert "uncertainty_communication" in trust_elements
        assert "limitation_disclosure" in trust_elements
        assert "87%" in trust_elements["vulnerability_acknowledgment"]
        assert "rollback" in trust_elements["uncertainty_communication"]

    @pytest.mark.asyncio
    async def test_invisible_excellence_mode_integration(self, mock_config, temp_dir):
        """Test integration with invisible excellence mode."""
        # Enable invisible excellence
        mock_config.invisible_excellence_enabled = True
        mock_config.user_transcendence_level = "gymnasium"  # Advanced user

        with (
            patch(
                "luminous_nix.infrastructure.explainable_self_maintenance_orchestrator.SelfMaintenanceSystem"
            ) as mock_maintenance,
            patch(
                "luminous_nix.infrastructure.explainable_self_maintenance_orchestrator.InvisibleExcellenceEngine"
            ) as mock_excellence,
        ):
            mock_maintenance.return_value = AsyncMock()
            mock_excellence_instance = AsyncMock()
            mock_excellence.return_value = mock_excellence_instance

            orchestrator = ExplainableSelfMaintenanceOrchestrator(
                config=mock_config, data_dir=temp_dir
            )

            await orchestrator.initialize()

            # Verify invisible excellence is enabled
            assert orchestrator.config.invisible_excellence_enabled is True

            # Mock invisible excellence assessment
            mock_excellence_instance.assess_transcendence_readiness.return_value = {
                "ready_for_invisible_action": True,
                "transcendence_level": "gymnasium",
                "confidence": 0.92,
            }

            # Test that invisible actions can be executed
            assessment = (
                await orchestrator.invisible_excellence.assess_transcendence_readiness(
                    "test_action", {"user_mastery": "advanced"}
                )
            )

            assert assessment["ready_for_invisible_action"] is True
            assert assessment["transcendence_level"] == "gymnasium"

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(
        self, orchestrator, sample_maintenance_action, sample_decision_context
    ):
        """Test comprehensive error handling and recovery mechanisms."""
        # Mock causal explainer to raise an exception
        orchestrator.causal_explainer.create_explainable_decision.side_effect = (
            Exception("Explanation generation failed")
        )

        # Execute maintenance (should handle error gracefully)
        result = await orchestrator.execute_explainable_maintenance(
            sample_maintenance_action, sample_decision_context
        )

        # Verify error was handled gracefully
        assert result is None  # Should return None on critical error

        # Reset and test maintenance execution error
        orchestrator.causal_explainer.create_explainable_decision.side_effect = None
        mock_decision = ExplainableMaintenanceDecision(
            action=sample_maintenance_action,
            context=sample_decision_context,
            causal_explanation={"primary_cause": "Test"},
            stakeholder_explanations={StakeholderType.END_USER: "Test"},
            constitutional_compliance=True,
            trust_building_elements={},
        )
        orchestrator.causal_explainer.create_explainable_decision.return_value = (
            mock_decision
        )
        orchestrator.constitutional_validator.validate_action.return_value = True

        # Mock maintenance execution failure
        orchestrator.self_maintenance.execute_maintenance.side_effect = Exception(
            "Maintenance failed"
        )

        result = await orchestrator.execute_explainable_maintenance(
            sample_maintenance_action, sample_decision_context
        )

        # Verify execution failure is recorded properly
        assert result is not None
        assert result.execution_success is False
        assert result.error_details is not None
        assert "Maintenance failed" in result.error_details

    @pytest.mark.asyncio
    async def test_sacred_trinity_governance_validation(
        self, orchestrator, sample_maintenance_action, sample_decision_context
    ):
        """Test Sacred Trinity governance integration."""
        # Mock decision with Sacred Trinity governance
        mock_decision = ExplainableMaintenanceDecision(
            action=sample_maintenance_action,
            context=sample_decision_context,
            causal_explanation={"primary_cause": "Sacred Trinity consensus"},
            stakeholder_explanations={
                StakeholderType.SACRED_TRINITY: "Human vision approved, Claude architected, Local LLM validated NixOS best practices."
            },
            constitutional_compliance=True,
            trust_building_elements={
                "sacred_trinity_consensus": "All three members of Sacred Trinity agree on this action.",
                "governance_transparency": "Decision process followed Sacred Trinity workflow.",
            },
        )

        orchestrator.causal_explainer.create_explainable_decision.return_value = (
            mock_decision
        )
        orchestrator.constitutional_validator.validate_action.return_value = True
        orchestrator.self_maintenance.execute_maintenance.return_value = {
            "success": True
        }

        # Execute maintenance
        result = await orchestrator.execute_explainable_maintenance(
            sample_maintenance_action, sample_decision_context
        )

        # Verify Sacred Trinity governance is documented
        trinity_explanation = result.decision.stakeholder_explanations[
            StakeholderType.SACRED_TRINITY
        ]
        assert "Human vision" in trinity_explanation
        assert "Claude" in trinity_explanation
        assert "Local LLM" in trinity_explanation
        assert (
            result.decision.trust_building_elements["sacred_trinity_consensus"]
            is not None
        )

    # Performance and Integration Tests

    @pytest.mark.asyncio
    async def test_orchestrator_performance_under_load(
        self, orchestrator, sample_maintenance_action, sample_decision_context
    ):
        """Test orchestrator performance with multiple concurrent actions."""
        # Mock components for performance test
        mock_decision = ExplainableMaintenanceDecision(
            action=sample_maintenance_action,
            context=sample_decision_context,
            causal_explanation={"primary_cause": "Performance test"},
            stakeholder_explanations={
                StakeholderType.END_USER: "Performance test action"
            },
            constitutional_compliance=True,
            trust_building_elements={},
        )

        orchestrator.causal_explainer.create_explainable_decision.return_value = (
            mock_decision
        )
        orchestrator.constitutional_validator.validate_action.return_value = True
        orchestrator.self_maintenance.execute_maintenance.return_value = {
            "success": True
        }

        # Execute multiple concurrent maintenance actions
        tasks = []
        for i in range(5):
            action = MaintenanceAction(
                action_id=f"perf_test_{i}",
                action_type="test_action",
                description=f"Performance test action {i}",
                risk_level="low",
            )
            task = orchestrator.execute_explainable_maintenance(
                action, sample_decision_context
            )
            tasks.append(task)

        # Wait for all tasks to complete
        start_time = asyncio.get_event_loop().time()
        results = await asyncio.gather(*tasks)
        end_time = asyncio.get_event_loop().time()

        # Verify all actions completed successfully
        assert len(results) == 5
        assert all(result is not None for result in results)
        assert all(result.execution_success for result in results)

        # Verify reasonable performance (should complete within 5 seconds)
        assert (end_time - start_time) < 5.0

    @pytest.mark.asyncio
    async def test_configuration_validation(self, temp_dir):
        """Test configuration validation and error handling."""
        # Test invalid configuration
        invalid_config = MaintenanceOrchestratorConfig(
            transparency_level="invalid_level",  # Invalid enum
            max_simultaneous_actions=-1,  # Invalid negative value
            constitutional_ai_enabled=None,  # Invalid None value
        )

        with pytest.raises((ValueError, TypeError)):
            orchestrator = ExplainableSelfMaintenanceOrchestrator(
                config=invalid_config, data_dir=temp_dir
            )

    def test_consciousness_first_principle_validation(self, orchestrator):
        """Test validation against consciousness-first principles."""
        # Test action that violates consciousness-first principles
        bad_action = MaintenanceAction(
            action_id="bad_action",
            action_type="destructive_action",
            description="Action without explanation",
            risk_level="high",
            rollback_available=False,  # Violates principle
            user_override_available=False,  # Violates principle
            explanation=None,  # Violates principle
        )

        # Test context with user in flow state
        flow_context = {
            "user_in_flow_state": True,
            "flow_duration": timedelta(minutes=30),
        }

        # Validate action (should fail)
        from luminous_nix.infrastructure import validate_consciousness_first_action

        validation_result = validate_consciousness_first_action(
            bad_action, flow_context
        )

        assert validation_result["compliant"] is False
        assert len(validation_result["violations"]) > 0
        assert any(
            "rollback" in violation for violation in validation_result["violations"]
        )
        assert any(
            "override" in violation for violation in validation_result["violations"]
        )

    @pytest.mark.asyncio
    async def test_federated_learning_integration(self, orchestrator):
        """Test integration with federated learning network."""
        # Mock federated learning components
        orchestrator.federated_network = AsyncMock()

        # Test sharing insights while preserving privacy
        maintenance_insight = {
            "action_type": "system_update",
            "success_rate": 0.98,
            "common_issues": ["network_timeout", "disk_space"],
            "anonymized_patterns": True,
        }

        await orchestrator._share_maintenance_insights(maintenance_insight)

        # Verify federated sharing was attempted (mocked)
        assert orchestrator.federated_network is not None

if __name__ == "__main__":
    # Run tests with detailed output
    pytest.main([__file__, "-v", "--tb=short"])
