/**
 * Typo correction for Nix for Humanity
 * Uses Levenshtein distance and common typo patterns
 */
/**
 * Calculate Levenshtein distance between two strings
 */
export declare function levenshteinDistance(str1: string, str2: string): number;
/**
 * Typo corrector for natural language input
 */
export declare class TypoCorrector {
    private wordList;
    private packageNames;
    constructor();
    /**
     * Correct typos in input
     */
    correct(input: string): string;
    /**
     * Correct a single word
     */
    private correctWord;
    /**
     * Suggest corrections for a word
     */
    suggestCorrections(word: string): string[];
}
export declare const typoCorrector: TypoCorrector;
