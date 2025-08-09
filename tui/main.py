#!/usr/bin/env python3
"""
from typing import Dict, List, Optional
🌟 Nix for Humanity - Unified TUI

A single, configurable interface that can toggle between:
- Simple Mode: Clean, focused UI with essential features
- Enhanced Mode: Full visualizations with consciousness orb and metrics

Press Ctrl+E to toggle between modes.
"""

import asyncio
import time
import math
import random
from datetime import datetime
from typing import Optional, Dict, Any, List
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, Button, ProgressBar, Label, ListView, ListItem
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer, VerticalScroll
from textual.reactive import reactive
from textual.binding import Binding
from textual.timer import Timer
from textual.message import Message
from textual import events
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
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
    from tui.voice_widget import create_voice_widget
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    from tui.voice_widget import SimpleVoiceWidget
    def create_voice_widget(enhanced=False):
        return SimpleVoiceWidget()

# Try to import enhanced components (may not exist yet)
try:
    from nix_humanity.ui.enhanced_consciousness_orb import EnhancedConsciousnessOrb, AIState, EmotionalState
    from nix_humanity.ui.visual_state_controller import VisualStateController, ComplexityLevel
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False
    # Define minimal stubs
    class AIState:
        IDLE = "idle"
        LISTENING = "listening"
        THINKING = "thinking"
        FLOW = "flow"
        ERROR = "error"
        LEARNING = "learning"
    
    class EmotionalState:
        NEUTRAL = "neutral"
        HAPPY = "happy"
        THINKING = "thinking"
        CONCERNED = "concerned"
        CONFUSED = "confused"
        ATTENTIVE = "attentive"
        LEARNING = "learning"


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


class SimpleConsciousnessOrb(Static):
    """Simple ASCII art consciousness orb for when enhanced isn't available"""
    
    def __init__(self):
        super().__init__()
        self.state = AIState.IDLE
        self.frame = 0
        
    def on_mount(self):
        self.set_interval(0.1, self.animate)
        
    def animate(self):
        self.frame += 1
        self.refresh()
        
    def set_state(self, ai_state, emotional_state=None):
        self.state = ai_state
        self.refresh()
        
    def render(self):
        # Simple ASCII orb animation
        if self.state == AIState.IDLE:
            frames = ["◯", "○", "◯", "●"]
        elif self.state == AIState.LISTENING:
            frames = ["◐", "◓", "◑", "◒"]
        elif self.state == AIState.THINKING:
            frames = ["◴", "◷", "◶", "◵"]
        elif self.state == AIState.ERROR:
            frames = ["⊗", "⊖", "⊗", "⊖"]
        else:
            frames = ["◉", "◎", "◉", "◎"]
            
        orb = frames[self.frame % len(frames)]
        
        # Create simple orb display
        lines = [
            "     ╭─────╮     ",
            f"     │  {orb}  │     ",
            "     ╰─────╯     ",
            f"    {self.state}    "
        ]
        
        return Text("\n".join(lines), style="cyan", justify="center")


