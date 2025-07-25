/**
 * Secure Command Executor for Nix for Humanity
 * Executes Nix commands safely with sandboxing and validation
 */

const { spawn, exec } = require('child_process');
const { promisify } = require('util');
const path = require('path');
const fs = require('fs').promises;
const { v4: uuidv4 } = require('uuid');

const execAsync = promisify(exec);

class CommandExecutor {
  constructor(options = {}) {
    this.timeout = options.timeout || 60000; // 60 seconds default
    this.maxBuffer = options.maxBuffer || 10 * 1024 * 1024; // 10MB
    this.workDir = options.workDir || '/tmp/nix-for-humanity';
    this.enableFlakes = options.enableFlakes !== false;
    
    // Command whitelist
    this.allowedCommands = new Set([
      'nix', 'nix-env', 'nixos-rebuild', 'nix-channel',
      'systemctl', 'journalctl', 'df', 'free', 'ps'
    ]);
    
    // Operation limits
    this.operationLimits = {
      install: { concurrent: 1, perHour: 10 },
      remove: { concurrent: 1, perHour: 10 },
      update: { concurrent: 1, perHour: 2 },
      rebuild: { concurrent: 1, perHour: 2 }
    };
    
    // Track operations
    this.activeOperations = new Map();
    this.operationHistory = [];
    
    // Initialize
    this.initPromise = this.initialize();
  }

  async initialize() {
    // Create work directory
    await fs.mkdir(this.workDir, { recursive: true, mode: 0o700 });
  }

  async ensureInitialized() {
    await this.initPromise;
  }

  // Main execution method
  async execute(command, options = {}) {
    await this.ensureInitialized();
    
    const executionId = uuidv4();
    const startTime = Date.now();
    
    try {
      // Validate command
      this.validateCommand(command);
      
      // Check rate limits
      await this.checkRateLimits(command);
      
      // Build safe command
      const safeCommand = this.buildSafeCommand(command, options);
      
      // Track operation
      this.trackOperation(executionId, command);
      
      // Execute with monitoring
      const result = await this.executeWithMonitoring(safeCommand, {
        ...options,
        executionId
      });
      
      // Record success
      this.recordOperation(executionId, command, true, Date.now() - startTime);
      
      return {
        success: true,
        output: result.stdout,
        error: result.stderr,
        duration: Date.now() - startTime,
        executionId
      };
      
    } catch (error) {
      // Record failure
      this.recordOperation(executionId, command, false, Date.now() - startTime);
      
      return {
        success: false,
        error: error.message,
        details: error.stderr || error.stdout,
        duration: Date.now() - startTime,
        executionId
      };
    } finally {
      // Clean up tracking
      this.activeOperations.delete(executionId);
    }
  }

