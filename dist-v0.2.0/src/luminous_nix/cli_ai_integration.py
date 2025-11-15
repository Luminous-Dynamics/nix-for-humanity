#!/usr/bin/env python3
"""
Integrate AI Orchestrator into Luminous Nix CLI
Seamless natural language processing with HRM + Ollama
"""

import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path

# Import our AI systems
from luminous_nix.ai.orchestrator import (
    AIOrchestrator,
    get_orchestrator,
    ask,
    ModelType,
)

# Import core CLI components
from luminous_nix.core import Query, Response, ResponseType

logger = logging.getLogger(__name__)


class AIEnabledCLI:
    """Enhanced CLI with AI orchestration"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize AI-enabled CLI"""
        self.config = config or {}

        # Initialize AI orchestrator
        self.orchestrator = get_orchestrator(config)

        # Check if HRM model is available
        self._check_hrm_model()

        # Track usage statistics
        self.stats = {
            "ai_queries": 0,
            "direct_commands": 0,
            "hrm_used": 0,
            "ollama_used": 0,
        }

    def _check_hrm_model(self):
        """Check if trained HRM model is available"""
        model_path = Path("models/hrm-nixos-v1/best_model.pt")

        if model_path.exists():
            logger.info(f"✅ HRM model found: {model_path}")
            self.hrm_available = True
        else:
            logger.warning("⚠️ HRM model not found. Using fallbacks.")
            self.hrm_available = False

    def process_query(self, query_text: str, **kwargs) -> Response:
        """
        Process user query with AI orchestration

        Args:
            query_text: Natural language query
            **kwargs: Additional options (force_model, verbose, etc.)

        Returns:
            Response object with AI-generated answer
        """
        # Check if this is a direct command or natural language
        if self._is_direct_command(query_text):
            self.stats["direct_commands"] += 1
            return self._process_direct_command(query_text)

        # Use AI orchestrator for natural language
        self.stats["ai_queries"] += 1

        # Extract options
        force_model = kwargs.get("model", None)
        verbose = kwargs.get("verbose", False)

        # Get AI response
        if verbose:
            result = ask(query_text, model=force_model, verbose=True)

            # Track which model was used
            if result["model_used"] == "hrm":
                self.stats["hrm_used"] += 1
            elif result["model_used"] == "ollama":
                self.stats["ollama_used"] += 1

            # Create detailed response
            return Response(
                type=ResponseType.SUCCESS,
                message=result["answer"],
                data={
                    "model": result["model_used"],
                    "confidence": result["confidence"],
                    "time_ms": result["response_time_ms"],
                    "reasoning": result.get("reasoning_steps", []),
                },
                metadata={
                    "ai_generated": True,
                    "fallback_used": result.get("fallback_used", False),
                },
            )
        else:
            # Simple response
            answer = ask(query_text, model=force_model)

            return Response(
                type=ResponseType.SUCCESS,
                message=answer,
                metadata={"ai_generated": True},
            )

    def _is_direct_command(self, query: str) -> bool:
        """Check if query is a direct NixOS command"""
        direct_commands = [
            "nix-env",
            "nix-shell",
            "nix-build",
            "nix-channel",
            "nixos-rebuild",
            "nix",
            "home-manager",
        ]

        # Check if query starts with a known command
        first_word = query.split()[0] if query.split() else ""
        return first_word in direct_commands

    def _process_direct_command(self, command: str) -> Response:
        """Process direct NixOS command"""
        # This would execute the actual command
        # For safety, we'll just return info about it

        return Response(
            type=ResponseType.INFO,
            message=f"Direct command detected: {command}",
            data={"command": command},
            metadata={"ai_generated": False},
        )

    def explain_last_response(self) -> Response:
        """Explain how the last response was generated"""
        if self.stats["ai_queries"] == 0:
            return Response(
                type=ResponseType.INFO, message="No AI queries processed yet."
            )

        explanation = f"""
🤖 AI Processing Explanation:

Total Queries: {self.stats['ai_queries'] + self.stats['direct_commands']}
- AI Processed: {self.stats['ai_queries']}
- Direct Commands: {self.stats['direct_commands']}

AI Model Usage:
- HRM (Fast NixOS): {self.stats['hrm_used']} queries
- Ollama (General): {self.stats['ollama_used']} queries
- Pattern Fallback: {self.stats['ai_queries'] - self.stats['hrm_used'] - self.stats['ollama_used']} queries

HRM handles: dependencies, configs, errors, optimization
Ollama handles: explanations, concepts, general knowledge
"""

        return Response(type=ResponseType.INFO, message=explanation)

    def get_statistics(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            **self.stats,
            "hrm_percentage": (
                self.stats["hrm_used"] / self.stats["ai_queries"] * 100
                if self.stats["ai_queries"] > 0
                else 0
            ),
            "ai_percentage": (
                self.stats["ai_queries"]
                / (self.stats["ai_queries"] + self.stats["direct_commands"])
                * 100
                if (self.stats["ai_queries"] + self.stats["direct_commands"]) > 0
                else 0
            ),
        }


