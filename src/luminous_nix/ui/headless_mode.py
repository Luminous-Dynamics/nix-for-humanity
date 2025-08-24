#!/usr/bin/env python3
"""
Headless/Scriptable mode for the TUI - enables automated testing and scripting.

This allows Claude, CI/CD systems, and users to interact with the TUI programmatically.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import sys
from io import StringIO

class CommandType(Enum):
    """Types of commands that can be sent to the TUI."""
    KEY = "key"           # Single keypress
    TEXT = "text"         # Text input
    WAIT = "wait"         # Wait for condition/time
    ASSERT = "assert"     # Assert state
    SCREENSHOT = "screenshot"  # Capture state

@dataclass
class TUICommand:
    """A single command to execute in the TUI."""
    type: CommandType
    value: Any
    description: Optional[str] = None
    
class HeadlessTUI:
    """
    Headless TUI controller for automated testing and scripting.
    
    This allows programmatic interaction with the TUI without a real terminal.
    """
    
    def __init__(self, record_mode: bool = False):
        """
        Initialize headless TUI controller.
        
        Args:
            record_mode: If True, record user interactions for playback
        """
        self.record_mode = record_mode
        self.recorded_commands: List[TUICommand] = []
        self.app = None
        self.virtual_screen = StringIO()
        self.state = {}
        
    async def initialize(self):
        """Initialize the TUI app in headless mode."""
        from luminous_nix.ui.main_app import NixForHumanityTUI
        
        # Create app with headless flag
        self.app = NixForHumanityTUI(headless=True)
        
        # Override the screen output to capture it
        self.app._driver = MockDriver(self.virtual_screen)
        
        return self
        
    async def execute_command(self, command: TUICommand) -> Dict[str, Any]:
        """
        Execute a single command.
        
        Returns:
            Result of the command execution
        """
        result = {"success": False, "output": None}
        
        if command.type == CommandType.KEY:
            # Simulate keypress
            await self.app.process_key(command.value)
            result["success"] = True
            
        elif command.type == CommandType.TEXT:
            # Simulate text input
            for char in command.value:
                await self.app.process_key(char)
            result["success"] = True
            
        elif command.type == CommandType.WAIT:
            # Wait for condition or time
            await asyncio.sleep(command.value)
            result["success"] = True
            
        elif command.type == CommandType.ASSERT:
            # Assert something about current state
            actual = self.get_state(command.value["property"])
            expected = command.value["expected"]
            result["success"] = actual == expected
            result["actual"] = actual
            result["expected"] = expected
            
        elif command.type == CommandType.SCREENSHOT:
            # Capture current screen state
            result["output"] = self.capture_screen()
            result["success"] = True
            
        if self.record_mode:
            self.recorded_commands.append(command)
            
        return result
        
    async def execute_script(self, script: Union[str, Path, List[TUICommand]]) -> Dict[str, Any]:
        """
        Execute a script of commands.
        
        Args:
            script: Path to script file, JSON string, or list of commands
            
        Returns:
            Results of script execution
        """
        # Parse script
        if isinstance(script, (str, Path)):
            if Path(script).exists():
                with open(script) as f:
                    commands = json.load(f)
            else:
                commands = json.loads(script)
        else:
            commands = script
            
        # Convert to TUICommand objects
        command_objects = []
        for cmd in commands:
            if isinstance(cmd, dict):
                command_objects.append(TUICommand(
                    type=CommandType[cmd["type"].upper()],
                    value=cmd["value"],
                    description=cmd.get("description")
                ))
            else:
                command_objects.append(cmd)
                
        # Execute commands
        results = []
        for i, command in enumerate(command_objects):
            print(f"  [{i+1}/{len(command_objects)}] {command.description or command.type.value}: {command.value}")
            result = await self.execute_command(command)
            results.append(result)
            
            if not result["success"] and command.type == CommandType.ASSERT:
                print(f"    ❌ Assertion failed: {result}")
                break
                
        return {
            "success": all(r["success"] for r in results),
            "results": results,
            "final_screen": self.capture_screen()
        }
        
    def capture_screen(self) -> str:
        """Capture current screen state."""
        return self.virtual_screen.getvalue()
        
    def get_state(self, property: str) -> Any:
        """Get a property from current TUI state."""
        # This would access the actual TUI state
        if hasattr(self.app, property):
            return getattr(self.app, property)
        return self.state.get(property)
        
    def save_recording(self, filepath: str):
        """Save recorded commands to a file."""
        commands = [
            {
                "type": cmd.type.value,
                "value": cmd.value,
                "description": cmd.description
            }
            for cmd in self.recorded_commands
        ]
        
        with open(filepath, 'w') as f:
            json.dump(commands, f, indent=2)
            
    @classmethod
    async def run_test_script(cls, script_path: str) -> bool:
        """
        Convenience method to run a test script.
        
        Returns:
            True if all tests passed
        """
        headless = cls()
        await headless.initialize()
        result = await headless.execute_script(script_path)
        return result["success"]


class MockDriver:
    """Mock driver for capturing TUI output."""
    
    def __init__(self, output_buffer: StringIO):
        self.output = output_buffer
        
    def write(self, text: str):
        """Capture output."""
        self.output.write(text)
        
    def flush(self):
        """Flush output."""
        self.output.flush()


# Example test scripts
EXAMPLE_SEARCH_TEST = [
    {"type": "key", "value": "s", "description": "Open search"},
    {"type": "wait", "value": 0.5, "description": "Wait for search to open"},
    {"type": "text", "value": "firefox", "description": "Type search query"},
    {"type": "key", "value": "enter", "description": "Execute search"},
    {"type": "wait", "value": 1.0, "description": "Wait for results"},
    {"type": "assert", "value": {"property": "search_results_count", "expected": ">0"}, "description": "Assert results found"},
    {"type": "screenshot", "value": None, "description": "Capture final state"}
]

EXAMPLE_INSTALL_TEST = [
    {"type": "key", "value": "s", "description": "Open search"},
    {"type": "text", "value": "vim", "description": "Search for vim"},
    {"type": "key", "value": "enter", "description": "Execute search"},
    {"type": "wait", "value": 1.0, "description": "Wait for results"},
    {"type": "key", "value": "down", "description": "Select first result"},
    {"type": "key", "value": "i", "description": "Install selected package"},
    {"type": "assert", "value": {"property": "install_preview_visible", "expected": True}, "description": "Assert install preview shown"},
    {"type": "key", "value": "y", "description": "Confirm installation"},
    {"type": "wait", "value": 2.0, "description": "Wait for installation"},
    {"type": "assert", "value": {"property": "last_message", "expected": "Installation simulated successfully"}, "description": "Assert success message"}
]


async def demo():
    """Demo the headless TUI capabilities."""
    print("🤖 Headless TUI Demo")
    print("=" * 50)
    
    # Create headless TUI
    headless = HeadlessTUI()
    await headless.initialize()
    
    print("\n📝 Running search test...")
    result = await headless.execute_script(EXAMPLE_SEARCH_TEST)
    
    if result["success"]:
        print("✅ Search test passed!")
    else:
        print("❌ Search test failed")
        
    print("\n📝 Running install test...")  
    result = await headless.execute_script(EXAMPLE_INSTALL_TEST)
    
    if result["success"]:
        print("✅ Install test passed!")
    else:
        print("❌ Install test failed")
        
    print("\n📸 Final screen state:")
    print(result["final_screen"])


if __name__ == "__main__":
    asyncio.run(demo())