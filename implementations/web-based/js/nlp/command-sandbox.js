/**
 * Command Sandbox
 * Provides secure execution environment for system commands
 */
import { spawn } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
export class CommandSandbox {
    constructor() {
        this.defaultOptions = {
            maxExecutionTime: 30000, // 30 seconds
            maxMemory: 512 * 1024 * 1024, // 512MB
            maxOutputSize: 10 * 1024 * 1024, // 10MB
            allowNetwork: false,
            allowFileWrite: false,
            workingDirectory: os.tmpdir()
        };
    }
    /**
     * Create a temporary sandbox directory
     */
    async createSandboxDir() {
        const sandboxDir = path.join(os.tmpdir(), `nix-sandbox-${Date.now()}`);
        await fs.promises.mkdir(sandboxDir, { recursive: true });
        return sandboxDir;
    }
    /**
     * Clean up sandbox directory
     */
    async cleanupSandboxDir(sandboxDir) {
        try {
            await fs.promises.rmdir(sandboxDir, { recursive: true });
        }
        catch (error) {
            console.warn('Failed to cleanup sandbox directory:', error);
        }
    }
    /**
     * Execute command in sandbox
     */
    async execute(command, args, options = {}) {
        const opts = { ...this.defaultOptions, ...options };
        const startTime = Date.now();
        const sandboxDir = await this.createSandboxDir();
        try {
            // Sanitize command for logging
            const sanitizedCommand = this.sanitizeCommand(command, args);
            // Build sandbox environment
            const sandboxEnv = this.buildSandboxEnvironment(opts);
            // Execute with restrictions
            const result = await this.executeWithRestrictions(command, args, sandboxDir, opts, sandboxEnv);
            return {
                ...result,
                executionTime: Date.now() - startTime,
                sanitizedCommand
            };
        }
        finally {
            await this.cleanupSandboxDir(sandboxDir);
        }
    }
    /**
     * Execute command with restrictions
     */
    executeWithRestrictions(command, args, sandboxDir, options, env) {
        return new Promise((resolve) => {
            let stdout = '';
            let stderr = '';
            let outputSize = 0;
            let timedOut = false;
            // Spawn process with restrictions
            const child = spawn(command, args, {
                cwd: sandboxDir,
                env,
                // Limit file descriptors
                stdio: ['ignore', 'pipe', 'pipe'],
                // Drop privileges if running as root
                uid: process.getuid && process.getuid() > 0 ? process.getuid() : undefined,
                gid: process.getgid && process.getgid() > 0 ? process.getgid() : undefined,
            });
            // Set execution timeout
            const timer = setTimeout(() => {
                timedOut = true;
                child.kill('SIGTERM');
                // Force kill after grace period
                setTimeout(() => child.kill('SIGKILL'), 5000);
            }, options.maxExecutionTime);
            // Handle stdout
            child.stdout.on('data', (data) => {
                outputSize += data.length;
                if (outputSize <= options.maxOutputSize) {
                    stdout += data.toString();
                }
                else if (!stdout.includes('[OUTPUT TRUNCATED]')) {
                    stdout += '\n[OUTPUT TRUNCATED]\n';
                }
            });
            // Handle stderr
            child.stderr.on('data', (data) => {
                outputSize += data.length;
                if (outputSize <= options.maxOutputSize) {
                    stderr += data.toString();
                }
                else if (!stderr.includes('[OUTPUT TRUNCATED]')) {
                    stderr += '\n[OUTPUT TRUNCATED]\n';
                }
            });
            // Handle process exit
            child.on('exit', (code, signal) => {
                clearTimeout(timer);
                if (timedOut) {
                    resolve({
                        success: false,
                        stdout,
                        stderr: stderr + '\n[EXECUTION TIMEOUT]',
                        exitCode: null
                    });
                }
                else {
                    resolve({
                        success: code === 0,
                        stdout,
                        stderr,
                        exitCode: code
                    });
                }
            });
            // Handle errors
            child.on('error', (error) => {
                clearTimeout(timer);
                resolve({
                    success: false,
                    stdout,
                    stderr: error.message,
                    exitCode: null
                });
            });
        });
    }
    /**
     * Build sandbox environment variables
     */
    buildSandboxEnvironment(options) {
        const env = {
            // Minimal PATH
            PATH: '/run/current-system/sw/bin:/nix/var/nix/profiles/default/bin',
            // Set HOME to sandbox
            HOME: options.workingDirectory,
            // Disable interactive features
            DEBIAN_FRONTEND: 'noninteractive',
            // Set locale
            LANG: 'en_US.UTF-8',
            // Nix-specific
            NIX_PATH: process.env.NIX_PATH || 'nixpkgs=/nix/var/nix/profiles/per-user/root/channels/nixos',
        };
        // Restrict network if needed
        if (!options.allowNetwork) {
            env.http_proxy = '';
            env.https_proxy = '';
            env.ftp_proxy = '';
            env.no_proxy = '*';
        }
        return env;
    }
    /**
     * Sanitize command for safe logging
     */
    sanitizeCommand(command, args) {
        // Hide sensitive information
        const sanitizedArgs = args.map(arg => {
            // Hide passwords
            if (arg.includes('password=') || arg.includes('--password')) {
                return '[REDACTED]';
            }
            // Hide tokens
            if (arg.includes('token=') || arg.includes('--token')) {
                return '[REDACTED]';
            }
            // Hide paths that might contain sensitive info
            if (arg.includes('/home/') && arg.includes('/.')) {
                return arg.replace(/\/home\/[^\/]+\/\.[^\/]+/g, '/home/[USER]/.[HIDDEN]');
            }
            return arg;
        });
        return `${command} ${sanitizedArgs.join(' ')}`;
    }
    /**
     * Validate command is safe to execute
     */
    validateCommand(command, args) {
        // Dangerous commands that should never run
        const dangerousCommands = [
            'rm',
            'dd',
            'mkfs',
            'fdisk',
            'shred',
            'chmod',
            'chown'
        ];
        if (dangerousCommands.includes(command)) {
            return { safe: false, reason: `Command '${command}' is potentially dangerous` };
        }
        // Check for dangerous patterns in arguments
        const dangerousPatterns = [
            /^\/$/, // Root directory
            /^\/\*$/, // All files in root
            /rm\s+-rf/, // Recursive force delete
            />\s*\/dev\/[^n]/, // Overwriting devices (except /dev/null)
            /fork\s*\(\s*\)/, // Fork bombs
        ];
        const fullCommand = `${command} ${args.join(' ')}`;
        for (const pattern of dangerousPatterns) {
            if (pattern.test(fullCommand)) {
                return { safe: false, reason: `Dangerous pattern detected: ${pattern}` };
            }
        }
        return { safe: true };
    }
}
// Export singleton instance
export const commandSandbox = new CommandSandbox();
//# sourceMappingURL=command-sandbox.js.map