# 🎤 Voice Personalization Design - Future Considerations

*Respecting user agency in voice interface adaptation*

## Overview

While our system can intelligently detect and suggest appropriate voices for different personas, true consciousness-first design requires transparency and user control. This document outlines future enhancements to make voice selection more respectful of user preferences and agency.

## Core Principles

### 1. Transparency First
Users should always know what the system is doing and why. Auto-selection should be a helpful suggestion, not a hidden decision.

### 2. User Agency
The user always has the final say. Any automatic selection can be overridden, and the system learns from these choices.

### 3. Intelligent Adaptation
The system should learn not just which voice a user prefers, but understand relational preferences ("voices like this one").

## Proposed Implementation

### Voice Selection Flow

```python
class VoicePersonalizationEngine:
    """Future enhancement for voice selection with user agency"""
    
    async def select_voice_with_transparency(self, detected_persona: str, user_profile: UserProfile) -> VoiceSelection:
        # 1. Check if user has explicit preference
        if user_profile.voice_preference:
            return VoiceSelection(
                voice_id=user_profile.voice_preference,
                reason="Using your preferred voice",
                is_user_choice=True
            )
        
        # 2. Check learned preferences
        if learned_preference := self.get_learned_preference(user_profile):
            return VoiceSelection(
                voice_id=learned_preference,
                reason="Using voice similar to ones you've chosen before",
                is_learned=True
            )
        
        # 3. Suggest based on persona
        suggested_voice = PERSONA_VOICE_MAP.get(detected_persona)
        return VoiceSelection(
            voice_id=suggested_voice,
            reason=f"Suggested voice for {detected_persona} profile",
            is_suggestion=True,
            confidence=0.7
        )
```

### User Notification System

```python
class VoiceAnnouncementSystem:
    """Transparent communication about voice selection"""
    
    def announce_voice_selection(self, selection: VoiceSelection) -> str:
        if selection.is_user_choice:
            return "Using your selected voice."
        
        elif selection.is_learned:
            return (
                f"I've selected a voice similar to ones you've preferred. "
                f"Say 'change voice' anytime to pick a different one."
            )
        
        else:  # Auto-selected
            return (
                f"I've selected a voice that might work well for you. "
                f"This is just a suggestion - say 'change voice' to hear other options."
            )
```

### Voice Change Interface

```python
class VoiceChangeDialog:
    """User-friendly voice selection interface"""
    
    async def handle_voice_change_request(self) -> None:
        # Announce current voice
        await self.tts.speak(
            "I'm currently using the Amy voice. "
            "Would you like to hear other options?"
        )
        
        if await self.get_confirmation():
            # Present options with examples
            for voice_id, voice_info in self.available_voices:
                await self.tts.speak_with_voice(
                    f"This is the {voice_info.name} voice. "
                    f"It's {voice_info.description}.",
                    voice_id=voice_id
                )
                
                response = await self.get_user_response(
                    "Would you like to use this voice? "
                    "Say yes, no, or 'more options'."
                )
                
                if response == "yes":
                    await self.set_user_voice(voice_id)
                    await self.learn_preference(voice_id)
                    break
```

## Intelligent Preference Learning

### Relational Voice Mapping

```python
class VoicePreferenceLearner:
    """Learn voice preferences beyond exact matches"""
    
    def __init__(self):
        # Voice features for similarity matching
        self.voice_features = {
            "en_US-amy-medium": {
                "gender": "female",
                "speed": "medium",
                "pitch": "medium",
                "clarity": "high",
                "warmth": "friendly"
            },
            # ... other voices
        }
    
    def find_similar_voices(self, preferred_voice: str, similarity_threshold: float = 0.7) -> List[str]:
        """Find voices similar to user's preference"""
        preferred_features = self.voice_features[preferred_voice]
        similar_voices = []
        
        for voice_id, features in self.voice_features.items():
            if voice_id == preferred_voice:
                continue
                
            similarity = self.calculate_similarity(preferred_features, features)
            if similarity > similarity_threshold:
                similar_voices.append((voice_id, similarity))
        
        return [v[0] for v in sorted(similar_voices, key=lambda x: x[1], reverse=True)]
    
    def learn_from_choice(self, user_id: str, chosen_voice: str, rejected_voice: str) -> None:
        """Learn from user's voice selection decisions"""
        # Update preference model
        self.preference_model.add_preference(
            user_id=user_id,
            preferred=self.voice_features[chosen_voice],
            rejected=self.voice_features[rejected_voice]
        )
        
        # Identify preference patterns
        patterns = self.identify_patterns(user_id)
        # e.g., "User prefers female voices with medium speed"
```

