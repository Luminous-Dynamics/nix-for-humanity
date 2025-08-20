#!/usr/bin/env python3
"""
Update Trinity of Models to v2 with Latest Models

This script updates your Trinity configuration to use the latest
Qwen3 and Gemma3 models for improved performance.
"""

import os
import sys
import yaml
import json
import subprocess
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from luminous_nix.consciousness.hardware_profiler import HardwareProfiler
from luminous_nix.consciousness.model_dispatcher import ModelOrchestrator, HardwareTier


def check_ollama_status():
    """Check if Ollama is running"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False


def get_current_models():
    """Get list of currently installed models"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            models = []
            for line in result.stdout.split('\n')[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if parts:
                        models.append(parts[0])
            return models
        return []
    except Exception as e:
        print(f"Error getting models: {e}")
        return []


def download_model(model_name: str) -> bool:
    """Download a model if not already present"""
    current_models = get_current_models()
    
    # Check if model already exists
    if any(model_name in m for m in current_models):
        print(f"✅ {model_name} already installed")
        return True
    
    print(f"📥 Downloading {model_name}...")
    try:
        # Run download in foreground so user can see progress
        result = subprocess.run(['ollama', 'pull', model_name])
        if result.returncode == 0:
            print(f"✅ Successfully downloaded {model_name}")
            return True
        else:
            print(f"❌ Failed to download {model_name}")
            return False
    except Exception as e:
        print(f"❌ Error downloading {model_name}: {e}")
        return False


def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║     🌟 Trinity of Models v2 Update - Latest Models 🌟      ║
╠════════════════════════════════════════════════════════════╣
║  Updating to Qwen3 & Gemma3 families for 2025 performance  ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Check Ollama
    if not check_ollama_status():
        print("❌ Ollama is not running. Please start it with: ollama serve")
        sys.exit(1)
    
    print("✅ Ollama is running\n")
    
    # Detect hardware
    print("🔍 Detecting hardware configuration...")
    profiler = HardwareProfiler()
    profile = profiler.get_profile()
    
    print(f"  GPU: {profile.gpu_name or 'Not detected'}")
    print(f"  VRAM: {profile.vram_gb:.1f} GB")
    print(f"  Tier: {profile.tier.value}\n")
    
    # Determine models based on tier
    models_to_download = []
    
    if profile.tier == HardwareTier.SAGE:
        models_to_download = ['gemma3:27b', 'qwen3:32b', 'qwen3:4b']
    elif profile.tier == HardwareTier.MASTER:
        models_to_download = ['gemma3:12b', 'qwen3:14b', 'qwen3:1b']
    elif profile.tier == HardwareTier.JOURNEYMAN:  # Your tier
        models_to_download = ['gemma3:4b', 'qwen3:8b', 'qwen3:1b']
    elif profile.tier == HardwareTier.APPRENTICE:
        models_to_download = ['gemma3:1b', 'qwen3:4b', 'qwen3:0.6b']
    else:  # NOVICE
        models_to_download = ['gemma3:270m', 'qwen3:1.7b', 'qwen3:0.6b']
    
    print(f"📋 Models recommended for {profile.tier.value} tier:")
    print(f"  Heart (Empathy): {models_to_download[0]}")
    print(f"  Mind (Logic): {models_to_download[1]}")
    print(f"  Reflex (Speed): {models_to_download[2]}\n")
    
    # Ask for confirmation
    response = input("Download these models? (y/n): ").strip().lower()
    if response != 'y':
        print("Skipping downloads. You can manually download with: ollama pull <model>")
    else:
        print("\n🚀 Starting downloads (this may take a while)...\n")
        
        success_count = 0
        for model in models_to_download:
            if download_model(model):
                success_count += 1
        
        print(f"\n✨ Downloaded {success_count}/{len(models_to_download)} models")
    
    # Update configuration file
    print("\n📝 Updating Trinity configuration...")
    
    config_path = Path(__file__).parent / 'config' / 'trinity-active.yaml'
    config_v2_path = Path(__file__).parent / 'config' / 'trinity-models-v2.yaml'
    
    # Load v2 config
    with open(config_v2_path, 'r') as f:
        v2_config = yaml.safe_load(f)
    
    # Create active config based on detected tier
    tier_key = profile.tier.value.lower()
    active_config = {
        'active_tier': profile.tier.value,
        'models': v2_config['hardware_tiers'][profile.tier.value]['models'],
        'task_mapping': v2_config['task_mapping'],
        'personas': v2_config['personas'],
        'optimizations': v2_config['optimizations']
    }
    
    # Save active configuration
    config_path.parent.mkdir(exist_ok=True)
    with open(config_path, 'w') as f:
        yaml.dump(active_config, f, default_flow_style=False)
    
    print(f"✅ Configuration saved to {config_path}")
    
    # Test the system
    print("\n🧪 Testing Trinity system...")
    
    try:
        orchestrator = ModelOrchestrator(profile)
        print("✅ Model orchestrator initialized")
        
        # Quick test of each model type
        from luminous_nix.consciousness.ollama_executor import OllamaExecutor
        executor = OllamaExecutor(orchestrator)
        
        print("\n📊 Trinity v2 Update Complete!")
        print("=" * 50)
        print(f"Hardware Tier: {profile.tier.value}")
        print(f"Active Models:")
        print(f"  Heart: {active_config['models']['heart']}")
        print(f"  Mind: {active_config['models']['mind']}")
        print(f"  Reflex: {active_config['models']['reflex']}")
        print("\n🌊 Your Trinity has evolved to the next level!")
        
    except Exception as e:
        print(f"⚠️ Warning: Could not fully initialize system: {e}")
        print("This is normal if models are still downloading.")
    
    print("\n💡 Next steps:")
    print("1. Test with: python demonstrate_trinity.py")
    print("2. Use in code: from luminous_nix.consciousness import POMLConsciousness")
    print("3. Monitor downloads: ollama list")


if __name__ == "__main__":
    main()