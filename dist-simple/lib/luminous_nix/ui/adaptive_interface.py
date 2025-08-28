"""
from typing import List
🎨 Adaptive Interface - Consciousness-First UI Complexity Management

Interface that reveals and hides complexity based on user cognitive state,
following the principle of progressive disclosure and The Disappearing Path.
"""

from textual.widget import Widget
from textual.reactive import reactive
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Input, Static, Header, Footer, Button, Label
from textual.app import ComposeResult
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from typing import Optional, List, Dict
from enum import Enum
from dataclasses import dataclass


class UserFlowState(Enum):
    """User's cognitive flow state"""
    NORMAL = "normal"
    FOCUSED = "focused"
    DEEP_FOCUS = "deep_focus"
    STRUGGLING = "struggling"
    EXPLORING = "exploring"


class ComplexityLevel(Enum):
    """Interface complexity levels"""
    ZEN = "zen"  # Minimal - just orb and input
    FOCUSED = "focused"  # Core functions visible
    EXPLORER = "explorer"  # All options available
    EXPERT = "expert"  # Dense information display


@dataclass
class ComplexityConfig:
    """Configuration for each complexity level"""
    name: str
    max_elements: int
    show_suggestions: bool
    show_history: bool
    show_metrics: bool
    show_advanced: bool
    animation_level: str  # minimal, moderate, rich
    information_density: str  # low, medium, high


# Complexity configurations
COMPLEXITY_CONFIGS = {
    ComplexityLevel.ZEN: ComplexityConfig(
        name="Zen Mode",
        max_elements=2,
        show_suggestions=False,
        show_history=False,
        show_metrics=False,
        show_advanced=False,
        animation_level="minimal",
        information_density="low"
    ),
    ComplexityLevel.FOCUSED: ComplexityConfig(
        name="Focused Mode",
        max_elements=5,
        show_suggestions=True,
        show_history=False,
        show_metrics=False,
        show_advanced=False,
        animation_level="moderate",
        information_density="medium"
    ),
    ComplexityLevel.EXPLORER: ComplexityConfig(
        name="Explorer Mode",
        max_elements=8,
        show_suggestions=True,
        show_history=True,
        show_metrics=False,
        show_advanced=True,
        animation_level="rich",
        information_density="high"
    ),
    ComplexityLevel.EXPERT: ComplexityConfig(
        name="Expert Mode",
        max_elements=12,
        show_suggestions=True,
        show_history=True,
        show_metrics=True,
        show_advanced=True,
        animation_level="rich",
        information_density="high"
    )
}


