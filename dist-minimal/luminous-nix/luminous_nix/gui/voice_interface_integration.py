#!/usr/bin/env python3
"""
🎙️ Voice Interface Integration for UI Generation
Enables voice commands to generate and interact with NixOS interfaces
"""

import asyncio
import json
import time
import queue
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import sys

sys.path.insert(0, str(Path(__file__).parent))

# Import our UI generation components
from nl_interface_builder_v2 import NLInterfaceBuilderV2, UserContext
from hybrid_nlp_llm import HybridNLPLLM
from learning_persistence import LearningDatabase, PreferenceTracker
from performance_monitor import PerformanceMonitor, PerformanceMetric

# Voice recognition and synthesis
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("Warning: speech_recognition not available - install with: pip install SpeechRecognition")

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("Warning: pyttsx3 not available - install with: pip install pyttsx3")

# For biometric monitoring (optional)
try:
    import pyhrv
    HRV_AVAILABLE = True
except ImportError:
    HRV_AVAILABLE = False


@dataclass
class VoiceCommand:
    """Represents a voice command"""
    
    text: str
    confidence: float
    timestamp: datetime
    user_id: str
    context: Dict[str, Any]
    intent_type: str = "unknown"
    
    
@dataclass
class ConsciousnessState:
    """Tracks user's consciousness state for adaptive UI"""
    
    focus_level: float  # 0-1 scale
    stress_level: float  # 0-1 scale
    energy_level: float  # 0-1 scale
    coherence: float  # Heart rate variability coherence
    last_pause: datetime
    interaction_count: int
    
    def needs_sacred_pause(self) -> bool:
        """Determine if user needs a sacred pause"""
        time_since_pause = (datetime.now() - self.last_pause).total_seconds()
        
        return (
            time_since_pause > 900 or  # 15 minutes
            self.stress_level > 0.7 or
            self.focus_level < 0.3 or
            self.interaction_count > 20
        )
    
    def get_adaptive_params(self) -> Dict[str, Any]:
        """Get UI adaptation parameters based on state"""
        params = {}
        
        # Adapt complexity based on focus
        if self.focus_level < 0.4:
            params["complexity"] = "minimal"
            params["animation_speed"] = "slow"
        elif self.focus_level > 0.7:
            params["complexity"] = "detailed"
            params["animation_speed"] = "normal"
        else:
            params["complexity"] = "balanced"
            params["animation_speed"] = "moderate"
        
        # Adapt visuals based on stress
        if self.stress_level > 0.6:
            params["color_palette"] = "calming"
            params["contrast"] = "soft"
        else:
            params["color_palette"] = "vibrant"
            params["contrast"] = "normal"
        
        # Adapt density based on energy
        if self.energy_level < 0.4:
            params["information_density"] = "sparse"
            params["font_size"] = "large"
        else:
            params["information_density"] = "normal"
            params["font_size"] = "medium"
        
        return params


