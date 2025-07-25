/**
 * Intent Recognition Engine for Nix for Humanity
 * Hybrid approach: Rules + Statistical + Neural (progressive enhancement)
 */
import { INTENT_PATTERNS } from './intent-patterns';
import { learningEngine } from './learning-engine';
import { ambiguityResolver } from './ambiguity-resolver';
import { typoCorrector } from './typo-corrector';
import { unsupportedHandler } from './unsupported-handler';
import { usageTracker } from './usage-tracker';
import { contextManager } from './context-manager';
/**
 * Core intent recognition engine using hybrid approach
 */
export class IntentEngine {
    constructor() {
        this.patterns = this.initializePatterns();
    }
    /**
     * Check for dangerous command injection patterns
     */
    containsDangerousPatterns(input) {
        const dangerousPatterns = [
            /[;&|`$]/, // Command separators and substitution
            /\.\.[\/\\]/, // Path traversal
            />|</, // Redirection
            /\|\|/, // OR operator
            /&&/, // AND operator
            /\$\(.*\)/, // Command substitution
            /`.*`/, // Backtick substitution
            /--option\s+sandbox\s+false/i, // Sandbox bypass
            /rm\s+-rf/i, // Dangerous rm
            /\/etc\/(passwd|shadow)/i // Sensitive files
        ];
        return dangerousPatterns.some(pattern => pattern.test(input));
    }
    /**
     * Main recognition method - combines all approaches
     */
    recognize(input) {
        // Security check first
        if (this.containsDangerousPatterns(input)) {
            return {
                type: 'unknown',
                confidence: 0,
                entities: [],
                original: input,
                alternatives: [{
                        type: 'unknown',
                        confidence: 0,
                        entities: [],
                        original: 'Input contains potentially unsafe characters. Please rephrase without special characters.'
                    }]
            };
        }
        const normalized = this.normalize(input);
        // 0. Apply typo correction
        const corrected = typoCorrector.correct(normalized);
        const inputToProcess = corrected !== normalized ? corrected : normalized;
        // 0.5. Check learned patterns first
        const learned = learningEngine.checkLearnedPattern(inputToProcess);
        if (learned && learned.confidence > 0.8) {
            return learned;
        }
        // 1. Fast path: Rule-based matching
        const ruleMatch = this.matchRules(inputToProcess);
        if (ruleMatch && ruleMatch.confidence > 0.9) {
            return ruleMatch;
        }
        // 2. Statistical matching for flexibility
        const statisticalMatch = this.statisticalMatch(inputToProcess);
        // 3. Ensemble decision
        let result = this.combineResults(ruleMatch, statisticalMatch, inputToProcess);
        // 3.5. Apply context awareness
        result = contextManager.processWithContext(input, result);
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
                };
            }
        }
        // 5. Handle unsupported commands
        if (result.type === 'unknown') {
            unsupportedHandler.handleUnsupported(input, result);
            usageTracker.trackUnsupported();
        }
        // 6. Track usage (privacy-preserving)
        usageTracker.trackIntent(result.type, result.confidence);
        return result;
    }
    /**
     * Normalize input for consistent matching
     */
    normalize(input) {
        return input
            .toLowerCase()
            .trim()
            .replace(/[?!.,]/g, '')
            .replace(/\s+/g, ' ');
    }
    /**
     * Rule-based pattern matching (fast path) - Enhanced version
     */
    matchRules(input) {
        // Try each intent category
        for (const [intentType, rules] of Object.entries(INTENT_PATTERNS)) {
            for (const rule of rules) {
                for (const pattern of rule.patterns) {
                    const match = input.match(pattern);
                    if (match) {
                        // Extract entities using the rule's extractor
                        const extracted = rule.extractor ? rule.extractor(match) : {};
                        const entities = this.extractedToEntities(intentType, extracted);
                        return {
                            type: intentType,
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
    extractedToEntities(intentType, extracted) {
        const entities = [];
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
        if (extracted.action) {
            entities.push({
                type: 'action',
                value: extracted.action,
                confidence: 0.9
            });
        }
        if (extracted.serviceName) {
            entities.push({
                type: 'service',
                value: extracted.serviceName,
                confidence: 0.9
            });
        }
        if (extracted.logType) {
            entities.push({
                type: 'logType',
                value: extracted.logType,
                confidence: 0.9
            });
        }
        if (extracted.timeframe) {
            entities.push({
                type: 'timeframe',
                value: extracted.timeframe,
                confidence: 0.9
            });
        }
        return entities;
    }
    /**
     * Old rule-based patterns (kept for compatibility)
     */
    matchOldRules(input) {
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
    statisticalMatch(input) {
        // Simple bag-of-words approach for MVP
        const words = input.split(' ');
        const scores = {
            install: 0,
            update: 0,
            query: 0,
            troubleshoot: 0,
            config: 0,
            maintenance: 0,
            logs: 0,
            service: 0
        };
        // Score based on keyword presence
        words.forEach(word => {
            if (['install', 'need', 'want', 'get', 'download'].includes(word))
                scores.install++;
            if (['update', 'upgrade', 'latest', 'new'].includes(word))
                scores.update++;
            if (['what', 'show', 'list', 'tell', 'which'].includes(word))
                scores.query++;
            if (['fix', 'broken', 'working', 'help', 'problem'].includes(word))
                scores.troubleshoot++;
            if (['change', 'configure', 'set', 'adjust', 'make'].includes(word))
                scores.config++;
            if (['clean', 'free', 'space', 'garbage', 'collection', 'disk'].includes(word))
                scores.maintenance++;
            if (['log', 'logs', 'error', 'wrong', 'fail', 'why'].includes(word))
                scores.logs++;
            if (['running', 'service', 'start', 'stop', 'status', 'active'].includes(word))
                scores.service++;
        });
        // Find highest scoring intent
        const maxScore = Math.max(...Object.values(scores));
        const bestIntent = Object.entries(scores).find(([_, score]) => score === maxScore)?.[0];
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
    combineResults(rule, statistical, input) {
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
            ].filter(Boolean),
            original: input
        };
    }
    /**
     * Extract package name from various formats
     */
    extractPackageName(text) {
        // Handle common phrases
        const replacements = {
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
    extractEntitiesForType(type, input) {
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
    extractQueryEntities(input) {
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
    extractProblemEntities(input) {
        const entities = [];
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
    extractConfigEntities(input) {
        const entities = [];
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
    initializePatterns() {
        const patterns = new Map();
        // This will be expanded with more patterns
        patterns.set('install_direct', {
            regex: /^install\s+(\S+)$/,
            type: 'install',
            confidence: 0.95
        });
        return patterns;
    }
}
// Export singleton instance
export const intentEngine = new IntentEngine();
//# sourceMappingURL=intent-engine.js.map