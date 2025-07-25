/**
 * Context Manager for Multi-Turn Conversations
 * Maintains conversation state and enables contextual understanding
 */

import { Intent, Entity } from './layers/intent-recognition';

export interface ConversationContext {
  sessionId: string;
  turns: ConversationTurn[];
  lastPackage?: string;
  lastService?: string;
  lastIntent?: string;
  lastResult?: 'success' | 'error' | 'clarification';
  currentTopic?: string;
  clarificationNeeded?: string;
}

export interface ConversationTurn {
  input: string;
  intent: Intent;
  timestamp: Date;
  response?: string;
  result?: 'success' | 'error' | 'clarification';
}

export interface ContextualIntent extends Intent {
  contextResolved?: boolean;
  resolvedEntities?: Entity[];
}

/**
 * Manages conversation context for multi-turn interactions
 */
export class ContextManager {
  private context: ConversationContext;
  private readonly maxTurns = 10;
  private readonly contextTimeout = 30 * 60 * 1000; // 30 minutes

  constructor() {
    this.context = this.initializeContext();
  }

  /**
   * Process input with context awareness
   */
  processWithContext(input: string, intent: Intent): ContextualIntent {
    // Clean up old context
    this.cleanupOldTurns();

    // Check for pronouns and references
    const contextualIntent = this.resolveReferences(input, intent);

    // Add to conversation history
    this.addTurn({
      input,
      intent: contextualIntent,
      timestamp: new Date()
    });

    // Update context based on intent
    this.updateContext(contextualIntent);

    return contextualIntent;
  }

  /**
   * Resolve pronouns and references using context
   */
  private resolveReferences(input: string, intent: Intent): ContextualIntent {
    const lowered = input.toLowerCase();
    let resolved = { ...intent } as ContextualIntent;

    // Handle "it" references
    if (lowered.includes('it') || lowered.includes('that')) {
      resolved = this.resolveItReference(lowered, resolved);
    }

    // Handle "again" references
    if (lowered.includes('again') || lowered.includes('retry')) {
      resolved = this.resolveAgainReference(resolved);
    }

    // Handle implicit references
    if (intent.type === 'install' && !intent.entities.find((e: Entity) => e.type === 'package')) {
      resolved = this.resolveImplicitPackage(resolved);
    }

    // Handle follow-up questions
    if (this.context.clarificationNeeded) {
      resolved = this.resolveClarification(input, resolved);
    }

    return resolved;
  }

  /**
   * Resolve "it" or "that" references
   */
  private resolveItReference(input: string, intent: ContextualIntent): ContextualIntent {
    // "install it" after searching for a package
    if (input.match(/install (it|that)/i) && this.context.lastPackage) {
      return {
        ...intent,
        type: 'install',
        entities: [{
          type: 'package',
          value: this.context.lastPackage,
          confidence: 0.9
        }],
        contextResolved: true
      };
    }

    // "start it" after discussing a service
    if (input.match(/start (it|that)/i) && this.context.lastService) {
      return {
        ...intent,
        type: 'service',
        entities: [
          { type: 'action', value: 'start', confidence: 0.9 },
          { type: 'service', value: this.context.lastService, confidence: 0.9 }
        ],
        contextResolved: true
      };
    }

    // "show me more about it"
    if (input.match(/more about (it|that)/i) && this.context.lastPackage) {
      return {
        ...intent,
        type: 'query',
        entities: [{
          type: 'package',
          value: this.context.lastPackage,
          confidence: 0.9
        }],
        contextResolved: true
      };
    }

    return intent;
  }

  /**
   * Resolve "again" references
   */
  private resolveAgainReference(intent: ContextualIntent): ContextualIntent {
    const lastTurn = this.getLastTurn();
    if (!lastTurn) return intent;

    // "try again" after an error
    if (this.context.lastResult === 'error') {
      return {
        ...lastTurn.intent,
        contextResolved: true
      };
    }

    // "do that again" for any previous action
    if (lastTurn.intent.type !== 'unknown') {
      return {
        ...lastTurn.intent,
        contextResolved: true
      };
    }

    return intent;
  }

  /**
   * Resolve implicit package references
   */
  private resolveImplicitPackage(intent: ContextualIntent): ContextualIntent {
    // If we were just talking about a package, use it
    if (this.context.lastPackage && this.isRecent(2)) {
      return {
        ...intent,
        entities: [{
          type: 'package',
          value: this.context.lastPackage,
          confidence: 0.8
        }],
        contextResolved: true
      };
    }

    return intent;
  }

