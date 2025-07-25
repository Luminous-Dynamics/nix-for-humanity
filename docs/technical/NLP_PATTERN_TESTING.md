# 🧪 NLP Pattern Testing Documentation

## Overview

This document describes how to test and validate NLP patterns for Nix for Humanity. Testing ensures high accuracy in understanding user intent across diverse speech patterns, accents, and phrasings.

## Testing Philosophy

1. **Text-First, Voice-Optional**: Every feature must work perfectly with text input
2. **Real Users First**: Test with actual user inputs (text and voice where available)
3. **Diversity Matters**: Include various phrasings, typing styles, and speech patterns
4. **Context Aware**: Test multi-turn conversations, not just single commands
5. **Graceful Failure**: Wrong intents should still be helpful
6. **Accessibility Always**: Must work for users who cannot speak or hear

## Pattern Testing Framework

### 1. Unit Testing for Patterns

Each intent pattern should have comprehensive tests:

```javascript
describe('Install Package Intent', () => {
  const testCases = [
    // Standard patterns
    { input: "install firefox", expected: "install_package", confidence: 0.99 },
    { input: "i need firefox", expected: "install_package", confidence: 0.95 },
    { input: "get me firefox", expected: "install_package", confidence: 0.95 },
    
    // Variations
    { input: "firefox install", expected: "install_package", confidence: 0.90 },
    { input: "install firefox please", expected: "install_package", confidence: 0.98 },
    { input: "can you install firefox", expected: "install_package", confidence: 0.95 },
    
    // Typos and misspellings
    { input: "instal firefox", expected: "install_package", confidence: 0.85 },
    { input: "install fierfix", expected: "install_package", confidence: 0.80 },
    
    // Natural language
    { input: "i want to browse the web", expected: "install_package", confidence: 0.70 },
    { input: "need something for internet", expected: "suggest_browser", confidence: 0.75 }
  ];

  testCases.forEach(({ input, expected, confidence }) => {
    it(`should recognize "${input}" as ${expected}`, () => {
      const result = nlp.process(input);
      expect(result.intent).toBe(expected);
      expect(result.confidence).toBeGreaterThanOrEqual(confidence);
    });
  });
});
```

### 2. Text Input Testing

Test text input variations that mirror how people type:

```javascript
describe('Text Input Variations', () => {
  const textVariations = [
    // Perfect typing
    { input: "install firefox", expected: "install_package", confidence: 0.99 },
    
    // Common typos
    { input: "isntall firefox", expected: "install_package", confidence: 0.85 },
    { input: "install friefox", expected: "install_package", confidence: 0.85 },
    
    // Mobile typing (autocorrect)
    { input: "install Firefox", expected: "install_package", confidence: 0.99 },
    { input: "Install dire fox", expected: "install_package", confidence: 0.80 },
    
    // Lazy typing
    { input: "inst firefox", expected: "install_package", confidence: 0.90 },
    { input: "firefox pls", expected: "install_package", confidence: 0.85 },
    
    // Copy-paste with extra spaces
    { input: "  install   firefox  ", expected: "install_package", confidence: 0.99 },
  ];

  textVariations.forEach(({ input, expected, confidence }) => {
    it(`should handle text variation: "${input}"`, () => {
      const result = nlp.process(input);
      expect(result.intent).toBe(expected);
      expect(result.confidence).toBeGreaterThanOrEqual(confidence);
    });
  });
});
```

### 3. Voice Recognition Testing (Optional Feature)

Test voice input when microphone is available:

```javascript
describe('Voice Recognition', () => {
  const voiceTestCases = [
    {
      file: 'audio/clear-speech.wav',
      expected: 'install firefox',
      confidence: 0.95
    },
    {
      file: 'audio/background-noise.wav',
      expected: 'install firefox',
      confidence: 0.80
    },
    {
      file: 'audio/accent-british.wav',
      expected: 'install firefox',
      confidence: 0.85
    },
    {
      file: 'audio/elderly-speaker.wav',
      expected: 'install firefox',
      confidence: 0.75
    }
  ];

  voiceTestCases.forEach(({ file, expected, confidence }) => {
    it(`should transcribe ${file} correctly`, async () => {
      const audio = loadAudioFile(file);
      const result = await stt.process(audio);
      expect(result.transcript).toBe(expected);
      expect(result.confidence).toBeGreaterThanOrEqual(confidence);
    });
  });
});
```

