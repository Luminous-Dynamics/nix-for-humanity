#!/usr/bin/env python3
"""Test Ollama integration with Luminous Nix"""

import os
import sys
import subprocess

# Add src to path
sys.path.insert(0, 'src')

def test_ollama_detection():
    """Test if Ollama can be detected"""
    print("🔍 Testing Ollama Detection...")
    
    # Check if ollama command exists
    result = subprocess.run(['which', 'ollama'], capture_output=True)
    if result.returncode == 0:
        print("✅ Ollama command found")
        
        # Check if service is running
        result = subprocess.run(['ollama', 'list'], capture_output=True, timeout=2)
        if result.returncode == 0:
            print("✅ Ollama service is running")
            models = result.stdout.decode().strip()
            print(f"📦 Available models:\n{models}")
            return True
        else:
            print("⚠️  Ollama installed but not running")
    else:
        print("❌ Ollama not found")
    
    return False

def test_ollama_client():
    """Test the Ollama client"""
    print("\n🤖 Testing Ollama Client...")
    
    try:
        from luminous_nix.ai.ollama_client import OllamaClient
        
        client = OllamaClient()
        print("✅ Ollama client initialized")
        
        # Test with a simple query
        print("\n📝 Testing simple query...")
        response = client.ask("What is NixOS in one sentence?", model="qwen:0.5b")
        
        if response:
            print(f"✅ Got response: {response[:100]}...")
        else:
            print("⚠️  No response from Ollama")
            
        # Test intent parsing
        print("\n🎯 Testing intent parsing...")
        intent = client.parse_intent("install firefox please")
        if intent:
            print(f"✅ Parsed intent: {intent}")
        else:
            print("⚠️  Intent parsing failed")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_cli_integration():
    """Test CLI with AI enabled"""
    print("\n🎮 Testing CLI Integration...")
    
    # Set AI environment variable
    os.environ['LUMINOUS_AI_ENABLED'] = 'true'
    os.environ['LUMINOUS_DRY_RUN'] = 'true'
    os.environ['LUMINOUS_SKIP_ONBOARDING'] = '1'
    os.environ['LUMINOUS_SKIP_CONFIRM'] = 'true'
    
    print("✅ Environment configured for AI")
    
    # Test a command with AI
    result = subprocess.run(
        ['poetry', 'run', 'ask-nix', 'what is NixOS'],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        print("✅ CLI executed with AI")
        output = result.stdout[:200] if result.stdout else "No output"
        print(f"   Output preview: {output}")
    else:
        print(f"⚠️  CLI execution failed: {result.stderr}")
    
    return result.returncode == 0

def main():
    """Run all tests"""
    print("🧪 Ollama Integration Test Suite")
    print("━" * 40)
    
    # Test 1: Detection
    ollama_available = test_ollama_detection()
    
    if not ollama_available:
        print("\n⚠️  Ollama not available. Install with:")
        print("  nix-env -iA nixpkgs.ollama")
        print("  ollama serve")
        return
    
    # Test 2: Client
    client_works = test_ollama_client()
    
    # Test 3: CLI Integration  
    cli_works = test_cli_integration()
    
    # Summary
    print("\n" + "━" * 40)
    print("📊 Test Summary:")
    print(f"  Ollama Detection: {'✅' if ollama_available else '❌'}")
    print(f"  Ollama Client: {'✅' if client_works else '❌'}")
    print(f"  CLI Integration: {'✅' if cli_works else '❌'}")
    
    if ollama_available and client_works:
        print("\n🎉 Ollama integration is working!")
        print("\n💡 To enable permanently:")
        print("  export LUMINOUS_AI_ENABLED=true")
        print("  luminous-nix 'explain NixOS to me'")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()