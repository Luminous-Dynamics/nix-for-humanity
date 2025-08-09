#!/usr/bin/env python3
"""
Enhanced WebSocket Server for Voice Interface
============================================

Bridges the web frontend with the Python voice processing backend.
Handles real-time communication for voice commands with full feature support.
"""

import asyncio
import websockets
import json
import logging
import os
import sys
from pathlib import Path
import base64
import tempfile
import traceback
from typing import Dict, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'scripts'))

from voice_interface import VoiceInterface
from voice_nlp_integration import VoiceNLPBridge, UserProfile
from adaptive_response_formatter import AdaptiveResponseFormatter, ResponseDimensions

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VoiceWebSocketServer:
    """Enhanced WebSocket server for voice interface"""
    
    def __init__(self):
        self.voice_interface = VoiceInterface()
        self.response_formatter = AdaptiveResponseFormatter()
        
        # Default to Grandma Rose profile
        self.default_profile = UserProfile(
            name="Grandma Rose",
            technical_level="beginner",
            age_group="senior",
            preferences={
                "voice_speed": 0.9,
                "response_style": "simple",
                "examples_needed": True
            }
        )
        
        # Simple Mode dimensions for Grandma Rose
        self.simple_dimensions = ResponseDimensions(
            complexity=0.0,      # Simplest possible
            verbosity=0.3,       # Concise
            warmth=0.9,          # Very warm
            examples=0.8,        # Lots of examples
            pace=0.2,            # Slow pace
            formality=0.2,       # Casual
            visual_structure=0.7 # Clear structure
        )
        
        self.clients = set()
        
    async def register(self, websocket):
        """Register a new client"""
        self.clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.clients)}")
        
        # Send welcome message
        await websocket.send(json.dumps({
            "type": "welcome",
            "message": "Voice interface connected and ready!"
        }))
        
    async def unregister(self, websocket):
        """Remove a client"""
        self.clients.remove(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.clients)}")
        
    async def process_voice_message(self, websocket, message):
        """Process incoming voice message"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'audio':
                await self.handle_audio(websocket, data)
            elif message_type == 'text':
                await self.handle_text(websocket, data)
            elif message_type == 'settings':
                await self.handle_settings(websocket, data)
            else:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }))
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            logger.error(traceback.format_exc())
            await websocket.send(json.dumps({
                "type": "error",
                "message": "Sorry, I had trouble processing that. Please try again."
            }))
            
    async def handle_audio(self, websocket, data):
        """Handle audio data from client"""
        logger.info("Processing audio message")
        
        try:
            # Send processing status
            await websocket.send(json.dumps({
                "type": "status",
                "message": "Processing your voice command..."
            }))
            
            # Decode audio data
            audio_data = base64.b64decode(data['audio'])
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name
                
            try:
                # Process with voice interface
                # Transcribe audio
                transcript = self.voice_interface.transcribe_audio(tmp_path)
                
                if not transcript:
                    raise ValueError("Could not understand audio")
                
                logger.info(f"Transcript: {transcript}")
                
                # Send transcript
                await websocket.send(json.dumps({
                    "type": "transcript",
                    "text": transcript
                }))
                
                # Process with NLP
                bridge = VoiceNLPBridge(self.default_profile)
                result = await bridge.process_voice_command(transcript)
                
                # Format response for Simple Mode
                response_text = result['command'].response
                adapted_response, _ = self.response_formatter.adapt_response_with_dimensions(
                    response_text,
                    self.simple_dimensions
                )
                
                # Generate speech
                audio_path = self.voice_interface.speak(adapted_response, return_path=True)
                
                # Read audio file and encode
                if audio_path and os.path.exists(audio_path):
                    with open(audio_path, 'rb') as f:
                        audio_content = f.read()
                    audio_base64 = base64.b64encode(audio_content).decode('utf-8')
                    
                    # Clean up temp audio
                    os.unlink(audio_path)
                else:
                    audio_base64 = None
                
                # Send response
                await websocket.send(json.dumps({
                    "type": "response",
                    "transcript": transcript,
                    "response": adapted_response,
                    "audio": audio_base64,
                    "intent": result['command'].intent.get('action', 'unknown'),
                    "needs_confirmation": result.get('needs_confirmation', False)
                }))
                
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    
        except Exception as e:
            logger.error(f"Error handling audio: {e}")
            await websocket.send(json.dumps({
                "type": "error",
                "message": "I couldn't understand that. Could you please try again?"
            }))
            
    async def handle_text(self, websocket, data):
        """Handle text command (for testing)"""
        logger.info(f"Processing text command: {data.get('text')}")
        
        try:
            text = data.get('text', '')
            
            # Process with NLP
            bridge = VoiceNLPBridge(self.default_profile)
            result = await bridge.process_voice_command(text)
            
            # Format response
            response_text = result['command'].response
            adapted_response, _ = self.response_formatter.adapt_response_with_dimensions(
                response_text,
                self.simple_dimensions
            )
            
            # Send response
            await websocket.send(json.dumps({
                "type": "response",
                "transcript": text,
                "response": adapted_response,
                "intent": result['command'].intent.get('action', 'unknown'),
                "needs_confirmation": result.get('needs_confirmation', False)
            }))
            
        except Exception as e:
            logger.error(f"Error handling text: {e}")
            await websocket.send(json.dumps({
                "type": "error",
                "message": "I had trouble processing that command."
            }))
            
    async def handle_settings(self, websocket, data):
        """Handle settings update"""
        settings = data.get('settings', {})
        logger.info(f"Updating settings: {settings}")
        
        # Update voice settings
        if 'voiceSpeed' in settings:
            self.voice_interface.voice_speed = settings['voiceSpeed']
        if 'voiceVolume' in settings:
            self.voice_interface.voice_volume = settings['voiceVolume']
            
        await websocket.send(json.dumps({
            "type": "settings_updated",
            "message": "Settings updated successfully"
        }))
        
    async def handle_client(self, websocket, path):
        """Handle a client connection"""
        await self.register(websocket)
        try:
            async for message in websocket:
                await self.process_voice_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client connection closed")
        finally:
            await self.unregister(websocket)


async def main():
    """Start the WebSocket server"""
    server = VoiceWebSocketServer()
    
    # Check dependencies first
    ok, message = server.voice_interface.check_dependencies()
    if not ok:
        logger.error(f"Missing dependencies:\n{message}")
        logger.error("Please install required components and try again.")
        return
        
    logger.info("Starting Voice WebSocket Server on ws://localhost:8765")
    logger.info("Waiting for connections...")
    
    async with websockets.serve(
        server.handle_client,
        "localhost",
        8765,
        max_size=10 * 1024 * 1024  # 10MB max message size for audio
    ):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        logger.error(traceback.format_exc())