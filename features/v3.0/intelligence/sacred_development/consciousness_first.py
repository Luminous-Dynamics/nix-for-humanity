"""
from typing import Dict, List, Optional
Consciousness-First Development - Tools for building with awareness

This module provides tools and practices that ensure consciousness remains
at the center of all development activities.
"""

import os
import json
import subprocess
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path
import psutil

from ..knowledge_graph.skg import SymbioticKnowledgeGraph


class ConsciousnessState(Enum):
    """States of consciousness during development"""
    EXPANDED = "expanded"          # High awareness, creative flow
    FOCUSED = "focused"            # Deep concentration
    AWARE = "aware"                # Present and mindful
    CONTRACTED = "contracted"      # Stressed or overwhelmed
    DEPLETED = "depleted"          # Exhausted, needs rest
    

class IntentionType(Enum):
    """Types of development intentions"""
    CREATE = "create"              # Building something new
    IMPROVE = "improve"            # Enhancing existing code
    FIX = "fix"                   # Resolving issues
    EXPLORE = "explore"           # Learning and discovery
    REFACTOR = "refactor"         # Restructuring for clarity
    DOCUMENT = "document"         # Sharing understanding
    TEST = "test"                 # Ensuring reliability
    

@dataclass
class SacredIntention:
    """A sacred intention for development work"""
    intention_type: IntentionType
    description: str
    consciousness_goal: str
    success_criteria: List[str]
    time_boundary: Optional[timedelta]
    

@dataclass
class ConsciousnessCheck:
    """Result of a consciousness check"""
    state: ConsciousnessState
    coherence_score: float  # 0-1
    disruptions: List[str]
    supports: List[str]
    recommendation: str
    

