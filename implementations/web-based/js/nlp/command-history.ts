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
  commonPhrases: Array<{ phrase: string; intent: string; count: number }>;
  safetyLevel: 'cautious' | 'normal' | 'expert';
}

export class CommandHistory {
  private history: CommandHistoryEntry[] = [];
  private preferences: UserPreferences = {
    preferredPackages: {},
    aliases: {},
    commonPhrases: [],
    safetyLevel: 'normal'
  };
  
  private readonly maxHistorySize = 1000;
  private readonly storageKey = 'nix-humanity-history';
  private readonly preferencesKey = 'nix-humanity-preferences';
  
  constructor() {
    this.loadFromStorage();
  }
  
  /**
   * Add command to history
   */
  addEntry(entry: Omit<CommandHistoryEntry, 'id'>): string {
    const id = this.generateId();
    const fullEntry: CommandHistoryEntry = { id, ...entry };
    
    this.history.unshift(fullEntry);
    
    // Keep history size manageable
    if (this.history.length > this.maxHistorySize) {
      this.history = this.history.slice(0, this.maxHistorySize);
    }
    
    // Learn from this entry
    this.learnFromEntry(fullEntry);
    
    // Save to storage
    this.saveToStorage();
    
    return id;
  }
  
  /**
   * Get recent history
   */
  getRecent(limit: number = 10): CommandHistoryEntry[] {
    return this.history.slice(0, limit);
  }
  
  /**
   * Search history
   */
  search(query: string): CommandHistoryEntry[] {
    const lowercaseQuery = query.toLowerCase();
    return this.history.filter(entry => 
      entry.naturalInput.toLowerCase().includes(lowercaseQuery) ||
      entry.executedCommand?.toLowerCase().includes(lowercaseQuery)
    );
  }
  
  /**
   * Get last successful command of type
   */
  getLastSuccessful(intentType: string): CommandHistoryEntry | undefined {
    return this.history.find(entry => 
      entry.success && 
      entry.recognizedIntent?.type === intentType
    );
  }
  
  /**
   * Mark entry as corrected
   */
  markCorrected(id: string, correctedInput: string): void {
    const entry = this.history.find(e => e.id === id);
    if (entry) {
      entry.correctedTo = correctedInput;
      this.learnFromCorrection(entry, correctedInput);
      this.saveToStorage();
    }
  }
  
  /**
   * Get user preferences
   */
  getPreferences(): UserPreferences {
    return { ...this.preferences };
  }
  
  /**
   * Update preference
   */
  updatePreference<K extends keyof UserPreferences>(
    key: K,
    value: UserPreferences[K]
  ): void {
    this.preferences[key] = value;
    this.savePreferences();
  }
  
  /**
   * Get suggested command based on partial input
   */
  getSuggestions(partialInput: string): string[] {
    const lowercase = partialInput.toLowerCase();
    
    // Find matching history entries
    const matches = this.history
      .filter(entry => 
        entry.success && 
        entry.naturalInput.toLowerCase().startsWith(lowercase)
      )
      .map(entry => entry.naturalInput);
    
    // Remove duplicates and return top 5
    return [...new Set(matches)].slice(0, 5);
  }
  
  /**
   * Get command statistics
   */
  getStats(): {
    totalCommands: number;
    successRate: number;
    mostCommonCommands: Array<{ command: string; count: number }>;
    averageResponseTime: number;
  } {
    const successful = this.history.filter(e => e.success).length;
    const commandCounts = new Map<string, number>();
    let totalDuration = 0;
    let durationCount = 0;
    
    this.history.forEach(entry => {
      if (entry.recognizedIntent?.type) {
        const count = commandCounts.get(entry.recognizedIntent.type) || 0;
        commandCounts.set(entry.recognizedIntent.type, count + 1);
      }
      if (entry.duration) {
        totalDuration += entry.duration;
        durationCount++;
      }
    });
    
    const mostCommon = Array.from(commandCounts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([command, count]) => ({ command, count }));
    
    return {
      totalCommands: this.history.length,
      successRate: this.history.length > 0 ? successful / this.history.length : 0,
      mostCommonCommands: mostCommon,
      averageResponseTime: durationCount > 0 ? totalDuration / durationCount : 0
    };
  }
  
