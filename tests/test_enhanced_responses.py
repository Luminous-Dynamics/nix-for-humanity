#!/usr/bin/env python3
"""
Test the enhanced two-path response system
"""

import os
import sys
from pathlib import Path

# Add the backend to the path
sys.path.insert(0, str(Path(__file__).parent))

# Enable enhanced responses
os.environ['NIX_HUMANITY_ENHANCED_RESPONSES'] = 'true'

from nix_humanity.core.responses import ResponseGenerator, Response

def test_responses():
    """Test various response types"""
    generator = ResponseGenerator()
    
    print("🌟 Testing Enhanced Two-Path Response System\n")
    print("=" * 80)
    
    # Test 1: Package Installation
    print("\n📦 Test 1: Installing Firefox")
    print("-" * 40)
    
    response = generator.generate('install_package', {'package': 'firefox'})
    print(response.format_for_cli())
    
    print("\n" + "=" * 80)
    
    # Test 2: System Update
    print("\n🔄 Test 2: System Update")
    print("-" * 40)
    
    response = generator.generate('update_system', {})
    print(response.format_for_cli())
    
    print("\n" + "=" * 80)
    
    # Test 3: Service Enable
    print("\n⚡ Test 3: Enable SSH Service")
    print("-" * 40)
    
    response = generator.generate('enable_service', {'service': 'ssh'})
    print(response.format_for_cli())
    
    print("\n" + "=" * 80)
    
    # Test 4: Remove Package
    print("\n🗑️ Test 4: Remove Package")
    print("-" * 40)
    
    response = generator.generate('remove_package', {'package': 'vim'})
    print(response.format_for_cli())
    
    print("\n✅ All tests complete!")

if __name__ == "__main__":
    test_responses()