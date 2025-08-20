"""
from typing import Optional
🌟 Enhanced Nix for Humanity TUI with Advanced Error Handling

Builds on the main app with:
- Comprehensive error handling and recovery
- Error notification system
- Guided error resolution
- Error history and reporting
"""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, Button
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.reactive import reactive
from textual.binding import Binding
from textual.message import Message
from textual.notifications import Notification, SeverityLevel
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich.console import Console
from rich.table import Table
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from .consciousness_orb import ConsciousnessOrb, AIState, EmotionalState
from .adaptive_interface import AdaptiveInterface, UserFlowState, ComplexityLevel
from .visual_state_controller import VisualStateController
from .error_handler import TUIErrorHandler, EnhancedError, ErrorSeverity
from .error_recovery import ErrorRecovery, RecoveryPlan
from ..core.engine import NixForHumanityBackend
from ..api.schema import Request, Context

logger = logging.getLogger(__name__)


class ErrorNotification(Notification):
    """Custom error notification"""
    
    def __init__(self, error: EnhancedError):
        # Map our severity to Textual severity
        severity_map = {
            ErrorSeverity.INFO: SeverityLevel.INFORMATION,
            ErrorSeverity.WARNING: SeverityLevel.WARNING,
            ErrorSeverity.ERROR: SeverityLevel.ERROR,
            ErrorSeverity.CRITICAL: SeverityLevel.ERROR
        }
        
        super().__init__(
            title=f"Error: {error.category.value.title()}",
            message=error.message,
            severity=severity_map.get(error.severity, SeverityLevel.ERROR)
        )
        self.error = error


class ErrorPanel(Static):
    """Panel showing current error with recovery options"""
    
    def __init__(self, error: EnhancedError, recovery_plan: Optional[RecoveryPlan] = None):
        self.error = error
        self.recovery_plan = recovery_plan
        super().__init__()
        
    def render(self) -> Panel:
        """Render error panel"""
        console = Console()
        
        # Create content
        content = Text()
        
        # Error message
        severity_colors = {
            ErrorSeverity.INFO: "blue",
            ErrorSeverity.WARNING: "yellow",
            ErrorSeverity.ERROR: "red",
            ErrorSeverity.CRITICAL: "bold red"
        }
        
        color = severity_colors.get(self.error.severity, "red")
        content.append(self.error.message, style=color)
        content.append("\n\n")
        
        # Solutions
        if self.error.solutions:
            content.append("💡 Suggested Solutions:\n", style="bold")
            for i, solution in enumerate(self.error.solutions, 1):
                content.append(f"{i}. {solution.description}\n", style="cyan")
                if solution.command:
                    content.append(f"   → {solution.command}\n", style="dim")
                    
        # Recovery options
        if self.recovery_plan:
            content.append("\n🔧 Recovery Options:\n", style="bold")
            for action in self.recovery_plan.actions[:3]:  # Show top 3
                content.append(f"• {action.description}\n", style="green")
                
        # Error code
        if self.error.error_code:
            content.append(f"\nError Code: {self.error.error_code}", style="dim")
            
        return Panel(
            content,
            title="⚠️ Error Detected",
            border_style=color,
            expand=False
        )


class ConversationMessage(Static):
    """Enhanced conversation message with error indicators"""
    
    def __init__(self, 
                 text: str, 
                 is_user: bool = True, 
                 timestamp: Optional[datetime] = None,
                 has_error: bool = False,
                 error: Optional[EnhancedError] = None):
        self.text = text
        self.is_user = is_user
        self.timestamp = timestamp or datetime.now()
        self.has_error = has_error
        self.error = error
        super().__init__()
        
    def render(self) -> Text:
        """Render the message"""
        time_str = self.timestamp.strftime("%H:%M")
        
        if self.is_user:
            style = "bold white" if not self.has_error else "bold red"
            prefix = "→ You:"
        else:
            style = "cyan" if not self.has_error else "yellow"
            prefix = "← Nix:"
            
        text = Text(f"[{time_str}] {prefix} {self.text}", style=style)
        
        # Add error indicator
        if self.has_error and self.error:
            text.append(f" ⚠️", style="red")
            
        return text


