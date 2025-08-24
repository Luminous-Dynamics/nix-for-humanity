#!/usr/bin/env python3
"""
🚀 Real-Time Ollama Executor - Optimized for Voice & Speed
This executor prioritizes speed for real-time STT/TTS interactions.
"""

import asyncio
import subprocess
import time
import logging
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
import json
from enum import Enum

logger = logging.getLogger(__name__)


class QueryComplexity(Enum):
    """Query complexity levels"""
    REALTIME = "realtime"      # < 2s target (for voice)
    QUICK = "quick"             # < 5s target (simple commands)
    BALANCED = "balanced"       # < 15s target (standard queries)
    THOUGHTFUL = "thoughtful"   # < 30s target (complex questions)
    DEEP = "deep"              # < 60s target (research/analysis)


@dataclass
class ExecutionResult:
    """Result from Ollama execution"""
    success: bool
    response: str
    model_used: str
    execution_time: float
    complexity: str
    cached: bool = False
    error: Optional[str] = None


class RealtimeOllamaExecutor:
    """
    Optimized Ollama executor for real-time STT/TTS with dynamic timeouts.
    
    Key features:
    - Ultra-fast models for voice interactions
    - Dynamic timeout based on query complexity
    - Specialized models for different tasks
    - Aggressive caching for common queries
    - Streaming support for long responses
    """
    
    def __init__(self):
        """Initialize real-time executor"""
        # Model configurations optimized for speed
        self.model_configs = {
            # REAL-TIME MODELS (for STT/TTS < 10s total)
            'qwen:0.5b': {'timeout': 2, 'priority': 1, 'category': 'realtime', 'speed': 'ultra-fast'},
            'gemma:2b': {'timeout': 3, 'priority': 2, 'category': 'realtime', 'speed': 'very-fast'},
            'phi3:mini': {'timeout': 3, 'priority': 2, 'category': 'realtime', 'speed': 'very-fast'},
            'tinyllama': {'timeout': 3, 'priority': 2, 'category': 'realtime', 'speed': 'very-fast'},
            'orca-mini': {'timeout': 4, 'priority': 3, 'category': 'realtime', 'speed': 'fast'},
            
            # QUICK RESPONSE MODELS (for commands < 10s)
            'qwen2.5:3b': {'timeout': 8, 'priority': 4, 'category': 'quick', 'speed': 'fast'},
            'gemma2:2b': {'timeout': 8, 'priority': 4, 'category': 'quick', 'speed': 'fast'},
            'mistral:7b-instruct-v0.3-q4': {'timeout': 10, 'priority': 5, 'category': 'quick', 'speed': 'moderate'},
            'llama3.2:3b': {'timeout': 10, 'priority': 5, 'category': 'quick', 'speed': 'moderate'},
            
            # BALANCED MODELS (standard queries < 20s)
            'qwen2:7b': {'timeout': 15, 'priority': 6, 'category': 'balanced', 'speed': 'moderate'},
            'gemma2:9b': {'timeout': 20, 'priority': 7, 'category': 'balanced', 'speed': 'moderate'},
            'mistral:7b': {'timeout': 20, 'priority': 7, 'category': 'balanced', 'speed': 'moderate'},
            
            # THOUGHTFUL MODELS (complex reasoning < 40s)
            'mixtral:8x7b-instruct-v0.1-q4': {'timeout': 35, 'priority': 8, 'category': 'thoughtful', 'speed': 'slow'},
            'llama3:8b': {'timeout': 40, 'priority': 9, 'category': 'thoughtful', 'speed': 'slow'},
            'solar:10.7b': {'timeout': 40, 'priority': 9, 'category': 'thoughtful', 'speed': 'slow'},
            
            # DEEP THINKING MODELS (research/analysis < 120s)
            'llama3:13b': {'timeout': 60, 'priority': 10, 'category': 'deep', 'speed': 'very-slow'},
            'gemma2:27b': {'timeout': 90, 'priority': 11, 'category': 'deep', 'speed': 'very-slow'},
            'llama3:70b-instruct-q4': {'timeout': 120, 'priority': 12, 'category': 'deep', 'speed': 'ultra-slow'},
        }
        
        # Voice-specific optimizations
        self.voice_shortcuts = {
            # Common voice commands with pre-cached responses
            'yes': 'Confirmed.',
            'no': 'Understood.',
            'stop': 'Stopping.',
            'help': 'How can I help you?',
            'hello': 'Hello! How can I assist you?',
            'hi': 'Hi there! What can I do for you?',
            'thanks': "You're welcome!",
            'thank you': "You're very welcome!",
        }
        
        # Circuit breaker for failing models
        self.failing_models = set()
        self.model_failures = {}
        
        # Advanced cache with TTL
        self.cache = {}
        self.cache_timestamps = {}
        self.cache_ttl = 300  # 5 minutes default
        
        # Track model performance
        self.performance_stats = {}
        
        logger.info("🚀 Real-Time Ollama Executor initialized")
        self._verify_ollama()
    
    def _verify_ollama(self):
        """Verify Ollama and list available models"""
        try:
            # Check Ollama version
            result = subprocess.run(
                ['ollama', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("✅ Ollama verified")
                
                # List available models
                list_result = subprocess.run(
                    ['ollama', 'list'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if list_result.returncode == 0:
                    available = list_result.stdout
                    logger.info(f"📦 Available models:\n{available}")
            else:
                logger.error("❌ Ollama not working properly")
        except Exception as e:
            logger.error(f"❌ Ollama verification failed: {e}")
    
    def analyze_query_complexity(self, prompt: str) -> QueryComplexity:
        """
        Analyze query to determine complexity level.
        This determines both model selection and timeout.
        """
        prompt_lower = prompt.lower().strip()
        
        # Check voice shortcuts first
        if prompt_lower in self.voice_shortcuts:
            return QueryComplexity.REALTIME
        
        # Real-time queries (voice, quick commands)
        realtime_keywords = ['hi', 'hello', 'yes', 'no', 'stop', 'start', 'ok', 'okay']
        if any(word == prompt_lower for word in realtime_keywords):
            return QueryComplexity.REALTIME
        if len(prompt.split()) <= 3:  # Very short commands
            return QueryComplexity.REALTIME
        
        # Quick queries (simple tasks)
        quick_keywords = ['install', 'remove', 'list', 'search', 'show', 'open', 'close']
        if any(word in prompt_lower for word in quick_keywords) and len(prompt.split()) <= 10:
            return QueryComplexity.QUICK
        
        # Thoughtful queries (complex questions)
        thoughtful_keywords = ['why', 'how', 'explain', 'compare', 'analyze', 'understand']
        if any(word in prompt_lower for word in thoughtful_keywords):
            return QueryComplexity.THOUGHTFUL
        if '?' in prompt and len(prompt.split()) > 10:  # Longer questions
            return QueryComplexity.THOUGHTFUL
        
        # Deep queries (research, generation)
        deep_keywords = ['generate', 'create', 'design', 'research', 'comprehensive', 'detailed']
        if any(word in prompt_lower for word in deep_keywords):
            return QueryComplexity.DEEP
        if len(prompt.split()) > 50:  # Long detailed requests
            return QueryComplexity.DEEP
        
        # Default to balanced
        return QueryComplexity.BALANCED
    
    async def execute_with_fallback(self, 
                                   prompt: str,
                                   model_preference: str = None,
                                   streaming: bool = False,
                                   progress_callback: Optional[Callable] = None) -> ExecutionResult:
        """
        Execute prompt with automatic complexity detection and model selection.
        
        Args:
            prompt: The prompt to execute
            model_preference: Override complexity detection
            streaming: Enable streaming for long responses
            progress_callback: Callback for progress updates
            
        Returns:
            ExecutionResult with response optimized for speed
        """
        start_time = time.time()
        
        # Check voice shortcuts for instant response
        prompt_lower = prompt.lower().strip()
        if prompt_lower in self.voice_shortcuts:
            logger.info("⚡ Voice shortcut - instant response!")
            return ExecutionResult(
                success=True,
                response=self.voice_shortcuts[prompt_lower],
                model_used='shortcut',
                execution_time=0.001,
                complexity='realtime',
                cached=True
            )
        
        # Detect complexity if not specified
        if not model_preference:
            complexity = self.analyze_query_complexity(prompt)
            model_preference = complexity.value
        else:
            complexity = QueryComplexity(model_preference)
        
        logger.info(f"🧠 Query complexity: {complexity.value}")
        
        # Check cache
        cache_key = f"{complexity.value}:{prompt[:100]}"
        if self._is_cache_valid(cache_key):
            logger.info("⚡ Cache hit - instant response!")
            return ExecutionResult(
                success=True,
                response=self.cache[cache_key],
                model_used='cached',
                execution_time=time.time() - start_time,
                complexity=complexity.value,
                cached=True
            )
        
        # Get models for this complexity level
        models_to_try = self._get_models_for_complexity(complexity)
        
        if not models_to_try:
            return ExecutionResult(
                success=False,
                response="No suitable models available",
                model_used='none',
                execution_time=time.time() - start_time,
                complexity=complexity.value,
                error="No models configured for this complexity"
            )
        
        # Try models in order
        for model in models_to_try:
            if model in self.failing_models:
                continue
                
            config = self.model_configs[model]
            timeout = config['timeout']
            
            if progress_callback:
                progress_callback(f"🚀 Trying {model} (timeout: {timeout}s)")
            
            try:
                # Execute with model
                result = await self._execute_with_model(
                    prompt=prompt,
                    model=model,
                    timeout=timeout,
                    streaming=streaming
                )
                
                if result.success:
                    # Cache successful response
                    self._cache_response(cache_key, result.response)
                    
                    # Track performance
                    self._track_performance(model, result.execution_time, True)
                    
                    result.complexity = complexity.value
                    return result
                else:
                    # Record failure and try next
                    self._record_failure(model)
                    continue
                    
            except Exception as e:
                logger.error(f"❌ Model {model} failed: {e}")
                self._record_failure(model)
                continue
        
        # All models failed
        return ExecutionResult(
            success=False,
            response="All suitable models failed",
            model_used='none',
            execution_time=time.time() - start_time,
            complexity=complexity.value,
            error="No models could handle this query"
        )
    
    async def _execute_with_model(self, prompt: str, model: str, 
                                  timeout: float, streaming: bool) -> ExecutionResult:
        """Execute prompt with specific model"""
        start_time = time.time()
        
        try:
            if streaming:
                # Use streaming for better perceived performance
                response = await self._execute_streaming(prompt, model, timeout)
            else:
                # Regular execution
                process = await asyncio.create_subprocess_exec(
                    'ollama', 'run', model,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(input=prompt.encode()),
                        timeout=timeout
                    )
                    
                    if process.returncode == 0:
                        response = stdout.decode().strip()
                    else:
                        raise Exception(f"Model returned error: {stderr.decode()}")
                        
                except asyncio.TimeoutError:
                    process.kill()
                    raise Exception(f"Model timed out after {timeout}s")
            
            execution_time = time.time() - start_time
            logger.info(f"✅ {model} responded in {execution_time:.1f}s")
            
            return ExecutionResult(
                success=True,
                response=response,
                model_used=model,
                execution_time=execution_time,
                complexity='',  # Set by caller
                cached=False
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                response=str(e),
                model_used=model,
                execution_time=time.time() - start_time,
                complexity='',
                error=str(e)
            )
    
    async def _execute_streaming(self, prompt: str, model: str, timeout: float) -> str:
        """Execute with streaming for better perceived performance"""
        # TODO: Implement streaming execution
        # For now, fall back to regular execution
        process = await asyncio.create_subprocess_exec(
            'ollama', 'run', model,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, _ = await asyncio.wait_for(
            process.communicate(input=prompt.encode()),
            timeout=timeout
        )
        
        return stdout.decode().strip()
    
    def _get_models_for_complexity(self, complexity: QueryComplexity) -> List[str]:
        """Get models suitable for complexity level"""
        models = []
        
        # Get primary models for this complexity
        for model, config in self.model_configs.items():
            if config.get('category') == complexity.value:
                models.append(model)
        
        # Add fallback models for reliability
        if complexity == QueryComplexity.THOUGHTFUL:
            # Can fall back to balanced models
            for model, config in self.model_configs.items():
                if config.get('category') == 'balanced':
                    models.append(model)
        elif complexity == QueryComplexity.DEEP:
            # Can fall back to thoughtful and balanced
            for model, config in self.model_configs.items():
                if config.get('category') in ['thoughtful', 'balanced']:
                    models.append(model)
        
        # Sort by priority
        models.sort(key=lambda m: self.model_configs[m]['priority'])
        
        return models
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if cache_key not in self.cache:
            return False
        
        # Check TTL
        if cache_key in self.cache_timestamps:
            age = time.time() - self.cache_timestamps[cache_key]
            if age > self.cache_ttl:
                # Expired
                del self.cache[cache_key]
                del self.cache_timestamps[cache_key]
                return False
        
        return True
    
    def _cache_response(self, cache_key: str, response: str):
        """Cache response with timestamp"""
        self.cache[cache_key] = response
        self.cache_timestamps[cache_key] = time.time()
        
        # Limit cache size
        if len(self.cache) > 1000:
            # Remove oldest entries
            oldest_keys = sorted(self.cache_timestamps.keys(), 
                               key=lambda k: self.cache_timestamps[k])[:100]
            for key in oldest_keys:
                del self.cache[key]
                del self.cache_timestamps[key]
    
    def _record_failure(self, model: str):
        """Record model failure"""
        self.model_failures[model] = self.model_failures.get(model, 0) + 1
        
        # Circuit breaker after 3 failures
        if self.model_failures[model] >= 3:
            logger.warning(f"🔌 Adding {model} to circuit breaker")
            self.failing_models.add(model)
    
    def _track_performance(self, model: str, execution_time: float, success: bool):
        """Track model performance statistics"""
        if model not in self.performance_stats:
            self.performance_stats[model] = {
                'total_calls': 0,
                'successful_calls': 0,
                'total_time': 0,
                'avg_time': 0
            }
        
        stats = self.performance_stats[model]
        stats['total_calls'] += 1
        if success:
            stats['successful_calls'] += 1
            stats['total_time'] += execution_time
            stats['avg_time'] = stats['total_time'] / stats['successful_calls']
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance statistics"""
        report = {
            'cache_stats': {
                'size': len(self.cache),
                'hit_rate': 'calculated dynamically'
            },
            'model_performance': {},
            'complexity_distribution': {},
            'recommendations': []
        }
        
        # Model performance
        for model, stats in self.performance_stats.items():
            if stats['total_calls'] > 0:
                report['model_performance'][model] = {
                    'avg_response_time': round(stats.get('avg_time', 0), 2),
                    'success_rate': round(stats['successful_calls'] / stats['total_calls'] * 100, 1),
                    'total_calls': stats['total_calls']
                }
        
        # Recommendations
        if any(stats.get('avg_time', 0) > 10 for stats in self.performance_stats.values()):
            report['recommendations'].append(
                "Consider using smaller models for real-time voice interactions"
            )
        
        if len(self.failing_models) > 0:
            report['recommendations'].append(
                f"Models in circuit breaker: {list(self.failing_models)}. Consider restarting Ollama."
            )
        
        return report
    
    def reset_circuit_breaker(self):
        """Reset circuit breaker"""
        self.failing_models.clear()
        self.model_failures.clear()
        logger.info("🔌 Circuit breaker reset")


async def test_realtime_executor():
    """Test the real-time executor"""
    print("🚀 Testing Real-Time Ollama Executor")
    print("=" * 60)
    
    executor = RealtimeOllamaExecutor()
    
    # Test 1: Voice shortcut (instant)
    print("\n1. Testing voice shortcut...")
    result = await executor.execute_with_fallback("hello")
    print(f"   Time: {result.execution_time:.3f}s")
    print(f"   Response: {result.response}")
    print(f"   Complexity: {result.complexity}")
    
    # Test 2: Real-time query
    print("\n2. Testing real-time query...")
    result = await executor.execute_with_fallback("What time?")
    print(f"   Time: {result.execution_time:.1f}s")
    print(f"   Model: {result.model_used}")
    print(f"   Complexity: {result.complexity}")
    
    # Test 3: Quick command
    print("\n3. Testing quick command...")
    result = await executor.execute_with_fallback("list packages")
    print(f"   Time: {result.execution_time:.1f}s")
    print(f"   Model: {result.model_used}")
    print(f"   Complexity: {result.complexity}")
    
    # Test 4: Thoughtful question
    print("\n4. Testing thoughtful question...")
    result = await executor.execute_with_fallback(
        "Why does NixOS use a functional approach to package management?"
    )
    print(f"   Time: {result.execution_time:.1f}s")
    print(f"   Model: {result.model_used}")
    print(f"   Complexity: {result.complexity}")
    
    # Test 5: Performance report
    print("\n5. Performance Report:")
    report = executor.get_performance_report()
    print(f"   Cache size: {report['cache_stats']['size']}")
    print(f"   Models tested: {len(report['model_performance'])}")
    for rec in report['recommendations']:
        print(f"   💡 {rec}")
    
    print("\n" + "=" * 60)
    print("✨ Real-time executor test complete!")


if __name__ == "__main__":
    asyncio.run(test_realtime_executor())