#!/usr/bin/env python3
"""
Run Voice Server - Complete Backend
===================================

This script runs the complete voice interface backend with all features.
It can run in different modes for testing and production.
"""

import sys
import os
import asyncio
import argparse
import logging
from pathlib import Path

# Add paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'scripts'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_enhanced_server():
    """Run the enhanced WebSocket server"""
    from voice_websocket_server_enhanced import main
    asyncio.run(main())


def run_simple_demo():
    """Run the simple voice demo"""
    from voice_demo_simple import main
    main()


def run_test_flow():
    """Run the test flow"""
    from test_voice_flow import main
    main()


def check_dependencies():
    """Check if all dependencies are available"""
    try:
        # Check for voice interface
        from voice_interface import VoiceInterface
        vi = VoiceInterface()
        ok, message = vi.check_dependencies()
        
        if not ok:
            print("\n❌ Missing dependencies:")
            print(message)
            print("\nPlease install the required dependencies:")
            print("1. Enter nix shell: nix develop")
            print("2. Install Python packages: pip install -r voice_requirements.txt")
            return False
            
        print("✅ All dependencies found!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Make sure you're in the correct directory and nix shell")
        return False


def print_usage():
    """Print usage information"""
    print("""
🎤 Nix for Humanity Voice Server
================================

Usage: python run_voice_server.py [mode]

Modes:
  server    - Run the WebSocket server (default)
  demo      - Run simple text demo
  test      - Run component tests
  check     - Check dependencies only

Examples:
  python run_voice_server.py          # Start server
  python run_voice_server.py demo     # Run demo
  python run_voice_server.py test     # Run tests

The server will run on ws://localhost:8765
Open frontend/voice-ui/index.html in a browser to test.
""")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Run Nix for Humanity Voice Server',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'mode',
        nargs='?',
        default='server',
        choices=['server', 'demo', 'test', 'check', 'help'],
        help='Mode to run in'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'help':
        print_usage()
        return
        
    # Always check dependencies first
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        return
        
    if args.mode == 'check':
        print("\n✅ Dependency check complete!")
        return
        
    # Run the selected mode
    try:
        if args.mode == 'server':
            print("\n🚀 Starting Voice WebSocket Server...")
            print("Connect at ws://localhost:8765")
            print("Press Ctrl+C to stop\n")
            run_enhanced_server()
            
        elif args.mode == 'demo':
            print("\n🎭 Running Simple Voice Demo...")
            run_simple_demo()
            
        elif args.mode == 'test':
            print("\n🧪 Running Voice Tests...")
            run_test_flow()
            
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()