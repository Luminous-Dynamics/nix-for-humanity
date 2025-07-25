"use strict";
/**
 * Command Builder Layer (Pure Functions)
 * Converts intents to NixOS commands - no execution
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildCommand = buildCommand;
exports.getCommandRiskLevel = getCommandRiskLevel;
exports.explainCommand = explainCommand;
/**
 * Build NixOS command from intent
 * Pure function - no side effects
 */
function buildCommand(intent) {
    switch (intent.type) {
        case 'search':
            return buildSearchCommand(intent.entities);
        case 'install':
            return buildInstallCommand(intent.entities);
        case 'remove':
            return buildRemoveCommand(intent.entities);
        case 'update':
            return buildUpdateCommand();
        case 'query':
            return buildQueryCommand();
        case 'service':
            return buildServiceCommand(intent.entities);
        case 'maintenance':
            return buildMaintenanceCommand(intent.entities);
        case 'logs':
            return buildLogsCommand(intent.entities);
        case 'troubleshoot':
            return buildTroubleshootCommand(intent.entities);
        case 'config':
            return buildConfigCommand(intent.entities);
        default:
            return {
                success: false,
                error: 'Unknown command type',
                suggestion: 'Try rephrasing your request'
            };
    }
}
/**
 * Build search command
 */
function buildSearchCommand(entities) {
    const packageEntity = entities.find(e => e.type === 'package');
    if (!packageEntity) {
        return {
            success: false,
            error: 'No package specified',
            suggestion: 'What would you like to search for?'
        };
    }
    return {
        success: true,
        command: {
            command: 'nix',
            args: ['search', 'nixpkgs', packageEntity.value],
            requiresSudo: false,
            requiresConfirmation: false,
            description: `Search for ${packageEntity.value} packages`,
            supportsDryRun: false
        }
    };
}
/**
 * Build install command
 */
function buildInstallCommand(entities) {
    const packageEntity = entities.find(e => e.type === 'package');
    if (!packageEntity) {
        return {
            success: false,
            error: 'No package specified',
            suggestion: 'What would you like to install?'
        };
    }
    return {
        success: true,
        command: {
            command: 'nix-env',
            args: ['-iA', `nixpkgs.${packageEntity.value}`],
            requiresSudo: false,
            requiresConfirmation: true,
            description: `Install ${packageEntity.value}`,
            rollbackCommand: 'nix-env --rollback',
            supportsDryRun: true
        }
    };
}
/**
 * Build remove command
 */
function buildRemoveCommand(entities) {
    const packageEntity = entities.find(e => e.type === 'package');
    if (!packageEntity) {
        return {
            success: false,
            error: 'No package specified',
            suggestion: 'What would you like to remove?'
        };
    }
    return {
        success: true,
        command: {
            command: 'nix-env',
            args: ['-e', packageEntity.value],
            requiresSudo: false,
            requiresConfirmation: true,
            description: `Remove ${packageEntity.value}`,
            rollbackCommand: 'nix-env --rollback',
            supportsDryRun: true
        }
    };
}
/**
 * Build update command
 */
function buildUpdateCommand() {
    return {
        success: true,
        command: {
            command: 'nixos-rebuild',
            args: ['switch', '--upgrade'],
            requiresSudo: true,
            requiresConfirmation: true,
            description: 'Update entire system',
            rollbackCommand: 'nixos-rebuild switch --rollback',
            supportsDryRun: true
        }
    };
}
/**
 * Build query command
 */
function buildQueryCommand() {
    return {
        success: true,
        command: {
            command: 'nix-env',
            args: ['-q'],
            requiresSudo: false,
            requiresConfirmation: false,
            description: 'List installed packages',
            supportsDryRun: false
        }
    };
}
/**
 * Build service command
 */
function buildServiceCommand(entities) {
    const serviceEntity = entities.find(e => e.type === 'service');
    const actionEntity = entities.find(e => e.type === 'action');
    if (!serviceEntity) {
        return {
            success: false,
            error: 'No service specified',
            suggestion: 'Which service would you like to manage?'
        };
    }
    const action = actionEntity?.value || 'status';
    const requiresSudo = ['start', 'stop', 'restart', 'enable', 'disable'].includes(action);
    const requiresConfirmation = ['stop', 'restart', 'disable'].includes(action);
    return {
        success: true,
        command: {
            command: 'systemctl',
            args: [action, serviceEntity.value],
            requiresSudo,
            requiresConfirmation,
            description: `${capitalize(action)} ${serviceEntity.value} service`,
            supportsDryRun: false
        }
    };
}
/**
 * Build maintenance command
 */
