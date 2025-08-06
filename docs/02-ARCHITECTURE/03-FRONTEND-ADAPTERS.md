# NLP Architecture - Nix for Humanity

## Overview

This document details the hybrid Natural Language Processing architecture that powers Nix for Humanity's conversational interface. Our approach combines rule-based patterns, statistical models, and neural networks to achieve high accuracy while maintaining explainability and performance.

## Core Architecture

### Hybrid NLP Pipeline

```yaml
┌─────────────────────────────────────────────────────────────┐
│                    User Input (Voice/Text)                   │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                    Input Processing Layer                     │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  Language   │  │ Tokenization │  │  Normalization  │   │
│  │  Detection  │  │  & Cleaning  │  │  & Expansion    │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                  Understanding Pipeline                       │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │Rule-Based   │  │ Statistical  │  │    Neural       │   │
│  │Pattern Match│  │   Models     │  │   Networks      │   │
│  │(Fast Path)  │  │(Flexibility) │  │(Deep Understanding)│ │
│  └──────┬──────┘  └──────┬───────┘  └────────┬────────┘   │
│         └─────────────────┴───────────────────┘            │
│                           │                                  │
│                    Ensemble Resolution                       │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                     Intent & Entities                         │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   Intent    │  │   Entity     │  │   Confidence    │   │
│  │Classification│  │ Recognition  │  │    Scoring      │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                    Dialogue Management                        │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  Context    │  │ Clarification│  │    Response     │   │
│  │  Tracking   │  │  Strategies  │  │   Generation    │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────┴───────────────────────────────┘
```

## Implementation Details

### 1. Input Processing Layer

```javascript
class InputProcessor {
  constructor() {
    this.languageDetector = new LanguageDetector({
      languages: ['en', 'es', 'de', 'fr', 'zh', 'ja'],
      fallback: 'en'
    });
    
    this.tokenizer = new AdvancedTokenizer({
      handleContractions: true,
      preserveCase: false,
      expandAbbreviations: true
    });
    
    this.normalizer = new TextNormalizer({
      correctSpelling: true,
      expandSynonyms: true,
      handleTypos: true
    });
  }
  
  async process(input) {
    // Detect language
    const language = await this.languageDetector.detect(input);
    
    // Tokenize with language-specific rules
    const tokens = this.tokenizer.tokenize(input, language);
    
    // Normalize and expand
    const normalized = this.normalizer.normalize(tokens);
    
    return {
      original: input,
      language,
      tokens,
      normalized,
      features: this.extractFeatures(normalized)
    };
  }
}
```

### 2. Rule-Based Pattern Matching (Fast Path)

```javascript
const CommonPatterns = {
  install: {
    patterns: [
      /^(install|add|get|download|i need|i want|set up)\s+(.+)$/i,
      /^(.+)\s+(is missing|not installed|isn't installed)$/i,
      /^can you (install|add|get)\s+(.+)(\s+for me)?$/i,
      /^please (install|add)\s+(.+)$/i
    ],
    
    extractor: (match, input) => ({
      intent: 'package.install',
      entities: {
        package: extractPackageName(match),
        urgent: detectUrgency(input)
      },
      confidence: 0.95
    })
  },
  
  troubleshoot: {
    patterns: [
      /^(fix|repair|troubleshoot|debug)\s+(.+)$/i,
      /^(.+)\s+(is broken|not working|won't start|crashed)$/i,
      /^(something's wrong with|problem with|issue with)\s+(.+)$/i,
      /^why (isn't|won't)\s+(.+)\s+(working|starting)$/i
    ],
    
    extractor: (match, input) => ({
      intent: 'system.troubleshoot',
      entities: {
        target: extractProblemTarget(match),
        symptoms: extractSymptoms(input)
      },
      confidence: 0.90
    })
  },
  
  update: {
    patterns: [
      /^(update|upgrade)\s*(everything|all|system)?$/i,
      /^check for updates$/i,
      /^what needs updating\??$/i,
      /^keep my system (current|up to date)$/i
    ],
    
    extractor: (match, input) => ({
      intent: 'system.update',
      entities: {
        scope: match[2] || 'system',
        checkOnly: input.includes('check')
      },
      confidence: 0.95
    })
  }
};

// Fast pattern matcher
class RuleBasedMatcher {
  match(input) {
    for (const [category, config] of Object.entries(CommonPatterns)) {
      for (const pattern of config.patterns) {
        const match = input.match(pattern);
        if (match) {
          return config.extractor(match, input);
        }
      }
    }
    return null;
  }
}
```

