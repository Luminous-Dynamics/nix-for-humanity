/**
 * Learning Engine for Nix for Humanity
 * Learns from user corrections and improves over time
 */

import { Intent } from './intent-engine';

export interface Correction {
  originalInput: string;
  recognizedIntent: Intent;
  correctedIntent: Intent;
  timestamp: number;
  accepted: boolean;
}

export interface LearningPattern {
  pattern: string;
  intent: string;
  entities: Record<string, string>;
  confidence: number;
  frequency: number;
  lastSeen: number;
}

export class LearningEngine {
  private corrections: Correction[] = [];
  private learnedPatterns: Map<string, LearningPattern> = new Map();
  private synonyms: Map<string, Set<string>> = new Map();
  
  constructor() {
    this.loadFromStorage();
  }

  /**
   * Record a user correction
   */
  recordCorrection(
    originalInput: string,
    recognizedIntent: Intent,
    correctedIntent: Intent,
    accepted: boolean = true
  ) {
    const correction: Correction = {
      originalInput,
      recognizedIntent,
      correctedIntent,
      timestamp: Date.now(),
      accepted
    };

    this.corrections.push(correction);
    
    if (accepted) {
      this.learnFromCorrection(correction);
    }
    
    this.saveToStorage();
  }

  /**
   * Learn from a correction
   */
  private learnFromCorrection(correction: Correction) {
    const { originalInput, correctedIntent } = correction;
    
    // Create a learning pattern
    const patternKey = this.normalizePattern(originalInput);
    const existing = this.learnedPatterns.get(patternKey);
    
    if (existing) {
      // Update existing pattern
      existing.frequency++;
      existing.lastSeen = Date.now();
      existing.confidence = Math.min(0.95, existing.confidence + 0.05);
    } else {
      // Create new pattern
      const newPattern: LearningPattern = {
        pattern: originalInput,
        intent: correctedIntent.type,
        entities: this.extractEntityMap(correctedIntent),
        confidence: 0.7,
        frequency: 1,
        lastSeen: Date.now()
      };
      this.learnedPatterns.set(patternKey, newPattern);
    }

    // Learn synonyms
    this.learnSynonyms(originalInput, correctedIntent);
  }

  /**
   * Check if we've learned this pattern
   */
  checkLearnedPattern(input: string): Intent | null {
    const normalized = this.normalizePattern(input);
    const learned = this.learnedPatterns.get(normalized);
    
    if (learned && learned.confidence > 0.6) {
      return {
        type: learned.intent as Intent['type'],
        confidence: learned.confidence,
        entities: this.mapToEntities(learned.entities),
        original: input
      };
    }
    
    // Check for similar patterns
    return this.findSimilarPattern(input);
  }

  /**
   * Find similar learned patterns
   */
  private findSimilarPattern(input: string): Intent | null {
    const inputWords = input.toLowerCase().split(' ');
    let bestMatch: LearningPattern | null = null;
    let bestScore = 0;

    this.learnedPatterns.forEach(pattern => {
      const patternWords = pattern.pattern.toLowerCase().split(' ');
      const score = this.calculateSimilarity(inputWords, patternWords);
      
      if (score > bestScore && score > 0.7) {
        bestScore = score;
        bestMatch = pattern;
      }
    });

    if (bestMatch) {
      return {
        type: bestMatch.intent as Intent['type'],
        confidence: bestMatch.confidence * bestScore,
        entities: this.mapToEntities(bestMatch.entities),
        original: input
      };
    }

    return null;
  }

  /**
   * Calculate similarity between word arrays
   */
  private calculateSimilarity(words1: string[], words2: string[]): number {
    const set1 = new Set(words1);
    const set2 = new Set(words2);
    
    // Expand with synonyms
    const expanded1 = this.expandWithSynonyms(set1);
    const expanded2 = this.expandWithSynonyms(set2);
    
    const intersection = new Set([...expanded1].filter(x => expanded2.has(x)));
    const union = new Set([...expanded1, ...expanded2]);
    
    return intersection.size / union.size;
  }

  /**
   * Expand word set with learned synonyms
   */
  private expandWithSynonyms(words: Set<string>): Set<string> {
    const expanded = new Set(words);
    
    words.forEach(word => {
      const synonyms = this.synonyms.get(word);
      if (synonyms) {
        synonyms.forEach(syn => expanded.add(syn));
      }
    });
    
    return expanded;
  }

