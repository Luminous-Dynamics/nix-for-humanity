#!/usr/bin/env python3
"""
WebSocket Server for Voice Interface
====================================

Bridges the web frontend with the voice processing backend.
Handles real-time audio streaming and command processing.
"""

import asyncio
import websockets
import json
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Set
import threading
import queue

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'scripts'))

# Import our modules
from voice_interface import VoiceInterface
from voice_nlp_integration import VoiceNLPBridge, UserProfile

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VoiceWebSocketServer:
    """WebSocket server for voice interface"""
    
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        
        # Initialize voice components
        self.voice_interface = VoiceInterface()
        self.voice_bridge = VoiceNLPBridge(
            UserProfile(name="Grandma Rose", technical_level="beginner")
        )
        
        # Check dependencies
        ok, message = self.voice_interface.check_dependencies()
        if not ok:
            logger.warning(f"Missing voice dependencies: {message}")
            self.voice_available = False
        else:
            self.voice_available = True
            logger.info("Voice interface ready")
        
        # Command queue for processing
        self.command_queue = queue.Queue()
        
    async def register(self, websocket):
        """Register a new client"""
        self.clients.add(websocket)
        logger.info(f"Client connected: {websocket.remote_address}")
        
        # Send welcome message
        await self.send_to_client(websocket, {
            'type': 'status',
            'message': 'Connected to voice assistant',
            'level': 'ready'
        })
        
    async def unregister(self, websocket):
        """Unregister a client"""
        self.clients.discard(websocket)
        logger.info(f"Client disconnected: {websocket.remote_address}")
    
    async def send_to_client(self, websocket, data: Dict):
        """Send data to a specific client"""
        try:
            await websocket.send(json.dumps(data))
        except websockets.exceptions.ConnectionClosed:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
    
    async def broadcast(self, data: Dict):
        """Broadcast data to all connected clients"""
        if self.clients:
            await asyncio.gather(
                *[self.send_to_client(client, data) for client in self.clients],
                return_exceptions=True
            )
    
    async def handle_client(self, websocket, path):
        """Handle a client connection"""
        await self.register(websocket)
        
        try:
            async for message in websocket:
                await self.process_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        finally:
            await self.unregister(websocket)
    
    async def process_message(self, websocket, message):
        """Process incoming WebSocket message"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'start_recording':
                await self.start_recording(websocket)
                
            elif msg_type == 'stop_recording':
                await self.stop_recording(websocket)
                
            elif msg_type == 'process_command':
                command = data.get('command', '')
                await self.process_text_command(websocket, command)
                
            else:
                logger.warning(f"Unknown message type: {msg_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {message}")
            await self.send_to_client(websocket, {
                'type': 'error',
                'message': 'Invalid message format'
            })
    
    async def start_recording(self, websocket):
        """Start voice recording"""
        if not self.voice_available:
            await self.send_to_client(websocket, {
                'type': 'error',
                'message': 'Voice input not available. Please check microphone.'
            })
            return
        
        # Start recording in a thread to not block
        loop = asyncio.get_event_loop()
        
        def volume_callback(level):
            """Send volume updates to client"""
            asyncio.run_coroutine_threadsafe(
                self.send_to_client(websocket, {
                    'type': 'volume',
                    'level': level
                }),
                loop
            )
        
        # Run recording in executor
        future = loop.run_in_executor(
            None,
            self.voice_interface.process_voice_command,
            volume_callback
        )
        
        # Process the result when done
        asyncio.create_task(self.handle_voice_result(websocket, future))
    
    async def stop_recording(self, websocket):
        """Stop voice recording"""
        # Signal the voice interface to stop
        self.voice_interface.is_recording = False
    
    async def handle_voice_result(self, websocket, future):
        """Handle the result of voice processing"""
        try:
            # Wait for voice processing to complete
            # Note: process_voice_command handles everything internally
            await future
            
            # The voice interface will have already processed and spoken the response
            # We just need to update the UI state
            await self.send_to_client(websocket, {
                'type': 'status',
                'message': 'Ready for another question!',
                'level': 'ready'
            })
            
        except Exception as e:
            logger.error(f"Voice processing error: {e}")
            await self.send_to_client(websocket, {
                'type': 'error',
                'message': 'Sorry, I had trouble understanding. Please try again.'
            })
    
    async def process_text_command(self, websocket, command_text):
        """Process a text command (from suggestion buttons)"""
        logger.info(f"Processing text command: {command_text}")
        
        # Map button commands to natural language
        command_map = {
            'install firefox': "I need to check my email",
            'fix wifi': "My internet isn't working",
            'update system': "Update my computer",
            'install zoom': "I want to video call my grandkids"
        }
        
        natural_text = command_map.get(command_text, command_text)
        
        try:
            # Process through voice bridge
            result = await self.voice_bridge.process_voice_command(natural_text)
            command = result['command']
            
            # Send transcript
            await self.send_to_client(websocket, {
                'type': 'transcript',
                'text': natural_text
            })
            
            # Send response
            await self.send_to_client(websocket, {
                'type': 'response',
                'text': command.response
            })
            
            # If needs confirmation, handle it
            if result['needs_confirmation']:
                # For demo, auto-confirm safe operations
                if command.intent.get('action') in ['install_package', 'fix_wifi']:
                    exec_result = await self.voice_bridge.execute_confirmed_command(command)
                    
                    await self.send_to_client(websocket, {
                        'type': 'response',
                        'text': exec_result['message']
                    })
            
        except Exception as e:
            logger.error(f"Command processing error: {e}")
            await self.send_to_client(websocket, {
                'type': 'error',
                'message': 'I encountered an error. Please try again.'
            })
    
    async def start_server(self):
        """Start the WebSocket server"""
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info(f"Voice WebSocket server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever


def main():
    """Run the WebSocket server"""
    server = VoiceWebSocketServer()
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")


if __name__ == "__main__":
    main()