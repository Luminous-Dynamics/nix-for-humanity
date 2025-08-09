"""
from typing import Optional
CLI Frontend Adapter for Nix for Humanity

This adapter connects the CLI interface to the unified backend,
handling all CLI-specific concerns while the backend handles the logic.
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
import argparse
import json
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from nix_humanity.core import NixForHumanityBackend, Request, Response, Context


class CLIAdapter:
    """Adapt CLI interface to unified backend"""
    
    def __init__(self):
        """Initialize CLI adapter with backend"""
        self.backend = NixForHumanityBackend()
        self.session_id = self._generate_session_id()
        
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import uuid
        return str(uuid.uuid4())[:8]
        
    def parse_arguments(self) -> argparse.Namespace:
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description="🗣️ Nix for Humanity - Natural Language NixOS Interface",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  ask-nix "install firefox"
  ask-nix --execute "update my system"
  ask-nix --voice "enable bluetooth"
  ask-nix --learning-mode "what is a generation?"
  
Personality Styles:
  --minimal      Just the facts
  --friendly     Warm and helpful (default)
  --encouraging  Supportive for beginners
  --technical    Detailed explanations
  --symbiotic    Co-evolutionary partner mode
  
For more help: ask-nix --docs
            """
        )
        
        # Main query argument
        parser.add_argument(
            'query',
            nargs='*',
            help='Natural language query or command'
        )
        
        # Execution modes
        execution_group = parser.add_mutually_exclusive_group()
        execution_group.add_argument(
            '--execute', '-e',
            action='store_true',
            help='Actually execute commands (default: show only)'
        )
        execution_group.add_argument(
            '--dry-run', '-n',
            action='store_true',
            help='Show what would be done without executing'
        )
        
        # Personality styles
        personality_group = parser.add_mutually_exclusive_group()
        personality_group.add_argument(
            '--minimal',
            action='store_const',
            const='minimal',
            dest='personality',
            help='Minimal responses - just the facts'
        )
        personality_group.add_argument(
            '--friendly',
            action='store_const',
            const='friendly',
            dest='personality',
            help='Friendly and warm responses (default)'
        )
        personality_group.add_argument(
            '--encouraging',
            action='store_const',
            const='encouraging',
            dest='personality',
            help='Encouraging responses for beginners'
        )
        personality_group.add_argument(
            '--technical',
            action='store_const',
            const='technical',
            dest='personality',
            help='Technical details included'
        )
        personality_group.add_argument(
            '--symbiotic',
            action='store_const',
            const='symbiotic',
            dest='personality',
            help='Symbiotic co-evolutionary mode'
        )
        
        # Input/output modes
        parser.add_argument(
            '--voice', '-v',
            action='store_true',
            help='Enable voice input/output'
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output in JSON format'
        )
        
        # Features
        parser.add_argument(
            '--learning-mode', '-l',
            action='store_true',
            help='Enable learning mode with explanations'
        )
        parser.add_argument(
            '--no-cache',
            action='store_true',
            help='Disable cache for fresh results'
        )
        parser.add_argument(
            '--no-feedback',
            action='store_true',
            help='Disable feedback collection'
        )
        
        # Utilities
        parser.add_argument(
            '--summary',
            action='store_true',
            help='Show system learning summary'
        )
        parser.add_argument(
            '--docs',
            action='store_true',
            help='Open documentation'
        )
        parser.add_argument(
            '--version',
            action='store_true',
            help='Show version information'
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug output'
        )
        
        # Plugin support
        parser.add_argument(
            '--plugin',
            help='Use specific plugin'
        )
        parser.add_argument(
            '--list-plugins',
            action='store_true',
            help='List available plugins'
        )
        
        # Set defaults
        parser.set_defaults(
            personality='friendly',
            execute=False,
            dry_run=False,
            voice=False,
            json=False,
            learning_mode=False,
            no_cache=False,
            no_feedback=False,
            debug=False
        )
        
        return parser.parse_args()
        
    def build_request(self, args: argparse.Namespace) -> Request:
        """Build request object from CLI arguments"""
        # Join query parts
        query = ' '.join(args.query) if args.query else ''
        
        # Handle special commands
        if args.summary:
            query = "show learning summary"
        elif args.docs:
            query = "open documentation"
        elif args.version:
            query = "show version"
        elif args.list_plugins:
            query = "list plugins"
            
        # Build context object
        context = Context(
            execute=args.execute,
            dry_run=args.dry_run,
            personality=args.personality,
            frontend='cli',
            session_id=self.session_id
        )
        
        # Add extra preferences 
        context.user_preferences.update({
            'voice': args.voice,
            'learning_mode': args.learning_mode,
            'use_cache': not args.no_cache,
            'collect_feedback': not args.no_feedback,
            'plugin': args.plugin,
            'debug': args.debug
        })
        
        return Request(
            query=query,
            context=context
        )
        
    def format_response(self, response: Response, args: argparse.Namespace) -> str:
        """Format response for CLI output"""
        if args.json:
            # JSON output
            return json.dumps({
                'success': response.success,
                'text': response.text,
                'commands': response.commands,
                'data': response.data,
                'session_id': self.session_id
            }, indent=2)
            
        # Human-readable output
        output = []
        
        # Main response text
        if response.text:
            output.append(response.text)
            
        # Commands executed
        if response.commands and args.execute:
            output.append("\n📦 Commands executed:")
            for cmd in response.commands:
                status = "✅" if cmd.get('success', True) else "❌"
                output.append(f"  {status} {cmd['description']}")
                if args.debug and 'command' in cmd:
                    output.append(f"     Command: {cmd['command']}")
                    
        # Additional data
        if response.data and args.debug:
            output.append("\n🔍 Debug data:")
            output.append(json.dumps(response.data, indent=2))
            
        return '\n'.join(output)
        
    def handle_voice_input(self) -> Optional[str]:
        """Handle voice input if enabled"""
        try:
            # Try to import voice module
            from nix_humanity.voice import VoiceInterface
            voice = VoiceInterface()
            
            print("🎤 Listening... (press Ctrl+C to cancel)")
            text = voice.listen()
            print(f"📝 Heard: {text}")
            return text
            
        except ImportError:
            print("❌ Voice input not available. Install required packages.")
            return None
        except KeyboardInterrupt:
            print("\n✋ Voice input cancelled")
            return None
            
    def speak_response(self, text: str):
        """Speak response if voice output enabled"""
        try:
            from nix_humanity.voice import VoiceInterface
            voice = VoiceInterface()
            voice.speak(text)
        except ImportError:
            print("❌ Voice output not available. Install required packages.")
            
    def collect_feedback(self, query: str, response: Response):
        """Collect user feedback if enabled"""
        if not response.data.get('collect_feedback', True):
            return
            
        try:
            print("\n" + "=" * 50)
            helpful = input("Was this helpful? (y/n/skip): ").lower().strip()
            
            if helpful == 'skip' or helpful == '':
                return
                
            feedback_data = {
                'query': query,
                'response': response.text,
                'helpful': helpful == 'y',
                'session_id': self.session_id
            }
            
            if helpful == 'n':
                improved = input("What would have been better? (or Enter to skip): ").strip()
                if improved:
                    feedback_data['improved_response'] = improved
                    
            # Send feedback to backend
            feedback_context = Context(
                frontend='cli',
                session_id=self.session_id
            )
            feedback_context.user_preferences['feedback'] = feedback_data
            
            feedback_request = Request(
                query="record feedback",
                context=feedback_context
            )
            self.backend.process(feedback_request)
            print("Thank you for your feedback!")
            
        except KeyboardInterrupt:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        except Exception as e:
            if os.getenv('DEBUG'):
                print(f"Feedback error: {e}")
                
    def run(self):
        """Main CLI execution"""
        args = self.parse_arguments()
        
        # Enable debug if requested
        if args.debug:
            os.environ['DEBUG'] = '1'
            
        # Handle voice input
        if args.voice and not args.query:
            voice_text = self.handle_voice_input()
            if voice_text:
                args.query = voice_text.split()
            else:
                return 1
                
        # Build request
        request = self.build_request(args)
        
        # Empty query check
        if not request.query:
            print("Please provide a query. Use --help for usage.")
            return 1
            
        # Process request
        try:
            response = self.backend.process(request)
            
            # Format and display response
            output = self.format_response(response, args)
            print(output)
            
            # Voice output if enabled
            if args.voice and response.text:
                self.speak_response(response.text)
                
            # Collect feedback if interactive
            if sys.stdin.isatty() and not args.json:
                self.collect_feedback(request.query, response)
                
            return 0 if response.success else 1
            
        except Exception as e:
            if args.debug:
                import traceback
                traceback.print_exc()
            else:
                print(f"❌ Error: {e}")
            return 1
            

def main():
    """Entry point for CLI"""
    adapter = CLIAdapter()
    sys.exit(adapter.run())
    

if __name__ == "__main__":
    main()