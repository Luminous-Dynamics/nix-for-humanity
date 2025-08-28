#!/usr/bin/env python3
"""
🔮 Visual Orb Integration - Bridging Consciousness Visualization with TUI

This module integrates the advanced consciousness detection from visual_orb.py
with the TUI's ConsciousnessOrb widget, creating a unified visualization.
"""

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import asyncio
import time
import math

# Import both orb implementations
from ..consciousness.visual_orb import (
    ConsciousnessOrb as VisualOrb,
    OrbState,
    ConsciousnessQuality,
    Particle
)
from ..consciousness.consciousness_detector import ConsciousnessBarometer
from .consciousness_orb import (
    ConsciousnessOrb as TUIOrb,
    AIState,
    EmotionalState
)


class VisualOrbBridge:
    """
    Bridges the consciousness detection from visual_orb with the TUI orb.
    
    This creates a unified visualization that:
    - Uses advanced consciousness detection from visual_orb
    - Displays through the beautiful Textual TUI widget
    - Synchronizes particle effects and colors
    - Maintains 60fps smooth animations
    """
    
    def __init__(self, tui_orb: TUIOrb):
        """Initialize the bridge with a TUI orb widget"""
        self.tui_orb = tui_orb
        self.visual_orb = VisualOrb()
        self.barometer = ConsciousnessBarometer()
        
        # State mapping from consciousness qualities to AI states
        self.quality_to_ai_state = {
            ConsciousnessQuality.FLOW: AIState.FLOW,
            ConsciousnessQuality.DEEP_WORK: AIState.THINKING,
            ConsciousnessQuality.LEARNING: AIState.LEARNING,
            ConsciousnessQuality.CREATIVE: AIState.THINKING,
            ConsciousnessQuality.OVERWHELMED: AIState.ERROR,
            ConsciousnessQuality.FRUSTRATED: AIState.ERROR,
            ConsciousnessQuality.BALANCED: AIState.IDLE,
        }
        
        # Emotional mapping based on consciousness spectrum
        self.spectrum_to_emotion = {
            'high_coherence': EmotionalState.FLOW,
            'high_energy': EmotionalState.HAPPY,
            'low_energy': EmotionalState.CONCERNED,
            'high_clarity': EmotionalState.ATTENTIVE,
            'low_clarity': EmotionalState.CONFUSED,
            'balanced': EmotionalState.NEUTRAL,
        }
        
        self.last_update = time.time()
        self.update_interval = 0.1  # 10Hz update for smooth animation
        
    def detect_consciousness_state(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Detect current consciousness state using advanced detection.
        
        Returns comprehensive state including:
        - Quality (flow, deep_work, etc.)
        - Spectrum values (coherence, energy, clarity, etc.)
        - Suggested visual parameters
        """
        # Use the barometer to sense current state
        reading = self.barometer.sense_user_state(context or {})
        
        # Extract spectrum from reading
        spectrum_obj = reading.spectrum
        
        # Convert spectrum to dict (spectrum uses state dict internally)
        spectrum = {
            'coherence': spectrum_obj.state.get('coherence', 0.5),
            'energy': spectrum_obj.state.get('energy', 0.5),
            'stability': spectrum_obj.state.get('stability', 0.5),
            'clarity': spectrum_obj.state.get('focus', 0.5),  # focus maps to clarity
            'openness': spectrum_obj.state.get('openness', 0.5),
            'flow': spectrum_obj.state.get('flow', 0.5),
            'presence': spectrum_obj.state.get('presence', 0.5),
        }
        
        # Determine quality based on spectrum
        quality = self._determine_quality(spectrum)
        
        # Update visual orb's internal state
        self.visual_orb.state.quality = quality
        self.visual_orb.state.spectrum = spectrum
        
        # Calculate visual parameters
        visual_params = self._calculate_visual_parameters(quality, spectrum)
        
        return {
            'quality': quality,
            'spectrum': spectrum,
            'visual_params': visual_params,
            'timestamp': time.time()
        }
    
    def _calculate_visual_parameters(self, quality: str, spectrum: Dict[str, float]) -> Dict[str, Any]:
        """Calculate visual parameters based on consciousness state"""
        # Base parameters from spectrum
        coherence = spectrum.get('coherence', 0.5)
        energy = spectrum.get('energy', 0.5)
        clarity = spectrum.get('clarity', 0.5)
        flow = spectrum.get('flow', 0.5)
        
        # Calculate breathing rate (slower when in flow)
        breathing_rate = 2.0 - (flow * 1.5)  # 0.5 to 2.0 Hz
        
        # Calculate pulse intensity (higher when energetic)
        pulse_intensity = 0.3 + (energy * 0.7)
        
        # Calculate attention level (based on clarity and coherence)
        attention = (clarity + coherence) / 2
        
        # Determine color based on quality
        color = self._get_quality_color(quality)
        
        # Particle parameters
        particle_count = int(5 + coherence * 15)  # 5-20 particles
        particle_speed = 0.5 + energy * 1.5  # 0.5-2.0 speed
        
        return {
            'breathing_rate': breathing_rate,
            'pulse_intensity': pulse_intensity,
            'attention_level': attention,
            'coherence': coherence,
            'color': color,
            'particle_count': particle_count,
            'particle_speed': particle_speed,
        }
    
    def _determine_quality(self, spectrum: Dict[str, float]) -> str:
        """Determine consciousness quality from spectrum values"""
        # High flow and coherence = FLOW state
        if spectrum['flow'] > 0.7 and spectrum['coherence'] > 0.7:
            return ConsciousnessQuality.FLOW
        
        # High clarity and stability = DEEP_WORK
        if spectrum['clarity'] > 0.7 and spectrum['stability'] > 0.7:
            return ConsciousnessQuality.DEEP_WORK
        
        # High openness and energy = CREATIVE
        if spectrum['openness'] > 0.7 and spectrum['energy'] > 0.7:
            return ConsciousnessQuality.CREATIVE
        
        # Learning pattern
        if spectrum['openness'] > 0.6 and spectrum['clarity'] > 0.5:
            return ConsciousnessQuality.LEARNING
        
        # Overwhelmed
        if spectrum['coherence'] < 0.3 and spectrum['energy'] > 0.7:
            return ConsciousnessQuality.OVERWHELMED
        
        # Frustrated
        if spectrum['stability'] < 0.3 and spectrum['energy'] > 0.6:
            return ConsciousnessQuality.FRUSTRATED
        
        # Default balanced
        return ConsciousnessQuality.BALANCED
    
    def _get_quality_color(self, quality: str) -> Tuple[int, int, int]:
        """Get RGB color for consciousness quality"""
        colors = {
            ConsciousnessQuality.FLOW: (38, 166, 154),     # Teal
            ConsciousnessQuality.DEEP_WORK: (126, 87, 194), # Purple
            ConsciousnessQuality.LEARNING: (92, 107, 192),  # Indigo
            ConsciousnessQuality.CREATIVE: (255, 167, 38),  # Orange
            ConsciousnessQuality.OVERWHELMED: (255, 87, 34), # Deep Orange
            ConsciousnessQuality.FRUSTRATED: (244, 67, 54),  # Red
            ConsciousnessQuality.BALANCED: (100, 200, 255),  # Sky Blue
        }
        return colors.get(quality, (128, 128, 128))
    
    def sync_with_tui(self, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Synchronize the visual orb state with the TUI orb.
        
        This should be called periodically (10Hz) to update the TUI
        with the latest consciousness detection.
        """
        # Detect current state
        state = self.detect_consciousness_state(context)
        
        # Map to TUI states
        quality = state['quality']
        ai_state = self.quality_to_ai_state.get(quality, AIState.IDLE)
        
        # Determine emotional state from spectrum
        spectrum = state['spectrum']
        if spectrum['coherence'] > 0.8 and spectrum['flow'] > 0.7:
            emotion = EmotionalState.FLOW
        elif spectrum['energy'] > 0.7:
            emotion = EmotionalState.HAPPY
        elif spectrum['clarity'] < 0.3:
            emotion = EmotionalState.CONFUSED
        elif spectrum['energy'] < 0.3:
            emotion = EmotionalState.CONCERNED
        elif spectrum['coherence'] > 0.6:
            emotion = EmotionalState.ATTENTIVE
        else:
            emotion = EmotionalState.NEUTRAL
        
        # Update TUI orb
        visual_params = state['visual_params']
        self.tui_orb.ai_state = ai_state
        self.tui_orb.emotional_state = emotion
        self.tui_orb.breathing_rate = visual_params['breathing_rate']
        self.tui_orb.attention_level = visual_params['attention_level']
        self.tui_orb.coherence = visual_params['coherence']
        self.tui_orb.pulse_intensity = visual_params['pulse_intensity']
        
        # Update particle system if TUI orb supports it
        if hasattr(self.tui_orb, 'set_particle_params'):
            self.tui_orb.set_particle_params(
                count=visual_params['particle_count'],
                speed=visual_params['particle_speed']
            )
    
    async def start_sync_loop(self, get_context_func=None):
        """
        Start the synchronization loop.
        
        Args:
            get_context_func: Optional function that returns current context
        """
        while True:
            try:
                # Get context if function provided
                context = get_context_func() if get_context_func else None
                
                # Sync states
                self.sync_with_tui(context)
                
                # Wait for next update
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                # Log error but keep running
                print(f"Visual orb sync error: {e}")
                await asyncio.sleep(1)  # Back off on error
    
    def get_description(self) -> str:
        """Get a text description of current consciousness state"""
        quality = self.visual_orb.state.quality
        spectrum = self.visual_orb.state.spectrum
        
        descriptions = {
            ConsciousnessQuality.FLOW: "🌊 In deep flow state - optimal performance",
            ConsciousnessQuality.DEEP_WORK: "🎯 Focused deep work - minimal distractions",
            ConsciousnessQuality.LEARNING: "📚 Active learning mode - absorbing patterns",
            ConsciousnessQuality.CREATIVE: "✨ Creative exploration - generating ideas",
            ConsciousnessQuality.OVERWHELMED: "😰 Feeling overwhelmed - need simplification",
            ConsciousnessQuality.FRUSTRATED: "😤 Experiencing frustration - seeking solutions",
            ConsciousnessQuality.BALANCED: "☯️ Balanced state - ready for anything",
        }
        
        base_desc = descriptions.get(quality, "🔮 Observing consciousness")
        
        # Add spectrum details
        if spectrum['coherence'] > 0.8:
            base_desc += " | High coherence"
        if spectrum['flow'] > 0.7:
            base_desc += " | Strong flow"
        if spectrum['energy'] < 0.3:
            base_desc += " | Low energy"
            
        return base_desc


def integrate_visual_orb_with_tui(app, context_provider=None):
    """
    Convenience function to integrate visual orb with a TUI app.
    
    Args:
        app: The NixForHumanityTUI app instance
        context_provider: Optional function to provide context
    
    Returns:
        VisualOrbBridge instance
    """
    # Get the TUI orb from the app
    tui_orb = app.orb
    if not tui_orb:
        raise ValueError("TUI app must have an orb widget")
    
    # Create the bridge
    bridge = VisualOrbBridge(tui_orb)
    
    # Start sync loop in background
    asyncio.create_task(bridge.start_sync_loop(context_provider))
    
    return bridge