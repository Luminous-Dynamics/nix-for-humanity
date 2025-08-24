#!/usr/bin/env python3
"""
🫀 Biometric Consciousness - Physiological Awareness System
Adapts system responses based on user's biometric and emotional state
Creates true human-computer symbiosis through biological awareness
"""

import time
import math
import random
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import hashlib
from pathlib import Path


class BiometricState(Enum):
    """User's overall biometric state"""
    FLOW = "flow"                    # Optimal performance state
    FOCUSED = "focused"              # Deep concentration
    RELAXED = "relaxed"              # Calm and receptive
    STRESSED = "stressed"            # Elevated stress indicators
    FATIGUED = "fatigued"           # Low energy, needs rest
    EXCITED = "excited"              # High energy, positive
    FRUSTRATED = "frustrated"        # Blocked, needs help
    CONTEMPLATIVE = "contemplative"  # Reflective, philosophical


class EmotionalTone(Enum):
    """Emotional tone detection"""
    JOYFUL = "joyful"
    PEACEFUL = "peaceful"
    CURIOUS = "curious"
    DETERMINED = "determined"
    ANXIOUS = "anxious"
    CONFUSED = "confused"
    ANGRY = "angry"
    SAD = "sad"
    NEUTRAL = "neutral"


@dataclass
class HeartRateVariability:
    """HRV metrics for coherence detection"""
    rmssd: float  # Root mean square of successive differences
    sdnn: float   # Standard deviation of NN intervals
    pnn50: float  # Percentage of successive differences > 50ms
    coherence: float  # Heart coherence score (0-1)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def calculate_coherence(self) -> float:
        """Calculate heart coherence from HRV metrics"""
        # Simplified coherence calculation
        # Real implementation would use frequency domain analysis
        coherence_factors = [
            min(1.0, self.rmssd / 50),  # Higher HRV = better
            min(1.0, self.sdnn / 60),
            min(1.0, self.pnn50 / 20)
        ]
        return sum(coherence_factors) / len(coherence_factors)


@dataclass
class BreathingPattern:
    """Breathing pattern analysis"""
    rate: float  # Breaths per minute
    depth: float  # Relative depth (0-1)
    rhythm_variance: float  # Regularity of breathing
    coherent_breathing: bool  # 4-7-8 or similar pattern detected
    
    def is_stressed(self) -> bool:
        """Check if breathing indicates stress"""
        return self.rate > 20 or self.rhythm_variance > 0.3
    
    def is_meditative(self) -> bool:
        """Check if breathing indicates meditation"""
        return 4 <= self.rate <= 8 and self.rhythm_variance < 0.1


@dataclass
class EyeTracking:
    """Eye movement and focus patterns"""
    fixation_duration: float  # Average fixation time
    saccade_velocity: float  # Eye movement speed
    pupil_dilation: float  # Relative dilation (0-1)
    blink_rate: float  # Blinks per minute
    screen_distance: float  # Estimated distance from screen
    
    def detect_fatigue(self) -> bool:
        """Detect eye fatigue indicators"""
        return (self.blink_rate < 10 or self.blink_rate > 30 or
                self.fixation_duration < 200 or
                self.screen_distance < 40)
    
    def detect_focus_level(self) -> float:
        """Detect focus level from eye patterns"""
        focus_score = 0.0
        
        # Optimal fixation duration
        if 300 <= self.fixation_duration <= 600:
            focus_score += 0.4
        
        # Moderate saccade velocity
        if 200 <= self.saccade_velocity <= 400:
            focus_score += 0.3
        
        # Normal blink rate
        if 15 <= self.blink_rate <= 20:
            focus_score += 0.3
        
        return min(1.0, focus_score)


