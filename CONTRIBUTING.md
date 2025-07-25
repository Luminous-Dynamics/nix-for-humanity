# 🤝 Contributing to Nix for Humanity

Welcome! We're building technology that makes NixOS accessible to everyone through natural language. Your contribution can help someone gain computational sovereignty.

## 🌟 Project Vision

**"Natural language is the interface"** - We're making NixOS accessible through human language, not computer commands. Type it or speak it, the choice is yours.

## 🚀 How to Contribute

### 1. Join the Luminous-Dynamics Community

While Nix for Humanity is currently developed solo (one developer + Claude Code Max), we welcome contributions through:

- **GitHub Issues**: Report bugs, suggest features
- **Pull Requests**: Submit improvements
- **Community Testing**: Try it and share feedback
- **Documentation**: Help others understand
- **Accessibility Testing**: Ensure it works for everyone

### 2. Development Philosophy

We follow the **$200/month revolution** approach:
- Ship weekly, not quarterly
- User needs over technical complexity
- Simple solutions over perfect code
- Learn by doing, not planning

## 🌟 Ways to Contribute

### For Everyone
- **Try it out** - Use the alpha and report your experience
- **Share ideas** - How would you talk to your computer?
- **Test accessibility** - Help us reach WCAG AAA
- **Spread the word** - Tell others about the project

### For Developers
- **Code** - Implement features and fix bugs
- **Documentation** - Improve guides and examples
- **Testing** - Write tests and find edge cases
- **Security** - Audit and harden the system

### For Designers
- **Accessibility** - Improve screen reader support
- **Progressive UI** - Design the learning journey
- **Voice UX** - Create conversational flows
- **Visual design** - Keep it minimal and calm

### For Language Experts
- **Intent patterns** - Add natural language variations
- **Translations** - Make it work in your language
- **Documentation** - Translate guides
- **Cultural adaptation** - Local idioms and phrases

## 🛠️ Technical Contribution Guide

### Tech Stack We're Building With

Based on the goal of using the best possible tech stack:

```yaml
Core Architecture:
  - Language: Rust (performance) + TypeScript (NLP flexibility)
  - Desktop: Tauri (lightweight, native)
  - NLP: Three-layer hybrid approach
  - Voice: Whisper.cpp (local, private)
  - Database: SQLite (simple, reliable)
  
Frontend:
  - Framework: Vanilla JS with Web Components
  - Build: Vite (fast, modern)
  - Styling: CSS with design tokens
  - Accessibility: ARIA-first design
  
Development:
  - AI Partner: Claude Code Max
  - Testing: Jest + Playwright
  - Security: Sandboxed execution
  - CI/CD: GitHub Actions
```

## 🚀 Getting Started

### 1. Set Up Your Environment

```bash
# Clone the repository
git clone https://github.com/Luminous-Dynamics/nix-for-humanity
cd nix-for-humanity

# Read the documentation
cat README.md
cat docs/QUICKSTART.md

# Set up development environment
./setup-environment.sh

# Test natural language processing
npm run test:nlp
```

### 2. Understand the Architecture

Read these docs in order:
1. [README.md](README.md) - Project overview
2. [Architecture](docs/architecture/ARCHITECTURE.md) - System design
3. [NLP Architecture](docs/nix-for-humanity/06-NLP_ARCHITECTURE.md) - Language processing
4. [Philosophy](docs/nix-for-humanity/02-PHILOSOPHY_INTEGRATION.md) - Design principles

### 3. Find Something to Work On

Check our issue tracker for:
- `good-first-issue` - Great for newcomers
- `help-wanted` - We need assistance
- `accessibility` - Improve universal access
- `nlp` - Natural language processing
- `security` - Security improvements

## 📝 Development Process

### 1. Before You Code

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Set your intention (optional but encouraged)
echo "Today I will [your intention]" > .intention

