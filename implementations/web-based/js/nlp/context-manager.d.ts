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
export declare class ContextManager {
    private context;
    private readonly maxTurns;
    private readonly contextTimeout;
    constructor();
    /**
     * Process input with context awareness
     */
    processWithContext(input: string, intent: Intent): ContextualIntent;
    /**
     * Resolve pronouns and references using context
     */
    private resolveReferences;
    /**
     * Resolve "it" or "that" references
     */
    private resolveItReference;
    /**
     * Resolve "again" references
     */
    private resolveAgainReference;
    /**
     * Resolve implicit package references
     */
    private resolveImplicitPackage;
    /**
     * Resolve clarification responses
     */
    private resolveClarification;
    /**
     * Update context based on intent
     */
    private updateContext;
    /**
     * Update current conversation topic
     */
    private updateTopic;
    /**
     * Add a turn to conversation history
     */
    private addTurn;
    /**
     * Get the last conversation turn
     */
    private getLastTurn;
    /**
     * Check if last interaction was recent
     */
    private isRecent;
    /**
     * Clean up old conversation turns
     */
    private cleanupOldTurns;
    /**
     * Set the result of the last turn
     */
    setLastResult(result: 'success' | 'error' | 'clarification', response?: string): void;
    /**
     * Set clarification needed
     */
    setClarificationNeeded(type: string): void;
    /**
     * Clear clarification flag
     */
    clearClarification(): void;
    /**
     * Get conversation summary
     */
    getSummary(): string;
    /**
     * Get contextual suggestions
     */
    getSuggestions(): string[];
    /**
     * Reset context
     */
    reset(): void;
    /**
     * Initialize new context
     */
    private initializeContext;
    /**
     * Export context for debugging
     */
    exportContext(): ConversationContext;
}
export declare const contextManager: ContextManager;