  // Validate command safety
  validateCommand(command) {
    if (!command || !command.command) {
      throw new Error('Invalid command structure');
    }
    
    // Check whitelist
    if (!this.allowedCommands.has(command.command)) {
      throw new Error(`Command '${command.command}' is not allowed`);
    }
    
    // Validate arguments
    if (!Array.isArray(command.args)) {
      throw new Error('Command arguments must be an array');
    }
    
    // Check for dangerous patterns
    const dangerousPatterns = [
      /rm\s+-rf/,
      />\s*\/dev\/null/,
      /2>&1/,
      /[;&|`$]/,
      /\.\.\//
    ];
    
    const fullCommand = `${command.command} ${command.args.join(' ')}`;
    for (const pattern of dangerousPatterns) {
      if (pattern.test(fullCommand)) {
        throw new Error('Command contains dangerous patterns');
      }
    }
  }

  // Check rate limits
  async checkRateLimits(command) {
    const operation = this.getOperationType(command);
    const limits = this.operationLimits[operation];
    
    if (!limits) return; // No limits for this operation
    
    // Check concurrent operations
    const activeCount = Array.from(this.activeOperations.values())
      .filter(op => op.operation === operation).length;
    
    if (activeCount >= limits.concurrent) {
      throw new Error(`Too many concurrent ${operation} operations`);
    }
    
    // Check hourly limits
    const hourAgo = Date.now() - 3600000;
    const recentCount = this.operationHistory
      .filter(op => 
        op.operation === operation && 
        op.timestamp > hourAgo &&
        op.success
      ).length;
    
    if (recentCount >= limits.perHour) {
      throw new Error(`Hourly limit reached for ${operation} operations`);
    }
  }

  // Get operation type from command
  getOperationType(command) {
    if (command.command === 'nix' || command.command === 'nix-env') {
      if (command.args.includes('install') || command.args.includes('-iA')) {
        return 'install';
      } else if (command.args.includes('remove') || command.args.includes('-e')) {
        return 'remove';
      }
    } else if (command.command === 'nixos-rebuild') {
      return 'rebuild';
    }
    
    return 'other';
  }

  // Build safe command with proper Nix configuration
  buildSafeCommand(command, options) {
    const safeCommand = {
      command: command.command,
      args: [...command.args],
      env: { ...process.env }
    };
    
    // Add Nix configuration
    if (this.enableFlakes) {
      safeCommand.env.NIX_CONFIG = 'experimental-features = nix-command flakes';
    }
    
    // Add safety flags
    if (options.dryRun) {
      if (command.command === 'nix') {
        safeCommand.args.push('--dry-run');
      } else if (command.command === 'nixos-rebuild') {
        safeCommand.args.push('--dry-run');
      }
    }
    
    // Use nixpkgs channel for consistency
    if (command.command === 'nix' && safeCommand.args[0] === 'search') {
      // Ensure we search nixpkgs
      if (!safeCommand.args.includes('nixpkgs')) {
        safeCommand.args.splice(1, 0, 'nixpkgs');
      }
    }
    
    return safeCommand;
  }

  // Execute with monitoring and timeout
  async executeWithMonitoring(command, options) {
    return new Promise((resolve, reject) => {
      const child = spawn(command.command, command.args, {
        env: command.env,
        cwd: this.workDir,
        timeout: options.timeout || this.timeout
      });
      
      let stdout = '';
      let stderr = '';
      let killed = false;
      
      // Capture output
      child.stdout.on('data', (data) => {
        stdout += data.toString();
        if (stdout.length > this.maxBuffer) {
          killed = true;
          child.kill('SIGTERM');
          reject(new Error('Output exceeded maximum buffer size'));
        }
      });
      
      child.stderr.on('data', (data) => {
        stderr += data.toString();
        if (stderr.length > this.maxBuffer) {
          killed = true;
          child.kill('SIGTERM');
          reject(new Error('Error output exceeded maximum buffer size'));
        }
      });
      
      // Handle completion
      child.on('exit', (code, signal) => {
        if (killed) return;
        
        if (code === 0) {
          resolve({ stdout, stderr });
        } else {
          const error = new Error(`Command failed with code ${code}`);
          error.code = code;
          error.signal = signal;
          error.stdout = stdout;
          error.stderr = stderr;
          reject(error);
        }
      });
      
      child.on('error', (error) => {
        if (killed) return;
        reject(error);
      });
      
      // Handle timeout
      if (options.timeout) {
        setTimeout(() => {
          if (!killed) {
            killed = true;
            child.kill('SIGTERM');
            reject(new Error('Command execution timeout'));
          }
        }, options.timeout);
      }
    });
  }

  // Track active operations
  trackOperation(id, command) {
    this.activeOperations.set(id, {
      id,
      command: command.command,
      args: command.args,
      operation: this.getOperationType(command),
      startTime: Date.now()
    });
  }

  // Record operation history
  recordOperation(id, command, success, duration) {
    this.operationHistory.push({
      id,
      command: command.command,
      operation: this.getOperationType(command),
      success,
      duration,
      timestamp: Date.now()
    });
    
    // Keep only recent history (last 24 hours)
    const dayAgo = Date.now() - 86400000;
    this.operationHistory = this.operationHistory
      .filter(op => op.timestamp > dayAgo);
  }

  // Package-specific operations
  async searchPackages(query) {
    const command = {
      command: 'nix',
      args: ['search', 'nixpkgs', query, '--json']
    };
    
    const result = await this.execute(command);
    
    if (result.success) {
      try {
        const packages = JSON.parse(result.output);
        return this.formatSearchResults(packages);
      } catch (error) {
        return [];
      }
    }
    
    return [];
  }

  formatSearchResults(packages) {
    const results = [];
    
    for (const [name, info] of Object.entries(packages)) {
      results.push({
        name: name.replace('legacyPackages.x86_64-linux.', ''),
        version: info.version || 'unknown',
        description: info.description || 'No description available'
      });
    }
    
    return results.slice(0, 10); // Limit results
  }

  async installPackage(packageName, options = {}) {
    const command = {
      command: 'nix',
      args: ['profile', 'install', `nixpkgs#${packageName}`]
    };
    
    // Fallback for systems without nix profile
    const fallbackCommand = {
      command: 'nix-env',
      args: ['-iA', `nixpkgs.${packageName}`]
    };
    
    let result = await this.execute(command, options);
    
    if (!result.success && result.error.includes('experimental')) {
      // Try fallback command
      result = await this.execute(fallbackCommand, options);
    }
    
    return result;
  }

  async removePackage(packageName, options = {}) {
    const command = {
      command: 'nix',
      args: ['profile', 'remove', packageName]
    };
    
    // Fallback for systems without nix profile
    const fallbackCommand = {
      command: 'nix-env',
      args: ['-e', packageName]
    };
    
    let result = await this.execute(command, options);
    
    if (!result.success && result.error.includes('experimental')) {
      // Try fallback command
      result = await this.execute(fallbackCommand, options);
    }
    
    return result;
  }

  async listPackages() {
    const command = {
      command: 'nix-env',
      args: ['-q']
    };
    
    const result = await this.execute(command);
    
    if (result.success) {
      return result.output
        .split('\n')
        .filter(line => line.trim())
        .map(line => {
          const match = line.match(/^([\w-]+)-([\d.]+.*?)$/);
          if (match) {
            return {
              name: match[1],
              version: match[2]
            };
          }
          return { name: line, version: 'unknown' };
        });
    }
    
    return [];
  }

  // Service operations
  async serviceOperation(serviceName, operation) {
    const validOperations = ['start', 'stop', 'restart', 'enable', 'disable', 'status'];
    
    if (!validOperations.includes(operation)) {
      throw new Error(`Invalid service operation: ${operation}`);
    }
    
    const command = {
      command: 'systemctl',
      args: [operation, serviceName]
    };
    
    // Status doesn't need sudo
    if (operation === 'status') {
      command.args.unshift('--user');
    }
    
    return this.execute(command);
  }

  // System information
  async getSystemInfo() {
    const info = {};
    
    // Get NixOS version
    try {
      const versionResult = await this.execute({
        command: 'nixos-version',
        args: []
      });
      
      if (versionResult.success) {
        info.nixosVersion = versionResult.output.trim();
      }
    } catch (e) {
      info.nixosVersion = 'Not available';
    }
    
    // Get disk usage
    try {
      const dfResult = await this.execute({
        command: 'df',
        args: ['-h', '/']
      });
      
      if (dfResult.success) {
        const lines = dfResult.output.trim().split('\n');
        if (lines[1]) {
          const parts = lines[1].split(/\s+/);
          info.disk = {
            total: parts[1],
            used: parts[2],
            available: parts[3],
            percentage: parts[4]
          };
        }
      }
    } catch (e) {
      // Ignore
    }
    
    // Get memory usage
    try {
      const freeResult = await this.execute({
        command: 'free',
        args: ['-h']
      });
      
      if (freeResult.success) {
        const lines = freeResult.output.trim().split('\n');
        const memLine = lines[1].split(/\s+/);
        info.memory = {
          total: memLine[1],
          used: memLine[2],
          free: memLine[3]
        };
      }
    } catch (e) {
      // Ignore
    }
    
    return info;
  }

  // System logs
  async getSystemLogs(options = {}) {
    const command = {
      command: 'journalctl',
      args: ['-n', String(options.lines || 100)]
    };
    
    if (options.service) {
      command.args.push('-u', options.service);
    }
    
    if (options.since) {
      command.args.push('--since', options.since);
    }
    
    // Add user flag for non-root access
    command.args.push('--user');
    
    const result = await this.execute(command);
    return result.success ? result.output : 'Could not retrieve logs';
  }

  // Get operation status
  getStatus(executionId) {
    const active = this.activeOperations.get(executionId);
    if (active) {
      return {
        status: 'running',
        operation: active.operation,
        duration: Date.now() - active.startTime
      };
    }
    
    const completed = this.operationHistory.find(op => op.id === executionId);
    if (completed) {
      return {
        status: completed.success ? 'completed' : 'failed',
        operation: completed.operation,
        duration: completed.duration
      };
    }
    
    return {
      status: 'unknown',
      operation: null,
      duration: 0
    };
  }
}

module.exports = CommandExecutor;