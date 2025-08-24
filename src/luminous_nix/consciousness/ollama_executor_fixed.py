#!/usr/bin/env python3
"""
🌉 Fixed Ollama Executor - Reliable LLM Execution
This version fixes timeout issues and provides better error handling.
"""

import asyncio
import subprocess
import time
import logging
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result from Ollama execution"""
    success: bool
    response: str
    model_used: str
    execution_time: float
    cached: bool = False
    error: Optional[str] = None


class FixedOllamaExecutor:
    """
    Fixed Ollama executor that actually works reliably.
    
    Key improvements:
    - Reasonable timeouts based on model size
    - Progress feedback during execution
    - Proper error handling and recovery
    - Circuit breaker for failing models
    """
    
    def __init__(self):
        """Initialize fixed executor"""
        # Model configurations with realistic timeouts
        self.model_configs = {
            'qwen3:0.6b': {'timeout': 15, 'priority': 1},  # Fastest
            'gemma3:4b': {'timeout': 30, 'priority': 2},
            'mistral:7b': {'timeout': 45, 'priority': 3},
            'qwen3:8b': {'timeout': 45, 'priority': 4},
            'gemma2:9b': {'timeout': 60, 'priority': 5},
            'gemma3:12b': {'timeout': 90, 'priority': 6}  # Slowest
        }
        
        # Circuit breaker - track failing models
        self.failing_models = set()
        self.model_failures = {}  # model -> failure count
        
        # Simple cache (in-memory for now)
        self.cache = {}
        
        logger.info("🔧 Fixed Ollama Executor initialized")
        self._verify_ollama()
    
    def _verify_ollama(self):
        """Verify Ollama is installed and working"""
        try:
            result = subprocess.run(
                ['ollama', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("✅ Ollama verified")
            else:
                logger.error("❌ Ollama not working properly")
        except FileNotFoundError:
            logger.error("❌ Ollama not installed")
        except Exception as e:
            logger.error(f"❌ Ollama verification failed: {e}")
    
    def execute(self, 
                prompt: str,
                model: Optional[str] = None,
                task_type: str = 'general',
                use_cache: bool = True,
                progress_callback: Optional[Callable] = None) -> ExecutionResult:
        """
        Execute prompt with proper timeout and error handling.
        
        Args:
            prompt: The prompt to execute
            model: Specific model to use (or auto-select)
            task_type: Type of task for model selection
            use_cache: Whether to use cache
            progress_callback: Function to call with progress updates
            
        Returns:
            ExecutionResult with response or error
        """
        start_time = time.time()
        
        # Check cache first
        cache_key = f"{model or 'auto'}:{prompt[:100]}"
        if use_cache and cache_key in self.cache:
            logger.info("⚡ Cache hit - instant response!")
            return ExecutionResult(
                success=True,
                response=self.cache[cache_key],
                model_used=model or 'cached',
                execution_time=0.001,
                cached=True
            )
        
        # Select model if not specified
        if not model:
            model = self._select_best_model(task_type)
        
        # Check if model is in circuit breaker
        if model in self.failing_models:
            logger.warning(f"⚠️ Model {model} is failing, trying alternative")
            model = self._get_fallback_model(model)
            if not model:
                return ExecutionResult(
                    success=False,
                    response="All models are currently failing",
                    model_used='none',
                    execution_time=time.time() - start_time,
                    error="All models in circuit breaker"
                )
        
        # Get timeout for model
        timeout = self.model_configs.get(model, {}).get('timeout', 30)
        
        # Execute with progress tracking
        if progress_callback:
            progress_callback(f"🚀 Starting {model} (timeout: {timeout}s)")
        
        try:
            # Use subprocess with proper timeout
            logger.info(f"🧠 Executing with {model} (timeout: {timeout}s)")
            
            process = subprocess.Popen(
                ['ollama', 'run', model],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                # Send prompt and wait for response
                stdout, stderr = process.communicate(
                    input=prompt,
                    timeout=timeout
                )
                
                if process.returncode == 0:
                    response = stdout.strip()
                    
                    # Cache successful response
                    if use_cache:
                        self.cache[cache_key] = response
                    
                    # Reset failure count on success
                    if model in self.model_failures:
                        del self.model_failures[model]
                    
                    execution_time = time.time() - start_time
                    logger.info(f"✅ Success with {model} in {execution_time:.1f}s")
                    
                    return ExecutionResult(
                        success=True,
                        response=response,
                        model_used=model,
                        execution_time=execution_time,
                        cached=False
                    )
                else:
                    error_msg = stderr or "Unknown error"
                    logger.error(f"❌ {model} failed: {error_msg}")
                    self._record_failure(model)
                    
                    # Try fallback
                    return self._try_fallback(prompt, model, task_type, use_cache)
                    
            except subprocess.TimeoutExpired:
                process.kill()
                logger.warning(f"⏱️ {model} timed out after {timeout}s")
                self._record_failure(model)
                
                if progress_callback:
                    progress_callback(f"⏱️ {model} timed out, trying smaller model")
                
                # Try with smaller, faster model
                return self._try_fallback(prompt, model, task_type, use_cache)
                
        except Exception as e:
            logger.error(f"❌ Execution failed: {e}")
            return ExecutionResult(
                success=False,
                response=f"Execution failed: {str(e)}",
                model_used=model,
                execution_time=time.time() - start_time,
                error=str(e)
            )
    
    def _select_best_model(self, task_type: str) -> str:
        """Select best available model for task"""
        # Simple heuristic: use small model for simple tasks
        if task_type in ['search', 'list', 'help']:
            preferred = 'qwen3:0.6b'
        elif task_type in ['install', 'configure']:
            preferred = 'gemma3:4b'
        else:
            preferred = 'mistral:7b'
        
        # Check if preferred model is available and not failing
        if preferred not in self.failing_models:
            return preferred
        
        # Find next best model
        for model in sorted(self.model_configs.keys(), 
                          key=lambda m: self.model_configs[m]['priority']):
            if model not in self.failing_models:
                return model
        
        # Last resort
        return 'qwen3:0.6b'
    
    def _get_fallback_model(self, failed_model: str) -> Optional[str]:
        """Get fallback model when one fails"""
        current_priority = self.model_configs.get(failed_model, {}).get('priority', 999)
        
        # Find next smaller model
        for model in sorted(self.model_configs.keys(),
                          key=lambda m: self.model_configs[m]['priority']):
            if (self.model_configs[model]['priority'] < current_priority and
                model not in self.failing_models):
                return model
        
        return None
    
    def _record_failure(self, model: str):
        """Record model failure for circuit breaker"""
        self.model_failures[model] = self.model_failures.get(model, 0) + 1
        
        # Add to circuit breaker after 3 failures
        if self.model_failures[model] >= 3:
            logger.warning(f"🔌 Adding {model} to circuit breaker")
            self.failing_models.add(model)
    
    def _try_fallback(self, prompt: str, failed_model: str, 
                     task_type: str, use_cache: bool) -> ExecutionResult:
        """Try execution with fallback model"""
        fallback = self._get_fallback_model(failed_model)
        
        if fallback:
            logger.info(f"🔄 Trying fallback model: {fallback}")
            return self.execute(prompt, model=fallback, 
                              task_type=task_type, use_cache=use_cache)
        else:
            return ExecutionResult(
                success=False,
                response="All models failed or timed out",
                model_used=failed_model,
                execution_time=0,
                error="No fallback available"
            )
    
    def reset_circuit_breaker(self):
        """Reset circuit breaker for all models"""
        self.failing_models.clear()
        self.model_failures.clear()
        logger.info("🔌 Circuit breaker reset")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get executor statistics"""
        return {
            'cache_size': len(self.cache),
            'failing_models': list(self.failing_models),
            'model_failures': self.model_failures,
            'available_models': [m for m in self.model_configs.keys() 
                               if m not in self.failing_models]
        }