function buildMaintenanceCommand(entities) {
    const actionEntity = entities.find(e => e.type === 'action');
    if (actionEntity?.value === 'garbage-collection') {
        return {
            success: true,
            command: {
                command: 'nix-collect-garbage',
                args: ['-d'],
                requiresSudo: false,
                requiresConfirmation: true,
                description: 'Free up disk space by removing old packages',
                supportsDryRun: true
            }
        };
    }
    return {
        success: true,
        command: {
            command: 'nix-collect-garbage',
            args: [],
            requiresSudo: false,
            requiresConfirmation: true,
            description: 'Clean up unused packages',
            supportsDryRun: true
        }
    };
}
/**
 * Build logs command
 */
function buildLogsCommand(entities) {
    const args = ['-xe']; // Show explanations and jump to end
    const timeframeEntity = entities.find(e => e.type === 'timeframe');
    if (timeframeEntity?.value === 'recent') {
        args.push('-n', '100'); // Last 100 lines
    }
    const logTypeEntity = entities.find(e => e.type === 'logType');
    if (logTypeEntity?.value === 'errors') {
        args.push('-p', 'err'); // Priority: errors only
    }
    return {
        success: true,
        command: {
            command: 'journalctl',
            args,
            requiresSudo: false,
            requiresConfirmation: false,
            description: 'View system logs',
            supportsDryRun: false
        }
    };
}
/**
 * Build troubleshooting command
 */
function buildTroubleshootCommand(entities) {
    const problemEntity = entities.find(e => e.type === 'problem');
    if (problemEntity?.value === 'network') {
        return {
            success: true,
            command: {
                command: 'systemctl',
                args: ['status', 'NetworkManager'],
                requiresSudo: false,
                requiresConfirmation: false,
                description: 'Check network service status',
                supportsDryRun: false
            }
        };
    }
    return {
        success: false,
        error: 'Unknown problem type',
        suggestion: 'What specific issue are you experiencing?'
    };
}
/**
 * Build configuration command
 */
function buildConfigCommand(entities) {
    const settingEntity = entities.find(e => e.type === 'setting');
    if (settingEntity?.value === 'font-size-increase') {
        return {
            success: true,
            command: {
                command: 'gsettings',
                args: ['set', 'org.gnome.desktop.interface', 'text-scaling-factor', '1.2'],
                requiresSudo: false,
                requiresConfirmation: true,
                description: 'Increase font size',
                supportsDryRun: false
            }
        };
    }
    if (settingEntity?.value === 'font-size-decrease') {
        return {
            success: true,
            command: {
                command: 'gsettings',
                args: ['set', 'org.gnome.desktop.interface', 'text-scaling-factor', '0.9'],
                requiresSudo: false,
                requiresConfirmation: true,
                description: 'Decrease font size',
                supportsDryRun: false
            }
        };
    }
    return {
        success: false,
        error: 'Configuration not supported yet',
        suggestion: 'This feature is coming soon'
    };
}
/**
 * Helper function to capitalize first letter
 */
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}
/**
 * Get command risk level for safety decisions
 * Pure function
 */
function getCommandRiskLevel(command) {
    // Safe commands - just queries
    const safeCommands = ['journalctl', 'systemctl status', 'nix-env -q'];
    if (safeCommands.some(safe => command.command === safe.split(' ')[0] &&
        (safe.split(' ')[1] ? command.args[0] === safe.split(' ')[1] : true))) {
        return 'safe';
    }
    // Dangerous commands - system modifications
    const dangerousCommands = ['nixos-rebuild', 'systemctl stop', 'systemctl disable'];
    if (dangerousCommands.some(dangerous => command.command === dangerous.split(' ')[0] &&
        (dangerous.split(' ')[1] ? command.args[0] === dangerous.split(' ')[1] : true))) {
        return 'dangerous';
    }
    // Everything else is moderate
    return 'moderate';
}
/**
 * Generate natural language description of what command will do
 * Pure function
 */
function explainCommand(command) {
    const { command: cmd, args, description } = command;
    let explanation = `This will ${description.toLowerCase()}.\n\n`;
    if (cmd === 'nix-env' && args[0] === '-iA') {
        const pkg = args[1].replace('nixpkgs.', '');
        explanation += `Technical details:\n`;
        explanation += `- Search for '${pkg}' in the nixpkgs repository\n`;
        explanation += `- Download the package and its dependencies\n`;
        explanation += `- Build or unpack as needed\n`;
        explanation += `- Add to your user profile\n`;
        explanation += `- Create a new generation (allowing rollback)\n`;
    }
    else if (cmd === 'nixos-rebuild' && args.includes('switch')) {
        explanation += `This is a system-wide operation that will:\n`;
        explanation += `- Update all system packages\n`;
        explanation += `- Rebuild your NixOS configuration\n`;
        explanation += `- Switch to the new configuration\n`;
        explanation += `- Create a new boot entry\n`;
        explanation += `\nYou can rollback if needed.`;
    }
    if (command.requiresSudo) {
        explanation += `\n⚠️  This requires administrator privileges.`;
    }
    if (command.supportsDryRun) {
        explanation += `\n💡 Tip: Add '--dry-run' to preview without making changes.`;
    }
    return explanation;
}
//# sourceMappingURL=command-builder.js.map