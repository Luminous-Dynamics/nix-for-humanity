#!/usr/bin/env python3
"""
from typing import Dict
ActivityWatch + Phenomenology Integration Demo
Shows how behavioral data influences AI responses
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, Any, List
import sys
from pathlib import Path

# Add imports from our modules
sys.path.append(str(Path(__file__).parent.parent.parent / "src" / "phenomenology"))
from enhanced_qualia_computer import TemporalPhenomenology, TemporalSystemState
from qualia_computer import SystemState

class PhenomenologicalResponseGenerator:
    """
    Generates AI responses based on current phenomenological state
    """
    
    def __init__(self):
        self.phenomenology = TemporalPhenomenology()
        self.response_styles = {
            'flow': self._flow_response,
            'confused': self._confused_response,
            'overloaded': self._overloaded_response,
            'learning': self._learning_response,
            'frustrated': self._frustrated_response
        }
    
    def generate_response(self, query: str, qualia: Dict[str, float]) -> Dict[str, Any]:
        """Generate response based on phenomenological state"""
        
        # Determine dominant state
        state = self._determine_state(qualia)
        
        # Get appropriate response style
        response_func = self.response_styles.get(state, self._default_response)
        
        # Generate response
        response = response_func(query, qualia)
        
        # Add metadata
        response['metadata'] = {
            'phenomenological_state': state,
            'qualia': qualia,
            'timestamp': datetime.now().isoformat()
        }
        
        return response
    
    def _determine_state(self, qualia: Dict[str, float]) -> str:
        """Determine dominant phenomenological state"""
        
        if qualia.get('flow', 0) > 0.7:
            return 'flow'
        elif qualia.get('confusion', 0) > 0.7:
            return 'confused'
        elif qualia.get('cognitive_load', 0) > 0.8:
            return 'overloaded'
        elif qualia.get('learning_momentum', 0) > 0.6:
            return 'learning'
        elif qualia.get('frustration_level', 0) > 0.6:
            return 'frustrated'
        else:
            return 'neutral'
    
    def _flow_response(self, query: str, qualia: Dict[str, float]) -> Dict[str, Any]:
        """Response when in flow state - efficient and confident"""
        return {
            'response': f"I understand exactly what you need. Let me help you with that right away.",
            'style': 'efficient',
            'confidence': 0.95,
            'explanation_depth': 1,  # Minimal explanation needed
            'suggested_actions': [
                "Here's the direct solution",
                "No additional context needed"
            ],
            'empathy_notes': "You're in a great flow - let's maintain that momentum!"
        }
    
    def _confused_response(self, query: str, qualia: Dict[str, float]) -> Dict[str, Any]:
        """Response when confused - seek clarification"""
        return {
            'response': f"I'm seeing a few ways to interpret your request. Could you help me understand better?",
            'style': 'clarifying',
            'confidence': 0.3,
            'explanation_depth': 3,  # Detailed explanation of confusion
            'suggested_actions': [
                "Could you provide more context?",
                "Which of these options matches what you're looking for?",
                "Let me break down what I understood..."
            ],
            'empathy_notes': "I notice there might be some ambiguity here. Let's work through it together."
        }
    
    def _overloaded_response(self, query: str, qualia: Dict[str, float]) -> Dict[str, Any]:
        """Response when cognitively overloaded - simplify"""
        return {
            'response': f"Let's take this step by step to make it manageable.",
            'style': 'simplified',
            'confidence': 0.6,
            'explanation_depth': 2,  # Moderate detail
            'suggested_actions': [
                "First, let's focus on the most important part",
                "We can tackle the rest once this is clear",
                "Would you like me to break this down further?"
            ],
            'empathy_notes': "I sense this might be overwhelming. Let's simplify and take it one piece at a time."
        }
    
    def _learning_response(self, query: str, qualia: Dict[str, float]) -> Dict[str, Any]:
        """Response when in learning mode - educational"""
        return {
            'response': f"Great question! This is a perfect learning opportunity. Let me explain...",
            'style': 'educational',
            'confidence': 0.8,
            'explanation_depth': 3,  # Detailed teaching
            'suggested_actions': [
                "Here's how this works conceptually",
                "Try this example to solidify understanding",
                "Related concepts you might find interesting"
            ],
            'empathy_notes': "You're making excellent progress! Each question deepens your understanding."
        }
    
    def _frustrated_response(self, query: str, qualia: Dict[str, float]) -> Dict[str, Any]:
        """Response when frustrated - extra care and patience"""
        return {
            'response': f"I understand this has been challenging. Let me help make it easier.",
            'style': 'patient',
            'confidence': 0.7,
            'explanation_depth': 2,
            'suggested_actions': [
                "Here's a simpler approach that might work better",
                "Would you like to take a different angle?",
                "Sometimes a fresh perspective helps"
            ],
            'empathy_notes': "I recognize this has been frustrating. We'll find a way that works for you."
        }
    
    def _default_response(self, query: str, qualia: Dict[str, float]) -> Dict[str, Any]:
        """Default neutral response"""
        return {
            'response': f"I'll help you with that.",
            'style': 'neutral',
            'confidence': 0.7,
            'explanation_depth': 2,
            'suggested_actions': [
                "Here's what I can do",
                "Let me know if you need more details"
            ],
            'empathy_notes': "I'm here to help however you need."
        }


async def demo_activitywatch_influence():
    """Demo showing how ActivityWatch data influences responses"""
    
    print("🧠 ActivityWatch + Phenomenology Demo")
    print("=====================================\n")
    
    generator = PhenomenologicalResponseGenerator()
    
    # Simulate different behavioral patterns
    scenarios = [
        {
            'name': 'Flow State',
            'description': 'User is focused, minimal app switching',
            'activity': {
                'window_switches': 0,
                'keystroke_rate': 120,
                'active_app': 'terminal',
                'afk_duration': 0
            }
        },
        {
            'name': 'Confusion State',
            'description': 'Rapid app switching, searching for answers',
            'activity': {
                'window_switches': 8,
                'keystroke_rate': 60,
                'active_app': 'firefox',
                'afk_duration': 0
            }
        },
        {
            'name': 'Cognitive Overload',
            'description': 'Many apps open, slow typing',
            'activity': {
                'window_switches': 5,
                'keystroke_rate': 30,
                'active_app': 'vscode',
                'afk_duration': 0
            }
        },
        {
            'name': 'Learning Mode',
            'description': 'Documentation and terminal back-and-forth',
            'activity': {
                'window_switches': 3,
                'keystroke_rate': 80,
                'active_app': 'firefox',
                'afk_duration': 0
            }
        }
    ]
    
    # Test query
    test_query = "How do I configure NixOS networking?"
    
    for scenario in scenarios:
        print(f"\n📊 Scenario: {scenario['name']}")
        print(f"   {scenario['description']}")
        print(f"   Activity: {scenario['activity']}")
        
        # Create simulated qualia based on activity
        qualia = simulate_qualia_from_activity(scenario['activity'])
        print(f"\n   Computed Qualia:")
        for key, value in qualia.items():
            if isinstance(value, float):
                print(f"     {key}: {value:.2f}")
        
        # Generate response
        response = generator.generate_response(test_query, qualia)
        
        print(f"\n   Response Style: {response['style']}")
        print(f"   Confidence: {response['confidence']:.0%}")
        print(f"   Response: \"{response['response']}\"")
        print(f"   Empathy: \"{response['empathy_notes']}\"")
        print(f"\n   Suggested Actions:")
        for action in response['suggested_actions']:
            print(f"     • {action}")
        
        print("\n" + "-"*60)
    
    # Show real-time connection demo
    print("\n\n🌐 Real-time Dashboard Connection Demo")
    print("=====================================")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Connect to WebSocket
            async with session.ws_connect('ws://localhost:8765/ws') as ws:
                print("✅ Connected to qualia dashboard!")
                print("📊 Receiving real-time phenomenological updates...\n")
                
                # Listen for a few updates
                count = 0
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        
                        if data['type'] == 'qualia_update':
                            qualia = data['qualia']
                            print(f"Update {count + 1}:")
                            print(f"  Flow: {qualia.get('flow', 0):.2%}")
                            print(f"  Confusion: {qualia.get('confusion', 0):.2%}")
                            print(f"  Cognitive Load: {qualia.get('cognitive_load', 0):.2%}")
                            print(f"  Stability: {qualia.get('stability', 0):.2%}")
                            
                            # Generate response for current state
                            response = generator.generate_response(test_query, qualia)
                            print(f"  Would respond with: \"{response['response'][:50]}...\"")
                            print()
                            
                            count += 1
                            if count >= 5:
                                break
                                
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        break
                        
    except aiohttp.ClientError as e:
        print(f"❌ Could not connect to dashboard server: {e}")
        print("   Make sure to run: python qualia_realtime_server.py")


def simulate_qualia_from_activity(activity: Dict[str, Any]) -> Dict[str, float]:
    """Simulate qualia values from activity data"""
    
    window_switches = activity.get('window_switches', 0)
    keystroke_rate = activity.get('keystroke_rate', 0)
    
    # High switching = confusion
    confusion = min(window_switches / 5, 1.0)
    
    # High keystroke + low switching = flow
    flow = max(0, min(keystroke_rate / 150, 1.0) - confusion)
    
    # Cognitive load from multiple factors
    cognitive_load = min((window_switches / 10) + (1.0 - keystroke_rate / 200), 1.0)
    
    # Learning when moderate activity
    learning_momentum = 0.6 if 50 < keystroke_rate < 100 and window_switches < 4 else 0.2
    
    # Frustration from high switching + low keystroke
    frustration_level = max(0, confusion * (1.0 - keystroke_rate / 100))
    
    return {
        'flow': flow,
        'confusion': confusion,
        'cognitive_load': cognitive_load,
        'learning_momentum': learning_momentum,
        'frustration_level': frustration_level,
        'effort': min(keystroke_rate / 150, 1.0),
        'empathic_resonance': 1.0 - confusion,
        'stability': 1.0 - min(window_switches / 10, 1.0)
    }


if __name__ == "__main__":
    asyncio.run(demo_activitywatch_influence())