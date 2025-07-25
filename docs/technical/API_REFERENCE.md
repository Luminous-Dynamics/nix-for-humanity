# 🔌 API Reference - Nix for Humanity

> Complete API documentation for developers integrating with or extending Nix for Humanity

**Last Updated**: 2025-07-25
**Status**: Current
**Audience**: Developers

## Overview

The Nix for Humanity API enables developers to:
- Integrate natural language processing into their applications
- Extend the AI partner's capabilities with custom plugins
- Build on top of the partnership framework
- Access learning and adaptation features

## Table of Contents

- [Core API](#core-api)
- [Natural Language Processing](#natural-language-processing)
- [Partnership Management](#partnership-management)
- [Learning System](#learning-system)
- [Plugin Development](#plugin-development)
- [Security & Privacy](#security--privacy)
- [Error Handling](#error-handling)
- [Examples](#examples)

## Core API

### Partnership

The main entry point for interacting with the AI partner.

```typescript
class Partnership {
  constructor(config?: PartnershipConfig)
  
  // Process natural language input
  async process(input: string, context?: Context): Promise<Response>
  
  // Get current partnership state
  getState(): PartnershipState
  
  // Manage partnership lifecycle
  async initialize(): Promise<void>
  async pause(): Promise<void>
  async resume(): Promise<void>
  async reset(): Promise<void>
}

interface PartnershipConfig {
  // User preferences
  language?: string              // Default: 'en'
  voiceEnabled?: boolean         // Default: true
  learningEnabled?: boolean      // Default: true
  privacyMode?: PrivacyLevel     // Default: 'balanced'
  
  // System configuration
  modelPath?: string             // Path to local AI model
  pluginDirectory?: string       // Custom plugins location
  dataDirectory?: string         // User data storage
  
  // Advanced options
  debug?: boolean                // Enable debug logging
  metrics?: boolean              // Collect anonymous metrics
}

enum PrivacyLevel {
  MINIMAL = 'minimal',           // No persistence, no learning
  BALANCED = 'balanced',         // Learn patterns, respect privacy
  FULL = 'full'                  // Maximum learning and adaptation
}
```

### Response Types

```typescript
interface Response {
  // The partnership's understanding
  intent: Intent
  confidence: number             // 0.0 to 1.0
  
  // Generated response
  message: string                // Natural language response
  actions?: Action[]             // System actions to perform
  
  // Learning opportunity
  learning?: LearningOpportunity
  
  // Metadata
  processingTime: number         // Milliseconds
  modelVersion: string
}

interface Intent {
  type: IntentType
  entities: Entity[]
  context: ContextualInfo
}

enum IntentType {
  INSTALL_SOFTWARE = 'install_software',
  UPDATE_SYSTEM = 'update_system',
  QUERY_STATUS = 'query_status',
  CONFIGURE_SETTING = 'configure_setting',
  TROUBLESHOOT = 'troubleshoot',
  LEARN_PREFERENCE = 'learn_preference',
  UNKNOWN = 'unknown'
}
```

## Natural Language Processing

### NLP Engine

```typescript
class NLPEngine {
  // Parse natural language input
  async parse(input: string): Promise<ParseResult>
  
  // Generate natural response
  async generate(intent: Intent, context: Context): Promise<string>
  
  // Detect language
  async detectLanguage(input: string): Promise<string>
  
  // Translate if needed
  async translate(text: string, targetLang: string): Promise<string>
}

interface ParseResult {
  tokens: Token[]
  entities: Entity[]
  intent: Intent
  sentiment: Sentiment
  language: string
}

interface Entity {
  type: EntityType
  value: string
  confidence: number
  position: [start: number, end: number]
}

enum EntityType {
  SOFTWARE_NAME = 'software_name',
  FILE_PATH = 'file_path',
  SETTING_NAME = 'setting_name',
  TIME_EXPRESSION = 'time_expression',
  QUANTITY = 'quantity'
}
```

### Context Management

```typescript
class ContextManager {
  // Get current context
  getCurrent(): Context
  
  // Update context with new information
  update(updates: Partial<Context>): void
  
  // Save context checkpoint
  saveCheckpoint(): string
  
  // Restore from checkpoint
  restoreCheckpoint(id: string): void
}

interface Context {
  // Conversation context
  conversationId: string
  turnCount: number
  history: ConversationTurn[]
  
  // System context
  systemState: SystemState
  userPreferences: UserPreferences
  
  // Temporal context
  timestamp: number
  timezone: string
  locale: string
}
```

## Partnership Management

### User Preferences

```typescript
class PreferenceManager {
  // Get all preferences
  getAll(): UserPreferences
  
  // Update preferences
  async update(prefs: Partial<UserPreferences>): Promise<void>
  
  // Get specific preference
  get<K extends keyof UserPreferences>(
    key: K
  ): UserPreferences[K]
  
  // Reset to defaults
  async reset(): Promise<void>
  
  // Export preferences
  async export(): Promise<string>
  
  // Import preferences
  async import(data: string): Promise<void>
}

interface UserPreferences {
  // Communication style
  formalityLevel: 'casual' | 'balanced' | 'formal'
  verbosity: 'concise' | 'balanced' | 'detailed'
  
  // Learning preferences
  adaptationSpeed: 'slow' | 'moderate' | 'fast'
  patternMemory: boolean
  
  // Privacy settings
  dataRetention: number          // Days to retain data
  shareAnonymousData: boolean
  
  // Interaction preferences
  confirmBeforeActions: boolean
  explainActions: boolean
  showConfidence: boolean
}
```

### Session Management

```typescript
class SessionManager {
  // Start new session
  async startSession(): Promise<Session>
  
  // Get active session
  getActiveSession(): Session | null
  
  // End session
  async endSession(sessionId: string): Promise<void>
  
  // List recent sessions
  async listSessions(limit?: number): Promise<Session[]>
  
  // Resume session
  async resumeSession(sessionId: string): Promise<Session>
}

interface Session {
  id: string
  startTime: number
  endTime?: number
  interactions: number
  state: SessionState
}
```

## Learning System

### Pattern Learning

```typescript
class LearningEngine {
  // Learn from interaction
  async learn(
    interaction: Interaction,
    outcome: Outcome
  ): Promise<LearningResult>
  
  // Get learned patterns
  getPatterns(filter?: PatternFilter): Pattern[]
  
  // Forget specific patterns
  async forget(patternId: string): Promise<void>
  
  // Export learning data
  async exportLearning(): Promise<LearningData>
  
  // Reset all learning
  async resetLearning(): Promise<void>
}

interface Pattern {
  id: string
  type: PatternType
  confidence: number
  frequency: number
  lastUsed: number
  examples: string[]
}

enum PatternType {
  PHRASE_PREFERENCE = 'phrase_preference',
  WORKFLOW_SEQUENCE = 'workflow_sequence',
  ERROR_RECOVERY = 'error_recovery',
  TIME_PREFERENCE = 'time_preference',
  STYLE_PREFERENCE = 'style_preference'
}

interface LearningResult {
  learned: boolean
  patternId?: string
  improvement: number
  message?: string
}
```

### Adaptation System

```typescript
class AdaptationEngine {
  // Adapt response based on learning
  async adapt(
    baseResponse: Response,
    patterns: Pattern[]
  ): Promise<Response>
  
  // Get adaptation suggestions
  getSuggestions(context: Context): Suggestion[]
  
  // Apply adaptation
  async applyAdaptation(
    suggestionId: string
  ): Promise<void>
  
  // Measure adaptation effectiveness
  getEffectiveness(): AdaptationMetrics
}

interface Suggestion {
  id: string
  type: 'phrase' | 'timing' | 'workflow' | 'style'
  description: string
  confidence: number
  impact: 'low' | 'medium' | 'high'
}
```

## Plugin Development

### Plugin Interface

```typescript
interface Plugin {
  // Metadata
  name: string
  version: string
  description: string
  author: string
  
  // Lifecycle hooks
  initialize?(context: PluginContext): Promise<void>
  activate?(): Promise<void>
  deactivate?(): Promise<void>
  
  // Intent handlers
  handlers?: IntentHandler[]
  
  // Extensions
  entities?: EntityExtension[]
  actions?: ActionExtension[]
}

interface IntentHandler {
  intent: string | RegExp
  priority?: number
  
  async handle(
    intent: Intent,
    context: Context
  ): Promise<HandlerResult>
}

interface HandlerResult {
  handled: boolean
  response?: Response
  fallthrough?: boolean
}
```

### Plugin Development Example

```typescript
// example-plugin.ts
import { Plugin, Intent, Context, HandlerResult } from 'nix-for-humanity';

const GitPlugin: Plugin = {
  name: 'git-helper',
  version: '1.0.0',
  description: 'Natural language git commands',
  author: 'Community',
  
  handlers: [{
    intent: /git|repository|commit/i,
    
    async handle(intent: Intent, context: Context): Promise<HandlerResult> {
      if (intent.type === 'VERSION_CONTROL') {
        const action = detectGitAction(intent);
        
        return {
          handled: true,
          response: {
            intent,
            confidence: 0.9,
            message: `I'll help you ${action.description}`,
            actions: [{
              type: 'execute',
              command: action.command,
              requireConfirmation: action.risky
            }]
          }
        };
      }
      
      return { handled: false };
    }
  }]
};

export default GitPlugin;
```

### Plugin Registration

```typescript
class PluginManager {
  // Register plugin
  async register(plugin: Plugin): Promise<void>
  
  // Load plugin from file
  async loadPlugin(path: string): Promise<void>
  
  // List active plugins
  getPlugins(): Plugin[]
  
  // Disable plugin
  async disablePlugin(name: string): Promise<void>
  
  // Remove plugin
  async removePlugin(name: string): Promise<void>
}
```

## Security & Privacy

### Permission System

```typescript
class PermissionManager {
  // Check permission
  async check(
    action: string,
    resource?: string
  ): Promise<boolean>
  
  // Request permission
  async request(
    permission: Permission
  ): Promise<PermissionResult>
  
  // List granted permissions
  getGranted(): Permission[]
  
  // Revoke permission
  async revoke(permissionId: string): Promise<void>
}

interface Permission {
  id: string
  action: PermissionAction
  resource?: string
  granted?: boolean
  grantedAt?: number
  expiresAt?: number
}

enum PermissionAction {
  INSTALL_SOFTWARE = 'install_software',
  MODIFY_SYSTEM = 'modify_system',
  ACCESS_NETWORK = 'access_network',
  READ_FILES = 'read_files',
  WRITE_FILES = 'write_files',
  LEARN_PATTERNS = 'learn_patterns'
}
```

### Privacy Controls

```typescript
class PrivacyManager {
  // Get privacy report
  async getPrivacyReport(): Promise<PrivacyReport>
  
  // Delete user data
  async deleteUserData(
    options?: DeleteOptions
  ): Promise<void>
  
  // Export user data
  async exportUserData(): Promise<UserDataExport>
  
  // Pause data collection
  pauseCollection(): void
  
  // Resume data collection
  resumeCollection(): void
}

interface PrivacyReport {
  dataCollected: DataCategory[]
  storageUsed: number
  lastCleaned: number
  retentionPolicy: string
  anonymousSharing: boolean
}

interface DeleteOptions {
  patterns?: boolean
  history?: boolean
  preferences?: boolean
  everything?: boolean
}
```

## Error Handling

### Error Types

```typescript
// Base error class
class PartnershipError extends Error {
  code: string
  recoverable: boolean
  suggestion?: string
}

// Specific error types
class IntentNotUnderstoodError extends PartnershipError {
  code = 'INTENT_NOT_UNDERSTOOD'
  recoverable = true
}

class PermissionDeniedError extends PartnershipError {
  code = 'PERMISSION_DENIED'
  recoverable = true
}

class SystemError extends PartnershipError {
  code = 'SYSTEM_ERROR'
  recoverable = false
}

class NetworkError extends PartnershipError {
  code = 'NETWORK_ERROR'
  recoverable = true
}
```

### Error Recovery

```typescript
class ErrorRecovery {
  // Register recovery handler
  registerHandler(
    errorType: string,
    handler: RecoveryHandler
  ): void
  
  // Attempt recovery
  async recover(
    error: PartnershipError,
    context: Context
  ): Promise<RecoveryResult>
  
  // Get recovery suggestions
  getSuggestions(
    error: PartnershipError
  ): RecoverySuggestion[]
}

type RecoveryHandler = (
  error: PartnershipError,
  context: Context
) => Promise<RecoveryResult>

interface RecoveryResult {
  recovered: boolean
  action?: Action
  message?: string
}
```

## Examples

### Basic Usage

```typescript
import { Partnership } from 'nix-for-humanity';

// Initialize partnership
const partner = new Partnership({
  language: 'en',
  learningEnabled: true,
  privacyMode: 'balanced'
});

await partner.initialize();

// Process natural language
const response = await partner.process(
  "install firefox please"
);

console.log(response.message);
// "I'll install Firefox for you. This will take about 2 minutes."

if (response.actions) {
  for (const action of response.actions) {
    await executeAction(action);
  }
}
```

### Learning from Feedback

```typescript
// Process with learning
const response = await partner.process(
  "install that browser we talked about"
);

// Provide feedback
if (response.learning) {
  await partner.provideFeedback({
    interactionId: response.learning.id,
    success: true,
    correction: null
  });
}
```

### Custom Plugin

```typescript
// Create custom plugin
const customPlugin: Plugin = {
  name: 'my-workflow',
  version: '1.0.0',
  description: 'Personal workflow automation',
  
  handlers: [{
    intent: /morning routine/i,
    
    async handle(intent, context) {
      return {
        handled: true,
        response: {
          intent,
          confidence: 0.95,
          message: "Starting your morning routine...",
          actions: [
            { type: 'open', application: 'firefox' },
            { type: 'open', application: 'terminal' },
            { type: 'execute', command: 'status-check' }
          ]
        }
      };
    }
  }]
};

// Register plugin
await pluginManager.register(customPlugin);
```

### Privacy-First Usage

```typescript
// Minimal privacy mode
const privatePartner = new Partnership({
  privacyMode: 'minimal',
  learningEnabled: false,
  metrics: false
});

// Check what data is stored
const report = await privatePartner
  .getPrivacyManager()
  .getPrivacyReport();

// Delete all data
await privatePartner
  .getPrivacyManager()
  .deleteUserData({ everything: true });
```

## WebSocket API

For real-time interactions:

```typescript
import { PartnershipWebSocket } from 'nix-for-humanity/ws';

const ws = new PartnershipWebSocket('ws://localhost:8080');

ws.on('connected', () => {
  console.log('Connected to AI partner');
});

ws.on('response', (response: Response) => {
  console.log('Partner says:', response.message);
});

ws.on('learning', (opportunity: LearningOpportunity) => {
  // Handle learning opportunity
});

// Send message
ws.send('install firefox');
```

## REST API

HTTP endpoints for integration:

```bash
# Process natural language
POST /api/process
Content-Type: application/json

{
  "input": "install firefox",
  "context": {
    "sessionId": "abc123"
  }
}

# Response
{
  "intent": {
    "type": "install_software",
    "entities": [{
      "type": "software_name",
      "value": "firefox"
    }]
  },
  "confidence": 0.95,
  "message": "I'll install Firefox for you.",
  "actions": [{
    "type": "install",
    "package": "firefox"
  }]
}
```

## Rate Limiting

API calls are rate limited:
- **Default**: 60 requests per minute
- **Authenticated**: 600 requests per minute
- **Learning endpoints**: 10 requests per minute

## Versioning

The API follows semantic versioning:
- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes

Current version: 1.0.0

## Support

- **Documentation**: https://docs.luminousdynamics.org
- **GitHub**: https://github.com/Luminous-Dynamics/nix-for-humanity
- **Discord**: https://discord.gg/luminous-dynamics
- **Email**: developers@luminousdynamics.org

---

**Remember**: This API is designed for partnership, not control. Every endpoint respects user sovereignty and privacy by design.

*"Code with consciousness, develop with respect."*