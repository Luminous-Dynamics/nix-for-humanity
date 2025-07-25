/**
 * Unsupported Command Handler
 * Logs unrecognized commands for future pattern learning
 */
/**
 * Privacy-preserving handler for unsupported commands
 */
export class UnsupportedCommandHandler {
    constructor() {
        this.unsupportedLog = [];
        this.maxLogSize = 1000;
        this.sessionId = Date.now().toString(36);
    }
    /**
     * Handle an unsupported command
     */
    handleUnsupported(input, intent) {
        const command = {
            input: this.sanitizeInput(input),
            timestamp: new Date(),
            confidence: intent.confidence,
            suggestedIntent: this.suggestIntent(input)
        };
        // Add to log (FIFO if full)
        if (this.unsupportedLog.length >= this.maxLogSize) {
            this.unsupportedLog.shift();
        }
        this.unsupportedLog.push(command);
        // Save to local storage (privacy-preserving)
        this.saveToLocalStorage();
        return command;
    }
    /**
     * Get natural language response for unsupported command
     */
    getResponse(command) {
        const responses = [
            "I didn't understand that. Could you try saying it differently?",
            "I'm not sure what you mean. Can you rephrase that?",
            "That's not something I know how to do yet. What are you trying to accomplish?",
            "I haven't learned that command yet. Could you describe what you want to do?"
        ];
        // Add suggestion if we have one
        if (command.suggestedIntent) {
            const suggestionResponses = {
                install: "Did you want to install something? Try 'install [package name]'",
                update: "Did you want to update your system? Try 'update system'",
                troubleshoot: "Are you having a problem? Try describing what's not working",
                config: "Did you want to change a setting? Try 'make text bigger' or similar"
            };
            const suggestion = suggestionResponses[command.suggestedIntent];
            if (suggestion) {
                return responses[0] + " " + suggestion;
            }
        }
        return responses[Math.floor(Math.random() * responses.length)];
    }
    /**
     * Sanitize input to remove personal information
     */
    sanitizeInput(input) {
        // Remove potential personal info patterns
        let sanitized = input;
        // Remove email addresses
        sanitized = sanitized.replace(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, '[EMAIL]');
        // Remove phone numbers
        sanitized = sanitized.replace(/(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/g, '[PHONE]');
        // Remove IP addresses
        sanitized = sanitized.replace(/\b(?:\d{1,3}\.){3}\d{1,3}\b/g, '[IP]');
        // Remove file paths with username
        sanitized = sanitized.replace(/\/home\/[^\/\s]+/g, '/home/[USER]');
        sanitized = sanitized.replace(/\/Users\/[^\/\s]+/g, '/Users/[USER]');
        // Remove potential passwords (common patterns)
        sanitized = sanitized.replace(/password[:\s]*\S+/gi, 'password:[HIDDEN]');
        sanitized = sanitized.replace(/pwd[:\s]*\S+/gi, 'pwd:[HIDDEN]');
        return sanitized.trim();
    }
    /**
     * Try to suggest what the user might have meant
     */
    suggestIntent(input) {
        const lowered = input.toLowerCase();
        // Simple keyword matching for suggestions
        if (lowered.includes('install') || lowered.includes('get') || lowered.includes('download')) {
            return 'install';
        }
        if (lowered.includes('update') || lowered.includes('upgrade')) {
            return 'update';
        }
        if (lowered.includes('problem') || lowered.includes('broken') || lowered.includes('fix')) {
            return 'troubleshoot';
        }
        if (lowered.includes('setting') || lowered.includes('change') || lowered.includes('configure')) {
            return 'config';
        }
        return undefined;
    }
    /**
     * Save to local storage (privacy-preserving)
     */
    saveToLocalStorage() {
        if (typeof localStorage !== 'undefined') {
            try {
                const key = `nfh_unsupported_${this.sessionId}`;
                const data = {
                    session: this.sessionId,
                    commands: this.unsupportedLog.slice(-100), // Only save last 100
                    timestamp: new Date().toISOString()
                };
                localStorage.setItem(key, JSON.stringify(data));
            }
            catch (e) {
                // Ignore storage errors
            }
        }
    }
    /**
     * Get analytics about unsupported commands
     */
    getAnalytics() {
        // Count frequency of similar patterns
        const patternMap = new Map();
        this.unsupportedLog.forEach(cmd => {
            // Extract key words (simple tokenization)
            const words = cmd.input.toLowerCase().split(/\s+/)
                .filter(w => w.length > 3 && !['that', 'this', 'with', 'from'].includes(w));
            const pattern = words.sort().join(' ');
            patternMap.set(pattern, (patternMap.get(pattern) || 0) + 1);
        });
        // Get top patterns
        const topPatterns = Array.from(patternMap.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10)
            .map(([pattern, count]) => ({ pattern, count }));
        return {
            commands: this.unsupportedLog,
            totalCount: this.unsupportedLog.length,
            uniqueCount: new Set(this.unsupportedLog.map(c => c.input)).size,
            topPatterns
        };
    }
    /**
     * Export anonymous analytics (for improving patterns)
     */
    exportAnonymousPatterns() {
        const analytics = this.getAnalytics();
        // Create anonymous pattern report
        const report = {
            version: '1.0',
            timestamp: new Date().toISOString(),
            sessionDuration: Date.now() - parseInt(this.sessionId, 36),
            patterns: analytics.topPatterns,
            summary: {
                total: analytics.totalCount,
                unique: analytics.uniqueCount,
                averageConfidence: this.unsupportedLog.reduce((sum, cmd) => sum + cmd.confidence, 0) / this.unsupportedLog.length || 0
            }
        };
        return JSON.stringify(report, null, 2);
    }
    /**
     * Clear the log (user privacy control)
     */
    clearLog() {
        this.unsupportedLog = [];
        // Clear from local storage
        if (typeof localStorage !== 'undefined') {
            const key = `nfh_unsupported_${this.sessionId}`;
            localStorage.removeItem(key);
        }
    }
    /**
     * Get user-friendly suggestions for common mistakes
     */
    getSuggestions() {
        const analytics = this.getAnalytics();
        const suggestions = [];
        // Analyze patterns and provide suggestions
        analytics.topPatterns.forEach(({ pattern }) => {
            const words = pattern.split(' ');
            if (words.includes('install') && words.length === 1) {
                suggestions.push("To install software, say 'install' followed by the program name");
            }
            if (words.includes('wifi') || words.includes('internet')) {
                suggestions.push("For network issues, try 'my wifi isn't working' or 'no internet'");
            }
            if (words.includes('update') && words.includes('all')) {
                suggestions.push("To update everything, just say 'update system'");
            }
        });
        return suggestions.slice(0, 3); // Top 3 suggestions
    }
}
// Export singleton instance
export const unsupportedHandler = new UnsupportedCommandHandler();
//# sourceMappingURL=unsupported-handler.js.map