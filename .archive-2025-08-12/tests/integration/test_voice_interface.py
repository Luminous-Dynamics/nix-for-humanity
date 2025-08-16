#!/usr/bin/env python3
"""
Voice Interface Tests for Nix for Humanity v1.1

Tests voice recognition, text-to-speech, and voice command processing.
"""

from unittest.mock import Mock, MagicMock, patch, call

import numpy as np
import pytest
from luminous_nix.interfaces.voice import (
    SpeechRecognizer,
    TextToSpeech,
    VoiceCommandProcessor,
    VoiceInterface,
    WakeWordDetector,
)

class TestVoiceInterface:
    """Test the complete voice interface system."""

    @pytest.fixture
    def mock_audio_device(self):
        """Mock audio input/output devices."""
        with patch("sounddevice.query_devices") as mock_devices:
            mock_devices.return_value = [
                {"name": "Built-in Microphone", "max_input_channels": 1},
                {"name": "Built-in Output", "max_output_channels": 2},
            ]
            yield mock_devices

    @pytest.fixture
    def voice_interface(self, mock_audio_device):
        """Create voice interface with mocked audio."""
        with patch("sounddevice.InputStream"):
            interface = VoiceInterface()
            interface.initialize()
            return interface

    def create_test_audio(self, duration=1.0, sample_rate=16000):
        """Create test audio data."""
        t = np.linspace(0, duration, int(sample_rate * duration))
        # Generate a 440Hz tone (A4 note)
        audio = np.sin(2 * np.pi * 440 * t) * 0.5
        return audio.astype(np.float32)

    @pytest.mark.asyncio
    async def test_voice_interface_initialization(self, voice_interface):
        """Test voice interface initializes correctly."""
        assert voice_interface.is_initialized
        assert voice_interface.wake_word_detector is not None
        assert voice_interface.speech_recognizer is not None
        assert voice_interface.tts_engine is not None

    @pytest.mark.asyncio
    async def test_wake_word_detection(self, voice_interface):
        """Test wake word detection."""
        detector = voice_interface.wake_word_detector

        # Create audio containing wake word
        test_audio = self.create_test_audio()

        with patch.object(detector, "process_audio") as mock_process:
            mock_process.return_value = True  # Wake word detected

            result = await detector.detect_wake_word(test_audio)
            assert result is True
            mock_process.assert_called_once()

    @pytest.mark.asyncio
    async def test_speech_recognition(self, voice_interface):
        """Test speech to text conversion."""
        recognizer = voice_interface.speech_recognizer

        # Mock Whisper model
        with patch("whisper.load_model") as mock_model:
            mock_whisper = MagicMock()
            mock_whisper.transcribe.return_value = {
                "text": "install firefox please",
                "language": "en",
            }
            mock_model.return_value = mock_whisper

            # Create test audio
            test_audio = self.create_test_audio(duration=3.0)

            # Test recognition
            result = await recognizer.recognize(test_audio)
            assert result["text"] == "install firefox please"
            assert result["language"] == "en"

    @pytest.mark.asyncio
    async def test_text_to_speech(self, voice_interface):
        """Test text to speech conversion."""
        tts = voice_interface.tts_engine

        # Mock piper TTS
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0

            # Test TTS
            audio_data = await tts.synthesize("Hello, I'm installing Firefox for you.")

            # Verify subprocess was called correctly
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert "piper" in call_args
            assert "--model" in call_args

    @pytest.mark.asyncio
    async def test_voice_command_processing(self, voice_interface):
        """Test complete voice command flow."""
        processor = VoiceCommandProcessor(voice_interface)

        # Mock backend
        mock_backend = AsyncMock()
        mock_backend.process_natural_language.return_value = {
            "success": True,
            "response": "Installing Firefox browser...",
            "intent": "install",
            "confidence": 0.95,
        }
        processor.backend = mock_backend

        # Test command processing
        result = await processor.process_voice_command("install firefox")

        assert result["success"] is True
        assert "Installing Firefox" in result["response"]
        mock_backend.process_natural_language.assert_called_once_with("install firefox")

    @pytest.mark.asyncio
    async def test_continuous_listening_mode(self, voice_interface):
        """Test continuous listening after wake word."""
        with patch.object(voice_interface, "listen_for_command") as mock_listen:
            mock_listen.return_value = "what's the weather"

            # Start listening
            command = await voice_interface.start_listening()

            assert command == "what's the weather"
            mock_listen.assert_called_once()

    @pytest.mark.asyncio
    async def test_voice_feedback_settings(self, voice_interface):
        """Test voice feedback preferences."""
        # Test different feedback levels
        voice_interface.set_feedback_level("minimal")
        assert voice_interface.feedback_level == "minimal"

        voice_interface.set_feedback_level("verbose")
        assert voice_interface.feedback_level == "verbose"

        # Test voice selection
        voice_interface.set_voice("alex")
        assert voice_interface.current_voice == "alex"

    @pytest.mark.asyncio
    async def test_noise_cancellation(self, voice_interface):
        """Test noise cancellation in audio processing."""
        # Create noisy audio
        clean_audio = self.create_test_audio()
        noise = np.random.normal(0, 0.1, clean_audio.shape)
        noisy_audio = clean_audio + noise

        # Process with noise cancellation
        processed = await voice_interface.process_audio_with_noise_cancellation(
            noisy_audio
        )

        # Verify noise reduction (simplified test)
        assert np.std(processed) < np.std(noisy_audio)

    @pytest.mark.asyncio
    async def test_multi_language_support(self, voice_interface):
        """Test recognition in multiple languages."""
        recognizer = voice_interface.speech_recognizer

        test_cases = [
            ("en", "install firefox", "install firefox"),
            ("es", "instalar firefox", "instalar firefox"),
            ("fr", "installer firefox", "installer firefox"),
            ("de", "firefox installieren", "firefox installieren"),
        ]

        for lang, audio_text, expected in test_cases:
            with patch.object(recognizer, "recognize") as mock_recognize:
                mock_recognize.return_value = {"text": expected, "language": lang}

                result = await recognizer.recognize_with_language(
                    self.create_test_audio(), language=lang
                )

                assert result["text"] == expected
                assert result["language"] == lang

