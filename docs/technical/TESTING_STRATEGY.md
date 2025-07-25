# 🧪 Testing Strategy - Nix for Humanity

## Testing Philosophy

We test to ensure:
1. **Grandma Rose can use it** (Usability)
2. **Alex can access it** (Accessibility)
3. **It won't break systems** (Safety)
4. **It responds quickly** (Performance)
5. **It understands humans** (Accuracy)

## Testing Pyramid

```
         ╱─────────────╲
        ╱   E2E Tests   ╲     5%
       ╱  (User Flows)   ╲
      ╱───────────────────╲
     ╱ Integration Tests   ╲   15%
    ╱  (API + NLP + Nix)    ╲
   ╱─────────────────────────╲
  ╱     Unit Tests            ╲  60%
 ╱ (Functions, Components)     ╲
╱───────────────────────────────╲
         Manual Testing          20%
    (Accessibility, Voice)
```

## Test Categories

### 1. Unit Tests (60%)

#### NLP Intent Recognition
```typescript
describe('Intent Recognition', () => {
  it('recognizes install commands', () => {
    const variations = [
      'install firefox',
      'i need firefox',
      'get me firefox',
      'can you install firefox please',
      'firefox install'
    ];
    
    variations.forEach(input => {
      const intent = recognizeIntent(input);
      expect(intent.name).toBe('install_package');
      expect(intent.entities.package).toBe('firefox');
    });
  });
  
  it('handles typos gracefully', () => {
    const intent = recognizeIntent('instal fierfix');
    expect(intent.name).toBe('install_package');
    expect(intent.entities.package).toBe('firefox');
    expect(intent.confidence).toBeGreaterThan(0.8);
  });
});
```

#### Safety Validation
```typescript
describe('Command Safety', () => {
  it('prevents dangerous commands', () => {
    const dangerous = [
      'rm -rf /',
      'delete everything',
      '; sudo rm -rf /',
      '&& malicious command'
    ];
    
    dangerous.forEach(input => {
      expect(() => generateCommand(input)).toThrow(SecurityError);
    });
  });
});
```

### 2. Integration Tests (15%)

#### NLP Pipeline Integration
```typescript
describe('NLP Pipeline', () => {
  it('processes voice to command', async () => {
    const audioFile = loadTestAudio('install-firefox.wav');
    
    const text = await speechToText(audioFile);
    expect(text).toContain('firefox');
    
    const intent = await processIntent(text);
    expect(intent.name).toBe('install_package');
    
    const command = await generateNixCommand(intent);
    expect(command).toContain('firefox');
  });
});
```

#### API Integration
```typescript
describe('API Endpoints', () => {
  it('handles install request end-to-end', async () => {
    const response = await request(app)
      .post('/api/process')
      .send({ text: 'install firefox' });
    
    expect(response.status).toBe(200);
    expect(response.body.command).toBeDefined();
    expect(response.body.confirmation).toBe('Install Firefox?');
  });
});
```

### 3. E2E Tests (5%)

#### Complete User Flows
```typescript
describe('User Journey - Grandma Rose', () => {
  it('installs software via voice', async () => {
    // Start app
    await page.goto('http://localhost:3456');
    
    // Click microphone
    await page.click('#voice-button');
    
    // Simulate voice input
    await page.evaluate(() => {
      window.simulateVoiceInput('I need to video chat');
    });
    
    // Wait for response
    await page.waitForText('Would you like Zoom or Skype?');
    
    // Choose option
    await page.evaluate(() => {
      window.simulateVoiceInput('Zoom please');
    });
    
    // Verify installation started
    await page.waitForText('Installing Zoom...');
  });
});
```

### 4. Accessibility Tests (Automated)

```typescript
describe('Accessibility Compliance', () => {
  it('meets WCAG AAA standards', async () => {
    const results = await axe(page);
    expect(results.violations).toHaveLength(0);
  });
  
  it('works with keyboard only', async () => {
    // Disconnect mouse
    await page.mouse.move(-1, -1);
    
    // Tab through interface
    await page.keyboard.press('Tab');
    expect(await page.getFocusedElement()).toBe('#search-input');
    
    // Complete task with keyboard
    await page.keyboard.type('install firefox');
    await page.keyboard.press('Enter');
    
    // Verify success
    await page.waitForText('Installing Firefox');
  });
});
```

