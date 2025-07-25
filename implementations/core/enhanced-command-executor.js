/**
 * Enhanced Command Executor with Progress Monitoring
 * Integrates dynamic timeouts and progress monitoring for better UX
 */

const { EventEmitter } = require('events');
const TimeoutManager = require('./timeout-manager');
const CommandExecutor = require('./command-executor');

class EnhancedCommandExecutor extends EventEmitter {
  constructor(options = {}) {
    super();
    
    // Initialize components
    this.timeoutManager = new TimeoutManager(options);
    this.baseExecutor = new CommandExecutor(options);
    
    // Progress monitoring state
    this.activeOperations = new Map();
    this.progressPatterns = this.initProgressPatterns();
  }

  /**
   * Execute command with enhanced monitoring
   */
  async execute(command, options = {}) {
    const executionId = this.generateExecutionId();
    const startTime = Date.now();
    
    try {
      // Calculate dynamic timeout
      const timeout = await this.timeoutManager.calculateTimeout(command, options);
      const timeoutInfo = this.timeoutManager.getTimeoutDescription(timeout);
      
      // Emit start event with timeout info
      this.emit('executionStart', {
        executionId,
        command,
        timeout,
        timeoutInfo,
        estimatedDuration: timeoutInfo.brief
      });
      
      // Track operation
      const operation = {
        id: executionId,
        command,
        startTime,
        timeout,
        progress: 0,
        status: 'running',
        messages: []
      };
      
      this.activeOperations.set(executionId, operation);
      
      // Execute with progress monitoring
      const result = await this.executeWithProgress(command, {
        ...options,
        timeout,
        executionId,
        onProgress: (progress) => this.updateProgress(executionId, progress)
      });
      
      // Record success
      const duration = Date.now() - startTime;
      this.timeoutManager.recordOperation(
        {
          type: this.getOperationType(command),
          command: command.command,
          packageName: this.extractPackageName(command)
        },
        duration,
        true
      );
      
      // Update operation status
      operation.status = 'completed';
      operation.progress = 100;
      operation.endTime = Date.now();
      
      // Emit completion
      this.emit('executionComplete', {
        executionId,
        result,
        duration
      });
      
      return {
        ...result,
        executionId,
        timeoutUsed: timeout,
        actualDuration: duration
      };
      
    } catch (error) {
      // Record failure
      const duration = Date.now() - startTime;
      this.timeoutManager.recordOperation(
        {
          type: this.getOperationType(command),
          command: command.command,
          packageName: this.extractPackageName(command)
        },
        duration,
        false
      );
      
      // Update operation status
      const operation = this.activeOperations.get(executionId);
      if (operation) {
        operation.status = 'failed';
        operation.error = error.message;
        operation.endTime = Date.now();
      }
      
      // Emit error
      this.emit('executionError', {
        executionId,
        error,
        duration
      });
      
      throw error;
      
    } finally {
      // Clean up after a delay
      setTimeout(() => {
        this.activeOperations.delete(executionId);
      }, 60000); // Keep for 1 minute for status queries
    }
  }

  /**
   * Execute with progress monitoring
   */
  async executeWithProgress(command, options) {
    return new Promise((resolve, reject) => {
      const { spawn } = require('child_process');
      const child = spawn(command.command, command.args, {
        env: { ...process.env, ...command.env },
        cwd: options.cwd || process.cwd()
      });
      
      let stdout = '';
      let stderr = '';
      let killed = false;
      let lastProgress = 0;
      
      // Set timeout
      const timeoutHandle = setTimeout(() => {
        if (!killed) {
          killed = true;
          child.kill('SIGTERM');
          reject(new Error(`Command timed out after ${options.timeout}ms`));
        }
      }, options.timeout);
      
      // Monitor stdout for progress
      child.stdout.on('data', (data) => {
        const chunk = data.toString();
        stdout += chunk;
        
        // Extract progress from output
        const progress = this.extractProgress(chunk, command);
        if (progress > lastProgress) {
          lastProgress = progress;
          if (options.onProgress) {
            options.onProgress({
              percent: progress,
              message: this.extractProgressMessage(chunk)
            });
          }
        }
        
        // Check output size limit
        if (stdout.length > this.baseExecutor.maxBuffer) {
          killed = true;
          child.kill('SIGTERM');
          clearTimeout(timeoutHandle);
          reject(new Error('Output exceeded maximum buffer size'));
        }
      });
      
      // Monitor stderr
      child.stderr.on('data', (data) => {
        const chunk = data.toString();
        stderr += chunk;
        
        // Some progress is reported on stderr (e.g., download progress)
        const progress = this.extractProgress(chunk, command);
        if (progress > lastProgress) {
          lastProgress = progress;
          if (options.onProgress) {
            options.onProgress({
              percent: progress,
              message: this.extractProgressMessage(chunk)
            });
          }
        }
        
        // Check error size limit
        if (stderr.length > this.baseExecutor.maxBuffer) {
          killed = true;
          child.kill('SIGTERM');
          clearTimeout(timeoutHandle);
          reject(new Error('Error output exceeded maximum buffer size'));
        }
      });
      
      // Handle completion
      child.on('exit', (code, signal) => {
        clearTimeout(timeoutHandle);
        
        if (killed) return;
        
        if (code === 0) {
          resolve({
            success: true,
            stdout,
            stderr,
            code: 0
          });
        } else {
          const error = new Error(`Command failed with code ${code}`);
          error.code = code;
          error.signal = signal;
          error.stdout = stdout;
          error.stderr = stderr;
          reject(error);
        }
      });
      
      // Handle errors
      child.on('error', (error) => {
        clearTimeout(timeoutHandle);
        if (!killed) {
          reject(error);
        }
      });
    });
  }

