/**
 * Privacy-Preserving Usage Tracker
 * Tracks anonymous usage patterns to improve the system
 */
export interface UsageEvent {
    eventType: 'intent' | 'success' | 'error' | 'clarification' | 'unsupported';
    intentType?: string;
    success?: boolean;
    duration?: number;
    timestamp: Date;
    sessionId: string;
}
export interface UsageStats {
    totalCommands: number;
    successRate: number;
    averageResponseTime: number;
    topIntents: {
        intent: string;
        count: number;
    }[];
    sessionDuration: number;
    errorRate: number;
}
/**
 * Privacy-preserving usage tracking
 * No personal information, only aggregate patterns
 */
export declare class UsageTracker {
    private events;
    private sessionId;
    private sessionStart;
    private readonly maxEvents;
    private readonly storageKey;
    constructor();
    /**
     * Track an intent recognition event
     */
    trackIntent(intentType: string, confidence: number): void;
    /**
     * Track command execution result
     */
    trackExecution(intentType: string, success: boolean, duration: number): void;
    /**
     * Track unsupported commands
     */
    trackUnsupported(): void;
    /**
     * Track clarification requests
     */
    trackClarification(intentType: string): void;
    /**
     * Get aggregated statistics
     */
    getStats(): UsageStats;
    /**
     * Export anonymous analytics
     */
    exportAnonymousAnalytics(): string;
    /**
     * Get usage patterns for learning
     */
    private getUsagePatterns;
    /**
     * Clear all tracking data
     */
    clearData(): void;
    /**
     * Add event with size limit
     */
    private addEvent;
    /**
     * Generate anonymous session ID
     */
    private generateSessionId;
    /**
     * Save to local storage
     */
    private saveToStorage;
    /**
     * Load from local storage
     */
    private loadFromStorage;
    /**
     * Get peak usage hour
     */
    private getPeakUsageHour;
    /**
     * Get average session length
     */
    private getAverageSessionLength;
    /**
     * Get privacy-friendly insights
     */
    getInsights(): string[];
}
export declare const usageTracker: UsageTracker;
