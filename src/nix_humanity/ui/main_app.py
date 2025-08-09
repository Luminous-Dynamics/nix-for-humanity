"""
from typing import Optional
🌟 Nix for Humanity TUI - The Main Application

A consciousness-first terminal interface that embodies our AI partner
through beautiful visual presence and adaptive complexity.
"""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.reactive import reactive
from textual.binding import Binding
from textual.message import Message
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
import asyncio
from typing import Optional, List
from datetime import datetime

from .consciousness_orb import ConsciousnessOrb, AIState, EmotionalState
from .adaptive_interface import AdaptiveInterface, UserFlowState, ComplexityLevel
from .visual_state_controller import VisualStateController
from ..core.engine import NixForHumanityBackend
from ..api.schema import Request, Context
from nix_humanity.core.advanced_features import AdvancedFeatures
from nix_humanity.core.native_operations import NativeOperationsManager, NativeOperationType


class ConversationMessage(Static):
    """A single message in the conversation"""
    
    def __init__(self, text: str, is_user: bool = True, timestamp: Optional[datetime] = None):
        self.text = text
        self.is_user = is_user
        self.timestamp = timestamp or datetime.now()
        super().__init__()
        
    def render(self) -> Text:
        """Render the message"""
        time_str = self.timestamp.strftime("%H:%M")
        
        if self.is_user:
            return Text(f"[{time_str}] → You: {self.text}", style="bold white")
        else:
            return Text(f"[{time_str}] ← Nix: {self.text}", style="cyan")


class ConversationPanel(ScrollableContainer):
    """Scrollable conversation history"""
    
    def add_message(self, text: str, is_user: bool = True) -> None:
        """Add a message to the conversation"""
        message = ConversationMessage(text, is_user)
        self.mount(message)
        
        # Auto-scroll to bottom
        self.scroll_end(animate=True)


class NixForHumanityTUI(App):
    """
    Main TUI Application - A living, breathing interface for NixOS.
    
    Features:
    - Consciousness Orb showing AI presence
    - Adaptive interface complexity
    - Natural conversation flow
    - Beautiful animations
    - Flow state protection
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
    
    #input-container {
        height: 3;
        margin: 1;
    }
    
    ConversationMessage {
        margin-bottom: 1;
    }
    
    .hidden {
        display: none;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", priority=True),
        Binding("ctrl+z", "toggle_zen", "Zen Mode"),
        Binding("ctrl+d", "toggle_debug", "Debug"),
        Binding("f1", "help", "Help"),
        Binding("tab", "focus_next", "Next", show=False),
        Binding("shift+tab", "focus_previous", "Previous", show=False),
    ]
    
    # App state
    zen_mode = reactive(False)
    debug_mode = reactive(False)
    
    def __init__(self, engine: Optional[NixForHumanityBackend] = None):
        super().__init__()
        self.engine = engine or NixForHumanityBackend()
        self.visual_controller = VisualStateController(self.engine)
        self.orb: Optional[ConsciousnessOrb] = None
        self.adaptive_interface: Optional[AdaptiveInterface] = None
        self.conversation: Optional[ConversationPanel] = None
        
    def compose(self) -> ComposeResult:
        """Compose the UI"""
        # Header
        yield Header(show_clock=True)
        
        # Main content area
        with Vertical():
            # Consciousness Orb
            with Container(id="orb-container"):
                self.orb = ConsciousnessOrb()
                yield self.orb
                
            # Adaptive interface container
            with Container(id="interface-container"):
                # Conversation history
                self.conversation = ConversationPanel(id="conversation")
                yield self.conversation
                
                # Adaptive UI elements
                self.adaptive_interface = AdaptiveInterface()
                yield self.adaptive_interface
                
            # Input area
            with Container(id="input-container"):
                yield Input(
                    placeholder="✨ Ask me anything... (or type 'help')",
                    id="main-input"
                )
        
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
        # This would normally get real state from engine
        # For now, we'll simulate some state changes
        if hasattr(self.engine, 'get_current_state'):
            state = self.engine.get_current_state()
            # Update visual controller with engine state
            self.visual_controller.update_from_engine(state)
            
    def _update_orb_state(self, visual_state) -> None:
        """Update orb based on visual state"""
        if self.orb:
            # Map visual state to orb state
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
            
    def add_user_message(self, text: str) -> None:
        """Add user message to conversation"""
        if self.conversation:
            self.conversation.add_message(text, is_user=True)
            
    def add_ai_message(self, text: str) -> None:
        """Add AI message to conversation"""
        if self.conversation:
            self.conversation.add_message(text, is_user=False)
            
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
        
        # Process input (would normally go through engine)
        await self.process_user_input(user_input)
        
    async def process_user_input(self, user_input: str) -> None:
        """Process user input through the engine"""
        # Show thinking state
        self.orb.set_state(AIState.THINKING, EmotionalState.THINKING)
        
        try:
            # Check for special UI commands first
            if user_input.lower() in ['quit', 'exit', 'bye']:
                self.add_ai_message("✨ Thank you for using Nix for Humanity! We flow with gratitude. 🌊")
                await asyncio.sleep(1)
                self.exit()
                return
                
            elif user_input.lower() == 'zen':
                self.action_toggle_zen()
                return
                
            elif user_input.lower() == 'flow':
                # Easter egg: enter flow state
                self.orb.enter_flow_state()
                self.add_ai_message("🌊 Entering flow state... We are one with the system.")
                return
                
            elif user_input.lower() == 'native':
                # Show native operations demo
                await self.show_native_operations()
                return
                
            elif user_input.lower() == 'advanced':
                # Show advanced features
                await self.show_advanced_features()
                return
            
            # Process through the real backend
            request = Request(
                query=user_input,
                context=Context(
                    personality="friendly",
                    execute=False,  # Don't execute for safety in demo
                    dry_run=True
                )
            )
            
            # Get response from backend
            response = self.engine.process(request)
            
            # Show response
            self.orb.set_state(AIState.SPEAKING, EmotionalState.HAPPY)
            
            if response.success:
                # Show the main response
                self.add_ai_message(response.text)
                
                # Show commands if any
                if response.commands:
                    commands_text = "\n\n📋 Commands I would run:\n"
                    for cmd in response.commands:
                        commands_text += f"  • `{cmd['command']}`\n"
                        if cmd.get('description'):
                            commands_text += f"    {cmd['description']}\n"
                    self.add_ai_message(commands_text)
                    
                # Show data if present
                if response.data and response.data.get('intent'):
                    self.add_ai_message(f"\n🧠 Intent: {response.data['intent']}")
            else:
                # Show error
                self.orb.set_state(AIState.ERROR, EmotionalState.CONCERNED)
                self.add_ai_message(f"❌ {response.text or response.error}")
                
        except Exception as e:
            # Handle errors gracefully
            self.orb.set_state(AIState.ERROR, EmotionalState.CONFUSED)
            self.add_ai_message(f"Sorry, I encountered an error: {str(e)}")
            self.add_ai_message("Try 'help' to see what I can do!")
            
        # Return to idle
        await asyncio.sleep(0.5)
        self.orb.set_state(AIState.IDLE, EmotionalState.NEUTRAL)
        
    async def show_native_operations(self) -> None:
        """Show native operations performance"""
        self.orb.set_state(AIState.SPEAKING, EmotionalState.HAPPY)
        self.add_ai_message("🚀 Native Operations Performance Demo:\n")
        
        try:
            native_ops = NativeOperationsManager()
            
            # Show instant operations
            start = datetime.now()
            result = await native_ops.execute_native_operation(
                NativeOperationType.LIST_GENERATIONS
            )
            duration = (datetime.now() - start).total_seconds() * 1000
            
            self.add_ai_message(f"✅ List generations: {duration:.1f}ms (INSTANT!)")
            
            if result.success and result.data.get('generations'):
                gens = result.data['generations'][:3]
                for gen in gens:
                    self.add_ai_message(f"  • Generation {gen['number']}: {gen['date']}")
                    
        except Exception as e:
            self.add_ai_message(f"Native operations not available: {e}")
            
    async def show_advanced_features(self) -> None:
        """Show advanced features available"""
        self.orb.set_state(AIState.SPEAKING, EmotionalState.HAPPY)
        
        features_text = """🌟 Advanced Features Available:

