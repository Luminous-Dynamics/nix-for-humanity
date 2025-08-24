# 📚 Adaptive Systems API Reference

## Overview

The Adaptive Systems API provides programmatic access to all personalization and learning features in Luminous Nix. This reference covers the unified integration system and all five adaptive subsystems.

## Quick Start

```python
from luminous_nix.consciousness.unified_integration import get_unified_system

# Get the global unified system
system = get_unified_system()

# Process a command with full adaptation
result = system.process_command(
    command="install firefox",
    user_id="user123"
)

# Access adapted response
print(result["ui_config"]["complexity_level"])  # e.g., "standard"
print(result["voice_profile"]["tone"])          # e.g., "patient"
```

## Core Classes

### UnifiedAdaptiveSystem

The master orchestrator for all adaptive features.

```python
class UnifiedAdaptiveSystem:
    def __init__(self, enable_all: bool = True)
    def get_or_create_persona(self, user_id: str) -> DynamicPersona
    def process_command(self, command: str, user_id: str = "default") -> Dict[str, Any]
    def adapt_response(self, response: str, user_id: str = "default", speak: bool = False) -> str
    def get_system_status(self) -> Dict[str, Any]
```

#### Methods

##### `__init__(enable_all: bool = True)`
Initialize the unified system.

**Parameters:**
- `enable_all`: Enable all adaptive subsystems (default: True)

**Example:**
```python
# Full system
system = UnifiedAdaptiveSystem(enable_all=True)

# Selective initialization
system = UnifiedAdaptiveSystem(enable_all=False)
system.voice_system = AdaptiveVoiceSystem()  # Only voice
```

##### `process_command(command: str, user_id: str = "default") -> Dict[str, Any]`
Process a command with full adaptive stack.

**Parameters:**
- `command`: The user's command
- `user_id`: Unique user identifier

**Returns:**
```python
{
    "command": str,
    "user_id": str,
    "adaptations": {
        "error_prevention": bool,
        "ui_complexity": bool,
        "voice": bool,
        "learning_path": bool
    },
    "potential_errors": List[PotentialError],  # If any
    "suggested_command": str,  # If correction available
    "ui_config": {
        "complexity_level": str,
        "font_size": int,
        "show_hints": bool,
        "max_options": int
    },
    "voice_profile": {
        "tone": str,
        "speed": float,
        "warmth": float
    },
    "learning": {
        "next_objective": str,
        "estimated_time": int
    }
}
```

### DynamicPersona

Represents a user's evolving profile.

```python
@dataclass
class DynamicPersona:
    user_id: str
    technical_proficiency: float = 0.5  # 0.0 to 1.0
    preferred_verbosity: float = 0.5    # 0.0 (terse) to 1.0 (verbose)
    patience_level: float = 0.5         # 0.0 (impatient) to 1.0 (patient)
    exploration_tendency: float = 0.5   # 0.0 (cautious) to 1.0 (adventurous)
    confidence_level: float = 0.5       # 0.0 to 1.0
    frustration_level: float = 0.0      # 0.0 to 1.0
    learning_speed: float = 0.5         # 0.0 (slow) to 1.0 (fast)
    current_mood: EmotionalState = EmotionalState.NEUTRAL
    interaction_count: int = 0
    success_rate: float = 0.5
    peak_hours: List[int] = field(default_factory=lambda: [9, 10, 14, 15])
```

#### Emotional States

```python
class EmotionalState(Enum):
    NEUTRAL = "neutral"
    FRUSTRATED = "frustrated"
    CONFUSED = "confused"
    SATISFIED = "satisfied"
    CURIOUS = "curious"
    RUSHED = "rushed"
    LEARNING = "learning"
    FOCUSED = "focused"
```

### PersonaLearningEngine

Manages persona learning and adaptation.

```python
class PersonaLearningEngine:
    def get_or_create_persona(self, user_id: str) -> DynamicPersona
    def learn_from_interaction(self, user_id: str, interaction: Interaction) -> DynamicPersona
    def predict_success(self, user_id: str, command: str) -> float
    def get_recommendations(self, user_id: str) -> List[str]
```

#### Interaction Object

```python
@dataclass
class Interaction:
    timestamp: datetime
    command: str
    success: bool
    response_time_ms: int
    error_message: Optional[str] = None
    used_advanced_feature: bool = False
    reading_time_ms: Optional[int] = None
    retry_count: int = 0
    help_requested: bool = False
```

## Adaptive Subsystems

### 1. Adaptive Voice System

```python
class AdaptiveVoiceSystem:
    def adapt_to_persona(self, persona: DynamicPersona) -> VoiceProfile
    def speak_with_emotion(self, text: str, persona: DynamicPersona, play_audio: bool = True)
    def get_voice_analytics(self) -> Dict[str, Any]
```

