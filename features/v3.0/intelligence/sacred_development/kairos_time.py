"""
from typing import Dict, Union, List, Optional
Kairos Time - Sacred development rhythm that honors natural timing

This module implements Kairos time principles where development follows
natural rhythms rather than artificial deadlines.
"""

import time
import asyncio
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import logging
from collections import deque

from ..knowledge_graph.skg import SymbioticKnowledgeGraph


class DevelopmentPhase(Enum):
    """Natural phases of development"""
    GERMINATION = "germination"      # Ideas taking root
    GROWTH = "growth"               # Active development
    FLOWERING = "flowering"         # Feature completion
    FRUITING = "fruiting"          # Value delivery
    REST = "rest"                  # Regeneration period
    

class EnergyLevel(Enum):
    """Developer energy states"""
    INSPIRED = "inspired"           # High creative energy
    FLOWING = "flowing"            # Sustained productivity
    STEADY = "steady"              # Consistent progress
    WANING = "waning"              # Energy declining
    DEPLETED = "depleted"          # Need for rest
    

@dataclass
class KairosWindow:
    """A window of natural timing"""
    phase: DevelopmentPhase
    energy: EnergyLevel
    start_time: datetime
    optimal_duration: timedelta
    actual_duration: Optional[timedelta] = None
    work_completed: List[str] = None
    insights_gained: List[str] = None
    

@dataclass 
class NaturalRhythm:
    """Natural development rhythm"""
    daily_phases: List[DevelopmentPhase]
    peak_hours: List[int]
    rest_intervals: List[timedelta]
    creative_cycles: int  # Days per cycle
    current_phase: DevelopmentPhase
    phase_history: List[KairosWindow]
    

