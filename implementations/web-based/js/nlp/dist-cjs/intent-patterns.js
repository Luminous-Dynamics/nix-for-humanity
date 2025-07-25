/**
 * Comprehensive pattern database for Nix for Humanity
 * Covers common variations for all 5 personas
 */
import { normalizeServiceName } from './service-normalizer';
export const INTENT_PATTERNS = {
    // System maintenance patterns (high priority additions)
    maintenance: [
        {
            patterns: [
                /^(?:free up|clean up|clear|reclaim)(?: disk| storage)? space$/i,
                /^(?:my |the )?(?:disk|drive|storage|computer) is (?:full|running out of space)$/i,
                /^(?:delete|remove|clean)(?: old| unused)? (?:packages?|programs?|stuff)$/i,
                /^(?:run |do )?(?:garbage collection|gc|cleanup)$/i,
                /^(?:how )?(?:much|what) (?:space|storage)(?: is| am i)(?: being)? (?:used|free|available)$/i
            ],
            intent: 'maintenance',
            extractor: () => ({ action: 'garbage-collection' }),
            examples: [
                "free up space",
                "my disk is full",
                "clean up old packages",
                "run garbage collection",
                "how much space is being used"
            ]
        }
    ],
    logs: [
        {
            patterns: [
                /^(?:show|display|view|check)(?: me)?(?: the)? (?:system |error )?logs?$/i,
                /^(?:what|show me)(?: is)? (?:in the |the )?(?:system |error )?logs?$/i,
                /^(?:let me |I want to |can I )?(?:see|view|check)(?: the)? logs?$/i,
                /^(?:what went|what's going|what is) wrong(?:\?)?$/i,
                /^(?:why did|why is)(?: that| it)? (?:fail|failing|not work|broken)$/i,
                /^(?:show|check)(?: me)? (?:recent |last |latest )?errors?$/i
            ],
            intent: 'logs',
            extractor: (match) => ({
                logType: match[0].includes('error') ? 'errors' : 'system',
                timeframe: match[0].includes('recent') || match[0].includes('last') ? 'recent' : 'all'
            }),
            examples: [
                "show me the logs",
                "check system logs",
                "what went wrong",
                "show recent errors",
                "why did that fail"
            ]
        }
    ],
    service: [
        {
            patterns: [
                /^(?:is |check if |see if )?(.+?) (?:is )?(?:running|active|started|on|enabled)(?:\?)?$/i,
                /^(?:check|show|display)(?: the)? (?:status|state)(?: of)? (.+)$/i,
                /^(?:start|stop|restart|enable|disable) (.+?)(?: service)?$/i,
                /^(?:turn|switch) (?:on|off) (.+)$/i,
                /^(?:what|which) (?:services?|programs?) (?:are|is) (?:running|active)(?:\?)?$/i
            ],
            intent: 'service',
            extractor: (match) => {
                if (match[0].includes('what') || match[0].includes('which')) {
                    return { action: 'list', serviceName: 'all' };
                }
                const action = match[0].match(/^(start|stop|restart|enable|disable|turn on|turn off|switch on|switch off)/i)?.[0]
                    ?.replace(/turn |switch /i, '')
                    ?.replace(' on', 'start')
                    ?.replace(' off', 'stop') || 'status';
                return {
                    action: action.toLowerCase(),
                    serviceName: normalizeServiceName(match[1] || '')
                };
            },
            examples: [
                "is nginx running",
                "check status of postgresql",
                "start docker",
                "stop mysql service",
                "what services are running"
            ]
        }
    ],
    install: [
        {
            patterns: [
                /^(?:i )?(?:need|want|would like|gotta have|require|must have)(?: a| an| the)? (.+)$/i,
                /^(?:can you |please |could you )?(?:install|get|download|add|setup|set up) (.+?)(?: for me)?$/i,
                /^(?:give me|get me|I'd like|lemme have) (.+)$/i,
                /^(.+) (?:please|pls|plz)$/i
            ],
            intent: 'install',
            extractor: (match) => ({ package: normalizePackageName(match[1]) }),
            examples: [
                "I need a web browser",
                "install firefox",
                "can you get me vscode",
                "I'd like spotify please"
            ]
        },
        {
            patterns: [
                /^(?:i )?(?:need|want) (?:to|a way to) (.+)$/i,
                /^(?:how do i|how can i|help me) (.+)$/i
            ],
            intent: 'install',
            extractor: (match) => ({ task: match[1], package: inferPackageFromTask(match[1]) }),
            examples: [
                "I need to edit photos",
                "I want to write code",
                "help me browse the internet"
            ]
        }
    ],
    update: [
        {
            patterns: [
                /^(?:please |can you )?(?:update|upgrade|refresh)(?: (?:my |the )?(?:system|computer|machine|everything))?$/i,
                /^(?:check for|look for|find)(?: system| any)? updates?$/i,
                /^(?:is|are) (?:there |my system |everything )?(?:any )?(?:updates?|up(?:-| )to(?:-| )date)(?:\?)?$/i,
                /^(?:make sure|ensure) (?:everything is|I'm|system is) (?:current|updated|up(?:-| )to(?:-| )date)$/i
            ],
            intent: 'update',
            examples: [
                "update my system",
                "check for updates",
                "is everything up to date?",
                "please upgrade"
            ]
        }
    ],
    query: [
        {
            patterns: [
                /^(?:what|which)(?: programs?| apps?| software)? (?:do i have|are|is) (?:installed|on (?:my |this )?(?:computer|system|machine))?$/i,
                /^(?:show|list|display)(?: me)?(?: all| the)? (?:installed |my )?(?:programs?|apps?|software|packages?)$/i,
                /^(?:what's|whats|what is) (?:installed|on (?:here|this|my computer))$/i
            ],
            intent: 'query',
            extractor: () => ({ queryType: 'list-installed' }),
            examples: [
                "what programs do I have",
                "show me installed software",
                "list my apps"
            ]
        },
        {
            patterns: [
                /^(?:what|whats|what's)(?: exactly)? (?:is |does )?(.+?)(?: do)?$/i,
                /^(?:tell me|explain|describe)(?: about)? (.+)$/i,
                /^(?:info|information)(?: (?:on|about))? (.+)$/i
            ],
            intent: 'query',
            extractor: (match) => ({ queryType: 'info', subject: match[1] }),
            examples: [
                "what is firefox",
                "tell me about vscode",
                "info on git"
            ]
        }
    ],
    troubleshoot: [
        {
            patterns: [
                /^(?:my |the )?(.+?) (?:isn't|isnt|is not|ain't|aint|won't|wont|doesn't|doesnt|don't|dont) (?:work|working|function|functioning)$/i,
                /^(?:I )?(?:can't|cant|cannot|can not) (.+)$/i,
                /^(?:help|fix|repair|troubleshoot)(?: me)?(?: with)?(?: my| the)? (.+)$/i,
                /^(.+?) (?:is |seems )?(?:broken|busted|dead|stuck|frozen|messed up|screwed up)$/i
            ],
            intent: 'troubleshoot',
            extractor: (match) => ({ problem: identifyProblem(match[1]) }),
            examples: [
                "my internet isn't working",
                "I can't print",
                "help with my sound",
                "wifi is broken"
            ]
        },
        {
            patterns: [
                /^(?:no|not getting any|don't have|dont have) (.+)$/i,
                /^(.+?) (?:stopped|quit|crashed)$/i
            ],
            intent: 'troubleshoot',
            extractor: (match) => ({ problem: identifyProblem(match[1]) }),
            examples: [
                "no internet",
                "firefox crashed",
                "sound stopped"
            ]
        }
    ],
    config: [
        {
            patterns: [
                /^(?:make|set|change)(?: the)? (.+?) (?:bigger|larger|smaller|louder|quieter|brighter|darker|faster|slower)$/i,
                /^(?:increase|decrease|raise|lower|boost|reduce)(?: the)? (.+)$/i,
                /^(?:I )?(?:can't|cant|cannot) (?:see|read|hear) (?:well|properly|clearly)?$/i
            ],
            intent: 'config',
            extractor: (match) => ({ setting: identifySetting(match[0]) }),
            examples: [
                "make the text bigger",
                "increase font size",
                "I can't see well",
                "make sound louder"
            ]
        },
        {
            patterns: [
                /^(?:how do i |can i |help me )?(?:change|adjust|modify|configure|setup|set up)(?: the| my)? (.+)$/i,
                /^(?:where|how)(?: do i| can i)? (?:find |go to )?(?:settings?|preferences?|options?|config(?:uration)?)(?: for (.+))?$/i
            ],
            intent: 'config',
            extractor: (match) => ({ configTarget: match[1] || 'general' }),
            examples: [
                "how do I change wallpaper",
                "where are settings",
                "configure my mouse"
            ]
        }
    ],
    // Friendly responses that don't need actions
    greeting: [
        {
            patterns: [
                /^(?:hi|hello|hey|howdy|greetings?|good (?:morning|afternoon|evening))(?:\!|\.)?$/i,
                /^(?:thank you|thanks|thx|ty|cheers)(?:\!|\.)?$/i
            ],
            intent: 'greeting',
            examples: ["hello", "hi there", "thank you"]
        }
    ],
    help: [
        {
            patterns: [
                /^(?:help|what can you do|how do you work|what do you do)(?:\?)?$/i,
                /^(?:I'm |I am )?(?:lost|confused|stuck|not sure what to do)$/i
            ],
            intent: 'help',
            examples: ["help", "what can you do", "I'm lost"]
        }
    ]
};
/**
 * Normalize package names from natural language
 */
export function normalizePackageName(input) {
    const commonMappings = {
        // Browsers
        'web browser': 'firefox',
        'browser': 'firefox',
        'internet browser': 'firefox',
        'chrome': 'google-chrome',
        'chromium': 'chromium',
        'brave': 'brave',
        'edge': 'microsoft-edge',
        // Editors
        'text editor': 'neovim',
        'code editor': 'vscode',
        'programming editor': 'vscode',
        'visual studio': 'vscode',
        'visual studio code': 'vscode',
        'vs code': 'vscode',
        'vscode': 'vscode',
        'coding program': 'vscode',
        'programming thing': 'vscode',
        'that coding thing': 'vscode',
        'vim': 'neovim',
        'neovim': 'neovim',
        'emacs': 'emacs',
        'sublime': 'sublime-text',
        'atom': 'atom',
        // Communication
        'email': 'thunderbird',
        'mail': 'thunderbird',
        'email client': 'thunderbird',
        'chat': 'discord',
        'discord': 'discord',
        'slack': 'slack',
        'teams': 'teams',
        'video chat': 'zoom',
        'video call': 'zoom',
        'zoom': 'zoom',
        'skype': 'skype',
        // Media
        'music': 'spotify',
        'music player': 'spotify',
        'spotify': 'spotify',
        'video player': 'vlc',
        'movie player': 'vlc',
        'vlc': 'vlc',
        'mpv': 'mpv',
        'photo editor': 'gimp',
        'image editor': 'gimp',
        'gimp': 'gimp',
        'photoshop alternative': 'gimp',
        'krita': 'krita',
        'inkscape': 'inkscape',
        // Office
        'office': 'libreoffice',
        'word processor': 'libreoffice',
        'word': 'libreoffice',
        'excel': 'libreoffice',
        'powerpoint': 'libreoffice',
        'spreadsheet': 'libreoffice',
        'libreoffice': 'libreoffice',
        // Development
        'git': 'git',
        'python': 'python3',
        'python3': 'python3',
        'node': 'nodejs',
        'nodejs': 'nodejs',
        'npm': 'nodejs',
        'docker': 'docker',
        'rust': 'rustup',
        'go': 'go',
        'java': 'openjdk',
        'gcc': 'gcc',
        'make': 'gnumake',
        // Utilities
        'calculator': 'gnome-calculator',
        'calc': 'gnome-calculator',
        'terminal': 'alacritty',
        'console': 'alacritty',
        'file manager': 'nautilus',
        'files': 'nautilus',
        'htop': 'htop',
        'top': 'htop',
        'neofetch': 'neofetch'
    };
    const normalized = input.toLowerCase().trim();
    // Check exact matches first
    if (commonMappings[normalized]) {
        return commonMappings[normalized];
    }
    // Check if input contains any mapping keys
    for (const [key, value] of Object.entries(commonMappings)) {
        if (normalized.includes(key)) {
            return value;
        }
    }
    // Return cleaned input as package name
    return normalized.replace(/[^a-z0-9\-]/g, '');
}
/**
 * Infer package from task description
 */
export function inferPackageFromTask(task) {
    const taskMappings = {
        'browse': 'firefox',
        'internet': 'firefox',
        'code': 'vscode',
        'program': 'vscode',
        'develop': 'vscode',
        'email': 'thunderbird',
        'music': 'spotify',
        'video': 'vlc',
        'movie': 'vlc',
        'photo': 'gimp',
        'image': 'gimp',
        'document': 'libreoffice',
        'write': 'libreoffice',
        'calculate': 'gnome-calculator',
        'terminal': 'alacritty'
    };
    const taskLower = task.toLowerCase();
    for (const [key, pkg] of Object.entries(taskMappings)) {
        if (taskLower.includes(key)) {
            return pkg;
        }
    }
    return '';
}
/**
 * Identify problem type from description
 */
export function identifyProblem(description) {
    const problemMappings = {
        'network': ['internet', 'wifi', 'network', 'connection', 'online', 'ethernet'],
        'audio': ['sound', 'audio', 'speaker', 'headphone', 'music', 'hear', 'volume'],
        'display': ['screen', 'display', 'monitor', 'resolution', 'graphics', 'see', 'visual'],
        'print': ['print', 'printer', 'printing'],
        'bluetooth': ['bluetooth', 'wireless', 'airpods'],
        'performance': ['slow', 'lag', 'freeze', 'frozen', 'stuck', 'performance']
    };
    const descLower = description.toLowerCase();
    for (const [problem, keywords] of Object.entries(problemMappings)) {
        if (keywords.some(keyword => descLower.includes(keyword))) {
            return problem;
        }
    }
    return 'general';
}
/**
 * Identify setting type from description
 */
export function identifySetting(description) {
    const settingMappings = {
        'font-size': ['text', 'font', 'bigger', 'larger', 'smaller', 'size', 'read', 'see'],
        'volume': ['sound', 'audio', 'louder', 'quieter', 'volume', 'hear'],
        'brightness': ['bright', 'dark', 'dim', 'light', 'screen'],
        'theme': ['theme', 'color', 'appearance', 'dark mode', 'light mode'],
        'wallpaper': ['wallpaper', 'background', 'desktop'],
        'mouse': ['mouse', 'cursor', 'pointer', 'click'],
        'keyboard': ['keyboard', 'typing', 'keys']
    };
    const descLower = description.toLowerCase();
    for (const [setting, keywords] of Object.entries(settingMappings)) {
        if (keywords.some(keyword => descLower.includes(keyword))) {
            return setting;
        }
    }
    return 'general';
}
//# sourceMappingURL=intent-patterns.js.map