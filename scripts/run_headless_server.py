#!/usr/bin/env python3
"""
Run the Nix for Humanity Headless Server
This script starts the JSON-RPC server that frontends can connect to
"""

import os
import sys
import signal
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.headless_engine import HeadlessEngine
from core.jsonrpc_server import JSONRPCServer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the headless server"""
    # Configuration
    socket_path = os.environ.get('NIX_FOR_HUMANITY_SOCKET', '/tmp/nix-for-humanity.sock')
    tcp_port = os.environ.get('NIX_FOR_HUMANITY_PORT')
    if tcp_port:
        tcp_port = int(tcp_port)
    
    # Create engine
    logger.info("🧠 Initializing headless engine...")
    engine = HeadlessEngine()
    
    # Create server
    logger.info(f"🚀 Starting JSON-RPC server...")
    server = JSONRPCServer(
        engine,
        socket_path=socket_path,
        tcp_port=tcp_port
    )
    
    # Handle shutdown gracefully
    def shutdown_handler(signum, frame):
        logger.info("🛑 Shutdown signal received")
        server.stop()
        engine.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)
    
    # Start server
    server.start()
    
    logger.info(f"✅ Nix for Humanity Headless Server running")
    logger.info(f"   Unix socket: {socket_path}")
    if tcp_port:
        logger.info(f"   TCP port: {tcp_port}")
    logger.info("   Press Ctrl+C to stop")
    
    # Keep running
    try:
        signal.pause()  # Wait for signals
    except KeyboardInterrupt:
        # TODO: Add proper error handling
        pass  # Silent for now, should log error
    
    # Cleanup
    shutdown_handler(None, None)


if __name__ == "__main__":
    main()