/**
 * Natural Language Processing Service for Nix for Humanity
 * Hybrid approach: Rules + Statistical + Neural (when needed)
 */

const natural = require('natural');
const Fuse = require('fuse.js');
const path = require('path');
const fs = require('fs').promises;

class NLPService {
  constructor(options = {}) {
    this.patternsFile = options.patternsFile || path.join(__dirname, 'patterns.json');
    this.contextWindow = options.contextWindow || 5;
    this.confidenceThreshold = options.confidenceThreshold || 0.7;
    
    // Initialize NLP components
    this.tokenizer = new natural.WordTokenizer();
    this.stemmer = natural.PorterStemmer;
    this.classifier = new natural.BayesClassifier();
    
    // Context management
    this.context = {
      history: [],
      lastIntent: null,
      lastPackage: null,
      lastService: null
    };
    
    // Initialize on construction
    this.initPromise = this.initialize();
  }

  async initialize() {
    // Load patterns
    this.patterns = await this.loadPatterns();
    
    // Initialize fuzzy search for package names
    this.packageSearch = new Fuse([], {
      keys: ['name', 'description'],
      threshold: 0.3,
      includeScore: true
    });
    
    // Train classifier
    this.trainClassifier();
  }

  async ensureInitialized() {
    await this.initPromise;
  }

