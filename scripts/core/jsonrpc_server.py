#!/usr/bin/env python3
"""
from typing import Dict
JSON-RPC 2.0 Server for Headless Engine
Provides a standard interface for all frontends to communicate with the engine
"""

import json
import socket
import threading
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Callable
import logging
from dataclasses import asdict

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from core.headless_engine import HeadlessEngine, Context, ExecutionMode

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JSONRPCError(Exception):
    """JSON-RPC error with code and message"""
    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)


class JSONRPCServer:
    """
    JSON-RPC 2.0 server for the headless engine
    Supports both Unix sockets (local) and TCP sockets (network)
    """
    
    # Standard JSON-RPC error codes
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    
    def __init__(self, engine: HeadlessEngine, socket_path: str = None, tcp_port: int = None):
        """
        Initialize the JSON-RPC server
        
        Args:
            engine: The headless engine instance
            socket_path: Path for Unix socket (local communication)
            tcp_port: Port for TCP socket (network communication)
        """
        self.engine = engine
        self.socket_path = socket_path or "/tmp/nix-for-humanity.sock"
        self.tcp_port = tcp_port
        self.running = False
        self.methods = self._register_methods()
        
        # Clean up existing socket
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
    
    def _register_methods(self) -> Dict[str, Callable]:
        """Register available JSON-RPC methods"""
        return {
            'process': self._handle_process,
            'collect_feedback': self._handle_feedback,
            'get_stats': self._handle_stats,
            'echo': self._handle_echo,  # For testing
            'list_methods': self._handle_list_methods
        }
    
    def start(self):
        """Start the JSON-RPC server"""
        self.running = True
        
        # Start Unix socket server
        unix_thread = threading.Thread(target=self._run_unix_server, daemon=True)
        unix_thread.start()
        logger.info(f"Unix socket server started at {self.socket_path}")
        
        # Start TCP server if port specified
        if self.tcp_port:
            tcp_thread = threading.Thread(target=self._run_tcp_server, daemon=True)
            tcp_thread.start()
            logger.info(f"TCP server started on port {self.tcp_port}")
    
    def stop(self):
        """Stop the JSON-RPC server"""
        self.running = False
        logger.info("JSON-RPC server stopped")
    
    def _run_unix_server(self):
        """Run Unix socket server"""
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(self.socket_path)
        server.listen(5)
        
        # Set permissions so any user can connect
        os.chmod(self.socket_path, 0o666)
        
        while self.running:
            try:
                client, _ = server.accept()
                thread = threading.Thread(
                    target=self._handle_client,
                    args=(client,),
                    daemon=True
                )
                thread.start()
            except Exception as e:
                if self.running:
                    logger.error(f"Unix server error: {e}")
        
        server.close()
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
    
    def _run_tcp_server(self):
        """Run TCP server"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('localhost', self.tcp_port))
        server.listen(5)
        
        while self.running:
            try:
                client, addr = server.accept()
                logger.info(f"TCP connection from {addr}")
                thread = threading.Thread(
                    target=self._handle_client,
                    args=(client,),
                    daemon=True
                )
                thread.start()
            except Exception as e:
                if self.running:
                    logger.error(f"TCP server error: {e}")
        
        server.close()
    
    def _handle_client(self, client_socket: socket.socket):
        """Handle a client connection"""
        try:
            # Read the request (assuming it's sent in one chunk for simplicity)
            data = client_socket.recv(4096).decode('utf-8')
            if not data:
                return
            
            # Process the request
            response = self._process_request(data)
            
            # Send response
            client_socket.sendall(response.encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Client handler error: {e}")
            error_response = self._create_error_response(
                None, 
                self.INTERNAL_ERROR, 
                str(e)
            )
            client_socket.sendall(json.dumps(error_response).encode('utf-8'))
        finally:
            client_socket.close()
    
    def _process_request(self, data: str) -> str:
        """Process a JSON-RPC request"""
        try:
            # Parse JSON
            try:
                request = json.loads(data)
            except json.JSONDecodeError:
                response = self._create_error_response(
                    None, 
                    self.PARSE_ERROR, 
                    "Parse error"
                )
                return json.dumps(response)
            
            # Validate JSON-RPC request
            if not isinstance(request, dict):
                response = self._create_error_response(
                    None, 
                    self.INVALID_REQUEST, 
                    "Request must be an object"
                )
                return json.dumps(response)
            
            # Check required fields
            if 'jsonrpc' not in request or request['jsonrpc'] != '2.0':
                response = self._create_error_response(
                    request.get('id'),
                    self.INVALID_REQUEST,
                    "Invalid JSON-RPC version"
                )
                return json.dumps(response)
            
            if 'method' not in request:
                response = self._create_error_response(
                    request.get('id'),
                    self.INVALID_REQUEST,
                    "Missing method"
                )
                return json.dumps(response)
            
            # Get method
            method_name = request['method']
            method = self.methods.get(method_name)
            
            if not method:
                response = self._create_error_response(
                    request.get('id'),
                    self.METHOD_NOT_FOUND,
                    f"Method '{method_name}' not found"
                )
                return json.dumps(response)
            
            # Execute method
            params = request.get('params', {})
            try:
                result = method(params)
                response = self._create_success_response(
                    request.get('id'),
                    result
                )
                return json.dumps(response)
            except JSONRPCError as e:
                response = self._create_error_response(
                    request.get('id'),
                    e.code,
                    e.message,
                    e.data
                )
                return json.dumps(response)
            except Exception as e:
                logger.error(f"Method execution error: {e}")
                response = self._create_error_response(
                    request.get('id'),
                    self.INTERNAL_ERROR,
                    str(e)
                )
                return json.dumps(response)
        
        except Exception as e:
            logger.error(f"Request processing error: {e}")
            response = self._create_error_response(
                None,
                self.INTERNAL_ERROR,
                "Internal error"
            )
            return json.dumps(response)
    
    def _create_success_response(self, request_id: Any, result: Any) -> Dict[str, Any]:
        """Create a success response"""
        return {
            'jsonrpc': '2.0',
            'result': result,
            'id': request_id
        }
    
    def _create_error_response(self, request_id: Any, code: int, message: str, data: Any = None) -> Dict[str, Any]:
        """Create an error response"""
        error = {
            'code': code,
            'message': message
        }
        if data is not None:
            error['data'] = data
        
        return {
            'jsonrpc': '2.0',
            'error': error,
            'id': request_id
        }
    
    # Method handlers
    
    def _handle_process(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle 'process' method"""
        if not isinstance(params, dict):
            raise JSONRPCError(
                self.INVALID_PARAMS,
                "Params must be an object"
            )
        
        # Extract parameters
        input_text = params.get('input')
        if not input_text:
            raise JSONRPCError(
                self.INVALID_PARAMS,
                "Missing 'input' parameter"
            )
        
        # Build context from params
        context_data = params.get('context', {})
        context = Context(
            user_id=context_data.get('user_id', 'anonymous'),
            session_id=context_data.get('session_id', ''),
            personality=context_data.get('personality', 'friendly'),
            capabilities=context_data.get('capabilities', ['text']),
            execution_mode=ExecutionMode(context_data.get('execution_mode', 'dry_run')),
            collect_feedback=context_data.get('collect_feedback', True)
        )
        
        # Process with engine
        response = self.engine.process(input_text, context)
        
        # Convert to dict for JSON serialization
        return response.to_dict()
    
    def _handle_feedback(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle 'collect_feedback' method"""
        session_id = params.get('session_id')
        if not session_id:
            raise JSONRPCError(
                self.INVALID_PARAMS,
                "Missing 'session_id' parameter"
            )
        
        feedback = params.get('feedback')
        if not feedback:
            raise JSONRPCError(
                self.INVALID_PARAMS,
                "Missing 'feedback' parameter"
            )
        
        success = self.engine.collect_feedback(session_id, feedback)
        
        return {
            'success': success,
            'message': 'Feedback collected' if success else 'Failed to collect feedback'
        }
    
    def _handle_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle 'get_stats' method"""
        return self.engine.get_stats()
    
    def _handle_echo(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle 'echo' method for testing"""
        return {
            'echo': params,
            'server': 'nix-for-humanity-headless'
        }
    
    def _handle_list_methods(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle 'list_methods' method"""
        return {
            'methods': list(self.methods.keys()),
            'version': '1.0.0'
        }


# Simple client for testing
class JSONRPCClient:
    """Simple JSON-RPC client for testing"""
    
    def __init__(self, socket_path: str = None, tcp_port: int = None):
        self.socket_path = socket_path or "/tmp/nix-for-humanity.sock"
        self.tcp_port = tcp_port
        self.request_id = 0
    
    def call(self, method: str, params: Dict[str, Any] = None) -> Any:
        """Call a JSON-RPC method"""
        self.request_id += 1
        
        request = {
            'jsonrpc': '2.0',
            'method': method,
            'params': params or {},
            'id': self.request_id
        }
        
        # Connect and send
        if self.tcp_port:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', self.tcp_port))
        else:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.socket_path)
        
        try:
            # Send request
            sock.sendall(json.dumps(request).encode('utf-8'))
            
            # Receive response
            response_data = sock.recv(4096).decode('utf-8')
            response = json.loads(response_data)
            
            # Check for error
            if 'error' in response:
                raise Exception(f"RPC Error: {response['error']}")
            
            return response.get('result')
        
        finally:
            sock.close()


if __name__ == "__main__":
    # Test the server
    engine = HeadlessEngine()
    server = JSONRPCServer(engine, tcp_port=9999)
    
    print("🚀 Starting JSON-RPC server...")
    server.start()
    
    # Test with client
    import time
    time.sleep(0.5)  # Wait for server to start
    
    client = JSONRPCClient(tcp_port=9999)
    
    print("\n🧪 Testing server...")
    
    # Test echo
    result = client.call('echo', {'test': 'hello'})
    print(f"Echo test: {result}")
    
    # Test process
    result = client.call('process', {
        'input': 'How do I install Firefox?',
        'context': {
            'personality': 'minimal',
            'capabilities': ['text', 'visual']
        }
    })
    print(f"\nProcess test:")
    print(f"Intent: {result['intent']['action']}")
    print(f"Response: {result['text'][:100]}...")
    
    # Test stats
    stats = client.call('get_stats')
    print(f"\nStats: {json.dumps(stats, indent=2)}")
    
    print("\n✅ Server test complete!")
    
    # Keep server running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
        print("\n👋 Server stopped")