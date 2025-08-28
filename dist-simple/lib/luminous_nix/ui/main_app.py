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
from .backend_connector import TUIBackendConnector, TUIState
from .visual_orb_integration import VisualOrbBridge
try:
    from ..core.engine import NixForHumanityBackend
    from ..api.schema import Request, Context
except ImportError:
    # Fallback if old engine not available
    pass


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
    
    def __init__(self, mindful_mode: bool = True, headless: bool = False):
        super().__init__()
        # Headless mode for testing
        self.headless = headless
        self.search_results_count = 0
        self.install_preview_visible = False
        self.last_message = ""
        
        # Use our new backend connector
        self.backend = TUIBackendConnector(mindful_mode=mindful_mode)
        
        # Subscribe to backend state updates
        self.backend.subscribe_state(self._on_backend_state_update)
        self.backend.subscribe_messages(self._on_backend_message)
        
        # For headless testing - override driver
        if headless:
            self._driver = None  # Will be overridden by test harness
        
        self.orb: Optional[ConsciousnessOrb] = None
        self.adaptive_interface: Optional[AdaptiveInterface] = None
        self.conversation: Optional[ConversationPanel] = None
        self.visual_orb_bridge: Optional[VisualOrbBridge] = None
        
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
        # Start the visual state sync
        self.set_interval(0.1, self._sync_visual_state)
        
        # Focus on input
        self.query_one("#main-input", Input).focus()
        
        # Welcome message based on mindful mode
        if self.backend.core.mindful_mode:
            self.add_ai_message(
                "🕉️ Welcome to Luminous Nix! I honor your presence. "
                "Together we flow in consciousness-first computing. "
                "What intention shall we manifest today?"
            )
        else:
            self.add_ai_message(
                "⚡ Welcome to Luminous Nix! Fast and efficient NixOS management. "
                "What would you like to do today?"
            )
        
        # Set initial orb state
        self.orb.set_state(AIState.IDLE, EmotionalState.HAPPY)
        
        # Initialize Visual Orb Bridge for enhanced consciousness visualization
        if self.orb:
            self.visual_orb_bridge = VisualOrbBridge(self.orb)
            
            # Create context provider function
            def get_tui_context():
                """Provide context for consciousness detection"""
                state = self.backend.get_current_state()
                return {
                    'user_activity': 'active' if state.get('last_interaction_time', 0) < 60 else 'idle',
                    'system_load': state.get('cpu_usage', 0.5),
                    'time_in_flow': state.get('flow_duration', 0),
                    'error_rate': state.get('error_rate', 0),
                    'success_rate': state.get('success_rate', 0.5),
                }
            
            # Start the visual orb synchronization
            asyncio.create_task(self.visual_orb_bridge.start_sync_loop(get_tui_context))
        
    def _sync_visual_state(self) -> None:
        """Sync visual state with backend"""
        # Get current backend state
        state = self.backend.get_current_state()
        
        # Update UI elements based on state
        if self.adaptive_interface:
            # Update complexity based on user experience
            if state['success_rate'] > 0.8:
                self.adaptive_interface.complexity_level = ComplexityLevel.INTERMEDIATE
            elif state['success_rate'] < 0.5:
                self.adaptive_interface.complexity_level = ComplexityLevel.BEGINNER
        
        # Update consciousness field visualization if available
        if hasattr(self, 'field_viz'):
            field_data = self.backend.get_field_visualization()
            self.update_field_visualization(field_data)
        
        # Update visual orb description if bridge is active
        if self.visual_orb_bridge:
            # Get consciousness description and display it
            description = self.visual_orb_bridge.get_description()
            if hasattr(self, 'status_bar'):
                self.status_bar.update(description)
            
    def _on_backend_state_update(self, state: TUIState) -> None:
        """Handle backend state updates"""
        if self.orb:
            # Use backend's state mappings
            ai_state_map = self.backend.get_ai_state_mapping()
            emotion_map = self.backend.get_emotion_mapping()
            
            ai_state = ai_state_map.get(state.ai_state, AIState.IDLE)
            emotion = emotion_map.get(state.ai_emotion, EmotionalState.NEUTRAL)
            
            self.orb.set_state(ai_state, emotion)
            self.orb.attention_level = state.emotion_intensity
            
            # Update consciousness coherence indicator
            self.orb.coherence = state.consciousness_coherence
    
    def _on_backend_message(self, message: str, is_user: bool = False) -> None:
        """Handle backend message updates"""
        if is_user:
            self.add_user_message(message)
        else:
            self.add_ai_message(message)
            
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
        """Process user input through the backend"""
        try:
            # Check for special UI commands first
            if user_input.lower() in ['quit', 'exit', 'bye']:
                if self.backend.core.mindful_mode:
                    self.add_ai_message("🙏 Thank you for this sacred time together. May you flow in awareness. 🌊")
                else:
                    self.add_ai_message("✨ Thank you for using Luminous Nix! Until next time!")
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
                
            elif user_input.lower() == 'mindful':
                # Toggle mindful mode
                new_mode = self.backend.toggle_mindful_mode()
                if new_mode:
                    self.add_ai_message("🧘 Mindful mode activated. Sacred pauses and natural rhythms will be honored.")
                else:
                    self.add_ai_message("⚡ Performance mode activated. Optimizing for speed.")
                return
            
            # Process through the backend connector
            response = await self.backend.process_query(user_input, dry_run=True)
            
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
            # Use sync version for now - async version needs proper event loop handling
            import asyncio
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(native_ops.execute_native_operation(
                NativeOperationType.LIST_GENERATIONS
            ))
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
        
    async def process_key(self, key: str):
        """Process a keypress (for headless mode testing)."""
        if self.headless:
            # Simulate key processing for testing
            if key == "s":
                self.action_search()
            elif key == "i":
                self.action_install()
            elif key == "c":
                self.action_config()
            elif key == "h":
                self.action_help()
            elif key == "q":
                self.exit()
            elif key == "enter":
                # Simulate enter key
                pass
            # Add more key handlers as needed
    
    def action_search(self) -> None:
        """Open search interface"""
        self.last_message = "Search opened"
        if not self.headless:
            try:
                self.push_screen("search")
            except:
                pass  # Screen not available in headless mode
        
    def action_install(self) -> None:
        """Open install interface"""
        self.install_preview_visible = True
        self.last_message = "Install preview shown"
        if not self.headless:
            try:
                self.push_screen("install")
            except:
                pass  # Screen not available in headless mode
        
    def action_config(self) -> None:
        """Open configuration"""
        self.last_message = "Config opened"
        if not self.headless:
            try:
                self.push_screen("config")
            except:
                pass  # Screen not available in headless mode
        
    def action_help(self) -> None:
        """Show help"""
        self.last_message = "Help opened"
        if not self.headless:
            try:
                self.push_screen("help")
            except:
                pass  # Screen not available in headless mode
        
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