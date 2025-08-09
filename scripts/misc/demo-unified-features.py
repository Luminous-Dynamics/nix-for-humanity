#!/usr/bin/env python3
"""
🎉 Demo of Unified Enhanced TUI with All Features

Shows:
- Enhanced consciousness orb with celebrations
- Connected backend with INSTANT operations
- Voice interface connection
- Educational error handling
- Progress indicators
- Flow state achievement
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nix_humanity.ui.unified_enhanced_tui import UnifiedEnhancedTUI
from nix_humanity.core.engine import NixForHumanityBackend
from textual.app import App
from rich.console import Console

console = Console()


async def demo_sequence():
    """Run the demo sequence"""
    console.print("\n[bold cyan]🌟 Nix for Humanity - Unified Enhanced TUI Demo[/bold cyan]\n")
    console.print("This demo showcases all enhanced features:")
    console.print("- ✨ Enhanced consciousness orb with celebrations")
    console.print("- ⚡ INSTANT native operations") 
    console.print("- 🎤 Voice interface integration")
    console.print("- 💡 Educational error handling")
    console.print("- 📊 Real-time performance metrics")
    console.print("- 🌊 Flow state visualization\n")
    
    console.print("[yellow]Starting TUI in 3 seconds...[/yellow]")
    await asyncio.sleep(3)
    
    # Create and run the app
    app = UnifiedEnhancedTUI()
    
    # Set up demo mode
    os.environ['NIX_HUMANITY_DEMO_MODE'] = 'true'
    os.environ['NIX_HUMANITY_PYTHON_BACKEND'] = 'true'
    
    console.print("\n[green]✨ TUI Started![/green]")
    console.print("\n[bold]Demo Commands to Try:[/bold]")
    console.print("1. 'list all generations' - See INSTANT operation")
    console.print("2. 'search firefox' - Watch 10x faster search")
    console.print("3. 'install non-existent' - See educational error")
    console.print("4. Press Ctrl+V - Enable voice mode")
    console.print("5. Quick commands - Build flow state\n")
    
    console.print("[yellow]Press Ctrl+C to exit[/yellow]\n")


def create_demo_app():
    """Create the demo application"""
    
    class DemoUnifiedTUI(UnifiedEnhancedTUI):
        """Demo version with auto-commands"""
        
        async def on_mount(self) -> None:
            """Initialize and run demo commands"""
            await super().on_mount()
            
            # Wait a bit then run demo commands
            self.set_timer(3.0, self._run_demo_commands)
            
        async def _run_demo_commands(self) -> None:
            """Run automatic demo commands"""
            # Show instant operation
            self.add_to_history({
                "type": "system",
                "message": "🎬 DEMO: Running instant operations...",
                "timestamp": datetime.now()
            })
            
            # Simulate instant generation listing
            self.input.value = "list all generations"
            await self.on_input_submitted(type('Event', (), {'value': 'list all generations'})())
            
            await asyncio.sleep(2)
            
            # Simulate voice activation
            self.add_to_history({
                "type": "system", 
                "message": "🎬 DEMO: Activating voice mode...",
                "timestamp": datetime.now()
            })
            self.action_toggle_voice()
            
    return DemoUnifiedTUI()


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_sequence())
    
    # Create and run the TUI
    app = UnifiedEnhancedTUI()
    app.run()