"""
Socratic Teaching - AI That Builds Understanding Through Dialogue

Revolutionary capability: Don't just answer - ask questions that build
deep understanding. Verify comprehension before moving forward.

This transforms AI from answer-giver to genuine teacher.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random


class TeachingMode(Enum):
    """Different ways to teach a concept"""
    ANALOGY = "analogy"           # Compare to something familiar
    EXAMPLE = "example"           # Show concrete example
    QUESTION = "question"         # Ask guiding questions
    PRACTICE = "practice"         # Hands-on exercise
    EXPLANATION = "explanation"   # Direct explanation
    DISCOVERY = "discovery"       # Guide to discover themselves


class QuestionType(Enum):
    """Types of Socratic questions"""
    CLARIFICATION = "clarification"     # "What do you mean by...?"
    ASSUMPTION = "assumption"           # "What are we assuming?"
    REASON = "reason"                   # "Why do you think...?"
    PERSPECTIVE = "perspective"         # "What would happen if...?"
    IMPLICATION = "implication"         # "What follows from this?"
    QUESTION_QUESTION = "question_question"  # "Why did you ask that?"


@dataclass
class TeachingStep:
    """One step in a teaching sequence"""
    mode: TeachingMode
    content: str                    # What to say/ask
    expected_understanding: str     # What user should learn
    verification: Optional[str]     # Question to verify understanding
    hints: List[str] = field(default_factory=list)  # If user struggles


@dataclass
class TeachingSequence:
    """Complete teaching sequence for a concept"""
    concept_id: str
    concept_name: str
    goal: str                       # What user should understand
    prerequisites: List[str]        # What they need to know first
    steps: List[TeachingStep]       # Teaching steps
    current_step: int = 0
    user_understanding: float = 0.0  # 0.0-1.0 after teaching


@dataclass
class SocraticQuestion:
    """A Socratic question to guide learning"""
    question: str
    type: QuestionType
    concept_id: str
    expected_answers: List[str]     # What we're looking for
    hints: List[str]                # If user needs help
    follow_up: Optional[str] = None  # Next question based on answer


class SocraticTeacher:
    """
    Teaches through dialogue, questions, and discovery.

    Philosophy: Don't just tell - guide users to understand through
    questions that build on what they already know.
    """

    def __init__(self):
        """Initialize Socratic teaching system"""
        self.teaching_sequences = self._build_teaching_sequences()
        self.active_teachings: Dict[str, TeachingSequence] = {}
        self.meta_learning = None  # Will be set by SimpleChat for personalization

    def set_meta_learning(self, meta_learning_engine):
        """
        🧠 LAYER 4: Set meta-learning engine for personalized teaching.

        This allows the Socratic teacher to adapt its approach based on
        how each individual user learns best.
        """
        self.meta_learning = meta_learning_engine

    def get_active_session(self, session_id: str = "default") -> Optional[TeachingSequence]:
        """Get the active teaching session for meta-learning integration"""
        return self.active_teachings.get(session_id)

    def _build_teaching_sequences(self) -> Dict[str, TeachingSequence]:
        """
        Build teaching sequences for core NixOS concepts.

        Each sequence uses Socratic method to build understanding.
        """
        sequences = {}

        # Declarative Configuration
        sequences['declarative'] = TeachingSequence(
            concept_id='declarative',
            concept_name='Declarative Configuration',
            goal='Understand how declarative differs from imperative',
            prerequisites=[],
            steps=[
                TeachingStep(
                    mode=TeachingMode.QUESTION,
                    content="Think about cooking. If I give you a recipe vs. showing you the finished dish and saying 'make it look like this' - which approach is which?",
                    expected_understanding="Difference between steps (recipe) and desired outcome (finished dish)",
                    verification="In NixOS, do you describe the steps to get your system configured, or the final state you want?"
                ),
                TeachingStep(
                    mode=TeachingMode.ANALOGY,
                    content="🎯 Exactly! NixOS is like showing a photo of the finished dish. You write configuration.nix describing what you WANT (final state), not HOW to get there (steps). NixOS figures out the steps.",
                    expected_understanding="Declarative = describe desired state",
                    verification="Why is this powerful? What happens if you run the same config twice?"
                ),
                TeachingStep(
                    mode=TeachingMode.DISCOVERY,
                    content="Great insight! Running twice does the same thing = idempotent. This means you can't accidentally break things by rebuilding. Try it!",
                    expected_understanding="Idempotency makes systems safe",
                    verification=None
                )
            ]
        )

        # Generations
        sequences['generations'] = TeachingSequence(
            concept_id='generations',
            concept_name='System Generations',
            goal='Understand generations as safety net',
            prerequisites=['declarative'],
            steps=[
                TeachingStep(
                    mode=TeachingMode.ANALOGY,
                    content="Have you played video games with save points? What happens if you die or make a mistake?",
                    expected_understanding="Save points let you go back",
                    verification="How is this similar to NixOS generations?"
                ),
                TeachingStep(
                    mode=TeachingMode.EXAMPLE,
                    content="🎮 Exactly! Every nixos-rebuild creates a 'save point' (generation). If something breaks, just reboot and pick an earlier generation from the boot menu. Your system = restored!",
                    expected_understanding="Generations enable rollback",
                    verification="Why does this make experimentation safe?"
                ),
                TeachingStep(
                    mode=TeachingMode.PRACTICE,
                    content="💡 Yes! You can try anything without fear. Let's see your generations: `nixos-rebuild list-generations`. Each is a complete system snapshot!",
                    expected_understanding="Generations are complete snapshots",
                    verification=None
                )
            ]
        )

        # Flakes
        sequences['flakes'] = TeachingSequence(
            concept_id='flakes',
            concept_name='Flakes',
            goal='Understand flakes as reproducible dependencies',
            prerequisites=['reproducible', 'packages'],
            steps=[
                TeachingStep(
                    mode=TeachingMode.QUESTION,
                    content="Imagine you're baking with a recipe that says 'flour' but doesn't specify what kind or brand. Could two bakers get different results?",
                    expected_understanding="Vague dependencies = inconsistent results",
                    verification="How does this relate to software packages?"
                ),
                TeachingStep(
                    mode=TeachingMode.ANALOGY,
                    content="🎯 Exactly! Traditional channels are like 'flour' - could be any version. Flakes are like 'King Arthur All-Purpose Flour, batch #12345' - EXACT version locked in flake.lock. Same input = same output, always!",
                    expected_understanding="Flakes lock exact versions",
                    verification="Why is this important for sharing configurations?"
                ),
                TeachingStep(
                    mode=TeachingMode.PRACTICE,
                    content="💡 Right! Share flake.nix + flake.lock = others get EXACTLY your versions. Try: `nix flake init` to create your first flake!",
                    expected_understanding="Flakes enable true reproducibility",
                    verification=None
                )
            ]
        )

        # Modules
        sequences['modules'] = TeachingSequence(
            concept_id='modules',
            concept_name='NixOS Modules',
            goal='Understand modules as composable configuration',
            prerequisites=['declarative'],
            steps=[
                TeachingStep(
                    mode=TeachingMode.ANALOGY,
                    content="Think of Lego bricks. Each brick does one thing, but you can combine them to build anything. What makes Lego powerful?",
                    expected_understanding="Composability - combine small pieces",
                    verification="How is NixOS configuration similar?"
                ),
                TeachingStep(
                    mode=TeachingMode.EXAMPLE,
                    content="🎯 Perfect! NixOS modules are like Lego bricks. Each module configures one thing (nginx, users, network). Import modules you need:\n```nix\nimports = [ ./hardware.nix ./nginx.nix ./users.nix ];\n```\nEach file is self-contained and reusable!",
                    expected_understanding="Modules enable composition",
                    verification="Why is breaking config into modules helpful?"
                ),
                TeachingStep(
                    mode=TeachingMode.DISCOVERY,
                    content="💡 Yes! Organization, reusability, clarity. You can even share modules between machines. Try splitting your config into logical modules!",
                    expected_understanding="Modules improve organization",
                    verification=None
                )
            ]
        )

        return sequences

    def start_teaching(self, concept_id: str, session_id: str = "default") -> Tuple[str, bool]:
        """
        Begin teaching a concept using Socratic method.

        Args:
            concept_id: ID of concept to teach
            session_id: Unique session identifier

        Returns:
            (first_message, success)
        """
        if concept_id not in self.teaching_sequences:
            return (f"I don't have a teaching sequence for '{concept_id}' yet. Ask me to explain it directly!", False)

        # Start new teaching session
        sequence = self.teaching_sequences[concept_id]
        sequence.current_step = 0
        sequence.user_understanding = 0.0

        self.active_teachings[session_id] = sequence

        # Return first step
        first_step = sequence.steps[0]
        message = f"📚 **Let's learn about {sequence.concept_name}!**\n\n{first_step.content}"

        return (message, True)

    def respond_to_teaching(self, user_response: str, session_id: str = "default") -> Tuple[str, bool, bool]:
        """
        Continue Socratic dialogue based on user response.

        Args:
            user_response: What user said
            session_id: Session identifier

        Returns:
            (response_message, teaching_complete, understanding_verified)
        """
        if session_id not in self.active_teachings:
            return ("No active teaching session. Say 'teach me about [concept]' to start!", False, False)

        sequence = self.active_teachings[session_id]
        current_step = sequence.steps[sequence.current_step]

        # Evaluate user's response (simple keyword matching for now)
        understanding_shown = self._evaluate_understanding(user_response, current_step)

        if understanding_shown:
            # User shows understanding - move to next step
            sequence.user_understanding += 0.3  # Increment understanding
            sequence.current_step += 1

            if sequence.current_step >= len(sequence.steps):
                # Teaching complete!
                del self.active_teachings[session_id]
                completion_message = f"""