  /**
   * Initialize progress patterns for different operations
   */
  initProgressPatterns() {
    return {
      // Download progress patterns
      download: [
        /(\d+)%/,                                    // Simple percentage
        /\[(\d+)\/(\d+)\]/,                         // [current/total]
        /(\d+\.?\d*)\s*(MB|GB).*?(\d+\.?\d*)\s*\1/, // Size progress
        /Downloaded:\s*(\d+)/                        // Downloaded count
      ],
      
      // Build progress patterns
      build: [
        /Building.*?(\d+)\/(\d+)/,                   // Building x/y
        /Compiling.*?(\d+)%/,                        // Compiling percentage
        /\[(\d+)\/(\d+)\]\s+(?:Building|Compiling)/, // Build steps
        /Phase:\s*(\w+)/                             // Build phases
      ],
      
      // Installation progress patterns
      install: [
        /Installing.*?(\d+)\/(\d+)/,                 // Installing x/y
        /Unpacking.*?(\d+)%/,                        // Unpacking percentage
        /Copying.*?(\d+)\s*files/,                   // File copying
        /Setting up.*?(\d+)\/(\d+)/                  // Setup steps
      ],
      
      // System update patterns
      update: [
        /Updating.*?(\d+)\/(\d+)/,                   // Update progress
        /Fetching.*?(\d+)%/,                         // Fetch percentage
        /Processing.*?(\d+)\s*packages/              // Package processing
      ]
    };
  }

  /**
   * Extract progress from output
   */
  extractProgress(output, command) {
    const operation = this.getOperationType(command);
    const patterns = this.progressPatterns[operation] || this.progressPatterns.download;
    
    for (const pattern of patterns) {
      const match = output.match(pattern);
      if (match) {
        if (match[2]) {
          // Fraction format (x/y)
          const current = parseInt(match[1]);
          const total = parseInt(match[2]);
          return Math.round((current / total) * 100);
        } else if (match[1]) {
          // Direct percentage
          return parseInt(match[1]);
        }
      }
    }
    
    // Check for common stage indicators
    const stages = {
      'downloading': 20,
      'unpacking': 40,
      'building': 60,
      'installing': 80,
      'cleaning up': 90,
      'done': 100
    };
    
    const lowerOutput = output.toLowerCase();
    for (const [stage, progress] of Object.entries(stages)) {
      if (lowerOutput.includes(stage)) {
        return progress;
      }
    }
    
    return 0;
  }

  /**
   * Extract human-readable progress message
   */
  extractProgressMessage(output) {
    // Extract meaningful lines
    const lines = output.split('\n').filter(line => line.trim());
    
    // Look for informative patterns
    for (const line of lines) {
      if (line.match(/downloading|unpacking|building|installing|updating/i)) {
        return line.trim();
      }
    }
    
    return lines[lines.length - 1] || '';
  }

  /**
   * Update progress for an operation
   */
  updateProgress(executionId, progress) {
    const operation = this.activeOperations.get(executionId);
    if (!operation) return;
    
    operation.progress = progress.percent;
    operation.lastMessage = progress.message;
    operation.lastUpdate = Date.now();
    
    this.emit('progress', {
      executionId,
      progress: progress.percent,
      message: progress.message,
      elapsed: Date.now() - operation.startTime
    });
  }

  /**
   * Get operation type from command
   */
  getOperationType(command) {
    return this.timeoutManager.identifyOperation(command);
  }

  /**
   * Extract package name from command
   */
  extractPackageName(command) {
    return this.timeoutManager.extractPackageName(command);
  }

  /**
   * Generate unique execution ID
   */
  generateExecutionId() {
    return `exec-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get status of an execution
   */
  getExecutionStatus(executionId) {
    const operation = this.activeOperations.get(executionId);
    if (!operation) {
      return {
        status: 'unknown',
        message: 'Operation not found'
      };
    }
    
    return {
      status: operation.status,
      progress: operation.progress,
      message: operation.lastMessage,
      elapsed: Date.now() - operation.startTime,
      timeout: operation.timeout
    };
  }

  /**
   * Cancel an execution
   */
  async cancelExecution(executionId) {
    const operation = this.activeOperations.get(executionId);
    if (!operation || operation.status !== 'running') {
      return false;
    }
    
    // This would need to track the child process
    // For now, mark as cancelled
    operation.status = 'cancelled';
    operation.endTime = Date.now();
    
    this.emit('executionCancelled', {
      executionId,
      elapsed: operation.endTime - operation.startTime
    });
    
    return true;
  }
}

module.exports = EnhancedCommandExecutor;