class EnhancedNixForHumanityTUI(App):
    """
    Enhanced TUI with comprehensive error handling
    """
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #orb-container {
        height: 15;
        margin: 1;
        border: solid $primary;
    }
    
    #conversation {
        height: 100%;
        margin: 1;
        border: solid $secondary;
        padding: 1;
    }
    
    #error-panel {
        margin: 1;
        height: auto;
        display: none;
    }
    
    #error-panel.visible {
        display: block;
    }
    
    #input-container {
        height: 3;
        margin: 1;
    }
    
    #error-history {
        dock: right;
        width: 40;
        margin: 1;
        border: solid $error;
        display: none;
    }
    
    #error-history.visible {
        display: block;
    }
    
    ConversationMessage {
        margin-bottom: 1;
    }
    
    .error-button {
        margin: 1;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", priority=True),
        Binding("ctrl+z", "toggle_zen", "Zen Mode"),
        Binding("ctrl+d", "toggle_debug", "Debug"),
        Binding("ctrl+e", "toggle_error_history", "Errors"),
        Binding("ctrl+r", "recover", "Recover"),
        Binding("f1", "help", "Help"),
        Binding("tab", "focus_next", "Next", show=False),
        Binding("shift+tab", "focus_previous", "Previous", show=False),
    ]
    
    # App state
    zen_mode = reactive(False)
    debug_mode = reactive(False)
    show_error_history = reactive(False)
    current_error = reactive(None)
    
    def __init__(self, engine: Optional[NixForHumanityBackend] = None):
        super().__init__()
        self.engine = engine or NixForHumanityBackend()
        self.visual_controller = VisualStateController(self.engine)
        self.error_handler = TUIErrorHandler()
        self.error_recovery = ErrorRecovery()
        
        # UI components
        self.orb: Optional[ConsciousnessOrb] = None
        self.adaptive_interface: Optional[AdaptiveInterface] = None
        self.conversation: Optional[ScrollableContainer] = None
        self.error_panel: Optional[Container] = None
        self.error_history_panel: Optional[ScrollableContainer] = None
        
        # State
        self.active_recovery_plan: Optional[RecoveryPlan] = None
        
    def compose(self) -> ComposeResult:
        """Compose the UI"""
        # Header
        yield Header(show_clock=True)
        
        with Horizontal():
            # Main content area
            with Vertical():
                # Consciousness Orb
                with Container(id="orb-container"):
                    self.orb = ConsciousnessOrb()
                    yield self.orb
                    
                # Error panel (hidden by default)
                self.error_panel = Container(id="error-panel")
                yield self.error_panel
                    
                # Conversation history
                self.conversation = ScrollableContainer(id="conversation")
                yield self.conversation
                    
                # Adaptive UI elements
                self.adaptive_interface = AdaptiveInterface()
                yield self.adaptive_interface
                    
                # Input area with error recovery button
                with Horizontal(id="input-container"):
                    yield Input(
                        placeholder="✨ Ask me anything... (or type 'help')",
                        id="main-input"
                    )
                    yield Button("🔧 Recover", id="recover-button", classes="error-button", disabled=True)
                    
            # Error history panel (hidden by default)
            self.error_history_panel = ScrollableContainer(id="error-history")
            yield self.error_history_panel
        
        # Footer
        yield Footer()
        
    def on_mount(self) -> None:
        """Initialize when mounted"""
        # Subscribe visual controller to orb updates
        self.visual_controller.subscribe(self._update_orb_state)
        
        # Start the visual state sync
        self.set_interval(0.1, self._sync_visual_state)
        
        # Focus on input
        self.query_one("#main-input", Input).focus()
        
        # Welcome message
        self.add_ai_message(
            "👋 Welcome to Nix for Humanity! I'm your AI partner for NixOS. "
            "What would you like to do today?"
        )
        
        # Set initial orb state
        self.orb.set_state(AIState.IDLE, EmotionalState.HAPPY)
        
    async def _sync_visual_state(self) -> None:
        """Sync visual state with engine"""
        if hasattr(self.engine, 'get_current_state'):
            state = self.engine.get_current_state()
            self.visual_controller.update_from_engine(state)
            
    def _update_orb_state(self, visual_state) -> None:
        """Update orb based on visual state"""
        if self.orb:
            ai_state_map = {
                'idle': AIState.IDLE,
                'listening': AIState.LISTENING,
                'processing': AIState.THINKING,
                'responding': AIState.SPEAKING,
                'learning': AIState.LEARNING,
                'error': AIState.ERROR
            }
            
            emotion_map = {
                'neutral': EmotionalState.NEUTRAL,
                'thinking': EmotionalState.THINKING,
                'happy': EmotionalState.HAPPY,
                'concerned': EmotionalState.CONCERNED,
                'confused': EmotionalState.CONFUSED,
                'curious': EmotionalState.LEARNING,
                'confident': EmotionalState.FLOW
            }
            
            ai_state = ai_state_map.get(visual_state.ai_state, AIState.IDLE)
            emotion = emotion_map.get(visual_state.ai_emotion, EmotionalState.NEUTRAL)
            
            self.orb.set_state(ai_state, emotion)
            self.orb.attention_level = visual_state.emotion_intensity
            
    def add_user_message(self, text: str, has_error: bool = False) -> None:
        """Add user message to conversation"""
        if self.conversation:
            msg = ConversationMessage(text, is_user=True, has_error=has_error)
            self.conversation.mount(msg)
            self.conversation.scroll_end(animate=True)
            
    def add_ai_message(self, text: str, has_error: bool = False, error: Optional[EnhancedError] = None) -> None:
        """Add AI message to conversation"""
        if self.conversation:
            msg = ConversationMessage(text, is_user=False, has_error=has_error, error=error)
            self.conversation.mount(msg)
            self.conversation.scroll_end(animate=True)
            
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission"""
        user_input = event.value.strip()
        if not user_input:
            return
            
        # Clear input
        event.input.value = ""
        
        # Add to conversation
        self.add_user_message(user_input)
        
        # Update orb to listening
        self.orb.set_state(AIState.LISTENING, EmotionalState.ATTENTIVE)
        
        # Process input
        await self.process_user_input(user_input)
        
    async def process_user_input(self, user_input: str) -> None:
        """Process user input with error handling"""
        # Show thinking state
        self.orb.set_state(AIState.THINKING, EmotionalState.THINKING)
        
        try:
            # Check for special commands
            if user_input.lower() == 'errors':
                await self.show_error_summary()
                return
            elif user_input.lower() == 'clear errors':
                self.clear_errors()
                return
            elif user_input.lower() == 'export errors':
                await self.export_error_report()
                return
                
            # Process through backend
            request = Request(
                query=user_input,
                context=Context(
                    personality="friendly",
                    execute=False,
                    dry_run=True
                )
            )
            
            response = self.engine.process(request)
            
            # Show response
            self.orb.set_state(AIState.SPEAKING, EmotionalState.HAPPY)
            
            if response.success:
                self.add_ai_message(response.text)
                
                if response.commands:
                    commands_text = "\n\n📋 Commands I would run:\n"
                    for cmd in response.commands:
                        commands_text += f"  • `{cmd['command']}`\n"
                    self.add_ai_message(commands_text)
                    
                # Hide error panel if showing
                self.hide_error_panel()
                    
            else:
                # Handle error
                await self.handle_error(
                    Exception(response.error or "Unknown error"),
                    "process_user_input",
                    user_input
                )
                
        except Exception as e:
            # Handle unexpected errors
            await self.handle_error(e, "process_user_input", user_input)
            
        # Return to idle
        await asyncio.sleep(0.5)
        self.orb.set_state(AIState.IDLE, EmotionalState.NEUTRAL)
        
    async def handle_error(self, error: Exception, component: str, user_input: Optional[str] = None) -> None:
        """Handle errors with recovery options"""
        # Create enhanced error
        enhanced_error = self.error_handler.handle_error(
            error=error,
            component=component,
            operation="user_command",
            user_input=user_input
        )
        
        # Update orb state
        emotion_map = {
            ErrorSeverity.INFO: EmotionalState.NEUTRAL,
            ErrorSeverity.WARNING: EmotionalState.CONCERNED,
            ErrorSeverity.ERROR: EmotionalState.CONFUSED,
            ErrorSeverity.CRITICAL: EmotionalState.CONCERNED
        }
        
        self.orb.set_state(AIState.ERROR, emotion_map.get(enhanced_error.severity, EmotionalState.CONFUSED))
        
        # Show error notification
        if enhanced_error.severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
            self.notify(ErrorNotification(enhanced_error))
            
        # Display error in conversation
        error_text = self.error_handler.format_error_for_display(enhanced_error, verbose=self.debug_mode)
        self.add_ai_message(error_text, has_error=True, error=enhanced_error)
        
        # Create recovery plan
        recovery_plan = await self.error_recovery.create_recovery_plan(enhanced_error)
        self.active_recovery_plan = recovery_plan
        
        # Show error panel with recovery options
        self.show_error_panel(enhanced_error, recovery_plan)
        
        # Enable recover button
        recover_button = self.query_one("#recover-button", Button)
        recover_button.disabled = False
        
        # Update error history
        self.update_error_history()
        
    def show_error_panel(self, error: EnhancedError, recovery_plan: RecoveryPlan) -> None:
        """Show error panel with recovery options"""
        self.current_error = error
        
        # Clear and populate error panel
        self.error_panel.remove_children()
        error_display = ErrorPanel(error, recovery_plan)
        self.error_panel.mount(error_display)
        
        # Show panel
        self.error_panel.add_class("visible")
        
    def hide_error_panel(self) -> None:
        """Hide error panel"""
        self.error_panel.remove_class("visible")
        self.current_error = None
        
        # Disable recover button
        recover_button = self.query_one("#recover-button", Button)
        recover_button.disabled = True
        
    async def show_error_summary(self) -> None:
        """Show error summary"""
        summary = self.error_handler.get_error_summary()
        self.add_ai_message(summary)
        
    def clear_errors(self) -> None:
        """Clear error history"""
        self.error_handler.clear_history()
        self.hide_error_panel()
        self.update_error_history()
        self.add_ai_message("✅ Error history cleared.")
        
    async def export_error_report(self) -> None:
        """Export error report"""
        report_path = self.error_handler.export_error_report()
        self.add_ai_message(f"📄 Error report exported to: {report_path}")
        
    def update_error_history(self) -> None:
        """Update error history panel"""
        if not self.error_history_panel:
            return
            
        # Clear panel
        self.error_history_panel.remove_children()
        
        # Add title
        title = Static("📋 Error History", classes="error-history-title")
        self.error_history_panel.mount(title)
        
        # Add recent errors
        for error in self.error_handler.error_history[-10:]:
            time_str = error.context.timestamp.strftime("%H:%M:%S")
            error_line = Static(
                f"[{time_str}] {error.category.value}: {error.message[:30]}...",
                classes="error-history-item"
            )
            self.error_history_panel.mount(error_line)
            
    def action_toggle_error_history(self) -> None:
        """Toggle error history panel"""
        self.show_error_history = not self.show_error_history
        
        if self.show_error_history:
            self.error_history_panel.add_class("visible")
            self.update_error_history()
        else:
            self.error_history_panel.remove_class("visible")
            
    async def action_recover(self) -> None:
        """Execute recovery plan"""
        if not self.active_recovery_plan:
            return
            
        self.add_ai_message("🔧 Executing recovery plan...")
        
        # Progress callback
        async def progress(message: str, current: int, total: int):
            self.add_ai_message(f"  {message} ({current}/{total})")
            
        # Execute recovery
        success = await self.error_recovery.execute_recovery_plan(
            self.active_recovery_plan,
            progress_callback=progress
        )
        
        if success:
            self.add_ai_message("✅ Recovery successful!")
            self.hide_error_panel()
            self.orb.set_state(AIState.IDLE, EmotionalState.HAPPY)
        else:
            self.add_ai_message("❌ Recovery failed. Try manual recovery or ask for help.")
            self.orb.set_state(AIState.ERROR, EmotionalState.CONCERNED)
            
        self.active_recovery_plan = None
        
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "recover-button":
            await self.action_recover()
            
    def action_toggle_zen(self) -> None:
        """Toggle zen mode"""
        self.zen_mode = not self.zen_mode
        
        if self.zen_mode:
            self.adaptive_interface.user_flow_state = UserFlowState.DEEP_FOCUS
            self.adaptive_interface.complexity_level = ComplexityLevel.ZEN
            self.add_ai_message("🧘 Zen mode activated. Minimal distractions.")
            # Hide error panels in zen mode
            self.hide_error_panel()
            self.error_history_panel.remove_class("visible")
        else:
            self.adaptive_interface.user_flow_state = UserFlowState.NORMAL
            self.adaptive_interface.complexity_level = ComplexityLevel.FOCUSED
            self.add_ai_message("Returned to normal mode.")
            
    def action_toggle_debug(self) -> None:
        """Toggle debug mode"""
        self.debug_mode = not self.debug_mode
        
        if self.debug_mode:
            self.adaptive_interface.complexity_level = ComplexityLevel.EXPERT
            self.add_ai_message("🔧 Debug mode activated. Verbose error information enabled.")
        else:
            self.adaptive_interface.complexity_level = ComplexityLevel.FOCUSED
            self.add_ai_message("Debug mode deactivated.")


def main():
    """Main entry point for enhanced TUI"""
    app = EnhancedNixForHumanityTUI()
    app.run()


if __name__ == "__main__":
    main()