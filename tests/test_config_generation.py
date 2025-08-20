#!/usr/bin/env python3
"""
Test the configuration generation feature
"""

import sys
import os

# Add the project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts'))

# Test direct config generator
print("=== Testing Config Generator Directly ===")
try:
    from luminous_nix.core.config_generator import NixConfigGenerator
    
    generator = NixConfigGenerator()
    
    # Test parsing intent
    test_descriptions = [
        "web server with nginx and postgresql",
        "desktop with KDE plasma",
        "development machine with docker and vscode",
        "minimal server with ssh"
    ]
    
    for desc in test_descriptions:
        print(f"\nTesting: {desc}")
        intent = generator.parse_intent(desc)
        print(f"Parsed intent: {intent}")
        
        # Check for conflicts
        conflicts = generator.check_conflicts(intent["modules"])
        if conflicts:
            print(f"Conflicts detected: {conflicts}")
        
        # Generate config
        config = generator.generate_config(intent)
        print(f"Generated config preview (first 200 chars):")
        print(config[:200] + "...")
        
except Exception as e:
    print(f"Error testing config generator: {e}")

# Test through knowledge engine
print("\n\n=== Testing Through Knowledge Engine ===")
try:
    from nix_knowledge_engine_modern import ModernNixOSKnowledgeEngine
    
    engine = ModernNixOSKnowledgeEngine()
    
    test_queries = [
        "generate configuration for web server with nginx",
        "create config for desktop with gnome",
        "make me a development system configuration",
        "build configuration for minimal server"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        
        # Extract intent
        intent = engine.extract_intent(query)
        print(f"Intent: {intent}")
        
        # Get solution
        solution = engine.get_solution(intent)
        print(f"Solution found: {solution.get('found', False)}")
        
        # Format response
        if solution.get('found'):
            response = engine.format_response(intent, solution)
            print("Response preview:")
            print(response[:300] + "...")
            
except Exception as e:
    print(f"Error testing through knowledge engine: {e}")

# Test through unified backend
print("\n\n=== Testing Through Unified Backend ===")
try:
    from luminous_nix.core.engine import UnifiedNixBackend, IntentType
    
    backend = UnifiedNixBackend()
    
    test_queries = [
        "generate config for nginx web server",
        "create configuration for kde desktop"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        
        # Extract intent
        intent = backend.extract_intent(query)
        print(f"Intent type: {intent.type}")
        print(f"Intent entities: {intent.entities}")
        
        # Process intent
        context = {'personality': 'friendly'}
        response = backend.process_intent(intent, context)
        
        print(f"Success: {response.success}")
        print(f"Response preview: {response.text[:200]}...")
        
except Exception as e:
    print(f"Error testing through unified backend: {e}")

print("\n\n=== Config Generation Feature Test Complete ===")