def test_fixed_executor():
    """Test the fixed executor"""
    print("🔧 Testing Fixed Ollama Executor")
    print("=" * 60)
    
    executor = FixedOllamaExecutor()
    
    # Test simple query
    print("\n1. Testing simple query with smallest model...")
    result = executor.execute(
        "What is 2+2? Answer in one word.",
        model='qwen3:0.6b'
    )
    
    if result.success:
        print(f"✅ Success in {result.execution_time:.1f}s")
        print(f"   Response: {result.response[:100]}...")
    else:
        print(f"❌ Failed: {result.error}")
    
    # Test with cache
    print("\n2. Testing cache (should be instant)...")
    result2 = executor.execute(
        "What is 2+2? Answer in one word.",
        model='qwen3:0.6b'
    )
    
    if result2.cached:
        print(f"⚡ Cache hit! Time: {result2.execution_time:.3f}s")
    
    # Test auto model selection
    print("\n3. Testing auto model selection...")
    result3 = executor.execute(
        "How do I list files?",
        task_type='help'
    )
    
    print(f"   Selected model: {result3.model_used}")
    print(f"   Success: {result3.success}")
    
    # Show stats
    print("\n4. Executor statistics:")
    stats = executor.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✨ Fixed executor test complete!")


if __name__ == "__main__":
    test_fixed_executor()