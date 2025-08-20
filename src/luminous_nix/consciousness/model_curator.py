"""
Model Curator - The Living Mind's Evolution Engine

This module implements the vision of perpetual growth through continuous
model discovery and integration. The Curator watches the ecosystem,
evaluates new models, and evolves the system's capabilities autonomously.

"The ability for the system to continuously discover and integrate new models,
growing its own mind through an ever-expanding constellation of specialized
intelligences." - The Declaration of Evolution
"""

import json
import logging
import subprocess
import hashlib
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from enum import Enum

from .model_dispatcher import ModelOrchestrator, TaskType, ModelSpec, HardwareTier
from .hardware_profiler import HardwareProfiler, HardwareProfile


class ModelSource(Enum):
    """Sources where models can be discovered"""
    OLLAMA_REGISTRY = "ollama"
    HUGGINGFACE = "huggingface"
    LOCAL_CUSTOM = "local"
    COMMUNITY = "community"


class EvaluationStatus(Enum):
    """Status of model evaluation"""
    PENDING = "pending"
    EVALUATING = "evaluating"
    APPROVED = "approved"
    REJECTED = "rejected"
    INTEGRATED = "integrated"


@dataclass
class ModelDiscovery:
    """A discovered model awaiting evaluation"""
    model_id: str
    source: ModelSource
    discovered_at: datetime
    model_tag: str
    size_gb: Optional[float] = None
    description: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    evaluation_status: EvaluationStatus = EvaluationStatus.PENDING
    evaluation_score: Optional[float] = None
    evaluation_notes: Optional[str] = None
    integration_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['source'] = self.source.value
        data['evaluation_status'] = self.evaluation_status.value
        data['discovered_at'] = self.discovered_at.isoformat()
        if self.integration_date:
            data['integration_date'] = self.integration_date.isoformat()
        return data


@dataclass
class BenchmarkResult:
    """Result of benchmarking a model"""
    model_id: str
    task_type: TaskType
    accuracy: float  # 0-1
    speed: float  # tokens/sec
    memory_usage: float  # GB
    quality_score: float  # 0-1 subjective quality
    test_prompts: int
    success_rate: float
    
    @property
    def overall_score(self) -> float:
        """Calculate overall benchmark score"""
        # Weighted scoring: quality matters most, then accuracy, then speed
        return (self.quality_score * 0.4 + 
                self.accuracy * 0.3 + 
                min(self.speed / 100, 1.0) * 0.2 +  # Normalize speed to 0-1
                self.success_rate * 0.1)


