# 🚀 Real NixOS Command Execution

## Overview

Nix for Humanity **executes real NixOS commands by default**. When you say "install firefox", it actually installs Firefox. This is not a simulation - it's real system management through natural language.

## The Layered Reality Approach

Nix for Humanity uses a layered architecture:
1. **Pure Logic Layers** - Intent recognition and command building (no execution)
2. **Execution Layer** - Real NixOS commands with safety options

This document explains how we achieve fast testing AND real execution.

## Architecture

```
Natural Language → Intent Recognition → Command Building → Safety Validation → Sandbox Execution → Natural Response
```

## The Architecture

### Layer 1: Pure Functions (No Execution Needed)
```javascript
// These can be tested without any execution
function recognizeIntent(input: string): Intent
function buildCommand(intent: Intent): NixCommand
function validateSafety(command: NixCommand): SafetyCheck
```

### Layer 2: Execution with Options
```javascript
interface ExecutionOptions {
  dryRun?: boolean;      // Use --dry-run flag
  confirm?: boolean;     // Ask user first
  sandbox?: boolean;     // Extra isolation
  timeout?: number;      // Max execution time
}

// One execution function, multiple safety levels
async function execute(cmd: NixCommand, opts?: ExecutionOptions): Result
```

### Safety Levels (Not "Modes")
- **Preview**: Always uses --dry-run
- **Cautious**: Requires confirmation
- **Normal**: Direct execution for safe commands
- **Force**: Skip safety checks (admin only)

## Safety Features

### Command Sandbox
All commands execute in a secure sandbox with:
- **Timeout Protection**: 30-second maximum execution time
- **Memory Limits**: 512MB maximum memory usage
- **Output Limits**: 10MB maximum output size
- **Network Control**: Only enabled for package downloads
- **File System Protection**: Restricted write access

### Safety Validator
Before execution, all commands are validated for:
- Dangerous command patterns (rm -rf, dd, etc.)
- Suspicious arguments
- Path traversal attempts
- Privilege escalation

### Example Safety Blocks
```javascript
// These commands will be rejected:
"rm -rf /"              // Dangerous
"dd if=/dev/zero"       // Destructive
"chmod 777 /etc"        // Security risk
```

## Usage

### Configuration
Set execution mode via environment variables:
```bash
# Use real execution
export NIX_EXECUTION_MODE=real

# Force simulation even in production
export SIMULATE_COMMANDS=true

# Enable command logging
export NIX_LOG_COMMANDS=true
```

### Programmatic Usage
```javascript
import { nixWrapper } from './nlp/nix-wrapper';
import { intentEngine } from './nlp/intent-engine';

// Process natural language
const intent = intentEngine.recognize("show me what's installed");
const command = nixWrapper.intentToCommand(intent);

// Execute with safety
const result = await nixWrapper.execute(command);
console.log(result.naturalLanguageResponse);
```

### Testing Real Execution
```bash
# Run integration tests with real commands
RUN_REAL_EXECUTION_TESTS=true npm test tests/integration/real-execution.test.js

# Manual testing
node tests/integration/real-execution.test.js
```

## Supported Commands

### Safe Query Commands (Always Allowed)
- `nix-env -q` - List installed packages
- `systemctl status [service]` - Check service status
- `journalctl` - View system logs
- `nix-channel --list` - List channels

### System Modification Commands (Sandboxed)
- `nix-env -iA nixpkgs.[package]` - Install packages
- `nix-collect-garbage -d` - Clean up old packages
- `systemctl start/stop [service]` - Manage services (with sudo)
- `nixos-rebuild switch` - Update system (with sudo)

### Blocked Commands
- File deletion commands (`rm`, `shred`)
- Disk formatting (`mkfs`, `fdisk`)
- Permission changes on system files
- Direct device manipulation

## Natural Language Examples

All of these work with real execution:

```
"install firefox"
→ nix-env -iA nixpkgs.firefox

"show me what's installed"
→ nix-env -q

"check if nginx is running"
→ systemctl status nginx

"free up disk space"
→ nix-collect-garbage -d

"show recent errors in logs"
→ journalctl -xe -p err -n 100
```

## Error Handling

### Permission Errors
```javascript
{
  success: false,
  error: "Permission denied",
  naturalLanguageResponse: "I need administrator privileges for that. Try running with sudo."
}
```

### Command Not Found
```javascript
{
  success: false,
  error: "Command not found",
  naturalLanguageResponse: "That command isn't available. Would you like me to help install it?"
}
```

### Timeout
```javascript
{
  success: false,
  error: "Command timed out after 30000ms",
  naturalLanguageResponse: "That command is taking too long. It might be stuck or downloading large files."
}
```

## Demo

Try the real execution demo:
```bash
# Start the development server
npm run dev

# Open the demo
open http://localhost:8080/demo-real-execution.html
```

The demo provides:
- Mode switching (simulation/real/hybrid)
- Example commands
- Live execution with progress
- Safety validation feedback
- Natural language responses

## Best Practices

1. **Always Test in Simulation First**
   - Verify intent recognition
   - Check command generation
   - Review safety validation

2. **Use Hybrid Mode for Production**
   - Safe commands execute
   - Dangerous commands simulate
   - Best user experience

3. **Monitor Command Logs**
   - Track what users request
   - Identify new patterns
   - Improve intent recognition

4. **Handle Errors Gracefully**
   - Provide helpful suggestions
   - Explain what went wrong
   - Offer alternatives

## Security Considerations

### Sudo Commands
Commands requiring sudo will prompt for authentication:
- User must be in sudoers/wheel group
- Standard system authentication applies
- No passwords stored or logged

### Audit Trail
All executed commands are logged with:
- Timestamp
- Original natural language input
- Generated command
- Execution result
- User context (if available)

### Rollback Support
System modifications track rollback commands:
```javascript
// After installing a package
rollbackCommand: "nix-env --rollback"

// After system rebuild
rollbackCommand: "nixos-rebuild switch --rollback"
```

## Troubleshooting

### Commands Not Executing
1. Check execution mode: `echo $NIX_EXECUTION_MODE`
2. Verify sandbox permissions
3. Check command is in allowed list
4. Review safety validator output

### Slow Execution
1. Network operations take time
2. Large package installations
3. System rebuilds are intensive
4. Check system resources

### Unexpected Results
1. Enable command logging
2. Check exact command generated
3. Verify intent recognition
4. Test command manually

## Future Enhancements

### Planned
- [ ] Async execution with progress updates
- [ ] Batch command support
- [ ] Confirmation dialogs for destructive ops
- [ ] Command history and undo

### Under Consideration
- [ ] Custom safety rules
- [ ] Plugin system for new commands
- [ ] Remote execution support
- [ ] Command queuing

---

*Remember: With great power comes great responsibility. Real command execution is powerful but must be used carefully. The safety measures are there to protect users, not restrict them.*