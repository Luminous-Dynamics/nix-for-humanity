/**
 * Unsupported Command Handler
 * Logs unrecognized commands for future pattern learning
 */
import { Intent } from './intent-engine';
export interface UnsupportedCommand {
    input: string;
    timestamp: Date;
    confidence: number;
    suggestedIntent?: string;
}
export interface CommandLog {
    commands: UnsupportedCommand[];
    totalCount: number;
    uniqueCount: number;
    topPatterns: {
        pattern: string;
        count: number;
    }[];
}
/**
 * Privacy-preserving handler for unsupported commands
 */
export declare class UnsupportedCommandHandler {
    private unsupportedLog;
    private readonly maxLogSize;
    private readonly sessionId;
    /**
     * Handle an unsupported command
     */
    handleUnsupported(input: string, intent: Intent): UnsupportedCommand;
    /**
     * Get natural language response for unsupported command
     */
    getResponse(command: UnsupportedCommand): string;
    /**
     * Sanitize input to remove personal information
     */
    private sanitizeInput;
    /**
     * Try to suggest what the user might have meant
     */
    private suggestIntent;
    /**
     * Save to local storage (privacy-preserving)
     */
    private saveToLocalStorage;
    /**
     * Get analytics about unsupported commands
     */
    getAnalytics(): CommandLog;
    /**
     * Export anonymous analytics (for improving patterns)
     */
    exportAnonymousPatterns(): string;
    /**
     * Clear the log (user privacy control)
     */
    clearLog(): void;
    /**
     * Get user-friendly suggestions for common mistakes
     */
    getSuggestions(): string[];
}
export declare const unsupportedHandler: UnsupportedCommandHandler;
