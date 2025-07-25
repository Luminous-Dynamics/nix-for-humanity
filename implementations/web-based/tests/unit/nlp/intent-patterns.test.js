/**
 * Unit tests for NLP intent patterns
 * Tests all pattern recognition including new maintenance, logs, and service patterns
 */

const { intentEngine } = require('../../../js/nlp/dist-cjs/intent-engine.js');

describe('NLP Intent Pattern Recognition', () => {
  
  describe('Installation Patterns', () => {
    test.each([
      ['install firefox', 'install', 'firefox'],
      ['i need firefox', 'install', 'firefox'],
      ['get me vscode', 'install', 'vscode'],
      ['I want spotify', 'install', 'spotify'],
      ['download git', 'install', 'git'],
      ['can you install chrome', 'install', 'google-chrome'],
      ['firefox please', 'install', 'firefox'],
      ['I need a web browser', 'install', 'firefox'],
      ['i need to edit photos', 'install', 'gimp'],
      ['help me browse the internet', 'install', 'firefox']
    ])('"%s" → intent: %s, package: %s', (input, expectedIntent, expectedPackage) => {
      const intent = intentEngine.recognize(input);
      
      expect(intent.type).toBe(expectedIntent);
      expect(intent.confidence).toBeGreaterThan(0.8);
      
      const packageEntity = intent.entities.find(e => e.type === 'package');
      expect(packageEntity).toBeDefined();
      expect(packageEntity.value).toBe(expectedPackage);
    });
  });

  describe('Maintenance Patterns (Garbage Collection)', () => {
    test.each([
      ['free up space', 'maintenance', 'garbage-collection'],
      ['clean up disk space', 'maintenance', 'garbage-collection'],
      ['my disk is full', 'maintenance', 'garbage-collection'],
      ['clean up old packages', 'maintenance', 'garbage-collection'],
      ['run garbage collection', 'maintenance', 'garbage-collection'],
      ['delete unused packages', 'maintenance', 'garbage-collection'],
      ['reclaim storage space', 'maintenance', 'garbage-collection'],
      ['how much space is being used', 'maintenance', 'garbage-collection']
    ])('"%s" → intent: %s, action: %s', (input, expectedIntent, expectedAction) => {
      const intent = intentEngine.recognize(input);
      
      expect(intent.type).toBe(expectedIntent);
      expect(intent.confidence).toBeGreaterThan(0.8);
      
      const actionEntity = intent.entities.find(e => e.type === 'action');
      expect(actionEntity).toBeDefined();
      expect(actionEntity.value).toBe(expectedAction);
    });
  });

  describe('System Logs Patterns', () => {
    test.each([
      ['show me the logs', 'logs', 'system', 'all'],
      ['check system logs', 'logs', 'system', 'all'],
      ['what went wrong', 'logs', 'system', 'all'],
      ['show recent errors', 'logs', 'errors', 'recent'],
      ['why did that fail', 'logs', 'system', 'all'],
      ['view error logs', 'logs', 'errors', 'all'],
      ['let me see the logs', 'logs', 'system', 'all'],
      ['check recent errors', 'logs', 'errors', 'recent']
    ])('"%s" → intent: %s, logType: %s, timeframe: %s', (input, expectedIntent, expectedLogType, expectedTimeframe) => {
      const intent = intentEngine.recognize(input);
      
      expect(intent.type).toBe(expectedIntent);
      expect(intent.confidence).toBeGreaterThan(0.8);
      
      const logTypeEntity = intent.entities.find(e => e.type === 'logType');
      expect(logTypeEntity).toBeDefined();
      expect(logTypeEntity.value).toBe(expectedLogType);
      
      const timeframeEntity = intent.entities.find(e => e.type === 'timeframe');
      expect(timeframeEntity).toBeDefined();
      expect(timeframeEntity.value).toBe(expectedTimeframe);
    });
  });

  describe('Service Management Patterns', () => {
    test.each([
      ['is nginx running', 'service', 'status', 'nginx'],
      ['check if mysql is active', 'service', 'status', 'mysql'],
      ['start docker', 'service', 'start', 'docker'],
      ['stop postgresql service', 'service', 'stop', 'postgresql'],
      ['restart nginx', 'service', 'restart', 'nginx'],
      ['what services are running', 'service', 'list', 'all'],
      ['turn on ssh', 'service', 'start', 'sshd'],
      ['disable bluetooth', 'service', 'disable', 'bluetooth'],
      ['check status of redis', 'service', 'status', 'redis']
    ])('"%s" → intent: %s, action: %s, service: %s', (input, expectedIntent, expectedAction, expectedService) => {
      const intent = intentEngine.recognize(input);
      
      expect(intent.type).toBe(expectedIntent);
      expect(intent.confidence).toBeGreaterThan(0.8);
      
      const actionEntity = intent.entities.find(e => e.type === 'action');
      expect(actionEntity).toBeDefined();
      expect(actionEntity.value).toBe(expectedAction);
      
      const serviceEntity = intent.entities.find(e => e.type === 'service');
      expect(serviceEntity).toBeDefined();
      expect(serviceEntity.value).toBe(expectedService);
    });
  });

  describe('Update Patterns', () => {
    test.each([
      ['update system', 'update'],
      ['upgrade everything', 'update'],
      ['check for updates', 'update'],
      ['is my system up to date', 'update'],
      ['make sure everything is current', 'update'],
      ['please update', 'update']
    ])('"%s" → intent: %s', (input, expectedIntent) => {
      const intent = intentEngine.recognize(input);
      
      expect(intent.type).toBe(expectedIntent);
      expect(intent.confidence).toBeGreaterThan(0.8);
    });
  });

  describe('Query Patterns', () => {
    test.each([
      ['what programs do I have', 'query'],
      ['show me installed software', 'query'],
      ['list my apps', 'query'],
      ['what is firefox', 'query'],
      ['tell me about vscode', 'query']
    ])('"%s" → intent: %s', (input, expectedIntent) => {
      const intent = intentEngine.recognize(input);
      
      expect(intent.type).toBe(expectedIntent);
      expect(intent.confidence).toBeGreaterThan(0.8);
    });
  });

  describe('Troubleshooting Patterns', () => {
    test.each([
      ['my internet isn\'t working', 'troubleshoot', 'network'],
      ['wifi is broken', 'troubleshoot', 'network'],
      ['no sound', 'troubleshoot', 'audio'],
      ['screen too bright', 'troubleshoot', 'display'],
      ['computer is slow', 'troubleshoot', 'performance'],
      ['firefox crashed', 'troubleshoot', 'general']
    ])('"%s" → intent: %s, problem: %s', (input, expectedIntent, expectedProblem) => {
      const intent = intentEngine.recognize(input);
      
      expect(intent.type).toBe(expectedIntent);
      expect(intent.confidence).toBeGreaterThan(0.8);
      
      const problemEntity = intent.entities.find(e => e.type === 'problem');
      expect(problemEntity).toBeDefined();
      expect(problemEntity.value).toBe(expectedProblem);
    });
  });

  describe('Configuration Patterns', () => {
    test.each([
      ['make the text bigger', 'config', 'font-size'],
      ['increase font size', 'config', 'font-size'],
      ['make sound louder', 'config', 'volume'],
      ['change wallpaper', 'config', 'wallpaper'],
      ['i can\'t see well', 'config', 'font-size']
    ])('"%s" → intent: %s, setting: %s', (input, expectedIntent, expectedSetting) => {
      const intent = intentEngine.recognize(input);
      
      expect(intent.type).toBe(expectedIntent);
      expect(intent.confidence).toBeGreaterThan(0.8);
      
      const settingEntity = intent.entities.find(e => e.type === 'setting');
      expect(settingEntity).toBeDefined();
      expect(settingEntity.value).toBe(expectedSetting);
    });
  });

  describe('Typo Tolerance', () => {
    test.each([
      ['instal firefox', 'install', 'firefox'],
      ['instlal vscode', 'install', 'vscode'],
      ['i neeed spotify', 'install', 'spotify'],
      ['udpate system', 'update'],
      ['clen up space', 'maintenance'],
      ['shwo me the logs', 'logs'],
      ['is ngix running', 'service', 'nginx']
    ])('Typo "%s" → intent: %s', (input, expectedIntent, expectedEntity) => {
      const intent = intentEngine.recognize(input);
      
      expect(intent.type).toBe(expectedIntent);
      expect(intent.confidence).toBeGreaterThan(0.7);
      
      if (expectedEntity) {
        const entity = intent.entities[0];
        expect(entity).toBeDefined();
        expect(entity.value).toBe(expectedEntity);
      }
    });
  });

  describe('Unknown/Ambiguous Patterns', () => {
    test.each([
      ['do something', 'unknown'],
      ['xyz123', 'unknown'],
      ['', 'unknown'],
      ['!!!', 'unknown']
    ])('"%s" → intent: %s', (input, expectedIntent) => {
      const intent = intentEngine.recognize(input);
      expect(intent.type).toBe(expectedIntent);
      expect(intent.confidence).toBeLessThan(0.5);
    });
  });

  describe('Security Validation', () => {
    test.each([
      ['install firefox; rm -rf /', 'unknown'],
      ['install firefox && sudo rm -rf /', 'unknown'],
      ['show logs | grep password', 'unknown'],
      ['$(malicious command)', 'unknown'],
      ['`dangerous`', 'unknown']
    ])('Dangerous input "%s" → blocked', (input) => {
      const intent = intentEngine.recognize(input);
      expect(intent.type).toBe('unknown');
      expect(intent.confidence).toBe(0);
    });
  });

  describe('Edge Cases', () => {
    test('Very long input is handled', () => {
      const longInput = 'install ' + 'a'.repeat(1000);
      const intent = intentEngine.recognize(longInput);
      expect(intent).toBeDefined();
      expect(intent.type).toBe('install');
    });

    test('Mixed case is normalized', () => {
      const intent = intentEngine.recognize('INSTALL FIREFOX');
      expect(intent.type).toBe('install');
      const packageEntity = intent.entities.find(e => e.type === 'package');
      expect(packageEntity.value).toBe('firefox');
    });

    test('Extra whitespace is handled', () => {
      const intent = intentEngine.recognize('  install    firefox   ');
      expect(intent.type).toBe('install');
    });

    test('Punctuation is stripped', () => {
      const intent = intentEngine.recognize('install firefox!!!');
      expect(intent.type).toBe('install');
    });
  });

  describe('Persona-Specific Language', () => {
    describe('Grandma Rose (simple language)', () => {
      test.each([
        ['i need that internet thing', 'install', 'firefox'],
        ['my computer is full', 'maintenance'],
        ['nothing works', 'troubleshoot'],
        ['make it bigger', 'config', 'font-size']
      ])('"%s" is understood', (input, expectedIntent, expectedEntity) => {
        const intent = intentEngine.recognize(input);
        expect(intent.type).toBe(expectedIntent);
        
        if (expectedEntity) {
          const entity = intent.entities[0];
          expect(entity.value).toBe(expectedEntity);
        }
      });
    });

    describe('Maya (teen language)', () => {
      test.each([
        ['get me spotify', 'install', 'spotify'],
        ['discord pls', 'install', 'discord'],
        ['wifi broken', 'troubleshoot', 'network']
      ])('"%s" is understood', (input, expectedIntent, expectedEntity) => {
        const intent = intentEngine.recognize(input);
        expect(intent.type).toBe(expectedIntent);
        
        if (expectedEntity) {
          const entity = intent.entities[0];
          expect(entity.value).toBe(expectedEntity);
        }
      });
    });

    describe('Dr. Sarah (technical language)', () => {
      test.each([
        ['run garbage collection', 'maintenance'],
        ['check nginx status', 'service', 'nginx'],
        ['view system logs', 'logs']
      ])('"%s" is understood', (input, expectedIntent, expectedEntity) => {
        const intent = intentEngine.recognize(input);
        expect(intent.type).toBe(expectedIntent);
        
        if (expectedEntity) {
          const serviceEntity = intent.entities.find(e => e.type === 'service');
          expect(serviceEntity.value).toBe(expectedEntity);
        }
      });
    });
  });
});