class UnifiedNixForHumanity(App):
    """
    The unified Nix for Humanity TUI experience.
    
    Features:
    - Toggle between Simple and Enhanced modes (Ctrl+E)
    - Educational error handling
    - Progress indicators
    - Voice interface (when available)
    - Native Python-Nix API
    - Optional consciousness orb and metrics
    """
    
    CSS = """
    /* Simple Mode Styles */
    Screen {
        background: $surface;
    }
    
    #header-info {
        height: 3;
        margin: 1;
        text-align: center;
        content-align: center middle;
    }
    
    #main-container {
        layout: horizontal;
        margin: 1;
    }
    
    #conversation-panel {
        border: solid $primary;
        width: 100%;
        padding: 1;
    }
    
    #status-panel {
        border: solid $secondary;
        width: 40;
        padding: 1;
        display: none;
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
    
    ProgressWidget {
        margin: 1;
        padding: 1;
    }
    
    /* Enhanced Mode Styles */
    #orb-container {
        height: 12;
        border: none;
        align: center middle;
        display: none;
    }
    
    #performance-display {
        height: 8;
        border: solid green;
        padding: 1;
        margin: 1;
        display: none;
    }
    
    #sacred-metrics {
        height: 10;
        border: solid $accent;
        padding: 1;
        display: none;
    }
    
    .enhanced-visible {
        display: block !important;
    }
    
    .conversation-message {
        margin-bottom: 1;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+e", "toggle_enhanced", "Toggle Enhanced"),
        Binding("ctrl+n", "native_demo", "Native Demo"),
        Binding("ctrl+p", "progress_demo", "Progress Demo"),
        Binding("ctrl+v", "toggle_voice", "Toggle Voice"),
        Binding("ctrl+l", "clear_conversation", "Clear"),
        Binding("f1", "help", "Help"),
        Binding("f2", "about", "About"),
    ]
    
    # Reactive state
    enhanced_mode = reactive(False)
    voice_enabled = reactive(False)
    
    def __init__(self):
        super().__init__()
        self.backend = NixForHumanityBackend()
        self.native_ops = None
        self.voice_assistant = None
        self.current_progress = None
        self.command_history: List[Dict[str, Any]] = []
        self.stats = {
            "queries": 0,
            "native_ops": 0,
            "errors_handled": 0,
            "voice_commands": 0,
            "avg_response_ms": 0,
            "fastest_op_ms": float('inf')
        }
        
        # Enhanced mode components
        self.orb = None
        self.visual_controller = VisualStateController() if ENHANCED_AVAILABLE else None
        self.voice_widget = None
        
        # Enhanced metrics
        self.network_connected = True
        self.network_latency = 20.0
        self.learning_progress = 0.1
        self.flow_score = 0.0
        
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        # Status header
        yield Static(
            "[bold cyan]🌟 Nix for Humanity[/] - Natural Language NixOS",
            id="header-info"
        )
        
        # Main content area
        with Container(id="main-container"):
            # Left side - conversation and main UI
            with Vertical(classes="main-content"):
                # Enhanced mode: consciousness orb
                with Container(id="orb-container"):
                    if ENHANCED_AVAILABLE:
                        self.orb = EnhancedConsciousnessOrb()
                    else:
                        self.orb = SimpleConsciousnessOrb()
                    yield self.orb
                
                # Enhanced mode: performance metrics
                with Container(id="performance-display"):
                    yield Label("⚡ Performance Metrics", classes="title")
                    yield Static(id="perf-metrics")
                
                # Conversation panel
                with ScrollableContainer(id="conversation-panel"):
                    pass
                
                # Enhanced mode: sacred metrics
                with Container(id="sacred-metrics"):
                    yield Label("✨ Sacred Metrics", classes="title")
                    yield Static(id="metrics-display")
            
            # Right side - status panel (always present but hidden in simple mode)
            with Container(id="status-panel"):
                yield Static("📊 System Status", classes="title")
                yield Static(id="stats-display")
                
                # Voice widget
                if VOICE_AVAILABLE:
                    yield Static("\n🎤 Voice Interface", classes="title")
                    self.voice_widget = create_voice_widget(self.enhanced_mode)
                    yield self.voice_widget
        
        # Quick action buttons
        with Horizontal(id="quick-actions"):
            yield Button("🚀 Native", id="btn-native", variant="primary")
            yield Button("📊 Progress", id="btn-progress", variant="primary")
            if VOICE_AVAILABLE:
                yield Button("🎤 Voice", id="btn-voice", variant="success")
            yield Button("💡 Enhanced", id="btn-enhanced", variant="warning")
            yield Button("💬 Help", id="btn-help", variant="success")
        
        # Input area
        with Container(id="input-container"):
            yield Input(
                placeholder="✨ Ask me anything: 'install firefox', 'update system', 'my wifi isn't working'...",
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
        self.show_welcome()
        
        # Start update timers
        self.set_interval(1, self.update_stats)
        
        if self.enhanced_mode:
            self.set_interval(1.0, self.update_enhanced_metrics)
            self.set_interval(0.1, self.update_voice_visualization)
            
        # Focus input
        self.query_one("#main-input").focus()
        
    def show_welcome(self):
        """Show welcome message appropriate to mode"""
        if self.enhanced_mode:
            welcome = Panel(
                """Welcome to [bold cyan]Nix for Humanity Enhanced Mode[/]! 🌟