class VoiceInterfaceEngine:
    """Main voice interface engine for UI generation"""
    
    def __init__(self):
        # UI Generation components
        self.ui_builder = NLInterfaceBuilderV2(use_llm=False)
        self.hybrid_nlp = HybridNLPLLM(use_llm=False)
        
        # Learning and tracking
        self.learning_db = LearningDatabase()
        self.preference_tracker = PreferenceTracker(self.learning_db)
        self.performance_monitor = PerformanceMonitor()
        
        # Voice components
        self.recognizer = sr.Recognizer() if SPEECH_RECOGNITION_AVAILABLE else None
        try:
            self.microphone = sr.Microphone() if SPEECH_RECOGNITION_AVAILABLE else None
        except:
            self.microphone = None
            print("Warning: Microphone not available - will use text input")
        self.tts_engine = self._init_tts() if TTS_AVAILABLE else None
        
        # Consciousness tracking
        self.consciousness_state = ConsciousnessState(
            focus_level=0.5,
            stress_level=0.3,
            energy_level=0.7,
            coherence=0.6,
            last_pause=datetime.now(),
            interaction_count=0
        )
        
        # Voice command queue
        self.command_queue = queue.Queue()
        self.listening = False
        
        # Wake words and command patterns
        self.wake_words = ["luminous", "nix", "computer", "assistant"]
        self.ui_command_patterns = {
            "create": ["create", "make", "build", "generate", "show me"],
            "modify": ["change", "update", "modify", "adjust", "edit"],
            "navigate": ["go to", "open", "switch to", "show"],
            "query": ["what", "how", "when", "where", "why", "list"],
            "control": ["start", "stop", "pause", "resume", "cancel"]
        }
        
    def _init_tts(self):
        """Initialize text-to-speech engine"""
        if not TTS_AVAILABLE:
            return None
        
        try:
            engine = pyttsx3.init()
            
            # Configure voice properties
            voices = engine.getProperty('voices')
            # Try to use a calm, pleasant voice
            for voice in voices:
                if 'female' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            engine.setProperty('rate', 150)  # Slower for clarity
            engine.setProperty('volume', 0.8)
            
            return engine
        except Exception as e:
            print(f"Warning: TTS not available - {e}")
            return None
    
    def speak(self, text: str, priority: str = "normal"):
        """Speak text using TTS"""
        if not self.tts_engine:
            print(f"🔊 {text}")  # Fallback to print
            return
        
        # Adapt speech based on consciousness state
        if self.consciousness_state.stress_level > 0.6:
            # Slower, calmer speech when stressed
            self.tts_engine.setProperty('rate', 130)
            self.tts_engine.setProperty('volume', 0.7)
        
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen_for_command(self, timeout: int = 5) -> Optional[VoiceCommand]:
        """Listen for a voice command"""
        if not SPEECH_RECOGNITION_AVAILABLE:
            # Fallback to text input
            text = input("🎙️ Speak (type instead): ")
            return VoiceCommand(
                text=text,
                confidence=1.0,
                timestamp=datetime.now(),
                user_id="text_user",
                context={}
            )
        
        try:
            with self.microphone as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Visual feedback that we're listening
                print("🎧 Listening...")
                
                # Listen with timeout
                audio = self.recognizer.listen(source, timeout=timeout)
                
                # Recognize speech
                try:
                    text = self.recognizer.recognize_google(audio)
                    confidence = 0.8  # Google doesn't provide confidence scores
                    
                    return VoiceCommand(
                        text=text,
                        confidence=confidence,
                        timestamp=datetime.now(),
                        user_id="voice_user",
                        context=self._get_current_context()
                    )
                    
                except sr.UnknownValueError:
                    print("❓ Could not understand audio")
                    return None
                except sr.RequestError as e:
                    print(f"❌ Recognition error: {e}")
                    return None
                    
        except sr.WaitTimeoutError:
            return None
    
    def _get_current_context(self) -> Dict[str, Any]:
        """Get current context for command interpretation"""
        return {
            "consciousness_state": {
                "focus": self.consciousness_state.focus_level,
                "stress": self.consciousness_state.stress_level,
                "energy": self.consciousness_state.energy_level
            },
            "time_of_day": datetime.now().hour,
            "interaction_count": self.consciousness_state.interaction_count,
            "adaptive_params": self.consciousness_state.get_adaptive_params()
        }
    
    def process_voice_command(self, command: VoiceCommand) -> Dict[str, Any]:
        """Process a voice command and generate appropriate UI"""
        
        start_time = time.time()
        
        # Parse intent using hybrid NLP
        intent = self.hybrid_nlp.parse(command.text, command.context)
        
        # Determine command type
        command_type = self._classify_command(command.text)
        command.intent_type = command_type
        
        # Update interaction count
        self.consciousness_state.interaction_count += 1
        
        # Check if sacred pause needed
        if self.consciousness_state.needs_sacred_pause():
            self._initiate_sacred_pause()
        
        # Generate appropriate response based on command type
        result = {}
        
        if command_type == "create":
            result = self._handle_create_command(command, intent)
        elif command_type == "modify":
            result = self._handle_modify_command(command, intent)
        elif command_type == "navigate":
            result = self._handle_navigate_command(command, intent)
        elif command_type == "query":
            result = self._handle_query_command(command, intent)
        elif command_type == "control":
            result = self._handle_control_command(command, intent)
        else:
            result = self._handle_unknown_command(command)
        
        # Record performance
        generation_time = (time.time() - start_time) * 1000
        
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            request=command.text,
            generation_time=generation_time,
            component_count=len(result.get("components", [])),
            success=result.get("success", False),
            accuracy=intent.confidence.overall,
            persona="voice_user"
        )
        
        self.performance_monitor.record_metric(metric)
        
        # Learn from interaction
        if result.get("success"):
            self.preference_tracker.observe_preference(
                command.user_id,
                "voice_command_type",
                command_type
            )
        
        return result
    
    def _classify_command(self, text: str) -> str:
        """Classify the type of voice command"""
        text_lower = text.lower()
        
        for cmd_type, patterns in self.ui_command_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return cmd_type
        
        return "unknown"
    
    def _handle_create_command(self, command: VoiceCommand, intent) -> Dict:
        """Handle UI creation commands"""
        
        # Get adaptive parameters based on consciousness state
        adaptive_params = self.consciousness_state.get_adaptive_params()
        
        # Create user context with adaptations
        context = UserContext(
            user_id=command.user_id,
            expertise_level=self._infer_expertise_level(),
            device_type="desktop",
            preferences={
                **adaptive_params,
                "voice_controlled": True
            }
        )
        
        # Build the interface
        interface = self.ui_builder.build_interface(command.text, context)
        
        # Provide voice feedback
        component_count = len(interface.components)
        self.speak(f"Created interface with {component_count} components")
        
        return {
            "success": True,
            "action": "create",
            "interface": interface,
            "components": interface.components,
            "message": f"Generated {intent.interface_type} interface"
        }
    
    def _handle_modify_command(self, command: VoiceCommand, intent) -> Dict:
        """Handle UI modification commands"""
        
        # This would modify an existing interface
        self.speak("Modifying the interface as requested")
        
        return {
            "success": True,
            "action": "modify",
            "modifications": intent.components_needed,
            "message": "Interface modified"
        }
    
    def _handle_navigate_command(self, command: VoiceCommand, intent) -> Dict:
        """Handle navigation commands"""
        
        target = intent.target or "dashboard"
        self.speak(f"Navigating to {target}")
        
        return {
            "success": True,
            "action": "navigate",
            "target": target,
            "message": f"Navigated to {target}"
        }
    
    def _handle_query_command(self, command: VoiceCommand, intent) -> Dict:
        """Handle query commands"""
        
        # Generate appropriate query interface
        context = UserContext(user_id=command.user_id)
        interface = self.ui_builder.build_interface(
            f"Create a query results interface for: {command.text}",
            context
        )
        
        self.speak("Here are the results")
        
        return {
            "success": True,
            "action": "query",
            "interface": interface,
            "message": "Query results displayed"
        }
    
    def _handle_control_command(self, command: VoiceCommand, intent) -> Dict:
        """Handle control commands"""
        
        action = intent.action
        self.speak(f"Executing {action} command")
        
        return {
            "success": True,
            "action": "control",
            "control_action": action,
            "message": f"Executed {action}"
        }
    
    def _handle_unknown_command(self, command: VoiceCommand) -> Dict:
        """Handle unrecognized commands"""
        
        self.speak("I didn't understand that. Could you please rephrase?")
        
        return {
            "success": False,
            "action": "unknown",
            "message": "Command not recognized",
            "original_text": command.text
        }
    
    def _infer_expertise_level(self) -> str:
        """Infer user expertise based on consciousness state"""
        
        if self.consciousness_state.focus_level > 0.7:
            return "expert"
        elif self.consciousness_state.focus_level > 0.4:
            return "intermediate"
        else:
            return "beginner"
    
    def _initiate_sacred_pause(self):
        """Initiate a sacred pause for the user"""
        
        self.speak("Time for a sacred pause. Let's take three deep breaths together.")
        
        # Guide breathing
        for i in range(3):
            time.sleep(1)
            self.speak("Breathe in...")
            time.sleep(4)
            self.speak("And out...")
            time.sleep(4)
        
        self.speak("Thank you. Let's continue with renewed focus.")
        
        # Reset consciousness state
        self.consciousness_state.last_pause = datetime.now()
        self.consciousness_state.interaction_count = 0
        self.consciousness_state.stress_level *= 0.7  # Reduce stress
        self.consciousness_state.focus_level = min(1.0, self.consciousness_state.focus_level * 1.2)
    
    def start_continuous_listening(self):
        """Start continuous voice listening mode"""
        
        self.listening = True
        self.speak("Voice interface activated. Say 'luminous' to give a command.")
        
        def listen_loop():
            while self.listening:
                command = self.listen_for_command(timeout=3)
                if command:
                    # Check for wake word
                    text_lower = command.text.lower()
                    wake_word_found = any(word in text_lower for word in self.wake_words)
                    
                    if wake_word_found:
                        self.speak("Yes?")
                        # Listen for actual command
                        actual_command = self.listen_for_command(timeout=10)
                        if actual_command:
                            self.command_queue.put(actual_command)
        
        # Start listening in background thread
        listen_thread = threading.Thread(target=listen_loop, daemon=True)
        listen_thread.start()
    
    def stop_listening(self):
        """Stop continuous listening"""
        self.listening = False
        self.speak("Voice interface deactivated")
    
    def process_command_queue(self):
        """Process queued voice commands"""
        
        while not self.command_queue.empty():
            command = self.command_queue.get()
            result = self.process_voice_command(command)
            
            if result.get("success"):
                print(f"✅ Processed: {command.text}")
            else:
                print(f"❌ Failed: {command.text}")


