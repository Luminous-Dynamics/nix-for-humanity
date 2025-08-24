#!/usr/bin/env python3
"""
Test the configuration generation through the ask-nix flow
"""

import sys
import os

# Add all necessary paths
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
sys.path.insert(0, os.path.join(os.path.dirname(script_dir), 'scripts'))

# Import the modern knowledge engine using importlib for hyphenated filename
import importlib.util
spec = importlib.util.spec_from_file_location(
    "nix_knowledge_engine_modern", 
    os.path.join(os.path.dirname(script_dir), 'scripts', 'nix-knowledge-engine-modern.py')
)
nix_knowledge_engine_modern = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nix_knowledge_engine_modern)
ModernNixOSKnowledgeEngine = nix_knowledge_engine_modern.ModernNixOSKnowledgeEngine

# Test queries
test_queries = [
    "generate configuration for web server with nginx",
    "create config for desktop with gnome",
    "make me a development system configuration with docker",
    "build configuration for minimal server with ssh"
]

print("=== Testing Configuration Generation Through Knowledge Engine ===\n")

engine = ModernNixOSKnowledgeEngine()

for query in test_queries:
    print(f"Query: {query}")
    print("-" * 50)
    
    # Extract intent
    intent = engine.extract_intent(query)
    print(f"Detected action: {intent['action']}")
    
    if intent['action'] == 'generate_config':
        print(f"Description: {intent.get('description', 'N/A')}")
        
        # Get solution
        solution = engine.get_solution(intent)
        
        # Format response
        response = engine.format_response(intent, solution)
        print(f"\nResponse:\n{response}")
    else:
        print(f"Wrong intent detected. Expected 'generate_config' but got '{intent['action']}'")
    
    print("\n" + "="*70 + "\n")

print("\n✅ Configuration generation test complete!")

# Also show the actual command that would be generated
print("\n📋 Example commands that would be generated:")
for query in test_queries:
    intent = engine.extract_intent(query)
    if intent['action'] == 'generate_config':
        print(f'ask-nix config generate "{intent.get("description", query)}"')