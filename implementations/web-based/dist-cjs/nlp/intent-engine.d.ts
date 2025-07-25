/**
 * Intent Recognition Engine for Nix for Humanity
 * Hybrid approach: Rules + Statistical + Neural (progressive enhancement)
 */
export interface Intent {
    type: 'install' | 'update' | 'query' | 'troubleshoot' | 'config' | 'maintenance' | 'logs' | 'service' | 'unknown';
    confidence: number;
    entities: Entity[];
    alternatives?: Intent[];
    original: string;
}
export interface Entity {
    type: 'package' | 'service' | 'setting' | 'problem' | 'action' | 'logType' | 'timeframe';
    value: string;
    confidence: number;
}
/**
 * Core intent recognition engine using hybrid approach
 */
export declare class IntentEngine {
    private patterns;
    constructor();
    /**
     * Check for dangerous command injection patterns
     */
    private containsDangerousPatterns;
    /**
     * Main recognition method - combines all approaches
     */
    recognize(input: string): Intent;
    /**
     * Normalize input for consistent matching
     */
    private normalize;
    /**
     * Rule-based pattern matching (fast path) - Enhanced version
     */
    private matchRules;
    /**
     * Convert extracted data to entities
     */
    private extractedToEntities;
    /**
     * Old rule-based patterns (kept for compatibility)
     */
    private matchOldRules;
    /**
     * Statistical matching for flexibility
     */
    private statisticalMatch;
    /**
     * Combine results from different methods
     */
    private combineResults;
    /**
     * Extract package name from various formats
     */
    private extractPackageName;
    /**
     * Extract entities based on intent type
     */
    private extractEntitiesForType;
    /**
     * Extract query-specific entities
     */
    private extractQueryEntities;
    /**
     * Extract problem entities
     */
    private extractProblemEntities;
    /**
     * Extract configuration entities
     */
    private extractConfigEntities;
    /**
     * Initialize pattern database
     */
    private initializePatterns;
}
export declare const intentEngine: IntentEngine;
