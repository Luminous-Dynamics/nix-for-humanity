#!/usr/bin/env python3
"""
🔮 Predictive Assistant - Anticipating user needs
Learning from patterns to suggest next actions
"""

from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass
import json
from pathlib import Path
import pickle


@dataclass
class CommandPattern:
    """Represents a command pattern with context"""
    command: str
    context: Dict[str, Any]
    frequency: int = 1
    success_rate: float = 1.0


@dataclass
class Prediction:
    """A predicted next action"""
    command: str
    confidence: float
    reason: str
    category: str  # workflow, correction, exploration, completion


class PredictiveAssistant:
    """
    Predicts and suggests next actions based on patterns
    Learning from user behavior to provide proactive help
    """
    
    def __init__(self, learning_file: Optional[Path] = None):
        # Pattern storage
        self.command_sequences = defaultdict(list)  # command -> [next_commands]
        self.error_corrections = {}  # error -> successful_command
        self.workflow_patterns = defaultdict(list)  # task -> [command_sequence]
        self.time_patterns = defaultdict(list)  # time_of_day -> [commands]
        
        # Current session tracking
        self.session_history = []
        self.last_error = None
        self.current_task = None
        
        # Learning configuration
        self.learning_enabled = True
        self.min_pattern_frequency = 2
        self.confidence_threshold = 0.6
        
        # Persistence
        self.learning_file = learning_file or Path.home() / ".local/share/nix-humanity/predictions.pkl"
        self._load_patterns()
    
    def _load_patterns(self):
        """Load learned patterns from disk"""
        if self.learning_file.exists():
            try:
                with open(self.learning_file, 'rb') as f:
                    data = pickle.load(f)
                    self.command_sequences = data.get('sequences', defaultdict(list))
                    self.error_corrections = data.get('corrections', {})
                    self.workflow_patterns = data.get('workflows', defaultdict(list))
            except Exception:
                pass  # Start fresh if load fails
    
    def _save_patterns(self):
        """Save learned patterns to disk"""
        if not self.learning_enabled:
            return
            
        try:
            self.learning_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.learning_file, 'wb') as f:
                pickle.dump({
                    'sequences': dict(self.command_sequences),
                    'corrections': self.error_corrections,
                    'workflows': dict(self.workflow_patterns)
                }, f)
        except Exception:
            pass  # Non-critical if save fails
    
    def record_command(
        self,
        command: str,
        success: bool = True,
        error: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Record a command execution for learning
        Builds patterns over time
        """
        if not self.learning_enabled:
            return
            
        # Add to session history
        self.session_history.append({
            'command': command,
            'success': success,
            'error': error,
            'context': context or {}
        })
        
        # Learn from sequences
        if len(self.session_history) > 1:
            prev_command = self.session_history[-2]['command']
            self.command_sequences[prev_command].append(command)
            
        # Learn from error corrections
        if self.last_error and success:
            self.error_corrections[self.last_error] = command
            self.last_error = None
        elif error:
            self.last_error = error
            
        # Detect workflow patterns
        self._detect_workflow_pattern()
        
        # Save periodically
        if len(self.session_history) % 10 == 0:
            self._save_patterns()
    
    def _detect_workflow_pattern(self):
        """Detect common workflow patterns"""
        if len(self.session_history) < 3:
            return
            
        # Look for repeated sequences
        recent = [h['command'] for h in self.session_history[-5:]]
        
        # Common workflows
        workflows = {
            'package_installation': ['search', 'install'],
            'configuration': ['configure', 'test', 'apply'],
            'troubleshooting': ['error', 'search', 'fix'],
            'exploration': ['info', 'search', 'info']
        }
        
        for workflow_name, pattern in workflows.items():
            if self._matches_pattern(recent, pattern):
                self.workflow_patterns[workflow_name].append(recent)
                self.current_task = workflow_name
    
    def _matches_pattern(self, commands: List[str], pattern: List[str]) -> bool:
        """Check if commands match a pattern"""
        for cmd in commands:
            for p in pattern:
                if p in cmd.lower():
                    return True
        return False
    
    def predict_next(
        self,
        current_command: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Prediction]:
        """
        Predict likely next actions
        Returns sorted list by confidence
        """
        predictions = []
        
        # Strategy 1: Sequence-based prediction
        seq_predictions = self._predict_from_sequences(current_command)
        predictions.extend(seq_predictions)
        
        # Strategy 2: Error correction prediction
        if self.last_error:
            correction = self._predict_error_correction()
            if correction:
                predictions.append(correction)
        
        # Strategy 3: Workflow completion
        workflow_pred = self._predict_workflow_completion(current_command)
        predictions.extend(workflow_pred)
        
        # Strategy 4: Context-based suggestions
        context_pred = self._predict_from_context(current_command, context or {})
        predictions.extend(context_pred)
        
        # Remove duplicates and sort by confidence
        unique_predictions = self._deduplicate_predictions(predictions)
        return sorted(unique_predictions, key=lambda p: p.confidence, reverse=True)
    
    def _predict_from_sequences(self, command: str) -> List[Prediction]:
        """Predict based on command sequences"""
        predictions = []
        
        if command in self.command_sequences:
            next_commands = self.command_sequences[command]
            if next_commands:
                # Count frequencies
                command_counts = Counter(next_commands)
                total = sum(command_counts.values())
                
                for next_cmd, count in command_counts.most_common(3):
                    confidence = count / total
                    if confidence >= self.confidence_threshold:
                        predictions.append(Prediction(
                            command=next_cmd,
                            confidence=confidence,
                            reason=f"Often follows '{command[:20]}...'",
                            category="workflow"
                        ))
        
        return predictions
    
    def _predict_error_correction(self) -> Optional[Prediction]:
        """Predict correction for last error"""
        if self.last_error in self.error_corrections:
            return Prediction(
                command=self.error_corrections[self.last_error],
                confidence=0.9,
                reason="This fixed the error before",
                category="correction"
            )
        
        # Generic error suggestions
        if "not found" in self.last_error:
            return Prediction(
                command="search <package>",
                confidence=0.7,
                reason="Search for the correct package name",
                category="correction"
            )
        elif "permission" in self.last_error.lower():
            return Prediction(
                command="sudo <previous command>",
                confidence=0.8,
                reason="Try with elevated privileges",
                category="correction"
            )
        
        return None
    
    def _predict_workflow_completion(self, command: str) -> List[Prediction]:
        """Predict next step in workflow"""
        predictions = []
        
        if not self.current_task:
            return predictions
            
        # Common workflow completions
        workflow_next = {
            'package_installation': {
                'search': "install <package>",
                'install': "configure <package>"
            },
            'configuration': {
                'configure': "nixos-rebuild test",
                'test': "nixos-rebuild switch"
            },
            'troubleshooting': {
                'error': "search <solution>",
                'search': "apply <fix>"
            }
        }
        
        if self.current_task in workflow_next:
            for trigger, next_cmd in workflow_next[self.current_task].items():
                if trigger in command.lower():
                    predictions.append(Prediction(
                        command=next_cmd,
                        confidence=0.75,
                        reason=f"Next step in {self.current_task.replace('_', ' ')}",
                        category="completion"
                    ))
                    break
        
        return predictions
    
    def _predict_from_context(self, command: str, context: Dict[str, Any]) -> List[Prediction]:
        """Predict based on context"""
        predictions = []
        
        # Time-based predictions
        hour = context.get('hour', 12)
        if 22 <= hour or hour <= 6:
            # Late night - suggest quick tasks
            predictions.append(Prediction(
                command="nixos-rebuild test",
                confidence=0.6,
                reason="Test changes before sleep",
                category="exploration"
            ))
        
        # Session length predictions
        session_length = len(self.session_history)
        if session_length > 20:
            predictions.append(Prediction(
                command="nix-collect-garbage -d",
                confidence=0.65,
                reason="Clean up after long session",
                category="completion"
            ))
        
        # Recent pattern predictions
        if len(self.session_history) >= 3:
            recent_types = [self._classify_command(h['command']) 
                          for h in self.session_history[-3:]]
            
            if recent_types.count('search') >= 2:
                predictions.append(Prediction(
                    command="install <best match>",
                    confidence=0.7,
                    reason="Found what you're looking for?",
                    category="workflow"
                ))
        
        return predictions
    
    def _classify_command(self, command: str) -> str:
        """Classify command type"""
        cmd_lower = command.lower()
        
        if any(word in cmd_lower for word in ['search', 'find', 'looking']):
            return 'search'
        elif any(word in cmd_lower for word in ['install', 'add']):
            return 'install'
        elif any(word in cmd_lower for word in ['config', 'configure']):
            return 'config'
        elif any(word in cmd_lower for word in ['error', 'fail', 'wrong']):
            return 'error'
        else:
            return 'other'
    
    def _deduplicate_predictions(self, predictions: List[Prediction]) -> List[Prediction]:
        """Remove duplicate predictions, keeping highest confidence"""
        seen = {}
        for pred in predictions:
            key = pred.command.split()[0]  # Group by first word
            if key not in seen or pred.confidence > seen[key].confidence:
                seen[key] = pred
        return list(seen.values())
    
    def get_suggestions(
        self,
        command: str,
        context: Optional[Dict[str, Any]] = None,
        max_suggestions: int = 3
    ) -> List[str]:
        """
        Get formatted suggestions for display
        User-friendly prediction output
        """
        predictions = self.predict_next(command, context)[:max_suggestions]
        
        if not predictions:
            return []
            
        suggestions = []
        for pred in predictions:
            if pred.confidence >= 0.8:
                prefix = "💯"  # High confidence
            elif pred.confidence >= 0.7:
                prefix = "💡"  # Good suggestion
            else:
                prefix = "🔮"  # Prediction
                
            suggestion = f"{prefix} {pred.reason}: `{pred.command}`"
            suggestions.append(suggestion)
        
        return suggestions
    
    def learn_from_feedback(self, command: str, was_helpful: bool):
        """
        Learn from user feedback on predictions
        Improves predictions over time
        """
        if not self.learning_enabled:
            return
            
        # Adjust confidence based on feedback
        if was_helpful:
            # Increase pattern frequency
            if len(self.session_history) > 1:
                prev = self.session_history[-2]['command']
                self.command_sequences[prev].append(command)
        else:
            # Reduce pattern confidence
            # Could implement more sophisticated learning here
            pass
        
        self._save_patterns()


# Global assistant instance
_ASSISTANT: Optional[PredictiveAssistant] = None

def get_predictive_assistant() -> PredictiveAssistant:
    """Get or create predictive assistant"""
    global _ASSISTANT
    if _ASSISTANT is None:
        _ASSISTANT = PredictiveAssistant()
    return _ASSISTANT


if __name__ == "__main__":
    # Test predictive assistant
    assistant = get_predictive_assistant()
    
    # Simulate a session
    test_session = [
        ("search firefox", True, None),
        ("install firefox", True, None),
        ("search text editor", True, None),
        ("install neovim", False, "attribute neovim not found"),
        ("install neovim", True, None)
    ]
    
    print("🔮 Testing Predictive Assistant\n")
    print("=" * 60)
    
    for command, success, error in test_session:
        print(f"\nCommand: {command}")
        print(f"Success: {success}")
        if error:
            print(f"Error: {error}")
        
        # Record and predict
        assistant.record_command(command, success, error)
        predictions = assistant.predict_next(command)
        
        if predictions:
            print("\nPredictions:")
            for pred in predictions[:2]:
                print(f"  • {pred.command} ({pred.confidence:.0%})")
                print(f"    → {pred.reason}")
        
        print("-" * 40)
    
    # Test suggestions
    print("\n📝 Formatted Suggestions:")
    suggestions = assistant.get_suggestions("search python")
    for suggestion in suggestions:
        print(suggestion)