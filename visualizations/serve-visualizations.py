#!/usr/bin/env python3
"""
🎨 Serve Knowledge Visualizations with Live Trinity Data
"""

import json
import logging
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import sys
import webbrowser
from typing import Dict, Any

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from luminous_nix.persistence.trinity_store import TrinityStore

logger = logging.getLogger(__name__)


class TrinityVisualizationHandler(SimpleHTTPRequestHandler):
    """HTTP handler that serves visualizations with Trinity data"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/api/graph-data':
            self.send_trinity_graph_data()
        elif self.path == '/api/user-progress':
            self.send_user_progress()
        elif self.path == '/api/learning-analytics':
            self.send_learning_analytics()
        else:
            # Serve static files
            super().do_GET()
    
    def send_trinity_graph_data(self):
        """Send knowledge graph data from Trinity"""
        try:
            # This would query the Trinity store for real data
            # For now, send sample data
            data = {
                "nodes": [
                    {"id": "basics", "label": "NixOS Basics", "level": 1, "mastery": 0.9},
                    {"id": "packages", "label": "Package Management", "level": 2, "mastery": 0.6},
                    {"id": "config", "label": "System Configuration", "level": 3, "mastery": 0.3},
                ],
                "links": [
                    {"source": "basics", "target": "packages", "type": "requires"},
                    {"source": "packages", "target": "config", "type": "builds_on"},
                ]
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
            
        except Exception as e:
            logger.error(f"Error sending graph data: {e}")
            self.send_error(500, str(e))
    
    def send_user_progress(self):
        """Send user progress data"""
        try:
            data = {
                "level": "Journeyman",
                "mastery": 0.45,
                "concepts_mastered": 8,
                "success_rate": 0.78,
                "total_sessions": 15,
                "learning_velocity": 2.3,
                "peak_hours": [9, 14, 20]
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
            
        except Exception as e:
            logger.error(f"Error sending progress data: {e}")
            self.send_error(500, str(e))
    
    def send_learning_analytics(self):
        """Send learning analytics from Trinity"""
        try:
            # Would query Trinity temporal store for real analytics
            data = {
                "timeline": [
                    {"date": "2024-01-01", "concepts": 2, "success": 0.8},
                    {"date": "2024-01-02", "concepts": 3, "success": 0.85},
                    {"date": "2024-01-03", "concepts": 1, "success": 0.9},
                ],
                "risk_distribution": {
                    "SAFE": 45,
                    "LOW": 20,
                    "MEDIUM": 15,
                    "HIGH": 10,
                    "CRITICAL": 10
                },
                "top_concepts": [
                    {"name": "Package Management", "count": 25},
                    {"name": "System Configuration", "count": 18},
                    {"name": "Garbage Collection", "count": 12}
                ]
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
            
        except Exception as e:
            logger.error(f"Error sending analytics: {e}")
            self.send_error(500, str(e))


def serve_visualizations(port: int = 8080):
    """Start the visualization server"""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║        🎨 Sacred Knowledge Visualization Server 🎨           ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Starting visualization server on port {port}...               ║
║                                                              ║
║  📊 Available Visualizations:                               ║
║                                                              ║
║  • Knowledge Graph:                                         ║
║    http://localhost:{port}/knowledge-graph.html              ║
║                                                              ║
║  • API Endpoints:                                           ║
║    http://localhost:{port}/api/graph-data                    ║
║    http://localhost:{port}/api/user-progress                 ║
║    http://localhost:{port}/api/learning-analytics            ║
║                                                              ║
║  Press Ctrl+C to stop the server                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Change to visualizations directory
    import os
    os.chdir(Path(__file__).parent)
    
    # Create server
    server = HTTPServer(('localhost', port), TrinityVisualizationHandler)
    
    # Try to open browser
    try:
        webbrowser.open(f'http://localhost:{port}/knowledge-graph.html')
        print("✨ Browser opened with visualization!")
    except:
        print("⚠️ Please open your browser manually")
    
    print(f"\n🌊 Server running on http://localhost:{port}")
    print("📊 Serving visualizations from:", Path.cwd())
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down visualization server...")
        server.shutdown()
        print("✅ Server stopped gracefully")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Serve Sacred Knowledge Visualizations")
    parser.add_argument('--port', type=int, default=8080, help='Port to serve on')
    args = parser.parse_args()
    
    serve_visualizations(args.port)