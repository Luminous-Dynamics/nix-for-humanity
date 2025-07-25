// Tauri-specific command executor that uses IPC
import { invoke } from '@tauri-apps/api/core';
import type { NixCommand } from '../../implementations/web-based/js/nlp/layers/command-builder';
import type { ExecutionOptions, ExecutionResult } from '../../implementations/web-based/js/nlp/layers/command-executor';

/**
 * Execute command through Tauri IPC instead of direct execution
 */
export async function executeTauriCommand(
  command: NixCommand,
  options: ExecutionOptions = {}
): Promise<ExecutionResult> {
  const startTime = Date.now();
  
  try {
    // Use Tauri's IPC to execute commands through Rust backend
    const result = await invoke<{
      success: boolean;
      output: string;
      error?: string;
    }>('execute_nix_command', {
      command: {
        command: command.command,
        args: command.args,
        dry_run: options.dryRun || false
      }
    });

    return {
      success: result.success,
      output: result.output,
      error: result.error,
      duration: Date.now() - startTime,
      rollbackAvailable: false // TODO: Implement rollback in Rust
    };
  } catch (error) {
    return {
      success: false,
      output: '',
      error: error instanceof Error ? error.message : String(error),
      duration: Date.now() - startTime,
      rollbackAvailable: false
    };
  }
}