#### Voice Tones

```python
class VoiceTone(Enum):
    CALM = "calm"           # Soothing, stress reduction
    ENCOURAGING = "encouraging"  # Supportive, learning
    EFFICIENT = "efficient"      # Quick, minimal
    PATIENT = "patient"          # Slow, clear
    CELEBRATORY = "celebratory"  # Joyful, success
    GENTLE = "gentle"            # Soft, frustration
    FOCUSED = "focused"          # Clear, complex tasks
```

#### Voice Profile

```python
@dataclass
class VoiceProfile:
    tone: VoiceTone
    speed: float      # 0.5 to 2.0
    pitch: float      # 0.5 to 2.0
    volume: float     # 0.0 to 1.0
    warmth: float     # 0.0 to 1.0
    clarity: float    # 0.0 to 1.0
```

### 2. Adaptive UI System

```python
class AdaptiveUISystem:
    def determine_complexity_level(self, persona: DynamicPersona) -> UIComplexityLevel
    def adapt_ui(self, persona: DynamicPersona) -> AdaptiveUIConfig
    def get_visible_elements(self, all_elements: List[UIElement], level: UIComplexityLevel = None) -> List[UIElement]
    def suggest_level_change(self, persona: DynamicPersona) -> Optional[UIComplexityLevel]
    def create_progressive_reveal(self, elements: List[UIElement], persona: DynamicPersona) -> List[Tuple[UIElement, float]]
```

#### UI Complexity Levels

```python
class UIComplexityLevel(Enum):
    MINIMAL = "minimal"      # Just essentials
    SIMPLE = "simple"        # Basic features
    STANDARD = "standard"    # Common features
    ADVANCED = "advanced"    # Power features
    EXPERT = "expert"        # Everything
```

#### UI Configuration

```python
@dataclass
class AdaptiveUIConfig:
    font_size: int = 14
    line_spacing: float = 1.2
    color_contrast: float = 1.0
    animation_speed: float = 1.0
    max_options_visible: int = 10
    show_descriptions: bool = True
    show_shortcuts: bool = False
    show_advanced_options: bool = False
    show_hints: bool = True
    auto_suggest: bool = True
    confirm_dangerous: bool = True
    explain_actions: bool = True
    compact_mode: bool = False
    show_technical_details: bool = False
```

### 3. Proactive Error Prevention

```python
class ProactiveErrorPrevention:
    def analyze_command(self, command: str, persona: DynamicPersona = None) -> List[PotentialError]
    def suggest_correction(self, command: str, errors: List[PotentialError]) -> Optional[str]
    def learn_from_error(self, command: str, error_message: str, solution: str = None, persona: DynamicPersona = None)
    def get_prevention_stats(self) -> Dict[str, Any]
```

#### Error Categories

```python
class ErrorCategory(Enum):
    TYPO = "typo"                    # Misspellings
    PERMISSION = "permission"         # Missing sudo
    DEPENDENCY = "dependency"         # Missing deps
    SYNTAX = "syntax"                # Command syntax
    STATE = "state"                  # System conflicts
    RESOURCE = "resource"            # Low resources
    COMPATIBILITY = "compatibility"   # Version issues
    DANGEROUS = "dangerous"          # Destructive ops
```

#### Potential Error

```python
@dataclass
class PotentialError:
    category: ErrorCategory
    risk_level: ErrorRisk
    description: str
    prevention_suggestion: str
    confidence: float  # 0.0 to 1.0
    command: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
```

### 4. Personalized Learning System

```python
class PersonalizedLearningSystem:
    def create_learning_path(self, persona: DynamicPersona, focus: TopicCategory = None) -> PersonalizedPath
    def get_next_objective(self, user_id: str) -> Optional[LearningObjective]
    def update_progress(self, user_id: str, objective_id: str, success: bool, notes: str = None)
    def get_learning_recommendations(self, user_id: str, persona: DynamicPersona) -> List[str]
    def get_progress_summary(self, user_id: str) -> Dict[str, Any]
```

#### Learning Components

```python
class SkillLevel(Enum):
    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class LearningStyle(Enum):
    VISUAL = "visual"
    TEXTUAL = "textual"
    PRACTICAL = "practical"
    CONCEPTUAL = "conceptual"
    SOCIAL = "social"

class TopicCategory(Enum):
    BASICS = "basics"
    CONFIGURATION = "configuration"
    DEVELOPMENT = "development"
    ADVANCED = "advanced"
    TROUBLESHOOTING = "troubleshooting"
    OPTIMIZATION = "optimization"
    CUSTOMIZATION = "customization"
```

### 5. Voice-Enabled CLI Integration

