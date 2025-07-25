/**
 * Timeout Manager for Nix Operations
 * Prevents frustrating timeouts on legitimate long-running operations
 */

const os = require('os');
const fs = require('fs').promises;
const path = require('path');

class TimeoutManager {
  constructor(options = {}) {
    this.configPath = options.configPath || 
      path.join(process.env.HOME, '.config/nix-for-humanity/timeout-config.json');
    
    // Base timeout configurations (in milliseconds)
    this.baseTimeouts = {
      // Query operations (fast)
      search: 15000,           // 15 seconds
      info: 10000,            // 10 seconds  
      list: 10000,            // 10 seconds
      status: 5000,           // 5 seconds
      
      // Package operations (variable)
      install: {
        instant: 30000,       // 30 seconds (tiny packages)
        small: 120000,        // 2 minutes
        medium: 300000,       // 5 minutes
        large: 900000,        // 15 minutes
        huge: 1800000,        // 30 minutes
        unknown: 600000       // 10 minutes (default)
      },
      remove: 60000,          // 1 minute
      
      // System operations (long)
      update: 600000,         // 10 minutes
      upgrade: 1800000,       // 30 minutes
      rebuild: 3600000,       // 60 minutes
      'switch': 1800000,      // 30 minutes
      'garbage-collect': 1200000, // 20 minutes
      
      // Channel operations
      'channel-update': 300000,  // 5 minutes
      'channel-add': 60000,      // 1 minute
    };
    
    // Package size database (this could be loaded from a file)
    this.packageDatabase = {
      instant: new Set([
        'hello', 'cowsay', 'fortune', 'sl', 'tree', 'ncdu',
        'htop', 'btop', 'jq', 'yq', 'bat', 'exa', 'fd', 'ripgrep'
      ]),
      
      small: new Set([
        'git', 'vim', 'neovim', 'nano', 'emacs-nox', 'tmux', 'screen',
        'zsh', 'fish', 'bash', 'curl', 'wget', 'rsync', 'ssh',
        'python3', 'nodejs', 'ruby', 'perl', 'lua'
      ]),
      
      medium: new Set([
        'firefox', 'firefox-esr', 'chromium', 'brave', 'thunderbird',
        'vscode', 'vscodium', 'sublime-text', 'atom',
        'gcc', 'clang', 'rustc', 'go', 'openjdk', 'dotnet-sdk',
        'docker', 'podman', 'postgresql', 'mysql', 'redis'
      ]),
      
      large: new Set([
        'libreoffice', 'libreoffice-fresh', 'openoffice',
        'gimp', 'inkscape', 'blender', 'krita',
        'obs-studio', 'kdenlive', 'davinci-resolve',
        'virtualbox', 'vmware-workstation', 'qemu',
        'android-studio', 'intellij-idea', 'pycharm'
      ]),
      
      huge: new Set([
        'cuda', 'cudatoolkit', 'cudnn', 'tensorflow', 'pytorch',
        'matlab', 'mathematica', 'maple',
        'unreal-engine', 'unity3d', 'godot',
        'texlive-full', 'mactex'
      ])
    };
    
    // User preferences
    this.userConfig = null;
    this.loadConfig();
  }

  async loadConfig() {
    try {
      const data = await fs.readFile(this.configPath, 'utf8');
      this.userConfig = JSON.parse(data);
    } catch {
      // Default config if none exists
      this.userConfig = {
        networkSpeed: 'auto',
        patientMode: false,
        timeoutMultiplier: 1.0,
        customTimeouts: {}
      };
    }
  }

