#!/usr/bin/env python3
"""
🎯 Service Layer for AI-Driven Interface Generation
Separates business logic from UI components
"""

import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from functools import lru_cache
from dataclasses import dataclass, asdict

from error_handler import safe_database_operation, safe_async_operation, get_logger, error_collector
from config_manager import get_config
from database_migrations import DatabaseMigrationManager

# Import core components
from nl_interface_builder_v2 import NLInterfaceBuilderV2, GeneratedInterface, UserContext
from component_synthesis_engine import ComponentDNA, ComponentSynthesizer
from learning_persistence import LearningDatabase, InterfaceMetrics
from pattern_analysis_dashboard import PatternAnalyzer, InsightReport
from feedback_collection_system import FeedbackCollector, FeedbackType, FeedbackItem
from ab_testing_framework import ABTestingEngine, VariationType
from automatic_optimization import AutomaticOptimizer, OptimizationResult
from performance_monitor import PerformanceMonitor


@dataclass
class ServiceResponse:
    """Standard response from service layer"""
    
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata or {}
        }


class BaseService:
    """Base class for all services"""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.config = get_config()
        self._ensure_database()
    
    def _ensure_database(self):
        """Ensure database is migrated to latest version"""
        try:
            manager = DatabaseMigrationManager(self.config.db_path)
            manager.migrate_to_version()
            manager.close()
        except Exception as e:
            self.logger.error(f"Database migration failed: {e}")


