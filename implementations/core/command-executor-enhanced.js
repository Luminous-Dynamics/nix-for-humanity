/**
 * Enhanced Command Executor with Dynamic Timeouts and Progress Monitoring
 * Prevents frustrating timeouts while tracking operation progress
 */

const { spawn } = require('child_process');
const { v4: uuidv4 } = require('uuid');
const TimeoutManager = require('./timeout-manager');
const ProgressMonitor = require('./progress-monitor');
const EventEmitter = require('events');

class EnhancedCommandExecutor extends EventEmitter {
  constructor(options = {}) {
    super();
    
    this.workDir = options.workDir || '/tmp/nix-for-humanity';
    this.maxBuffer = options.maxBuffer || 10 * 1024 * 1024; // 10MB
    
    // Initialize managers
    this.timeoutManager = new TimeoutManager(options.timeoutConfig);
    
    // Command whitelist
    this.allowedCommands = new Set([
      'nix', 'nix-env', 'nixos-rebuild', 'nix-channel',
      'nix-collect-garbage', 'systemctl', 'journalctl'
    ]);
    
    // Active operations tracking
    this.activeOperations = new Map();
  }

  /**
   * Execute command with intelligent timeout and progress monitoring
   */
  async execute(command, options = {}) {
    const executionId = uuidv4();
    const startTime = Date.now();
    
    // Validate command
    this.validateCommand(command);
    
    // Calculate appropriate timeout
    const timeout = await this.timeoutManager.calculateTimeout(command, options);
    const timeoutInfo = this.timeoutManager.getTimeoutDescription(timeout);
    
    // Notify about expected duration
    if (options.onProgress) {
      options.onProgress({
        type: 'start',
        message: timeoutInfo.message,
        estimatedDuration: timeout,
        executionId
      });
    }
    
    // Create progress monitor
    const progressMonitor = new ProgressMonitor({
      inactivityTimeout: Math.min(300000, timeout / 4) // 5 min or 1/4 of total timeout
    });
    
    // Set up progress forwarding
    progressMonitor.on('progress', (progress) => {
      if (options.onProgress) {
        options.onProgress({
          ...progress,
          executionId,
          elapsed: Date.now() - startTime
        });
      }
    });
    
    progressMonitor.on('timeout', (info) => {
      this.emit('warning', {
        executionId,
        type: 'inactivity',
        message: 'Operation appears stuck - no progress detected',
        ...info
      });
    });
    
    // Track operation
    const operation = {
      id: executionId,
      command,
      startTime,
      timeout,
      progressMonitor,
      status: 'running'
    };
    
    this.activeOperations.set(executionId, operation);
    
    try {
      // Execute with monitoring
      const result = await this.executeWithMonitoring(command, {
        ...options,
        executionId,
        timeout,
        progressMonitor
      });
      
      // Mark as completed
      operation.status = 'completed';
      operation.endTime = Date.now();
      operation.result = result;
      
      return {
        success: true,
        output: result.stdout,
        error: result.stderr,
        duration: Date.now() - startTime,
        executionId
      };
      
    } catch (error) {
      // Mark as failed
      operation.status = 'failed';
      operation.endTime = Date.now();
      operation.error = error;
      
      // Check if it was a timeout
      if (error.message.includes('timeout')) {
        const suggestion = this.getTimeoutSuggestion(command, timeout, progressMonitor.getState());
        error.suggestion = suggestion;
      }
      
      return {
        success: false,
        error: error.message,
        suggestion: error.suggestion,
        details: error.stderr || error.stdout,
        duration: Date.now() - startTime,
        executionId
      };
      
    } finally {
      // Clean up
      progressMonitor.stop();
      
      // Keep operation info for a while for status queries
      setTimeout(() => {
        this.activeOperations.delete(executionId);
      }, 300000); // 5 minutes
    }
  }

