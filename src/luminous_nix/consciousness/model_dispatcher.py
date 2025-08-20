"""
Model Dispatcher - The Conductor of the Mental Orchestra

This module orchestrates the Trinity of Models, selecting the right
intelligence for each task based on hardware capabilities and task requirements.
It is the conductor that ensures each part of consciousness uses the
appropriate mind.
"""

import logging
import subprocess
import json
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path

from .hardware_profiler import HardwareProfile, HardwareTier, HardwareProfiler


class TaskType(Enum):
    """Types of cognitive tasks requiring different models"""
    CONVERSATION = "conversation"      # Natural dialogue (Heart)
    CODE_GENERATION = "code_generation"  # Writing code (Mind)
    INTENT_CLASSIFICATION = "intent_classification"  # Quick parsing (Reflex)
    ERROR_EXPLANATION = "error_explanation"  # Compassionate help (Heart)
    CONFIGURATION = "configuration"    # System setup (Mind)
    SEARCH = "search"                  # Finding packages (Reflex)
    LEARNING = "learning"              # Pattern recognition (Mind)
    VISION = "vision"                  # Image understanding (Special)


@dataclass
class ModelSpec:
    """Specification for a model"""
    name: str
    task_types: List[TaskType]
    min_tier: HardwareTier
    context_window: int
    strengths: List[str]
    ollama_tag: str  # The actual Ollama model tag
    
    def supports_task(self, task_type: TaskType) -> bool:
        """Check if this model supports a given task"""
        return task_type in self.task_types


