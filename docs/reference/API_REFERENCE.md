# 🔌 API Reference - Nix for Humanity

## Overview

The Nix for Humanity API provides programmatic access to natural language processing for NixOS system management. This is a RESTful API with WebSocket support for real-time voice/text streaming.

### Base URLs
```
NLP API:        http://localhost:3456/api
WebSocket:      ws://localhost:3457
Learning GUI:   http://localhost:3458
```

### Core Philosophy
Unlike traditional APIs, Nix for Humanity's API is designed around natural language intents rather than CRUD operations. The primary endpoint accepts human language and returns system actions.

## Authentication

### Public Mode (Default)
The API runs locally without authentication by default, as it only accepts connections from localhost.

### Secure Mode (Optional)
For multi-user systems or network exposure:

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "alice",
  "password": "secret123"
}
```

Response:
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expiresIn": 3600
}
```

Use token in subsequent requests:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

## Core Endpoints

### 1. Natural Language Processing

#### POST /api/process
Process natural language input and return NixOS actions.

**Request:**
```json
{
  "input": "install firefox",
  "context": {
    "previousIntent": "search_packages",
    "sessionId": "abc123"
  }
}
```

**Response:**
```json
{
  "success": true,
  "intent": {
    "name": "install_package",
    "confidence": 0.98
  },
  "entities": {
    "package": "firefox"
  },
  "action": {
    "type": "package_install",
    "preview": "nix-env -iA nixpkgs.firefox",
    "requiresAuth": true,
    "estimatedTime": "2 minutes",
    "diskSpace": "150MB"
  },
  "response": "I'll install Firefox for you. This will take about 2 minutes.",
  "suggestions": [
    "firefox-developer-edition",
    "firefox-esr"
  ]
}
```

### 2. Voice Processing

#### POST /api/voice/process
Process voice input (audio file) and return actions.

**Request:**
```
Content-Type: multipart/form-data
audio: <audio file (WAV/MP3)>
```

**Response:**
```json
{
  "success": true,
  "transcript": "install firefox please",
  "confidence": 0.95,
  "intent": {
    "name": "install_package",
    "confidence": 0.98
  },
  "action": {
    "type": "package_install",
    "package": "firefox"
  }
}
```

### 3. Intent Patterns

#### GET /api/intents
List all available intent patterns.

**Response:**
```json
{
  "success": true,
  "intents": [
    {
      "name": "install_package",
      "patterns": [
        "install {package}",
        "i need {package}",
        "get me {package}"
      ],
      "examples": [
        "install firefox",
        "i need vscode",
        "get me discord"
      ]
    },
    {
      "name": "remove_package",
      "patterns": [
        "remove {package}",
        "uninstall {package}",
        "delete {package}"
      ]
    }
  ]
}
```

### 4. Command Execution

#### POST /api/execute
Execute a validated NixOS command.

**Request:**
```json
{
  "actionId": "abc123",
  "confirm": true
}
```

**Response:**
```json
{
  "success": true,
  "status": "executing",
  "progress": {
    "percent": 0,
    "message": "Downloading firefox..."
  },
  "rollbackId": "rollback-123"
}
```

### 5. System State

#### GET /api/system/packages
List installed packages.

**Query Parameters:**
- `search`: Filter packages by name
- `limit`: Number of results (default: 50)
- `offset`: Pagination offset

**Response:**
```json
{
  "success": true,
  "packages": [
    {
      "name": "firefox",
      "version": "120.0.1",
      "description": "Web browser",
      "installed": true
    }
  ],
  "total": 1523
}
```

#### GET /api/system/services
List system services.

**Response:**
```json
{
  "success": true,
  "services": [
    {
      "name": "nginx",
      "enabled": true,
      "running": true,
      "description": "Web server"
    }
  ]
}
```

### 6. Learning & Preferences

#### POST /api/learn
Submit user feedback for pattern learning.

