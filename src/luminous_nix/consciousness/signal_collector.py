#!/usr/bin/env python3
"""
📡 Signal Collector - Gathering consciousness signals from user interactions

This module collects real signals from user behavior to feed into
the ConsciousnessBarometer for accurate state detection.
"""

import time
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import deque
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class InteractionEvent:
    """A single user interaction event"""
    timestamp: datetime
    event_type: str  # command, error, help_request, pause, etc.
    data: Dict[str, Any] = field(default_factory=dict)
    duration: Optional[float] = None


class RealTimeSignalCollector:
    """
    Collects real-time signals from user interactions to detect consciousness state.
    
    This is the bridge between raw user behavior and consciousness detection.
    """
    
    def __init__(self, window_size: int = 50):
        """
        Initialize signal collector.
        
        Args:
            window_size: Number of recent events to keep for analysis
        """
        self.events = deque(maxlen=window_size)
        self.session_start = datetime.now()
        self.last_command_time = None
        self.command_history = deque(maxlen=20)
        self.command_execution_times = deque(maxlen=20)  # Track execution times
        self.error_count = 0
        self.help_request_count = 0
        self.last_analysis_time = datetime.now()
        
        # Timing patterns
        self.inter_command_times = deque(maxlen=10)
        self.typing_speeds = deque(maxlen=10)
        
        # Current state cache
        self._cached_signals = None
        self._cache_time = None
        
        logger.info("📡 Signal collector initialized")
    
    def record_command(self, command: str, execution_time: float = None):
        """Record a command execution"""
        now = datetime.now()
        
        # Calculate inter-command time
        if self.last_command_time:
            inter_time = (now - self.last_command_time).total_seconds()
            self.inter_command_times.append(inter_time)
        
        self.last_command_time = now
        self.command_history.append(command)
        
        # Store execution time if provided
        if execution_time is not None:
            self.command_execution_times.append(execution_time)
        
        # Record event
        event = InteractionEvent(
            timestamp=now,
            event_type="command",
            data={"command": command},
            duration=execution_time
        )
        self.events.append(event)
        
        # Invalidate cache
        self._cached_signals = None
        
        logger.debug(f"Recorded command: {command[:50]}...")
    
    def record_error(self, error_type: str, error_message: str = None):
        """Record an error occurrence"""
        self.error_count += 1
        
        event = InteractionEvent(
            timestamp=datetime.now(),
            event_type="error",
            data={
                "type": error_type,
                "message": error_message,
                "count": self.error_count
            }
        )
        self.events.append(event)
        
        # Invalidate cache
        self._cached_signals = None
        
        logger.debug(f"Recorded error: {error_type}")
    
    def record_help_request(self, help_topic: str = None):
        """Record a help request"""
        self.help_request_count += 1
        
        event = InteractionEvent(
            timestamp=datetime.now(),
            event_type="help_request",
            data={
                "topic": help_topic,
                "count": self.help_request_count
            }
        )
        self.events.append(event)
        
        # Invalidate cache
        self._cached_signals = None
        
        logger.debug(f"Recorded help request: {help_topic}")
    
    def record_pause(self, duration: float):
        """Record a pause in activity"""
        event = InteractionEvent(
            timestamp=datetime.now(),
            event_type="pause",
            duration=duration
        )
        self.events.append(event)
        
        # Invalidate cache
        self._cached_signals = None
    
    def record_typing_speed(self, characters_per_second: float):
        """Record typing speed"""
        self.typing_speeds.append(characters_per_second)
        
        event = InteractionEvent(
            timestamp=datetime.now(),
            event_type="typing",
            data={"speed": characters_per_second}
        )
        self.events.append(event)
        
        # Invalidate cache
        self._cached_signals = None
    
    def get_consciousness_signals(self) -> Dict[str, Any]:
        """
        Analyze collected signals and return consciousness indicators.
        
        Returns:
            Dictionary of signals for ConsciousnessBarometer
        """
        # Use cache if recent (within 2 seconds)
        if self._cached_signals and self._cache_time:
            if (datetime.now() - self._cache_time).total_seconds() < 2:
                return self._cached_signals
        
        now = datetime.now()
        session_duration = (now - self.session_start).total_seconds() / 60  # minutes
        
        # Calculate error rate
        recent_commands = sum(1 for e in self.events if e.event_type == "command")
        error_rate = self.error_count / max(recent_commands, 1)
        
        # Calculate help request frequency
        help_frequency = self.help_request_count / max(recent_commands, 1)
        
        # Analyze timing patterns
        timing_patterns = list(self.inter_command_times) if self.inter_command_times else [5.0]
        
        # Analyze command complexity
        # Convert to dict format that tests expect
        command_history = [{'command': cmd} for cmd in self.command_history]
        
        # Check for repetitive patterns (might indicate frustration or focus)
        # Use string list for repetition calculation
        command_strings = [cmd['command'] for cmd in command_history]
        repetition_score = self._calculate_repetition_score(command_strings)
        
        # Calculate activity level
        activity_level = self._calculate_activity_level()
        
        # Estimate cognitive load based on error patterns
        cognitive_load = self._estimate_cognitive_load()
        
        # Calculate average command execution time
        avg_command_time = 0.0
        if self.command_execution_times:
            avg_command_time = statistics.mean(self.command_execution_times)
        elif self.inter_command_times:
            # Fallback to inter-command times if no execution times recorded
            avg_command_time = statistics.mean(self.inter_command_times)
        
        signals = {
            'command_history': command_history,
            'timing_patterns': timing_patterns,
            'error_rate': error_rate,
            'help_requests': help_frequency,
            'session_duration': session_duration,
            'repetition_score': repetition_score,
            'activity_level': activity_level,
            'cognitive_load': cognitive_load,
            'avg_command_time': avg_command_time
        }
        
        # Add typing speed if available
        if self.typing_speeds:
            signals['typing_speed'] = statistics.mean(self.typing_speeds)
        
        # Cache the results
        self._cached_signals = signals
        self._cache_time = now
        
        return signals
    
    def _calculate_repetition_score(self, commands: List[str]) -> float:
        """
        Calculate how repetitive recent commands are.
        High repetition might indicate frustration or deep focus.
        """
        if len(commands) < 2:
            return 0.0
        
        # Count unique vs total
        unique_commands = len(set(commands))
        total_commands = len(commands)
        
        # More repetition = higher score
        repetition = 1.0 - (unique_commands / total_commands)
        
        return repetition
    
    def _calculate_activity_level(self) -> float:
        """
        Calculate current activity level (0=idle, 1=very active).
        """
        if not self.events:
            return 0.0
        
        now = datetime.now()
        recent_events = [
            e for e in self.events 
            if (now - e.timestamp).total_seconds() < 60  # Last minute
        ]
        
        # Normalize to 0-1 (assume 20 events/minute is very active)
        activity = min(1.0, len(recent_events) / 20)
        
        return activity
    
    def _estimate_cognitive_load(self) -> float:
        """
        Estimate cognitive load based on error patterns and help requests.
        """
        # Recent errors increase cognitive load
        recent_errors = sum(
            1 for e in self.events 
            if e.event_type == "error" and 
            (datetime.now() - e.timestamp).total_seconds() < 120
        )
        
        # Help requests indicate learning/confusion
        recent_help = sum(
            1 for e in self.events 
            if e.event_type == "help_request" and 
            (datetime.now() - e.timestamp).total_seconds() < 120
        )
        
        # Combine factors
        load = min(1.0, (recent_errors * 0.3 + recent_help * 0.2))
        
        return load
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a human-readable summary of detected patterns"""
        signals = self.get_consciousness_signals()
        
        summary = {
            'session_length': f"{signals['session_duration']:.1f} minutes",
            'activity': 'high' if signals['activity_level'] > 0.7 else 'moderate' if signals['activity_level'] > 0.3 else 'low',
            'error_rate': 'high' if signals['error_rate'] > 0.3 else 'moderate' if signals['error_rate'] > 0.1 else 'low',
            'pattern': 'repetitive' if signals['repetition_score'] > 0.5 else 'varied',
            'cognitive_load': 'high' if signals['cognitive_load'] > 0.6 else 'moderate' if signals['cognitive_load'] > 0.3 else 'low'
        }
        
        # Infer likely state
        if signals['error_rate'] > 0.3 and signals['cognitive_load'] > 0.6:
            summary['likely_state'] = 'overwhelmed'
        elif signals['activity_level'] > 0.7 and signals['error_rate'] < 0.1:
            summary['likely_state'] = 'flow'
        elif signals['help_requests'] > 0.2:
            summary['likely_state'] = 'learning'
        elif signals['repetition_score'] > 0.7:
            summary['likely_state'] = 'focused' if signals['error_rate'] < 0.2 else 'frustrated'
        else:
            summary['likely_state'] = 'balanced'
        
        return summary
    
    def reset_session(self):
        """Reset session data for a fresh start"""
        self.events.clear()
        self.session_start = datetime.now()
        self.last_command_time = None
        self.command_history.clear()
        self.command_execution_times.clear()
        self.error_count = 0
        self.help_request_count = 0
        self.inter_command_times.clear()
        self.typing_speeds.clear()
        self._cached_signals = None
        self._cache_time = None
        
        logger.info("📡 Signal collector reset")


class IntegrationBridge:
    """
    Bridge between SignalCollector and ConsciousnessBarometer.
    Automatically feeds real signals into consciousness detection.
    """
    
    def __init__(self, signal_collector: RealTimeSignalCollector, consciousness_barometer):
        """
        Initialize the bridge.
        
        Args:
            signal_collector: The signal collector instance
            consciousness_barometer: The consciousness detection instance
        """
        self.collector = signal_collector
        self.barometer = consciousness_barometer
        self.auto_update = True
        self.update_interval = 5.0  # seconds
        self.last_update = time.time()
    
    def update_consciousness(self) -> Any:
        """
        Update consciousness state with real signals.
        
        Returns:
            ConsciousnessReading from the barometer
        """
        # Get real signals
        signals = self.collector.get_consciousness_signals()
        
        # Feed to consciousness detector
        reading = self.barometer.sense_user_state(signals)
        
        # Log the update
        logger.debug(f"Updated consciousness: {reading.quality}")
        
        return reading
    
    def should_update(self) -> bool:
        """Check if it's time for an automatic update"""
        if not self.auto_update:
            return False
        
        return (time.time() - self.last_update) >= self.update_interval
    
    def maybe_update(self) -> Optional[Any]:
        """Update consciousness if it's time"""
        if self.should_update():
            self.last_update = time.time()
            return self.update_consciousness()
        return None


