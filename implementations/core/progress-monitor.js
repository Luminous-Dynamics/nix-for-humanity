/**
 * Progress Monitor for Long-Running Nix Operations
 * Detects progress and prevents premature timeouts
 */

const EventEmitter = require('events');

class ProgressMonitor extends EventEmitter {
  constructor(options = {}) {
    super();
    
    // Configuration
    this.inactivityTimeout = options.inactivityTimeout || 300000; // 5 minutes
    this.checkInterval = options.checkInterval || 1000; // Check every second
    
    // Progress detection patterns
    this.progressPatterns = [
      // Download progress
      {
        pattern: /(\d+)%.*?(\d+(?:\.\d+)?)\s*([KMG]i?B).*?(\d+(?:\.\d+)?)\s*([KMG]i?B)/,
        handler: this.handleDownloadProgress.bind(this)
      },
      {
        pattern: /downloading.*?'([^']+)'/i,
        handler: this.handleDownloadStart.bind(this)
      },
      
      // Building progress
      {
        pattern: /building\s+'([^']+)'/i,
        handler: this.handleBuildProgress.bind(this)
      },
      {
        pattern: /\[(\d+)\/(\d+)\]\s+building/i,
        handler: this.handleBuildCount.bind(this)
      },
      
      // Copying/Installing
      {
        pattern: /copying\s+(\d+)\s+paths?/i,
        handler: this.handleCopyProgress.bind(this)
      },
      {
        pattern: /installing\s+'([^']+)'/i,
        handler: this.handleInstallProgress.bind(this)
      },
      
      // Nix-specific progress
      {
        pattern: /evaluating\s+(?:derivation|file)/i,
        handler: this.handleEvaluation.bind(this)
      },
      {
        pattern: /querying\s+info\s+about\s+(\d+)\s+paths?/i,
        handler: this.handleQuerying.bind(this)
      },
      {
        pattern: /fetching\s+(\d+)\s+store\s+paths?/i,
        handler: this.handleFetching.bind(this)
      },
      
      // Channel updates
      {
        pattern: /unpacking\s+channels/i,
        handler: this.handleChannelUpdate.bind(this)
      },
      
      // Garbage collection
      {
        pattern: /deleting\s+'([^']+)'/i,
        handler: this.handleGarbageCollection.bind(this)
      },
      {
        pattern: /(\d+(?:\.\d+)?)\s*([KMG]i?B)\s+freed/i,
        handler: this.handleFreedSpace.bind(this)
      }
    ];
    
    // State tracking
    this.state = {
      lastActivity: Date.now(),
      lastProgress: null,
      phase: 'starting',
      details: {},
      history: []
    };
    
    // Timers
    this.checkTimer = null;
    this.inactivityTimer = null;
  }

  /**
   * Start monitoring a process
   */
  start() {
    this.state.startTime = Date.now();
    this.state.lastActivity = Date.now();
    this.state.phase = 'running';
    
    // Start inactivity timer
    this.resetInactivityTimer();
    
    // Start periodic state check
    this.checkTimer = setInterval(() => {
      this.checkState();
    }, this.checkInterval);
    
    this.emit('start', { phase: 'running' });
  }

  /**
   * Stop monitoring
   */
  stop() {
    if (this.checkTimer) {
      clearInterval(this.checkTimer);
      this.checkTimer = null;
    }
    
    if (this.inactivityTimer) {
      clearTimeout(this.inactivityTimer);
      this.inactivityTimer = null;
    }
    
    this.state.phase = 'stopped';
    this.emit('stop', { duration: Date.now() - this.state.startTime });
  }

  /**
   * Process output line
   */
  processOutput(line) {
    // Check each pattern
    for (const { pattern, handler } of this.progressPatterns) {
      const match = line.match(pattern);
      if (match) {
        this.state.lastActivity = Date.now();
        this.resetInactivityTimer();
        
        const progress = handler(match, line);
        if (progress) {
          this.updateProgress(progress);
        }
        
        // Don't break - multiple patterns might match
      }
    }
    
    // Store recent output for context
    this.state.history.push({
      timestamp: Date.now(),
      line: line.substring(0, 200) // Limit length
    });
    
    // Keep only recent history
    if (this.state.history.length > 100) {
      this.state.history.shift();
    }
  }

  /**
   * Update progress state
   */
  updateProgress(progress) {
    this.state.lastProgress = {
      ...progress,
      timestamp: Date.now()
    };
    
    // Update phase if provided
    if (progress.phase) {
      this.state.phase = progress.phase;
    }
    
    // Merge details
    if (progress.details) {
      Object.assign(this.state.details, progress.details);
    }
    
    this.emit('progress', progress);
  }

  /**
   * Check if operation should timeout
   */
  shouldTimeout() {
    const inactivityDuration = Date.now() - this.state.lastActivity;
    return inactivityDuration > this.inactivityTimeout;
  }

  /**
   * Reset inactivity timer
   */
  resetInactivityTimer() {
    if (this.inactivityTimer) {
      clearTimeout(this.inactivityTimer);
    }
    
    this.inactivityTimer = setTimeout(() => {
      this.emit('timeout', {
        reason: 'inactivity',
        duration: Date.now() - this.state.lastActivity,
        lastProgress: this.state.lastProgress
      });
    }, this.inactivityTimeout);
  }

  /**
   * Periodic state check
   */
  checkState() {
    const now = Date.now();
    const runtime = now - this.state.startTime;
    const inactivity = now - this.state.lastActivity;
    
    // Emit periodic status
    this.emit('status', {
      phase: this.state.phase,
      runtime,
      inactivity,
      lastProgress: this.state.lastProgress,
      details: this.state.details
    });
  }

  // Progress handlers

  handleDownloadProgress(match) {
    const percentage = parseInt(match[1]);
    const downloaded = parseFloat(match[2]);
    const downloadedUnit = match[3];
    const total = parseFloat(match[4]);
    const totalUnit = match[5];
    
    return {
      type: 'download',
      phase: 'downloading',
      percentage,
      message: `Downloading: ${percentage}% (${downloaded}${downloadedUnit}/${total}${totalUnit})`,
      details: {
        downloaded: `${downloaded}${downloadedUnit}`,
        total: `${total}${totalUnit}`,
        percentage
      }
    };
  }

  handleDownloadStart(match) {
    const item = match[1];
    return {
      type: 'download-start',
      phase: 'downloading',
      message: `Downloading: ${item}`,
      details: { item }
    };
  }

  handleBuildProgress(match) {
    const item = match[1];
    return {
      type: 'build',
      phase: 'building',
      message: `Building: ${item}`,
      details: { item }
    };
  }

  handleBuildCount(match) {
    const current = parseInt(match[1]);
    const total = parseInt(match[2]);
    const percentage = Math.round((current / total) * 100);
    
    return {
      type: 'build-count',
      phase: 'building',
      percentage,
      message: `Building: ${current}/${total} (${percentage}%)`,
      details: { current, total, percentage }
    };
  }

  handleCopyProgress(match) {
    const count = parseInt(match[1]);
    return {
      type: 'copy',
      phase: 'copying',
      message: `Copying ${count} paths to store...`,
      details: { count }
    };
  }

  handleInstallProgress(match) {
    const item = match[1];
    return {
      type: 'install',
      phase: 'installing',
      message: `Installing: ${item}`,
      details: { item }
    };
  }

  handleEvaluation() {
    return {
      type: 'evaluation',
      phase: 'evaluating',
      message: 'Evaluating package definitions...'
    };
  }

  handleQuerying(match) {
    const count = parseInt(match[1]);
    return {
      type: 'query',
      phase: 'querying',
      message: `Querying info about ${count} paths...`,
      details: { count }
    };
  }

  handleFetching(match) {
    const count = parseInt(match[1]);
    return {
      type: 'fetch',
      phase: 'fetching',
      message: `Fetching ${count} paths from cache...`,
      details: { count }
    };
  }

  handleChannelUpdate() {
    return {
      type: 'channel',
      phase: 'updating',
      message: 'Updating channels...'
    };
  }

  handleGarbageCollection(match) {
    const item = match[1];
    return {
      type: 'gc',
      phase: 'cleaning',
      message: `Removing: ${item}`,
      details: { item }
    };
  }

  handleFreedSpace(match) {
    const amount = parseFloat(match[1]);
    const unit = match[2];
    return {
      type: 'gc-freed',
      phase: 'complete',
      message: `Freed ${amount} ${unit} of disk space`,
      details: { freed: `${amount} ${unit}` }
    };
  }

  /**
   * Get current state summary
   */
  getState() {
    return {
      phase: this.state.phase,
      runtime: Date.now() - this.state.startTime,
      lastActivity: this.state.lastActivity,
      lastProgress: this.state.lastProgress,
      details: this.state.details,
      isActive: !this.shouldTimeout()
    };
  }

  /**
   * Format progress for user display
   */
  formatProgress(progress) {
    if (!progress) return 'Working...';
    
    // Add emoji based on phase
    const phaseEmoji = {
      downloading: '📥',
      building: '🔨',
      copying: '📋',
      installing: '📦',
      evaluating: '🔍',
      querying: '🔎',
      fetching: '🌐',
      updating: '🔄',
      cleaning: '🧹',
      complete: '✅'
    };
    
    const emoji = phaseEmoji[progress.phase] || '⚙️';
    
    // Format with percentage if available
    if (progress.percentage !== undefined) {
      return `${emoji} ${progress.message} [${this.createProgressBar(progress.percentage)}]`;
    }
    
    return `${emoji} ${progress.message}`;
  }

  /**
   * Create text progress bar
   */
  createProgressBar(percentage, width = 20) {
    const filled = Math.round((percentage / 100) * width);
    const empty = width - filled;
    return '█'.repeat(filled) + '░'.repeat(empty) + ` ${percentage}%`;
  }
}

module.exports = ProgressMonitor;