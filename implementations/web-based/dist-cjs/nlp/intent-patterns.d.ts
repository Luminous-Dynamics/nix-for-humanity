/**
 * Comprehensive pattern database for Nix for Humanity
 * Covers common variations for all 5 personas
 */
export interface PatternRule {
    patterns: RegExp[];
    intent: string;
    extractor?: (match: RegExpMatchArray) => any;
    examples: string[];
}
export declare const INTENT_PATTERNS: Record<string, PatternRule[]>;
/**
 * Normalize package names from natural language
 */
export declare function normalizePackageName(input: string): string;
/**
 * Infer package from task description
 */
export declare function inferPackageFromTask(task: string): string;
/**
 * Identify problem type from description
 */
export declare function identifyProblem(description: string): string;
/**
 * Identify setting type from description
 */
export declare function identifySetting(description: string): string;
