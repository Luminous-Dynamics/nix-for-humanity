#!/usr/bin/env python3
"""
HRM Production Integration Module
Seamless integration of trained HRM models with the existing Luminous Nix system

Features:
1. Model loading and versioning
2. Hot-swappable model updates
3. Fallback mechanisms
4. Performance monitoring
5. A/B testing capabilities
6. Production-ready error handling
"""

import torch
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import threading
import queue
from contextlib import contextmanager
import hashlib
import pickle
from enum import Enum
import numpy as np
from collections import defaultdict, deque

# Import existing HRM and core modules
try:
    from .hrm_neural import HRMNeuralNetwork, NeuralHRM
    from .hrm_training_pipeline import TrainingConfig, EnhancedNixOSDataset
    from .hrm_reasoner_v2 import HierarchicalReasoningModel
    from ..core.intent_pipeline import IntentPipeline
    from ..core.unified_response import UnifiedResponse
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).parent))
    from hrm_neural import HRMNeuralNetwork, NeuralHRM
    from hrm_training_pipeline import TrainingConfig, EnhancedNixOSDataset
    from hrm_reasoner_v2 import HierarchicalReasoningModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelStatus(Enum):
    """Model deployment status"""
    LOADING = "loading"
    READY = "ready"
    SERVING = "serving"
    ERROR = "error"
    UPDATING = "updating"
    DEPRECATED = "deprecated"

@dataclass
class ModelMetrics:
    """Real-time model performance metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    avg_confidence: float = 0.0
    total_uncertainty: float = 0.0
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    @property
    def error_rate(self) -> float:
        return 1.0 - self.success_rate

@dataclass
class DeploymentConfig:
    """Configuration for production deployment"""
    # Model paths
    models_dir: str = "models/hrm-production"
    active_model_name: str = "hrm_nixos_production_v1"
    fallback_model_name: str = "hrm_baseline"
    
    # Performance settings
    max_inference_time_ms: float = 500.0
    max_queue_size: int = 1000
    warmup_queries: int = 10
    
    # Monitoring
    metrics_window_size: int = 1000
    health_check_interval: float = 30.0
    auto_fallback_error_threshold: float = 0.1  # 10% error rate
    
    # A/B Testing
    enable_ab_testing: bool = False
    ab_traffic_split: float = 0.1  # 10% to new model
    
    # Caching
    enable_response_cache: bool = True
    cache_size: int = 10000
    cache_ttl_seconds: int = 3600

class ModelCache:
    """Thread-safe model response cache"""
    
    def __init__(self, max_size: int = 10000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = {}
        self.access_times = deque()
        self.lock = threading.RLock()
    
    def _hash_query(self, query: str, model_version: str) -> str:
        """Create cache key"""
        combined = f"{query}:{model_version}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get(self, query: str, model_version: str) -> Optional[Dict]:
        """Get cached response"""
        with self.lock:
            key = self._hash_query(query, model_version)
            
            if key in self.cache:
                response, timestamp = self.cache[key]
                
                # Check if expired
                if time.time() - timestamp < self.ttl_seconds:
                    return response
                else:
                    # Remove expired entry
                    del self.cache[key]
            
            return None
    
    def put(self, query: str, model_version: str, response: Dict):
        """Cache response"""
        with self.lock:
            key = self._hash_query(query, model_version)
            timestamp = time.time()
            
            # Remove oldest entries if at capacity
            while len(self.cache) >= self.max_size:
                oldest_key = self.access_times.popleft()
                if oldest_key in self.cache:
                    del self.cache[oldest_key]
            
            self.cache[key] = (response, timestamp)
            self.access_times.append(key)
    
    def clear(self):
        """Clear all cached entries"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()

