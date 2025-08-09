#!/usr/bin/env python3
"""
Simple Voice Development Server
===============================

A lightweight HTTP server for testing the voice interface without WebSockets.
Perfect for rapid development and demos.
"""

import http.server
import socketserver
import json
import os
import sys
from urllib.parse import urlparse, parse_qs
import mimetypes

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'scripts'))

from voice_nlp_integration import VoiceNLPBridge, UserProfile
import asyncio

PORT = 8080


class VoiceRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Handle voice interface requests"""
    
    def __init__(self, *args, **kwargs):
        # Initialize voice bridge
        self.voice_bridge = VoiceNLPBridge(
            UserProfile(name="Grandma Rose", technical_level="beginner")
        )
        
        # Set the directory to serve files from
        super().__init__(*args, directory="../../frontend/voice-ui", **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/process':
            self.handle_voice_command()
        else:
            # Serve static files
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/process':
            self.handle_voice_command()
        else:
            self.send_error(404)
    
    def handle_voice_command(self):
        """Process a voice command"""
        # Get command from query string or POST body
        if self.command == 'GET':
            parsed_path = urlparse(self.path)
            params = parse_qs(parsed_path.query)
            command = params.get('command', [''])[0]
        else:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            command = data.get('command', '')
        
        # Process command
        response = asyncio.run(self.process_command_async(command))
        
        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    async def process_command_async(self, command_text):
        """Process command through NLP pipeline"""
        try:
            # Process through voice bridge
            result = await self.voice_bridge.process_voice_command(command_text)
            command = result['command']
            
            return {
                'success': True,
                'transcript': command_text,
                'processed': result['processed_text'],
                'intent': command.intent,
                'response': command.response,
                'needs_confirmation': result['needs_confirmation']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': "I'm sorry, I encountered an error. Please try again."
            }
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{self.log_date_time_string()}] {format % args}")


class VoiceDemoHandler(VoiceRequestHandler):
    """Enhanced handler with demo features"""
    
    def do_GET(self):
        """Handle GET with special demo endpoints"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            # Serve the demo page
            self.serve_demo_page()
        elif parsed_path.path == '/api/status':
            self.send_json({'status': 'ready', 'voice_available': False})
        else:
            super().do_GET()
    
    def serve_demo_page(self):
        """Serve a simplified demo page"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Voice Interface Demo</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 { color: #4a90e2; text-align: center; }
        .demo-input {
            width: 100%;
            padding: 15px;
            font-size: 18px;
            border: 2px solid #4a90e2;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .demo-button {
            width: 100%;
            padding: 15px;
            font-size: 20px;
            background: #4a90e2;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }
        .demo-button:hover { background: #357abd; }
        .response {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .suggestions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 20px;
        }
        .suggestion {
            padding: 10px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            cursor: pointer;
            text-align: center;
        }
        .suggestion:hover { border-color: #4a90e2; }
    </style>
</head>
<body>
    <h1>🎤 Voice Interface Demo</h1>
    <p style="text-align: center; color: #666;">
        Type what you'd say naturally, just like talking to a helpful friend.
    </p>
    
    <input type="text" id="commandInput" class="demo-input" 
           placeholder="e.g., 'I need to check my email'" 
           onkeypress="if(event.key==='Enter') processCommand()">
    
    <button onclick="processCommand()" class="demo-button">
        Ask for Help
    </button>
    
    <div id="response" class="response" style="display: none;"></div>
    
    <div class="suggestions">
        <div class="suggestion" onclick="setCommand('I need to check my email')">
            📧 Check email
        </div>
        <div class="suggestion" onclick="setCommand('My internet is not working')">
            🌐 Fix internet
        </div>
        <div class="suggestion" onclick="setCommand('Update my computer')">
            🔄 Update system
        </div>
        <div class="suggestion" onclick="setCommand('Install zoom for video calls')">
            📹 Video calls
        </div>
    </div>
    
    <script>
        function setCommand(text) {
            document.getElementById('commandInput').value = text;
            processCommand();
        }
        
        async function processCommand() {
            const input = document.getElementById('commandInput');
            const responseDiv = document.getElementById('response');
            const command = input.value.trim();
            
            if (!command) return;
            
            responseDiv.style.display = 'block';
            responseDiv.innerHTML = '<p>🤔 Thinking...</p>';
            
            try {
                const response = await fetch(`/api/process?command=${encodeURIComponent(command)}`);
                const data = await response.json();
                
                if (data.success) {
                    responseDiv.innerHTML = `
                        <p><strong>You said:</strong> "${data.transcript}"</p>
                        <p><strong>I understood:</strong> ${data.intent.action}</p>
                        <hr>
                        <div>${data.response.replace(/\\n/g, '<br>')}</div>
                    `;
                } else {
                    responseDiv.innerHTML = `<p style="color: red;">Error: ${data.response}</p>`;
                }
            } catch (error) {
                responseDiv.innerHTML = `<p style="color: red;">Connection error. Is the server running?</p>`;
            }
        }
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def send_json(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))


def run_server(port=PORT, handler_class=VoiceDemoHandler):
    """Run the HTTP server"""
    
    with socketserver.TCPServer(("", port), handler_class) as httpd:
        print(f"""
🎤 Voice Interface Development Server
====================================

Server running at: http://localhost:{port}

Available endpoints:
  http://localhost:{port}/              - Demo interface
  http://localhost:{port}/index.html    - Full voice UI
  http://localhost:{port}/api/process   - Process commands
  http://localhost:{port}/api/status    - Check status

Press Ctrl+C to stop
        """)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Voice Interface Development Server')
    parser.add_argument('--port', type=int, default=PORT, help='Port to run on')
    parser.add_argument('--simple', action='store_true', help='Use simple handler')
    
    args = parser.parse_args()
    
    handler = VoiceRequestHandler if args.simple else VoiceDemoHandler
    run_server(args.port, handler)