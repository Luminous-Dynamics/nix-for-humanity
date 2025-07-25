# 🧠 NLP Implementation Guide

## Overview

This guide details the technical implementation of the Natural Language Processing engine for Nix for Humanity.

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│            Input Layer                       │
│  ┌──────────┐        ┌─────────────────┐   │
│  │  Voice   │───────▶│ Whisper.cpp     │   │
│  │  Input   │        │ (Local STT)     │   │
│  └──────────┘        └────────┬────────┘   │
│                               │             │
│  ┌──────────┐                │             │
│  │  Text    │────────────────┘             │
│  │  Input   │                              │
│  └──────────┘                              │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│           NLP Pipeline (TypeScript)          │
│  ┌────────────────────────────────────────┐ │
│  │ 1. Tokenization & Normalization        │ │
│  └────────────────────┬───────────────────┘ │
│  ┌────────────────────▼───────────────────┐ │
│  │ 2. Intent Recognition (Hybrid)         │ │
│  │    - Rule-based (Fast path)           │ │
│  │    - Statistical (Fuzzy matching)     │ │
│  │    - Neural (Context understanding)   │ │
│  └────────────────────┬───────────────────┘ │
│  ┌────────────────────▼───────────────────┐ │
│  │ 3. Entity Extraction                   │ │
│  │    - Package names                    │ │
│  │    - Service names                    │ │
│  │    - Configuration values             │ │
│  └────────────────────┬───────────────────┘ │
│  ┌────────────────────▼───────────────────┐ │
│  │ 4. Context Resolution                  │ │
│  │    - Pronoun resolution               │ │
│  │    - Multi-turn memory                │ │
│  └────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│         Command Generation (Rust)            │
│  ┌────────────────────────────────────────┐ │
│  │ Safe Nix AST Builder                   │ │
│  └────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

## Implementation Details

### 1. Input Processing

#### Voice Input (Whisper.cpp)
```typescript
import { WhisperCpp } from './whisper-bindings';

class VoiceProcessor {
  private whisper: WhisperCpp;
  
  constructor() {
    this.whisper = new WhisperCpp({
      model: 'base.en', // 140MB model
      language: 'en',
      threads: 4,
      maxLength: 30, // seconds
    });
  }
  
  async processAudio(audioBuffer: ArrayBuffer): Promise<string> {
    // Convert to 16kHz mono PCM
    const pcmData = await this.convertToPCM(audioBuffer);
    
    // Run Whisper
    const text = await this.whisper.transcribe(pcmData);
    
    return this.normalizeText(text);
  }
}
```

### 2. Hybrid NLP Pipeline

#### Layer 1: Rule-Based (95% accuracy for common commands)
```typescript
interface RulePattern {
  pattern: RegExp;
  intent: string;
  entities: string[];
  confidence: number;
}

const RULE_PATTERNS: RulePattern[] = [
  {
    pattern: /^install\s+(.+)$/i,
    intent: 'install_package',
    entities: ['package_name'],
    confidence: 0.99
  },
  {
    pattern: /^update\s*(system|everything)?$/i,
    intent: 'system_update',
    entities: [],
    confidence: 0.99
  },
  // ... 50+ patterns
];
```

#### Layer 2: Statistical (Handles variations)
```typescript
class StatisticalMatcher {
  private tfidf: TFIDF;
  private classifier: NaiveBayes;
  
  match(input: string): IntentMatch {
    // Fuzzy matching for typos
    const corrected = this.spellCheck(input);
    
    // Feature extraction
    const features = this.extractFeatures(corrected);
    
    // Classification
    const intent = this.classifier.classify(features);
    const confidence = this.classifier.getConfidence(features);
    
    return { intent, confidence };
  }
}
```

#### Layer 3: Neural (Context understanding)
```typescript
class NeuralUnderstanding {
  private model: TransformerModel;
  
  async understand(input: string, context: Context): Promise<Intent> {
    // Encode input with context
    const encoding = await this.model.encode(input, context);
    
    // Predict intent and entities
    const prediction = await this.model.predict(encoding);
    
    return {
      intent: prediction.intent,
      entities: prediction.entities,
      confidence: prediction.confidence
    };
  }
}
```

### 3. Entity Extraction

```typescript
class EntityExtractor {
  extractPackageName(text: string): string | null {
    // Direct match against nixpkgs
    const directMatch = this.nixpkgsIndex.find(text);
    if (directMatch) return directMatch;
    
    // Fuzzy search
    const fuzzyMatch = this.fuzzySearch(text);
    if (fuzzyMatch.score > 0.8) return fuzzyMatch.package;
    
    // Ask for clarification
    return null;
  }
  
  extractServiceName(text: string): string | null {
    // Known services
    const services = ['nginx', 'apache', 'mysql', 'postgresql'];
    return this.findBestMatch(text, services);
  }
}
```