  /**
   * Calculate appropriate timeout for a command
   */
  async calculateTimeout(command, options = {}) {
    // Allow explicit timeout override
    if (options.timeout) {
      return options.timeout;
    }
    
    // Dry-run operations are always fast
    if (this.isDryRun(command, options)) {
      return 30000; // 30 seconds max
    }
    
    // Get base timeout for operation
    const operation = this.identifyOperation(command);
    let timeout = this.getBaseTimeout(operation, command);
    
    // Apply modifiers
    const modifiers = await this.calculateModifiers(command, options);
    timeout = this.applyModifiers(timeout, modifiers);
    
    // Apply user preferences
    if (this.userConfig.patientMode) {
      timeout *= 2; // Double all timeouts in patient mode
    }
    
    timeout *= this.userConfig.timeoutMultiplier;
    
    // Check for custom timeout
    const packageName = this.extractPackageName(command);
    if (packageName && this.userConfig.customTimeouts[packageName]) {
      timeout = this.userConfig.customTimeouts[packageName];
    }
    
    // Set reasonable bounds
    const MIN_TIMEOUT = 5000;   // 5 seconds minimum
    const MAX_TIMEOUT = 7200000; // 2 hours maximum
    
    return Math.min(Math.max(timeout, MIN_TIMEOUT), MAX_TIMEOUT);
  }

  /**
   * Identify the operation type from command
   */
  identifyOperation(command) {
    const cmd = command.command;
    const args = command.args.join(' ');
    
    // Nix commands
    if (cmd === 'nix') {
      if (args.includes('search')) return 'search';
      if (args.includes('show') || args.includes('info')) return 'info';
      if (args.includes('profile install') || args.includes('install')) return 'install';
      if (args.includes('profile remove') || args.includes('remove')) return 'remove';
      if (args.includes('profile upgrade') || args.includes('upgrade')) return 'upgrade';
    }
    
    // Nix-env commands
    if (cmd === 'nix-env') {
      if (args.includes('-qa') || args.includes('--query')) return 'search';
      if (args.includes('-i') || args.includes('--install')) return 'install';
      if (args.includes('-e') || args.includes('--uninstall')) return 'remove';
      if (args.includes('-u') || args.includes('--upgrade')) return 'upgrade';
      if (args.includes('-q') || args.includes('--installed')) return 'list';
    }
    
    // NixOS commands
    if (cmd === 'nixos-rebuild') {
      if (args.includes('switch')) return 'switch';
      if (args.includes('boot')) return 'rebuild';
      if (args.includes('test')) return 'rebuild';
      if (args.includes('build')) return 'rebuild';
    }
    
    // Other commands
    if (cmd === 'nix-collect-garbage') return 'garbage-collect';
    if (cmd === 'nix-channel' && args.includes('--update')) return 'channel-update';
    if (cmd === 'systemctl') return 'status';
    
    return 'unknown';
  }

  /**
   * Get base timeout for operation
   */
  getBaseTimeout(operation, command) {
    if (operation === 'install') {
      const packageName = this.extractPackageName(command);
      const size = this.getPackageSize(packageName);
      return this.baseTimeouts.install[size] || this.baseTimeouts.install.unknown;
    }
    
    return this.baseTimeouts[operation] || 300000; // 5 minutes default
  }

