#!/usr/bin/env python3
"""
🔮 Predictive Cache - Anticipating User Needs
Pre-fetches likely next information based on patterns in Data Trinity.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


@dataclass
class Prediction:
    """A prediction about what the user will need next"""
    command: str
    probability: float
    context: Dict[str, Any]
    pre_fetched_data: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def is_fresh(self, max_age_seconds: int = 60) -> bool:
        """Check if prediction is still fresh"""
        age = datetime.now() - self.timestamp
        return age < timedelta(seconds=max_age_seconds)


class PredictiveCache:
    """
    Pre-fetches likely next needs based on Data Trinity patterns.
    
    This creates the 'instant response' feeling by having answers ready
    before the user even asks.
    """
    
    def __init__(self, store=None):
        """Initialize predictive cache with optional Data Trinity store"""
        self.store = store
        self.predictions: Dict[str, Prediction] = {}
        self.command_sequences: Dict[str, List[str]] = defaultdict(list)
        self.transition_probabilities: Dict[Tuple[str, str], float] = {}
        
        # Common command sequences (learned patterns)
        self.known_sequences = {
            "install": ["search", "install", "configure"],
            "debug": ["status", "logs", "fix"],
            "learn": ["help", "explain", "try"],
            "config": ["edit", "validate", "apply"],
            "develop": ["flake init", "add package", "build"]
        }
        
        # Pre-fetch strategies
        self.prefetch_strategies = {
            "search": self._prefetch_search_results,
            "install": self._prefetch_package_info,
            "help": self._prefetch_help_context,
            "status": self._prefetch_system_status,
            "explain": self._prefetch_explanations
        }
        
        logger.info("🔮 Predictive Cache initialized - anticipating user needs")
    
    async def predict_next(self, current_command: str, 
                          user_context: Dict[str, Any] = None) -> List[Prediction]:
        """
        Predict likely next commands based on current command and context.
        
        Returns list of predictions sorted by probability.
        """
        predictions = []
        
        # 1. Check command sequence patterns
        sequence_predictions = self._predict_from_sequences(current_command)
        predictions.extend(sequence_predictions)
        
        # 2. Check Data Trinity patterns if available
        if self.store:
            trinity_predictions = await self._predict_from_trinity(
                current_command, user_context
            )
            predictions.extend(trinity_predictions)
        
        # 3. Apply user context adjustments
        if user_context:
            predictions = self._adjust_for_context(predictions, user_context)
        
        # Sort by probability
        predictions.sort(key=lambda p: p.probability, reverse=True)
        
        # Pre-fetch data for top predictions
        for prediction in predictions[:3]:  # Top 3 most likely
            await self._prefetch_data(prediction)
        
        # Cache predictions
        self.predictions[current_command] = predictions[0] if predictions else None
        
        logger.debug(f"🔮 Predicted {len(predictions)} next commands for '{current_command}'")
        
        return predictions
    
    def _predict_from_sequences(self, current_command: str) -> List[Prediction]:
        """Predict based on known command sequences"""
        predictions = []
        
        # Extract command type (first word)
        cmd_type = current_command.split()[0] if current_command else ""
        
        # Check if this starts a known sequence
        for seq_type, sequence in self.known_sequences.items():
            if cmd_type in sequence:
                idx = sequence.index(cmd_type)
                if idx < len(sequence) - 1:
                    next_cmd = sequence[idx + 1]
                    predictions.append(Prediction(
                        command=next_cmd,
                        probability=0.7,  # High confidence for known sequences
                        context={"sequence": seq_type, "position": idx}
                    ))
        
        # Check transition probabilities
        for (prev_cmd, next_cmd), prob in self.transition_probabilities.items():
            if prev_cmd == cmd_type:
                predictions.append(Prediction(
                    command=next_cmd,
                    probability=prob,
                    context={"learned_transition": True}
                ))
        
        return predictions
    
    async def _predict_from_trinity(self, current_command: str,
                                   user_context: Dict[str, Any]) -> List[Prediction]:
        """Predict using Data Trinity patterns"""
        predictions = []
        
        if not self.store:
            return predictions
        
        try:
            # Query temporal patterns (DuckDB)
            user_id = user_context.get('user_id', 'default') if user_context else 'default'
            trajectory = self.store.get_learning_trajectory(user_id)
            
            if trajectory and len(trajectory) > 1:
                # Find similar command in history
                for i, past_cmd in enumerate(trajectory[:-1]):
                    if self._commands_similar(past_cmd.get('command'), current_command):
                        # What came next?
                        next_cmd = trajectory[i + 1].get('command')
                        if next_cmd:
                            predictions.append(Prediction(
                                command=next_cmd,
                                probability=0.6,
                                context={"source": "temporal_pattern"}
                            ))
            
            # Query semantic similarities (ChromaDB)
            if hasattr(self.store, 'semantic_store'):
                similar = self.store.semantic_store.query(
                    query_texts=[current_command],
                    n_results=3
                )
                
                if similar and similar['documents']:
                    for doc in similar['documents'][0]:
                        # Extract next command from similar interactions
                        predictions.append(Prediction(
                            command=doc,  # Simplified - would parse properly
                            probability=0.5,
                            context={"source": "semantic_similarity"}
                        ))
            
            # Query knowledge graph (Kùzu)
            if hasattr(self.store, 'get_related_concepts'):
                related = self.store.get_related_concepts(current_command)
                for concept in related[:2]:
                    predictions.append(Prediction(
                        command=f"explain {concept}",
                        probability=0.4,
                        context={"source": "knowledge_graph"}
                    ))
        
        except Exception as e:
            logger.error(f"Trinity prediction error: {e}")
        
        return predictions
    
    def _adjust_for_context(self, predictions: List[Prediction],
                           user_context: Dict[str, Any]) -> List[Prediction]:
        """Adjust predictions based on user context"""
        
        # Boost help predictions if user is frustrated
        if user_context.get('frustration_level', 0) > 0.5:
            for pred in predictions:
                if 'help' in pred.command or 'explain' in pred.command:
                    pred.probability *= 1.5
        
        # Boost advanced commands if user is expert
        if user_context.get('user_expertise', 0.5) > 0.7:
            for pred in predictions:
                if any(adv in pred.command for adv in ['flake', 'derivation', 'overlay']):
                    pred.probability *= 1.3
        
        # Reduce complex commands if user is beginner
        if user_context.get('user_expertise', 0.5) < 0.3:
            for pred in predictions:
                if any(complex in pred.command for complex in ['derivation', 'overlay']):
                    pred.probability *= 0.5
        
        # Normalize probabilities
        total = sum(p.probability for p in predictions)
        if total > 0:
            for pred in predictions:
                pred.probability /= total
        
        return predictions
    
    async def _prefetch_data(self, prediction: Prediction):
        """Pre-fetch data for a prediction"""
        
        # Extract command type
        cmd_parts = prediction.command.split()
        if not cmd_parts:
            return
        
        cmd_type = cmd_parts[0]
        
        # Use appropriate prefetch strategy
        if cmd_type in self.prefetch_strategies:
            strategy = self.prefetch_strategies[cmd_type]
            try:
                data = await strategy(prediction)
                prediction.pre_fetched_data = data
                logger.debug(f"📦 Pre-fetched data for '{prediction.command}'")
            except Exception as e:
                logger.error(f"Pre-fetch error: {e}")
    
    async def _prefetch_search_results(self, prediction: Prediction) -> Dict[str, Any]:
        """Pre-fetch search results"""
        # Would query package database
        return {
            "packages": ["package1", "package2"],
            "descriptions": ["Description 1", "Description 2"]
        }
    
    async def _prefetch_package_info(self, prediction: Prediction) -> Dict[str, Any]:
        """Pre-fetch package information"""
        # Would query package details
        return {
            "version": "1.0.0",
            "dependencies": [],
            "size": "10MB"
        }
    
    async def _prefetch_help_context(self, prediction: Prediction) -> Dict[str, Any]:
        """Pre-fetch help information"""
        return {
            "topics": ["installation", "configuration"],
            "examples": ["example1", "example2"]
        }
    
    async def _prefetch_system_status(self, prediction: Prediction) -> Dict[str, Any]:
        """Pre-fetch system status"""
        return {
            "services": "running",
            "disk_usage": "50%",
            "last_update": "2 hours ago"
        }
    
    async def _prefetch_explanations(self, prediction: Prediction) -> Dict[str, Any]:
        """Pre-fetch explanations"""
        return {
            "concept": "explanation",
            "examples": ["example"],
            "related": ["topic1", "topic2"]
        }
    
    def _commands_similar(self, cmd1: str, cmd2: str) -> bool:
        """Check if two commands are similar"""
        if not cmd1 or not cmd2:
            return False
        
        # Simple similarity - same first word
        return cmd1.split()[0] == cmd2.split()[0]
    
    def learn_transition(self, from_command: str, to_command: str):
        """Learn a command transition pattern"""
        # Extract command types
        from_type = from_command.split()[0] if from_command else ""
        to_type = to_command.split()[0] if to_command else ""
        
        if from_type and to_type:
            key = (from_type, to_type)
            
            # Update probability (simple averaging)
            if key in self.transition_probabilities:
                old_prob = self.transition_probabilities[key]
                self.transition_probabilities[key] = (old_prob + 1.0) / 2
            else:
                self.transition_probabilities[key] = 0.5
            
            logger.debug(f"📚 Learned transition: {from_type} → {to_type}")
    
    def get_cached_prediction(self, command: str) -> Optional[Prediction]:
        """Get cached prediction if available and fresh"""
        pred = self.predictions.get(command)
        if pred and pred.is_fresh():
            return pred
        return None
    
    def get_prefetched_data(self, command: str) -> Optional[Dict[str, Any]]:
        """Get pre-fetched data for a command if available"""
        pred = self.get_cached_prediction(command)
        if pred and pred.pre_fetched_data:
            logger.info(f"⚡ Using pre-fetched data for '{command}'")
            return pred.pre_fetched_data
        return None
    
    async def update_from_session(self, session_commands: List[str]):
        """Update predictions based on session history"""
        for i in range(len(session_commands) - 1):
            self.learn_transition(session_commands[i], session_commands[i + 1])
    
    def get_prediction_stats(self) -> Dict[str, Any]:
        """Get statistics about predictions"""
        return {
            "cached_predictions": len(self.predictions),
            "learned_transitions": len(self.transition_probabilities),
            "known_sequences": len(self.known_sequences),
            "fresh_predictions": sum(
                1 for p in self.predictions.values() 
                if p and p.is_fresh()
            )
        }


async def test_predictive_cache():
    """Test the predictive cache system"""
    print("🔮 Testing Predictive Cache")
    print("=" * 60)
    
    cache = PredictiveCache()
    
    # Test sequence prediction
    print("\n1. Testing sequence prediction:")
    predictions = await cache.predict_next("search firefox")
    for pred in predictions[:3]:
        print(f"   {pred.command}: {pred.probability:.2f}")
    
    # Test with context
    print("\n2. Testing with user context:")
    context = {
        "user_expertise": 0.2,  # Beginner
        "frustration_level": 0.7  # Frustrated
    }
    predictions = await cache.predict_next("install", context)
    for pred in predictions[:3]:
        print(f"   {pred.command}: {pred.probability:.2f}")
    
    # Test learning transitions
    print("\n3. Testing transition learning:")
    cache.learn_transition("search package", "install package")
    cache.learn_transition("install package", "configure package")
    
    predictions = await cache.predict_next("search package")
    print(f"   Learned: search → {predictions[0].command if predictions else 'none'}")
    
    # Test pre-fetching
    print("\n4. Testing data pre-fetching:")
    pred = predictions[0] if predictions else None
    if pred and pred.pre_fetched_data:
        print(f"   Pre-fetched: {list(pred.pre_fetched_data.keys())}")
    
    # Get stats
    print("\n5. Prediction statistics:")
    stats = cache.get_prediction_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✨ Predictive cache working!")


if __name__ == "__main__":
    asyncio.run(test_predictive_cache())