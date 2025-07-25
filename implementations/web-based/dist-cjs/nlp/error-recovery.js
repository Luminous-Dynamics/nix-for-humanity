/**
 * Error Recovery System for Nix for Humanity
 * Turns errors into teaching moments
 */
export class ErrorRecoverySystem {
    constructor() {
        this.errorHistory = [];
    }
    /**
     * Analyze error and provide recovery strategies
     */
    analyzeError(error) {
        // Record error for pattern analysis
        this.errorHistory.push(error);
        // Detect error type if not provided
        if (error.errorType === 'unknown') {
            error.errorType = this.detectErrorType(error.errorMessage);
        }
        // Generate recovery strategy based on error type
        switch (error.errorType) {
            case 'package_not_found':
                return this.recoverFromPackageNotFound(error);
            case 'permission_denied':
                return this.recoverFromPermissionDenied(error);
            case 'network_error':
                return this.recoverFromNetworkError(error);
            case 'dependency_conflict':
                return this.recoverFromDependencyConflict(error);
            case 'disk_space':
                return this.recoverFromDiskSpace(error);
            case 'command_failed':
                return this.recoverFromCommandFailed(error);
            default:
                return this.genericRecovery(error);
        }
    }
    /**
     * Detect error type from message
     */
    detectErrorType(errorMessage) {
        const message = errorMessage.toLowerCase();
        if (message.includes('not found') || message.includes('no such package')) {
            return 'package_not_found';
        }
        if (message.includes('permission denied') || message.includes('operation not permitted')) {
            return 'permission_denied';
        }
        if (message.includes('network') || message.includes('connection') || message.includes('timeout')) {
            return 'network_error';
        }
        if (message.includes('conflict') || message.includes('dependency')) {
            return 'dependency_conflict';
        }
        if (message.includes('disk space') || message.includes('no space left')) {
            return 'disk_space';
        }
        return 'unknown';
    }
    /**
     * Recovery for package not found errors
     */
    recoverFromPackageNotFound(error) {
        const packageName = this.extractPackageName(error.userInput);
        return {
            explanation: `I couldn't find a package called "${packageName}". This might be because:
• The package name is slightly different in NixOS
• The package is in a different channel
• There's a typo in the name`,
            suggestions: [
                {
                    action: `Search for similar packages`,
                    command: `nix search ${packageName}`,
                    confidence: 0.9,
                    requiresConfirmation: false
                },
                {
                    action: `Try common alternatives`,
                    confidence: 0.8,
                    requiresConfirmation: true
                },
                {
                    action: `Update package channels`,
                    command: 'sudo nix-channel --update',
                    confidence: 0.7,
                    requiresConfirmation: true
                }
            ],
            learnMore: `Package names in NixOS can be different from other distributions. For example, "google-chrome" might be "google-chrome-stable".`
        };
    }
    /**
     * Recovery for permission denied errors
     */
    recoverFromPermissionDenied(error) {
        const needsSudo = error.command && !error.command.startsWith('sudo');
        return {
            explanation: `This operation requires administrator privileges. ${needsSudo ? 'I need to run this with sudo.' : 'Even with sudo, this action was blocked.'}`,
            suggestions: needsSudo ? [
                {
                    action: `Run with administrator privileges`,
                    command: `sudo ${error.command}`,
                    confidence: 0.95,
                    requiresConfirmation: true
                }
            ] : [
                {
                    action: `Check if you're in the right user group`,
                    command: 'groups',
                    confidence: 0.7,
                    requiresConfirmation: false
                },
                {
                    action: `Check file permissions`,
                    confidence: 0.6,
                    requiresConfirmation: false
                }
            ],
            learnMore: `Some operations in NixOS require root privileges. I'll always ask for confirmation before using sudo.`
        };
    }
    /**
     * Recovery for network errors
     */
    recoverFromNetworkError(error) {
        return {
            explanation: `There seems to be a network issue. This could be:
• No internet connection
• DNS problems
• Firewall blocking the connection
• The remote server is down`,
            suggestions: [
                {
                    action: `Check internet connection`,
                    command: 'ping -c 3 google.com',
                    confidence: 0.9,
                    requiresConfirmation: false
                },
                {
                    action: `Check DNS resolution`,
                    command: 'nslookup nixos.org',
                    confidence: 0.8,
                    requiresConfirmation: false
                },
                {
                    action: `Restart network service`,
                    command: 'sudo systemctl restart NetworkManager',
                    confidence: 0.7,
                    requiresConfirmation: true
                },
                {
                    action: `Try using a different DNS`,
                    confidence: 0.6,
                    requiresConfirmation: true
                }
            ],
            learnMore: `Network issues can often be fixed by restarting the NetworkManager service or checking your DNS settings.`
        };
    }
    /**
     * Recovery for dependency conflicts
     */
    recoverFromDependencyConflict(error) {
        return {
            explanation: `There's a conflict between packages. This happens when:
• Two packages need different versions of the same dependency
• A package conflicts with something already installed
• The system profile has inconsistencies`,
            suggestions: [
                {
                    action: `Try installing in a user profile instead`,
                    command: error.command?.replace('sudo ', ''),
                    confidence: 0.8,
                    requiresConfirmation: true
                },
                {
                    action: `Check for conflicting packages`,
                    command: 'nix-env -q',
                    confidence: 0.7,
                    requiresConfirmation: false
                },
                {
                    action: `Use nix-shell for isolated environment`,
                    confidence: 0.9,
                    requiresConfirmation: false
                },
                {
                    action: `Garbage collect and retry`,
                    command: 'nix-collect-garbage',
                    confidence: 0.6,
                    requiresConfirmation: true
                }
            ],
            learnMore: `NixOS prevents conflicts by design. Sometimes using nix-shell or separate profiles can help isolate problematic packages.`
        };
    }
    /**
     * Recovery for disk space errors
     */
    recoverFromDiskSpace(error) {
        return {
            explanation: `You're running low on disk space. NixOS keeps old versions of packages for rollback, which can use significant space.`,
            suggestions: [
                {
                    action: `Check disk usage`,
                    command: 'df -h',
                    confidence: 0.95,
                    requiresConfirmation: false
                },
                {
                    action: `Clean up old generations`,
                    command: 'sudo nix-collect-garbage -d',
                    confidence: 0.9,
                    requiresConfirmation: true
                },
                {
                    action: `Remove old system profiles`,
                    command: 'sudo nix-collect-garbage --delete-old',
                    confidence: 0.85,
                    requiresConfirmation: true
                },
                {
                    action: `Check what's using space`,
                    command: 'du -sh /nix/store/* | sort -h | tail -20',
                    confidence: 0.7,
                    requiresConfirmation: false
                }
            ],
            learnMore: `NixOS stores all packages in /nix/store. Running garbage collection regularly helps manage disk space.`
        };
    }
    /**
     * Recovery for generic command failures
     */
    recoverFromCommandFailed(error) {
        return {
            explanation: `The command didn't work as expected. Let me help you troubleshoot.`,
            suggestions: [
                {
                    action: `Check the exact error message`,
                    confidence: 0.8,
                    requiresConfirmation: false
                },
                {
                    action: `Try a simpler version of the command`,
                    confidence: 0.7,
                    requiresConfirmation: true
                },
                {
                    action: `Look for alternative approaches`,
                    confidence: 0.6,
                    requiresConfirmation: false
                }
            ]
        };
    }
    /**
     * Generic recovery strategy
     */
    genericRecovery(error) {
        return {
            explanation: `Something went wrong, but I'm not sure exactly what. Here are some general troubleshooting steps:`,
            suggestions: [
                {
                    action: `Check system logs`,
                    command: 'journalctl -xe',
                    confidence: 0.6,
                    requiresConfirmation: false
                },
                {
                    action: `Try the command with verbose output`,
                    confidence: 0.5,
                    requiresConfirmation: true
                },
                {
                    action: `Search for this error online`,
                    confidence: 0.7,
                    requiresConfirmation: false
                }
            ],
            learnMore: `When in doubt, the NixOS manual and community forums are great resources for troubleshooting.`
        };
    }
    /**
     * Extract package name from user input
     */
    extractPackageName(input) {
        const patterns = [
            /install\s+(\S+)/i,
            /package\s+(\S+)/i,
            /get\s+(\S+)/i,
            /need\s+(\S+)/i
        ];
        for (const pattern of patterns) {
            const match = input.match(pattern);
            if (match)
                return match[1];
        }
        return 'the package';
    }
    /**
     * Learn from successful recoveries
     */
    recordSuccessfulRecovery(error, suggestion) {
        // In a real implementation, this would update confidence scores
        console.log('Recording successful recovery:', { error, suggestion });
    }
    /**
     * Get common errors for proactive help
     */
    getCommonErrors() {
        const patterns = new Map();
        this.errorHistory.forEach(error => {
            const key = `${error.errorType}:${error.command || 'unknown'}`;
            const existing = patterns.get(key);
            if (existing) {
                existing.frequency++;
                existing.lastSeen = error.timestamp;
            }
            else {
                patterns.set(key, {
                    errorType: error.errorType,
                    command: error.command,
                    frequency: 1,
                    lastSeen: error.timestamp
                });
            }
        });
        return Array.from(patterns.values())
            .sort((a, b) => b.frequency - a.frequency)
            .slice(0, 10);
    }
}
// Export singleton
export const errorRecovery = new ErrorRecoverySystem();
//# sourceMappingURL=error-recovery.js.map