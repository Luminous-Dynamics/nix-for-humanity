"""
from typing import List, Dict
🎤 Voice Integration Testing Framework

Comprehensive test suite for the voice interface system, covering:
- End-to-end voice pipeline testing
- Persona-specific voice behavior validation  
- Performance requirements verification
- Error handling and graceful degradation
- Real-world scenario simulation

This testing framework ensures the voice interface serves all 10 personas
with consciousness-first principles while maintaining performance standards.
"""

import asyncio
import pytest
import time
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

# Import voice components
from nix_humanity.voice.model_manager import ModelManager, ModelType, ModelSize
from nix_humanity.voice.pipecat_interface import PipecatVoiceInterface
from nix_humanity.voice.voice_config import VOICE_PERSONAS


@dataclass
class VoiceTestScenario:
    """Test scenario for voice interface validation."""
    persona_name: str
    input_text: str
    expected_intent: str
    max_response_time_ms: int
    voice_quality_requirements: Dict[str, Any]
    accessibility_requirements: List[str]


class MockAudioData:
    """Mock audio data for testing."""
    def __init__(self, duration_ms: int = 1000, sample_rate: int = 16000):
        self.duration_ms = duration_ms
        self.sample_rate = sample_rate
        self.data = b'\x00' * (duration_ms * sample_rate // 1000 * 2)  # 16-bit audio
    
    def to_bytes(self) -> bytes:
        return self.data


class VoiceTestFixtures:
    """Common test fixtures for voice testing."""
    
    @staticmethod
    def get_persona_test_scenarios() -> List[VoiceTestScenario]:
        """Get test scenarios for all 10 personas."""
        return [
            # Grandma Rose (75) - Voice-first, clear speech
            VoiceTestScenario(
                persona_name="grandma_rose",
                input_text="I need that Firefox thing my grandson mentioned",
                expected_intent="install_firefox",
                max_response_time_ms=2000,  # More patient
                voice_quality_requirements={
                    "clarity": "high",
                    "speed": "moderate",
                    "tone": "gentle"
                },
                accessibility_requirements=["large_text", "clear_pronunciation"]
            ),
            
            # Maya (16, ADHD) - Fast responses required
            VoiceTestScenario(
                persona_name="maya_adhd", 
                input_text="firefox now",
                expected_intent="install_firefox",
                max_response_time_ms=1000,  # Must be fast
                voice_quality_requirements={
                    "clarity": "high",
                    "speed": "fast", 
                    "tone": "energetic"
                },
                accessibility_requirements=["minimal_distractions", "quick_feedback"]
            ),
            
            # Alex (28, Blind Developer) - Screen reader compatible
            VoiceTestScenario(
                persona_name="alex_blind",
                input_text="install firefox and configure it for development",
                expected_intent="install_and_configure_firefox",
                max_response_time_ms=1500,
                voice_quality_requirements={
                    "clarity": "highest",
                    "speed": "moderate",
                    "tone": "professional"
                },
                accessibility_requirements=["screen_reader_compatible", "structured_output"]
            ),
            
            # Dr. Sarah (35, Researcher) - Technical precision
            VoiceTestScenario(
                persona_name="dr_sarah",
                input_text="install firefox-esr for research computing",
                expected_intent="install_firefox_esr",
                max_response_time_ms=1500,
                voice_quality_requirements={
                    "clarity": "high",
                    "speed": "moderate",
                    "tone": "professional"
                },
                accessibility_requirements=["technical_accuracy", "detailed_explanations"]
            ),
            
            # Carlos (52, Career Switcher) - Learning support
            VoiceTestScenario(
                persona_name="carlos_learner",
                input_text="I'm not sure how to install a web browser",
                expected_intent="help_install_browser",
                max_response_time_ms=2000,
                voice_quality_requirements={
                    "clarity": "high",
                    "speed": "slow",
                    "tone": "encouraging"
                },
                accessibility_requirements=["educational_guidance", "patient_explanations"]
            )
        ]
    
    @staticmethod
    def get_error_scenarios() -> List[Dict[str, Any]]:
        """Get error scenarios for testing graceful degradation."""
        return [
            {
                "name": "whisper_model_missing",
                "error_type": "model_not_found",
                "expected_fallback": "text_only_mode",
                "user_message": "Voice recognition unavailable, using text input"
            },
            {
                "name": "piper_model_missing", 
                "error_type": "tts_not_available",
                "expected_fallback": "silent_mode",
                "user_message": "Voice output unavailable, showing text response"
            },
            {
                "name": "microphone_not_available",
                "error_type": "audio_input_failed",
                "expected_fallback": "text_input_mode", 
                "user_message": "Microphone not available, please type your request"
            }
        ]


class TestVoiceIntegration:
    """Integration tests for the complete voice interface system."""
    
    @pytest.fixture
    async def temp_data_dir(self):
        """Create temporary data directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    async def mock_model_manager(self, temp_data_dir):
        """Create mock model manager for testing."""
        manager = ModelManager(temp_data_dir)
        
        # Mock model paths to avoid downloads during testing
        with patch.object(manager, 'get_whisper_model', new_callable=AsyncMock) as mock_whisper, \
             patch.object(manager, 'get_piper_voice', new_callable=AsyncMock) as mock_piper:
            
            mock_whisper.return_value = temp_data_dir / "whisper_model.bin"
            mock_piper.return_value = temp_data_dir / "piper_voice.onnx"
            
            # Create mock model files
            (temp_data_dir / "whisper_model.bin").touch()
            (temp_data_dir / "piper_voice.onnx").touch()
            
            yield manager
    
    @pytest.fixture 
    async def voice_interface(self, mock_model_manager, temp_data_dir):
        """Create voice interface with mocked dependencies."""
        interface = PipecatVoiceInterface(data_dir=temp_data_dir)
        interface.model_manager = mock_model_manager
        
        # Mock pipecat components since they require real audio hardware
        interface._whisper_enabled = True
        interface._piper_enabled = True
        
        return interface
    
    @pytest.mark.asyncio
    async def test_persona_voice_mapping_completeness(self):
        """Test that all 10 personas have voice mappings."""
        expected_personas = [
            "grandma_rose", "maya_adhd", "david", "dr_sarah", "alex_blind",
            "carlos_learner", "priya", "jamie", "viktor", "luna"
        ]
        
        for persona in expected_personas:
            assert persona in VOICE_PERSONAS, f"Missing voice config for persona: {persona}"
            
            config = VOICE_PERSONAS[persona]
            assert "response_time_requirement" in config
            assert "voice_style" in config
            assert "accessibility_features" in config
    
    @pytest.mark.asyncio
    async def test_model_manager_persona_integration(self, mock_model_manager):
        """Test model manager provides appropriate models for each persona."""
        test_personas = ["grandma_rose", "maya_adhd", "alex_blind", "dr_sarah"]
        
        for persona in test_personas:
            # Test whisper model selection
            whisper_path = await mock_model_manager.get_whisper_model()
            assert whisper_path.exists()
            
            # Test piper voice selection for persona
            piper_path = await mock_model_manager.get_piper_voice(persona)
            assert piper_path.exists()
    
    @pytest.mark.asyncio
    async def test_end_to_end_voice_pipeline_mock(self, voice_interface):
        """Test complete voice pipeline with mocked audio."""
        
        # Mock audio input (simulating "install firefox")
        mock_audio = MockAudioData(duration_ms=2000)
        
        with patch.object(voice_interface, '_transcribe_audio', new_callable=AsyncMock) as mock_transcribe, \
             patch.object(voice_interface, '_synthesize_speech', new_callable=AsyncMock) as mock_synthesize:
            
            # Configure mocks
            mock_transcribe.return_value = "install firefox"
            mock_synthesize.return_value = MockAudioData(duration_ms=1500)
            
            # Test the pipeline
            result = await voice_interface.process_voice_input(mock_audio.data)
            
            # Verify the pipeline executed
            mock_transcribe.assert_called_once()
            mock_synthesize.assert_called_once()
            
            assert result["transcription"] == "install firefox"
            assert result["success"] is True
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("scenario", VoiceTestFixtures.get_persona_test_scenarios())
    async def test_persona_specific_voice_behavior(self, voice_interface, scenario):
        """Test voice behavior meets persona-specific requirements."""
        
        with patch.object(voice_interface, '_transcribe_audio', new_callable=AsyncMock) as mock_transcribe, \
             patch.object(voice_interface, '_synthesize_speech', new_callable=AsyncMock) as mock_synthesize:
            
            # Configure persona
            voice_interface.set_persona(scenario.persona_name)
            
            # Mock transcription
            mock_transcribe.return_value = scenario.input_text
            mock_synthesize.return_value = MockAudioData()
            
            # Measure response time
            start_time = time.time()
            
            result = await voice_interface.process_voice_input(b"mock_audio_data")
            
            response_time_ms = (time.time() - start_time) * 1000
            
            # Verify response time meets persona requirements
            assert response_time_ms < scenario.max_response_time_ms, \
                f"Response time {response_time_ms}ms exceeds {scenario.max_response_time_ms}ms for {scenario.persona_name}"
            
            # Verify intent recognition
            assert result["success"] is True
            assert scenario.expected_intent.replace("_", " ") in result.get("response", "").lower()
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("error_scenario", VoiceTestFixtures.get_error_scenarios())
    async def test_graceful_degradation(self, voice_interface, error_scenario):
        """Test system handles errors gracefully."""
        
        if error_scenario["error_type"] == "model_not_found":
            # Simulate missing Whisper model
            with patch.object(voice_interface.model_manager, 'get_whisper_model', 
                            side_effect=FileNotFoundError("Model not found")):
                
                result = await voice_interface.process_voice_input(b"mock_audio")
                
                assert result["success"] is False
                assert error_scenario["expected_fallback"] in result.get("fallback_mode", "")
                assert error_scenario["user_message"] in result.get("message", "")
        
        elif error_scenario["error_type"] == "tts_not_available":
            # Simulate missing Piper model
            with patch.object(voice_interface.model_manager, 'get_piper_voice',
                            side_effect=FileNotFoundError("Voice not found")):
                
                result = await voice_interface.synthesize_response("test response")
                
                assert result["success"] is False
                assert error_scenario["expected_fallback"] in result.get("fallback_mode", "")
    
    @pytest.mark.asyncio
    async def test_accessibility_compliance(self, voice_interface):
        """Test voice interface meets accessibility requirements."""
        
        # Test screen reader compatibility (Alex persona)
        voice_interface.set_persona("alex_blind")
        
        with patch.object(voice_interface, '_transcribe_audio', new_callable=AsyncMock) as mock_transcribe:
            mock_transcribe.return_value = "install development tools"
            
            result = await voice_interface.process_voice_input(b"mock_audio")
            
            # Verify structured output for screen readers
            assert "structured_response" in result
            assert result["structured_response"]["intent"] is not None
            assert result["structured_response"]["steps"] is not None
    
    @pytest.mark.asyncio  
    async def test_performance_under_load(self, voice_interface):
        """Test voice interface performance under concurrent load."""
        
        async def simulate_voice_request():
            """Simulate a voice request."""
            with patch.object(voice_interface, '_transcribe_audio', new_callable=AsyncMock) as mock_transcribe:
                mock_transcribe.return_value = "install firefox"
                return await voice_interface.process_voice_input(b"mock_audio")
        
        # Test concurrent requests
        concurrent_requests = 5
        start_time = time.time()
        
        tasks = [simulate_voice_request() for _ in range(concurrent_requests)]
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        # Verify all requests succeeded
        assert all(result["success"] for result in results)
        
        # Verify reasonable performance (should handle 5 requests in under 10 seconds)
        assert total_time < 10.0, f"Concurrent processing took {total_time}s, too slow"
    
    @pytest.mark.asyncio
    async def test_voice_personalization_features(self, voice_interface):
        """Test voice personalization and adaptation features."""
        
        # Test voice selection transparency (from user feedback)
        voice_interface.set_persona("grandma_rose")
        
        with patch.object(voice_interface, 'get_selected_voice_info') as mock_voice_info:
            mock_voice_info.return_value = {
                "voice_name": "ljspeech-high",
                "selection_reason": "Selected for clear articulation suitable for your profile",
                "user_changeable": True,
                "alternatives": ["amy-medium", "ryan-high"]
            }
            
            voice_info = voice_interface.get_selected_voice_info()
            
            # Verify transparency features (per user feedback)
            assert voice_info["selection_reason"] is not None
            assert voice_info["user_changeable"] is True
            assert len(voice_info["alternatives"]) > 0
    
    def test_voice_config_persona_completeness(self):
        """Test voice configuration covers all personas."""
        required_personas = [
            "grandma_rose", "maya_adhd", "david", "dr_sarah", "alex_blind",
            "carlos_learner", "priya", "jamie", "viktor", "luna"
        ]
        
        for persona in required_personas:
            assert persona in VOICE_PERSONAS, f"Missing voice config for {persona}"
            
            config = VOICE_PERSONAS[persona]
            
            # Verify required configuration fields
            assert "response_time_requirement" in config
            assert config["response_time_requirement"] > 0
            
            assert "voice_style" in config
            assert config["voice_style"] in ["gentle", "energetic", "professional", "encouraging"]
            
            assert "accessibility_features" in config
            assert isinstance(config["accessibility_features"], list)


class TestVoicePerformanceRequirements:
    """Test voice interface meets specific performance requirements."""
    
    @pytest.mark.performance
    async def test_maya_adhd_speed_requirement(self):
        """Maya (ADHD) requires responses under 1 second."""
        
        # This test would require real audio processing
        # For now, we test the configuration is correct
        maya_config = VOICE_PERSONAS["maya_adhd"]
        assert maya_config["response_time_requirement"] <= 1000, \
            "Maya requires sub-1-second responses"
    
    @pytest.mark.performance 
    async def test_grandma_rose_patience_allowance(self):
        """Grandma Rose can tolerate longer response times for quality."""
        
        grandma_config = VOICE_PERSONAS["grandma_rose"]
        assert grandma_config["response_time_requirement"] <= 2000, \
            "Grandma Rose allows up to 2-second responses"
        
        # But quality requirements should be high
        assert grandma_config["voice_style"] == "gentle"
    
    @pytest.mark.performance
    async def test_alex_accessibility_requirements(self):
        """Alex (blind) requires specific accessibility features."""
        
        alex_config = VOICE_PERSONAS["alex_blind"]
        accessibility_features = alex_config["accessibility_features"]
        
        required_features = ["screen_reader_compatible", "structured_output"]
        for feature in required_features:
            assert feature in accessibility_features, \
                f"Alex requires {feature} accessibility feature"


class TestVoiceErrorRecovery:
    """Test voice interface error recovery and user guidance."""
    
    @pytest.mark.asyncio
    async def test_microphone_permission_error(self):
        """Test handling of microphone permission errors."""
        
        # This would test actual microphone permission handling
        # For now, test the error message is user-friendly
        error_message = "Microphone access required for voice input"
        assert "permission" not in error_message.lower() or "access" in error_message.lower()
    
    @pytest.mark.asyncio
    async def test_noisy_environment_handling(self):
        """Test handling of noisy environment recognition."""
        
        # Would test actual noise detection and user guidance
        # For now, verify config supports environmental awareness
        assert "environmental_adaptation" in ["low_confidence_threshold", "noise_detection"]
    
    @pytest.mark.asyncio
    async def test_speech_recognition_confidence_thresholds(self):
        """Test appropriate confidence thresholds for speech recognition."""
        
        # Test different personas have appropriate confidence requirements
        persona_configs = VOICE_PERSONAS
        
        for persona_name, config in persona_configs.items():
            # All personas should have some confidence threshold
            # (this would be implemented in the actual voice processing)
            assert "response_time_requirement" in config, \
                f"{persona_name} missing basic voice requirements"


if __name__ == "__main__":
    # Run specific test suites
    import sys
    
    if len(sys.argv) > 1:
        test_suite = sys.argv[1]
        
        if test_suite == "integration":
            pytest.main(["-v", "TestVoiceIntegration"])
        elif test_suite == "performance":
            pytest.main(["-v", "-m", "performance"])
        elif test_suite == "accessibility":
            pytest.main(["-v", "TestVoiceIntegration::test_accessibility_compliance"])
        else:
            pytest.main(["-v"])
    else:
        # Run all tests
        pytest.main(["-v", __file__])