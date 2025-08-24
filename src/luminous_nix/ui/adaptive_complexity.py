#!/usr/bin/env python3
"""
🎨 Adaptive UI Complexity System
UI that adjusts complexity based on user proficiency
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import logging

from luminous_nix.consciousness.adaptive_persona import (
    DynamicPersona,
    EmotionalState
)

logger = logging.getLogger(__name__)


class UIComplexityLevel(Enum):
    """UI complexity levels from simplest to most advanced"""
    MINIMAL = "minimal"        # Just essentials, large text, few options
    SIMPLE = "simple"          # Basic features, clear labels, guided flow
    STANDARD = "standard"      # Normal interface, all common features
    ADVANCED = "advanced"      # Power user features, shortcuts, dense info
    EXPERT = "expert"          # Maximum information density, all features


class UIElementVisibility(Enum):
    """Controls which UI elements are shown"""
    ALWAYS = "always"          # Always visible regardless of level
    SIMPLE_UP = "simple_up"    # Visible from SIMPLE and above
    STANDARD_UP = "standard_up" # Visible from STANDARD and above
    ADVANCED_UP = "advanced_up" # Visible from ADVANCED and above
    EXPERT_ONLY = "expert_only" # Only visible in EXPERT mode


@dataclass
class UIElement:
    """Represents a UI element with adaptive visibility"""
    name: str
    visibility: UIElementVisibility
    default_value: Any = None
    help_text: str = ""
    keyboard_shortcut: Optional[str] = None
    position_priority: int = 100  # Lower = higher priority


@dataclass
class AdaptiveUIConfig:
    """Configuration for adaptive UI"""
    # Visual parameters
    font_size: int = 14
    line_spacing: float = 1.2
    color_contrast: float = 1.0
    animation_speed: float = 1.0
    
    # Layout parameters
    max_options_visible: int = 10
    show_descriptions: bool = True
    show_shortcuts: bool = False
    show_advanced_options: bool = False
    
    # Assistance parameters
    show_hints: bool = True
    auto_suggest: bool = True
    confirm_dangerous: bool = True
    explain_actions: bool = True
    
    # Information density
    compact_mode: bool = False
    show_technical_details: bool = False
    show_system_info: bool = False
    
    # Navigation
    breadcrumbs: bool = True
    search_enabled: bool = True
    history_visible: bool = False


class AdaptiveUISystem:
    """
    System that adjusts UI complexity based on user proficiency
    Progressively reveals features as users gain expertise
    """
    
    def __init__(self):
        """Initialize adaptive UI system"""
        self.complexity_configs = self._init_complexity_configs()
        self.current_level = UIComplexityLevel.STANDARD
        self.ui_elements = {}
        self.progressive_reveals = []
    
    def _init_complexity_configs(self) -> Dict[UIComplexityLevel, AdaptiveUIConfig]:
        """Initialize configurations for each complexity level"""
        return {
            UIComplexityLevel.MINIMAL: AdaptiveUIConfig(
                font_size=18,
                line_spacing=1.5,
                color_contrast=1.2,
                animation_speed=0.5,
                max_options_visible=5,
                show_descriptions=True,
                show_shortcuts=False,
                show_advanced_options=False,
                show_hints=True,
                auto_suggest=True,
                confirm_dangerous=True,
                explain_actions=True,
                compact_mode=False,
                show_technical_details=False,
                show_system_info=False,
                breadcrumbs=True,
                search_enabled=False,
                history_visible=False
            ),
            UIComplexityLevel.SIMPLE: AdaptiveUIConfig(
                font_size=16,
                line_spacing=1.3,
                color_contrast=1.1,
                animation_speed=0.7,
                max_options_visible=7,
                show_descriptions=True,
                show_shortcuts=False,
                show_advanced_options=False,
                show_hints=True,
                auto_suggest=True,
                confirm_dangerous=True,
                explain_actions=True,
                compact_mode=False,
                show_technical_details=False,
                show_system_info=False,
                breadcrumbs=True,
                search_enabled=True,
                history_visible=False
            ),
            UIComplexityLevel.STANDARD: AdaptiveUIConfig(
                font_size=14,
                line_spacing=1.2,
                color_contrast=1.0,
                animation_speed=1.0,
                max_options_visible=10,
                show_descriptions=True,
                show_shortcuts=True,
                show_advanced_options=False,
                show_hints=True,
                auto_suggest=True,
                confirm_dangerous=True,
                explain_actions=False,
                compact_mode=False,
                show_technical_details=False,
                show_system_info=True,
                breadcrumbs=True,
                search_enabled=True,
                history_visible=True
            ),
            UIComplexityLevel.ADVANCED: AdaptiveUIConfig(
                font_size=13,
                line_spacing=1.1,
                color_contrast=0.9,
                animation_speed=1.5,
                max_options_visible=15,
                show_descriptions=False,
                show_shortcuts=True,
                show_advanced_options=True,
                show_hints=False,
                auto_suggest=True,
                confirm_dangerous=False,
                explain_actions=False,
                compact_mode=True,
                show_technical_details=True,
                show_system_info=True,
                breadcrumbs=True,
                search_enabled=True,
                history_visible=True
            ),
            UIComplexityLevel.EXPERT: AdaptiveUIConfig(
                font_size=12,
                line_spacing=1.0,
                color_contrast=0.8,
                animation_speed=2.0,
                max_options_visible=50,
                show_descriptions=False,
                show_shortcuts=True,
                show_advanced_options=True,
                show_hints=False,
                auto_suggest=False,
                confirm_dangerous=False,
                explain_actions=False,
                compact_mode=True,
                show_technical_details=True,
                show_system_info=True,
                breadcrumbs=False,
                search_enabled=True,
                history_visible=True
            )
        }
    
    def determine_complexity_level(self, persona: DynamicPersona) -> UIComplexityLevel:
        """
        Determine appropriate UI complexity based on user persona
        
        Args:
            persona: User's dynamic persona
            
        Returns:
            Appropriate complexity level
        """
        # Calculate complexity score based on multiple factors
        score = 0.0
        
        # Technical proficiency is primary factor (0-50 points)
        score += persona.technical_proficiency * 50
        
        # Learning speed indicates growth (0-20 points)
        score += persona.learning_speed * 20
        
        # Confidence affects willingness to explore (0-15 points)
        score += persona.confidence_level * 15
        
        # Exploration tendency shows curiosity (0-10 points)
        score += persona.exploration_tendency * 10
        
        # Time spent in system (0-5 points)
        # Use interaction count as proxy if available
        hours_in_system = getattr(persona, 'session_count', 10) * 0.5  # Estimate hours
        score += min(hours_in_system / 20, 1.0) * 5
        
        # Adjust based on current state
        if persona.frustration_level > 0.6:
            score -= 10  # Simplify when frustrated
        
        if persona.current_mood == EmotionalState.RUSHED:
            score += 10  # Show shortcuts when rushed
        
        if persona.current_mood == EmotionalState.LEARNING:
            score -= 5  # Slightly simpler when learning
        
        # Map score to complexity level
        if score < 20:
            return UIComplexityLevel.MINIMAL
        elif score < 40:
            return UIComplexityLevel.SIMPLE
        elif score < 60:
            return UIComplexityLevel.STANDARD
        elif score < 80:
            return UIComplexityLevel.ADVANCED
        else:
            return UIComplexityLevel.EXPERT
    
    def adapt_ui(self, persona: DynamicPersona) -> AdaptiveUIConfig:
        """
        Adapt UI configuration based on user persona
        
        Args:
            persona: User's dynamic persona
            
        Returns:
            Adapted UI configuration
        """
        # Determine base complexity level
        level = self.determine_complexity_level(persona)
        self.current_level = level
        
        # Get base configuration
        config = self.complexity_configs[level]
        
        # Fine-tune based on specific persona attributes
        
        # Adjust for patience level
        if persona.patience_level < 0.3:
            config.animation_speed *= 1.5  # Faster animations
            config.auto_suggest = False  # Less interruption
        elif persona.patience_level > 0.7:
            config.show_descriptions = True  # More detail ok
        
        # Adjust for preferred verbosity
        if persona.preferred_verbosity < 0.3:
            config.show_descriptions = False
            config.explain_actions = False
            config.compact_mode = True
        elif persona.preferred_verbosity > 0.7:
            config.show_descriptions = True
            config.explain_actions = True
        
        # Adjust for error frequency (based on frustration as proxy)
        if persona.frustration_level > 0.3:
            config.confirm_dangerous = True
            config.show_hints = True
        
        # Adjust for time of day
        import datetime
        hour = datetime.datetime.now().hour
        if hour < 6 or hour > 22:
            config.color_contrast *= 0.8  # Softer contrast at night
            config.animation_speed *= 0.8  # Slower animations
        
        return config
    
    def get_visible_elements(self, 
                            all_elements: List[UIElement],
                            level: Optional[UIComplexityLevel] = None) -> List[UIElement]:
        """
        Filter UI elements based on complexity level
        
        Args:
            all_elements: All possible UI elements
            level: Complexity level (or use current)
            
        Returns:
            List of visible elements
        """
        if level is None:
            level = self.current_level
        
        visible = []
        for element in all_elements:
            if self._is_visible_at_level(element.visibility, level):
                visible.append(element)
        
        # Sort by priority
        visible.sort(key=lambda e: e.position_priority)
        
        return visible
    
    def _is_visible_at_level(self, 
                            visibility: UIElementVisibility,
                            level: UIComplexityLevel) -> bool:
        """Check if element is visible at given level"""
        level_order = [
            UIComplexityLevel.MINIMAL,
            UIComplexityLevel.SIMPLE,
            UIComplexityLevel.STANDARD,
            UIComplexityLevel.ADVANCED,
            UIComplexityLevel.EXPERT
        ]
        
        current_index = level_order.index(level)
        
        if visibility == UIElementVisibility.ALWAYS:
            return True
        elif visibility == UIElementVisibility.SIMPLE_UP:
            return current_index >= 1
        elif visibility == UIElementVisibility.STANDARD_UP:
            return current_index >= 2
        elif visibility == UIElementVisibility.ADVANCED_UP:
            return current_index >= 3
        elif visibility == UIElementVisibility.EXPERT_ONLY:
            return current_index >= 4
        
        return False
    
    def suggest_level_change(self, persona: DynamicPersona) -> Optional[UIComplexityLevel]:
        """
        Suggest if user should move to different complexity level
        
        Args:
            persona: User's persona
            
        Returns:
            Suggested new level or None if current is appropriate
        """
        suggested = self.determine_complexity_level(persona)
        
        if suggested != self.current_level:
            # Check if change is significant enough
            level_order = [
                UIComplexityLevel.MINIMAL,
                UIComplexityLevel.SIMPLE,
                UIComplexityLevel.STANDARD,
                UIComplexityLevel.ADVANCED,
                UIComplexityLevel.EXPERT
            ]
            
            current_idx = level_order.index(self.current_level)
            suggested_idx = level_order.index(suggested)
            
            # Only suggest if difference is significant
            if abs(suggested_idx - current_idx) >= 1:
                return suggested
        
        return None
    
    def create_progressive_reveal(self,
                                 elements: List[UIElement],
                                 persona: DynamicPersona) -> List[Tuple[UIElement, float]]:
        """
        Create a progressive reveal sequence for UI elements
        Elements appear over time as user gains proficiency
        
        Args:
            elements: UI elements to reveal
            persona: User's persona
            
        Returns:
            List of (element, reveal_progress) tuples
        """
        revealed = []
        
        # Calculate reveal progress for each element
        for element in elements:
            if self._is_visible_at_level(element.visibility, self.current_level):
                # Element is fully visible
                reveal_progress = 1.0
            else:
                # Calculate partial reveal based on proximity to threshold
                reveal_progress = self._calculate_reveal_progress(
                    element.visibility,
                    persona
                )
            
            revealed.append((element, reveal_progress))
        
        return revealed
    
    def _calculate_reveal_progress(self,
                                  visibility: UIElementVisibility,
                                  persona: DynamicPersona) -> float:
        """Calculate how close element is to being revealed"""
        # This creates a smooth transition effect
        score = persona.technical_proficiency
        
        thresholds = {
            UIElementVisibility.SIMPLE_UP: 0.3,
            UIElementVisibility.STANDARD_UP: 0.5,
            UIElementVisibility.ADVANCED_UP: 0.7,
            UIElementVisibility.EXPERT_ONLY: 0.9
        }
        
        if visibility in thresholds:
            threshold = thresholds[visibility]
            if score >= threshold:
                return 1.0
            elif score >= threshold - 0.1:
                # Partial reveal when close to threshold
                return (score - (threshold - 0.1)) / 0.1
        
        return 0.0
    
    def format_for_complexity(self,
                             content: str,
                             level: Optional[UIComplexityLevel] = None) -> str:
        """
        Format content appropriately for complexity level
        
        Args:
            content: Original content
            level: Complexity level
            
        Returns:
            Formatted content
        """
        if level is None:
            level = self.current_level
        
        if level == UIComplexityLevel.MINIMAL:
            # Simplify language, remove jargon
            content = content.replace("configuration", "settings")
            content = content.replace("execute", "run")
            content = content.replace("parameter", "option")
        
        elif level == UIComplexityLevel.SIMPLE:
            # Slight simplification
            content = content.replace("instantiate", "create")
            content = content.replace("terminate", "stop")
        
        elif level in [UIComplexityLevel.ADVANCED, UIComplexityLevel.EXPERT]:
            # Can use technical terms and abbreviations
            content = content.replace("configuration", "config")
            content = content.replace("environment", "env")
            content = content.replace("development", "dev")
        
        return content


# Example UI elements for NixOS management
NIXOS_UI_ELEMENTS = [
    UIElement(
        name="install_package",
        visibility=UIElementVisibility.ALWAYS,
        help_text="Install a new package",
        position_priority=1
    ),
    UIElement(
        name="search_packages",
        visibility=UIElementVisibility.ALWAYS,
        help_text="Search for packages",
        position_priority=2
    ),
    UIElement(
        name="update_system",
        visibility=UIElementVisibility.SIMPLE_UP,
        help_text="Update your system",
        position_priority=3
    ),
    UIElement(
        name="edit_configuration",
        visibility=UIElementVisibility.STANDARD_UP,
        help_text="Edit system configuration",
        keyboard_shortcut="Ctrl+E",
        position_priority=4
    ),
    UIElement(
        name="rollback",
        visibility=UIElementVisibility.STANDARD_UP,
        help_text="Rollback to previous generation",
        keyboard_shortcut="Ctrl+R",
        position_priority=5
    ),
    UIElement(
        name="garbage_collect",
        visibility=UIElementVisibility.ADVANCED_UP,
        help_text="Clean up old generations",
        keyboard_shortcut="Ctrl+G",
        position_priority=10
    ),
    UIElement(
        name="nix_repl",
        visibility=UIElementVisibility.EXPERT_ONLY,
        help_text="Open Nix REPL",
        keyboard_shortcut="Ctrl+N",
        position_priority=20
    ),
    UIElement(
        name="flake_management",
        visibility=UIElementVisibility.ADVANCED_UP,
        help_text="Manage Nix flakes",
        position_priority=15
    )
]


if __name__ == "__main__":
    # Test adaptive UI system
    ui_system = AdaptiveUISystem()
    
    # Test with different user personas
    print("Testing UI adaptation for different user types...")
    print("=" * 50)
    
    # Beginner user
    beginner = DynamicPersona(
        user_id="beginner",
        technical_proficiency=0.2,
        confidence_level=0.3,
        patience_level=0.8,
        preferred_verbosity=0.7
    )
    
    level = ui_system.determine_complexity_level(beginner)
    config = ui_system.adapt_ui(beginner)
    visible = ui_system.get_visible_elements(NIXOS_UI_ELEMENTS)
    
    print(f"\nBeginner User:")
    print(f"  Complexity Level: {level.value}")
    print(f"  Font Size: {config.font_size}")
    print(f"  Visible Options: {config.max_options_visible}")
    print(f"  Show Hints: {config.show_hints}")
    print(f"  Visible Elements: {[e.name for e in visible]}")
    
    # Expert user
    expert = DynamicPersona(
        user_id="expert",
        technical_proficiency=0.9,
        confidence_level=0.9,
        patience_level=0.4,
        preferred_verbosity=0.2
    )
    
    ui_system.current_level = UIComplexityLevel.STANDARD  # Reset
    level = ui_system.determine_complexity_level(expert)
    config = ui_system.adapt_ui(expert)
    visible = ui_system.get_visible_elements(NIXOS_UI_ELEMENTS)
    
    print(f"\nExpert User:")
    print(f"  Complexity Level: {level.value}")
    print(f"  Font Size: {config.font_size}")
    print(f"  Visible Options: {config.max_options_visible}")
    print(f"  Compact Mode: {config.compact_mode}")
    print(f"  Visible Elements: {[e.name for e in visible]}")
    
    # Frustrated user (should simplify)
    frustrated = DynamicPersona(
        user_id="frustrated",
        technical_proficiency=0.5,
        confidence_level=0.3,
        frustration_level=0.8,
        current_mood=EmotionalState.FRUSTRATED
    )
    
    level = ui_system.determine_complexity_level(frustrated)
    config = ui_system.adapt_ui(frustrated)
    
    print(f"\nFrustrated User:")
    print(f"  Complexity Level: {level.value}")
    print(f"  Show Hints: {config.show_hints}")
    print(f"  Confirm Dangerous: {config.confirm_dangerous}")
    print(f"  Font Size: {config.font_size}")
    
    # Test progressive reveal
    print(f"\nProgressive Reveal for Standard User:")
    standard_user = DynamicPersona(
        user_id="standard",
        technical_proficiency=0.45  # Just below standard threshold
    )
    
    ui_system.current_level = UIComplexityLevel.SIMPLE
    reveals = ui_system.create_progressive_reveal(NIXOS_UI_ELEMENTS, standard_user)
    
    for element, progress in reveals:
        if 0 < progress < 1:
            print(f"  {element.name}: {progress:.0%} revealed")
        elif progress == 1:
            print(f"  {element.name}: Fully visible")
    
    print("\n✨ UI Complexity Adjustment System Ready!")