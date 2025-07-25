/**
 * Safe Nix Command Wrapper
 * Executes Nix commands with rollback capability and safety checks
 */
import { Intent } from './intent-engine';
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
export declare class NixSafeWrapper {
    private commandHistory;
    private currentGeneration;
    /**
     * Convert intent to safe Nix command
     */
    intentToCommand(intent: Intent): NixCommand | null;
    /**
     * Execute command with safety checks
     */
    execute(command: NixCommand): Promise<ExecutionResult>;
    /**
     * Create install command
     */
    private createInstallCommand;
    /**
     * Create update command
     */
    private createUpdateCommand;
    /**
     * Create query command
     */
    private createQueryCommand;
    /**
     * Create troubleshooting command
     */
    private createTroubleshootCommand;
    /**
     * Create configuration command
     */
    private createConfigCommand;
    /**
     * Create maintenance command (garbage collection, cleanup)
     */
    private createMaintenanceCommand;
    /**
     * Create logs viewing command
     */
    private createLogsCommand;
    /**
     * Create service management command
     */
    private createServiceCommand;
    /**
     * Validate command safety
     */
    private validateCommand;
    /**
     * Create rollback point
     */
    private createRollbackPoint;
    /**
     * Rollback to previous state
     */
    private rollback;
    /**
     * Simulate command execution (for MVP)
     */
    private simulateExecution;
    /**
     * Generate natural language success response
     */
    private generateSuccessResponse;
    /**
     * Generate natural language error response
     */
    private generateErrorResponse;
    /**
     * Get rollback options
     */
    getRollbackOptions(): string[];
    /**
     * Get intent type from command for tracking
     */
    private getIntentTypeFromCommand;
}
export declare const nixWrapper: NixSafeWrapper;
