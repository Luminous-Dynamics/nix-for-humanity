/**
 * Ambiguity Resolution for Nix for Humanity
 * Handles cases where user intent is unclear
 */
import { Intent } from './intent-engine';
export interface AmbiguityResolution {
    originalInput: string;
    possibleIntents: Intent[];
    clarificationQuestion: string;
    clarificationOptions: ClarificationOption[];
}
export interface ClarificationOption {
    label: string;
    intent: Intent;
    example: string;
}
export declare class AmbiguityResolver {
    /**
     * Resolve ambiguous intents
     */
    resolve(intents: Intent[]): AmbiguityResolution | null;
    /**
     * Generate clarification question and options
     */
    private generateClarification;
    /**
     * Clarify between different intent types
     */
    private clarifyIntentType;
    /**
     * Clarify between different entities for same intent
     */
    private clarifyEntities;
    /**
     * Clarify which package to install
     */
    private clarifyPackages;
    /**
     * Clarify which problem to troubleshoot
     */
    private clarifyProblems;
    /**
     * Get user-friendly label for intent
     */
    private getIntentLabel;
    /**
     * Get example for intent
     */
    private getIntentExample;
    /**
     * Generate follow-up question for more context
     */
    generateContextQuestion(intent: Intent): string | null;
}
export declare const ambiguityResolver: AmbiguityResolver;
