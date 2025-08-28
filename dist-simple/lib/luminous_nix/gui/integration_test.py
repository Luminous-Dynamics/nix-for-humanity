#!/usr/bin/env python3
"""
🔄 Integration Test - Complete Flow Demonstration
Validates the entire pipeline from natural language to persistent learning
"""

import asyncio
import time
from pathlib import Path
import tempfile
import json
from datetime import datetime
from typing import Dict, List, Any

# Import all our components
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from component_synthesis_engine import ComponentSynthesizer, ComponentRequirements
from nl_interface_builder import NLInterfaceBuilder, UserContext
from synthesis_bridge import SynthesisBridge, DynamicModificationEngine
from learning_persistence import (
    LearningDatabase,
    ContinuousImprovementEngine,
    InterfaceMetrics
)


class IntegrationTestSuite:
    """Complete integration test suite"""
    
    def __init__(self, db_path: str = None):
        """Initialize test suite with all components"""
        
        # Create temporary database if not specified
        if db_path is None:
            self.temp_dir = tempfile.mkdtemp()
            db_path = Path(self.temp_dir) / "test_learning.db"
        
        # Initialize all components
        self.builder = NLInterfaceBuilder()
        self.bridge = SynthesisBridge()
        self.modifier = DynamicModificationEngine(self.bridge)
        self.db = LearningDatabase(str(db_path))
        self.learning_engine = ContinuousImprovementEngine(self.db)
        
        # Test tracking
        self.test_results = []
        self.performance_metrics = {}
    
    async def test_complete_flow(self):
        """Test the complete flow from request to learning"""
        
        print("\n" + "="*60)
        print("🔄 INTEGRATION TEST: Complete Flow")
        print("="*60)
        
        # Step 1: Natural Language Request
        print("\n1️⃣ Natural Language Request")
        request = "Create a dashboard for monitoring server metrics with dark theme"
        print(f"   Request: {request}")
        
        # Step 2: Build Interface
        print("\n2️⃣ Building Interface...")
        start_time = time.time()
        
        context = UserContext(
            user_id="test_user_001",
            expertise_level="intermediate",
            device_type="desktop",
            preferences={"theme": "dark"},
            time_context="evening"
        )
        
        interface = self.builder.build_interface(request, context)
        generation_time = (time.time() - start_time) * 1000  # Convert to ms
        
        print(f"   ✅ Generated {len(interface.components)} components")
        print(f"   ⏱️ Generation time: {generation_time:.2f}ms")
        print(f"   📐 Layout: {interface.layout.get('type')}")
        print(f"   🎨 Theme: {interface.theme.get('mode')}")
        
        # Step 3: Render to UI
        print("\n3️⃣ Rendering to UI...")
        ui_container = self.bridge.render_interface(interface)
        
        if ui_container:
            print(f"   ✅ Rendered to {type(ui_container).__name__}")
            print(f"   📦 Widget cache size: {len(self.bridge.widget_map)}")
        else:
            print("   ⚠️ No UI container available (Textual not installed)")
        
        # Step 4: Record Interaction
        print("\n4️⃣ Recording Interaction...")
        self.learning_engine.record_interaction(
            user_id=context.user_id,
            interface=interface,
            request=request,
            generation_time=generation_time
        )
        print("   ✅ Interaction recorded")
        
        # Step 5: Simulate User Interaction
        print("\n5️⃣ Simulating User Interaction...")
        await asyncio.sleep(0.5)  # Simulate interaction time
        
        interaction_time = 45.0  # seconds
        satisfaction = 0.85
        task_completed = True
        
        print(f"   ⏱️ Interaction time: {interaction_time}s")
        print(f"   😊 Satisfaction: {satisfaction:.0%}")
        print(f"   ✅ Task completed: {task_completed}")
        
        # Step 6: Dynamic Modification
        if interface.components:
            print("\n6️⃣ Testing Dynamic Modification...")
            component_id = interface.components[0].id
            
            await self.modifier.modify_component(
                component_id,
                {'text': 'Live Update!', 'style': {'color': 'green'}},
                animated=True
            )
            print("   ✅ Component modified dynamically")
        
        # Step 7: Record Feedback
        print("\n7️⃣ Recording Feedback...")
        interface_id = str(id(interface))
        
        self.learning_engine.record_feedback(
            user_id=context.user_id,
            interface_id=interface_id,
            satisfaction=satisfaction,
            interaction_time=interaction_time,
            task_completed=task_completed
        )
        print("   ✅ Feedback recorded")
        
        # Step 8: Learn from Success
        print("\n8️⃣ Learning from Success...")
        self.learning_engine.learn_from_success(interface, satisfaction)
        print("   ✅ Patterns learned")
        
        # Step 9: Check Learning Persistence
        print("\n9️⃣ Checking Learning Persistence...")
        
        # Get learned patterns
        patterns = self.db.get_component_patterns(min_success_rate=0.7)
        print(f"   📚 Patterns stored: {len(patterns)}")
        
        # Get user preferences
        preferences = self.learning_engine.preference_tracker.get_strong_preferences(
            context.user_id
        )
        print(f"   👤 Preferences learned: {list(preferences.keys())}")
        
        # Get average metrics
        metrics = self.db.get_average_metrics(days=1)
        print(f"   📊 Metrics tracked: {len(metrics)} categories")
        
        # Step 10: Test Next Generation
        print("\n🔟 Testing Improved Generation...")
        
        # Use learned preferences for next request
        optimized_requirements = self.learning_engine.optimize_for_user(
            context.user_id,
            {"base": "requirements"}
        )
        print(f"   ✅ Requirements optimized with preferences")
        
        # Get improvement suggestions
        suggestions = self.learning_engine.get_improvement_suggestions("dashboard")
        print(f"   💡 Improvement suggestions: {len(suggestions)}")
        
        # Summary
        print("\n" + "="*60)
        print("✅ INTEGRATION TEST COMPLETE")
        print("="*60)
        print(f"\n📊 Test Summary:")
        print(f"   • Components generated: {len(interface.components)}")
        print(f"   • Generation time: {generation_time:.2f}ms")
        print(f"   • User satisfaction: {satisfaction:.0%}")
        print(f"   • Patterns learned: {len(patterns)}")
        print(f"   • Preferences tracked: {len(preferences)}")
        print(f"   • Improvement suggestions: {len(suggestions)}")
        
        return {
            'success': True,
            'components': len(interface.components),
            'generation_time': generation_time,
            'satisfaction': satisfaction,
            'patterns_learned': len(patterns),
            'preferences': preferences
        }
    
    def test_natural_language_parsing(self):
        """Test natural language parsing capabilities"""
        
        print("\n" + "="*60)
        print("🗣️ Testing Natural Language Parsing")
        print("="*60)
        
        test_requests = [
            "Create a simple form for user feedback",
            "Show me a list of tasks in a playful way",
            "Build a zen writing environment without distractions",
            "I need a dark theme dashboard for monitoring metrics",
            "Make a real-time chart showing server performance"
        ]
        
        results = []
        
        for request in test_requests:
            print(f"\n📝 Request: '{request}'")
            
            # Parse the request
            intent = self.builder.parser.parse(request)
            
            print(f"   Action: {intent.action.value}")
            print(f"   Type: {intent.interface_type.value if intent.interface_type else 'None'}")
            print(f"   Target: {intent.target or 'None'}")
            print(f"   Styles: {intent.style_preferences}")
            print(f"   Modifiers: {intent.modifiers}")
            
            results.append({
                'request': request,
                'intent': intent,
                'success': intent.action is not None
            })
        
        success_rate = sum(1 for r in results if r['success']) / len(results)
        print(f"\n✅ Parsing success rate: {success_rate:.0%}")
        
        return results
    
    def test_component_synthesis(self):
        """Test component synthesis capabilities"""
        
        print("\n" + "="*60)
        print("🧬 Testing Component Synthesis")
        print("="*60)
        
        synthesizer = ComponentSynthesizer()
        
        # Test different requirement sets
        requirement_sets = [
            ComponentRequirements(
                functionality="display metrics",
                data_type="chart",
                visual_style="modern",
                color_scheme="dark"
            ),
            ComponentRequirements(
                functionality="collect user input",
                interactions=["input", "submit"],
                visual_style="minimal"
            ),
            ComponentRequirements(
                functionality="show items",
                data_type="list",
                visual_style="playful",
                animation_level="rich"
            )
        ]
        
        results = []
        
        for i, reqs in enumerate(requirement_sets, 1):
            print(f"\n🔬 Test {i}: {reqs.functionality}")
            
            # Synthesize component
            component = synthesizer.synthesize(reqs)
            
            print(f"   ID: {component.id}")
            print(f"   Name: {component.name}")
            print(f"   DNA Purpose: {component.dna.purpose}")
            print(f"   Visual Style: {component.dna.visual_traits['style']}")
            print(f"   Structure Type: {component.structure.get('type')}")
            
            # Test evolution
            evolved = synthesizer.evolve_component(
                component.id,
                {'satisfaction': 0.6}
            )
            
            print(f"   Evolved ID: {evolved.id}")
            print(f"   Mutation Applied: ✅")
            
            results.append({
                'component': component,
                'evolved': evolved,
                'success': True
            })
        
        print(f"\n✅ Synthesized {len(results)} components successfully")
        
        return results
    
    def test_learning_persistence(self):
        """Test learning and persistence capabilities"""
        
        print("\n" + "="*60)
        print("💾 Testing Learning Persistence")
        print("="*60)
        
        # Create test data
        from learning_persistence import ComponentPattern, UserPreference
        
        # Test pattern storage
        print("\n📚 Testing Pattern Storage...")
        
        pattern = ComponentPattern(
            id="test_pattern_001",
            dna=ComponentRequirements(functionality="test"),
            success_rate=0.85,
            usage_count=10,
            contexts=["dashboard", "monitoring"],
            created_at=datetime.now(),
            last_used=datetime.now(),
            feedback_scores=[0.8, 0.85, 0.9],
            evolution_history=[]
        )
        
        # Save pattern
        self.db.save_component_pattern(pattern)
        print("   ✅ Pattern saved")
        
        # Retrieve patterns
        patterns = self.db.get_component_patterns(context="dashboard")
        print(f"   ✅ Retrieved {len(patterns)} patterns")
        
        # Test preference tracking
        print("\n👤 Testing Preference Tracking...")
        
        preference = UserPreference(
            user_id="test_user_001",
            preference_type="theme_mode",
            preference_value="dark",
            confidence=0.8,
            evidence_count=5,
            last_observed=datetime.now()
        )
        
        # Save preference
        self.db.save_user_preference(preference)
        print("   ✅ Preference saved")
        
        # Retrieve preferences
        preferences = self.db.get_user_preferences("test_user_001")
        print(f"   ✅ Retrieved {len(preferences)} preferences")
        
        # Test metrics storage
        print("\n📊 Testing Metrics Storage...")
        
        metrics = InterfaceMetrics(
            interface_id="test_interface_001",
            request="Test request",
            generation_time=50.0,
            component_count=5,
            user_satisfaction=0.9,
            interaction_time=30.0,
            task_completion=True,
            modifications_made=1,
            timestamp=datetime.now()
        )
        
        # Save metrics
        self.db.save_interface_metrics(metrics)
        print("   ✅ Metrics saved")
        
        # Get average metrics
        avg_metrics = self.db.get_average_metrics(days=1)
        print(f"   ✅ Calculated {len(avg_metrics)} average metrics")
        
        # Test continuous improvement
        print("\n🔄 Testing Continuous Improvement...")
        
        suggestions = self.learning_engine.get_improvement_suggestions("dashboard")
        print(f"   ✅ Generated {len(suggestions)} improvement suggestions")
        
        for suggestion in suggestions:
            print(f"      • {suggestion.get('type')}: {suggestion.get('message')}")
        
        print("\n✅ Learning persistence test complete")
        
        return {
            'patterns': len(patterns),
            'preferences': len(preferences),
            'metrics': len(avg_metrics),
            'suggestions': len(suggestions)
        }
    
    async def run_all_tests(self):
        """Run all integration tests"""
        
        print("\n" + "#"*60)
        print("#" + " "*16 + "INTEGRATION TEST SUITE" + " "*16 + "#")
        print("#"*60)
        print(f"\n🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        test_results = {}
        
        # Test 1: Natural Language Parsing
        try:
            test_results['parsing'] = self.test_natural_language_parsing()
            print("\n✅ Natural Language Parsing: PASSED")
        except Exception as e:
            print(f"\n❌ Natural Language Parsing: FAILED - {e}")
            test_results['parsing'] = None
        
        # Test 2: Component Synthesis
        try:
            test_results['synthesis'] = self.test_component_synthesis()
            print("\n✅ Component Synthesis: PASSED")
        except Exception as e:
            print(f"\n❌ Component Synthesis: FAILED - {e}")
            test_results['synthesis'] = None
        
        # Test 3: Learning Persistence
        try:
            test_results['persistence'] = self.test_learning_persistence()
            print("\n✅ Learning Persistence: PASSED")
        except Exception as e:
            print(f"\n❌ Learning Persistence: FAILED - {e}")
            test_results['persistence'] = None
        
        # Test 4: Complete Flow
        try:
            test_results['complete_flow'] = await self.test_complete_flow()
            print("\n✅ Complete Flow: PASSED")
        except Exception as e:
            print(f"\n❌ Complete Flow: FAILED - {e}")
            test_results['complete_flow'] = None
        
        # Summary
        print("\n" + "#"*60)
        print("#" + " "*20 + "TEST SUMMARY" + " "*20 + "#")
        print("#"*60)
        
        passed = sum(1 for v in test_results.values() if v is not None)
        total = len(test_results)
        
        print(f"\n📊 Results: {passed}/{total} tests passed")
        print(f"\n✅ Passed Tests:")
        for test_name, result in test_results.items():
            if result is not None:
                print(f"   • {test_name}")
        
        if passed < total:
            print(f"\n❌ Failed Tests:")
            for test_name, result in test_results.items():
                if result is None:
                    print(f"   • {test_name}")
        
        print(f"\n🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n" + "#"*60)
        
        # Clean up
        self.db.close()
        
        return test_results


def run_integration_demo():
    """Run a quick integration demonstration"""
    
    print("\n🚀 Quick Integration Demo")
    print("="*40)
    
    # Initialize components
    builder = NLInterfaceBuilder()
    bridge = SynthesisBridge()
    
    # Create user context
    context = UserContext(
        user_id="demo_user",
        expertise_level="intermediate",
        device_type="desktop"
    )
    
    # Test requests
    requests = [
        "Create a simple dashboard with dark theme",
        "Build a form for collecting feedback",
        "Show me a zen writing interface"
    ]
    
    for request in requests:
        print(f"\n📝 Request: {request}")
        
        # Build interface
        interface = builder.build_interface(request, context)
        
        # Display results
        print(f"   Components: {len(interface.components)}")
        print(f"   Layout: {interface.layout.get('type')}")
        print(f"   Theme: {interface.theme.get('mode')}")
        
        # Render (if available)
        container = bridge.render_interface(interface)
        if container:
            print(f"   Rendered: ✅")
        else:
            print(f"   Rendered: ⚠️ (Textual not available)")
    
    print("\n✅ Demo complete!")


async def main():
    """Main entry point for full test suite"""
    
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_integration_demo()
    else:
        # Run full test suite
        suite = IntegrationTestSuite()
        results = await suite.run_all_tests()
        
        # Return appropriate exit code
        if all(v is not None for v in results.values()):
            sys.exit(0)  # All tests passed
        else:
            sys.exit(1)  # Some tests failed


if __name__ == "__main__":
    # Run with asyncio
    import asyncio
    asyncio.run(main())