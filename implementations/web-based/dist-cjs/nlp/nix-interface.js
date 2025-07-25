"use strict";
/**
 * Nix Interface - Main Entry Point
 * Ties together all layers of the refactored architecture
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.nixInterface = exports.NixInterface = void 0;
const intent_recognition_1 = require("./layers/intent-recognition");
const command_builder_1 = require("./layers/command-builder");
const command_executor_1 = require("./layers/command-executor");
const error_handler_1 = require("./error-handler");
const command_history_1 = require("./command-history");
const batch_operations_1 = require("./batch-operations");
const context_manager_1 = require("./context-manager");
const usage_tracker_1 = require("./usage-tracker");
class NixInterface {
    constructor() {
        this.executionOptions = {
            dryRun: false,
            requireConfirmation: false,
            timeout: 30000
        };
    }
    /**
     * Process natural language input
     */
    async processInput(input) {
        const startTime = Date.now();
        try {
            // Check for special commands
            if (this.isSpecialCommand(input)) {
                return this.handleSpecialCommand(input);
            }
            // Check for batch operations
            if (this.isBatchOperation(input)) {
                return this.processBatchOperation(input);
            }
            // Layer 1: Intent Recognition (pure function)
            let intent = (0, intent_recognition_1.recognizeIntent)(input);
            // Handle unknown intents
            if (intent.type === 'unknown') {
                const suggestion = (0, intent_recognition_1.suggestIntent)(input);
                return {
                    success: false,
                    response: "I didn't understand that. Try rephrasing it.",
                    suggestions: suggestion ? [`Did you mean to ${suggestion} something?`] : undefined
                };
            }
            // Apply context if available
            intent = context_manager_1.contextManager.processWithContext(input, intent);
            // Track intent
            usage_tracker_1.usageTracker.trackIntent(intent.type, intent.confidence);
            // Layer 2: Command Building (pure function)
            const buildResult = (0, command_builder_1.buildCommand)(intent);
            if (!buildResult.success || !buildResult.command) {
                return {
                    success: false,
                    response: buildResult.error || 'Could not create command',
                    suggestions: buildResult.suggestion ? [buildResult.suggestion] : undefined
                };
            }
            const command = buildResult.command;
            // Check if user wants explanation
            if (input.toLowerCase().startsWith('explain:')) {
                return {
                    success: true,
                    response: (0, command_builder_1.explainCommand)(command),
                    command: `${command.command} ${command.args.join(' ')}`
                };
            }
            // Check if user wants preview
            if (input.toLowerCase().startsWith('preview:')) {
                this.executionOptions.dryRun = true;
            }
            // Determine execution options based on risk
            const risk = (0, command_builder_1.getCommandRiskLevel)(command);
            const options = {
                ...this.executionOptions,
                requireConfirmation: risk === 'dangerous' || command.requiresConfirmation
            };
            // Layer 3: Command Execution
            const result = await (0, command_executor_1.executeCommand)(command, options);
            // Track execution
            usage_tracker_1.usageTracker.trackExecution(intent.type, result.success, result.duration);
            // Add to history
            const historyId = command_history_1.commandHistory.addEntry({
                timestamp: new Date(),
                naturalInput: input,
                recognizedIntent: intent,
                executedCommand: `${command.command} ${command.args.join(' ')}`,
                success: result.success,
                error: result.error,
                duration: result.duration
            });
            // Update context
            context_manager_1.contextManager.setLastResult(result.success ? 'success' : 'error', result.success ? command.description : result.error || 'Unknown error');
            // Format response
            if (result.success) {
                return {
                    success: true,
                    response: this.formatSuccessResponse(command, result),
                    command: `${command.command} ${command.args.join(' ')}`,
                    output: result.output,
                    duration: Date.now() - startTime
                };
            }
            else if (result.wasCancelled) {
                return {
                    success: false,
                    response: "Command cancelled.",
                    duration: Date.now() - startTime
                };
            }
            else {
                const error = (0, error_handler_1.handleError)(result.error || '', command.command);
                return {
                    success: false,
                    response: (0, error_handler_1.formatErrorResponse)(error),
                    error: result.error,
                    suggestions: error.suggestion ? [error.suggestion] : undefined,
                    duration: Date.now() - startTime
                };
            }
        }
        catch (error) {
            console.error('Processing error:', error);
            return {
                success: false,
                response: "An unexpected error occurred. Please try again.",
                error: error instanceof Error ? error.message : 'Unknown error',
                duration: Date.now() - startTime
            };
        }
    }
    /**
     * Check if input is a special command
     */
    isSpecialCommand(input) {
        const specialCommands = ['undo', 'history', 'help', 'clear', 'stats'];
        return specialCommands.some(cmd => input.toLowerCase().startsWith(cmd));
    }
    /**
     * Handle special commands
     */
    async handleSpecialCommand(input) {
        const command = input.toLowerCase().split(' ')[0];
        switch (command) {
            case 'undo':
                return this.handleUndo();
            case 'history':
                return this.handleHistory();
            case 'help':
                return this.handleHelp();
            case 'clear':
                return {
                    success: true,
                    response: "Output cleared."
                };
            case 'stats':
                return this.handleStats();
            default:
                return {
                    success: false,
                    response: "Unknown special command."
                };
        }
    }
    /**
     * Check if input is a batch operation
     */
    isBatchOperation(input) {
        return /\s+(?:and|,|then|after that|next)\s+/i.test(input);
    }
    /**
     * Process batch operation
     */
    async processBatchOperation(input) {
        const batch = (0, batch_operations_1.parseBatchOperations)(input);
        const result = await (0, batch_operations_1.executeBatch)(batch, {
            stopOnError: false,
            dryRun: this.executionOptions.dryRun,
            confirmEach: this.executionOptions.requireConfirmation
        });
        return {
            success: result.failed === 0,
            response: (0, batch_operations_1.formatBatchResult)(result),
            duration: result.duration
        };
    }
    /**
     * Handle undo command
     */
    async handleUndo() {
        const lastCommand = command_history_1.commandHistory.getRecent(1)[0];
        if (!lastCommand || !lastCommand.success) {
            return {
                success: false,
                response: "No recent successful command to undo."
            };
        }
        // TODO: Implement actual rollback
        return {
            success: true,
            response: `Would undo: ${lastCommand.naturalInput}`
        };
    }
    /**
     * Handle history command
     */
    handleHistory() {
        const recent = command_history_1.commandHistory.getRecent(10);
        if (recent.length === 0) {
            return {
                success: true,
                response: "No command history yet."
            };
        }
        const lines = recent.map((entry, index) => `${index + 1}. ${entry.naturalInput} ${entry.success ? '✅' : '❌'}`);
        return {
            success: true,
            response: "Recent commands:\n" + lines.join('\n')
        };
    }
    /**
     * Handle help command
     */
    handleHelp() {
        const help = `
Natural Language Commands:
• install [package] - Install a package
• remove [package] - Remove a package  
• update system - Update NixOS
• show installed - List installed packages
• free up space - Clean old packages
• [service] is running? - Check service status
• show logs - View system logs

Special Commands:
• undo - Undo last command
• history - Show command history
• clear - Clear output
• stats - Show usage statistics
• help - Show this help

Tips:
• Use natural language - "I need firefox"
• Chain commands - "install firefox and vscode"
• Preview first - "preview: update system"
• Get explanations - "explain: install docker"
    `.trim();
        return {
            success: true,
            response: help
        };
    }
    /**
     * Handle stats command
     */
    handleStats() {
        const stats = command_history_1.commandHistory.getStats();
        const usage = usage_tracker_1.usageTracker.getStats();
        const response = `
Usage Statistics:
• Total commands: ${stats.totalCommands}
• Success rate: ${(stats.successRate * 100).toFixed(1)}%
• Average response time: ${stats.averageResponseTime.toFixed(0)}ms

Most common commands:
${stats.mostCommonCommands.map(cmd => `• ${cmd.command}: ${cmd.count} times`).join('\n')}

Intent recognition:
• Total commands: ${usage.totalCommands}
• Success rate: ${(usage.successRate * 100).toFixed(1)}%
    `.trim();
        return {
            success: true,
            response
        };
    }
    /**
     * Format success response
     */
    formatSuccessResponse(command, result) {
        // Use natural language responses
        const responses = {
            install: (cmd, res) => {
                const pkg = cmd.args[1]?.replace('nixpkgs.', '') || 'the package';
                return `Great! I've installed ${pkg} for you. You can find it in your applications menu.`;
            },
            remove: (cmd, res) => {
                const pkg = cmd.args[1] || 'the package';
                return `I've removed ${pkg} from your system.`;
            },
            update: () => "Your system is now up to date!",
            query: (cmd, res) => {
                const packages = res.output?.split('\n').filter(Boolean) || [];
                return `You have ${packages.length} packages installed.`;
            },
            service: (cmd, res) => {
                if (cmd.args[0] === 'status') {
                    return `I've checked the status of ${cmd.args[1]}. ${res.output?.includes('active') ? "It's running." : "It's not running."}`;
                }
                return `Service ${cmd.args[1]} ${cmd.args[0]}ed successfully.`;
            },
            maintenance: () => "I've cleaned up old packages and freed up disk space!",
            logs: () => "Here are the recent system logs.",
            troubleshoot: () => "I've checked the network status. See the details above.",
            config: () => "Settings updated successfully!"
        };
        const formatter = responses[command.type];
        if (formatter) {
            return formatter(command, result);
        }
        return `Done! ${command.description} completed successfully.`;
    }
    /**
     * Get autocomplete suggestions
     */
    getSuggestions(partial) {
        return command_history_1.commandHistory.getSuggestions(partial);
    }
    /**
     * Set execution options
     */
    setOptions(options) {
        this.executionOptions = { ...this.executionOptions, ...options };
    }
    /**
     * Get current options
     */
    getOptions() {
        return { ...this.executionOptions };
    }
}
exports.NixInterface = NixInterface;
// Export singleton instance
exports.nixInterface = new NixInterface();
//# sourceMappingURL=nix-interface.js.map