### Contextual Voice Preferences

```python
class ContextualVoiceManager:
    """Different voices for different contexts"""
    
    def __init__(self):
        self.context_preferences = {}
    
    def learn_contextual_preference(self, user_id: str, context: Context, voice_id: str) -> None:
        """Learn that user prefers certain voices in certain contexts"""
        # Context might include:
        # - Time of day (morning vs evening)
        # - Task type (system updates vs casual chat)
        # - Mood indicators (stressed vs relaxed)
        # - Environment (quiet vs noisy)
        
        key = (user_id, context.type)
        if key not in self.context_preferences:
            self.context_preferences[key] = {}
        
        self.context_preferences[key][context.value] = voice_id
    
    def get_contextual_voice(self, user_id: str, current_context: Context) -> Optional[str]:
        """Get voice preference for current context"""
        key = (user_id, current_context.type)
        if key in self.context_preferences:
            return self.context_preferences[key].get(current_context.value)
        return None
```

## User Control Interface

### Voice Commands

```yaml
Voice Management Commands:
  - "change voice" / "switch voice" / "different voice"
  - "I don't like this voice"
  - "speak slower" / "speak faster" 
  - "use a male/female voice"
  - "use a calmer voice" / "use a more energetic voice"
  - "what voices are available?"
  - "go back to my usual voice"
  - "remember this voice for [context]"
  - "use different voices for different times"
```

### Settings Persistence

```python
class VoicePreferenceStorage:
    """Persistent storage of voice preferences"""
    
    def save_preferences(self, user_id: str, preferences: VoicePreferences) -> None:
        """Save to local privacy-preserving storage"""
        data = {
            "primary_voice": preferences.primary_voice,
            "contextual_voices": preferences.contextual_voices,
            "rejected_voices": preferences.rejected_voices,
            "feature_preferences": preferences.feature_preferences,
            "last_updated": datetime.now().isoformat()
        }
        
        # Encrypt and store locally
        encrypted = self.encrypt(json.dumps(data))
        self.storage.save(f"voice_prefs_{user_id}", encrypted)
```

## Privacy Considerations

### Local-Only Learning
- All voice preferences stored locally
- No sharing of voice selection patterns
- User can delete all preferences anytime
- Export/import preferences for backup

### Consent for Learning
```python
def request_learning_consent(self) -> None:
    """Ask user if system can learn from their choices"""
    message = (
        "I notice you've changed voices a few times. "
        "Would you like me to learn from your choices "
        "to make better suggestions in the future? "
        "This information stays completely private on your device."
    )
    # Get explicit consent before enabling learning
```

## Implementation Priority

### Phase 1: Basic Transparency (Sprint 2)
- Announce voice selection
- Simple voice change command
- Save explicit preferences

### Phase 2: Intelligent Learning (Sprint 3)
- Similarity-based recommendations
- Learn from rejections
- Pattern identification

### Phase 3: Contextual Adaptation (Sprint 4)
- Time-based preferences
- Task-based preferences
- Mood-responsive selection

## Success Metrics

- User changes voice less often over time (system learns well)
- Satisfaction with auto-selected voices increases
- Users report feeling in control
- Reduced friction in voice interactions

## Related Documentation

- [Model Management System](../../../src/nix_for_humanity/voice/model_manager.py)
- [Voice Config](../../../src/nix_for_humanity/voice/voice_config.py)
- [Learning System Architecture](./09-LEARNING-SYSTEM.md)
- [Privacy Architecture](./11-PRIVACY-ARCHITECTURE.md)

---

*"True intelligence is not about making perfect choices for users, but about learning how to better support the choices they want to make."*

**Status**: Future Enhancement Proposal  
**Priority**: High (Phase 3)  
**Aligns with**: Consciousness-First Computing, User Agency, Privacy-First Design