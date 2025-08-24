#!/usr/bin/env python3
"""
🧠 CLI Consciousness Integration

Hooks the signal collector into the CLI to capture real user interactions
and adapt the system's behavior based on detected consciousness state.
"""

import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from ..consciousness.signal_collector import RealTimeSignalCollector, IntegrationBridge
    from ..consciousness.consciousness_detector import ConsciousnessBarometer
    from ..voice.unified_voice import UnifiedVoiceSystem
except ImportError:
    # For standalone execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from luminous_nix.consciousness.signal_collector import RealTimeSignalCollector, IntegrationBridge
    from luminous_nix.consciousness.consciousness_detector import ConsciousnessBarometer
    from luminous_nix.voice.unified_voice import UnifiedVoiceSystem

logger = logging.getLogger(__name__)


class ConsciousnessAwareCLI:
    """
    Makes the CLI consciousness-aware by tracking user interactions
    and adapting responses based on detected state.
    """
    
    def __init__(self):
        """Initialize consciousness-aware CLI components"""
        # Core components
        self.signal_collector = RealTimeSignalCollector()
        self.consciousness_barometer = ConsciousnessBarometer()
        self.bridge = IntegrationBridge(self.signal_collector, self.consciousness_barometer)
        self.voice_interface = UnifiedVoiceSystem()
        
        # State tracking
        self.last_command = None
        self.command_start_time = None
        self.current_reading = None
        
        # Adaptation settings
        self.adaptive_responses = True
        self.show_consciousness_hints = False  # Show hints about detected state
        
        logger.info("🧠 Consciousness-aware CLI initialized")
    
    def before_command(self, command: str):
        """
        Called before executing a command.
        Records the command and timing.
        """
        self.last_command = command
        self.command_start_time = time.time()
        
        # Record command in signal collector
        self.signal_collector.record_command(command)
        
        # Check if we should update consciousness
        self.current_reading = self.bridge.maybe_update()
        
        # Log state if changed significantly
        if self.current_reading:
            logger.debug(f"Consciousness state: {self.current_reading.quality}")
    
    def after_command(self, command: str, success: bool, result: Any = None):
        """
        Called after executing a command.
        Records execution time and any errors.
        """
        if self.command_start_time:
            execution_time = time.time() - self.command_start_time
            
            # Record timing
            if execution_time > 0:
                self.signal_collector.inter_command_times.append(execution_time)
        
        # Record errors if command failed
        if not success:
            self.signal_collector.record_error("command_failed", str(result))
        
        # Update consciousness after command
        self.current_reading = self.bridge.update_consciousness()
    
    def on_help_request(self, topic: str = None):
        """Called when user requests help"""
        self.signal_collector.record_help_request(topic)
        
        # Immediately update consciousness for help requests
        self.current_reading = self.bridge.update_consciousness()
    
    def on_error(self, error_type: str, error_message: str = None):
        """Called when an error occurs"""
        self.signal_collector.record_error(error_type, error_message)
        
        # Update consciousness for errors
        self.current_reading = self.bridge.update_consciousness()
    
    def get_adaptive_response(self, base_response: str) -> str:
        """
        Adapt response based on consciousness state.
        
        Args:
            base_response: The original response text
            
        Returns:
            Adapted response appropriate for user's state
        """
        if not self.adaptive_responses or not self.current_reading:
            return base_response
        
        quality = self.current_reading.quality
        
        # Adapt based on consciousness quality
        if quality == "overwhelmed":
            # Simplify and be extra supportive
            response = f"💚 {base_response}\n"
            if "error" in base_response.lower():
                response += "\n💡 Tip: Take a breath. Let's solve this step by step."
            return response
            
        elif quality == "frustrated":
            # Be encouraging and offer shortcuts
            response = base_response
            if "failed" in base_response.lower() or "error" in base_response.lower():
                response += "\n\n💪 Don't worry, this happens to everyone. Try: ask-nix help"
            return response
            
        elif quality == "flow":
            # Minimal, fast responses
            # Remove any verbose explanations
            lines = base_response.split('\n')
            essential_lines = [l for l in lines if not l.startswith('  ') or '✓' in l or '✗' in l]
            return '\n'.join(essential_lines)
            
        elif quality == "learning":
            # Add educational context
            response = base_response
            if any(word in self.last_command for word in ['install', 'search', 'configure']):
                response += "\n\n📚 Learn more: ask-nix explain " + self.last_command.split()[0]
            return response
            
        else:
            return base_response
    
    def get_voice_parameters(self) -> Dict[str, Any]:
        """Get voice parameters based on current consciousness state"""
        if not self.current_reading:
            return {}
        
        # Get consciousness-adapted voice parameters
        consciousness_state = {
            'quality': self.current_reading.quality,
            'user_state': self.current_reading.spectrum.state
        }
        
        params = self.voice_interface.adapt_voice_to_consciousness(
            "Response",
            consciousness_state
        )
        
        return params.to_dict()
    
    def should_offer_break(self) -> bool:
        """Check if we should suggest a break"""
        summary = self.signal_collector.get_state_summary()
        
        # Suggest break if:
        # - Session > 45 minutes
        # - High cognitive load
        # - Overwhelmed state
        session_minutes = self.signal_collector.get_consciousness_signals()['session_duration']
        
        if session_minutes > 45:
            return True
        if summary['cognitive_load'] == 'high' and session_minutes > 20:
            return True
        if summary['likely_state'] == 'overwhelmed':
            return True
            
        return False
    
    def get_consciousness_hint(self) -> Optional[str]:
        """Get a hint about current consciousness state (if enabled)"""
        if not self.show_consciousness_hints or not self.current_reading:
            return None
        
        quality = self.current_reading.quality
        energy = self.current_reading.energy_level
        stability = self.current_reading.stability
        
        # Generate appropriate hint
        if quality == "flow":
            return "🌊 You're in flow - maintaining momentum..."
        elif quality == "overwhelmed":
            return "🫂 I sense you might be feeling overwhelmed. I'm here to help."
        elif quality == "learning":
            return "📖 Learning mode detected - providing extra context..."
        elif quality == "frustrated":
            return "💝 I understand this is frustrating. Let's find a simpler way."
        elif energy < 0.3:
            return "☕ Low energy detected - keeping things simple..."
        elif stability < 0.3:
            return "🌱 Let's take this one step at a time..."
        
        return None
    
    def format_for_consciousness(self, text: str, format_type: str = "output") -> str:
        """
        Format text based on consciousness state.
        
        Args:
            text: Text to format
            format_type: Type of formatting (output, error, help, etc.)
            
        Returns:
            Formatted text appropriate for user's state
        """
        if not self.current_reading:
            return text
        
        quality = self.current_reading.quality
        
        if quality == "overwhelmed":
            # Use more whitespace and clearer structure
            lines = text.split('\n')
            formatted = []
            for line in lines:
                if line.strip():
                    formatted.append(line)
                    if not line.startswith(' '):
                        formatted.append('')  # Extra space after headers
            return '\n'.join(formatted)
            
        elif quality == "flow":
            # Compact format for flow state
            lines = text.split('\n')
            # Remove empty lines
            formatted = [l for l in lines if l.strip()]
            return '\n'.join(formatted)
            
        else:
            return text
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session"""
        signals = self.signal_collector.get_consciousness_signals()
        summary = self.signal_collector.get_state_summary()
        
        # Add consciousness insights
        if self.current_reading:
            summary['consciousness_quality'] = self.current_reading.quality
            summary['energy_level'] = f"{self.current_reading.energy_level:.1%}"
            summary['stability'] = f"{self.current_reading.stability:.1%}"
        
        # Add recommendations
        recommendations = []
        
        if self.should_offer_break():
            recommendations.append("Consider taking a break")
        
        if summary['error_rate'] == 'high':
            recommendations.append("Try 'ask-nix help' for guidance")
        
        if summary['cognitive_load'] == 'high':
            recommendations.append("Consider simpler commands")
        
        summary['recommendations'] = recommendations
        
        return summary
    
    def reset_session(self):
        """Reset for a new session"""
        self.signal_collector.reset_session()
        self.current_reading = None
        self.last_command = None
        
        logger.info("🧠 Consciousness tracking reset for new session")


# Global instance for CLI integration
consciousness_cli = None

def get_consciousness_cli() -> ConsciousnessAwareCLI:
    """Get or create the global consciousness CLI instance"""
    global consciousness_cli
    if consciousness_cli is None:
        consciousness_cli = ConsciousnessAwareCLI()
    return consciousness_cli


def integrate_with_cli(cli_instance):
    """
    Integrate consciousness awareness with an existing CLI.
    
    This should be called by the main CLI to add consciousness tracking.
    """
    consciousness = get_consciousness_cli()
    
    # Hook into CLI methods
    original_execute = cli_instance.execute if hasattr(cli_instance, 'execute') else None
    
    def consciousness_aware_execute(command: str, *args, **kwargs):
        # Before command
        consciousness.before_command(command)
        
        # Execute original
        try:
            if original_execute:
                result = original_execute(command, *args, **kwargs)
            else:
                result = None
            
            # After successful command
            consciousness.after_command(command, True, result)
            
            # Adapt response if it's a string
            if isinstance(result, str):
                result = consciousness.get_adaptive_response(result)
            
            return result
            
        except Exception as e:
            # After failed command
            consciousness.after_command(command, False, str(e))
            consciousness.on_error("execution_error", str(e))
            raise
    
    # Replace execute method
    if hasattr(cli_instance, 'execute'):
        cli_instance.execute = consciousness_aware_execute
    
    logger.info("🧠 Consciousness integration complete")
    
    return consciousness


def demonstrate_consciousness_cli():
    """Demonstrate consciousness-aware CLI features"""
    print("\n🧠 Consciousness-Aware CLI Demonstration")
    print("=" * 50)
    
    cli = ConsciousnessAwareCLI()
    
    # Simulate a user session
    print("\n1. Simulating normal workflow...")
    commands = ["install firefox", "search editor", "configure git"]
    
    for cmd in commands:
        cli.before_command(cmd)
        time.sleep(0.5)  # Simulate execution
        cli.after_command(cmd, True)
        
        response = f"✓ Executed: {cmd}"
        adapted = cli.get_adaptive_response(response)
        print(f"   {adapted}")
    
    print("\n2. Simulating learning with errors...")
    cli.on_help_request("nix commands")
    cli.before_command("nix-env -i firefox")
    cli.on_error("command_not_found", "nix-env not found")
    cli.after_command("nix-env -i firefox", False)
    
    response = "❌ Error: Command failed"
    adapted = cli.get_adaptive_response(response)
    print(f"   {adapted}")
    
    hint = cli.get_consciousness_hint()
    if hint:
        print(f"   {hint}")
    
    print("\n3. Session summary...")
    summary = cli.get_session_summary()
    print(f"   Session: {summary['session_length']}")
    print(f"   Activity: {summary['activity']}")
    print(f"   State: {summary.get('likely_state', 'unknown')}")
    
    if summary.get('recommendations'):
        print("   Recommendations:")
        for rec in summary['recommendations']:
            print(f"     • {rec}")
    
    print("\n" + "=" * 50)
    print("✅ Consciousness CLI demonstration complete!")


if __name__ == "__main__":
    demonstrate_consciousness_cli()