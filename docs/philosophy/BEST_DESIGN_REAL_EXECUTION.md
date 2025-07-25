# 🎯 Best Design: Layered Reality Approach

## The Problem with Binary Thinking

We don't need "simulation mode" vs "real mode". We need the right tool for each situation.

## The Layered Approach

### Layer 1: Intent Recognition (Pure Functions)
```javascript
// This needs no execution at all
function recognizeIntent(input: string): Intent {
  // Pure pattern matching - no side effects
  return { type: 'install', package: 'firefox' };
}

// Test without any execution
test('recognizes install intent', () => {
  expect(recognizeIntent('install firefox')).toEqual({
    type: 'install',
    package: 'firefox'
  });
});
```

### Layer 2: Command Generation (Pure Functions)
```javascript
// Generate commands without executing
function generateCommand(intent: Intent): NixCommand {
  return {
    command: 'nix-env',
    args: ['-iA', `nixpkgs.${intent.package}`],
    description: `Install ${intent.package}`
  };
}

// Test command generation separately
test('generates correct nix command', () => {
  const cmd = generateCommand({ type: 'install', package: 'firefox' });
  expect(cmd.args).toContain('nixpkgs.firefox');
});
```

### Layer 3: Execution (With Options)
```javascript
// Real execution with safety options
async function executeCommand(cmd: NixCommand, options: ExecutionOptions = {}) {
  // Option 1: Dry run (real NixOS feature)
  if (options.dryRun) {
    cmd.args.push('--dry-run');
    const result = await exec(cmd);
    return { ...result, dryRun: true };
  }
  
  // Option 2: Confirmation required
  if (options.requireConfirmation) {
    const confirmed = await ui.confirm(`Execute: ${cmd.description}?`);
    if (!confirmed) return { cancelled: true };
  }
  
  // Option 3: Just execute
  return await exec(cmd);
}
```

## The Right Tool for Each Job

### For Unit Testing
```javascript
// Mock only at the boundary
jest.mock('./executor', () => ({
  exec: jest.fn().mockResolvedValue({ success: true })
}));

// Test the logic, not the execution
test('install command flow', async () => {
  const intent = recognizeIntent('install firefox');
  const command = generateCommand(intent);
  expect(command.command).toBe('nix-env');
  // Don't test actual installation in unit tests
});
```

### For Integration Testing
```bash
# Use a real NixOS container
docker run -it nixos/nix bash -c "
  nix-env -iA nixpkgs.hello --dry-run
  echo 'Would install hello package'
"
```

### For Development
```javascript
// Use --dry-run by default in dev
const isDev = process.env.NODE_ENV === 'development';
const defaultOptions = {
  dryRun: isDev && !process.env.FORCE_REAL_EXECUTION
};
```

### For User Safety
```javascript
// Categorize commands by risk
const SAFE_COMMANDS = ['query', 'list', 'search', 'status'];
const RISKY_COMMANDS = ['install', 'remove', 'update'];
const DANGEROUS_COMMANDS = ['delete', 'format', 'rebuild'];

function getExecutionOptions(intent: Intent): ExecutionOptions {
  if (SAFE_COMMANDS.includes(intent.type)) {
    return {}; // Just run it
  }
  
  if (RISKY_COMMANDS.includes(intent.type)) {
    return { requireConfirmation: true };
  }
  
  if (DANGEROUS_COMMANDS.includes(intent.type)) {
    return { 
      requireConfirmation: true,
      requirePassword: true,
      showWarning: true
    };
  }
}
```

## The Complete Flow

```javascript
async function processNaturalLanguage(input: string) {
  // 1. Pure function - no execution needed
  const intent = recognizeIntent(input);
  
  // 2. Pure function - no execution needed
  const command = generateCommand(intent);
  
  // 3. Determine safety level
  const options = getExecutionOptions(intent);
  
  // 4. Execute with appropriate safety
  const result = await executeCommand(command, options);
  
  // 5. Return natural language response
  return formatResponse(result);
}
```

## Benefits of This Approach

1. **Unit tests are fast**: Test logic without execution
2. **Integration tests are real**: Use containers/VMs
3. **Development is safe**: --dry-run by default
4. **Production is real**: Actual commands execute
5. **Users have control**: Confirmation when needed

## What We DON'T Do

❌ Create fake outputs
```javascript
// BAD: Making up data
function simulateInstall() {
  return "Successfully installed firefox-1.2.3"; // Fake!
}
```

✅ Use real --dry-run
```javascript
// GOOD: Real NixOS feature
function previewInstall(package) {
  return exec(`nix-env -iA nixpkgs.${package} --dry-run`);
}
```

## Implementation Recommendations

### 1. Separate Concerns
```typescript
// intent-engine.ts - Pure functions, no I/O
export function recognizeIntent(input: string): Intent

// command-builder.ts - Pure functions, no I/O  
export function buildCommand(intent: Intent): NixCommand

// command-executor.ts - All I/O happens here
export function execute(cmd: NixCommand, opts?: ExecutionOptions): Promise<Result>
```

### 2. Test at the Right Level
```javascript
// Unit test - test logic only
describe('Intent Recognition', () => {
  test('recognizes patterns', () => {
    // No execution needed
  });
});

// Integration test - test with real NixOS
describe('Command Execution', () => {
  test('installs package', async () => {
    // Run in container with --dry-run
  });
});
```

### 3. Progressive Safety
```javascript
const safetyLevels = {
  preview: { dryRun: true, explain: true },
  cautious: { requireConfirmation: true, showChanges: true },
  normal: { requireConfirmation: false },
  force: { skipAllChecks: true } // Only for experts
};
```

## Conclusion

The best design is NOT simulation vs real. It's:

1. **Separate pure logic from execution**
2. **Test logic without execution**
3. **Use --dry-run for safe preview**
4. **Execute real commands with appropriate safety**
5. **Give users control over safety level**

This gives us all the benefits (fast tests, safety, real execution) without the confusion of "simulation mode".