  /**
   * Learn synonyms from corrections
   */
  private learnSynonyms(input: string, intent: Intent) {
    // Extract package synonyms
    if (intent.type === 'install') {
      const packageEntity = intent.entities.find(e => e.type === 'package');
      if (packageEntity) {
        const words = input.toLowerCase().split(' ');
        words.forEach(word => {
          if (word !== packageEntity.value && word.length > 2) {
            this.addSynonym(word, packageEntity.value);
          }
        });
      }
    }
  }

  /**
   * Add a synonym relationship
   */
  private addSynonym(word1: string, word2: string) {
    // Add bidirectional synonym
    if (!this.synonyms.has(word1)) {
      this.synonyms.set(word1, new Set());
    }
    if (!this.synonyms.has(word2)) {
      this.synonyms.set(word2, new Set());
    }
    
    this.synonyms.get(word1)!.add(word2);
    this.synonyms.get(word2)!.add(word1);
  }

  /**
   * Get learning statistics
   */
  getStats() {
    const totalCorrections = this.corrections.length;
    const acceptedCorrections = this.corrections.filter(c => c.accepted).length;
    const learnedPatterns = this.learnedPatterns.size;
    const synonymPairs = this.synonyms.size;
    
    // Calculate accuracy improvement
    const recentCorrections = this.corrections.slice(-100);
    const recentAccuracy = recentCorrections.length > 0 
      ? (recentCorrections.filter(c => !c.accepted).length / recentCorrections.length)
      : 0;

    return {
      totalCorrections,
      acceptedCorrections,
      learnedPatterns,
      synonymPairs,
      recentAccuracy,
      improvementRate: (1 - recentAccuracy) * 100
    };
  }

  /**
   * Get suggestions for a partial input
   */
  getSuggestions(partialInput: string): string[] {
    const normalized = partialInput.toLowerCase();
    const suggestions: string[] = [];
    
    this.learnedPatterns.forEach(pattern => {
      if (pattern.pattern.toLowerCase().startsWith(normalized)) {
        suggestions.push(pattern.pattern);
      }
    });
    
    return suggestions
      .sort((a, b) => {
        const patternA = this.learnedPatterns.get(this.normalizePattern(a))!;
        const patternB = this.learnedPatterns.get(this.normalizePattern(b))!;
        return (patternB.frequency * patternB.confidence) - (patternA.frequency * patternA.confidence);
      })
      .slice(0, 5);
  }

  /**
   * Normalize pattern for storage
   */
  private normalizePattern(input: string): string {
    return input.toLowerCase().trim().replace(/[^\w\s]/g, '');
  }

  /**
   * Extract entity map from intent
   */
  private extractEntityMap(intent: Intent): Record<string, string> {
    const map: Record<string, string> = {};
    intent.entities.forEach(entity => {
      map[entity.type] = entity.value;
    });
    return map;
  }

  /**
   * Convert entity map to entities array
   */
  private mapToEntities(entityMap: Record<string, string>): Intent['entities'] {
    return Object.entries(entityMap).map(([type, value]) => ({
      type: type as any,
      value,
      confidence: 0.9
    }));
  }

  /**
   * Save learning data to storage
   */
  private saveToStorage() {
    try {
      const data = {
        corrections: this.corrections.slice(-1000), // Keep last 1000
        patterns: Array.from(this.learnedPatterns.entries()),
        synonyms: Array.from(this.synonyms.entries()).map(([k, v]) => [k, Array.from(v)])
      };
      
      if (typeof window !== 'undefined' && window.localStorage) {
        localStorage.setItem('nix-humanity-learning', JSON.stringify(data));
      }
    } catch (e) {
      console.error('Failed to save learning data:', e);
    }
  }

  /**
   * Load learning data from storage
   */
  private loadFromStorage() {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        const stored = localStorage.getItem('nix-humanity-learning');
        if (stored) {
          const data = JSON.parse(stored);
          
          this.corrections = data.corrections || [];
          this.learnedPatterns = new Map(data.patterns || []);
          this.synonyms = new Map(
            (data.synonyms || []).map(([k, v]: [string, string[]]) => [k, new Set(v)])
          );
        }
      }
    } catch (e) {
      console.error('Failed to load learning data:', e);
    }
  }

  /**
   * Export learning data for analysis
   */
  exportLearningData() {
    return {
      corrections: this.corrections,
      patterns: Array.from(this.learnedPatterns.values()),
      synonyms: Array.from(this.synonyms.entries()).map(([k, v]) => ({
        word: k,
        synonyms: Array.from(v)
      }))
    };
  }
}

// Export singleton
export const learningEngine = new LearningEngine();