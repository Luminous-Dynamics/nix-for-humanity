#!/usr/bin/env python3
"""
Demo: TUI + Native Operations Integration

Shows how the beautiful TUI can leverage instant native operations.
"""

import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button
from textual.containers import Container, Vertical, Horizontal
from textual.reactive import reactive
from rich.text import Text
from rich.panel import Panel
from datetime import datetime
import time

# Import our native operations
from nix_humanity.core.native_operations import NativeOperationsManager, NativeOperationType


class NativeOperationResult(Static):
    """Display for operation results"""
    
    def __init__(self, operation: str = "", result: str = "", duration: str = ""):
        super().__init__()
        self.operation = operation
        self.result = result
        self.duration = duration
        
    def render(self):
        if not self.operation:
            return Panel("Ready for native operations...", title="🚀 Native API Status")
            
        return Panel(
            f"Operation: {self.operation}\n"
            f"Result: {self.result}\n"
            f"Duration: {self.duration}",
            title="✨ Operation Complete",
            border_style="green"
        )


class NativeTUIDemo(App):
    """Demo app showing TUI + Native Operations"""
    
    CSS = """
    Screen {
        align: center middle;
    }
    
    #container {
        width: 80;
        height: 40;
        border: solid $primary;
        padding: 2;
    }
    
    Button {
        margin: 1;
        width: 100%;
    }
    
    #result {
        height: 10;
        margin-top: 2;
    }
    """
    
    def __init__(self):
        super().__init__()
        self.native_ops = None
        self.result_display = None
        
    def compose(self) -> ComposeResult:
        """Build the UI"""
        yield Header()
        
        with Container(id="container"):
            yield Static(
                "[bold cyan]🌟 Nix for Humanity - Native Operations Demo[/]\n\n"
                "Experience the power of instant NixOS operations!",
                id="title"
            )
            
            with Vertical():
                # Operation buttons
                yield Button("📋 List Generations (INSTANT!)", id="list-generations", variant="primary")
                yield Button("🔍 System Info (INSTANT!)", id="system-info", variant="primary") 
                yield Button("📦 Search Firefox (10x faster)", id="search-firefox", variant="primary")
                yield Button("🗑️ Check Garbage Collection", id="check-gc", variant="primary")
                yield Button("🔧 Show Config Options (INSTANT!)", id="show-options", variant="primary")
                
                # Result display
                self.result_display = NativeOperationResult()
                yield self.result_display
                
        yield Footer()
        
    async def on_mount(self) -> None:
        """Initialize native operations"""
        try:
            self.native_ops = NativeOperationsManager()
            self.log("✅ Native operations ready!")
        except Exception as e:
            self.log(f"❌ Native ops unavailable: {e}")
            
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if not self.native_ops:
            self.update_result("Error", "Native operations not available", "N/A")
            return
            
        # Map buttons to operations
        operations = {
            "list-generations": (NativeOperationType.LIST_GENERATIONS, None),
            "system-info": (NativeOperationType.SYSTEM_INFO, None),
            "search-firefox": (NativeOperationType.SEARCH_PACKAGES, ["firefox"]),
            "check-gc": (NativeOperationType.GARBAGE_COLLECT, None),
            "show-options": (NativeOperationType.SHOW_CONFIG_OPTIONS, None),
        }
        
        if button_id in operations:
            op_type, packages = operations[button_id]
            await self.run_native_operation(op_type, packages)
            
    async def run_native_operation(self, op_type: NativeOperationType, packages: list = None):
        """Run a native operation and display results"""
        self.update_result(op_type.value, "Running...", "⏳")
        
        start = time.time()
        try:
            result = await self.native_ops.execute_native_operation(
                op_type,
                packages=packages
            )
            duration = (time.time() - start) * 1000
            
            if result.success:
                # Format result based on operation
                if op_type == NativeOperationType.LIST_GENERATIONS and result.data.get('generations'):
                    msg = f"Found {len(result.data['generations'])} generations"
                elif op_type == NativeOperationType.SYSTEM_INFO:
                    msg = f"NixOS {result.data.get('nixos_version', 'Unknown')}"
                else:
                    msg = result.message
                    
                self.update_result(
                    op_type.value,
                    f"✅ {msg}",
                    f"{duration:.1f}ms"
                )
            else:
                self.update_result(
                    op_type.value,
                    f"❌ {result.message}",
                    f"{duration:.1f}ms"
                )
        except Exception as e:
            self.update_result(
                op_type.value,
                f"❌ Error: {str(e)}",
                "N/A"
            )
            
    def update_result(self, operation: str, result: str, duration: str):
        """Update the result display"""
        self.result_display.operation = operation
        self.result_display.result = result
        self.result_display.duration = duration
        self.result_display.refresh()


if __name__ == "__main__":
    app = NativeTUIDemo()
    app.run()