Features active:
• 🎭 Consciousness Orb visualization
• 📊 Real-time performance metrics
• ✨ Sacred metrics and flow state
• 🎓 Educational error messages
• 📈 Progress indicators
• 🚀 Native Python-Nix API

Press [bold]Ctrl+E[/] to toggle back to simple mode.
Press [bold]F1[/] for help.""",
                title="🌟 Enhanced Mode Active",
                border_style="cyan"
            )
        else:
            welcome = Panel(
                """Welcome to [bold cyan]Nix for Humanity[/]!

I'm your AI partner for NixOS. Try natural commands like:
• "install firefox"
• "what's using my disk space?"
• "update my system"
• "my wifi isn't working"

Press [bold]Ctrl+E[/] for enhanced visualizations.
Press [bold]F1[/] for help or [bold]Ctrl+C[/] to quit.""",
                title="🌟 Welcome",
                border_style="cyan"
            )
        
        self.add_message(welcome, False)
        
    def add_message(self, content: Any, is_user: bool = True, timestamp: Optional[datetime] = None):
        """Add message to conversation"""
        timestamp = timestamp or datetime.now()
        time_str = timestamp.strftime("%H:%M")
        
        # Create message widget
        if isinstance(content, str):
            if is_user:
                msg = Static(f"[{time_str}] You: {content}", classes="conversation-message user-message")
                msg.styles.color = "cyan"
                msg.styles.text_style = "bold"
            else:
                msg = Static(f"[{time_str}] Nix: {content}", classes="conversation-message")
                msg.styles.color = "green"
        else:
            # Rich content like panels
            msg = Static(content, classes="conversation-message")
            
        # Add to conversation
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
        
        # Add to conversation and history
        self.add_message(user_input, True)
        self.stats["queries"] += 1
        self.command_history.append({
            "type": "user",
            "message": user_input,
            "timestamp": datetime.now()
        })
        
        # Update orb state if in enhanced mode
        if self.enhanced_mode and self.orb:
            self.orb.set_state(AIState.LISTENING, EmotionalState.ATTENTIVE)
            await asyncio.sleep(0.5)
            self.orb.set_state(AIState.THINKING, EmotionalState.THINKING)
        
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
                await self.action_clear_conversation()
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
            
            # Update orb for success/failure
            if self.enhanced_mode and self.orb:
                if response.success:
                    self.orb.set_state(AIState.IDLE, EmotionalState.HAPPY)
                else:
                    self.orb.set_state(AIState.ERROR, EmotionalState.CONCERNED)
            
            # Show response
            if response.success:
                # Format response nicely
                if len(response.text) > 200:
                    # Long response - use panel
                    panel = Panel(response.text, title="Response", border_style="green")
                    self.add_message(panel, False)
                else:
                    self.add_message(response.text, False)
                
                # Add to history
                self.command_history.append({
                    "type": "assistant",
                    "message": response.text,
                    "success": True,
                    "timestamp": datetime.now()
                })
                
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
                
                # Add to history
                self.command_history.append({
                    "type": "assistant",
                    "message": error_msg,
                    "success": False,
                    "timestamp": datetime.now()
                })
                
                # Mark progress as error if active
                if self.current_progress:
                    self.current_progress.error("Operation failed - see explanation above")
                    self.current_progress = None
                
        except Exception as e:
            # Use educational error handler for exceptions too
            educational_msg = make_error_educational(str(e), verbose=False)
            self.add_message(f"❌ {educational_msg}", False)
            self.stats["errors_handled"] += 1
            
            # Update orb for error
            if self.enhanced_mode and self.orb:
                self.orb.set_state(AIState.ERROR, EmotionalState.CONFUSED)
            
            # Mark progress as error if active
            if self.current_progress:
                self.current_progress.error("Unexpected error")
                self.current_progress = None
            
        # Update stats
        elapsed_ms = (time.time() - start_time) * 1000
        self.update_response_time(elapsed_ms)
        
        # Update performance display if in enhanced mode
        if self.enhanced_mode:
            operation_name = self.detect_operation_type(user_input) or "Operation"
            if elapsed_ms < 100:
                self.add_system_message(f"⚡ INSTANT! {operation_name} completed in {elapsed_ms:.0f}ms")
        
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
        elif 'generation' in query_lower:
            return "list_generations"
        elif 'rollback' in query_lower:
            return "rollback"
            
        return None
        
    def update_stats(self):
        """Update stats display"""
        stats_text = f"""Queries: {self.stats['queries']}
