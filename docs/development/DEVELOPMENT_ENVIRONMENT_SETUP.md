# 🛠️ Development Environment Setup

## Quick Start (5 minutes)

```bash
# Clone the repository
git clone https://github.com/Luminous-Dynamics/nix-for-humanity
cd nix-for-humanity

# Enter Nix shell (provides all dependencies)
nix-shell

# Install Node dependencies
npm install

# Start development
npm run dev
```

## Detailed Setup

### 1. Prerequisites

#### Required Software
- **NixOS** or Nix package manager
- **Git** 2.25+
- **Terminal** with UTF-8 support

#### Recommended
- **VS Code** with Nix IDE extension
- **Firefox** for testing voice features
- **Zellij/Tmux** for terminal management

### 2. Clone and Navigate

```bash
# Clone to sacred location
cd /srv/luminous-dynamics/11-meta-consciousness
git clone https://github.com/Luminous-Dynamics/nix-for-humanity
cd nix-for-humanity

# Or use existing clone
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity
```

### 3. Nix Shell Environment

We use Nix for reproducible development environments:

```bash
# Enter development shell
nix-shell

# This provides:
# - Node.js 18
# - Rust toolchain
# - TypeScript
# - Testing tools
# - Linters
```

#### Shell Features
```nix
# shell.nix provides
{
  nodejs_18      # JavaScript runtime
  rustc          # Rust compiler
  cargo          # Rust package manager
  typescript     # Type safety
  whisper-cpp    # Voice recognition
  
  # Dev tools
  prettier       # Code formatting
  eslint        # Linting
  jest          # Testing
}
```

### 4. Install Dependencies

```bash
# Node.js dependencies
npm install

# If using Rust components
cd implementations/backend-services
cargo build
```

### 5. Configuration

#### Create Local Environment
```bash
# Copy example environment
cp .env.example .env

# Edit with your settings
$EDITOR .env
```

#### Essential Settings
```env
# Development ports
NLP_API_PORT=3456
WEBSOCKET_PORT=3457

# Development mode
NODE_ENV=development
LOG_LEVEL=debug

# Local models path
MODELS_PATH=~/.config/nix-for-humanity/models

# Voice settings
VOICE_ENABLED=true
WHISPER_MODEL=base.en
```

### 6. Download Language Models

```bash
# Run setup script
npm run setup:models

# Or manually
mkdir -p ~/.config/nix-for-humanity/models
cd ~/.config/nix-for-humanity/models
wget https://models.example.com/whisper-base.en.bin
```

### 7. Start Development Server

```bash
# Start all services
npm run dev

# Or individually
npm run dev:nlp    # NLP engine
npm run dev:api    # REST API
npm run dev:ws     # WebSocket server
npm run dev:ui     # Frontend
```

### 8. Verify Installation

```bash
# Run health checks
npm run check:health

# Expected output:
✅ NLP Engine: Ready
✅ API Server: http://localhost:3456
✅ WebSocket: ws://localhost:3457
✅ Voice Input: Available
✅ Models: Loaded
```

## IDE Setup

### VS Code (Recommended)

```json
// .vscode/settings.json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "typescript.tsdk": "node_modules/typescript/lib",
  "eslint.validate": ["javascript", "typescript"],
  "files.associations": {
    "*.nix": "nix"
  }
}
```

#### Recommended Extensions
- Nix IDE (arrterian.nix-env-selector)
- TypeScript (ms-vscode.vscode-typescript-next)
- ESLint (dbaeumer.vscode-eslint)
- Prettier (esbenp.prettier-vscode)
- Jest (orta.vscode-jest)

### Neovim Setup

```lua
-- Add to init.lua
require('lspconfig').tsserver.setup{}
require('lspconfig').rust_analyzer.setup{}
require('lspconfig').rnix.setup{} -- For Nix files
```

## Testing Setup

### Unit Tests
```bash
# Run all tests
npm test

# Watch mode
npm test -- --watch

# Coverage
npm test -- --coverage
```

### Integration Tests
```bash
# Start test environment
npm run test:integration

# Run specific test
npm test -- nlp.integration.test.ts
```

### Accessibility Tests
```bash
# Automated a11y tests
npm run test:a11y

# Manual screen reader test
npm run dev:screenreader
```

## Common Development Tasks

### Adding a New Intent Pattern
```bash
# 1. Add pattern to library
$EDITOR .claude/NLP_INTENT_PATTERNS.md

# 2. Implement in code
$EDITOR implementations/nlp-core/intents/your-intent.ts

# 3. Add tests
$EDITOR implementations/nlp-core/intents/your-intent.test.ts

# 4. Run tests
npm test -- your-intent.test.ts
```

### Testing Voice Input
```bash
# Start with voice debug
npm run dev:voice-debug

# Speak test commands
# Check console for recognition
```

### Building for Production
```bash
# Full build
npm run build

# Test production build
npm run preview
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :3456

# Use alternative ports
NLP_API_PORT=13456 npm run dev
```

### Nix Shell Issues
```bash
# Clean Nix store
nix-collect-garbage -d

# Rebuild shell
nix-shell --pure
```

### Voice Not Working
```bash
# Check microphone permissions
# Firefox: about:preferences#privacy
# Chrome: chrome://settings/content/microphone

# Test microphone
npm run test:microphone
```

## Development Workflow

### 1. Daily Startup
```bash
# Navigate to project
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity

# Update dependencies
git pull
nix-shell
npm install

# Start development
npm run dev
```

### 2. Making Changes
```bash
# Create feature branch
git checkout -b feature/natural-language-improvement

# Make changes with hot reload
# Test as you go

# Run tests
npm test

# Commit with sacred message
git commit -m "✨ Improve package name recognition

- Added fuzzy matching for common typos
- Expanded package alias database
- Tests included"
```

### 3. Sacred Development Practices

#### Morning Intention
```bash
echo "Today I will improve voice recognition accuracy" > .intention
```

#### Sacred Pauses
- Every 25 minutes
- Stand and breathe
- Return refreshed

#### Evening Gratitude
```bash
git commit -m "🙏 Gratitude for today's progress"
```

## Additional Resources

### Documentation
- [Architecture Guide](./architecture/ARCHITECTURE.md)
- [NLP Implementation](./NLP_IMPLEMENTATION_GUIDE.md)
- [Contributing Guide](../CONTRIBUTING.md)

### Community
- Discord: [Coming Soon]
- Forum: [Planning]
- Office Hours: Fridays 2pm CT

---

*Remember: Development is a sacred practice. Code with intention, test with care, ship with confidence.*