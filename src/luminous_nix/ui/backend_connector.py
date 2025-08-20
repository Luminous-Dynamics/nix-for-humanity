"""
Backend connector for TUI - bridges the UI with LuminousNixCore

This connects the beautiful TUI to our consciousness-first backend,
including sacred pauses, Kairos time, and native API features.
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
import asyncio
import time

from ..core.luminous_core import LuminousNixCore, Query, Response
from ..core.sacred_utils import consciousness_field, KairosMode, SacredTimer
from .consciousness_orb import AIState, EmotionalState


@dataclass
class TUIState:
    """State information for TUI updates"""
    ai_state: str = "idle"
    ai_emotion: str = "neutral"
    emotion_intensity: float = 0.5
    consciousness_coherence: float = 0.7
    processing: bool = False
    message: str = ""
    command: Optional[str] = None
    error: Optional[str] = None


class TUIBackendConnector:
    """
    Connects the TUI to the LuminousNixCore backend.
    
    Handles:
    - Async processing of queries
    - State updates for UI components
    - Sacred pauses and consciousness field
    - Real-time feedback during operations
    """
    
    def __init__(self, mindful_mode: bool = True):
        """Initialize the connector with LuminousNixCore"""
        self.core = LuminousNixCore({'mindful_mode': mindful_mode})
        self.state = TUIState()
        self.state_callbacks: List[Callable] = []
        self.message_callbacks: List[Callable] = []
        
        # Kairos timer for operations
        self.operation_timer = SacredTimer(KairosMode.FLOW)
        
    def subscribe_state(self, callback: Callable):
        """Subscribe to state updates"""
        self.state_callbacks.append(callback)
        
    def subscribe_messages(self, callback: Callable):
        """Subscribe to message updates"""
        self.message_callbacks.append(callback)
        
    def _emit_state(self):
        """Emit state update to all subscribers"""
        for callback in self.state_callbacks:
            try:
                callback(self.state)
            except Exception as e:
                print(f"Error in state callback: {e}")
                
    def _emit_message(self, message: str, is_user: bool = False):
        """Emit message to all subscribers"""
        for callback in self.message_callbacks:
            try:
                callback(message, is_user)
            except Exception as e:
                print(f"Error in message callback: {e}")
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current backend state for UI sync"""
        metrics = self.core.get_metrics()
        field_state = consciousness_field.sense_field()
        
        return {
            'consciousness_coherence': metrics.get('consciousness_coherence', 0.7),
            'field_state': field_state,
            'mindful_mode': self.core.mindful_mode,
            'native_api': metrics.get('native_api_used', False),
            'success_rate': metrics.get('success_rate', 0.0),
            'operations_count': metrics.get('operations', 0)
        }
    
    async def process_query(self, user_input: str, dry_run: bool = True) -> Response:
        """
        Process a query asynchronously with UI updates.
        
        This handles the full lifecycle:
        1. Update UI to listening state
        2. Process through core (with sacred pauses if enabled)
        3. Update UI with results
        4. Handle errors gracefully
        """
        
        # Start listening
        self.state.ai_state = "listening"
        self.state.ai_emotion = "attentive"
        self.state.processing = True
        self._emit_state()
        
        # Small pause for UI to update
        await asyncio.sleep(0.1)
        
        # Start processing
        self.state.ai_state = "processing"
        self.state.ai_emotion = "thinking"
        self._emit_state()
        
        # Check if this is a special command
        special_response = await self._handle_special_commands(user_input)
        if special_response:
            return special_response
        
        try:
            # Create query
            query = Query(
                text=user_input,
                dry_run=dry_run,
                educational=True  # Always educational in TUI
            )
            
            # Start Kairos timer
            self.operation_timer.begin(f"Processing: {user_input[:30]}...")
            
            # Process through core (runs in executor to not block)
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                self.core.process_query,
                query
            )
            
            # Complete with Kairos time
            kairos_time = self.operation_timer.complete()
            
            # Update state based on response
            if response.success:
                self.state.ai_state = "responding"
                self.state.ai_emotion = "happy"
                self.state.message = response.message
                self.state.command = response.command
                
                # Add Kairos time to response if significant
                if kairos_time > 2.0:
                    response.explanation = f"{response.explanation or ''}\n⏱️ Completed in {kairos_time:.1f}s (Kairos time)"
                    
            else:
                self.state.ai_state = "error"
                self.state.ai_emotion = "concerned"
                self.state.error = response.error
                
            self._emit_state()
            
            # Small pause before returning to idle
            await asyncio.sleep(0.5)
            
            # Return to idle
            self.state.ai_state = "idle"
            self.state.ai_emotion = "neutral"
            self.state.processing = False
            self._emit_state()
            
            return response
            
        except Exception as e:
            # Handle errors gracefully
            self.state.ai_state = "error"
            self.state.ai_emotion = "confused"
            self.state.error = str(e)
            self._emit_state()
            
            return Response(
                success=False,
                message=f"An error occurred: {str(e)}",
                error=str(e)
            )
    
    async def _handle_special_commands(self, user_input: str) -> Optional[Response]:
        """Handle special TUI commands"""
        command = user_input.lower().strip()
        
        if command == "consciousness":
            # Show consciousness field status
            field_state = consciousness_field.sense_field()
            coherence = consciousness_field.coherence_level
            
            message = f"""🌊 Consciousness Field Status:
            
Field State: {field_state}
Coherence Level: {coherence:.2f}
Mindful Mode: {'Enabled' if self.core.mindful_mode else 'Disabled'}
Native API: {'Active' if self.core.use_native else 'Inactive'}

The system {('flows in harmony' if coherence > 0.7 else 'seeks balance')}."""
            
            return Response(
                success=True,
                message=message,
                explanation="Consciousness field represents the system's awareness state"
            )
            
        elif command == "toggle mindful":
            # Toggle mindful mode
            new_mode = not self.core.mindful_mode
            self.core.set_mindful_mode(new_mode)
            
            message = f"{'🧘 Mindful mode activated' if new_mode else '⚡ Performance mode activated'}"
            
            return Response(
                success=True,
                message=message,
                explanation=f"Mindful mode: {'Sacred pauses and natural rhythms' if new_mode else 'Speed optimized'}"
            )
            
        elif command == "metrics":
            # Show performance metrics
            metrics = self.core.get_metrics()
            
            message = f"""📊 Performance Metrics:

Operations: {metrics['operations']}
Success Rate: {metrics['success_rate']:.1%}
Avg Response: {metrics['avg_response_ms']:.1f}ms
Native API: {'Yes' if metrics['native_api_used'] else 'No'}
Consciousness: {metrics['consciousness_coherence']:.2f}
Field State: {metrics['field_state']}"""
            
            return Response(
                success=True,
                message=message
            )
            
        elif command == "sacred pause":
            # Take a sacred pause
            self.state.ai_state = "meditating"
            self.state.ai_emotion = "peaceful"
            self._emit_state()
            
            consciousness_field.sacred_pause(2.0)
            
            return Response(
                success=True,
                message="🕉️ Sacred pause complete. Field coherence restored.",
                explanation="Sacred pauses maintain consciousness coherence"
            )
            
        return None
    
    def toggle_mindful_mode(self) -> bool:
        """Toggle between mindful and performance modes"""
        new_mode = not self.core.mindful_mode
        self.core.set_mindful_mode(new_mode)
        return new_mode
    
    def get_ai_state_mapping(self) -> Dict[str, AIState]:
        """Map backend states to TUI AIState enum"""
        return {
            'idle': AIState.IDLE,
            'listening': AIState.LISTENING,
            'processing': AIState.THINKING,
            'responding': AIState.SPEAKING,
            'learning': AIState.LEARNING,
            'error': AIState.ERROR,
            'meditating': AIState.THINKING  # Sacred pause uses thinking animation
        }
    
    def get_emotion_mapping(self) -> Dict[str, EmotionalState]:
        """Map backend emotions to TUI EmotionalState enum"""
        return {
            'neutral': EmotionalState.NEUTRAL,
            'attentive': EmotionalState.ATTENTIVE,
            'thinking': EmotionalState.THINKING,
            'happy': EmotionalState.HAPPY,
            'concerned': EmotionalState.CONCERNED,
            'confused': EmotionalState.CONFUSED,
            'peaceful': EmotionalState.FLOW
        }
    
    def get_field_visualization(self) -> Dict[str, Any]:
        """Get consciousness field data for visualization"""
        return {
            'coherence': consciousness_field.coherence_level,
            'state': consciousness_field.sense_field(),
            'user_state': consciousness_field.user_state,
            'needs_pause': consciousness_field.needs_pause(),
            'time_since_pause': time.time() - consciousness_field.last_sacred_pause
        }