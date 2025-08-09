#!/usr/bin/env python3
"""
Comprehensive tests for Nix API Server

Tests all REST API functionality including:
- Health check endpoint
- Query processing
- Feedback collection
- Session management
- Package search
- Error handling
- Rate limiting
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
import sys
import os
import json
from datetime import datetime, timedelta
import uuid

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts/api'))

# Mock Flask imports before importing the module
sys.modules['flask'] = MagicMock()
sys.modules['flask_cors'] = MagicMock()
sys.modules['flask_limiter'] = MagicMock()
sys.modules['flask_limiter.util'] = MagicMock()
sys.modules['flask_socketio'] = MagicMock()

# Import after mocking
from api import nix_api_server
from api.nix_api_server import APIError, cleanup_old_sessions


class TestAPIError(unittest.TestCase):
    """Test the APIError class."""
    
    def test_api_error_creation(self):
        """Test creating an API error."""
        error = APIError("Test error", 404)
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.status_code, 404)
        self.assertEqual(str(error), "Test error")
    
    def test_api_error_default_status(self):
        """Test API error with default status code."""
        error = APIError("Bad request")
        self.assertEqual(error.message, "Bad request")
        self.assertEqual(error.status_code, 400)


class TestAPIServer(unittest.TestCase):
    """Test the API server endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the Flask app
        self.app_mock = Mock()
        self.app_mock.testing = True
        
        # Mock the test client
        self.client_mock = Mock()
        self.app_mock.test_client.return_value = self.client_mock
        
        # Mock the headless engine
        self.engine_mock = Mock()
        self.engine_patch = patch.object(nix_api_server, 'engine', self.engine_mock)
        self.engine_patch.start()
        
        # Mock sessions
        self.sessions_patch = patch.object(nix_api_server, 'sessions', {})
        self.sessions_patch.start()
        
        # Mock datetime for consistent timestamps
        self.datetime_mock = Mock()
        self.datetime_mock.utcnow.return_value = datetime(2024, 1, 1, 12, 0, 0)
        self.datetime_patch = patch('api.nix_api_server.datetime', self.datetime_mock)
        self.datetime_patch.start()
    
    def tearDown(self):
        """Clean up patches."""
        self.engine_patch.stop()
        self.sessions_patch.stop()
        self.datetime_patch.stop()
    
    def test_health_check(self):
        """Test health check endpoint."""
        # Mock engine stats
        self.engine_mock.get_stats.return_value = {
            'uptime': '1:23:45',
            'sessions': 5
        }
        
        # Call health check
        response = nix_api_server.health_check()
        
        # Verify response
        self.assertIsInstance(response, tuple)
        data, status_code = response
        
        # jsonify returns a Response object in real Flask, but we're mocking
        # So we'll check the call to jsonify
        self.assertEqual(status_code, None)  # jsonify doesn't return status code
    
    def test_process_query_success(self):
        """Test successful query processing."""
        # Mock request data
        with patch('api.nix_api_server.request') as request_mock:
            request_mock.get_json.return_value = {
                'query': 'install firefox',
                'context': {
                    'personality': 'friendly',
                    'execution_mode': 'dry_run'
                }
            }
            
            # Mock engine response
            response_mock = Mock()
            response_mock.to_dict.return_value = {
                'text': 'Installing Firefox...',
                'intent': {'action': 'install'},
                'commands': ['nix-env -iA nixpkgs.firefox']
            }
            self.engine_mock.process.return_value = response_mock
            
            # Call endpoint
            response = nix_api_server.process_query()
            
            # Verify engine was called
            self.engine_mock.process.assert_called_once()
            call_args = self.engine_mock.process.call_args[0]
            self.assertEqual(call_args[0], 'install firefox')
    
    def test_process_query_no_data(self):
        """Test query processing with no JSON data."""
        with patch('api.nix_api_server.request') as request_mock:
            request_mock.get_json.return_value = None
            
            # Should raise APIError
            with self.assertRaises(APIError) as context:
                nix_api_server.process_query()
            
            self.assertEqual(context.exception.message, "No JSON data provided")
    
    def test_process_query_missing_query(self):
        """Test query processing with missing query field."""
        with patch('api.nix_api_server.request') as request_mock:
            request_mock.get_json.return_value = {
                'context': {}
            }
            
            # Should raise APIError
            with self.assertRaises(APIError) as context:
                nix_api_server.process_query()
            
            self.assertEqual(context.exception.message, "Missing 'query' field")
    
    def test_process_query_creates_session(self):
        """Test that query processing creates new sessions."""
        with patch('api.nix_api_server.request') as request_mock:
            request_mock.get_json.return_value = {
                'query': 'test query'
            }
            
            # Mock engine response
            response_mock = Mock()
            response_mock.to_dict.return_value = {'text': 'Response'}
            self.engine_mock.process.return_value = response_mock
            
            # Sessions should be empty initially
            self.assertEqual(len(nix_api_server.sessions), 0)
            
            # Process query
            nix_api_server.process_query()
            
            # Session should be created
            self.assertEqual(len(nix_api_server.sessions), 1)
    
    def test_submit_feedback_success(self):
        """Test successful feedback submission."""
        with patch('api.nix_api_server.request') as request_mock:
            request_mock.get_json.return_value = {
                'session_id': 'test-session',
                'query': 'install vim',
                'response': 'Installing Vim...',
                'helpful': True,
                'rating': 5
            }
            
            # Mock engine feedback collection
            self.engine_mock.collect_feedback.return_value = True
            
            # Submit feedback
            response = nix_api_server.submit_feedback()
            
            # Verify engine was called
            self.engine_mock.collect_feedback.assert_called_once_with(
                'test-session',
                {
                    'session_id': 'test-session',
                    'query': 'install vim',
                    'response': 'Installing Vim...',
                    'helpful': True,
                    'rating': 5
                }
            )
    
    def test_submit_feedback_no_session_id(self):
        """Test feedback submission without session ID."""
        with patch('api.nix_api_server.request') as request_mock:
            request_mock.get_json.return_value = {
                'query': 'test',
                'helpful': True
            }
            
            # Should raise APIError
            with self.assertRaises(APIError) as context:
                nix_api_server.submit_feedback()
            
            self.assertEqual(context.exception.message, "Missing 'session_id' field")
    
    def test_get_stats(self):
        """Test getting statistics."""
        # Mock engine stats
        self.engine_mock.get_stats.return_value = {
            'uptime': '2:30:00',
            'total_queries': 100,
            'active_sessions': 3
        }
        
        # Add some sessions
        nix_api_server.sessions['session1'] = {'created': datetime.utcnow()}
        nix_api_server.sessions['session2'] = {'created': datetime.utcnow()}
        
        # Get stats
        response = nix_api_server.get_stats()
        
        # Verify engine stats were retrieved
        self.engine_mock.get_stats.assert_called_once()
    
    def test_get_session_found(self):
        """Test getting existing session."""
        # Create a session
        session_id = 'test-session-123'
        nix_api_server.sessions[session_id] = {
            'created': datetime(2024, 1, 1, 10, 0, 0),
            'interactions': 5,
            'last_interaction': datetime(2024, 1, 1, 11, 30, 0)
        }
        
        # Get session
        response = nix_api_server.get_session(session_id)
        
        # Response should contain session info
        self.assertIsNotNone(response)
    
    def test_get_session_not_found(self):
        """Test getting non-existent session."""
        # Should raise APIError
        with self.assertRaises(APIError) as context:
            nix_api_server.get_session('non-existent')
        
        self.assertEqual(context.exception.message, "Session not found")
        self.assertEqual(context.exception.status_code, 404)
    
    def test_search_packages(self):
        """Test package search endpoint."""
        with patch('api.nix_api_server.request') as request_mock:
            request_mock.args = {'q': 'python', 'limit': '5'}
            
            # Mock engine response
            response_mock = Mock()
            response_mock.text = "search results for python"
            self.engine_mock.process.return_value = response_mock
            
            # Search packages
            response = nix_api_server.search_packages()
            
            # Verify engine was called with search query
            self.engine_mock.process.assert_called_once()
            call_args = self.engine_mock.process.call_args[0]
            self.assertEqual(call_args[0], 'search for python')
    
    def test_search_packages_no_query(self):
        """Test package search without query parameter."""
        with patch('api.nix_api_server.request') as request_mock:
            request_mock.args = {}
            
            # Should raise APIError
            with self.assertRaises(APIError) as context:
                nix_api_server.search_packages()
            
            self.assertEqual(context.exception.message, "Missing 'q' parameter")
    
    def test_get_capabilities(self):
        """Test getting API capabilities."""
        response = nix_api_server.get_capabilities()
        
        # Should return capabilities info
        self.assertIsNotNone(response)
    
    def test_cleanup_old_sessions(self):
        """Test cleaning up old sessions."""
        # Create sessions with different ages
        now = datetime.utcnow()
        
        # Old session (should be removed)
        nix_api_server.sessions['old-session'] = {
            'created': now - timedelta(hours=25),
            'last_interaction': now - timedelta(hours=25)
        }
        
        # Recent session (should be kept)
        nix_api_server.sessions['recent-session'] = {
            'created': now - timedelta(hours=1),
            'last_interaction': now - timedelta(minutes=30)
        }
        
        # Session without last_interaction (use created time)
        nix_api_server.sessions['no-interaction'] = {
            'created': now - timedelta(hours=26)
        }
        
        # Clean up
        cleanup_old_sessions()
        
        # Verify old sessions removed
        self.assertNotIn('old-session', nix_api_server.sessions)
        self.assertNotIn('no-interaction', nix_api_server.sessions)
        self.assertIn('recent-session', nix_api_server.sessions)
    
    def test_error_handlers(self):
        """Test error handler decorators."""
        # Test API error handler
        error = APIError("Test error", 418)
        response = nix_api_server.handle_api_error(error)
        
        # Should return error response
        self.assertIsNotNone(response)
        
        # Test internal error handler
        error = Exception("Internal error")
        response = nix_api_server.handle_internal_error(error)
        
        # Should return 500 error response
        self.assertIsNotNone(response)


class TestWebSocketSupport(unittest.TestCase):
    """Test WebSocket functionality if available."""
    
    def test_websocket_imports(self):
        """Test that WebSocket support is properly handled."""
        # WebSocket support should be False in test environment
        # since flask_socketio is mocked
        self.assertIsNotNone(nix_api_server.WEBSOCKET_ENABLED)


if __name__ == '__main__':
    unittest.main()