  async loadPatterns() {
    try {
      const data = await fs.readFile(this.patternsFile, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      // Return default patterns if file doesn't exist
      return this.getDefaultPatterns();
    }
  }

  getDefaultPatterns() {
    return {
      intents: {
        install: {
          patterns: [
            'install {package}',
            'i need {package}',
            'get me {package}',
            'add {package}',
            'setup {package}',
            'i want to use {package}',
            'put {package} on my computer',
            'download {package}',
            'install {package} please',
            'can you install {package}',
            'help me install {package}'
          ],
          examples: [
            'install firefox',
            'i need a web browser',
            'get me something to browse the internet',
            'setup development tools'
          ]
        },
        remove: {
          patterns: [
            'remove {package}',
            'uninstall {package}',
            'delete {package}',
            'get rid of {package}',
            'i dont need {package} anymore',
            'take off {package}',
            'remove {package} from my system',
            'clean up {package}'
          ],
          examples: [
            'remove firefox',
            'uninstall that browser',
            'get rid of old packages'
          ]
        },
        update: {
          patterns: [
            'update',
            'update system',
            'update everything',
            'upgrade',
            'get latest',
            'check for updates',
            'make everything current',
            'refresh system',
            'update all packages',
            'upgrade nixos'
          ],
          examples: [
            'update my system',
            'check for updates',
            'upgrade everything'
          ]
        },
        search: {
          patterns: [
            'search {query}',
            'find {query}',
            'look for {query}',
            'what packages for {query}',
            'show me {query}',
            'list {query}',
            'search for {query}'
          ],
          examples: [
            'search browsers',
            'find text editors',
            'what packages for python'
          ]
        },
        service: {
          patterns: [
            'start {service}',
            'stop {service}',
            'restart {service}',
            'enable {service}',
            'disable {service}',
            'is {service} running',
            '{service} status',
            'check {service}'
          ],
          examples: [
            'start nginx',
            'is mysql running',
            'restart the web server'
          ]
        },
        troubleshoot: {
          patterns: [
            'wifi not working',
            'no internet',
            'cant connect',
            'network broken',
            'no sound',
            'audio not working',
            'screen issues',
            'system slow',
            'help',
            'something wrong'
          ],
          examples: [
            'my wifi isnt working',
            'i have no sound',
            'the system is slow'
          ]
        },
        query: {
          patterns: [
            'show installed',
            'list packages',
            'what is installed',
            'disk space',
            'memory usage',
            'system info',
            'show logs',
            'recent errors'
          ],
          examples: [
            'show me whats installed',
            'how much disk space',
            'check system logs'
          ]
        }
      },
      entities: {
        packages: {
          browsers: ['firefox', 'chromium', 'brave', 'chrome', 'opera', 'vivaldi'],
          editors: ['vim', 'neovim', 'emacs', 'vscode', 'sublime', 'atom', 'nano'],
          development: ['git', 'nodejs', 'python', 'rust', 'gcc', 'docker'],
          media: ['vlc', 'mpv', 'spotify', 'audacity', 'gimp', 'inkscape'],
          terminal: ['alacritty', 'kitty', 'konsole', 'gnome-terminal'],
          utilities: ['htop', 'tree', 'wget', 'curl', 'jq', 'ripgrep']
        },
        services: {
          web: ['nginx', 'apache', 'httpd'],
          database: ['mysql', 'postgresql', 'mongodb', 'redis'],
          network: ['NetworkManager', 'sshd', 'firewall'],
          system: ['systemd', 'cron', 'docker']
        },
        categories: {
          'web browser': ['firefox', 'chromium', 'brave'],
          'text editor': ['vim', 'neovim', 'emacs', 'vscode'],
          'development': ['git', 'nodejs', 'python'],
          'music player': ['spotify', 'rhythmbox', 'clementine'],
          'video player': ['vlc', 'mpv', 'mplayer']
        }
      },
      corrections: {
        'firfox': 'firefox',
        'chorme': 'chrome',
        'chromuim': 'chromium',
        'vs code': 'vscode',
        'git hub': 'github',
        'node js': 'nodejs',
        'post gres': 'postgresql',
        'my sql': 'mysql'
      }
    };
  }

  trainClassifier() {
    // Train the classifier with examples
    const patterns = this.patterns.intents;
    
    for (const [intent, data] of Object.entries(patterns)) {
      if (data.examples) {
        data.examples.forEach(example => {
          this.classifier.addDocument(example, intent);
        });
      }
    }
    
    this.classifier.train();
  }

  async processInput(input, context = {}) {
    await this.ensureInitialized();
    
    // Normalize input
    const normalized = this.normalizeInput(input);
    
    // Update context
    this.updateContext(normalized, context);
    
    // Layer 1: Rule-based pattern matching (fast)
    let intent = this.matchRuleBasedPattern(normalized);
    
    // Layer 2: Statistical classification if no rule match
    if (!intent || intent.confidence < this.confidenceThreshold) {
      const statistical = this.classifyStatistically(normalized);
      if (!intent || statistical.confidence > intent.confidence) {
        intent = statistical;
      }
    }
    
    // Layer 3: Context enhancement
    intent = this.enhanceWithContext(intent);
    
    // Extract entities
    intent.entities = this.extractEntities(normalized, intent);
    
    // Apply corrections
    intent = this.applyCorrections(intent);
    
    return intent;
  }

  normalizeInput(input) {
    // Convert to lowercase and trim
    let normalized = input.toLowerCase().trim();
    
    // Expand contractions
    normalized = normalized
      .replace(/can't/g, 'cannot')
      .replace(/won't/g, 'will not')
      .replace(/n't/g, ' not')
      .replace(/'ll/g, ' will')
      .replace(/'ve/g, ' have')
      .replace(/'re/g, ' are')
      .replace(/'d/g, ' would');
    
    // Remove extra spaces
    normalized = normalized.replace(/\s+/g, ' ');
    
    return normalized;
  }

  matchRuleBasedPattern(input) {
    const patterns = this.patterns.intents;
    let bestMatch = null;
    let highestConfidence = 0;
    
    for (const [intentType, intentData] of Object.entries(patterns)) {
      for (const pattern of intentData.patterns) {
        const match = this.matchPattern(input, pattern);
        if (match && match.confidence > highestConfidence) {
          highestConfidence = match.confidence;
          bestMatch = {
            type: intentType,
            confidence: match.confidence,
            matches: match.captures
          };
        }
      }
    }
    
    return bestMatch;
  }

  matchPattern(input, pattern) {
    // Convert pattern to regex
    const regexPattern = pattern
      .replace(/\{(\w+)\}/g, '(?<$1>.*?)') // Named capture groups
      .replace(/\s+/g, '\\s+'); // Flexible whitespace
    
    try {
      const regex = new RegExp(`^${regexPattern}$`, 'i');
      const match = input.match(regex);
      
      if (match) {
        return {
          confidence: 1.0, // Rule-based matches have high confidence
          captures: match.groups || {}
        };
      }
    } catch (e) {
      // Invalid regex, skip
    }
    
    // Fuzzy matching for partial matches
    const words = pattern.toLowerCase().split(/\s+/);
    const inputWords = input.toLowerCase().split(/\s+/);
    let matches = 0;
    
    words.forEach(word => {
      if (!word.includes('{') && inputWords.includes(word)) {
        matches++;
      }
    });
    
    const confidence = matches / words.length;
    if (confidence > 0.5) {
      return { confidence: confidence * 0.8, captures: {} };
    }
    
    return null;
  }

  classifyStatistically(input) {
    const classifications = this.classifier.getClassifications(input);
    
    if (classifications.length > 0) {
      const best = classifications[0];
      return {
        type: best.label,
        confidence: best.value,
        method: 'statistical'
      };
    }
    
    return {
      type: 'unknown',
      confidence: 0,
      method: 'none'
    };
  }

  enhanceWithContext(intent) {
    // Use context to improve intent recognition
    if (intent.type === 'unknown' && this.context.lastIntent) {
      // Check if this might be a follow-up
      if (this.context.lastIntent === 'search' && intent.matches) {
        // "install it" after a search
        if (intent.input?.includes('it') || intent.input?.includes('that')) {
          return {
            ...intent,
            type: 'install',
            confidence: 0.8,
            contextual: true
          };
        }
      }
    }
    
    // Boost confidence if consistent with recent context
    if (intent.type === this.context.lastIntent) {
      intent.confidence = Math.min(1.0, intent.confidence * 1.1);
    }
    
    return intent;
  }

  extractEntities(input, intent) {
    const entities = {
      packages: [],
      services: [],
      categories: []
    };
    
    // Extract package names
    if (intent.matches?.package) {
      entities.packages.push(intent.matches.package);
    } else {
      // Look for known packages
      const words = input.split(/\s+/);
      words.forEach(word => {
        for (const [category, packages] of Object.entries(this.patterns.entities.packages)) {
          if (packages.includes(word)) {
            entities.packages.push(word);
            entities.categories.push(category);
          }
        }
      });
    }
    
    // Extract service names
    if (intent.matches?.service) {
      entities.services.push(intent.matches.service);
    } else {
      // Look for known services
      const words = input.split(/\s+/);
      words.forEach(word => {
        for (const [category, services] of Object.entries(this.patterns.entities.services)) {
          if (services.includes(word)) {
            entities.services.push(word);
          }
        }
      });
    }
    
    // Extract categories
    for (const [category, keywords] of Object.entries(this.patterns.entities.categories)) {
      if (input.includes(category)) {
        entities.categories.push(category);
        // Also add associated packages
        entities.packages.push(...keywords);
      }
    }
    
    return entities;
  }

  applyCorrections(intent) {
    // Apply spelling corrections to entities
    const corrections = this.patterns.corrections;
    
    if (intent.entities?.packages) {
      intent.entities.packages = intent.entities.packages.map(pkg => {
        return corrections[pkg] || pkg;
      });
    }
    
    if (intent.matches) {
      for (const [key, value] of Object.entries(intent.matches)) {
        if (corrections[value]) {
          intent.matches[key] = corrections[value];
        }
      }
    }
    
    return intent;
  }

  updateContext(input, context) {
    // Add to history
    this.context.history.push({
      input,
      timestamp: Date.now(),
      ...context
    });
    
    // Keep only recent history
    if (this.context.history.length > this.contextWindow) {
      this.context.history.shift();
    }
  }

  setLastIntent(intent) {
    this.context.lastIntent = intent.type;
    if (intent.entities?.packages?.[0]) {
      this.context.lastPackage = intent.entities.packages[0];
    }
    if (intent.entities?.services?.[0]) {
      this.context.lastService = intent.entities.services[0];
    }
  }

  // Voice processing (stub for now)
  async processVoice(audioData, options = {}) {
    // TODO: Integrate with Whisper.cpp
    throw new Error('Voice processing not yet implemented');
  }

  // Get suggestions for partial input
  getSuggestions(partial) {
    const suggestions = [];
    const normalizedPartial = partial.toLowerCase();
    
    // Check all patterns
    for (const intentData of Object.values(this.patterns.intents)) {
      for (const pattern of intentData.patterns) {
        if (pattern.toLowerCase().startsWith(normalizedPartial)) {
          suggestions.push(pattern.replace(/\{.*?\}/g, '...'));
        }
      }
    }
    
    // Also check examples
    for (const intentData of Object.values(this.patterns.intents)) {
      if (intentData.examples) {
        for (const example of intentData.examples) {
          if (example.toLowerCase().startsWith(normalizedPartial)) {
            suggestions.push(example);
          }
        }
      }
    }
    
    return [...new Set(suggestions)].slice(0, 5);
  }

  // Save learned patterns
  async savePatterns() {
    await fs.writeFile(
      this.patternsFile,
      JSON.stringify(this.patterns, null, 2)
    );
  }

  // Add new pattern based on user feedback
  async learnPattern(input, intent, success) {
    if (success && intent.confidence < 0.9) {
      // Add as example for future training
      if (!this.patterns.intents[intent.type].examples) {
        this.patterns.intents[intent.type].examples = [];
      }
      
      if (!this.patterns.intents[intent.type].examples.includes(input)) {
        this.patterns.intents[intent.type].examples.push(input);
        
        // Retrain classifier
        this.classifier.addDocument(input, intent.type);
        this.classifier.train();
        
        // Save updated patterns
        await this.savePatterns();
      }
    }
  }
}

module.exports = NLPService;