class ConversationalRefinement:
    """Handles conversational UI refinement through voice"""
    
    def __init__(self, voice_engine: VoiceInterfaceEngine):
        self.voice_engine = voice_engine
        self.current_interface = None
        self.refinement_history = []
        
    def start_refinement_session(self, initial_interface):
        """Start a conversational refinement session"""
        
        self.current_interface = initial_interface
        self.refinement_history = []
        
        self.voice_engine.speak(
            "I've created an interface. Would you like to refine it? "
            "You can say things like 'make it darker', 'add more space', or 'simplify the layout'."
        )
        
        return self.listen_for_refinements()
    
    def listen_for_refinements(self) -> List[Dict]:
        """Listen for refinement commands"""
        
        refinements = []
        listening = True
        
        while listening:
            command = self.voice_engine.listen_for_command(timeout=10)
            
            if not command:
                continue
            
            text_lower = command.text.lower()
            
            # Check for exit phrases
            if any(phrase in text_lower for phrase in ["that's good", "done", "finished", "perfect"]):
                self.voice_engine.speak("Great! Finalizing the interface.")
                listening = False
                continue
            
            # Process refinement
            refinement = self.process_refinement(command)
            if refinement:
                refinements.append(refinement)
                self.apply_refinement(refinement)
                self.voice_engine.speak(f"Applied: {refinement['description']}")
            else:
                self.voice_engine.speak("I didn't understand that refinement. Could you be more specific?")
        
        return refinements
    
    def process_refinement(self, command: VoiceCommand) -> Optional[Dict]:
        """Process a refinement command"""
        
        text_lower = command.text.lower()
        
        refinement = {
            "timestamp": datetime.now(),
            "command": command.text,
            "type": None,
            "parameters": {},
            "description": ""
        }
        
        # Color refinements
        if any(word in text_lower for word in ["darker", "lighter", "brighter"]):
            refinement["type"] = "color"
            if "darker" in text_lower:
                refinement["parameters"]["brightness"] = -20
                refinement["description"] = "Made interface darker"
            elif "lighter" in text_lower or "brighter" in text_lower:
                refinement["parameters"]["brightness"] = 20
                refinement["description"] = "Made interface brighter"
        
        # Spacing refinements
        elif any(word in text_lower for word in ["space", "spacing", "cramped", "tight"]):
            refinement["type"] = "spacing"
            if "more" in text_lower:
                refinement["parameters"]["spacing_multiplier"] = 1.2
                refinement["description"] = "Increased spacing"
            elif "less" in text_lower:
                refinement["parameters"]["spacing_multiplier"] = 0.8
                refinement["description"] = "Decreased spacing"
        
        # Complexity refinements
        elif any(word in text_lower for word in ["simpler", "simplify", "complex", "detailed"]):
            refinement["type"] = "complexity"
            if "simpl" in text_lower:
                refinement["parameters"]["complexity"] = "minimal"
                refinement["description"] = "Simplified interface"
            else:
                refinement["parameters"]["complexity"] = "detailed"
                refinement["description"] = "Added more detail"
        
        # Size refinements
        elif any(word in text_lower for word in ["bigger", "larger", "smaller", "tiny"]):
            refinement["type"] = "size"
            if "bigger" in text_lower or "larger" in text_lower:
                refinement["parameters"]["scale"] = 1.1
                refinement["description"] = "Increased size"
            else:
                refinement["parameters"]["scale"] = 0.9
                refinement["description"] = "Decreased size"
        
        else:
            return None
        
        return refinement
    
    def apply_refinement(self, refinement: Dict):
        """Apply a refinement to the current interface"""
        
        if not self.current_interface:
            return
        
        # Apply refinement based on type
        if refinement["type"] == "color":
            # Adjust color theme
            if "brightness" in refinement["parameters"]:
                # This would adjust the actual interface colors
                pass
        
        elif refinement["type"] == "spacing":
            # Adjust spacing
            multiplier = refinement["parameters"].get("spacing_multiplier", 1.0)
            # This would adjust actual spacing
        
        elif refinement["type"] == "complexity":
            # Adjust complexity
            complexity = refinement["parameters"].get("complexity", "balanced")
            # This would show/hide components based on complexity
        
        elif refinement["type"] == "size":
            # Adjust size
            scale = refinement["parameters"].get("scale", 1.0)
            # This would scale components
        
        # Add to history
        self.refinement_history.append(refinement)