class ModelOrchestrator:
    """
    The conductor of our mental orchestra, dynamically selecting
    the right model for each task based on hardware and requirements.
    
    This implements the Trinity of Models:
    - Heart (Conversation): GPT-OSS, Gemma
    - Mind (Logic/Code): Qwen 2
    - Reflex (Fast tasks): Gemma Edge
    """
    
    def __init__(self, hardware_profile: Optional[HardwareProfile] = None):
        """Initialize the model orchestrator"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Get hardware profile
        if hardware_profile is None:
            profiler = HardwareProfiler()
            hardware_profile = profiler.get_profile()
        
        self.hardware_profile = hardware_profile
        
        # Initialize model registry
        self.model_registry = self._build_model_registry()
        
        # Track active models
        self.active_models: Dict[str, Any] = {}
        
        # Model selection cache
        self.selection_cache: Dict[str, str] = {}
        
        self.logger.info(f"🎼 Model Orchestrator initialized for {hardware_profile.tier.value} tier")
    
    def _build_model_registry(self) -> Dict[str, ModelSpec]:
        """Build the registry of available models"""
        return {
            # === HEART MODELS (Conversation) ===
            # Gemma 3 models (newer, better performance)
            'gemma3-4b': ModelSpec(
                name='Gemma 3 4B',
                task_types=[TaskType.CONVERSATION, TaskType.ERROR_EXPLANATION],
                min_tier=HardwareTier.APPRENTICE,
                context_window=8192,
                strengths=['modern', 'efficient', 'balanced'],
                ollama_tag='gemma3:4b'
            ),
            'gemma3-12b': ModelSpec(
                name='Gemma 3 12B',
                task_types=[TaskType.CONVERSATION, TaskType.ERROR_EXPLANATION],
                min_tier=HardwareTier.JOURNEYMAN,
                context_window=8192,
                strengths=['powerful', 'nuanced', 'comprehensive'],
                ollama_tag='gemma3:12b'
            ),
            'gpt-oss-large': ModelSpec(
                name='GPT-OSS Large',
                task_types=[TaskType.CONVERSATION, TaskType.ERROR_EXPLANATION],
                min_tier=HardwareTier.MASTER,
                context_window=8192,
                strengths=['empathy', 'nuance', 'safety'],
                ollama_tag='gpt-oss:latest'
            ),
            'gemma2-27b': ModelSpec(
                name='Gemma 2 27B',
                task_types=[TaskType.CONVERSATION, TaskType.ERROR_EXPLANATION],
                min_tier=HardwareTier.MASTER,
                context_window=8192,
                strengths=['efficiency', 'instruction-following', 'safety'],
                ollama_tag='gemma2:27b'
            ),
            'gemma2-9b': ModelSpec(
                name='Gemma 2 9B',
                task_types=[TaskType.CONVERSATION, TaskType.ERROR_EXPLANATION],
                min_tier=HardwareTier.JOURNEYMAN,
                context_window=8192,
                strengths=['balanced', 'efficient', 'safe'],
                ollama_tag='gemma2:9b'
            ),
            'gemma-7b': ModelSpec(
                name='Gemma 7B',
                task_types=[TaskType.CONVERSATION, TaskType.ERROR_EXPLANATION],
                min_tier=HardwareTier.APPRENTICE,
                context_window=8192,
                strengths=['compact', 'fast', 'reliable'],
                ollama_tag='gemma:7b'
            ),
            
            # === MIND MODELS (Code/Logic) ===
            'qwen2-72b': ModelSpec(
                name='Qwen 2 72B',
                task_types=[TaskType.CODE_GENERATION, TaskType.CONFIGURATION, TaskType.LEARNING],
                min_tier=HardwareTier.SAGE,
                context_window=32768,
                strengths=['code-mastery', 'logic', 'architecture'],
                ollama_tag='qwen2:72b'
            ),
            'qwen2-32b': ModelSpec(
                name='Qwen 2 32B',
                task_types=[TaskType.CODE_GENERATION, TaskType.CONFIGURATION, TaskType.LEARNING],
                min_tier=HardwareTier.MASTER,
                context_window=32768,
                strengths=['code-excellence', 'reasoning', 'planning'],
                ollama_tag='qwen2:32b'
            ),
            'qwen2-7b': ModelSpec(
                name='Qwen 2 7B',
                task_types=[TaskType.CODE_GENERATION, TaskType.CONFIGURATION],
                min_tier=HardwareTier.JOURNEYMAN,
                context_window=32768,
                strengths=['code-competent', 'efficient', 'precise'],
                ollama_tag='qwen2:7b'
            ),
            'qwen2-1.5b': ModelSpec(
                name='Qwen 2 1.5B',
                task_types=[TaskType.CODE_GENERATION, TaskType.CONFIGURATION],
                min_tier=HardwareTier.APPRENTICE,
                context_window=32768,
                strengths=['code-basic', 'fast', 'lightweight'],
                ollama_tag='qwen2:1.5b'
            ),
            
            # === REFLEX MODELS (Fast/Light) ===
            'gemma3-1b': ModelSpec(
                name='Gemma 3 1B',
                task_types=[TaskType.INTENT_CLASSIFICATION, TaskType.SEARCH],
                min_tier=HardwareTier.NOVICE,
                context_window=8192,
                strengths=['modern', 'ultra-fast', 'efficient'],
                ollama_tag='gemma3:1b'
            ),
            'gemma3-270m': ModelSpec(
                name='Gemma 3 270M',
                task_types=[TaskType.INTENT_CLASSIFICATION, TaskType.SEARCH],
                min_tier=HardwareTier.NOVICE,
                context_window=8192,
                strengths=['tiny', 'instant', 'minimal'],
                ollama_tag='gemma3:270m'
            ),
            'gemma-2b': ModelSpec(
                name='Gemma 2B',
                task_types=[TaskType.INTENT_CLASSIFICATION, TaskType.SEARCH],
                min_tier=HardwareTier.NOVICE,
                context_window=8192,
                strengths=['ultra-fast', 'efficient', 'instant'],
                ollama_tag='gemma:2b'
            ),
            'tinyllama': ModelSpec(
                name='TinyLlama',
                task_types=[TaskType.INTENT_CLASSIFICATION, TaskType.SEARCH],
                min_tier=HardwareTier.NOVICE,
                context_window=2048,
                strengths=['tiny', 'instant', 'minimal'],
                ollama_tag='tinyllama:latest'
            ),
            
            # === VISION MODELS (Multimodal) ===
            'llava-34b': ModelSpec(
                name='LLaVA 34B',
                task_types=[TaskType.VISION],
                min_tier=HardwareTier.SAGE,
                context_window=4096,
                strengths=['vision', 'multimodal', 'description'],
                ollama_tag='llava:34b'
            ),
            'llava-13b': ModelSpec(
                name='LLaVA 13B',
                task_types=[TaskType.VISION],
                min_tier=HardwareTier.MASTER,
                context_window=4096,
                strengths=['vision', 'balanced', 'accurate'],
                ollama_tag='llava:13b'
            ),
            'llava-7b': ModelSpec(
                name='LLaVA 7B',
                task_types=[TaskType.VISION],
                min_tier=HardwareTier.JOURNEYMAN,
                context_window=4096,
                strengths=['vision', 'efficient', 'capable'],
                ollama_tag='llava:7b'
            ),
            'bakllava': ModelSpec(
                name='BakLLaVA',
                task_types=[TaskType.VISION],
                min_tier=HardwareTier.APPRENTICE,
                context_window=2048,
                strengths=['vision', 'compact', 'basic'],
                ollama_tag='bakllava:latest'
            )
        }
    
    def select_model_for_task(self, 
                             task_type: TaskType,
                             context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Select the best model for a given task.
        
        This is where the conductor chooses which instrument plays.
        """
        # Check cache
        cache_key = f"{task_type.value}_{self.hardware_profile.tier.value}"
        if cache_key in self.selection_cache:
            model_tag = self.selection_cache[cache_key]
            self.logger.info(f"🎵 Using cached model for {task_type.value}: {model_tag}")
            return model_tag
        
        # Find compatible models
        compatible_models = []
        for model_id, spec in self.model_registry.items():
            if (spec.supports_task(task_type) and 
                self._tier_value(spec.min_tier) <= self._tier_value(self.hardware_profile.tier)):
                compatible_models.append((model_id, spec))
        
        if not compatible_models:
            self.logger.warning(f"No compatible model found for {task_type.value}")
            return self._get_fallback_model()
        
        # Sort by capability (prefer larger models if hardware allows)
        compatible_models.sort(key=lambda x: self._tier_value(x[1].min_tier), reverse=True)
        
        # Select the best model
        selected_id, selected_spec = compatible_models[0]
        
        # Cache the selection
        self.selection_cache[cache_key] = selected_spec.ollama_tag
        
        self.logger.info(f"🎼 Selected {selected_spec.name} for {task_type.value}")
        self.logger.info(f"   Strengths: {', '.join(selected_spec.strengths)}")
        
        return selected_spec.ollama_tag
    
    def get_model_for_poml(self, poml_metadata: Dict[str, Any]) -> Optional[str]:
        """
        Select model based on POML template metadata.
        
        This reads the 'musical score' to know which instrument to use.
        """
        # Extract task type from POML metadata
        task_type_str = poml_metadata.get('task_type', 'conversation')
        
        # Convert to TaskType enum
        try:
            task_type = TaskType(task_type_str)
        except ValueError:
            self.logger.warning(f"Unknown task type: {task_type_str}, defaulting to conversation")
            task_type = TaskType.CONVERSATION
        
        # Get additional context
        context = {
            'persona': poml_metadata.get('persona'),
            'complexity': poml_metadata.get('complexity', 'medium'),
            'requires_speed': poml_metadata.get('requires_speed', False)
        }
        
        # If speed is critical, prefer reflex models
        if context.get('requires_speed'):
            # Try to use a reflex model even for other tasks
            reflex_model = self.select_model_for_task(TaskType.INTENT_CLASSIFICATION)
            if reflex_model:
                self.logger.info("⚡ Using reflex model for speed")
                return reflex_model
        
        return self.select_model_for_task(task_type, context)
    
    def ensure_model_available(self, model_tag: str) -> bool:
        """
        Ensure a model is available in Ollama.
        
        This is like tuning the instrument before playing.
        """
        try:
            # Check if model exists
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and model_tag in result.stdout:
                self.logger.info(f"✅ Model {model_tag} is available")
                return True
            
            # Pull the model
            self.logger.info(f"📥 Pulling model {model_tag}...")
            result = subprocess.run(
                ['ollama', 'pull', model_tag],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes for download
            )
            
            if result.returncode == 0:
                self.logger.info(f"✅ Successfully pulled {model_tag}")
                return True
            else:
                self.logger.error(f"Failed to pull {model_tag}: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error ensuring model availability: {e}")
            return False
    
    def execute_with_model(self,
                          model_tag: str,
                          prompt: str,
                          temperature: float = 0.7) -> Optional[str]:
        """
        Execute a prompt with a specific model.
        
        This is where the selected instrument plays its part.
        """
        try:
            # Ensure model is available
            if not self.ensure_model_available(model_tag):
                return None
            
            # Execute via Ollama
            self.logger.info(f"🎵 Executing with {model_tag}")
            
            result = subprocess.run(
                ['ollama', 'run', model_tag, '--temperature', str(temperature)],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes max
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                self.logger.error(f"Execution failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Model execution timed out")
            return None
        except Exception as e:
            self.logger.error(f"Error executing model: {e}")
            return None
    
    def _tier_value(self, tier: HardwareTier) -> int:
        """Convert tier to numeric value for comparison"""
        tier_values = {
            HardwareTier.NOVICE: 1,
            HardwareTier.APPRENTICE: 2,
            HardwareTier.JOURNEYMAN: 3,
            HardwareTier.MASTER: 4,
            HardwareTier.SAGE: 5
        }
        return tier_values.get(tier, 1)
    
    def _get_fallback_model(self) -> str:
        """Get the ultimate fallback model"""
        return 'gemma:2b'  # Smallest, works everywhere
    
    def get_orchestra_status(self) -> Dict[str, Any]:
        """
        Get the status of the mental orchestra.
        
        Shows which minds are available for which tasks.
        """
        status = {
            'hardware_tier': self.hardware_profile.tier.value,
            'available_tasks': {},
            'model_assignments': {}
        }
        
        # Check what tasks we can handle
        for task_type in TaskType:
            model = self.select_model_for_task(task_type)
            if model:
                status['available_tasks'][task_type.value] = True
                status['model_assignments'][task_type.value] = model
            else:
                status['available_tasks'][task_type.value] = False
        
        return status


def test_model_orchestrator():
    """Test the model orchestrator"""
    print("🎼 Testing Model Orchestrator")
    print("=" * 60)
    
    # Get hardware profile
    profiler = HardwareProfiler()
    profile = profiler.get_profile()
    
    # Initialize orchestrator
    orchestrator = ModelOrchestrator(profile)
    
    # Test model selection for different tasks
    print("\n🎯 Model Selection for Tasks:")
    for task_type in TaskType:
        model = orchestrator.select_model_for_task(task_type)
        if model:
            print(f"   {task_type.value}: {model}")
        else:
            print(f"   {task_type.value}: No compatible model")
    
    # Get orchestra status
    status = orchestrator.get_orchestra_status()
    
    print(f"\n🎭 Orchestra Status for {status['hardware_tier'].upper()} tier:")
    print("   Available Tasks:")
    for task, available in status['available_tasks'].items():
        symbol = "✅" if available else "❌"
        print(f"      {task}: {symbol}")
    
    # Test POML-based selection
    print("\n📜 POML-based Selection:")
    poml_metadata = {
        'task_type': 'code_generation',
        'complexity': 'high',
        'persona': 'dr_sarah'
    }
    model = orchestrator.get_model_for_poml(poml_metadata)
    print(f"   Selected: {model}")
    
    print("\n✨ Model orchestration complete!")


if __name__ == "__main__":
    test_model_orchestrator()