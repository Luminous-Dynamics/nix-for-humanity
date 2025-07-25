# 🚀 Nix for Humanity v0.1 - Installation Guide

## Quick Start (5 minutes)

### Prerequisites
- Node.js 18+ (or use nix-shell)
- Modern web browser (Chrome, Firefox, Safari)
- NixOS or Nix package manager installed

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Luminous-Dynamics/nix-for-humanity.git
   cd nix-for-humanity/implementations/web-based
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Build the project**
   ```bash
   npm run build
   ```

4. **Start the server**
   ```bash
   npm start
   ```

5. **Open in browser**
   Navigate to http://localhost:3456

## What's Working in v0.1

✅ **10 Basic Commands**
- `search [package]` - Search for packages
- `install [package]` - Install a package
- `remove [package]` - Uninstall a package  
- `update system` - Update NixOS
- `list installed` - Show installed packages
- `clean up` - Free disk space
- `service status [name]` - Check service status
- `enable [service]` - Enable a service
- `disable [service]` - Disable a service
- `show logs` - View system logs

✅ **Natural Language Understanding**
- Multiple ways to express each command
- Typo tolerance
- Basic context understanding

✅ **Error Handling**
- User-friendly error messages
- Recovery suggestions
- No technical jargon

## Usage Examples

### Text Input
Just type naturally in the input box:
- "search for firefox"
- "install vs code"
- "what's installed?"
- "clean up old packages"
- "is nginx running?"

### Voice Input (Coming Soon)
Click the microphone button and speak naturally.

## Configuration

### Environment Variables
Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Key settings:
- `PORT` - Server port (default: 3456)
- `LOG_LEVEL` - Logging verbosity (default: info)
- `DRY_RUN` - Test mode without executing (default: false)

### Security Note
⚠️ **For v0.1 testing only** - Commands execute with your user permissions. Use `DRY_RUN=true` for safe testing.

## Troubleshooting

### Common Issues

**"Command not recognized"**
- Try rephrasing more simply
- Check supported commands list above
- Use exact package names

**"Permission denied"**
- Some operations need sudo
- Run the server as administrator (not recommended)
- Use declarative configuration instead

**"Package not found"**
- Search first to find exact name
- Package might not be in nixpkgs
- Check spelling

### Getting Help

1. Check browser console for errors
2. Enable debug logging: `LOG_LEVEL=debug npm start`
3. Report issues: https://github.com/Luminous-Dynamics/nix-for-humanity/issues

## Development Mode

For developers who want to modify the code:

```bash
# Watch mode for auto-rebuild
npm run dev

# Run tests
npm test

# Type checking
npm run type-check
```

## What's Next (v0.2)

Coming in the next release:
- Voice input with Whisper
- 40+ more commands
- Multi-turn conversations
- Preference learning
- Better error recovery

## System Requirements

### Minimum
- 2GB RAM
- 1GB disk space
- Any modern browser
- Node.js 18+

### Recommended  
- 4GB RAM
- 2GB disk space
- Chrome/Firefox latest
- NixOS 23.11+

## Uninstallation

To remove Nix for Humanity:

```bash
# Stop the server (Ctrl+C)
# Remove the directory
rm -rf nix-for-humanity
```

No system files are modified.

---

## 🎉 Congratulations!

You've installed Nix for Humanity v0.1. Start exploring natural language control of your NixOS system!

**Remember**: This is an early version. We're actively developing and would love your feedback.

**Try saying**: "search firefox" to get started!

---

*Built with ❤️ by Luminous-Dynamics*