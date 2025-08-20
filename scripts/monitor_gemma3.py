#!/usr/bin/env python3
"""
Gemma 3 and New Model Monitor

Checks for availability of Gemma 3 and other new models in Ollama.
Can be run manually or via cron to alert when new models arrive.
"""

import subprocess
import json
from datetime import datetime
from pathlib import Path


def check_model_availability():
    """Check if specific models are available in Ollama"""
    
    # Models we're specifically waiting for
    awaited_models = {
        'gemma3:270m': 'Gemma 3 270M - Ultra lightweight',
        'gemma3:1b': 'Gemma 3 1B - Fast reflex model',
        'gemma3:4b': 'Gemma 3 4B - Balanced conversation',
        'gemma3:12b': 'Gemma 3 12B - Powerful reasoning',
        'gemma3:27b': 'Gemma 3 27B - Maximum capability',
        'llama3:latest': 'Llama 3 - Latest from Meta',
        'mixtral:latest': 'Mixtral - MoE architecture',
        'qwen2.5:latest': 'Qwen 2.5 - Enhanced coding',
        'deepseek-coder:latest': 'DeepSeek Coder - Specialized for code'
    }
    
    available = []
    newly_available = []
    
    # Check what's in local Ollama
    try:
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        local_models = result.stdout if result.returncode == 0 else ""
    except:
        local_models = ""
    
    # Check each awaited model
    for model_tag, description in awaited_models.items():
        # First check if it's local
        if model_tag in local_models:
            available.append((model_tag, description, 'local'))
            continue
        
        # Then check if it can be pulled
        try:
            check = subprocess.run(
                ['ollama', 'show', model_tag],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # If it mentions pulling or has info, it exists in registry
            if check.returncode == 0 or 'pulling' in check.stderr.lower():
                available.append((model_tag, description, 'registry'))
                newly_available.append(model_tag)
        except:
            pass
    
    # Log results
    log_file = Path.home() / '.luminous-nix' / 'model-watch.log'
    log_file.parent.mkdir(exist_ok=True)
    
    # Check what we found before
    previously_found = set()
    if log_file.exists():
        with open(log_file) as f:
            for line in f:
                if 'AVAILABLE:' in line:
                    model = line.split('AVAILABLE:')[1].split()[0]
                    previously_found.add(model)
    
    # Log current findings
    with open(log_file, 'a') as f:
        f.write(f"\n{datetime.now().isoformat()} - Check Results:\n")
        for model_tag, desc, location in available:
            f.write(f"  AVAILABLE: {model_tag} ({location}) - {desc}\n")
            
            # Alert if this is newly discovered
            if model_tag not in previously_found:
                f.write(f"  🎉 NEW DISCOVERY: {model_tag} is now available!\n")
    
    # Print results
    print("=" * 70)
    print("🔍 MODEL AVAILABILITY CHECK")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    if available:
        print("✅ AVAILABLE MODELS:")
        for model_tag, desc, location in available:
            status = "📦 Local" if location == 'local' else "☁️ Registry"
            print(f"  {status} {model_tag}")
            print(f"      {desc}")
            
            if model_tag not in previously_found:
                print(f"      🎉 NEWLY DISCOVERED!")
    else:
        print("⏳ No awaited models available yet")
    
    # Special alert for Gemma 3
    gemma3_models = [m for m, _, _ in available if m.startswith('gemma3:')]
    if gemma3_models:
        print("\n" + "🌟" * 20)
        print("🎊 GEMMA 3 IS AVAILABLE! 🎊")
        print("Models:", ", ".join(gemma3_models))
        print("Run: ollama pull gemma3:4b  # or other variant")
        print("🌟" * 20)
    
    print()
    print("Next steps:")
    if newly_available:
        print(f"  1. Pull new models: ollama pull {newly_available[0]}")
        print(f"  2. Run curator: python test_model_curator.py")
        print(f"  3. Models will auto-integrate into consciousness")
    else:
        print("  • Add to cron: 0 */6 * * * python3 monitor_gemma3.py")
        print("  • Run curator when new models appear")
    
    return available


if __name__ == "__main__":
    check_model_availability()