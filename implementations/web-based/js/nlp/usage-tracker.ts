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
  topIntents: { intent: string; count: number }[];
  sessionDuration: number;
  errorRate: number;
}

/**
 * Privacy-preserving usage tracking
 * No personal information, only aggregate patterns
 */
export class UsageTracker {
  private events: UsageEvent[] = [];
  private sessionId: string;
  private sessionStart: Date;
  private readonly maxEvents = 1000;
  private readonly storageKey = 'nfh_usage_stats';

  constructor() {
    this.sessionId = this.generateSessionId();
    this.sessionStart = new Date();
    this.loadFromStorage();
  }

  /**
   * Track an intent recognition event
   */
  trackIntent(intentType: string, confidence: number): void {
    this.addEvent({
      eventType: 'intent',
      intentType,
      timestamp: new Date(),
      sessionId: this.sessionId
    });
  }

  /**
   * Track command execution result
   */
  trackExecution(intentType: string, success: boolean, duration: number): void {
    this.addEvent({
      eventType: success ? 'success' : 'error',
      intentType,
      success,
      duration,
      timestamp: new Date(),
      sessionId: this.sessionId
    });
  }

  /**
   * Track unsupported commands
   */
  trackUnsupported(): void {
    this.addEvent({
      eventType: 'unsupported',
      timestamp: new Date(),
      sessionId: this.sessionId
    });
  }

  /**
   * Track clarification requests
   */
  trackClarification(intentType: string): void {
    this.addEvent({
      eventType: 'clarification',
      intentType,
      timestamp: new Date(),
      sessionId: this.sessionId
    });
  }

  /**
   * Get aggregated statistics
   */
  getStats(): UsageStats {
    const intentCounts = new Map<string, number>();
    let successCount = 0;
    let errorCount = 0;
    let totalDuration = 0;
    let durationCount = 0;

    this.events.forEach(event => {
      if (event.intentType) {
        intentCounts.set(event.intentType, (intentCounts.get(event.intentType) || 0) + 1);
      }
      
      if (event.eventType === 'success') {
        successCount++;
      } else if (event.eventType === 'error') {
        errorCount++;
      }
      
      if (event.duration) {
        totalDuration += event.duration;
        durationCount++;
      }
    });

    const totalCommands = this.events.filter(e => e.eventType === 'intent').length;
    const topIntents = Array.from(intentCounts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([intent, count]) => ({ intent, count }));

    return {
      totalCommands,
      successRate: totalCommands > 0 ? successCount / totalCommands : 0,
      averageResponseTime: durationCount > 0 ? totalDuration / durationCount : 0,
      topIntents,
      sessionDuration: Date.now() - this.sessionStart.getTime(),
      errorRate: totalCommands > 0 ? errorCount / totalCommands : 0
    };
  }

  /**
   * Export anonymous analytics
   */
  exportAnonymousAnalytics(): string {
    const stats = this.getStats();
    
    // Create anonymous report
    const report = {
      version: '1.0',
      timestamp: new Date().toISOString(),
      stats: {
        totalCommands: stats.totalCommands,
        successRate: Math.round(stats.successRate * 100),
        averageResponseTime: Math.round(stats.averageResponseTime),
        topIntents: stats.topIntents,
        sessionDuration: Math.round(stats.sessionDuration / 1000), // seconds
        errorRate: Math.round(stats.errorRate * 100)
      },
      patterns: this.getUsagePatterns()
    };

    return JSON.stringify(report, null, 2);
  }

  /**
   * Get usage patterns for learning
   */
  private getUsagePatterns(): any {
    // Analyze event sequences
    const sequences: string[] = [];
    for (let i = 1; i < this.events.length; i++) {
      if (this.events[i-1].intentType && this.events[i].intentType) {
        sequences.push(`${this.events[i-1].intentType} -> ${this.events[i].intentType}`);
      }
    }

    // Count common sequences
    const sequenceCounts = new Map<string, number>();
    sequences.forEach(seq => {
      sequenceCounts.set(seq, (sequenceCounts.get(seq) || 0) + 1);
    });

    const commonSequences = Array.from(sequenceCounts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([sequence, count]) => ({ sequence, count }));

    return {
      commonSequences,
      peakUsageHour: this.getPeakUsageHour(),
      averageSessionLength: Math.round(this.getAverageSessionLength() / 1000)
    };
  }

