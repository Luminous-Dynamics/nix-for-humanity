#!/usr/bin/env python3
"""
🎵 Tests for Adaptive Voice System
Verifies that voice adapts correctly to different emotional states
"""

import pytest
from pathlib import Path
import tempfile
from unittest.mock import MagicMock, patch, call

from luminous_nix.voice.unified_voice import (
    UnifiedVoiceSystem,
    VoiceTone,
    VoiceProfile,
    VOICE_PROFILES
)
from luminous_nix.consciousness.adaptive_persona import (
    DynamicPersona,
    EmotionalState
)


class TestAdaptiveVoiceSystem:
    """Test suite for adaptive voice functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.voice_system = UnifiedVoiceSystem(tts_engine="espeak-ng")
        
        # Create test personas with different states
        self.calm_user = DynamicPersona(
            user_id="calm_user",
            current_mood=EmotionalState.FOCUSED,
            technical_proficiency=0.7,
            patience_level=0.8,
            frustration_level=0.1,
            confidence_level=0.8
        )
        
        self.frustrated_user = DynamicPersona(
            user_id="frustrated_user",
            current_mood=EmotionalState.FRUSTRATED,
            technical_proficiency=0.3,
            patience_level=0.2,
            frustration_level=0.8,
            confidence_level=0.3
        )
        
        self.curious_user = DynamicPersona(
            user_id="curious_user",
            current_mood=EmotionalState.CURIOUS,
            technical_proficiency=0.5,
            patience_level=0.6,
            frustration_level=0.2,
            confidence_level=0.5,
            exploration_tendency=0.9
        )
        
        self.satisfied_user = DynamicPersona(
            user_id="satisfied_user",
            current_mood=EmotionalState.SATISFIED,
            technical_proficiency=0.6,
            patience_level=0.7,
            frustration_level=0.1,
            confidence_level=0.9
        )
    
    def test_voice_profile_selection(self):
        """Test that correct voice profiles are selected for emotional states"""
        # Test each emotional state maps to expected profile
        for state, expected_profile in VOICE_PROFILES.items():
            persona = DynamicPersona(
                user_id="test",
                current_mood=state
            )
            profile = self.voice_system.adapt_to_persona(persona)
            
            # Base tone should match
            assert profile.tone == expected_profile.tone
    
    def test_frustration_adaptation(self):
        """Test that frustrated users get gentler, slower voice"""
        profile = self.voice_system.adapt_to_persona(self.frustrated_user)
        
        # Should use gentle tone
        assert profile.tone == VoiceTone.GENTLE
        
        # Should be slower
        assert profile.speed < 1.0
        
        # Should have high warmth
        assert profile.warmth >= 0.9
        
        # Should have lower volume
        assert profile.volume < 0.7
    
    def test_expert_user_adaptation(self):
        """Test that expert users get faster, more efficient voice"""
        expert = DynamicPersona(
            user_id="expert",
            technical_proficiency=0.9,
            patience_level=0.5,
            current_mood=EmotionalState.FOCUSED
        )
        
        profile = self.voice_system.adapt_to_persona(expert)
        
        # Should be faster than base
        base_speed = VOICE_PROFILES[EmotionalState.FOCUSED].speed
        assert profile.speed > base_speed
        
        # Should have shorter pauses
        base_pause = VOICE_PROFILES[EmotionalState.FOCUSED].pause_length
        assert profile.pause_length < base_pause
    
    def test_beginner_user_adaptation(self):
        """Test that beginners get slower, more patient voice"""
        beginner = DynamicPersona(
            user_id="beginner",
            technical_proficiency=0.2,
            patience_level=0.6,
            current_mood=EmotionalState.LEARNING
        )
        
        profile = self.voice_system.adapt_to_persona(beginner)
        
        # Should be slower
        base_speed = VOICE_PROFILES[EmotionalState.LEARNING].speed
        assert profile.speed < base_speed
        
        # Should have longer pauses
        base_pause = VOICE_PROFILES[EmotionalState.LEARNING].pause_length
        assert profile.pause_length > base_pause
    
    def test_time_of_day_adaptation(self):
        """Test that voice adapts to time of day"""
        from datetime import datetime
        from unittest.mock import patch
        
        # Test late night (should be quieter, calmer)
        with patch('luminous_nix.voice.adaptive_voice.datetime') as mock_dt:
            mock_dt.now.return_value.hour = 2  # 2 AM
            
            profile = self.voice_system.adapt_to_persona(self.calm_user)
            
            # Should use calm tone
            assert profile.tone == VoiceTone.CALM
            
            # Should be quieter
            assert profile.volume < 0.7
    
    def test_content_adaptation_frustrated(self):
        """Test that text content is adapted for frustrated users"""
        original_text = "Here's how to configure the system."
        
        adapted = self.voice_system._adapt_text_content(
            original_text,
            self.frustrated_user
        )
        
        # Should add empathetic prefix
        assert "understand" in adapted.lower()
        assert "frustrating" in adapted.lower()
        
        # Should offer more help
        assert "help" in adapted.lower()
    
    def test_content_adaptation_confused(self):
        """Test that text content is adapted for confused users"""
        original_text = "Configure the network settings."
        
        confused_user = DynamicPersona(
            user_id="confused",
            current_mood=EmotionalState.CONFUSED
        )
        
        adapted = self.voice_system._adapt_text_content(
            original_text,
            confused_user
        )
        
        # Should add explanatory prefix
        assert "step by step" in adapted.lower()
    
    def test_content_adaptation_satisfied(self):
        """Test that text content celebrates satisfied users"""
        original_text = "Configuration complete."
        
        satisfied_user = DynamicPersona(
            user_id="satisfied",
            current_mood=EmotionalState.SATISFIED
        )
        
        adapted = self.voice_system._adapt_text_content(
            original_text,
            satisfied_user
        )
        
        # Should add celebratory prefix
        assert any(word in adapted for word in ["Great", "Excellent", "Perfect"])
    
    @patch('subprocess.run')
    def test_espeak_generation(self, mock_run):
        """Test espeak-ng speech generation with correct parameters"""
        # Mock espeak being available
        self.voice_system.available_engines['espeak-ng'] = True
        
        profile = VoiceProfile(
            tone=VoiceTone.CALM,
            speed=0.8,
            pitch=0.9,
            volume=0.6,
            pause_length=1.0,
            emphasis_level=0.3,
            warmth=0.8
        )
        
        with tempfile.NamedTemporaryFile(suffix='.wav') as tmp:
            self.voice_system._generate_espeak(
                "Test text",
                profile,
                Path(tmp.name)
            )
            
            # Check espeak was called with correct parameters
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            
            assert 'espeak-ng' in call_args
            assert '-s' in call_args  # Speed parameter
            assert '-p' in call_args  # Pitch parameter
            assert '-a' in call_args  # Amplitude parameter
            assert '-v' in call_args  # Voice variant
    
    def test_voice_caching(self):
        """Test that generated speech is cached"""
        text = "Test caching"
        profile = self.voice_system.current_profile
        
        with patch.object(self.voice_system, '_generate_espeak') as mock_gen:
            # First call should generate
            self.voice_system.generate_speech(text, profile)
            assert mock_gen.call_count == 1
            
            # Second call should use cache
            self.voice_system.generate_speech(text, profile)
            assert mock_gen.call_count == 1  # Still 1, not 2
    
    def test_peak_hours_adaptation(self):
        """Test voice adapts during user's peak productivity hours"""
        productive_user = DynamicPersona(
            user_id="productive",
            current_mood=EmotionalState.FOCUSED,
            peak_hours=[9, 10, 11, 14, 15, 16]  # Morning and afternoon
        )
        
        with patch('luminous_nix.voice.adaptive_voice.datetime') as mock_dt:
            # During peak hour
            mock_dt.now.return_value.hour = 10
            
            profile = self.voice_system.adapt_to_persona(productive_user)
            base_speed = VOICE_PROFILES[EmotionalState.FOCUSED].speed
            
            # Should be slightly faster during peak hours
            assert profile.speed > base_speed
    
    def test_impatient_user_adaptation(self):
        """Test that impatient users get faster responses"""
        impatient_user = DynamicPersona(
            user_id="impatient",
            patience_level=0.2,
            current_mood=EmotionalState.RUSHED
        )
        
        profile = self.voice_system.adapt_to_persona(impatient_user)
        
        # Should be fast
        assert profile.speed > 1.2
        
        # Should have minimal pauses
        assert profile.pause_length < 0.3
        
        # Should use focused tone
        assert profile.tone == VoiceTone.FOCUSED
    
    def test_low_confidence_adaptation(self):
        """Test that low confidence users get more encouragement"""
        nervous_user = DynamicPersona(
            user_id="nervous",
            confidence_level=0.2,
            current_mood=EmotionalState.LEARNING
        )
        
        profile = self.voice_system.adapt_to_persona(nervous_user)
        base_emphasis = VOICE_PROFILES[EmotionalState.LEARNING].emphasis_level
        
        # Should have more emphasis for encouragement
        assert profile.emphasis_level > base_emphasis
    
    def test_voice_analytics(self):
        """Test voice analytics reporting"""
        analytics = self.voice_system.get_voice_analytics()
        
        assert 'current_tone' in analytics
        assert 'current_speed' in analytics
        assert 'current_warmth' in analytics
        assert 'available_engines' in analytics
        assert 'active_engine' in analytics
        assert analytics['active_engine'] == 'espeak-ng'
    
    @patch('subprocess.run')
    def test_speak_with_emotion_integration(self, mock_run):
        """Test full integration of speaking with emotion"""
        # Mock audio player availability
        mock_run.return_value.returncode = 0
        
        text = "Installation complete!"
        
        # Speak to satisfied user
        audio_file = self.voice_system.speak_with_emotion(
            text,
            self.satisfied_user,
            play_audio=False  # Don't actually play
        )
        
        # Should return a path
        assert audio_file is not None
        
        # Voice should have adapted to satisfied state
        assert self.voice_system.current_profile.tone == VoiceTone.CELEBRATORY


