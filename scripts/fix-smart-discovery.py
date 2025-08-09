#!/usr/bin/env python3
"""Fix smart package discovery to pass all tests."""

from pathlib import Path
import re

from typing import List
def fix_smart_discovery():
    """Add smart discovery to the backend."""
    
    print("🔧 Fixing Smart Package Discovery\n")
    
    # Step 1: Add search_packages method to the backend
    engine_file = Path('src/nix_humanity/core/engine.py')
    
    with open(engine_file) as f:
        content = f.read()
    
    # Check if PackageDiscovery is imported
    if 'from .package_discovery import PackageDiscovery' not in content:
        # Add import after other imports
        import_pos = content.find('from .knowledge import KnowledgeBase')
        if import_pos > 0:
            end_of_line = content.find('\n', import_pos)
            new_import = '\nfrom .package_discovery import PackageDiscovery'
            content = content[:end_of_line] + new_import + content[end_of_line:]
            print("✅ Added PackageDiscovery import")
    
    # Check if package_discovery is initialized
    if 'self.package_discovery = PackageDiscovery()' not in content:
        # Find __init__ method
        init_match = re.search(r'def __init__\(self[^)]*\):[^}]+?(?=\n    def)', content, re.DOTALL)
        if init_match:
            init_content = init_match.group(0)
            
            # Add after knowledge base initialization
            kb_init_pos = init_content.find('self.knowledge_base = KnowledgeBase()')
            if kb_init_pos > 0:
                end_of_line = init_content.find('\n', kb_init_pos)
                new_init = '\n        self.package_discovery = PackageDiscovery()'
                new_init_content = init_content[:end_of_line] + new_init + init_content[end_of_line:]
                content = content.replace(init_content, new_init_content)
                print("✅ Added package_discovery initialization")
    
    # Check if search_packages method exists
    if 'def search_packages(' not in content:
        # Add the method
        search_method = '''
    def search_packages(self, query: str, limit: int = 10) -> List[Any]:
        """Search for packages using smart discovery.
        
        Args:
            query: Natural language search query
            limit: Maximum number of results
            
        Returns:
            List of package matches
        """
        return self.package_discovery.search_packages(query, limit)
'''
        
        # Add before the last method or at the end of the class
        # Find the last method definition
        last_method = list(re.finditer(r'\n    def \w+\([^)]*\):', content))[-1]
        # Find the end of that method (next method or end of class)
        next_method_pos = content.find('\n    def ', last_method.end())
        if next_method_pos == -1:
            # No next method, find end of class
            next_method_pos = content.rfind('\n\n')
        
        content = content[:next_method_pos] + search_method + content[next_method_pos:]
        print("✅ Added search_packages method")
    
    # Write back
    with open(engine_file, 'w') as f:
        f.write(content)
    
    print("\n✅ Smart discovery integration complete!")
    
    # Step 2: Create a test script to verify it works
    test_script = '''#!/usr/bin/env python3
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

print("🧪 Testing Smart Package Discovery\\n")

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

print(f"\\n📊 Results: {passed} passed, {failed} failed")
print(f"Success rate: {passed}/{passed+failed} ({passed/(passed+failed)*100:.1f}%)")
'''
    
    with open('scripts/test-smart-discovery.py', 'w') as f:
        f.write(test_script)
    
    print("\n📝 Created test script: scripts/test-smart-discovery.py")
    print("Run it to verify smart discovery is working!")

if __name__ == '__main__':
    fix_smart_discovery()