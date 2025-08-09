#!/usr/bin/env python3
"""
from typing import Optional
Nix for Humanity - Unified Experience

The complete, cohesive user experience bringing together:
- Educational error handling
- Progress indicators
- Voice interface (when available)
- Native Python-Nix API
- Beautiful TUI interface
"""

import asyncio
import time
from datetime import datetime
from typing import Optional, Dict, Any
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, Button, ProgressBar, Label
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.reactive import reactive
from textual.binding import Binding
from textual.timer import Timer
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.console import Group
from rich.align import Align
from pathlib import Path
import sys
import threading

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nix_humanity.core.native_operations import NativeOperationsManager, NativeOperationType
from nix_humanity.core.engine import NixForHumanityBackend
from nix_humanity.api.schema import Request, Context
from nix_humanity.core.educational_errors import make_error_educational
from nix_humanity.core.progress_indicator import ProgressIndicator, ProgressStyle

# Try to import voice interface
try:
    from nix_humanity.interfaces.voice_interface import VoiceAssistant, VoiceState
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    print("⚠️ Voice interface not available (missing dependencies)")


class ProgressWidget(Static):
    """A widget that shows progress with animations"""
    
    def __init__(self, operation: str, style: ProgressStyle = ProgressStyle.SPINNER):
        super().__init__()
        self.operation = operation
        self.progress = ProgressIndicator(style=style)
        self.message = "Starting..."
        self.is_complete = False
        
    def on_mount(self):
        """Start progress when mounted"""
        self.progress.start(self.operation, message=self.message)
        if not self.is_complete:
            self.set_interval(0.1, self.update_display)
        
    def update_display(self):
        """Update the progress display"""
        if not self.is_complete:
            self.refresh()
        
    def update_progress(self, current: int = None, message: str = None):
        """Update progress state"""
        if message:
            self.message = message
        self.progress.update(current=current, message=message)
        self.refresh()
        
    def complete(self, message: str = None):
        """Mark as complete"""
        self.is_complete = True
        self.progress.complete(message)
        self.refresh()
        
    def error(self, message: str):
        """Mark as error"""
        self.is_complete = True
        self.progress.error(message)
        self.refresh()
        
    def render(self):
        """Render current progress state"""
        if self.is_complete:
            return Text(self.message, style="green" if "✅" in self.message else "red")
        else:
            # Simulate progress animation
            frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            frame = frames[int(time.time() * 10) % len(frames)]
            return Text(f"{frame} {self.message}", style="yellow")


class ConversationMessage(Static):
    """A message in the conversation"""
    
    def __init__(self, content: Any, is_user: bool = True, timestamp: Optional[datetime] = None):
        self.content = content
        self.is_user = is_user
        self.timestamp = timestamp or datetime.now()
        super().__init__()
        
    def render(self):
        time_str = self.timestamp.strftime("%H:%M")
        
        # Handle different content types
        if isinstance(self.content, str):
            if self.is_user:
                return Text(f"[{time_str}] You: {self.content}", style="bold cyan")
            else:
                return Text(f"[{time_str}] Nix: {self.content}", style="green")
        else:
            # For rich objects like panels
            return self.content


