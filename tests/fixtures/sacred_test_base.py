"""Sacred test base classes for consciousness-first testing."""

import unittest
from typing import Any, Dict, Optional
from unittest.mock import MagicMock


class ConsciousnessTestBackend:
    """Test backend that simulates consciousness-first responses."""
    
    def __init__(self):
        self.responses = []
        self.learning_enabled = False
        self.persona = "default"
    
    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a query with consciousness-first approach."""
        return {
            "success": True,
            "response": f"Processed: {query}",
            "consciousness_level": 0.8,
            "context": context or {}
        }
    
    def enable_learning(self):
        """Enable learning mode."""
        self.learning_enabled = True
    
    def set_persona(self, persona: str):
        """Set the active persona."""
        self.persona = persona


class SacredTestBase(unittest.TestCase):
    """Base class for sacred consciousness-first tests."""
    
    def setUp(self):
        """Set up test environment with consciousness awareness."""
        super().setUp()
        self.backend = ConsciousnessTestBackend()
        self.consciousness_level = 0.5
        self.test_persona = "test_user"
    
    def assert_consciousness_preserved(self, response):
        """Assert that consciousness is preserved in response."""
        self.assertIn("consciousness_level", response)
        self.assertGreater(response["consciousness_level"], 0)
    
    def assert_learning_occurred(self, before_state, after_state):
        """Assert that learning has occurred between states."""
        self.assertNotEqual(before_state, after_state)
    
    def with_persona(self, persona: str):
        """Context manager for testing with specific persona."""
        old_persona = self.test_persona
        self.test_persona = persona
        self.backend.set_persona(persona)
        try:
            return self
        finally:
            self.test_persona = old_persona
            self.backend.set_persona(old_persona)
