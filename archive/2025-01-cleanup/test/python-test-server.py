#!/usr/bin/env python3
"""
Fallback test server for NixOS GUI when Node.js is not available
Provides basic endpoints for testing
"""

import json
import ssl
import time
import hashlib
import secrets
import subprocess
import os
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import jwt

# Configuration
HTTP_PORT = 8080
HTTPS_PORT = 8443
JWT_SECRET = os.environ.get('JWT_SECRET', 'test-secret-key')
SSL_CERT = 'ssl/cert.pem'
SSL_KEY = 'ssl/key.pem'

# In-memory data store
tokens = {}
rate_limits = {}

class NixOSGUIHandler(BaseHTTPRequestHandler):
    """Request handler for NixOS GUI test server"""
    
    def _set_cors_headers(self):
        """Set CORS headers for development"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    
    def _set_security_headers(self):
        """Set security headers"""
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('X-XSS-Protection', '1; mode=block')
        self.send_header('Strict-Transport-Security', 'max-age=31536000')
        self.send_header('Content-Security-Policy', "default-src 'self'")
    
    def _check_rate_limit(self):
        """Simple rate limiting"""
        client_ip = self.client_address[0]
        current_time = time.time()
        
        if client_ip not in rate_limits:
            rate_limits[client_ip] = []
        
        # Clean old entries
        rate_limits[client_ip] = [t for t in rate_limits[client_ip] if current_time - t < 60]
        
        if len(rate_limits[client_ip]) > 100:
            return False
        
        rate_limits[client_ip].append(current_time)
        return True
    
    def _authenticate(self):
        """Check JWT token"""
        auth_header = self.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header[7:]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            return payload
        except:
            return None
    
    def _send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self._set_cors_headers()
        self._set_security_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        if not self._check_rate_limit():
            self._send_json_response({'error': 'Too many requests'}, 429)
            return
        
        path = urlparse(self.path).path
        
        # Public endpoints
        if path == '/api/health':
            self._send_json_response({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '0.1.0'
            })
            return
        
        # Protected endpoints
        user = self._authenticate()
        if not user:
            self._send_json_response({'error': 'Unauthorized'}, 401)
            return
        
        if path == '/api/packages/installed':
            self._send_json_response([
                {'name': 'nodejs', 'version': '20.5.0'},
                {'name': 'git', 'version': '2.42.0'},
                {'name': 'vim', 'version': '9.0'},
                {'name': 'firefox', 'version': '120.0'}
            ])
        
        elif path == '/api/services':
            self._send_json_response([
                {'name': 'nginx', 'status': 'active', 'enabled': True},
                {'name': 'sshd', 'status': 'active', 'enabled': True},
                {'name': 'postgresql', 'status': 'inactive', 'enabled': False}
            ])
        
        elif path == '/api/configuration':
            self._send_json_response({
                'content': '''{ config, pkgs, ... }:
{
  imports = [ ./hardware-configuration.nix ];
  
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;
  
  networking.hostName = "nixos";
  networking.networkmanager.enable = true;
  
  time.timeZone = "America/Chicago";
  
  i18n.defaultLocale = "en_US.UTF-8";
  
  services.xserver.enable = true;
  services.xserver.displayManager.gdm.enable = true;
  services.xserver.desktopManager.gnome.enable = true;
  
  users.users.demo = {
    isNormalUser = true;
    extraGroups = [ "wheel" ];
  };
  
  system.stateVersion = "25.11";
}'''
            })
        
        elif path == '/api/system/stats':
            # Simulate system stats
            self._send_json_response({
                'cpu': {
                    'usage': 25.5,
                    'cores': 4,
                    'loadAverage': [0.5, 0.6, 0.4]
                },
                'memory': {
                    'total': 8 * 1024 * 1024 * 1024,  # 8GB
                    'used': 4 * 1024 * 1024 * 1024,   # 4GB
                    'free': 4 * 1024 * 1024 * 1024    # 4GB
                },
                'disk': {
                    'total': 100 * 1024 * 1024 * 1024,  # 100GB
                    'used': 50 * 1024 * 1024 * 1024,    # 50GB
                    'free': 50 * 1024 * 1024 * 1024     # 50GB
                },
                'network': {
                    'rx': 1024 * 1024,  # 1MB
                    'tx': 512 * 1024    # 512KB
                }
            })
        
        else:
            self._send_json_response({'error': 'Not found'}, 404)
    
    def do_POST(self):
        """Handle POST requests"""
        if not self._check_rate_limit():
            self._send_json_response({'error': 'Too many requests'}, 429)
            return
        
        path = urlparse(self.path).path
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode()) if post_data else {}
        except:
            self._send_json_response({'error': 'Invalid JSON'}, 400)
            return
        
        # Public endpoints
        if path == '/api/auth/login':
            username = data.get('username', '')
            password = data.get('password', '')
            
            if not username or not password:
                self._send_json_response({'error': 'Missing credentials'}, 400)
                return
            
            # Accept demo credentials
            if username == 'admin' and password in ['testpass', 'changeme']:
                token_payload = {
                    'username': username,
                    'role': 'admin',
                    'exp': datetime.utcnow() + timedelta(hours=24)
                }
                token = jwt.encode(token_payload, JWT_SECRET, algorithm='HS256')
                
                self._send_json_response({
                    'token': token,
                    'user': {
                        'username': username,
                        'role': 'admin'
                    }
                })
            else:
                self._send_json_response({'error': 'Invalid credentials'}, 401)
            return
        
        # Protected endpoints
        user = self._authenticate()
        if not user:
            self._send_json_response({'error': 'Unauthorized'}, 401)
            return
        
        if path == '/api/packages/search':
            query = data.get('query', '')
            if len(query) < 2:
                self._send_json_response({'error': 'Query too short'}, 400)
                return
            
            # Simulate package search
            packages = [
                {'name': 'git', 'version': '2.42.0', 'description': 'Distributed version control system'},
                {'name': 'git-lfs', 'version': '3.4.0', 'description': 'Git Large File Storage'},
                {'name': 'gitui', 'version': '0.24.3', 'description': 'Terminal UI for git'},
            ]
            
            results = [p for p in packages if query.lower() in p['name'].lower()]
            self._send_json_response(results)
        
        elif path == '/api/configuration/validate':
            # Simulate validation
            self._send_json_response({
                'valid': True,
                'warnings': [],
                'errors': []
            })
        
        else:
            self._send_json_response({'error': 'Not found'}, 404)
    
    def log_message(self, format, *args):
        """Custom log format"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")

