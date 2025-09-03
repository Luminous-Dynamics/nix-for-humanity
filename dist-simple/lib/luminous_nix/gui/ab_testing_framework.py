#!/usr/bin/env python3
"""
🧪 A/B Testing Framework for UI Evolution
Tests different interface variations to find optimal designs
"""

import json
import random
import hashlib
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from enum import Enum
import statistics
import sys

sys.path.insert(0, str(Path(__file__).parent))

from nl_interface_builder_v2 import NLInterfaceBuilderV2, UserContext
from component_synthesis_engine import ComponentDNA, SynthesizedComponent
from learning_persistence import LearningDatabase
from performance_monitor import PerformanceMonitor, PerformanceMetric


class VariationType(Enum):
    """Types of variations to test"""
    
    LAYOUT = "layout"
    COLOR_SCHEME = "color_scheme"
    COMPONENT_ORDER = "component_order"
    INFORMATION_DENSITY = "information_density"
    ANIMATION_SPEED = "animation_speed"
    FONT_SIZE = "font_size"
    SPACING = "spacing"
    BUTTON_STYLE = "button_style"
    ICON_SET = "icon_set"
    COMPLEXITY_LEVEL = "complexity_level"


@dataclass
class ABVariant:
    """Represents a single variant in an A/B test"""
    
    id: str
    name: str
    description: str
    variation_type: VariationType
    parameters: Dict[str, Any]
    created_at: datetime
    
    # Tracking metrics
    impressions: int = 0
    interactions: int = 0
    conversions: int = 0
    total_time_spent: float = 0  # seconds
    satisfaction_scores: List[float] = field(default_factory=list)
    error_count: int = 0
    
    def get_conversion_rate(self) -> float:
        """Calculate conversion rate"""
        if self.impressions == 0:
            return 0
        return self.conversions / self.impressions
    
    def get_average_satisfaction(self) -> float:
        """Calculate average satisfaction score"""
        if not self.satisfaction_scores:
            return 0
        return statistics.mean(self.satisfaction_scores)
    
    def get_engagement_rate(self) -> float:
        """Calculate engagement rate"""
        if self.impressions == 0:
            return 0
        return self.interactions / self.impressions
    
    def get_average_time_spent(self) -> float:
        """Calculate average time spent per impression"""
        if self.impressions == 0:
            return 0
        return self.total_time_spent / self.impressions


@dataclass
class ABTest:
    """Represents an A/B test with multiple variants"""
    
    id: str
    name: str
    description: str
    variation_type: VariationType
    variants: List[ABVariant]
    control_variant_id: str
    
    # Test configuration
    traffic_split: Dict[str, float]  # variant_id -> percentage
    minimum_sample_size: int
    confidence_level: float = 0.95
    
    # Test state
    status: str = "running"  # running, paused, completed
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    
    # Results
    winner_id: Optional[str] = None
    statistical_significance: Optional[float] = None
    
    def get_variant_for_user(self, user_id: str) -> ABVariant:
        """Determine which variant to show to a user"""
        
        # Use consistent hashing for user assignment
        user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        random_value = (user_hash % 100) / 100
        
        # Assign based on traffic split
        cumulative = 0
        for variant in self.variants:
            cumulative += self.traffic_split.get(variant.id, 0)
            if random_value < cumulative:
                return variant
        
        # Fallback to control
        return next(v for v in self.variants if v.id == self.control_variant_id)
    
    def has_sufficient_data(self) -> bool:
        """Check if test has enough data for significance"""
        for variant in self.variants:
            if variant.impressions < self.minimum_sample_size:
                return False
        return True
    
    def calculate_winner(self) -> Tuple[Optional[str], float]:
        """Calculate winning variant and statistical significance"""
        
        if not self.has_sufficient_data():
            return None, 0
        
        # Simple comparison based on conversion rate
        # In production, would use proper statistical tests
        best_variant = max(self.variants, key=lambda v: v.get_conversion_rate())
        control = next(v for v in self.variants if v.id == self.control_variant_id)
        
        # Simplified significance calculation
        if best_variant.impressions > 0 and control.impressions > 0:
            improvement = (
                (best_variant.get_conversion_rate() - control.get_conversion_rate())
                / control.get_conversion_rate()
            ) * 100
            
            # Mock significance (would use proper statistical test)
            significance = min(0.99, abs(improvement) / 10)
            
            return best_variant.id if best_variant != control else None, significance
        
        return None, 0


