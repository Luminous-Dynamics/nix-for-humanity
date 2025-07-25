# NixOS GUI API Reference

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
   - [Authentication Endpoints](#authentication-endpoints)
   - [Package Management](#package-management)
   - [Service Management](#service-management)
   - [Configuration Management](#configuration-management)
   - [System Management](#system-management)
4. [WebSocket Events](#websocket-events)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Examples](#examples)

## Overview

The NixOS GUI API is a RESTful interface that provides programmatic access to NixOS system management features. All endpoints return JSON responses unless otherwise specified.

### Base URL
```
http://localhost:8080/api
```

### Common Headers
```http
Content-Type: application/json
Authorization: Bearer <jwt-token>
X-Request-ID: <unique-request-id>
```

### Response Format
```json
{
  "success": true,
  "data": {},
  "meta": {
    "timestamp": "2024-01-15T10:30:45Z",
    "requestId": "123e4567-e89b-12d3-a456-426614174000"
  }
}
```

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "PACKAGE_NOT_FOUND",
    "message": "Package 'firefox' not found",
    "details": {},
    "recoveryActions": ["Try searching for 'firefox-bin' instead"]
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:45Z",
    "requestId": "123e4567-e89b-12d3-a456-426614174000"
  }
}
```

## Authentication

### Overview
The API uses JWT (JSON Web Tokens) for authentication. Tokens are obtained by authenticating with system credentials via PAM.

### Token Lifecycle
- Access tokens expire after 15 minutes
- Refresh tokens expire after 7 days
- Refresh tokens are rotated on each use

## API Endpoints

### Authentication Endpoints

#### POST /api/auth/login
Authenticate user and receive tokens.

**Request:**
```json
{
  "username": "admin",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIs...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIs...",
    "expiresIn": 900,
    "user": {
      "username": "admin",
      "groups": ["wheel", "nixos-gui"],
      "permissions": ["packages.read", "packages.write", "services.manage"]
    }
  }
}
```

**Status Codes:**
- `200 OK` - Successfully authenticated
- `401 Unauthorized` - Invalid credentials
- `429 Too Many Requests` - Rate limit exceeded

#### POST /api/auth/refresh
Refresh access token using refresh token.

**Request:**
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIs...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIs...",
    "expiresIn": 900
  }
}
```

#### POST /api/auth/logout
Invalidate current session.

**Request:**
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Successfully logged out"
  }
}
```

#### GET /api/auth/verify
Verify if current token is valid.

**Response:**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "user": {
      "username": "admin",
      "groups": ["wheel", "nixos-gui"]
    }
  }
}
```

### Package Management

#### GET /api/packages
List installed packages with pagination and filtering.

**Query Parameters:**
- `page` (number): Page number (default: 1)
- `limit` (number): Items per page (default: 50, max: 200)
- `search` (string): Search term
- `category` (string): Filter by category

**Response:**
```json
{
  "success": true,
  "data": {
    "packages": [
      {
        "name": "firefox",
        "version": "121.0",
        "description": "A web browser built from Firefox source tree",
        "installed": true,
        "category": "applications/networking/browsers"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 1250,
      "pages": 25
    }
  }
}
```

#### GET /api/packages/search
Search available packages in nixpkgs.

**Query Parameters:**
- `q` (string, required): Search query
- `limit` (number): Maximum results (default: 20)

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "name": "firefox",
        "version": "121.0",
        "description": "A web browser built from Firefox source tree",
        "installed": false,
        "homepage": "https://www.mozilla.org/firefox/"
      }
    ],
    "total": 5
  }
}
```

#### GET /api/packages/:name
Get detailed information about a specific package.

**Response:**
```json
{
  "success": true,
  "data": {
    "name": "firefox",
    "version": "121.0",
    "description": "A web browser built from Firefox source tree",
    "longDescription": "Mozilla Firefox is a free and open-source web browser...",
    "installed": true,
    "homepage": "https://www.mozilla.org/firefox/",
    "license": "MPL-2.0",
    "maintainers": ["mozilla-team"],
    "platforms": ["x86_64-linux", "aarch64-linux"],
    "dependencies": [
      "gtk3",
      "libXt",
      "libnotify"
    ],
    "size": 268435456
  }
}
```

#### POST /api/packages/install
Install a package.

**Request:**
```json
{
  "package": "firefox",
  "channel": "nixpkgs" 
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "jobId": "550e8400-e29b-41d4-a716-446655440000",
    "status": "queued",
    "package": "firefox"
  }
}
```

**WebSocket Updates:**
```json
{
  "type": "job.progress",
  "jobId": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "status": "building",
    "progress": 45,
    "message": "Building firefox-121.0...",
    "output": "unpacking sources..."
  }
}
```

#### DELETE /api/packages/:name
Remove an installed package.

**Response:**
```json
{
  "success": true,
  "data": {
    "jobId": "550e8400-e29b-41d4-a716-446655440001",
    "status": "queued",
    "package": "firefox"
  }
}
```

### Service Management

#### GET /api/services
List all system services.

**Query Parameters:**
- `status` (string): Filter by status (running, stopped, failed)
- `type` (string): Filter by type (service, timer, socket)

**Response:**
```json
{
  "success": true,
  "data": {
    "services": [
      {
        "name": "nginx",
        "description": "Nginx Web Server",
        "status": "running",
        "enabled": true,
        "type": "service",
        "pid": 1234,
        "memory": 52428800,
        "cpu": 0.5,
        "uptime": 86400
      }
    ]
  }
}
```

#### GET /api/services/:name
Get detailed service information.

**Response:**
```json
{
  "success": true,
  "data": {
    "name": "nginx",
    "description": "Nginx Web Server",
    "status": "running",
    "enabled": true,
    "type": "service",
    "mainPid": 1234,
    "controlGroup": "/system.slice/nginx.service",
    "dependencies": ["network.target"],
    "loadState": "loaded",
    "activeState": "active",
    "subState": "running",
    "unitFileState": "enabled",
    "activeSince": "2024-01-14T10:30:45Z",
    "memory": {
      "current": 52428800,
      "peak": 104857600,
      "limit": 1073741824
    },
    "cpu": {
      "usage": 0.5,
      "shares": 1024
    }
  }
}
```

#### POST /api/services/:name/start
Start a service.

**Response:**
```json
{
  "success": true,
  "data": {
    "service": "nginx",
    "action": "start",
    "status": "starting"
  }
}
```

#### POST /api/services/:name/stop
Stop a service.

**Response:**
```json
{
  "success": true,
  "data": {
    "service": "nginx",
    "action": "stop",
    "status": "stopping"
  }
}
```

#### POST /api/services/:name/restart
Restart a service.

**Response:**
```json
{
  "success": true,
  "data": {
    "service": "nginx",
    "action": "restart",
    "status": "restarting"
  }
}
```

#### POST /api/services/:name/enable
Enable a service to start on boot.

**Request:**
```json
{
  "persistent": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "service": "nginx",
    "enabled": true
  }
}
```

#### POST /api/services/:name/disable
Disable a service from starting on boot.

**Response:**
```json
{
  "success": true,
  "data": {
    "service": "nginx",
    "enabled": false
  }
}
```

#### GET /api/services/:name/logs
Get service logs.

**Query Parameters:**
- `lines` (number): Number of lines (default: 100)
- `since` (string): Show logs since timestamp
- `until` (string): Show logs until timestamp
- `follow` (boolean): Stream logs in real-time

**Response:**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "timestamp": "2024-01-15T10:30:45Z",
        "level": "info",
        "message": "Server started on port 80"
      }
    ]
  }
}
```