### 3. Statistical Models (Flexibility Layer)

```javascript
class StatisticalIntentClassifier {
  constructor() {
    // CRF model for sequence labeling
    this.crf = new CRFModel({
      features: [
        'word', 'pos', 'shape', 'prefix', 'suffix',
        'prev_word', 'next_word', 'bigram', 'trigram'
      ],
      labels: IntentCategories,
      modelPath: './models/nix-intent-crf.model'
    });
    
    // Maximum Entropy classifier for intent
    this.maxent = new MaxEntClassifier({
      features: ['bow', 'bigrams', 'syntax', 'length'],
      smoothing: 'laplace'
    });
  }
  
  async classify(input, context) {
    // Extract features
    const features = await this.extractFeatures(input);
    
    // CRF for sequence understanding
    const sequence = await this.crf.label(features.sequence);
    
    // MaxEnt for intent classification
    const intent = await this.maxent.classify(features.document);
    
    // Combine predictions
    return {
      intent: intent.label,
      confidence: intent.probability * 0.8, // Conservative confidence
      entities: this.extractEntitiesFromSequence(sequence),
      alternativeIntents: intent.alternatives
    };
  }
}
```

### 4. Neural Network Models (Deep Understanding)

```javascript
class NeuralIntentUnderstanding {
  constructor() {
    // Small BERT variant for NixOS domain
    this.transformer = new TransformerModel({
      modelName: 'nix-bert-small',
      maxLength: 128,
      numLabels: 47, // Number of intent categories
      architecture: {
        hiddenSize: 256,
        numLayers: 6,
        numHeads: 8
      }
    });
    
    // Entity recognition model
    this.ner = new NERModel({
      modelName: 'nix-ner',
      entities: ['PACKAGE', 'SERVICE', 'CONFIG', 'FILE', 'ERROR']
    });
  }
  
  async understand(input, context) {
    // Encode input with context
    const encoding = await this.transformer.encode(input, context);
    
    // Get intent predictions
    const intentLogits = await this.transformer.predictIntent(encoding);
    const intent = this.decodeIntent(intentLogits);
    
    // Extract entities
    const entities = await this.ner.extractEntities(encoding);
    
    // Context-aware adjustments
    const adjusted = this.adjustForContext(intent, entities, context);
    
    return {
      intent: adjusted.intent,
      confidence: adjusted.confidence,
      entities: adjusted.entities,
      explanation: this.generateExplanation(encoding)
    };
  }
}
```

### 5. Ensemble Resolution

```javascript
class EnsembleResolver {
  constructor() {
    this.weights = {
      rules: 0.4,      // Fast and accurate for common cases
      statistical: 0.3, // Good generalization
      neural: 0.3      // Deep understanding
    };
    
    this.confidenceThreshold = 0.8;
  }
  
  async resolve(results, context) {
    const { ruleResult, statResult, neuralResult } = results;
    
    // Fast path: High confidence rule match
    if (ruleResult && ruleResult.confidence > 0.9) {
      return this.formatResult(ruleResult, 'rule-based');
    }
    
    // Weighted ensemble
    const ensemble = this.weightedVote([
      { result: ruleResult, weight: this.weights.rules },
      { result: statResult, weight: this.weights.statistical },
      { result: neuralResult, weight: this.weights.neural }
    ]);
    
    // Confidence check
    if (ensemble.confidence < this.confidenceThreshold) {
      return this.requestClarification(ensemble, context);
    }
    
    return this.formatResult(ensemble, 'ensemble');
  }
  
  weightedVote(results) {
    const intentVotes = {};
    let totalWeight = 0;
    
    for (const { result, weight } of results) {
      if (!result) continue;
      
      const vote = result.confidence * weight;
      intentVotes[result.intent] = (intentVotes[result.intent] || 0) + vote;
      totalWeight += weight;
    }
    
    // Find winning intent
    const winner = Object.entries(intentVotes)
      .sort(([,a], [,b]) => b - a)[0];
    
    return {
      intent: winner[0],
      confidence: winner[1] / totalWeight,
      entities: this.mergeEntities(results)
    };
  }
}
```

