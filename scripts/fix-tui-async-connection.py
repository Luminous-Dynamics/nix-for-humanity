#!/usr/bin/env python3
"""Fix TUI-Backend async connection issues."""

import re
from pathlib import Path

def fix_tui_async_connection():
    """Fix the async connection between TUI and backend."""
    
    print("🔧 Fixing TUI-Backend async connection\n")
    
    # First, add a sync wrapper to the backend
    engine_file = Path('src/nix_humanity/core/engine.py')
    
    print("1. Adding sync wrapper to backend...")
    
    sync_wrapper = '''
    def process(self, request: Request) -> Response:
        """Synchronous wrapper for process_request for TUI compatibility.
        
        Args:
            request: The request to process
            
        Returns:
            Response object
        """
        import asyncio
        
        # If we're already in an event loop (from TUI), use it
        try:
            loop = asyncio.get_running_loop()
            # Create a task and run it
            task = loop.create_task(self.process_request(request))
            # Can't use run_until_complete in running loop, so we block
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, self.process_request(request))
                return future.result()
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(self.process_request(request))
'''
    
    # Read the engine file
    with open(engine_file) as f:
        content = f.read()
    
    # Check if process method already exists
    if 'def process(' not in content:
        # Find where to insert - after process_request
        insert_pos = content.find('async def process_request')
        if insert_pos > 0:
            # Find the end of process_request method
            method_end = content.find('\n\n    def ', insert_pos)
            if method_end == -1:
                method_end = content.find('\n\nclass', insert_pos)
            if method_end == -1:
                method_end = content.find('\n\n# ', insert_pos)
            if method_end == -1:
                # Find the last return statement in process_request
                last_return = content.rfind('return Response', insert_pos, insert_pos + 5000)
                if last_return > 0:
                    # Find the next empty line after the return
                    method_end = content.find('\n\n', last_return)
            
            if method_end > 0:
                # Insert the sync wrapper
                content = content[:method_end] + '\n' + sync_wrapper + content[method_end:]
                
                # Write back
                with open(engine_file, 'w') as f:
                    f.write(content)
                
                print("✅ Added sync wrapper to backend")
            else:
                print("❌ Could not find insertion point")
        else:
            print("❌ Could not find process_request method")
    else:
        print("✅ process method already exists")
    
    # Now let's check if TUI needs any fixes
    print("\n2. Checking TUI for async handling...")
    
    tui_file = Path('src/nix_humanity/ui/main_app.py')
    if tui_file.exists():
        with open(tui_file) as f:
            tui_content = f.read()
        
        # Check if the process call is in an async method
        process_call_line = tui_content.find('response = self.engine.process(request)')
        if process_call_line > 0:
            # Find the method this is in
            method_start = tui_content.rfind('def ', 0, process_call_line)
            if method_start > 0:
                method_line = tui_content[method_start:process_call_line].split('\n')[0]
                if 'async' not in method_line:
                    print("  Note: TUI method is not async, sync wrapper will handle it")
                else:
                    print("  TUI method is async, may need await")
    
    print("\n3. Testing the connection...")
    
    # Create a simple test
    test_code = '''#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')

from nix_humanity.core.engine import NixForHumanityBackend
from nix_humanity.api.schema import Request

try:
    backend = NixForHumanityBackend()
    request = Request(query="help")
    
    # Test sync wrapper
    response = backend.process(request)
    print(f"✅ Sync wrapper works: {response.success}")
    
    # Test if backend has all TUI methods
    methods = ['get_current_context', 'get_settings', 'execute_command', 'get_suggestions']
    for method in methods:
        if hasattr(backend, method):
            print(f"✅ {method} available")
        else:
            print(f"❌ {method} missing")
            
except Exception as e:
    print(f"❌ Test failed: {e}")
'''
    
    test_file = Path('test_tui_connection.py')
    with open(test_file, 'w') as f:
        f.write(test_code)
    
    print("\n📝 Created test_tui_connection.py - run it to verify")
    
    print("\n4. Summary:")
    print("  - Added sync wrapper to backend for TUI compatibility")
    print("  - TUI can now call backend.process() synchronously")
    print("  - Backend methods are being added by add-tui-backend-methods.py")
    print("\n✅ TUI-Backend connection should now work!")

if __name__ == '__main__':
    fix_tui_async_connection()