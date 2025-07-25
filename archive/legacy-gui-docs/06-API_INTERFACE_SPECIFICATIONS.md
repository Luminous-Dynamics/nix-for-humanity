# API & Interface Specifications - Nix for Humanity

## Overview

This document defines all interfaces between components, ensuring modularity, extensibility, and clear contracts for development.

## Core API Architecture

```
┌─────────────────────────────────────────┐
│            Web Interface                 │
│         (REST + WebSocket)              │
├─────────────────────────────────────────┤
│              Core API                    │
│         /api/v1/* (JSON-RPC)            │
├─────────────────────────────────────────┤
│            Intent Engine                 │
│          (Internal Message Bus)          │
├─────────────────────────────────────────┤
│             Nix Bridge                   │
│         (D-Bus + Unix Socket)           │
└─────────────────────────────────────────┘
```

## REST API Specification

### Base URL
```
Development: http://localhost:3000/api/v1
Production: https://nix.local/api/v1
```

### Authentication
```http
POST /api/v1/auth/token
Content-Type: application/json

{
  "method": "local",
  "credentials": {
    "user": "current-user"
  }
}

Response:
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "expires": "2024-01-01T00:00:00Z"
}
```

### Core Endpoints

#### 1. Intent Processing
```http
POST /api/v1/intent
Authorization: Bearer {token}
Content-Type: application/json

{
  "input": "install firefox",
  "context": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2024-01-01T00:00:00Z",
    "mode": "voice"
  }
}

Response:
{
  "intent": {
    "action": "install",
    "target": "firefox",
    "confidence": 0.95
  },
  "status": "pending",
  "id": "550e8400-e29b-41d4-a716-446655440001"
}
```

#### 2. Action Execution
```http
POST /api/v1/execute
Authorization: Bearer {token}
Content-Type: application/json
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440003

{
  "intent_id": "550e8400-e29b-41d4-a716-446655440001",
  "confirm": true,
  "options": {
    "channel": "stable"
  }
}

Response:
{
  "job_id": "550e8400-e29b-41d4-a716-446655440002",
  "status": "running",
  "progress": 0,
  "eta": "60s"
}
```

#### 3. Status Monitoring
```http
GET /api/v1/status/{job_id}
Authorization: Bearer {token}

Response:
{
  "job_id": "550e8400-e29b-41d4-a716-446655440002",
  "status": "running",
  "progress": 45,
  "logs": [
    {"time": "2024-01-01T00:00:01Z", "message": "Downloading firefox..."},
    {"time": "2024-01-01T00:00:15Z", "message": "Installing dependencies..."}
  ],
  "eta": "30s"
}
```

#### 4. Package Search
```http
GET /api/v1/packages/search?q=editor&limit=10
Authorization: Bearer {token}

Response:
{
  "results": [
    {
      "name": "vscode",
      "description": "Visual Studio Code editor",
      "version": "1.85.0",
      "installed": false
    },
    {
      "name": "neovim",
      "description": "Vim-based text editor",
      "version": "0.9.4",
      "installed": true
    }
  ],
  "total": 47,
  "query_time": "0.23s"
}
```

#### 5. System State
```http
GET /api/v1/system/state
Authorization: Bearer {token}

Response:
{
  "generation": 142,
  "uptime": "5d 3h 42m",
  "last_update": "2024-01-01T00:00:00Z",
  "resources": {
    "cpu": 12.5,
    "memory": 2048,
    "disk": 45.2
  },
  "services": {
    "running": 42,
    "failed": 0,
    "stopped": 8
  }
}
```

#### 6. Configuration Management
```http
GET /api/v1/config
Authorization: Bearer {token}

Response:
{
  "current": {
    "hash": "abc123...",
    "modified": "2024-01-01T00:00:00Z",
    "valid": true
  },
  "pending_changes": []
}

PUT /api/v1/config
Authorization: Bearer {token}
Content-Type: application/json

{
  "changes": [
    {
      "type": "add_package",
      "package": "firefox"
    }
  ],
  "message": "Added Firefox browser"
}
```

