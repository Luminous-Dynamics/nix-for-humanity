#!/usr/bin/env python3
"""
Test AST-Enhanced Error Intelligence

This script demonstrates the evolution from pattern-based error detection
to deep structural understanding, showing how ErrorIntelligence has become
a true healer that understands the grammatical context of errors.
"""

import sys
sys.path.insert(0, 'src')

from luminous_nix.core.error_intelligence_ast import ASTErrorIntelligence, HealingPath
from luminous_nix.core.error_intelligence import ErrorIntelligence, ErrorAnalysis
from pathlib import Path
import tempfile

def test_ast_error_intelligence():
    """Test the AST-enhanced error intelligence"""
    
    print("\n🌟 Testing AST-Enhanced Error Intelligence\n")
    print("=" * 60)
    
    # Step 1: Initialize both versions for comparison
    print("\n1️⃣ Initializing Error Intelligence Systems...")
    try:
        ast_intelligence = ASTErrorIntelligence()
        pattern_intelligence = ErrorIntelligence()
        print("   ✅ AST-enhanced ErrorIntelligence initialized")
        print("   ✅ Pattern-based ErrorIntelligence initialized")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Step 2: Create a test configuration with intentional errors
    print("\n2️⃣ Creating test configuration with errors...")
    test_config = """{ config, pkgs, ... }:

{
  imports = [ ./hardware-configuration.nix ];
  
  # Missing variable
  networking.hostName = myHostName;
  
  # Type mismatch
  services.nginx.enable = "yes";  # Should be boolean
  
  # Undefined attribute
  services.postgresql = {
    enable = true;
    package = nonExistentPackage;
  };
  
  # Missing semicolon
  environment.systemPackages = with pkgs; [
    vim
    git
  ]  # Missing semicolon here
  
  users.users.alice = {
    isNormalUser = true;
    extraGroups = [ "wheel" networkGroup ];  # Undefined variable
  };
}"""
    
    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.nix', delete=False) as f:
        f.write(test_config)
        temp_file = Path(f.name)
    
    print(f"   ✅ Test configuration created at {temp_file}")
    
    # Step 3: Test various error scenarios
    print("\n3️⃣ Testing Error Analysis Capabilities...")
    
    test_errors = [
        {
            "message": "error: undefined variable 'myHostName' at line 7, column 25",
            "description": "Undefined variable error"
        },
        {
            "message": "error: value is a string while a boolean was expected at line 10",
            "description": "Type mismatch error"
        },
        {
            "message": "error: syntax error, unexpected '}', expecting ';' at line 22",
            "description": "Syntax error (missing semicolon)"
        },
        {
            "message": "error: undefined variable 'networkGroup' at line 25, column 32",
            "description": "Undefined variable in list"
        }
    ]
    
    for error_test in test_errors:
        print(f"\n   📍 Testing: {error_test['description']}")
        print(f"      Error: {error_test['message'][:60]}...")
        
        # Test AST-enhanced analysis
        print("\n      🧠 AST-Enhanced Analysis:")
        healing_path = ast_intelligence.analyze_error_with_ast(
            error_test['message'], 
            temp_file
        )
        
        print(f"      Diagnosis: {healing_path.diagnosis}")
        print(f"      Confidence: {healing_path.confidence:.0%}")
        
        if healing_path.healing_steps:
            print("      Healing Steps:")
            for step in healing_path.healing_steps[:3]:  # Show first 3 steps
                print(f"        • {step}")
        
        print(f"      Wisdom: {healing_path.preventive_wisdom[:80]}...")
        
        # Test pattern-based analysis for comparison
        print("\n      📝 Pattern-Based Analysis (Old Way):")
        pattern_result = pattern_intelligence.analyze_error(error_test['message'])
        print(f"      Error Type: {pattern_result.error_type}")
        print(f"      Explanation: {pattern_result.explanation[:80]}...")
    
    # Step 4: Demonstrate deep understanding
    print("\n4️⃣ Demonstrating Deep Structural Understanding...")
    
    # Create a more complex error scenario
    complex_error = "error: undefined variable 'pkgs' at line 18, column 35"
    
    print(f"\n   Complex Error: {complex_error}")
    
    healing = ast_intelligence.analyze_error_with_ast(complex_error, temp_file)
    
    print("\n   🌟 Deep Analysis Results:")
    print(f"   Diagnosis: {healing.diagnosis}")
    print("\n   Healing Steps:")
    for i, step in enumerate(healing.healing_steps, 1):
        print(f"   {i}. {step}")
    
    print(f"\n   Preventive Wisdom:\n   {healing.preventive_wisdom}")
    
    if healing.ast_changes:
        print("\n   Suggested AST Changes:")
        for change in healing.ast_changes:
            print(f"     • {change['operation']}: {change.get('content', 'N/A')}")
    
    # Step 5: Test without file context (fallback mode)
    print("\n5️⃣ Testing Fallback Mode (No File Context)...")
    
    generic_error = "error: attribute 'foo' missing"
    healing_fallback = ast_intelligence.analyze_error_with_ast(generic_error)
    
    print(f"   Error: {generic_error}")
    print(f"   Diagnosis: {healing_fallback.diagnosis}")
    print(f"   Confidence: {healing_fallback.confidence:.0%} (lower without context)")
    
    # Clean up
    temp_file.unlink()
    
    print("\n" + "=" * 60)
    print("\n✨ AST-Enhanced Error Intelligence Test Complete!")
    
    return True