```python
class VoiceEnabledCLI:
    def __init__(self, enable_voice: bool = True, tts_engine: str = "espeak-ng", auto_speak: bool = False)
    def respond(self, text: str, user_id: str = "default", speak: bool = None) -> str
    def update_emotional_state(self, user_id: str, interaction_type: str, success: bool)
    def speak_notification(self, message: str, urgency: str = "normal", user_id: str = "default")
    def get_voice_status(self) -> Dict[str, Any]
```

## Usage Examples

### Example 1: Basic Adaptation

```python
from luminous_nix.consciousness.unified_integration import UnifiedAdaptiveSystem

# Initialize system
system = UnifiedAdaptiveSystem()

# Process command for new user
result = system.process_command("install firefox", "new_user")

# Check adaptations
if result.get("potential_errors"):
    print("Errors prevented:", result["potential_errors"])
    
if result.get("suggested_command"):
    print("Suggestion:", result["suggested_command"])

print(f"UI Level: {result['ui_config']['complexity_level']}")
print(f"Voice Tone: {result['voice_profile']['tone']}")
```

### Example 2: Learning from Errors

```python
from luminous_nix.consciousness.adaptive_persona import Interaction
from datetime import datetime

# Create interaction record
interaction = Interaction(
    timestamp=datetime.now(),
    command="nixos-rebuild switch",
    success=False,
    response_time_ms=500,
    error_message="Permission denied"
)

# Learn from failure
persona = system.persona_engine.learn_from_interaction("user123", interaction)

# System will now suggest sudo for this user
next_result = system.process_command("nixos-rebuild switch", "user123")
print(next_result["suggested_command"])  # "sudo nixos-rebuild switch"
```

### Example 3: Progressive UI Reveal

```python
# Check what UI elements to show
ui_system = system.ui_system
persona = system.get_or_create_persona("user123")

# Get visible elements for user's level
from luminous_nix.ui.adaptive_complexity import NIXOS_UI_ELEMENTS
visible = ui_system.get_visible_elements(NIXOS_UI_ELEMENTS)

for element in visible:
    print(f"{element.name}: {element.help_text}")

# Check if user ready for next level
suggested_level = ui_system.suggest_level_change(persona)
if suggested_level:
    print(f"Consider moving to {suggested_level.value} mode")
```

### Example 4: Personalized Learning

```python
# Create learning path
learning = system.learning_system
persona = system.get_or_create_persona("learner")

path = learning.create_learning_path(
    persona,
    focus=TopicCategory.DEVELOPMENT
)

# Get next objective
next_obj = learning.get_next_objective("learner")
print(f"Next: {next_obj.title}")
print(f"Time: {next_obj.estimated_time_minutes} minutes")
print(f"Practice: {next_obj.practice_commands}")

# Update progress
learning.update_progress(
    "learner",
    next_obj.id,
    success=True,
    notes="Completed easily"
)
```

### Example 5: Voice Adaptation

```python
# Adapt voice to emotional state
from luminous_nix.consciousness.adaptive_persona import EmotionalState

persona = system.get_or_create_persona("user123")
persona.current_mood = EmotionalState.FRUSTRATED
persona.frustration_level = 0.8

# System automatically uses GENTLE tone
response = system.adapt_response(
    "There was an error with your command",
    "user123",
    speak=True  # Will speak with gentle, slower voice
)
```

## Configuration

### Environment Variables

```bash
# Enable/disable adaptive features
export LUMINOUS_NIX_ADAPTIVE=true
export LUMINOUS_NIX_VOICE=true
export LUMINOUS_NIX_UI_ADAPTATION=true
export LUMINOUS_NIX_ERROR_PREVENTION=true
export LUMINOUS_NIX_LEARNING_PATHS=true

# Set default levels
export LUMINOUS_NIX_DEFAULT_UI_LEVEL=standard
export LUMINOUS_NIX_DEFAULT_VOICE_TONE=calm
```

### Configuration File

```yaml
# ~/.config/luminous-nix/adaptive.yaml
adaptive:
  enabled: true
  
  persona:
    learning_rate: 0.1  # How fast to adapt
    min_interactions: 5  # Before significant changes
    
  voice:
    engine: espeak-ng
    default_tone: calm
    auto_speak: false
    
  ui:
    default_level: standard
    allow_suggestions: true
    progressive_reveal: true
    
  error_prevention:
    enabled: true
    auto_correct_typos: true
    confirm_dangerous: true
    
  learning:
    enabled: true
    default_style: practical
    pace: normal
```

## Performance Considerations

### Memory Usage
- Each persona: ~10KB
- Interaction history: ~1KB per 100 interactions
- Learning paths: ~5KB per user

### CPU Impact
- Persona updates: <10ms
- Error analysis: <50ms per command
- UI adaptation: <5ms
- Voice synthesis: Depends on TTS engine

### Optimization Tips

