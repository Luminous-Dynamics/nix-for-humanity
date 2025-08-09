#!/usr/bin/env python3
"""
Demo: Enhanced CLI with Two-Path Responses
Shows how the intelligent guide works in practice
"""

import os
import sys
from pathlib import Path

# Add the backend to the path
sys.path.insert(0, str(Path(__file__).parent))

# Enable enhanced responses
os.environ['NIX_HUMANITY_ENHANCED_RESPONSES'] = 'true'
os.environ['NIX_HUMANITY_PYTHON_BACKEND'] = 'true'

from nix_humanity.api.schema import Request, Context
from nix_humanity.core.engine import create_backend

def demo_enhanced_cli():
    """Demonstrate the enhanced CLI experience"""
    
    print("🌟 Nix for Humanity - The NixOS Guide")
    print("=" * 60)
    print("Type 'quit' to exit\n")
    
    backend = create_backend()
    
    # Demo queries
    demo_queries = [
        "install docker",
        "how do I update my system?",
        "enable ssh service",
        "remove firefox"
    ]
    
    print("📝 Demo mode - showing example queries:")
    print("Available demos:", ", ".join(f'"{q}"' for q in demo_queries))
    print()
    
    while True:
        try:
            query = input("🗣️ You: ").strip()
            
            if query.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Thank you for using Nix for Humanity!")
                break
            
            if not query:
                continue
            
            # Process the query
            print("\n🤖 Nix Guide:\n")
            
            request = Request(
                query=query,
                context=Context(
                    personality='friendly',
                    execute=False,
                    collect_feedback=True
                )
            )
            
            try:
                response = backend.process(request)
                
                if hasattr(response, 'explanation'):
                    print(response.explanation)
                else:
                    print(response.text)
                
                # Show commands that would be executed
                if hasattr(response, 'commands') and response.commands:
                    print("\n📋 Commands available:")
                    for cmd in response.commands[:3]:
                        if isinstance(cmd, dict):
                            print(f"  • {cmd.get('command', cmd)}")
                        else:
                            print(f"  • {cmd}")
                
                print("\n" + "-" * 60 + "\n")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                print("\n" + "-" * 60 + "\n")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except EOFError:
            print("\n\n👋 Goodbye!")
            break

if __name__ == "__main__":
    demo_enhanced_cli()