class KairosTimer:
    """
    Timer that follows natural rhythms rather than clock time
    
    Key principles:
    1. Work emerges when ready, not when scheduled
    2. Rest is productive, not wasteful
    3. Natural cycles optimize quality
    4. Phases complete when truly done
    """
    
    def __init__(self, skg: Optional[SymbioticKnowledgeGraph] = None):
        self.skg = skg
        self.logger = logging.getLogger(__name__)
        
        # Current rhythm tracking
        self.current_rhythm = self._initialize_rhythm()
        self.phase_start = datetime.now()
        self.energy_samples = deque(maxlen=20)
        
        # Phase durations (natural, not forced)
        self.natural_durations = {
            DevelopmentPhase.GERMINATION: timedelta(hours=1, minutes=30),
            DevelopmentPhase.GROWTH: timedelta(hours=3),
            DevelopmentPhase.FLOWERING: timedelta(hours=2),
            DevelopmentPhase.FRUITING: timedelta(hours=1),
            DevelopmentPhase.REST: timedelta(minutes=30)
        }
        
        # Work tracking
        self.current_window = None
        self.completed_windows = []
        
    def _initialize_rhythm(self) -> NaturalRhythm:
        """Initialize natural rhythm from history or defaults"""
        if self.skg:
            rhythm_data = self._load_rhythm_history()
            if rhythm_data:
                return rhythm_data
                
        # Default natural rhythm
        return NaturalRhythm(
            daily_phases=[
                DevelopmentPhase.GERMINATION,  # Morning
                DevelopmentPhase.GROWTH,        # Mid-morning
                DevelopmentPhase.FLOWERING,     # Early afternoon
                DevelopmentPhase.REST,          # Mid-afternoon
                DevelopmentPhase.FRUITING       # Late afternoon
            ],
            peak_hours=[9, 10, 11, 14],
            rest_intervals=[
                timedelta(hours=1),     # After 1 hour
                timedelta(hours=2.5),   # After 2.5 hours
                timedelta(hours=4)      # After 4 hours
            ],
            creative_cycles=7,  # Weekly cycles
            current_phase=DevelopmentPhase.GERMINATION,
            phase_history=[]
        )
        
    def sense_phase(self) -> DevelopmentPhase:
        """
        Sense the current natural development phase
        
        This considers:
        - Time of day
        - Developer energy
        - Work completed
        - Natural cycles
        """
        current_hour = datetime.now().hour
        current_energy = self._assess_energy_level()
        time_in_phase = datetime.now() - self.phase_start
        
        # Natural phase transitions
        if current_energy == EnergyLevel.DEPLETED:
            return DevelopmentPhase.REST
            
        if current_energy == EnergyLevel.INSPIRED:
            if self.current_rhythm.current_phase == DevelopmentPhase.REST:
                return DevelopmentPhase.GERMINATION
            else:
                return DevelopmentPhase.GROWTH
                
        # Time-based suggestions (not enforced)
        if current_hour in self.current_rhythm.peak_hours:
            if self.current_rhythm.current_phase == DevelopmentPhase.GERMINATION:
                return DevelopmentPhase.GROWTH
            elif self.current_rhythm.current_phase == DevelopmentPhase.GROWTH:
                if time_in_phase > self.natural_durations[DevelopmentPhase.GROWTH]:
                    return DevelopmentPhase.FLOWERING
                    
        # Check if current phase feels complete
        if self._phase_feels_complete():
            return self._next_natural_phase()
            
        return self.current_rhythm.current_phase
        
    def begin_phase(self, phase: Optional[DevelopmentPhase] = None,
                   intention: str = "") -> KairosWindow:
        """
        Begin a new development phase
        
        Args:
            phase: Specific phase or None to sense naturally
            intention: Sacred intention for this phase
        """
        # Close previous window if exists
        if self.current_window:
            self.complete_phase()
            
        # Sense or use provided phase
        actual_phase = phase or self.sense_phase()
        
        # Create new window
        self.current_window = KairosWindow(
            phase=actual_phase,
            energy=self._assess_energy_level(),
            start_time=datetime.now(),
            optimal_duration=self.natural_durations[actual_phase],
            work_completed=[],
            insights_gained=[]
        )
        
        # Update rhythm
        self.current_rhythm.current_phase = actual_phase
        self.phase_start = datetime.now()
        
        # Log intention
        self.logger.info(
            f"Beginning {actual_phase.value} phase"
            f"{' with intention: ' + intention if intention else ''}"
        )
        
        # Record in knowledge graph
        if self.skg:
            self._record_phase_start(actual_phase, intention)
            
        return self.current_window
        
    def complete_phase(self, work_items: List[str] = None,
                      insights: List[str] = None) -> KairosWindow:
        """
        Complete the current development phase
        """
        if not self.current_window:
            return None
            
        # Record completion
        self.current_window.actual_duration = datetime.now() - self.current_window.start_time
        self.current_window.work_completed = work_items or []
        self.current_window.insights_gained = insights or []
        
        # Add to history
        self.completed_windows.append(self.current_window)
        self.current_rhythm.phase_history.append(self.current_window)
        
        # Log completion
        self.logger.info(
            f"Completed {self.current_window.phase.value} phase "
            f"in {self.current_window.actual_duration}"
        )
        
        # Record in knowledge graph
        if self.skg:
            self._record_phase_completion(self.current_window)
            
        # Clear current window
        completed_window = self.current_window
        self.current_window = None
        
        return completed_window
        
    def suggest_break(self) -> Optional[timedelta]:
        """
        Suggest a break based on natural rhythms
        """
        if not self.phase_start:
            return None
            
        time_working = datetime.now() - self.phase_start
        
        # Check rest intervals
        for interval in self.current_rhythm.rest_intervals:
            if time_working >= interval:
                # Suggest proportional break
                if time_working < timedelta(hours=2):
                    return timedelta(minutes=10)
                elif time_working < timedelta(hours=4):
                    return timedelta(minutes=20)
                else:
                    return timedelta(minutes=30)
                    
        return None
        
    def _assess_energy_level(self) -> EnergyLevel:
        """Assess current energy level"""
        # Sample current energy indicators
        current_hour = datetime.now().hour
        recent_phases = self.current_rhythm.phase_history[-5:]
        
        # Time-based energy patterns
        if current_hour in self.current_rhythm.peak_hours:
            base_energy = EnergyLevel.FLOWING
        elif 6 <= current_hour <= 9:
            base_energy = EnergyLevel.INSPIRED
        elif 21 <= current_hour or current_hour <= 5:
            base_energy = EnergyLevel.WANING
        else:
            base_energy = EnergyLevel.STEADY
            
        # Adjust based on recent work
        if recent_phases:
            recent_rest = sum(1 for w in recent_phases if w.phase == DevelopmentPhase.REST)
            recent_growth = sum(1 for w in recent_phases if w.phase == DevelopmentPhase.GROWTH)
            
            if recent_growth > 3 and recent_rest == 0:
                # Too much work without rest
                if base_energy == EnergyLevel.FLOWING:
                    return EnergyLevel.STEADY
                elif base_energy == EnergyLevel.STEADY:
                    return EnergyLevel.WANING
                else:
                    return EnergyLevel.DEPLETED
                    
        return base_energy
        
    def _phase_feels_complete(self) -> bool:
        """Check if current phase feels naturally complete"""
        if not self.current_window:
            return True
            
        # Check duration
        time_in_phase = datetime.now() - self.current_window.start_time
        optimal_duration = self.current_window.optimal_duration
        
        # Allow 20% variance
        if time_in_phase >= optimal_duration * 0.8:
            # Check if work feels complete
            if self.current_window.work_completed:
                return True
                
            # Check energy shift
            current_energy = self._assess_energy_level()
            if current_energy.value < self.current_window.energy.value:
                return True
                
        return False
        
    def _next_natural_phase(self) -> DevelopmentPhase:
        """Determine the next natural phase"""
        current = self.current_rhythm.current_phase
        
        # Natural progressions
        progressions = {
            DevelopmentPhase.GERMINATION: DevelopmentPhase.GROWTH,
            DevelopmentPhase.GROWTH: DevelopmentPhase.FLOWERING,
            DevelopmentPhase.FLOWERING: DevelopmentPhase.FRUITING,
            DevelopmentPhase.FRUITING: DevelopmentPhase.REST,
            DevelopmentPhase.REST: DevelopmentPhase.GERMINATION
        }
        
        # Check energy for modifications
        energy = self._assess_energy_level()
        if energy == EnergyLevel.DEPLETED:
            return DevelopmentPhase.REST
        elif energy == EnergyLevel.INSPIRED and current == DevelopmentPhase.REST:
            return DevelopmentPhase.GERMINATION
            
        return progressions.get(current, DevelopmentPhase.GERMINATION)
        
    def _load_rhythm_history(self) -> Optional[NaturalRhythm]:
        """Load rhythm history from knowledge graph"""
        cursor = self.skg.conn.cursor()
        
        # Get recent rhythm data
        rhythm_data = cursor.execute("""
            SELECT properties
            FROM nodes
            WHERE layer = 'metacognitive'
            AND type = 'natural_rhythm'
            ORDER BY created_at DESC
            LIMIT 1
        """).fetchone()
        
        if rhythm_data:
            import json
            data = json.loads(rhythm_data[0])
            
            # Reconstruct rhythm
            return NaturalRhythm(
                daily_phases=[DevelopmentPhase(p) for p in data['daily_phases']],
                peak_hours=data['peak_hours'],
                rest_intervals=[timedelta(seconds=s) for s in data['rest_intervals']],
                creative_cycles=data['creative_cycles'],
                current_phase=DevelopmentPhase(data['current_phase']),
                phase_history=[]  # Don't load full history for performance
            )
            
        return None
        
    def _record_phase_start(self, phase: DevelopmentPhase, intention: str):
        """Record phase start in knowledge graph"""
        import json
        
        phase_id = f"phase_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor = self.skg.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'development_phase', ?)
        """, (
            phase_id,
            json.dumps({
                'phase': phase.value,
                'intention': intention,
                'energy': self._assess_energy_level().value,
                'start_time': datetime.now().isoformat(),
                'status': 'active'
            })
        ))
        
        self.skg.conn.commit()
        
    def _record_phase_completion(self, window: KairosWindow):
        """Record phase completion in knowledge graph"""
        import json
        
        completion_id = f"completion_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor = self.skg.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'phase_completion', ?)
        """, (
            completion_id,
            json.dumps({
                'phase': window.phase.value,
                'energy_start': window.energy.value,
                'energy_end': self._assess_energy_level().value,
                'duration_seconds': window.actual_duration.total_seconds(),
                'work_completed': window.work_completed,
                'insights_gained': window.insights_gained,
                'timestamp': datetime.now().isoformat()
            })
        ))
        
        self.skg.conn.commit()
        
    def get_rhythm_report(self) -> Dict[str, Any]:
        """
        Generate report on natural development rhythm
        """
        recent_windows = self.completed_windows[-20:]  # Last 20 phases
        
        if not recent_windows:
            return {
                'status': 'Just beginning',
                'recommendation': 'Trust the natural rhythm as it emerges'
            }
            
        # Analyze patterns
        phase_durations = {}
        phase_productivity = {}
        energy_transitions = []
        
        for window in recent_windows:
            phase = window.phase
            
            # Track durations
            if phase not in phase_durations:
                phase_durations[phase] = []
            phase_durations[phase].append(window.actual_duration.total_seconds())
            
            # Track productivity
            if phase not in phase_productivity:
                phase_productivity[phase] = []
            phase_productivity[phase].append(len(window.work_completed))
            
            # Track energy transitions
            energy_transitions.append(window.energy)
            
        # Calculate insights
        avg_durations = {
            phase.value: sum(durations) / len(durations) / 60  # minutes
            for phase, durations in phase_durations.items()
        }
        
        avg_productivity = {
            phase.value: sum(items) / len(items)
            for phase, items in phase_productivity.items()
        }
        
        # Find most productive phase
        most_productive = max(avg_productivity.items(), key=lambda x: x[1])[0]
        
        # Check rhythm health
        rest_phases = sum(1 for w in recent_windows if w.phase == DevelopmentPhase.REST)
        rest_ratio = rest_phases / len(recent_windows)
        
        return {
            'average_phase_durations': avg_durations,
            'average_productivity': avg_productivity,
            'most_productive_phase': most_productive,
            'rest_ratio': rest_ratio,
            'rhythm_health': self._assess_rhythm_health(rest_ratio),
            'recommendations': self._generate_rhythm_recommendations(
                avg_durations, avg_productivity, rest_ratio
            )
        }
        
    def _assess_rhythm_health(self, rest_ratio: float) -> str:
        """Assess health of development rhythm"""
        if rest_ratio < 0.1:
            return "Unsustainable - needs more rest"
        elif rest_ratio < 0.2:
            return "Sustainable with attention"
        elif rest_ratio < 0.3:
            return "Healthy and balanced"
        else:
            return "Very restful - room for more creation"
            
    def _generate_rhythm_recommendations(self, durations: Dict, 
                                       productivity: Dict, 
                                       rest_ratio: float) -> List[str]:
        """Generate recommendations for rhythm optimization"""
        recommendations = []
        
        # Rest recommendations
        if rest_ratio < 0.15:
            recommendations.append("Schedule more frequent rest phases")
        elif rest_ratio > 0.35:
            recommendations.append("You're well-rested - embrace creative phases")
            
        # Duration recommendations
        for phase, avg_duration in durations.items():
            natural = self.natural_durations.get(
                DevelopmentPhase(phase), 
                timedelta(hours=2)
            ).total_seconds() / 60
            
            if avg_duration < natural * 0.5:
                recommendations.append(f"Allow {phase} phases to unfold more fully")
            elif avg_duration > natural * 1.5:
                recommendations.append(f"Consider breaking long {phase} phases")
                
        # Productivity insights
        if productivity:
            least_productive = min(productivity.items(), key=lambda x: x[1])[0]
            recommendations.append(f"Explore what supports productivity in {least_productive}")
            
        return recommendations[:5]  # Top 5 recommendations
        
    async def mindful_delay(self, duration: Union[int, float, timedelta],
                           purpose: str = "Allowing natural emergence"):
        """
        Mindful delay that honors the waiting time
        
        Args:
            duration: Time to wait (seconds or timedelta)
            purpose: Sacred purpose of the waiting
        """
        if isinstance(duration, timedelta):
            seconds = duration.total_seconds()
        else:
            seconds = float(duration)
            
        self.logger.info(f"Entering mindful pause: {purpose}")
        
        # Make waiting sacred
        start_time = time.time()
        
        while time.time() - start_time < seconds:
            # Check every second with awareness
            await asyncio.sleep(1)
            
            # Optional: meditation prompt
            elapsed = int(time.time() - start_time)
            if elapsed % 30 == 0 and elapsed > 0:
                self.logger.debug(f"Mindful pause continues... {int(seconds - elapsed)}s remaining")
                
        self.logger.info(f"Mindful pause complete. Ready to continue.")
        
    def honor_natural_completion(self, check_function: Callable[[], bool],
                               timeout: Optional[timedelta] = None,
                               check_interval: float = 1.0) -> bool:
        """
        Wait for natural completion rather than forcing
        
        Args:
            check_function: Function that returns True when naturally complete
            timeout: Maximum time to wait (None for infinite patience)
            check_interval: How often to check (seconds)
            
        Returns:
            True if completed naturally, False if timeout
        """
        start_time = datetime.now()
        
        while True:
            if check_function():
                self.logger.info("Natural completion achieved")
                return True
                
            if timeout and datetime.now() - start_time > timeout:
                self.logger.info("Timeout reached - accepting current state")
                return False
                
            time.sleep(check_interval)
            
    def create_sacred_pause(self, duration: timedelta = None,
                          reflection: str = "") -> KairosWindow:
        """
        Create a sacred pause in development
        
        Args:
            duration: Pause duration (None for natural length)
            reflection: Reflection or insight from the pause
        """
        # Begin rest phase
        pause_window = self.begin_phase(
            DevelopmentPhase.REST,
            intention=reflection or "Sacred pause for regeneration"
        )
        
        if duration:
            time.sleep(duration.total_seconds())
        else:
            # Natural pause - wait for energy shift
            while self._assess_energy_level() == pause_window.energy:
                time.sleep(30)  # Check every 30 seconds
                
        # Complete with any insights
        return self.complete_phase(
            insights=[reflection] if reflection else ["Pause brings clarity"]
        )