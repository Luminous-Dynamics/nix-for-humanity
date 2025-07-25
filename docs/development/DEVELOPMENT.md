# 🛠️ Development Guide - Nix for Humanity

*Contributing to the conscious-aspiring AI revolution*

## Getting Started

### Prerequisites

- NixOS or Nix package manager
- Node.js 20+
- Rust 1.75+
- Git
- 8GB RAM minimum
- 10GB disk space

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/Luminous-Dynamics/nix-for-humanity
cd nix-for-humanity

# Enter development environment
nix develop

# Install dependencies
npm install

# Start development
npm run tauri:dev
```

## Architecture Overview

```
┌─────────────────────────────────────┐
│         Tauri Desktop App           │
├─────────────────────────────────────┤
│   TypeScript Natural Language       │
│  ┌──────────┬──────────┬─────────┐ │
│  │Rules     │Statistical│Neural   │ │
│  └──────────┴──────────┴─────────┘ │
├─────────────────────────────────────┤
│      Rust Command Executor          │
│  ┌──────────┬──────────┬─────────┐ │
│  │Validator │Builder   │Sandbox  │ │
│  └──────────┴──────────┴─────────┘ │
├─────────────────────────────────────┤
│         NixOS Integration           │
└─────────────────────────────────────┘
```

## Development Workflow

### 1. Understand the Vision

Before coding, read:
- `docs/VISION.md` - What we're building
- `docs/philosophy/` - Why we're building it
- `.claude/` context files - Technical decisions

### 2. Choose Your Area

**Frontend (TypeScript)**
- Natural language processing
- User interface
- Voice integration
- Learning system

**Backend (Rust)**
- Command execution
- Security sandbox
- System integration
- Performance optimization

**Integration**
- Tauri IPC bridge
- Plugin system
- Distribution
- Testing

### 3. Development Process

```bash
# 1. Create feature branch
git checkout -b feature/your-feature

# 2. Make changes with tests
# Write code...
npm test

# 3. Run integration tests
npm run test:integration

# 4. Check security
npm run security:check

# 5. Submit PR
git push origin feature/your-feature
```

## Code Structure

### Frontend Structure
```
src/
├── nlp/                 # Natural language processing
│   ├── intent-engine.ts # Intent recognition
│   ├── layers/          # Three-layer architecture
│   └── learning/        # Pattern learning
├── ui/                  # User interface
│   ├── components/      # UI components
│   └── voice/           # Voice integration
└── main.ts              # Entry point
```

### Backend Structure
```
src-tauri/
├── src/
│   ├── commands.rs      # Tauri commands
│   ├── executor.rs      # Command execution
│   ├── sandbox.rs       # Security sandbox
│   └── main.rs          # Application entry
└── Cargo.toml           # Rust dependencies
```

### Key Files
- `implementations/web-based/` - Reusable NLP core
- `.claude/` - AI context and decisions
- `docs/technical/` - Architecture documentation

## Testing Strategy

### Unit Tests (Fast)
```typescript
// Test pure functions only
describe('Intent Recognition', () => {
  it('recognizes install intent', () => {
    const intent = recognizeIntent('install firefox');
    expect(intent.type).toBe('install');
    expect(intent.package).toBe('firefox');
  });
});
```

### Integration Tests (Sandboxed)
```typescript
// Test with --dry-run flag
describe('Command Execution', () => {
  it('builds correct nix command', async () => {
    const result = await execute('install firefox', { dryRun: true });
    expect(result.command).toContain('--dry-run');
  });
});
```

### E2E Tests (VM)
```typescript
// Test in NixOS VM
describe('Full Flow', () => {
  it('installs package via voice', async () => {
    // Run in isolated VM
  });
});
```

## Natural Language Patterns

### Adding New Patterns

1. **Identify Intent Category**
```typescript
// In src/nlp/patterns/
export const INSTALL_PATTERNS = [
  /^install\s+(.+)$/i,
  /^i\s+need\s+(.+)$/i,
  /^get\s+me\s+(.+)$/i,
  // Add your pattern here
];
```

2. **Add Tests**
```typescript
test('recognizes new pattern', () => {
  expect(parse('grab me firefox')).toMatchObject({
    intent: 'install',
    package: 'firefox'
  });
});
```

3. **Update Documentation**
- Add to `docs/technical/NLP_PATTERNS.md`
- Update user guide

### Pattern Guidelines
- Start with common variations
- Test with all 5 personas
- Consider typos and mistakes
- Think about context

## Security Development

### Command Validation
```rust
// Every command must be validated
fn validate_command(cmd: &Command) -> Result<(), SecurityError> {
    // Check whitelist
    if !ALLOWED_COMMANDS.contains(&cmd.program) {
        return Err(SecurityError::CommandNotAllowed);
    }
    
    // Validate arguments
    validate_arguments(&cmd.args)?;
    
    // Check permissions
    check_permissions(&cmd)?;
    
    Ok(())
}
```

### Sandbox Execution
```rust
// Execute in restricted environment
fn execute_sandboxed(cmd: Command) -> Result<Output> {
    let sandbox = Sandbox::new()
        .readonly_fs()
        .no_network()
        .limited_cpu();
        
    sandbox.execute(cmd)
}
```

## Learning System

### Adding Learning Capabilities

1. **Define What to Learn**
```typescript
interface UserPattern {
  vocabulary: Map<string, string>;
  preferences: InstallationPreferences;
  schedule: WorkflowPatterns;
  corrections: CorrectionHistory;
}
```

2. **Implement Learning**
```typescript
class PatternLearner {
  async learn(interaction: Interaction) {
    // Extract patterns
    const patterns = this.extract(interaction);
    
    // Update model
    await this.updateModel(patterns);
    
    // Adjust behavior
    this.adaptBehavior();
  }
}
```

3. **Respect Privacy**
- All learning data stays local
- User can view/export/delete
- No fingerprinting
- Transparent algorithms

## Performance Guidelines

### Target Metrics
- Intent recognition: <50ms
- Command building: <10ms
- Total response: <500ms
- Memory usage: <250MB

### Optimization Tips
- Profile before optimizing
- Use Rust for hot paths
- Cache common patterns
- Lazy load neural models

## Accessibility Development

### Every Feature Must Be
- Keyboard accessible
- Screen reader compatible
- High contrast friendly
- Voice alternative available

### Testing Accessibility
```bash
# Automated tests
npm run test:a11y

