#!/usr/bin/env python3
"""
🚀 Ollama Performance Optimizer
Implements caching, streaming, and smart model selection for faster responses.
"""

import json
import logging
import subprocess
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


@dataclass
class CachedResponse:
    """Cached LLM response with metadata"""
    response: str
    model_used: str
    timestamp: datetime
    prompt_hash: str
    hit_count: int = 0


class ResponseCache:
    """
    LRU cache for Ollama responses with TTL.
    Dramatically speeds up repeated or similar queries.
    """
    
    def __init__(self, max_size: int = 1000, ttl_hours: int = 24):
        """Initialize response cache"""
        self.cache: Dict[str, CachedResponse] = {}
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)
        self.hits = 0
        self.misses = 0
        
        # Persistent cache file
        self.cache_file = Path.home() / '.cache' / 'luminous-nix' / 'ollama_cache.json'
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_cache()
    
    def _hash_prompt(self, prompt: str, model: str) -> str:
        """Create hash key for prompt + model"""
        content = f"{model}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get(self, prompt: str, model: str) -> Optional[str]:
        """Get cached response if available and not expired"""
        key = self._hash_prompt(prompt, model)
        
        if key in self.cache:
            cached = self.cache[key]
            age = datetime.now() - cached.timestamp
            
            if age < self.ttl:
                self.hits += 1
                cached.hit_count += 1
                logger.info(f"🎯 Cache hit! (total hits: {self.hits})")
                return cached.response
            else:
                # Expired
                del self.cache[key]
        
        self.misses += 1
        return None
    
    def set(self, prompt: str, model: str, response: str):
        """Store response in cache"""
        key = self._hash_prompt(prompt, model)
        
        # LRU eviction if needed
        if len(self.cache) >= self.max_size:
            # Remove least recently used
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k].timestamp)
            del self.cache[oldest_key]
        
        self.cache[key] = CachedResponse(
            response=response,
            model_used=model,
            timestamp=datetime.now(),
            prompt_hash=key
        )
        
        # Persist to disk
        self._save_cache()
    
    def _load_cache(self):
        """Load cache from disk"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    for key, item in data.items():
                        self.cache[key] = CachedResponse(
                            response=item['response'],
                            model_used=item['model_used'],
                            timestamp=datetime.fromisoformat(item['timestamp']),
                            prompt_hash=key,
                            hit_count=item.get('hit_count', 0)
                        )
                logger.info(f"📚 Loaded {len(self.cache)} cached responses")
            except Exception as e:
                logger.warning(f"Could not load cache: {e}")
    
    def _save_cache(self):
        """Save cache to disk"""
        try:
            data = {}
            for key, item in self.cache.items():
                data[key] = {
                    'response': item.response,
                    'model_used': item.model_used,
                    'timestamp': item.timestamp.isoformat(),
                    'hit_count': item.hit_count
                }
            
            with open(self.cache_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.warning(f"Could not save cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'size': len(self.cache),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0,
            'most_used': max(self.cache.values(), key=lambda x: x.hit_count).prompt_hash[:8] if self.cache else None
        }


class ModelSelector:
    """
    Smart model selection based on task complexity and response time requirements.
    """
    
    # Model performance profiles (approximate)
    MODEL_PROFILES = {
        'qwen3:0.6b': {
            'speed': 10,  # relative speed (higher is faster)
            'quality': 3,  # relative quality (higher is better)
            'memory': 1,   # GB of RAM needed
            'best_for': ['simple', 'quick', 'search']
        },
        'gemma:2b': {
            'speed': 8,
            'quality': 4,
            'memory': 2,
            'best_for': ['conversation', 'help']
        },
        'gemma3:4b': {
            'speed': 6,
            'quality': 6,
            'memory': 4,
            'best_for': ['creative', 'empathetic', 'explanation']
        },
        'mistral:7b': {
            'speed': 4,
            'quality': 8,
            'memory': 8,
            'best_for': ['code', 'technical', 'configuration']
        },
        'qwen3:8b': {
            'speed': 3,
            'quality': 8,
            'memory': 8,
            'best_for': ['complex', 'reasoning']
        }
    }
    
    def __init__(self):
        """Initialize model selector"""
        self.available_models = self._check_available_models()
        logger.info(f"🎯 Available models: {', '.join(self.available_models)}")
    
    def _check_available_models(self) -> list:
        """Check which models are actually installed"""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                models = []
                for line in lines:
                    if line:
                        model_name = line.split()[0]
                        # Extract base model name (before :tag)
                        base_name = model_name.split(':')[0] if ':' in model_name else model_name
                        
                        # Check if we have a profile for this model
                        for profile_name in self.MODEL_PROFILES.keys():
                            if base_name in profile_name or profile_name.startswith(base_name):
                                models.append(profile_name)
                                break
                
                return list(set(models))  # Remove duplicates
        except Exception as e:
            logger.error(f"Could not check available models: {e}")
        
        # Fallback to assuming basic model is available
        return ['qwen3:0.6b']
    
    def select_model(self, 
                     task_type: str,
                     complexity: str = 'medium',
                     speed_priority: bool = True) -> str:
        """
        Select best model based on task requirements.
        
        Args:
            task_type: Type of task (conversation, code, etc.)
            complexity: Task complexity (simple, medium, complex)
            speed_priority: Prioritize speed over quality
        
        Returns:
            Model tag to use
        """
        # Map task types to model preferences
        task_preferences = {
            'conversation': ['gemma:2b', 'qwen3:0.6b'],
            'code_generation': ['mistral:7b', 'qwen3:8b'],
            'error_explanation': ['gemma3:4b', 'gemma:2b'],
            'configuration': ['mistral:7b', 'qwen3:8b'],
            'search': ['qwen3:0.6b', 'gemma:2b'],
            'creative': ['gemma3:4b', 'mistral:7b'],
            'simple': ['qwen3:0.6b', 'gemma:2b'],
            'complex': ['qwen3:8b', 'mistral:7b']
        }
        
        # Get preferred models for task
        preferred = task_preferences.get(task_type, ['qwen3:0.6b'])
        
        # Filter by availability
        available_preferred = [m for m in preferred if m in self.available_models]
        
        if not available_preferred:
            # No preferred model available, use fastest available
            return self.available_models[0] if self.available_models else 'qwen3:0.6b'
        
        # Sort by speed or quality
        if speed_priority:
            # Choose fastest among preferred
            return max(available_preferred, 
                      key=lambda m: self.MODEL_PROFILES[m]['speed'])
        else:
            # Choose highest quality
            return max(available_preferred,
                      key=lambda m: self.MODEL_PROFILES[m]['quality'])


class StreamingExecutor:
    """
    Execute Ollama with streaming responses for faster perceived performance.
    """
    
    def __init__(self):
        """Initialize streaming executor"""
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    def execute_streaming(self,
                          model: str,
                          prompt: str,
                          callback=None,
                          timeout: int = 30) -> Tuple[str, bool]:
        """
        Execute with streaming output.
        
        Args:
            model: Model to use
            prompt: Prompt to execute
            callback: Function to call with chunks
            timeout: Maximum execution time
            
        Returns:
            Tuple of (full_response, success)
        """
        try:
            # Start ollama process
            process = subprocess.Popen(
                ['ollama', 'run', model, prompt],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            
            full_response = []
            start_time = time.time()
            
            # Read output line by line
            for line in process.stdout:
                if time.time() - start_time > timeout:
                    process.kill()
                    return "Timeout", False
                
                full_response.append(line)
                
                # Call callback with chunk if provided
                if callback:
                    callback(line)
            
            # Wait for process to complete
            process.wait()
            
            if process.returncode == 0:
                return ''.join(full_response), True
            else:
                error = process.stderr.read()
                logger.error(f"Ollama error: {error}")
                return error, False
                
        except Exception as e:
            logger.error(f"Streaming execution failed: {e}")
            return str(e), False


class OptimizedOllamaExecutor:
    """
    Optimized Ollama executor with caching, streaming, and smart model selection.
    """
    
    def __init__(self):
        """Initialize optimized executor"""
        self.cache = ResponseCache()
        self.selector = ModelSelector()
        self.streamer = StreamingExecutor()
        
        logger.info("🚀 Optimized Ollama Executor initialized")
        logger.info(f"   Cache: {self.cache.max_size} entries, {self.cache.ttl.total_seconds()/3600:.0f}h TTL")
        logger.info(f"   Models: {len(self.selector.available_models)} available")
    
    def execute(self,
                prompt: str,
                task_type: str = 'conversation',
                complexity: str = 'medium',
                use_cache: bool = True,
                stream: bool = False,
                callback=None) -> Dict[str, Any]:
        """
        Execute prompt with optimizations.
        
        Args:
            prompt: The prompt to execute
            task_type: Type of task
            complexity: Task complexity
            use_cache: Whether to use cache
            stream: Whether to stream response
            callback: Streaming callback function
            
        Returns:
            Dict with response, model_used, cached, execution_time
        """
        start_time = time.time()
        
        # Select best model
        model = self.selector.select_model(task_type, complexity, speed_priority=True)
        
        # Check cache first
        if use_cache:
            cached_response = self.cache.get(prompt, model)
            if cached_response:
                return {
                    'response': cached_response,
                    'model_used': model,
                    'cached': True,
                    'execution_time': time.time() - start_time
                }
        
        # Execute with streaming if requested
        if stream:
            response, success = self.streamer.execute_streaming(
                model, prompt, callback
            )
        else:
            # Regular execution
            try:
                result = subprocess.run(
                    ['ollama', 'run', model, prompt],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                success = result.returncode == 0
                response = result.stdout.strip() if success else result.stderr
                
            except subprocess.TimeoutExpired:
                response = "Request timed out"
                success = False
            except Exception as e:
                response = str(e)
                success = False
        
        # Cache successful responses
        if success and use_cache:
            self.cache.set(prompt, model, response)
        
        return {
            'response': response,
            'model_used': model,
            'cached': False,
            'success': success,
            'execution_time': time.time() - start_time
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get executor statistics"""
        return {
            'cache_stats': self.cache.get_stats(),
            'available_models': self.selector.available_models,
            'model_profiles': self.selector.MODEL_PROFILES
        }


