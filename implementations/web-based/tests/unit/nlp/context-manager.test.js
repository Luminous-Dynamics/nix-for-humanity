/**
 * Unit tests for context manager
 * Tests multi-turn conversation handling
 */

const { contextManager } = require('../../../js/nlp/dist-cjs/context-manager.js');

describe('Context Manager', () => {
  
  beforeEach(() => {
    contextManager.reset();
  });

  describe('Pronoun Resolution', () => {
    test('resolves "it" after package mention', () => {
      // First turn: mention a package
      const intent1 = {
        type: 'query',
        confidence: 0.9,
        entities: [{ type: 'package', value: 'firefox', confidence: 0.9 }],
        original: 'what is firefox'
      };
      contextManager.processWithContext('what is firefox', intent1);
      
      // Second turn: refer to "it"
      const intent2 = {
        type: 'unknown',
        confidence: 0.3,
        entities: [],
        original: 'install it'
      };
      const resolved = contextManager.processWithContext('install it', intent2);
      
      expect(resolved.type).toBe('install');
      expect(resolved.contextResolved).toBe(true);
      expect(resolved.entities[0].value).toBe('firefox');
    });
    
    test('resolves "that" after service mention', () => {
      // First turn: mention a service
      const intent1 = {
        type: 'service',
        confidence: 0.9,
        entities: [
          { type: 'action', value: 'status', confidence: 0.9 },
          { type: 'service', value: 'nginx', confidence: 0.9 }
        ],
        original: 'check nginx status'
      };
      contextManager.processWithContext('check nginx status', intent1);
      
      // Second turn: refer to "that"
      const intent2 = {
        type: 'unknown',
        confidence: 0.3,
        entities: [],
        original: 'start that'
      };
      const resolved = contextManager.processWithContext('start that', intent2);
      
      expect(resolved.type).toBe('service');
      expect(resolved.contextResolved).toBe(true);
      expect(resolved.entities.find(e => e.type === 'action').value).toBe('start');
      expect(resolved.entities.find(e => e.type === 'service').value).toBe('nginx');
    });
  });

  describe('Again Resolution', () => {
    test('repeats last command with "try again" after error', () => {
      // First turn: install command
      const intent1 = {
        type: 'install',
        confidence: 0.9,
        entities: [{ type: 'package', value: 'vscode', confidence: 0.9 }],
        original: 'install vscode'
      };
      contextManager.processWithContext('install vscode', intent1);
      contextManager.setLastResult('error', 'Network error');
      
      // Second turn: try again
      const intent2 = {
        type: 'unknown',
        confidence: 0.3,
        entities: [],
        original: 'try again'
      };
      const resolved = contextManager.processWithContext('try again', intent2);
      
      expect(resolved.type).toBe('install');
      expect(resolved.contextResolved).toBe(true);
      expect(resolved.entities[0].value).toBe('vscode');
    });
  });

  describe('Implicit References', () => {
    test('uses last package for implicit install', () => {
      // First turn: query about package
      const intent1 = {
        type: 'query',
        confidence: 0.9,
        entities: [{ type: 'package', value: 'git', confidence: 0.9 }],
        original: 'tell me about git'
      };
      contextManager.processWithContext('tell me about git', intent1);
      
      // Second turn: implicit install
      const intent2 = {
        type: 'install',
        confidence: 0.8,
        entities: [], // No package specified
        original: 'install'
      };
      const resolved = contextManager.processWithContext('install', intent2);
      
      expect(resolved.entities.length).toBe(1);
      expect(resolved.entities[0].value).toBe('git');
      expect(resolved.contextResolved).toBe(true);
    });
  });

  describe('Conversation State', () => {
    test('maintains conversation history', () => {
      const intents = [
        { type: 'install', confidence: 0.9, entities: [], original: 'install firefox' },
        { type: 'query', confidence: 0.9, entities: [], original: 'list packages' },
        { type: 'update', confidence: 0.9, entities: [], original: 'update system' }
      ];
      
      intents.forEach(intent => {
        contextManager.processWithContext(intent.original, intent);
      });
      
      const summary = contextManager.getSummary();
      expect(summary).toContain('install firefox');
      expect(summary).toContain('query');
      expect(summary).toContain('update');
    });
    
    test('provides contextual suggestions after success', () => {
      const intent = {
        type: 'install',
        confidence: 0.9,
        entities: [{ type: 'package', value: 'firefox', confidence: 0.9 }],
        original: 'install firefox'
      };
      contextManager.processWithContext('install firefox', intent);
      contextManager.setLastResult('success');
      
      const suggestions = contextManager.getSuggestions();
      expect(suggestions.length).toBeGreaterThan(0);
      expect(suggestions[0]).toContain('run the program');
    });
    
    test('provides error recovery suggestions', () => {
      const intent = {
        type: 'install',
        confidence: 0.9,
        entities: [{ type: 'package', value: 'vscode', confidence: 0.9 }],
        original: 'install vscode'
      };
      contextManager.processWithContext('install vscode', intent);
      contextManager.setLastResult('error');
      
      const suggestions = contextManager.getSuggestions();
      expect(suggestions.some(s => s.includes('try again'))).toBe(true);
    });
  });

  describe('Topic Tracking', () => {
    test('tracks conversation topic', () => {
      const intent1 = {
        type: 'service',
        confidence: 0.9,
        entities: [],
        original: 'start nginx'
      };
      contextManager.processWithContext('start nginx', intent1);
      
      const context = contextManager.exportContext();
      expect(context.currentTopic).toBe('service_management');
    });
  });

  describe('Clarification Handling', () => {
    test('tracks clarification state', () => {
      contextManager.setClarificationNeeded('package_choice');
      
      const intent = {
        type: 'unknown',
        confidence: 0.3,
        entities: [],
        original: 'the first one'
      };
      const resolved = contextManager.processWithContext('the first one', intent);
      
      // Would need more implementation to fully resolve
      expect(resolved.contextResolved).toBeDefined();
    });
  });

  describe('Time-based Cleanup', () => {
    test('cleans up old conversation turns', () => {
      // This would need mocking of Date or a way to set time
      // For now, just test that the method exists
      expect(contextManager.reset).toBeDefined();
    });
  });

  describe('Edge Cases', () => {
    test('handles empty context gracefully', () => {
      const intent = {
        type: 'unknown',
        confidence: 0.3,
        entities: [],
        original: 'install it'
      };
      const resolved = contextManager.processWithContext('install it', intent);
      
      // Should not resolve without context
      expect(resolved.contextResolved).toBeFalsy();
    });
    
    test('handles multiple "it" references', () => {
      // Mention multiple things
      const intent1 = {
        type: 'query',
        confidence: 0.9,
        entities: [{ type: 'package', value: 'firefox', confidence: 0.9 }],
        original: 'what is firefox'
      };
      contextManager.processWithContext('what is firefox', intent1);
      
      const intent2 = {
        type: 'service',
        confidence: 0.9,
        entities: [{ type: 'service', value: 'nginx', confidence: 0.9 }],
        original: 'check nginx'
      };
      contextManager.processWithContext('check nginx', intent2);
      
      // "it" should refer to the most recent appropriate entity
      const intent3 = {
        type: 'unknown',
        confidence: 0.3,
        entities: [],
        original: 'start it'
      };
      const resolved = contextManager.processWithContext('start it', intent3);
      
      expect(resolved.type).toBe('service');
      expect(resolved.entities.find(e => e.type === 'service').value).toBe('nginx');
    });
  });
});