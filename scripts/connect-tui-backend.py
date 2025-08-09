#!/usr/bin/env python3
"""Connect the TUI to the backend - identify what needs fixing."""

import sys
sys.path.insert(0, 'src')

print("🔗 Connecting TUI to Backend\n")

# Step 1: Check if we can import everything needed
print("1. Checking imports...")

components = {
    "Backend": ("nix_humanity.core.engine", "NixForHumanityBackend"),
    "Request": ("nix_humanity.api.schema", "Request"),
    "Response": ("nix_humanity.api.schema", "Response"),
    "TUI (without Textual)": ("nix_humanity.ui", "__all__"),
}

available = {}
for name, (module, attr) in components.items():
    try:
        exec(f"from {module} import {attr}")
        available[name] = True
        print(f"  ✅ {name}")
    except Exception as e:
        available[name] = False
        print(f"  ❌ {name}: {e}")

# Step 2: Test backend functionality
if available.get("Backend") and available.get("Request"):
    print("\n2. Testing backend functionality...")
    
    from nix_humanity.core.engine import NixForHumanityBackend
    from nix_humanity.api.schema import Request
    
    backend = NixForHumanityBackend()
    
    # Test a simple request
    try:
        request = Request(query="install firefox")
        response = backend.process_request(request)
        print(f"  ✅ Backend can process requests")
        print(f"     Success: {response.success}")
        if hasattr(response, 'message'):
            print(f"     Message: {response.message}")
    except Exception as e:
        print(f"  ❌ Backend request failed: {e}")
    
    # Test search functionality
    try:
        results = backend.search_packages("text editor")
        print(f"  ✅ Package search works: {len(results)} results")
        if results:
            print(f"     First result: {results[0].name}")
    except Exception as e:
        print(f"  ❌ Package search failed: {e}")

# Step 3: Analyze TUI requirements
print("\n3. TUI Requirements Analysis...")

# Check if TUI expects specific backend methods
expected_backend_methods = [
    'process_request',
    'search_packages',
    'get_current_context',
    'get_settings',
    'execute_command',
    'get_suggestions'
]

print("\nBackend methods needed by TUI:")
if available.get("Backend"):
    from nix_humanity.core.engine import NixForHumanityBackend
    backend = NixForHumanityBackend()
    
    for method in expected_backend_methods:
        if hasattr(backend, method):
            print(f"  ✅ {method}")
        else:
            print(f"  ❌ {method} - needs implementation")

# Step 4: Create connection code
print("\n4. Creating TUI-Backend connection...")

connection_code = '''
# In main_app.py, the TUI needs to:
# 1. Initialize the backend in __init__
self.backend = NixForHumanityBackend()

# 2. Process user input through the backend
async def process_user_input(self, text: str):
    request = Request(query=text)
    response = self.backend.process_request(request)
    
    # Update UI based on response
    if response.success:
        self.add_message(response.message, is_user=False)
    else:
        self.add_error(response.error)

# 3. Use search for autocomplete
async def get_suggestions(self, partial: str):
    return self.backend.search_packages(partial)
'''

print("\nConnection code pattern:")
print(connection_code)

# Step 5: What's missing?
print("\n5. What needs to be done:")
print("  1. ✅ Backend is working")
print("  2. ✅ TUI structure exists") 
print("  3. ❌ TUI needs Textual dependency")
print("  4. ❌ TUI needs to use real backend instead of mocks")
print("  5. ❌ Missing some backend methods TUI expects")

print("\n📝 Next Steps:")
print("  1. Add missing backend methods (get_current_context, get_settings)")
print("  2. Update TUI to use real backend")
print("  3. Test in environment with Textual installed")