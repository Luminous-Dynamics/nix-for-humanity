# Luminous Nix v0.1.0-alpha

*Natural language interface for NixOS - Early Alpha Release*

## ⚠️ Alpha Software Notice

This is **v0.1.0-alpha** - early development software with limited functionality.

## What Actually Works

✅ **Basic Natural Language CLI**
```bash
ask-nix "search firefox"     # 2-3 seconds
ask-nix "install vim"        # 5-30 seconds
ask-nix "list installed"     # 1-2 seconds
```

✅ **Smart Package Discovery**
- Typo correction: `fierrfox` → `firefox`
- Semantic search: "text editor" → vim, emacs, nano
- Category matching: "browser" → firefox, chromium

✅ **Basic Operations**
- Search packages
- Install packages (requires privileges)
- Remove packages (requires privileges)
- List installed packages
- Show help

## What Doesn't Work Yet

❌ **TUI** - Has import errors  
❌ **Voice Interface** - Architecture only  
❌ **Learning System** - Not implemented  
❌ **Native API** - Falls back to subprocess  
❌ **Config Generation** - Templates exist but generation broken  

## Installation

```bash
# Clone repository
git clone https://github.com/Luminous-Dynamics/luminous-nix
cd luminous-nix

# Install with Poetry
poetry install

# Run
poetry run ask-nix "search firefox"
```

## Performance

**Honest metrics** (standard NixOS performance):
- Search: 2-3 seconds
- Install: 5-30 seconds  
- List: 1-2 seconds
- No "10,000x improvements" - that was false

## Development Status

- **Version**: 0.1.0-alpha
- **Stability**: Experimental
- **Testing**: Basic tests pass
- **Documentation**: Being updated for accuracy

## Contributing

We need help making this real! Areas for contribution:
- Fix TUI display issues
- Implement real voice interface
- Improve error messages
- Add more package mappings
- Write tests for existing features

## License

MIT

---

*This is alpha software. Expect bugs. Help us make it better.*