### 3. Context Testing

Test multi-turn conversations:

```javascript
describe('Contextual Understanding', () => {
  it('should handle pronouns with context', () => {
    const session = nlp.createSession();
    
    // First turn
    let result = session.process("search for firefox");
    expect(result.intent).toBe('search_package');
    
    // Second turn with pronoun
    result = session.process("install it");
    expect(result.intent).toBe('install_package');
    expect(result.entities.package).toBe('firefox');
  });

  it('should handle follow-up questions', () => {
    const session = nlp.createSession();
    
    session.process("install vscode");
    const result = session.process("how long will it take?");
    
    expect(result.intent).toBe('query_duration');
    expect(result.context.action).toBe('install_vscode');
  });
});
```

### 4. Ambiguity Testing

Test ambiguous inputs:

```javascript
describe('Ambiguity Resolution', () => {
  it('should ask for clarification when ambiguous', () => {
    const result = nlp.process("install code");
    
    expect(result.intent).toBe('clarify_package');
    expect(result.suggestions).toContain('vscode');
    expect(result.suggestions).toContain('vscodium');
    expect(result.response).toContain('Did you mean');
  });

  it('should handle multiple valid interpretations', () => {
    const result = nlp.process("update");
    
    expect(result.intent).toBe('clarify_scope');
    expect(result.options).toEqual([
      'update_system',
      'update_packages',
      'update_specific_package'
    ]);
  });
});
```

## Test Data Organization

### Directory Structure
```
tests/
├── patterns/
│   ├── install-package.test.js
│   ├── remove-package.test.js
│   ├── system-management.test.js
│   └── troubleshooting.test.js
├── voice/
│   ├── audio-samples/
│   │   ├── accents/
│   │   ├── age-groups/
│   │   ├── environments/
│   │   └── speech-patterns/
│   └── voice-recognition.test.js
├── context/
│   ├── multi-turn.test.js
│   └── session-state.test.js
└── personas/
    ├── grandma-rose.test.js
    ├── maya-teen.test.js
    ├── david-parent.test.js
    ├── sarah-professional.test.js
    └── alex-blind.test.js
```

## Persona-Based Testing

### Grandma Rose (75, Non-technical)
```javascript
describe('Grandma Rose Persona', () => {
  const rosePatterns = [
    "how do i get on the internet",
    "i want to see my grandchildren",
    "the computer is being slow",
    "nothing is working"
  ];

  rosePatterns.forEach(input => {
    it(`should understand: "${input}"`, () => {
      const result = nlp.process(input, { persona: 'elderly' });
      expect(result.response).toBeInPlainLanguage();
      expect(result.response).not.toContain('sudo');
      expect(result.response).not.toContain('terminal');
    });
  });
});
```

### Maya (16, ADHD, Tech-savvy)
```javascript
describe('Maya Persona', () => {
  const mayaPatterns = [
    "install vscode rn",  // shortcuts
    "git nodejs npm all of them",  // multiple
    "make it faster",  // vague but urgent
    "keyboard shortcuts?"  // learning
  ];

  mayaPatterns.forEach(input => {
    it(`should handle Maya's style: "${input}"`, () => {
      const result = nlp.process(input, { persona: 'teen-tech' });
      expect(result.responseTime).toBeLessThan(500); // Fast
      expect(result.suggestions).toBeDefined(); // Helpful
    });
  });
});
```

## Automated Test Generation

### Pattern Variation Generator
```javascript
function generateVariations(basePattern) {
  const variations = [];
  
  // Add politeness
  variations.push(`please ${basePattern}`);
  variations.push(`${basePattern} please`);
  variations.push(`can you ${basePattern}`);
  variations.push(`could you ${basePattern}`);
  
  // Add typos
  const typos = generateCommonTypos(basePattern);
  variations.push(...typos);
  
  // Add filler words
  variations.push(`um ${basePattern}`);
  variations.push(`like ${basePattern}`);
  variations.push(`just ${basePattern}`);
  
  return variations;
}

