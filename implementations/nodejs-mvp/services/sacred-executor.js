// 🔨 Sacred Command Executor - Where Intentions Manifest
// This bridges the sacred intent engine with real NixOS execution

const { exec, spawn } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

class SacredExecutor {
  constructor() {
    this.safeMode = true; // Start in safe mode
    this.requireConfirmation = true;
    this.sudoCommands = this.initializeSudoCommands();
    this.dangerousCommands = this.initializeDangerousCommands();
  }

  initializeSudoCommands() {
    // Commands that require elevated privileges
    return new Set([
      'nixos-rebuild',
      'shutdown',
      'reboot',
      'nix-collect-garbage',
      'nix-channel',
      'systemctl'
    ]);
  }

  initializeDangerousCommands() {
    // Commands that need extra confirmation
    return new Set([
      'rm',
      'shutdown',
      'reboot',
      'nixos-rebuild switch',
      'nix-collect-garbage -d'
    ]);
  }

  // Main execution method
  async execute(intent, options = {}) {
    try {
      // 1. Validate the intent
      const validation = await this.validateIntent(intent);
      if (!validation.safe) {
        return {
          success: false,
          error: validation.reason,
          suggestion: validation.suggestion,
          mantra: 'Sacred boundaries protect us'
        };
      }

      // 2. Build the actual command
      const command = this.buildCommand(intent);
      
      // 3. Check if confirmation needed
      if (this.needsConfirmation(command, intent)) {
        return {
          success: false,
          requiresConfirmation: true,
          command: command,
          warning: this.getWarningMessage(intent),
          mantra: intent.mantra || 'Mindful action requires presence'
        };
      }

      // 4. Execute with sacred care
      const result = await this.executeWithCare(command, intent);
      
      // 5. Format response with love
      return this.formatResponse(result, intent);

    } catch (error) {
      return this.handleErrorWithCompassion(error, intent);
    }
  }

  // Validate intent for safety
  async validateIntent(intent) {
    // Check for malicious patterns
    const maliciousPatterns = [
      /rm\s+-rf\s+\//,
      /:\(\)\{:\|:&\}\;:/,  // Fork bomb
      /mkfs/,               // Format disk
      /dd\s+if=.*of=\/dev\//  // Disk destroyer
    ];

    for (const pattern of maliciousPatterns) {
      if (pattern.test(intent.command)) {
        return {
          safe: false,
          reason: 'This command could harm your system',
          suggestion: 'Please reconsider this action'
        };
      }
    }

    // Check for missing parameters
    if (intent.command.includes('undefined') || intent.command.includes('null')) {
      return {
        safe: false,
        reason: 'Command is incomplete',
        suggestion: 'Please provide all required information'
      };
    }

    return { safe: true };
  }

  // Build the actual command from intent
  buildCommand(intent) {
    let command = intent.command;

    // Add parameters if present
    if (intent.package) {
      command += intent.package;
    }
    if (intent.service) {
      command += ` ${intent.service}`;
    }
    if (intent.path) {
      command += ` "${intent.path}"`;
    }
    if (intent.query) {
      command += ` "${intent.query}"`;
    }

    // Add safety flags
    if (this.safeMode && !intent.force) {
      // Add dry-run where applicable
      if (command.includes('nix-env -u')) {
        command += ' --dry-run';
      }
      if (command.includes('nix-collect-garbage')) {
        command = command.replace('-d', '--dry-run');
      }
    }

    return command;
  }

  // Check if command needs confirmation
  needsConfirmation(command, intent) {
    if (!this.requireConfirmation || intent.confirmed) {
      return false;
    }

    // Check if it's a dangerous command
    const baseCommand = command.split(' ')[0];
    if (this.dangerousCommands.has(command) || 
        this.dangerousCommands.has(baseCommand)) {
      return true;
    }

    // System modifications need confirmation
    if (command.includes('nixos-rebuild switch') ||
        command.includes('shutdown') ||
        command.includes('reboot')) {
      return true;
    }

    return false;
  }

  // Get appropriate warning message
  getWarningMessage(intent) {
    const warnings = {
      'shutdown': '⚠️ This will turn off your computer',
      'reboot': '⚠️ This will restart your computer',
      'nixos-rebuild switch': '⚠️ This will change your system configuration',
      'nix-collect-garbage -d': '⚠️ This will delete old system generations',
      'rm': '⚠️ This will permanently delete files'
    };

    const baseCommand = intent.command.split(' ')[0];
    return warnings[intent.command] || warnings[baseCommand] || 
           '⚠️ Please confirm this action';
  }

  // Execute command with care
  async executeWithCare(command, intent) {
    console.log(`🙏 Executing: ${command}`);
    console.log(`✨ Mantra: ${intent.mantra || 'Manifesting intention'}`);

    // Handle internal commands
    if (command.startsWith('internal:')) {
      return this.handleInternalCommand(command, intent);
    }

    // Check if sudo is needed
    const needsSudo = this.checkSudoRequired(command);
    if (needsSudo && !command.startsWith('sudo')) {
      return {
        success: false,
        error: 'This command requires administrator privileges',
        suggestion: 'Please run with sudo or provide your password'
      };
    }

    // Execute the command
    try {
      const { stdout, stderr } = await execAsync(command, {
        timeout: 30000, // 30 second timeout
        maxBuffer: 1024 * 1024 * 10 // 10MB buffer
      });

      return {
        success: true,
        output: stdout,
        error: stderr,
        command: command
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        code: error.code,
        command: command
      };
    }
  }

