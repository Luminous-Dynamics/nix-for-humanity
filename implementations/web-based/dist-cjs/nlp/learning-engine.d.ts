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
export declare class LearningEngine {
    private corrections;
    private learnedPatterns;
    private synonyms;
    constructor();
    /**
     * Record a user correction
     */
    recordCorrection(originalInput: string, recognizedIntent: Intent, correctedIntent: Intent, accepted?: boolean): void;
    /**
     * Learn from a correction
     */
    private learnFromCorrection;
    /**
     * Check if we've learned this pattern
     */
    checkLearnedPattern(input: string): Intent | null;
    /**
     * Find similar learned patterns
     */
    private findSimilarPattern;
    /**
     * Map entity record to Entity array
     */
    private mapToEntities;
    /**
     * Calculate similarity between word arrays
     */
    private calculateSimilarity;
    /**
     * Expand word set with learned synonyms
     */
    private expandWithSynonyms;
    /**
     * Learn synonyms from corrections
     */
    private learnSynonyms;
    /**
     * Add a synonym relationship
     */
    private addSynonym;
    /**
     * Get learning statistics
     */
    getStats(): {
        totalCorrections: number;
        acceptedCorrections: number;
        learnedPatterns: number;
        synonymPairs: number;
        recentAccuracy: number;
        improvementRate: number;
    };
    /**
     * Get suggestions for a partial input
     */
    getSuggestions(partialInput: string): string[];
    /**
     * Normalize pattern for storage
     */
    private normalizePattern;
    /**
     * Extract entity map from intent
     */
    private extractEntityMap;
    /**
     * Save learning data to storage
     */
    private saveToStorage;
    /**
     * Load learning data from storage
     */
    private loadFromStorage;
    /**
     * Export learning data for analysis
     */
    exportLearningData(): {
        corrections: Correction[];
        patterns: LearningPattern[];
        synonyms: {
            word: string;
            synonyms: string[];
        }[];
    };
}
export declare const learningEngine: LearningEngine;
