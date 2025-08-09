#!/usr/bin/env python3
"""
Nix for Humanity v1.0 - Simple, Reliable, Human-Friendly NixOS

This is the streamlined v1.0 entry point focusing on core functionality:
- Natural language understanding for common NixOS tasks
- Fast native Python-Nix API integration
- Two personas: Beginner-friendly and Expert
- Essential commands that work 100% reliably
"""

import sys
import os
from pathlib import Path
from typing import Optional

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from nix_humanity.core.engine import NixHumanityEngine
from nix_humanity.core.intents import Intent
from nix_humanity.interfaces.cli import CLIInterface
from nix_humanity.config.loader import load_config


class NixHumanityV1:
    """Streamlined v1.0 implementation focusing on reliability and simplicity."""
    
    def __init__(self):
        """Initialize v1.0 with core features only."""
        # Load v1.0 configuration
        self.config = load_config(version="1.0")
        
        # Initialize core engine with v1.0 features
        self.engine = NixHumanityEngine(
            config=self.config,
            enable_voice=False,  # v2.0 feature
            enable_xai=False,    # v3.0 feature
            enable_advanced_learning=False,  # v3.0 feature
            max_personas=2,      # Just beginner and expert for v1.0
        )
        
        # Simple CLI interface
        self.cli = CLIInterface(self.engine)
    
    def run(self, query: str) -> str:
        """Process a natural language query and return the result."""
        try:
            # Parse intent
            intent = self.engine.parse_intent(query)
            
            # Execute command
            result = self.engine.execute(intent)
            
            # Format response
            return self.cli.format_response(result)
            
        except Exception as e:
            return f"I encountered an error: {str(e)}\nLet me help you understand what went wrong..."
    
    def interactive_mode(self):
        """Run in interactive mode for continuous conversation."""
        print("🌟 Nix for Humanity v1.0 - Making NixOS Human-Friendly")
        print("Type 'help' for available commands or 'exit' to quit.\n")
        
        while True:
            try:
                query = input("nix> ").strip()
                
                if query.lower() in ['exit', 'quit', 'bye']:
                    print("Thank you for using Nix for Humanity! 🌊")
                    break
                
                response = self.run(query)
                print(f"\n{response}\n")
                
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit properly. 😊")
            except Exception as e:
                print(f"Unexpected error: {e}")


def main():
    """Main entry point for v1.0."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Nix for Humanity v1.0 - Natural Language NixOS",
        epilog="Making NixOS accessible to everyone, one command at a time."
    )
    
    parser.add_argument(
        'query',
        nargs='*',
        help='Natural language command (interactive mode if empty)'
    )
    
    parser.add_argument(
        '--persona',
        choices=['beginner', 'expert'],
        default='beginner',
        help='Choose interaction style (default: beginner)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without executing'
    )
    
    args = parser.parse_args()
    
    # Initialize v1.0
    nix = NixHumanityV1()
    
    # Set persona
    nix.engine.set_persona(args.persona)
    
    # Set dry-run mode
    if args.dry_run:
        nix.engine.set_dry_run(True)
    
    # Run query or interactive mode
    if args.query:
        query = ' '.join(args.query)
        response = nix.run(query)
        print(response)
    else:
        nix.interactive_mode()


if __name__ == '__main__':
    main()