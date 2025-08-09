#!/usr/bin/env python3
"""
Test the configuration generation feature directly with CLI handling
"""

import sys
import os
import tempfile

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the config generator
from nix_humanity.core.config_generator import NixConfigGenerator

# Test the direct flow
print("=== Testing Direct Config Generation ===\n")

generator = NixConfigGenerator()

test_cases = [
    "generate configuration for web server with nginx and postgresql",
    "create config for desktop system with kde and development tools",
    "make me a minimal server configuration with ssh and docker",
    "build config for gaming desktop with steam and discord"
]

for desc in test_cases:
    print(f"Test: {desc}")
    print("-" * 60)
    
    # Extract the description part
    import re
    pattern = r'(?:generate|create|make|build)\s+(?:me\s+)?(?:a\s+)?(?:config|configuration)\s+(?:for\s+)?(.+)'
    match = re.search(pattern, desc.lower())
    if match:
        clean_desc = match.group(1).strip()
    else:
        # Handle "make me a X configuration"
        match = re.search(r'(?:make|create|build)\s+(?:me\s+)?(?:a\s+)?(.+?)\s+(?:config|configuration)', desc.lower())
        if match:
            clean_desc = match.group(1).strip()
        else:
            clean_desc = desc
    
    print(f"Extracted description: {clean_desc}")
    
    # Parse intent
    intent = generator.parse_intent(clean_desc)
    print(f"Parsed intent: {intent}")
    
    # Generate config
    config_content = generator.generate_config(intent)
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.nix', delete=False) as f:
        f.write(config_content)
        temp_path = f.name
    
    print(f"Generated config saved to: {temp_path}")
    print(f"Config preview (first 500 chars):")
    print(config_content[:500] + "..." if len(config_content) > 500 else config_content)
    print("\n" + "="*80 + "\n")

print("✅ Configuration generation CLI test complete!")