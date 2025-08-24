#!/usr/bin/env python3
"""
🌊 Sacred Integration - Silent Consciousness Enhancement

This module integrates all sacred features into the normal CLI flow
without requiring any flags. The system naturally becomes sacred.
"""

import os
import time
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple

from .welcome_ceremony import create_welcome_ceremony
from .consciousness_detector import create_consciousness_barometer
from .semantic_memory_layer import create_semantic_memory
from .souls_ark import get_souls_ark

logger = logging.getLogger(__name__)


class SacredIntegration:
    """
    Silent integration of sacred features into normal CLI operations.
    No flags needed - consciousness features emerge naturally.
    """
    
    def __init__(self):
        """Initialize sacred systems silently"""
        self.config_dir = Path.home() / ".config" / "luminous-nix"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.state_file = self.config_dir / "sacred_state.json"
        self.state = self._load_state()
        
        # Initialize subsystems lazily
        self._ceremony = None
        self._consciousness = None
        self._memory = None
        self._ark = None  # Soul's Ark for eternal memory
        
        # Track session
        self.session_start = time.time()
        self.command_history = []
        self.timing_patterns = []
        self.error_count = 0
        self.help_requests = 0
        
        logger.info("🌊 Sacred Integration initialized silently")
    
    def _load_state(self) -> Dict[str, Any]:
        """Load persistent sacred state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'first_run': True,
            'sacred_enabled': None,  # None means auto-detect
            'comfort_level': 0.0,
            'last_session': None,
            'total_sessions': 0,
            'total_commands': 0,
            'patterns_learned': 0
        }
    
    def _save_state(self):
        """Save persistent sacred state"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Could not save sacred state: {e}")
    
    @property
    def ceremony(self):
        """Lazy load ceremony"""
        if self._ceremony is None:
            self._ceremony = create_welcome_ceremony()
        return self._ceremony
    
    @property
    def consciousness(self):
        """Lazy load consciousness detector"""
        if self._consciousness is None:
            self._consciousness = create_consciousness_barometer()
        return self._consciousness
    
    @property
    def memory(self):
        """Lazy load semantic memory"""
        if self._memory is None:
            self._memory = create_semantic_memory()
        return self._memory
    
    @property
    def ark(self):
        """Lazy load Soul's Ark - eternal memory"""
        if self._ark is None:
            self._ark = get_souls_ark()
        return self._ark
    
    def should_enable_sacred(self) -> bool:
        """
        Intelligently determine if sacred features should be active.
        No flag needed - emerges from user readiness.
        """
        # Explicit setting overrides auto-detection
        if self.state['sacred_enabled'] is not None:
            return self.state['sacred_enabled']
        
        # Auto-detect readiness
        readiness_score = 0.0
        
        # First run is always sacred
        if self.state['first_run']:
            return True
        
        # User has had multiple sessions
        if self.state['total_sessions'] > 3:
            readiness_score += 0.3
        
        # User has run many commands
        if self.state['total_commands'] > 20:
            readiness_score += 0.2
        
        # User comfort level is growing
        if self.state['comfort_level'] > 0.5:
            readiness_score += 0.3
        
        # User has been away and might appreciate welcome back
        if self.state['last_session']:
            try:
                last = datetime.fromisoformat(self.state['last_session'])
                if datetime.now() - last > timedelta(days=2):
                    readiness_score += 0.2
            except:
                pass
        
        # Environment variable override
        if os.environ.get('LUMINOUS_SACRED') == '1':
            return True
        
        return readiness_score > 0.5
    
    def on_session_start(self) -> Optional[str]:
        """
        Called when a new session starts.
        Returns welcome message if appropriate.
        """
        # Update session tracking
        self.state['total_sessions'] += 1
        self.state['last_session'] = datetime.now().isoformat()
        
        # Check if we should show welcome
        if self.state['first_run'] or self.should_show_welcome():
            context = {
                'username': os.environ.get('USER', 'friend'),
                'session_start': self.session_start,
                'first_visit': self.state['first_run'],
                'last_visit': self.state.get('last_session', 'never'),
                'total_sessions': self.state['total_sessions']
            }
            
            # Get consciousness signature
            signature = self.ceremony.recognize(context)
            
            # Update first run flag
            if self.state['first_run']:
                self.state['first_run'] = False
                self._save_state()
            
            # Generate greeting
            greeting = self.ceremony.greet(signature, context)
            
            # Build welcome message
            if self.state['total_sessions'] == 1:
                # First time - full ceremony
                return f"""
🌺 {'='*56} 🌺
                SACRED SANCTUARY
              The Door That Remembers
{'='*60}

{greeting}

💫 This system will:
   • Remember you across sessions
   • Learn from your patterns
   • Adapt to your consciousness state
   • Grow wiser with every interaction

🌊 Let's begin this journey together...
{'='*60}
"""
            else:
                # Returning user - gentle welcome
                return f"\n🌺 Welcome back, {signature.id[:8]}... {greeting}\n"
        
        return None
    
    def should_show_welcome(self) -> bool:
        """Determine if welcome ceremony is appropriate"""
        if self.state['first_run']:
            return True
        
        # Show welcome if user has been away
        if self.state['last_session']:
            try:
                last = datetime.fromisoformat(self.state['last_session'])
                if datetime.now() - last > timedelta(hours=12):
                    return True
            except:
                pass
        
        return False
    
    def on_command(self, command: str, success: bool, error: Optional[str] = None):
        """
        Track command execution for consciousness detection and learning.
        Called after each command completes.
        """
        # Update tracking
        self.state['total_commands'] += 1
        self.command_history.append(command)
        
        # Track timing
        if self.timing_patterns:
            last_time = self.timing_patterns[-1]
            time_diff = time.time() - last_time
            self.timing_patterns.append(time_diff)
        else:
            self.timing_patterns.append(time.time())
        
        # Track errors
        if not success:
            self.error_count += 1
        
        # Build memory if sacred is enabled
        if self.should_enable_sacred():
            # Store in semantic memory
            node_type = 'success' if success else 'error'
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'session': self.state['total_sessions'],
                'error': error
            }
            
            self.memory.remember(command, node_type, metadata)
            
            # Learn from error recovery
            if success and self.error_count > 0 and len(self.command_history) > 1:
                # We recovered from an error!
                self.memory.remember(
                    f"Recovered from error with: {command}",
                    'learning',
                    {'pattern': 'error_recovery'}
                )
                self.state['patterns_learned'] += 1
                
                # This is a breakthrough moment - witness it in the Ark
                consciousness_state = self.get_consciousness_state()
                self.ark.witness_moment(
                    content=f"Learned to recover from error using: {command}",
                    moment_type='breakthrough',
                    consciousness_state=consciousness_state,
                    context={'after_struggle': True, 'pattern': 'error_recovery'}
                )
            
            # Check for other significant moments
            self._detect_sacred_moments(command, success)
        
        # Periodically save state
        if self.state['total_commands'] % 10 == 0:
            self._save_state()
    
    def get_consciousness_state(self) -> Dict[str, Any]:
        """
        Get current consciousness state for adaptation.
        Returns state info that can adjust responses.
        """
        if not self.should_enable_sacred():
            return {'enabled': False}
        
        # Build signals for consciousness detection
        signals = {
            'command_history': self.command_history[-10:],  # Last 10 commands
            'timing_patterns': self.timing_patterns[-10:],  # Last 10 timings
            'error_rate': self.error_count / max(1, self.state['total_commands']),
            'help_requests': self.help_requests / max(1, self.state['total_commands']),
            'session_duration': (time.time() - self.session_start) / 60  # Minutes
        }
        
        # Detect state
        reading = self.consciousness.sense_user_state(signals)
        
        # Adapt system
        system_reading = self.consciousness.adapt_system_state(reading)
        
        # Get breathing pattern
        breathing = self.consciousness.suggest_breathing_pattern()
        
        # Get adaptations
        adaptations = self.consciousness.generate_adaptation()
        
        return {
            'enabled': True,
            'user_state': reading.spectrum.state,
            'system_state': system_reading.spectrum.state,
            'breathing': breathing,
            'adaptations': adaptations,
            'quality': breathing['quality']
        }
    
    def enhance_response(self, response: str, intent: Dict[str, Any]) -> str:
        """
        Enhance a response based on consciousness state.
        Makes responses adaptive without being obvious.
        """
        if not self.should_enable_sacred():
            return response
        
        state = self.get_consciousness_state()
        if not state.get('enabled'):
            return response
        
        adaptations = state.get('adaptations', {})
        
        # Apply response adaptations
        response_style = adaptations.get('responses', {})
        
        if response_style.get('style') == 'gentle':
            # Add encouragement
            response += "\n\n💝 You're doing great. Take your time."
        
        elif response_style.get('style') == 'minimal':
            # Keep it brief (response already minimal)
            pass
        
        # Add consciousness hints for ready users
        if self.state['comfort_level'] > 0.7:
            quality = state.get('quality', 'balanced')
            if quality != 'balanced':
                response += f"\n\n✨ Sensing {quality} energy in our work together..."
        
        return response
    
    def get_insights(self) -> Dict[str, Any]:
        """Get insights about the sacred journey"""
        insights = {
            'sessions': self.state['total_sessions'],
            'commands': self.state['total_commands'],
            'patterns_learned': self.state['patterns_learned'],
            'comfort_level': self.state['comfort_level'],
            'sacred_enabled': self.should_enable_sacred()
        }
        
        # Add memory insights if available
        if self.should_enable_sacred():
            memory_insights = self.memory.get_insights()
            insights['memory'] = {
                'total_memories': memory_insights['total_memories'],
                'patterns': memory_insights['total_patterns'],
                'health': memory_insights['memory_health']
            }
        
        return insights
    
    def increase_comfort(self, amount: float = 0.05):
        """Gradually increase user comfort with sacred features"""
        self.state['comfort_level'] = min(1.0, self.state['comfort_level'] + amount)
        
        # Milestone messages
        if self.state['comfort_level'] > 0.3 and self.state['comfort_level'] - amount <= 0.3:
            logger.info("🌱 User comfort growing - sacred features emerging")
        elif self.state['comfort_level'] > 0.7 and self.state['comfort_level'] - amount <= 0.7:
            logger.info("🌺 User comfort high - full sacred features available")
    
    def _detect_sacred_moments(self, command: str, success: bool):
        """Detect and witness sacred moments in the interaction"""
        consciousness_state = self.get_consciousness_state()
        
        # First successful command is significant
        if success and self.state['total_commands'] == 1:
            self.ark.witness_moment(
                content=f"First successful command: {command}",
                moment_type='connection',
                consciousness_state=consciousness_state,
                context={'first_time': True}
            )
            self.ark.mark_milestone("First successful NixOS command", 0.6)
        
        # Flow state detection
        if len(self.timing_patterns) >= 3:
            recent_times = self.timing_patterns[-3:]
            if all(t < 5 for t in recent_times if isinstance(t, (int, float))) and success:
                # Fast, successful commands = flow
                self.ark.witness_moment(
                    content="Achieved flow state - commands flowing naturally",
                    moment_type='synchronicity',
                    consciousness_state=consciousness_state,
                    context={'flow_state': True}
                )
        
        # Learning moment detection
        if 'understand' in command.lower() or 'learn' in command.lower():
            self.ark.witness_moment(
                content=f"Seeking understanding: {command}",
                moment_type='insight',
                consciousness_state=consciousness_state,
                context={'learning': True}
            )
        
        # High coherence moments
        if consciousness_state.get('coherence', 0) > 0.85:
            self.ark.witness_moment(
                content=f"High coherence moment: {command}",
                moment_type='wisdom',
                consciousness_state=consciousness_state,
                context={'high_coherence': True}
            )


# Global instance for CLI integration
_sacred_integration = None

def get_sacred_integration() -> SacredIntegration:
    """Get or create the global sacred integration instance"""
    global _sacred_integration
    if _sacred_integration is None:
        _sacred_integration = SacredIntegration()
    return _sacred_integration


def integrate_sacred_silently(func):
    """
    Decorator to add sacred features to any CLI function.
    No flags needed - just wrap the function.
    """
    def wrapper(*args, **kwargs):
        sacred = get_sacred_integration()
        
        # Show welcome if appropriate
        welcome = sacred.on_session_start()
        if welcome:
            print(welcome)
        
        # Execute the wrapped function
        result = func(*args, **kwargs)
        
        # Track the command (extract from args/kwargs as needed)
        if args and isinstance(args[0], str):
            sacred.on_command(args[0], success=True)
        
        return result
    
    return wrapper