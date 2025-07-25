import { RuleBasedEngine } from './RuleBasedEngine';
import { StatisticalEngine } from './StatisticalEngine';
import { Intent, Context, NLPResult } from './types';

export class NLPEngine {
  private ruleEngine: RuleBasedEngine;
  private statisticalEngine: StatisticalEngine;
  // Neural engine will be loaded on demand
  private neuralEngine?: any;

  constructor() {
    this.ruleEngine = new RuleBasedEngine();
    this.statisticalEngine = new StatisticalEngine();
  }

  async processInput(input: string, context?: Context): Promise<NLPResult> {
    const startTime = Date.now();
    
    // Normalize input
    const normalizedInput = this.normalizeInput(input);
    
    // Layer 1: Try rule-based engine first (fastest, handles 95% of cases)
    const ruleResult = this.ruleEngine.match(normalizedInput);
    if (ruleResult.confidence > 0.95) {
      return {
        ...ruleResult,
        processingTime: Date.now() - startTime,
        engine: 'rule-based'
      };
    }
    
    // Layer 2: Try statistical engine for variations
    const statResult = await this.statisticalEngine.match(normalizedInput, context);
    if (statResult.confidence > 0.85) {
      return {
        ...statResult,
        processingTime: Date.now() - startTime,
        engine: 'statistical'
      };
    }
    
    // Layer 3: Load neural engine if needed (for complex understanding)
    if (!this.neuralEngine && statResult.confidence < 0.85) {
      // In real implementation, this would load a small neural model
      // For now, we'll return the best result we have
      console.log('Would load neural engine here for complex query:', normalizedInput);
    }
    
    // Return best result
    return {
      ...(ruleResult.confidence > statResult.confidence ? ruleResult : statResult),
      processingTime: Date.now() - startTime,
      engine: ruleResult.confidence > statResult.confidence ? 'rule-based' : 'statistical'
    };
  }

  private normalizeInput(input: string): string {
    return input
      .toLowerCase()
      .trim()
      .replace(/\s+/g, ' ')  // Normalize whitespace
      .replace(/['']/g, "'") // Normalize quotes
      .replace(/[""]/g, '"');
  }

  // Get all available intents for documentation/testing
  getAvailableIntents(): string[] {
    return this.ruleEngine.getAvailableIntents();
  }

  // Add new patterns dynamically (for learning)
  addPattern(intent: string, pattern: string): void {
    this.ruleEngine.addPattern(intent, pattern);
    this.statisticalEngine.addTrainingData(pattern, intent);
  }
}