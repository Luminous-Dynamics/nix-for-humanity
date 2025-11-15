#!/usr/bin/env python3
"""
Enhanced AI Integration

This module brings together all Phase C improvements:
- Corpus-based knowledge
- Prompt refinement
- Personality modes
- Learning from corrections
"""

import os
from typing import Dict, List, Optional, Any
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from .corpus_builder import NixOSCorpusBuilder
from .prompt_refiner import PromptRefiner, SmartOllamaClient
from .personality_modes import PersonalityManager, PersonalityType
from .learning_system import LearningSystem, InteractiveLearning


class EnhancedAI:
    """
    Enhanced AI system with all Phase C improvements

    Features:
    - Reduced hallucinations through prompt refinement
    - Multiple personality modes
    - Learning from user corrections
    - Corpus-based accurate responses
    """

    def __init__(self, personality: str = "friend"):
        """Initialize enhanced AI"""
        self.console = Console()

        # Initialize components
        self.smart_client = SmartOllamaClient()
        self.preferences = get_preferences()
        self.learning_system = LearningSystem()
        self.interactive_learning = InteractiveLearning()

        # Set initial personality
        personality_map = {
            "teacher": PersonalityType.TEACHER,
            "expert": PersonalityType.EXPERT,
            "friend": PersonalityType.FRIEND,
            "grandma": PersonalityType.GRANDMA,
        }

        if personality in personality_map:
            self.preferences.set_personality(personality_map[personality])

        # Check if corpus exists
        self.corpus_dir = Path("corpus")
        if not self.corpus_dir.exists():
            self.console.print("[yellow]Building NixOS knowledge corpus...[/yellow]")
            self._build_corpus()

    def _build_corpus(self):
        """Build the NixOS corpus if needed"""
        builder = NixOSCorpusBuilder()
        builder.build_corpus()

    def ask(
        self,
        question: str,
        interactive_feedback: bool = False,
        auto_personality: bool = True,
    ) -> str:
        """
        Ask a question with enhanced AI

        Args:
            question: The user's question
            interactive_feedback: Whether to ask for feedback
            auto_personality: Whether to auto-select personality

        Returns:
            The AI's response
        """

        # Check for learned correction first
        learned_response = self.learning_system.check_for_correction(question)

        if learned_response:
            # Apply personality formatting to learned response
            formatted = self.preferences.format_response(
                learned_response, auto_select=auto_personality, user_input=question
            )
            return formatted

        # Get refined AI response
        result = self.smart_client.ask(question, validate=True)

        if result.get("answer"):
            # Apply personality formatting
            formatted = self.preferences.format_response(
                result["answer"], auto_select=auto_personality, user_input=question
            )

            # Show confidence if low
            if result.get("confidence", 1.0) < 0.5:
                self.console.print(f"[dim]Confidence: {result['confidence']:.0%}[/dim]")

            # Show validation warnings
            if result.get("validation") and not result["validation"]["valid"]:
                self.console.print(
                    "[yellow]⚠ Response may contain inaccuracies[/yellow]"
                )

            # Interactive feedback if requested
            if interactive_feedback:
                feedback = self.interactive_learning.get_feedback(question, formatted)

                if feedback:
                    self.console.print("[dim]Thank you for your feedback![/dim]")

            return formatted

        else:
            # Fallback response
            return self.preferences.format_response(
                "I don't have enough information to answer that accurately. "
                "Could you provide more details?",
                auto_select=auto_personality,
                user_input=question,
            )

    def set_personality(self, personality: str):
        """Set the AI personality"""
        personality_map = {
            "teacher": PersonalityType.TEACHER,
            "expert": PersonalityType.EXPERT,
            "friend": PersonalityType.FRIEND,
            "grandma": PersonalityType.GRANDMA,
        }

        if personality in personality_map:
            self.preferences.set_personality(personality_map[personality])
        else:
            self.console.print(f"[red]Unknown personality: {personality}[/red]")

    def get_stats(self) -> Panel:
        """Get AI statistics"""

        learning_stats = self.learning_system.stats
        personality_info = self.preferences.current_personality.profile

        stats_text = f"""
[bold]Enhanced AI Status:[/bold]

🎭 Current Personality: {personality_info.name}
📚 Corpus Documents: {len(self.smart_client.refiner.documents)}
🧠 Patterns Learned: {learning_stats['patterns_learned']}
✏️ Corrections Made: {learning_stats['corrections']}
📊 Total Feedback: {learning_stats['total_feedback']}

[bold]Personality Settings:[/bold]
• Formality: {"█" * int(personality_info.formality * 5)}{"░" * (5 - int(personality_info.formality * 5))}
• Technical: {"█" * int(personality_info.technicality * 5)}{"░" * (5 - int(personality_info.technicality * 5))}
• Verbosity: {"█" * int(personality_info.verbosity * 5)}{"░" * (5 - int(personality_info.verbosity * 5))}

[bold]Learning Progress:[/bold]
• Accuracy Improvement: {learning_stats.get('accuracy_improvement', 0):.1f}%
"""

        return Panel(stats_text, title="[cyan]Enhanced AI System[/cyan]")

    def export_knowledge(self, output_file: str):
        """Export learned knowledge"""
        self.learning_system.export_knowledge(output_file)

    def rebuild_corpus(self):
        """Rebuild the NixOS corpus"""
        self.console.print("[yellow]Rebuilding NixOS knowledge corpus...[/yellow]")
        builder = NixOSCorpusBuilder()
        result = builder.build_corpus()
        self.console.print(
            f"[green]✅ Corpus rebuilt: {result['documents']} documents[/green]"
        )

        # Reload in refiner
        self.smart_client.refiner.documents = (
            self.smart_client.refiner._load_corpus_documents()
        )
        self.smart_client.refiner.qa_pairs = self.smart_client.refiner._load_qa_pairs()


