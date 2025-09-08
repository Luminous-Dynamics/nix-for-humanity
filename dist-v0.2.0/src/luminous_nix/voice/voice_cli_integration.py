"""
🎙️ Voice-CLI Integration for Luminous Nix
Seamlessly adds voice capabilities to the command-line interface
"""

import click
import logging
import sys
from pathlib import Path
from typing import Optional

from .sacred_voice_interface import VoiceConfig, InterruptionLevel
from .voice_nlp_bridge import VoiceNLPBridge, create_voice_bridge
from ..core.backend import LuminousNixBackend

logger = logging.getLogger(__name__)


@click.group(invoke_without_command=True)
@click.option('--voice', '-v', is_flag=True, help='Enable voice mode')
@click.option('--voice-only', is_flag=True, help='Voice-only mode (no text)')
@click.option('--personality', type=click.Choice(['gentle', 'energetic', 'professional']), 
              default='gentle', help='Voice personality')
@click.option('--verbosity', type=click.Choice(['minimal', 'normal', 'detailed']),
              default='normal', help='Response verbosity')
@click.option('--focus-protection/--no-focus-protection', default=True,
              help='Enable focus protection mode')
@click.pass_context
def voice(ctx, voice, voice_only, personality, verbosity, focus_protection):
    """
    Voice interface for Luminous Nix
    
    Examples:
        ask-nix voice                    # Start voice mode
        ask-nix voice --voice-only       # Voice-only (no text output)
        ask-nix voice --personality energetic
        ask-nix voice listen             # One-shot voice command
        ask-nix voice config             # Configure voice settings
    """
    
    if ctx.invoked_subcommand is None:
        # Start interactive voice mode
        start_voice_mode(
            voice_only=voice_only,
            personality=personality,
            verbosity=verbosity,
            focus_protection=focus_protection
        )


@voice.command()
@click.argument('command', required=False)
@click.pass_context
def listen(ctx, command):
    """
    Listen for a single voice command
    
    Examples:
        ask-nix voice listen
        ask-nix voice listen "then install firefox"
    """
    config = VoiceConfig(
        voice_personality=ctx.parent.params.get('personality', 'gentle'),
        focus_protection=ctx.parent.params.get('focus_protection', True)
    )
    
    backend = LuminousNixBackend()
    bridge = create_voice_bridge(backend, config)
    
    try:
        if command:
            # Process provided command
            bridge.voice.speak(f"Processing: {command}")
            response = bridge.process_voice_command(command)
            bridge.voice.speak(response)
        else:
            # Listen for one command
            bridge.voice.speak("Listening...")
            text = bridge.voice.listen(timeout=10)
            
            if text:
                response = bridge.process_voice_command(text)
                bridge.voice.speak(response)
            else:
                bridge.voice.speak("No command heard.")
                
    except KeyboardInterrupt:
        bridge.voice.speak("Goodbye!")
    except Exception as e:
        logger.error(f"Voice error: {e}")
        click.echo(f"Voice error: {e}", err=True)


@voice.command()
@click.option('--rate', type=int, help='Speech rate (100-300)')
@click.option('--volume', type=float, help='Volume (0.0-1.0)')
@click.option('--personality', type=click.Choice(['gentle', 'energetic', 'professional']))
@click.option('--verbosity', type=click.Choice(['minimal', 'normal', 'detailed']))
@click.option('--test', is_flag=True, help='Test voice with sample text')
def config(rate, volume, personality, verbosity, test):
    """
    Configure voice settings
    
    Examples:
        ask-nix voice config --rate 150
        ask-nix voice config --personality energetic
        ask-nix voice config --test
    """
    config = load_voice_config()
    
    if rate:
        config.voice_rate = rate
        click.echo(f"Speech rate set to {rate}")
    
    if volume is not None:
        config.voice_volume = max(0.0, min(1.0, volume))
        click.echo(f"Volume set to {config.voice_volume}")
    
    if personality:
        config.voice_personality = personality
        click.echo(f"Personality set to {personality}")
    
    # Save config
    save_voice_config(config)
    
    if test:
        # Test voice with current settings
        from .sacred_voice_interface import create_voice_interface
        voice = create_voice_interface(config)
        
        test_text = {
            'gentle': "Hello! I'm here to help you with NixOS in a gentle way.",
            'energetic': "Hey there! Ready to tackle some NixOS tasks together?",
            'professional': "Greetings. I am ready to assist with your NixOS requirements."
        }
        
        voice.speak(
            test_text.get(config.voice_personality, test_text['gentle']),
            InterruptionLevel.NORMAL
        )
        
        if verbosity:
            click.echo(f"Verbosity: {verbosity}")


