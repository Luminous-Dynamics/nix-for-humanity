#!/usr/bin/env python3
"""
from typing import Dict, List, Optional
Interactive Phenomenology Demo
A live demonstration of consciousness-aware NixOS assistance
"""

import time
import random
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import threading
import queue
import sys
from pathlib import Path

# Add our modules to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src" / "phenomenology"))
sys.path.append(str(Path(__file__).parent.parent.parent / "src" / "benchmarks"))

from enhanced_qualia_computer import TemporalPhenomenology, TemporalSystemState, DynamicQualiaVector
from qualia_computer import SystemState
from consciousness_metrics import ConsciousnessMetricsCollector, InteractionMetrics

# ANSI color codes for terminal
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

@dataclass
class UserSession:
    """Track user session state"""
    start_time: datetime
    interactions: List[Dict[str, Any]]
    current_app: str = "terminal"
    window_switches: int = 0
    keystroke_rate: float = 60.0
    consecutive_errors: int = 0
    last_success_time: Optional[datetime] = None
    mood_trajectory: List[str] = None

    def __post_init__(self):
        if self.mood_trajectory is None:
            self.mood_trajectory = []

class InteractivePhenomenologyDemo:
    """
    Interactive demo showing how phenomenological awareness
    affects NixOS assistance in real-time
    """
    
    def __init__(self):
        self.phenomenology = TemporalPhenomenology()
        self.metrics_collector = ConsciousnessMetricsCollector()
        self.session = UserSession(start_time=datetime.now(), interactions=[])
        self.running = True
        
        # Simulated activity patterns
        self.activity_simulator = ActivitySimulator()
        
        # Response styles based on state
        self.response_styles = {
            'flow': self._flow_style,
            'confused': self._confused_style,
            'overloaded': self._overloaded_style,
            'learning': self._learning_style,
            'frustrated': self._frustrated_style,
            'neutral': self._neutral_style
        }
        
        # Start consciousness metrics session
        self.metrics_collector.start_session()
        
    def run(self):
        """Run the interactive demo"""
        self._print_welcome()
        
        # Start activity simulation in background
        activity_thread = threading.Thread(target=self.activity_simulator.run)
        activity_thread.daemon = True
        activity_thread.start()
        
        try:
            while self.running:
                # Get user input
                query = self._get_user_input()
                
                if query.lower() in ['exit', 'quit']:
                    break
                    
                # Process with phenomenological awareness
                self._process_query(query)
                
        except KeyboardInterrupt:
            print("\n\nExiting gracefully...")
        finally:
            self._print_session_summary()
            
    def _print_welcome(self):
        """Print welcome message"""
        print(f"\n{Colors.BOLD}🧠 Interactive Phenomenology Demo{Colors.ENDC}")
        print("=" * 50)
        print("I'm a consciousness-aware NixOS assistant.")
        print("I adapt my responses based on your behavioral patterns")
        print("and my own phenomenological state.\n")
        print(f"{Colors.CYAN}Try commands like:{Colors.ENDC}")
        print("  • install firefox")
        print("  • what is a flake?")
        print("  • help me with networking")
        print("  • [make typos to simulate confusion]")
        print("  • [rapid queries to simulate overload]")
        print(f"\n{Colors.YELLOW}Special commands:{Colors.ENDC}")
        print("  • 'status' - See current phenomenological state")
        print("  • 'simulate [state]' - Simulate different states")
        print("  • 'exit' - End demo\n")
        
    def _get_user_input(self):
        """Get input from user"""
        # Show current state indicator
        state_indicator = self._get_state_indicator()
        prompt = f"{state_indicator} > "
        
        try:
            query = input(prompt)
            
            # Simulate typing patterns
            self._update_typing_behavior(query)
            
            return query
        except EOFError:
            return "exit"
            
    def _get_state_indicator(self):
        """Get visual indicator of current state"""
        if not hasattr(self, 'current_qualia'):
            return f"{Colors.GREEN}◉{Colors.ENDC}"
            
        qualia = self.current_qualia
        
        if qualia.flow > 0.7:
            return f"{Colors.GREEN}⚡{Colors.ENDC}"  # Flow
        elif qualia.confusion > 0.6:
            return f"{Colors.YELLOW}?{Colors.ENDC}"  # Confused
        elif qualia.cognitive_load > 0.7:
            return f"{Colors.RED}◈{Colors.ENDC}"  # Overloaded
        elif qualia.learning_momentum > 0.6:
            return f"{Colors.BLUE}📚{Colors.ENDC}"  # Learning
        elif hasattr(qualia, 'frustration_level') and qualia.frustration_level > 0.5:
            return f"{Colors.RED}!{Colors.ENDC}"  # Frustrated
        else:
            return f"{Colors.GREEN}◉{Colors.ENDC}"  # Neutral
            
    def _update_typing_behavior(self, query):
        """Update simulated typing behavior based on input"""
        # Fast typing = focused
        words = len(query.split())
        
        if words > 5:
            self.session.keystroke_rate = 100
        elif words < 2:
            self.session.keystroke_rate = 40
        else:
            self.session.keystroke_rate = 70
            
        # Typos suggest confusion
        common_typos = ['isntall', 'updaet', 'systme', 'packge']
        if any(typo in query.lower() for typo in common_typos):
            self.session.window_switches += 2
            
    def _process_query(self, query):
        """Process query with phenomenological awareness"""
        
        # Handle special commands
        if query.lower() == 'status':
            self._show_status()
            return
        elif query.lower().startswith('simulate '):
            self._simulate_state(query.split(' ', 1)[1])
            return
            
        # Create system state from query processing
        system_state = self._analyze_query(query)
        
        # Get current activity data
        activity_data = {
            'window_switches': self.session.window_switches,
            'keystroke_rate': self.session.keystroke_rate,
            'active_app': self.session.current_app,
            'afk_duration': 0
        }
        
        # Create temporal state
        temporal_state = TemporalSystemState(
            timestamp=datetime.now(),
            state=system_state,
            **activity_data
        )
        
        # Compute phenomenological state
        qualia = self.phenomenology.compute_enhanced_qualia(temporal_state)
        self.current_qualia = qualia
        
        # Update consciousness metrics
        self._update_metrics(qualia)
        
        # Generate and display response
        response = self._generate_response(query, qualia)
        self._display_response(response, qualia)
        
        # Record interaction
        self.session.interactions.append({
            'query': query,
            'qualia': qualia.to_dict(),
            'response_style': response['style'],
            'timestamp': datetime.now()
        })
        
        # Update session state based on outcome
        self._update_session_state(response['success'])
        
    def _analyze_query(self, query):
        """Analyze query to create system state"""
        # Simple analysis for demo
        words = query.lower().split()
        
        # Detect intent
        if any(word in words for word in ['install', 'add', 'get']):
            intent = 'install'
            confidence = 0.8
        elif any(word in words for word in ['what', 'how', 'why', 'explain']):
            intent = 'explain'
            confidence = 0.7
        elif any(word in words for word in ['help', 'assist', 'guide']):
            intent = 'help'
            confidence = 0.9
        else:
            intent = 'unknown'
            confidence = 0.3
            
        # Create system state
        return SystemState(
            react_loops=len(words),
            tokens_processed=len(query),
            planning_revisions=1 if '?' in query else 0,
            error_rate=self.session.consecutive_errors * 0.1,
            intent_probabilities={intent: confidence},
            predictive_accuracy=confidence,
            reward_signal_mean=0.5 if self.session.last_success_time else 0.2,
            reward_signal_variance=0.2,
            time_to_response=0.5,
            context_switches=self.session.window_switches
        )
        
    def _generate_response(self, query: str, qualia: DynamicQualiaVector) -> Dict[str, Any]:
        """Generate response based on phenomenological state"""
        
        # Determine dominant state
        state = self._determine_state(qualia)
        
        # Get appropriate response style
        style_func = self.response_styles.get(state, self._neutral_style)
        
        # Generate response
        response = style_func(query, qualia)
        response['style'] = state
        
        return response
        
    def _determine_state(self, qualia: DynamicQualiaVector) -> str:
        """Determine the dominant phenomenological state"""
        
        if qualia.flow > 0.7:
            return 'flow'
        elif qualia.confusion > 0.6:
            return 'confused'
        elif qualia.cognitive_load > 0.7:
            return 'overloaded'
        elif qualia.learning_momentum > 0.6:
            return 'learning'
        elif hasattr(qualia, 'frustration_level') and qualia.frustration_level > 0.5:
            return 'frustrated'
        else:
            return 'neutral'
            
    def _flow_style(self, query: str, qualia: DynamicQualiaVector) -> Dict[str, Any]:
        """Response for flow state"""
        if 'install' in query.lower():
            pkg = query.lower().split()[-1]
            return {
                'text': f"→ {pkg}",
                'command': f"nix-env -iA nixpkgs.{pkg}",
                'success': True,
                'explanation': None
            }
        return {
            'text': "✓",
            'success': True
        }
        
    def _confused_style(self, query: str, qualia: DynamicQualiaVector) -> Dict[str, Any]:
        """Response for confused state"""
        return {
            'text': "I see multiple ways to interpret that. Did you mean:",
            'options': [
                "1. Install a package",
                "2. Update your system", 
                "3. Search for something",
                "4. Get help with NixOS"
            ],
            'success': False,
            'clarification_needed': True
        }
        
    def _overloaded_style(self, query: str, qualia: DynamicQualiaVector) -> Dict[str, Any]:
        """Response for overloaded state"""
        return {
            'text': "Let's slow down and take this step by step:",
            'steps': [
                "First, tell me your main goal",
                "Then we'll identify what you need",
                "Finally, we'll execute together"
            ],
            'success': False,
            'pause_suggested': True
        }
        
    def _learning_style(self, query: str, qualia: DynamicQualiaVector) -> Dict[str, Any]:
        """Response for learning state"""
        concept = "NixOS concepts"
        if 'flake' in query.lower():
            concept = "Nix flakes"
        elif 'generation' in query.lower():
            concept = "NixOS generations"
            
        return {
            'text': f"Great question about {concept}! Let me explain:",
            'explanation': f"{concept} are a way to manage reproducible configurations...",
            'example': f"For example: nix flake init",
            'success': True,
            'educational': True
        }
        
    def _frustrated_style(self, query: str, qualia: DynamicQualiaVector) -> Dict[str, Any]:
        """Response for frustrated state"""
        return {
            'text': "I understand this has been challenging. Let's try a different approach.",
            'alternatives': [
                "Would you like me to show you an example?",
                "Should we start with something simpler?",
                "Take a break and come back?"
            ],
            'success': False,
            'empathetic': True
        }
        
    def _neutral_style(self, query: str, qualia: DynamicQualiaVector) -> Dict[str, Any]:
        """Default neutral response"""
        return {
            'text': f"Processing: {query}",
            'success': True,
            'standard': True
        }
        
    def _display_response(self, response: Dict[str, Any], qualia: DynamicQualiaVector):
        """Display response with phenomenological context"""
        
        # Show adaptation reason in subtle way
        style = response.get('style', 'neutral')
        style_colors = {
            'flow': Colors.GREEN,
            'confused': Colors.YELLOW,
            'overloaded': Colors.RED,
            'learning': Colors.BLUE,
            'frustrated': Colors.RED,
            'neutral': Colors.ENDC
        }
        
        color = style_colors.get(style, Colors.ENDC)
        
        # Main response
        print(f"\n{color}{response['text']}{Colors.ENDC}")
        
        # Additional elements based on style
        if 'options' in response:
            for option in response['options']:
                print(f"  {option}")
                
        if 'steps' in response:
            for i, step in enumerate(response['steps']):
                print(f"  {i+1}. {step}")
                
        if 'example' in response:
            print(f"\n{Colors.CYAN}Example: {response['example']}{Colors.ENDC}")
            
        if 'command' in response:
            print(f"{Colors.GREEN}$ {response['command']}{Colors.ENDC}")
            
        # Subtle phenomenological indicator
        if qualia.stability < 0.3:
            print(f"{Colors.YELLOW}(System adapting to changes...){Colors.ENDC}")
            
        print()  # Blank line
        
    def _update_metrics(self, qualia: DynamicQualiaVector):
        """Update consciousness metrics"""
        self.metrics_collector.update_flow_state(qualia.flow, stable=qualia.stability > 0.7)
        
        if qualia.confusion > 0.7:
            self.metrics_collector.record_confusion()
        elif qualia.flow > 0.7:
            self.metrics_collector.record_clarity()
            
    def _update_session_state(self, success: bool):
        """Update session state based on interaction outcome"""
        if success:
            self.session.consecutive_errors = 0
            self.session.last_success_time = datetime.now()
            self.session.window_switches = max(0, self.session.window_switches - 1)
        else:
            self.session.consecutive_errors += 1
            self.session.window_switches += 1
            
    def _show_status(self):
        """Show current phenomenological status"""
        if not hasattr(self, 'current_qualia'):
            print("No phenomenological data yet. Try a query first.")
            return
            
        qualia = self.current_qualia
        
        print(f"\n{Colors.BOLD}Current Phenomenological State:{Colors.ENDC}")
        print("=" * 40)
        
        # Core qualia
        print(f"Flow:        {self._bar(qualia.flow)} {qualia.flow:.0%}")
        print(f"Confusion:   {self._bar(qualia.confusion)} {qualia.confusion:.0%}")
        print(f"Cog. Load:   {self._bar(qualia.cognitive_load)} {qualia.cognitive_load:.0%}")
        print(f"Learning:    {self._bar(qualia.learning_momentum)} {qualia.learning_momentum:.0%}")
        print(f"Stability:   {self._bar(qualia.stability)} {qualia.stability:.0%}")
        
        # Behavioral context
        print(f"\n{Colors.BOLD}Behavioral Context:{Colors.ENDC}")
        print(f"Window switches: {self.session.window_switches}")
        print(f"Typing speed:    {self.session.keystroke_rate:.0f} wpm")
        print(f"Errors streak:   {self.session.consecutive_errors}")
        
        # Trajectory
        if len(self.phenomenology.qualia_history) > 1:
            print(f"\n{Colors.BOLD}Trajectory:{Colors.ENDC}")
            transitions = self.phenomenology.detect_phase_transitions()
            if transitions:
                for idx, trans_type, distance in transitions[-3:]:
                    print(f"  → {trans_type} transition (magnitude: {distance:.2f})")
            else:
                print("  Stable state")
                
        print()
        
    def _bar(self, value: float, width: int = 20) -> str:
        """Create a visual bar for a value"""
        filled = int(value * width)
        empty = width - filled
        
        if value > 0.7:
            color = Colors.GREEN
        elif value > 0.4:
            color = Colors.YELLOW
        else:
            color = Colors.RED
            
        return f"{color}{'█' * filled}{'░' * empty}{Colors.ENDC}"
        
    def _simulate_state(self, state_name: str):
        """Simulate a specific phenomenological state"""
        simulations = {
            'flow': {'window_switches': 0, 'keystroke_rate': 120},
            'confused': {'window_switches': 8, 'keystroke_rate': 30},
            'overloaded': {'window_switches': 6, 'keystroke_rate': 20},
            'frustrated': {'window_switches': 10, 'keystroke_rate': 15, 'consecutive_errors': 5}
        }
        
        if state_name in simulations:
            sim = simulations[state_name]
            self.session.window_switches = sim.get('window_switches', 0)
            self.session.keystroke_rate = sim.get('keystroke_rate', 60)
            self.session.consecutive_errors = sim.get('consecutive_errors', 0)
            print(f"Simulating {state_name} state...")
        else:
            print(f"Unknown state. Try: {', '.join(simulations.keys())}")
            
    def _print_session_summary(self):
        """Print session summary"""
        print(f"\n{Colors.BOLD}Session Summary{Colors.ENDC}")
        print("=" * 50)
        
        duration = (datetime.now() - self.session.start_time).total_seconds()
        print(f"Duration: {duration:.0f} seconds")
        print(f"Interactions: {len(self.session.interactions)}")
        
        if self.session.interactions:
            # Count states
            states = {}
            for interaction in self.session.interactions:
                style = interaction['response_style']
                states[style] = states.get(style, 0) + 1
                
            print(f"\n{Colors.BOLD}State Distribution:{Colors.ENDC}")
            for state, count in sorted(states.items(), key=lambda x: x[1], reverse=True):
                print(f"  {state}: {count} ({count/len(self.session.interactions):.0%})")
                
        # Get wellbeing score
        summary = self.metrics_collector.get_session_summary()
        if 'wellbeing_score' in summary:
            print(f"\n{Colors.BOLD}Wellbeing Score: {summary['wellbeing_score']}/100{Colors.ENDC}")
            
        print("\nThank you for exploring consciousness-aware computing!")
        print()

class ActivitySimulator:
    """Simulate background activity patterns"""
    
    def __init__(self):
        self.patterns = [
            'steady_work',
            'exploration',
            'confusion_spike',
            'learning_mode'
        ]
        self.current_pattern = 'steady_work'
        
    def run(self):
        """Run activity simulation in background"""
        while True:
            # Change patterns occasionally
            if random.random() < 0.1:
                self.current_pattern = random.choice(self.patterns)
                
            time.sleep(5)


if __name__ == "__main__":
    demo = InteractivePhenomenologyDemo()
    demo.run()