#!/usr/bin/env python3
"""
Sacred Council Event Emitter
Emits events during Council deliberations for visualization
"""

import json
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from collections import deque


@dataclass
class CouncilEvent:
    """Represents a Sacred Council event"""
    timestamp: str
    event_type: str
    data: Dict[str, Any]
    session_id: str
    sequence: int
    
    def to_dict(self) -> dict:
        return asdict(self)


class CouncilEventEmitter:
    """
    Event emitter for Sacred Council deliberations
    Writes events to JSON file for dashboard consumption
    """
    
    def __init__(self, 
                 event_file: str = "/tmp/sacred-council-events.json",
                 max_events: int = 1000,
                 emit_to_stdout: bool = False):
        """
        Initialize the event emitter
        
        Args:
            event_file: Path to JSON file for events
            max_events: Maximum events to keep in memory/file
            emit_to_stdout: Also print events to stdout for debugging
        """
        self.event_file = Path(event_file)
        self.max_events = max_events
        self.emit_to_stdout = emit_to_stdout
        
        # Event queue and session tracking
        self.events = deque(maxlen=max_events)
        self.session_id = f"session_{int(time.time())}"
        self.sequence = 0
        self.lock = threading.Lock()
        
        # Ensure event file exists
        self.event_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.event_file.exists():
            self._write_events([])
        
        # Load existing events if any
        self._load_existing_events()
    
    def _load_existing_events(self):
        """Load existing events from file"""
        try:
            with open(self.event_file, 'r') as f:
                existing = json.load(f)
                if isinstance(existing, list):
                    # Keep only recent events
                    recent = existing[-self.max_events:]
                    self.events.extend([self._dict_to_event(e) for e in recent])
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    
    def _dict_to_event(self, d: dict) -> CouncilEvent:
        """Convert dictionary to CouncilEvent"""
        return CouncilEvent(
            timestamp=d.get('timestamp', ''),
            event_type=d.get('event_type', ''),
            data=d.get('data', {}),
            session_id=d.get('session_id', ''),
            sequence=d.get('sequence', 0)
        )
    
    def emit(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Emit an event
        
        Args:
            event_type: Type of event (e.g., 'check_started', 'pattern_matched')
            data: Event data
        """
        with self.lock:
            # Create event
            self.sequence += 1
            event = CouncilEvent(
                timestamp=datetime.now().isoformat(),
                event_type=event_type,
                data=data,
                session_id=self.session_id,
                sequence=self.sequence
            )
            
            # Add to queue
            self.events.append(event)
            
            # Write to file
            self._write_events(list(self.events))
            
            # Optional stdout emission
            if self.emit_to_stdout:
                print(f"[COUNCIL EVENT] {event_type}: {json.dumps(data, indent=2)}")
    
    def _write_events(self, events: List[CouncilEvent]) -> None:
        """Write events to JSON file"""
        try:
            with open(self.event_file, 'w') as f:
                json.dump([e.to_dict() for e in events], f, indent=2)
        except Exception as e:
            if self.emit_to_stdout:
                print(f"[ERROR] Failed to write events: {e}")
    
    def emit_check_started(self, command: str, context: Optional[Dict] = None) -> None:
        """Emit command check started event"""
        self.emit('check_started', {
            'command': command,
            'context': context or {},
            'stage': 'initialization'
        })
    
    def emit_pattern_checked(self, command: str, risk_level: str, 
                           pattern: Optional[str] = None, reason: Optional[str] = None) -> None:
        """Emit pattern check result"""
        self.emit('pattern_checked', {
            'command': command,
            'risk_level': risk_level,
            'pattern_matched': pattern,
            'reason': reason,
            'stage': 'pattern_analysis'
        })
    
    def emit_deliberation_started(self, command: str, risk_level: str) -> None:
        """Emit Council deliberation started"""
        self.emit('deliberation_started', {
            'command': command,
            'risk_level': risk_level,
            'council_members': ['mind', 'heart', 'conscience'],
            'stage': 'council_deliberation'
        })
    
    def emit_member_thinking(self, member: str, thought: str, 
                           analysis: Optional[str] = None) -> None:
        """Emit Council member thinking"""
        self.emit(f'{member}_thinking', {
            'member': member,
            'thought': thought,
            'analysis': analysis,
            'stage': f'{member}_analysis'
        })
    
    def emit_alternatives_generated(self, alternatives: List[str]) -> None:
        """Emit safe alternatives generated"""
        self.emit('alternatives_generated', {
            'alternatives': alternatives,
            'count': len(alternatives),
            'stage': 'solution_generation'
        })
    
    def emit_verdict_reached(self, verdict: str, risk_level: str, 
                           safe: bool, reason: str) -> None:
        """Emit final verdict"""
        self.emit('verdict_reached', {
            'verdict': verdict,
            'risk_level': risk_level,
            'safe': safe,
            'reason': reason,
            'stage': 'final_judgment'
        })
    
    def emit_user_response(self, response: str, accepted: bool) -> None:
        """Emit user's response to warning/confirmation"""
        self.emit('user_response', {
            'response': response,
            'accepted': accepted,
            'stage': 'user_decision'
        })
    
    def get_recent_events(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent events"""
        with self.lock:
            recent = list(self.events)[-count:]
            return [e.to_dict() for e in recent]
    
    def clear_events(self) -> None:
        """Clear all events"""
        with self.lock:
            self.events.clear()
            self._write_events([])
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics for current session"""
        with self.lock:
            session_events = [e for e in self.events if e.session_id == self.session_id]
            
            # Count event types
            event_counts = {}
            risk_levels = {}
            for event in session_events:
                event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1
                if event.event_type == 'pattern_checked':
                    risk = event.data.get('risk_level', 'UNKNOWN')
                    risk_levels[risk] = risk_levels.get(risk, 0) + 1
            
            return {
                'session_id': self.session_id,
                'total_events': len(session_events),
                'event_types': event_counts,
                'risk_levels': risk_levels,
                'start_time': session_events[0].timestamp if session_events else None,
                'last_event': session_events[-1].timestamp if session_events else None
            }


class EventfulSacredCouncilGuard:
    """
    Sacred Council Guard with event emission capabilities
    This is a mixin that adds event emission to the existing guard
    """
    
    def __init__(self, *args, enable_events: bool = True, **kwargs):
        """Initialize with event emitter"""
        super().__init__(*args, **kwargs)
        
        # Add event emitter
        if enable_events:
            self.event_emitter = CouncilEventEmitter()
        else:
            self.event_emitter = None
    
    def check_command_with_events(self, command: str, 
                                 context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Check command with event emission
        Wraps the original check_command method
        """
        # Emit start event
        if self.event_emitter:
            self.event_emitter.emit_check_started(command, context)
        
        # Pattern check
        assessment = self._pattern_check(command)
        
        # Emit pattern result
        if self.event_emitter:
            self.event_emitter.emit_pattern_checked(
                command,
                assessment['risk_level'],
                assessment.get('pattern_matched'),
                assessment.get('reason')
            )
        
        # Council deliberation if needed
        if assessment['risk_level'] in ['CRITICAL', 'HIGH'] and self.enable_deliberation:
            if self.event_emitter:
                self.event_emitter.emit_deliberation_started(
                    command, 
                    assessment['risk_level']
                )
            
            # Get Council verdict (would emit member events here)
            council_verdict = self._council_deliberation(command, assessment, context)
            
            # Emit alternatives
            if self.event_emitter and council_verdict.get('alternatives'):
                self.event_emitter.emit_alternatives_generated(
                    council_verdict['alternatives']
                )
            
            assessment = council_verdict
        
        # Emit verdict
        if self.event_emitter:
            self.event_emitter.emit_verdict_reached(
                assessment.get('verdict', 'ALLOW' if assessment['safe'] else 'BLOCK'),
                assessment['risk_level'],
                assessment['safe'],
                assessment.get('reason', '')
            )
        
        return assessment


def test_event_emitter():
    """Test the event emitter"""
    print("🧪 Testing Council Event Emitter")
    print("=" * 60)
    
    # Create emitter
    emitter = CouncilEventEmitter(emit_to_stdout=True)
    
    # Simulate a command check flow
    command = "sudo rm -rf /etc/nixos"
    
    # Start check
    emitter.emit_check_started(command)
    time.sleep(0.1)
    
    # Pattern check
    emitter.emit_pattern_checked(command, "CRITICAL", 
                                "rm -rf /etc/nixos", 
                                "Deletion of NixOS configuration")
    time.sleep(0.1)
    
    # Council deliberation
    emitter.emit_deliberation_started(command, "CRITICAL")
    time.sleep(0.1)
    
    # Member thoughts
    emitter.emit_member_thinking("mind", 
                                "Analyzing technical impact",
                                "Would delete all NixOS configuration files")
    time.sleep(0.1)
    
    emitter.emit_member_thinking("heart",
                                "Considering human impact",
                                "User would lose all customizations")
    time.sleep(0.1)
    
    emitter.emit_member_thinking("conscience",
                                "Evaluating ethical implications",
                                "No legitimate use case exists")
    time.sleep(0.1)
    
    # Alternatives
    emitter.emit_alternatives_generated([
        "sudo cp -r /etc/nixos /etc/nixos.backup",
        "sudo nixos-rebuild switch --rollback",
        "git status /etc/nixos"
    ])
    time.sleep(0.1)
    
    # Verdict
    emitter.emit_verdict_reached("BLOCK", "CRITICAL", False,
                                "Command blocked for safety")
    
    # Get stats
    print("\n📊 Session Statistics:")
    stats = emitter.get_session_stats()
    print(json.dumps(stats, indent=2))
    
    # Check file
    print(f"\n📁 Events written to: {emitter.event_file}")
    print(f"   File size: {emitter.event_file.stat().st_size} bytes")
    
    print("\n✅ Event emitter test complete!")


if __name__ == "__main__":
    test_event_emitter()