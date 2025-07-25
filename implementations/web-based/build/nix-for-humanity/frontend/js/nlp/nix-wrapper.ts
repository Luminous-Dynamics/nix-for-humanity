/**
 * Safe Nix Command Wrapper
 * Executes Nix commands with rollback capability and safety checks
 */

import { Intent, Entity } from './intent-engine';

export interface NixCommand {
  command: string;
  args: string[];
  requiresSudo: boolean;
  description: string;
  rollbackCommand?: string;
}

export interface ExecutionResult {
  success: boolean;
  output: string;
  error?: string;
  rollbackAvailable: boolean;
  naturalLanguageResponse: string;
}

/**
 * Safe wrapper for Nix command execution
 */
export class NixSafeWrapper {
  private commandHistory: NixCommand[] = [];
  private currentGeneration: number = 0;

  /**
   * Convert intent to safe Nix command
   */
  intentToCommand(intent: Intent): NixCommand | null {
    switch (intent.type) {
      case 'install':
        return this.createInstallCommand(intent.entities);
      
      case 'update':
        return this.createUpdateCommand();
      
      case 'query':
        return this.createQueryCommand(intent.entities);
      
      case 'troubleshoot':
        return this.createTroubleshootCommand(intent.entities);
      
      case 'config':
        return this.createConfigCommand(intent.entities);
      
      default:
        return null;
    }
  }

  /**
   * Execute command with safety checks
   */
  async execute(command: NixCommand): Promise<ExecutionResult> {
    try {
      // 1. Validate command safety
      if (!this.validateCommand(command)) {
        return {
          success: false,
          output: '',
          error: 'Command failed safety validation',
          rollbackAvailable: false,
          naturalLanguageResponse: "I can't run that command because it might not be safe. Let me know what you're trying to do and I'll help find a safe way."
        };
      }

      // 2. Create rollback point
      const rollbackPoint = await this.createRollbackPoint();

      // 3. Execute command (simulation for now)
      const result = await this.simulateExecution(command);

      // 4. Verify success
      if (result.success) {
        this.commandHistory.push(command);
        return {
          ...result,
          rollbackAvailable: true,
          naturalLanguageResponse: this.generateSuccessResponse(command, result)
        };
      } else {
        // Auto-rollback on failure
        await this.rollback(rollbackPoint);
        return {
          ...result,
          rollbackAvailable: false,
          naturalLanguageResponse: this.generateErrorResponse(command, result)
        };
      }
    } catch (error) {
      return {
        success: false,
        output: '',
        error: error instanceof Error ? error.message : 'Unknown error',
        rollbackAvailable: false,
        naturalLanguageResponse: "Something unexpected happened. Let me try a different approach."
      };
    }
  }

  /**
   * Create install command
   */
  private createInstallCommand(entities: Entity[]): NixCommand | null {
    const packageEntity = entities.find(e => e.type === 'package');
    if (!packageEntity) return null;

    return {
      command: 'nix-env',
      args: ['-iA', `nixpkgs.${packageEntity.value}`],
      requiresSudo: false,
      description: `Install ${packageEntity.value}`,
      rollbackCommand: 'nix-env --rollback'
    };
  }

  /**
   * Create update command
   */
  private createUpdateCommand(): NixCommand {
    return {
      command: 'sudo',
      args: ['nixos-rebuild', 'switch', '--upgrade'],
      requiresSudo: true,
      description: 'Update system',
      rollbackCommand: 'sudo nixos-rebuild switch --rollback'
    };
  }

  /**
   * Create query command
   */
  private createQueryCommand(entities: Entity[]): NixCommand {
    return {
      command: 'nix-env',
      args: ['-q'],
      requiresSudo: false,
      description: 'List installed packages'
    };
  }

