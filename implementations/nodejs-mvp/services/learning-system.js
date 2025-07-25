// 🧠 Simple Learning System - JSON-based for MVP
const fs = require('fs').promises;
const path = require('path');

class LearningSystem {
  constructor() {
    this.dataFile = path.join(__dirname, '..', 'storage', 'learning.json');
    this.data = {
      userPatterns: {},
      commandHistory: [],
      preferences: {},
      statistics: {
        totalCommands: 0,
        successfulCommands: 0,
        commonIntents: {}
      }
    };
    
    // Load existing data on startup
    this.loadData();
  }

  async loadData() {
    try {
      const content = await fs.readFile(this.dataFile, 'utf8');
      this.data = JSON.parse(content);
    } catch (error) {
      // File doesn't exist yet, use defaults
      console.log('No existing learning data, starting fresh');
      await this.saveData();
    }
  }

  async saveData() {
    try {
      await fs.mkdir(path.dirname(this.dataFile), { recursive: true });
      await fs.writeFile(this.dataFile, JSON.stringify(this.data, null, 2));
    } catch (error) {
      console.error('Failed to save learning data:', error);
    }
  }

  async learn(interaction) {
    const { input, intent, command, result, context } = interaction;
    
    // Update statistics
    this.data.statistics.totalCommands++;
    if (result.success) {
      this.data.statistics.successfulCommands++;
    }
    
    // Track intent frequency
    const intentKey = intent.action || 'unknown';
    this.data.statistics.commonIntents[intentKey] = 
      (this.data.statistics.commonIntents[intentKey] || 0) + 1;
    
    // Learn user patterns (word substitutions)
    if (intent.confidence > 0.8) {
      this.learnPattern(input, intent);
    }
    
    // Add to history (keep last 100)
    this.data.commandHistory.push({
      timestamp: new Date().toISOString(),
      input,
      intent: intent.action,
      success: result.success,
      command: command.raw
    });
    
    if (this.data.commandHistory.length > 100) {
      this.data.commandHistory = this.data.commandHistory.slice(-100);
    }
    
    // Save periodically (every 10 commands)
    if (this.data.statistics.totalCommands % 10 === 0) {
      await this.saveData();
    }
  }

  learnPattern(input, intent) {
    // Extract potential synonyms the user uses
    const words = input.toLowerCase().split(' ');
    
    // Map user words to standard actions
    const actionMappings = {
      'search': ['find', 'look', 'locate', 'get'],
      'list': ['show', 'display', 'what'],
      'install': ['add', 'get', 'grab', 'download']
    };
    
    for (const [standard, synonyms] of Object.entries(actionMappings)) {
      for (const word of words) {
        if (synonyms.includes(word) && intent.action === standard) {
          // User uses this word for this action
          if (!this.data.userPatterns[word]) {
            this.data.userPatterns[word] = {};
          }
          this.data.userPatterns[word][standard] = 
            (this.data.userPatterns[word][standard] || 0) + 1;
        }
      }
    }
  }

  async getTopCommands() {
    // Return most common commands for suggestions
    const intents = Object.entries(this.data.statistics.commonIntents)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5)
      .map(([intent, count]) => ({
        intent,
        count,
        example: this.getExampleForIntent(intent)
      }));
    
    return intents;
  }

  getExampleForIntent(intent) {
    const examples = {
      'search': 'search firefox',
      'list': 'show installed packages',
      'info': 'system info',
      'check': 'check system health'
    };
    
    return examples[intent] || `${intent} command`;
  }

  async getData() {
    // Return all learning data (for development)
    return this.data;
  }

  getSuccessRate() {
    if (this.data.statistics.totalCommands === 0) return 0;
    return this.data.statistics.successfulCommands / this.data.statistics.totalCommands;
  }
}

module.exports = LearningSystem;