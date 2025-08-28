#!/usr/bin/env python3
"""
🎨 Textual UI Renderer
Converts abstract interface specifications into real Textual UI applications
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, Static, Button, Input, Label, 
    DataTable, Tree, TextArea, ProgressBar, Sparkline,
    Tabs, Tab, TabbedContent, TabPane, Switch, Select,
    RadioButton, RadioSet, Checkbox, ListView, ListItem
)
from textual.containers import (
    Container, Horizontal, Vertical, Grid, 
    ScrollableContainer, HorizontalScroll
)
from textual.binding import Binding
from textual.reactive import reactive
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.align import Align

try:
    from nl_interface_builder import InterfaceSpecification
    from component_synthesis_engine import SynthesizedComponent
except ImportError:
    print("Warning: Some imports failed, running in limited mode")


class ComponentLibrary:
    """Library of Textual component generators"""
    
    def __init__(self):
        self.generators = {
            # Display components
            'display': self.create_display,
            'text': self.create_text,
            'metrics_display': self.create_metrics,
            'status_panel': self.create_status,
            'status_indicator': self.create_status_indicator,
            
            # Input components
            'input': self.create_input,
            'input_field': self.create_input,
            'input_group': self.create_input_group,
            'form': self.create_form,
            'submit_button': self.create_button,
            'button': self.create_button,
            
            # Data components
            'table': self.create_table,
            'list': self.create_list,
            'item_list': self.create_list,
            'tree': self.create_tree,
            
            # Charts (simplified for terminal)
            'chart': self.create_chart,
            'sparkline': self.create_sparkline,
            'gauge': self.create_gauge,
            
            # Layout components
            'tabs': self.create_tabs,
            'container': self.create_container,
            'panel': self.create_panel,
            
            # Interactive components
            'switch': self.create_switch,
            'checkbox': self.create_checkbox,
            'radio': self.create_radio,
            'select': self.create_select,
            
            # Special components
            'editor': self.create_editor,
            'text_area': self.create_editor,
            'terminal': self.create_terminal,
            'filter_bar': self.create_filter_bar,
            'toolbar': self.create_toolbar
        }
    
    def create_component(self, component: SynthesizedComponent) -> Any:
        """Create Textual widget from synthesized component"""
        
        # Determine component type
        comp_type = component.dna.purpose.lower().replace(' ', '_')
        
        # Find appropriate generator
        generator = None
        for key in self.generators:
            if key in comp_type or comp_type in key:
                generator = self.generators[key]
                break
        
        if not generator:
            # Default to display
            generator = self.create_display
        
        return generator(component)
    
    def create_display(self, component: SynthesizedComponent) -> Static:
        """Create display component"""
        
        content = Panel(
            Text(component.name, justify="center"),
            title=component.dna.purpose,
            border_style="blue"
        )
        
        return Static(content, id=component.id)
    
    def create_text(self, component: SynthesizedComponent) -> Static:
        """Create text display"""
        
        text = Text("Sample text content")
        
        # Apply styles from DNA
        if component.dna.visual_traits.get('emphasis') == 'bold':
            text.stylize("bold")
        
        return Static(text, id=component.id)
    
    def create_metrics(self, component: SynthesizedComponent) -> Container:
        """Create metrics display"""
        
        container = Vertical(id=component.id)
        
        # Create metric cards
        metrics = [
            ("CPU", "45%", "green"),
            ("Memory", "2.1GB", "yellow"),
            ("Disk", "67%", "blue"),
            ("Network", "1.2MB/s", "cyan")
        ]
        
        for label, value, color in metrics:
            metric_text = Text()
            metric_text.append(f"{label}: ", style="bold")
            metric_text.append(value, style=color)
            container.mount(Static(Panel(metric_text)))
        
        return container
    
    def create_status(self, component: SynthesizedComponent) -> Static:
        """Create status panel"""
        
        table = Table(title="System Status")
        table.add_column("Service", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Uptime")
        
        table.add_row("Web Server", "✅ Running", "5d 14h")
        table.add_row("Database", "✅ Running", "5d 14h")
        table.add_row("Cache", "⚠️ Warning", "2h 30m")
        
        return Static(table, id=component.id)
    
    def create_status_indicator(self, component: SynthesizedComponent) -> Static:
        """Create status indicator"""
        
        status = Text("● Online", style="green bold")
        return Static(Panel(status, title="Status"), id=component.id)
    
    def create_input(self, component: SynthesizedComponent) -> Input:
        """Create input field"""
        
        placeholder = "Enter value..."
        if component.structure and 'props' in component.structure:
            placeholder = component.structure['props'].get('placeholder', placeholder)
        
        return Input(placeholder=placeholder, id=component.id)
    
    def create_input_group(self, component: SynthesizedComponent) -> Container:
        """Create group of inputs"""
        
        container = Vertical(id=component.id)
        
        # Add multiple input fields
        fields = ["Name", "Email", "Message"]
        for field in fields:
            container.mount(Label(f"{field}:"))
            container.mount(Input(placeholder=f"Enter {field.lower()}..."))
        
        return container
    
    def create_form(self, component: SynthesizedComponent) -> Container:
        """Create form"""
        
        container = Vertical(id=component.id)
        
        container.mount(Label("Form"))
        container.mount(Input(placeholder="Field 1"))
        container.mount(Input(placeholder="Field 2"))
        container.mount(Button("Submit", variant="primary"))
        
        return container
    
    def create_button(self, component: SynthesizedComponent) -> Button:
        """Create button"""
        
        label = "Click Me"
        variant = "default"
        
        if component.structure and 'children' in component.structure:
            label = str(component.structure['children'])
        
        if component.dna.visual_traits.get('emphasis') == 'bold':
            variant = "primary"
        
        return Button(label, id=component.id, variant=variant)
    
    def create_table(self, component: SynthesizedComponent) -> DataTable:
        """Create data table"""
        
        table = DataTable(id=component.id)
        
        # Add sample columns and data
        table.add_columns("ID", "Name", "Status", "Action")
        table.add_rows([
            ["1", "Item One", "Active", "Edit"],
            ["2", "Item Two", "Pending", "Edit"],
            ["3", "Item Three", "Complete", "View"]
        ])
        
        return table
    
    def create_list(self, component: SynthesizedComponent) -> ListView:
        """Create list view"""
        
        items = [
            ListItem(Label(f"Item {i}"))
            for i in range(1, 6)
        ]
        
        return ListView(*items, id=component.id)
    
    def create_tree(self, component: SynthesizedComponent) -> Tree:
        """Create tree view"""
        
        tree = Tree("Root", id=component.id)
        
        branch1 = tree.root.add("Branch 1")
        branch1.add_leaf("Leaf 1.1")
        branch1.add_leaf("Leaf 1.2")
        
        branch2 = tree.root.add("Branch 2")
        branch2.add_leaf("Leaf 2.1")
        
        return tree
    
    def create_chart(self, component: SynthesizedComponent) -> Container:
        """Create chart (simplified)"""
        
        container = Vertical(id=component.id)
        
        # Create ASCII chart
        chart_text = """
        Sales Performance
        ═══════════════════════════
        Jan ████████████░░░░░░░░ 60%
        Feb ████████████████░░░░ 80%
        Mar ██████████████████░░ 90%
        Apr ████████████████████ 100%
        """
        
        container.mount(Static(Text(chart_text, style="cyan")))
        
        return container
    
    def create_sparkline(self, component: SynthesizedComponent) -> Sparkline:
        """Create sparkline chart"""
        
        data = [10, 20, 15, 30, 25, 40, 35, 45, 50, 40]
        return Sparkline(data, id=component.id)
    
    def create_gauge(self, component: SynthesizedComponent) -> Container:
        """Create gauge display"""
        
        container = Vertical(id=component.id)
        
        # Simple progress bar as gauge
        container.mount(Label("CPU Usage"))
        container.mount(ProgressBar(total=100, progress=65))
        
        return container
    
    def create_tabs(self, component: SynthesizedComponent) -> TabbedContent:
        """Create tabbed interface"""
        
        with TabbedContent(id=component.id):
            with TabPane("Tab 1", id="tab1"):
                yield Label("Content 1")
            with TabPane("Tab 2", id="tab2"):
                yield Label("Content 2")
            with TabPane("Tab 3", id="tab3"):
                yield Label("Content 3")
    
    def create_container(self, component: SynthesizedComponent) -> Container:
        """Create generic container"""
        
        return Container(id=component.id)
    
    def create_panel(self, component: SynthesizedComponent) -> Static:
        """Create panel"""
        
        return Static(
            Panel("Panel Content", title=component.name),
            id=component.id
        )
    
    def create_switch(self, component: SynthesizedComponent) -> Switch:
        """Create toggle switch"""
        
        return Switch(value=False, id=component.id)
    
    def create_checkbox(self, component: SynthesizedComponent) -> Checkbox:
        """Create checkbox"""
        
        return Checkbox("Option", id=component.id)
    
    def create_radio(self, component: SynthesizedComponent) -> RadioSet:
        """Create radio buttons"""
        
        return RadioSet(
            RadioButton("Option 1"),
            RadioButton("Option 2"),
            RadioButton("Option 3"),
            id=component.id
        )
    
    def create_select(self, component: SynthesizedComponent) -> Select:
        """Create dropdown select"""
        
        options = [("opt1", "Option 1"), ("opt2", "Option 2"), ("opt3", "Option 3")]
        return Select(options, id=component.id)
    
    def create_editor(self, component: SynthesizedComponent) -> TextArea:
        """Create text editor"""
        
        return TextArea("# Welcome to the editor\n\nStart typing...", id=component.id)
    
    def create_terminal(self, component: SynthesizedComponent) -> Container:
        """Create terminal emulator (mock)"""
        
        container = Vertical(id=component.id)
        
        terminal_content = """