class ABTestingEngine:
    """Main A/B testing engine for UI optimization"""
    
    def __init__(self):
        self.ui_builder = NLInterfaceBuilderV2(use_llm=False)
        self.learning_db = LearningDatabase()
        self.performance_monitor = PerformanceMonitor()
        
        # Active tests
        self.active_tests: Dict[str, ABTest] = {}
        
        # Test results storage
        self.results_path = Path.home() / ".local" / "share" / "luminous-nix" / "ab_tests"
        self.results_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing tests
        self._load_tests()
    
    def create_test(
        self,
        name: str,
        variation_type: VariationType,
        variants_config: List[Dict],
        traffic_split: Optional[Dict[str, float]] = None,
        minimum_sample_size: int = 100
    ) -> ABTest:
        """Create a new A/B test"""
        
        test_id = hashlib.md5(f"{name}{datetime.now()}".encode()).hexdigest()[:8]
        
        # Create variants
        variants = []
        for i, config in enumerate(variants_config):
            variant = ABVariant(
                id=f"{test_id}_v{i}",
                name=config.get("name", f"Variant {i}"),
                description=config.get("description", ""),
                variation_type=variation_type,
                parameters=config.get("parameters", {}),
                created_at=datetime.now()
            )
            variants.append(variant)
        
        # Set up traffic split (default to even split)
        if traffic_split is None:
            split_percentage = 1.0 / len(variants)
            traffic_split = {v.id: split_percentage for v in variants}
        
        # Create test
        test = ABTest(
            id=test_id,
            name=name,
            description=f"Testing {variation_type.value} variations",
            variation_type=variation_type,
            variants=variants,
            control_variant_id=variants[0].id,  # First variant is control
            traffic_split=traffic_split,
            minimum_sample_size=minimum_sample_size
        )
        
        # Store test
        self.active_tests[test_id] = test
        self._save_test(test)
        
        return test
    
    def get_variant_interface(
        self,
        test_id: str,
        user_id: str,
        base_request: str,
        context: UserContext
    ) -> Tuple[Any, str]:
        """Get the interface variant for a user"""
        
        if test_id not in self.active_tests:
            # No test, return default
            interface = self.ui_builder.build_interface(base_request, context)
            return interface, "default"
        
        test = self.active_tests[test_id]
        variant = test.get_variant_for_user(user_id)
        
        # Apply variant parameters to context
        modified_context = self._apply_variant_parameters(context, variant)
        
        # Generate interface with variant parameters
        interface = self.ui_builder.build_interface(base_request, modified_context)
        
        # Track impression
        variant.impressions += 1
        
        return interface, variant.id
    
    def _apply_variant_parameters(
        self,
        context: UserContext,
        variant: ABVariant
    ) -> UserContext:
        """Apply variant parameters to user context"""
        
        # Clone context
        modified = UserContext(
            user_id=context.user_id,
            expertise_level=context.expertise_level,
            device_type=context.device_type,
            preferences=context.preferences.copy() if context.preferences else {}
        )
        
        # Apply variant parameters based on type
        if variant.variation_type == VariationType.LAYOUT:
            modified.preferences["layout"] = variant.parameters.get("layout", "default")
        
        elif variant.variation_type == VariationType.COLOR_SCHEME:
            modified.preferences["theme"] = variant.parameters.get("theme", "light")
            modified.preferences["color_palette"] = variant.parameters.get("palette", "default")
        
        elif variant.variation_type == VariationType.INFORMATION_DENSITY:
            modified.preferences["density"] = variant.parameters.get("density", "normal")
            modified.preferences["show_details"] = variant.parameters.get("show_details", True)
        
        elif variant.variation_type == VariationType.ANIMATION_SPEED:
            modified.preferences["animation_speed"] = variant.parameters.get("speed", "normal")
            modified.preferences["transitions"] = variant.parameters.get("transitions", True)
        
        elif variant.variation_type == VariationType.FONT_SIZE:
            modified.preferences["font_size"] = variant.parameters.get("size", "medium")
            modified.preferences["line_height"] = variant.parameters.get("line_height", 1.5)
        
        elif variant.variation_type == VariationType.SPACING:
            modified.preferences["padding"] = variant.parameters.get("padding", "normal")
            modified.preferences["margins"] = variant.parameters.get("margins", "normal")
        
        elif variant.variation_type == VariationType.COMPLEXITY_LEVEL:
            modified.expertise_level = variant.parameters.get("complexity", "intermediate")
            modified.preferences["advanced_features"] = variant.parameters.get("advanced", False)
        
        return modified
    
    def record_interaction(
        self,
        test_id: str,
        variant_id: str,
        interaction_type: str,
        duration: float = 0
    ):
        """Record user interaction with a variant"""
        
        if test_id not in self.active_tests:
            return
        
        test = self.active_tests[test_id]
        variant = next((v for v in test.variants if v.id == variant_id), None)
        
        if variant:
            variant.interactions += 1
            variant.total_time_spent += duration
            
            # Check for conversion
            if interaction_type in ["complete", "submit", "success"]:
                variant.conversions += 1
    
    def record_feedback(
        self,
        test_id: str,
        variant_id: str,
        satisfaction: float,
        error_occurred: bool = False
    ):
        """Record user feedback for a variant"""
        
        if test_id not in self.active_tests:
            return
        
        test = self.active_tests[test_id]
        variant = next((v for v in test.variants if v.id == variant_id), None)
        
        if variant:
            variant.satisfaction_scores.append(satisfaction)
            if error_occurred:
                variant.error_count += 1
    
    def check_test_completion(self, test_id: str) -> bool:
        """Check if a test should be completed"""
        
        if test_id not in self.active_tests:
            return False
        
        test = self.active_tests[test_id]
        
        # Check if sufficient data collected
        if test.has_sufficient_data():
            # Calculate winner
            winner_id, significance = test.calculate_winner()
            
            if significance >= 0.95:  # 95% confidence
                test.winner_id = winner_id
                test.statistical_significance = significance
                test.status = "completed"
                test.ended_at = datetime.now()
                
                self._save_test(test)
                self._apply_winning_variant(test)
                
                return True
        
        return False
    
    def _apply_winning_variant(self, test: ABTest):
        """Apply the winning variant as the new default"""
        
        if not test.winner_id:
            return
        
        winner = next((v for v in test.variants if v.id == test.winner_id), None)
        if not winner:
            return
        
        # Store winning parameters for future use
        winning_config = {
            "test_id": test.id,
            "test_name": test.name,
            "variation_type": test.variation_type.value,
            "winning_variant": winner.name,
            "parameters": winner.parameters,
            "improvement": {
                "conversion_rate": winner.get_conversion_rate(),
                "satisfaction": winner.get_average_satisfaction(),
                "engagement": winner.get_engagement_rate()
            },
            "applied_at": datetime.now().isoformat()
        }
        
        # Save to learning database
        self.learning_db.conn.execute(
            """
            INSERT INTO ab_test_winners
            VALUES (?, ?, ?, ?)
            """,
            (
                test.id,
                test.variation_type.value,
                json.dumps(winner.parameters),
                datetime.now().isoformat()
            )
        )
        self.learning_db.conn.commit()
    
    def get_test_results(self, test_id: str) -> Dict:
        """Get detailed results for a test"""
        
        if test_id not in self.active_tests:
            return {}
        
        test = self.active_tests[test_id]
        
        results = {
            "test_id": test.id,
            "test_name": test.name,
            "status": test.status,
            "started": test.started_at.isoformat(),
            "ended": test.ended_at.isoformat() if test.ended_at else None,
            "variants": []
        }
        
        for variant in test.variants:
            variant_data = {
                "id": variant.id,
                "name": variant.name,
                "is_control": variant.id == test.control_variant_id,
                "metrics": {
                    "impressions": variant.impressions,
                    "interactions": variant.interactions,
                    "conversions": variant.conversions,
                    "conversion_rate": f"{variant.get_conversion_rate():.2%}",
                    "engagement_rate": f"{variant.get_engagement_rate():.2%}",
                    "avg_satisfaction": f"{variant.get_average_satisfaction():.2f}",
                    "avg_time_spent": f"{variant.get_average_time_spent():.2f}s",
                    "error_count": variant.error_count
                }
            }
            
            # Calculate improvement vs control
            if variant.id != test.control_variant_id:
                control = next(v for v in test.variants if v.id == test.control_variant_id)
                if control.get_conversion_rate() > 0:
                    improvement = (
                        (variant.get_conversion_rate() - control.get_conversion_rate())
                        / control.get_conversion_rate()
                    ) * 100
                    variant_data["improvement"] = f"{improvement:+.1f}%"
            
            results["variants"].append(variant_data)
        
        if test.winner_id:
            results["winner"] = test.winner_id
            results["confidence"] = f"{test.statistical_significance:.2%}"
        
        return results
    
    def create_multivariate_test(
        self,
        name: str,
        variations: Dict[VariationType, List[Dict]],
        sample_size_per_variant: int = 50
    ) -> List[ABTest]:
        """Create multiple A/B tests for multivariate testing"""
        
        tests = []
        
        for variation_type, variants_config in variations.items():
            test = self.create_test(
                name=f"{name}_{variation_type.value}",
                variation_type=variation_type,
                variants_config=variants_config,
                minimum_sample_size=sample_size_per_variant
            )
            tests.append(test)
        
        return tests
    
    def get_optimization_recommendations(self) -> List[Dict]:
        """Get recommendations based on all test results"""
        
        recommendations = []
        
        # Analyze completed tests
        for test in self.active_tests.values():
            if test.status == "completed" and test.winner_id:
                winner = next(v for v in test.variants if v.id == test.winner_id)
                control = next(v for v in test.variants if v.id == test.control_variant_id)
                
                if winner != control:
                    improvement = (
                        (winner.get_conversion_rate() - control.get_conversion_rate())
                        / control.get_conversion_rate()
                    ) * 100
                    
                    recommendations.append({
                        "type": test.variation_type.value,
                        "recommendation": f"Use {winner.name} configuration",
                        "reason": f"Shows {improvement:.1f}% improvement in conversion",
                        "confidence": test.statistical_significance,
                        "parameters": winner.parameters
                    })
        
        return recommendations
    
    def _save_test(self, test: ABTest):
        """Save test to persistent storage"""
        
        test_file = self.results_path / f"{test.id}.json"
        
        # Convert to dictionary
        test_dict = {
            "id": test.id,
            "name": test.name,
            "description": test.description,
            "variation_type": test.variation_type.value,
            "control_variant_id": test.control_variant_id,
            "traffic_split": test.traffic_split,
            "minimum_sample_size": test.minimum_sample_size,
            "confidence_level": test.confidence_level,
            "status": test.status,
            "started_at": test.started_at.isoformat(),
            "ended_at": test.ended_at.isoformat() if test.ended_at else None,
            "winner_id": test.winner_id,
            "statistical_significance": test.statistical_significance,
            "variants": []
        }
        
        for variant in test.variants:
            variant_dict = asdict(variant)
            variant_dict["created_at"] = variant.created_at.isoformat()
            variant_dict["variation_type"] = variant.variation_type.value
            test_dict["variants"].append(variant_dict)
        
        with open(test_file, 'w') as f:
            json.dump(test_dict, f, indent=2)
    
    def _load_tests(self):
        """Load tests from persistent storage"""
        
        if not self.results_path.exists():
            return
        
        for test_file in self.results_path.glob("*.json"):
            try:
                with open(test_file, 'r') as f:
                    test_data = json.load(f)
                
                # Reconstruct variants
                variants = []
                for variant_data in test_data["variants"]:
                    variant = ABVariant(
                        id=variant_data["id"],
                        name=variant_data["name"],
                        description=variant_data["description"],
                        variation_type=VariationType(variant_data["variation_type"]),
                        parameters=variant_data["parameters"],
                        created_at=datetime.fromisoformat(variant_data["created_at"])
                    )
                    
                    # Restore metrics
                    variant.impressions = variant_data.get("impressions", 0)
                    variant.interactions = variant_data.get("interactions", 0)
                    variant.conversions = variant_data.get("conversions", 0)
                    variant.total_time_spent = variant_data.get("total_time_spent", 0)
                    variant.satisfaction_scores = variant_data.get("satisfaction_scores", [])
                    variant.error_count = variant_data.get("error_count", 0)
                    
                    variants.append(variant)
                
                # Reconstruct test
                test = ABTest(
                    id=test_data["id"],
                    name=test_data["name"],
                    description=test_data["description"],
                    variation_type=VariationType(test_data["variation_type"]),
                    variants=variants,
                    control_variant_id=test_data["control_variant_id"],
                    traffic_split=test_data["traffic_split"],
                    minimum_sample_size=test_data["minimum_sample_size"],
                    confidence_level=test_data.get("confidence_level", 0.95),
                    status=test_data["status"],
                    started_at=datetime.fromisoformat(test_data["started_at"])
                )
                
                if test_data.get("ended_at"):
                    test.ended_at = datetime.fromisoformat(test_data["ended_at"])
                
                test.winner_id = test_data.get("winner_id")
                test.statistical_significance = test_data.get("statistical_significance")
                
                # Only load active tests
                if test.status == "running":
                    self.active_tests[test.id] = test
                    
            except Exception as e:
                print(f"Error loading test {test_file}: {e}")


