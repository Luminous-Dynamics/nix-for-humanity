/**
 * Error Recovery System for Nix for Humanity
 * Turns errors into teaching moments
 */
export interface ErrorContext {
    errorType: ErrorType;
    command?: string;
    userInput: string;
    errorMessage: string;
    timestamp: number;
}
export type ErrorType = 'command_failed' | 'package_not_found' | 'permission_denied' | 'network_error' | 'dependency_conflict' | 'disk_space' | 'syntax_error' | 'unknown';
export interface RecoveryStrategy {
    explanation: string;
    suggestions: RecoverySuggestion[];
    learnMore?: string;
}
export interface RecoverySuggestion {
    action: string;
    command?: string;
    confidence: number;
    requiresConfirmation: boolean;
}
export declare class ErrorRecoverySystem {
    private errorHistory;
    /**
     * Analyze error and provide recovery strategies
     */
    analyzeError(error: ErrorContext): RecoveryStrategy;
    /**
     * Detect error type from message
     */
    private detectErrorType;
    /**
     * Recovery for package not found errors
     */
    private recoverFromPackageNotFound;
    /**
     * Recovery for permission denied errors
     */
    private recoverFromPermissionDenied;
    /**
     * Recovery for network errors
     */
    private recoverFromNetworkError;
    /**
     * Recovery for dependency conflicts
     */
    private recoverFromDependencyConflict;
    /**
     * Recovery for disk space errors
     */
    private recoverFromDiskSpace;
    /**
     * Recovery for generic command failures
     */
    private recoverFromCommandFailed;
    /**
     * Generic recovery strategy
     */
    private genericRecovery;
    /**
     * Extract package name from user input
     */
    private extractPackageName;
    /**
     * Learn from successful recoveries
     */
    recordSuccessfulRecovery(error: ErrorContext, suggestion: RecoverySuggestion): void;
    /**
     * Get common errors for proactive help
     */
    getCommonErrors(): ErrorPattern[];
}
interface ErrorPattern {
    errorType: ErrorType;
    command?: string;
    frequency: number;
    lastSeen: number;
}
export declare const errorRecovery: ErrorRecoverySystem;
export {};
