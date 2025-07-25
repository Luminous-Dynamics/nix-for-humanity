/**
 * Safety Validator for Nix for Humanity
 * Ensures all commands are safe before execution
 */
export interface SafetyCheck {
    isSafe: boolean;
    reason?: string;
    suggestion?: string;
}
/**
 * Comprehensive safety validation for Nix commands
 */
export declare class SafetyValidator {
    private readonly dangerousPatterns;
    private readonly safeCommands;
    private readonly safeOperations;
    /**
     * Validate a command for safety
     */
    validateCommand(command: string, args: string[]): SafetyCheck;
    /**
     * Validate package name
     */
    validatePackageName(packageName: string): SafetyCheck;
    /**
     * Validate file path for operations
     */
    validatePath(path: string): SafetyCheck;
    /**
     * Get safety explanation for users
     */
    explainSafety(command: string): string;
}
export declare const safetyValidator: SafetyValidator;