## Entity Recognition and Extraction

### Package Name Resolution

```javascript
class PackageNameResolver {
  constructor() {
    // Common aliases and variations
    this.aliases = {
      'firefox': ['firefox-esr', 'firefox-bin', 'firefox'],
      'chrome': ['google-chrome', 'chromium', 'ungoogled-chromium'],
      'vscode': ['vscode', 'vscodium', 'code'],
      'python': ['python3', 'python311', 'python312'],
      // ... hundreds more
    };
    
    // Fuzzy matcher for close matches
    this.fuzzyMatcher = new FuzzyMatcher({
      threshold: 0.8,
      algorithm: 'levenshtein'
    });
  }
  
  async resolve(userInput) {
    // Check exact match
    if (await this.packageExists(userInput)) {
      return { package: userInput, confidence: 1.0 };
    }
    
    // Check aliases
    if (this.aliases[userInput.toLowerCase()]) {
      const candidates = this.aliases[userInput.toLowerCase()];
      return this.rankCandidates(candidates);
    }
    
    // Fuzzy search
    const fuzzyMatches = await this.fuzzySearch(userInput);
    if (fuzzyMatches.length > 0) {
      return this.presentOptions(fuzzyMatches);
    }
    
    // Semantic search using embeddings
    const semanticMatches = await this.semanticSearch(userInput);
    return this.presentOptions(semanticMatches);
  }
}
```

## Context Management

### Multi-Turn Conversation Tracking

```javascript
class ConversationContext {
  constructor() {
    this.history = [];
    this.entities = new Map();
    this.activeTask = null;
    this.userPreferences = new Map();
  }
  
  update(turn) {
    // Add to history
    this.history.push({
      timestamp: Date.now(),
      input: turn.input,
      intent: turn.intent,
      entities: turn.entities,
      result: turn.result
    });
    
    // Update entity memory
    for (const [type, value] of Object.entries(turn.entities)) {
      this.entities.set(type, {
        value,
        lastMentioned: Date.now(),
        mentions: (this.entities.get(type)?.mentions || 0) + 1
      });
    }
    
    // Track active task
    if (turn.intent.includes('start')) {
      this.activeTask = turn.intent;
    } else if (turn.intent.includes('complete')) {
      this.activeTask = null;
    }
    
    // Learn preferences
    this.updatePreferences(turn);
  }
  
  resolveReference(reference) {
    // Handle pronouns and references
    switch (reference.toLowerCase()) {
      case 'it':
      case 'that':
        return this.getLastEntity('PACKAGE') || this.getLastEntity('SERVICE');
      
      case 'the last one':
        return this.history[this.history.length - 1]?.entities;
      
      case 'the same':
        return this.getLastEntity();
      
      default:
        return null;
    }
  }
}
```

## Error Recovery and Clarification

### Intelligent Error Handling

