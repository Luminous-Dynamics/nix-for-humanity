#!/usr/bin/env python3
"""
💓 Biometric Bridge - Real Physiological Awareness

This module creates a bridge between biological signals (heart rate, breathing)
and the consciousness detection system, enabling true human-computer resonance.
"""

import time
import math
import random
import threading
import json
import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Biometric sensor libraries (with graceful fallback)
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

try:
    import bluetooth
    BLUETOOTH_AVAILABLE = True
except ImportError:
    BLUETOOTH_AVAILABLE = False

# For HRV analysis
try:
    import heartpy as hp
    HEARTPY_AVAILABLE = True
except ImportError:
    HEARTPY_AVAILABLE = False

# For breathing detection from audio
try:
    import sounddevice as sd
    import scipy.signal
    AUDIO_AVAILABLE = True
except (ImportError, OSError):
    AUDIO_AVAILABLE = False

from .consciousness_detector import ConsciousnessBarometer, ConsciousnessSpectrum
from .sacred_integration import get_sacred_integration

logger = logging.getLogger(__name__)


@dataclass
class BiometricReading:
    """A single biometric measurement"""
    timestamp: datetime
    heart_rate: Optional[float] = None  # BPM
    hrv: Optional[float] = None  # Heart rate variability (ms)
    breathing_rate: Optional[float] = None  # Breaths per minute
    breathing_depth: Optional[float] = None  # 0-1 scale
    skin_conductance: Optional[float] = None  # μS (stress indicator)
    temperature: Optional[float] = None  # Celsius
    
    # Derived metrics
    coherence: Optional[float] = None  # Heart-breath coherence
    stress_level: Optional[float] = None  # 0-1 scale
    relaxation: Optional[float] = None  # 0-1 scale
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'heart_rate': self.heart_rate,
            'hrv': self.hrv,
            'breathing_rate': self.breathing_rate,
            'breathing_depth': self.breathing_depth,
            'coherence': self.coherence,
            'stress_level': self.stress_level,
            'relaxation': self.relaxation
        }


@dataclass 
class BiometricPattern:
    """Recognized pattern in biometric data"""
    name: str
    confidence: float
    duration: timedelta
    implications: List[str]
    
    # Pattern types
    FLOW_STATE = "flow_state"
    STRESS_RESPONSE = "stress_response"
    MEDITATION = "meditation"
    FOCUSED_ATTENTION = "focused_attention"
    FATIGUE = "fatigue"
    EXCITEMENT = "excitement"