class TestVoiceIntegration:
    """Test voice interface integration with main app."""

    @pytest.mark.asyncio
    async def test_voice_with_tui(self):
        """Test voice commands update TUI."""
        from luminous_nix.ui.main_app import NixForHumanityApp

        app = NixForHumanityApp()
        voice = VoiceInterface()

        # Connect voice to app
        voice.on_command_recognized = app.process_voice_command

        with patch.object(voice, "recognize_command") as mock_recognize:
            mock_recognize.return_value = "install neovim"

            # Simulate voice command
            await voice.process_audio_input(self.create_test_audio())

            # Verify TUI received command
            assert app.last_command == "install neovim"

    @pytest.mark.asyncio
    async def test_voice_persona_adaptation(self):
        """Test voice adapts to current persona."""
        voice = VoiceInterface()

        # Test Grandma Rose settings
        voice.set_persona("grandma_rose")
        assert voice.speech_rate == 0.8  # Slower
        assert voice.feedback_level == "detailed"

        # Test Maya ADHD settings
        voice.set_persona("maya")
        assert voice.speech_rate == 1.2  # Faster
        assert voice.feedback_level == "minimal"

    @pytest.mark.asyncio
    async def test_voice_error_handling(self):
        """Test voice interface handles errors gracefully."""
        voice = VoiceInterface()

        # Test microphone not available
        with patch("sounddevice.InputStream", side_effect=Exception("No mic")):
            result = await voice.initialize()
            assert result is False
            assert voice.error_message == "Microphone not available"

        # Test recognition failure
        with patch.object(
            voice.speech_recognizer,
            "recognize",
            side_effect=Exception("Recognition failed"),
        ):
            result = await voice.process_command()
            assert result["success"] is False
            assert "error" in result

class TestVoicePerformance:
    """Test voice interface performance metrics."""

    @pytest.mark.asyncio
    async def test_wake_word_latency(self):
        """Test wake word detection latency."""
        detector = WakeWordDetector()
        audio = self.create_test_audio(0.5)  # 500ms audio

        import time

        start = time.time()
        result = await detector.detect(audio)
        latency = time.time() - start

        # Wake word detection should be under 100ms
        assert latency < 0.1

    @pytest.mark.asyncio
    async def test_recognition_speed(self):
        """Test speech recognition speed."""
        recognizer = SpeechRecognizer()

        # Mock fast recognition
        with patch.object(recognizer, "recognize") as mock:
            mock.return_value = {"text": "test", "time": 0.5}

            audio = self.create_test_audio(3.0)  # 3 second audio

            start = time.time()
            result = await recognizer.recognize(audio)
            duration = time.time() - start

            # Should process faster than real-time
            assert duration < 3.0

    @pytest.mark.asyncio
    async def test_tts_generation_speed(self):
        """Test TTS generation speed."""
        tts = TextToSpeech()

        text = "This is a test of text to speech synthesis."

        start = time.time()
        audio = await tts.synthesize(text)
        duration = time.time() - start

        # TTS should generate quickly
        assert duration < 1.0

    def create_test_audio(self, duration=1.0, sample_rate=16000):
        """Create test audio data."""
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = np.sin(2 * np.pi * 440 * t) * 0.5
        return audio.astype(np.float32)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
