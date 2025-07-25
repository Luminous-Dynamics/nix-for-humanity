import { Intent, Pattern, IntentAction, Entity } from './types';

export class RuleBasedEngine {
  private patterns: Pattern[] = [
    // Install patterns
    {
      pattern: /^install\s+(.+)$/i,
      intent: 'install_package',
      entities: ['package'],
      confidence: 0.99
    },
    {
      pattern: /^(?:get|add|download)\s+(.+)$/i,
      intent: 'install_package',
      entities: ['package'],
      confidence: 0.95
    },
    {
      pattern: /^i\s+(?:need|want)\s+(.+)$/i,
      intent: 'install_package',
      entities: ['package'],
      confidence: 0.92
    },
    
    // Remove patterns
    {
      pattern: /^(?:remove|uninstall|delete)\s+(.+)$/i,
      intent: 'remove_package',
      entities: ['package'],
      confidence: 0.99
    },
    {
      pattern: /^get\s+rid\s+of\s+(.+)$/i,
      intent: 'remove_package',
      entities: ['package'],
      confidence: 0.95
    },
    
    // Update patterns
    {
      pattern: /^update(?:\s+system)?$/i,
      intent: 'update_system',
      entities: [],
      confidence: 0.99
    },
    {
      pattern: /^(?:upgrade|refresh)\s*(?:everything)?$/i,
      intent: 'update_system',
      entities: [],
      confidence: 0.95
    },
    
    // Search patterns
    {
      pattern: /^(?:search|find|look for)\s+(.+)$/i,
      intent: 'search_packages',
      entities: ['query'],
      confidence: 0.99
    },
    {
      pattern: /^what\s+(?:packages?|programs?)\s+(?:for|to)\s+(.+)$/i,
      intent: 'search_packages',
      entities: ['query'],
      confidence: 0.92
    },
    
    // Help patterns
    {
      pattern: /^help(?:\s+(?:with|me))?\s*(.*)$/i,
      intent: 'get_help',
      entities: ['topic'],
      confidence: 0.99
    },
    {
      pattern: /^(?:how\s+do\s+i|how\s+to)\s+(.+)$/i,
      intent: 'get_help',
      entities: ['topic'],
      confidence: 0.95
    },
    
    // Troubleshooting patterns
    {
      pattern: /^(?:my\s+)?(.+?)\s+(?:is\s+)?(?:not\s+working|broken|isn't\s+working)$/i,
      intent: 'troubleshoot',
      entities: ['component'],
      confidence: 0.95
    },
    {
      pattern: /^(?:fix|repair)\s+(?:my\s+)?(.+)$/i,
      intent: 'troubleshoot',
      entities: ['component'],
      confidence: 0.92
    },
    
    // Query patterns
    {
      pattern: /^(?:show|list|what)\s+(?:is|are)\s+(?:my\s+)?(.+)$/i,
      intent: 'query_info',
      entities: ['subject'],
      confidence: 0.95
    },
    {
      pattern: /^(?:disk|memory|cpu)\s+(?:usage|space)$/i,
      intent: 'query_info',
      entities: [],
      confidence: 0.99
    }
  ];

  match(input: string): Intent {
    // Try each pattern
    for (const pattern of this.patterns) {
      const regex = pattern.pattern instanceof RegExp ? pattern.pattern : new RegExp(pattern.pattern);
      const match = input.match(regex);
      
      if (match) {
        const entities: Entity[] = [];
        
        // Extract entities from capture groups
        if (pattern.entities && match.length > 1) {
          for (let i = 0; i < pattern.entities.length && i < match.length - 1; i++) {
            if (match[i + 1]) {
              entities.push({
                type: pattern.entities[i] as any,
                value: match[i + 1].trim(),
                confidence: pattern.confidence
              });
            }
          }
        }
        
        return {
          action: pattern.intent,
          entities,
          confidence: pattern.confidence,
          rawInput: input
        };
      }
    }
    
    // No match found
    return {
      action: 'unknown',
      entities: [],
      confidence: 0.0,
      rawInput: input
    };
  }

  getAvailableIntents(): string[] {
    const intents = new Set<string>();
    this.patterns.forEach(p => intents.add(p.intent));
    return Array.from(intents);
  }

  addPattern(intent: IntentAction, pattern: string): void {
    this.patterns.push({
      pattern: new RegExp(pattern, 'i'),
      intent,
      entities: [],
      confidence: 0.9
    });
  }
}