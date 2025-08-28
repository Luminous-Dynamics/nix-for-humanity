"""
from typing import List, Optional
🎬 Demo Mode for Nix for Humanity TUI

Automated demonstration of all features with scripted interactions.
Perfect for creating videos, GIFs, or live demonstrations.
"""

import asyncio
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

from textual.app import App
from textual import events


@dataclass
class DemoStep:
    """A single step in the demo sequence"""
    action: str  # "type", "key", "wait", "narrate"
    content: str
    duration: float = 0.0
    description: Optional[str] = None


class DemoScript:
    """Manages the demo script execution"""
    
    def __init__(self, app: App):
        self.app = app
        self.current_step = 0
        self.running = False
        self.script: List[DemoStep] = []
        
    def load_showcase_script(self) -> None:
        """Load the full feature showcase script"""
        self.script = [
            # Introduction
            DemoStep("narrate", "🌟 Welcome to Nix for Humanity Enhanced TUI Demo", 3.0,
                    "Introduction"),
            DemoStep("wait", "", 1.0),
            
            # Basic help
            DemoStep("type", "help", 0.1, "Show available commands"),
            DemoStep("key", "enter", 0.5),
            DemoStep("wait", "", 3.0, "Let user read help"),
            
            # Install with particles
            DemoStep("narrate", "✨ Watch the thought particles as we install software", 2.0),
            DemoStep("type", "install firefox", 0.1, "Natural language install"),
            DemoStep("key", "enter", 0.5),
            DemoStep("wait", "", 4.0, "Show particle effects"),
            
            # Voice mode
            DemoStep("narrate", "🎤 Activating voice visualization", 2.0),
            DemoStep("type", "voice on", 0.1),
            DemoStep("key", "enter", 0.5),
            DemoStep("wait", "", 4.0, "Show voice waveforms"),
            
            # Learning mode
            DemoStep("narrate", "🧠 Watch the AI learn from interactions", 2.0),
            DemoStep("type", "learn about nix generations", 0.1),
            DemoStep("key", "enter", 0.5),
            DemoStep("wait", "", 4.0, "Show learning particles"),
            
            # Network status
            DemoStep("narrate", "🌐 Real-time network monitoring", 2.0),
            DemoStep("type", "check network status", 0.1),
            DemoStep("key", "enter", 0.5),
            DemoStep("wait", "", 3.0),
            
            # Build flow state
            DemoStep("narrate", "🌊 Building flow state with multiple commands", 2.0),
            DemoStep("type", "update system", 0.1),
            DemoStep("key", "enter", 0.5),
            DemoStep("wait", "", 2.0),
            
            DemoStep("type", "search text editor", 0.1),
            DemoStep("key", "enter", 0.5),
            DemoStep("wait", "", 2.0),
            
            DemoStep("type", "list installed packages", 0.1),
            DemoStep("key", "enter", 0.5),
            DemoStep("wait", "", 2.0),
            
            DemoStep("type", "show disk usage", 0.1),
            DemoStep("key", "enter", 0.5),
            DemoStep("wait", "", 2.0),
            
            DemoStep("type", "clean cache", 0.1),
            DemoStep("key", "enter", 0.5),
            DemoStep("wait", "", 3.0, "Flow state should activate"),
            
            # Zen mode
            DemoStep("narrate", "🧘 Entering Zen Mode for minimal distraction", 2.0),
            DemoStep("key", "ctrl+z", 0.5),
            DemoStep("wait", "", 3.0, "Show minimal UI"),
            DemoStep("key", "ctrl+z", 0.5),
            DemoStep("wait", "", 2.0, "Return to normal"),
            
            # Advanced features
            DemoStep("narrate", "⚡ Quick actions and sacred metrics", 2.0),
            DemoStep("wait", "", 3.0, "Show right panel features"),
            
            # Finale
            DemoStep("narrate", "✨ Consciousness-first computing in action!", 3.0),
            DemoStep("type", "Thank you for watching!", 0.1),
            DemoStep("key", "enter", 0.5),
            DemoStep("wait", "", 3.0),
            
            DemoStep("narrate", "🌟 Visit github.com/Luminous-Dynamics/nix-for-humanity", 5.0),
        ]
        
    def load_quick_script(self) -> None:
        """Load a quick 30-second demo script"""
        self.script = [
            DemoStep("type", "help", 0.1),
            DemoStep("key", "enter", 0.5),
            DemoStep("wait", "", 2.0),
            
            DemoStep("type", "install firefox", 0.1),
            DemoStep("key", "enter", 0.5),
            DemoStep("wait", "", 3.0),
            
            DemoStep("type", "voice on", 0.1),
            DemoStep("key", "enter", 0.5),
            DemoStep("wait", "", 3.0),
            
            DemoStep("type", "learn about nix", 0.1),
            DemoStep("key", "enter", 0.5),
            DemoStep("wait", "", 3.0),
            
            DemoStep("narrate", "🌟 Nix for Humanity - Making NixOS Accessible", 3.0),
        ]
        
    async def play(self, on_complete: Optional[Callable] = None) -> None:
        """Play the demo script"""
        self.running = True
        self.current_step = 0
        
        try:
            while self.running and self.current_step < len(self.script):
                step = self.script[self.current_step]
                
                # Show description if available
                if step.description:
                    self.app.notify(f"Demo: {step.description}", severity="information")
                
                # Execute the step
                if step.action == "type":
                    await self._type_text(step.content, step.duration)
                elif step.action == "key":
                    await self._press_key(step.content)
                elif step.action == "wait":
                    await asyncio.sleep(step.duration)
                elif step.action == "narrate":
                    await self._show_narration(step.content, step.duration)
                
                self.current_step += 1
                
        except asyncio.CancelledError:
            self.running = False
            
        if on_complete:
            on_complete()
            
    async def _type_text(self, text: str, speed: float) -> None:
        """Simulate typing text character by character"""
        input_widget = self.app.query_one("#command-input")
        
        # Clear existing text
        input_widget.value = ""
        
        # Type character by character
        for char in text:
            if not self.running:
                break
            input_widget.value += char
            input_widget.refresh()
            await asyncio.sleep(speed)
            
    async def _press_key(self, key: str) -> None:
        """Simulate key press"""
        # Map key names to actual keys
        key_map = {
            "enter": events.Key("enter"),
            "ctrl+z": events.Key("ctrl+z"),
            "ctrl+v": events.Key("ctrl+v"),
            "ctrl+d": events.Key("ctrl+d"),
            "ctrl+c": events.Key("ctrl+c"),
            "f1": events.Key("f1"),
        }
        
        if key in key_map:
            await self.app._on_key(key_map[key])
            
    async def _show_narration(self, text: str, duration: float) -> None:
        """Show narration text overlay"""
        # Add to history as system message
        self.app.add_to_history({
            "type": "system",
            "message": text,
            "timestamp": datetime.now()
        })
        
        await asyncio.sleep(duration)
        
    def stop(self) -> None:
        """Stop the demo playback"""
        self.running = False
        

