# ⏱️ Timeout Strategy for Nix Operations

## Critical Issue Identified

**Problem**: Using a fixed 60-second timeout for all Nix operations would cause frequent failures for legitimate long-running operations like:
- Installing large packages (LibreOffice, CUDA, etc.)
- System rebuilds
- Channel updates on slow connections
- First-time package installations

**Impact**: Users would experience frustrating timeouts on normal operations, making the system unusable for real work.

## Solution: Dynamic Timeout Strategy

### Core Principles

1. **Operation-Aware**: Different operations have vastly different expected durations
2. **Package-Size-Aware**: Installing `hello` vs `tensorflow` requires different timeouts
3. **Network-Aware**: Adapt to user's connection speed
4. **Progress-Aware**: Extend timeout if operation is making progress
5. **User-Informed**: Tell users what to expect

### Timeout Categories

#### 🚀 Fast Operations (5-30 seconds)
- Package search
- List installed packages
- Check service status
- Query operations
- Dry-run operations

#### ⚡ Medium Operations (1-5 minutes)
- Install small packages (< 50MB)
- Remove packages
- Service start/stop/restart
- Configuration checks

#### 🐌 Long Operations (5-30 minutes)
- Install medium packages (50MB-500MB)
- Channel updates
- Garbage collection
- Install development tools

#### 🐢 Very Long Operations (30-120 minutes)
- Install large packages (> 500MB)
- System rebuild
- Major system upgrade
- First-time installations with database download

### Implementation Strategy

```javascript
// Timeout calculation based on operation analysis
calculateTimeout(command, context) {
  // 1. Check operation type
  const baseTimeout = this.getBaseTimeout(command);
  
  // 2. Apply multipliers
  let timeout = baseTimeout;
  
  // Network speed multiplier
  if (context.networkSpeed === 'slow') {
    timeout *= 2;
  }
  
  // First-time installation multiplier
  if (context.isFirstInstall) {
    timeout *= 1.5;
  }
  
  // System load multiplier
  if (context.systemLoad > 0.8) {
    timeout *= 1.5;
  }
  
  // 3. Set reasonable bounds
  const MIN_TIMEOUT = 10000;  // 10 seconds
  const MAX_TIMEOUT = 7200000; // 2 hours
  
  return Math.min(Math.max(timeout, MIN_TIMEOUT), MAX_TIMEOUT);
}
```

### Package Classification

We need to maintain a database of package sizes/complexity:

```javascript
const packageClassification = {
  instant: [
    'hello', 'tree', 'htop', 'ncdu', 'jq', 'ripgrep', 'fd'
  ],
  
  small: [
    'git', 'vim', 'neovim', 'tmux', 'zsh', 'fish', 'curl', 'wget'
  ],
  
  medium: [
    'nodejs', 'python3', 'ruby', 'go', 'rust', 'firefox', 'thunderbird'
  ],
  
  large: [
    'chromium', 'vscode', 'emacs', 'libreoffice', 'gimp', 'inkscape',
    'docker', 'virtualbox', 'steam'
  ],
  
  huge: [
    'cuda', 'cudnn', 'tensorflow', 'pytorch', 'android-studio',
    'unity3d', 'unreal-engine', 'matlab'
  ]
};
```

### Progress Detection

Instead of fixed timeouts, monitor progress:

```javascript
class ProgressMonitor {
  constructor() {
    this.lastActivity = Date.now();
    this.progressPattern = [
      /downloading.*?(\d+)%/i,
      /unpacking/i,
      /building/i,
      /installing/i,
      /copied (\d+) files/i
    ];
  }
  
  checkProgress(output) {
    for (const pattern of this.progressPattern) {
      if (pattern.test(output)) {
        this.lastActivity = Date.now();
        return true;
      }
    }
    return false;
  }
  
  shouldTimeout() {
    // Only timeout if no progress for 5 minutes
    return Date.now() - this.lastActivity > 300000;
  }
}
```

### User Communication

```javascript
// Inform users about expected duration
function getUserMessage(estimatedMinutes) {
  if (estimatedMinutes < 1) {
    return "This should be quick! ⚡";
  } else if (estimatedMinutes < 5) {
    return `This will take about ${estimatedMinutes} minutes. ☕`;
  } else if (estimatedMinutes < 15) {
    return `This might take ${estimatedMinutes} minutes. Good time for a coffee break! ☕`;
  } else if (estimatedMinutes < 30) {
    return `This is a bigger operation (up to ${estimatedMinutes} minutes). Feel free to do other things! 🎵`;
  } else {
    return `This is a major operation that could take ${estimatedMinutes}+ minutes. I'll run it in the background. 🚀`;
  }
}
```

### Network Speed Detection

```javascript
async function detectNetworkSpeed() {
  try {
    // Test download speed with small file
    const start = Date.now();
    await downloadTestFile('https://cache.nixos.org/test'); // 1MB file
    const duration = Date.now() - start;
    
    if (duration > 10000) return 'slow';
    if (duration > 3000) return 'medium';
    return 'fast';
  } catch {
    return 'unknown';
  }
}
```

### Special Cases

1. **Nixpkgs Database Updates**
   - First run can take 30+ minutes
   - Subsequent updates are faster
   - Detect with: `~/.cache/nix/` existence

2. **Build-from-source Packages**
   - Can take hours for complex packages
   - Detect with: presence of `.drv` in output
   - Warn user and suggest binary cache

3. **System Rebuilds**
   - Highly variable (5 minutes to 2 hours)
   - Depends on configuration changes
   - Always warn user

4. **Offline Operations**
   - Some operations work offline
   - Detect network availability
   - Adjust timeouts accordingly

### Configuration

Allow users to configure timeout preferences:

```json
{
  "timeouts": {
    "networkSpeed": "auto|fast|medium|slow",
    "patientMode": true,
    "maxTimeout": 7200000,
    "progressTimeout": 300000,
    "customTimeouts": {
      "libreoffice": 1800000,
      "tensorflow": 3600000
    }
  }
}
```

### Error Messages

Make timeout errors helpful:

```javascript
function formatTimeoutError(operation, duration, progress) {
  if (progress.hadActivity) {
    return `The operation was making progress but took longer than expected (${duration}ms). ` +
           `This might be due to slow network or system load. ` +
           `Try again with patience mode: 'set patient mode on'`;
  } else {
    return `The operation appears to be stuck (no progress for 5 minutes). ` +
           `This could be a network issue or the package server might be down. ` +
           `Try: 1) Check your internet, 2) Try again later, 3) Use --dry-run to test`;
  }
}
```

## Summary

The timeout strategy must be:
1. **Dynamic** - Adapt to operation type and context
2. **Intelligent** - Monitor actual progress
3. **Configurable** - Respect user preferences
4. **Informative** - Keep users informed
5. **Forgiving** - Err on the side of patience

This prevents the frustration of legitimate operations timing out while still protecting against truly stuck processes.