def integrate_with_cli():
    """Integration code for the main CLI"""

    from ..cli import cli
    import click

    # Add AI commands to CLI
    @cli.group(name="ai")
    def ai_group():
        """Enhanced AI commands"""
        pass

    @ai_group.command(name="ask")
    @click.argument("question", nargs=-1)
    @click.option(
        "--personality",
        "-p",
        type=click.Choice(["teacher", "expert", "friend", "grandma"]),
        default="friend",
        help="AI personality mode",
    )
    @click.option(
        "--feedback", "-f", is_flag=True, help="Provide feedback to improve responses"
    )
    def ask_command(question, personality, feedback):
        """Ask the enhanced AI a question"""

        ai = EnhancedAI(personality)
        question_text = " ".join(question)

        response = ai.ask(question_text, interactive_feedback=feedback)
        click.echo(response)

    @ai_group.command(name="personality")
    @click.argument(
        "mode", type=click.Choice(["teacher", "expert", "friend", "grandma"])
    )
    def set_personality(mode):
        """Set AI personality mode"""

        ai = EnhancedAI()
        ai.set_personality(mode)
        click.echo(f"Personality set to: {mode}")

    @ai_group.command(name="stats")
    def show_stats():
        """Show AI learning statistics"""

        ai = EnhancedAI()
        console = Console()
        console.print(ai.get_stats())

    @ai_group.command(name="export")
    @click.argument("output_file")
    def export_knowledge(output_file):
        """Export learned knowledge"""

        ai = EnhancedAI()
        ai.export_knowledge(output_file)

    @ai_group.command(name="rebuild-corpus")
    def rebuild_corpus():
        """Rebuild the NixOS knowledge corpus"""

        ai = EnhancedAI()
        ai.rebuild_corpus()


def demo():
    """Demo the enhanced AI"""

    console = Console()
    ai = EnhancedAI()

    console.print(
        Panel.fit(
            "[bold cyan]🤖 Enhanced AI Demo[/bold cyan]\n"
            "Now with reduced hallucinations, personalities, and learning!",
            border_style="cyan",
        )
    )

    # Test questions
    test_questions = [
        ("How do I install Firefox?", "friend"),
        ("Enable SSH service", "expert"),
        ("What is NixOS?", "teacher"),
        ("I need help installing vim", "grandma"),
    ]

    for question, personality in test_questions:
        console.print(f"\n[bold]Question:[/bold] {question}")
        console.print(f"[dim]Using {personality} personality...[/dim]")

        ai.set_personality(personality)
        response = ai.ask(question, interactive_feedback=False)

        console.print(f"[bold]Answer:[/bold] {response[:300]}...")
        console.print("-" * 60)

    # Show stats
    console.print("\n")
    console.print(ai.get_stats())


if __name__ == "__main__":
    demo()
