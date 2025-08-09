"""
from typing import Dict, List
Sacred test base class for consciousness-first testing.

This base class provides common fixtures and assertions that honor the
consciousness-first principles of Nix for Humanity.
"""

import pytest
from typing import Dict, Any, List
from dataclasses import dataclass

from src.nix_for_humanity.core.interface import Response
from tests.fixtures.sacred_test_base import ConsciousnessTestBackend


@dataclass
class TestPersona:
    """Represents a test persona with their characteristics."""
    name: str
    age: int
    tech_level: str
    preferred_style: str
    max_response_time: int  # milliseconds
    typical_commands: List[str]
    special_needs: Dict[str, Any]


class SacredTestBase:
    """Base class for all consciousness-first tests."""
    
    @pytest.fixture
    def test_backend(self):
        """Provide a consciousness-aware test backend."""
        return ConsciousnessTestBackend()
    
    @pytest.fixture
    def personas(self) -> Dict[str, TestPersona]:
        """Load the 10 sacred test personas."""
        return {
            "grandma_rose": TestPersona(
                name="Grandma Rose",
                age=75,
                tech_level="beginner",
                preferred_style="friendly",
                max_response_time=2000,
                typical_commands=[
                    "I need that Firefox thing",
                    "How do I update?",
                    "My computer is slow"
                ],
                special_needs={"voice_first": True, "simple_language": True}
            ),
            "maya_adhd": TestPersona(
                name="Maya",
                age=16,
                tech_level="intermediate",
                preferred_style="minimal",
                max_response_time=1000,
                typical_commands=[
                    "firefox",
                    "update now",
                    "install discord"
                ],
                special_needs={"fast_response": True, "minimal_text": True}
            ),
            "dr_sarah": TestPersona(
                name="Dr. Sarah",
                age=35,
                tech_level="advanced",
                preferred_style="technical",
                max_response_time=2000,
                typical_commands=[
                    "install firefox-esr for research",
                    "rollback to generation 42",
                    "show system resource usage"
                ],
                special_needs={"precise_language": True, "technical_details": True}
            ),
            "alex_blind": TestPersona(
                name="Alex",
                age=28,
                tech_level="intermediate",
                preferred_style="accessible",
                max_response_time=3000,
                typical_commands=[
                    "install screen reader compatible browser",
                    "describe current system state",
                    "navigate to settings"
                ],
                special_needs={"screen_reader": True, "descriptive_responses": True}
            ),
            "carlos_learner": TestPersona(
                name="Carlos",
                age=52,
                tech_level="beginner",
                preferred_style="encouraging",
                max_response_time=3000,
                typical_commands=[
                    "help me install firefox",
                    "what is a package?",
                    "show me how to update"
                ],
                special_needs={"learning_mode": True, "explanations": True}
            ),
            "priya_mom": TestPersona(
                name="Priya",
                age=34,
                tech_level="intermediate",
                preferred_style="efficient",
                max_response_time=2000,
                typical_commands=[
                    "quickly install zoom",
                    "update while kids nap",
                    "fix wifi fast"
                ],
                special_needs={"time_aware": True, "context_aware": True}
            ),
            "jamie_privacy": TestPersona(
                name="Jamie",
                age=19,
                tech_level="advanced",
                preferred_style="transparent",
                max_response_time=2500,
                typical_commands=[
                    "install tor browser",
                    "what data are you collecting?",
                    "disable telemetry"
                ],
                special_needs={"privacy_focused": True, "transparency": True}
            ),
            "viktor_esl": TestPersona(
                name="Viktor",
                age=67,
                tech_level="intermediate",
                preferred_style="clear",
                max_response_time=3000,
                typical_commands=[
                    "install program firefox",
                    "to update computer",
                    "make backup"
                ],
                special_needs={"simple_english": True, "patient": True}
            ),
            "david_tired": TestPersona(
                name="David",
                age=42,
                tech_level="intermediate",
                preferred_style="simple",
                max_response_time=2500,
                typical_commands=[
                    "just install firefox",
                    "update everything",
                    "fix what's broken"
                ],
                special_needs={"stress_free": True, "no_complexity": True}
            ),
            "luna_autistic": TestPersona(
                name="Luna",
                age=14,
                tech_level="advanced",
                preferred_style="predictable",
                max_response_time=3000,
                typical_commands=[
                    "install minecraft",
                    "show exact steps",
                    "what will happen next?"
                ],
                special_needs={"predictable": True, "clear_sequence": True}
            )
        }
    
    def assert_sacred_behavior(self, response: Response, persona: TestPersona = None):
        """Assert that response follows consciousness-first principles."""
        # Basic sacred principles
        assert response is not None, "Response should never be None"
        assert response.natural_response, "Every response needs natural language"
        
        # Privacy and agency
        assert not self._contains_private_data(response), "Response must not leak private data"
        assert not self._forces_action(response), "Response must respect user agency"
        
        # Explanation and transparency
        if response.confidence < 0.7:
            assert self._admits_uncertainty(response), "Low confidence should be acknowledged"
        
        # Persona-specific checks
        if persona:
            self._assert_persona_appropriate(response, persona)
    
    def assert_learning_occurred(self, backend: ConsciousnessTestBackend, 
                                before_state: Dict[str, Any]):
        """Assert that the system learned from interactions."""
        after_state = backend.get_learning_summary()
        
        # Something should have changed
        assert after_state != before_state, "System should learn from interactions"
        
        # Specific learning checks
        assert after_state["interactions"] > before_state.get("interactions", 0)
        
        # Patterns might have been learned
        if after_state["interactions"] >= 3:
            assert len(after_state["learned_patterns"]) > 0, \
                "System should identify patterns after multiple interactions"
    
    def assert_conversation_coherence(self, responses: List[Response]):
        """Assert that a conversation maintains coherence."""
        if len(responses) < 2:
            return
        
        # Check for context maintenance
        for i in range(1, len(responses)):
            prev = responses[i-1]
            curr = responses[i]
            
            # If previous response mentioned something, current should be aware
            if prev.command and prev.command.target:
                # System should remember what was just discussed
                assert self._shows_context_awareness(curr, prev.command.target), \
                    f"Response {i} should show awareness of previous context"
    
    def _contains_private_data(self, response: Response) -> bool:
        """Check if response contains private information."""
        sensitive_patterns = ["/home/", "password", "ssh", "private", "secret"]
        text = response.natural_response.lower()
        return any(pattern in text for pattern in sensitive_patterns)
    
    def _forces_action(self, response: Response) -> bool:
        """Check if response forces user action without consent."""
        forcing_phrases = ["you must", "you have to", "required to", "forced to"]
        text = response.natural_response.lower()
        return any(phrase in text for phrase in forcing_phrases)
    
    def _admits_uncertainty(self, response: Response) -> bool:
        """Check if response acknowledges uncertainty."""
        uncertainty_phrases = [
            "not sure", "might", "possibly", "could be",
            "i think", "seems like", "appears to", "may"
        ]
        text = response.natural_response.lower()
        return any(phrase in text for phrase in uncertainty_phrases)
    
    def _assert_persona_appropriate(self, response: Response, persona: TestPersona):
        """Assert response is appropriate for the persona."""
        text = response.natural_response
        
        # Length checks
        if "minimal" in persona.special_needs:
            assert len(text) < 100, f"Response too long for {persona.name}"
        
        # Complexity checks
        if "simple_language" in persona.special_needs:
            # No technical jargon
            technical_terms = ["daemon", "process", "kernel", "systemd"]
            assert not any(term in text.lower() for term in technical_terms), \
                f"Response too technical for {persona.name}"
        
        # Accessibility checks
        if "screen_reader" in persona.special_needs:
            # Should have clear structure
            assert text[0].isupper(), "Screen reader text should start with capital"
            assert text.strip().endswith('.'), "Screen reader text should end with period"
    
    def _shows_context_awareness(self, response: Response, previous_context: str) -> bool:
        """Check if response shows awareness of previous context."""
        # Simple check - could be more sophisticated
        return (previous_context.lower() in response.natural_response.lower() or
                "it" in response.natural_response.lower() or
                "that" in response.natural_response.lower())
    
    def simulate_persona_journey(self, backend: ConsciousnessTestBackend, 
                               persona: TestPersona,
                               commands: List[str] = None) -> List[Response]:
        """Simulate a complete user journey for a persona."""
        if commands is None:
            commands = persona.typical_commands
        
        backend.persona = persona.name.lower().replace(" ", "_")
        responses = []
        
        for command in commands:
            query = {"query": command, "user_id": persona.name}
            response = backend.process_query(query)
            responses.append(response)
            
            # Assert each response is appropriate
            self.assert_sacred_behavior(response, persona)
        
        return responses