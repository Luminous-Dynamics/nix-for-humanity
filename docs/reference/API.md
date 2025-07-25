# API Documentation

## Table of Contents
- [Overview](#overview)
- [Authentication](#authentication)
- [Common Headers](#common-headers)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
  - [Auth API](#auth-api)
  - [Package API](#package-api)
  - [Configuration API](#configuration-api)
  - [Service API](#service-api)
  - [Generation API](#generation-api)
  - [System API](#system-api)
  - [User API](#user-api)
- [WebSocket API](#websocket-api)
- [Examples](#examples)

## Overview

The Nix for Humanity API is a RESTful API that provides programmatic access to NixOS system management functions through natural language processing. All API endpoints are prefixed with `/api/`.

### Base URL
```
http://localhost:8080/api
```

### Content Type
All requests and responses use JSON:
```
Content-Type: application/json
```

## Authentication

The API uses JWT (JSON Web Token) authentication. Tokens are passed via cookies or Authorization header.

### Login
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
  "user": {
    "username": "alice",
    "groups": ["wheel", "users"],
    "role": "admin"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 3600
}
```

### Using the Token

Option 1: Cookie (automatic)
```http
Cookie: nixos-gui-token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Option 2: Authorization Header
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Common Headers

### Request Headers
```http
Accept: application/json
Content-Type: application/json
X-Requested-With: XMLHttpRequest
```

### Response Headers
```http
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1642531200
```

## Error Handling

All errors follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input provided",
    "details": {
      "field": "username",
      "constraint": "minLength",
      "value": "ab"
    },
    "timestamp": "2024-01-20T15:30:45.123Z",
    "requestId": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Missing or invalid authentication |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 400 | Invalid input data |
| `CONFLICT` | 409 | Resource conflict |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

## Endpoints

### Auth API

#### Login
```http
POST /api/auth/login
```

Request:
```json
{
  "username": "alice",
  "password": "secret123",
  "remember": true
}
```

Response:
```json
{
  "success": true,
  "user": {
    "username": "alice",
    "groups": ["wheel", "users"],
    "role": "admin",
    "lastLogin": "2024-01-20T15:30:45.123Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 3600
}
```

#### Logout
```http
POST /api/auth/logout
```

Response:
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

#### Get Session
```http
GET /api/auth/session
```

Response:
```json
{
  "authenticated": true,
  "user": {
    "username": "alice",
    "groups": ["wheel", "users"],
    "role": "admin"
  },
  "expiresAt": "2024-01-20T16:30:45.123Z"
}
```

#### Refresh Token
```http
POST /api/auth/refresh
```

Response:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 3600
}
```

### Package API

#### Search Packages
```http
GET /api/packages/search?q=firefox&limit=10&offset=0
```

Parameters:
- `q` (required): Search query
- `limit`: Results per page (default: 20, max: 100)
- `offset`: Pagination offset (default: 0)
- `channel`: Nix channel to search (default: current)

Response:
```json
{
  "results": [
    {
      "name": "firefox",
      "version": "109.0",
      "description": "A free and open source web browser",
      "homepage": "https://www.mozilla.org/firefox/",
      "license": "MPL-2.0",
      "installed": true,
      "platforms": ["x86_64-linux", "aarch64-linux"]
    }
  ],
  "total": 15,
  "limit": 10,
  "offset": 0
}
```

#### Get Package Details
```http
GET /api/packages/firefox
```

Response:
```json
{
  "name": "firefox",
  "version": "109.0",
  "description": "A free and open source web browser",
  "longDescription": "Mozilla Firefox is a free and open-source web browser...",
  "homepage": "https://www.mozilla.org/firefox/",
  "license": "MPL-2.0",
  "maintainers": ["john@example.com"],
  "platforms": ["x86_64-linux", "aarch64-linux"],
  "dependencies": [
    "gtk3",
    "libXt",
    "mime-types"
  ],
  "size": 215000000,
  "installed": true,
  "installedVersion": "108.0",
  "availableVersions": ["109.0", "108.0", "107.0"]
}
```

#### Install Package
```http
POST /api/packages/install
```

Request:
```json
{
  "package": "firefox",
  "version": "109.0"
}
```

Response:
```json
{
  "success": true,
  "message": "Package installation started",
  "jobId": "550e8400-e29b-41d4-a716-446655440000",
  "details": {
    "package": "firefox",
    "version": "109.0",
    "estimatedTime": 120
  }
}
```

#### Remove Package
```http
DELETE /api/packages/firefox
```

Response:
```json
{
  "success": true,
  "message": "Package marked for removal",
  "package": "firefox"
}
```

#### List Installed Packages
```http
GET /api/packages/installed?category=applications
```

Parameters:
- `category`: Filter by category
- `search`: Search in installed packages

Response:
```json
{
  "packages": [
    {
      "name": "firefox",
      "version": "108.0",
      "description": "A free and open source web browser",
      "category": "applications",
      "size": 215000000,
      "installedDate": "2024-01-15T10:00:00.000Z"
    }
  ],
  "total": 150,
  "categories": {
    "applications": 45,
    "development": 30,
    "system": 75
  }
}
```

### Configuration API

#### Get Current Configuration
```http
GET /api/config
```

Response:
```json
{
  "content": "{ config, pkgs, ... }:\n{\n  imports = [ ./hardware-configuration.nix ];\n  ...\n}",
  "path": "/etc/nixos/configuration.nix",
  "lastModified": "2024-01-20T15:00:00.000Z",
  "syntax": "nix"
}
```

#### Update Configuration
```http
PUT /api/config
```

Request:
```json
{
  "content": "{ config, pkgs, ... }:\n{\n  imports = [ ./hardware-configuration.nix ];\n  ...\n}",
  "validate": true
}
```

Response:
```json
{
  "success": true,
  "message": "Configuration updated",
  "validation": {
    "valid": true,
    "warnings": []
  },
  "backup": "/etc/nixos/configuration.nix.backup.20240120150000"
}
```

#### Validate Configuration
```http
POST /api/config/validate
```

Request:
```json
{
  "content": "{ config, pkgs, ... }:\n{\n  services.nginx.enable = true;\n}"
}
```

Response:
```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    {
      "line": 3,
      "column": 15,
      "message": "nginx service enabled but no sites configured"
    }
  ],
  "info": {
    "derivation": "/nix/store/...-nixos-system-...",
    "closureSize": 1250000000
  }
}
```

#### Compare Configurations
```http
GET /api/config/diff?from=current&to=proposed
```

Response:
```json
{
  "diff": [
    {
      "type": "added",
      "line": 15,
      "content": "+  services.nginx.enable = true;"
    },
    {
      "type": "removed",
      "line": 20,
      "content": "-  services.apache.enable = true;"
    }
  ],
  "summary": {
    "additions": 5,
    "deletions": 3,
    "modifications": 2
  }
}
```

### Service API

#### List Services
```http
GET /api/services?status=running&type=system
```

Parameters:
- `status`: Filter by status (running, stopped, failed)
- `type`: Filter by type (system, user)
- `search`: Search in service names/descriptions

Response:
```json
{
  "services": [
    {
      "name": "nginx.service",
      "description": "Nginx Web Server",
      "status": "running",
      "enabled": true,
      "type": "system",
      "pid": 1234,
      "memory": 52428800,
      "cpu": 0.5,
      "uptime": 3600
    }
  ],
  "total": 45,
  "byStatus": {
    "running": 30,
    "stopped": 10,
    "failed": 5
  }
}
```

#### Get Service Details
```http
GET /api/services/nginx.service
```

Response:
```json
{
  "name": "nginx.service",
  "description": "Nginx Web Server",
  "status": "running",
  "enabled": true,
  "type": "system",
  "pid": 1234,
  "user": "nginx",
  "group": "nginx",
  "dependencies": ["network.target"],
  "dependents": ["php-fpm.service"],
  "memory": {
    "current": 52428800,
    "peak": 104857600,
    "limit": 2147483648
  },
  "cpu": {
    "usage": 0.5,
    "time": 3600
  },
  "io": {
    "read": 1048576,
    "write": 2097152
  },
  "processes": [
    {
      "pid": 1234,
      "command": "nginx: master process",
      "cpu": 0.1,
      "memory": 10485760
    }
  ]
}
```

#### Control Service
```http
POST /api/services/nginx.service/start
POST /api/services/nginx.service/stop
POST /api/services/nginx.service/restart
POST /api/services/nginx.service/reload
```

Response:
```json
{
  "success": true,
  "action": "start",
  "service": "nginx.service",
  "newStatus": "running",
  "message": "Service started successfully"
}
```

#### Get Service Logs
```http
GET /api/services/nginx.service/logs?lines=100&since=1h
```

Parameters:
- `lines`: Number of lines (default: 100)
- `since`: Time range (e.g., "1h", "24h", "2024-01-20T00:00:00Z")
- `follow`: Stream logs (WebSocket upgrade)

Response:
```json
{
  "service": "nginx.service",
  "logs": [
    {
      "timestamp": "2024-01-20T15:30:45.123Z",
      "level": "info",
      "message": "Server started on port 80",
      "pid": 1234
    }
  ],
  "total": 100,
  "range": {
    "from": "2024-01-20T14:30:45.123Z",
    "to": "2024-01-20T15:30:45.123Z"
  }
}
```

### Generation API

#### List Generations
```http
GET /api/generations
```

Response:
```json
{
  "current": 42,
  "generations": [
    {
      "id": 42,
      "date": "2024-01-20T15:00:00.000Z",
      "current": true,
      "nixosVersion": "23.11",
      "configurationRevision": "abc123",
      "kernelVersion": "6.1.69",
      "label": "Updated nginx configuration",
      "packages": {
        "total": 1250,
        "added": 5,
        "removed": 2,
        "updated": 10
      }
    }
  ]
}
```

#### Switch Generation
```http
POST /api/generations/switch/41
```

Response:
```json
{
  "success": true,
  "message": "Switched to generation 41",
  "previousGeneration": 42,
  "currentGeneration": 41,
  "rebootRequired": false
}
```

#### Delete Generation
```http
DELETE /api/generations/40
```

Response:
```json
{
  "success": true,
  "message": "Generation 40 deleted",
  "freedSpace": 524288000
}
```

#### Compare Generations
```http
GET /api/generations/diff?from=41&to=42
```

Response:
```json
{
  "from": 41,
  "to": 42,
  "changes": {
    "packages": {
      "added": ["nginx-1.24.0"],
      "removed": ["apache-2.4.57"],
      "updated": [
        {
          "package": "firefox",
          "from": "108.0",
          "to": "109.0"
        }
      ]
    },
    "services": {
      "added": ["nginx.service"],
      "removed": ["apache.service"]
    },
    "configuration": {
      "diff": "...",
      "additions": 10,
      "deletions": 8
    }
  }
}
```

### System API

#### Get System Information
```http
GET /api/system/info
```

Response:
```json
{
  "hostname": "nixos-desktop",
  "nixosVersion": "23.11",
  "kernelVersion": "6.1.69",
  "architecture": "x86_64-linux",
  "uptime": 432000,
  "loadAverage": [0.5, 0.7, 0.8],
  "memory": {
    "total": 16777216000,
    "used": 8388608000,
    "free": 8388608000,
    "available": 10485760000
  },
  "disk": {
    "total": 512000000000,
    "used": 256000000000,
    "free": 256000000000,
    "percentage": 50
  },
  "cpu": {
    "model": "Intel Core i7-9700K",
    "cores": 8,
    "threads": 8,
    "usage": 25.5
  }
}
```

#### Get Hardware Information
```http
GET /api/system/hardware
```

Response:
```json
{
  "cpu": {
    "model": "Intel Core i7-9700K",
    "vendor": "GenuineIntel",
    "cores": 8,
    "threads": 8,
    "frequency": {
      "current": 3600,
      "min": 800,
      "max": 4900
    }
  },
  "memory": {
    "slots": [
      {
        "size": 8589934592,
        "type": "DDR4",
        "speed": 3200,
        "manufacturer": "Corsair"
      }
    ]
  },
  "graphics": [
    {
      "vendor": "NVIDIA",
      "model": "GeForce RTX 3080",
      "driver": "nvidia",
      "version": "545.29.06"
    }
  ],
  "storage": [
    {
      "device": "/dev/nvme0n1",
      "model": "Samsung 980 PRO",
      "size": 1000204886016,
      "type": "NVMe"
    }
  ]
}
```

### User API

#### List Users
```http
GET /api/users
```

Response:
```json
{
  "users": [
    {
      "username": "alice",
      "uid": 1000,
      "groups": ["wheel", "users", "video", "audio"],
      "shell": "/run/current-system/sw/bin/bash",
      "home": "/home/alice",
      "lastLogin": "2024-01-20T15:00:00.000Z"
    }
  ]
}
```

#### Get User Preferences
```http
GET /api/users/preferences
```

Response:
```json
{
  "theme": "dark",
  "language": "en",
  "dashboardLayout": {
    "widgets": ["system-info", "services", "packages"],
    "collapsed": ["logs"]
  },
  "notifications": {
    "email": false,
    "desktop": true,
    "sound": false
  }
}
```

#### Update User Preferences
```http
PUT /api/users/preferences
```

Request:
```json
{
  "theme": "light",
  "notifications": {
    "desktop": false
  }
}
```

Response:
```json
{
  "success": true,
  "message": "Preferences updated",
  "preferences": {
    "theme": "light",
    "language": "en",
    "notifications": {
      "email": false,
      "desktop": false,
      "sound": false
    }
  }
}
```

## WebSocket API

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8080/ws');

// Send authentication
ws.send(JSON.stringify({
  type: 'auth',
  token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
}));

// Subscribe to channels
ws.send(JSON.stringify({
  type: 'subscribe',
  channels: ['packages', 'services', 'logs']
}));
```

### Event Types

#### Package Events
```json
{
  "type": "package:installing",
  "data": {
    "package": "firefox",
    "version": "109.0",
    "progress": 45,
    "eta": 60
  }
}

{
  "type": "package:installed",
  "data": {
    "package": "firefox",
    "version": "109.0",
    "size": 215000000
  }
}
```

#### Service Events
```json
{
  "type": "service:status",
  "data": {
    "service": "nginx.service",
    "oldStatus": "stopped",
    "newStatus": "running",
    "pid": 1234
  }
}
```

#### Log Events
```json
{
  "type": "log:entry",
  "data": {
    "service": "nginx.service",
    "timestamp": "2024-01-20T15:30:45.123Z",
    "level": "error",
    "message": "Failed to bind to port 80: Address already in use"
  }
}
```

#### System Events
```json
{
  "type": "system:alert",
  "data": {
    "severity": "warning",
    "category": "disk",
    "message": "Disk usage above 90%",
    "details": {
      "mount": "/",
      "used": 461373440000,
      "total": 512000000000,
      "percentage": 90.1
    }
  }
}
```

## Examples

### Complete Package Installation Flow

```javascript
// 1. Search for package
const searchResponse = await fetch('/api/packages/search?q=firefox');
const { results } = await searchResponse.json();

// 2. Get package details
const detailsResponse = await fetch(`/api/packages/${results[0].name}`);
const packageInfo = await detailsResponse.json();

// 3. Install package
const installResponse = await fetch('/api/packages/install', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    package: packageInfo.name,
    version: packageInfo.version
  })
});

const { jobId } = await installResponse.json();

// 4. Monitor progress via WebSocket
ws.send(JSON.stringify({
  type: 'subscribe',
  channels: [`job:${jobId}`]
}));

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'job:progress') {
    console.log(`Installation ${data.progress}% complete`);
  }
};
```

### Service Management with Logs

```javascript
// 1. Get service status
const statusResponse = await fetch('/api/services/nginx.service');
const service = await statusResponse.json();

// 2. Start service if stopped
if (service.status === 'stopped') {
  await fetch('/api/services/nginx.service/start', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
}

// 3. Stream logs
const ws = new WebSocket('ws://localhost:8080/ws');
ws.send(JSON.stringify({
  type: 'auth',
  token: token
}));

ws.send(JSON.stringify({
  type: 'subscribe',
  channels: ['logs:nginx.service']
}));

ws.onmessage = (event) => {
  const { type, data } = JSON.parse(event.data);
  if (type === 'log:entry') {
    console.log(`[${data.timestamp}] ${data.message}`);
  }
};
```

### Configuration Update with Validation

```javascript
// 1. Get current configuration
const configResponse = await fetch('/api/config');
const { content } = await configResponse.json();

// 2. Modify configuration
const newConfig = content.replace(
  'services.nginx.enable = false;',
  'services.nginx.enable = true;'
);

// 3. Validate changes
const validateResponse = await fetch('/api/config/validate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({ content: newConfig })
});

const validation = await validateResponse.json();

// 4. Apply if valid
if (validation.valid) {
  await fetch('/api/config', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ 
      content: newConfig,
      validate: true 
    })
  });
}