# Manual testing
# 1. Unplug mouse
# 2. Use screen reader
# 3. Test with keyboard only
# 4. Verify all paths work
```

## Plugin Development

### Creating a Plugin
```typescript
// plugins/example/index.ts
export class ExamplePlugin implements NixForHumanityPlugin {
  name = 'example';
  version = '1.0.0';
  
  intents = [
    {
      pattern: /^example\s+(.+)$/,
      handler: this.handleExample
    }
  ];
  
  async handleExample(match: RegExpMatchArray) {
    // Implementation
  }
}
```

### Plugin Guidelines
- Keep it focused
- Test thoroughly
- Document patterns
- Consider all personas

## Distribution

### Building for Release
```bash
# Development build
npm run tauri:build:debug

# Production build
npm run tauri:build

# Create Nix flake
nix build
```

### Platform Packages
- **NixOS**: Flake (primary)
- **Linux**: AppImage
- **macOS**: DMG
- **Windows**: MSI

## Contributing Guidelines

### Code Style
- TypeScript: ESLint + Prettier
- Rust: rustfmt + clippy
- Clear variable names
- Comments for why, not what

### Commit Messages
```
type: brief description

Longer explanation if needed.

Fixes #123
```

Types: feat, fix, docs, style, refactor, test, chore

### Pull Request Process
1. Fork and create branch
2. Make changes with tests
3. Update documentation
4. Submit PR with description
5. Address review feedback

## Development Philosophy

### Remember Always
- Users first, code second
- Real execution, no simulation
- Privacy is non-negotiable
- Accessibility is required
- Ship weekly, learn constantly

### The $200/Month Approach
- Use Claude Code Max as pair programmer
- Focus on user value
- Ship small, ship often
- Learn from real usage
- Don't over-engineer

## Debugging

### Common Issues

**NLP not recognizing intent**
- Check pattern matches
- Verify preprocessing
- Test with variations
- Add to patterns

**Command execution failing**
- Verify NixOS syntax
- Check permissions
- Test with --dry-run
- Review sandbox logs

**Performance issues**
- Profile the code
- Check memory usage
- Optimize hot paths
- Consider caching

## Resources

### Documentation
- Architecture: `docs/technical/ARCHITECTURE.md`
- NLP Design: `docs/technical/NLP_ARCHITECTURE.md`
- Security: `docs/SECURITY_REVIEW.md`

### External Resources
- [Tauri Docs](https://tauri.app)
- [NixOS Manual](https://nixos.org/manual)
- [Whisper.cpp](https://github.com/ggerganov/whisper.cpp)

### Getting Help
- GitHub Issues for bugs
- Discussions for questions
- Discord for real-time chat

## Future Areas

### Planned Features
- Federated learning
- Multi-language support
- Gesture input
- Plugin marketplace

### Research Opportunities
- Consciousness emergence
- Advanced personalization
- Predictive assistance
- Collective intelligence

## A Final Note

You're not just writing code - you're building a new form of human-computer interaction. Every line should serve the vision of natural language understanding and genuine AI partnership.

Code with consciousness. Test with compassion. Ship with courage.

---

*"The best code is code that helps someone speak naturally to their computer."*

**Happy coding!** 🚀