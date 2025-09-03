#!/usr/bin/env python3
"""
🌐 RESTful API Server for AI-Driven Interface Generation
Production-ready API with authentication, rate limiting, and documentation
"""

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import jwt
import asyncio
import json
import hashlib
import hmac
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Any, Optional
import logging

from production_deployment import ProductionDeployment
from services import ServiceResponse
from config_manager import get_config
from error_handler import get_logger


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
CORS(app)

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize services
deployment = ProductionDeployment()
deployment.initialize_services()

# Logger
logger = get_logger(__name__)


# Authentication decorator
def require_auth(f):
    """Require valid JWT token for endpoint access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Decode token
            payload = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # Add user info to request
            request.user_id = payload.get('user_id')
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


# Health check endpoint (no auth required)
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    loop = asyncio.new_event_loop()
    health = loop.run_until_complete(deployment.run_health_checks())
    loop.close()
    
    return jsonify(health), 200 if health['status'] == 'healthy' else 503


# Authentication endpoints
@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """Login endpoint - returns JWT token"""
    data = request.get_json()
    
    # In production, verify against database
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    # Simple demo authentication (replace with real authentication)
    if username == 'demo' and password == 'demo123':
        # Generate token
        payload = {
            'user_id': username,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(
            payload,
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        
        return jsonify({
            'token': token,
            'expires_in': 86400  # 24 hours
        }), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401


# Interface Generation API
@app.route('/api/interface/generate', methods=['POST'])
@require_auth
@limiter.limit("30 per minute")
def generate_interface():
    """Generate interface from natural language"""
    data = request.get_json()
    
    request_text = data.get('request')
    user_context = data.get('context', {})
    
    if not request_text:
        return jsonify({'error': 'Request text required'}), 400
    
    # Add user ID to context
    user_context['user_id'] = request.user_id
    
    # Generate interface
    service = deployment.services['interface']
    response = service.generate_interface(request_text, user_context)
    
    if response.success:
        return jsonify({
            'success': True,
            'interface': response.data,
            'metadata': response.metadata
        }), 200
    else:
        return jsonify({
            'success': False,
            'error': response.error
        }), 500


@app.route('/api/interface/<interface_id>/evolve', methods=['POST'])
@require_auth
def evolve_interface(interface_id):
    """Evolve an existing interface"""
    data = request.get_json()
    evolution_type = data.get('type', 'optimize')
    
    service = deployment.services['interface']
    response = service.evolve_interface(interface_id, evolution_type)
    
    if response.success:
        return jsonify(response.to_dict()), 200
    else:
        return jsonify(response.to_dict()), 400


# Pattern Analysis API
@app.route('/api/patterns/analyze', methods=['GET'])
@require_auth
def analyze_patterns():
    """Analyze usage patterns"""
    service = deployment.services['pattern']
    response = service.analyze_patterns()
    
    return jsonify(response.to_dict()), 200 if response.success else 500


@app.route('/api/patterns/insights', methods=['GET'])
@require_auth
def get_insights():
    """Get actionable insights"""
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    
    service = deployment.services['pattern']
    response = service.get_insights(force_refresh)
    
    return jsonify(response.to_dict()), 200 if response.success else 500


# Feedback API
@app.route('/api/feedback/session/start', methods=['POST'])
@require_auth
def start_feedback_session():
    """Start a feedback session"""
    service = deployment.services['feedback']
    response = service.start_feedback_session(request.user_id)
    
    return jsonify(response.to_dict()), 200 if response.success else 500


@app.route('/api/feedback/collect', methods=['POST'])
@require_auth
def collect_feedback():
    """Collect feedback"""
    data = request.get_json()
    
    required = ['session_id', 'interface_id', 'feedback_type', 'value']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    service = deployment.services['feedback']
    response = service.collect_feedback(
        data['session_id'],
        data['interface_id'],
        data['feedback_type'],
        data['value'],
        data.get('metadata')
    )
    
    return jsonify(response.to_dict()), 200 if response.success else 500


@app.route('/api/feedback/summary', methods=['GET'])
@require_auth
def get_feedback_summary():
    """Get feedback summary"""
    days = int(request.args.get('days', 7))
    
    service = deployment.services['feedback']
    response = service.get_feedback_summary(days)
    
    return jsonify(response.to_dict()), 200 if response.success else 500


# A/B Testing API
@app.route('/api/ab-test/create', methods=['POST'])
@require_auth
def create_ab_test():
    """Create A/B test"""
    data = request.get_json()
    
    required = ['name', 'variants']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    service = deployment.services['ab_testing']
    response = service.create_test(
        data['name'],
        data['variants'],
        data.get('test_type', 'FEATURE')
    )
    
    return jsonify(response.to_dict()), 200 if response.success else 500


@app.route('/api/ab-test/<test_id>/results', methods=['GET'])
@require_auth
def get_test_results(test_id):
    """Get A/B test results"""
    service = deployment.services['ab_testing']
    response = service.get_test_results(test_id)
    
    return jsonify(response.to_dict()), 200 if response.success else 500


@app.route('/api/ab-test/<test_id>/conclude', methods=['POST'])
@require_auth
def conclude_test(test_id):
    """Conclude A/B test"""
    service = deployment.services['ab_testing']
    response = service.conclude_test(test_id)
    
    return jsonify(response.to_dict()), 200 if response.success else 500


# Performance API
@app.route('/api/performance/metrics', methods=['GET'])
@require_auth
def get_performance_metrics():
    """Get performance metrics"""
    service = deployment.services['performance']
    response = service.get_performance_metrics()
    
    return jsonify(response.to_dict()), 200 if response.success else 500


@app.route('/api/performance/summary', methods=['GET'])
@require_auth
def get_performance_summary():
    """Get performance summary"""
    service = deployment.services['performance']
    response = service.get_performance_summary()
    
    return jsonify(response.to_dict()), 200 if response.success else 500


# Optimization API
@app.route('/api/optimization/status', methods=['GET'])
@require_auth
def get_optimization_status():
    """Get optimization status"""
    service = deployment.services['optimization']
    response = service.get_optimization_status()
    
    return jsonify(response.to_dict()), 200 if response.success else 500


@app.route('/api/optimization/run', methods=['POST'])
@require_auth
@limiter.limit("1 per minute")
async def run_optimization():
    """Run optimization cycle"""
    service = deployment.services['optimization']
    response = await service.run_optimization_cycle()
    
    return jsonify(response.to_dict()), 200 if response.success else 500


@app.route('/api/optimization/configure', methods=['PUT'])
@require_auth
def configure_optimization():
    """Configure optimization settings"""
    data = request.get_json()
    
    service = deployment.services['optimization']
    response = service.configure_optimization(
        data.get('auto_apply'),
        data.get('require_approval')
    )
    
    return jsonify(response.to_dict()), 200 if response.success else 500


# System Management API
@app.route('/api/system/deployment-report', methods=['GET'])
@require_auth
def get_deployment_report():
    """Get deployment report"""
    report = deployment.generate_deployment_report()
    return jsonify(report), 200


@app.route('/api/system/cleanup', methods=['POST'])
@require_auth
@limiter.limit("1 per hour")
async def cleanup_data():
    """Run data cleanup"""
    result = await deployment.cleanup_old_data()
    
    return jsonify({
        'success': result,
        'timestamp': datetime.now().isoformat()
    }), 200 if result else 500


# API Documentation
@app.route('/api/docs', methods=['GET'])
def api_documentation():
    """Return API documentation"""
    docs = {
        'version': '1.0.0',
        'title': 'Luminous NixOS GUI API',
        'description': 'AI-Driven Interface Generation System',
        'base_url': request.host_url,
        'authentication': {
            'type': 'JWT',
            'login_endpoint': '/api/auth/login',
            'header': 'Authorization: Bearer <token>'
        },
        'endpoints': {
            'health': {
                'path': '/health',
                'method': 'GET',
                'description': 'Health check endpoint',
                'auth_required': False
            },
            'auth': {
                'login': {
                    'path': '/api/auth/login',
                    'method': 'POST',
                    'description': 'Login to get JWT token',
                    'body': {
                        'username': 'string',
                        'password': 'string'
                    }
                }
            },
            'interface': {
                'generate': {
                    'path': '/api/interface/generate',
                    'method': 'POST',
                    'description': 'Generate interface from natural language',
                    'auth_required': True,
                    'body': {
                        'request': 'string',
                        'context': 'object (optional)'
                    }
                },
                'evolve': {
                    'path': '/api/interface/<interface_id>/evolve',
                    'method': 'POST',
                    'description': 'Evolve an existing interface',
                    'auth_required': True,
                    'body': {
                        'type': 'string (optimize|simplify)'
                    }
                }
            },
            'patterns': {
                'analyze': {
                    'path': '/api/patterns/analyze',
                    'method': 'GET',
                    'description': 'Analyze usage patterns',
                    'auth_required': True
                },
                'insights': {
                    'path': '/api/patterns/insights',
                    'method': 'GET',
                    'description': 'Get actionable insights',
                    'auth_required': True,
                    'query_params': {
                        'refresh': 'boolean (optional)'
                    }
                }
            },
            'feedback': {
                'start_session': {
                    'path': '/api/feedback/session/start',
                    'method': 'POST',
                    'description': 'Start feedback session',
                    'auth_required': True
                },
                'collect': {
                    'path': '/api/feedback/collect',
                    'method': 'POST',
                    'description': 'Collect feedback',
                    'auth_required': True,
                    'body': {
                        'session_id': 'string',
                        'interface_id': 'string',
                        'feedback_type': 'string',
                        'value': 'any',
                        'metadata': 'object (optional)'
                    }
                },
                'summary': {
                    'path': '/api/feedback/summary',
                    'method': 'GET',
                    'description': 'Get feedback summary',
                    'auth_required': True,
                    'query_params': {
                        'days': 'integer (default: 7)'
                    }
                }
            }
        },
        'rate_limits': {
            'default': '200 per day, 50 per hour',
            'login': '5 per minute',
            'generate_interface': '30 per minute',
            'run_optimization': '1 per minute',
            'cleanup': '1 per hour'
        }
    }
    
    return jsonify(docs), 200


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': str(error.description)
    }), 429


def run_server(host='0.0.0.0', port=5000, debug=False):
    """Run the API server"""
    
    print(f"""
╔════════════════════════════════════════════════════════════════════╗
║        🌐 API SERVER STARTING                                      ║
╚════════════════════════════════════════════════════════════════════╝

Server Configuration:
• Host: {host}
• Port: {port}
• Debug: {debug}
• API Docs: http://{host}:{port}/api/docs

Authentication:
• Demo credentials: username='demo', password='demo123'
• Token type: JWT (24-hour expiry)

Rate Limits:
• Default: 200/day, 50/hour
• Login: 5/minute
• Interface Generation: 30/minute

Press Ctrl+C to stop the server
    """)
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Luminous NixOS GUI API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    run_server(args.host, args.port, args.debug)