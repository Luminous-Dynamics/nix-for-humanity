import { Intent, Context, IntentAction } from './types';

// Simple statistical engine for handling variations and typos
export class StatisticalEngine {
  private vocabulary: Map<string, string[]> = new Map([
    ['install', ['instal', 'installl', 'intall', 'instsll', 'istall']],
    ['remove', ['rmove', 'remov', 'removve', 'delet', 'uninstal']],
    ['update', ['updae', 'upadte', 'upgrate', 'updte', 'refresh']],
    ['firefox', ['firefx', 'firfox', 'firefoz', 'mozila', 'ffox']],
    ['package', ['packge', 'pakage', 'pckage', 'pkg']],
  ]);

  private intentKeywords: Map<IntentAction, string[]> = new Map([
    ['install_package', ['install', 'get', 'add', 'need', 'want', 'download', 'setup']],
    ['remove_package', ['remove', 'uninstall', 'delete', 'rid', 'uninstal']],
    ['update_system', ['update', 'upgrade', 'refresh', 'current', 'latest']],
    ['search_packages', ['search', 'find', 'look', 'what', 'which']],
    ['get_help', ['help', 'how', 'explain', 'what', 'guide']],
    ['troubleshoot', ['broken', 'working', 'fix', 'problem', 'issue', 'wrong']],
  ]);

  async match(input: string, context?: Context): Promise<Intent> {
    // Tokenize and clean input
    const tokens = this.tokenize(input);
    const correctedTokens = tokens.map(token => this.correctSpelling(token));
    
    // Score each intent based on keyword matches
    const scores = new Map<IntentAction, number>();
    
    for (const [intent, keywords] of this.intentKeywords.entries()) {
      let score = 0;
      
      for (const token of correctedTokens) {
        if (keywords.includes(token)) {
          score += 1;
        }
        // Partial matches
        for (const keyword of keywords) {
          if (this.fuzzyMatch(token, keyword)) {
            score += 0.5;
          }
        }
      }
      
      scores.set(intent, score);
    }
    
    // Find best matching intent
    let bestIntent: IntentAction = 'unknown';
    let bestScore = 0;
    
    for (const [intent, score] of scores.entries()) {
      if (score > bestScore) {
        bestScore = score;
        bestIntent = intent;
      }
    }
    
    // Calculate confidence based on score
    const confidence = Math.min(bestScore / 3, 0.9); // Cap at 0.9 for statistical
    
    // Extract entities based on intent
    const entities = this.extractEntities(correctedTokens, bestIntent);
    
    return {
      action: bestIntent,
      entities,
      confidence,
      rawInput: input
    };
  }

  private tokenize(input: string): string[] {
    return input.toLowerCase().split(/\s+/).filter(t => t.length > 0);
  }

  private correctSpelling(word: string): string {
    // Check if word is in our typo map
    for (const [correct, typos] of this.vocabulary.entries()) {
      if (typos.includes(word)) {
        return correct;
      }
    }
    return word;
  }

  private fuzzyMatch(word1: string, word2: string): boolean {
    // Simple Levenshtein distance check
    if (Math.abs(word1.length - word2.length) > 2) return false;
    
    let distance = 0;
    for (let i = 0; i < Math.min(word1.length, word2.length); i++) {
      if (word1[i] !== word2[i]) distance++;
    }
    
    return distance <= 2;
  }

  private extractEntities(tokens: string[], intent: IntentAction): any[] {
    const entities = [];
    
    // Simple entity extraction based on intent
    if (intent === 'install_package' || intent === 'remove_package') {
      // Find package name (usually after the action verb)
      const actionIndex = tokens.findIndex(t => 
        ['install', 'remove', 'get', 'add', 'delete'].includes(t)
      );
      
      if (actionIndex >= 0 && actionIndex < tokens.length - 1) {
        entities.push({
          type: 'package',
          value: tokens.slice(actionIndex + 1).join(' '),
          confidence: 0.8
        });
      }
    }
    
    return entities;
  }

  addTrainingData(input: string, intent: IntentAction): void {
    // In a real implementation, this would update the model
    console.log(`Learning: "${input}" → ${intent}`);
  }
}