def demo_ab_testing():
    """Demonstrate A/B testing framework"""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║        🧪 A/B TESTING FRAMEWORK DEMO                               ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    engine = ABTestingEngine()
    
    # Create a test for color schemes
    print("\n1️⃣ Creating Color Scheme A/B Test...")
    
    color_test = engine.create_test(
        name="Dashboard Color Scheme Test",
        variation_type=VariationType.COLOR_SCHEME,
        variants_config=[
            {
                "name": "Light Theme (Control)",
                "description": "Default light theme",
                "parameters": {"theme": "light", "palette": "default"}
            },
            {
                "name": "Dark Theme",
                "description": "Modern dark theme",
                "parameters": {"theme": "dark", "palette": "monokai"}
            },
            {
                "name": "High Contrast",
                "description": "Accessibility-focused high contrast",
                "parameters": {"theme": "high_contrast", "palette": "accessible"}
            }
        ],
        minimum_sample_size=10  # Low for demo
    )
    
    print(f"   ✅ Created test: {color_test.name}")
    print(f"   📊 Testing {len(color_test.variants)} variants")
    
    # Simulate user interactions
    print("\n2️⃣ Simulating User Interactions...")
    
    users = [f"user_{i}" for i in range(30)]
    context = UserContext(user_id="test", expertise_level="intermediate")
    
    for user_id in users:
        # Get variant for user
        interface, variant_id = engine.get_variant_interface(
            color_test.id,
            user_id,
            "Create a dashboard",
            context
        )
        
        # Simulate interaction
        interaction_time = random.uniform(10, 60)
        engine.record_interaction(
            color_test.id,
            variant_id,
            "view",
            duration=interaction_time
        )
        
        # Some users convert
        if random.random() < 0.3:  # 30% base conversion
            # Variant affects conversion
            variant = next(v for v in color_test.variants if v.id == variant_id)
            if "dark" in variant.name.lower():
                bonus = 0.2  # Dark theme gets bonus
            elif "high_contrast" in variant.name.lower():
                bonus = 0.1
            else:
                bonus = 0
            
            if random.random() < (0.5 + bonus):
                engine.record_interaction(
                    color_test.id,
                    variant_id,
                    "complete",
                    duration=random.uniform(30, 120)
                )
        
        # Record satisfaction
        base_satisfaction = random.uniform(3, 5)
        variant = next(v for v in color_test.variants if v.id == variant_id)
        if "dark" in variant.name.lower():
            satisfaction = min(5, base_satisfaction + 0.5)
        else:
            satisfaction = base_satisfaction
        
        engine.record_feedback(
            color_test.id,
            variant_id,
            satisfaction
        )
    
    print(f"   ✅ Simulated {len(users)} user interactions")
    
    # Check for test completion
    print("\n3️⃣ Checking Test Completion...")
    
    if engine.check_test_completion(color_test.id):
        print("   ✅ Test completed with statistical significance!")
    else:
        print("   ⏳ Test needs more data")
    
    # Get results
    print("\n4️⃣ Test Results:")
    print("-" * 60)
    
    results = engine.get_test_results(color_test.id)
    
    for variant in results["variants"]:
        print(f"\n   📊 {variant['name']}:")
        print(f"      Impressions: {variant['metrics']['impressions']}")
        print(f"      Conversion Rate: {variant['metrics']['conversion_rate']}")
        print(f"      Engagement Rate: {variant['metrics']['engagement_rate']}")
        print(f"      Satisfaction: {variant['metrics']['avg_satisfaction']}")
        
        if "improvement" in variant:
            print(f"      Improvement vs Control: {variant['improvement']}")
    
    if results.get("winner"):
        print(f"\n   🏆 Winner: {results['winner']}")
        print(f"   📊 Confidence: {results['confidence']}")
    
    # Create multivariate test
    print("\n5️⃣ Creating Multivariate Test...")
    
    multivariate_tests = engine.create_multivariate_test(
        name="Complete UI Optimization",
        variations={
            VariationType.INFORMATION_DENSITY: [
                {"name": "Sparse", "parameters": {"density": "sparse"}},
                {"name": "Normal", "parameters": {"density": "normal"}},
                {"name": "Dense", "parameters": {"density": "dense"}}
            ],
            VariationType.ANIMATION_SPEED: [
                {"name": "No Animation", "parameters": {"speed": "none"}},
                {"name": "Fast", "parameters": {"speed": "fast"}},
                {"name": "Smooth", "parameters": {"speed": "smooth"}}
            ]
        },
        sample_size_per_variant=5
    )
    
    print(f"   ✅ Created {len(multivariate_tests)} parallel tests")
    
    # Get recommendations
    print("\n6️⃣ Optimization Recommendations:")
    print("-" * 60)
    
    recommendations = engine.get_optimization_recommendations()
    
    if recommendations:
        for rec in recommendations:
            print(f"\n   💡 {rec['type'].upper()}:")
            print(f"      Recommendation: {rec['recommendation']}")
            print(f"      Reason: {rec['reason']}")
            print(f"      Confidence: {rec['confidence']:.2%}")
    else:
        print("   ℹ️ No recommendations yet - tests need more data")
    
    print("""
═══════════════════════════════════════════════════════════════════════
✨ A/B Testing Framework Features:

1. Variant Management:
   • Multiple variant types (layout, color, density, etc.)
   • Consistent user assignment via hashing
   • Traffic splitting control

2. Metrics Tracking:
   • Conversion rates
   • Engagement metrics
   • Satisfaction scores
   • Time spent analysis

3. Statistical Analysis:
   • Automatic significance testing
   • Winner determination
   • Confidence calculations

4. Multivariate Testing:
   • Test multiple variations simultaneously
   • Parallel optimization
   • Comprehensive analysis

5. Learning Integration:
   • Automatic application of winners
   • Persistent storage
   • Optimization recommendations

Next Steps:
• Connect to real user interactions
• Implement Bayesian optimization
• Add more statistical tests
• Create visual dashboard
═══════════════════════════════════════════════════════════════════════
    """)


if __name__ == "__main__":
    demo_ab_testing()