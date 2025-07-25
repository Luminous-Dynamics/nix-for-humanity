// 🎯 Intent Recognition Engine
// Reuses patterns from web-based implementation but simplified for MVP

class IntentEngine {
  constructor() {
    // Define intent patterns for our 10 safe commands
    this.patterns = [
      // Search patterns
      {
        patterns: [
          /^search\s+(?:for\s+)?(.+)$/i,
          /^find\s+(?:me\s+)?(.+)$/i,
          /^look\s+for\s+(.+)$/i,
          /^what\s+packages?\s+(?:are\s+)?(?:available\s+)?(?:for\s+)?(.+)$/i,
          /^show\s+me\s+(.+)\s+packages?$/i
        ],
        intent: {
          action: 'search',
          command: 'nix search'
        },
        extractor: (match) => ({ package: match[1].trim() })
      },

      // List installed packages
      {
        patterns: [
          /^(?:list|show)\s+installed(?:\s+packages)?$/i,
          /^what(?:'s|\s+is)\s+installed\??$/i,
          /^show\s+me\s+what(?:'s|\s+is)\s+installed$/i,
          /^my\s+packages$/i
        ],
        intent: {
          action: 'list',
          command: 'nix-env -q'
        },
        extractor: () => ({})
      },

      // System info
      {
        patterns: [
          /^system\s+info(?:rmation)?$/i,
          /^nix\s+info$/i,
          /^show\s+(?:me\s+)?system\s+(?:details|info)$/i,
          /^what(?:'s|\s+is)\s+my\s+nix\s+version\??$/i
        ],
        intent: {
          action: 'info',
          command: 'nix-info'
        },
        extractor: () => ({})
      },

      // Check system health
      {
        patterns: [
          /^check\s+system(?:\s+health)?$/i,
          /^nix\s+doctor$/i,
          /^is\s+(?:my\s+)?(?:system|nix)\s+(?:ok|healthy|working)\??$/i,
          /^diagnose\s+(?:my\s+)?system$/i
        ],
        intent: {
          action: 'check',
          command: 'nix doctor'
        },
        extractor: () => ({})
      },

      // Package info
      {
        patterns: [
          /^(?:info|information)\s+(?:about\s+)?(.+)$/i,
          /^tell\s+me\s+about\s+(.+)$/i,
          /^what(?:'s|\s+is)\s+(.+)\??$/i,
          /^describe\s+(.+)$/i
        ],
        intent: {
          action: 'info',
          command: 'nix path-info'
        },
        extractor: (match) => ({ package: match[1].trim() })
      },

      // Install packages (dry-run for MVP)
      {
        patterns: [
          /^install\s+(.+)$/i,
          /^i\s+(?:want|need)\s+(.+)$/i,
          /^get\s+(?:me\s+)?(.+)$/i,
          /^add\s+(.+)$/i,
          /^download\s+(.+)$/i
        ],
        intent: {
          action: 'install',
          command: 'nix-env -iA'
        },
        extractor: (match) => ({ package: match[1].trim() })
      },

      // Remove packages (dry-run for MVP)
      {
        patterns: [
          /^(?:remove|uninstall|delete)\s+(.+)$/i,
          /^get\s+rid\s+of\s+(.+)$/i,
          /^i\s+don'?t\s+(?:want|need)\s+(.+)(?:\s+anymore)?$/i
        ],
        intent: {
          action: 'remove',
          command: 'nix-env -e'
        },
        extractor: (match) => ({ package: match[1].trim() })
      },

      // Update system/packages
      {
        patterns: [
          /^update\s*(?:everything|all|system)?$/i,
          /^upgrade\s*(?:everything|all|system)?$/i,
          /^check\s+for\s+updates?$/i,
          /^update\s+(.+)$/i
        ],
        intent: {
          action: 'update',
          command: 'nix-channel --update'
        },
        extractor: (match) => ({ package: match[1] ? match[1].trim() : null })
      },

      // Show available updates
      {
        patterns: [
          /^what(?:'s|\s+is)\s+(?:available\s+to\s+)?updat(?:e|able)\??$/i,
          /^show\s+(?:me\s+)?updates?$/i,
          /^list\s+updates?$/i
        ],
        intent: {
          action: 'list-updates',
          command: 'nix-env -u --dry-run'
        },
        extractor: () => ({})
      },

      // Garbage collection
      {
        patterns: [
          /^clean(?:\s+up)?\s*(?:my\s+)?(?:system|space|disk)?$/i,
          /^free\s+(?:up\s+)?space$/i,
          /^garbage\s+collect$/i,
          /^remove\s+(?:old|unused)\s+(?:packages|stuff)$/i
        ],
        intent: {
          action: 'garbage-collect',
          command: 'nix-collect-garbage'
        },
        extractor: () => ({})
      }
    ];

    // Common variations and corrections
    this.corrections = new Map([
      ['isntall', 'install'],
      ['intall', 'install'],
      ['serach', 'search'],
      ['fnd', 'find'],
      ['lst', 'list'],
      ['python3', 'python'],
      ['fire fox', 'firefox'],
      ['vs code', 'vscode']
    ]);
  }

  async recognize(input) {
    // Normalize input
    const normalized = this.normalize(input);
    
    // Try pattern matching first (fast path)
    for (const patternGroup of this.patterns) {
      for (const pattern of patternGroup.patterns) {
        const match = normalized.match(pattern);
        if (match) {
          const entities = patternGroup.extractor(match);
          return {
            ...patternGroup.intent,
            ...entities,
            confidence: 0.95,
            originalInput: input
          };
        }
      }
    }

    // If no pattern matches, try fuzzy matching
    return this.fuzzyMatch(normalized, input);
  }

  normalize(input) {
    let normalized = input.toLowerCase().trim();
    
    // Apply corrections
    for (const [typo, correct] of this.corrections) {
      normalized = normalized.replace(new RegExp(typo, 'gi'), correct);
    }
    
    // Remove extra spaces
    normalized = normalized.replace(/\s+/g, ' ');
    
    return normalized;
  }

  fuzzyMatch(normalized, originalInput) {
    // Simple fuzzy matching for MVP
    const words = normalized.split(' ');
    
    // Check for key action words
    if (words.includes('search') || words.includes('find')) {
      return {
        action: 'search',
        command: 'nix search',
        package: words.filter(w => !['search', 'find', 'for'].includes(w)).join(' '),
        confidence: 0.7,
        originalInput
      };
    }

    if (words.includes('list') || words.includes('installed')) {
      return {
        action: 'list',
        command: 'nix-env -q',
        confidence: 0.7,
        originalInput
      };
    }

    // No match found
    return {
      action: 'unknown',
      confidence: 0.0,
      originalInput,
      normalized
    };
  }

  getSuggestions(input) {
    // Provide helpful suggestions when intent is unclear
    return [
      "search [package name] - Find available packages",
      "list installed - Show what's installed",
      "system info - Display system information",
      "check system - Run health diagnostics"
    ];
  }
}

module.exports = IntentEngine;