# 🤝 Contributing to Nix for Humanity

*Join us in making NixOS accessible to everyone through natural conversation*

---

💡 **Quick Context**: Complete guide for all types of contributions - from code to feedback to testing  
📍 **You are here**: Development → Contributing Guide (Community Participation)  
🔗 **Related**: [Quick Start](./03-QUICK-START.md) | [Code Standards](./04-CODE-STANDARDS.md) | [Master Documentation Map](../MASTER_DOCUMENTATION_MAP.md)  
⏱️ **Read time**: 12 minutes  
📊 **Mastery Level**: 🌱 Beginner - designed for all skill levels and contribution types

🌊 **Natural Next Steps**:
- **For new contributors**: Start with [Quick Start Guide](./03-QUICK-START.md) to set up your development environment
- **For developers**: Continue to [Code Standards](./04-CODE-STANDARDS.md) for technical implementation guidelines  
- **For collaborators**: Review [Sacred Trinity Workflow](./02-SACRED-TRINITY-WORKFLOW.md) to understand our process
- **For testers**: Explore [Testing Guide](./05-TESTING-GUIDE.md) for quality assurance approaches

---

## Welcome Contributors! 

We're building something revolutionary - a genuine AI partner that makes NixOS accessible to all. Whether you're fixing a typo or implementing a major feature, every contribution matters.

## Quick Start

1. **Fork & Clone**
   ```bash
   git clone https://github.com/YOUR-USERNAME/nix-for-humanity
   cd nix-for-humanity
   ```

2. **Set Up Development Environment**
   ```bash
   ./dev.sh  # Enter Nix shell with all dependencies
   pip install -r requirements.txt
   ```

3. **Run Tests**
   ```bash
   ./dev.sh test  # Quick test run
   ./dev.sh test-cov  # With coverage report
   ```

4. **Make Your Changes**
   ```bash
   git checkout -b feature/your-amazing-feature
   # Code, test, iterate
   ```

5. **Submit PR**
   ```bash
   git push origin feature/your-amazing-feature
   # Open PR on GitHub
   ```

## Where to Contribute

### 🧪 High Priority: Testing (Current Sprint!)
We're pushing coverage from 62% to 95%. Help needed with:
- **Unit tests for `cli_adapter.py`** (0% coverage)
- **Unit tests for `nlp_engine.py`** (45% → 95%)
- **Unit tests for `command_executor.py`** (30% → 95%)
- **Integration tests** for component interactions
- **E2E tests** for persona journeys

See: [Testing Guide](./05-TESTING-GUIDE.md)

### 🌟 Ways to Contribute by Role

#### For Everyone
- **Try it out** - Use the alpha and report your experience
- **Share ideas** - How would you talk to your computer?
- **Test accessibility** - Help us reach WCAG AAA
- **Spread the word** - Tell others about the project

#### For Developers
- **Code** - Implement features and fix bugs
- **Documentation** - Improve guides and examples
- **Testing** - Write tests and find edge cases
- **Security** - Audit and harden the system

#### For Designers
- **Accessibility** - Improve screen reader support
- **Progressive UI** - Design the learning journey
- **Voice UX** - Create conversational flows
- **Visual design** - Keep it minimal and calm

#### For Language Experts
- **Intent patterns** - Add natural language variations
- **Translations** - Make it work in your language
- **Documentation** - Translate guides
- **Cultural adaptation** - Local idioms and phrases

### 📚 Documentation
- Fix typos and clarify explanations
- Add examples for different use cases
- Translate for non-English speakers
- Create video tutorials