Native Ops: {self.stats['native_ops']}
Errors Handled: {self.stats['errors_handled']}
Voice Commands: {self.stats['voice_commands']}

Performance:
Avg: {self.stats['avg_response_ms']:.1f}ms
Best: {self.stats['fastest_op_ms']:.1f}ms if self.stats['fastest_op_ms'] != float('inf') else 'N/A'

Features:
✅ Educational Errors
✅ Progress Indicators
✅ Native API
{'✅' if self.voice_enabled else '❌'} Voice
{'✅' if self.enhanced_mode else '❌'} Enhanced Mode"""
        
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
            
    async def update_enhanced_metrics(self):
        """Update enhanced mode metrics"""
        if not self.enhanced_mode:
            return
            
        # Update performance metrics
        perf_text = Text()
        if hasattr(self, 'operation_times') and self.operation_times:
            perf_text.append("Recent Operations:\n", style="bold")
            for op, time_taken in list(self.operation_times.items())[-5:]:
                if time_taken < 0.1:
                    perf_text.append(f"  {op}: INSTANT! ", style="cyan bold")
                    perf_text.append(f"({time_taken*1000:.0f}ms)\n", style="dim")
                else:
                    perf_text.append(f"  {op}: {time_taken:.2f}s\n", style="green")
                    
        # Native API status
        if self.native_ops:
            perf_text.append("\n🚀 Native API: ", style="bold")
            perf_text.append("CONNECTED\n", style="green bold")
        else:
            perf_text.append("\n⚠️  Native API: ", style="bold")
            perf_text.append("Fallback mode\n", style="yellow")
            
        self.query_one("#perf-metrics").update(perf_text)
        
        # Update sacred metrics
        metrics_text = Text()
        
        # Calculate flow score based on recent command success
        recent_successes = sum(1 for cmd in self.command_history[-10:]
                             if cmd.get("type") == "assistant" and cmd.get("success"))
        self.flow_score = min(1.0, recent_successes * 0.15)
        
        metrics_text.append("Flow Score: ", style="bold")
        metrics_text.append(f"{self.flow_score:.0%}\n", style="green" if self.flow_score > 0.7 else "yellow")
        
        metrics_text.append("Commands: ", style="bold")
        metrics_text.append(f"{len(self.command_history)}\n", style="magenta")
        
        metrics_text.append("Learning: ", style="bold")
        metrics_text.append(f"{self.learning_progress:.0%}\n", style="cyan")
        
        self.query_one("#metrics-display").update(metrics_text)
        
    async def update_voice_visualization(self):
        """Update voice visualization in enhanced mode"""
        if self.voice_widget and self.voice_enabled and VOICE_AVAILABLE:
            # Simulate audio level for demo (in real use, this would come from audio input)
            if hasattr(self.voice_widget, 'set_audio_level'):
                import random
                if self.voice_assistant and hasattr(self.voice_assistant, 'interface'):
                    # Get actual voice state
                    state = self.voice_assistant.interface.current_state
                    if state == VoiceState.LISTENING:
                        # Simulate varying audio levels
                        level = random.uniform(0.1, 0.8)
                        self.voice_widget.set_audio_level(level)
                    elif state == VoiceState.SPEAKING:
                        # Simulate speech output levels
                        level = random.uniform(0.3, 0.9)
                        self.voice_widget.set_audio_level(level)
                    else:
                        # No audio
                        self.voice_widget.set_audio_level(0.0)
            
    # Action handlers
    async def action_toggle_enhanced(self):
        """Toggle between simple and enhanced modes"""
        self.enhanced_mode = not self.enhanced_mode
        
        # Toggle visibility of enhanced elements
        elements = ["#orb-container", "#performance-display", "#sacred-metrics", "#status-panel"]
        for element_id in elements:
            element = self.query_one(element_id)
            if self.enhanced_mode:
                element.add_class("enhanced-visible")
                element.display = True
            else:
                element.remove_class("enhanced-visible")
                element.display = False
        
        # Adjust conversation panel width
        if self.enhanced_mode:
            self.query_one("#conversation-panel").styles.width = "auto"
            # Start enhanced timers
            self.set_interval(1.0, self.update_enhanced_metrics)
            self.add_system_message("✨ Enhanced mode activated - consciousness orb and metrics enabled")
        else:
            self.query_one("#conversation-panel").styles.width = "100%"
            self.add_system_message("💫 Simple mode activated - clean, focused interface")
            
        # Show appropriate welcome
        self.show_welcome()
        
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
            if self.voice_widget:
                self.voice_widget.set_active(False)
            self.add_system_message("🎤 Voice interface disabled")
        else:
            # Enable voice
            try:
                # Import enhanced interface if available
                try:
                    from nix_humanity.interfaces.voice_interface_enhanced import VoiceAssistant as EnhancedVoiceAssistant
                    assistant_class = EnhancedVoiceAssistant
                except ImportError:
                    assistant_class = VoiceAssistant
                
                # Create voice assistant with state callback
                self.voice_assistant = assistant_class(backend=self.backend)
                
                # Set up state callback if we have a voice widget
                if self.voice_widget and hasattr(self.voice_widget, 'set_voice_state'):
                    def on_voice_state_change(state):
                        self.voice_widget.set_voice_state(state)
                    
                    # Use enhanced interface if available
                    if hasattr(self.voice_assistant, 'interface'):
                        self.voice_assistant.interface.state_callback = on_voice_state_change
                
                self.voice_assistant.start()
                self.voice_enabled = True
                
                if self.voice_widget:
                    self.voice_widget.set_active(True)
                    
                self.add_system_message("🎤 Voice interface enabled - say 'Hey Nix' to activate")
            except Exception as e:
                self.add_system_message(f"🎤 Failed to start voice: {e}")
                
    async def action_clear_conversation(self):
        """Clear conversation history"""
        panel = self.query_one("#conversation-panel")
        await panel.remove_children()
        self.add_system_message("Conversation cleared")
        
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
• Ctrl+E - Toggle enhanced mode
• Ctrl+N - Native operations demo
• Ctrl+P - Progress indicators demo
• Ctrl+V - Toggle voice interface
• Ctrl+L - Clear conversation
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

[bold]Current Mode:[/] """ + ("Enhanced ✨" if self.enhanced_mode else "Simple 💫") + """

[bold]Features:[/]
• 🎓 Educational error messages
• 📊 Real-time progress indicators
• 🚀 Native Python-Nix API
• 🎤 Voice interface support
• 🧠 AI-powered understanding
• 🔒 Privacy-first local processing

Press Ctrl+E to toggle modes.

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
            "btn-progress": self.action_progress_demo,
            "btn-voice": self.action_toggle_voice,
            "btn-enhanced": self.action_toggle_enhanced,
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
    app = UnifiedNixForHumanity()
    app.run()