  /**
   * Clear all tracking data
   */
  clearData(): void {
    this.events = [];
    this.saveToStorage();
  }

  /**
   * Add event with size limit
   */
  private addEvent(event: UsageEvent): void {
    if (this.events.length >= this.maxEvents) {
      this.events.shift(); // Remove oldest
    }
    this.events.push(event);
    this.saveToStorage();
  }

  /**
   * Generate anonymous session ID
   */
  private generateSessionId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }

  /**
   * Save to local storage
   */
  private saveToStorage(): void {
    if (typeof localStorage !== 'undefined') {
      try {
        const data = {
          events: this.events.slice(-500), // Only save last 500
          sessionId: this.sessionId,
          sessionStart: this.sessionStart.toISOString()
        };
        localStorage.setItem(this.storageKey, JSON.stringify(data));
      } catch (e) {
        // Ignore storage errors
      }
    }
  }

  /**
   * Load from local storage
   */
  private loadFromStorage(): void {
    if (typeof localStorage !== 'undefined') {
      try {
        const stored = localStorage.getItem(this.storageKey);
        if (stored) {
          const data = JSON.parse(stored);
          // Only load if same session
          if (data.sessionId === this.sessionId) {
            this.events = data.events.map((e: any) => ({
              ...e,
              timestamp: new Date(e.timestamp)
            }));
          }
        }
      } catch (e) {
        // Ignore load errors
      }
    }
  }

  /**
   * Get peak usage hour
   */
  private getPeakUsageHour(): number {
    const hourCounts = new Array(24).fill(0);
    this.events.forEach(event => {
      const hour = new Date(event.timestamp).getHours();
      hourCounts[hour]++;
    });
    
    let maxHour = 0;
    let maxCount = 0;
    hourCounts.forEach((count, hour) => {
      if (count > maxCount) {
        maxCount = count;
        maxHour = hour;
      }
    });
    
    return maxHour;
  }

  /**
   * Get average session length
   */
  private getAverageSessionLength(): number {
    // Simple heuristic: gap > 30 minutes = new session
    const sessions: number[] = [];
    let sessionStart = this.events[0]?.timestamp.getTime() || Date.now();
    let lastEvent = sessionStart;

    this.events.forEach(event => {
      const eventTime = event.timestamp.getTime();
      if (eventTime - lastEvent > 30 * 60 * 1000) { // 30 minute gap
        sessions.push(lastEvent - sessionStart);
        sessionStart = eventTime;
      }
      lastEvent = eventTime;
    });
    
    // Add current session
    sessions.push(lastEvent - sessionStart);
    
    return sessions.reduce((sum, len) => sum + len, 0) / sessions.length;
  }

  /**
   * Get privacy-friendly insights
   */
  getInsights(): string[] {
    const stats = this.getStats();
    const insights: string[] = [];

    if (stats.successRate < 0.7) {
      insights.push("Success rate is below 70%. Consider reviewing common error patterns.");
    }

    if (stats.averageResponseTime > 2000) {
      insights.push("Response time is above 2 seconds. Performance optimization may help.");
    }

    if (stats.topIntents[0]?.count > stats.totalCommands * 0.5) {
      insights.push(`Most commands are '${stats.topIntents[0].intent}'. Consider optimizing this flow.`);
    }

    const unsupportedRate = this.events.filter(e => e.eventType === 'unsupported').length / stats.totalCommands;
    if (unsupportedRate > 0.2) {
      insights.push("Over 20% of commands are unsupported. Review unsupported patterns.");
    }

    return insights;
  }
}

// Export singleton instance
export const usageTracker = new UsageTracker();