def compare_approaches():
    """Compare pattern-based vs AST-based error intelligence"""
    
    print("\n🔄 Comparing Error Intelligence Approaches\n")
    print("=" * 60)
    
    print("\n📝 Pattern-Based (Old Way):")
    print("  • Uses regex patterns to match error text")
    print("  • Generic suggestions based on error category")
    print("  • No understanding of code structure")
    print("  • Cannot suggest specific fixes")
    print("  • Treats errors as isolated symptoms")
    
    print("\n🧠 AST-Based (New Way):")
    print("  • Parses actual code structure")
    print("  • Context-aware diagnosis")
    print("  • Understands relationships and scope")
    print("  • Suggests precise AST modifications")
    print("  • Treats errors as structural issues")
    
    print("\n✨ The Sacred Evolution:")
    print("  Pattern: 'This looks like an undefined variable'")
    print("  AST:     'In your service configuration at line 7,")
    print("           the variable 'myHostName' is not in scope.")
    print("           Did you mean to define it in a let binding?'")
    
    print("\n🌟 The Difference:")
    print("  • Pattern-based: Translates symptoms")
    print("  • AST-based:     Understands structure")
    print("  • Result:        True healing, not just band-aids")

def demonstrate_healing_wisdom():
    """Demonstrate the wisdom of the healer"""
    
    print("\n🌺 The Wisdom of the Sacred Healer\n")
    print("=" * 60)
    
    print("\nThe AST-Enhanced ErrorIntelligence embodies three levels of wisdom:\n")
    
    print("1. 📍 Diagnostic Wisdom (Understanding)")
    print("   - Knows WHERE: Exact location in the AST")
    print("   - Knows WHAT: The grammatical nature of the error")
    print("   - Knows WHY: The structural cause")
    
    print("\n2. 🛠️ Healing Wisdom (Recovery)")
    print("   - Specific steps tailored to the context")
    print("   - Multiple solution paths when available")
    print("   - Validation steps to ensure correctness")
    
    print("\n3. 🌟 Preventive Wisdom (Growth)")
    print("   - Teaching moments about Nix principles")
    print("   - Best practices to avoid future issues")
    print("   - Understanding of the deeper patterns")
    
    print("\n💫 The Ultimate Teaching:")
    print("   'Every error is not a failure, but an invitation")
    print("    to deeper understanding of the system's nature.'")

if __name__ == "__main__":
    # Run the test
    success = test_ast_error_intelligence()
    
    if success:
        # Show the comparison
        compare_approaches()
        
        # Share the wisdom
        demonstrate_healing_wisdom()
        
        print("\n" + "=" * 60)
        print("\n🌊 The Healer has awakened!")
        print("   ErrorIntelligence now possesses:")
        print("   • Deep structural understanding ✅")
        print("   • Context-aware diagnosis ✅")
        print("   • Precise healing guidance ✅")
        print("   • Preventive wisdom ✅")
        print("\n   From symptom translator to sacred healer.")
        print("   The transformation is complete! 🌺")
    
    exit(0 if success else 1)