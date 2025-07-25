/**
 * Intent Recognition Engine for Nix for Humanity
 * Hybrid approach: Rules + Statistical + Neural (progressive enhancement)
 */

import { INTENT_PATTERNS, PatternRule } from './intent-patterns';
import { learningEngine } from './learning-engine';
import { ambiguityResolver } from './ambiguity-resolver';

export interface Intent {
  type: 'install' | 'update' | 'query' | 'troubleshoot' | 'config' | 'unknown';
  confidence: number;
  entities: Entity[];
  alternatives?: Intent[];
  original: string;
}

export interface Entity {
  type: 'package' | 'service' | 'setting' | 'problem';
  value: string;
  confidence: number;
}

/**
 * Core intent recognition engine using hybrid approach
 */
export class IntentEngine {
  private patterns: Map<string, IntentPattern>;

  constructor() {
    this.patterns = this.initializePatterns();
  }

  /**
   * Main recognition method - combines all approaches
   */
  recognize(input: string): Intent {
    const normalized = this.normalize(input);
    
    // 0. Check learned patterns first
    const learned = learningEngine.checkLearnedPattern(normalized);
    if (learned && learned.confidence > 0.8) {
      return learned;
    }
    
    // 1. Fast path: Rule-based matching
    const ruleMatch = this.matchRules(normalized);
    if (ruleMatch && ruleMatch.confidence > 0.9) {
      return ruleMatch;
    }

    // 2. Statistical matching for flexibility
    const statisticalMatch = this.statisticalMatch(normalized);
    
    // 3. Ensemble decision
    const result = this.combineResults(ruleMatch, statisticalMatch, normalized);
    
    // 4. Check for ambiguity
    if (result.alternatives && result.alternatives.length > 0) {
      const allIntents = [result, ...result.alternatives].filter(i => i.confidence > 0.3);
      const ambiguity = ambiguityResolver.resolve(allIntents);
      if (ambiguity) {
        // Return the top intent but mark it as ambiguous
        return {
          ...result,
          ambiguous: true,
          clarification: ambiguity
        } as Intent & { ambiguous?: boolean; clarification?: any };
      }
    }
    
    return result;
  }

  /**
   * Normalize input for consistent matching
   */
  private normalize(input: string): string {
    return input
      .toLowerCase()
      .trim()
      .replace(/[?!.,]/g, '')
      .replace(/\s+/g, ' ');
  }

  /**
   * Rule-based pattern matching (fast path) - Enhanced version
   */
  private matchRules(input: string): Intent | null {
    // Try each intent category
    for (const [intentType, rules] of Object.entries(INTENT_PATTERNS)) {
      for (const rule of rules) {
        for (const pattern of rule.patterns) {
          const match = input.match(pattern);
          if (match) {
            // Extract entities using the rule's extractor
            const extracted = rule.extractor ? rule.extractor(match) : {};
            const entities = this.extractedToEntities(intentType as Intent['type'], extracted);
            
            return {
              type: intentType as Intent['type'],
              confidence: 0.95,
              entities,
              original: input
            };
          }
        }
      }
    }

    // Fallback to old patterns if new ones don't match
    return this.matchOldRules(input);
  }

  /**
   * Convert extracted data to entities
   */
  private extractedToEntities(intentType: Intent['type'], extracted: any): Entity[] {
    const entities: Entity[] = [];
    
    if (extracted.package) {
      entities.push({
        type: 'package',
        value: extracted.package,
        confidence: 0.9
      });
    }
    
    if (extracted.problem) {
      entities.push({
        type: 'problem',
        value: extracted.problem,
        confidence: 0.9
      });
    }
    
    if (extracted.setting) {
      entities.push({
        type: 'setting',
        value: extracted.setting,
        confidence: 0.9
      });
    }
    
    return entities;
  }

  /**
   * Old rule-based patterns (kept for compatibility)
   */
  private matchOldRules(input: string): Intent | null {
    // Install patterns
    if (input.match(/^(install|i need|i want|get me|download)\s+(.+)$/)) {
      const packageMatch = input.match(/^(?:install|i need|i want|get me|download)\s+(.+)$/);
      const packageName = packageMatch ? this.extractPackageName(packageMatch[1]) : '';
      
      return {
        type: 'install',
        confidence: 0.95,
        entities: [{
          type: 'package',
          value: packageName,
          confidence: 0.9
        }],
        original: input
      };
    }

    // Update patterns
    if (input.match(/^(update|upgrade|check for updates|is.*up to date)/)) {
      return {
        type: 'update',
        confidence: 0.95,
        entities: [],
        original: input
      };
    }

    // Query patterns
    if (input.match(/^(what is|show me|list|what.*installed|what programs)/)) {
      return {
        type: 'query',
        confidence: 0.9,
        entities: this.extractQueryEntities(input),
        original: input
      };
    }

    // Troubleshooting patterns
    if (input.match(/(not working|broken|fix|help|problem|issue|error)/)) {
      return {
        type: 'troubleshoot',
        confidence: 0.85,
        entities: this.extractProblemEntities(input),
        original: input
      };
    }

    // Config patterns
    if (input.match(/(make.*bigger|change|configure|set up|adjust|setting)/)) {
      return {
        type: 'config',
        confidence: 0.85,
        entities: this.extractConfigEntities(input),
        original: input
      };
    }

    return null;
  }

