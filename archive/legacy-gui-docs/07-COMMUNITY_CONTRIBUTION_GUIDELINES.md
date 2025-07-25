# Community Contribution Guidelines - Nix for Humanity

> "Every line of code is a gift to humanity. Every contribution makes NixOS more accessible to someone, somewhere."

## Welcome Contributors! 

Whether you're fixing a typo, translating to a new language, or implementing major features - you're helping democratize computational power. This guide will help you contribute effectively.

## Table of Contents
1. [Code of Conduct](#code-of-conduct)
2. [How to Contribute](#how-to-contribute)
3. [Development Setup](#development-setup)
4. [Contribution Types](#contribution-types)
5. [Code Standards](#code-standards)
6. [Testing Requirements](#testing-requirements)
7. [Pull Request Process](#pull-request-process)
8. [Community Resources](#community-resources)

## Code of Conduct

### Our Pledge
We are committed to making Nix for Humanity welcoming to everyone, regardless of:
- Technical experience level
- Age, body size, disability
- Ethnicity, gender identity and expression
- Nationality, personal appearance
- Race, religion, or sexual identity

### Our Standards

**Examples of behavior that contributes to a positive environment:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for humanity
- Showing empathy towards other community members
- Helping newcomers learn and grow

**Examples of unacceptable behavior:**
- Trolling, insulting/derogatory comments
- Public or private harassment
- Publishing others' private information
- Gatekeeping or elitism about technical knowledge
- Any conduct which could reasonably be considered inappropriate

### Remember Our Users
When contributing, always remember:
- Grandma Rose who just wants to write letters
- Maya who's learning to code
- David running his business
- Dr. Sarah doing critical research
- Alex who needs perfect accessibility

Every decision should serve ALL of them.

## How to Contribute

### 1. Find Your Contribution Style

#### 🐛 Bug Hunter
- Browse [Issues](https://github.com/nixos/nix-for-humanity/issues)
- Look for `good-first-issue` tags
- Test on different hardware
- Report edge cases

#### 🎨 UX Improver
- Simplify complex flows
- Improve error messages
- Enhance accessibility
- Polish animations

#### 🌍 Translator
- Translate UI strings
- Localize error messages
- Adapt voice commands
- Review existing translations

#### 📚 Documentation Writer
- Clarify confusing sections
- Add examples
- Create tutorials
- Update screenshots

#### 💻 Feature Developer
- Check the [Roadmap](./03-DEVELOPMENT_ROADMAP.md)
- Discuss in issues first
- Follow architecture guidelines
- Write comprehensive tests

#### 🧪 Tester
- Manual testing on various setups
- Accessibility testing
- Performance testing
- User journey validation

### 2. Before You Start

1. **Check existing work**
   ```bash
   # Search issues and PRs
   gh issue list --search "your feature"
   gh pr list --search "your feature"
   ```

2. **Discuss major changes**
   - Open an issue first
   - Get community feedback
   - Ensure alignment with project philosophy

3. **Claim your work**
   - Comment on the issue you're working on
   - Prevents duplicate effort

## Development Setup

### Prerequisites
```bash
# Required
- NixOS or Nix package manager
- Git
- Node.js 18+ (via Nix)
- Rust toolchain (via Nix)

# Recommended
- VS Code with Nix extensions
- GitHub CLI (`gh`)
- Voice input hardware (for testing)
```

### Quick Start
```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR-USERNAME/nix-for-humanity
cd nix-for-humanity

# 3. Enter development environment
nix develop

# 4. Install dependencies
npm install

# 5. Run development server
npm run dev

# 6. Run tests
npm test

# 7. Create your branch
git checkout -b feature/your-amazing-feature
```

### Development Environment

The `flake.nix` provides everything you need:
```nix
{
  description = "Nix for Humanity Development Environment";
  
  outputs = { self, nixpkgs }: {
    devShells.default = nixpkgs.mkShell {
      packages = with nixpkgs; [
        nodejs_18
        rustc
        cargo
        wasm-pack
        playwright
        # All other dependencies
      ];
      
      shellHook = ''
        echo "Welcome to Nix for Humanity development!"
        echo "Run 'npm run dev' to start"
      '';
    };
  };
}
```

## Contribution Types

### 🌟 Core Contributions

#### Intent Patterns
Add new ways users might express needs:
```javascript
// File: src/intents/patterns.js
export const patterns = {
  install: [
    /^install (.+)$/i,
    /^i need (.+)$/i,
    /^can you install (.+)$/i,
    // Add your pattern here:
    /^set up (.+) for me$/i,  // New!
  ]
};
```

#### Language Support
Add a new language:
```javascript
// File: src/i18n/es.json
{
  "welcome": "¡Hola! ¿Qué necesitas?",
  "installing": "Instalando {package}...",
  "success": "¡{package} está listo!",
  // Add all UI strings
}
```

#### Accessibility Improvements
Enhance screen reader support:
```html
<!-- Add ARIA labels -->
<button 
  aria-label="Install Firefox browser"
  aria-describedby="install-help"
>
  Install Firefox
</button>
<span id="install-help" class="sr-only">
  This will install the Firefox web browser on your system
</span>
```

### 🔧 Plugin Contributions

Create plugins for specific use cases:
```javascript
// File: plugins/education/index.js
export default {
  name: 'education-tools',
  version: '1.0.0',
  
  intents: [
    {
      pattern: /set up classroom/i,
      handler: async (api) => {
        await api.installPackages([
          'libreoffice',
          'gcompris',
          'stellarium'
        ]);
        return 'Classroom tools ready!';
      }
    }
  ]
};
```

### 📖 Documentation Contributions

#### User Guides
Write guides for specific audiences:
```markdown
# Nix for Humanity: Teacher's Guide

## Setting Up a Computer Lab

1. Install Nix for Humanity on one computer
2. Say: "Set up classroom environment"
3. Nix will install:
   - Educational software
   - Content filters
   - Shared folders
   
## Managing Student Accounts
...
```

#### Video Tutorials
- Screen recordings with voiceover
- Accessibility-focused tutorials
- Different language versions
- Real-world use cases

## Code Standards

### Philosophy First
Every contribution must align with our philosophy:
```javascript
// ❌ BAD: Adds complexity
function showAdvancedOptions() {
  // 50 configuration options
}

// ✅ GOOD: Progressive disclosure
function showOptions(userLevel) {
  if (userLevel === 'beginner') {
    return basicOptions;  // 3 options
  }
  // Advanced users can access more
}
```

### Code Style

#### JavaScript/TypeScript
```javascript
// Clear, self-documenting code
async function installPackage(packageName) {
  // Validate input first
  if (!isValidPackageName(packageName)) {
    throw new UserError(`"${packageName}" doesn't look like a package name`);
  }
  
  // Check if already installed
  const installed = await isInstalled(packageName);
  if (installed) {
    return {
      success: true,
      message: `${packageName} is already installed!`
    };
  }
  
  // Perform installation
  try {
    const jobId = await nixBridge.install(packageName);
    return {
      success: true,
      jobId,
      message: `Installing ${packageName}...`
    };
  } catch (error) {
    // Always provide helpful error messages
    throw new UserError(
      `Couldn't install ${packageName}. ${getHelpfulErrorMessage(error)}`
    );
  }
}
```

#### Rust
```rust
// Safe, readable, documented
/// Parses user intent from natural language input
/// 
/// # Examples
/// ```
/// let intent = parse_intent("install firefox");
/// assert_eq!(intent.action, Action::Install);
/// assert_eq!(intent.target, Some("firefox"));
/// ```
pub fn parse_intent(input: &str) -> Result<Intent, ParseError> {
    // Normalize input
    let normalized = input.trim().to_lowercase();
    
    // Match against patterns
    for pattern in &PATTERNS {
        if let Some(captures) = pattern.regex.captures(&normalized) {
            return Ok(Intent {
                action: pattern.action.clone(),
                target: captures.get(1).map(|m| m.as_str().to_string()),
                confidence: calculate_confidence(&captures),
            });
        }
    }
    
    Err(ParseError::NoMatch(input.to_string()))
}
```

### Commit Messages
Follow conventional commits:
```bash
# Format: <type>(<scope>): <subject>

feat(voice): add support for Scottish accents
fix(install): handle spaces in package names  
docs(api): clarify rate limiting behavior
test(intents): add edge cases for install patterns
refactor(ui): simplify voice button component
chore(deps): update playwright to 1.40.0

# Breaking changes
feat(api)!: change intent response format

BREAKING CHANGE: Intent responses now include confidence scores
```

### File Organization
```
src/
├── core/           # Core functionality
├── intents/        # Intent parsing
├── ui/             # User interface
├── voice/          # Voice handling
├── plugins/        # Plugin system
├── i18n/           # Translations
├── tests/          # Test files
└── utils/          # Shared utilities
```

## Testing Requirements

### Test Categories

#### 1. Unit Tests (Required)
```javascript
// Test file: src/intents/patterns.test.js
describe('Intent Patterns', () => {
  test('recognizes install variations', () => {
    const variations = [
      'install firefox',
      'Install Firefox',
      'INSTALL FIREFOX',
      'install   firefox',  // Extra spaces
      'can you install firefox',
      'i need firefox',
      'set up firefox for me'
    ];
    
    variations.forEach(input => {
      const intent = parseIntent(input);
      expect(intent.action).toBe('install');
      expect(intent.target).toBe('firefox');
    });
  });
  
  test('handles unclear input gracefully', () => {
    const intent = parseIntent('do the thing');
    expect(intent).toBeNull();
  });
});
```

#### 2. Integration Tests (Required for core features)
```javascript
// Test file: tests/integration/install-flow.test.js
test('complete install flow', async () => {
  const { page } = await createTestEnvironment();
  
  // User says they need an editor
  await page.fill('#input', 'I need to edit documents');
  await page.press('#input', 'Enter');
  
  // System suggests options
  await expect(page).toContainText('LibreOffice');
  await expect(page).toContainText('VS Code');
  
  // User selects one
  await page.click('button:has-text("LibreOffice")');
  
  // Installation proceeds
  await expect(page).toContainText('Installing LibreOffice');
  
  // Verify success
  await expect(page).toContainText('LibreOffice is ready!', {
    timeout: 60000  // Installation can take time
  });
});
```

#### 3. Accessibility Tests (Required)
```javascript
// Test file: tests/a11y/voice-navigation.test.js
test('fully navigable by voice', async () => {
  const { page, voice } = await createVoiceEnvironment();
  
  // Navigate entirely by voice
  await voice.say('Install Firefox');
  await expect(page).toContainText('Install Firefox browser?');
  
  await voice.say('Yes');
  await expect(page).toContainText('Installing Firefox');
  
  // Verify screen reader announcements
  const announcements = await page.getAnnouncements();
  expect(announcements).toContain('Firefox installation started');
});
```

### Test Coverage Requirements
- Core functionality: 90%+ coverage
- New features: Must include tests
- Bug fixes: Must include regression test
- Accessibility: WCAG 2.1 AA compliance

## Pull Request Process

### 1. Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally (`npm test`)
- [ ] Documentation updated if needed
- [ ] Accessibility verified
- [ ] Philosophy alignment checked

### 2. PR Template
```markdown
## Description
Brief description of what this PR does

## Motivation
Why is this change needed? Who does it help?

## Changes
- List key changes
- Be specific

## Testing
How has this been tested?
- [ ] Unit tests
- [ ] Integration tests  
- [ ] Manual testing
- [ ] Accessibility testing

## Screenshots (if UI changes)
Before | After

## Checklist
- [ ] Follows code style
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Serves our users (not just developers)
```

### 3. Review Process

#### What Reviewers Look For
1. **Philosophy alignment** - Does this make NixOS more human?
2. **Simplicity** - Is this the simplest solution?
3. **Accessibility** - Can everyone use this?
4. **Quality** - Is the code clean and tested?
5. **Impact** - How does this affect our users?

#### Review Timeline
- First response: Within 48 hours
- Full review: Within 1 week
- Merging: After 2 approvals

### 4. After Merge
- Your contribution is celebrated! 🎉
- Added to [CONTRIBUTORS.md](./CONTRIBUTORS.md)
- Mentioned in release notes
- Eternal gratitude from users

## Community Resources

### Communication Channels

#### Discord
- `#general` - Community chat
- `#development` - Technical discussion
- `#help` - Get assistance
- `#showcase` - Share your setup
- `#triage` - Help prioritize issues

#### GitHub Discussions
- Feature requests
- Philosophy discussions
- User stories
- Q&A

#### Weekly Community Call
- Thursdays 18:00 UTC
- Open to everyone
- Recorded for timezones

### Issue Triaging

We use labels to organize issues:

#### Priority Labels
- `P0-critical`: System breaking bugs
- `P1-high`: Important features/fixes
- `P2-medium`: Nice to have
- `P3-low`: Future considerations

#### Status Labels
- `needs-triage`: New, needs review
- `ready-to-work`: Clear and actionable
- `in-progress`: Someone's working on it
- `blocked`: Waiting on something

#### Type Labels
- `bug`: Something's broken
- `feature`: New functionality
- `docs`: Documentation improvements
- `a11y`: Accessibility issues

Help us triage by:
- Adding relevant labels
- Providing reproduction steps
- Confirming bug reports
- Suggesting priority levels

### Learning Resources

#### For New Contributors
1. [First Contribution Tutorial](./tutorials/first-contribution.md)
2. [Understanding the Codebase](./tutorials/codebase-tour.md)
3. [Testing Guide](./tutorials/testing-guide.md)
4. [Voice Interface Primer](./tutorials/voice-development.md)

#### Architecture Deep Dives
- [Intent Engine Internals](./architecture/intent-engine.md)
- [Nix Bridge Design](./architecture/nix-bridge.md)
- [Learning System](./architecture/learning-system.md)
- [Plugin Architecture](./architecture/plugins.md)

### Recognition

#### Contributor Levels
- 🌱 **First PR** - Welcome to the community!
- 🌿 **Regular** (5+ PRs) - Trusted contributor
- 🌳 **Core** (20+ PRs) - Deep knowledge
- 🌲 **Maintainer** - Project steward

#### Special Recognition
- 🌍 **Translator** - Making Nix global
- ♿ **Accessibility Champion** - Ensuring everyone can use Nix
- 📚 **Documentation Hero** - Making knowledge accessible
- 🐛 **Bug Slayer** - Keeping Nix reliable

We use [all-contributors](https://allcontributors.org/) to recognize every type of contribution:
- Code, docs, design, ideas
- Bug reports, reviews, testing  
- Translations, examples, tutorials
- Community building and support

## FAQ for Contributors

### Q: I'm not a programmer. Can I still contribute?
**A: Absolutely!** We need:
- Translators for new languages
- Testers on different hardware
- Documentation writers
- UI/UX designers
- Community moderators
- Tutorial video creators

### Q: How do I test voice features without a microphone?
**A:** Use the text input with voice simulation:
```javascript
// In development mode
npm run dev -- --simulate-voice
```

### Q: What if my PR is rejected?
**A:** We provide constructive feedback to help improve it. Common reasons:
- Adds unnecessary complexity
- Doesn't align with philosophy
- Missing tests or documentation
- Can be simplified

We'll work with you to get it mergeable!

### Q: Can I contribute anonymously?
**A:** Yes! We respect privacy. You can:
- Use a pseudonym
- Contribute via anonymous email
- Have someone else submit your code

### Q: How do I get help?
**A:** Multiple options:
1. Comment on your issue/PR
2. Ask in Discord `#help`
3. Join weekly community call
4. Email: contribute@nixforhumanity.org

## What Not to Contribute

While we welcome most contributions, some things don't align with our vision:

### Please Avoid
- ❌ **Cloud-required features** - We're local-first
- ❌ **Complex configuration screens** - Simplicity is key
- ❌ **Engagement metrics** - No tracking or gamification
- ❌ **Dense technical jargon** - Keep it human
- ❌ **Features that fragment attention** - Protect focus

### Examples
- ❌ "Add 50 configuration toggles for power users"
- ❌ "Integrate with Google Analytics"  
- ❌ "Add achievement system for daily use"
- ❌ "Require login for basic features"

If unsure, ask: "Does this serve Grandma Rose AND Maya equally?"

## Final Words

Every contribution, no matter how small, brings us closer to a world where anyone can use NixOS. Whether you fix a typo or implement a major feature, you're part of democratizing computational power.

Remember our users. Code with empathy. Make technology more human.

**Welcome to the Nix for Humanity community! We're glad you're here.** 🌟

---

*"The best code is not the cleverest, but the kindest - code that serves humanity."*