  /**
   * Learn from command entry
   */
  private learnFromEntry(entry: CommandHistoryEntry): void {
    if (!entry.success) return;
    
    // Learn package preferences
    if (entry.recognizedIntent?.type === 'install') {
      const packageName = entry.recognizedIntent.entities?.find(
        (e: any) => e.type === 'package'
      )?.value;
      
      if (packageName) {
        // Track generic name to specific package mapping
        const genericNames: Record<string, string> = {
          'browser': 'firefox',
          'editor': 'vscode',
          'terminal': 'alacritty'
        };
        
        Object.entries(genericNames).forEach(([generic, specific]) => {
          if (entry.naturalInput.includes(generic) && packageName === specific) {
            this.preferences.preferredPackages[generic] = specific;
          }
        });
      }
    }
    
    // Learn common phrases
    const phrase = entry.naturalInput.toLowerCase();
    const existingPhrase = this.preferences.commonPhrases.find(
      p => p.phrase === phrase
    );
    
    if (existingPhrase) {
      existingPhrase.count++;
    } else if (this.preferences.commonPhrases.length < 50) {
      this.preferences.commonPhrases.push({
        phrase,
        intent: entry.recognizedIntent.type,
        count: 1
      });
    }
    
    // Sort by frequency
    this.preferences.commonPhrases.sort((a, b) => b.count - a.count);
  }
  
  /**
   * Learn from correction
   */
  private learnFromCorrection(
    original: CommandHistoryEntry,
    correctedInput: string
  ): void {
    // Add alias mapping
    const originalLower = original.naturalInput.toLowerCase();
    const correctedLower = correctedInput.toLowerCase();
    
    if (originalLower !== correctedLower) {
      this.preferences.aliases[originalLower] = correctedLower;
    }
  }
  
  /**
   * Load from storage
   */
  private loadFromStorage(): void {
    try {
      const historyData = localStorage.getItem(this.storageKey);
      if (historyData) {
        this.history = JSON.parse(historyData, (key, value) => {
          if (key === 'timestamp' && typeof value === 'string') {
            return new Date(value);
          }
          return value;
        });
      }
      
      const prefsData = localStorage.getItem(this.preferencesKey);
      if (prefsData) {
        this.preferences = JSON.parse(prefsData);
      }
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  }
  
  /**
   * Save to storage
   */
  private saveToStorage(): void {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.history));
      this.savePreferences();
    } catch (error) {
      console.error('Failed to save history:', error);
    }
  }
  
  /**
   * Save preferences
   */
  private savePreferences(): void {
    try {
      localStorage.setItem(this.preferencesKey, JSON.stringify(this.preferences));
    } catch (error) {
      console.error('Failed to save preferences:', error);
    }
  }
  
  /**
   * Generate unique ID
   */
  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
  
  /**
   * Clear history
   */
  clearHistory(): void {
    this.history = [];
    this.saveToStorage();
  }
  
  /**
   * Export history
   */
  exportHistory(): string {
    return JSON.stringify({
      history: this.history,
      preferences: this.preferences,
      exportDate: new Date().toISOString()
    }, null, 2);
  }
  
  /**
   * Import history
   */
  importHistory(data: string): boolean {
    try {
      const parsed = JSON.parse(data);
      if (parsed.history && Array.isArray(parsed.history)) {
        this.history = parsed.history;
        if (parsed.preferences) {
          this.preferences = parsed.preferences;
        }
        this.saveToStorage();
        return true;
      }
    } catch (error) {
      console.error('Failed to import history:', error);
    }
    return false;
  }
}

// Export singleton instance
export const commandHistory = new CommandHistory();