### Configuration Management

#### GET /api/config
Read current system configuration.

**Response:**
```json
{
  "success": true,
  "data": {
    "content": "{ config, pkgs, ... }:\n{\n  imports = [ ./hardware-configuration.nix ];\n  ...\n}",
    "path": "/etc/nixos/configuration.nix",
    "lastModified": "2024-01-15T10:30:45Z",
    "syntax": "nix"
  }
}
```

#### POST /api/config/validate
Validate configuration syntax.

**Request:**
```json
{
  "content": "{ config, pkgs, ... }:\n{\n  services.nginx.enable = true;\n}"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "warnings": [],
    "info": {
      "packages": ["nginx"],
      "services": ["nginx"]
    }
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "SYNTAX_ERROR",
    "message": "Syntax error at line 3",
    "details": {
      "line": 3,
      "column": 15,
      "expected": "';'",
      "found": "}"
    }
  }
}
```

#### PUT /api/config
Update system configuration.

**Request:**
```json
{
  "content": "{ config, pkgs, ... }:\n{\n  services.nginx.enable = true;\n}",
  "message": "Enable nginx service"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "backup": {
      "id": "config-backup-20240115-103045",
      "path": "/var/lib/nixos-gui/backups/configuration.nix.20240115-103045"
    },
    "changes": {
      "additions": 1,
      "deletions": 0,
      "files": ["/etc/nixos/configuration.nix"]
    }
  }
}
```

