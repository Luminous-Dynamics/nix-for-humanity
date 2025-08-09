#!/usr/bin/env python3
"""
from typing import Dict
CLI Adapter for Headless Engine
Demonstrates how the CLI frontend can use the headless engine
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
import argparse

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from core.headless_engine import HeadlessEngine, Context, ExecutionMode
from core.jsonrpc_server import JSONRPCClient


class CLIAdapter:
    """
    CLI adapter that can work with either:
    1. Direct headless engine (embedded mode)
    2. JSON-RPC server (client mode)
    """
    
    def __init__(self, use_server: bool = False, server_address: str = None):
        """
        Initialize CLI adapter
        
        Args:
            use_server: If True, connect to JSON-RPC server. If False, use embedded engine
            server_address: Address of JSON-RPC server (socket path or tcp://host:port)
        """
        self.use_server = use_server
        
        if use_server:
            # Parse server address
            if server_address and server_address.startswith('tcp://'):
                # TCP connection
                parts = server_address[6:].split(':')
                host = parts[0]
                port = int(parts[1]) if len(parts) > 1 else 9999
                self.client = JSONRPCClient(tcp_port=port)
            else:
                # Unix socket
                socket_path = server_address or "/tmp/nix-for-humanity.sock"
                self.client = JSONRPCClient(socket_path=socket_path)
            self.engine = None
        else:
            # Embedded engine
            self.engine = HeadlessEngine()
            self.client = None
    
    def process_query(self, query: str, context: Context) -> Dict[str, Any]:
        """Process a query using either embedded engine or server"""
        if self.use_server:
            # Use JSON-RPC
            params = {
                'input': query,
                'context': {
                    'user_id': context.user_id,
                    'session_id': context.session_id,
                    'personality': context.personality,
                    'capabilities': context.capabilities,
                    'execution_mode': context.execution_mode.value,
                    'collect_feedback': context.collect_feedback
                }
            }
            return self.client.call('process', params)
        else:
            # Use embedded engine
            response = self.engine.process(query, context)
            return response.to_dict()
    
    def collect_feedback(self, session_id: str, feedback: Dict[str, Any]) -> bool:
        """Collect feedback"""
        if self.use_server:
            result = self.client.call('collect_feedback', {
                'session_id': session_id,
                'feedback': feedback
            })
            return result.get('success', False)
        else:
            return self.engine.collect_feedback(session_id, feedback)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        if self.use_server:
            return self.client.call('get_stats')
        else:
            return self.engine.get_stats()
    
    def run_interactive(self, context: Context):
        """Run interactive CLI session"""
        print("🗣️ Nix for Humanity - Natural Language NixOS Interface")
        print("Type 'help' for assistance or 'exit' to quit\n")
        
        while True:
            try:
                # Get input
                query = input("❓ ask-nix> ").strip()
                
                # Handle special commands
                if query.lower() in ['exit', 'quit', 'q']:
                    print("👋 Goodbye!")
                    break
                elif query.lower() in ['help', '?']:
                    self._show_help()
                    continue
                elif query.lower() == 'stats':
                    stats = self.get_stats()
                    print(f"📊 Stats: {stats}")
                    continue
                elif not query:
                    continue
                
                # Process query
                result = self.process_query(query, context)
                
                # Display response
                print(f"\n{result['text']}\n")
                
                # Show commands if available
                if result.get('commands'):
                    print("📦 Commands:")
                    for cmd in result['commands']:
                        print(f"  $ {cmd}")
                    print()
                
                # Collect feedback if requested
                if result.get('feedback_request') and context.collect_feedback:
                    self._collect_feedback(result, context)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _show_help(self):
        """Show help message"""
        print("""
Available commands:
  help, ?     - Show this help
  stats       - Show engine statistics
  exit, quit  - Exit the program

Personality options (use flags when starting):
  --minimal     - Just the facts
  --friendly    - Warm and helpful (default)
  --encouraging - Supportive for beginners
  --technical   - Detailed explanations
  --symbiotic   - Co-evolutionary mode

Examples:
  How do I install Firefox?
  Update my system
  My WiFi isn't working
  What's a generation?
        """)
    
    def _collect_feedback(self, result: Dict[str, Any], context: Context):
        """Collect user feedback"""
        feedback_request = result.get('feedback_request', {})
        prompt = feedback_request.get('prompt', 'Was this helpful?')
        options = feedback_request.get('options', ['yes', 'no'])
        
        print(f"\n💬 {prompt}")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        
        try:
            choice = input("Your choice (or press Enter to skip): ").strip()
            if not choice:
                return
            
            # Parse choice
            if choice.isdigit():
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(options):
                    choice = options[choice_idx]
            
            # Build feedback
            feedback = {
                'query': result.get('intent', {}).get('query', ''),
                'response': result.get('text', ''),
                'helpful': choice in ['yes', 'helpful', 'perfect'],
                'rating': self._choice_to_rating(choice)
            }
            
            # Collect improved response if not helpful
            if choice in ['no', 'not helpful']:
                improved = input("What would have been better? (or press Enter to skip): ").strip()
                if improved:
                    feedback['improved_response'] = improved
            
            # Send feedback
            success = self.collect_feedback(context.session_id, feedback)
            if success:
                print("✅ Thank you for your feedback!")
        
        except Exception as e:
            print(f"⚠️  Feedback error: {e}")
    
    def _choice_to_rating(self, choice: str) -> int:
        """Convert feedback choice to numeric rating"""
        ratings = {
            'perfect': 5,
            'yes': 4,
            'helpful': 4,
            'partially helpful': 3,
            'no': 2,
            'not helpful': 1
        }
        return ratings.get(choice, 3)


def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        description='Nix for Humanity - Natural Language NixOS Interface'
    )
    
    # Connection options
    parser.add_argument(
        '--server',
        help='Connect to headless server instead of embedded engine',
        action='store_true'
    )
    parser.add_argument(
        '--server-address',
        help='Server address (default: /tmp/nix-for-humanity.sock, or tcp://host:port)',
        default=None
    )
    
    # Personality options
    parser.add_argument('--minimal', action='store_true', help='Just the facts')
    parser.add_argument('--friendly', action='store_true', help='Warm and helpful (default)')
    parser.add_argument('--encouraging', action='store_true', help='Supportive for beginners')
    parser.add_argument('--technical', action='store_true', help='Detailed explanations')
    parser.add_argument('--symbiotic', action='store_true', help='Co-evolutionary mode')
    
    # Execution options
    parser.add_argument('--execute', action='store_true', help='Execute commands (default: dry-run)')
    parser.add_argument('--no-feedback', action='store_true', help='Disable feedback collection')
    
    # Query
    parser.add_argument('query', nargs='*', help='Your question or command')
    
    args = parser.parse_args()
    
    # Determine personality
    personality = 'friendly'
    if args.minimal:
        personality = 'minimal'
    elif args.encouraging:
        personality = 'encouraging'
    elif args.technical:
        personality = 'technical'
    elif args.symbiotic:
        personality = 'symbiotic'
    
    # Create context
    context = Context(
        personality=personality,
        execution_mode=ExecutionMode.SAFE if args.execute else ExecutionMode.DRY_RUN,
        collect_feedback=not args.no_feedback,
        capabilities=['text', 'visual']  # CLI can show visual representations
    )
    
    # Create adapter
    adapter = CLIAdapter(
        use_server=args.server,
        server_address=args.server_address
    )
    
    # Process query or run interactive
    if args.query:
        query = ' '.join(args.query)
        result = adapter.process_query(query, context)
        
        print(result['text'])
        
        if result.get('commands'):
            print("\n📦 Commands:")
            for cmd in result['commands']:
                print(f"  $ {cmd}")
    else:
        # Interactive mode
        adapter.run_interactive(context)


if __name__ == "__main__":
    main()