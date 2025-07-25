/**
 * Nix Interface - Main Entry Point
 * Ties together all layers of the refactored architecture
 */
import { ExecutionOptions } from './layers/command-executor';
export interface ProcessResult {
    success: boolean;
    response: string;
    command?: string;
    output?: string;
    error?: string;
    suggestions?: string[];
    duration?: number;
}
export declare class NixInterface {
    private executionOptions;
    /**
     * Process natural language input
     */
    processInput(input: string): Promise<ProcessResult>;
    /**
     * Check if input is a special command
     */
    private isSpecialCommand;
    /**
     * Handle special commands
     */
    private handleSpecialCommand;
    /**
     * Check if input is a batch operation
     */
    private isBatchOperation;
    /**
     * Process batch operation
     */
    private processBatchOperation;
    /**
     * Handle undo command
     */
    private handleUndo;
    /**
     * Handle history command
     */
    private handleHistory;
    /**
     * Handle help command
     */
    private handleHelp;
    /**
     * Handle stats command
     */
    private handleStats;
    /**
     * Format success response
     */
    private formatSuccessResponse;
    /**
     * Get autocomplete suggestions
     */
    getSuggestions(partial: string): string[];
    /**
     * Set execution options
     */
    setOptions(options: Partial<ExecutionOptions>): void;
    /**
     * Get current options
     */
    getOptions(): ExecutionOptions;
}
export declare const nixInterface: NixInterface;