**Request:**
```json
{
  "input": "get firefox",
  "expectedIntent": "install_package",
  "actualIntent": "search_package",
  "correct": false
}
```

#### GET /api/preferences
Get user preferences and learned patterns.

**Response:**
```json
{
  "success": true,
  "preferences": {
    "confirmBeforeExecute": true,
    "voiceEnabled": true,
    "language": "en-US",
    "guiLevel": "intermediate"
  },
  "learnedPatterns": [
    {
      "pattern": "grab {package}",
      "intent": "install_package",
      "confidence": 0.9
    }
  ]
}
```

## WebSocket API

### Connection
```javascript
const ws = new WebSocket('ws://localhost:3457');
```

### Events

#### voice-stream
Stream voice data for real-time processing.
```json
{
  "type": "voice-stream",
  "data": {
    "audio": "<base64 encoded audio chunk>",
    "final": false
  }
}
```

#### intent-update
Receive real-time intent recognition updates.
```json
{
  "type": "intent-update",
  "data": {
    "partial": "install fire",
    "possibleIntents": ["install_package"],
    "suggestions": ["firefox", "firewall"]
  }
}
```

#### progress
Receive command execution progress.
```json
{
  "type": "progress",
  "data": {
    "actionId": "abc123",
    "percent": 45,
    "message": "Downloading dependencies...",
    "eta": "1m 30s"
  }
}
```

## Error Handling

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "INTENT_NOT_RECOGNIZED",
    "message": "I didn't understand that command",
    "suggestions": [
      "Try: 'install package-name'",
      "Try: 'search for package-name'"
    ],
    "recoverable": true
  }
}
```

### Common Error Codes
| Code | Description | Recoverable |
|------|-------------|-------------|
| `INTENT_NOT_RECOGNIZED` | Could not understand the input | Yes |
| `PACKAGE_NOT_FOUND` | Package doesn't exist in nixpkgs | Yes |
| `PERMISSION_DENIED` | Needs sudo/admin rights | Yes |
| `NETWORK_ERROR` | Cannot download packages | Yes |
| `SYNTAX_ERROR` | Invalid Nix syntax generated | No |
| `SYSTEM_ERROR` | Internal system error | No |

## Rate Limiting

Local API has generous limits:
- 60 requests per minute per endpoint
- 10 concurrent WebSocket connections
- No limit on voice streaming

Headers indicate rate limit status:
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
X-RateLimit-Reset: 1642531260
```

## Examples

### Complete Installation Flow
```javascript
// 1. Process natural language
const response = await fetch('http://localhost:3456/api/process', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ input: 'install vscode' })
});

const { action } = await response.json();

// 2. Confirm and execute
const execution = await fetch('http://localhost:3456/api/execute', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    actionId: action.id,
    confirm: true 
  })
});

// 3. Monitor progress via WebSocket
ws.on('message', (data) => {
  const msg = JSON.parse(data);
  if (msg.type === 'progress') {
    console.log(`${msg.data.percent}% - ${msg.data.message}`);
  }
});
```

### Voice Command Flow
```javascript
// 1. Start voice streaming
const ws = new WebSocket('ws://localhost:3457');

// 2. Stream audio chunks
mediaRecorder.ondataavailable = (event) => {
  ws.send(JSON.stringify({
    type: 'voice-stream',
    data: {
      audio: btoa(event.data),
      final: false
    }
  }));
};

// 3. Receive intent updates
ws.on('message', (data) => {
  const msg = JSON.parse(data);
  if (msg.type === 'intent-update') {
    updateUI(msg.data.suggestions);
  }
});
```

## SDK Support

Official SDKs planned for:
- JavaScript/TypeScript (available)
- Python (coming soon)
- Rust (coming soon)

## API Versioning

Current version: v1

Version included in URL for future compatibility:
```
http://localhost:3456/api/v1/process
```

---

*API designed for humans first, machines second.*