/**
 * Command Sandbox
 * Provides secure execution environment for system commands
 */
export interface SandboxOptions {
    maxExecutionTime?: number;
    maxMemory?: number;
    maxOutputSize?: number;
    allowNetwork?: boolean;
    allowFileWrite?: boolean;
    workingDirectory?: string;
}
export interface SandboxResult {
    success: boolean;
    stdout: string;
    stderr: string;
    exitCode: number | null;
    executionTime: number;
    sanitizedCommand: string;
}
export declare class CommandSandbox {
    private readonly defaultOptions;
    /**
     * Create a temporary sandbox directory
     */
    private createSandboxDir;
    /**
     * Clean up sandbox directory
     */
    private cleanupSandboxDir;
    /**
     * Execute command in sandbox
     */
    execute(command: string, args: string[], options?: SandboxOptions): Promise<SandboxResult>;
    /**
     * Execute command with restrictions
     */
    private executeWithRestrictions;
    /**
     * Build sandbox environment variables
     */
    private buildSandboxEnvironment;
    /**
     * Sanitize command for safe logging
     */
    private sanitizeCommand;
    /**
     * Validate command is safe to execute
     */
    validateCommand(command: string, args: string[]): {
        safe: boolean;
        reason?: string;
    };
}
export declare const commandSandbox: CommandSandbox;