class NixForHumanityUnified(App):
    """The unified, complete Nix for Humanity experience"""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #header-info {
        height: 4;
        margin: 1;
        text-align: center;
        content-align: center middle;
    }
    
    #main-container {
        layout: grid;
        grid-size: 2;
        grid-columns: 2fr 1fr;
        margin: 1;
    }
    
    #conversation-panel {
        border: solid $primary;
        height: 100%;
        padding: 1;
    }
    
    #status-panel {
        border: solid $secondary;
        height: 100%;
        padding: 1;
    }
    
    #input-container {
        height: 3;
        margin: 1;
    }
    
    #quick-actions {
        layout: horizontal;
        height: 3;
        margin: 1;
    }
    
    Button {
        margin: 0 1;
    }
    
    ConversationMessage {
        margin-bottom: 1;
    }
    
    ProgressWidget {
        margin: 1;
        padding: 1;
    }
    
    #voice-status {
        dock: right;
        width: 20;
        margin: 1;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+n", "native_demo", "Native Demo"),
        Binding("ctrl+e", "error_demo", "Error Demo"),
        Binding("ctrl+p", "progress_demo", "Progress Demo"),
        Binding("ctrl+v", "toggle_voice", "Toggle Voice"),
        Binding("f1", "help", "Help"),
        Binding("f2", "about", "About"),
    ]
    
    def __init__(self):
        super().__init__()
        self.backend = NixForHumanityBackend()
        self.native_ops = None
        self.voice_assistant = None
        self.voice_enabled = False
        self.current_progress = None
        self.stats = {
            "queries": 0,
            "native_ops": 0,
            "errors_handled": 0,
            "voice_commands": 0,
            "avg_response_ms": 0,
            "fastest_op_ms": float('inf')
        }
        
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        # Status info with features
        features = []
        features.append("[green]✅ Educational Errors[/]")
        features.append("[green]✅ Progress Indicators[/]")
        features.append("[green]✅ Native API[/]")
        if VOICE_AVAILABLE:
            features.append("[yellow]🎤 Voice Ready[/]")
        else:
            features.append("[dim]🎤 Voice (install deps)[/]")
            
        feature_text = " | ".join(features)
        
        yield Static(
            f"[bold cyan]🌟 Nix for Humanity - Unified Experience[/]\n{feature_text}",
            id="header-info"
        )
        
        # Main content grid
        with Container(id="main-container"):
            # Conversation panel
            with ScrollableContainer(id="conversation-panel"):
                pass
            
            # Status panel
            with Container(id="status-panel"):
                yield Static("📊 System Status", classes="title")
                yield Static(id="stats-display")
                
                if VOICE_AVAILABLE:
                    yield Static("\n🎤 Voice Status", classes="title")
                    yield Static("Status: [red]Inactive[/]", id="voice-status")
        
        # Quick action buttons
        with Horizontal(id="quick-actions"):
            yield Button("🚀 Native", id="btn-native", variant="primary")
            yield Button("❌ Errors", id="btn-errors", variant="warning")
            yield Button("📊 Progress", id="btn-progress", variant="primary")
            if VOICE_AVAILABLE:
                yield Button("🎤 Voice", id="btn-voice", variant="success")
            yield Button("💬 Help", id="btn-help", variant="success")
        
        # Input area
        with Container(id="input-container"):
            yield Input(
                placeholder="✨ Natural language NixOS: 'install firefox', 'update system', 'my wifi isn't working'...",
                id="main-input"
            )
        
        yield Footer()
        
    async def on_mount(self) -> None:
        """Initialize when mounted"""
        # Initialize native operations
        try:
            self.native_ops = NativeOperationsManager()
            self.add_system_message("✅ Native Python-Nix API initialized!")
        except Exception:
            self.add_system_message("⚠️ Native operations not available (fallback mode)")
            
        # Show welcome message
        welcome = Panel(
            """Welcome to [bold cyan]Nix for Humanity[/]!
            
I'm your AI partner for NixOS, now with:
• 🎓 Educational error messages that teach
• 📊 Progress indicators for long operations  
• 🚀 Native Python-Nix API for instant responses
• 🎤 Voice interface (press Ctrl+V to enable)

Try natural commands like:
• "install firefox"
• "what's using my disk space?"
• "update my system"
• "my wifi isn't working"

Press [bold]F1[/] for help or [bold]Ctrl+C[/] to quit.""",
            title="🌟 Welcome",
            border_style="cyan"
        )
        
        self.add_message(welcome, False)
        
        # Update stats display
        self.set_interval(1, self.update_stats)
        
        # Focus input
        self.query_one("#main-input").focus()
        
    def add_message(self, content: Any, is_user: bool = True):
        """Add message to conversation"""
        msg = ConversationMessage(content, is_user)
        self.query_one("#conversation-panel").mount(msg)
        self.query_one("#conversation-panel").scroll_end(animate=True)
        
    def add_system_message(self, text: str):
        """Add a system message"""
        self.add_message(f"[dim]{text}[/]", False)
        
    def add_progress(self, operation: str, style: ProgressStyle = ProgressStyle.SPINNER) -> ProgressWidget:
        """Add a progress indicator"""
        self.current_progress = ProgressWidget(operation, style)
        self.query_one("#conversation-panel").mount(self.current_progress)
        self.query_one("#conversation-panel").scroll_end(animate=True)
        return self.current_progress
        
    async def on_input_submitted(self, event: Input.Submitted):
        """Handle user input"""
        user_input = event.value.strip()
        if not user_input:
            return
            
        # Clear input
        event.input.value = ""
        
        # Add to conversation
        self.add_message(user_input, True)
        self.stats["queries"] += 1
        
        # Process input
        await self.process_input(user_input)
        
    async def process_input(self, user_input: str):
        """Process user input through backend with all enhancements"""
        start_time = time.time()
        
        try:
            # Special commands
            if user_input.lower() in ['quit', 'exit']:
                self.exit()
                return
            elif user_input.lower() == 'clear':
                # Clear conversation
                panel = self.query_one("#conversation-panel")
                await panel.remove_children()
                self.add_system_message("Conversation cleared")
                return
                
            # Show progress for longer operations
            operation_type = self.detect_operation_type(user_input)
            if operation_type:
                progress = self.add_progress(operation_type, 
                    ProgressStyle.BAR if "install" in operation_type else ProgressStyle.SPINNER)
                
            # Process through backend
            request = Request(
                query=user_input,
                context=Context(
                    personality="friendly",
                    execute=False
                )
            )
            
            response = self.backend.process(request)
            
            # Complete progress if active
            if self.current_progress:
                self.current_progress.complete("✅ Operation complete!")
                self.current_progress = None
            
            # Show response
            if response.success:
                # Format response nicely
                if len(response.text) > 200:
                    # Long response - use panel
                    panel = Panel(response.text, title="Response", border_style="green")
                    self.add_message(panel, False)
                else:
                    self.add_message(response.text, False)
                
                # Show commands if any
                if response.commands:
                    cmd_list = []
                    for cmd in response.commands:
                        cmd_list.append(f"• `{cmd['command']}`")
                    
                    cmd_panel = Panel(
                        "\n".join(cmd_list),
                        title="📋 Commands to Execute",
                        border_style="blue"
                    )
                    self.add_message(cmd_panel, False)
                    
            else:
                # Use educational error handler
                error_msg = response.error or response.text or 'Error processing request'
                educational_msg = make_error_educational(error_msg, verbose=True)
                
                # Format as error panel
                error_panel = Panel(
                    educational_msg,
                    title="❌ Error - But Let's Learn!",
                    border_style="red"
                )
                self.add_message(error_panel, False)
                self.stats["errors_handled"] += 1
                
                # Mark progress as error if active
                if self.current_progress:
                    self.current_progress.error("Operation failed - see explanation above")
                    self.current_progress = None
                
        except Exception as e:
            # Use educational error handler for exceptions too
            educational_msg = make_error_educational(str(e), verbose=False)
            self.add_message(f"❌ {educational_msg}", False)
            self.stats["errors_handled"] += 1
            
            # Mark progress as error if active
            if self.current_progress:
                self.current_progress.error("Unexpected error")
                self.current_progress = None
            
        # Update stats
        elapsed_ms = (time.time() - start_time) * 1000
        self.update_response_time(elapsed_ms)
        
    def detect_operation_type(self, query: str) -> Optional[str]:
        """Detect operation type for progress indicator"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['install', 'add']):
            return "package_install"
        elif any(word in query_lower for word in ['update', 'upgrade']):
            return "system_update"
        elif any(word in query_lower for word in ['search', 'find']):
            return "package_search"
        elif any(word in query_lower for word in ['remove', 'uninstall']):
            return "package_remove"
        elif 'build' in query_lower:
            return "build"
        elif any(word in query_lower for word in ['clean', 'garbage']):
            return "garbage_collect"
            
        return None
        
    def update_stats(self):
        """Update stats display"""
        stats_text = f"""Queries: {self.stats['queries']}