def integrate_with_existing_cli():
    """
    Integration code to add AI to existing CLI
    This would be called from the main CLI module
    """

    # Import existing CLI
    try:
        from luminous_nix.cli import CLI, main

        # Monkey-patch AI capabilities
        original_process = CLI.process_input

        def ai_enhanced_process(self, user_input: str) -> Response:
            """Enhanced input processing with AI"""

            # Check if AI is enabled
            if self.config.get("ai_enabled", True):
                # Create AI-enabled processor
                ai_cli = AIEnabledCLI(self.config)

                # Process with AI
                return ai_cli.process_query(user_input)
            else:
                # Fall back to original processing
                return original_process(self, user_input)

        # Replace method
        CLI.process_input = ai_enhanced_process

        logger.info("✅ AI integration successful!")
        return True

    except ImportError:
        logger.error("Could not import existing CLI")
        return False


# CLI Entry Point Enhancement
def enhanced_cli_main():
    """Enhanced main function with AI support"""
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="Luminous Nix - Natural Language NixOS with AI"
    )

    parser.add_argument("query", nargs="*", help="Natural language query or command")

    parser.add_argument(
        "--model",
        choices=["hrm", "ollama", "auto"],
        default="auto",
        help="Force specific AI model",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed AI processing info"
    )

    parser.add_argument("--no-ai", action="store_true", help="Disable AI processing")

    parser.add_argument(
        "--explain", action="store_true", help="Explain AI routing decision"
    )

    args = parser.parse_args()

    # Create AI-enabled CLI
    config = {"ai_enabled": not args.no_ai, "hrm_enabled": True, "ollama_enabled": True}

    cli = AIEnabledCLI(config)

    # Process query
    if args.query:
        query_text = " ".join(args.query)

        if args.explain:
            # Explain routing
            orchestrator = get_orchestrator()
            explanation = orchestrator.explain_routing(query_text)
            print(f"🔍 Query: {query_text}")
            print(f"📍 Would route to: {explanation['selected_model']}")
            print(f"📝 Reasoning: {', '.join(explanation['reasoning'])}")
        else:
            # Process query
            response = cli.process_query(
                query_text,
                model=args.model if args.model != "auto" else None,
                verbose=args.verbose,
            )

            # Display response
            print(response.message)

            if args.verbose and response.data:
                print(f"\n📊 AI Details:")
                print(f"  Model: {response.data.get('model', 'unknown')}")
                print(f"  Confidence: {response.data.get('confidence', 0):.0%}")
                print(f"  Time: {response.data.get('time_ms', 0):.1f}ms")

                if response.data.get("reasoning"):
                    print(f"  Reasoning steps: {len(response.data['reasoning'])}")

    else:
        # Interactive mode
        print("🤖 Luminous Nix AI Assistant")
        print("Type 'help' for commands, 'exit' to quit")
        print("-" * 40)

        while True:
            try:
                user_input = input("\n> ").strip()

                if user_input.lower() in ["exit", "quit", "q"]:
                    break
                elif user_input.lower() == "stats":
                    stats = cli.get_statistics()
                    print(f"📊 Statistics:")
                    print(f"  AI queries: {stats['ai_queries']}")
                    print(f"  Direct commands: {stats['direct_commands']}")
                    print(f"  HRM usage: {stats['hrm_percentage']:.0f}%")
                elif user_input.lower() == "explain":
                    response = cli.explain_last_response()
                    print(response.message)
                elif user_input:
                    response = cli.process_query(user_input, verbose=args.verbose)
                    print(response.message)

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

        # Show final statistics
        stats = cli.get_statistics()
        if stats["ai_queries"] > 0:
            print(f"\n📊 Session Statistics:")
            print(f"  Total queries: {stats['ai_queries'] + stats['direct_commands']}")
            print(f"  AI handled: {stats['ai_percentage']:.0f}%")
            print(f"  HRM used: {stats['hrm_percentage']:.0f}% of AI queries")


if __name__ == "__main__":
    # Run enhanced CLI
    enhanced_cli_main()