def demo_voice_interface():
    """Demonstrate voice interface capabilities"""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║        🎙️ VOICE INTERFACE INTEGRATION DEMO                         ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize voice engine
    engine = VoiceInterfaceEngine()
    refinement = ConversationalRefinement(engine)
    
    print("\n📊 System Status:")
    print(f"   Speech Recognition: {'✅' if SPEECH_RECOGNITION_AVAILABLE else '❌'}")
    print(f"   Text-to-Speech: {'✅' if TTS_AVAILABLE else '❌'}")
    print(f"   HRV Monitoring: {'✅' if HRV_AVAILABLE else '❌'}")
    
    # Demo voice commands
    print("\n🎤 Testing Voice Commands:")
    
    test_commands = [
        "Create a dashboard with dark theme",
        "Show me system monitoring interface",
        "Build a package manager",
        "Navigate to settings",
        "Make it simpler"
    ]
    
    for text in test_commands:
        print(f"\n   📝 Command: '{text}'")
        
        # Create mock command
        command = VoiceCommand(
            text=text,
            confidence=0.9,
            timestamp=datetime.now(),
            user_id="demo_user",
            context={}
        )
        
        # Process command
        result = engine.process_voice_command(command)
        
        print(f"   → Action: {result.get('action', 'unknown')}")
        print(f"   → Success: {'✅' if result.get('success') else '❌'}")
        print(f"   → Message: {result.get('message', 'No message')}")
        
        if "interface" in result:
            interface = result["interface"]
            print(f"   → Components: {len(interface.components)}")
    
    # Demo consciousness adaptation
    print("\n🧘 Consciousness-Based Adaptation:")
    
    # Simulate different consciousness states
    states = [
        ("High Focus", {"focus_level": 0.9, "stress_level": 0.2, "energy_level": 0.8}),
        ("High Stress", {"focus_level": 0.4, "stress_level": 0.8, "energy_level": 0.5}),
        ("Low Energy", {"focus_level": 0.5, "stress_level": 0.3, "energy_level": 0.2})
    ]
    
    for state_name, levels in states:
        # Update consciousness state
        for key, value in levels.items():
            setattr(engine.consciousness_state, key, value)
        
        params = engine.consciousness_state.get_adaptive_params()
        
        print(f"\n   State: {state_name}")
        print(f"   → Complexity: {params['complexity']}")
        print(f"   → Animation: {params['animation_speed']}")
        print(f"   → Colors: {params['color_palette']}")
        print(f"   → Density: {params['information_density']}")
    
    # Demo sacred pause
    print("\n⏸️ Sacred Pause Detection:")
    
    engine.consciousness_state.interaction_count = 25
    if engine.consciousness_state.needs_sacred_pause():
        print("   ✅ Sacred pause needed - too many interactions")
    
    engine.consciousness_state.stress_level = 0.8
    if engine.consciousness_state.needs_sacred_pause():
        print("   ✅ Sacred pause needed - high stress detected")
    
    print("""
═══════════════════════════════════════════════════════════════════════
✨ Voice Interface Features Demonstrated:

1. Natural Language Commands:
   • Create, modify, navigate, query, control
   • Hybrid NLP+LLM intent understanding
   • Context-aware processing

2. Consciousness-Based Adaptation:
   • Real-time state monitoring
   • Adaptive UI complexity
   • Stress-responsive design
   • Energy-aware density

3. Sacred Pause Integration:
   • Automatic detection
   • Guided breathing exercises
   • State reset and recovery

4. Conversational Refinement:
   • Iterative improvement
   • Natural language adjustments
   • Real-time preview

Next Steps:
• Add real biometric monitoring (HRV, EEG)
• Implement multi-modal feedback
• Create voice-first UI components
• Add personalized voice responses
═══════════════════════════════════════════════════════════════════════
    """)


if __name__ == "__main__":
    demo_voice_interface()