```javascript
class SmartErrorRecovery {
  async handleLowConfidence(result, context) {
    const strategies = [
      this.suggestAlternatives,
      this.askForClarification,
      this.providExamples,
      this.offerManualMode
    ];
    
    for (const strategy of strategies) {
      const recovery = await strategy(result, context);
      if (recovery.applicable) {
        return recovery.response;
      }
    }
    
    return this.defaultFallback();
  }
  
  async suggestAlternatives(result, context) {
    if (result.alternativeIntents?.length > 0) {
      return {
        applicable: true,
        response: {
          type: 'clarification',
          message: "I'm not sure what you mean. Did you want to:",
          options: result.alternativeIntents.map(intent => ({
            intent,
            description: this.describeIntent(intent),
            example: this.getExample(intent)
          }))
        }
      };
    }
    return { applicable: false };
  }
  
  async askForClarification(result, context) {
    const missingInfo = this.identifyMissingInfo(result);
    
    if (missingInfo.length > 0) {
      return {
        applicable: true,
        response: {
          type: 'question',
          message: this.generateClarificationQuestion(missingInfo),
          expecting: missingInfo[0].type
        }
      };
    }
    return { applicable: false };
  }
}
```

## Performance Optimizations

### Caching and Precomputation

```javascript
class NLPCache {
  constructor() {
    // LRU cache for recent interpretations
    this.interpretationCache = new LRUCache({
      maxSize: 1000,
      ttl: 3600000 // 1 hour
    });
    
    // Precomputed embeddings for common phrases
    this.embeddingCache = new Map();
    
    // Compiled patterns for performance
    this.compiledPatterns = this.compileAllPatterns();
  }
  
  async getInterpretation(input) {
    const cacheKey = this.generateKey(input);
    
    // Check cache
    if (this.interpretationCache.has(cacheKey)) {
      return this.interpretationCache.get(cacheKey);
    }
    
    // Compute and cache
    const interpretation = await this.compute(input);
    this.interpretationCache.set(cacheKey, interpretation);
    
    return interpretation;
  }
}
```

### Progressive Enhancement

```javascript
class ProgressiveNLP {
  constructor(capabilities) {
    this.capabilities = capabilities;
    
    // Load components based on available resources
    if (capabilities.memory < 200) {
      this.mode = 'minimal';
      this.loadMinimalModels();
    } else if (capabilities.memory < 500) {
      this.mode = 'standard';
      this.loadStandardModels();
    } else {
      this.mode = 'full';
      this.loadFullModels();
    }
  }
  
  async understand(input, context) {
    switch (this.mode) {
      case 'minimal':
        // Rules only
        return this.ruleBasedOnly(input);
      
      case 'standard':
        // Rules + statistical
        return this.hybridUnderstanding(input, context);
      
      case 'full':
        // All models
        return this.fullUnderstanding(input, context);
    }
  }
}
```

## Testing and Validation

### Intent Recognition Test Suite

```yaml
Test Categories:
  1. Common Commands:
     - "install firefox" → package.install
     - "update system" → system.update
     - "show running services" → service.list
     
  2. Natural Variations:
     - "i need a text editor" → package.search + install
     - "my internet isn't working" → network.troubleshoot
     - "make the text bigger" → accessibility.font.increase
     
  3. Ambiguous Inputs:
     - "python" → clarify: package/version/documentation?
     - "help" → show common commands or specific help?
     - "fix it" → request more context
     
  4. Multi-turn Conversations:
     - "install that" (after package search)
     - "the same as yesterday" (context recall)
     - "cancel that" (action reversal)
     
  5. Error Conditions:
     - Typos: "instal fierfix" → install firefox
     - Mixed language: "install navigateur web"
     - Impossible requests: "install windows"
```

## Future Enhancements

### Planned Improvements

1. **Multilingual Support**
   - Language-specific models
   - Cross-lingual understanding
   - Automatic translation

2. **Advanced Context**
   - Long-term memory
   - User profiling
   - Task prediction

3. **Specialized Domains**
   - Development workflows
   - Server administration
   - Security operations

4. **Continuous Learning**
   - Online model updates
   - User feedback integration
   - Community patterns

## Conclusion

This hybrid NLP architecture provides Nix for Humanity with robust natural language understanding that scales from simple commands to complex conversations. By combining multiple approaches, we achieve high accuracy while maintaining explainability and performance across diverse hardware configurations.