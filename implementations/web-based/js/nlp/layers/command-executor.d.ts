/**
 * Command Executor Layer
 * Handles actual command execution with safety options
 */
import { NixCommand } from './command-builder';
export interface ExecutionOptions {
    dryRun?: boolean;
    requireConfirmation?: boolean;
    timeout?: number;
    streamOutput?: boolean;
    onProgress?: (output: string) => void;
}
export interface ExecutionResult {
    success: boolean;
    output: string;
    error?: string;
    exitCode?: number;
    duration: number;
    wasCancelled?: boolean;
    rollbackAvailable: boolean;
}
/**
 * Execute NixOS command with safety options
 * This is the ONLY place where actual execution happens
 */
export declare function executeCommand(command: NixCommand, options?: ExecutionOptions): Promise<ExecutionResult>;
/**
 * Execute rollback command
 */
export declare function executeRollback(originalCommand: NixCommand, options?: ExecutionOptions): Promise<ExecutionResult>;
/**
 * Stream command output in real-time
 */
export declare function createOutputStreamer(onData: (chunk: string) => void, onComplete: () => void): (output: string) => void;
