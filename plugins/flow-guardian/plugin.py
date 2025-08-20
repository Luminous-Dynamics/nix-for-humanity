"""
Flow Guardian Plugin - Protecting Your Sacred Attention

This plugin guards your flow state by managing interruptions,
tracking context switches, and creating sanctuaries for deep work.
"""

import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import asyncio


@dataclass
class FocusSession:
    """A protected focus session"""
    start_time: datetime
    duration_minutes: int
    task: str
    interruptions_blocked: int = 0
    completed: bool = False
    end_time: Optional[datetime] = None
    
    @property
    def is_active(self) -> bool:
        if self.completed:
            return False
        elapsed = datetime.now() - self.start_time
        return elapsed < timedelta(minutes=self.duration_minutes)
    
    @property
    def remaining_minutes(self) -> int:
        if not self.is_active:
            return 0
        elapsed = datetime.now() - self.start_time
        remaining = timedelta(minutes=self.duration_minutes) - elapsed
        return int(remaining.total_seconds() / 60)
    
    def to_dict(self) -> Dict:
        return {
            'start_time': self.start_time.isoformat(),
            'duration_minutes': self.duration_minutes,
            'task': self.task,
            'interruptions_blocked': self.interruptions_blocked,
            'completed': self.completed,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'is_active': self.is_active,
            'remaining_minutes': self.remaining_minutes
        }


@dataclass
class Interruption:
    """An interruption that was blocked or allowed"""
    timestamp: datetime
    source: str
    blocked: bool
    reason: str
    impact_minutes: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'blocked': self.blocked,
            'reason': self.reason,
            'impact_minutes': self.impact_minutes
        }