@dataclass
class KeyboardDynamics:
    """Typing pattern analysis"""
    typing_speed: float  # WPM
    key_press_duration: float  # Average hold time
    inter_key_interval: float  # Time between keystrokes
    deletion_rate: float  # Backspaces per 100 chars
    pause_frequency: float  # Pauses > 1 sec per minute
    pressure_variance: float  # If pressure-sensitive
    
    def detect_emotional_state(self) -> EmotionalTone:
        """Detect emotion from typing patterns"""
        if self.typing_speed > 80 and self.deletion_rate < 5:
            return EmotionalTone.DETERMINED
        elif self.deletion_rate > 20:
            return EmotionalTone.FRUSTRATED
        elif self.typing_speed < 30 and self.pause_frequency > 10:
            return EmotionalTone.CONTEMPLATIVE
        elif self.pressure_variance > 0.5:
            return EmotionalTone.ANXIOUS
        else:
            return EmotionalTone.NEUTRAL


@dataclass
class CircadianRhythm:
    """Circadian rhythm tracking"""
    local_time: datetime
    wake_time: datetime
    sleep_time: datetime
    chronotype: str  # "lark", "owl", or "third_bird"
    
    def get_alertness_level(self) -> float:
        """Calculate alertness based on circadian rhythm"""
        hours_awake = (self.local_time - self.wake_time).seconds / 3600
        
        # Simplified alertness curve
        if hours_awake < 1:
            return 0.6  # Still waking up
        elif 2 <= hours_awake <= 4:
            return 0.9  # Peak morning alertness
        elif 4 < hours_awake <= 8:
            return 0.8  # Good alertness
        elif 8 < hours_awake <= 13:
            return 0.7  # Post-lunch dip
        elif 13 < hours_awake <= 16:
            return 0.85  # Second peak
        else:
            return max(0.3, 1.0 - (hours_awake - 16) * 0.1)  # Evening decline


@dataclass
class BiometricReading:
    """Complete biometric reading at a moment"""
    timestamp: datetime
    hrv: Optional[HeartRateVariability]
    breathing: Optional[BreathingPattern]
    eyes: Optional[EyeTracking]
    keyboard: Optional[KeyboardDynamics]
    circadian: Optional[CircadianRhythm]
    ambient_light: float = 0.5  # 0=dark, 1=bright
    ambient_noise: float = 0.3  # 0=quiet, 1=loud
    temperature: float = 22.0  # Celsius
    
    def calculate_overall_state(self) -> BiometricState:
        """Determine overall biometric state"""
        stress_indicators = 0
        flow_indicators = 0
        fatigue_indicators = 0
        
        # Check HRV
        if self.hrv:
            if self.hrv.coherence > 0.7:
                flow_indicators += 2
            elif self.hrv.coherence < 0.3:
                stress_indicators += 2
        
        # Check breathing
        if self.breathing:
            if self.breathing.is_stressed():
                stress_indicators += 1
            elif self.breathing.is_meditative():
                flow_indicators += 1
        
        # Check eyes
        if self.eyes:
            if self.eyes.detect_fatigue():
                fatigue_indicators += 2
            focus = self.eyes.detect_focus_level()
            if focus > 0.7:
                flow_indicators += 1
        
        # Check keyboard
        if self.keyboard:
            emotion = self.keyboard.detect_emotional_state()
            if emotion == EmotionalTone.FRUSTRATED:
                stress_indicators += 1
            elif emotion == EmotionalTone.DETERMINED:
                flow_indicators += 1
        
        # Check circadian
        if self.circadian:
            alertness = self.circadian.get_alertness_level()
            if alertness < 0.4:
                fatigue_indicators += 2
        
        # Determine state
        if flow_indicators >= 3 and stress_indicators == 0:
            return BiometricState.FLOW
        elif fatigue_indicators >= 2:
            return BiometricState.FATIGUED
        elif stress_indicators >= 2:
            return BiometricState.STRESSED
        elif flow_indicators >= 2:
            return BiometricState.FOCUSED
        else:
            return BiometricState.RELAXED