class DemoRecorder:
    """Records user interactions for creating custom demos"""
    
    def __init__(self):
        self.recording = False
        self.actions: List[DemoStep] = []
        self.last_action_time = None
        
    def start_recording(self) -> None:
        """Start recording user actions"""
        self.recording = True
        self.actions = []
        self.last_action_time = datetime.now()
        
    def stop_recording(self) -> List[DemoStep]:
        """Stop recording and return the script"""
        self.recording = False
        return self.actions
        
    def record_action(self, action: str, content: str, description: str = "") -> None:
        """Record a user action"""
        if not self.recording:
            return
            
        # Calculate duration since last action
        now = datetime.now()
        if self.last_action_time:
            duration = (now - self.last_action_time).total_seconds()
        else:
            duration = 0.0
            
        # Add wait step if there was a pause
        if duration > 0.5:
            self.actions.append(DemoStep("wait", "", duration))
            
        # Add the action
        self.actions.append(DemoStep(action, content, 0.1, description))
        self.last_action_time = now
        
    def export_script(self, filename: str) -> None:
        """Export recorded script to a Python file"""
        with open(filename, 'w') as f:
            f.write("# Recorded Demo Script\n")
            f.write("demo_script = [\n")
            for step in self.actions:
                f.write(f"    DemoStep('{step.action}', '{step.content}', "
                       f"{step.duration}, '{step.description}'),\n")
            f.write("]\n")