"use strict";
/**
 * Command Executor Layer
 * Handles actual command execution with safety options
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.executeCommand = executeCommand;
exports.executeRollback = executeRollback;
exports.createOutputStreamer = createOutputStreamer;
// Use mock sandbox for browser environment
let commandSandbox;
// Dynamic import based on environment
async function getCommandSandbox() {
    if (!commandSandbox) {
        if (typeof window !== 'undefined') {
            // Browser environment - use mock
            const module = await Promise.resolve().then(() => __importStar(require('../command-sandbox-mock.js')));
            commandSandbox = module.commandSandbox;
        }
        else {
            // Node.js environment - use real sandbox
            const module = await Promise.resolve().then(() => __importStar(require('../command-sandbox.js')));
            commandSandbox = module.commandSandbox;
        }
    }
    return commandSandbox;
}
/**
 * Execute NixOS command with safety options
 * This is the ONLY place where actual execution happens
 */
async function executeCommand(command, options = {}) {
    const startTime = Date.now();
    // Add --dry-run if requested
    if (options.dryRun && command.supportsDryRun) {
        command.args.push('--dry-run');
    }
    // Handle confirmation if required
    if (options.requireConfirmation || command.requiresConfirmation) {
        const confirmed = await confirmWithUser(command);
        if (!confirmed) {
            return {
                success: false,
                output: '',
                wasCancelled: true,
                duration: Date.now() - startTime,
                rollbackAvailable: false
            };
        }
    }
    try {
        // Get the appropriate command sandbox
        const sandbox = await getCommandSandbox();
        // Execute in sandbox
        const result = await sandbox.execute(command.command, command.args, {
            maxExecutionTime: options.timeout || 30000,
            allowNetwork: commandNeedsNetwork(command),
            allowFileWrite: commandNeedsFileWrite(command)
        });
        // Stream output if requested
        if (options.onProgress && result.stdout) {
            options.onProgress(result.stdout);
        }
        return {
            success: result.success,
            output: result.stdout,
            error: result.stderr,
            exitCode: result.exitCode || undefined,
            duration: Date.now() - startTime,
            rollbackAvailable: Boolean(command.rollbackCommand)
        };
    }
    catch (error) {
        return {
            success: false,
            output: '',
            error: error instanceof Error ? error.message : 'Unknown error',
            duration: Date.now() - startTime,
            rollbackAvailable: false
        };
    }
}
/**
 * Execute rollback command
 */
async function executeRollback(originalCommand, options = {}) {
    if (!originalCommand.rollbackCommand) {
        return {
            success: false,
            output: '',
            error: 'No rollback available for this command',
            duration: 0,
            rollbackAvailable: false
        };
    }
    // Parse rollback command
    const [cmd, ...args] = originalCommand.rollbackCommand.split(' ');
    const rollbackCommand = {
        command: cmd,
        args,
        requiresSudo: cmd === 'sudo' || originalCommand.requiresSudo,
        requiresConfirmation: false, // Already confirmed
        description: `Rollback: ${originalCommand.description}`,
        supportsDryRun: false
    };
    return executeCommand(rollbackCommand, options);
}
/**
 * Check if command needs network access
 */
function commandNeedsNetwork(command) {
    const networkCommands = ['nix-env', 'nixos-rebuild', 'nix-channel'];
    const downloadActions = ['-i', '-iA', '--install', '--upgrade', 'update'];
    if (networkCommands.includes(command.command)) {
        return command.args.some(arg => downloadActions.includes(arg));
    }
    return false;
}
/**
 * Check if command needs file write access
 */
function commandNeedsFileWrite(command) {
    const writeCommands = ['nix-env', 'nixos-rebuild', 'systemctl', 'gsettings'];
    const writeActions = ['-i', '-e', '--install', '--uninstall', 'switch', 'enable', 'disable', 'set'];
    if (writeCommands.includes(command.command)) {
        return command.args.some(arg => writeActions.includes(arg));
    }
    return false;
}
/**
 * Confirm with user (stub - would be implemented by UI layer)
 */
async function confirmWithUser(command) {
    // This would be implemented by the UI layer
    // For now, return true in development, false in production
    if (process.env.NODE_ENV === 'development') {
        console.log(`[DEV] Would ask user to confirm: ${command.description}`);
        return true;
    }
    // In production, this would show a dialog
    return false;
}
/**
 * Stream command output in real-time
 */
function createOutputStreamer(onData, onComplete) {
    let buffer = '';
    let isComplete = false;
    return (output) => {
        if (isComplete)
            return;
        buffer += output;
        const lines = buffer.split('\n');
        // Keep the last incomplete line in buffer
        buffer = lines.pop() || '';
        // Process complete lines
        lines.forEach(line => {
            if (line.trim()) {
                onData(line + '\n');
            }
        });
        // Check for completion markers
        if (output.includes('successfully installed') ||
            output.includes('error:') ||
            output.includes('failed:')) {
            isComplete = true;
            if (buffer) {
                onData(buffer);
            }
            onComplete();
        }
    };
}
//# sourceMappingURL=command-executor.js.map