/**
 * Unit tests for Nix command wrapper
 * Tests safe command generation and execution simulation
 */

const { nixWrapper } = require('../../../js/nlp/dist-cjs/nix-wrapper.js');
const { intentEngine } = require('../../../js/nlp/dist-cjs/intent-engine.js');

describe('Nix Command Wrapper', () => {
  
  describe('Install Command Generation', () => {
    test('generates correct install command', () => {
      const intent = {
        type: 'install',
        entities: [{ type: 'package', value: 'firefox', confidence: 0.9 }]
      };
      
      const command = nixWrapper.intentToCommand(intent);
      
      expect(command).toBeDefined();
      expect(command.command).toBe('nix-env');
      expect(command.args).toEqual(['-iA', 'nixpkgs.firefox']);
      expect(command.requiresSudo).toBe(false);
      expect(command.description).toBe('Install firefox');
    });
    
    test('handles package name normalization', () => {
      const intent = {
        type: 'install',
        entities: [{ type: 'package', value: 'visual-studio-code', confidence: 0.9 }]
      };
      
      const command = nixWrapper.intentToCommand(intent);
      expect(command.args).toEqual(['-iA', 'nixpkgs.visual-studio-code']);
    });
  });

  describe('Maintenance Command Generation', () => {
    test('generates garbage collection command', () => {
      const intent = {
        type: 'maintenance',
        entities: [{ type: 'action', value: 'garbage-collection', confidence: 0.9 }]
      };
      
      const command = nixWrapper.intentToCommand(intent);
      
      expect(command).toBeDefined();
      expect(command.command).toBe('nix-collect-garbage');
      expect(command.args).toEqual(['-d']);
      expect(command.requiresSudo).toBe(false);
      expect(command.description).toContain('Free up disk space');
    });
  });

  describe('Logs Command Generation', () => {
    test('generates basic logs command', () => {
      const intent = {
        type: 'logs',
        entities: [
          { type: 'logType', value: 'system', confidence: 0.9 },
          { type: 'timeframe', value: 'all', confidence: 0.9 }
        ]
      };
      
      const command = nixWrapper.intentToCommand(intent);
      
      expect(command).toBeDefined();
      expect(command.command).toBe('journalctl');
      expect(command.args).toContain('-xe');
      expect(command.requiresSudo).toBe(false);
    });
    
    test('generates error logs command', () => {
      const intent = {
        type: 'logs',
        entities: [
          { type: 'logType', value: 'errors', confidence: 0.9 },
          { type: 'timeframe', value: 'recent', confidence: 0.9 }
        ]
      };
      
      const command = nixWrapper.intentToCommand(intent);
      
      expect(command.args).toContain('-p');
      expect(command.args).toContain('err');
      expect(command.args).toContain('-n');
      expect(command.args).toContain('100');
    });
  });

  describe('Service Command Generation', () => {
    test('generates service status command', () => {
      const intent = {
        type: 'service',
        entities: [
          { type: 'action', value: 'status', confidence: 0.9 },
          { type: 'service', value: 'nginx', confidence: 0.9 }
        ]
      };
      
      const command = nixWrapper.intentToCommand(intent);
      
      expect(command).toBeDefined();
      expect(command.command).toBe('systemctl');
      expect(command.args).toEqual(['status', 'nginx']);
      expect(command.requiresSudo).toBe(false);
    });
    
    test('generates service start command with sudo', () => {
      const intent = {
        type: 'service',
        entities: [
          { type: 'action', value: 'start', confidence: 0.9 },
          { type: 'service', value: 'docker', confidence: 0.9 }
        ]
      };
      
      const command = nixWrapper.intentToCommand(intent);
      
      expect(command.args).toEqual(['start', 'docker']);
      expect(command.requiresSudo).toBe(true);
    });
    
    test('generates list services command', () => {
      const intent = {
        type: 'service',
        entities: [
          { type: 'action', value: 'list', confidence: 0.9 },
          { type: 'service', value: 'all', confidence: 0.9 }
        ]
      };
      
      const command = nixWrapper.intentToCommand(intent);
      
      expect(command.args).toContain('list-units');
      expect(command.args).toContain('--type=service');
      expect(command.args).toContain('--state=running');
    });
  });

  describe('Update Command Generation', () => {
    test('generates system update command', () => {
      const intent = { type: 'update', entities: [] };
      const command = nixWrapper.intentToCommand(intent);
      
      expect(command.command).toBe('sudo');
      expect(command.args).toContain('nixos-rebuild');
      expect(command.args).toContain('switch');
      expect(command.args).toContain('--upgrade');
      expect(command.requiresSudo).toBe(true);
    });
  });

  describe('Query Command Generation', () => {
    test('generates list packages command', () => {
      const intent = { type: 'query', entities: [] };
      const command = nixWrapper.intentToCommand(intent);
      
      expect(command.command).toBe('nix-env');
      expect(command.args).toEqual(['-q']);
      expect(command.requiresSudo).toBe(false);
    });
  });

  describe('Safety Validation', () => {
    test('blocks dangerous commands', async () => {
      const dangerousCommand = {
        command: 'rm',
        args: ['-rf', '/'],
        requiresSudo: true,
        description: 'Remove everything'
      };
      
      const result = await nixWrapper.execute(dangerousCommand);
      
      expect(result.success).toBe(false);
      expect(result.error).toContain('safety');
      expect(result.naturalLanguageResponse).toContain("can't run that");
    });
    
    test('allows safe commands', async () => {
      const safeCommand = {
        command: 'nix-env',
        args: ['-iA', 'nixpkgs.firefox'],
        requiresSudo: false,
        description: 'Install firefox'
      };
      
      const result = await nixWrapper.execute(safeCommand);
      
      expect(result.success).toBe(true);
      expect(result.naturalLanguageResponse).toContain('installed');
    });
  });

  describe('Natural Language Responses', () => {
    test('generates friendly install response', async () => {
      const command = {
        command: 'nix-env',
        args: ['-iA', 'nixpkgs.firefox'],
        requiresSudo: false,
        description: 'Install firefox'
      };
      
      const result = await nixWrapper.execute(command);
      
      expect(result.naturalLanguageResponse).toContain('Great!');
      expect(result.naturalLanguageResponse).toContain('firefox');
      expect(result.naturalLanguageResponse).toContain('applications menu');
    });
    
    test('generates friendly cleanup response', async () => {
      const command = {
        command: 'nix-collect-garbage',
        args: ['-d'],
        requiresSudo: false,
        description: 'Free up disk space by removing old packages'
      };
      
      const result = await nixWrapper.execute(command);
      
      expect(result.naturalLanguageResponse).toContain('cleaned up');
      expect(result.naturalLanguageResponse).toContain('more room');
    });
    
    test('generates friendly service response', async () => {
      const command = {
        command: 'systemctl',
        args: ['status', 'nginx'],
        requiresSudo: false,
        description: 'Check status of nginx'
      };
      
      const result = await nixWrapper.execute(command);
      
      expect(result.naturalLanguageResponse).toContain('checked the status');
      expect(result.naturalLanguageResponse).toContain('nginx');
    });
  });

  describe('Rollback Support', () => {
    test('tracks rollback commands', () => {
      const intent = {
        type: 'install',
        entities: [{ type: 'package', value: 'firefox', confidence: 0.9 }]
      };
      
      const command = nixWrapper.intentToCommand(intent);
      
      expect(command.rollbackCommand).toBe('nix-env --rollback');
    });
    
    test('provides rollback options', () => {
      const options = nixWrapper.getRollbackOptions();
      expect(Array.isArray(options)).toBe(true);
    });
  });

  describe('Edge Cases', () => {
    test('handles missing entities gracefully', () => {
      const intent = {
        type: 'install',
        entities: [] // No package specified
      };
      
      const command = nixWrapper.intentToCommand(intent);
      expect(command).toBeNull();
    });
    
    test('handles unknown intent types', () => {
      const intent = {
        type: 'unknown',
        entities: []
      };
      
      const command = nixWrapper.intentToCommand(intent);
      expect(command).toBeNull();
    });
    
    test('handles service command without action', () => {
      const intent = {
        type: 'service',
        entities: [
          { type: 'service', value: 'nginx', confidence: 0.9 }
          // Missing action entity
        ]
      };
      
      const command = nixWrapper.intentToCommand(intent);
      expect(command).toBeNull();
    });
  });

  describe('Integration with Intent Engine', () => {
    test('full pipeline: natural language to safe command', async () => {
      // User input
      const userInput = 'free up some space';
      
      // Parse intent
      const intent = intentEngine.recognize(userInput);
      expect(intent.type).toBe('maintenance');
      
      // Generate command
      const command = nixWrapper.intentToCommand(intent);
      expect(command).toBeDefined();
      expect(command.command).toBe('nix-collect-garbage');
      
      // Execute safely
      const result = await nixWrapper.execute(command);
      expect(result.success).toBe(true);
      expect(result.naturalLanguageResponse).toContain('cleaned up');
    });
    
    test('full pipeline: service management', async () => {
      const userInput = 'is nginx running?';
      
      const intent = intentEngine.recognize(userInput);
      expect(intent.type).toBe('service');
      
      const command = nixWrapper.intentToCommand(intent);
      expect(command.command).toBe('systemctl');
      expect(command.args).toContain('status');
      
      const result = await nixWrapper.execute(command);
      expect(result.success).toBe(true);
    });
  });
});