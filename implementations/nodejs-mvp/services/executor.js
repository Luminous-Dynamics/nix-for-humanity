// 🚀 Command Executor - Safely executes NixOS commands
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

class Executor {
  constructor() {
    // Timeout for commands (in milliseconds)
    this.timeout = 30000; // 30 seconds
    
    // Environment variables for safer execution
    this.env = {
      ...process.env,
      NIX_REMOTE: '', // Ensure local evaluation
      NO_COLOR: '1',  // Disable color output for parsing
    };
  }

  async execute(command) {
    try {
      console.log(`Executing: ${command.raw}`);

      // For MVP, check if we're in development mode
      if (process.env.NODE_ENV === 'development' && process.env.MOCK_COMMANDS === 'true') {
        return this.mockExecute(command);
      }

      // Execute the command with timeout
      const { stdout, stderr } = await execAsync(command.raw, {
        timeout: this.timeout,
        env: this.env,
        maxBuffer: 1024 * 1024 * 10 // 10MB buffer
      });

      // Parse the output based on command type
      const result = this.parseOutput(command, stdout, stderr);
      
      return {
        success: true,
        data: result,
        raw: stdout,
        command: command.raw
      };

    } catch (error) {
      console.error('Execution error:', error);
      
      // Handle specific error types
      if (error.code === 'ETIMEDOUT') {
        return {
          success: false,
          error: 'Command timed out. This might happen with large searches.',
          command: command.raw
        };
      }

      if (error.code === 127) {
        return {
          success: false,
          error: 'Nix command not found. Make sure Nix is installed.',
          command: command.raw
        };
      }

      // Parse error output for user-friendly messages
      const userError = this.parseError(error.stderr || error.message);
      
      return {
        success: false,
        error: userError,
        raw: error.stderr || error.message,
        command: command.raw
      };
    }
  }

  parseOutput(command, stdout, stderr) {
    // Parse based on intent
    switch (command.intent) {
      case 'search':
        return this.parseSearchOutput(stdout);
      
      case 'list':
        return this.parseListOutput(stdout);
      
      case 'info':
        return this.parseInfoOutput(stdout);
      
      case 'check':
        return this.parseCheckOutput(stdout);
      
      case 'install':
        return this.parseInstallOutput(stdout);
      
      case 'remove':
        return this.parseRemoveOutput(stdout);
      
      case 'update':
        return this.parseUpdateOutput(stdout);
      
      case 'list-updates':
        return this.parseListUpdatesOutput(stdout);
      
      case 'garbage-collect':
        return this.parseGarbageCollectOutput(stdout);
      
      default:
        return { raw: stdout };
    }
  }

  parseSearchOutput(output) {
    try {
      // If JSON output is available
      if (output.startsWith('{') || output.startsWith('[')) {
        const data = JSON.parse(output);
        return {
          count: Object.keys(data).length,
          packages: Object.keys(data).slice(0, 10) // First 10 results
        };
      }

      // Parse text output
      const lines = output.split('\n').filter(line => line.trim());
      const packages = lines
        .filter(line => line.includes('nixpkgs.'))
        .map(line => {
          const match = line.match(/nixpkgs\.(\S+)/);
          return match ? match[1] : null;
        })
        .filter(Boolean)
        .slice(0, 10);

      return {
        count: packages.length,
        packages
      };
    } catch (e) {
      return { raw: output };
    }
  }

  parseListOutput(output) {
    const lines = output.split('\n').filter(line => line.trim());
    return {
      count: lines.length,
      packages: lines.slice(0, 20) // First 20 installed packages
    };
  }

  parseInfoOutput(output) {
    // Keep it simple for MVP
    return {
      info: output.substring(0, 500) // First 500 chars
    };
  }

  parseCheckOutput(output) {
    const issues = output.match(/\[FAIL\]/g);
    const warnings = output.match(/\[WARN\]/g);
    
    return {
      healthy: !issues,
      issues: issues ? issues.length : 0,
      warnings: warnings ? warnings.length : 0,
      summary: output.substring(0, 300)
    };
  }

  parseInstallOutput(output) {
    if (output.includes('--dry-run')) {
      const packages = output.match(/would be installed:(.+)/);
      return {
        dryRun: true,
        message: 'This would install the package (dry-run mode)',
        packages: packages ? packages[1].trim() : 'Package installation simulated'
      };
    }
    return { raw: output };
  }

  parseRemoveOutput(output) {
    if (output.includes('--dry-run')) {
      return {
        dryRun: true,
        message: 'This would remove the package (dry-run mode)',
        details: output.substring(0, 200)
      };
    }
    return { raw: output };
  }

  parseUpdateOutput(output) {
    return {
      message: 'Channel update completed',
      details: output.substring(0, 200)
    };
  }

  parseListUpdatesOutput(output) {
    const updates = output.split('\n').filter(line => line.includes('->'));
    return {
      count: updates.length,
      updates: updates.slice(0, 10),
      message: `${updates.length} updates available`
    };
  }

  parseGarbageCollectOutput(output) {
    const freed = output.match(/(\d+(?:\.\d+)?)\s*(MiB|GiB|KiB)/);
    return {
      dryRun: true,
      message: 'Garbage collection would free space (dry-run mode)',
      spaceFreed: freed ? `${freed[1]} ${freed[2]}` : 'Unknown amount'
    };
  }

  parseError(errorText) {
    // Common error patterns and user-friendly messages
    if (errorText.includes('not found')) {
      return 'Package not found. Try searching with a different name.';
    }
    
    if (errorText.includes('permission denied')) {
      return 'Permission denied. This command requires different privileges.';
    }
    
    if (errorText.includes('network')) {
      return 'Network error. Check your internet connection.';
    }
    
    // Generic error
    return 'Command failed. Try rephrasing your request.';
  }

  // Mock execution for development
  mockExecute(command) {
    console.log(`MOCK: Would execute: ${command.raw}`);
    
    switch (command.intent) {
      case 'search':
        return {
          success: true,
          data: {
            count: 5,
            packages: ['firefox', 'firefox-esr', 'firefox-beta', 'firefox-devedition', 'firefox-wayland']
          }
        };
      
      case 'list':
        return {
          success: true,
          data: {
            count: 3,
            packages: ['nodejs-18.17.0', 'git-2.42.0', 'vim-9.0.1897']
          }
        };
      
      case 'install':
        return {
          success: true,
          data: {
            dryRun: true,
            message: 'This would install the package (dry-run mode)',
            packages: `${command.package}-2.0.0`
          }
        };
      
      case 'remove':
        return {
          success: true,
          data: {
            dryRun: true,
            message: 'This would remove the package (dry-run mode)',
            details: `Removing ${command.package}...`
          }
        };
      
      case 'update':
        return {
          success: true,
          data: {
            message: 'Channel update completed',
            details: 'nixos-24.05 channel updated'
          }
        };
      
      case 'list-updates':
        return {
          success: true,
          data: {
            count: 3,
            updates: ['firefox: 119.0 -> 120.0', 'nodejs: 18.17.0 -> 18.18.0', 'git: 2.42.0 -> 2.43.0'],
            message: '3 updates available'
          }
        };
      
      case 'garbage-collect':
        return {
          success: true,
          data: {
            dryRun: true,
            message: 'Garbage collection would free space (dry-run mode)',
            spaceFreed: '2.3 GiB'
          }
        };
      
      default:
        return {
          success: true,
          data: { message: 'Mock execution successful' }
        };
    }
  }
}

module.exports = Executor;