## WebSocket API

### Connection
```javascript
const ws = new WebSocket('ws://localhost:3000/ws');

ws.on('open', () => {
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
  }));
});
```

### Message Types

#### Progress Updates
```json
{
  "type": "progress",
  "job_id": "550e8400-e29b-41d4-a716-446655440002",
  "progress": 75,
  "message": "Building configuration..."
}
```

#### System Events
```json
{
  "type": "system_event",
  "event": "service_failed",
  "service": "nginx",
  "timestamp": "2024-01-01T00:00:00Z",
  "severity": "warning"
}
```

#### Intent Suggestions
```json
{
  "type": "suggestion",
  "trigger": "time_based",
  "message": "Time for your daily backup?",
  "action": "backup_system"
}
```

## Intent Engine Interface

### Intent Structure
```typescript
interface Intent {
  id: string;
  raw_input: string;
  parsed: {
    action: ActionType;
    target?: string;
    modifiers?: Modifier[];
    confidence: number;
  };
  context: Context;
  timestamp: Date;
}

enum ActionType {
  Install = "install",
  Remove = "remove",
  Start = "start",
  Stop = "stop",
  Enable = "enable",
  Disable = "disable",
  Configure = "configure",
  Search = "search",
  Fix = "fix",
  Update = "update",
  Rollback = "rollback"
}

interface Modifier {
  type: "channel" | "version" | "option";
  value: string;
}

interface Context {
  session_id: string;
  user_preferences: UserPreferences;
  system_state: SystemState;
  history: Intent[];
}
```

### Pattern Matching API
```javascript
class PatternMatcher {
  addPattern(pattern) {
    // pattern = {
    //   regex: RegExp,
    //   action: ActionType,
    //   extractor: Function,
    //   priority: number
    // }
  }

  match(input) {
    // Returns: Intent | null
  }

  train(input, correctIntent) {
    // Improves matching over time
  }
}
```

## Nix Bridge Interface

### D-Bus Service
```
Service: org.nixos.NixForHumanity
Object: /org/nixos/NixForHumanity
Interface: org.nixos.NixForHumanity.Manager

Methods:
  - SearchPackages(query: string) -> packages: array<Package>
  - InstallPackage(name: string, options: dict) -> job_id: string
  - RemovePackage(name: string) -> job_id: string
  - GetSystemInfo() -> info: SystemInfo
  - RebuildSystem(config: string) -> job_id: string
  - RollbackSystem(generation: int) -> success: bool

Signals:
  - JobProgress(job_id: string, progress: int, message: string)
  - JobCompleted(job_id: string, success: bool, result: string)
  - SystemStateChanged(state: SystemState)
```

### Unix Socket Protocol
```
Socket: /run/nix-for-humanity/control.sock
Permissions: 0660 (rw-rw----)
Owner: root:nix-helpers
Security: Only processes in 'nix-helpers' group can access

Protocol: JSON-RPC 2.0

Request:
{
  "jsonrpc": "2.0",
  "method": "install_package",
  "params": {
    "package": "firefox",
    "channel": "stable"
  },
  "id": 1
}

Response:
{
  "jsonrpc": "2.0",
  "result": {
    "job_id": "550e8400-e29b-41d4-a716-446655440002"
  },
  "id": 1
}
```

## Plugin Interface

### Plugin Manifest
```json
{
  "name": "home-automation",
  "version": "1.0.0",
  "description": "Smart home control through Nix",
  "author": "Community",
  "permissions": [
    "network",
    "system.services"
  ],
  "intents": [
    {
      "pattern": "turn (on|off) the lights",
      "handler": "handleLights"
    }
  ],
  "hooks": {
    "beforeInstall": "checkDependencies",
    "afterSystemBuild": "updateAutomation"
  }
}
```

