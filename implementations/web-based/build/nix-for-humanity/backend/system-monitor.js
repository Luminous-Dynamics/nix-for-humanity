/**
 * System State Monitor for Nix for Humanity
 * Tracks system changes and provides real-time updates
 */

const { spawn } = require('child_process');
const EventEmitter = require('events');
const fs = require('fs').promises;
const path = require('path');

class SystemMonitor extends EventEmitter {
  constructor() {
    super();
    this.monitoring = false;
    this.state = {
      packages: new Map(),
      channels: [],
      generations: [],
      diskUsage: {},
      systemHealth: 'good'
    };
    this.pollInterval = null;
  }

  /**
   * Start monitoring system state
   */
  async start() {
    if (this.monitoring) return;
    
    this.monitoring = true;
    console.log('🔍 Starting system monitoring...');
    
    // Initial state scan
    await this.updateState();
    
    // Poll for changes every 30 seconds
    this.pollInterval = setInterval(() => {
      this.updateState();
    }, 30000);
    
    // Monitor specific events
    this.watchNixStore();
    this.watchGenerations();
  }

  /**
   * Stop monitoring
   */
  stop() {
    this.monitoring = false;
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
      this.pollInterval = null;
    }
    console.log('🛑 Stopped system monitoring');
  }

  /**
   * Update complete system state
   */
  async updateState() {
    try {
      const oldState = JSON.stringify(this.state);
      
      // Update all components
      await Promise.all([
        this.updatePackages(),
        this.updateChannels(),
        this.updateGenerations(),
        this.updateDiskUsage(),
        this.checkSystemHealth()
      ]);
      
      const newState = JSON.stringify(this.state);
      
      // Emit change event if state changed
      if (oldState !== newState) {
        this.emit('state-changed', this.state);
      }
      
    } catch (error) {
      console.error('Failed to update system state:', error);
      this.state.systemHealth = 'error';
    }
  }

  /**
   * Update installed packages list
   */
  async updatePackages() {
    return new Promise((resolve) => {
      const proc = spawn('nix-env', ['-q', '--json']);
      let output = '';
      
      proc.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      proc.on('close', (code) => {
        if (code === 0) {
          try {
            const packages = JSON.parse(output);
            const oldCount = this.state.packages.size;
            
            this.state.packages.clear();
            Object.entries(packages).forEach(([name, info]) => {
              this.state.packages.set(name, {
                name,
                version: info.version,
                system: info.system
              });
            });
            
            // Detect package changes
            const newCount = this.state.packages.size;
            if (newCount !== oldCount) {
              this.emit('packages-changed', {
                installed: newCount - oldCount,
                total: newCount
              });
            }
            
          } catch (error) {
            console.error('Failed to parse packages:', error);
          }
        }
        resolve();
      });
    });
  }

  /**
   * Update channel information
   */
  async updateChannels() {
    return new Promise((resolve) => {
      const proc = spawn('nix-channel', ['--list']);
      let output = '';
      
      proc.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      proc.on('close', (code) => {
        if (code === 0) {
          const channels = output.trim().split('\n')
            .filter(line => line)
            .map(line => {
              const [name, url] = line.split(' ');
              return { name, url };
            });
            
          this.state.channels = channels;
        }
        resolve();
      });
    });
  }

  /**
   * Update generation history
   */
  async updateGenerations() {
    return new Promise((resolve) => {
      const proc = spawn('nix-env', ['--list-generations']);
      let output = '';
      
      proc.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      proc.on('close', (code) => {
        if (code === 0) {
          const generations = output.trim().split('\n')
            .filter(line => line)
            .map(line => {
              const match = line.match(/^\s*(\d+)\s+(.+?)\s+(\(current\))?$/);
              if (match) {
                return {
                  number: parseInt(match[1]),
                  date: match[2],
                  current: !!match[3]
                };
              }
              return null;
            })
            .filter(gen => gen);
            
          const oldCurrent = this.state.generations.find(g => g.current)?.number;
          const newCurrent = generations.find(g => g.current)?.number;
          
          if (oldCurrent !== newCurrent && oldCurrent !== undefined) {
            this.emit('generation-changed', {
              from: oldCurrent,
              to: newCurrent
            });
          }
          
          this.state.generations = generations;
        }
        resolve();
      });
    });
  }

  /**
   * Update disk usage
   */
  async updateDiskUsage() {
    return new Promise((resolve) => {
      const proc = spawn('df', ['-h', '/nix/store']);
      let output = '';
      
      proc.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      proc.on('close', (code) => {
        if (code === 0) {
          const lines = output.split('\n');
          if (lines[1]) {
            const parts = lines[1].split(/\s+/);
            const usage = {
              total: parts[1],
              used: parts[2],
              available: parts[3],
              percentage: parseInt(parts[4])
            };
            
            // Warn if disk usage is high
            if (usage.percentage > 90) {
              this.emit('disk-warning', usage);
            }
            
            this.state.diskUsage = usage;
          }
        }
        resolve();
      });
    });
  }

  /**
   * Check overall system health
   */
  async checkSystemHealth() {
    const issues = [];
    
    // Check disk space
    if (this.state.diskUsage.percentage > 90) {
      issues.push('Low disk space');
    }
    
    // Check for broken packages
    try {
      const result = await this.runCommand('nix-store', ['--verify', '--check-contents']);
      if (result.stderr.includes('error')) {
        issues.push('Store integrity issues');
      }
    } catch (error) {
      // Ignore verification errors for now
    }
    
    // Update health status
    if (issues.length === 0) {
      this.state.systemHealth = 'good';
    } else if (issues.length === 1) {
      this.state.systemHealth = 'warning';
    } else {
      this.state.systemHealth = 'critical';
    }
    
    if (issues.length > 0) {
      this.emit('health-issues', issues);
    }
  }

  /**
   * Watch Nix store for changes
   */
  watchNixStore() {
    // Simple polling approach for cross-platform compatibility
    let lastModified = null;
    
    setInterval(async () => {
      try {
        const stats = await fs.stat('/nix/store');
        const currentModified = stats.mtime.getTime();
        
        if (lastModified && currentModified !== lastModified) {
          this.emit('store-changed');
          // Trigger package update
          await this.updatePackages();
        }
        
        lastModified = currentModified;
      } catch (error) {
        // Store might not exist in demo mode
      }
    }, 5000);
  }

  /**
   * Watch for generation changes
   */
  watchGenerations() {
    let lastGeneration = null;
    
    setInterval(async () => {
      const current = this.state.generations.find(g => g.current);
      if (current && lastGeneration && current.number !== lastGeneration) {
        this.emit('generation-switched', {
          from: lastGeneration,
          to: current.number
        });
      }
      lastGeneration = current?.number;
    }, 2000);
  }

  /**
   * Run command helper
   */
  runCommand(command, args) {
    return new Promise((resolve, reject) => {
      const proc = spawn(command, args);
      let stdout = '';
      let stderr = '';
      
      proc.stdout.on('data', (data) => {
        stdout += data.toString();
      });
      
      proc.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      
      proc.on('close', (code) => {
        resolve({ stdout, stderr, code });
      });
      
      proc.on('error', reject);
    });
  }

  /**
   * Get current state
   */
  getState() {
    return {
      ...this.state,
      packages: Array.from(this.state.packages.values()),
      monitoring: this.monitoring
    };
  }

  /**
   * Get state summary
   */
  getSummary() {
    return {
      packageCount: this.state.packages.size,
      channelCount: this.state.channels.length,
      currentGeneration: this.state.generations.find(g => g.current)?.number || 0,
      diskUsage: this.state.diskUsage.percentage || 0,
      health: this.state.systemHealth
    };
  }
}

// Export singleton
module.exports = new SystemMonitor();