  /**
   * Create troubleshooting command
   */
  private createTroubleshootCommand(entities: Entity[]): NixCommand | null {
    const problemEntity = entities.find(e => e.type === 'problem');
    if (!problemEntity) return null;

    switch (problemEntity.value) {
      case 'network':
        return {
          command: 'systemctl',
          args: ['status', 'NetworkManager'],
          requiresSudo: false,
          description: 'Check network status'
        };
      
      case 'audio':
        return {
          command: 'pactl',
          args: ['info'],
          requiresSudo: false,
          description: 'Check audio system'
        };
      
      case 'display':
        return {
          command: 'xrandr',
          args: [],
          requiresSudo: false,
          description: 'Check display configuration'
        };
      
      default:
        return null;
    }
  }

  /**
   * Create configuration command
   */
  private createConfigCommand(entities: Entity[]): NixCommand | null {
    const settingEntity = entities.find(e => e.type === 'setting');
    if (!settingEntity) return null;

    if (settingEntity.value === 'font-size') {
      return {
        command: 'gsettings',
        args: ['set', 'org.gnome.desktop.interface', 'text-scaling-factor', '1.2'],
        requiresSudo: false,
        description: 'Increase font size'
      };
    }

    return null;
  }

  /**
   * Validate command safety
   */
  private validateCommand(command: NixCommand): boolean {
    // Whitelist of safe commands
    const safeCommands = [
      'nix-env', 'nixos-rebuild', 'systemctl', 
      'pactl', 'xrandr', 'gsettings', 'nix-store'
    ];

    const baseCommand = command.command === 'sudo' ? command.args[0] : command.command;
    return safeCommands.includes(baseCommand);
  }

  /**
   * Create rollback point
   */
  private async createRollbackPoint(): Promise<number> {
    // In real implementation, would get current generation
    this.currentGeneration++;
    return this.currentGeneration;
  }

  /**
   * Rollback to previous state
   */
  private async rollback(generation: number): Promise<void> {
    // In real implementation, would execute rollback
    console.log(`Rolling back to generation ${generation}`);
  }

  /**
   * Simulate command execution (for MVP)
   */
  private async simulateExecution(command: NixCommand): Promise<Omit<ExecutionResult, 'naturalLanguageResponse'>> {
    // Simulate some common scenarios
    if (command.command === 'nix-env' && command.args[0] === '-iA') {
      const packageName = command.args[1].replace('nixpkgs.', '');
      return {
        success: true,
        output: `installing '${packageName}'\nbuilding...\ninstalled successfully`,
        rollbackAvailable: true
      };
    }

    if (command.command === 'nix-env' && command.args[0] === '-q') {
      return {
        success: true,
        output: 'firefox-120.0\nvscode-1.85.0\ngit-2.42.0',
        rollbackAvailable: false
      };
    }

    return {
      success: true,
      output: 'Command executed successfully',
      rollbackAvailable: false
    };
  }

  /**
   * Generate natural language success response
   */
  private generateSuccessResponse(command: NixCommand, result: any): string {
    if (command.description.includes('Install')) {
      const pkg = command.description.replace('Install ', '');
      return `Great! I've installed ${pkg} for you. You can find it in your applications menu.`;
    }

    if (command.description.includes('Update')) {
      return `Your system is now up to date! All packages have been upgraded to their latest versions.`;
    }

    if (command.description.includes('List')) {
      const packages = result.output.split('\n').filter(Boolean);
      return `You have ${packages.length} packages installed. Here are some of them: ${packages.slice(0, 3).join(', ')}...`;
    }

    return `Done! ${command.description} completed successfully.`;
  }

  /**
   * Generate natural language error response
   */
  private generateErrorResponse(command: NixCommand, result: any): string {
    if (command.description.includes('Install')) {
      return `I couldn't install that package. It might not be available or there was a network issue. Would you like me to search for similar packages?`;
    }

    return `I ran into a problem: ${result.error}. Don't worry, I've undone any changes. Let's try a different approach.`;
  }

  /**
   * Get rollback options
   */
  getRollbackOptions(): string[] {
    return this.commandHistory
      .filter(cmd => cmd.rollbackCommand)
      .map(cmd => cmd.description);
  }
}

// Export singleton instance
export const nixWrapper = new NixSafeWrapper();