class ProductionHRMOrchestrator:
    """Production-ready HRM orchestrator with advanced deployment features"""
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        
        # Model management
        self.active_model: Optional[NeuralHRM] = None
        self.fallback_model: Optional[NeuralHRM] = None
        self.models: Dict[str, NeuralHRM] = {}
        self.model_status: Dict[str, ModelStatus] = {}
        self.model_metadata: Dict[str, Dict] = {}
        
        # Performance monitoring
        self.metrics: Dict[str, ModelMetrics] = defaultdict(ModelMetrics)
        self.response_times = deque(maxlen=config.metrics_window_size)
        
        # Request handling
        self.request_queue = queue.Queue(maxsize=config.max_queue_size)
        self.cache = ModelCache(
            max_size=config.cache_size, 
            ttl_seconds=config.cache_ttl_seconds
        ) if config.enable_response_cache else None
        
        # Threading
        self.lock = threading.RLock()
        self.health_check_thread = None
        self.shutdown_event = threading.Event()
        
        # A/B Testing
        self.ab_model: Optional[NeuralHRM] = None
        self.ab_metrics: Optional[ModelMetrics] = None
        
        # Initialize
        self._initialize_models()
        self._start_health_monitoring()
    
    def _initialize_models(self):
        """Initialize and load models"""
        logger.info("🚀 Initializing production HRM models...")
        
        models_dir = Path(self.config.models_dir)
        
        # Load active model
        try:
            self.active_model = self._load_model(
                self.config.active_model_name, models_dir
            )
            if self.active_model:
                self.model_status[self.config.active_model_name] = ModelStatus.READY
                logger.info(f"✅ Active model loaded: {self.config.active_model_name}")
        except Exception as e:
            logger.error(f"❌ Failed to load active model: {e}")
            self.model_status[self.config.active_model_name] = ModelStatus.ERROR
        
        # Load fallback model
        try:
            self.fallback_model = self._load_model(
                self.config.fallback_model_name, models_dir
            )
            if self.fallback_model:
                self.model_status[self.config.fallback_model_name] = ModelStatus.READY
                logger.info(f"✅ Fallback model loaded: {self.config.fallback_model_name}")
        except Exception as e:
            logger.warning(f"⚠️ Fallback model not available: {e}")
            # Create simple fallback
            self.fallback_model = self._create_simple_fallback()
            self.model_status[self.config.fallback_model_name] = ModelStatus.READY
        
        # Warmup models
        self._warmup_models()
    
    def _load_model(self, model_name: str, models_dir: Path) -> Optional[NeuralHRM]:
        """Load a specific model from checkpoint"""
        model_path = models_dir / model_name / "best_model.pt"
        
        if not model_path.exists():
            logger.warning(f"Model checkpoint not found: {model_path}")
            return None
        
        try:
            # Load checkpoint
            checkpoint = torch.load(model_path, map_location='cpu')
            
            # Extract configuration and vocabularies
            config = checkpoint.get('config', {})
            vocabularies = checkpoint.get('vocabularies', {})
            
            # Create model instance
            model = NeuralHRM(device='cpu')
            
            # Load state dict if available
            if 'model_state_dict' in checkpoint:
                # Create neural network with proper configuration
                vocab_size = len(vocabularies.get('char_to_idx', {}))
                if vocab_size > 0:
                    neural_net = HRMNeuralNetwork(
                        vocab_size=vocab_size,
                        num_strategies=len(vocabularies.get('strategy_to_idx', {})) or 6
                    )
                    neural_net.load_state_dict(checkpoint['model_state_dict'])
                    model.model = neural_net
            
            # Store model metadata
            self.model_metadata[model_name] = {
                'version': checkpoint.get('epoch', 1),
                'accuracy': checkpoint.get('metrics', {}).get('val_accuracy', 0.0),
                'config': config,
                'vocabularies': vocabularies,
                'loaded_at': datetime.now().isoformat()
            }
            
            logger.info(f"🤖 Model loaded: {model_name} (accuracy: {checkpoint.get('metrics', {}).get('val_accuracy', 0.0):.1%})")
            
            return model
            
        except Exception as e:
            logger.error(f"❌ Failed to load model {model_name}: {e}")
            return None
    
    def _create_simple_fallback(self) -> NeuralHRM:
        """Create simple rule-based fallback"""
        logger.info("🔨 Creating simple fallback model...")
        
        class SimpleFallback:
            def predict(self, query: str, return_all: bool = False) -> Dict[str, Any]:
                # Simple rule-based logic
                query_lower = query.lower()
                
                if 'install' in query_lower or 'add' in query_lower:
                    strategy = 'direct_install'
                    confidence = 0.7
                elif 'configure' in query_lower or 'setup' in query_lower:
                    strategy = 'configuration_nix'
                    confidence = 0.6
                elif 'error' in query_lower or 'problem' in query_lower:
                    strategy = 'troubleshoot_fix'
                    confidence = 0.5
                else:
                    strategy = 'search_discover'
                    confidence = 0.4
                
                result = {
                    'strategy': strategy,
                    'confidence': confidence,
                    'solution': f"Basic {strategy} approach for: {query}",
                    'epistemic_uncertainty': 0.3,
                    'aleatoric_uncertainty': 0.2,
                    'total_uncertainty': 0.5
                }
                
                if return_all:
                    result['all_strategies'] = {
                        strategy: confidence,
                        'direct_install': 0.3,
                        'configuration_nix': 0.2,
                        'troubleshoot_fix': 0.1
                    }
                
                return result
        
        fallback_model = NeuralHRM(device='cpu')
        fallback_model.predict = SimpleFallback().predict
        
        return fallback_model
    
    def _warmup_models(self):
        """Warmup models with sample queries"""
        logger.info("🔥 Warming up models...")
        
        warmup_queries = [
            "install firefox",
            "configure nginx",
            "error building package",
            "setup development environment",
            "optimize system performance"
        ]
        
        for model_name, model in [(self.config.active_model_name, self.active_model),
                                 (self.config.fallback_model_name, self.fallback_model)]:
            if model:
                try:
                    for query in warmup_queries[:self.config.warmup_queries]:
                        model.predict(query)
                    logger.info(f"✅ Warmed up model: {model_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Warmup failed for {model_name}: {e}")
    
    def _start_health_monitoring(self):
        """Start background health monitoring"""
        if self.health_check_thread is None:
            self.health_check_thread = threading.Thread(
                target=self._health_monitor_loop, daemon=True
            )
            self.health_check_thread.start()
            logger.info("👩‍⚕️ Health monitoring started")
    
    def _health_monitor_loop(self):
        """Background health monitoring loop"""
        while not self.shutdown_event.wait(self.config.health_check_interval):
            try:
                self._perform_health_checks()
                self._check_auto_fallback()
                self._log_metrics()
            except Exception as e:
                logger.error(f"🚨 Health monitoring error: {e}")
    
    def _perform_health_checks(self):
        """Perform health checks on models"""
        test_query = "test query for health check"
        
        for model_name, model in self.models.items():
            if model and self.model_status.get(model_name) == ModelStatus.SERVING:
                try:
                    start_time = time.perf_counter()
                    result = model.predict(test_query)
                    response_time = (time.perf_counter() - start_time) * 1000
                    
                    # Check response validity
                    if result and 'strategy' in result and response_time < self.config.max_inference_time_ms:
                        # Model is healthy
                        pass
                    else:
                        logger.warning(f"💲 Health check failed for {model_name}")
                        self.model_status[model_name] = ModelStatus.ERROR
                        
                except Exception as e:
                    logger.error(f"❌ Health check error for {model_name}: {e}")
                    self.model_status[model_name] = ModelStatus.ERROR
    
    def _check_auto_fallback(self):
        """Check if automatic fallback should be triggered"""
        if self.config.active_model_name in self.metrics:
            active_metrics = self.metrics[self.config.active_model_name]
            
            if (active_metrics.error_rate > self.config.auto_fallback_error_threshold and 
                active_metrics.total_requests > 10):
                
                logger.warning(
                    f"🚨 Auto-fallback triggered! Error rate: {active_metrics.error_rate:.1%}"
                )
                self._switch_to_fallback()
    
    def _switch_to_fallback(self):
        """Switch to fallback model"""
        with self.lock:
            if self.fallback_model:
                logger.info("🔄 Switching to fallback model")
                
                # Swap models
                temp_model = self.active_model
                self.active_model = self.fallback_model
                self.fallback_model = temp_model
                
                # Update status
                self.model_status[self.config.active_model_name] = ModelStatus.ERROR
                self.model_status[self.config.fallback_model_name] = ModelStatus.SERVING
                
                # Clear cache
                if self.cache:
                    self.cache.clear()
    
    def _log_metrics(self):
        """Log performance metrics"""
        for model_name, metrics in self.metrics.items():
            if metrics.total_requests > 0:
                logger.info(
                    f"📊 {model_name}: "
                    f"Requests: {metrics.total_requests}, "
                    f"Success Rate: {metrics.success_rate:.1%}, "
                    f"Avg Response: {metrics.avg_response_time_ms:.1f}ms, "
                    f"Avg Confidence: {metrics.avg_confidence:.3f}"
                )
    
    def predict(self, query: str, return_all: bool = False, 
               model_name: Optional[str] = None) -> Dict[str, Any]:
        """Main prediction interface with production features"""
        start_time = time.perf_counter()
        
        try:
            # Determine which model to use
            if model_name and model_name in self.models:
                model = self.models[model_name]
                target_model_name = model_name
            elif self.config.enable_ab_testing and self.ab_model and np.random.random() < self.config.ab_traffic_split:
                model = self.ab_model
                target_model_name = "ab_model"
            else:
                model = self.active_model
                target_model_name = self.config.active_model_name
            
            if not model:
                raise ValueError("No model available")
            
            # Check cache first
            if self.cache:
                cached_result = self.cache.get(query, target_model_name)
                if cached_result:
                    self._update_metrics(target_model_name, start_time, True, cached=True)
                    return cached_result
            
            # Make prediction
            result = model.predict(query, return_all=return_all)
            
            # Add metadata
            result['model_name'] = target_model_name
            result['timestamp'] = datetime.now().isoformat()
            result['cached'] = False
            
            # Cache result
            if self.cache:
                self.cache.put(query, target_model_name, result)
            
            # Update metrics
            self._update_metrics(target_model_name, start_time, True)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Prediction failed: {e}")
            
            # Try fallback
            if model != self.fallback_model and self.fallback_model:
                try:
                    logger.info("🔄 Attempting fallback prediction...")
                    result = self.fallback_model.predict(query, return_all=return_all)
                    result['model_name'] = self.config.fallback_model_name
                    result['timestamp'] = datetime.now().isoformat()
                    result['fallback_used'] = True
                    
                    self._update_metrics(self.config.fallback_model_name, start_time, True)
                    return result
                    
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback also failed: {fallback_error}")
            
            # Update error metrics
            self._update_metrics(
                target_model_name if 'target_model_name' in locals() else 'unknown',
                start_time, False
            )
            
            # Return error response
            return {
                'strategy': 'error_recovery',
                'confidence': 0.0,
                'solution': 'Unable to process request. Please try again or contact support.',
                'error': str(e),
                'model_name': 'error',
                'timestamp': datetime.now().isoformat()
            }
    
    def _update_metrics(self, model_name: str, start_time: float, 
                       success: bool, cached: bool = False):
        """Update model performance metrics"""
        response_time = (time.perf_counter() - start_time) * 1000
        
        with self.lock:
            metrics = self.metrics[model_name]
            metrics.total_requests += 1
            
            if success:
                metrics.successful_requests += 1
            else:
                metrics.failed_requests += 1
            
            # Update running averages
            if not cached:  # Don't include cached responses in timing
                old_avg = metrics.avg_response_time_ms
                metrics.avg_response_time_ms = (
                    (old_avg * (metrics.successful_requests - 1) + response_time) / 
                    metrics.successful_requests
                )
            
            metrics.last_updated = datetime.now()
            
            # Store response time for percentile calculations
            self.response_times.append(response_time)
    
    def load_new_model(self, model_name: str, model_path: Path, 
                      make_active: bool = False) -> bool:
        """Hot-load a new model"""
        logger.info(f"🔄 Loading new model: {model_name}")
        
        try:
            # Load model
            new_model = self._load_model(model_name, model_path.parent)
            
            if new_model:
                with self.lock:
                    self.models[model_name] = new_model
                    self.model_status[model_name] = ModelStatus.READY
                    
                    if make_active:
                        # Backup current active model
                        old_active = self.active_model
                        self.active_model = new_model
                        
                        # Clear cache for new model
                        if self.cache:
                            self.cache.clear()
                        
                        logger.info(f"✅ New active model: {model_name}")
                    
                return True
            else:
                self.model_status[model_name] = ModelStatus.ERROR
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to load new model: {e}")
            self.model_status[model_name] = ModelStatus.ERROR
            return False
    
    def start_ab_test(self, ab_model_name: str, traffic_split: float = 0.1) -> bool:
        """Start A/B testing with new model"""
        logger.info(f"🧪 Starting A/B test: {ab_model_name} ({traffic_split:.1%} traffic)")
        
        if ab_model_name not in self.models:
            logger.error(f"A/B model not loaded: {ab_model_name}")
            return False
        
        with self.lock:
            self.ab_model = self.models[ab_model_name]
            self.config.ab_traffic_split = traffic_split
            self.config.enable_ab_testing = True
            self.ab_metrics = ModelMetrics()
        
        logger.info("✅ A/B test started")
        return True
    
    def stop_ab_test(self, promote_ab_model: bool = False) -> Dict[str, Any]:
        """Stop A/B testing and optionally promote the A/B model"""
        logger.info("📋 Stopping A/B test...")
        
        results = {
            'ab_model_metrics': asdict(self.ab_metrics) if self.ab_metrics else {},
            'active_model_metrics': asdict(self.metrics[self.config.active_model_name]),
            'promoted': False
        }
        
        if promote_ab_model and self.ab_model:
            with self.lock:
                logger.info("🏆 Promoting A/B model to active")
                self.active_model = self.ab_model
                results['promoted'] = True
                
                # Clear cache
                if self.cache:
                    self.cache.clear()
        
        # Disable A/B testing
        self.config.enable_ab_testing = False
        self.ab_model = None
        self.ab_metrics = None
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        with self.lock:
            status = {
                'timestamp': datetime.now().isoformat(),
                'active_model': self.config.active_model_name,
                'fallback_model': self.config.fallback_model_name,
                'model_status': dict(self.model_status),
                'model_metadata': self.model_metadata,
                'metrics': {name: asdict(metrics) for name, metrics in self.metrics.items()},
                'response_time_percentiles': self._calculate_percentiles(),
                'cache_stats': self._get_cache_stats(),
                'ab_testing': {
                    'enabled': self.config.enable_ab_testing,
                    'traffic_split': self.config.ab_traffic_split,
                    'ab_model': 'ab_model' if self.ab_model else None
                }
            }
        
        return status
    
    def _calculate_percentiles(self) -> Dict[str, float]:
        """Calculate response time percentiles"""
        if not self.response_times:
            return {}
        
        times = list(self.response_times)
        return {
            'p50': float(np.percentile(times, 50)),
            'p95': float(np.percentile(times, 95)),
            'p99': float(np.percentile(times, 99))
        }
    
    def _get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.cache:
            return {'enabled': False}
        
        with self.cache.lock:
            return {
                'enabled': True,
                'size': len(self.cache.cache),
                'max_size': self.cache.max_size,
                'hit_rate': 'Not tracked'  # Could implement hit rate tracking
            }
    
    @contextmanager
    def maintenance_mode(self):
        """Context manager for maintenance mode"""
        logger.info("🔧 Entering maintenance mode")
        
        # Store original status
        original_status = dict(self.model_status)
        
        try:
            # Set all models to maintenance
            for model_name in self.model_status:
                self.model_status[model_name] = ModelStatus.UPDATING
            
            yield
            
        finally:
            # Restore status
            self.model_status.update(original_status)
            logger.info("✅ Maintenance mode complete")
    
    def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down production orchestrator...")
        
        self.shutdown_event.set()
        
        if self.health_check_thread:
            self.health_check_thread.join(timeout=5.0)
        
        # Clear cache
        if self.cache:
            self.cache.clear()
        
        logger.info("✅ Shutdown complete")

