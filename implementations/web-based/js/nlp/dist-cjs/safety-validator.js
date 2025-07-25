/**
 * Safety Validator for Nix for Humanity
 * Ensures all commands are safe before execution
 */
/**
 * Comprehensive safety validation for Nix commands
 */
export class SafetyValidator {
    constructor() {
        // Dangerous patterns that should never be allowed
        this.dangerousPatterns = [
            // File system destruction
            /rm\s+-rf\s+\//,
            /rm\s+-rf\s+\/\*/,
            /rm\s+-rf\s+~\//,
            /rm\s+-rf\s+\$HOME/,
            /mkfs/,
            /dd\s+if=.*of=\/dev/,
            // System corruption
            /chmod\s+-R\s+000/,
            /chmod\s+000\s+\//,
            /chown\s+-R\s+nobody:nogroup\s+\//,
            // Fork bombs
            /:\(\)\s*{\s*:\|:&\s*};:/,
            /\$\(\s*\$0\s*\)/,
            // Network attacks
            /nc\s+-l/,
            /nmap/,
            // Password/security files
            /\/etc\/(passwd|shadow|sudoers)/,
            /\.ssh\/.*key/,
            // Kernel/boot
            /\/boot\//,
            /grub/,
            /kernel/,
            // Infinite loops
            /while\s+true.*do/,
            /for\s*\(\s*;\s*;\s*\)/
        ];
        // Whitelist of safe Nix commands
        this.safeCommands = new Set([
            'nix-env',
            'nix-shell',
            'nix-build',
            'nix-store',
            'nix-channel',
            'nix-collect-garbage',
            'nixos-rebuild',
            'nixos-option',
            'nixos-generate-config',
            'home-manager',
            'systemctl',
            'journalctl',
            'pactl',
            'xrandr',
            'gsettings',
            'nmcli',
            'ip',
            'ping',
            'traceroute',
            'df',
            'du',
            'free',
            'top',
            'htop',
            'ps',
            'lsblk',
            'lscpu',
            'uname',
            'date',
            'whoami',
            'which',
            'whereis',
            'man',
            'help'
        ]);
        // Safe operations for each command
        this.safeOperations = {
            'nix-env': ['-i', '-iA', '-e', '-u', '-q', '-qa', '--list-generations', '--rollback'],
            'nixos-rebuild': ['switch', 'test', 'boot', 'build', 'dry-build', 'dry-activate'],
            'systemctl': ['status', 'start', 'stop', 'restart', 'enable', 'disable', 'list-units'],
            'nix-channel': ['--list', '--add', '--remove', '--update'],
            'nix-store': ['--query', '--gc', '--verify', '--optimise'],
            'nmcli': ['device', 'connection', 'general', 'networking'],
            'gsettings': ['get', 'set', 'list-schemas', 'list-keys']
        };
    }
    /**
     * Validate a command for safety
     */
    validateCommand(command, args) {
        // Check for dangerous patterns
        const fullCommand = `${command} ${args.join(' ')}`;
        for (const pattern of this.dangerousPatterns) {
            if (pattern.test(fullCommand)) {
                return {
                    isSafe: false,
                    reason: 'This command contains potentially dangerous operations',
                    suggestion: 'Please describe what you want to accomplish, and I\'ll suggest a safe approach'
                };
            }
        }
        // Check if command is in whitelist
        const baseCommand = command === 'sudo' && args.length > 0 ? args[0] : command;
        if (!this.safeCommands.has(baseCommand)) {
            return {
                isSafe: false,
                reason: `Command '${baseCommand}' is not in the approved list`,
                suggestion: 'I can only run pre-approved system commands for safety'
            };
        }
        // Check if operation is allowed for this command
        if (this.safeOperations[baseCommand]) {
            const operation = command === 'sudo' ? args[1] : args[0];
            if (operation && !this.safeOperations[baseCommand].includes(operation)) {
                return {
                    isSafe: false,
                    reason: `Operation '${operation}' is not allowed for ${baseCommand}`,
                    suggestion: `Try one of these: ${this.safeOperations[baseCommand].join(', ')}`
                };
            }
        }
        // Additional checks for specific commands
        if (baseCommand === 'nixos-rebuild' && args.includes('switch')) {
            return {
                isSafe: true,
                reason: 'System update will create a rollback point automatically'
            };
        }
        if (baseCommand === 'nix-env' && args.some(arg => arg.startsWith('-i'))) {
            // Check package name is reasonable
            const packageArg = args.find(arg => arg.startsWith('nixpkgs.'));
            if (packageArg) {
                const packageName = packageArg.replace('nixpkgs.', '');
                if (packageName.match(/^[a-zA-Z0-9\-_]+$/)) {
                    return { isSafe: true };
                }
            }
        }
        return { isSafe: true };
    }
    /**
     * Validate package name
     */
    validatePackageName(packageName) {
        // Check for path traversal attempts
        if (packageName.includes('..') || packageName.includes('/')) {
            return {
                isSafe: false,
                reason: 'Package name contains invalid characters',
                suggestion: 'Package names should only contain letters, numbers, and hyphens'
            };
        }
        // Check for command injection
        if (packageName.match(/[;&|`$<>\\]/)) {
            return {
                isSafe: false,
                reason: 'Package name contains shell metacharacters',
                suggestion: 'Please use a simple package name'
            };
        }
        // Reasonable length
        if (packageName.length > 100) {
            return {
                isSafe: false,
                reason: 'Package name is too long',
                suggestion: 'Please provide a shorter package name'
            };
        }
        return { isSafe: true };
    }
    /**
     * Validate file path for operations
     */
    validatePath(path) {
        // Never allow operations on system directories
        const protectedPaths = [
            '/',
            '/etc',
            '/boot',
            '/dev',
            '/proc',
            '/sys',
            '/nix',
            '/var',
            '/usr',
            '/bin',
            '/sbin',
            '/lib'
        ];
        const normalizedPath = path.replace(/\/+$/, ''); // Remove trailing slashes
        if (protectedPaths.includes(normalizedPath)) {
            return {
                isSafe: false,
                reason: 'Operations on system directories are not allowed',
                suggestion: 'System directories are protected for your safety'
            };
        }
        // Check for attempts to escape restrictions
        if (path.includes('../') || path.includes('..\\')) {
            return {
                isSafe: false,
                reason: 'Path traversal is not allowed',
                suggestion: 'Please use absolute paths or paths within your home directory'
            };
        }
        return { isSafe: true };
    }
    /**
     * Get safety explanation for users
     */
    explainSafety(command) {
        if (command.includes('nixos-rebuild')) {
            return 'This will update your system configuration. A restore point will be created automatically.';
        }
        if (command.includes('nix-env -i')) {
            return 'This will install software from the official Nix package repository.';
        }
        if (command.includes('nix-collect-garbage')) {
            return 'This will clean up old, unused packages to free disk space.';
        }
        if (command.includes('systemctl')) {
            return 'This will manage system services. Changes can be reversed.';
        }
        return 'This operation has been verified as safe to run.';
    }
}
// Export singleton instance
export const safetyValidator = new SafetyValidator();
//# sourceMappingURL=safety-validator.js.map