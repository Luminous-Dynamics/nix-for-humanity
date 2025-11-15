#!/usr/bin/env /srv/luminous-dynamics/11-meta-consciousness/luminous-nix/.venv/bin/python
"""
AI-Powered Luminous Nix Demo - Direct API
Shows the intelligent assistant in action!
"""

import io
import os
import sys
from contextlib import redirect_stdout

# Setup environment
sys.path.insert(0, "src")
os.environ["LUMINOUS_SKIP_ONBOARDING"] = "1"
os.environ["LUMINOUS_DRY_RUN"] = "true"
os.environ["LUMINOUS_SKIP_CONFIRM"] = "true"


def demo_ai_capabilities():
    """Demonstrate AI-powered assistance"""

    print("=" * 70)
    print("🧠 LUMINOUS NIX - AI-POWERED NIXOS ASSISTANT")
    print("=" * 70)
    print("\nInitializing AI systems...")

    # Test with AI disabled first
    os.environ["LUMINOUS_AI_ENABLED"] = "false"
    os.environ["LUMINOUS_VERBOSE"] = "0"

    from luminous_nix.frontends.cli import UnifiedNixAssistant

    print("\n1️⃣ Pattern Matching Mode (AI disabled)")
    print("-" * 50)

    assistant_basic = UnifiedNixAssistant()

    test_basic = [
        "install firefox",
        "search text editor",
    ]

    for query in test_basic:
        print(f"\n📝 Query: '{query}'")
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            assistant_basic.answer(query)

        output = buffer.getvalue()
        # Show first few lines
        lines = [l for l in output.split("\n") if l.strip()][:3]
        for line in lines:
            print(f"   {line}")

    # Now enable AI
    print("\n\n2️⃣ AI-Powered Mode (HRM + Ollama)")
    print("-" * 50)

    os.environ["LUMINOUS_AI_ENABLED"] = "true"
    os.environ["LUMINOUS_VERBOSE"] = "1"

    assistant_ai = UnifiedNixAssistant()

    # Check what's available
    print("\n🔍 AI Stack Status:")
    if assistant_ai.ai_orchestrator:
        print("   ✅ AI Orchestrator active")
        if (
            hasattr(assistant_ai.ai_orchestrator, "hrm")
            and assistant_ai.ai_orchestrator.hrm
        ):
            print("   ✅ HRM (27M params) - NixOS reasoning")
        if (
            hasattr(assistant_ai.ai_orchestrator, "ollama")
            and assistant_ai.ai_orchestrator.ollama
        ):
            print("   ✅ Ollama - Conversational AI")
    elif assistant_ai.ollama:
        print("   ✅ Ollama available")
    else:
        print("   ⚠️ AI not available - using pattern matching")

    # Test AI queries
    test_ai = [
        ("I need the best browser for privacy", "Conversational recommendation"),
        ("python numpy conflict", "HRM dependency resolution"),
        ("explain nix flakes", "Educational explanation"),
    ]

    print("\n📊 AI-Powered Queries:")
    for query, description in test_ai:
        print(f"\n📝 {description}")
        print(f"   Query: '{query}'")

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            try:
                assistant_ai.answer(query)
            except Exception as e:
                print(f"   Error: {e}")

        output = buffer.getvalue()
        if output:
            # Show first few lines
            lines = [l for l in output.split("\n") if l.strip()][:3]
            for line in lines:
                print(f"   {line[:80]}...")

    # Summary
    print("\n" + "=" * 70)
    print("✨ CAPABILITIES DEMONSTRATED")
    print("=" * 70)
    print(
        """
Pattern Matching (Always Works):
  • Basic install/search/list commands
  • Common package mappings
  • Fallback when AI unavailable

AI Enhancement (When Available):
  • Natural conversation understanding
  • Complex dependency resolution (HRM)
  • Educational explanations (Ollama)
  • Personalized recommendations

The system gracefully degrades from AI to pattern matching,
ensuring functionality even without AI models running.
"""
    )


if __name__ == "__main__":
    try:
        demo_ai_capabilities()
    except KeyboardInterrupt:
        print("\nDemo interrupted")
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