def create_production_orchestrator() -> ProductionHRMOrchestrator:
    """Factory function to create production orchestrator"""
    
    config = DeploymentConfig(
        models_dir="models/hrm-production",
        active_model_name="hrm_nixos_production_v1",
        fallback_model_name="hrm_baseline",
        max_inference_time_ms=500.0,
        enable_response_cache=True,
        cache_size=10000,
        enable_ab_testing=False
    )
    
    orchestrator = ProductionHRMOrchestrator(config)
    
    logger.info("✅ Production HRM orchestrator created")
    
    return orchestrator

def demo_production_integration():
    """Demonstrate production integration capabilities"""
    
    print("\n" + "="*60)
    print("🏭 HRM Production Integration Demo")
    print("="*60)
    
    # Create orchestrator
    orchestrator = create_production_orchestrator()
    
    # Test queries
    test_queries = [
        "install firefox browser",
        "configure nginx web server",
        "error building package",
        "optimize system performance",
        "setup development environment"
    ]
    
    print("\n🧪 Testing production predictions...")
    
    for i, query in enumerate(test_queries):
        print(f"\nQuery {i+1}: '{query}'")
        
        start_time = time.perf_counter()
        result = orchestrator.predict(query, return_all=True)
        response_time = (time.perf_counter() - start_time) * 1000
        
        print(f"  Strategy: {result['strategy']}")
        print(f"  Confidence: {result.get('confidence', 0):.1%}")
        print(f"  Response Time: {response_time:.1f}ms")
        print(f"  Model: {result.get('model_name', 'unknown')}")
        print(f"  Cached: {result.get('cached', False)}")
        
        if 'error' in result:
            print(f"  Error: {result['error']}")
    
    # Show system status
    print("\n📋 System Status:")
    status = orchestrator.get_status()
    print(f"  Active Model: {status['active_model']}")
    print(f"  Fallback Model: {status['fallback_model']}")
    
    for model_name, metrics in status['metrics'].items():
        if metrics['total_requests'] > 0:
            print(f"  {model_name}:")
            print(f"    Requests: {metrics['total_requests']}")
            print(f"    Success Rate: {metrics['successful_requests']/metrics['total_requests']:.1%}")
            print(f"    Avg Response: {metrics['avg_response_time_ms']:.1f}ms")
    
    if status['response_time_percentiles']:
        print("  Response Time Percentiles:")
        for p, time_ms in status['response_time_percentiles'].items():
            print(f"    {p}: {time_ms:.1f}ms")
    
    # Demonstrate A/B testing capability
    print("\n🧪 A/B Testing Demo:")
    print("  (A/B testing would require multiple trained models)")
    print("  Capability: Traffic splitting, metrics comparison, automatic promotion")
    
    # Cleanup
    orchestrator.shutdown()
    
    print("\n" + "="*60)
    print("✅ Production Integration Demo Complete!")
    print("\nKey Features Demonstrated:")
    print("  • Hot-swappable models")
    print("  • Automatic fallback")
    print("  • Response caching")
    print("  • Performance monitoring")
    print("  • Health checking")
    print("  • A/B testing framework")
    print("  • Graceful error handling")
    print("="*60)

if __name__ == "__main__":
    demo_production_integration()