  // Check if command needs sudo
  checkSudoRequired(command) {
    const baseCommand = command.split(' ')[0].replace('sudo', '').trim();
    return this.sudoCommands.has(baseCommand);
  }

  // Handle internal commands (help, about, etc)
  handleInternalCommand(command, intent) {
    const action = command.replace('internal:', '');
    
    switch (action) {
      case 'help':
        return {
          success: true,
          output: this.getHelpText(),
          internal: true
        };
      
      case 'about':
        return {
          success: true,
          output: this.getAboutText(),
          internal: true
        };
      
      case 'gratitude':
        return {
          success: true,
          output: this.getGratitudeText(),
          internal: true
        };
      
      default:
        return {
          success: false,
          error: `Unknown internal command: ${action}`
        };
    }
  }

  // Format response with sacred touch
  formatResponse(result, intent) {
    if (result.internal) {
      return {
        success: true,
        message: result.output,
        mantra: intent.mantra || 'Sacred wisdom shared'
      };
    }

    if (result.success) {
      return {
        success: true,
        message: this.beautifyOutput(result.output, intent),
        rawOutput: result.output,
        error: result.error,
        mantra: intent.mantra || 'Intention manifested',
        command: result.command
      };
    }

    return {
      success: false,
      error: result.error,
      suggestion: this.getSuggestion(result.error),
      command: result.command,
      mantra: 'Learning through experience'
    };
  }

  // Beautify command output for humans
  beautifyOutput(output, intent) {
    if (!output || output.trim() === '') {
      return '✅ Command completed successfully';
    }

    // Package installation
    if (intent.action === 'install') {
      const lines = output.split('\n').filter(l => l.trim());
      const installed = lines.find(l => l.includes('installed'));
      if (installed) {
        return `✅ Successfully installed ${intent.package}`;
      }
    }

    // Service status - make it human readable
    if (intent.action === 'service-status') {
      if (output.includes('Active: active (running)')) {
        return `✅ ${intent.service} is running healthy`;
      } else if (output.includes('Active: inactive')) {
        return `⭕ ${intent.service} is not running`;
      }
    }

    // System info - extract key details
    if (intent.action === 'system-info') {
      const version = output.match(/(\d+\.\d+\.\w+)/);
      if (version) {
        return `🖥️ NixOS ${version[1]} - Your sacred system`;
      }
    }

    // Default: clean up output
    return output
      .split('\n')
      .filter(line => line.trim() && !line.includes('warning:'))
      .slice(0, 10)
      .join('\n');
  }

  // Handle errors with compassion
  handleErrorWithCompassion(error, intent) {
    const compassionateErrors = {
      'ENOENT': 'Command not found. Let me help you find the right one.',
      'EACCES': 'Permission needed. This action requires special privileges.',
      'ETIMEDOUT': 'This is taking longer than expected. Shall we try again?',
      'ENOTFOUND': 'Cannot find what you\'re looking for. Let\'s search together.'
    };

    return {
      success: false,
      error: compassionateErrors[error.code] || error.message,
      suggestion: this.getSuggestion(error.message),
      mantra: 'Every error is a teacher',
      command: intent.command
    };
  }

  // Get suggestions for common errors
  getSuggestion(error) {
    if (error.includes('not found')) {
      return 'Try searching for the package first with "search [name]"';
    }
    if (error.includes('permission') || error.includes('denied')) {
      return 'This action needs administrator privileges. Try with sudo.';
    }
    if (error.includes('network')) {
      return 'Check your internet connection and try again.';
    }
    if (error.includes('conflict')) {
      return 'There might be a version conflict. Try updating first.';
    }
    return 'Would you like to try a different approach?';
  }

  // Help text
  getHelpText() {
    return `🙏 Nix for Humanity - Sacred Commands

I understand natural language! Try:
• "install firefox" - Add new software
• "update system" - Keep everything current  
• "clean up" - Free disk space
• "what's installed" - See your programs
• "help with [topic]" - Get specific guidance

I'm here to make NixOS accessible to all beings. 
Speak naturally, and I'll understand. 🌟`;
  }

  // About text
  getAboutText() {
    return `🌟 Nix for Humanity v0.1.1

A sacred bridge between human intention and NixOS power.
Created with love to make declarative systems accessible to all.

• 50+ natural language commands
• Full accessibility support
• Privacy-first (100% local)
• Sacred mantras for each action

We believe technology should adapt to humans, not the other way around.

Built by Luminous-Dynamics with 💝`;
  }

  // Gratitude text
  getGratitudeText() {
    const gratitudes = [
      '🙏 Thank you for this sacred interaction',
      '✨ May your system run with grace and stability',
      '🌟 Grateful for this moment of co-creation',
      '💫 Your presence brings light to this digital space',
      '🌊 We flow together in the river of technology'
    ];
    
    return gratitudes[Math.floor(Math.random() * gratitudes.length)];
  }

  // Toggle safe mode
  setSafeMode(enabled) {
    this.safeMode = enabled;
    console.log(`🛡️ Safe mode: ${enabled ? 'ON' : 'OFF'}`);
  }

  // Set confirmation requirement
  setRequireConfirmation(enabled) {
    this.requireConfirmation = enabled;
    console.log(`✋ Confirmation required: ${enabled ? 'YES' : 'NO'}`);
  }
}

module.exports = SacredExecutor;