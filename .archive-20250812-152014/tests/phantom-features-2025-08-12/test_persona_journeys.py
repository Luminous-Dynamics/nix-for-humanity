#!/usr/bin/env python3
"""
End-to-End tests for persona-based user journeys.
Tests complete workflows for each of our 10 core personas.
"""

import os
import sys
import tempfile
import time
import unittest
import subprocess

from unittest.mock import Mock, MagicMock, patch, call

# Add src directory to path
src_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src"
)
sys.path.insert(0, src_path)

from luminous_nix.core.engine import NixForHumanityBackend as Engine
from luminous_nix.core.intents import IntentRecognizer as IntentEngine
from luminous_nix.core.personality import PersonalityManager

# Mock non-existent modules
class ExecutionEngine:
    """Mock execution engine"""
    def execute(self, command):
        return {"status": "success"}

class KnowledgeBase:
    """Mock knowledge base"""
    def __init__(self, db_path=None):
        self.db_path = db_path
        
    def query(self, query):
        return []

class PersonaJourney:
    """Base class for persona test journeys."""

    def __init__(self, name, age, characteristics, typical_commands, success_criteria):
        self.name = name
        self.age = age
        self.characteristics = characteristics
        self.typical_commands = typical_commands
        self.success_criteria = success_criteria

# Define our 10 personas
PERSONAS = [
    PersonaJourney(
        name="Grandma Rose",
        age=75,
        characteristics=["voice-first", "zero technical knowledge", "patient"],
        typical_commands=[
            "I need that Firefox thing",
            "How do I see my photos?",
            "Make the text bigger please",
        ],
        success_criteria={
            "response_time": 2.0,  # seconds
            "language_complexity": "simple",
            "technical_terms": 0,
            "success_rate": 0.95,
        },
    ),
    PersonaJourney(
        name="Maya",
        age=16,
        characteristics=["ADHD", "fast-paced", "minimal attention span"],
        typical_commands=["install discord", "update everything", "wifi broken fix it"],
        success_criteria={
            "response_time": 1.0,  # Must be fast
            "language_complexity": "minimal",
            "steps": 3,  # Maximum steps
            "success_rate": 0.90,
        },
    ),
    PersonaJourney(
        name="David",
        age=42,
        characteristics=["tired parent", "stressed", "needs reliability"],
        typical_commands=[
            "install zoom for work",
            "why is computer slow",
            "backup my files",
        ],
        success_criteria={
            "response_time": 3.0,
            "stress_free": True,
            "clear_instructions": True,
            "success_rate": 0.95,
        },
    ),
    PersonaJourney(
        name="Dr. Sarah",
        age=35,
        characteristics=["researcher", "technical", "efficient"],
        typical_commands=[
            "install latex with all scientific packages",
            "configure jupyter with GPU support",
            "optimize compilation flags for numerical computing",
        ],
        success_criteria={
            "response_time": 2.0,
            "technical_accuracy": 1.0,
            "detailed_options": True,
            "success_rate": 0.98,
        },
    ),
    PersonaJourney(
        name="Alex",
        age=28,
        characteristics=["blind developer", "screen reader", "keyboard only"],
        typical_commands=[
            "install neovim with accessibility plugins",
            "configure audio feedback",
            "list all keyboard shortcuts",
        ],
        success_criteria={
            "screen_reader_compatible": True,
            "keyboard_navigable": True,
            "audio_feedback": True,
            "success_rate": 1.0,  # Must be perfect
        },
    ),
    PersonaJourney(
        name="Carlos",
        age=52,
        characteristics=["career switcher", "learning tech", "needs encouragement"],
        typical_commands=[
            "I'm learning programming, what do I need?",
            "help me install development tools",
            "what's the difference between these editors?",
        ],
        success_criteria={
            "response_time": 3.0,
            "educational": True,
            "encouraging_tone": True,
            "success_rate": 0.92,
        },
    ),
    PersonaJourney(
        name="Priya",
        age=34,
        characteristics=["single mom", "time-constrained", "needs efficiency"],
        typical_commands=[
            "quick install of office software",
            "fastest way to update system",
            "fix this fast, kids need computer",
        ],
        success_criteria={
            "response_time": 1.5,  # Must be fast
            "efficiency_focused": True,
            "clear_priorities": True,
            "success_rate": 0.95,
        },
    ),
    PersonaJourney(
        name="Jamie",
        age=19,
        characteristics=["privacy advocate", "security conscious", "tech savvy"],
        typical_commands=[
            "install tor browser securely",
            "what data does this collect?",
            "most private way to do this?",
        ],
        success_criteria={
            "response_time": 2.0,
            "privacy_transparent": True,
            "security_focused": True,
            "success_rate": 0.98,
        },
    ),
    PersonaJourney(
        name="Viktor",
        age=67,
        characteristics=["ESL speaker", "careful with language", "patient"],
        typical_commands=[
            "please install program for documents",
            "I need help with computer updating",
            "can you explain this more simple?",
        ],
        success_criteria={
            "response_time": 4.0,  # Can wait for clarity
            "simple_language": True,
            "clear_instructions": True,
            "success_rate": 0.90,
        },
    ),
    PersonaJourney(
        name="Luna",
        age=14,
        characteristics=["autistic", "needs predictability", "detail-oriented"],
        typical_commands=[
            "install exactly the same version as last time",
            "why did this change?",
            "show me all the steps first",
        ],
        success_criteria={
            "response_time": 3.0,
            "consistency": True,
            "detailed_explanations": True,
            "success_rate": 0.95,
        },
    ),
]

