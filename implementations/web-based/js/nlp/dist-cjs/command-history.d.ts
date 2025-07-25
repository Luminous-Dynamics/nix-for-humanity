/**
 * Command History & Learning
 * Tracks user commands and learns preferences
 */
export interface CommandHistoryEntry {
    id: string;
    timestamp: Date;
    naturalInput: string;
    recognizedIntent: any;
    executedCommand?: string;
    success: boolean;
    error?: string;
    correctedTo?: string;
    duration?: number;
}
export interface UserPreferences {
    preferredPackages: Record<string, string>;
    aliases: Record<string, string>;
    commonPhrases: Array<{
        phrase: string;
        intent: string;
        count: number;
    }>;
    safetyLevel: 'cautious' | 'normal' | 'expert';
}
export declare class CommandHistory {
    private history;
    private preferences;
    private readonly maxHistorySize;
    private readonly storageKey;
    private readonly preferencesKey;
    constructor();
    /**
     * Add command to history
     */
    addEntry(entry: Omit<CommandHistoryEntry, 'id'>): string;
    /**
     * Get recent history
     */
    getRecent(limit?: number): CommandHistoryEntry[];
    /**
     * Search history
     */
    search(query: string): CommandHistoryEntry[];
    /**
     * Get last successful command of type
     */
    getLastSuccessful(intentType: string): CommandHistoryEntry | undefined;
    /**
     * Mark entry as corrected
     */
    markCorrected(id: string, correctedInput: string): void;
    /**
     * Get user preferences
     */
    getPreferences(): UserPreferences;
    /**
     * Update preference
     */
    updatePreference<K extends keyof UserPreferences>(key: K, value: UserPreferences[K]): void;
    /**
     * Get suggested command based on partial input
     */
    getSuggestions(partialInput: string): string[];
    /**
     * Get command statistics
     */
    getStats(): {
        totalCommands: number;
        successRate: number;
        mostCommonCommands: Array<{
            command: string;
            count: number;
        }>;
        averageResponseTime: number;
    };
    /**
     * Learn from command entry
     */
    private learnFromEntry;
    /**
     * Learn from correction
     */
    private learnFromCorrection;
    /**
     * Load from storage
     */
    private loadFromStorage;
    /**
     * Save to storage
     */
    private saveToStorage;
    /**
     * Save preferences
     */
    private savePreferences;
    /**
     * Generate unique ID
     */
    private generateId;
    /**
     * Clear history
     */
    clearHistory(): void;
    /**
     * Export history
     */
    exportHistory(): string;
    /**
     * Import history
     */
    importHistory(data: string): boolean;
}
export declare const commandHistory: CommandHistory;