$ ls -la
total 48
drwxr-xr-x  6 user user 4096 Jan 25 14:30 .
drwxr-xr-x 12 user user 4096 Jan 25 12:15 ..
-rw-r--r--  1 user user  234 Jan 25 14:30 README.md

$ echo "Terminal emulator"
Terminal emulator

$ _
        """
        
        container.mount(Static(
            Panel(Text(terminal_content, style="green on black"), 
                  title="Terminal",
                  border_style="green")
        ))
        
        return container
    
    def create_filter_bar(self, component: SynthesizedComponent) -> Horizontal:
        """Create filter bar"""
        
        container = Horizontal(id=component.id)
        
        container.mount(Input(placeholder="Search..."))
        container.mount(Select([("all", "All"), ("active", "Active"), ("done", "Done")]))
        container.mount(Button("Filter", variant="primary"))
        
        return container
    
    def create_toolbar(self, component: SynthesizedComponent) -> Horizontal:
        """Create toolbar"""
        
        container = Horizontal(id=component.id)
        
        container.mount(Button("New"))
        container.mount(Button("Open"))
        container.mount(Button("Save"))
        container.mount(Button("Cut"))
        container.mount(Button("Copy"))
        container.mount(Button("Paste"))
        
        return container


class DynamicTextualApp(App):
    """Dynamic Textual application generated from interface specification"""
    
    CSS = """
    Screen {
        align: center middle;
    }
    
    #main-container {
        width: 100%;
        height: 100%;
    }
    
    .panel {
        margin: 1;
        padding: 1;
    }
    
    .metrics {
        height: auto;
        margin: 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("d", "toggle_dark", "Toggle dark mode"),
        Binding("f", "feedback", "Feedback"),
    ]
    
    def __init__(self, interface: InterfaceSpecification):
        super().__init__()
        self.interface = interface
        self.component_library = ComponentLibrary()
        self.widgets = []
    
    def compose(self) -> ComposeResult:
        """Compose the UI from interface specification"""
        
        yield Header()
        
        # Main container
        with self._create_layout_container():
            # Generate widgets from components
            for component in self.interface.components:
                widget = self.component_library.create_component(component)
                if widget:
                    self.widgets.append(widget)
                    yield widget
        
        yield Footer()
    
    def _create_layout_container(self):
        """Create appropriate layout container"""
        
        layout_type = self.interface.layout.get('type', 'vertical')
        
        if layout_type == 'grid':
            cols = self.interface.layout.get('columns', 3)
            return Grid(id="main-container")
        elif layout_type == 'horizontal':
            return Horizontal(id="main-container")
        elif layout_type == 'split':
            return Horizontal(id="main-container")
        else:  # vertical or default
            return Vertical(id="main-container")
    
    def action_feedback(self):
        """Show feedback dialog"""
        self.push_screen(FeedbackScreen(self.interface))


