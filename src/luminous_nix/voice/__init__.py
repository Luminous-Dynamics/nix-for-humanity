"""
🎤 Luminous Nix Voice Interface Module
Natural voice interaction with consciousness-first design

Features:
- Natural speech recognition (Whisper/SpeechRecognition)
- Expressive speech synthesis (Piper/pyttsx3)
- Sacred pauses and flow protection
- Seamless CLI/TUI/GUI integration
- Multi-persona support
"""

__version__ = "1.0.0"

# Core components (always available)
from .sacred_voice_interface import (
    SacredVoiceInterface,
    VoiceConfig,
    FlowState,
    InterruptionLevel,
    create_voice_interface
)

# NLP Bridge (optional - may have dependencies)
try:
    from .voice_nlp_bridge import (
        VoiceNLPBridge,
        VoiceContext,
        create_voice_bridge
    )
    NLP_BRIDGE_AVAILABLE = True
except ImportError:
    VoiceNLPBridge = None
    VoiceContext = None
    create_voice_bridge = None
    NLP_BRIDGE_AVAILABLE = False

# CLI Integration (optional - requires click)
try:
    from .voice_cli_integration import (
        voice as voice_cli_group,
        start_voice_mode,
        add_voice_to_cli,
        load_voice_config,
        save_voice_config
    )
    CLI_INTEGRATION_AVAILABLE = True
except ImportError:
    voice_cli_group = None
    start_voice_mode = None
    add_voice_to_cli = None
    load_voice_config = None
    save_voice_config = None
    CLI_INTEGRATION_AVAILABLE = False

# TUI Integration (optional - requires textual)
try:
    from .voice_tui_integration import (
        VoiceStatusWidget,
        VoiceControlPanel,
        VoiceHistoryWidget,
        VoiceTUIIntegration,
        integrate_voice_with_tui,
        VOICE_TUI_CSS
    )
    TUI_INTEGRATION_AVAILABLE = True
except ImportError:
    VoiceStatusWidget = None
    VoiceControlPanel = None
    VoiceHistoryWidget = None
    VoiceTUIIntegration = None
    integrate_voice_with_tui = None
    VOICE_TUI_CSS = ""
    TUI_INTEGRATION_AVAILABLE = False

# Export main interface
__all__ = [
    # Core (always available)
    'SacredVoiceInterface',
    'VoiceConfig',
    'FlowState',
    'InterruptionLevel',
    'create_voice_interface',

    # Availability flags
    'NLP_BRIDGE_AVAILABLE',
    'CLI_INTEGRATION_AVAILABLE',
    'TUI_INTEGRATION_AVAILABLE',

    # Bridge (optional)
    'VoiceNLPBridge',
    'VoiceContext',
    'create_voice_bridge',

    # CLI (optional)
    'voice_cli_group',
    'start_voice_mode',
    'add_voice_to_cli',
    'load_voice_config',
    'save_voice_config',

    # TUI (optional)
    'VoiceStatusWidget',
    'VoiceControlPanel',
    'VoiceHistoryWidget',
    'VoiceTUIIntegration',
    'integrate_voice_with_tui',
    'VOICE_TUI_CSS',

    # Utility functions
    'is_voice_available',
    'get_voice_status',
]


def is_voice_available() -> bool:
    """Check if core voice dependencies are available"""
    try:
        import speech_recognition
        import pyttsx3
        return True
    except ImportError:
        return False


def get_voice_status() -> dict:
    """Get voice system status"""
    status = {
        'core_available': False,
        'whisper_available': False,
        'piper_available': False,
        'speech_recognition': False,
        'text_to_speech': False,
        'nlp_bridge': NLP_BRIDGE_AVAILABLE,
        'cli_integration': CLI_INTEGRATION_AVAILABLE,
        'tui_integration': TUI_INTEGRATION_AVAILABLE,
    }

    try:
        import speech_recognition
        status['speech_recognition'] = True
        status['core_available'] = True
    except ImportError:
        pass

    try:
        import pyttsx3
        status['text_to_speech'] = True
    except ImportError:
        pass

    try:
        import whisper
        status['whisper_available'] = True
    except ImportError:
        pass

    return status
