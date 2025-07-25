/**
 * Safe Nix Command Wrapper
 * Executes Nix commands with rollback capability and safety checks
 */
import { safetyValidator } from './safety-validator';
import { usageTracker } from './usage-tracker';
import { contextManager } from './context-manager';
/**
 * Safe wrapper for Nix command execution
 */
export class NixSafeWrapper {
    constructor() {
        this.commandHistory = [];
        this.currentGeneration = 0;
    }
    /**
     * Convert intent to safe Nix command
     */
    intentToCommand(intent) {
        switch (intent.type) {
            case 'install':
                return this.createInstallCommand(intent.entities);
            case 'update':
                return this.createUpdateCommand();
            case 'query':
                return this.createQueryCommand(intent.entities);
            case 'troubleshoot':
                return this.createTroubleshootCommand(intent.entities);
            case 'config':
                return this.createConfigCommand(intent.entities);
            case 'maintenance':
                return this.createMaintenanceCommand(intent.entities);
            case 'logs':
                return this.createLogsCommand(intent.entities);
            case 'service':
                return this.createServiceCommand(intent.entities);
            default:
                return null;
        }
    }
    /**
     * Execute command with safety checks
     */
    async execute(command) {
        const startTime = Date.now();
        try {
            // 1. Validate command safety
            const safetyCheck = safetyValidator.validateCommand(command.command, command.args);
            if (!safetyCheck.isSafe) {
                return {
                    success: false,
                    output: '',
                    error: safetyCheck.reason || 'Command failed safety validation',
                    rollbackAvailable: false,
                    naturalLanguageResponse: safetyCheck.suggestion || "I can't run that command because it might not be safe. Let me know what you're trying to do and I'll help find a safe way."
                };
            }
            // 2. Create rollback point
            const rollbackPoint = await this.createRollbackPoint();
            // 3. Execute command (simulation for now)
            const result = await this.simulateExecution(command);
            // 4. Verify success
            if (result.success) {
                this.commandHistory.push(command);
                const duration = Date.now() - startTime;
                // Track successful execution
                const intentType = this.getIntentTypeFromCommand(command);
                usageTracker.trackExecution(intentType, true, duration);
                // Update context with success
                const response = this.generateSuccessResponse(command, result);
                contextManager.setLastResult('success', response);
                return {
                    ...result,
                    rollbackAvailable: true,
                    naturalLanguageResponse: response
                };
            }
            else {
                // Auto-rollback on failure
                await this.rollback(rollbackPoint);
                const duration = Date.now() - startTime;
                // Track failed execution
                const intentType = this.getIntentTypeFromCommand(command);
                usageTracker.trackExecution(intentType, false, duration);
                // Update context with error
                const response = this.generateErrorResponse(command, result);
                contextManager.setLastResult('error', response);
                return {
                    ...result,
                    rollbackAvailable: false,
                    naturalLanguageResponse: response
                };
            }
        }
        catch (error) {
            return {
                success: false,
                output: '',
                error: error instanceof Error ? error.message : 'Unknown error',
                rollbackAvailable: false,
                naturalLanguageResponse: "Something unexpected happened. Let me try a different approach."
            };
        }
    }
    /**
     * Create install command
     */
    createInstallCommand(entities) {
        const packageEntity = entities.find(e => e.type === 'package');
        if (!packageEntity)
            return null;
        return {
            command: 'nix-env',
            args: ['-iA', `nixpkgs.${packageEntity.value}`],
            requiresSudo: false,
            description: `Install ${packageEntity.value}`,
            rollbackCommand: 'nix-env --rollback'
        };
    }
    /**
     * Create update command
     */
    createUpdateCommand() {
        return {
            command: 'sudo',
            args: ['nixos-rebuild', 'switch', '--upgrade'],
            requiresSudo: true,
            description: 'Update system',
            rollbackCommand: 'sudo nixos-rebuild switch --rollback'
        };
    }
    /**
     * Create query command
     */
    createQueryCommand(entities) {
        return {
            command: 'nix-env',
            args: ['-q'],
            requiresSudo: false,
            description: 'List installed packages'
        };
    }
    /**
     * Create troubleshooting command
     */
    createTroubleshootCommand(entities) {
        const problemEntity = entities.find(e => e.type === 'problem');
        if (!problemEntity)
            return null;
        switch (problemEntity.value) {
            case 'network':
                return {
                    command: 'systemctl',
                    args: ['status', 'NetworkManager'],
                    requiresSudo: false,
                    description: 'Check network status'
                };
            case 'audio':
                return {
                    command: 'pactl',
                    args: ['info'],
                    requiresSudo: false,
                    description: 'Check audio system'
                };
            case 'display':
                return {
                    command: 'xrandr',
                    args: [],
                    requiresSudo: false,
                    description: 'Check display configuration'
                };
            default:
                return null;
        }
    }
    /**
     * Create configuration command
     */
    createConfigCommand(entities) {
        const settingEntity = entities.find(e => e.type === 'setting');
        if (!settingEntity)
            return null;
        if (settingEntity.value === 'font-size') {
            return {
                command: 'gsettings',
                args: ['set', 'org.gnome.desktop.interface', 'text-scaling-factor', '1.2'],
                requiresSudo: false,
                description: 'Increase font size'
            };
        }
        return null;
    }
    /**
     * Create maintenance command (garbage collection, cleanup)
     */
    createMaintenanceCommand(entities) {
        const actionEntity = entities.find(e => e.type === 'action');
        if (actionEntity?.value === 'garbage-collection') {
            return {
                command: 'nix-collect-garbage',
                args: ['-d'],
                requiresSudo: false,
                description: 'Free up disk space by removing old packages',
                rollbackCommand: undefined
            };
        }
        // Default to garbage collection
        return {
            command: 'nix-collect-garbage',
            args: ['-d'],
            requiresSudo: false,
            description: 'Clean up unused packages'
        };
    }
    /**
     * Create logs viewing command
     */
    createLogsCommand(entities) {
        const logTypeEntity = entities.find(e => e.type === 'logType');
        const timeframeEntity = entities.find(e => e.type === 'timeframe');
        const args = ['-xe']; // Show explanations and jump to end
        if (timeframeEntity?.value === 'recent') {
            args.push('-n', '100'); // Last 100 lines
        }
        if (logTypeEntity?.value === 'errors') {
            args.push('-p', 'err'); // Priority: errors only
        }
        return {
            command: 'journalctl',
            args: args,
            requiresSudo: false,
            description: 'View system logs'
        };
    }
    /**
     * Create service management command
     */
    createServiceCommand(entities) {
        const actionEntity = entities.find(e => e.type === 'action');
        const serviceEntity = entities.find(e => e.type === 'service');
        if (!actionEntity || !serviceEntity)
            return null;
        const action = actionEntity.value;
        const serviceName = serviceEntity.value;
        if (action === 'list') {
            return {
                command: 'systemctl',
                args: ['list-units', '--type=service', '--state=running'],
                requiresSudo: false,
                description: 'List running services'
            };
        }
        // Service control commands
        const validActions = ['start', 'stop', 'restart', 'status', 'enable', 'disable'];
        if (validActions.includes(action)) {
            return {
                command: 'systemctl',
                args: [action, serviceName],
                requiresSudo: ['start', 'stop', 'restart', 'enable', 'disable'].includes(action),
                description: `${action} ${serviceName} service`
            };
        }
        // Default to status
        return {
            command: 'systemctl',
            args: ['status', serviceName],
            requiresSudo: false,
            description: `Check status of ${serviceName}`
        };
    }
    /**
     * Validate command safety
     */
    validateCommand(command) {
        // Use comprehensive safety validator
        const safetyCheck = safetyValidator.validateCommand(command.command, command.args);
        if (!safetyCheck.isSafe) {
            console.warn(`Command failed safety check: ${safetyCheck.reason}`);
        }
        return safetyCheck.isSafe;
    }
    /**
     * Create rollback point
     */
    async createRollbackPoint() {
        // In real implementation, would get current generation
        this.currentGeneration++;
        return this.currentGeneration;
    }
    /**
     * Rollback to previous state
     */
    async rollback(generation) {
        // In real implementation, would execute rollback
        console.log(`Rolling back to generation ${generation}`);
    }
    /**
     * Simulate command execution (for MVP)
     */
    async simulateExecution(command) {
        // Simulate some common scenarios
        if (command.command === 'nix-env' && command.args[0] === '-iA') {
            const packageName = command.args[1].replace('nixpkgs.', '');
            return {
                success: true,
                output: `installing '${packageName}'\nbuilding...\ninstalled successfully`,
                rollbackAvailable: true
            };
        }
        if (command.command === 'nix-env' && command.args[0] === '-q') {
            return {
                success: true,
                output: 'firefox-120.0\nvscode-1.85.0\ngit-2.42.0',
                rollbackAvailable: false
            };
        }
        return {
            success: true,
            output: 'Command executed successfully',
            rollbackAvailable: false
        };
    }
    /**
     * Generate natural language success response
     */
    generateSuccessResponse(command, result) {
        if (command.description.includes('Install')) {
            const pkg = command.description.replace('Install ', '');
            return `Great! I've installed ${pkg} for you. You can find it in your applications menu.`;
        }
        if (command.description.includes('Update')) {
            return `Your system is now up to date! All packages have been upgraded to their latest versions.`;
        }
        if (command.description.includes('List')) {
            const packages = result.output.split('\n').filter(Boolean);
            return `You have ${packages.length} packages installed. Here are some of them: ${packages.slice(0, 3).join(', ')}...`;
        }
        if (command.description.includes('Free up disk space')) {
            return `I've cleaned up old packages and freed up disk space. Your system should have more room now!`;
        }
        if (command.description.includes('View system logs')) {
            return `Here are the system logs. Look for any error messages or warnings that might explain the issue.`;
        }
        if (command.description.includes('status')) {
            const serviceName = command.description.match(/status of (.+)/)?.[1] || 'the service';
            return `I've checked the status of ${serviceName}. See above for details about whether it's running.`;
        }
        if (command.description.includes('start')) {
            const serviceName = command.description.match(/start (.+) service/)?.[1] || 'the service';
            return `I've started ${serviceName} for you. It should be running now.`;
        }
        if (command.description.includes('stop')) {
            const serviceName = command.description.match(/stop (.+) service/)?.[1] || 'the service';
            return `I've stopped ${serviceName}. It's no longer running.`;
        }
        return `Done! ${command.description} completed successfully.`;
    }
    /**
     * Generate natural language error response
     */
    generateErrorResponse(command, result) {
        if (command.description.includes('Install')) {
            return `I couldn't install that package. It might not be available or there was a network issue. Would you like me to search for similar packages?`;
        }
        return `I ran into a problem: ${result.error}. Don't worry, I've undone any changes. Let's try a different approach.`;
    }
    /**
     * Get rollback options
     */
    getRollbackOptions() {
        return this.commandHistory
            .filter(cmd => cmd.rollbackCommand)
            .map(cmd => cmd.description);
    }
    /**
     * Get intent type from command for tracking
     */
    getIntentTypeFromCommand(command) {
        if (command.description.includes('Install'))
            return 'install';
        if (command.description.includes('Update'))
            return 'update';
        if (command.description.includes('List'))
            return 'query';
        if (command.description.includes('Check'))
            return 'query';
        if (command.description.includes('Free up'))
            return 'maintenance';
        if (command.description.includes('logs'))
            return 'logs';
        if (command.description.includes('service'))
            return 'service';
        return 'unknown';
    }
}
// Export singleton instance
export const nixWrapper = new NixSafeWrapper();
//# sourceMappingURL=nix-wrapper.js.map