class FeedbackScreen(App):
    """Feedback collection screen"""
    
    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("How was the generated interface?"),
            Horizontal(
                Button("👍 Good", id="good"),
                Button("😐 OK", id="ok"),
                Button("👎 Needs Work", id="bad"),
            ),
            Button("Close", id="close"),
            id="feedback-container"
        )
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "close":
            self.app.pop_screen()
        else:
            # Record feedback
            print(f"Feedback: {event.button.id}")
            self.app.pop_screen()


class TextualUIRenderer:
    """Main renderer for converting interfaces to Textual apps"""
    
    def render(self, interface: InterfaceSpecification) -> DynamicTextualApp:
        """Render interface specification as Textual app"""
        
        # Apply theme if specified
        if interface.theme.get('mode') == 'dark':
            # Textual uses dark mode by default
            pass
        
        return DynamicTextualApp(interface)
    
    def preview(self, interface: InterfaceSpecification):
        """Preview interface in terminal"""
        
        app = self.render(interface)
        app.run()


# Testing and demo
if __name__ == "__main__":
    from nl_interface_builder_v2 import NLInterfaceBuilderV2, UserContext
    
    print("🎨 TEXTUAL UI RENDERER DEMO")
    print("="*60)
    print("\nGenerating interface from natural language...\n")
    
    # Build an interface
    builder = NLInterfaceBuilderV2(use_llm=False)  # Use NLP only for speed
    
    context = UserContext(
        user_id="demo",
        expertise_level="intermediate",
        device_type="desktop",
        preferences={"theme": "dark"}
    )
    
    # Test different requests
    request = "Create a dashboard with metrics, status panel, and charts with dark theme"
    
    print(f"Request: {request}")
    interface = builder.build_interface(request, context)
    
    print(f"Generated {len(interface.components)} components")
    print(f"Layout: {interface.layout.get('type')}")
    print(f"Theme: {interface.theme.get('mode')}")
    
    # Render as Textual app
    print("\nLaunching Textual UI preview...")
    print("Press 'q' to quit, 'd' for dark mode, 'f' for feedback\n")
    
    renderer = TextualUIRenderer()
    renderer.preview(interface)