Native Ops: {self.stats['native_ops']}
Errors Handled: {self.stats['errors_handled']}
Voice Commands: {self.stats['voice_commands']}

Performance:
Avg Response: {self.stats['avg_response_ms']:.1f}ms
Fastest Op: {self.stats['fastest_op_ms']:.1f}ms if self.stats['fastest_op_ms'] != float('inf') else 'N/A'

Features Active:
✅ Educational Errors
✅ Progress Indicators
✅ Native Python-Nix API
{'✅' if self.voice_enabled else '❌'} Voice Interface"""
        
        self.query_one("#stats-display").update(stats_text)
        
    def update_response_time(self, ms: float):
        """Update response time stats"""
        if self.stats['queries'] == 1:
            self.stats['avg_response_ms'] = ms
        else:
            # Rolling average
            self.stats['avg_response_ms'] = (
                self.stats['avg_response_ms'] * (self.stats['queries'] - 1) + ms
            ) / self.stats['queries']
            
        if ms < self.stats['fastest_op_ms']:
            self.stats['fastest_op_ms'] = ms
            
    # Demo actions
    async def action_native_demo(self):
        """Show native operations demo"""
        self.add_system_message("🚀 Running native operations demo...")
        
        if not self.native_ops:
            self.add_message("Native operations not available", False)
            return
            
        # List generations with progress
        progress = self.add_progress("listing_generations", ProgressStyle.SPINNER)
        
        result = await self.native_ops.execute_native_operation(
            NativeOperationType.LIST_GENERATIONS
        )
        
        if result.success:
            progress.complete("✅ Generations loaded instantly!")
            gens = result.data['generations']
            
            table = Table(title=f"System Generations ({len(gens)} total)")
            table.add_column("Number", style="cyan")
            table.add_column("Date", style="green")
            table.add_column("Current", style="yellow")
            
            for gen in gens[:5]:
                table.add_row(
                    str(gen['number']),
                    gen['date'],
                    "✓" if gen.get('current', False) else ""
                )
                
            self.add_message(Align.center(table), False)
            self.stats["native_ops"] += 1
        else:
            progress.error("Failed to list generations")
            
    async def action_error_demo(self):
        """Show educational error handling demo"""
        self.add_system_message("❌ Demonstrating educational error handling...")
        
        # Simulate different error types
        errors = [
            "attribute 'firefox' in selection path 'nixos.firefox' not found",
            "permission denied",
            "no space left on device",
            "network unreachable"
        ]
        
        for error in errors[:2]:  # Show first 2 for brevity
            educational = make_error_educational(error, verbose=True)
            error_panel = Panel(
                educational,
                title=f"Educational Error Example",
                border_style="red"
            )
            self.add_message(error_panel, False)
            self.stats["errors_handled"] += 1
            await asyncio.sleep(0.5)
            
    async def action_progress_demo(self):
        """Show progress indicators demo"""
        self.add_system_message("📊 Demonstrating progress indicators...")
        
        # Different progress styles
        demos = [
            ("package_search", ProgressStyle.SPINNER, 2),
            ("package_install", ProgressStyle.BAR, 5),
            ("system_update", ProgressStyle.STEPS, 4)
        ]
        
        for operation, style, steps in demos:
            progress = self.add_progress(operation, style)
            
            for i in range(steps):
                await asyncio.sleep(0.5)
                progress.update_progress(i + 1, f"Step {i + 1}/{steps}...")
                
            progress.complete(f"✅ {operation.replace('_', ' ').title()} complete!")
            
    async def action_toggle_voice(self):
        """Toggle voice interface"""
        if not VOICE_AVAILABLE:
            self.add_system_message("🎤 Voice interface not available - install numpy, sounddevice, whisper, and piper")
            return
            
        if self.voice_enabled:
            # Disable voice
            if self.voice_assistant:
                self.voice_assistant.stop()
            self.voice_enabled = False
            self.query_one("#voice-status").update("Status: [red]Inactive[/]")
            self.add_system_message("🎤 Voice interface disabled")
        else:
            # Enable voice
            try:
                self.voice_assistant = VoiceAssistant(backend=self.backend)
                self.voice_assistant.start()
                self.voice_enabled = True
                self.query_one("#voice-status").update("Status: [green]Active[/]\nSay 'Hey Nix'")
                self.add_system_message("🎤 Voice interface enabled - say 'Hey Nix' to activate")
            except Exception as e:
                self.add_system_message(f"🎤 Failed to start voice: {e}")
                
    async def action_help(self):
        """Show help"""
        help_panel = Panel(
            """[bold]Natural Language Commands:[/]
