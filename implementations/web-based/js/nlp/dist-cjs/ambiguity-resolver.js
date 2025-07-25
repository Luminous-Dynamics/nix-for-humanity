/**
 * Ambiguity Resolution for Nix for Humanity
 * Handles cases where user intent is unclear
 */
export class AmbiguityResolver {
    /**
     * Resolve ambiguous intents
     */
    resolve(intents) {
        // No ambiguity if only one intent or one is clearly better
        if (intents.length <= 1)
            return null;
        const topIntent = intents[0];
        const secondIntent = intents[1];
        // If top intent is significantly more confident, no ambiguity
        if (topIntent.confidence - secondIntent.confidence > 0.3)
            return null;
        // Generate clarification based on intent types
        return this.generateClarification(intents);
    }
    /**
     * Generate clarification question and options
     */
    generateClarification(intents) {
        const topIntents = intents.slice(0, 3); // Top 3 possibilities
        // Group by intent type
        const intentTypes = new Set(topIntents.map(i => i.type));
        if (intentTypes.size === 1) {
            // Same intent type but different entities
            return this.clarifyEntities(topIntents);
        }
        else {
            // Different intent types
            return this.clarifyIntentType(topIntents);
        }
    }
    /**
     * Clarify between different intent types
     */
    clarifyIntentType(intents) {
        const options = intents.map(intent => {
            const label = this.getIntentLabel(intent);
            const example = this.getIntentExample(intent);
            return {
                label,
                intent,
                example
            };
        });
        return {
            originalInput: intents[0].original,
            possibleIntents: intents,
            clarificationQuestion: "I want to make sure I understand. Are you trying to:",
            clarificationOptions: options
        };
    }
    /**
     * Clarify between different entities for same intent
     */
    clarifyEntities(intents) {
        const intentType = intents[0].type;
        if (intentType === 'install') {
            return this.clarifyPackages(intents);
        }
        else if (intentType === 'troubleshoot') {
            return this.clarifyProblems(intents);
        }
        else {
            return this.clarifyIntentType(intents);
        }
    }
    /**
     * Clarify which package to install
     */
    clarifyPackages(intents) {
        const options = [];
        // Extract unique packages
        const packages = new Map();
        for (const intent of intents) {
            const pkg = intent.entities.find(e => e.type === 'package')?.value;
            if (pkg && !packages.has(pkg)) {
                packages.set(pkg, intent);
            }
        }
        // Common package clarifications
        const packageDescriptions = {
            'firefox': 'Firefox Web Browser (recommended)',
            'google-chrome': 'Google Chrome Browser',
            'chromium': 'Chromium Open-Source Browser',
            'vscode': 'Visual Studio Code (coding editor)',
            'neovim': 'NeoVim (terminal text editor)',
            'emacs': 'Emacs (advanced text editor)',
            'libreoffice': 'LibreOffice (full office suite)',
            'onlyoffice': 'OnlyOffice (MS Office compatible)',
            'gimp': 'GIMP (photo editing like Photoshop)',
            'inkscape': 'Inkscape (vector graphics)',
            'spotify': 'Spotify (music streaming)',
            'rhythmbox': 'Rhythmbox (local music player)'
        };
        packages.forEach((intent, pkg) => {
            options.push({
                label: packageDescriptions[pkg] || pkg,
                intent,
                example: `install ${pkg}`
            });
        });
        return {
            originalInput: intents[0].original,
            possibleIntents: intents,
            clarificationQuestion: "Which program would you like to install?",
            clarificationOptions: options
        };
    }
    /**
     * Clarify which problem to troubleshoot
     */
    clarifyProblems(intents) {
        const options = [];
        // Extract unique problems
        const problems = new Map();
        for (const intent of intents) {
            const problem = intent.entities.find(e => e.type === 'problem')?.value;
            if (problem && !problems.has(problem)) {
                problems.set(problem, intent);
            }
        }
        const problemDescriptions = {
            'network': 'Internet/WiFi connection issues',
            'audio': 'Sound/Audio problems',
            'display': 'Screen/Display issues',
            'print': 'Printer problems',
            'bluetooth': 'Bluetooth connection issues',
            'performance': 'System running slow'
        };
        problems.forEach((intent, problem) => {
            options.push({
                label: problemDescriptions[problem] || problem,
                intent,
                example: `fix ${problem}`
            });
        });
        return {
            originalInput: intents[0].original,
            possibleIntents: intents,
            clarificationQuestion: "What kind of problem are you experiencing?",
            clarificationOptions: options
        };
    }
    /**
     * Get user-friendly label for intent
     */
    getIntentLabel(intent) {
        const labels = {
            'install': 'Install a program',
            'update': 'Update your system',
            'query': 'Get information',
            'troubleshoot': 'Fix a problem',
            'config': 'Change settings',
            'greeting': 'Say hello',
            'help': 'Get help'
        };
        const baseLabel = labels[intent.type] || intent.type;
        // Add entity info if available
        if (intent.entities.length > 0) {
            const entity = intent.entities[0];
            if (entity.type === 'package') {
                return `Install ${entity.value}`;
            }
            else if (entity.type === 'problem') {
                return `Fix ${entity.value} issues`;
            }
            else if (entity.type === 'setting') {
                return `Change ${entity.value}`;
            }
        }
        return baseLabel;
    }
    /**
     * Get example for intent
     */
    getIntentExample(intent) {
        const examples = {
            'install': ['install firefox', 'I need a web browser'],
            'update': ['update my system', 'check for updates'],
            'query': ['what is installed?', 'show me my programs'],
            'troubleshoot': ['my wifi isn\'t working', 'fix my sound'],
            'config': ['make text bigger', 'change my wallpaper'],
            'greeting': ['hello', 'thank you'],
            'help': ['help', 'what can you do?']
        };
        const intentExamples = examples[intent.type] || [];
        return intentExamples[0] || intent.original;
    }
    /**
     * Generate follow-up question for more context
     */
    generateContextQuestion(intent) {
        if (intent.type === 'install' && !intent.entities.find(e => e.type === 'package')) {
            return "What kind of program are you looking for? For example: web browser, text editor, music player?";
        }
        if (intent.type === 'troubleshoot' && !intent.entities.find(e => e.type === 'problem')) {
            return "Can you tell me more about what's not working? For example: no internet, no sound, screen issues?";
        }
        if (intent.type === 'config' && !intent.entities.find(e => e.type === 'setting')) {
            return "What would you like to change? For example: font size, volume, wallpaper?";
        }
        return null;
    }
}
// Export singleton
export const ambiguityResolver = new AmbiguityResolver();
//# sourceMappingURL=ambiguity-resolver.js.map