class BiometricConsciousness:
    """
    Biometric consciousness system that adapts to user's physiological state
    Creates true human-computer symbiosis through biological awareness
    """
    
    def __init__(self):
        # Biometric history
        self.reading_history: List[BiometricReading] = []
        self.max_history = 100
        
        # Current state
        self.current_state = BiometricState.RELAXED
        self.current_emotion = EmotionalTone.NEUTRAL
        
        # Baselines for normalization
        self.baselines = {
            'hrv_coherence': 0.5,
            'breathing_rate': 14,
            'typing_speed': 50,
            'blink_rate': 17,
            'alertness': 0.7
        }
        
        # Adaptation strategies
        self.adaptation_strategies = {
            BiometricState.FLOW: self._adapt_for_flow,
            BiometricState.FOCUSED: self._adapt_for_focused,
            BiometricState.RELAXED: self._adapt_for_relaxed,
            BiometricState.STRESSED: self._adapt_for_stressed,
            BiometricState.FATIGUED: self._adapt_for_fatigued,
            BiometricState.EXCITED: self._adapt_for_excited,
            BiometricState.FRUSTRATED: self._adapt_for_frustrated,
            BiometricState.CONTEMPLATIVE: self._adapt_for_contemplative
        }
        
        # Simulated sensors (for demo)
        self.simulate_sensors = True
        self.simulation_seed = int(time.time())
    
    def read_biometrics(self) -> BiometricReading:
        """
        Read current biometric data from sensors
        In production, would interface with real biometric devices
        """
        if self.simulate_sensors:
            return self._simulate_biometric_reading()
        else:
            # Real sensor integration would go here
            # Could use:
            # - Apple Watch / Android Wear API for HRV
            # - Webcam for eye tracking and breathing
            # - Keyboard event timing analysis
            # - System time for circadian
            pass
    
    def _simulate_biometric_reading(self) -> BiometricReading:
        """Simulate realistic biometric data for testing"""
        # Create time-based variations
        t = time.time()
        base_variation = math.sin(t / 60) * 0.2 + 0.5  # Slow wave
        
        # Simulate HRV
        hrv = HeartRateVariability(
            rmssd=40 + base_variation * 20 + random.gauss(0, 5),
            sdnn=50 + base_variation * 15 + random.gauss(0, 3),
            pnn50=15 + base_variation * 10 + random.gauss(0, 2),
            coherence=0
        )
        hrv.coherence = hrv.calculate_coherence()
        
        # Simulate breathing
        breathing = BreathingPattern(
            rate=14 + base_variation * 4 + random.gauss(0, 1),
            depth=0.6 + base_variation * 0.2,
            rhythm_variance=0.15 + (1 - base_variation) * 0.15,
            coherent_breathing=random.random() > 0.7
        )
        
        # Simulate eye tracking
        eyes = EyeTracking(
            fixation_duration=400 + base_variation * 100 + random.gauss(0, 50),
            saccade_velocity=300 + random.gauss(0, 50),
            pupil_dilation=0.5 + base_variation * 0.2,
            blink_rate=17 + random.gauss(0, 3),
            screen_distance=50 + random.gauss(0, 5)
        )
        
        # Simulate keyboard dynamics
        keyboard = KeyboardDynamics(
            typing_speed=50 + base_variation * 20 + random.gauss(0, 5),
            key_press_duration=100 + random.gauss(0, 20),
            inter_key_interval=200 + random.gauss(0, 50),
            deletion_rate=5 + (1 - base_variation) * 10 + random.gauss(0, 2),
            pause_frequency=5 + random.gauss(0, 2),
            pressure_variance=0.2 + (1 - base_variation) * 0.3
        )
        
        # Simulate circadian rhythm
        now = datetime.now()
        wake_time = now.replace(hour=7, minute=0, second=0)
        sleep_time = now.replace(hour=23, minute=0, second=0)
        
        circadian = CircadianRhythm(
            local_time=now,
            wake_time=wake_time,
            sleep_time=sleep_time,
            chronotype="third_bird"
        )
        
        return BiometricReading(
            timestamp=now,
            hrv=hrv,
            breathing=breathing,
            eyes=eyes,
            keyboard=keyboard,
            circadian=circadian,
            ambient_light=0.6 + math.sin(t / 120) * 0.3,
            ambient_noise=0.3 + random.random() * 0.2,
            temperature=22 + math.sin(t / 180) * 2
        )
    
    def process_biometric_state(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process current biometric state and generate adaptations
        """
        # Get current reading
        reading = self.read_biometrics()
        
        # Add to history
        self.reading_history.append(reading)
        if len(self.reading_history) > self.max_history:
            self.reading_history.pop(0)
        
        # Calculate state
        self.current_state = reading.calculate_overall_state()
        
        # Detect emotion if keyboard data available
        if reading.keyboard:
            self.current_emotion = reading.keyboard.detect_emotional_state()
        
        # Get adaptation strategy
        adaptation = self.adaptation_strategies[self.current_state](reading, context)
        
        # Calculate trends
        trends = self._calculate_biometric_trends()
        
        return {
            'state': self.current_state.value,
            'emotion': self.current_emotion.value,
            'adaptation': adaptation,
            'trends': trends,
            'metrics': {
                'hrv_coherence': reading.hrv.coherence if reading.hrv else None,
                'breathing_rate': reading.breathing.rate if reading.breathing else None,
                'focus_level': reading.eyes.detect_focus_level() if reading.eyes else None,
                'alertness': reading.circadian.get_alertness_level() if reading.circadian else None
            }
        }
    
    def _adapt_for_flow(self, reading: BiometricReading, context: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptation for flow state - maintain it!"""
        return {
            'response_style': 'minimal',
            'interruption_level': 'none',
            'suggestions': 'silent',
            'interface_mode': 'invisible',
            'message': "You're in flow - continuing silent support",
            'actions': [
                'maintain_current_environment',
                'suppress_non_critical_notifications',
                'prepare_next_task_silently'
            ]
        }
    
    def _adapt_for_focused(self, reading: BiometricReading, context: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptation for focused state"""
        return {
            'response_style': 'concise',
            'interruption_level': 'minimal',
            'suggestions': 'contextual',
            'interface_mode': 'streamlined',
            'message': "Deep focus detected - streamlining interface",
            'actions': [
                'reduce_visual_complexity',
                'queue_non_urgent_messages',
                'optimize_for_current_task'
            ]
        }
    
    def _adapt_for_relaxed(self, reading: BiometricReading, context: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptation for relaxed state"""
        return {
            'response_style': 'conversational',
            'interruption_level': 'normal',
            'suggestions': 'exploratory',
            'interface_mode': 'full',
            'message': "Relaxed state - full features available",
            'actions': [
                'enable_all_features',
                'show_interesting_suggestions',
                'allow_exploration'
            ]
        }
    
    def _adapt_for_stressed(self, reading: BiometricReading, context: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptation for stressed state"""
        return {
            'response_style': 'calming',
            'interruption_level': 'emergency_only',
            'suggestions': 'stress_reducing',
            'interface_mode': 'simplified',
            'message': "Stress detected - simplifying and supporting",
            'actions': [
                'simplify_interface',
                'offer_breathing_exercise',
                'reduce_cognitive_load',
                'suggest_break_if_prolonged'
            ],
            'breathing_guide': self._generate_breathing_exercise()
        }
    
    def _adapt_for_fatigued(self, reading: BiometricReading, context: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptation for fatigued state"""
        return {
            'response_style': 'gentle',
            'interruption_level': 'critical_only',
            'suggestions': 'rest_oriented',
            'interface_mode': 'low_stimulation',
            'message': "Fatigue detected - suggesting rest",
            'actions': [
                'reduce_brightness',
                'increase_font_size',
                'suggest_task_postponement',
                'offer_quick_wins_only',
                'recommend_break'
            ],
            'break_suggestion': self._generate_break_suggestion(reading)
        }
    
    def _adapt_for_excited(self, reading: BiometricReading, context: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptation for excited state"""
        return {
            'response_style': 'energetic',
            'interruption_level': 'normal',
            'suggestions': 'ambitious',
            'interface_mode': 'dynamic',
            'message': "High energy detected - channeling enthusiasm",
            'actions': [
                'suggest_challenging_tasks',
                'enable_advanced_features',
                'increase_responsiveness'
            ]
        }
    
    def _adapt_for_frustrated(self, reading: BiometricReading, context: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptation for frustrated state"""
        return {
            'response_style': 'supportive',
            'interruption_level': 'helpful_only',
            'suggestions': 'solution_focused',
            'interface_mode': 'assistive',
            'message': "Frustration detected - here to help",
            'actions': [
                'offer_immediate_help',
                'simplify_current_task',
                'provide_alternative_approaches',
                'increase_error_tolerance'
            ],
            'help_options': self._generate_help_options(context)
        }
    
    def _adapt_for_contemplative(self, reading: BiometricReading, context: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptation for contemplative state"""
        return {
            'response_style': 'philosophical',
            'interruption_level': 'minimal',
            'suggestions': 'thought_provoking',
            'interface_mode': 'spacious',
            'message': "Contemplative mood - providing space for thought",
            'actions': [
                'increase_white_space',
                'reduce_information_density',
                'offer_deeper_insights',
                'enable_reflection_tools'
            ]
        }
    
    def _calculate_biometric_trends(self) -> Dict[str, Any]:
        """Calculate trends from biometric history"""
        if len(self.reading_history) < 3:
            return {'status': 'insufficient_data'}
        
        recent = self.reading_history[-10:]
        
        # Calculate HRV trend
        hrv_values = [r.hrv.coherence for r in recent if r.hrv]
        hrv_trend = 'improving' if hrv_values and hrv_values[-1] > hrv_values[0] else 'declining'
        
        # Calculate stress trend
        stress_states = [r.calculate_overall_state() for r in recent]
        stress_count = sum(1 for s in stress_states if s == BiometricState.STRESSED)
        stress_trend = 'increasing' if stress_count > len(stress_states) / 3 else 'stable'
        
        # Calculate fatigue trend
        if recent[-1].circadian:
            alertness = recent[-1].circadian.get_alertness_level()
            fatigue_trend = 'increasing' if alertness < 0.5 else 'stable'
        else:
            fatigue_trend = 'unknown'
        
        return {
            'hrv_trend': hrv_trend,
            'stress_trend': stress_trend,
            'fatigue_trend': fatigue_trend,
            'recommendation': self._generate_trend_recommendation(hrv_trend, stress_trend, fatigue_trend)
        }
    
    def _generate_trend_recommendation(self, hrv: str, stress: str, fatigue: str) -> str:
        """Generate recommendation based on trends"""
        if stress == 'increasing' and fatigue == 'increasing':
            return "Consider taking a longer break - both stress and fatigue are rising"
        elif hrv == 'improving':
            return "Your coherence is improving - keep up the good rhythm"
        elif fatigue == 'increasing':
            return "Fatigue is building - perhaps time for a short rest"
        else:
            return "Biometrics stable - continue as comfortable"
    
    def _generate_breathing_exercise(self) -> Dict[str, Any]:
        """Generate a breathing exercise for stress relief"""
        return {
            'type': 'box_breathing',
            'instructions': [
                "Inhale for 4 counts",
                "Hold for 4 counts",
                "Exhale for 4 counts",
                "Hold for 4 counts"
            ],
            'duration': 5,  # minutes
            'purpose': 'stress_relief'
        }
    
    def _generate_break_suggestion(self, reading: BiometricReading) -> Dict[str, Any]:
        """Generate appropriate break suggestion"""
        if reading.eyes and reading.eyes.detect_fatigue():
            return {
                'type': 'eye_rest',
                'duration': 20,
                'activity': 'Look at something 20 feet away for 20 seconds'
            }
        elif reading.circadian and reading.circadian.get_alertness_level() < 0.4:
            return {
                'type': 'power_nap',
                'duration': 15,
                'activity': 'Short rest to restore alertness'
            }
        else:
            return {
                'type': 'movement',
                'duration': 5,
                'activity': 'Quick walk or stretch'
            }
    
    def _generate_help_options(self, context: Dict[str, Any]) -> List[str]:
        """Generate contextual help options for frustration"""
        return [
            "Show me a simpler way",
            "Explain what went wrong",
            "Try a different approach",
            "Take a break and return",
            "Get community help"
        ]
    
    def get_consciousness_recommendation(self, state: BiometricState) -> Dict[str, Any]:
        """Get consciousness-level recommendations for biometric state"""
        recommendations = {
            BiometricState.FLOW: {
                'quantum_mode': True,
                'sacred_geometry': 'golden_spiral',
                'coherence_target': 0.9,
                'interface_opacity': 0.1
            },
            BiometricState.FOCUSED: {
                'quantum_mode': False,
                'sacred_geometry': 'merkaba',
                'coherence_target': 0.8,
                'interface_opacity': 0.3
            },
            BiometricState.STRESSED: {
                'quantum_mode': False,
                'sacred_geometry': 'flower_of_life',
                'coherence_target': 0.6,
                'interface_opacity': 0.5,
                'healing_frequency': 528  # Hz - Love frequency
            },
            BiometricState.FATIGUED: {
                'quantum_mode': False,
                'sacred_geometry': 'vesica_piscis',
                'coherence_target': 0.5,
                'interface_opacity': 0.7,
                'healing_frequency': 396  # Hz - Liberation from fear
            }
        }
        
        return recommendations.get(state, {
            'quantum_mode': False,
            'sacred_geometry': 'torus',
            'coherence_target': 0.7,
            'interface_opacity': 0.5
        })


# Global biometric consciousness instance
_BIOMETRIC_CONSCIOUSNESS: Optional[BiometricConsciousness] = None

def get_biometric_consciousness() -> BiometricConsciousness:
    """Get or create biometric consciousness"""
    global _BIOMETRIC_CONSCIOUSNESS
    if _BIOMETRIC_CONSCIOUSNESS is None:
        _BIOMETRIC_CONSCIOUSNESS = BiometricConsciousness()
    return _BIOMETRIC_CONSCIOUSNESS


if __name__ == "__main__":
    # Test biometric consciousness
    bio = get_biometric_consciousness()
    
    print("🫀 Testing Biometric Consciousness\n")
    print("=" * 60)
    
    # Simulate different contexts
    contexts = [
        {'task': 'coding', 'duration': 30},
        {'task': 'debugging', 'duration': 60},
        {'task': 'reading', 'duration': 15}
    ]
    
    for context in contexts:
        print(f"\nContext: {context}")
        print("-" * 40)
        
        # Get biometric state and adaptation
        result = bio.process_biometric_state(context)
        
        print(f"State: {result['state']}")
        print(f"Emotion: {result['emotion']}")
        print(f"Adaptation: {result['adaptation']['response_style']}")
        print(f"Message: {result['adaptation']['message']}")
        
        if result['metrics']['hrv_coherence']:
            print(f"\nMetrics:")
            print(f"  HRV Coherence: {result['metrics']['hrv_coherence']:.2%}")
            print(f"  Breathing Rate: {result['metrics']['breathing_rate']:.1f} bpm")
            print(f"  Focus Level: {result['metrics']['focus_level']:.2%}")
            print(f"  Alertness: {result['metrics']['alertness']:.2%}")
        
        if result['trends']['status'] != 'insufficient_data':
            print(f"\nTrends:")
            print(f"  HRV: {result['trends']['hrv_trend']}")
            print(f"  Stress: {result['trends']['stress_trend']}")
            print(f"  Fatigue: {result['trends']['fatigue_trend']}")
            print(f"  Recommendation: {result['trends']['recommendation']}")
        
        # Get consciousness recommendations
        recommendations = bio.get_consciousness_recommendation(bio.current_state)
        print(f"\nConsciousness Settings:")
        print(f"  Quantum Mode: {recommendations.get('quantum_mode')}")
        print(f"  Sacred Geometry: {recommendations.get('sacred_geometry')}")
        print(f"  Coherence Target: {recommendations.get('coherence_target')}")
        
        if 'healing_frequency' in recommendations:
            print(f"  Healing Frequency: {recommendations['healing_frequency']} Hz")
        
        time.sleep(1)  # Simulate time passing
    
    print("\n" + "=" * 60)
    print("✨ Biometric consciousness creates true human-computer symbiosis!")