/**
 * Typo correction for Nix for Humanity
 * Uses Levenshtein distance and common typo patterns
 */
/**
 * Calculate Levenshtein distance between two strings
 */
export function levenshteinDistance(str1, str2) {
    const len1 = str1.length;
    const len2 = str2.length;
    // Create distance matrix
    const matrix = Array(len1 + 1)
        .fill(null)
        .map(() => Array(len2 + 1).fill(0));
    // Initialize first column and row
    for (let i = 0; i <= len1; i++)
        matrix[i][0] = i;
    for (let j = 0; j <= len2; j++)
        matrix[0][j] = j;
    // Fill matrix
    for (let i = 1; i <= len1; i++) {
        for (let j = 1; j <= len2; j++) {
            const cost = str1[i - 1] === str2[j - 1] ? 0 : 1;
            matrix[i][j] = Math.min(matrix[i - 1][j] + 1, // deletion
            matrix[i][j - 1] + 1, // insertion
            matrix[i - 1][j - 1] + cost // substitution
            );
        }
    }
    return matrix[len1][len2];
}
const TYPO_PATTERNS = [
    // Doubled letters
    { pattern: /(.)\1+/g, replacement: '$1' },
    // Common keyboard proximity errors
    { from: 'teh', to: 'the' },
    { from: 'taht', to: 'that' },
    { from: 'wiht', to: 'with' },
    { from: 'waht', to: 'what' },
    { from: 'cna', to: 'can' },
    { from: 'dont', to: "don't" },
    { from: 'wont', to: "won't" },
    { from: 'cant', to: "can't" },
    { from: 'isnt', to: "isn't" },
    { from: 'arent', to: "aren't" },
    { from: 'doesnt', to: "doesn't" },
    { from: 'wouldnt', to: "wouldn't" },
    { from: 'couldnt', to: "couldn't" },
    { from: 'shouldnt', to: "shouldn't" },
    // Common package name typos
    { from: 'fierfix', to: 'firefox' },
    { from: 'firefox', to: 'firefox' },
    { from: 'firfox', to: 'firefox' },
    { from: 'chorme', to: 'chrome' },
    { from: 'chorome', to: 'chrome' },
    { from: 'vscod', to: 'vscode' },
    { from: 'vsocde', to: 'vscode' },
    { from: 'vs cod', to: 'vscode' },
    { from: 'spotifi', to: 'spotify' },
    { from: 'sptoify', to: 'spotify' },
    { from: 'dicord', to: 'discord' },
    { from: 'disocrd', to: 'discord' },
    { from: 'pyhton', to: 'python' },
    { from: 'pyton', to: 'python' },
    { from: 'pytohn', to: 'python' },
    // Common command typos
    { from: 'instal', to: 'install' },
    { from: 'intall', to: 'install' },
    { from: 'isntall', to: 'install' },
    { from: 'insatll', to: 'install' },
    { from: 'instlal', to: 'install' },
    { from: 'udpate', to: 'update' },
    { from: 'updtae', to: 'update' },
    { from: 'upadte', to: 'update' },
    { from: 'upgrad', to: 'upgrade' },
    { from: 'upgarde', to: 'upgrade' }
];
/**
 * Typo corrector for natural language input
 */
export class TypoCorrector {
    constructor() {
        // Common words in commands
        this.wordList = new Set([
            'install', 'update', 'upgrade', 'remove', 'delete', 'uninstall',
            'need', 'want', 'get', 'give', 'show', 'list', 'display',
            'help', 'fix', 'repair', 'troubleshoot', 'configure', 'setup',
            'my', 'the', 'a', 'an', 'is', 'are', 'not', 'working',
            'broken', 'please', 'can', 'you', 'me', 'for', 'with',
            'internet', 'wifi', 'network', 'sound', 'audio', 'screen',
            'display', 'text', 'font', 'bigger', 'smaller', 'larger'
        ]);
        // Common package names
        this.packageNames = new Set([
            'firefox', 'chrome', 'chromium', 'brave', 'vscode', 'vim', 'neovim',
            'emacs', 'spotify', 'vlc', 'gimp', 'krita', 'inkscape', 'discord',
            'slack', 'zoom', 'skype', 'thunderbird', 'libreoffice', 'git',
            'python', 'python3', 'nodejs', 'docker', 'rust', 'go', 'java',
            'gcc', 'make', 'htop', 'neofetch', 'alacritty', 'nautilus'
        ]);
    }
    /**
     * Correct typos in input
     */
    correct(input) {
        // Apply pattern-based corrections
        let corrected = input;
        for (const pattern of TYPO_PATTERNS) {
            if ('pattern' in pattern && 'replacement' in pattern) {
                corrected = corrected.replace(pattern.pattern, pattern.replacement);
            }
            else if ('from' in pattern && 'to' in pattern) {
                const regex = new RegExp(`\\b${pattern.from}\\b`, 'gi');
                corrected = corrected.replace(regex, pattern.to);
            }
        }
        // Split into words and correct each
        const words = corrected.split(/\s+/);
        const correctedWords = words.map(word => this.correctWord(word));
        return correctedWords.join(' ');
    }
    /**
     * Correct a single word
     */
    correctWord(word) {
        const lowerWord = word.toLowerCase();
        // If word is correct, return as-is
        if (this.wordList.has(lowerWord) || this.packageNames.has(lowerWord)) {
            return word;
        }
        // Find closest match
        let minDistance = Infinity;
        let bestMatch = word;
        // Check against common words
        for (const candidate of this.wordList) {
            const distance = levenshteinDistance(lowerWord, candidate);
            if (distance < minDistance && distance <= 2) {
                minDistance = distance;
                bestMatch = candidate;
            }
        }
        // Check against package names
        for (const candidate of this.packageNames) {
            const distance = levenshteinDistance(lowerWord, candidate);
            if (distance < minDistance && distance <= 2) {
                minDistance = distance;
                bestMatch = candidate;
            }
        }
        // Preserve original casing if no correction found
        return minDistance <= 2 ? bestMatch : word;
    }
    /**
     * Suggest corrections for a word
     */
    suggestCorrections(word) {
        const suggestions = [];
        const lowerWord = word.toLowerCase();
        // Check all candidates
        const allWords = [...this.wordList, ...this.packageNames];
        for (const candidate of allWords) {
            const distance = levenshteinDistance(lowerWord, candidate);
            if (distance <= 3 && distance > 0) {
                suggestions.push({ word: candidate, distance });
            }
        }
        // Sort by distance and return top 5
        return suggestions
            .sort((a, b) => a.distance - b.distance)
            .slice(0, 5)
            .map(s => s.word);
    }
}
// Export singleton instance
export const typoCorrector = new TypoCorrector();
//# sourceMappingURL=typo-corrector.js.map