  /**
   * Execute with progress monitoring
   */
  async executeWithMonitoring(command, options) {
    return new Promise((resolve, reject) => {
      const { timeout, progressMonitor } = options;
      
      // Build safe command with environment
      const env = {
        ...process.env,
        NIX_CONFIG: 'experimental-features = nix-command flakes'
      };
      
      // Add dry-run flag if requested
      const args = [...command.args];
      if (options.dryRun) {
        if (command.command === 'nix' || command.command === 'nixos-rebuild') {
          args.push('--dry-run');
        }
      }
      
      // Spawn process
      const child = spawn(command.command, args, {
        env,
        cwd: this.workDir
      });
      
      let stdout = '';
      let stderr = '';
      let killed = false;
      
      // Start progress monitoring
      progressMonitor.start();
      
      // Handle stdout
      child.stdout.on('data', (data) => {
        const chunk = data.toString();
        stdout += chunk;
        
        // Process each line for progress
        chunk.split('\n').forEach(line => {
          if (line.trim()) {
            progressMonitor.processOutput(line);
          }
        });
        
        // Check buffer size
        if (stdout.length > this.maxBuffer) {
          killed = true;
          child.kill('SIGTERM');
          reject(new Error('Output exceeded maximum buffer size'));
        }
      });
      
      // Handle stderr (Nix outputs progress here too)
      child.stderr.on('data', (data) => {
        const chunk = data.toString();
        stderr += chunk;
        
        // Process for progress
        chunk.split('\n').forEach(line => {
          if (line.trim()) {
            progressMonitor.processOutput(line);
          }
        });
        
        // Check buffer size
        if (stderr.length > this.maxBuffer) {
          killed = true;
          child.kill('SIGTERM');
          reject(new Error('Error output exceeded maximum buffer size'));
        }
      });
      
      // Set up dynamic timeout
      let timeoutHandle = null;
      let lastProgressTime = Date.now();
      
      // Check progress periodically
      const progressCheckInterval = setInterval(() => {
        const state = progressMonitor.getState();
        
        if (state.lastProgress) {
          lastProgressTime = state.lastProgress.timestamp;
        }
        
        // Extend timeout if making progress
        const timeSinceProgress = Date.now() - lastProgressTime;
        if (timeSinceProgress < 60000 && timeoutHandle) { // Progress within last minute
          // Reset timeout
          clearTimeout(timeoutHandle);
          timeoutHandle = setTimeout(() => {
            if (!killed) {
              killed = true;
              child.kill('SIGTERM');
              reject(new Error(`Operation timed out after ${timeout}ms (with progress extension)`));
            }
          }, timeout);
        }
      }, 5000); // Check every 5 seconds
      
      // Initial timeout
      timeoutHandle = setTimeout(() => {
        if (!killed) {
          killed = true;
          child.kill('SIGTERM');
          
          const state = progressMonitor.getState();
          const error = new Error(`Operation timed out after ${timeout}ms`);
          error.progressState = state;
          reject(error);
        }
      }, timeout);
      
      // Handle process exit
      child.on('exit', (code, signal) => {
        clearTimeout(timeoutHandle);
        clearInterval(progressCheckInterval);
        
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
      
      // Handle process error
      child.on('error', (error) => {
        clearTimeout(timeoutHandle);
        clearInterval(progressCheckInterval);
        
        if (killed) return;
        reject(error);
      });
    });
  }

  /**
   * Validate command safety
   */
  validateCommand(command) {
    if (!command || !command.command) {
      throw new Error('Invalid command structure');
    }
    
    if (!this.allowedCommands.has(command.command)) {
      throw new Error(`Command '${command.command}' is not allowed`);
    }
    
    if (!Array.isArray(command.args)) {
      throw new Error('Command arguments must be an array');
    }
  }

  /**
   * Get suggestion for timeout error
   */
  getTimeoutSuggestion(command, timeout, progressState) {
    const operation = this.timeoutManager.identifyOperation(command);
    const minutes = Math.round(timeout / 60000);
    
    if (progressState.lastProgress) {
      // Had progress but still timed out
      return `The operation was making progress but took longer than ${minutes} minutes. ` +
             `Try:\n` +
             `1. Enable patient mode: "set patient mode on"\n` +
             `2. Check your internet connection\n` +
             `3. Run with --dry-run first to see what will happen`;
    } else {
      // No progress detected
      return `The operation showed no progress for ${Math.round(progressState.inactivity / 60000)} minutes. ` +
             `This might indicate:\n` +
             `1. Network connectivity issues\n` +
             `2. The package server is down\n` +
             `3. The operation is stuck\n` +
             `Try running with --dry-run to test`;
    }
  }

  /**
   * Get operation status
   */
  getOperationStatus(executionId) {
    const operation = this.activeOperations.get(executionId);
    
    if (!operation) {
      return { status: 'unknown', message: 'Operation not found' };
    }
    
    const runtime = Date.now() - operation.startTime;
    const progress = operation.progressMonitor.getState();
    
    return {
      status: operation.status,
      runtime,
      progress: progress.lastProgress,
      phase: progress.phase,
      details: progress.details,
      estimatedRemaining: operation.timeout - runtime
    };
  }

  /**
   * Cancel operation
   */
  cancelOperation(executionId) {
    const operation = this.activeOperations.get(executionId);
    
    if (!operation || operation.status !== 'running') {
      return false;
    }
    
    // This would need to track the child process
    // For now, mark as cancelled
    operation.status = 'cancelled';
    operation.endTime = Date.now();
    
    return true;
  }

  /**
   * Update timeout preferences
   */
  async updateTimeoutPreferences(preferences) {
    await this.timeoutManager.updatePreferences(preferences);
  }
}

module.exports = EnhancedCommandExecutor;