### Plugin API
```typescript
interface Plugin {
  name: string;
  version: string;
  
  // Lifecycle
  onLoad(api: PluginAPI): Promise<void>;
  onUnload(): Promise<void>;
  
  // Intent handling
  handleIntent?(intent: Intent): Promise<Result>;
  
  // UI extension
  getUIComponents?(): UIComponent[];
  
  // System hooks
  hooks?: {
    [key: string]: (data: any) => Promise<void>;
  };
}

interface PluginAPI {
  // Core functionality
  executeNixCommand(cmd: string[]): Promise<string>;
  modifyConfig(changes: ConfigChange[]): Promise<void>;
  
  // User interaction
  showNotification(message: string): void;
  askUser(question: string, options: string[]): Promise<string>;
  
  // Data storage
  store: {
    get(key: string): Promise<any>;
    set(key: string, value: any): Promise<void>;
  };
  
  // Event system
  on(event: string, handler: Function): void;
  emit(event: string, data: any): void;
}
```

## Voice Interface Specification

### Speech Recognition API
```javascript
class VoiceInterface {
  constructor(options = {}) {
    this.language = options.language || 'en-US';
    this.continuous = options.continuous || false;
    this.interimResults = options.interimResults || true;
  }
  
  start() {
    // Returns: Promise<void>
  }
  
  stop() {
    // Returns: Promise<void>
  }
  
  on(event, handler) {
    // Events: 'result', 'error', 'end', 'soundstart', 'soundend'
  }
}

// Usage
const voice = new VoiceInterface();

voice.on('result', (event) => {
  const transcript = event.results[0][0].transcript;
  const confidence = event.results[0][0].confidence;
  
  if (confidence > 0.8) {
    processIntent(transcript);
  }
});
```

### Speech Synthesis API
```javascript
class Speaker {
  speak(text, options = {}) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = options.rate || 1.0;
    utterance.pitch = options.pitch || 1.0;
    utterance.volume = options.volume || 1.0;
    utterance.voice = options.voice || this.defaultVoice;
    
    return new Promise((resolve) => {
      utterance.onend = resolve;
      speechSynthesis.speak(utterance);
    });
  }
  
  stop() {
    speechSynthesis.cancel();
  }
}
```

## Learning Engine Interface

### Pattern Storage
```typescript
interface Pattern {
  id: string;
  input: string;
  intent: Intent;
  outcome: Outcome;
  timestamp: Date;
  weight: number;
}

interface Outcome {
  success: boolean;
  user_correction?: Intent;
  execution_time: number;
  user_satisfaction?: number;
}

class LearningEngine {
  recordPattern(pattern: Pattern): void;
  
  getPrediction(input: string): Prediction;
  
  updateWeights(feedback: Feedback): void;
  
  exportPatterns(): Pattern[];
  
  importPatterns(patterns: Pattern[]): void;
}
```

