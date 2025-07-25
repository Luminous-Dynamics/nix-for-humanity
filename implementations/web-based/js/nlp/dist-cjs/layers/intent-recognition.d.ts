/**
 * Intent Recognition Layer (Pure Functions)
 * No side effects, no I/O, just pattern matching
 */
export interface Intent {
    type: string;
    confidence: number;
    entities: Entity[];
    rawInput: string;
}
export interface Entity {
    type: string;
    value: string;
    confidence: number;
}
/**
 * Recognize intent from natural language input
 * Pure function - no side effects
 */
export declare function recognizeIntent(input: string): Intent;
/**
 * Get suggested intent for unknown inputs
 * Pure function
 */
export declare function suggestIntent(input: string): string | null;