class AdaptiveInterface(Container):
    """
    Interface that adapts complexity based on user state.
    
    Following The Disappearing Path philosophy:
    - Starts rich for new users
    - Simplifies as mastery grows
    - Eventually becomes nearly invisible
    """
    
    # Reactive properties
    user_flow_state = reactive(UserFlowState.NORMAL)
    complexity_level = reactive(ComplexityLevel.FOCUSED)
    user_expertise = reactive(0.5)  # 0.0 to 1.0
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command_history: List[str] = []
        self.suggestions: List[str] = []
        self.current_config = COMPLEXITY_CONFIGS[self.complexity_level]
        
    def determine_complexity(self) -> ComplexityLevel:
        """Determine optimal complexity based on user state and expertise"""
        # Map flow states to base complexity
        flow_complexity_map = {
            UserFlowState.DEEP_FOCUS: ComplexityLevel.ZEN,
            UserFlowState.FOCUSED: ComplexityLevel.FOCUSED,
            UserFlowState.NORMAL: ComplexityLevel.FOCUSED,
            UserFlowState.EXPLORING: ComplexityLevel.EXPLORER,
            UserFlowState.STRUGGLING: ComplexityLevel.FOCUSED  # Simplify when struggling
        }
        
        base_level = flow_complexity_map[self.user_flow_state]
        
        # Adjust based on expertise
        if self.user_expertise > 0.8 and base_level != ComplexityLevel.ZEN:
            # Experts might want more info (unless in deep focus)
            if base_level == ComplexityLevel.FOCUSED:
                return ComplexityLevel.EXPLORER
            elif base_level == ComplexityLevel.EXPLORER:
                return ComplexityLevel.EXPERT
                
        elif self.user_expertise < 0.3 and base_level in [ComplexityLevel.EXPLORER, ComplexityLevel.EXPERT]:
            # New users shouldn't be overwhelmed
            return ComplexityLevel.FOCUSED
            
        return base_level
        
    def watch_user_flow_state(self, new_state: UserFlowState) -> None:
        """React to flow state changes"""
        self.complexity_level = self.determine_complexity()
        self.current_config = COMPLEXITY_CONFIGS[self.complexity_level]
        self.refresh_interface()
        
    def compose(self) -> ComposeResult:
        """Compose the adaptive interface"""
        # Always show input at bottom
        yield CommandInput(id="main-input")
        
        # Conditionally show other elements based on complexity
        if self.current_config.show_suggestions:
            yield SuggestionsPanel(id="suggestions")
            
        if self.current_config.show_history:
            yield HistoryPanel(id="history")
            
        if self.current_config.show_metrics:
            yield MetricsPanel(id="metrics")
            
        if self.current_config.show_advanced:
            yield AdvancedPanel(id="advanced")
            
    def refresh_interface(self) -> None:
        """Smoothly transition between complexity levels"""
        # This would trigger smooth animations in a real implementation
        # For now, we'll just log the transition
        self.log(f"Transitioning to {self.current_config.name}")
        
        # Update visibility of components
        self._update_component_visibility()
        
    def _update_component_visibility(self) -> None:
        """Show/hide components based on complexity"""
        # Get all child widgets
        suggestions = self.query_one("#suggestions", SuggestionsPanel)
        history = self.query_one("#history", HistoryPanel) 
        metrics = self.query_one("#metrics", MetricsPanel)
        advanced = self.query_one("#advanced", AdvancedPanel)
        
        # Update visibility with smooth transitions
        if suggestions:
            suggestions.display = self.current_config.show_suggestions
        if history:
            history.display = self.current_config.show_history
        if metrics:
            metrics.display = self.current_config.show_metrics
        if advanced:
            advanced.display = self.current_config.show_advanced


class CommandInput(Widget):
    """Adaptive command input that changes based on context"""
    
    def compose(self) -> ComposeResult:
        yield Input(
            placeholder="✨ Ask me anything...",
            id="command-input"
        )
        
    def on_mount(self) -> None:
        """Focus on mount"""
        self.query_one(Input).focus()


class SuggestionsPanel(Widget):
    """Smart suggestions based on context"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.suggestions = [
            "install firefox",
            "update system",
            "check disk space",
            "show network status"
        ]
        
    def render(self) -> Panel:
        """Render suggestions"""
        suggestion_text = Text()
        suggestion_text.append("💡 Suggestions:\n", style="bold yellow")
        
        for i, suggestion in enumerate(self.suggestions[:4]):
            suggestion_text.append(f"  {i+1}. {suggestion}\n", style="cyan")
            
        return Panel(
            suggestion_text,
            title="Quick Actions",
            border_style="yellow"
        )


class HistoryPanel(Widget):
    """Command history with smart filtering"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.history = []
        
    def render(self) -> Panel:
        """Render history"""
        if not self.history:
            return Panel(
                "No commands yet",
                title="Recent History",
                border_style="blue"
            )
            
        history_text = Text()
        for cmd in self.history[-5:]:
            history_text.append(f"• {cmd}\n", style="dim")
            
        return Panel(
            history_text,
            title="Recent Commands",
            border_style="blue"
        )


class MetricsPanel(Widget):
    """System metrics for power users"""
    
    def render(self) -> Panel:
        """Render metrics"""
        table = Table(show_header=False, box=None)
        table.add_column("Metric")
        table.add_column("Value", style="green")
        
        table.add_row("CPU", "45%")
        table.add_row("Memory", "2.1GB")
        table.add_row("Response", "0.8s")
        table.add_row("Accuracy", "94%")
        
        return Panel(
            table,
            title="System Metrics",
            border_style="green"
        )


class AdvancedPanel(Widget):
    """Advanced options for expert users"""
    
    def compose(self) -> ComposeResult:
        yield Horizontal(
            Button("Shell", id="shell-btn", variant="primary"),
            Button("Config", id="config-btn"),
            Button("Debug", id="debug-btn"),
            Button("Logs", id="logs-btn"),
            id="advanced-buttons"
        )