class TestPersonaJourneys(unittest.TestCase):
    """Test complete user journeys for each persona."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary knowledge base
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.knowledge_base = KnowledgeBase(self.temp_db.name)

        # Initialize engine
        self.engine = Engine(
            IntentEngine(), self.knowledge_base, ExecutionEngine(), PersonalityManager()
        )

    def tearDown(self):
        """Clean up."""
        self.temp_db.close()
        os.unlink(self.temp_db.name)

    def test_grandma_rose_journey(self):
        """Test Grandma Rose's typical interaction journey."""
        persona = PERSONAS[0]  # Grandma Rose

        # Set appropriate personality
        self.engine.personality_system.set_personality("friendly")

        for command in persona.typical_commands:
            start_time = time.time()
            response = self.engine.process(command)
            response_time = time.time() - start_time

            # Check response time
            self.assertLess(
                response_time,
                persona.success_criteria["response_time"],
                f"Response too slow for Grandma Rose: {response_time}s",
            )

            # Check language simplicity
            display_text = response.get("display", "")

            # No technical jargon
            technical_terms = ["repository", "binary", "compilation", "dependency"]
            for term in technical_terms:
                self.assertNotIn(
                    term.lower(),
                    display_text.lower(),
                    f"Technical term '{term}' used with Grandma Rose",
                )

            # Should be encouraging and friendly
            self.assertTrue(
                any(
                    word in display_text.lower() for word in ["help", "happy", "great"]
                ),
                "Response not friendly enough for Grandma Rose",
            )

    def test_maya_adhd_journey(self):
        """Test Maya's ADHD-optimized journey."""
        persona = PERSONAS[1]  # Maya

        # Set minimal personality for speed
        self.engine.personality_system.set_personality("minimal")

        for command in persona.typical_commands:
            start_time = time.time()
            response = self.engine.process(command)
            response_time = time.time() - start_time

            # Must be FAST
            self.assertLess(
                response_time,
                persona.success_criteria["response_time"],
                f"Too slow for Maya with ADHD: {response_time}s",
            )

            # Response must be concise
            display_text = response.get("display", "")
            self.assertLess(
                len(display_text),
                200,  # characters
                "Response too long for Maya's attention span",
            )

            # Direct action, no fluff
            self.assertIn("command", response)
            self.assertIsNotNone(response["command"])

    def test_alex_accessibility_journey(self):
        """Test Alex's accessibility requirements."""
        persona = PERSONAS[4]  # Alex

        for command in persona.typical_commands:
            response = self.engine.process(command)

            # Must have screen reader text
            self.assertIn("display", response)
            display_text = response["display"]

            # No ASCII art or visual elements
            self.assertNotIn("═", display_text)
            self.assertNotIn("│", display_text)
            self.assertNotIn("└", display_text)

            # Clear structure with punctuation for pauses
            self.assertTrue(
                "." in display_text or "," in display_text,
                "No punctuation for screen reader pauses",
            )

            # Commands should be clearly separated
            if "command" in response:
                self.assertTrue(
                    "Command:" in display_text
                    or "Run:" in display_text
                    or "Execute:" in display_text,
                    "Command not clearly labeled for screen reader",
                )

    def test_dr_sarah_technical_journey(self):
        """Test Dr. Sarah's technical requirements."""
        persona = PERSONAS[3]  # Dr. Sarah

        # Set technical personality
        self.engine.personality_system.set_personality("technical")

        for command in persona.typical_commands:
            response = self.engine.process(command)

            # Should provide detailed technical information
            self.assertIn("explanation", response)

            # Should offer options
            if "latex" in command:
                display_text = response.get("display", "")
                self.assertTrue(
                    "texlive-full" in display_text or "texlive" in display_text,
                    "Missing technical package details",
                )

            # Should be precise
            if "command" in response:
                self.assertIn("nixos", response["command"].lower())

    @patch("subprocess.run")
    def test_carlos_learning_journey(self):
        """Test Carlos's career-switching learning needs."""
        persona = PERSONAS[5]  # Carlos

        # Set encouraging personality
        self.engine.personality_system.set_personality("encouraging")

        for command in persona.typical_commands:
            response = self.engine.process(command)

            # Should be educational
            self.assertIn("display", response)
            display_text = response["display"]

            # Should explain concepts
            educational_indicators = [
                "learn",
                "understand",
                "explain",
                "because",
                "this helps",
            ]
            self.assertTrue(
                any(
                    indicator in display_text.lower()
                    for indicator in educational_indicators
                ),
                "Response not educational enough for Carlos",
            )

            # Should be encouraging
            encouraging_words = ["great", "good", "well done", "excellent", "perfect"]
            self.assertTrue(
                any(word in display_text.lower() for word in encouraging_words),
                "Response not encouraging enough for Carlos",
            )

    def test_priya_efficiency_journey(self):
        """Test Priya's time-constrained efficiency needs."""
        persona = PERSONAS[6]  # Priya

        for command in persona.typical_commands:
            start_time = time.time()
            response = self.engine.process(command)
            response_time = time.time() - start_time

            # Must be fast
            self.assertLess(
                response_time,
                persona.success_criteria["response_time"],
                f"Too slow for Priya: {response_time}s",
            )

            # Should prioritize speed and efficiency
            display_text = response.get("display", "")
            efficiency_indicators = [
                "quick",
                "fast",
                "immediately",
                "right away",
                "now",
            ]
            self.assertTrue(
                any(
                    indicator in display_text.lower()
                    for indicator in efficiency_indicators
                ),
                "Response doesn't emphasize efficiency for Priya",
            )

    def test_jamie_privacy_journey(self):
        """Test Jamie's privacy-conscious requirements."""
        persona = PERSONAS[7]  # Jamie

        for command in persona.typical_commands:
            response = self.engine.process(command)

            # Should address privacy concerns
            display_text = response.get("display", "")

            if "data" in command or "collect" in command:
                privacy_terms = ["private", "local", "secure", "anonymous", "encrypted"]
                self.assertTrue(
                    any(term in display_text.lower() for term in privacy_terms),
                    "Response doesn't address privacy for Jamie",
                )

            # Should be transparent about operations
            if "command" in response:
                self.assertIn(
                    "explanation",
                    response,
                    "Commands not explained transparently for Jamie",
                )

    def test_viktor_esl_journey(self):
        """Test Viktor's ESL language requirements."""
        persona = PERSONAS[8]  # Viktor

        for command in persona.typical_commands:
            response = self.engine.process(command)

            # Check simple language usage
            display_text = response.get("display", "")

            # No complex technical jargon
            complex_terms = [
                "repository",
                "binary",
                "compilation",
                "instantiation",
                "derivation",
            ]
            for term in complex_terms:
                self.assertNotIn(
                    term.lower(),
                    display_text.lower(),
                    f"Complex term '{term}' used with Viktor (ESL)",
                )

            # Should use simple, clear sentences
            sentences = display_text.split(".")
            for sentence in sentences[:3]:  # Check first 3 sentences
                words = sentence.split()
                if len(words) > 0:
                    self.assertLess(
                        len(words),
                        15,
                        f"Sentence too long for Viktor: '{sentence.strip()}'",
                    )

    def test_luna_consistency_journey(self):
        """Test Luna's autism-related consistency needs."""
        persona = PERSONAS[9]  # Luna

        # Test same command multiple times - should be consistent
        test_command = persona.typical_commands[0]
        responses = []

        for _ in range(3):
            response = self.engine.process(test_command)
            responses.append(response)

        # Responses should be very similar (consistency)
        display_texts = [r.get("display", "") for r in responses]

        # Check command consistency
        commands = [r.get("command", "") for r in responses if "command" in r]
        if len(commands) > 1:
            self.assertEqual(
                commands[0], commands[1], "Commands inconsistent for Luna (autism)"
            )

        # Check explanation detail (Luna needs detailed explanations)
        for display_text in display_texts:
            if display_text:
                self.assertGreater(
                    len(display_text), 50, "Response too brief for Luna's detail needs"
                )

    def test_all_personas_core_task_success(self):
        """Test that all personas can complete core installation task."""
        core_task = "install firefox"

        for persona in PERSONAS:
            # Set appropriate personality for persona
            if "technical" in persona.characteristics:
                self.engine.personality_system.set_personality("technical")
            elif "beginner" in persona.characteristics:
                self.engine.personality_system.set_personality("friendly")
            else:
                self.engine.personality_system.set_personality("encouraging")

            start_time = time.time()
            response = self.engine.process(core_task)
            response_time = time.time() - start_time

            # Check response time meets persona requirements
            max_time = persona.success_criteria.get("response_time", 3.0)
            self.assertLess(
                response_time,
                max_time,
                f"{persona.name} response time {response_time:.2f}s > {max_time}s",
            )

            # Check basic success
            self.assertIn(
                "display", response, f"No display response for {persona.name}"
            )

            # Check appropriate complexity level
            display_text = response["display"]
            if persona.age >= 65:  # Older personas
                self.assertLess(
                    len(display_text), 200, f"Response too long for {persona.name}"
                )

            if "ADHD" in persona.characteristics:
                self.assertLess(
                    len(display_text),
                    150,
                    f"Response too long for {persona.name} (ADHD)",
                )

    @patch("subprocess.run")
    def test_complete_user_flow(self, mock_run):
        """Test a complete multi-step user flow."""
        # Simulate David (tired parent) trying to install Zoom

        # Step 1: Initial request
        response1 = self.engine.process("I need zoom for work")
        self.assertIn("zoom", response1["display"].lower())

        # Step 2: Confirmation
        mock_run.return_value = MagicMock(returncode=0, stdout="Success")
        response2 = self.engine.process("yes install it")

        # Should understand context
        self.assertIn("zoom", response2.get("command", "").lower())

        # Step 3: Follow-up question
        response3 = self.engine.process("how do I start it?")

        # Should provide launch instructions
        self.assertIn("display", response3)
        self.assertTrue(
            "zoom" in response3["display"].lower()
            or "application" in response3["display"].lower()
        )

    def test_error_recovery_flow(self):
        """Test how different personas handle errors."""
        error_command = "install nonexistent-package-xyz"

        personas_to_test = [
            ("friendly", "Grandma Rose"),  # Should be very gentle
            ("minimal", "Maya"),  # Should be quick
            ("technical", "Dr. Sarah"),  # Should be detailed
        ]

        for personality, persona_name in personas_to_test:
            self.engine.personality_system.set_personality(personality)
            response = self.engine.process(error_command)

            # All should handle gracefully
            self.assertNotIn("error", response.get("display", "").lower())
            self.assertIn("suggestions", response)

            # Personality-specific checks
            if personality == "friendly":
                self.assertIn("try", response["display"].lower())
            elif personality == "minimal":
                self.assertLess(len(response["display"]), 100)
            elif personality == "technical":
                self.assertTrue(
                    "package" in response["display"].lower()
                    or "not found" in response["display"].lower()
                )

    def measure_response_time_percentiles(self):
        """Measure response time percentiles across all personas."""
        response_times = []

        # Collect 100 samples
        for _ in range(100):
            for persona in PERSONAS[:5]:  # Test first 5 personas
                for command in persona.typical_commands[:1]:  # First command only
                    start = time.time()
                    self.engine.process(command)
                    response_times.append(time.time() - start)

        # Calculate percentiles
        response_times.sort()
        p50 = response_times[len(response_times) // 2]
        p90 = response_times[int(len(response_times) * 0.9)]
        p95 = response_times[int(len(response_times) * 0.95)]

        # Verify SLAs
        self.assertLess(p50, 1.0, "Median response time too slow")
        self.assertLess(p90, 2.0, "90th percentile too slow")
        self.assertLess(p95, 3.0, "95th percentile too slow")

if __name__ == "__main__":
    unittest.main()
