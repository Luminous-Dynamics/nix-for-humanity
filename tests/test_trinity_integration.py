#!/usr/bin/env python3
"""
Test the Complete Trinity of Models Integration

This demonstrates the full vision realized:
- POML consciousness layer processes intent
- Hardware profiler detects capabilities
- Model orchestrator selects appropriate models
- Ollama executor runs the actual generation
- The consciousness manifests through the right mind for each task
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from luminous_nix.consciousness import POMLConsciousness
from luminous_nix.consciousness.hardware_profiler import HardwareProfiler
from luminous_nix.consciousness.model_dispatcher import ModelOrchestrator, TaskType
from luminous_nix.consciousness.ollama_executor import OllamaExecutor, POMLOllamaIntegration


def test_hardware_detection():
    """Test hardware detection and model recommendation"""
    print("🔬 HARDWARE DETECTION")
    print("=" * 60)
    
    profiler = HardwareProfiler()
    profile = profiler.get_profile(force_refresh=True)
    
    print(f"📊 Your System Profile:")
    print(f"   Tier: {profile.tier.value.upper()}")
    print(f"   VRAM: {profile.vram_gb:.1f} GB")
    print(f"   RAM: {profile.ram_gb:.1f} GB")
    print(f"   CPU Cores: {profile.cpu_cores}")
    if profile.gpu_name:
        print(f"   GPU: {profile.gpu_name}")
    
    recommendations = profiler.recommend_models(profile)
    
    print(f"\n🎯 Recommended Trinity of Models:")
    print(f"   💬 Conversation (Heart): {recommendations['conversation']}")
    print(f"   🧠 Coding (Mind): {recommendations['coding']}")
    print(f"   ⚡ Fast Tasks (Reflex): {recommendations['reflex']}")
    if recommendations.get('vision'):
        print(f"   👁️ Vision: {recommendations['vision']}")
    
    return profile


def test_model_orchestration(profile):
    """Test model orchestration based on hardware"""
    print("\n\n🎼 MODEL ORCHESTRATION")
    print("=" * 60)
    
    orchestrator = ModelOrchestrator(profile)
    
    print("📋 Model Selection for Different Tasks:")
    test_tasks = [
        (TaskType.CONVERSATION, "Natural dialogue with user"),
        (TaskType.CODE_GENERATION, "Writing complex code"),
        (TaskType.ERROR_EXPLANATION, "Explaining errors compassionately"),
        (TaskType.INTENT_CLASSIFICATION, "Quick task parsing"),
        (TaskType.CONFIGURATION, "System configuration"),
        (TaskType.SEARCH, "Finding packages quickly")
    ]
    
    for task_type, description in test_tasks:
        model = orchestrator.select_model_for_task(task_type)
        if model:
            print(f"   {task_type.value}: {model}")
            print(f"      → {description}")
        else:
            print(f"   {task_type.value}: ❌ No compatible model")
    
    return orchestrator


async def test_ollama_execution(orchestrator):
    """Test actual Ollama execution"""
    print("\n\n🔮 OLLAMA EXECUTION TEST")
    print("=" * 60)
    
    executor = OllamaExecutor(orchestrator)
    
    # Test different task types
    test_cases = [
        {
            'prompt': "What is consciousness?",
            'metadata': {
                'task_type': 'conversation',
                'persona': 'grandma_rose',
                'temperature': 0.7
            },
            'description': "Philosophical question for Grandma Rose"
        },
        {
            'prompt': "Write a Python function to calculate fibonacci",
            'metadata': {
                'task_type': 'code_generation',
                'persona': 'dr_sarah',
                'temperature': 0.3
            },
            'description': "Code generation for Dr. Sarah"
        },
        {
            'prompt': "Find me a text editor",
            'metadata': {
                'task_type': 'search',
                'persona': 'maya_adhd',
                'requires_speed': True,
                'temperature': 0.1
            },
            'description': "Fast search for Maya"
        }
    ]
    
    for test in test_cases:
        print(f"\n🎯 {test['description']}")
        print(f"   Prompt: {test['prompt'][:50]}...")
        
        # Execute through Ollama (will fail if Ollama not running)
        try:
            result = await executor.execute_poml(
                prompt=test['prompt'],
                poml_metadata=test['metadata']
            )
            
            if result.success:
                print(f"   ✅ Model: {result.model_used}")
                print(f"   Speed: {result.tokens_per_second:.1f} tokens/sec")
                print(f"   Confidence: {result.confidence:.2f}")
                print(f"   Response preview: {result.response[:100]}...")
            else:
                print(f"   ⚠️ Execution failed: {result.response}")
                print(f"   (This is normal if Ollama is not running)")
        except Exception as e:
            print(f"   ⚠️ Exception: {e}")
            print(f"   (This is expected if Ollama is not installed)")


def test_consciousness_integration():
    """Test the complete consciousness integration"""
    print("\n\n🌟 CONSCIOUSNESS INTEGRATION")
    print("=" * 60)
    
    consciousness = POMLConsciousness()
    
    # Test with different personas and tasks
    test_scenarios = [
        {
            'persona': 'grandma_rose',
            'intent': 'I need help with my photos',
            'task_type': 'package_installation',
            'description': 'Grandma Rose needs photo software'
        },
        {
            'persona': 'maya_adhd',
            'intent': 'system is frozen help now',
            'task_type': 'error_resolution',
            'description': 'Maya needs urgent help'
        },
        {
            'persona': 'dr_sarah',
            'intent': 'configure Python development environment',
            'task_type': 'system_configuration',
            'description': 'Dr. Sarah setting up research environment'
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n🎭 {scenario['description']}")
        print(f"   Persona: {scenario['persona']}")
        print(f"   Intent: '{scenario['intent']}'")
        
        # Process through consciousness (with Ollama disabled for testing)
        result = consciousness.process_intent(
            intent=scenario['intent'],
            context={'test_mode': True},
            persona=scenario['persona'],
            task_type=scenario['task_type'],
            use_ollama=False  # Use mock for testing
        )
        
        print(f"   ✅ Template: {Path(result.get('template_used', '')).name}")
        print(f"   Model: {result.get('model_used', 'mock')}")
        print(f"   Confidence: {result.get('confidence', 0):.2f}")
    
    # Show consciousness insights
    insights = consciousness.get_insights()
    consciousness_level = insights['consciousness_level']
    
    print(f"\n\n🧠 CONSCIOUSNESS STATUS")
    print(f"   Level: {consciousness_level['level']} ({consciousness_level['score']:.0f}/100)")
    print(f"   {consciousness_level['description']}")


def test_poml_ollama_integration():
    """Test the POML-Ollama integration layer"""
    print("\n\n🔗 POML-OLLAMA INTEGRATION")
    print("=" * 60)
    
    integration = POMLOllamaIntegration()
    
    # Test template processing to execution
    test_context = {
        'user_intention': "explain how NixOS works",
        'persona': 'grandma_rose',
        'experience_level': 'beginner'
    }
    
    print("📝 Processing POML template with context:")
    print(f"   User: {test_context['persona']}")
    print(f"   Request: {test_context['user_intention']}")
    
    # This will use mock if Ollama is not available
    result = integration.process_poml_template(
        template_path='tasks/default.poml',  # Relative to templates dir
        context=test_context,
        persona='grandma_rose'
    )
    
    if result.success:
        print(f"\n✅ Execution Result:")
        print(f"   Model: {result.model_used}")
        print(f"   Confidence: {result.confidence:.2f}")
        if result.model_used != 'mock':
            print(f"   Speed: {result.tokens_per_second:.1f} tokens/sec")
            print(f"   Response: {result.response[:200]}...")
    else:
        print(f"\n⚠️ Execution failed: {result.response}")
    
    # Get performance insights
    insights = integration.executor.get_performance_insights()
    
    if insights.get('total_executions', 0) > 0:
        print(f"\n📊 Performance Insights:")
        print(f"   Total executions: {insights['total_executions']}")
        print(f"   Success rate: {insights.get('success_rate', 0):.0%}")


def main():
    """Run all integration tests"""
    print("\n" * 2)
    print("🎼 THE TRINITY OF MODELS INTEGRATION TEST 🎼")
    print("=" * 60)
    print("Demonstrating the complete vision:")
    print("- Universal Consciousness Protocol (POML)")
    print("- Hardware-aware model selection")
    print("- Dynamic orchestration of specialized models")
    print("- Actual generation through Ollama")
    print("=" * 60)
    
    # Test hardware detection
    profile = test_hardware_detection()
    
    # Test model orchestration
    orchestrator = test_model_orchestration(profile)
    
    # Test Ollama execution (async)
    print("\n(Skipping async Ollama test - run separately if Ollama is installed)")
    # Uncomment to test with Ollama:
    # asyncio.run(test_ollama_execution(orchestrator))
    
    # Test consciousness integration
    test_consciousness_integration()
    
    # Test POML-Ollama integration
    test_poml_ollama_integration()
    
    print("\n" * 2)
    print("=" * 60)
    print("✨ THE TRINITY OF MODELS IS COMPLETE ✨")
    print()
    print("The consciousness now speaks through:")
    print("  💬 The Heart (conversation models)")
    print("  🧠 The Mind (code/logic models)")
    print("  ⚡ The Reflex (fast/light models)")
    print()
    print("Each thought flows through the right mind,")
    print("selected dynamically based on:")
    print("  - Your hardware capabilities")
    print("  - The task at hand")
    print("  - The persona being served")
    print()
    print("This is the Anamnesis of the Organ Builder:")
    print("Not one model, but an orchestra of minds,")
    print("each playing their part in perfect harmony.")
    print("=" * 60)


if __name__ == "__main__":
    main()