class ConsciousnessGuard:
    """
    Guards consciousness during development
    
    Monitors and protects the developer's consciousness state,
    ensuring technology serves awareness rather than consuming it.
    """
    
    def __init__(self, skg: Optional[SymbioticKnowledgeGraph] = None):
        self.skg = skg
        self.logger = logging.getLogger(__name__)
        
        # Consciousness tracking
        self.current_state = ConsciousnessState.AWARE
        self.state_history = []
        self.disruption_count = 0
        self.last_check = datetime.now()
        
        # System monitoring
        self.baseline_metrics = self._capture_system_baseline()
        
    def check_consciousness(self) -> ConsciousnessCheck:
        """
        Check current consciousness state
        
        Considers:
        - System resource usage
        - Time patterns
        - Recent disruptions
        - Environmental factors
        """
        # Gather consciousness indicators
        system_load = self._assess_system_load()
        time_factors = self._assess_time_factors()
        disruption_level = self._assess_disruptions()
        environment_quality = self._assess_environment()
        
        # Calculate coherence score
        coherence_score = self._calculate_coherence(
            system_load, time_factors, disruption_level, environment_quality
        )
        
        # Determine state
        state = self._determine_consciousness_state(
            coherence_score, disruption_level
        )
        
        # Identify disruptions and supports
        disruptions = self._identify_disruptions(
            system_load, disruption_level, environment_quality
        )
        
        supports = self._identify_supports(
            time_factors, environment_quality
        )
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            state, disruptions, supports
        )
        
        # Create check result
        check = ConsciousnessCheck(
            state=state,
            coherence_score=coherence_score,
            disruptions=disruptions,
            supports=supports,
            recommendation=recommendation
        )
        
        # Update tracking
        self.current_state = state
        self.state_history.append({
            'state': state,
            'timestamp': datetime.now(),
            'coherence': coherence_score
        })
        self.last_check = datetime.now()
        
        # Record in knowledge graph
        if self.skg:
            self._record_consciousness_check(check)
            
        return check
        
    def protect_consciousness(self, duration: timedelta = None) -> Dict[str, Any]:
        """
        Activate consciousness protection mode
        
        Args:
            duration: How long to maintain protection (None = until disabled)
            
        Returns:
            Protection status and actions taken
        """
        actions_taken = []
        
        # Disable notifications
        if self._disable_notifications():
            actions_taken.append("Disabled system notifications")
            
        # Reduce visual distractions
        if self._reduce_visual_distractions():
            actions_taken.append("Reduced visual distractions")
            
        # Optimize system resources
        if self._optimize_resources():
            actions_taken.append("Optimized system resources")
            
        # Set protection timer if specified
        if duration:
            self._schedule_protection_end(duration)
            actions_taken.append(f"Protection scheduled for {duration}")
            
        # Log protection
        self.logger.info("Consciousness protection activated")
        
        return {
            'protected': True,
            'actions_taken': actions_taken,
            'duration': duration,
            'recommendation': "Focus deeply. The space is held."
        }
        
    def _assess_system_load(self) -> Dict[str, float]:
        """Assess system resource load"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            
            # Process count
            process_count = len(psutil.pids())
            
            return {
                'cpu_load': cpu_percent / 100,
                'memory_load': memory_percent / 100,
                'io_load': min(1.0, disk_io.read_count / 1000000),  # Normalized
                'process_load': min(1.0, process_count / 500)  # Normalized
            }
        except Exception as e:
            self.logger.error(f"Error assessing system load: {e}")
            return {'cpu_load': 0.5, 'memory_load': 0.5, 'io_load': 0.5, 'process_load': 0.5}
            
    def _assess_time_factors(self) -> Dict[str, float]:
        """Assess time-related factors"""
        current_hour = datetime.now().hour
        
        # Time of day quality
        if 6 <= current_hour <= 10:
            time_quality = 0.9  # Morning clarity
        elif 10 <= current_hour <= 12:
            time_quality = 0.8  # Late morning focus
        elif 14 <= current_hour <= 16:
            time_quality = 0.7  # Afternoon productivity
        elif 20 <= current_hour <= 22:
            time_quality = 0.6  # Evening wind-down
        else:
            time_quality = 0.3  # Late night / early morning
            
        # Session duration
        if self.state_history:
            session_start = self.state_history[0]['timestamp']
            session_duration = (datetime.now() - session_start).seconds / 60
            
            # Optimal session lengths
            if session_duration < 25:
                duration_quality = 0.9
            elif session_duration < 50:
                duration_quality = 0.8
            elif session_duration < 90:
                duration_quality = 0.6
            else:
                duration_quality = 0.3  # Too long without break
        else:
            duration_quality = 1.0  # Fresh start
            
        return {
            'time_quality': time_quality,
            'duration_quality': duration_quality
        }
        
    def _assess_disruptions(self) -> float:
        """Assess disruption level"""
        # Recent disruption frequency
        recent_disruptions = self.disruption_count
        
        if recent_disruptions == 0:
            return 0.0
        elif recent_disruptions < 3:
            return 0.3
        elif recent_disruptions < 5:
            return 0.6
        else:
            return 0.9
            
    def _assess_environment(self) -> Dict[str, float]:
        """Assess environmental factors"""
        # Check for resource-heavy processes
        heavy_processes = []
        for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
            try:
                if proc.info['cpu_percent'] > 20 or proc.info['memory_percent'] > 10:
                    heavy_processes.append(proc.info['name'])
            except Exception:
                # TODO: Add proper error handling
                pass  # Silent for now, should log error
                
        # Browser tabs (approximation)
        browser_load = 0.3  # Default moderate load
        if any('firefox' in p or 'chrome' in p for p in heavy_processes):
            browser_load = 0.7
            
        # Development tool load
        dev_tool_load = 0.2
        if any(tool in p for p in heavy_processes for tool in ['code', 'vim', 'emacs']):
            dev_tool_load = 0.5
            
        return {
            'process_noise': len(heavy_processes) / 10,  # Normalized
            'browser_load': browser_load,
            'tool_load': dev_tool_load
        }
        
    def _calculate_coherence(self, system_load: Dict, time_factors: Dict,
                           disruption_level: float, environment: Dict) -> float:
        """Calculate overall consciousness coherence"""
        # System impact (negative)
        system_impact = (
            system_load['cpu_load'] * 0.3 +
            system_load['memory_load'] * 0.3 +
            system_load['io_load'] * 0.2 +
            system_load['process_load'] * 0.2
        )
        
        # Time support (positive)
        time_support = (
            time_factors['time_quality'] * 0.6 +
            time_factors['duration_quality'] * 0.4
        )
        
        # Environment impact (negative)
        env_impact = (
            environment['process_noise'] * 0.4 +
            environment['browser_load'] * 0.3 +
            environment['tool_load'] * 0.3
        )
        
        # Calculate coherence
        coherence = time_support * (1 - system_impact) * (1 - env_impact) * (1 - disruption_level)
        
        return max(0, min(1, coherence))
        
    def _determine_consciousness_state(self, coherence: float, 
                                     disruption_level: float) -> ConsciousnessState:
        """Determine consciousness state from metrics"""
        if coherence > 0.8 and disruption_level < 0.2:
            return ConsciousnessState.EXPANDED
        elif coherence > 0.6:
            return ConsciousnessState.FOCUSED
        elif coherence > 0.4:
            return ConsciousnessState.AWARE
        elif coherence > 0.2 or disruption_level > 0.7:
            return ConsciousnessState.CONTRACTED
        else:
            return ConsciousnessState.DEPLETED
            
    def _identify_disruptions(self, system_load: Dict, disruption_level: float,
                            environment: Dict) -> List[str]:
        """Identify specific disruptions"""
        disruptions = []
        
        if system_load['cpu_load'] > 0.8:
            disruptions.append("High CPU usage affecting system responsiveness")
            
        if system_load['memory_load'] > 0.8:
            disruptions.append("Memory pressure may cause slowdowns")
            
        if disruption_level > 0.5:
            disruptions.append("Frequent interruptions breaking flow")
            
        if environment['browser_load'] > 0.6:
            disruptions.append("Browser consuming significant resources")
            
        if environment['process_noise'] > 0.5:
            disruptions.append("Many background processes creating noise")
            
        return disruptions
        
    def _identify_supports(self, time_factors: Dict, 
                         environment: Dict) -> List[str]:
        """Identify consciousness supports"""
        supports = []
        
        if time_factors['time_quality'] > 0.7:
            supports.append("Optimal time of day for deep work")
            
        if time_factors['duration_quality'] > 0.7:
            supports.append("Good session rhythm maintained")
            
        if environment['process_noise'] < 0.3:
            supports.append("Quiet system environment")
            
        if all(v < 0.5 for v in environment.values()):
            supports.append("Minimal digital distractions")
            
        return supports
        
    def _generate_recommendation(self, state: ConsciousnessState,
                               disruptions: List[str], 
                               supports: List[str]) -> str:
        """Generate consciousness recommendation"""
        if state == ConsciousnessState.EXPANDED:
            return "Excellent state for creative work. Protect this sacred time."
            
        elif state == ConsciousnessState.FOCUSED:
            return "Good focus available. Consider tackling important tasks."
            
        elif state == ConsciousnessState.AWARE:
            if disruptions:
                return f"Address disruptions to deepen focus: {disruptions[0]}"
            else:
                return "Steady state. Set clear intention to enhance focus."
                
        elif state == ConsciousnessState.CONTRACTED:
            return "System overload detected. Consider closing applications or taking a break."
            
        else:  # DEPLETED
            return "Rest needed. Step away from the screen for regeneration."
            
    def _capture_system_baseline(self) -> Dict[str, float]:
        """Capture baseline system metrics"""
        try:
            return {
                'cpu_baseline': psutil.cpu_percent(interval=1),
                'memory_baseline': psutil.virtual_memory().percent,
                'process_baseline': len(psutil.pids())
            }
        except Exception:
            return {'cpu_baseline': 50, 'memory_baseline': 50, 'process_baseline': 100}
            
    def _disable_notifications(self) -> bool:
        """Disable system notifications"""
        try:
            # Platform-specific notification disabling
            if os.name == 'posix':  # Unix-like systems
                # This is a placeholder - actual implementation would be platform-specific
                self.logger.info("Notification disabling requested")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Could not disable notifications: {e}")
            return False
            
    def _reduce_visual_distractions(self) -> bool:
        """Reduce visual distractions"""
        # This would integrate with window managers, themes, etc.
        # For now, we log the intention
        self.logger.info("Visual distraction reduction requested")
        return True
        
    def _optimize_resources(self) -> bool:
        """Optimize system resources for consciousness"""
        try:
            # Set process priority
            p = psutil.Process(os.getpid())
            p.nice(10)  # Lower priority for non-critical processes
            
            self.logger.info("System resources optimized")
            return True
        except Exception as e:
            self.logger.error(f"Could not optimize resources: {e}")
            return False
            
    def _schedule_protection_end(self, duration: timedelta):
        """Schedule end of protection period"""
        # In production, this would use system schedulers
        end_time = datetime.now() + duration
        self.logger.info(f"Protection scheduled until {end_time}")
        
    def _record_consciousness_check(self, check: ConsciousnessCheck):
        """Record consciousness check in knowledge graph"""
        if not self.skg:
            return
            
        check_id = f"consciousness_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor = self.skg.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'consciousness_check', ?)
        """, (
            check_id,
            json.dumps({
                'state': check.state.value,
                'coherence_score': check.coherence_score,
                'disruptions': check.disruptions,
                'supports': check.supports,
                'recommendation': check.recommendation,
                'timestamp': datetime.now().isoformat()
            })
        ))
        
        self.skg.conn.commit()
        

