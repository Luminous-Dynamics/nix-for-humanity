/**
 * Learning Engine for Nix for Humanity
 * Learns from user corrections and improves over time
 */
export class LearningEngine {
    constructor() {
        this.corrections = [];
        this.learnedPatterns = new Map();
        this.synonyms = new Map();
        this.loadFromStorage();
    }
    /**
     * Record a user correction
     */
    recordCorrection(originalInput, recognizedIntent, correctedIntent, accepted = true) {
        const correction = {
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
    learnFromCorrection(correction) {
        const { originalInput, correctedIntent } = correction;
        // Create a learning pattern
        const patternKey = this.normalizePattern(originalInput);
        const existing = this.learnedPatterns.get(patternKey);
        if (existing) {
            // Update existing pattern
            existing.frequency++;
            existing.lastSeen = Date.now();
            existing.confidence = Math.min(0.95, existing.confidence + 0.05);
        }
        else {
            // Create new pattern
            const newPattern = {
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
    checkLearnedPattern(input) {
        const normalized = this.normalizePattern(input);
        const learned = this.learnedPatterns.get(normalized);
        if (learned && learned.confidence > 0.6) {
            return {
                type: learned.intent,
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
    findSimilarPattern(input) {
        const inputWords = input.toLowerCase().split(' ');
        let bestMatch = null;
        let bestScore = 0;
        this.learnedPatterns.forEach(pattern => {
            const patternWords = pattern.pattern.toLowerCase().split(' ');
            const score = this.calculateSimilarity(inputWords, patternWords);
            if (score > bestScore && score > 0.7) {
                bestScore = score;
                bestMatch = pattern;
            }
        });
        if (bestMatch !== null && bestMatch) {
            const match = bestMatch;
            return {
                type: match.intent,
                confidence: match.confidence * bestScore,
                entities: this.mapToEntities(match.entities),
                original: input
            };
        }
        return null;
    }
    /**
     * Map entity record to Entity array
     */
    mapToEntities(entityMap) {
        return Object.entries(entityMap).map(([type, value]) => ({
            type: type,
            value,
            confidence: 0.9
        }));
    }
    /**
     * Calculate similarity between word arrays
     */
    calculateSimilarity(words1, words2) {
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
    expandWithSynonyms(words) {
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
    learnSynonyms(input, intent) {
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
    addSynonym(word1, word2) {
        // Add bidirectional synonym
        if (!this.synonyms.has(word1)) {
            this.synonyms.set(word1, new Set());
        }
        if (!this.synonyms.has(word2)) {
            this.synonyms.set(word2, new Set());
        }
        this.synonyms.get(word1).add(word2);
        this.synonyms.get(word2).add(word1);
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
    getSuggestions(partialInput) {
        const normalized = partialInput.toLowerCase();
        const suggestions = [];
        this.learnedPatterns.forEach(pattern => {
            if (pattern.pattern.toLowerCase().startsWith(normalized)) {
                suggestions.push(pattern.pattern);
            }
        });
        return suggestions
            .sort((a, b) => {
            const patternA = this.learnedPatterns.get(this.normalizePattern(a));
            const patternB = this.learnedPatterns.get(this.normalizePattern(b));
            return (patternB.frequency * patternB.confidence) - (patternA.frequency * patternA.confidence);
        })
            .slice(0, 5);
    }
    /**
     * Normalize pattern for storage
     */
    normalizePattern(input) {
        return input.toLowerCase().trim().replace(/[^\w\s]/g, '');
    }
    /**
     * Extract entity map from intent
     */
    extractEntityMap(intent) {
        const map = {};
        intent.entities.forEach(entity => {
            map[entity.type] = entity.value;
        });
        return map;
    }
    /**
     * Save learning data to storage
     */
    saveToStorage() {
        try {
            const data = {
                corrections: this.corrections.slice(-1000), // Keep last 1000
                patterns: Array.from(this.learnedPatterns.entries()),
                synonyms: Array.from(this.synonyms.entries()).map(([k, v]) => [k, Array.from(v)])
            };
            if (typeof window !== 'undefined' && window.localStorage) {
                localStorage.setItem('nix-humanity-learning', JSON.stringify(data));
            }
        }
        catch (e) {
            console.error('Failed to save learning data:', e);
        }
    }
    /**
     * Load learning data from storage
     */
    loadFromStorage() {
        try {
            if (typeof window !== 'undefined' && window.localStorage) {
                const stored = localStorage.getItem('nix-humanity-learning');
                if (stored) {
                    const data = JSON.parse(stored);
                    this.corrections = data.corrections || [];
                    this.learnedPatterns = new Map(data.patterns || []);
                    this.synonyms = new Map((data.synonyms || []).map(([k, v]) => [k, new Set(v)]));
                }
            }
        }
        catch (e) {
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
//# sourceMappingURL=learning-engine.js.map