  /**
   * Extract package name from command
   */
  extractPackageName(command) {
    const args = command.args.join(' ');
    
    // Try different patterns
    const patterns = [
      /nixpkgs#(\S+)/,           // nix profile install nixpkgs#package
      /nixpkgs\.(\S+)/,          // nix-env -iA nixpkgs.package
      /install\s+(\S+)/,         // generic install package
      /'([^']+)'/,               // quoted package name
    ];
    
    for (const pattern of patterns) {
      const match = args.match(pattern);
      if (match) {
        return match[1];
      }
    }
    
    return null;
  }

  /**
   * Determine package size category
   */
  getPackageSize(packageName) {
    if (!packageName) return 'unknown';
    
    // Check exact matches first
    for (const [size, packages] of Object.entries(this.packageDatabase)) {
      if (packages.has(packageName)) {
        return size;
      }
    }
    
    // Check patterns
    if (packageName.endsWith('-doc') || packageName.endsWith('-man')) {
      return 'small'; // Documentation is usually small
    }
    
    if (packageName.includes('-full') || packageName.includes('-all')) {
      return 'large'; // Full versions are usually large
    }
    
    if (packageName.startsWith('python3-') || packageName.startsWith('perl-')) {
      return 'small'; // Language libraries are usually small
    }
    
    if (packageName.includes('texlive') || packageName.includes('cuda')) {
      return 'huge'; // These are known to be huge
    }
    
    return 'medium'; // Default to medium
  }

  /**
   * Calculate timeout modifiers based on system state
   */
  async calculateModifiers(command, options) {
    const modifiers = {
      networkSpeed: 1.0,
      systemLoad: 1.0,
      firstInstall: 1.0,
      buildFromSource: 1.0
    };
    
    // Network speed modifier
    if (options.networkSpeed) {
      modifiers.networkSpeed = this.getNetworkSpeedModifier(options.networkSpeed);
    } else if (this.userConfig.networkSpeed === 'auto') {
      // Could implement actual speed test here
      modifiers.networkSpeed = 1.0;
    } else {
      modifiers.networkSpeed = this.getNetworkSpeedModifier(this.userConfig.networkSpeed);
    }
    
    // System load modifier
    const load = os.loadavg()[0];
    const cores = os.cpus().length;
    if (load > cores * 0.8) {
      modifiers.systemLoad = 1.5; // 50% slower under high load
    }
    
    // First install modifier (needs to download Nix database)
    if (await this.isFirstInstall()) {
      modifiers.firstInstall = 2.0; // Double the timeout
    }
    
    // Build from source modifier
    if (options.buildFromSource || this.mightBuildFromSource(command)) {
      modifiers.buildFromSource = 3.0; // Triple the timeout
    }
    
    return modifiers;
  }

  /**
   * Apply modifiers to base timeout
   */
  applyModifiers(timeout, modifiers) {
    let modified = timeout;
    
    for (const [key, multiplier] of Object.entries(modifiers)) {
      modified *= multiplier;
    }
    
    return Math.round(modified);
  }

  /**
   * Get network speed modifier
   */
  getNetworkSpeedModifier(speed) {
    const modifiers = {
      'fast': 0.8,    // Reduce timeout by 20%
      'medium': 1.0,  // No change
      'slow': 2.0,    // Double timeout
      'very-slow': 3.0 // Triple timeout
    };
    
    return modifiers[speed] || 1.0;
  }

  /**
   * Check if this is a dry-run operation
   */
  isDryRun(command, options) {
    return options.dryRun || 
           command.args.includes('--dry-run') ||
           command.args.includes('--dry-activate');
  }

  /**
   * Check if this is the first Nix installation
   */
  async isFirstInstall() {
    try {
      // Check if Nix database exists
      await fs.access(path.join(process.env.HOME, '.cache/nix'));
      return false;
    } catch {
      return true;
    }
  }

  /**
   * Check if command might build from source
   */
  mightBuildFromSource(command) {
    const args = command.args.join(' ');
    
    // Look for signs of source building
    return args.includes('.drv') ||
           args.includes('--fallback') ||
           args.includes('--option build-fallback true');
  }

  /**
   * Get human-friendly timeout description
   */
  getTimeoutDescription(timeout) {
    const minutes = Math.round(timeout / 60000);
    
    if (minutes < 1) {
      return {
        brief: "a few seconds",
        message: "This should be quick! ⚡"
      };
    } else if (minutes === 1) {
      return {
        brief: "about a minute",
        message: "This will just take a minute."
      };
    } else if (minutes < 5) {
      return {
        brief: `about ${minutes} minutes`,
        message: `This will take about ${minutes} minutes.`
      };
    } else if (minutes < 15) {
      return {
        brief: `${minutes} minutes`,
        message: `This might take up to ${minutes} minutes. Good time for a quick break! ☕`
      };
    } else if (minutes < 30) {
      return {
        brief: `${minutes} minutes`,
        message: `This is a bigger operation (up to ${minutes} minutes). Feel free to do other things!`
      };
    } else {
      return {
        brief: `${minutes}+ minutes`,
        message: `This is a major operation that could take ${minutes} minutes or more. I'll work in the background.`
      };
    }
  }

  /**
   * Save user preferences
   */
  async saveConfig() {
    await fs.mkdir(path.dirname(this.configPath), { recursive: true });
    await fs.writeFile(
      this.configPath,
      JSON.stringify(this.userConfig, null, 2)
    );
  }

  /**
   * Update user preferences
   */
  async updatePreferences(preferences) {
    Object.assign(this.userConfig, preferences);
    await this.saveConfig();
  }
}

module.exports = TimeoutManager;