def demonstrate_signal_collection():
    """Demonstrate signal collection and consciousness detection"""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    from luminous_nix.consciousness.consciousness_detector import ConsciousnessBarometer
    
    print("\n📡 Signal Collection Demonstration")
    print("=" * 50)
    
    # Initialize components
    collector = RealTimeSignalCollector()
    barometer = ConsciousnessBarometer()
    bridge = IntegrationBridge(collector, barometer)
    
    # Simulate user interactions
    print("\n1. Simulating focused work session...")
    commands = [
        "install firefox",
        "install vscode", 
        "install git",
        "configure development environment"
    ]
    
    for i, cmd in enumerate(commands):
        collector.record_command(cmd)
        time.sleep(0.1)  # Simulate fast, regular commands
        if i == 0:
            collector.record_typing_speed(8.5)  # Fast typing
    
    # Get consciousness reading
    reading = bridge.update_consciousness()
    summary = collector.get_state_summary()
    
    print(f"   Detected state: {reading.quality}")
    print(f"   Activity: {summary['activity']}")
    print(f"   Cognitive load: {summary['cognitive_load']}")
    
    print("\n2. Simulating learning/confusion...")
    collector.record_help_request("how to configure network")
    collector.record_error("command_not_found", "nix-env: command not found")
    collector.record_help_request("nix commands")
    collector.record_command("search network manager")
    collector.record_error("syntax_error", "unexpected token")
    
    reading = bridge.update_consciousness()
    summary = collector.get_state_summary()
    
    print(f"   Detected state: {reading.quality}")
    print(f"   Error rate: {summary['error_rate']}")
    print(f"   Likely state: {summary['likely_state']}")
    
    print("\n3. Simulating overwhelm...")
    for _ in range(5):
        collector.record_error("build_failed", "Package build failed")
        collector.record_command("nixos-rebuild switch")
        time.sleep(0.05)
    
    collector.record_help_request("fix build errors")
    collector.record_pause(10.0)  # Long pause
    
    reading = bridge.update_consciousness()
    summary = collector.get_state_summary()
    
    print(f"   Detected state: {reading.quality}")
    print(f"   Pattern: {summary['pattern']}")
    print(f"   Cognitive load: {summary['cognitive_load']}")
    print(f"   Likely state: {summary['likely_state']}")
    
    print("\n" + "=" * 50)
    print("✅ Signal collection demonstration complete!")


if __name__ == "__main__":
    demonstrate_signal_collection()