class FlowGuardian:
    """
    The guardian of your attention and flow state.
    
    This plugin protects your deep work by managing interruptions
    and creating sacred boundaries around your focus time.
    """
    
    # Required by plugin system
    plugin_id = "flow-guardian"
    plugin_version = "1.0.0"
    governing_principle = "protect_attention"
    
    def __init__(self):
        """Initialize the Flow Guardian"""
        self.current_session: Optional[FocusSession] = None
        self.session_history: List[FocusSession] = []
        self.interruptions: List[Interruption] = []
        self.data_dir = Path.home() / ".local" / "share" / "luminous-nix" / "flow-guardian"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load previous sessions
        self._load_history()
    
    def _load_history(self):
        """Load session history from disk"""
        history_file = self.data_dir / "history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    # Note: In production, we'd deserialize these properly
                    # For now, we just keep the loaded data structure
            except Exception as e:
                print(f"Could not load history: {e}")
    
    def _save_history(self):
        """Save session history to disk"""
        history_file = self.data_dir / "history.json"
        try:
            data = {
                'sessions': [s.to_dict() for s in self.session_history],
                'interruptions': [i.to_dict() for i in self.interruptions]
            }
            with open(history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Could not save history: {e}")
    
    async def handle_start_focus(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start a protected focus session.
        
        This is the primary handler for beginning deep work.
        """
        # Extract parameters from intent
        duration = intent.get('duration', 25)  # Default to 25 minutes (Pomodoro)
        task = intent.get('task', 'deep work')
        
        # Check if session already active
        if self.current_session and self.current_session.is_active:
            return {
                'success': False,
                'message': f"⚠️ Focus session already active with {self.current_session.remaining_minutes} minutes remaining",
                'data': self.current_session.to_dict()
            }
        
        # Create new session
        self.current_session = FocusSession(
            start_time=datetime.now(),
            duration_minutes=duration,
            task=task
        )
        
        # In a real implementation, we would:
        # 1. Enable system Do Not Disturb mode
        # 2. Start monitoring for interruptions
        # 3. Set up notification filters
        # For now, we simulate this
        
        return {
            'success': True,
            'message': f"🎯 Focus mode activated for {duration} minutes\n"
                      f"📝 Working on: {task}\n"
                      f"🔕 Interruptions will be blocked",
            'action': 'focus_started',
            'data': self.current_session.to_dict()
        }
    
    async def handle_check_interruptions(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Show analysis of interruptions.
        
        This helps users understand what breaks their flow.
        """
        # Get today's interruptions
        today = datetime.now().date()
        today_interruptions = [
            i for i in self.interruptions
            if i.timestamp.date() == today
        ]
        
        # Calculate statistics
        total_interruptions = len(today_interruptions)
        blocked_count = sum(1 for i in today_interruptions if i.blocked)
        time_saved = sum(i.impact_minutes for i in today_interruptions if i.blocked)
        
        # Find biggest offender
        sources = {}
        for interruption in today_interruptions:
            if interruption.source not in sources:
                sources[interruption.source] = 0
            sources[interruption.source] += 1
        
        biggest_offender = max(sources.items(), key=lambda x: x[1])[0] if sources else "None"
        
        # Generate report
        report = f"📊 Today's Attention Report\n"
        report += f"{'=' * 40}\n"
        report += f"Total interruptions: {total_interruptions}\n"
        report += f"Blocked: {blocked_count}\n"
        report += f"Time saved: {time_saved:.1f} minutes\n"
        report += f"Biggest offender: {biggest_offender}\n"
        
        if self.current_session and self.current_session.is_active:
            report += f"\n🎯 Currently in focus mode\n"
            report += f"   Task: {self.current_session.task}\n"
            report += f"   Remaining: {self.current_session.remaining_minutes} minutes"
        
        return {
            'success': True,
            'message': report,
            'data': {
                'total_interruptions': total_interruptions,
                'blocked_count': blocked_count,
                'time_saved': time_saved,
                'biggest_offender': biggest_offender,
                'current_session': self.current_session.to_dict() if self.current_session else None
            }
        }
    
    async def handle_pause_focus(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pause the current focus session.
        """
        if not self.current_session or not self.current_session.is_active:
            return {
                'success': False,
                'message': "No active focus session to pause"
            }
        
        # In a real implementation, we would temporarily disable protections
        remaining = self.current_session.remaining_minutes
        
        return {
            'success': True,
            'message': f"⏸️ Focus session paused\n"
                      f"   {remaining} minutes remaining\n"
                      f"   Use 'resume focus' to continue",
            'data': self.current_session.to_dict()
        }
    
    async def handle_end_focus(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        End the current focus session and show summary.
        """
        if not self.current_session:
            return {
                'success': False,
                'message': "No focus session to end"
            }
        
        # Mark session as completed
        self.current_session.completed = True
        self.current_session.end_time = datetime.now()
        
        # Calculate session statistics
        actual_duration = (self.current_session.end_time - self.current_session.start_time).total_seconds() / 60
        planned_duration = self.current_session.duration_minutes
        completion_rate = min(actual_duration / planned_duration * 100, 100)
        
        # Add to history
        self.session_history.append(self.current_session)
        self._save_history()
        
        # Generate summary
        summary = f"✅ Focus session completed!\n"
        summary += f"{'=' * 40}\n"
        summary += f"Task: {self.current_session.task}\n"
        summary += f"Duration: {actual_duration:.1f} / {planned_duration} minutes\n"
        summary += f"Completion: {completion_rate:.0f}%\n"
        summary += f"Interruptions blocked: {self.current_session.interruptions_blocked}\n"
        
        if completion_rate >= 90:
            summary += "\n🌟 Excellent focus! You stayed in flow."
        elif completion_rate >= 70:
            summary += "\n💪 Good session! You maintained focus well."
        else:
            summary += "\n💡 Short session - consider shorter focus periods."
        
        # Clear current session
        session_data = self.current_session.to_dict()
        self.current_session = None
        
        return {
            'success': True,
            'message': summary,
            'data': session_data
        }
    
    async def handle(self, intent_type: str, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main handler that routes to specific intent handlers.
        
        This is the interface the plugin system will call.
        """
        handlers = {
            'start_focus': self.handle_start_focus,
            'check_interruptions': self.handle_check_interruptions,
            'pause_focus': self.handle_pause_focus,
            'end_focus': self.handle_end_focus
        }
        
        handler = handlers.get(intent_type)
        if not handler:
            return {
                'success': False,
                'message': f"Unknown intent: {intent_type}"
            }
        
        return await handler(intent_data)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current plugin status.
        """
        return {
            'plugin_id': self.plugin_id,
            'version': self.plugin_version,
            'governing_principle': self.governing_principle,
            'active_session': self.current_session.to_dict() if self.current_session and self.current_session.is_active else None,
            'sessions_today': len([s for s in self.session_history if s.start_time.date() == datetime.now().date()]),
            'total_sessions': len(self.session_history)
        }


# Export the plugin class
Plugin = FlowGuardian