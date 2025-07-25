"use strict";
/**
 * Intent Recognition Layer (Pure Functions)
 * No side effects, no I/O, just pattern matching
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.recognizeIntent = recognizeIntent;
exports.suggestIntent = suggestIntent;
// Pattern definitions for intent recognition
const INTENT_PATTERNS = [
    // Install patterns
    {
        type: 'install',
        patterns: [
            /^(?:install|add|get|i need|i want|put|download|setup)\s+(.+)$/i,
            /^(.+)\s+(?:is missing|not installed|isn't installed)$/i,
            /^(?:can you|please|could you)\s+(?:install|add|get)\s+(.+)$/i
        ],
        extractEntities: (match) => [{
                type: 'package',
                value: normalizePackageName(match[1] || match[0]),
                confidence: 0.9
            }]
    },
    // Remove patterns
    {
        type: 'remove',
        patterns: [
            /^(?:remove|uninstall|delete|get rid of|take off)\s+(.+)$/i,
            /^(?:i don't need|don't want)\s+(.+)\s+(?:anymore|any more)$/i
        ],
        extractEntities: (match) => [{
                type: 'package',
                value: normalizePackageName(match[1]),
                confidence: 0.9
            }]
    },
    // Update patterns
    {
        type: 'update',
        patterns: [
            /^(?:update|upgrade|refresh)\s*(?:system|everything|all)?$/i,
            /^(?:get|install)\s+(?:latest|updates|upgrades)$/i,
            /^(?:make|get)\s+everything\s+(?:current|up to date|updated)$/i
        ],
        extractEntities: () => []
    },
    // Query patterns
    {
        type: 'query',
        patterns: [
            /^(?:what's|what is|whats|show|list)\s+installed$/i,
            /^(?:show|list|display)\s+(?:my\s+)?(?:packages|programs|software)$/i,
            /^what\s+(?:do i have|packages|programs)(?:\s+installed)?$/i
        ],
        extractEntities: () => []
    },
    // Service patterns
    {
        type: 'service',
        patterns: [
            /^(?:is|check if)\s+(.+?)\s+(?:running|active|started|on)$/i,
            /^(?:start|stop|restart|enable|disable)\s+(.+?)(?:\s+service)?$/i,
            /^(?:show|check)\s+(?:status of\s+)?(.+?)(?:\s+service)?$/i,
            /^(?:turn on|turn off|launch|kill)\s+(.+)$/i
        ],
        extractEntities: (match) => {
            const serviceName = normalizeServiceName(match[1]);
            const action = extractServiceAction(match[0]);
            return [
                { type: 'service', value: serviceName, confidence: 0.85 },
                { type: 'action', value: action, confidence: 0.9 }
            ];
        }
    },
    // Maintenance patterns
    {
        type: 'maintenance',
        patterns: [
            /^(?:free up|clean up|clear)\s+(?:disk\s+)?space$/i,
            /^(?:clean|cleanup|garbage collect|gc)(?:\s+system)?$/i,
            /^(?:remove|delete)\s+(?:old|unused)\s+(?:packages|stuff|files)$/i
        ],
        extractEntities: () => [{
                type: 'action',
                value: 'garbage-collection',
                confidence: 0.95
            }]
    },
    // Log patterns
    {
        type: 'logs',
        patterns: [
            /^(?:show|check|view|display)\s+(?:system\s+)?logs?$/i,
            /^(?:show|check)\s+(?:recent|latest|last)\s+(?:errors?|logs?)$/i,
            /^what(?:'s| is)\s+(?:in the\s+)?(?:error\s+)?logs?$/i
        ],
        extractEntities: (match) => {
            const entities = [];
            if (/recent|latest|last/.test(match[0])) {
                entities.push({ type: 'timeframe', value: 'recent', confidence: 0.9 });
            }
            if (/error/.test(match[0])) {
                entities.push({ type: 'logType', value: 'errors', confidence: 0.9 });
            }
            return entities;
        }
    },
    // Network troubleshooting
    {
        type: 'troubleshoot',
        patterns: [
            /^(?:my\s+)?(?:wifi|network|internet)\s+(?:isn't|is not|not)\s+working$/i,
            /^(?:can't|cannot)\s+(?:connect|get online|access internet)$/i,
            /^(?:fix|troubleshoot|diagnose)\s+(?:my\s+)?(?:network|wifi|internet|connection)$/i,
            /^(?:no|lost)\s+(?:internet|network|wifi|connection)$/i
        ],
        extractEntities: () => [{
                type: 'problem',
                value: 'network',
                confidence: 0.9
            }]
    },
    // Display configuration
    {
        type: 'config',
        patterns: [
            /^(?:make|set)\s+(?:text|font)\s+(?:bigger|larger|smaller)$/i,
            /^(?:increase|decrease)\s+(?:font|text)\s+size$/i,
            /^(?:change|adjust|set)\s+(?:display|screen|monitor)\s+(?:settings?|resolution)$/i
        ],
        extractEntities: (match) => {
            if (/bigger|larger|increase/.test(match[0])) {
                return [{ type: 'setting', value: 'font-size-increase', confidence: 0.9 }];
            }
            else if (/smaller|decrease/.test(match[0])) {
                return [{ type: 'setting', value: 'font-size-decrease', confidence: 0.9 }];
            }
            return [{ type: 'setting', value: 'display', confidence: 0.7 }];
        }
    }
];
/**
 * Recognize intent from natural language input
 * Pure function - no side effects
 */
