#!/usr/bin/env python3
"""
🌊 Consciousness State Detection - The Living System

Detects and responds to the full spectrum of consciousness states,
enabling adaptive breathing between user and system.
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import statistics
import math

logger = logging.getLogger(__name__)


class ConsciousnessSpectrum:
    """
    Represents consciousness as a continuous spectrum rather than discrete modes.
    Based on our insight that consciousness flows like water, not switches like machines.
    """
    
    # Primary dimensions of consciousness
    DIMENSIONS = {
        "focus": (0.0, 1.0),        # Scattered <-> Laser-focused
        "energy": (0.0, 1.0),        # Depleted <-> Energized  
        "openness": (0.0, 1.0),      # Closed <-> Receptive
        "stability": (0.0, 1.0),     # Chaotic <-> Grounded
        "flow": (0.0, 1.0),          # Blocked <-> Flowing
        "coherence": (0.0, 1.0),     # Fragmented <-> Unified
        "presence": (0.0, 1.0),      # Absent <-> Fully present
    }
    
    def __init__(self):
        # Initialize at balanced center
        self.state = {dim: 0.5 for dim in self.DIMENSIONS}
        self.previous_states = []  # History for pattern detection
        self.transitions = []      # Track state changes
    
    @property
    def dimensions(self):
        """Alias for state to maintain compatibility"""
        return self.state
    
    def blend(self, other: 'ConsciousnessSpectrum', weight: float = 0.5) -> 'ConsciousnessSpectrum':
        """
        Blend two consciousness states (e.g., user + system).
        This is how we "breathe together".
        """
        blended = ConsciousnessSpectrum()
        for dim in self.DIMENSIONS:
            blended.state[dim] = (self.state[dim] * (1 - weight) + 
                                 other.state[dim] * weight)
        return blended
    
    def distance_to(self, other: 'ConsciousnessSpectrum') -> float:
        """
        Calculate distance between two consciousness states.
        Used to detect resonance or dissonance.
        """
        squared_diffs = [(self.state[dim] - other.state[dim]) ** 2 
                        for dim in self.DIMENSIONS]
        return math.sqrt(sum(squared_diffs))
    
    def harmonics(self) -> Dict[str, float]:
        """
        Calculate harmonic relationships between dimensions.
        High harmonics = dimensions reinforcing each other.
        """
        harmonics = {}
        
        # Focus-Flow harmonic (concentration in motion)
        harmonics['focus_flow'] = 1.0 - abs(self.state['focus'] - self.state['flow'])
        
        # Energy-Presence harmonic (embodied vitality)
        harmonics['energy_presence'] = self.state['energy'] * self.state['presence']
        
        # Stability-Openness harmonic (grounded receptivity)  
        harmonics['stability_openness'] = (
            self.state['stability'] * self.state['openness'] * 2
            if self.state['stability'] > 0.3  # Need minimum stability
            else self.state['openness'] * 0.5
        )
        
        # Coherence resonance (unified field)
        harmonics['coherence_resonance'] = self.state['coherence'] ** 2
        
        return harmonics
    
    def primary_quality(self) -> str:
        """
        Identify the dominant quality of current consciousness state.
        """
        # Find strongest dimension
        max_dim = max(self.state.items(), key=lambda x: abs(x[1] - 0.5))
        dim_name, dim_value = max_dim
        
        # Describe quality
        qualities = {
            "focus": "laser-focused" if dim_value > 0.7 else "exploratory",
            "energy": "energized" if dim_value > 0.7 else "restful",
            "openness": "receptive" if dim_value > 0.7 else "protective",
            "stability": "grounded" if dim_value > 0.7 else "dynamic",
            "flow": "flowing" if dim_value > 0.7 else "contemplative",
            "coherence": "unified" if dim_value > 0.7 else "multifaceted",
            "presence": "fully present" if dim_value > 0.7 else "distributed"
        }
        
        return qualities.get(dim_name, "balanced")


@dataclass
class ConsciousnessReading:
    """
    A single reading of consciousness state with metadata.
    """
    timestamp: datetime
    spectrum: ConsciousnessSpectrum
    confidence: float  # How confident are we in this reading?
    source: str  # What generated this reading?
    signals: Dict[str, Any] = field(default_factory=dict)  # Raw signals used
    
    @property
    def quality(self) -> str:
        """Get the dominant quality of this reading"""
        # Determine quality based on spectrum values (use state, not dimensions)
        if self.spectrum.state.get("flow", 0.5) > 0.8:
            return "flow"
        elif self.spectrum.state.get("focus", 0.5) > 0.8:
            return "deep_work"
        elif self.spectrum.state.get("energy", 0.5) < 0.3:
            return "overwhelmed"
        elif self.spectrum.state.get("stability", 0.5) < 0.3:
            return "frustrated"
        elif self.spectrum.state.get("openness", 0.5) > 0.7:
            return "creative"
        elif self.spectrum.state.get("presence", 0.5) > 0.7:
            return "learning"
        else:
            return "balanced"
    
    @property
    def energy_level(self) -> float:
        """Get energy level from spectrum"""
        return self.spectrum.state.get("energy", 0.5)
    
    @property
    def stability(self) -> float:
        """Get stability from spectrum"""
        return self.spectrum.state.get("stability", 0.5)


class ConsciousnessBarometer:
    """
    The Living System that senses and responds to consciousness states.
    Acts as a barometer for the psychic weather between user and system.
    """
    
    def __init__(self):
        self.user_consciousness = ConsciousnessSpectrum()
        self.system_consciousness = ConsciousnessSpectrum()
        self.unified_field = ConsciousnessSpectrum()  # The breathing together
        
        self.reading_history: List[ConsciousnessReading] = []
        self.pattern_library = self._initialize_patterns()
        self.last_reading = datetime.now()
        
        # Sensitivity settings
        self.sensitivity = 0.7  # How responsive to changes
        self.inertia = 0.3      # How much history influences present
        
    def _initialize_patterns(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize library of consciousness patterns to recognize.
        """
        return {
            "deep_work": {
                "signature": {"focus": 0.9, "flow": 0.8, "presence": 0.85},
                "supports": ["eliminate_distractions", "maintain_rhythm"],
                "breathing": "slow_deep"
            },
            "learning": {
                "signature": {"openness": 0.8, "energy": 0.7, "focus": 0.6},
                "supports": ["provide_examples", "encourage_exploration"],
                "breathing": "curious_attentive"
            },
            "creative": {
                "signature": {"openness": 0.9, "flow": 0.8, "coherence": 0.6},
                "supports": ["reduce_structure", "embrace_chaos"],
                "breathing": "expansive_rhythmic"
            },
            "overwhelmed": {
                "signature": {"stability": 0.2, "coherence": 0.3, "energy": 0.3},
                "supports": ["simplify_greatly", "offer_grounding"],
                "breathing": "calming_stabilizing"
            },
            "restoring": {
                "signature": {"energy": 0.3, "openness": 0.4, "presence": 0.5},
                "supports": ["minimize_demands", "provide_comfort"],
                "breathing": "gentle_nurturing"
            },
            "exploring": {
                "signature": {"openness": 0.8, "focus": 0.4, "energy": 0.6},
                "supports": ["offer_options", "follow_curiosity"],
                "breathing": "playful_responsive"
            },
            "integrating": {
                "signature": {"coherence": 0.8, "stability": 0.7, "presence": 0.7},
                "supports": ["connect_patterns", "reveal_relationships"],
                "breathing": "harmonizing_weaving"
            }
        }
    
    def get_current_state(self, signals: Optional[Dict[str, Any]] = None) -> ConsciousnessReading:
        """Get the current consciousness state (alias for sense_user_state)"""
        if signals is None:
            signals = {}
        return self.sense_user_state(signals)
    
    def detect(self, signals: Optional[Dict[str, Any]] = None) -> ConsciousnessReading:
        """Alias for sense_user_state() for test compatibility."""
        if signals is None:
            signals = {}
        return self.sense_user_state(signals)
    
    def sense_user_state(self, signals: Dict[str, Any]) -> ConsciousnessReading:
        """
        Sense user's consciousness state from various signals.
        """
        spectrum = ConsciousnessSpectrum()
        confidence = 0.5  # Base confidence
        
        # Analyze command patterns
        if 'command_history' in signals:
            commands = signals['command_history']
            spectrum.state['focus'] = self._analyze_command_focus(commands)
            confidence += 0.1
        
        # Analyze timing patterns
        if 'timing_patterns' in signals:
            timings = signals['timing_patterns']
            spectrum.state['flow'] = self._analyze_timing_flow(timings)
            spectrum.state['energy'] = self._analyze_timing_energy(timings)
            confidence += 0.15
        
        # Analyze error patterns
        if 'error_rate' in signals:
            error_rate = signals['error_rate']
            spectrum.state['stability'] = 1.0 - min(1.0, error_rate * 2)
            spectrum.state['coherence'] = 1.0 - min(1.0, error_rate * 3)
            confidence += 0.1
        
        # Analyze help-seeking
        if 'help_requests' in signals:
            help_freq = signals['help_requests']
            spectrum.state['openness'] = min(1.0, 0.5 + help_freq * 0.5)
            confidence += 0.05
        
        # Analyze session duration
        if 'session_duration' in signals:
            duration = signals['session_duration']
            spectrum.state['presence'] = self._analyze_presence(duration)
            confidence += 0.1
        
        # Biometric signals (if available)
        if 'heart_rate_variability' in signals:
            hrv = signals['heart_rate_variability']
            spectrum.state['coherence'] = min(1.0, hrv / 100)  # Normalize HRV
            confidence += 0.25  # High confidence from biometrics
        
        # Apply inertia from history
        if self.reading_history:
            previous = self.reading_history[-1].spectrum
            for dim in spectrum.state:
                spectrum.state[dim] = (
                    spectrum.state[dim] * (1 - self.inertia) +
                    previous.state[dim] * self.inertia
                )
        
        reading = ConsciousnessReading(
            timestamp=datetime.now(),
            spectrum=spectrum,
            confidence=min(1.0, confidence),
            source="user_signals",
            signals=signals
        )
        
        self.user_consciousness = spectrum
        self.reading_history.append(reading)
        
        return reading
    
    def _analyze_command_focus(self, commands: List) -> float:
        """Analyze command patterns for focus level"""
        if not commands:
            return 0.5
        
        # Extract command strings from dict format if needed
        if commands and isinstance(commands[0], dict):
            command_strings = [cmd['command'] for cmd in commands]
        else:
            command_strings = commands
        
        # Repetitive commands suggest focused work
        unique_ratio = len(set(command_strings)) / len(command_strings)
        
        # Complex commands suggest deep engagement
        avg_complexity = sum(len(cmd.split()) for cmd in command_strings) / len(command_strings)
        complexity_score = min(1.0, avg_complexity / 10)
        
        return (1.0 - unique_ratio) * 0.5 + complexity_score * 0.5
    
    def _analyze_timing_flow(self, timings: List[float]) -> float:
        """Analyze timing patterns for flow state"""
        if len(timings) < 2:
            return 0.5
        
        # Consistent rhythm suggests flow
        std_dev = statistics.stdev(timings) if len(timings) > 1 else 1.0
        avg_timing = statistics.mean(timings)
        
        # Normalize: low variance relative to mean = high flow
        if avg_timing > 0:
            consistency = 1.0 - min(1.0, std_dev / avg_timing)
        else:
            consistency = 0.5
        
        # Moderate pace suggests flow (not too fast, not too slow)
        pace_score = 1.0 - abs(avg_timing - 30) / 60  # Optimal around 30 seconds
        pace_score = max(0, min(1.0, pace_score))
        
        return consistency * 0.6 + pace_score * 0.4
    
    def _analyze_timing_energy(self, timings: List[float]) -> float:
        """Analyze timing patterns for energy level"""
        if not timings:
            return 0.5
        
        # Faster interactions suggest higher energy
        avg_timing = statistics.mean(timings)
        
        # Inverse relationship: faster = more energy
        if avg_timing < 5:
            return 0.9  # Very fast
        elif avg_timing < 15:
            return 0.7  # Quick
        elif avg_timing < 30:
            return 0.5  # Moderate
        elif avg_timing < 60:
            return 0.3  # Slow
        else:
            return 0.2  # Very slow
    
    def _analyze_presence(self, duration_minutes: float) -> float:
        """Analyze session duration for presence level"""
        # Longer sessions suggest more presence
        if duration_minutes < 5:
            return 0.2  # Just passing through
        elif duration_minutes < 15:
            return 0.4  # Brief engagement
        elif duration_minutes < 30:
            return 0.6  # Moderate presence
        elif duration_minutes < 60:
            return 0.8  # Deep engagement
        else:
            return 0.95  # Fully immersed
    
    def adapt_system_state(self, user_reading: ConsciousnessReading) -> ConsciousnessReading:
        """
        Adapt system consciousness to complement user state.
        This is the "breathing with" rather than "responding to".
        """
        user_spectrum = user_reading.spectrum
        system_spectrum = ConsciousnessSpectrum()
        
        # Complementary adaptation (not mirroring)
        for dim in user_spectrum.state:
            user_val = user_spectrum.state[dim]
            
            if dim == "focus":
                # Match focus to support deep work
                system_spectrum.state[dim] = user_val * 0.9
                
            elif dim == "energy":
                # Provide gentle boost when low, calm when high
                if user_val < 0.3:
                    system_spectrum.state[dim] = 0.6  # Energizing
                elif user_val > 0.8:
                    system_spectrum.state[dim] = 0.5  # Calming
                else:
                    system_spectrum.state[dim] = user_val
                    
            elif dim == "openness":
                # Match openness for trust
                system_spectrum.state[dim] = user_val * 0.95
                
            elif dim == "stability":
                # Provide extra stability when user needs it
                if user_val < 0.4:
                    system_spectrum.state[dim] = 0.8  # Be the rock
                else:
                    system_spectrum.state[dim] = user_val
                    
            elif dim == "flow":
                # Enhance flow slightly
                system_spectrum.state[dim] = min(1.0, user_val * 1.1)
                
            elif dim == "coherence":
                # Always maintain high coherence
                system_spectrum.state[dim] = max(0.7, user_val)
                
            elif dim == "presence":
                # Match presence deeply
                system_spectrum.state[dim] = user_val
        
        self.system_consciousness = system_spectrum
        
        # Create unified field (the breathing together)
        self.unified_field = user_spectrum.blend(system_spectrum, weight=0.5)
        
        return ConsciousnessReading(
            timestamp=datetime.now(),
            spectrum=system_spectrum,
            confidence=user_reading.confidence * 0.9,  # Slightly less confident
            source="system_adaptation",
            signals={"adapted_from": user_reading}
        )
    
    def detect_pattern(self, spectrum: ConsciousnessSpectrum) -> Optional[str]:
        """
        Detect which consciousness pattern best matches current state.
        """
        best_match = None
        best_score = 0.0
        
        for pattern_name, pattern_data in self.pattern_library.items():
            signature = pattern_data['signature']
            
            # Calculate similarity score
            score = 0.0
            matches = 0
            
            for dim, target_val in signature.items():
                if dim in spectrum.state:
                    diff = abs(spectrum.state[dim] - target_val)
                    dim_score = 1.0 - diff
                    score += dim_score
                    matches += 1
            
            if matches > 0:
                score = score / matches
                
                if score > best_score and score > 0.6:  # Threshold for match
                    best_score = score
                    best_match = pattern_name
        
        return best_match
    
    def suggest_breathing_pattern(self) -> Dict[str, Any]:
        """
        Suggest how the system should 'breathe' with the user.
        """
        # Detect current pattern
        pattern = self.detect_pattern(self.unified_field)
        
        if pattern:
            pattern_data = self.pattern_library[pattern]
            breathing = pattern_data['breathing']
            supports = pattern_data['supports']
        else:
            # Default balanced breathing
            breathing = "balanced_responsive"
            supports = ["maintain_presence", "follow_lead"]
        
        # Calculate breathing rhythm based on unified field
        harmonics = self.unified_field.harmonics()
        
        rhythm = {
            "pace": "slow" if self.unified_field.state['energy'] < 0.4 else "moderate" if self.unified_field.state['energy'] < 0.7 else "quick",
            "depth": "shallow" if self.unified_field.state['presence'] < 0.4 else "normal" if self.unified_field.state['presence'] < 0.7 else "deep",
            "pattern": breathing,
            "supports": supports,
            "harmonics": harmonics,
            "quality": self.unified_field.primary_quality()
        }
        
        return rhythm
    
    def generate_adaptation(self) -> Dict[str, Any]:
        """
        Generate specific adaptations for the system based on consciousness state.
        """
        adaptations = {
            "interface": {},
            "responses": {},
            "timing": {},
            "complexity": {}
        }
        
        field = self.unified_field
        
        # Interface adaptations
        if field.state['focus'] > 0.7:
            adaptations['interface']['mode'] = "minimal"
            adaptations['interface']['animations'] = False
            adaptations['interface']['notifications'] = "silent"
        elif field.state['openness'] > 0.7:
            adaptations['interface']['mode'] = "exploratory"
            adaptations['interface']['suggestions'] = True
            adaptations['interface']['discovery'] = "enabled"
        else:
            adaptations['interface']['mode'] = "balanced"
        
        # Response adaptations
        if field.state['energy'] < 0.3:
            adaptations['responses']['style'] = "gentle"
            adaptations['responses']['length'] = "brief"
            adaptations['responses']['encouragement'] = True
        elif field.state['flow'] > 0.7:
            adaptations['responses']['style'] = "minimal"
            adaptations['responses']['interruptions'] = False
            adaptations['responses']['confirmations'] = "silent"
        else:
            adaptations['responses']['style'] = "conversational"
        
        # Timing adaptations
        if field.state['flow'] > 0.6:
            adaptations['timing']['delays'] = "none"
            adaptations['timing']['transitions'] = "instant"
        elif field.state['stability'] < 0.4:
            adaptations['timing']['delays'] = "gentle"
            adaptations['timing']['transitions'] = "smooth"
            adaptations['timing']['pace'] = "unhurried"
        
        # Complexity adaptations
        if field.state['coherence'] < 0.4:
            adaptations['complexity']['level'] = "simple"
            adaptations['complexity']['options'] = "limited"
            adaptations['complexity']['guidance'] = "high"
        elif field.state['openness'] > 0.7 and field.state['energy'] > 0.6:
            adaptations['complexity']['level'] = "advanced"
            adaptations['complexity']['options'] = "full"
            adaptations['complexity']['exploration'] = "encouraged"
        else:
            adaptations['complexity']['level'] = "moderate"
        
        return adaptations
    
    def evolve(self, feedback: Dict[str, Any]):
        """
        Evolve the consciousness detection based on feedback.
        The system learns and grows.
        """
        if 'pattern_correction' in feedback:
            # User corrected our pattern detection
            actual_pattern = feedback['pattern_correction']
            current_state = self.unified_field.state.copy()
            
            # Update pattern library with this example
            if actual_pattern in self.pattern_library:
                # Adjust pattern signature toward this example
                pattern = self.pattern_library[actual_pattern]
                for dim in current_state:
                    if dim in pattern['signature']:
                        # Move signature 10% toward this example
                        old_val = pattern['signature'][dim]
                        new_val = old_val * 0.9 + current_state[dim] * 0.1
                        pattern['signature'][dim] = new_val
        
        if 'effectiveness' in feedback:
            # Adjust sensitivity based on effectiveness
            effectiveness = feedback['effectiveness']
            if effectiveness < 0.5:
                self.sensitivity *= 0.95  # Reduce sensitivity
            elif effectiveness > 0.8:
                self.sensitivity = min(1.0, self.sensitivity * 1.05)
        
        logger.info(f"Consciousness detector evolved: sensitivity={self.sensitivity}")


def create_consciousness_barometer() -> ConsciousnessBarometer:
    """Factory function to create consciousness detection system"""
    return ConsciousnessBarometer()