#### POST /api/config/backup
Create a configuration backup.

**Request:**
```json
{
  "description": "Before enabling nginx"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "backup": {
      "id": "manual-backup-20240115-103045",
      "path": "/var/lib/nixos-gui/backups/configuration.nix.20240115-103045",
      "description": "Before enabling nginx",
      "size": 4096
    }
  }
}
```

#### GET /api/config/diff
Show differences between current and active configuration.

**Response:**
```json
{
  "success": true,
  "data": {
    "hasChanges": true,
    "diff": "@@ -10,6 +10,7 @@\n   services.openssh.enable = true;\n+  services.nginx.enable = true;\n   ...",
    "additions": 1,
    "deletions": 0
  }
}
```

### System Management

#### GET /api/system/info
Get system information.

**Response:**
```json
{
  "success": true,
  "data": {
    "hostname": "nixos-desktop",
    "nixosVersion": "23.11",
    "kernel": "6.1.69",
    "architecture": "x86_64-linux",
    "uptime": 259200,
    "loadAverage": [0.5, 0.7, 0.8],
    "memory": {
      "total": 16777216000,
      "used": 8388608000,
      "free": 8388608000,
      "available": 10737418240
    },
    "disk": {
      "total": 1099511627776,
      "used": 549755813888,
      "free": 549755813888,
      "percent": 50
    },
    "cpu": {
      "model": "Intel Core i7-9700K",
      "cores": 8,
      "threads": 8,
      "usage": 15.5
    }
  }
}
```

#### GET /api/system/generations
List system generations.

**Response:**
```json
{
  "success": true,
  "data": {
    "current": 42,
    "generations": [
      {
        "id": 42,
        "date": "2024-01-15T10:30:45Z",
        "current": true,
        "nixosVersion": "23.11",
        "configurationRevision": "abc123",
        "kernelVersion": "6.1.69",
        "description": "Enable nginx service"
      },
      {
        "id": 41,
        "date": "2024-01-14T15:20:30Z",
        "current": false,
        "nixosVersion": "23.11",
        "configurationRevision": "def456",
        "kernelVersion": "6.1.69",
        "description": "Update packages"
      }
    ]
  }
}
```

#### POST /api/system/rebuild
Rebuild the system with current configuration.

**Request:**
```json
{
  "action": "switch",
  "upgrade": false
}
```

**Actions:**
- `switch`: Build and activate immediately
- `boot`: Build and activate on next boot
- `test`: Build and activate temporarily
- `build`: Build only, don't activate
- `dry-build`: Show what would be built

**Response:**
```json
{
  "success": true,
  "data": {
    "jobId": "rebuild-550e8400-e29b-41d4-a716-446655440000",
    "action": "switch",
    "status": "queued"
  }
}
```

#### POST /api/system/rollback
Rollback to a previous generation.

**Request:**
```json
{
  "generation": 41
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "jobId": "rollback-550e8400-e29b-41d4-a716-446655440001",
    "fromGeneration": 42,
    "toGeneration": 41,
    "status": "queued"
  }
}
```

#### GET /api/system/metrics
Get system performance metrics.

**Query Parameters:**
- `interval` (string): Time interval (1m, 5m, 15m, 1h)
- `metrics` (array): Specific metrics to include

**Response:**
```json
{
  "success": true,
  "data": {
    "timestamp": "2024-01-15T10:30:45Z",
    "interval": "5m",
    "metrics": {
      "cpu": {
        "usage": 15.5,
        "user": 10.2,
        "system": 5.3,
        "idle": 84.5,
        "history": [14.2, 15.1, 16.0, 15.8, 15.5]
      },
      "memory": {
        "used": 8388608000,
        "free": 8388608000,
        "buffers": 1073741824,
        "cached": 2147483648,
        "history": [8.0, 8.1, 8.2, 8.3, 8.4]
      },
      "disk": {
        "read": 1048576,
        "write": 524288,
        "history": {
          "read": [1.0, 1.1, 1.0, 1.2, 1.0],
          "write": [0.5, 0.6, 0.5, 0.5, 0.5]
        }
      },
      "network": {
        "rx": 10485760,
        "tx": 5242880,
        "history": {
          "rx": [10.0, 10.5, 11.0, 10.2, 10.5],
          "tx": [5.0, 5.5, 5.2, 5.1, 5.2]
        }
      }
    }
  }
}
```

## WebSocket Events