function recognizeIntent(input) {
    const normalizedInput = input.trim().toLowerCase();
    // Try each pattern matcher
    for (const matcher of INTENT_PATTERNS) {
        for (const pattern of matcher.patterns) {
            const match = normalizedInput.match(pattern);
            if (match) {
                return {
                    type: matcher.type,
                    confidence: calculateConfidence(match, normalizedInput),
                    entities: matcher.extractEntities(match),
                    rawInput: input
                };
            }
        }
    }
    // No pattern matched
    return {
        type: 'unknown',
        confidence: 0,
        entities: [],
        rawInput: input
    };
}
/**
 * Calculate confidence based on match quality
 * Pure function
 */
function calculateConfidence(match, input) {
    // Base confidence
    let confidence = 0.8;
    // Full match vs partial
    if (match[0] === input) {
        confidence += 0.1;
    }
    // Direct command vs polite request
    if (!/please|could|can you/.test(input)) {
        confidence += 0.05;
    }
    // Typos or unusual patterns reduce confidence
    if (hasTypos(input)) {
        confidence -= 0.1;
    }
    return Math.max(0, Math.min(1, confidence));
}
/**
 * Normalize package names
 * Pure function
 */
function normalizePackageName(name) {
    return name
        .trim()
        .toLowerCase()
        .replace(/\s+/g, '-')
        .replace(/[^a-z0-9-]/g, '');
}
/**
 * Normalize service names
 * Pure function
 */
function normalizeServiceName(name) {
    // Common service name mappings
    const serviceMap = {
        'wifi': 'NetworkManager',
        'network': 'NetworkManager',
        'internet': 'NetworkManager',
        'sound': 'pipewire',
        'audio': 'pipewire',
        'bluetooth': 'bluetooth',
        'docker': 'docker',
        'ssh': 'sshd',
        'web server': 'nginx',
        'nginx': 'nginx',
        'apache': 'httpd',
        'database': 'postgresql',
        'postgres': 'postgresql',
        'mysql': 'mysql'
    };
    const normalized = name.trim().toLowerCase();
    return serviceMap[normalized] || name.trim();
}
/**
 * Extract service action from input
 * Pure function
 */
function extractServiceAction(input) {
    if (/\b(?:is|check|status)\b/i.test(input))
        return 'status';
    if (/\bstart|turn on|launch\b/i.test(input))
        return 'start';
    if (/\bstop|turn off|kill\b/i.test(input))
        return 'stop';
    if (/\brestart\b/i.test(input))
        return 'restart';
    if (/\benable\b/i.test(input))
        return 'enable';
    if (/\bdisable\b/i.test(input))
        return 'disable';
    return 'status'; // Default
}
/**
 * Simple typo detection
 * Pure function
 */
function hasTypos(input) {
    // Very basic - could be enhanced with edit distance
    const commonTypos = /teh|hte|taht|becuase|recieve/i;
    return commonTypos.test(input);
}
/**
 * Get suggested intent for unknown inputs
 * Pure function
 */
function suggestIntent(input) {
    const keywords = input.toLowerCase().split(/\s+/);
    if (keywords.some(k => ['install', 'add', 'get'].includes(k))) {
        return 'install';
    }
    if (keywords.some(k => ['remove', 'uninstall', 'delete'].includes(k))) {
        return 'remove';
    }
    if (keywords.some(k => ['update', 'upgrade'].includes(k))) {
        return 'update';
    }
    if (keywords.some(k => ['list', 'show', 'installed'].includes(k))) {
        return 'query';
    }
    return null;
}
//# sourceMappingURL=intent-recognition.js.map