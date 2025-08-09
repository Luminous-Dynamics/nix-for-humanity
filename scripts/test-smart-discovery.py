#!/usr/bin/env python3
"""Test smart package discovery."""

import sys
sys.path.insert(0, 'src')

from nix_humanity.core.engine import NixForHumanityBackend

# Test queries from the test file
test_queries = [
    # Direct package names
    ("firefox", ["firefox", "firefox-esr", "firefox-bin"]),
    ("python", ["python3", "python311", "python310"]),
    
    # Categories
    ("web browser", ["firefox", "chromium", "brave"]),
    ("text editor", ["vim", "neovim", "emacs", "vscode"]),
    
    # Typos and fuzzy matching
    ("fierrfox", ["firefox"]),
    ("pythn", ["python3", "python311"]),
]

backend = NixForHumanityBackend()
passed = 0
failed = 0

print("🧪 Testing Smart Package Discovery\n")

for query, expected_packages in test_queries:
    print(f"Query: '{query}'")
    
    try:
        results = backend.search_packages(query)
        
        if not results:
            print(f"  ❌ No results returned")
            failed += 1
            continue
        
        # Check if results have the expected structure
        result_names = []
        for result in results:
            if hasattr(result, 'name'):
                result_names.append(result.name)
            elif isinstance(result, dict) and 'name' in result:
                result_names.append(result['name'])
            else:
                print(f"  ⚠️  Unexpected result type: {type(result)}")
        
        # Check if any expected package is in results
        found = False
        for expected in expected_packages:
            if any(expected in name for name in result_names):
                found = True
                break
        
        if found:
            print(f"  ✅ Found expected packages in: {result_names[:3]}")
            passed += 1
        else:
            print(f"  ❌ Expected packages not found. Got: {result_names[:3]}")
            failed += 1
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        failed += 1

print(f"\n📊 Results: {passed} passed, {failed} failed")
print(f"Success rate: {passed}/{passed+failed} ({passed/(passed+failed)*100:.1f}%)")