Connect to WebSocket endpoint for real-time updates:
```
ws://localhost:8080/ws
```

### Authentication
Send authentication message after connection:
```json
{
  "type": "auth",
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Event Types

#### Job Progress
```json
{
  "type": "job.progress",
  "jobId": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "status": "running",
    "progress": 75,
    "message": "Building derivations...",
    "output": "building '/nix/store/...'"
  }
}
```

#### Job Complete
```json
{
  "type": "job.complete",
  "jobId": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "status": "success",
    "result": {
      "package": "firefox",
      "version": "121.0",
      "action": "installed"
    }
  }
}
```

#### Job Failed
```json
{
  "type": "job.failed",
  "jobId": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "status": "failed",
    "error": {
      "code": "BUILD_FAILED",
      "message": "Build failed for firefox-121.0",
      "details": "error: build of '/nix/store/...' failed"
    }
  }
}
```

#### System Update
```json
{
  "type": "system.update",
  "data": {
    "event": "generation.created",
    "generation": 43,
    "timestamp": "2024-01-15T10:35:00Z"
  }
}
```

#### Service Status
```json
{
  "type": "service.status",
  "data": {
    "service": "nginx",
    "previousStatus": "stopped",
    "currentStatus": "running",
    "timestamp": "2024-01-15T10:35:00Z"
  }
}
```

#### Configuration Changed
```json
{
  "type": "config.changed",
  "data": {
    "path": "/etc/nixos/configuration.nix",
    "user": "admin",
    "timestamp": "2024-01-15T10:35:00Z"
  }
}
```

### Subscriptions
Subscribe to specific event channels:
```json
{
  "type": "subscribe",
  "channels": ["jobs", "system", "services"]
}
```

Unsubscribe:
```json
{
  "type": "unsubscribe",
  "channels": ["services"]
}
```

## Error Handling

### Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `AUTH_REQUIRED` | Authentication required | 401 |
| `AUTH_INVALID` | Invalid credentials | 401 |
| `TOKEN_EXPIRED` | Access token expired | 401 |
| `PERMISSION_DENIED` | Insufficient permissions | 403 |
| `NOT_FOUND` | Resource not found | 404 |
| `VALIDATION_ERROR` | Invalid request data | 400 |
| `SYNTAX_ERROR` | Configuration syntax error | 400 |
| `OPERATION_FAILED` | System operation failed | 500 |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable | 503 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |

### Error Response Structure
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": {
      "field": "username",
      "constraint": "required",
      "value": null
    },
    "recoveryActions": [
      "Provide a valid username",
      "Check the API documentation"
    ]
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:45Z",
    "requestId": "123e4567-e89b-12d3-a456-426614174000"
  }
}
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

| Endpoint Type | Limit | Window |
|--------------|-------|---------|
| Authentication | 5 requests | 15 minutes |
| Read operations | 100 requests | 1 minute |
| Write operations | 20 requests | 1 minute |
| System operations | 5 requests | 5 minutes |

Rate limit headers:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705318245
```

## Examples

### Complete Authentication Flow
```bash
# 1. Login
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'

# Response
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIs...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIs..."
  }
}

# 2. Use access token for API calls
curl http://localhost:8080/api/packages \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."

# 3. Refresh token when expired
curl -X POST http://localhost:8080/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refreshToken": "eyJhbGciOiJIUzI1NiIs..."}'
```

### Install Package with Progress
```javascript
// 1. Connect to WebSocket
const ws = new WebSocket('ws://localhost:8080/ws');

ws.onopen = () => {
  // 2. Authenticate
  ws.send(JSON.stringify({
    type: 'auth',
    token: accessToken
  }));
  
  // 3. Subscribe to job updates
  ws.send(JSON.stringify({
    type: 'subscribe',
    channels: ['jobs']
  }));
};

// 4. Handle progress updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'job.progress') {
    console.log(`Progress: ${data.data.progress}% - ${data.data.message}`);
  }
};

// 5. Install package
fetch('/api/packages/install', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    package: 'firefox'
  })
});
```

### Rebuild System with Validation
```javascript
// 1. Validate configuration
const validateRes = await fetch('/api/config/validate', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    content: newConfigContent
  })
});

if (!validateRes.ok) {
  // Handle validation errors
  return;
}

// 2. Update configuration
await fetch('/api/config', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    content: newConfigContent,
    message: 'Enable new service'
  })
});

// 3. Rebuild system
const rebuildRes = await fetch('/api/system/rebuild', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    action: 'switch'
  })
});

// 4. Monitor progress via WebSocket
```