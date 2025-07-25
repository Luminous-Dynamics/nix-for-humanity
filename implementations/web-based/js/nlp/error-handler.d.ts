/**
 * Error Handler
 * Converts technical errors to user-friendly messages
 */
export interface UserFriendlyError {
    message: string;
    suggestion?: string;
    technicalDetails?: string;
    canRetry: boolean;
}
/**
 * Convert technical errors to user-friendly messages
 */
export declare function handleError(error: string, command?: string): UserFriendlyError;
/**
 * Generate natural language response for errors
 */
export declare function formatErrorResponse(error: UserFriendlyError): string;
/**
 * Extract actionable steps from error
 */
export declare function getErrorRecoverySteps(error: UserFriendlyError, originalCommand?: string): string[];
/**
 * Common error patterns for quick detection
 */
export declare const ERROR_PATTERNS: {
    NETWORK: RegExp;
    NOT_FOUND: RegExp;
    PERMISSION: RegExp;
    DISK_SPACE: RegExp;
    ALREADY_EXISTS: RegExp;
    BUILD_FAIL: RegExp;
    SERVICE_NOT_FOUND: RegExp;
    SYNTAX_ERROR: RegExp;
    TIMEOUT: RegExp;
};
/**
 * Check if error is recoverable
 */
export declare function isRecoverableError(error: string): boolean;
