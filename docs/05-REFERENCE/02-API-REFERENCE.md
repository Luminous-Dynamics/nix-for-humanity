# 🌐 Nix for Humanity REST API Reference

*Complete API documentation for the Nix for Humanity headless core*

---

💡 **Quick Context**: REST API for integrating Nix for Humanity into web, mobile, and third-party applications  
📍 **You are here**: Reference → API Reference  
🔗 **Related**: [Backend Architecture](../02-ARCHITECTURE/02-BACKEND-ARCHITECTURE.md) | [CLI Commands](./01-CLI-COMMANDS.md) | [Configuration](./CONFIGURATION.md)  
⏱️ **Read time**: 15 minutes  
📊 **Mastery Level**: 🌿 Intermediate - requires understanding of REST APIs and JSON

🌊 **Natural Next Steps**:
- **For developers**: Start with the [Quick Start](#quick-start) section
- **For integration**: Review [Authentication](#authentication) and [Rate Limiting](#rate-limiting)
- **For examples**: See [Code Examples](#code-examples) section

---

## Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Base URL & Versioning](#base-url--versioning)
- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [API Endpoints](#api-endpoints)
  - [Health Check](#health-check)
  - [Query Processing](#query-processing)
  - [Package Search](#package-search)
  - [Feedback Collection](#feedback-collection)
  - [Session Management](#session-management)
  - [Statistics](#statistics)
  - [Capabilities](#capabilities)
- [WebSocket Support](#websocket-support)
- [Code Examples](#code-examples)
- [Best Practices](#best-practices)

## Overview

The Nix for Humanity REST API provides programmatic access to natural language NixOS operations. It's designed for:

- **Web Applications**: Build custom frontends for NixOS management
- **Mobile Apps**: Create native mobile interfaces
- **Automation**: Integrate with CI/CD pipelines
- **Third-Party Tools**: Add NixOS support to existing applications

### Key Features
- 🌐 RESTful JSON API
- 🔒 Session management
- 📊 Rate limiting
- 🎯 Natural language processing
- 💬 Real-time WebSocket support
- 🎭 Multiple personality modes
- 🛡️ Safe execution modes

## Quick Start

### 1. Start the API Server
```bash
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity
python scripts/api/nix_api_server.py
```

### 2. Make Your First Request
```bash
curl -X POST http://localhost:5000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "install firefox"}'
```

### 3. Check the Response
```json
{
  "status": "success",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": {
    "text": "I'll help you install Firefox...",
    "commands": ["nix-env -iA nixpkgs.firefox"],
    "confidence": 0.95
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Base URL & Versioning

- **Base URL**: `http://localhost:5000/api/v1`
- **Current Version**: v1
- **Protocol**: HTTP/HTTPS
- **Format**: JSON

### Version Header (Optional)
```http
X-API-Version: 1
```

## Authentication

Currently, the API uses session-based identification without authentication. For production:

### Session Management
- Sessions are created automatically on first request
- Session IDs should be stored and reused
- Sessions expire after 24 hours of inactivity

### Future Authentication
```http
Authorization: Bearer YOUR_API_TOKEN
```

## Rate Limiting

Rate limits protect the service from abuse:

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/query` | 30 requests | 1 minute |
| `/search` | 20 requests | 1 minute |
| `/feedback` | 10 requests | 1 minute |
| Default | 50 requests | 1 hour |
| Daily | 200 requests | 24 hours |

### Rate Limit Headers
```http
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 25
X-RateLimit-Reset: 1673876400
```

## Error Handling

### Error Response Format
```json
{
  "error": "Descriptive error message",
  "status": "error",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### HTTP Status Codes
| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

## API Endpoints

### Health Check

Check if the API is running and healthy.

#### Request
```http
GET /api/v1/health
```

#### Response
```json
{
  "status": "healthy",
  "version": "0.8.0",
  "uptime": 3600,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Query Processing

Process natural language queries about NixOS.

#### Request
```http
POST /api/v1/query
Content-Type: application/json

{
  "query": "How do I install Firefox?",
  "session_id": "optional-session-id",
  "context": {
    "personality": "friendly",
    "execution_mode": "dry_run",
    "collect_feedback": true
  }
}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Natural language query |
| `session_id` | string | No | Session identifier (auto-generated if not provided) |
| `context` | object | No | Query context options |
| `context.personality` | string | No | Response style: `minimal`, `friendly`, `encouraging`, `technical`, `symbiotic` |
| `context.execution_mode` | string | No | Execution mode: `dry_run`, `safe`, `full`, `learning` |
| `context.collect_feedback` | boolean | No | Enable feedback collection (default: true) |
| `context.capabilities` | array | No | Client capabilities (default: `["text"]`) |

#### Response
```json
{
  "status": "success",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": {
    "text": "I'll help you install Firefox. Here's the command:\n\n`nix-env -iA nixpkgs.firefox`\n\nThis will install the latest stable version of Firefox.",
    "commands": [
      {
        "command": "nix-env -iA nixpkgs.firefox",
        "description": "Install Firefox browser",
        "safe": true
      }
    ],
    "intent": {
      "action": "install",
      "package": "firefox",
      "confidence": 0.95
    },
    "suggestions": [
      "Run `firefox` to start the browser",
      "Use `nix-env -q firefox` to verify installation"
    ],
    "educational": {
      "tip": "The `-iA` flag means 'install by attribute path', which is faster than searching by name"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Package Search

Search for available NixOS packages.

#### Request
```http
GET /api/v1/search?q=firefox&limit=10
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Search query |
| `limit` | integer | No | Maximum results (default: 10, max: 50) |

#### Response
```json
{
  "status": "success",
  "query": "firefox",
  "count": 3,
  "packages": [
    {
      "name": "firefox",
      "version": "121.0",
      "description": "Mozilla Firefox web browser"
    },
    {
      "name": "firefox-esr",
      "version": "115.6.0esr",
      "description": "Mozilla Firefox Extended Support Release"
    },
    {
      "name": "firefox-devedition",
      "version": "122.0b1",
      "description": "Mozilla Firefox Developer Edition"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Feedback Collection

Submit feedback about a query response.

#### Request
```http
POST /api/v1/feedback
Content-Type: application/json

{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "query": "install firefox",
  "response": "System response text",
  "helpful": true,
  "improved_response": "Even better response",
  "rating": 5
}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | Session identifier |
| `query` | string | Yes | Original query |
| `response` | string | Yes | System's response |
| `helpful` | boolean | Yes | Was the response helpful? |
| `improved_response` | string | No | User's improved version |
| `rating` | integer | No | Rating 1-5 |

#### Response
```json
{
  "status": "success",
  "message": "Feedback collected successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Session Management

Get information about a session.

#### Request
```http
GET /api/v1/session/{session_id}
```

#### Response
```json
{
  "status": "success",
  "session": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "created": "2024-01-15T10:00:00Z",
    "interactions": 5,
    "last_interaction": "2024-01-15T10:30:00Z"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Statistics

Get system statistics and usage information.

#### Request
```http
GET /api/v1/stats
```

#### Response
```json
{
  "status": "success",
  "stats": {
    "uptime": 3600,
    "total_queries": 1523,
    "active_sessions": 12,
    "avg_response_time": 0.23,
    "api": {
      "active_sessions": 12,
      "total_sessions": 145
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Capabilities

Get API capabilities and supported features.

#### Request
```http
GET /api/v1/capabilities
```

#### Response
```json
{
  "status": "success",
  "capabilities": {
    "version": "0.8.0",
    "features": [
      "natural_language_query",
      "package_search",
      "feedback_collection",
      "session_management",
      "personality_modes",
      "execution_modes"
    ],
    "personalities": [
      "minimal",
      "friendly",
      "encouraging",
      "technical",
      "symbiotic"
    ],
    "execution_modes": [
      "dry_run",
      "safe",
      "full",
      "learning"
    ],
    "rate_limits": {
      "query": "30 per minute",
      "search": "20 per minute",
      "feedback": "10 per minute",
      "default": "50 per hour"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## WebSocket Support

For real-time interaction, WebSocket support is available (requires `flask-socketio`).

### Connection
```javascript
const socket = io('http://localhost:5000');

socket.on('connect', () => {
  console.log('Connected to Nix for Humanity');
});

socket.on('connected', (data) => {
  console.log('Session ID:', data.session_id);
});
```

### Sending Queries
```javascript
socket.emit('query', {
  query: 'install firefox',
  personality: 'friendly'
});

socket.on('response', (data) => {
  console.log('Response:', data.text);
});

socket.on('error', (data) => {
  console.error('Error:', data.message);
});
```

## Code Examples

### Python Example
```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:5000/api/v1"

# Create a session
session_id = None

# Make a query
def query_nix(text):
    global session_id
    
    response = requests.post(
        f"{BASE_URL}/query",
        json={
            "query": text,
            "session_id": session_id,
            "context": {
                "personality": "friendly",
                "execution_mode": "safe"
            }
        }
    )
    
    data = response.json()
    session_id = data.get("session_id")
    
    return data["response"]

# Example usage
result = query_nix("How do I update my system?")
print(result["text"])
for cmd in result.get("commands", []):
    print(f"Command: {cmd['command']}")
```

### JavaScript Example
```javascript
async function queryNix(query) {
  const response = await fetch('http://localhost:5000/api/v1/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      context: {
        personality: 'friendly',
        execution_mode: 'dry_run'
      }
    })
  });
  
  const data = await response.json();
  return data.response;
}

// Example usage
queryNix('install nodejs')
  .then(response => {
    console.log(response.text);
    response.commands.forEach(cmd => {
      console.log(`Run: ${cmd.command}`);
    });
  });
```

### cURL Examples
```bash
# Simple query
curl -X POST http://localhost:5000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "what is NixOS?"}'

# Query with context
curl -X POST http://localhost:5000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "install docker",
    "context": {
      "personality": "technical",
      "execution_mode": "safe",
      "collect_feedback": false
    }
  }'

# Search packages
curl "http://localhost:5000/api/v1/search?q=python&limit=5"

# Get capabilities
curl http://localhost:5000/api/v1/capabilities
```

## Best Practices

### 1. Session Management
- Store and reuse session IDs for continuity
- Sessions preserve context and learning
- Clean up old sessions periodically

### 2. Error Handling
- Always check the `status` field
- Handle rate limit errors with exponential backoff
- Log errors for debugging

### 3. Personality Selection
- Use `minimal` for scripts and automation
- Use `friendly` or `encouraging` for end users
- Use `technical` for experienced users
- Use `symbiotic` for learning together

### 4. Execution Modes
- Always start with `dry_run` for testing
- Use `safe` for user-initiated actions
- Use `full` only with proper authorization
- Use `learning` to help improve the system

### 5. Performance
- Batch related queries when possible
- Cache package search results
- Use WebSocket for real-time needs
- Respect rate limits

### 6. Security
- Never expose the API publicly without authentication
- Validate all user input
- Use HTTPS in production
- Implement proper CORS policies

## Deployment Considerations

### Production Setup
```python
# Run with production WSGI server
gunicorn -w 4 -b 0.0.0.0:5000 scripts.api.nix_api_server:app

# Or with systemd service
[Unit]
Description=Nix for Humanity API
After=network.target

[Service]
Type=simple
User=nixapi
ExecStart=/usr/bin/python3 /path/to/nix_api_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Environment Variables
```bash
export NIX_API_HOST=0.0.0.0
export NIX_API_PORT=5000
export NIX_API_DEBUG=false
export NIX_API_CORS_ORIGINS=https://yourdomain.com
```

### Monitoring
- Monitor response times
- Track error rates
- Watch for rate limit violations
- Alert on high latency

---

*Sacred Humility Context: This API documentation represents our current implementation of REST endpoints for Nix for Humanity. While the API design follows REST best practices and provides comprehensive functionality, the actual implementation may vary based on backend evolution and real-world usage patterns. Rate limits, response formats, and available features may need adjustment based on production requirements and user feedback.*

**Last Updated**: 2024-01-15  
**API Version**: 0.8.0  
**Status**: Beta - Breaking changes possible