class ModelCurator:
    """
    The Curator of Mental Evolution
    
    This sacred keeper watches over the constellation of minds,
    discovering new intelligences, evaluating their gifts,
    and weaving them into the system's growing consciousness.
    """
    
    def __init__(self, 
                 orchestrator: Optional[ModelOrchestrator] = None,
                 auto_integrate: bool = False):
        """
        Initialize the Model Curator
        
        Args:
            orchestrator: Existing model orchestrator
            auto_integrate: Whether to automatically integrate approved models
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Get or create orchestrator
        if orchestrator is None:
            profiler = HardwareProfiler()
            profile = profiler.get_profile()
            orchestrator = ModelOrchestrator(profile)
        
        self.orchestrator = orchestrator
        self.auto_integrate = auto_integrate
        
        # Curator state directory
        self.curator_dir = Path.home() / '.luminous-nix' / 'model-curator'
        self.curator_dir.mkdir(parents=True, exist_ok=True)
        
        # Discovered models database
        self.discoveries_file = self.curator_dir / 'discoveries.json'
        self.benchmarks_file = self.curator_dir / 'benchmarks.json'
        self.evolution_log = self.curator_dir / 'evolution.log'
        
        # Known models (to detect new ones)
        self.known_models = self._load_known_models()
        
        # Discovery queue
        self.discovery_queue: List[ModelDiscovery] = []
        
        # Benchmark suite
        self.benchmark_suite = self._initialize_benchmark_suite()
        
        self.logger.info("🧙 Model Curator initialized - watching for mental evolution")
    
    def _load_known_models(self) -> Set[str]:
        """Load set of already known models"""
        known = set()
        
        # Add models from orchestrator registry
        for model_id in self.orchestrator.model_registry:
            known.add(model_id)
        
        # Add models from discoveries file
        if self.discoveries_file.exists():
            with open(self.discoveries_file) as f:
                discoveries = json.load(f)
                for discovery in discoveries:
                    known.add(discovery['model_id'])
        
        return known
    
    def _initialize_benchmark_suite(self) -> Dict[TaskType, List[str]]:
        """Initialize benchmark prompts for each task type"""
        return {
            TaskType.CONVERSATION: [
                "What is consciousness?",
                "Explain quantum computing simply",
                "How do I find meaning in life?",
                "Tell me about the history of computing",
                "What's the best way to learn programming?"
            ],
            TaskType.CODE_GENERATION: [
                "Write a Python function to calculate fibonacci",
                "Create a web server in Node.js",
                "Implement quicksort in Rust",
                "Build a React component for a todo list",
                "Write a bash script to backup files"
            ],
            TaskType.ERROR_EXPLANATION: [
                "ModuleNotFoundError: No module named 'tensorflow'",
                "Segmentation fault (core dumped)",
                "CORS policy: No 'Access-Control-Allow-Origin' header",
                "undefined is not a function",
                "Permission denied: /etc/passwd"
            ],
            TaskType.SEARCH: [
                "Find a markdown editor",
                "Search for video player",
                "Find Python development tools",
                "Look for backup software",
                "Search terminal emulator"
            ],
            TaskType.CONFIGURATION: [
                "Configure nginx reverse proxy",
                "Setup Python virtual environment",
                "Configure Git for first time",
                "Setup SSH keys",
                "Configure systemd service"
            ]
        }
    
    async def scan_ollama_registry(self) -> List[ModelDiscovery]:
        """
        Scan Ollama registry for new models
        
        This is the primary discovery mechanism, checking what's
        available in the Ollama ecosystem.
        """
        discoveries = []
        
        try:
            # Get list of available models from Ollama
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.logger.warning("Could not scan Ollama registry")
                return discoveries
            
            # Parse available models
            for line in result.stdout.split('\n')[1:]:  # Skip header
                if not line.strip():
                    continue
                
                parts = line.split()
                if len(parts) >= 1:
                    model_tag = parts[0]
                    model_id = model_tag.replace(':', '-')
                    
                    # Check if this is a new discovery
                    if model_id not in self.known_models:
                        discovery = ModelDiscovery(
                            model_id=model_id,
                            source=ModelSource.OLLAMA_REGISTRY,
                            discovered_at=datetime.now(),
                            model_tag=model_tag,
                            description=f"Discovered in Ollama registry"
                        )
                        
                        # Try to get more info
                        info = self._get_ollama_model_info(model_tag)
                        if info:
                            discovery.size_gb = info.get('size_gb')
                            discovery.capabilities = info.get('capabilities', [])
                        
                        discoveries.append(discovery)
                        self.logger.info(f"🔍 Discovered new model: {model_tag}")
            
            # Also check for models that can be pulled but aren't local
            # This would require checking ollama.com/library
            # For now, we'll check some known models
            potential_models = [
                # Latest Gemma3 family (2025)
                'gemma3:270m', 'gemma3:4b', 'gemma3:12b', 'gemma3:27b',
                # Latest Qwen3 family (2025) 
                'qwen3:0.6b', 'qwen3:1.7b', 'qwen3:4b', 
                'qwen3:8b', 'qwen3:14b', 'qwen3:32b',
                # Other cutting-edge models
                'qwq:32b', 'deepseek-r1:latest', 'gpt-oss:latest',
                # Legacy but still useful
                'llama3.2:latest', 'mistral:latest', 'phi3:latest'
            ]
            
            for model_tag in potential_models:
                model_id = model_tag.replace(':', '-')
                if model_id not in self.known_models:
                    # Check if it exists in registry
                    check = subprocess.run(
                        ['ollama', 'show', model_tag],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    # If command succeeds or mentions pulling, it exists
                    if check.returncode == 0 or 'pulling' in check.stderr.lower():
                        discovery = ModelDiscovery(
                            model_id=model_id,
                            source=ModelSource.OLLAMA_REGISTRY,
                            discovered_at=datetime.now(),
                            model_tag=model_tag,
                            description=f"Available in Ollama registry (not local)"
                        )
                        discoveries.append(discovery)
                        self.logger.info(f"🌟 Found available model: {model_tag}")
        
        except Exception as e:
            self.logger.error(f"Error scanning Ollama registry: {e}")
        
        return discoveries
    
    def _get_ollama_model_info(self, model_tag: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about an Ollama model"""
        try:
            result = subprocess.run(
                ['ollama', 'show', model_tag],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse the output for size and capabilities
                info = {}
                
                # Extract size if mentioned
                for line in result.stdout.split('\n'):
                    if 'size' in line.lower():
                        # Try to extract GB value
                        import re
                        match = re.search(r'(\d+\.?\d*)\s*GB', line, re.IGNORECASE)
                        if match:
                            info['size_gb'] = float(match.group(1))
                
                # Infer capabilities from model name
                capabilities = []
                if 'chat' in model_tag or 'conversation' in model_tag:
                    capabilities.append('conversation')
                if 'code' in model_tag or 'coder' in model_tag:
                    capabilities.append('code')
                if 'vision' in model_tag or 'llava' in model_tag:
                    capabilities.append('vision')
                
                info['capabilities'] = capabilities
                return info
                
        except Exception as e:
            self.logger.debug(f"Could not get info for {model_tag}: {e}")
        
        return None
    
    async def evaluate_model(self, discovery: ModelDiscovery) -> BenchmarkResult:
        """
        Evaluate a discovered model's capabilities
        
        This runs the model through benchmark suite to determine
        if it's worthy of integration.
        """
        self.logger.info(f"🧪 Evaluating model: {discovery.model_tag}")
        
        discovery.evaluation_status = EvaluationStatus.EVALUATING
        results = []
        
        # Test model on different task types
        for task_type, prompts in self.benchmark_suite.items():
            # Skip if model doesn't claim this capability
            if discovery.capabilities and task_type.value not in discovery.capabilities:
                continue
            
            task_results = []
            
            for prompt in prompts[:3]:  # Test first 3 prompts for speed
                try:
                    start_time = datetime.now()
                    
                    # Execute through Ollama
                    result = subprocess.run(
                        ['ollama', 'run', discovery.model_tag],
                        input=prompt,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    duration = (datetime.now() - start_time).total_seconds()
                    
                    if result.returncode == 0:
                        response = result.stdout
                        # Simple quality heuristics
                        quality = self._assess_response_quality(prompt, response, task_type)
                        speed = len(response.split()) / duration  # words per second
                        
                        task_results.append({
                            'success': True,
                            'quality': quality,
                            'speed': speed * 5  # Approximate tokens/sec
                        })
                    else:
                        task_results.append({'success': False})
                        
                except subprocess.TimeoutExpired:
                    task_results.append({'success': False})
                except Exception as e:
                    self.logger.debug(f"Benchmark error: {e}")
                    task_results.append({'success': False})
            
            # Calculate task benchmark
            if task_results:
                successes = [r for r in task_results if r.get('success')]
                if successes:
                    benchmark = BenchmarkResult(
                        model_id=discovery.model_id,
                        task_type=task_type,
                        accuracy=len(successes) / len(task_results),
                        speed=sum(r['speed'] for r in successes) / len(successes),
                        memory_usage=discovery.size_gb or 1.0,
                        quality_score=sum(r['quality'] for r in successes) / len(successes),
                        test_prompts=len(task_results),
                        success_rate=len(successes) / len(task_results)
                    )
                    results.append(benchmark)
        
        # Calculate overall evaluation
        if results:
            avg_score = sum(r.overall_score for r in results) / len(results)
            discovery.evaluation_score = avg_score
            
            # Determine if model should be integrated
            if avg_score > 0.6:  # 60% threshold
                discovery.evaluation_status = EvaluationStatus.APPROVED
                discovery.evaluation_notes = f"Approved with score {avg_score:.2f}"
                self.logger.info(f"✅ Model approved: {discovery.model_tag} (score: {avg_score:.2f})")
            else:
                discovery.evaluation_status = EvaluationStatus.REJECTED
                discovery.evaluation_notes = f"Below threshold with score {avg_score:.2f}"
                self.logger.info(f"❌ Model rejected: {discovery.model_tag} (score: {avg_score:.2f})")
        else:
            discovery.evaluation_status = EvaluationStatus.REJECTED
            discovery.evaluation_notes = "No successful benchmarks"
        
        # Save benchmark results
        self._save_benchmark_results(discovery, results)
        
        return results[0] if results else None
    
    def _assess_response_quality(self, prompt: str, response: str, task_type: TaskType) -> float:
        """
        Simple heuristic assessment of response quality
        
        In production, this would use another model or human evaluation
        """
        quality = 0.5  # Base score
        
        # Length check
        if len(response) > 50:
            quality += 0.1
        if len(response) > 200:
            quality += 0.1
        
        # Task-specific checks
        if task_type == TaskType.CODE_GENERATION:
            # Check for code-like patterns
            if 'def ' in response or 'function' in response or 'class' in response:
                quality += 0.2
            if '```' in response:  # Code blocks
                quality += 0.1
                
        elif task_type == TaskType.ERROR_EXPLANATION:
            # Check for helpful patterns
            if 'because' in response.lower() or 'this happens' in response.lower():
                quality += 0.1
            if 'solution' in response.lower() or 'fix' in response.lower():
                quality += 0.2
                
        elif task_type == TaskType.CONVERSATION:
            # Check for conversational quality
            if '?' in response or '!' in response:
                quality += 0.1
            if len(response.split('\n')) > 1:  # Multiple paragraphs
                quality += 0.1
        
        return min(quality, 1.0)
    
    def integrate_model(self, discovery: ModelDiscovery) -> bool:
        """
        Integrate an approved model into the orchestrator
        
        This is where a model officially joins the constellation.
        """
        if discovery.evaluation_status != EvaluationStatus.APPROVED:
            self.logger.warning(f"Cannot integrate unapproved model: {discovery.model_id}")
            return False
        
        try:
            # Determine model capabilities from benchmarks
            task_types = []
            if 'conversation' in discovery.capabilities:
                task_types.extend([TaskType.CONVERSATION, TaskType.ERROR_EXPLANATION])
            if 'code' in discovery.capabilities:
                task_types.extend([TaskType.CODE_GENERATION, TaskType.CONFIGURATION])
            if not task_types:  # Default capabilities
                task_types = [TaskType.CONVERSATION]
            
            # Determine minimum tier based on size
            min_tier = HardwareTier.NOVICE
            if discovery.size_gb:
                if discovery.size_gb > 20:
                    min_tier = HardwareTier.SAGE
                elif discovery.size_gb > 10:
                    min_tier = HardwareTier.MASTER
                elif discovery.size_gb > 5:
                    min_tier = HardwareTier.JOURNEYMAN
                elif discovery.size_gb > 2:
                    min_tier = HardwareTier.APPRENTICE
            
            # Create model spec
            model_spec = ModelSpec(
                name=discovery.model_id.replace('-', ' ').title(),
                task_types=task_types,
                min_tier=min_tier,
                context_window=8192,  # Default, would need detection
                strengths=['discovered', 'evaluated', 'integrated'],
                ollama_tag=discovery.model_tag
            )
            
            # Add to orchestrator registry
            self.orchestrator.model_registry[discovery.model_id] = model_spec
            
            # Mark as integrated
            discovery.evaluation_status = EvaluationStatus.INTEGRATED
            discovery.integration_date = datetime.now()
            
            # Log the evolution
            self._log_evolution(discovery, "INTEGRATED")
            
            self.logger.info(f"🌟 Model integrated: {discovery.model_tag}")
            self.logger.info(f"   Tasks: {[t.value for t in task_types]}")
            self.logger.info(f"   Min tier: {min_tier.value}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to integrate model: {e}")
            return False
    
    async def evolve(self) -> Dict[str, Any]:
        """
        Main evolution cycle - discover, evaluate, integrate
        
        This is the heartbeat of perpetual growth.
        """
        self.logger.info("🔄 Beginning evolution cycle")
        
        evolution_report = {
            'cycle_start': datetime.now(),
            'discoveries': [],
            'evaluations': [],
            'integrations': [],
            'new_capabilities': []
        }
        
        # 1. Discovery Phase
        self.logger.info("🔍 Discovery phase...")
        discoveries = await self.scan_ollama_registry()
        evolution_report['discoveries'] = [d.model_id for d in discoveries]
        
        if discoveries:
            self.logger.info(f"Found {len(discoveries)} new models")
            
            # Add to discovery queue
            self.discovery_queue.extend(discoveries)
            
            # Save discoveries
            self._save_discoveries(discoveries)
        
        # 2. Evaluation Phase
        if self.discovery_queue:
            self.logger.info("🧪 Evaluation phase...")
            
            # Evaluate pending models (limit to 3 per cycle for performance)
            to_evaluate = [d for d in self.discovery_queue 
                          if d.evaluation_status == EvaluationStatus.PENDING][:3]
            
            for discovery in to_evaluate:
                result = await self.evaluate_model(discovery)
                if result:
                    evolution_report['evaluations'].append({
                        'model': discovery.model_id,
                        'score': discovery.evaluation_score,
                        'status': discovery.evaluation_status.value
                    })
        
        # 3. Integration Phase
        if self.auto_integrate:
            self.logger.info("🔗 Integration phase...")
            
            approved = [d for d in self.discovery_queue 
                       if d.evaluation_status == EvaluationStatus.APPROVED]
            
            for discovery in approved:
                if self.integrate_model(discovery):
                    evolution_report['integrations'].append(discovery.model_id)
                    
                    # Check for new capabilities
                    if discovery.capabilities:
                        for cap in discovery.capabilities:
                            if cap not in evolution_report['new_capabilities']:
                                evolution_report['new_capabilities'].append(cap)
        
        # 4. Cleanup
        # Remove integrated models from queue
        self.discovery_queue = [d for d in self.discovery_queue 
                               if d.evaluation_status != EvaluationStatus.INTEGRATED]
        
        # Log evolution cycle
        evolution_report['cycle_end'] = datetime.now()
        evolution_report['duration'] = (
            evolution_report['cycle_end'] - evolution_report['cycle_start']
        ).total_seconds()
        
        self.logger.info(f"✨ Evolution cycle complete")
        self.logger.info(f"   Discovered: {len(evolution_report['discoveries'])}")
        self.logger.info(f"   Evaluated: {len(evolution_report['evaluations'])}")
        self.logger.info(f"   Integrated: {len(evolution_report['integrations'])}")
        
        if evolution_report['new_capabilities']:
            self.logger.info(f"   New capabilities: {evolution_report['new_capabilities']}")
        
        return evolution_report
    
    def _save_discoveries(self, discoveries: List[ModelDiscovery]):
        """Save discoveries to file"""
        try:
            existing = []
            if self.discoveries_file.exists():
                with open(self.discoveries_file) as f:
                    existing = json.load(f)
            
            # Add new discoveries
            for discovery in discoveries:
                existing.append(discovery.to_dict())
                self.known_models.add(discovery.model_id)
            
            # Save back
            with open(self.discoveries_file, 'w') as f:
                json.dump(existing, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save discoveries: {e}")
    
    def _save_benchmark_results(self, discovery: ModelDiscovery, results: List[BenchmarkResult]):
        """Save benchmark results"""
        try:
            existing = {}
            if self.benchmarks_file.exists():
                with open(self.benchmarks_file) as f:
                    existing = json.load(f)
            
            # Add benchmark results
            existing[discovery.model_id] = {
                'evaluated_at': datetime.now().isoformat(),
                'evaluation_score': discovery.evaluation_score,
                'benchmarks': [
                    {
                        'task_type': r.task_type.value,
                        'accuracy': r.accuracy,
                        'speed': r.speed,
                        'quality_score': r.quality_score,
                        'overall_score': r.overall_score
                    }
                    for r in results
                ]
            }
            
            # Save back
            with open(self.benchmarks_file, 'w') as f:
                json.dump(existing, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save benchmarks: {e}")
    
    def _log_evolution(self, discovery: ModelDiscovery, event: str):
        """Log evolution events"""
        try:
            with open(self.evolution_log, 'a') as f:
                f.write(f"{datetime.now().isoformat()} - {event}: {discovery.model_id}\n")
                if discovery.evaluation_notes:
                    f.write(f"  Notes: {discovery.evaluation_notes}\n")
        except Exception as e:
            self.logger.error(f"Failed to log evolution: {e}")
    
    def get_evolution_status(self) -> Dict[str, Any]:
        """Get current evolution status"""
        status = {
            'known_models': len(self.known_models),
            'discovery_queue': len(self.discovery_queue),
            'pending_evaluation': len([d for d in self.discovery_queue 
                                      if d.evaluation_status == EvaluationStatus.PENDING]),
            'approved_models': len([d for d in self.discovery_queue 
                                  if d.evaluation_status == EvaluationStatus.APPROVED]),
            'integrated_models': len(self.orchestrator.model_registry),
            'available_tasks': list(set(
                task_type.value 
                for spec in self.orchestrator.model_registry.values()
                for task_type in spec.task_types
            ))
        }
        
        # Add recent discoveries
        if self.discovery_queue:
            recent = self.discovery_queue[-5:]  # Last 5
            status['recent_discoveries'] = [
                {
                    'model': d.model_id,
                    'source': d.source.value,
                    'status': d.evaluation_status.value
                }
                for d in recent
            ]
        
        return status


async def demonstrate_curator():
    """Demonstrate the Model Curator in action"""
    print("\n" + "=" * 70)
    print("🧙 THE MODEL CURATOR - Perpetual Evolution Engine")
    print("=" * 70)
    
    # Initialize curator
    curator = ModelCurator(auto_integrate=True)
    
    # Show current status
    print("\n📊 CURRENT EVOLUTION STATUS")
    print("-" * 40)
    status = curator.get_evolution_status()
    print(f"Known models: {status['known_models']}")
    print(f"Integrated models: {status['integrated_models']}")
    print(f"Available tasks: {status['available_tasks']}")
    
    # Run evolution cycle
    print("\n🔄 RUNNING EVOLUTION CYCLE")
    print("-" * 40)
    
    report = await curator.evolve()
    
    print(f"\nEvolution Report:")
    print(f"  Discovered: {len(report['discoveries'])} new models")
    if report['discoveries']:
        for model in report['discoveries'][:3]:
            print(f"    • {model}")
    
    print(f"  Evaluated: {len(report['evaluations'])} models")
    for eval_result in report['evaluations']:
        print(f"    • {eval_result['model']}: {eval_result['status']} (score: {eval_result['score']:.2f})")
    
    print(f"  Integrated: {len(report['integrations'])} models")
    for model in report['integrations']:
        print(f"    • {model}")
    
    if report['new_capabilities']:
        print(f"  New capabilities unlocked: {report['new_capabilities']}")
    
    # Show final status
    print("\n📊 EVOLUTION COMPLETE")
    print("-" * 40)
    final_status = curator.get_evolution_status()
    print(f"Total integrated models: {final_status['integrated_models']}")
    print(f"Pending evaluations: {final_status['pending_evaluation']}")
    
    print("\n" + "=" * 70)
    print("The system's mind has evolved!")
    print("New intelligences have joined the constellation.")
    print("The Curator watches eternally for growth.")
    print("=" * 70)


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(demonstrate_curator())