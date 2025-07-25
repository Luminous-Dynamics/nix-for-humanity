/**
 * Error Handler
 * Converts technical errors to user-friendly messages
 */
/**
 * Convert technical errors to user-friendly messages
 */
export function handleError(error, command) {
    // Network errors
    if (/network|connection|download|timeout/i.test(error)) {
        return {
            message: "I'm having trouble connecting to the internet.",
            suggestion: "Check your network connection and try again.",
            technicalDetails: error,
            canRetry: true
        };
    }
    // Package not found
    if (/attribute.*missing|package.*not found/i.test(error)) {
        const packageMatch = error.match(/attribute\s+'([^']+)'/);
        const packageName = packageMatch ? packageMatch[1] : 'that package';
        return {
            message: `I couldn't find ${packageName} in the package repository.`,
            suggestion: "Try searching for a similar package or check the spelling.",
            technicalDetails: error,
            canRetry: false
        };
    }
    // Permission denied
    if (/permission denied|unauthorized|sudo/i.test(error)) {
        return {
            message: "I need administrator privileges to do that.",
            suggestion: "Try running with sudo or as an administrator.",
            technicalDetails: error,
            canRetry: true
        };
    }
    // Disk space
    if (/no space|disk full/i.test(error)) {
        return {
            message: "Your disk is full and I can't complete this operation.",
            suggestion: "Free up some space and try again. You can use 'free up space' to clean old packages.",
            technicalDetails: error,
            canRetry: true
        };
    }
    // Already installed
    if (/already installed|collision between/i.test(error)) {
        return {
            message: "That package is already installed.",
            suggestion: "If you want to update it, try 'update [package]' instead.",
            technicalDetails: error,
            canRetry: false
        };
    }
    // Build failures
    if (/build.*failed|compilation error/i.test(error)) {
        return {
            message: "The package failed to build.",
            suggestion: "This might be a temporary issue. Try again later or check for known issues with this package.",
            technicalDetails: error,
            canRetry: true
        };
    }
    // Service errors
    if (/unit.*not found|service.*not found/i.test(error)) {
        const serviceMatch = error.match(/unit\s+(\S+)/);
        const serviceName = serviceMatch ? serviceMatch[1] : 'that service';
        return {
            message: `I couldn't find a service called ${serviceName}.`,
            suggestion: "Check the service name or try 'list services' to see what's available.",
            technicalDetails: error,
            canRetry: false
        };
    }
    // Configuration errors
    if (/syntax error|parse error/i.test(error)) {
        return {
            message: "There's a problem with your system configuration.",
            suggestion: "Check your configuration.nix file for syntax errors.",
            technicalDetails: error,
            canRetry: false
        };
    }
    // Rollback available
    if (/generation.*does not exist/i.test(error)) {
        return {
            message: "I couldn't find that system generation to rollback to.",
            suggestion: "Try 'list generations' to see available rollback points.",
            technicalDetails: error,
            canRetry: false
        };
    }
    // Generic command not found
    if (/command not found/i.test(error)) {
        return {
            message: "That command isn't available on your system.",
            suggestion: "The command might need to be installed first.",
            technicalDetails: error,
            canRetry: false
        };
    }
    // Default error
    return {
        message: "Something went wrong while executing that command.",
        suggestion: "Check the technical details below or try a simpler command.",
        technicalDetails: error,
        canRetry: true
    };
}
/**
 * Generate natural language response for errors
 */
export function formatErrorResponse(error) {
    let response = error.message;
    if (error.suggestion) {
        response += ` ${error.suggestion}`;
    }
    if (error.canRetry) {
        response += " Would you like me to try again?";
    }
    return response;
}
/**
 * Extract actionable steps from error
 */
export function getErrorRecoverySteps(error, originalCommand) {
    const steps = [];
    // Network errors
    if (error.message.includes('internet')) {
        steps.push('Check your network connection');
        steps.push('Try "check network status"');
        steps.push('Retry the command');
    }
    // Package not found
    else if (error.message.includes("couldn't find")) {
        steps.push('Search for similar packages');
        steps.push('Check spelling');
        steps.push('Try the official package name');
    }
    // Permission errors
    else if (error.message.includes('privileges')) {
        steps.push('Run with administrator privileges');
        steps.push('Check if you\'re in the right user group');
    }
    // Disk space
    else if (error.message.includes('disk is full')) {
        steps.push('Run "free up space"');
        steps.push('Check disk usage with "show disk space"');
        steps.push('Remove unused packages');
    }
    // Already installed
    else if (error.message.includes('already installed')) {
        steps.push('Check installed version with "show package info"');
        steps.push('Update instead with "update [package]"');
        steps.push('Remove first if you want to reinstall');
    }
    return steps;
}
/**
 * Common error patterns for quick detection
 */
export const ERROR_PATTERNS = {
    NETWORK: /curl.*failed|download.*failed|unable to download|connection.*refused/i,
    NOT_FOUND: /attribute.*missing|package.*not found|unknown package/i,
    PERMISSION: /permission denied|operation not permitted|access denied|needs sudo/i,
    DISK_SPACE: /no space left|disk full|out of space/i,
    ALREADY_EXISTS: /already installed|collision between|already exists/i,
    BUILD_FAIL: /build failed|compilation error|make.*error/i,
    SERVICE_NOT_FOUND: /unit.*not found|service.*not found|unknown service/i,
    SYNTAX_ERROR: /syntax error|parse error|unexpected/i,
    TIMEOUT: /timeout|timed out|took too long/i
};
/**
 * Check if error is recoverable
 */
export function isRecoverableError(error) {
    const recoverablePatterns = [
        ERROR_PATTERNS.NETWORK,
        ERROR_PATTERNS.PERMISSION,
        ERROR_PATTERNS.DISK_SPACE,
        ERROR_PATTERNS.TIMEOUT
    ];
    return recoverablePatterns.some(pattern => pattern.test(error));
}
//# sourceMappingURL=error-handler.js.map