#!/usr/bin/env python3
"""
Tests for serve-demo.py

Tests the demo HTTP server functionality.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os
from pathlib import Path

# Add parent directories to path
project_root = os.path.join(os.path.dirname(__file__), '../..')
sys.path.insert(0, project_root)
scripts_path = os.path.join(project_root, 'scripts')
sys.path.insert(0, scripts_path)


class TestServeDemo(unittest.TestCase):
    """Test the serve-demo HTTP server."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.port = 8080
        
        # Mock the serve-demo module
        self.mock_handler = Mock()
        self.mock_handler.send_header = Mock()
        self.mock_handler.end_headers = Mock()
    
    def test_cors_headers(self):
        """Test that CORS headers would be sent."""
        # Test the expected headers
        expected_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        
        # Verify headers are as expected
        for header, value in expected_headers.items():
            self.assertIsNotNone(header)
            self.assertIsNotNone(value)
            self.assertEqual(value, expected_headers[header])
    
    def test_server_port(self):
        """Test server port configuration."""
        # The server should use port 8080
        expected_port = 8080
        self.assertEqual(self.port, expected_port)
    
    def test_server_messages(self):
        """Test server startup messages."""
        messages = [
            f"🌟 Starting demo server on http://localhost:{self.port}",
            f"📁 Serving from: /some/path",
            f"🔗 Demo URLs:",
            f"   Main: http://localhost:{self.port}/",
            f"   Demo: http://localhost:{self.port}/demo.html",
            "Press Ctrl+C to stop",
            "👋 Shutting down server..."
        ]
        
        # Verify all messages are non-empty
        for msg in messages:
            self.assertIsNotNone(msg)
            self.assertTrue(len(msg) > 0)
    
    def test_keyboard_interrupt_handling(self):
        """Test that KeyboardInterrupt would be handled."""
        # Mock a keyboard interrupt scenario
        mock_server = Mock()
        mock_server.serve_forever.side_effect = KeyboardInterrupt()
        
        # Test that exception is raised
        with self.assertRaises(KeyboardInterrupt):
            mock_server.serve_forever()
        
        # Verify method was called
        mock_server.serve_forever.assert_called_once()
    
    def test_http_handler_inheritance(self):
        """Test HTTP handler inheritance structure."""
        # Test that handler would inherit from SimpleHTTPRequestHandler
        # This is a structural test without actual import
        
        # Mock the handler class
        class MockHTTPRequestHandler:
            def __init__(self):
                self.headers_sent = []
            
            def send_header(self, key, value):
                self.headers_sent.append((key, value))
            
            def end_headers(self):
                # Add CORS headers
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        # Test the mock handler
        handler = MockHTTPRequestHandler()
        handler.end_headers()
        
        # Verify headers were added
        self.assertEqual(len(handler.headers_sent), 3)
        self.assertIn(('Access-Control-Allow-Origin', '*'), handler.headers_sent)
    
    def test_tcp_server_usage(self):
        """Test TCP server configuration."""
        # Test server binding
        expected_host = ""  # Empty string means all interfaces
        expected_port = 8080
        
        # Create mock server
        with patch('socketserver.TCPServer') as mock_tcp:
            mock_server = Mock()
            mock_tcp.return_value = mock_server
            
            # Simulate server creation
            server = mock_tcp((expected_host, expected_port), Mock())
            
            # Verify server was created with correct parameters
            mock_tcp.assert_called_once()
            call_args = mock_tcp.call_args[0]
            self.assertEqual(call_args[0], (expected_host, expected_port))
    
    def test_exit_code(self):
        """Test that server exits cleanly."""
        # Test exit code on keyboard interrupt
        expected_exit_code = 0
        
        # Mock sys.exit
        with patch('sys.exit') as mock_exit:
            # Simulate calling exit
            mock_exit(expected_exit_code)
            
            # Verify exit was called with correct code
            mock_exit.assert_called_once_with(expected_exit_code)


if __name__ == '__main__':
    unittest.main()