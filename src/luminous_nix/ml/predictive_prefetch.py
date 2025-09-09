"""
Predictive Prefetching with Machine Learning
Uses neural networks to predict and prefetch packages before user requests
"""

import json
import time
import pickle
import random
import math
from collections import deque, Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import threading
import hashlib


@dataclass
class PredictionContext:
    """Context for making predictions"""
    current_query: str
    previous_queries: List[str]
    time_of_day: int  # Hour (0-23)
    day_of_week: int  # 0=Monday, 6=Sunday
    session_queries: List[str]
    user_profile: Optional[Dict] = None


class SequencePredictor:
    """
    Simple neural network for sequence prediction
    Uses patterns to predict next likely queries
    """
    
    def __init__(self, embedding_size: int = 50, hidden_size: int = 100):
        """Initialize sequence predictor"""
        self.embedding_size = embedding_size
        self.hidden_size = hidden_size
        
        # Simple vocabulary mapping
        self.vocab = {}
        self.reverse_vocab = {}
        self.vocab_size = 0
        
        # Neural network weights (simplified, no external deps)
        self.weights = {
            'embedding': None,  # vocab_size x embedding_size
            'hidden': None,     # embedding_size x hidden_size
            'output': None      # hidden_size x vocab_size
        }
        
        # Training data
        self.sequences = []
        self.initialized = False
    
    def _initialize_weights(self):
        """Initialize random weights"""
        random.seed(42)  # Reproducible
        
        # Create weight matrices as nested lists
        self.weights['embedding'] = [
            [random.gauss(0, 0.01) for _ in range(self.embedding_size)]
            for _ in range(self.vocab_size)
        ]
        
        self.weights['hidden'] = [
            [random.gauss(0, 0.01) for _ in range(self.hidden_size)]
            for _ in range(self.embedding_size)
        ]
        
        self.weights['output'] = [
            [random.gauss(0, 0.01) for _ in range(self.vocab_size)]
            for _ in range(self.hidden_size)
        ]
        
        self.initialized = True
    
    def _tokenize(self, query: str) -> int:
        """Convert query to token ID"""
        if query not in self.vocab:
            self.vocab[query] = self.vocab_size
            self.reverse_vocab[self.vocab_size] = query
            self.vocab_size += 1
            self.initialized = False  # Need to reinitialize weights
        
        return self.vocab[query]
    
    def _softmax(self, x: List[float]) -> List[float]:
        """Softmax activation"""
        max_x = max(x) if x else 0
        exp_x = [math.exp(val - max_x) for val in x]
        sum_exp = sum(exp_x)
        return [val / sum_exp for val in exp_x] if sum_exp > 0 else x
    
    def _relu(self, x: List[float]) -> List[float]:
        """ReLU activation"""
        return [max(0, val) for val in x]
    
    def _dot_product(self, vec: List[float], matrix: List[List[float]]) -> List[float]:
        """Compute dot product of vector and matrix"""
        result = []
        for row in matrix:
            if len(vec) == len(row):
                result.append(sum(v * w for v, w in zip(vec, row)))
            else:
                result.append(0)
        return result
    
    def predict(self, context: List[str], top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Predict next likely queries
        
        Returns: List of (query, probability) tuples
        """
        if not context or self.vocab_size == 0:
            return []
        
        if not self.initialized:
            self._initialize_weights()
        
        # Use last query for simple prediction
        last_query = context[-1]
        if last_query not in self.vocab:
            return []
        
        token_id = self.vocab[last_query]
        
        # Forward pass through network
        # 1. Embedding lookup
        if token_id < len(self.weights['embedding']):
            embedding = self.weights['embedding'][token_id]
        else:
            embedding = [0] * self.embedding_size
        
        # 2. Hidden layer with ReLU
        hidden = self._relu(self._dot_product(embedding, self.weights['hidden']))
        
        # 3. Output layer
        output = self._dot_product(hidden, self.weights['output'])
        
        # 4. Softmax for probabilities
        probs = self._softmax(output)
        
        # Get top-k predictions
        indexed_probs = [(i, p) for i, p in enumerate(probs)]
        indexed_probs.sort(key=lambda x: x[1], reverse=True)
        top_indices = [idx for idx, _ in indexed_probs[:top_k]]
        
        predictions = []
        for idx in top_indices:
            if idx in self.reverse_vocab:
                query = self.reverse_vocab[idx]
                prob = probs[idx]
                predictions.append((query, float(prob)))
        
        return predictions
    
    def train(self, sequences: List[List[str]], epochs: int = 10):
        """
        Train on query sequences
        Simple training without backprop (for demonstration)
        """
        self.sequences.extend(sequences)
        
        # Build vocabulary
        for sequence in sequences:
            for query in sequence:
                self._tokenize(query)
        
        if not self.initialized:
            self._initialize_weights()
        
        # Simple weight updates based on co-occurrence
        cooccurrence = [[0] * self.vocab_size for _ in range(self.vocab_size)]
        
        for sequence in self.sequences:
            for i in range(len(sequence) - 1):
                curr_token = self._tokenize(sequence[i])
                next_token = self._tokenize(sequence[i + 1])
                if curr_token < self.vocab_size and next_token < self.vocab_size:
                    cooccurrence[curr_token][next_token] += 1
        
        # Normalize co-occurrence matrix
        for i in range(self.vocab_size):
            row_sum = sum(cooccurrence[i])
            if row_sum > 0:
                for j in range(self.vocab_size):
                    cooccurrence[i][j] /= row_sum
        
        # Update output weights based on co-occurrence
        # This is a simplified approach - real implementation would use backprop
        for i in range(min(self.vocab_size, len(self.weights['output'][0]))):
            avg_cooc = sum(cooccurrence[i]) / self.vocab_size if self.vocab_size > 0 else 0
            for j in range(len(self.weights['output'])):
                if i < len(self.weights['output'][j]):
                    self.weights['output'][j][i] *= (1 + avg_cooc * 0.1)
        
        return True


class MarkovChainPredictor:
    """
    Markov chain predictor for query sequences
    Simpler but effective for common patterns
    """
    
    def __init__(self, order: int = 2):
        """Initialize with Markov chain order"""
        self.order = order
        self.transitions = defaultdict(Counter)
        self.query_counts = Counter()
    
    def train(self, sequences: List[List[str]]):
        """Train on query sequences"""
        for sequence in sequences:
            # Count individual queries
            for query in sequence:
                self.query_counts[query] += 1
            
            # Build transition matrix
            for i in range(len(sequence) - self.order):
                # Create context (previous queries)
                context = tuple(sequence[i:i+self.order])
                next_query = sequence[i+self.order]
                
                self.transitions[context][next_query] += 1
    
    def predict(self, context: List[str], top_k: int = 5) -> List[Tuple[str, float]]:
        """Predict next queries based on context"""
        if len(context) < self.order:
            # Not enough context, use frequency
            total = sum(self.query_counts.values())
            if total == 0:
                return []
            
            predictions = [
                (query, count / total)
                for query, count in self.query_counts.most_common(top_k)
            ]
            return predictions
        
        # Get recent context
        context_key = tuple(context[-self.order:])
        
        if context_key not in self.transitions:
            # Unseen context, fall back to frequency
            return self.predict([], top_k)
        
        # Calculate probabilities
        next_queries = self.transitions[context_key]
        total = sum(next_queries.values())
        
        predictions = [
            (query, count / total)
            for query, count in next_queries.most_common(top_k)
        ]
        
        return predictions


class PredictivePrefetchEngine:
    """
    Main engine for predictive prefetching
    Combines multiple prediction strategies
    """
    
    def __init__(self, cache=None):
        """Initialize prefetch engine"""
        self.cache = cache
        
        # Prediction models
        self.sequence_model = SequencePredictor()
        self.markov_model = MarkovChainPredictor(order=2)
        
        # Session tracking
        self.current_session = []
        self.session_history = deque(maxlen=1000)  # Last 1000 sessions
        
        # Prefetch queue
        self.prefetch_queue = deque(maxlen=20)
        self.prefetch_thread = None
        self.stop_prefetch = threading.Event()
        
        # Performance metrics
        self.metrics = {
            'predictions_made': 0,
            'prefetch_hits': 0,
            'prefetch_misses': 0,
            'accuracy': 0.0
        }
        
        # Model persistence
        self.model_path = Path.home() / ".cache" / "luminous-nix" / "ml_models"
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing models
        self._load_models()
        
        # Start prefetch thread
        self._start_prefetch_thread()
    
    def track_query(self, query: str):
        """Track a query in current session"""
        self.current_session.append(query)
        
        # Make predictions for next query
        predictions = self.predict_next(query)
        
        if predictions:
            self.metrics['predictions_made'] += 1
            
            # Add top predictions to prefetch queue
            for predicted_query, confidence in predictions[:3]:
                if confidence > 0.3:  # Confidence threshold
                    self.prefetch_queue.append(predicted_query)
    
    def predict_next(
        self, current_query: str,
        context: Optional[PredictionContext] = None
    ) -> List[Tuple[str, float]]:
        """
        Predict next likely queries
        
        Returns: List of (query, confidence) tuples
        """
        if not context:
            context = PredictionContext(
                current_query=current_query,
                previous_queries=self.current_session[-5:] if self.current_session else [],
                time_of_day=time.localtime().tm_hour,
                day_of_week=time.localtime().tm_wday,
                session_queries=self.current_session
            )
        
        predictions = []
        
        # Get predictions from each model
        if len(self.current_session) > 0:
            # Sequence model predictions
            seq_predictions = self.sequence_model.predict(
                self.current_session[-3:], top_k=5
            )
            
            # Markov model predictions
            markov_predictions = self.markov_model.predict(
                self.current_session[-2:], top_k=5
            )
            
            # Combine predictions with weighted average
            combined = {}
            
            # Weight: 60% Markov, 40% Sequence (Markov is simpler but often more accurate)
            for query, prob in markov_predictions:
                combined[query] = prob * 0.6
            
            for query, prob in seq_predictions:
                if query in combined:
                    combined[query] += prob * 0.4
                else:
                    combined[query] = prob * 0.4
            
            # Add time-based predictions
            time_predictions = self._get_time_based_predictions(context)
            for query, prob in time_predictions:
                if query in combined:
                    combined[query] = (combined[query] + prob) / 2
                else:
                    combined[query] = prob * 0.3
            
            # Sort by combined probability
            predictions = sorted(
                combined.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        
        return predictions
    
    def _get_time_based_predictions(
        self, context: PredictionContext
    ) -> List[Tuple[str, float]]:
        """Get predictions based on time patterns"""
        # Simple time-based heuristics
        predictions = []
        
        hour = context.time_of_day
        
        # Morning (6-10): Development tools
        if 6 <= hour <= 10:
            predictions.extend([
                ("python3", 0.3),
                ("git", 0.3),
                ("vim", 0.2)
            ])
        
        # Afternoon (14-17): Productivity tools
        elif 14 <= hour <= 17:
            predictions.extend([
                ("firefox", 0.3),
                ("libreoffice", 0.2),
                ("slack", 0.2)
            ])
        
        # Evening (19-23): Entertainment
        elif 19 <= hour <= 23:
            predictions.extend([
                ("spotify", 0.3),
                ("vlc", 0.2),
                ("discord", 0.2)
            ])
        
        return predictions
    
    def validate_prediction(self, predicted: str, actual: str) -> bool:
        """Check if prediction was correct"""
        correct = predicted.lower() == actual.lower()
        
        if correct:
            self.metrics['prefetch_hits'] += 1
        else:
            self.metrics['prefetch_misses'] += 1
        
        # Update accuracy
        total = self.metrics['prefetch_hits'] + self.metrics['prefetch_misses']
        if total > 0:
            self.metrics['accuracy'] = self.metrics['prefetch_hits'] / total
        
        return correct
    
    def end_session(self):
        """End current session and train models"""
        if len(self.current_session) > 1:
            # Add to history
            self.session_history.append(self.current_session)
            
            # Retrain models with new data
            self._train_models()
            
            # Save models
            self._save_models()
        
        # Reset session
        self.current_session = []
    
    def _train_models(self):
        """Train prediction models on session history"""
        if len(self.session_history) < 5:
            return  # Not enough data
        
        # Convert deque to list for training
        sessions = list(self.session_history)
        
        # Train Markov model
        self.markov_model.train(sessions)
        
        # Train sequence model
        self.sequence_model.train(sessions, epochs=5)
    
    def _start_prefetch_thread(self):
        """Start background prefetch thread"""
        def prefetch_worker():
            while not self.stop_prefetch.is_set():
                try:
                    # Check prefetch queue
                    if self.prefetch_queue and self.cache:
                        query = self.prefetch_queue.popleft()
                        
                        # Prefetch in cache
                        self.cache.search_hybrid(query)
                        
                        time.sleep(0.1)  # Small delay
                    else:
                        time.sleep(1)  # Wait when queue empty
                
                except Exception:
                    pass  # Silent fail
        
        self.prefetch_thread = threading.Thread(
            target=prefetch_worker,
            daemon=True
        )
        self.prefetch_thread.start()
    
    def get_metrics(self) -> Dict:
        """Get prediction metrics"""
        return {
            **self.metrics,
            'queue_size': len(self.prefetch_queue),
            'session_length': len(self.current_session),
            'trained_sessions': len(self.session_history)
        }
    
    def _save_models(self):
        """Save trained models to disk"""
        try:
            # Save Markov model
            markov_file = self.model_path / "markov_model.pkl"
            with open(markov_file, 'wb') as f:
                pickle.dump({
                    'transitions': dict(self.markov_model.transitions),
                    'query_counts': dict(self.markov_model.query_counts)
                }, f)
            
            # Save sequence model weights
            seq_file = self.model_path / "sequence_model.pkl"
            with open(seq_file, 'wb') as f:
                pickle.dump({
                    'weights': self.sequence_model.weights,
                    'vocab': self.sequence_model.vocab,
                    'reverse_vocab': self.sequence_model.reverse_vocab,
                    'vocab_size': self.sequence_model.vocab_size
                }, f)
            
            # Save session history
            history_file = self.model_path / "session_history.json"
            with open(history_file, 'w') as f:
                json.dump(list(self.session_history), f)
        
        except Exception:
            pass  # Silent fail
    
    def _load_models(self):
        """Load saved models from disk"""
        try:
            # Load Markov model
            markov_file = self.model_path / "markov_model.pkl"
            if markov_file.exists():
                with open(markov_file, 'rb') as f:
                    data = pickle.load(f)
                    self.markov_model.transitions = defaultdict(
                        Counter, data['transitions']
                    )
                    self.markov_model.query_counts = Counter(data['query_counts'])
            
            # Load sequence model
            seq_file = self.model_path / "sequence_model.pkl"
            if seq_file.exists():
                with open(seq_file, 'rb') as f:
                    data = pickle.load(f)
                    self.sequence_model.weights = data['weights']
                    self.sequence_model.vocab = data['vocab']
                    self.sequence_model.reverse_vocab = data['reverse_vocab']
                    self.sequence_model.vocab_size = data['vocab_size']
                    self.sequence_model.initialized = True
            
            # Load session history
            history_file = self.model_path / "session_history.json"
            if history_file.exists():
                with open(history_file, 'r') as f:
                    sessions = json.load(f)
                    self.session_history = deque(sessions, maxlen=1000)
        
        except Exception:
            pass  # Silent fail
    
    def shutdown(self):
        """Clean shutdown"""
        self.stop_prefetch.set()
        if self.prefetch_thread:
            self.prefetch_thread.join(timeout=1)
        
        # Save final state
        self._save_models()


class SmartPrefetchCache:
    """
    Cache with integrated predictive prefetching
    """
    
    def __init__(self, base_cache):
        """Initialize with base cache"""
        self.cache = base_cache
        self.prefetch_engine = PredictivePrefetchEngine(base_cache)
        
        # Track actual vs predicted
        self.last_predictions = []
    
    def search(self, query: str) -> Tuple[List[Dict], float, str]:
        """
        Search with predictive prefetching
        """
        # Track query
        self.prefetch_engine.track_query(query)
        
        # Check if this was predicted
        if self.last_predictions:
            for predicted_query, confidence in self.last_predictions:
                if self.prefetch_engine.validate_prediction(predicted_query, query):
                    # Prediction was correct!
                    break
        
        # Get predictions for next query
        self.last_predictions = self.prefetch_engine.predict_next(query)
        
        # Perform actual search
        results, elapsed_ms, source = self.cache.search_hybrid(query)
        
        return results, elapsed_ms, source
    
    def get_predictions(self) -> List[Tuple[str, float]]:
        """Get current predictions"""
        return self.last_predictions
    
    def get_metrics(self) -> Dict:
        """Get prefetch metrics"""
        return self.prefetch_engine.get_metrics()
    
    def end_session(self):
        """End current session"""
        self.prefetch_engine.end_session()
    
    def shutdown(self):
        """Clean shutdown"""
        self.prefetch_engine.shutdown()
        if hasattr(self.cache, 'shutdown'):
            self.cache.shutdown()