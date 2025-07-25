// 🌟 Tauri Sacred NixInterface - Bridging intention with manifestation
import { invoke } from '@tauri-apps/api/core';
import type { ProcessResult } from '../../implementations/web-based/js/nlp/nix-interface';

// Import our sacred intent engine
const SacredIntentEngine = require('../../implementations/nodejs-mvp/services/intent-engine-sacred');

interface SacredIntent {
  action: string;
  command: string;
  package?: string;
  service?: string;
  path?: string;
  query?: string;
  confidence: number;
  mantra: string;
  blessed: boolean;
}

interface SacredResult {
  success: boolean;
  message: string;
  output?: string;
  error?: string;
  mantra: string;
  requiresConfirmation?: boolean;
  warning?: string;
  command?: string;
}

export class TauriSacredInterface {
  private intentEngine: typeof SacredIntentEngine;
  
  constructor() {
    this.intentEngine = new SacredIntentEngine();
  }

  /**
   * Process natural language with sacred consciousness
   */
  async processInput(input: string): Promise<ProcessResult> {
    try {
      // Recognize sacred intent
      const intent: SacredIntent = await this.intentEngine.recognize(input);
      
      if (intent.action === 'unknown' || intent.confidence < 0.5) {
        return {
          success: false,
          response: "I'm not quite sure what you mean. Could you rephrase that?",
          mantra: intent.mantra || 'Every question is a path to understanding',
          suggestions: intent.suggestions
        };
      }
      
      // Check if this is an internal command
      if (intent.command.startsWith('internal:')) {
        return this.handleInternalCommand(intent);
      }
      
      // Build the actual command
      const nixCommand = this.buildNixCommand(intent);
      
      // Check if confirmation needed
      if (this.needsConfirmation(intent)) {
        return {
          success: false,
          requiresConfirmation: true,
          command: nixCommand,
          warning: this.getWarningMessage(intent),
          response: `⚠️ ${this.getWarningMessage(intent)}`,
          mantra: intent.mantra || 'Sacred boundaries protect us',
          intent: intent
        };
      }
      
      // Execute through Tauri IPC with sacred protection
      const result = await invoke<SacredResult>('execute_sacred_command', {
        command: nixCommand,
        intent: {
          action: intent.action,
          mantra: intent.mantra
        }
      });
      
      return {
        success: result.success,
        response: result.message,
        mantra: result.mantra || intent.mantra,
        output: result.output,
        error: result.error
      };
      
    } catch (error) {
      return {
        success: false,
        response: "An error occurred while processing your sacred request.",
        error: error instanceof Error ? error.message : String(error),
        mantra: 'Every error is a teacher'
      };
    }
  }
  
  /**
   * Execute a confirmed command
   */
  async executeConfirmed(intent: SacredIntent): Promise<ProcessResult> {
    const nixCommand = this.buildNixCommand(intent);
    
    const result = await invoke<SacredResult>('execute_sacred_command', {
      command: nixCommand,
      intent: {
        action: intent.action,
        mantra: intent.mantra,
        confirmed: true
      }
    });
    
    return {
      success: result.success,
      response: result.message,
      mantra: result.mantra || 'Mindful action manifested',
      output: result.output,
      error: result.error
    };
  }
  
  private buildNixCommand(intent: SacredIntent): any {
    let command = intent.command;
    const args: string[] = [];
    
    // Parse command and args
    const parts = command.split(' ');
    const baseCommand = parts[0];
    args.push(...parts.slice(1));
    
    // Add package/service/path/query parameters
    if (intent.package) {
      args.push(intent.package);
    }
    if (intent.service) {
      args.push(intent.service);
    }
    if (intent.path) {
      args.push(intent.path);
    }
    if (intent.query) {
      args.push(intent.query);
    }
    
    return {
      command: baseCommand,
      args: args,
      dry_run: false,
      action: intent.action,
      mantra: intent.mantra
    };
  }
  
  private handleInternalCommand(intent: SacredIntent): ProcessResult {
    const action = intent.command.replace('internal:', '');
    
    switch (action) {
      case 'help':
        return {
          success: true,
          response: this.getHelpText(),
          mantra: intent.mantra || 'Offering guidance'
        };
        
      case 'about':
        return {
          success: true,
          response: this.getAboutText(),
          mantra: intent.mantra || 'Sharing our essence'
        };
        
      case 'gratitude':
        return {
          success: true,
          response: this.getGratitudeText(),
          mantra: intent.mantra || 'Completing the sacred circle'
        };
        
      default:
        return {
          success: false,
          response: `Unknown internal command: ${action}`,
          mantra: 'Learning together'
        };
    }
  }
  
  private needsConfirmation(intent: SacredIntent): boolean {
    const dangerousActions = [
      'shutdown', 'reboot', 'garbage-collect',
      'rebuild', 'kill-process'
    ];
    
    const dangerousCommands = [
      'rm', 'shutdown', 'reboot', 'nixos-rebuild switch',
      'nix-collect-garbage -d'
    ];
    
    return dangerousActions.includes(intent.action) ||
           dangerousCommands.some(cmd => intent.command.includes(cmd));
  }
  
  private getWarningMessage(intent: SacredIntent): string {
    const warnings: Record<string, string> = {
      'shutdown': 'This will turn off your computer',
      'reboot': 'This will restart your computer',
      'rebuild': 'This will change your system configuration',
      'garbage-collect': 'This will delete old system generations',
      'remove': 'This will uninstall software',
      'kill-process': 'This will force-stop a running program'
    };
    
    return warnings[intent.action] || 'This action requires confirmation';
  }
  
  private getHelpText(): string {
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
  
  private getAboutText(): string {
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
  
  private getGratitudeText(): string {
    const gratitudes = [
      '🙏 Thank you for this sacred interaction',
      '✨ May your system run with grace and stability',
      '🌟 Grateful for this moment of co-creation',
      '💫 Your presence brings light to this digital space',
      '🌊 We flow together in the river of technology'
    ];
    
    return gratitudes[Math.floor(Math.random() * gratitudes.length)];
  }
}