class TestVoiceProfiles:
    """Test predefined voice profiles"""
    
    def test_all_states_have_profiles(self):
        """Ensure all emotional states have voice profiles"""
        for state in EmotionalState:
            assert state in VOICE_PROFILES
            profile = VOICE_PROFILES[state]
            
            # Validate profile parameters
            assert 0.5 <= profile.speed <= 2.0
            assert 0.5 <= profile.pitch <= 2.0
            assert 0.0 <= profile.volume <= 1.0
            assert 0.0 <= profile.pause_length <= 2.0
            assert 0.0 <= profile.emphasis_level <= 1.0
            assert 0.0 <= profile.warmth <= 1.0
    
    def test_tone_variety(self):
        """Ensure we use a variety of voice tones"""
        tones_used = set()
        for profile in VOICE_PROFILES.values():
            tones_used.add(profile.tone)
        
        # Should use at least 5 different tones
        assert len(tones_used) >= 5
    
    def test_frustrated_profile_is_patient(self):
        """Frustrated users should get patient handling"""
        profile = VOICE_PROFILES[EmotionalState.FRUSTRATED]
        
        assert profile.tone == VoiceTone.PATIENT
        assert profile.speed < 1.0  # Slower
        assert profile.warmth > 0.8  # Very warm
        assert profile.pause_length > 0.5  # Longer pauses
    
    def test_rushed_profile_is_efficient(self):
        """Rushed users should get quick, efficient handling"""
        profile = VOICE_PROFILES[EmotionalState.RUSHED]
        
        assert profile.tone == VoiceTone.FOCUSED
        assert profile.speed > 1.2  # Faster
        assert profile.pause_length < 0.3  # Short pauses
        assert profile.emphasis_level < 0.3  # Less dramatic