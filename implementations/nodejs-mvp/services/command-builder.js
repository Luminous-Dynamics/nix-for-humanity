// 🔨 Command Builder - Constructs safe NixOS commands

class CommandBuilder {
  constructor() {
    // Map of allowed commands for MVP (user-space only)
    this.commandTemplates = {
      'nix search': {
        base: 'nix search nixpkgs',
        requiresPackage: true,
        options: ['--json']
      },
      'nix-env -q': {
        base: 'nix-env -q',
        requiresPackage: false,
        options: ['--installed', '--json']
      },
      'nix-info': {
        base: 'nix-info -m',
        requiresPackage: false,
        options: []
      },
      'nix doctor': {
        base: 'nix doctor',
        requiresPackage: false,
        options: []
      },
      'nix path-info': {
        base: 'nix path-info',
        requiresPackage: true,
        options: ['--json']
      },
      'nix-env -iA': {
        base: 'nix-env -iA nixpkgs',
        requiresPackage: true,
        options: ['--dry-run'] // Safe for MVP
      },
      'nix-env -e': {
        base: 'nix-env -e',
        requiresPackage: true,
        options: ['--dry-run'] // Safe for MVP
      },
      'nix-channel --update': {
        base: 'nix-channel --update',
        requiresPackage: false,
        options: []
      },
      'nix-env -u --dry-run': {
        base: 'nix-env -u --dry-run',
        requiresPackage: false,
        options: []
      },
      'nix-collect-garbage': {
        base: 'nix-collect-garbage --dry-run',
        requiresPackage: false,
        options: []
      }
    };
  }

  async build(intent) {
    const template = this.commandTemplates[intent.command];
    
    if (!template) {
      throw new Error(`Unknown command template: ${intent.command}`);
    }

    // Build command parts
    const parts = [template.base];

    // Add package name if required
    if (template.requiresPackage && intent.package) {
      parts.push(this.sanitizePackageName(intent.package));
    } else if (template.requiresPackage && !intent.package) {
      throw new Error('Package name required for this command');
    }

    // Add options for better parsing
    if (template.options.length > 0) {
      parts.push(...template.options);
    }

    // Build final command
    const command = {
      raw: parts.join(' '),
      parts: parts,
      safe: true, // All MVP commands are user-space safe
      intent: intent.action,
      package: intent.package
    };

    // Validate the command
    this.validate(command);

    return command;
  }

  sanitizePackageName(packageName) {
    // Remove potentially dangerous characters
    let sanitized = packageName
      .replace(/[;&|<>`$(){}[\]]/g, '') // Remove shell special chars
      .replace(/\s+/g, '-')              // Replace spaces with hyphens
      .toLowerCase()                      // Normalize case
      .trim();

    // Ensure it's not empty after sanitization
    if (!sanitized) {
      throw new Error('Invalid package name');
    }

    // Common package name corrections
    const corrections = {
      'firefox': 'firefox',
      'fire-fox': 'firefox',
      'vscode': 'vscode',
      'vs-code': 'vscode',
      'visual-studio-code': 'vscode',
      'python': 'python3',
      'python3': 'python3',
      'nodejs': 'nodejs',
      'node': 'nodejs'
    };

    return corrections[sanitized] || sanitized;
  }

  validate(command) {
    // Ensure command doesn't contain dangerous patterns
    const dangerous = [
      /sudo/i,
      /rm\s+-rf/i,
      />\s*\/dev\/null/,
      /2>&1/,
      /\|\s*sh/,
      /curl.*\|/,
      /wget.*\|/
    ];

    for (const pattern of dangerous) {
      if (pattern.test(command.raw)) {
        throw new Error('Command contains potentially dangerous pattern');
      }
    }

    // Ensure command starts with allowed base
    const allowedBases = Object.values(this.commandTemplates).map(t => t.base);
    const startsWithAllowed = allowedBases.some(base => 
      command.raw.startsWith(base)
    );

    if (!startsWithAllowed) {
      throw new Error('Command does not start with allowed base');
    }

    return true;
  }
}

module.exports = CommandBuilder;