# Run existing tests
npm test
```

### 2. Coding Standards

#### TypeScript/JavaScript
```typescript
// Clear, self-documenting code
async function recognizeIntent(input: string): Promise<Intent> {
  // Validate input first
  if (!input || input.length > MAX_INPUT_LENGTH) {
    throw new ValidationError('Invalid input');
  }
  
  // Process through pipeline
  const normalized = normalize(input);
  const intent = await this.pipeline.process(normalized);
  
  // Always return typed results
  return intent;
}
```

#### Rust
```rust
// Safe, performant, clear
pub async fn execute_command(cmd: &NixCommand) -> Result<Output> {
    // Validate permissions
    self.validate_permissions(cmd)?;
    
    // Execute in sandbox
    let output = self.sandbox.execute(cmd).await?;
    
    // Audit log
    self.audit.log_execution(cmd, &output);
    
    Ok(output)
}
```

### 3. Testing Requirements

All code must include tests:

```typescript
describe('Intent Recognition', () => {
  it('should recognize package installation', async () => {
    const inputs = [
      'install firefox',
      'I need firefox',
      'get me a web browser'
    ];
    
    for (const input of inputs) {
      const intent = await recognizer.recognize(input);
      expect(intent.action).toBe('install-package');
    }
  });
  
  it('should handle accessibility', async () => {
    // Test with screen reader active
    const intent = await recognizer.recognize('install firefox', {
      screenReader: true
    });
    
    expect(intent.response).toHaveProperty('ariaLabel');
  });
});
```

### 4. Documentation

Update relevant docs:
- API changes → Update API docs
- New features → Update user guide
- Architecture changes → Update technical docs

### 5. Commit Messages

Follow conventional commits:

```bash
feat: add voice recognition for package names
fix: correct typo in German translations
docs: update NLP architecture diagram
test: add edge cases for intent recognition
refactor: simplify command validation logic
perf: optimize pattern matching performance
security: prevent command injection in voice input
```

### 6. Pull Request Process

1. **Ensure all tests pass**
   ```bash
   npm test
   npm run lint
   npm run security-check
   ```

2. **Write a clear PR description**
   ```markdown
   ## What
   Brief description of changes
   
   ## Why
   The motivation for these changes
   
   ## How
   Technical approach taken
   
   ## Testing
   How you tested the changes
   
   ## Screenshots (if UI changes)
   Before/after screenshots
   ```

3. **Be responsive to feedback**
   - Address review comments promptly
   - Ask questions if unclear
   - Update based on suggestions

## 🎯 What We're Looking For

### High Priority

1. **Core NLP Patterns**
   - Common system tasks
   - Error scenarios
   - Multi-language support

2. **Accessibility Testing**
   - Screen reader compatibility
   - Keyboard navigation
   - Voice command alternatives

3. **Security Hardening**
   - Input validation
   - Sandbox escapes
   - Permission models

### Good First Issues

1. **Natural Language Patterns**
   ```typescript
   // Add variations for existing intents
   addPattern({
     intent: 'install_package',
     patterns: [
       "download {package}",
       "add {package} to my system", 
       "I want {package}",
       "get me {package}",
       "put {package} on here"
     ]
   });
   ```

2. **Persona Testing**
   ```typescript
   // Test with our five personas
   test('Grandma Rose can install Firefox', async () => {
     const response = await nlp.process("I need to get on the internet");
     expect(response.intent).toBe('install_browser');
     expect(response.suggestion).toContain('Firefox');
   });
   ```

3. **Accessibility Improvements**
   - Screen reader announcements
   - Keyboard navigation fixes
   - High contrast support
   - Voice feedback timing

## 🏗️ Architecture Guidelines

### Natural Language First
- Every feature must work via voice/text
- GUI is only for learning, not primary interaction
- Test with "would Grandma understand?"

### Progressive Enhancement
```typescript
// Start simple
if (user.isNew()) {
  return simpleResponse(result);
}

// Add complexity gradually
if (user.hasUsedFeature('advanced')) {
  return detailedResponse(result);
}

// Eventually become invisible
if (user.isExpert()) {
  return minimalResponse(result);
}
```

### Security by Default
- Never trust user input
- Validate at every boundary
- Fail safely and clearly
- Audit everything

## 🧪 Testing Guidelines

### Unit Tests
- Test individual functions
- Mock external dependencies
- Focus on edge cases

### Integration Tests
- Test component interactions
- Use real Nix (in sandbox)
- Verify security boundaries

### Accessibility Tests
- Automated WCAG checks
- Manual screen reader testing
- Keyboard navigation verification

### Performance Tests
- Response time < 2 seconds
- Memory usage < limits
- CPU usage reasonable

## 🌍 Internationalization

### Adding a New Language

1. Create language file:
   ```typescript
   // locales/es.json
   {
     "intents": {
       "install": ["instalar", "agregar", "necesito"],
       "update": ["actualizar", "mejorar"],
       "remove": ["eliminar", "quitar", "borrar"]
     }
   }
   ```

2. Add tests:
   ```typescript
   it('should recognize Spanish intents', async () => {
     const intent = await recognize('instalar firefox', 'es');
     expect(intent.action).toBe('install-package');
   });
   ```

3. Update documentation

## 📊 Code Review Checklist

Before submitting PR, ensure:

- [ ] Tests pass locally
- [ ] New tests added for changes
- [ ] Documentation updated
- [ ] Security considered
- [ ] Accessibility verified
- [ ] Performance impact minimal
- [ ] Follows code style
- [ ] Commit messages clear

## 🤔 Decision Making

### Major Changes
1. Open an issue for discussion
2. Get consensus from maintainers
3. Create proof of concept
4. Submit PR with full implementation

### Minor Changes
1. Submit PR directly
2. Explain reasoning in description
3. Be open to feedback

## 🙏 Recognition

Contributors are recognized in:
- Release notes
- Contributors file
- Project website
- Annual report

## 📜 Code of Conduct

### Be Respectful
- Welcome newcomers
- Patient with questions
- Constructive feedback
- Celebrate diversity

### Be Inclusive
- Simple language in discussions
- Consider accessibility always
- Welcome all skill levels
- Global perspective

### Be Collaborative
- Share knowledge
- Help others learn
- Build on ideas
- Give credit

## 📚 Resources

### Essential Reading
- [Vision Alignment](.claude/VISION_ALIGNMENT.md)
- [Development Philosophy](.claude/DEVELOPMENT_PHILOSOPHY.md)
- [Accessibility Requirements](.claude/ACCESSIBILITY_REQUIREMENTS.md)
- [NLP Patterns](.claude/NLP_INTENT_PATTERNS.md)

## 🆘 Getting Help

### Resources
- **GitHub Discussions**: Ask questions
- **Issue Tracker**: Report bugs
- **Discord**: [Join our community](https://discord.gg/luminous-dynamics)
- **Email**: contributions@luminousdynamics.org

### Community Guidelines
- Use clear, simple language
- Consider all abilities
- Welcome newcomers
- Share knowledge freely

## 📄 License

By contributing, you agree that your contributions will be licensed under the project's license (currently evaluating between MIT and SRL).

---

**Thank you for helping make NixOS accessible to everyone! Together, we're building technology that speaks human.** 🗣️

*"The best contribution is the one that helps someone else contribute."*