class InterfaceGenerationService(BaseService):
    """Service for generating and managing interfaces"""
    
    def __init__(self):
        super().__init__()
        self.builder = NLInterfaceBuilderV2(use_llm=False)
        self.synthesizer = ComponentSynthesizer()
        self.learning_db = LearningDatabase()
        
        # Cache for generated interfaces
        self._interface_cache = {}
        self._cache_ttl = timedelta(minutes=15)
    
    @lru_cache(maxsize=100)
    def generate_interface(
        self,
        request: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> ServiceResponse:
        """Generate an interface from natural language request"""
        
        try:
            # Check cache first
            cache_key = f"{request}_{json.dumps(user_context or {})}"
            if cache_key in self._interface_cache:
                cached = self._interface_cache[cache_key]
                if datetime.now() - cached['timestamp'] < self._cache_ttl:
                    return ServiceResponse(
                        success=True,
                        data=cached['interface'],
                        metadata={"from_cache": True}
                    )
            
            # Create user context
            context = UserContext(**(user_context or {})) if user_context else None
            
            # Generate interface
            interface = self.builder.build_interface(request, context)
            
            # Store in cache
            self._interface_cache[cache_key] = {
                'interface': interface,
                'timestamp': datetime.now()
            }
            
            # Store in database for learning
            self.learning_db.store_interface(interface)
            
            return ServiceResponse(
                success=True,
                data=interface,
                metadata={
                    "generation_time": interface.metadata.get("generation_time", 0),
                    "component_count": len(interface.components)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate interface: {e}")
            return ServiceResponse(
                success=False,
                error=str(e)
            )
    
    def evolve_interface(
        self,
        interface_id: str,
        evolution_type: str = "optimize"
    ) -> ServiceResponse:
        """Evolve an existing interface"""
        
        try:
            # Get existing interface
            interface_data = self.learning_db.get_interface(interface_id)
            if not interface_data:
                return ServiceResponse(
                    success=False,
                    error=f"Interface {interface_id} not found"
                )
            
            # Apply evolution based on type
            if evolution_type == "optimize":
                # Use component synthesis for optimization
                evolved_components = []
                for component in interface_data.get("components", []):
                    dna = ComponentDNA(
                        base_type=component.get("type"),
                        traits=component.get("properties", {})
                    )
                    evolved_dna = self.synthesizer.evolve_population([dna], generations=5)[0]
                    evolved_components.append({
                        "type": evolved_dna.base_type,
                        "properties": evolved_dna.traits
                    })
                
                return ServiceResponse(
                    success=True,
                    data={
                        "original_id": interface_id,
                        "evolved_components": evolved_components
                    }
                )
            
            elif evolution_type == "simplify":
                # Reduce complexity
                simplified = [c for i, c in enumerate(interface_data.get("components", [])) 
                             if i % 2 == 0]  # Simple reduction for demo
                
                return ServiceResponse(
                    success=True,
                    data={
                        "original_id": interface_id,
                        "simplified_components": simplified
                    }
                )
            
            else:
                return ServiceResponse(
                    success=False,
                    error=f"Unknown evolution type: {evolution_type}"
                )
                
        except Exception as e:
            self.logger.error(f"Failed to evolve interface: {e}")
            return ServiceResponse(
                success=False,
                error=str(e)
            )
    
    def get_interface_history(
        self,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> ServiceResponse:
        """Get interface generation history"""
        
        try:
            # This would query the database for historical interfaces
            # For now, return mock data
            history = []
            
            return ServiceResponse(
                success=True,
                data=history,
                metadata={"total_count": len(history)}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get interface history: {e}")
            return ServiceResponse(
                success=False,
                error=str(e)
            )


class PatternAnalysisService(BaseService):
    """Service for analyzing usage patterns and generating insights"""
    
    def __init__(self):
        super().__init__()
        self.analyzer = PatternAnalyzer()
        self._insights_cache = None
        self._cache_timestamp = None
    
    def analyze_patterns(self, force_refresh: bool = False) -> ServiceResponse:
        """Analyze usage patterns"""
        
        try:
            patterns = self.analyzer.analyze_usage_patterns()
            
            return ServiceResponse(
                success=True,
                data={
                    "patterns": [
                        {
                            "id": p.id,
                            "name": p.name,
                            "type": p.pattern_type,
                            "frequency": p.frequency,
                            "confidence": p.confidence,
                            "optimization_score": p.optimization_score
                        }
                        for p in patterns[:10]  # Top 10
                    ]
                },
                metadata={
                    "total_patterns": len(patterns),
                    "analysis_timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to analyze patterns: {e}")
            return ServiceResponse(
                success=False,
                error=str(e)
            )
    
    @lru_cache(maxsize=1)
    def get_insights(self, force_refresh: bool = False) -> ServiceResponse:
        """Get actionable insights with caching"""
        
        try:
            # Check cache
            if not force_refresh and self._insights_cache:
                cache_age = datetime.now() - self._cache_timestamp
                if cache_age < timedelta(hours=1):
                    return ServiceResponse(
                        success=True,
                        data=self._insights_cache,
                        metadata={"from_cache": True}
                    )
            
            # Generate fresh insights
            insights = self.analyzer.generate_insights()
            
            # Process for response
            processed_insights = []
            for insight in insights[:5]:  # Top 5
                processed_insights.append({
                    "id": insight.id,
                    "title": insight.title,
                    "description": insight.description,
                    "category": insight.category,
                    "priority": insight.priority,
                    "confidence": insight.confidence,
                    "recommendations": insight.recommendations,
                    "expected_impact": insight.expected_impact
                })
            
            # Update cache
            self._insights_cache = processed_insights
            self._cache_timestamp = datetime.now()
            
            return ServiceResponse(
                success=True,
                data=processed_insights,
                metadata={
                    "total_insights": len(insights),
                    "high_priority_count": len([i for i in insights if i.priority == "high"])
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get insights: {e}")
            return ServiceResponse(
                success=False,
                error=str(e)
            )
    
    def get_dashboard_data(self) -> ServiceResponse:
        """Get comprehensive dashboard data"""
        
        try:
            data = self.analyzer.generate_dashboard_data()
            
            return ServiceResponse(
                success=True,
                data=data,
                metadata={
                    "generated_at": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get dashboard data: {e}")
            return ServiceResponse(
                success=False,
                error=str(e)
            )


class FeedbackService(BaseService):
    """Service for managing user feedback"""
    
    def __init__(self):
        super().__init__()
        self.collector = FeedbackCollector()
        self.active_sessions = {}
    
    def start_feedback_session(self, user_id: str) -> ServiceResponse:
        """Start a new feedback session"""
        
        try:
            session_id = self.collector.start_session(user_id)
            self.active_sessions[session_id] = user_id
            
            return ServiceResponse(
                success=True,
                data={"session_id": session_id},
                metadata={"user_id": user_id}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to start feedback session: {e}")
            return ServiceResponse(
                success=False,
                error=str(e)
            )
    
    def collect_feedback(
        self,
        session_id: str,
        interface_id: str,
        feedback_type: str,
        value: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ServiceResponse:
        """Collect user feedback"""
        
        try:
            # Convert string to enum
            fb_type = FeedbackType[feedback_type.upper()]
            
            # Collect feedback
            feedback = self.collector.collect_feedback(
                session_id,
                interface_id,
                fb_type,
                value,
                **(metadata or {})
            )
            
            return ServiceResponse(
                success=True,
                data={
                    "feedback_id": feedback.id,
                    "sentiment": feedback.sentiment
                },
                metadata={
                    "timestamp": feedback.timestamp.isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to collect feedback: {e}")
            return ServiceResponse(
                success=False,
                error=str(e)
            )
    
    def get_feedback_summary(self, days: int = 7) -> ServiceResponse:
        """Get feedback summary"""
        
        try:
            summary = self.collector.get_feedback_summary(days)
            
            return ServiceResponse(
                success=True,
                data=summary,
                metadata={
                    "period_days": days,
                    "generated_at": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get feedback summary: {e}")
            return ServiceResponse(
                success=False,
                error=str(e)
            )


class OptimizationService(BaseService):
    """Service for automatic optimization"""
    
    def __init__(self):
        super().__init__()
        self.optimizer = AutomaticOptimizer()
        self._optimization_running = False
    
    @safe_async_operation(default_return=ServiceResponse(success=False, error="Async operation failed"))
    async def run_optimization_cycle(self) -> ServiceResponse:
        """Run an optimization cycle"""
        
        if self._optimization_running:
            return ServiceResponse(
                success=False,
                error="Optimization already in progress"
            )
        
        try:
            self._optimization_running = True
            
            # Run optimization
            results = await self.optimizer.run_optimization_cycle()
            
            # Process results
            processed_results = []
            for result in results:
                processed_results.append({
                    "id": result.id,
                    "rule_id": result.rule_id,
                    "target": f"{result.target_type}:{result.target_id}",
                    "status": result.status,
                    "confidence": result.confidence
                })
            
            return ServiceResponse(
                success=True,
                data=processed_results,
                metadata={
                    "optimizations_applied": len(results),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Optimization cycle failed: {e}")
            return ServiceResponse(
                success=False,
                error=str(e)
            )
        finally:
            self._optimization_running = False
    
    def get_optimization_status(self) -> ServiceResponse:
        """Get current optimization status"""
        
        try:
            dashboard = self.optimizer.get_optimization_dashboard()
            
            return ServiceResponse(
                success=True,
                data=dashboard,
                metadata={
                    "is_running": self._optimization_running
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get optimization status: {e}")
            return ServiceResponse(
                success=False,
                error=str(e)
            )
    
    def configure_optimization(
        self,
        auto_apply: Optional[bool] = None,
        require_approval: Optional[bool] = None
    ) -> ServiceResponse:
        """Configure optimization settings"""
        
        try:
            if auto_apply is not None:
                self.optimizer.auto_apply = auto_apply
            
            if require_approval is not None:
                self.optimizer.require_approval = require_approval
            
            return ServiceResponse(
                success=True,
                data={
                    "auto_apply": self.optimizer.auto_apply,
                    "require_approval": self.optimizer.require_approval
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to configure optimization: {e}")
            return ServiceResponse(
                success=False,
                error=str(e)
            )


class ABTestingService(BaseService):
    """Service for A/B testing"""
    
    def __init__(self):
        super().__init__()
        self.ab_testing = ABTestingEngine()
    
    def create_test(
        self,
        name: str,
        variants: List[Dict[str, Any]],
        test_type: str = "FEATURE"
    ) -> ServiceResponse:
        """Create a new A/B test"""
        
        try:
            # Convert string to enum
            variation_type = VariationType[test_type]
            
            # Create test
            test = self.ab_testing.create_test(
                name=name,
                variation_type=variation_type,
                variants_config=variants,
                minimum_sample_size=self.config.ab_testing.minimum_sample_size
            )
            
            return ServiceResponse(
                success=True,
                data={
                    "test_id": test.id,
                    "name": test.name,
                    "status": test.status,
                    "variants": [
                        {"id": v.id, "name": v.name}
                        for v in test.variants
                    ]
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create A/B test: {e}")
            return ServiceResponse(
                success=False,
                error=str(e)
            )
    
    def get_test_results(self, test_id: str) -> ServiceResponse:
        """Get A/B test results"""
        
        try:
            results = self.ab_testing.get_test_results(test_id)
            
            return ServiceResponse(
                success=True,
                data=results
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get test results: {e}")
            return ServiceResponse(
                success=False,
                error=str(e)
            )
    
    def conclude_test(self, test_id: str) -> ServiceResponse:
        """Conclude an A/B test"""
        
        try:
            winner = self.ab_testing.conclude_test(test_id)
            
            return ServiceResponse(
                success=True,
                data={
                    "winner_id": winner.id if winner else None,
                    "winner_name": winner.name if winner else None
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to conclude test: {e}")
            return ServiceResponse(
                success=False,
                error=str(e)
            )


class PerformanceService(BaseService):
    """Service for performance monitoring"""
    
    def __init__(self):
        super().__init__()
        self.monitor = PerformanceMonitor()
    
    @lru_cache(maxsize=1)
    def get_performance_metrics(self) -> ServiceResponse:
        """Get current performance metrics"""
        
        try:
            metrics = self.monitor.get_current_metrics()
            
            return ServiceResponse(
                success=True,
                data=metrics,
                metadata={
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get performance metrics: {e}")
            return ServiceResponse(
                success=False,
                error=str(e)
            )
    
    def get_performance_summary(self) -> ServiceResponse:
        """Get performance summary"""
        
        try:
            summary = self.monitor.calculate_summary()
            
            return ServiceResponse(
                success=True,
                data=summary
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get performance summary: {e}")
            return ServiceResponse(
                success=False,
                error=str(e)
            )


def demo_services():
    """Demonstrate service layer"""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║        🎯 SERVICE LAYER DEMO                                       ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    # Test Interface Generation Service
    print("\n1️⃣ Interface Generation Service:")
    print("-" * 60)
    
    interface_service = InterfaceGenerationService()
    
    response = interface_service.generate_interface(
        "Create a user dashboard",
        {"skill_level": "intermediate"}
    )
    
    print(f"   Success: {response.success}")
    if response.success:
        print(f"   Components: {response.metadata['component_count']}")
        print(f"   Generation time: {response.metadata['generation_time']}ms")
    
    # Test Pattern Analysis Service
    print("\n2️⃣ Pattern Analysis Service:")
    print("-" * 60)
    
    pattern_service = PatternAnalysisService()
    
    response = pattern_service.get_insights()
    
    print(f"   Success: {response.success}")
    if response.success:
        print(f"   Insights found: {response.metadata['total_insights']}")
        print(f"   High priority: {response.metadata['high_priority_count']}")
    
    # Test Feedback Service
    print("\n3️⃣ Feedback Service:")
    print("-" * 60)
    
    feedback_service = FeedbackService()
    
    # Start session
    response = feedback_service.start_feedback_session("demo_user")
    if response.success:
        session_id = response.data["session_id"]
        print(f"   Session started: {session_id}")
        
        # Collect feedback
        response = feedback_service.collect_feedback(
            session_id,
            "interface_001",
            "rating",
            4,
            {"interface_type": "dashboard"}
        )
        print(f"   Feedback collected: {response.success}")
        
        # Get summary
        response = feedback_service.get_feedback_summary(days=1)
        if response.success:
            print(f"   Total feedback: {response.data.get('total_feedback', 0)}")
    
    # Test Optimization Service
    print("\n4️⃣ Optimization Service:")
    print("-" * 60)
    
    optimization_service = OptimizationService()
    
    response = optimization_service.get_optimization_status()
    
    print(f"   Success: {response.success}")
    if response.success:
        summary = response.data.get("summary", {})
        print(f"   Total rules: {summary.get('total_rules', 0)}")
        print(f"   Active optimizations: {summary.get('active_optimizations', 0)}")
    
    # Test A/B Testing Service
    print("\n5️⃣ A/B Testing Service:")
    print("-" * 60)
    
    ab_service = ABTestingService()
    
    response = ab_service.create_test(
        "Button Color Test",
        [
            {"name": "Blue", "parameters": {"color": "blue"}},
            {"name": "Green", "parameters": {"color": "green"}}
        ],
        "FEATURE"
    )
    
    print(f"   Success: {response.success}")
    if response.success:
        print(f"   Test ID: {response.data['test_id']}")
        print(f"   Variants: {len(response.data['variants'])}")
    
    # Test Performance Service
    print("\n6️⃣ Performance Service:")
    print("-" * 60)
    
    performance_service = PerformanceService()
    
    response = performance_service.get_performance_summary()
    
    print(f"   Success: {response.success}")
    if response.success and response.data:
        print(f"   Avg generation time: {response.data.get('avg_generation_time', 0)}ms")
        print(f"   Total generations: {response.data.get('total_generations', 0)}")
    
    print("""

═══════════════════════════════════════════════════════════════════════
✨ Service Layer Features:

1. Separation of Concerns:
   • Business logic separated from UI
   • Clean service interfaces
   • Consistent response format

2. Caching Strategy:
   • LRU cache for expensive operations
   • Time-based cache invalidation
   • Cache control in responses

3. Error Handling:
   • Consistent error responses
   • Logged exceptions
   • Graceful degradation

4. Service Components:
   • Interface Generation
   • Pattern Analysis
   • Feedback Collection
   • Optimization Control
   • A/B Testing
   • Performance Monitoring

5. Benefits:
   • Testable business logic
   • Reusable across UIs
   • Clear API boundaries
   • Easy to extend

Next Steps:
• Add service orchestration
• Implement service events
• Add service metrics
• Create service documentation
═══════════════════════════════════════════════════════════════════════
    """)


if __name__ == "__main__":
    demo_services()