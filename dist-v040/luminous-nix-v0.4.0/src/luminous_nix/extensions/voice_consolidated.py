"""Consolidated voice extension for Luminous Nix."""


class VoiceInterface:
    """Optional voice interface for natural speech interaction."""

    def __init__(self):
        self.enabled = False
        self.piper_available = False
        self.whisper_available = False

    def enable(self):
        """Enable voice interface if dependencies available."""
        try:
            import pyttsx3
            import speech_recognition

            self.enabled = True
            return True
        except ImportError:
            return False

    def listen(self) -> str:
        """Listen for voice input."""
        if not self.enabled:
            return ""
        # Implementation when enabled
        return ""

    def speak(self, text: str):
        """Speak text output."""
        if not self.enabled:
            return
        # Implementation when enabled
        pass