// Test all variations
const base = "install firefox";
const variations = generateVariations(base);
variations.forEach(v => testPattern(v, 'install_package'));
```

## Performance Testing

### Response Time Benchmarks
```javascript
describe('Performance', () => {
  it('should process simple commands in <50ms', () => {
    const start = Date.now();
    nlp.process("install firefox");
    const duration = Date.now() - start;
    expect(duration).toBeLessThan(50);
  });

  it('should handle complex queries in <200ms', () => {
    const start = Date.now();
    nlp.process("install all the development tools I need for web development with react and typescript");
    const duration = Date.now() - start;
    expect(duration).toBeLessThan(200);
  });
});
```

### Accuracy Metrics
```javascript
class AccuracyTracker {
  constructor() {
    this.correct = 0;
    this.total = 0;
    this.byIntent = {};
  }

  track(input, expectedIntent, actualIntent) {
    this.total++;
    const correct = expectedIntent === actualIntent;
    if (correct) this.correct++;
    
    if (!this.byIntent[expectedIntent]) {
      this.byIntent[expectedIntent] = { correct: 0, total: 0 };
    }
    this.byIntent[expectedIntent].total++;
    if (correct) this.byIntent[expectedIntent].correct++;
  }

  report() {
    console.log(`Overall Accuracy: ${(this.correct/this.total*100).toFixed(2)}%`);
    Object.entries(this.byIntent).forEach(([intent, stats]) => {
      const accuracy = (stats.correct/stats.total*100).toFixed(2);
      console.log(`  ${intent}: ${accuracy}%`);
    });
  }
}
```

## Continuous Testing

### Test on Every Commit
```yaml
# .github/workflows/nlp-tests.yml
name: NLP Pattern Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - run: npm run test:patterns
      - run: npm run test:accuracy
      - name: Upload accuracy report
        uses: actions/upload-artifact@v3
        with:
          name: accuracy-report
          path: test-results/accuracy.json
```

### Weekly Regression Tests
Run comprehensive tests weekly with real user data:

```bash
#!/bin/bash
# Run full test suite with production data
npm run test:full

# Test with new voice samples
npm run test:voice -- --samples=./new-samples/

# Generate accuracy report
npm run report:accuracy > reports/week-$(date +%U).md
```

## Success Criteria

### Minimum Accuracy Requirements
- **Core Intents**: 95% accuracy
- **Common Variations**: 90% accuracy  
- **Edge Cases**: 80% accuracy
- **Voice Recognition**: 85% accuracy
- **Overall System**: 90% accuracy

### Performance Requirements
- **Simple Commands**: <50ms
- **Complex Queries**: <200ms
- **Voice Processing**: <500ms
- **Total Response**: <1000ms

### User Satisfaction Metrics
- **Task Completion Rate**: >95%
- **Error Recovery Rate**: >90%
- **Clarification Success**: >85%
- **User Retention**: >80%

## Testing Best Practices

1. **Test Real Scenarios**: Use actual user recordings and inputs
2. **Test Failures**: Ensure graceful handling of unrecognized input
3. **Test Context**: Multi-turn conversations are critical
4. **Test Accessibility**: Screen reader compatibility for all responses
5. **Test Performance**: Speed matters for voice interfaces
6. **Test Personas**: Each user type has different needs

## Debugging Failed Patterns

When a pattern fails:

```javascript
function debugPattern(input, expectedIntent) {
  console.log(`\nDebugging: "${input}"`);
  
  // Show tokenization
  const tokens = tokenize(input);
  console.log('Tokens:', tokens);
  
  // Show each layer's result
  const ruleResult = ruleEngine.process(input);
  console.log('Rule Engine:', ruleResult);
  
  const statsResult = statsEngine.process(input);
  console.log('Statistical:', statsResult);
  
  const neuralResult = neuralEngine.process(input);
  console.log('Neural:', neuralResult);
  
  // Show final fusion
  const final = fusion(ruleResult, statsResult, neuralResult);
  console.log('Final:', final);
  
  // Suggest fix
  if (final.intent !== expectedIntent) {
    console.log('\nSuggested fixes:');
    console.log('1. Add pattern to rule engine');
    console.log('2. Retrain statistical model');
    console.log('3. Add to training data');
  }
}
```

---

*Test like a user, not like a developer. The best test is a grandmother successfully installing software with her voice.*