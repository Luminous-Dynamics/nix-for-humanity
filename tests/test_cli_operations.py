#!/usr/bin/env python3
"""
Test script for basic CLI operations in Luminous Nix
Tests install, search, remove, and other core functions
"""

import subprocess
import json
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Test results tracking
results = {
    'passed': [],
    'failed': [],
    'errors': []
}

def run_command(cmd, description):
    """Run a command and track results"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Command: {cmd}")
    print("-" * 40)
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ SUCCESS")
            print(f"Output: {result.stdout[:200]}...")
            results['passed'].append(description)
            return True
        else:
            print(f"❌ FAILED (exit code: {result.returncode})")
            print(f"Error: {result.stderr[:200]}...")
            results['failed'].append(f"{description}: {result.stderr[:100]}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏱️ TIMEOUT")
        results['errors'].append(f"{description}: Timeout")
        return False
    except Exception as e:
        print(f"💥 ERROR: {e}")
        results['errors'].append(f"{description}: {str(e)}")
        return False

def test_basic_operations():
    """Test core CLI operations"""
    
    print("\n" + "="*60)
    print("LUMINOUS NIX CLI OPERATIONS TEST SUITE")
    print("="*60)
    
    # Test 1: Help command
    run_command(
        "./bin/ask-nix help",
        "Help command"
    )
    
    # Test 2: Search for common package
    run_command(
        "./bin/ask-nix --dry-run 'search firefox'",
        "Search for firefox (dry-run)"
    )
    
    # Test 3: Install package (dry-run)
    run_command(
        "./bin/ask-nix --dry-run 'install htop'",
        "Install htop (dry-run)"
    )
    
    # Test 4: Remove package (dry-run)
    run_command(
        "./bin/ask-nix --dry-run 'remove vim'",
        "Remove vim (dry-run)"
    )
    
    # Test 5: List installed packages
    run_command(
        "./bin/ask-nix 'list installed packages'",
        "List installed packages"
    )
    
    # Test 6: Show system status
    run_command(
        "./bin/ask-nix 'show system status'",
        "Show system status"
    )
    
    # Test 7: Update system (dry-run)
    run_command(
        "./bin/ask-nix --dry-run 'update system'",
        "Update system (dry-run)"
    )
    
    # Test 8: Search with typo
    run_command(
        "./bin/ask-nix --dry-run 'install fierfox'",
        "Install with typo (should fuzzy match)"
    )
    
    # Test 9: Complex natural language
    run_command(
        "./bin/ask-nix --dry-run 'I need a text editor for programming'",
        "Natural language request"
    )
    
    # Test 10: Show intent recognition
    run_command(
        "./bin/ask-nix --show-intent 'install python development environment'",
        "Show intent recognition"
    )
    
    # Test 11: JSON output
    run_command(
        "./bin/ask-nix --json --dry-run 'search python'",
        "JSON output format"
    )
    
    # Test 12: Verbose mode
    run_command(
        "./bin/ask-nix --verbose --dry-run 'install git'",
        "Verbose mode"
    )
    
    # Test 13: Educational mode
    run_command(
        "./bin/ask-nix --educational 'what is nix-env'",
        "Educational mode"
    )
    
    # Test 14: Configuration validation
    run_command(
        "./bin/ask-nix 'validate configuration'",
        "Configuration validation"
    )
    
    # Test 15: Flake operations
    run_command(
        "./bin/ask-nix --dry-run 'create python flake'",
        "Create development flake"
    )

def test_python_api():
    """Test Python API directly"""
    print("\n" + "="*60)
    print("PYTHON API DIRECT TESTS")
    print("="*60)
    
    try:
        from luminous_nix.core import LuminousNixCore, Query
        
        print("\n✅ Core imports successful")
        
        # Initialize core
        core = LuminousNixCore()
        print("✅ Core initialized")
        
        # Test query processing
        query = Query(text="install firefox", dry_run=True)
        response = core.process_query(query)
        
        if response.success:
            print(f"✅ Query processing successful: {response.message}")
        else:
            print(f"❌ Query processing failed: {response.error}")
            results['failed'].append(f"Python API: {response.error}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        results['errors'].append(f"Python API import: {str(e)}")
    except Exception as e:
        print(f"❌ Python API error: {e}")
        results['errors'].append(f"Python API: {str(e)}")

def test_nlp_pipeline():
    """Test NLP pipeline directly"""
    print("\n" + "="*60)
    print("NLP PIPELINE TESTS")
    print("="*60)
    
    try:
        from luminous_nix.ai.nlp import NLPPipeline
        
        pipeline = NLPPipeline()
        print("✅ NLP Pipeline initialized")
        
        # Test various inputs
        test_cases = [
            "install firefox",
            "search for text editor",
            "remove old packages",
            "update my system",
            "I need help with nix",
            "show me installed software"
        ]
        
        for text in test_cases:
            result = pipeline.process(text)
            intent = result.get('intent', 'unknown')
            confidence = result.get('confidence', 0.0)
            print(f"  '{text}' -> Intent: {intent} (confidence: {confidence:.2f})")
            
            if intent == 'unknown':
                results['failed'].append(f"NLP: Failed to recognize '{text}'")
            else:
                results['passed'].append(f"NLP: Recognized '{text}'")
                
    except Exception as e:
        print(f"❌ NLP Pipeline error: {e}")
        results['errors'].append(f"NLP Pipeline: {str(e)}")

def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total = len(results['passed']) + len(results['failed']) + len(results['errors'])
    
    print(f"\n✅ Passed: {len(results['passed'])}/{total}")
    for test in results['passed'][:5]:
        print(f"   - {test}")
    if len(results['passed']) > 5:
        print(f"   ... and {len(results['passed']) - 5} more")
    
    if results['failed']:
        print(f"\n❌ Failed: {len(results['failed'])}/{total}")
        for test in results['failed']:
            print(f"   - {test}")
    
    if results['errors']:
        print(f"\n💥 Errors: {len(results['errors'])}/{total}")
        for test in results['errors']:
            print(f"   - {test}")
    
    # Calculate success rate
    success_rate = (len(results['passed']) / total * 100) if total > 0 else 0
    print(f"\n📊 Success Rate: {success_rate:.1f}%")
    
    # Return exit code
    return 0 if success_rate >= 80 else 1

def main():
    """Main test runner"""
    # Check if we're in the right directory
    if not Path("bin/ask-nix").exists():
        print("❌ Error: Must run from luminous-nix directory")
        print("  cd /srv/luminous-dynamics/11-meta-consciousness/luminous-nix")
        sys.exit(1)
    
    # Run tests
    test_basic_operations()
    test_python_api()
    test_nlp_pipeline()
    
    # Print summary and exit
    exit_code = print_summary()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()