  /**
   * Resolve clarification responses
   */
  private resolveClarification(input: string, intent: ContextualIntent): ContextualIntent {
    // User answering a clarification question
    if (this.context.clarificationNeeded === 'package_choice') {
      // Handle "the first one", "number 2", etc.
      const numberMatch = input.match(/(\d+|first|second|third|last)/i);
      if (numberMatch) {
        // This would need access to the choices presented
        return {
          ...intent,
          type: 'install',
          contextResolved: true
        };
      }
    }

    return intent;
  }

  /**
   * Update context based on intent
   */
  private updateContext(intent: ContextualIntent): void {
    // Update last intent
    this.context.lastIntent = intent.type;

    // Extract and store entities
    intent.entities.forEach((entity: Entity) => {
      if (entity.type === 'package') {
        this.context.lastPackage = entity.value;
      } else if (entity.type === 'service') {
        this.context.lastService = entity.value;
      }
    });

    // Update topic
    this.updateTopic(intent);
  }

  /**
   * Update current conversation topic
   */
  private updateTopic(intent: ContextualIntent): void {
    if (intent.type === 'install' || intent.type === 'query') {
      this.context.currentTopic = 'package_management';
    } else if (intent.type === 'service') {
      this.context.currentTopic = 'service_management';
    } else if (intent.type === 'troubleshoot') {
      this.context.currentTopic = 'troubleshooting';
    }
  }

  /**
   * Add a turn to conversation history
   */
  private addTurn(turn: ConversationTurn): void {
    this.context.turns.push(turn);
    
    // Keep only recent turns
    if (this.context.turns.length > this.maxTurns) {
      this.context.turns.shift();
    }
  }

  /**
   * Get the last conversation turn
   */
  private getLastTurn(): ConversationTurn | undefined {
    return this.context.turns[this.context.turns.length - 1];
  }

  /**
   * Check if last interaction was recent
   */
  private isRecent(minutes: number): boolean {
    const lastTurn = this.getLastTurn();
    if (!lastTurn) return false;
    
    const elapsed = Date.now() - lastTurn.timestamp.getTime();
    return elapsed < minutes * 60 * 1000;
  }

  /**
   * Clean up old conversation turns
   */
  private cleanupOldTurns(): void {
    const cutoff = Date.now() - this.contextTimeout;
    this.context.turns = this.context.turns.filter(
      turn => turn.timestamp.getTime() > cutoff
    );
  }

  /**
   * Set the result of the last turn
   */
  setLastResult(result: 'success' | 'error' | 'clarification', response?: string): void {
    const lastTurn = this.getLastTurn();
    if (lastTurn) {
      lastTurn.result = result;
      lastTurn.response = response;
    }
    this.context.lastResult = result;
  }

  /**
   * Set clarification needed
   */
  setClarificationNeeded(type: string): void {
    this.context.clarificationNeeded = type;
  }

  /**
   * Clear clarification flag
   */
  clearClarification(): void {
    this.context.clarificationNeeded = undefined;
  }

  /**
   * Get conversation summary
   */
  getSummary(): string {
    if (this.context.turns.length === 0) {
      return "No conversation history.";
    }

    const recentTurns = this.context.turns.slice(-3);
    const summary = recentTurns
      .map(turn => `You: "${turn.input}" → ${turn.intent.type}`)
      .join('\n');

    return `Recent conversation:\n${summary}`;
  }

  /**
   * Get contextual suggestions
   */
  getSuggestions(): string[] {
    const suggestions: string[] = [];

    // Based on last intent
    if (this.context.lastIntent === 'install' && this.context.lastResult === 'success') {
      suggestions.push(`You can now run the program you installed`);
      suggestions.push(`Try "show me ${this.context.lastPackage}" to learn more`);
    }

    // Based on topic
    if (this.context.currentTopic === 'troubleshooting') {
      suggestions.push(`Try "show logs" to see what went wrong`);
      suggestions.push(`You can also check service status`);
    }

    // Based on errors
    if (this.context.lastResult === 'error') {
      suggestions.push(`Say "try again" to retry the last command`);
      suggestions.push(`Or describe the problem differently`);
    }

    return suggestions.slice(0, 2);
  }

  /**
   * Reset context
   */
  reset(): void {
    this.context = this.initializeContext();
  }

  /**
   * Initialize new context
   */
  private initializeContext(): ConversationContext {
    return {
      sessionId: Date.now().toString(36),
      turns: []
    };
  }

  /**
   * Export context for debugging
   */
  exportContext(): ConversationContext {
    return { ...this.context };
  }
}

// Export singleton instance
export const contextManager = new ContextManager();