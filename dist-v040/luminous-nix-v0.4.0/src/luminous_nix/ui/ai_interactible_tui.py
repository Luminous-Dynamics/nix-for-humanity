#!/usr/bin/env python3
"""
🤖 AI-Interactible TUI Wrapper

This module makes the TUI fully controllable via AI or automated scripts.
Instead of requiring an interactive terminal, it provides a programmatic
interface that can be driven by AI agents, test scripts, or headless environments.
"""

import asyncio
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# Add textual driver support for headless mode
try:
    from textual._driver import Driver as BaseDriver
    from textual.driver import Driver
except ImportError:
    Driver = None
    BaseDriver = None

from ..interfaces.cli import UnifiedNixAssistant
from .main_app import NixForHumanityTUI


@dataclass
class TUIResponse:
    """Response from AI-driven TUI interaction"""

    success: bool
    output: str
    state: dict[str, Any]
    commands_executed: list[str]
    timestamp: datetime


class HeadlessDriver:
    """Mock driver for headless TUI operation"""

    def __init__(self):
        self.output_buffer = []
        self.state = {}
        self.is_inline = False  # Added for compatibility
        self.size = (80, 24)  # Default terminal size

    def write(self, text: str):
        """Capture output"""
        self.output_buffer.append(text)

    def get_output(self) -> str:
        """Get captured output"""
        return "".join(self.output_buffer)

    def clear_output(self):
        """Clear output buffer"""
        self.output_buffer = []

    def start_application_mode(self):
        """Mock method for compatibility"""
        pass

    def stop_application_mode(self):
        """Mock method for compatibility"""
        pass


class AIInteractibleTUI:
    """
    AI-Interactible TUI Interface

    This class provides a programmatic interface to the TUI that can be
    controlled without an interactive terminal. Perfect for:
    - AI agents controlling the interface
    - Automated testing
    - Headless server environments
    - Scripted interactions
    """

    def __init__(self, mindful_mode: bool = False):
        """Initialize the AI-interactible TUI"""
        self.mindful_mode = mindful_mode
        self.tui: NixForHumanityTUI | None = None
        self.cli_backend = UnifiedNixAssistant()
        self.conversation_history: list[tuple[str, str]] = []
        self.state = {
            "mode": "normal",
            "last_command": None,
            "search_results": [],
            "install_queue": [],
            "errors": [],
            "flow_state": False,
            "zen_mode": False,
        }

    async def initialize(self) -> bool:
        """Initialize the TUI in headless mode"""
        try:
            # Create TUI in headless mode
            self.tui = NixForHumanityTUI(mindful_mode=self.mindful_mode, headless=True)

            # Set up headless driver
            if not hasattr(self.tui, "_driver") or self.tui._driver is None:
                self.tui._driver = HeadlessDriver()

            # Initialize components without display
            await self._initialize_components()

            return True

        except Exception as e:
            print(f"Failed to initialize AI-TUI: {e}")
            return False

    async def _initialize_components(self):
        """Initialize TUI components for headless operation"""
        # Don't call on_mount in headless mode as it expects a screen stack
        # Just set up the backend and state directly
        self.state["initialized"] = True
        self.state["timestamp"] = datetime.now().isoformat()

        # Initialize TUI backend if available
        if hasattr(self.tui, "backend"):
            # Backend is already initialized in __init__
            pass

    async def send_command(self, command: str) -> TUIResponse:
        """
        Send a command to the TUI and get response

        This is the main interface for AI interaction.
        Commands can be natural language or specific TUI commands.
        """
        try:
            # Track command
            self.state["last_command"] = command
            commands_executed = []

            # Process special TUI commands
            if command.lower() == "zen":
                self.state["zen_mode"] = not self.state["zen_mode"]
                output = "🧘 Zen mode " + (
                    "activated" if self.state["zen_mode"] else "deactivated"
                )

            elif command.lower() == "flow":
                self.state["flow_state"] = True
                output = "🌊 Entering flow state..."

            elif command.lower() == "help":
                output = self._get_help_text()

            elif command.lower() in ["quit", "exit"]:
                output = "👋 Goodbye!"
                self.state["exiting"] = True

            else:
                # Process through backend CLI
                output = await self._process_natural_language(command)
                commands_executed = self.state.get("nix_commands", [])

            # Add to conversation history
            self.conversation_history.append((command, output))

            # Create response
            return TUIResponse(
                success=True,
                output=output,
                state=self.state.copy(),
                commands_executed=commands_executed,
                timestamp=datetime.now(),
            )

        except Exception as e:
            self.state["errors"].append(str(e))
            return TUIResponse(
                success=False,
                output=f"Error: {e}",
                state=self.state.copy(),
                commands_executed=[],
                timestamp=datetime.now(),
            )

    async def _process_natural_language(self, query: str) -> str:
        """Process natural language query through CLI backend"""
        try:
            # Use the CLI backend to process
            import io
            from contextlib import redirect_stdout

            f = io.StringIO()
            with redirect_stdout(f):
                self.cli_backend.answer(query)
            output = f.getvalue()

            # Extract any Nix commands that would be executed
            if "Would install:" in output or "Would run:" in output:
                lines = output.split("\n")
                commands = []
                for line in lines:
                    if line.strip().startswith("nix"):
                        commands.append(line.strip())
                self.state["nix_commands"] = commands

            return output

        except Exception as e:
            return f"Failed to process: {e}"

    def _get_help_text(self) -> str:
        """Get help text for AI interaction"""
        return """
🤖 AI-Interactible TUI Commands:

Natural Language:
• "install firefox" - Install a package
• "search text editor" - Search for packages
• "list installed" - Show installed packages
• "update system" - Update NixOS
• "clean up disk" - Run garbage collection
• "create python shell" - Make dev environment

Special Commands:
• "zen" - Toggle zen mode (minimal UI)
• "flow" - Enter flow state
• "help" - Show this help
• "status" - Get current state
• "quit" - Exit

AI Control Features:
• Fully headless operation
• State tracking and history
• Command preview (dry-run)
• Error recovery
• Batch operations

Example AI Workflow:
1. Send: "search for video editor"
2. Get: List of options
3. Send: "install kdenlive"
4. Get: Installation confirmation
5. Send: "status"
6. Get: Current system state
"""

    async def get_state(self) -> dict[str, Any]:
        """Get current TUI state for AI inspection"""
        return {
            "state": self.state.copy(),
            "conversation_count": len(self.conversation_history),
            "last_interaction": self.conversation_history[-1]
            if self.conversation_history
            else None,
            "mode": "mindful" if self.mindful_mode else "performance",
            "zen_active": self.state.get("zen_mode", False),
            "flow_active": self.state.get("flow_state", False),
        }

    async def batch_commands(self, commands: list[str]) -> list[TUIResponse]:
        """Execute multiple commands in sequence"""
        responses = []
        for cmd in commands:
            response = await self.send_command(cmd)
            responses.append(response)

            # Stop on error or exit
            if not response.success or self.state.get("exiting"):
                break

        return responses

    async def simulate_interaction(
        self, script: list[dict[str, str]]
    ) -> list[TUIResponse]:
        """
        Simulate a scripted interaction

        Script format:
        [
            {"command": "search editor", "wait": 1},
            {"command": "install vim", "wait": 2},
            {"command": "status", "wait": 0}
        ]
        """
        responses = []

        for step in script:
            command = step.get("command", "")
            wait = step.get("wait", 0)

            response = await self.send_command(command)
            responses.append(response)

            if wait > 0:
                await asyncio.sleep(wait)

            if not response.success or self.state.get("exiting"):
                break

        return responses

    def get_conversation_history(self) -> list[tuple[str, str]]:
        """Get full conversation history"""
        return self.conversation_history.copy()

    def export_session(self, filepath: Path | None = None) -> str:
        """Export session data as JSON"""
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "mode": "mindful" if self.mindful_mode else "performance",
            "conversation": [
                {"input": cmd, "output": resp, "index": i}
                for i, (cmd, resp) in enumerate(self.conversation_history)
            ],
            "final_state": self.state,
            "statistics": {
                "total_commands": len(self.conversation_history),
                "errors": len(self.state.get("errors", [])),
            },
        }

        json_str = json.dumps(session_data, indent=2, default=str)

        if filepath:
            filepath.write_text(json_str)

        return json_str


