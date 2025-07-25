# Web-Based Natural Language Development Environment

## ⚠️ Important: Development Tool Only

This is NOT the primary implementation of Nix for Humanity. This web-based environment is used for:
- Rapid NLP pattern testing
- Accessibility verification 
- Quick iteration during development
- Browser-based demos

**For the main application, see the Tauri implementation in `src-tauri/`**

## What This Is

A development environment for testing the natural language processing components of Nix for Humanity. It provides:

- **NLP Testing Interface** - Test intent recognition patterns
- **Command Preview** - See what commands would be executed (with --dry-run)
- **Pattern Learning** - Test the context-aware learning system
- **Accessibility Testing** - Verify screen reader compatibility

## What This Is NOT

- ❌ NOT a GUI for NixOS
- ❌ NOT the production implementation
- ❌ NOT feature-complete
- ❌ NOT for end users

## Quick Start (Development Only)

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Access at http://localhost:3456
```

## Architecture

```
TypeScript NLP Engine
    ├── Intent Recognition (pure functions)
    ├── Command Building (pure functions)
    └── Command Execution (real with --dry-run)
```

## Testing Natural Language

```javascript
// Example test cases
"install firefox" → nix-env -iA nixpkgs.firefox --dry-run
"my wifi stopped" → nmcli device status
"free up space" → nix-collect-garbage -d --dry-run
```

## Development Workflow

1. Edit NLP patterns in `js/nlp/layers/`
2. Test in browser interface
3. Verify with `npm test`
4. Port working patterns to Tauri implementation

## Key Files

- `js/nlp/layers/intent-recognition.ts` - Pattern matching
- `js/nlp/layers/command-builder.ts` - Command generation
- `js/nlp/layers/command-executor.ts` - Safe execution
- `config/execution.config.ts` - Safety settings

## Remember

This is a development tool for the Nix for Humanity **context-aware natural language interface**. It is NOT a traditional GUI and should not be described as such.

---

*For production use, see the main Tauri application.*