@voice.command()
def status():
    """
    Show voice interface status
    
    Shows current configuration and statistics
    """
    config = load_voice_config()
    
    click.echo("Voice Interface Status")
    click.echo("=" * 40)
    click.echo(f"Personality: {config.voice_personality}")
    click.echo(f"Speech Rate: {config.voice_rate}")
    click.echo(f"Volume: {config.voice_volume}")
    click.echo(f"Focus Protection: {config.focus_protection}")
    click.echo(f"Sacred Pauses: {config.pause_before_speech}s before, {config.pause_after_listening}s after")
    
    # Check if dependencies are available
    try:
        import speech_recognition
        click.echo("✓ Speech recognition available")
    except ImportError:
        click.echo("✗ Speech recognition not installed")
    
    try:
        import pyttsx3
        click.echo("✓ Text-to-speech available")
    except ImportError:
        click.echo("✗ Text-to-speech not installed")
    
    try:
        import whisper
        click.echo("✓ Whisper (advanced) available")
    except ImportError:
        click.echo("✗ Whisper not installed (using basic recognition)")


def start_voice_mode(voice_only=False, personality='gentle', 
                    verbosity='normal', focus_protection=True):
    """
    Start interactive voice mode
    """
    click.echo("""
╔════════════════════════════════════════════════════════════╗
║         🎤 Luminous Nix Voice Interface                    ║
║                                                            ║
║  Commands:                                                ║
║    • Say commands naturally                               ║
║    • "Install Firefox"                                    ║
║    • "Search for editors"                                 ║
║    • "What's installed?"                                  ║
║                                                            ║
║  Voice Control:                                           ║
║    • "Speak louder/softer"                               ║
║    • "Speak faster/slower"                               ║
║    • "Be minimal/detailed"                               ║
║    • "Focus mode" / "Normal mode"                        ║
║    • "Take a breath" (sacred pause)                      ║
║                                                            ║
║  Press Ctrl+C to exit                                     ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Create voice configuration
    config = VoiceConfig(
        voice_personality=personality,
        focus_protection=focus_protection,
        use_acknowledgments=not voice_only,
        use_thinking_sounds=not voice_only
    )
    
    # Create backend and bridge
    backend = LuminousNixBackend()
    bridge = create_voice_bridge(backend, config)
    bridge.context.preferred_verbosity = verbosity
    
    # Start voice interface
    try:
        bridge.start()
        
        # If not voice-only, also show text output
        if not voice_only:
            def enhanced_processor(text):
                """Process with text output"""
                click.echo(f"\n👂 Heard: {text}")
                response = bridge.process_voice_command(text)
                click.echo(f"🗣️ Response: {response}")
                return response
            
            bridge.voice.on_command = enhanced_processor
        
        # Keep running
        click.echo("\n🎤 Voice interface active. Listening...")
        
        while True:
            try:
                import time
                time.sleep(1)
            except KeyboardInterrupt:
                break
                
    except KeyboardInterrupt:
        pass
    finally:
        bridge.stop()
        click.echo("\n👋 Voice interface stopped.")


def load_voice_config() -> VoiceConfig:
    """Load voice configuration from file"""
    config_path = Path.home() / ".config" / "luminous-nix" / "voice.json"
    
    if config_path.exists():
        import json
        with open(config_path, 'r') as f:
            data = json.load(f)
            return VoiceConfig(**data)
    
    return VoiceConfig()


def save_voice_config(config: VoiceConfig):
    """Save voice configuration to file"""
    config_path = Path.home() / ".config" / "luminous-nix" / "voice.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    import json
    with open(config_path, 'w') as f:
        json.dump({
            'voice_rate': config.voice_rate,
            'voice_volume': config.voice_volume,
            'voice_personality': config.voice_personality,
            'focus_protection': config.focus_protection,
            'pause_before_speech': config.pause_before_speech,
            'pause_after_listening': config.pause_after_listening,
            'use_acknowledgments': config.use_acknowledgments,
            'use_thinking_sounds': config.use_thinking_sounds,
        }, f, indent=2)


# Integration with main CLI
def add_voice_to_cli(cli_group):
    """
    Add voice commands to existing CLI
    
    Usage:
        from luminous_nix.cli import cli
        from luminous_nix.voice.voice_cli_integration import add_voice_to_cli
        
        add_voice_to_cli(cli)
    """
    cli_group.add_command(voice)