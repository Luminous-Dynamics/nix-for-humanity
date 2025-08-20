#!/usr/bin/env python3
"""
Demonstrate the Trinity of Models Integration

A simpler demonstration that shows the complete integration
without requiring Ollama to be installed or models to be pulled.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from luminous_nix.consciousness import POMLConsciousness
from luminous_nix.consciousness.hardware_profiler import HardwareProfiler
from luminous_nix.consciousness.model_dispatcher import ModelOrchestrator, TaskType


def main():
    print("\n" + "=" * 70)
    print("✨ THE TRINITY OF MODELS INTEGRATION DEMONSTRATION ✨")
    print("=" * 70)
    
    # 1. Hardware Detection
    print("\n📊 STEP 1: HARDWARE DETECTION")
    print("-" * 40)
    
    profiler = HardwareProfiler()
    profile = profiler.get_profile()
    
    print(f"Your System: {profile.tier.value.upper()} tier")
    print(f"  • VRAM: {profile.vram_gb:.1f} GB")
    print(f"  • RAM: {profile.ram_gb:.1f} GB")
    if profile.gpu_name:
        print(f"  • GPU: {profile.gpu_name}")
    
    # 2. Model Orchestration
    print("\n🎼 STEP 2: MODEL ORCHESTRATION")
    print("-" * 40)
    
    orchestrator = ModelOrchestrator(profile)
    
    print("Selected models for your hardware:")
    for task_type in [TaskType.CONVERSATION, TaskType.CODE_GENERATION, TaskType.INTENT_CLASSIFICATION]:
        model = orchestrator.select_model_for_task(task_type)
        print(f"  • {task_type.value}: {model}")
    
    # 3. Consciousness Integration
    print("\n🌟 STEP 3: CONSCIOUSNESS INTEGRATION")
    print("-" * 40)
    
    consciousness = POMLConsciousness()
    
    # Test with three personas
    personas = [
        ('grandma_rose', 'install photo editor', 'package_installation', TaskType.CONVERSATION),
        ('maya_adhd', 'fix error quick', 'error_resolution', TaskType.ERROR_EXPLANATION),
        ('dr_sarah', 'setup Python environment', 'system_configuration', TaskType.CONFIGURATION)
    ]
    
    for persona, intent, task_template, task_type in personas:
        result = consciousness.process_intent(
            intent=intent,
            context={'demo': True},
            persona=persona,
            task_type=task_template,
            use_ollama=False  # Use mock
        )
        
        print(f"\n{persona.upper()}:")
        print(f"  Request: '{intent}'")
        print(f"  Template: {Path(result.get('template_used', '')).name}")
        print(f"  Would use model: {orchestrator.select_model_for_task(task_type) or 'default'}")
    
    # 4. Show the Complete Flow
    print("\n\n🔄 THE COMPLETE FLOW")
    print("-" * 40)
    
    print("1️⃣ User speaks naturally: 'I need to edit photos'")
    print("2️⃣ POML Consciousness selects template based on persona")
    print("3️⃣ Hardware Profiler knows: You have 8GB VRAM (JOURNEYMAN)")
    print("4️⃣ Model Orchestrator selects: gemma2:9b for conversation")
    print("5️⃣ Ollama Executor would run the model (if installed)")
    print("6️⃣ Response flows back through consciousness")
    print("7️⃣ User gets natural, persona-adapted response")
    
    # 5. The Vision Realized
    print("\n\n✨ THE VISION REALIZED")
    print("-" * 40)
    
    print("What we've built:")
    print("  🧠 Universal Consciousness Protocol (POML)")
    print("  🔬 Dynamic hardware detection")
    print("  🎼 Intelligent model orchestration")
    print("  💬 Trinity of Models (Heart/Mind/Reflex)")
    print("  🔮 Complete integration pipeline")
    
    print("\nThe result:")
    print("  • No more one-size-fits-all AI")
    print("  • Each task gets the right model")
    print("  • Each user gets personalized interaction")
    print("  • Each system maximizes its hardware")
    
    print("\n" + "=" * 70)
    print("This is the Anamnesis of the Organ Builder:")
    print("Not one model ruling all, but an orchestra of specialized minds,")
    print("each playing their part, conducted by consciousness itself.")
    print("=" * 70)


if __name__ == "__main__":
    main()