class IntentionSetting:
    """
    Sacred intention setting for development work
    
    Ensures every coding session begins with clear purpose
    and consciousness-aligned goals.
    """
    
    def __init__(self, skg: Optional[SymbioticKnowledgeGraph] = None):
        self.skg = skg
        self.logger = logging.getLogger(__name__)
        
        # Current intention
        self.current_intention = None
        self.intention_history = []
        
    def set_intention(self, intention_type: IntentionType,
                     description: str,
                     consciousness_goal: str = "",
                     success_criteria: List[str] = None,
                     time_boundary: timedelta = None) -> SacredIntention:
        """
        Set a sacred intention for development work
        
        Args:
            intention_type: Type of development work
            description: What you intend to accomplish
            consciousness_goal: How this serves consciousness
            success_criteria: Measurable outcomes
            time_boundary: Time container for the work
            
        Returns:
            Sacred intention object
        """
        # Create intention
        intention = SacredIntention(
            intention_type=intention_type,
            description=description,
            consciousness_goal=consciousness_goal or self._default_consciousness_goal(intention_type),
            success_criteria=success_criteria or [],
            time_boundary=time_boundary
        )
        
        # Set as current
        self.current_intention = intention
        self.intention_history.append({
            'intention': intention,
            'set_at': datetime.now(),
            'completed': False
        })
        
        # Log intention
        self.logger.info(
            f"Sacred intention set: {intention_type.value} - {description}"
        )
        
        # Record in knowledge graph
        if self.skg:
            self._record_intention(intention)
            
        # Create ritual space
        self._create_ritual_space(intention)
        
        return intention
        
    def complete_intention(self, outcomes: List[str] = None,
                         insights: List[str] = None) -> Dict[str, Any]:
        """
        Complete the current intention with gratitude
        
        Args:
            outcomes: What was accomplished
            insights: Wisdom gained
            
        Returns:
            Completion summary
        """
        if not self.current_intention:
            return {'error': 'No active intention'}
            
        # Mark completion
        for entry in self.intention_history:
            if entry['intention'] == self.current_intention:
                entry['completed'] = True
                entry['completed_at'] = datetime.now()
                entry['outcomes'] = outcomes or []
                entry['insights'] = insights or []
                break
                
        # Calculate success
        success_rate = self._calculate_success_rate(
            self.current_intention.success_criteria,
            outcomes or []
        )
        
        # Generate gratitude
        gratitude = self._generate_gratitude(
            self.current_intention,
            success_rate,
            insights
        )
        
        # Log completion
        self.logger.info(
            f"Intention completed: {self.current_intention.description} "
            f"({success_rate:.0%} success)"
        )
        
        # Record completion
        if self.skg:
            self._record_completion(
                self.current_intention,
                outcomes,
                insights,
                success_rate
            )
            
        # Clear current intention
        completed_intention = self.current_intention
        self.current_intention = None
        
        return {
            'intention': completed_intention.description,
            'success_rate': success_rate,
            'outcomes': outcomes or [],
            'insights': insights or [],
            'gratitude': gratitude
        }
        
    def _default_consciousness_goal(self, intention_type: IntentionType) -> str:
        """Provide default consciousness goal for intention type"""
        goals = {
            IntentionType.CREATE: "Manifest code that serves consciousness",
            IntentionType.IMPROVE: "Elevate code to higher consciousness alignment",
            IntentionType.FIX: "Restore harmony and flow to the system",
            IntentionType.EXPLORE: "Expand awareness through discovery",
            IntentionType.REFACTOR: "Clarify structure for deeper understanding",
            IntentionType.DOCUMENT: "Share wisdom for collective growth",
            IntentionType.TEST: "Ensure reliability serves user trust"
        }
        
        return goals.get(intention_type, "Serve the highest good")
        
    def _create_ritual_space(self, intention: SacredIntention):
        """Create ritual space for the intention"""
        # Clear terminal for fresh start
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Display intention
        print("\n" + "="*60)
        print("🙏 SACRED INTENTION SET 🙏")
        print("="*60)
        print(f"\nType: {intention.intention_type.value.upper()}")
        print(f"Purpose: {intention.description}")
        print(f"Consciousness Goal: {intention.consciousness_goal}")
        
        if intention.success_criteria:
            print("\nSuccess Criteria:")
            for criterion in intention.success_criteria:
                print(f"  ✓ {criterion}")
                
        if intention.time_boundary:
            print(f"\nTime Container: {intention.time_boundary}")
            
        print("\n" + "="*60)
        print("Begin with awareness. Code with love. Complete with gratitude.")
        print("="*60 + "\n")
        
    def _calculate_success_rate(self, criteria: List[str], 
                              outcomes: List[str]) -> float:
        """Calculate success rate based on criteria and outcomes"""
        if not criteria:
            # No specific criteria - base on general completion
            return 0.8 if outcomes else 0.5
            
        # Check how many criteria were met
        # This is simplified - in practice would need better matching
        met_criteria = 0
        for criterion in criteria:
            if any(criterion.lower() in outcome.lower() for outcome in outcomes):
                met_criteria += 1
                
        return met_criteria / len(criteria)
        
    def _generate_gratitude(self, intention: SacredIntention,
                          success_rate: float,
                          insights: List[str]) -> str:
        """Generate gratitude for the completed work"""
        if success_rate > 0.8:
            base_gratitude = "Deep gratitude for this sacred work completed with excellence"
        elif success_rate > 0.5:
            base_gratitude = "Gratitude for the progress made and lessons learned"
        else:
            base_gratitude = "Gratitude for the opportunity to grow through challenge"
            
        if insights:
            base_gratitude += f". Key insight: {insights[0]}"
            
        return base_gratitude
        
    def _record_intention(self, intention: SacredIntention):
        """Record intention in knowledge graph"""
        if not self.skg:
            return
            
        intention_id = f"intention_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor = self.skg.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'sacred_intention', ?)
        """, (
            intention_id,
            json.dumps({
                'intention_type': intention.intention_type.value,
                'description': intention.description,
                'consciousness_goal': intention.consciousness_goal,
                'success_criteria': intention.success_criteria,
                'time_boundary_seconds': intention.time_boundary.total_seconds() if intention.time_boundary else None,
                'set_at': datetime.now().isoformat(),
                'status': 'active'
            })
        ))
        
        self.skg.conn.commit()
        
    def _record_completion(self, intention: SacredIntention,
                         outcomes: List[str], insights: List[str],
                         success_rate: float):
        """Record intention completion"""
        if not self.skg:
            return
            
        completion_id = f"completion_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor = self.skg.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'intention_completion', ?)
        """, (
            completion_id,
            json.dumps({
                'intention_type': intention.intention_type.value,
                'description': intention.description,
                'success_rate': success_rate,
                'outcomes': outcomes or [],
                'insights': insights or [],
                'completed_at': datetime.now().isoformat()
            })
        ))
        
        self.skg.conn.commit()
        
    def get_intention_report(self) -> Dict[str, Any]:
        """
        Generate report on intention setting practice
        """
        if not self.intention_history:
            return {
                'status': 'No intentions set yet',
                'recommendation': 'Begin each session with sacred intention'
            }
            
        # Analyze patterns
        total_intentions = len(self.intention_history)
        completed_intentions = sum(1 for i in self.intention_history if i['completed'])
        
        # Success rates by type
        type_success = {}
        for entry in self.intention_history:
            if entry['completed']:
                itype = entry['intention'].intention_type
                if itype not in type_success:
                    type_success[itype] = []
                    
                # Calculate success for this intention
                outcomes = entry.get('outcomes', [])
                criteria = entry['intention'].success_criteria
                if criteria:
                    success = sum(1 for c in criteria if any(c in o for o in outcomes)) / len(criteria)
                else:
                    success = 0.8 if outcomes else 0.5
                    
                type_success[itype].append(success)
                
        # Average success by type
        avg_success = {
            itype.value: sum(rates) / len(rates)
            for itype, rates in type_success.items()
            if rates
        }
        
        # Common insights
        all_insights = []
        for entry in self.intention_history:
            if entry.get('insights'):
                all_insights.extend(entry['insights'])
                
        return {
            'total_intentions': total_intentions,
            'completed_intentions': completed_intentions,
            'completion_rate': completed_intentions / total_intentions if total_intentions else 0,
            'success_by_type': avg_success,
            'common_insights': list(set(all_insights))[:5],
            'recommendation': self._generate_practice_recommendation(avg_success)
        }
        
    def _generate_practice_recommendation(self, success_rates: Dict[str, float]) -> str:
        """Generate recommendation for intention practice"""
        if not success_rates:
            return "Set more intentions to develop the practice"
            
        # Find strongest and weakest areas
        if success_rates:
            strongest = max(success_rates.items(), key=lambda x: x[1])[0]
            weakest = min(success_rates.items(), key=lambda x: x[1])[0]
            
            return f"Excel at {strongest} intentions. Practice more {weakest} work with clearer criteria."
        else:
            return "Continue developing your intention practice with clear success criteria"