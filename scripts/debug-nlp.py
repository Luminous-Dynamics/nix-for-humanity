#!/usr/bin/env python3
"""Debug NLP processing to understand what's being returned."""

import sys
sys.path.insert(0, 'src')

from luminous_nix.ai.nlp import NLPPipeline

# Create pipeline
nlp = NLPPipeline()

# Test a simple query
query = "install firefox"
print(f"Testing: '{query}'")

try:
    result = nlp.process_text(query)
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")
    
    if isinstance(result, dict):
        print("\nDict contents:")
        for key, value in result.items():
            print(f"  {key}: {value}")
    
    # Check what methods the pipeline has
    print("\nNLPPipeline methods:")
    for attr in dir(nlp):
        if not attr.startswith('_') and callable(getattr(nlp, attr)):
            print(f"  - {attr}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()