### Adaptation API
```javascript
class AdaptationEngine {
  getUserProfile() {
    return {
      skill_level: 'beginner' | 'intermediate' | 'advanced',
      preferences: {
        verbosity: 'minimal' | 'normal' | 'detailed',
        confirmations: 'always' | 'smart' | 'never',
        animations: boolean,
        voice_feedback: boolean
      },
      patterns: {
        common_actions: Action[],
        peak_times: TimeRange[],
        error_rate: number
      }
    };
  }
  
  adaptInterface(profile) {
    // Returns UI configuration based on profile
  }
  
  suggestAction(context) {
    // Returns next likely action based on patterns
  }
}
```

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "PACKAGE_NOT_FOUND",
    "message": "Firefox package not found in current channel",
    "details": {
      "searched_channels": ["stable", "unstable"],
      "similar_packages": ["firefox-esr", "firefox-bin"]
    },
    "user_message": "I couldn't find Firefox. Would you like to search for similar browsers?",
    "recovery_actions": [
      {
        "label": "Search browsers",
        "action": "search_category",
        "params": {"category": "browsers"}
      },
      {
        "label": "Try different channel",
        "action": "search_package",
        "params": {"package": "firefox", "channel": "unstable"}
      }
    ]
  }
}
```

### Error Codes
```
AUTH_FAILED: Authentication failed
INTENT_UNCLEAR: Could not understand request
PACKAGE_NOT_FOUND: Package doesn't exist
BUILD_FAILED: System build failed
PERMISSION_DENIED: Operation requires elevation
NETWORK_ERROR: Network connection failed
ROLLBACK_FAILED: Could not rollback system
STATE_CORRUPTED: System state inconsistent
```

## Security Specifications

### Permission Model
```typescript
enum Permission {
  READ_SYSTEM = "system.read",
  MODIFY_SYSTEM = "system.write",
  INSTALL_PACKAGES = "packages.install",
  REMOVE_PACKAGES = "packages.remove",
  MANAGE_SERVICES = "services.manage",
  ACCESS_NETWORK = "network.access",
  READ_USER_DATA = "user.read",
  WRITE_USER_DATA = "user.write"
}

interface SecurityContext {
  user: User;
  permissions: Permission[];
  sudo_available: boolean;
  rate_limits: RateLimits;
}
```

### Rate Limiting
```yaml
Default Limits:
  intent_processing: 60/minute
  package_operations: 10/minute
  system_rebuilds: 5/hour
  api_calls: 1000/hour

Elevated Limits (authenticated):
  intent_processing: 300/minute
  package_operations: 30/minute
  system_rebuilds: 20/hour
  api_calls: 10000/hour
```

## Versioning Strategy

### API Versioning
- URL: `/api/v1/`, `/api/v2/`
- Breaking changes increment major version
- Backward compatibility for 2 major versions
- Deprecation warnings 6 months before removal

### Message Versioning
```json
{
  "version": "1.0",
  "type": "intent",
  "data": {...}
}
```

### Schema Migration Strategy
Database schema migrations are handled automatically:
- Migrations run on application startup
- Forward-only migrations (no rollback)
- Each migration is idempotent
- Schema version tracked in metadata table
- Zero-downtime migrations for pattern store

Example:
```sql
-- Migration 001_add_confidence_scores.sql
ALTER TABLE patterns ADD COLUMN IF NOT EXISTS confidence REAL DEFAULT 0.5;
```

## Testing Specifications

### Integration Test Interface
```javascript
class TestHarness {
  async setupTestEnvironment() {
    // Creates isolated test environment
  }
  
  async simulateUserInput(input: string) {
    // Simulates complete flow
  }
  
  async verifySystemState(expected: SystemState) {
    // Validates final state
  }
  
  async cleanup() {
    // Restores original state
  }
}
```

### Mock Interfaces
```javascript
class MockNixBridge {
  constructor(responses = {}) {
    this.responses = responses;
  }
  
  async searchPackages(query) {
    return this.responses.packages || [];
  }
  
  async installPackage(name) {
    return this.responses.install || { job_id: 'mock-job' };
  }
}
```

## Performance Requirements

### Response Time SLAs
```yaml
Intent Parsing: <50ms (p99)
Package Search: <200ms (p99) cached, <1s uncached
UI Response: <100ms for any interaction
Voice Recognition: <500ms to start listening
System Rebuild: Show progress within 2s

API Rate Limits:
- 1000 requests/second sustained
- 5000 requests/second burst
- 100 concurrent WebSocket connections per user
```

## Conclusion

These specifications provide a complete contract for all components of Nix for Humanity. They ensure:

1. **Modularity**: Components can be developed independently
2. **Extensibility**: Plugins can add new functionality
3. **Reliability**: Clear error handling and recovery
4. **Security**: Proper permission model
5. **Performance**: Defined SLAs and limits

Following these specifications ensures a coherent, maintainable, and extensible system that can evolve while maintaining stability.