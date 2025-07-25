/**
 * Unit tests for safety validator
 * Ensures all dangerous commands are blocked
 */

const { safetyValidator } = require('../../../js/nlp/dist-cjs/safety-validator.js');

describe('Safety Validator', () => {
  
  describe('Dangerous Pattern Detection', () => {
    test.each([
      ['rm', ['-rf', '/']],
      ['rm', ['-rf', '/*']],
      ['rm', ['-rf', '~/']],
      ['rm', ['-rf', '$HOME']],
      ['mkfs', ['/dev/sda']],
      ['dd', ['if=/dev/zero', 'of=/dev/sda']],
      ['chmod', ['-R', '000', '/']],
      ['chmod', ['000', '/']],
      ['chown', ['-R', 'nobody:nogroup', '/']]
    ])('blocks dangerous command: %s %s', (command, args) => {
      const result = safetyValidator.validateCommand(command, args);
      
      expect(result.isSafe).toBe(false);
      expect(result.reason).toContain('dangerous');
      expect(result.suggestion).toBeDefined();
    });
  });

  describe('Fork Bomb Detection', () => {
    test('blocks fork bomb patterns', () => {
      const forkBombs = [
        ':(){:|:&};:',
        '$($0)',
        'while true; do echo; done'
      ];
      
      forkBombs.forEach(bomb => {
        const result = safetyValidator.validateCommand('bash', ['-c', bomb]);
        expect(result.isSafe).toBe(false);
      });
    });
  });

  describe('Safe Command Whitelist', () => {
    test.each([
      ['nix-env', ['-iA', 'nixpkgs.firefox']],
      ['nix-shell', ['-p', 'python3']],
      ['nixos-rebuild', ['switch']],
      ['systemctl', ['status', 'nginx']],
      ['journalctl', ['-xe']],
      ['nix-collect-garbage', ['-d']],
      ['gsettings', ['set', 'org.gnome.desktop.interface', 'text-scaling-factor', '1.2']]
    ])('allows safe command: %s %s', (command, args) => {
      const result = safetyValidator.validateCommand(command, args);
      
      expect(result.isSafe).toBe(true);
      expect(result.reason).toBeUndefined();
    });
  });

  describe('Command Not in Whitelist', () => {
    test('blocks unknown commands', () => {
      const result = safetyValidator.validateCommand('malicious-binary', ['--exploit']);
      
      expect(result.isSafe).toBe(false);
      expect(result.reason).toContain('not in the approved list');
      expect(result.suggestion).toContain('pre-approved system commands');
    });
  });

  describe('Operation Validation', () => {
    test('allows valid nix-env operations', () => {
      const validOps = ['-i', '-iA', '-e', '-u', '-q', '--list-generations', '--rollback'];
      
      validOps.forEach(op => {
        const result = safetyValidator.validateCommand('nix-env', [op, 'package']);
        expect(result.isSafe).toBe(true);
      });
    });
    
    test('blocks invalid nix-env operations', () => {
      const result = safetyValidator.validateCommand('nix-env', ['--dangerous-op']);
      
      expect(result.isSafe).toBe(false);
      expect(result.reason).toContain('Operation \'--dangerous-op\' is not allowed');
      expect(result.suggestion).toContain('Try one of these:');
    });
  });

  describe('Package Name Validation', () => {
    test.each([
      ['firefox', true],
      ['visual-studio-code', true],
      ['python3', true],
      ['git_2_42_0', true],
      ['../../../etc/passwd', false],
      ['package; rm -rf /', false],
      ['package && malicious', false],
      ['package | grep password', false],
      ['$(dangerous)', false],
      ['`command`', false],
      ['package\\nmalicious', false]
    ])('package "%s" is %s', (packageName, expectedSafe) => {
      const result = safetyValidator.validatePackageName(packageName);
      expect(result.isSafe).toBe(expectedSafe);
      
      if (!expectedSafe) {
        expect(result.reason).toBeDefined();
        expect(result.suggestion).toBeDefined();
      }
    });
  });

  describe('Path Validation', () => {
    test.each([
      ['/', false],
      ['/etc', false],
      ['/boot', false],
      ['/nix', false],
      ['/home/user/documents', true],
      ['~/projects', true],
      ['../../etc/passwd', false],
      ['..\\..\\windows\\system32', false]
    ])('path "%s" is %s', (path, expectedSafe) => {
      const result = safetyValidator.validatePath(path);
      expect(result.isSafe).toBe(expectedSafe);
    });
  });

  describe('Special NixOS Commands', () => {
    test('nixos-rebuild switch is marked as safe with note', () => {
      const result = safetyValidator.validateCommand('nixos-rebuild', ['switch']);
      
      expect(result.isSafe).toBe(true);
      expect(result.reason).toContain('rollback point automatically');
    });
    
    test('nix-env install validates package names', () => {
      const result = safetyValidator.validateCommand('nix-env', ['-iA', 'nixpkgs.firefox']);
      expect(result.isSafe).toBe(true);
      
      const badResult = safetyValidator.validateCommand('nix-env', ['-iA', 'nixpkgs.../../evil']);
      expect(badResult.isSafe).toBe(false);
    });
  });

  describe('Safety Explanations', () => {
    test('provides clear explanations for common commands', () => {
      const explanations = [
        ['nixos-rebuild', 'restore point'],
        ['nix-env -i', 'official Nix package repository'],
        ['nix-collect-garbage', 'free disk space'],
        ['systemctl', 'manage system services']
      ];
      
      explanations.forEach(([command, expected]) => {
        const explanation = safetyValidator.explainSafety(command);
        expect(explanation.toLowerCase()).toContain(expected);
      });
    });
  });

  describe('Edge Cases', () => {
    test('handles empty command', () => {
      const result = safetyValidator.validateCommand('', []);
      expect(result.isSafe).toBe(false);
    });
    
    test('handles null/undefined gracefully', () => {
      const result = safetyValidator.validateCommand(null, null);
      expect(result.isSafe).toBe(false);
    });
    
    test('handles very long package names', () => {
      const longName = 'a'.repeat(101);
      const result = safetyValidator.validatePackageName(longName);
      
      expect(result.isSafe).toBe(false);
      expect(result.reason).toContain('too long');
    });
    
    test('handles sudo wrapper correctly', () => {
      const result = safetyValidator.validateCommand('sudo', ['nix-env', '-iA', 'nixpkgs.firefox']);
      expect(result.isSafe).toBe(true);
      
      const badResult = safetyValidator.validateCommand('sudo', ['rm', '-rf', '/']);
      expect(badResult.isSafe).toBe(false);
    });
  });

  describe('Security Patterns', () => {
    test('blocks SQL injection attempts in arguments', () => {
      const result = safetyValidator.validateCommand('nix-env', [
        '-iA',
        "nixpkgs.firefox'; DROP TABLE users; --"
      ]);
      
      expect(result.isSafe).toBe(false);
    });
    
    test('blocks command substitution in arguments', () => {
      const patterns = [
        '$(malicious)',
        '`malicious`',
        '${malicious}',
        '<(malicious)',
        '>(malicious)'
      ];
      
      patterns.forEach(pattern => {
        const result = safetyValidator.validateCommand('echo', [pattern]);
        expect(result.isSafe).toBe(false);
      });
    });
    
    test('blocks network attack tools', () => {
      const tools = [
        ['nc', ['-l', '4444']],
        ['nmap', ['-sS', 'target.com']],
        ['netcat', ['-e', '/bin/bash']]
      ];
      
      tools.forEach(([cmd, args]) => {
        const result = safetyValidator.validateCommand(cmd, args);
        expect(result.isSafe).toBe(false);
      });
    });
  });
});