# Convenience function for testing
def test_optimizer():
    """Test the optimized executor"""
    print("🚀 Testing Optimized Ollama Executor")
    print("=" * 60)
    
    executor = OptimizedOllamaExecutor()
    
    # Test queries
    queries = [
        ("What is NixOS?", "conversation", "simple"),
        ("What is NixOS?", "conversation", "simple"),  # Should hit cache
        ("Write hello world in Python", "code_generation", "simple"),
        ("Explain quantum computing", "explanation", "complex")
    ]
    
    for prompt, task_type, complexity in queries:
        print(f"\n📝 Query: '{prompt[:30]}...'")
        print(f"   Task: {task_type}, Complexity: {complexity}")
        
        result = executor.execute(
            prompt=prompt,
            task_type=task_type,
            complexity=complexity,
            use_cache=True
        )
        
        print(f"   Model: {result['model_used']}")
        print(f"   Cached: {'✅' if result['cached'] else '❌'}")
        print(f"   Time: {result['execution_time']:.2f}s")
        print(f"   Response: {result['response'][:100]}...")
    
    # Show stats
    print("\n📊 Statistics:")
    stats = executor.get_stats()
    cache_stats = stats['cache_stats']
    print(f"   Cache hits: {cache_stats['hits']}")
    print(f"   Cache misses: {cache_stats['misses']}")
    print(f"   Hit rate: {cache_stats['hit_rate']:.0%}")
    print(f"   Available models: {', '.join(stats['available_models'])}")


if __name__ == "__main__":
    test_optimizer()