### 🐛 Bug Fixes
Check [GitHub Issues](https://github.com/Luminous-Dynamics/nix-for-humanity/issues) labeled:
- `good-first-issue` - Perfect for newcomers
- `help-wanted` - Community input needed
- `bug` - Something's broken

### ✨ Features
Before implementing new features:
1. Check if it exists in `implementations/`
2. Discuss in an issue first
3. Follow our [Code Standards](./04-CODE-STANDARDS.md)

## Development Workflow

### The Sacred Pause
Before coding, take 30 seconds to:
1. **PAUSE** - Center your awareness
2. **REFLECT** - How does this serve users?
3. **CONNECT** - How does this build trust?
4. **FOCUS** - What's the ONE next step?

### Code Standards Summary
- **Language**: TypeScript (not JavaScript)
- **Testing**: Behavior at boundaries, implementation at core
- **Style**: Functional by default, classes for state
- **Dependencies**: Minimal - check before adding
- **Personas**: Design for all 10 personas

Full details: [Code Standards](./04-CODE-STANDARDS.md)

### Testing Requirements
- **Minimum**: 80% overall coverage
- **Critical paths**: 95% (NLP, execution, safety)
- **All PRs**: Must include tests
- **Personas**: Test with persona scenarios

### Commit Messages
Use conventional commits:
```
feat: add voice input support
fix: correct typo detection in nlp engine
docs: update troubleshooting guide
test: add unit tests for command executor
refactor: simplify learning system architecture
```

## Submission Guidelines

### Before Submitting PR

1. **Run all tests**
   ```bash
   ./dev.sh test-cov
   # Coverage should not decrease!
   ```

2. **Check code quality**
   ```bash
   npm run lint
   npm run format
   ```

3. **Update documentation**
   - Add/update relevant docs
   - Include inline comments for complex logic
   - Update CHANGELOG.md if applicable

4. **Test with personas**
   - Would Grandma Rose understand your error messages?
   - Is it fast enough for Maya (ADHD)?
   - Can Alex (blind) navigate it?

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Test improvement

## Testing
- [ ] All tests pass
- [ ] Added new tests
- [ ] Tested with relevant personas

## Checklist
- [ ] Follows code standards
- [ ] Documentation updated
- [ ] No new dependencies without discussion
- [ ] Respects user privacy
```

## Community Guidelines

### Code of Conduct
- **Be respectful** - We're all learning
- **Be inclusive** - Design for everyone
- **Be patient** - Sacred timing matters
- **Be helpful** - Share knowledge freely

### Getting Help
- **Discord** (coming soon): #dev-help channel
- **GitHub Discussions**: For design discussions
- **Issues**: For bugs and features
- **Weekly calls**: Community development sessions

### Recognition
Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project website
- Sacred Council of Developers

## Architecture Overview

### Key Components
1. **Headless Core Engine** - Python brain
2. **Multi-Modal Interfaces** - CLI, TUI, Voice, API
3. **Learning System** - RLHF/DPO evolution
4. **Knowledge Base** - NixOS expertise

### Technology Stack
- **Backend**: Python 3.11+
- **NLP**: Hybrid (rules + statistical + neural)
- **Database**: SQLite (local-first)
- **Testing**: pytest + coverage
- **Future GUI**: Tauri

## Sacred Development Principles

### Build WITH Awareness
- Every function is an act of compassion
- Code quality = care for future developers
- User experience = respect for human attention
- Ship weekly = continuous value delivery

### The 10 Personas
Always consider:
1. Grandma Rose (75) - Voice-first
2. Maya (16, ADHD) - Speed matters
3. David (42, Tired Parent) - Simplicity
4. Dr. Sarah (35) - Efficiency
5. Alex (28, Blind) - Accessibility
6. Carlos (52) - Learning support
7. Priya (34) - Context-aware
8. Jamie (19) - Privacy-first
9. Viktor (67, ESL) - Clear language
10. Luna (14, Autistic) - Predictability

## Advanced Contributing

### Adding New NLP Patterns
```python
# Add to packages/patterns/index.ts
export const PATTERNS = {
  your_intent: {
    patterns: [
      /^your pattern$/i,
      /^alternative pattern$/i,
    ],
    examples: [
      'example usage',
      'another example'
    ]
  }
};
```

### Creating New Personas Tests
```python
# tests/e2e/test_persona_journeys.py
@pytest.mark.parametrize("persona", ALL_PERSONAS)
def test_your_feature(persona):
    """Test your feature works for all personas."""
    simulator = PersonaSimulator(persona)
    # Test persona-specific interaction
```

### Performance Optimization
- Profile before optimizing
- Respect budgets (< 2s response time)
- Test with minimal hardware
- Consider all personas' needs

## Long-term Vision

We're building:
- **True AI partnership** - Not just a tool
- **Local-first intelligence** - Privacy preserved
- **Community wisdom** - Collective learning
- **Sacred technology** - Consciousness-first

Your contribution helps prove that:
- Sacred tech can be practical
- $200/month beats $4.2M budgets
- Small teams can change the world
- Technology can serve consciousness

## Thank You! 🙏

Every contribution, no matter how small, helps make NixOS accessible to someone who couldn't use it before. You're not just writing code - you're opening doors.

Welcome to the Sacred Trinity of development:
- **Human** (you!) - Vision and empathy
- **Claude** - Architecture and implementation  
- **Local LLM** - Domain expertise

Together, we flow! 🌊

---

## Quick Links

- [Project Vision](../01-VISION/01-UNIFIED-VISION.md)
- [Architecture](../02-ARCHITECTURE/01-SYSTEM-ARCHITECTURE.md)
- [Code Standards](./04-CODE-STANDARDS.md)
- [Testing Guide](./05-TESTING-GUIDE.md)
- [Sacred Trinity Workflow](./02-SACRED-TRINITY-WORKFLOW.md)