### 4. Context Management

```typescript
class ContextManager {
  private history: Turn[] = [];
  private entities: Map<string, any> = new Map();
  
  resolvePronouns(text: string): string {
    // "install it" -> "install firefox" (if firefox was last mentioned)
    const resolved = text.replace(/\bit\b/g, () => {
      const lastEntity = this.getLastEntity('package');
      return lastEntity || 'it';
    });
    
    return resolved;
  }
  
  updateContext(turn: Turn) {
    this.history.push(turn);
    
    // Extract entities for future reference
    turn.entities.forEach(e => {
      this.entities.set(e.type, e.value);
    });
    
    // Keep only last 10 turns
    if (this.history.length > 10) {
      this.history.shift();
    }
  }
}
```

## Performance Optimization

### 1. Response Time Targets
- Tokenization: <10ms
- Rule matching: <20ms
- Statistical: <50ms
- Neural: <200ms
- Total: <300ms

### 2. Caching Strategy
```typescript
class IntentCache {
  private cache = new LRU<string, Intent>(1000);
  
  get(input: string): Intent | null {
    const normalized = this.normalize(input);
    return this.cache.get(normalized);
  }
  
  set(input: string, intent: Intent) {
    const normalized = this.normalize(input);
    this.cache.set(normalized, intent);
  }
}
```

### 3. Progressive Loading
```typescript
// Load models progressively
async function initializeNLP() {
  // Start with rules (instant)
  const ruleEngine = new RuleEngine();
  
  // Load statistical in background
  const statEngine = loadStatistical();
  
  // Load neural only if needed
  let neuralEngine: NeuralEngine | null = null;
  
  return {
    async process(input: string) {
      // Try rules first
      const ruleMatch = ruleEngine.match(input);
      if (ruleMatch.confidence > 0.9) return ruleMatch;
      
      // Try statistical
      if (statEngine) {
        const statMatch = await statEngine.match(input);
        if (statMatch.confidence > 0.8) return statMatch;
      }
      
      // Load neural on demand
      if (!neuralEngine) {
        neuralEngine = await loadNeural();
      }
      
      return neuralEngine.understand(input);
    }
  };
}
```

## Training Data Format

### Intent Patterns
```json
{
  "intents": [
    {
      "name": "install_package",
      "patterns": [
        "install {package}",
        "i need {package}",
        "get me {package}",
        "can you install {package}",
        "please add {package} to my system"
      ],
      "responses": [
        "Installing {package}...",
        "I'll install {package} for you.",
        "Getting {package} ready..."
      ]
    }
  ]
}
```

### Entity Lists
```json
{
  "entities": {
    "package": [
      "firefox",
      "chromium",
      "vscode",
      "vim",
      "emacs"
    ],
    "service": [
      "nginx",
      "apache",
      "mysql",
      "postgresql"
    ]
  }
}
```

## Testing Strategy

### Unit Tests
```typescript
describe('Intent Recognition', () => {
  it('recognizes basic install command', () => {
    const intent = nlp.process('install firefox');
    expect(intent.name).toBe('install_package');
    expect(intent.entities.package).toBe('firefox');
    expect(intent.confidence).toBeGreaterThan(0.95);
  });
  
  it('handles typos', () => {
    const intent = nlp.process('instal firfox');
    expect(intent.name).toBe('install_package');
    expect(intent.entities.package).toBe('firefox');
  });
});
```

### Integration Tests
```typescript
describe('End-to-End NLP', () => {
  it('processes voice to command', async () => {
    const audioFile = loadTestAudio('install-firefox.wav');
    const command = await voiceToCommand(audioFile);
    
    expect(command).toBe('nix-env -iA nixpkgs.firefox');
  });
});
```

## Deployment Considerations

### Resource Requirements
- RAM: 400MB (base) + 200MB (neural models)
- Disk: 500MB (includes models)
- CPU: 2 cores recommended

### Model Management
```typescript
// Download models on first run
async function ensureModels() {
  const modelsDir = '~/.config/nix-for-humanity/models';
  
  if (!fs.existsSync(modelsDir)) {
    console.log('Downloading language models...');
    await downloadModels(modelsDir);
  }
}
```

## Security Considerations

### Input Sanitization
```typescript
function sanitizeInput(text: string): string {
  // Remove potential command injection
  return text
    .replace(/[;&|`$]/g, '')
    .replace(/\.\./g, '')
    .trim();
}
```

### Intent Validation
```typescript
function validateIntent(intent: Intent): boolean {
  // Whitelist of allowed intents
  const allowedIntents = [
    'install_package',
    'remove_package',
    'update_system',
    'query_status'
  ];
  
  return allowedIntents.includes(intent.name);
}
```

---

*This implementation provides a fast, accurate, and secure NLP engine for natural language system management.*