### 5. Performance Tests

```typescript
describe('Performance Benchmarks', () => {
  it('responds within 2 seconds', async () => {
    const start = Date.now();
    
    await nlp.process('install firefox');
    
    const duration = Date.now() - start;
    expect(duration).toBeLessThan(2000);
  });
  
  it('handles concurrent requests', async () => {
    const requests = Array(10).fill(0).map((_, i) => 
      nlp.process(`install package${i}`)
    );
    
    const start = Date.now();
    await Promise.all(requests);
    const duration = Date.now() - start;
    
    expect(duration).toBeLessThan(5000); // All in 5s
  });
});
```

## Manual Testing Protocols

### 1. Voice Recognition Testing

**Test Environment**:
- Quiet room
- Normal room with background noise
- Multiple accents/speakers

**Test Script**:
```
1. "Install Firefox" (clear speech)
2. "Install Firefox" (with background TV)
3. "Install Firefox" (different accents)
4. "Um, can you like, install Firefox?" (natural speech)
5. "Install Fire... I mean Firefox" (corrections)
```

### 2. Screen Reader Testing

**Tools**: NVDA, JAWS, Orca

**Test Protocol**:
```
1. Launch with screen reader active
2. Navigate all controls with keyboard
3. Complete installation task
4. Verify all feedback is announced
5. Test error scenarios
```

### 3. Real User Testing

**The Five Personas**:
- **Grandma Rose**: Voice commands, simple tasks
- **Maya**: Speed test, shortcuts discovery
- **David**: Business software installation
- **Dr. Sarah**: Complex configurations
- **Alex**: Full screen reader journey

## Test Data

### Voice Samples
```
test/audio/
├── accents/
│   ├── american-midwest.wav
│   ├── british.wav
│   ├── indian.wav
│   └── spanish-accent.wav
├── environments/
│   ├── quiet.wav
│   ├── coffee-shop.wav
│   └── home-with-kids.wav
└── speech-patterns/
    ├── fast-speaker.wav
    ├── slow-speaker.wav
    └── stutter.wav
```

### NLP Test Patterns
```json
{
  "test_patterns": {
    "install": [
      "install {package}",
      "please install {package}",
      "i need {package}",
      "can u get {package}",
      "{package} install",
      "put {package} on computer"
    ],
    "typos": [
      "instal firfox",
      "isntall firefox",
      "intall friefox"
    ]
  }
}
```

## Continuous Testing

### Pre-commit Hooks
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run unit tests
npm test -- --bail

# Check accessibility
npm run test:a11y

# Lint check
npm run lint

# Type check
npm run type-check
```

### CI/CD Pipeline
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: cachix/install-nix-action@v20
      
      - name: Enter Nix Shell
        run: nix-shell --run "npm install"
        
      - name: Unit Tests
        run: nix-shell --run "npm test"
        
      - name: Integration Tests
        run: nix-shell --run "npm run test:integration"
        
      - name: E2E Tests
        run: nix-shell --run "npm run test:e2e"
        
      - name: Coverage Report
        run: nix-shell --run "npm run coverage"
```

## Testing Metrics

### Coverage Targets
- Overall: 85%
- NLP Core: 95%
- Safety Critical: 100%
- UI Components: 80%

### Performance Targets
- Unit tests: <5 seconds
- Integration tests: <30 seconds
- E2E tests: <2 minutes
- Full suite: <5 minutes

### Quality Gates
- No failing tests
- Coverage not decreased
- Performance benchmarks met
- Accessibility tests pass

## Test Reporting

### Daily Testing Dashboard
```
┌─────────────────────────────────┐
│   Nix for Humanity Testing      │
├─────────────────────────────────┤
│ Unit Tests:        ✅ 245/245   │
│ Integration:       ✅ 42/42     │
│ E2E:              ✅ 15/15     │
│ Accessibility:     ✅ WCAG AAA  │
│ Performance:       ✅ <2s       │
│ Coverage:          📊 87.3%     │
└─────────────────────────────────┘
```

---

*Testing is not about finding bugs. It's about ensuring every human can successfully use our system.*