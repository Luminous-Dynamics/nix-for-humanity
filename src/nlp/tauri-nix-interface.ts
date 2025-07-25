// Tauri-specific NixInterface wrapper
import { invoke } from '@tauri-apps/api/core';
import { recognizeIntent } from '../../implementations/web-based/js/nlp/layers/intent-recognition';
import { buildCommand } from '../../implementations/web-based/js/nlp/layers/command-builder';
import type { ProcessResult } from '../../implementations/web-based/js/nlp/nix-interface';

export class TauriNixInterface {
  /**
   * Process natural language input using Tauri IPC for execution
   */
  async processInput(input: string): Promise<ProcessResult> {
    try {
      // Layer 1: Intent Recognition (reuse from web implementation)
      const intent = recognizeIntent(input);
      
      if (intent.type === 'unknown') {
        return {
          success: false,
          response: "I didn't understand that. Try rephrasing it.",
        };
      }
      
      // Layer 2: Command Building (reuse from web implementation)
      const buildResult = buildCommand(intent);
      
      if (!buildResult.success || !buildResult.command) {
        return {
          success: false,
          response: buildResult.error || 'Could not create command',
        };
      }
      
      // Layer 3: Execute through Tauri IPC
      const result = await invoke<{
        success: boolean;
        output: string;
        error?: string;
      }>('execute_nix_command', {
        command: {
          command: buildResult.command.command,
          args: buildResult.command.args,
          dry_run: false
        }
      });
      
      if (result.success) {
        return {
          success: true,
          response: this.formatSuccessResponse(buildResult.command),
          command: buildResult.command,
          output: result.output
        };
      } else {
        return {
          success: false,
          response: `Command failed: ${result.error}`,
          error: result.error
        };
      }
    } catch (error) {
      return {
        success: false,
        response: "An error occurred while processing your request.",
        error: error instanceof Error ? error.message : String(error)
      };
    }
  }
  
  private formatSuccessResponse(command: any): string {
    const responses: Record<string, string> = {
      install: `Great! I've installed ${command.args[2]?.replace('nixpkgs.', '') || 'the package'} for you.`,
      remove: `I've removed ${command.args[1] || 'the package'} from your system.`,
      update: "Your system is now up to date!",
      query: "Here are your installed packages.",
      service: `Service operation completed successfully.`,
      maintenance: "I've cleaned up old packages and freed up disk space!",
    };
    
    return responses[command.type] || `Done! ${command.description} completed successfully.`;
  }
}