class AICLI:
    """
    Command-line interface for AI-driven TUI interaction

    This allows AI agents to control the TUI from the command line.
    """

    @staticmethod
    async def run_interactive():
        """Run interactive AI-controlled session"""
        print("🤖 AI-Interactible TUI - Command Line Interface")
        print("Type 'help' for commands, 'quit' to exit")
        print("-" * 50)

        tui = AIInteractibleTUI(mindful_mode=False)
        await tui.initialize()

        while True:
            try:
                # Get input
                command = input("AI> ").strip()

                if not command:
                    continue

                # Process command
                response = await tui.send_command(command)

                # Show output
                print(response.output)

                # Check for exit
                if command.lower() in ["quit", "exit"]:
                    break

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

        # Export session
        print("\nExporting session...")
        session_json = tui.export_session()
        session_file = (
            Path.home() / f"luminous-nix-ai-session-{datetime.now():%Y%m%d-%H%M%S}.json"
        )
        session_file.write_text(session_json)
        print(f"Session exported to: {session_file}")

    @staticmethod
    async def run_script(script_file: Path):
        """Run a scripted AI interaction"""
        print(f"🤖 Running AI script: {script_file}")

        # Load script
        script_data = json.loads(script_file.read_text())

        # Initialize TUI
        tui = AIInteractibleTUI(mindful_mode=script_data.get("mindful_mode", False))
        await tui.initialize()

        # Run script
        responses = await tui.simulate_interaction(script_data["commands"])

        # Show results
        print(f"\n{'='*50}")
        print(f"Script completed: {len(responses)} commands executed")

        for i, response in enumerate(responses):
            print(f"\n[{i+1}] Success: {response.success}")
            print(f"Output: {response.output[:100]}...")

        # Export results
        results_file = script_file.with_suffix(".results.json")
        tui.export_session(results_file)
        print(f"\nResults exported to: {results_file}")


# Make it importable and runnable
async def test_ai_tui():
    """Test the AI-interactible TUI"""
    print("Testing AI-Interactible TUI...")

    tui = AIInteractibleTUI(mindful_mode=False)
    if not await tui.initialize():
        print("Failed to initialize")
        return

    # Test commands
    test_commands = [
        "help",
        "search text editor",
        "list installed",
        "zen",
        "flow",
        "status",
    ]

    print("\nRunning test commands:")
    for cmd in test_commands:
        print(f"\n> {cmd}")
        response = await tui.send_command(cmd)
        print(f"Success: {response.success}")
        print(f"Output preview: {response.output[:200]}...")

    print("\n✅ AI-Interactible TUI test complete!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            asyncio.run(test_ai_tui())
        elif sys.argv[1] == "script" and len(sys.argv) > 2:
            asyncio.run(AICLI.run_script(Path(sys.argv[2])))
        else:
            print("Usage: ai_interactible_tui.py [test|script <file>]")
    else:
        asyncio.run(AICLI.run_interactive())