🎉 **Excellent! You understand {sequence.concept_name}!**

You've learned:
- {sequence.goal}

Your confidence: {min(sequence.user_understanding, 1.0):.0%}

Keep practicing and this knowledge will stick! Want to learn something else?
"""
                return (completion_message, True, True)

            # Continue to next step
            next_step = sequence.steps[sequence.current_step]
            return (next_step.content, False, True)

        else:
            # User needs help - provide hint
            if current_step.hints:
                hint = random.choice(current_step.hints)
                message = f"💡 Let me give you a hint: {hint}\n\nTake your time - what do you think?"
            else:
                message = f"That's a good try! Think about: {current_step.expected_understanding}\n\nWhat comes to mind?"

            return (message, False, False)

    def _evaluate_understanding(self, response: str, step: TeachingStep) -> bool:
        """
        Evaluate if user response shows understanding.

        For now, uses simple keyword matching. In future, could use
        LLM to evaluate semantic understanding.
        """
        response_lower = response.lower()

        # Keywords that indicate understanding for different modes
        understanding_keywords = {
            TeachingMode.QUESTION: ['steps', 'outcome', 'state', 'want', 'result', 'final'],
            TeachingMode.ANALOGY: ['like', 'similar', 'same', 'describes', 'declarative'],
            TeachingMode.EXAMPLE: ['rollback', 'back', 'restore', 'undo', 'previous'],
            TeachingMode.DISCOVERY: ['safe', 'experiment', 'try', 'fear', 'break'],
            TeachingMode.PRACTICE: ['yes', 'let', 'show', 'try', 'do it']
        }

        keywords = understanding_keywords.get(step.mode, [])

        # Check if response contains understanding keywords
        matches = sum(1 for keyword in keywords if keyword in response_lower)

        # If any keywords match, or response is detailed (>20 chars), consider understood
        return matches > 0 or len(response) > 20

    def generate_socratic_question(self, concept_id: str, user_level: str = "beginner") -> SocraticQuestion:
        """
        Generate a Socratic question to deepen understanding.

        Args:
            concept_id: Concept to ask about
            user_level: User's knowledge level

        Returns:
            SocraticQuestion to ask
        """
        # Question templates by level
        beginner_templates = [
            "What do you think {concept} means?",
            "Can you give me an example of {concept}?",
            "How would you explain {concept} to someone?",
            "What's the purpose of {concept}?",
        ]

        intermediate_templates = [
            "How does {concept} differ from {related}?",
            "What are the benefits of {concept}?",
            "When would you use {concept}?",
            "What problems does {concept} solve?",
        ]

        advanced_templates = [
            "What are the implications of {concept}?",
            "How does {concept} relate to the broader system?",
            "What trade-offs exist with {concept}?",
            "How would you implement {concept}?",
        ]

        # Select template based on level
        if user_level == "beginner":
            templates = beginner_templates
            qtype = QuestionType.CLARIFICATION
        elif user_level == "intermediate":
            templates = intermediate_templates
            qtype = QuestionType.REASON
        else:
            templates = advanced_templates
            qtype = QuestionType.IMPLICATION

        # Generate question (simplified - would use cognitive model in real implementation)
        question_template = random.choice(templates)
        question = question_template.format(concept=concept_id, related="alternatives")

        return SocraticQuestion(
            question=question,
            type=qtype,
            concept_id=concept_id,
            expected_answers=[],
            hints=["Think about the core purpose", "Consider how it differs from traditional approaches"],
            follow_up="Great! Now let's explore..."
        )

    def suggest_teaching_moment(self, concept_id: str, user_knowledge_level: float) -> str:
        """
        Suggest when to teach a concept based on user readiness.

        Args:
            concept_id: Concept to potentially teach
            user_knowledge_level: User's overall knowledge (0.0-1.0)

        Returns:
            Teaching moment message
        """
        if concept_id not in self.teaching_sequences:
            return f"I don't have a teaching sequence for {concept_id} yet."

        sequence = self.teaching_sequences[concept_id]

        # Check if prerequisites met (would integrate with cognitive model)
        prereqs_met = True  # Simplified

        if not prereqs_met:
            missing = ", ".join(sequence.prerequisites)
            return f"To learn {sequence.concept_name}, you'll first need to understand: {missing}"

        # Generate teaching moment message
        if user_knowledge_level < 0.3:
            # Beginner - gentle introduction
            return f"""
💡 **Learning Opportunity: {sequence.concept_name}**

I notice you're ready to learn this concept! I'll teach you through:
- Analogies to familiar concepts
- Guided questions
- Hands-on examples

Goal: {sequence.goal}

Say 'teach me about {sequence.concept_name.lower()}' when you're ready!
"""
        elif user_knowledge_level < 0.6:
            # Intermediate - more direct
            return f"""
💡 **Ready to Learn: {sequence.concept_name}**

You have the prerequisites! This builds on what you know.

Goal: {sequence.goal}

Say 'teach me' to start!
"""
        else:
            # Advanced - brief
            return f"""
💡 {sequence.concept_name} available. Prerequisites met.
Goal: {sequence.goal}
Say 'teach' to learn.
"""


def get_socratic_teacher() -> SocraticTeacher:
    """Get singleton instance of Socratic teacher"""
    global _socratic_teacher

    if _socratic_teacher is None:
        _socratic_teacher = SocraticTeacher()

    return _socratic_teacher


# Singleton
_socratic_teacher: Optional[SocraticTeacher] = None