```python
# Batch persona updates
interactions = []
for cmd in commands:
    interactions.append(process_command(cmd))
    
# Update once at end
system.persona_engine.batch_update(user_id, interactions)

# Disable unused features
system = UnifiedAdaptiveSystem(enable_all=False)
system.ui_system = AdaptiveUISystem()  # Only what you need

# Use caching for predictions
@lru_cache(maxsize=100)
def get_cached_prediction(user_id, command):
    return system.persona_engine.predict_success(user_id, command)
```

## Error Handling

```python
try:
    result = system.process_command(command, user_id)
except Exception as e:
    # Fallback to non-adaptive mode
    logger.error(f"Adaptive system error: {e}")
    result = basic_process_command(command)
    
# Check for partial failures
if not result.get("adaptations", {}).get("voice"):
    logger.warning("Voice adaptation failed, using default")
```

## Testing

```python
import pytest
from luminous_nix.consciousness.unified_integration import UnifiedAdaptiveSystem

def test_persona_adaptation():
    system = UnifiedAdaptiveSystem()
    
    # Simulate beginner
    result1 = system.process_command("instal firefox", "test_user")
    assert result1.get("suggested_command") == "install firefox"
    
    # Simulate learning
    for _ in range(10):
        system.process_command("install package", "test_user")
    
    # Check adaptation
    persona = system.get_or_create_persona("test_user")
    assert persona.technical_proficiency > 0.5

def test_error_prevention():
    system = UnifiedAdaptiveSystem()
    
    # Test dangerous command detection
    result = system.process_command("rm -rf /", "test_user")
    assert any(e.category == ErrorCategory.DANGEROUS 
              for e in result.get("potential_errors", []))
```

## Migration Guide

### From Static Personas

```python
# Old way (static personas)
from luminous_nix.consciousness.persona_adapter import PersonaAdapter
adapter = PersonaAdapter()
persona = adapter.get_persona("grandma_rose")  # Fixed persona

# New way (dynamic personas)
from luminous_nix.consciousness.unified_integration import get_unified_system
system = get_unified_system()
persona = system.get_or_create_persona("user123")  # Unique, evolving
```

### Backwards Compatibility

The system provides a compatibility layer:

```python
# Old code still works
from luminous_nix.consciousness.unified_integration import PersonaAdapter
adapter = PersonaAdapter()  # Compatibility wrapper
```

## Troubleshooting

### Common Issues

**Issue**: Persona not updating
```python
# Check interaction buffer
print(system.persona_engine.interaction_buffer.get(user_id, []))

# Force update
interaction = Interaction(...)
system.persona_engine.learn_from_interaction(user_id, interaction)
```

**Issue**: Wrong complexity level
```python
# Override automatic detection
persona = system.get_or_create_persona(user_id)
persona.technical_proficiency = 0.8  # Set manually
system.ui_system.current_level = UIComplexityLevel.ADVANCED
```

**Issue**: Voice not working
```python
# Check voice system status
status = system.get_system_status()
print(status["systems"]["voice"])  # Should be True

# Test TTS engine
system.voice_system.test_tts()
```

## Advanced Topics

### Custom Learning Algorithms

```python
class CustomLearningEngine(PersonaLearningEngine):
    def learn_from_interaction(self, user_id, interaction):
        persona = super().learn_from_interaction(user_id, interaction)
        
        # Custom learning logic
        if "flake" in interaction.command:
            persona.technical_proficiency += 0.1
            
        return persona
```

### Plugin Integration

```python
from luminous_nix.plugins import AdaptivePlugin

class MyAdaptivePlugin(AdaptivePlugin):
    def on_persona_update(self, persona):
        # React to persona changes
        pass
        
    def on_error_prevented(self, error):
        # Log prevented errors
        pass
```

### Extending Emotional States

```python
# Add custom emotional states
EmotionalState.INSPIRED = "inspired"
EmotionalState.OVERWHELMED = "overwhelmed"

# Map to voice tones
EMOTION_TO_TONE_EXTENDED = {
    EmotionalState.INSPIRED: VoiceTone.CELEBRATORY,
    EmotionalState.OVERWHELMED: VoiceTone.GENTLE,
}
```

## API Versioning

Current version: **1.0.0**

The API follows semantic versioning:
- **Major**: Breaking changes
- **Minor**: New features, backwards compatible
- **Patch**: Bug fixes

Check version:
```python
from luminous_nix.consciousness import __version__
print(__version__)  # 1.0.0
```

---

## Further Reading

- [Adaptive Features Guide](../ADAPTIVE_FEATURES_GUIDE.md) - User-facing documentation
- [Dynamic User Modeling](../02-ARCHITECTURE/03-DYNAMIC-USER-MODELING.md) - Research background
- [Privacy First Onboarding](../PRIVACY_FIRST_ONBOARDING.md) - Privacy considerations

---

*API Reference Version 1.0.0 - Last updated: Session continuation*