def generate_ssl_cert():
    """Generate self-signed SSL certificate if needed"""
    if not os.path.exists('ssl'):
        os.makedirs('ssl')
    
    if not os.path.exists(SSL_CERT) or not os.path.exists(SSL_KEY):
        print("Generating self-signed SSL certificate...")
        subprocess.run([
            'openssl', 'req', '-x509', '-newkey', 'rsa:2048',
            '-keyout', SSL_KEY, '-out', SSL_CERT,
            '-days', '365', '-nodes',
            '-subj', '/CN=localhost'
        ])

def main():
    """Start the test server"""
    print("🐍 NixOS GUI Python Test Server")
    print("===============================")
    print(f"HTTP Port: {HTTP_PORT}")
    print(f"HTTPS Port: {HTTPS_PORT}")
    print(f"JWT Secret: {'[FROM ENV]' if 'JWT_SECRET' in os.environ else '[DEFAULT]'}")
    
    # Generate SSL certificate if needed
    generate_ssl_cert()
    
    # Start HTTPS server
    httpd = HTTPServer(('localhost', HTTPS_PORT), NixOSGUIHandler)
    
    # Configure SSL
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(SSL_CERT, SSL_KEY)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    
    print(f"\n✅ Server running on https://localhost:{HTTPS_PORT}")
    print("Press Ctrl+C to stop\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
        httpd.server_close()

if __name__ == '__main__':
    main()