📦 Flake Support:
  • Initialize, update, build flakes
  • Modern NixOS configuration
  • Example: "init a flake"

👤 Profile Management:
  • Switch between work/home/gaming profiles
  • Instant environment changes
  • Example: "switch to work profile"

💬 Interactive REPL:
  • Launch Nix REPL for exploration
  • Example: "open nix repl"

🌐 Remote Deployment:
  • Build and deploy to servers
  • Example: "deploy to myserver.com"

💿 Image Building:
  • Create ISOs, VMs, containers
  • Example: "build an iso"

All powered by native Python-Nix API for instant operations!"""
        
        self.add_ai_message(features_text)
        
    def show_help(self) -> None:
        """Show help information"""
        self.orb.set_state(AIState.SPEAKING, EmotionalState.HAPPY)
        
        help_text = """
I can help you with:
• Installing/removing software: "install firefox", "remove vim"
• System updates: "update system", "check for updates" 
• Network issues: "my wifi isn't working", "show network status"
• System info: "disk space", "memory usage"
• Package search: "search for editors", "find python packages"

🚀 New Features:
• "native": Show native operations performance demo
• "advanced": Show advanced features (flakes, profiles, etc.)
• "generations": List system generations instantly

Special commands:
• Ctrl+Z: Toggle Zen mode (minimal interface)
• Ctrl+D: Toggle debug mode  
• "flow": Enter flow state (Easter egg!)
• "quit": Exit the application

Just describe what you need naturally!
        """
        
        self.add_ai_message(help_text.strip())
        
    def action_toggle_zen(self) -> None:
        """Toggle zen mode"""
        self.zen_mode = not self.zen_mode
        
        if self.zen_mode:
            # Hide everything except orb and input
            self.adaptive_interface.user_flow_state = UserFlowState.DEEP_FOCUS
            self.adaptive_interface.complexity_level = ComplexityLevel.ZEN
            self.add_ai_message("🧘 Zen mode activated. Minimal distractions.")
        else:
            # Return to normal
            self.adaptive_interface.user_flow_state = UserFlowState.NORMAL
            self.adaptive_interface.complexity_level = ComplexityLevel.FOCUSED
            self.add_ai_message("Returned to normal mode.")
            
    def action_toggle_debug(self) -> None:
        """Toggle debug mode"""
        self.debug_mode = not self.debug_mode
        
        if self.debug_mode:
            self.adaptive_interface.complexity_level = ComplexityLevel.EXPERT
            self.add_ai_message("🔧 Debug mode activated. All information visible.")
        else:
            self.adaptive_interface.complexity_level = ComplexityLevel.FOCUSED
            self.add_ai_message("Debug mode deactivated.")


def main():
    """Main entry point for the TUI"""
    app = NixForHumanityTUI()
    app.run()


if __name__ == "__main__":
    main()