  /**
   * Statistical matching for flexibility
   */
  private statisticalMatch(input: string): Intent {
    // Simple bag-of-words approach for MVP
    const words = input.split(' ');
    const scores = {
      install: 0,
      update: 0,
      query: 0,
      troubleshoot: 0,
      config: 0
    };

    // Score based on keyword presence
    words.forEach(word => {
      if (['install', 'need', 'want', 'get', 'download'].includes(word)) scores.install++;
      if (['update', 'upgrade', 'latest', 'new'].includes(word)) scores.update++;
      if (['what', 'show', 'list', 'tell', 'which'].includes(word)) scores.query++;
      if (['fix', 'broken', 'working', 'help', 'problem'].includes(word)) scores.troubleshoot++;
      if (['change', 'configure', 'set', 'adjust', 'make'].includes(word)) scores.config++;
    });

    // Find highest scoring intent
    const maxScore = Math.max(...Object.values(scores));
    const bestIntent = Object.entries(scores).find(([_, score]) => score === maxScore)?.[0] as Intent['type'];

    return {
      type: bestIntent || 'unknown',
      confidence: maxScore > 0 ? Math.min(maxScore * 0.3, 0.8) : 0.1,
      entities: [],
      original: input
    };
  }

  /**
   * Combine results from different methods
   */
  private combineResults(rule: Intent | null, statistical: Intent, input: string): Intent {
    if (rule && rule.confidence > 0.8) {
      return rule;
    }

    if (statistical.confidence > 0.5) {
      return {
        ...statistical,
        entities: this.extractEntitiesForType(statistical.type, input)
      };
    }

    // Fallback with alternatives
    return {
      type: 'unknown',
      confidence: 0.3,
      entities: [],
      alternatives: [
        rule,
        statistical
      ].filter(Boolean) as Intent[],
      original: input
    };
  }

  /**
   * Extract package name from various formats
   */
  private extractPackageName(text: string): string {
    // Handle common phrases
    const replacements: Record<string, string> = {
      'a web browser': 'firefox',
      'web browser': 'firefox',
      'that programming thing': 'vscode',
      'that coding program': 'vscode',
      'code editor': 'vscode',
      'text editor': 'neovim',
      'music player': 'spotify',
      'video player': 'vlc',
      'email': 'thunderbird',
      'mail': 'thunderbird'
    };

    for (const [phrase, pkg] of Object.entries(replacements)) {
      if (text.includes(phrase)) {
        return pkg;
      }
    }

    // Extract direct package name
    const packageMatch = text.match(/^([\w\-]+)$/);
    return packageMatch ? packageMatch[1] : text;
  }

  /**
   * Extract entities based on intent type
   */
  private extractEntitiesForType(type: Intent['type'], input: string): Entity[] {
    switch (type) {
      case 'install':
        return [{
          type: 'package',
          value: this.extractPackageName(input.replace(/^(install|i need|i want|get me|download)\s+/, '')),
          confidence: 0.7
        }];
      case 'query':
        return this.extractQueryEntities(input);
      case 'troubleshoot':
        return this.extractProblemEntities(input);
      case 'config':
        return this.extractConfigEntities(input);
      default:
        return [];
    }
  }

  /**
   * Extract query-specific entities
   */
  private extractQueryEntities(input: string): Entity[] {
    if (input.includes('installed')) {
      return [{
        type: 'package',
        value: 'all',
        confidence: 0.9
      }];
    }
    return [];
  }

  /**
   * Extract problem entities
   */
  private extractProblemEntities(input: string): Entity[] {
    const entities: Entity[] = [];
    
    if (input.includes('internet') || input.includes('wifi') || input.includes('network')) {
      entities.push({
        type: 'problem',
        value: 'network',
        confidence: 0.9
      });
    }
    
    if (input.includes('sound') || input.includes('audio') || input.includes('hear')) {
      entities.push({
        type: 'problem',
        value: 'audio',
        confidence: 0.9
      });
    }
    
    if (input.includes('screen') || input.includes('display') || input.includes('see')) {
      entities.push({
        type: 'problem',
        value: 'display',
        confidence: 0.9
      });
    }
    
    return entities;
  }

  /**
   * Extract configuration entities
   */
  private extractConfigEntities(input: string): Entity[] {
    const entities: Entity[] = [];
    
    if (input.includes('text') || input.includes('font')) {
      entities.push({
        type: 'setting',
        value: 'font-size',
        confidence: 0.8
      });
    }
    
    if (input.includes('bigger') || input.includes('larger')) {
      entities.push({
        type: 'setting',
        value: 'increase',
        confidence: 0.9
      });
    }
    
    if (input.includes('smaller')) {
      entities.push({
        type: 'setting',
        value: 'decrease',
        confidence: 0.9
      });
    }
    
    return entities;
  }

  /**
   * Initialize pattern database
   */
  private initializePatterns(): Map<string, IntentPattern> {
    const patterns = new Map<string, IntentPattern>();
    
    // This will be expanded with more patterns
    patterns.set('install_direct', {
      regex: /^install\s+(\S+)$/,
      type: 'install',
      confidence: 0.95
    });
    
    return patterns;
  }
}

interface IntentPattern {
  regex: RegExp;
  type: Intent['type'];
  confidence: number;
}

// Export singleton instance
export const intentEngine = new IntentEngine();