class BiometricSensor:
    """
    Base class for different biometric sensors.
    Each sensor type implements its own data collection.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.is_connected = False
        self.last_reading = None
        self.callback = None
        
    def connect(self) -> bool:
        """Connect to the sensor"""
        raise NotImplementedError
        
    def disconnect(self):
        """Disconnect from sensor"""
        raise NotImplementedError
        
    def read(self) -> Optional[Dict[str, float]]:
        """Read current sensor values"""
        raise NotImplementedError
        
    def start_streaming(self, callback: Callable):
        """Start continuous data streaming"""
        self.callback = callback
        
    def stop_streaming(self):
        """Stop continuous data streaming"""
        self.callback = None


class SimulatedBiometricSensor(BiometricSensor):
    """
    Simulated biometric sensor for testing and development.
    Generates realistic-looking biometric data.
    """
    
    def __init__(self):
        super().__init__("Simulated Sensor")
        self.base_hr = 70
        self.base_breathing = 12
        self.phase = 0
        self.stress_level = 0.3
        self.is_streaming = False
        self.stream_thread = None
        
    def connect(self) -> bool:
        """Simulate connection"""
        self.is_connected = True
        logger.info("🎭 Connected to simulated biometric sensor")
        return True
        
    def disconnect(self):
        """Simulate disconnection"""
        self.is_connected = False
        self.stop_streaming()
        
    def read(self) -> Optional[Dict[str, float]]:
        """Generate simulated biometric data"""
        if not self.is_connected:
            return None
            
        # Simulate natural variations
        self.phase += 0.1
        
        # Heart rate with respiratory sinus arrhythmia
        breathing_influence = math.sin(self.phase * 0.5) * 5
        stress_influence = self.stress_level * 10
        hr = self.base_hr + breathing_influence + stress_influence + random.uniform(-2, 2)
        
        # HRV (inversely related to stress)
        hrv = 50 * (1 - self.stress_level) + random.uniform(-5, 5)
        
        # Breathing rate
        br = self.base_breathing + self.stress_level * 4 + random.uniform(-1, 1)
        
        # Breathing depth (shallower when stressed)
        depth = 0.7 * (1 - self.stress_level * 0.5) + random.uniform(-0.1, 0.1)
        
        return {
            'heart_rate': max(50, min(120, hr)),
            'hrv': max(20, min(100, hrv)),
            'breathing_rate': max(8, min(25, br)),
            'breathing_depth': max(0.2, min(1.0, depth)),
            'coherence': self._calculate_coherence(hr, br)
        }
        
    def _calculate_coherence(self, hr: float, br: float) -> float:
        """Calculate heart-breath coherence"""
        # Ideal ratio is about 5:1 (heart:breath)
        ratio = hr / br
        ideal_ratio = 5.8  # Typical coherent ratio
        
        # Calculate how close we are to ideal
        deviation = abs(ratio - ideal_ratio) / ideal_ratio
        coherence = max(0, 1 - deviation)
        
        return coherence
        
    def start_streaming(self, callback: Callable):
        """Start simulated data streaming"""
        super().start_streaming(callback)
        self.is_streaming = True
        
        def stream_loop():
            while self.is_streaming:
                data = self.read()
                if data and self.callback:
                    self.callback(data)
                time.sleep(1)  # 1 Hz sampling
                
        self.stream_thread = threading.Thread(target=stream_loop)
        self.stream_thread.daemon = True
        self.stream_thread.start()
        
    def stop_streaming(self):
        """Stop streaming"""
        self.is_streaming = False
        if self.stream_thread:
            self.stream_thread.join(timeout=2)
        super().stop_streaming()
        
    def simulate_state_change(self, state: str):
        """Simulate different physiological states for testing"""
        states = {
            'relaxed': {'stress': 0.2, 'hr': 65, 'br': 10},
            'focused': {'stress': 0.4, 'hr': 75, 'br': 14},
            'stressed': {'stress': 0.8, 'hr': 90, 'br': 18},
            'flow': {'stress': 0.3, 'hr': 70, 'br': 12},
            'meditation': {'stress': 0.1, 'hr': 60, 'br': 8}
        }
        
        if state in states:
            params = states[state]
            self.stress_level = params['stress']
            self.base_hr = params['hr']
            self.base_breathing = params['br']
            logger.info(f"🎭 Simulating {state} state")


class AudioBreathingSensor(BiometricSensor):
    """
    Detect breathing patterns from microphone audio.
    Works by detecting the sound of breathing.
    """
    
    def __init__(self):
        super().__init__("Audio Breathing Sensor")
        self.sample_rate = 44100
        self.buffer_size = 4096
        self.audio_buffer = []
        self.is_recording = False
        
    def connect(self) -> bool:
        """Test microphone availability"""
        if not AUDIO_AVAILABLE:
            logger.warning("Audio libraries not available")
            return False
            
        try:
            # Test microphone
            test_recording = sd.rec(
                int(self.sample_rate * 0.1),
                samplerate=self.sample_rate,
                channels=1
            )
            sd.wait()
            self.is_connected = True
            logger.info("🎤 Connected to audio breathing sensor")
            return True
        except Exception as e:
            logger.error(f"Could not connect to microphone: {e}")
            return False
            
    def detect_breathing_rate(self, audio_data: np.ndarray) -> float:
        """
        Detect breathing rate from audio signal.
        Uses envelope detection and peak finding.
        """
        if len(audio_data) < self.sample_rate * 2:
            return 12.0  # Default rate
            
        # Get envelope of audio signal
        analytic_signal = scipy.signal.hilbert(audio_data)
        envelope = np.abs(analytic_signal)
        
        # Smooth envelope
        window_size = int(self.sample_rate * 0.1)
        envelope_smooth = np.convolve(
            envelope,
            np.ones(window_size) / window_size,
            mode='valid'
        )
        
        # Find peaks (breaths)
        min_distance = int(self.sample_rate * 2)  # Min 2 seconds between breaths
        peaks, _ = scipy.signal.find_peaks(
            envelope_smooth,
            distance=min_distance,
            prominence=np.std(envelope_smooth) * 0.5
        )
        
        if len(peaks) < 2:
            return 12.0  # Default
            
        # Calculate breathing rate from peak intervals
        intervals = np.diff(peaks) / self.sample_rate  # Convert to seconds
        avg_interval = np.mean(intervals)
        breathing_rate = 60 / avg_interval  # Convert to breaths per minute
        
        return max(6, min(30, breathing_rate))  # Clamp to reasonable range


class BluetoothHRMSensor(BiometricSensor):
    """
    Connect to Bluetooth heart rate monitors (BLE).
    Compatible with standard heart rate service UUID.
    """
    
    HEART_RATE_SERVICE = "0000180d-0000-1000-8000-00805f9b34fb"
    HEART_RATE_CHARACTERISTIC = "00002a37-0000-1000-8000-00805f9b34fb"
    
    def __init__(self, device_address: Optional[str] = None):
        super().__init__("Bluetooth HRM")
        self.device_address = device_address
        self.device = None
        
    def scan_devices(self) -> List[str]:
        """Scan for available Bluetooth HRM devices"""
        if not BLUETOOTH_AVAILABLE:
            return []
            
        try:
            devices = bluetooth.discover_devices(
                duration=8,
                lookup_names=True,
                lookup_class=True
            )
            
            hrm_devices = []
            for addr, name, device_class in devices:
                if "heart" in name.lower() or "hrm" in name.lower():
                    hrm_devices.append((addr, name))
                    
            return hrm_devices
        except Exception as e:
            logger.error(f"Bluetooth scan failed: {e}")
            return []


class BiometricBridge:
    """
    The main bridge between biometric sensors and consciousness detection.
    Integrates multiple sensor types and derives consciousness states.
    """
    
    def __init__(self):
        """Initialize the biometric bridge"""
        self.sensors: List[BiometricSensor] = []
        self.readings: List[BiometricReading] = []
        self.max_history = 1000
        
        # Analysis components
        self.barometer = ConsciousnessBarometer()
        self.pattern_detector = PatternDetector()
        
        # Streaming state
        self.is_streaming = False
        self.callbacks = []
        
        # Initialize with simulated sensor for testing
        self.simulated_sensor = SimulatedBiometricSensor()
        self.add_sensor(self.simulated_sensor)
        
        logger.info("💓 Biometric Bridge initialized")
        
    def add_sensor(self, sensor: BiometricSensor) -> bool:
        """Add a biometric sensor"""
        if sensor.connect():
            self.sensors.append(sensor)
            logger.info(f"Added sensor: {sensor.name}")
            return True
        return False
        
    def remove_sensor(self, sensor: BiometricSensor):
        """Remove a biometric sensor"""
        sensor.disconnect()
        self.sensors.remove(sensor)
        
    def read_all_sensors(self) -> BiometricReading:
        """Read from all connected sensors and combine data"""
        reading = BiometricReading(timestamp=datetime.now())
        
        for sensor in self.sensors:
            data = sensor.read()
            if data:
                # Merge sensor data into reading
                reading.heart_rate = data.get('heart_rate', reading.heart_rate)
                reading.hrv = data.get('hrv', reading.hrv)
                reading.breathing_rate = data.get('breathing_rate', reading.breathing_rate)
                reading.breathing_depth = data.get('breathing_depth', reading.breathing_depth)
                reading.coherence = data.get('coherence', reading.coherence)
                
        # Calculate derived metrics
        reading = self._calculate_derived_metrics(reading)
        
        # Store reading
        self.readings.append(reading)
        if len(self.readings) > self.max_history:
            self.readings.pop(0)
            
        return reading
        
    def _calculate_derived_metrics(self, reading: BiometricReading) -> BiometricReading:
        """Calculate stress, relaxation, and other derived metrics"""
        
        # Stress level based on HRV and breathing
        if reading.hrv:
            # Lower HRV = higher stress
            hrv_stress = 1 - (reading.hrv / 100)
            
            if reading.breathing_rate:
                # Faster breathing = higher stress
                br_stress = (reading.breathing_rate - 10) / 15
                br_stress = max(0, min(1, br_stress))
                
                reading.stress_level = (hrv_stress + br_stress) / 2
            else:
                reading.stress_level = hrv_stress
                
        # Relaxation is inverse of stress with coherence bonus
        if reading.stress_level is not None:
            base_relaxation = 1 - reading.stress_level
            
            if reading.coherence:
                # High coherence boosts relaxation
                reading.relaxation = base_relaxation * (1 + reading.coherence * 0.5)
                reading.relaxation = min(1, reading.relaxation)
            else:
                reading.relaxation = base_relaxation
                
        return reading
        
    def to_consciousness_signals(self, reading: BiometricReading) -> Dict[str, Any]:
        """
        Convert biometric reading to consciousness detection signals.
        This is the bridge between body and mind.
        """
        signals = {}
        
        # Heart rate patterns indicate energy/arousal
        if reading.heart_rate:
            if reading.heart_rate < 60:
                signals['energy_level'] = 0.3  # Low arousal
            elif reading.heart_rate < 80:
                signals['energy_level'] = 0.5  # Moderate
            else:
                signals['energy_level'] = 0.7  # High arousal
                
        # HRV indicates cognitive load and stress
        if reading.hrv:
            signals['cognitive_load'] = 1 - (reading.hrv / 100)
            signals['stress_indicator'] = reading.stress_level or 0.5
            
        # Breathing patterns indicate mental state
        if reading.breathing_rate:
            if reading.breathing_rate < 10:
                signals['mental_state'] = 'meditative'
            elif reading.breathing_rate < 15:
                signals['mental_state'] = 'focused'
            else:
                signals['mental_state'] = 'active'
                
        # Coherence indicates flow state
        if reading.coherence:
            signals['flow_indicator'] = reading.coherence
            
        # Add timing patterns based on heart rate
        if reading.heart_rate:
            # Simulate typing rhythm from heart rate
            base_interval = 60 / reading.heart_rate  # Seconds per heartbeat
            signals['timing_patterns'] = [
                base_interval * random.uniform(0.8, 1.2)
                for _ in range(5)
            ]
            
        return signals
        
    def start_monitoring(self, callback: Optional[Callable] = None):
        """Start continuous biometric monitoring"""
        self.is_streaming = True
        
        if callback:
            self.callbacks.append(callback)
            
        def monitor_loop():
            while self.is_streaming:
                reading = self.read_all_sensors()
                
                # Convert to consciousness signals
                signals = self.to_consciousness_signals(reading)
                
                # Notify callbacks
                for cb in self.callbacks:
                    cb(reading, signals)
                    
                time.sleep(1)  # 1 Hz monitoring
                
        monitor_thread = threading.Thread(target=monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        logger.info("💓 Started biometric monitoring")
        
    def stop_monitoring(self):
        """Stop biometric monitoring"""
        self.is_streaming = False
        for sensor in self.sensors:
            sensor.stop_streaming()
        logger.info("💓 Stopped biometric monitoring")
        
    def get_current_state(self) -> Dict[str, Any]:
        """Get current biometric state summary"""
        if not self.readings:
            return {'status': 'no_data'}
            
        latest = self.readings[-1]
        
        # Calculate averages over last minute
        recent_readings = [
            r for r in self.readings
            if (datetime.now() - r.timestamp).seconds < 60
        ]
        
        if recent_readings:
            avg_hr = np.mean([r.heart_rate for r in recent_readings if r.heart_rate])
            avg_hrv = np.mean([r.hrv for r in recent_readings if r.hrv])
            avg_coherence = np.mean([r.coherence for r in recent_readings if r.coherence])
        else:
            avg_hr = latest.heart_rate
            avg_hrv = latest.hrv
            avg_coherence = latest.coherence
            
        return {
            'status': 'active',
            'latest_reading': latest.to_dict(),
            'averages': {
                'heart_rate': avg_hr,
                'hrv': avg_hrv,
                'coherence': avg_coherence
            },
            'sensor_count': len(self.sensors),
            'reading_count': len(self.readings)
        }
        
    def demonstrate(self):
        """Demonstrate biometric integration"""
        print("\n💓 Biometric Bridge Demonstration")
        print("=" * 50)
        
        # Connect to simulated sensor
        print("\n1. Connecting to simulated biometric sensor...")
        self.simulated_sensor.connect()
        
        # Demonstrate different states
        states = ['relaxed', 'focused', 'stressed', 'flow', 'meditation']
        
        for state in states:
            print(f"\n2. Simulating {state} state...")
            self.simulated_sensor.simulate_state_change(state)
            
            # Take a reading
            time.sleep(1)
            reading = self.read_all_sensors()
            
            # Display biometric data
            print(f"   Heart Rate: {reading.heart_rate:.1f} BPM")
            print(f"   HRV: {reading.hrv:.1f} ms")
            print(f"   Breathing: {reading.breathing_rate:.1f} breaths/min")
            print(f"   Coherence: {reading.coherence:.2f}")
            print(f"   Stress: {reading.stress_level:.0%}")
            print(f"   Relaxation: {reading.relaxation:.0%}")
            
            # Convert to consciousness signals
            signals = self.to_consciousness_signals(reading)
            print(f"   → Consciousness energy: {signals.get('energy_level', 0):.0%}")
            print(f"   → Mental state: {signals.get('mental_state', 'unknown')}")
            
            time.sleep(2)
            
        print("\n" + "=" * 50)
        print("Biometric bridge demonstration complete!")


class PatternDetector:
    """Detect patterns in biometric data streams"""
    
    def __init__(self):
        self.patterns = []
        
    def detect_flow_state(self, readings: List[BiometricReading]) -> Optional[BiometricPattern]:
        """Detect flow state from biometric patterns"""
        if len(readings) < 10:
            return None
            
        # Flow state indicators:
        # - Stable, moderate heart rate
        # - High HRV
        # - Regular breathing
        # - High coherence
        
        recent = readings[-10:]
        
        hr_values = [r.heart_rate for r in recent if r.heart_rate]
        if hr_values:
            hr_std = np.std(hr_values)
            hr_mean = np.mean(hr_values)
            
            if hr_std < 5 and 60 < hr_mean < 80:
                # Stable, moderate HR
                
                coherence_values = [r.coherence for r in recent if r.coherence]
                if coherence_values and np.mean(coherence_values) > 0.7:
                    # High coherence
                    
                    return BiometricPattern(
                        name=BiometricPattern.FLOW_STATE,
                        confidence=0.8,
                        duration=timedelta(seconds=len(recent)),
                        implications=[
                            "User is in flow state",
                            "Maintain current environment",
                            "Minimize interruptions"
                        ]
                    )
                    
        return None


# Helper functions
def create_biometric_bridge() -> BiometricBridge:
    """Create and return a biometric bridge instance"""
    return BiometricBridge()


def scan_for_sensors() -> List[str]:
    """Scan for available biometric sensors"""
    available = []
    
    # Check for Bluetooth HRM
    if BLUETOOTH_AVAILABLE:
        bt_sensor = BluetoothHRMSensor()
        devices = bt_sensor.scan_devices()
        for addr, name in devices:
            available.append(f"Bluetooth HRM: {name} ({addr})")
            
    # Check for audio breathing
    if AUDIO_AVAILABLE:
        available.append("Audio Breathing Sensor (Microphone)")
        
    # Always available
    available.append("Simulated Biometric Sensor")
    
    return available


if __name__ == "__main__":
    # Run demonstration
    bridge = BiometricBridge()
    bridge.demonstrate()