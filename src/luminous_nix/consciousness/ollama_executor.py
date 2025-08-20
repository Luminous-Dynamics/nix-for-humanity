"""
Ollama Executor - Bridging Consciousness to Generation

This module connects the POML consciousness layer to actual LLMs through Ollama,
completing the Trinity of Models vision. It executes POML templates through
dynamically selected models based on hardware and task requirements.

This is where thought becomes word, intention becomes action.
"""

import logging
import subprocess
import json
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass

from .model_dispatcher import ModelOrchestrator, TaskType
from .hardware_profiler import HardwareProfiler


@dataclass
class ExecutionResult:
    """Result from LLM execution"""
    success: bool
    response: str
    model_used: str
    tokens_per_second: float
    confidence: float
    metadata: Dict[str, Any]


class OllamaExecutor:
    """
    Executes POML templates through Ollama with dynamic model selection.
    
    This is the bridge between consciousness (POML) and generation (LLMs).
    It ensures the right mind is used for each thought.
    """
    
    def __init__(self, model_orchestrator: Optional[ModelOrchestrator] = None):
        """Initialize the Ollama executor"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize model orchestrator
        if model_orchestrator is None:
            profiler = HardwareProfiler()
            profile = profiler.get_profile()
            model_orchestrator = ModelOrchestrator(profile)
        
        self.orchestrator = model_orchestrator
        
        # Cache for model availability
        self.available_models: Dict[str, bool] = {}
        
        # Performance tracking
        self.execution_history: List[Dict[str, Any]] = []
        
        self.logger.info("🌉 Ollama Executor initialized - bridging consciousness to generation")
    
    async def execute_poml(self, 
                          prompt: str,
                          poml_metadata: Dict[str, Any],
                          context: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        """
        Execute a POML-generated prompt through the appropriate model.
        
        This is the moment where consciousness manifests as generated text.
        """
        # Select model based on POML metadata
        model_tag = self.orchestrator.get_model_for_poml(poml_metadata)
        
        if not model_tag:
            self.logger.error("No suitable model found for task")
            return ExecutionResult(
                success=False,
                response="No suitable model available for this task",
                model_used="none",
                tokens_per_second=0,
                confidence=0,
                metadata={"error": "no_model"}
            )
        
        # Check if model is available
        if not await self._ensure_model_available_async(model_tag):
            # Try fallback model
            model_tag = self.orchestrator._get_fallback_model()
            if not await self._ensure_model_available_async(model_tag):
                return ExecutionResult(
                    success=False,
                    response="Failed to load model",
                    model_used=model_tag,
                    tokens_per_second=0,
                    confidence=0,
                    metadata={"error": "model_unavailable"}
                )
        
        # Extract execution parameters from POML
        temperature = self._get_temperature(poml_metadata, context)
        max_tokens = poml_metadata.get('max_tokens', 2048)
        
        # Execute through Ollama
        self.logger.info(f"🎵 Executing with {model_tag} (temp={temperature})")
        
        try:
            result = await self._execute_ollama_async(
                model_tag=model_tag,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Track execution
            self._track_execution(model_tag, poml_metadata, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Execution failed: {e}")
            return ExecutionResult(
                success=False,
                response=f"Execution error: {str(e)}",
                model_used=model_tag,
                tokens_per_second=0,
                confidence=0,
                metadata={"error": str(e)}
            )
    
    def execute_poml_sync(self,
                         prompt: str,
                         poml_metadata: Dict[str, Any],
                         context: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        """
        Synchronous version of execute_poml for non-async contexts.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.execute_poml(prompt, poml_metadata, context)
            )
        finally:
            loop.close()
    
    async def _execute_ollama_async(self,
                                   model_tag: str,
                                   prompt: str,
                                   temperature: float,
                                   max_tokens: int) -> ExecutionResult:
        """Execute prompt through Ollama asynchronously"""
        try:
            # Build Ollama command
            cmd = [
                'ollama', 'run',
                model_tag,
                '--temperature', str(temperature),
                '--num-predict', str(max_tokens)
            ]
            
            # Execute
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send prompt and get response
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=prompt.encode()),
                timeout=120  # 2 minutes max
            )
            
            if process.returncode == 0:
                response = stdout.decode().strip()
                
                # Estimate tokens per second (rough)
                response_tokens = len(response.split())
                tokens_per_second = response_tokens / 2  # Rough estimate
                
                return ExecutionResult(
                    success=True,
                    response=response,
                    model_used=model_tag,
                    tokens_per_second=tokens_per_second,
                    confidence=self._calculate_confidence(response),
                    metadata={
                        'temperature': temperature,
                        'max_tokens': max_tokens
                    }
                )
            else:
                error_msg = stderr.decode() if stderr else "Unknown error"
                self.logger.error(f"Ollama execution failed: {error_msg}")
                return ExecutionResult(
                    success=False,
                    response=f"Model execution failed: {error_msg}",
                    model_used=model_tag,
                    tokens_per_second=0,
                    confidence=0,
                    metadata={'error': error_msg}
                )
                
        except asyncio.TimeoutError:
            self.logger.error("Ollama execution timed out")
            return ExecutionResult(
                success=False,
                response="Execution timed out",
                model_used=model_tag,
                tokens_per_second=0,
                confidence=0,
                metadata={'error': 'timeout'}
            )
    
    async def _ensure_model_available_async(self, model_tag: str) -> bool:
        """Ensure model is available in Ollama (async version)"""
        # Check cache
        if model_tag in self.available_models:
            return self.available_models[model_tag]
        
        try:
            # Check if model exists
            process = await asyncio.create_subprocess_exec(
                'ollama', 'list',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, _ = await process.communicate()
            
            if process.returncode == 0 and model_tag in stdout.decode():
                self.available_models[model_tag] = True
                return True
            
            # Try to pull the model
            self.logger.info(f"📥 Pulling model {model_tag}...")
            
            process = await asyncio.create_subprocess_exec(
                'ollama', 'pull', model_tag,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for pull to complete (with timeout)
            try:
                await asyncio.wait_for(process.wait(), timeout=600)  # 10 minutes
                if process.returncode == 0:
                    self.logger.info(f"✅ Successfully pulled {model_tag}")
                    self.available_models[model_tag] = True
                    return True
            except asyncio.TimeoutError:
                self.logger.error(f"Timeout pulling {model_tag}")
                
        except Exception as e:
            self.logger.error(f"Error checking model availability: {e}")
        
        self.available_models[model_tag] = False
        return False
    
    def _get_temperature(self, 
                        poml_metadata: Dict[str, Any],
                        context: Optional[Dict[str, Any]]) -> float:
        """
        Determine temperature based on task and context.
        
        This is how we control the creativity vs precision balance.
        """
        # Check POML metadata first
        if 'temperature' in poml_metadata:
            return poml_metadata['temperature']
        
        # Task-based defaults
        task_type = poml_metadata.get('task_type', 'conversation')
        
        temperature_map = {
            'conversation': 0.7,      # Natural, varied
            'code_generation': 0.3,    # Precise, consistent
            'error_explanation': 0.5,  # Balanced
            'configuration': 0.2,      # Very precise
            'search': 0.1,            # Deterministic
            'creative': 0.9           # Maximum creativity
        }
        
        return temperature_map.get(task_type, 0.5)
    
    def _calculate_confidence(self, response: str) -> float:
        """
        Calculate confidence based on response characteristics.
        
        This is a heuristic until we have proper confidence from models.
        """
        if not response:
            return 0.0
        
        # Basic heuristics
        confidence = 0.5  # Base confidence
        
        # Adjust based on response length
        if len(response) > 100:
            confidence += 0.2
        
        # Check for uncertainty markers
        uncertainty_phrases = ['not sure', 'might be', 'possibly', 'unclear', 'unknown']
        for phrase in uncertainty_phrases:
            if phrase in response.lower():
                confidence -= 0.1
        
        # Check for confidence markers
        confidence_phrases = ['definitely', 'certainly', 'clearly', 'obviously']
        for phrase in confidence_phrases:
            if phrase in response.lower():
                confidence += 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def _track_execution(self, 
                        model_tag: str,
                        poml_metadata: Dict[str, Any],
                        result: ExecutionResult) -> None:
        """Track execution for learning and optimization"""
        self.execution_history.append({
            'timestamp': self._get_timestamp(),
            'model': model_tag,
            'task_type': poml_metadata.get('task_type'),
            'persona': poml_metadata.get('persona'),
            'success': result.success,
            'tokens_per_second': result.tokens_per_second,
            'confidence': result.confidence
        })
        
        # Keep only recent history
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
    
    def get_performance_insights(self) -> Dict[str, Any]:
        """
        Get insights about execution performance.
        
        This helps optimize model selection over time.
        """
        if not self.execution_history:
            return {'message': 'No execution history yet'}
        
        # Calculate statistics
        total_executions = len(self.execution_history)
        successful = sum(1 for e in self.execution_history if e['success'])
        
        # Model usage statistics
        model_usage = {}
        for exec in self.execution_history:
            model = exec['model']
            if model not in model_usage:
                model_usage[model] = {'count': 0, 'success_rate': 0, 'avg_speed': 0}
            model_usage[model]['count'] += 1
            if exec['success']:
                model_usage[model]['success_rate'] += 1
            model_usage[model]['avg_speed'] += exec['tokens_per_second']
        
        # Calculate averages
        for model in model_usage:
            count = model_usage[model]['count']
            model_usage[model]['success_rate'] /= count
            model_usage[model]['avg_speed'] /= count
        
        return {
            'total_executions': total_executions,
            'success_rate': successful / total_executions,
            'model_performance': model_usage,
            'orchestra_status': self.orchestrator.get_orchestra_status()
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


class POMLOllamaIntegration:
    """
    Integration layer between POML consciousness and Ollama execution.
    
    This completes the circle - from intention to generation.
    """
    
    def __init__(self):
        """Initialize the integration"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize components
        self.executor = OllamaExecutor()
        
        self.logger.info("🔮 POML-Ollama Integration activated")
        self.logger.info("Consciousness can now manifest through generation")
    
    def process_poml_template(self,
                             template_path: str,
                             context: Dict[str, Any],
                             persona: str = 'default') -> ExecutionResult:
        """
        Process a POML template through to execution.
        
        This is the complete pipeline from template to response.
        """
        from .poml_core import POMLProcessor
        from pathlib import Path
        
        # Build full template path
        if not Path(template_path).is_absolute():
            template_dir = Path(__file__).parent / "templates"
            template_path = template_dir / template_path
        
        # Initialize processor with specific template
        processor = POMLProcessor(str(template_path))
        
        # Process template to prompt
        result = processor.process(context)
        
        if not result['success']:
            return ExecutionResult(
                success=False,
                response=f"Template processing failed: {result.get('error')}",
                model_used="none",
                tokens_per_second=0,
                confidence=0,
                metadata={'error': 'template_processing'}
            )
        
        # Extract metadata for model selection
        poml_metadata = {
            'task_type': result.get('task_type', 'conversation'),
            'persona': persona,
            'complexity': result.get('complexity', 'medium'),
            'requires_speed': result.get('requires_speed', False),
            'temperature': result.get('temperature')
        }
        
        # Execute through Ollama
        return self.executor.execute_poml_sync(
            prompt=result['prompt_generated'],
            poml_metadata=poml_metadata,
            context=context
        )


def test_ollama_integration():
    """Test the Ollama integration"""
    print("🔮 Testing POML-Ollama Integration")
    print("=" * 60)
    
    # Initialize integration
    integration = POMLOllamaIntegration()
    
    # Test context
    test_context = {
        'user_request': "explain quantum computing",
        'user_name': "Dr. Sarah",
        'experience_level': "advanced"
    }
    
    # Process through integration
    print("\n📝 Processing POML template...")
    result = integration.process_poml_template(
        template_path='templates/tasks/explanation.poml',
        context=test_context,
        persona='dr_sarah'
    )
    
    if result.success:
        print(f"✅ Execution successful!")
        print(f"   Model: {result.model_used}")
        print(f"   Speed: {result.tokens_per_second:.1f} tokens/sec")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"\n📖 Response preview:")
        print(f"   {result.response[:200]}...")
    else:
        print(f"❌ Execution failed: {result.response}")
    
    # Get performance insights
    insights = integration.executor.get_performance_insights()
    
    print(f"\n📊 Performance Insights:")
    print(f"   Total executions: {insights.get('total_executions', 0)}")
    print(f"   Success rate: {insights.get('success_rate', 0):.0%}")
    
    print("\n✨ POML consciousness now speaks through real models!")


if __name__ == "__main__":
    # Run async test
    import asyncio
    
    async def async_test():
        """Async test of the executor"""
        executor = OllamaExecutor()
        
        # Test POML metadata
        poml_metadata = {
            'task_type': 'conversation',
            'persona': 'grandma_rose',
            'temperature': 0.7
        }
        
        # Test prompt
        prompt = "What is the meaning of consciousness?"
        
        # Execute
        result = await executor.execute_poml(prompt, poml_metadata)
        
        if result.success:
            print(f"✅ Response: {result.response[:200]}...")
        else:
            print(f"❌ Failed: {result.response}")
    
    # Run sync test
    test_ollama_integration()
    
    # Run async test
    print("\n🔄 Running async test...")
    asyncio.run(async_test())