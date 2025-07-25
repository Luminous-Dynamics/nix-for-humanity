/**
 * Safe Nix Command Executor
 * Executes Nix commands with safety checks and rollback capability
 */

const { spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');
const EventEmitter = require('events');

class NixExecutor extends EventEmitter {
  constructor() {
    super();
    this.executionLog = [];
    this.currentGeneration = null;
    this.isDryRun = process.env.NIX_DRY_RUN === 'true';
  }

  /**
   * Execute a Nix command safely
   */
  async execute(command) {
    // Validate command safety
    if (!this.isCommandSafe(command)) {
      throw new Error('Command failed safety validation');
    }

    // Get current generation for rollback
    this.currentGeneration = await this.getCurrentGeneration();
    
    // Log execution attempt
    const execution = {
      id: Date.now().toString(),
      command: command.command,
      args: command.args,
      timestamp: new Date().toISOString(),
      status: 'running'
    };
    
    this.executionLog.push(execution);
    this.emit('execution:start', execution);

    try {
      // Execute command
      const result = await this.runCommand(command);
      
      execution.status = 'success';
      execution.result = result;
      this.emit('execution:success', execution);
      
      return {
        success: true,
        output: result.stdout,
        generation: this.currentGeneration,
        executionId: execution.id
      };
      
    } catch (error) {
      execution.status = 'failed';
      execution.error = error.message;
      this.emit('execution:error', execution);
      
      // Auto-rollback on critical errors
      if (this.shouldAutoRollback(error)) {
        await this.rollback(this.currentGeneration);
      }
      
      throw error;
    }
  }

  /**
   * Run command with progress tracking
   */
  runCommand(command) {
    return new Promise((resolve, reject) => {
      const args = this.isDryRun ? ['--dry-run', ...command.args] : command.args;
      const proc = spawn(command.command, args, {
        env: { ...process.env, NIX_PAGER: 'cat' }
      });

      let stdout = '';
      let stderr = '';
      let lastProgress = 0;

      proc.stdout.on('data', (data) => {
        stdout += data.toString();
        
        // Parse progress from Nix output
        const progress = this.parseProgress(data.toString());
        if (progress > lastProgress) {
          lastProgress = progress;
          this.emit('execution:progress', {
            command: command.command,
            progress,
            message: this.parseProgressMessage(data.toString())
          });
        }
      });

      proc.stderr.on('data', (data) => {
        stderr += data.toString();
        
        // Check for warnings
        if (data.toString().includes('warning:')) {
          this.emit('execution:warning', {
            command: command.command,
            warning: data.toString()
          });
        }
      });

      proc.on('close', (code) => {
        if (code === 0) {
          resolve({ stdout, stderr, code });
        } else {
          reject(new Error(`Command failed with code ${code}: ${stderr}`));
        }
      });

      proc.on('error', (error) => {
        reject(error);
      });
    });
  }

  /**
   * Validate command safety
   */
  isCommandSafe(command) {
    // Whitelist of allowed commands
    const allowedCommands = [
      'nix-env', 'nix-store', 'nix-channel', 
      'nixos-rebuild', 'nix', 'nix-shell',
      'systemctl', 'journalctl'
    ];

    // Extract base command
    const baseCommand = command.command === 'sudo' 
      ? command.args[0] 
      : command.command;

    if (!allowedCommands.includes(baseCommand)) {
      return false;
    }

    // Check for dangerous flags
    const dangerousFlags = ['--force', '--no-backup', 'rm', 'delete'];
    const allArgs = command.args.join(' ');
    
    for (const flag of dangerousFlags) {
      if (allArgs.includes(flag)) {
        return false;
      }
    }

    return true;
  }

  /**
   * Get current system generation
   */
  async getCurrentGeneration() {
    try {
      const result = await this.runCommand({
        command: 'nix-env',
        args: ['--list-generations']
      });

      const lines = result.stdout.split('\n');
      const current = lines.find(line => line.includes('(current)'));
      
      if (current) {
        const match = current.match(/^\s*(\d+)/);
        return match ? parseInt(match[1]) : null;
      }
    } catch (error) {
      console.error('Failed to get current generation:', error);
    }
    
    return null;
  }

  /**
   * Rollback to specific generation
   */
  async rollback(generation) {
    if (!generation) return;

    this.emit('rollback:start', { generation });

    try {
      await this.runCommand({
        command: 'nix-env',
        args: ['--rollback']
      });
      
      this.emit('rollback:success', { generation });
      return true;
    } catch (error) {
      this.emit('rollback:error', { generation, error: error.message });
      return false;
    }
  }

  /**
   * Check if error should trigger auto-rollback
   */
  shouldAutoRollback(error) {
    const criticalErrors = [
      'collision between',
      'infinite recursion',
      'assertion failed',
      'out of memory'
    ];

    const errorMessage = error.message.toLowerCase();
    return criticalErrors.some(critical => errorMessage.includes(critical));
  }

  /**
   * Parse progress from Nix output
   */
  parseProgress(output) {
    // Parse download progress
    const downloadMatch = output.match(/(\d+)%/);
    if (downloadMatch) {
      return parseInt(downloadMatch[1]);
    }

    // Parse build progress
    const buildMatch = output.match(/\[(\d+)\/(\d+)\]/);
    if (buildMatch) {
      const current = parseInt(buildMatch[1]);
      const total = parseInt(buildMatch[2]);
      return Math.round((current / total) * 100);
    }

    // Parse copying progress
    if (output.includes('copying path')) {
      return 50; // Rough estimate
    }

    return 0;
  }

  /**
   * Parse human-readable progress message
   */
  parseProgressMessage(output) {
    if (output.includes('downloading')) {
      return 'Downloading packages...';
    }
    if (output.includes('building')) {
      return 'Building from source...';
    }
    if (output.includes('copying')) {
      return 'Installing files...';
    }
    if (output.includes('querying')) {
      return 'Checking availability...';
    }
    return 'Processing...';
  }

  /**
   * Search for packages
   */
  async searchPackages(query) {
    try {
      const result = await this.runCommand({
        command: 'nix',
        args: ['search', 'nixpkgs', query, '--json']
      });

      const packages = JSON.parse(result.stdout);
      
      // Format results
      return Object.entries(packages).map(([name, info]) => ({
        name: name.replace('legacyPackages.x86_64-linux.', ''),
        version: info.version,
        description: info.description,
        pname: info.pname
      })).slice(0, 10); // Limit to 10 results
      
    } catch (error) {
      console.error('Package search failed:', error);
      return [];
    }
  }

  /**
   * Get system information
   */
  async getSystemInfo() {
    const info = {};

    try {
      // NixOS version
      const versionResult = await this.runCommand({
        command: 'nixos-version',
        args: []
      });
      info.nixosVersion = versionResult.stdout.trim();

      // Channel info
      const channelResult = await this.runCommand({
        command: 'nix-channel',
        args: ['--list']
      });
      info.channels = channelResult.stdout.trim().split('\n');

      // Disk usage
      const diskResult = await this.runCommand({
        command: 'df',
        args: ['-h', '/nix/store']
      });
      const diskLines = diskResult.stdout.split('\n');
      if (diskLines[1]) {
        const parts = diskLines[1].split(/\s+/);
        info.diskUsage = {
          used: parts[2],
          available: parts[3],
          percentage: parts[4]
        };
      }

      // Generation count
      const genResult = await this.runCommand({
        command: 'nix-env',
        args: ['--list-generations']
      });
      info.generations = genResult.stdout.split('\n').length - 1;

    } catch (error) {
      console.error('Failed to get system info:', error);
    }

    return info;
  }

  /**
   * Get execution history
   */
  getHistory(limit = 10) {
    return this.executionLog.slice(-limit);
  }
}

// Export singleton
module.exports = new NixExecutor();