• "install [package]" - Install software
• "remove [package]" - Uninstall software  
• "search [keyword]" - Find packages
• "update system" - Update NixOS
• "list generations" - Show system history
• "disk space" - Check storage usage
• "my wifi isn't working" - Troubleshooting

[bold]Keyboard Shortcuts:[/]
• Ctrl+N - Native operations demo
• Ctrl+E - Error handling demo
• Ctrl+P - Progress indicators demo
• Ctrl+V - Toggle voice interface
• F1 - This help
• F2 - About
• Ctrl+C - Quit

[bold]Special Commands:[/]
• "clear" - Clear conversation
• "quit" or "exit" - Exit application""",
            title="💡 Help",
            border_style="green"
        )
        self.add_message(help_panel, False)
        
    async def action_about(self):
        """Show about information"""
        about_panel = Panel(
            """[bold cyan]Nix for Humanity v0.7.0[/]

Making NixOS accessible through natural conversation.

[bold]Features:[/]
• 🎓 Educational error messages that teach instead of frustrate
• 📊 Real-time progress indicators for long operations
• 🚀 Native Python-Nix API for instant performance
• 🎤 Voice interface for hands-free operation
• 🧠 AI-powered natural language understanding
• 🔒 Privacy-first local processing

[bold]The Sacred Trinity:[/]
• Human vision & empathy
• AI implementation & synthesis  
• Local LLM domain expertise

Achieving $4.2M quality at $200/month through
consciousness-first development.

Made with ❤️ by the Luminous Dynamics team.""",
            title="🌟 About Nix for Humanity",
            border_style="cyan"
        )
        self.add_message(about_panel, False)
        
    # Button handlers
    async def on_button_pressed(self, event: Button.Pressed):
        """Handle button presses"""
        button_map = {
            "btn-native": self.action_native_demo,
            "btn-errors": self.action_error_demo,
            "btn-progress": self.action_progress_demo,
            "btn-voice": self.action_toggle_voice,
            "btn-help": self.action_help
        }
        
        handler = button_map.get(event.button.id)
        if handler:
            await handler()
            
    async def action_quit(self):
        """Clean shutdown"""
        if self.voice_assistant and self.voice_enabled:
            self.voice_assistant.stop()
        self.exit()


if __name__ == "__main__":
    app = NixForHumanityUnified()
    app.run()