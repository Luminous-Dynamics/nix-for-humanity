# 🎯 Layered Reality Policy

## Core Development Principle

**Nix for Humanity uses a layered approach:** Pure functions for logic, real execution for actions.

## The Philosophy

We separate what can be tested without side effects (intent recognition, command generation) from what requires real execution. This gives us fast tests AND honest functionality.

## Implementation Guidelines

### ✅ DO
- Execute real NixOS commands
- Use `--dry-run` for previews
- Test in VMs/containers
- Mock only at test boundaries
- Be honest about what will happen

### ❌ DON'T
- Create fake command outputs
- Pretend commands succeeded
- Build simulation modes
- Generate artificial responses
- Add "demo" modes with fake data

## The Layered Approach

### Layer 1: Pure Functions (No Execution)
```javascript
// Intent recognition - pure function
function recognizeIntent(input: string): Intent {
  return { type: 'install', package: 'firefox' };
}

// Command building - pure function
function buildCommand(intent: Intent): NixCommand {
  return { command: 'nix-env', args: ['-iA', `nixpkgs.${intent.package}`] };
}
```

### Layer 2: Execution with Options
```javascript
// Real execution with safety controls
async function execute(cmd: NixCommand, opts: ExecutionOptions) {
  if (opts.dryRun) cmd.args.push('--dry-run');
  if (opts.confirm) await confirmWithUser();
  return realExecution(cmd);
}
```

### Testing Strategy
- **Unit Tests**: Test pure functions only (fast, no side effects)
- **Integration Tests**: Use containers with --dry-run
- **E2E Tests**: Real NixOS with safety flags

## Exceptions

The ONLY acceptable "simulation" is:
1. Mocking system calls in unit tests
2. Using --dry-run flags (which is real NixOS functionality)

## Remember

Users trust us to manage their system. That trust requires honesty. Real commands only.