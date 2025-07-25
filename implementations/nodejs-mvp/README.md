# 🗣️ Nix for Humanity MVP - Node.js/Express Implementation

## What This Is

A simple, working MVP that lets you control NixOS using natural language. No more memorizing commands - just say what you want!

**Status**: Ready for testing on your NixOS system

## Quick Start

```bash
# 1. Navigate to the project
cd implementations/nodejs-mvp

# 2. Start the server
./start.sh

# 3. Open your browser
open http://localhost:3456
```

## Features

### ✅ 10 Safe Commands Implemented
1. **Search packages**: "search firefox", "find python", "look for vscode"
2. **List installed**: "show installed", "what's installed", "my packages"
3. **System info**: "system info", "nix version"
4. **Health check**: "check system", "is everything ok"
5. **Package info**: "tell me about nodejs", "info about git"

### 🧠 Natural Language Understanding
- Multiple ways to say the same thing
- Typo correction
- Context awareness
- Helpful suggestions when unclear

### 📚 Simple Learning System
- Learns your vocabulary preferences
- Tracks successful commands
- Improves over time

## Architecture

```
nodejs-mvp/
├── server.js          # Express server
├── routes/
│   └── nlp.js        # API endpoints
├── services/
│   ├── intent-engine.js    # NLP processing
│   ├── command-builder.js  # Safe command construction
│   ├── executor.js         # Command execution
│   └── learning-system.js  # JSON-based learning
├── public/            # Simple web interface
├── storage/           # Learning data (gitignored)
└── test/             # Jest tests
```

## API Endpoints

### POST /api/nlp/process
Process natural language input
```json
{
  "input": "search for firefox",
  "context": {
    "sessionId": "optional-session-id"
  }
}
```

### GET /api/health
Check service health

### GET /api/nlp/suggestions
Get command suggestions based on usage

## Development

### Testing Without NixOS
```bash
# Set mock mode in .env
MOCK_COMMANDS=true

# Run tests
npm test
```

### Adding New Commands
1. Add pattern to `intent-engine.js`
2. Add command template to `command-builder.js`
3. Add parser to `executor.js`
4. Test thoroughly!

## Security

- ✅ All commands are user-space only (no sudo)
- ✅ Command sanitization
- ✅ No shell injection possible
- ✅ Timeout protection
- ✅ Rate limiting ready

## What's Next?

This MVP proves the concept works. Next steps:
1. Test with real users
2. Add more commands
3. Improve NLP accuracy
4. Build Tauri desktop app (V1.0)

## Troubleshooting

### "Command not found"
Make sure you're running on NixOS or have Nix installed.

### "Permission denied"
All MVP commands should work without sudo. If you see this, please report it.

### Slow responses
First-time searches can be slow. The system caches results for faster subsequent searches.

## Contributing

1. Keep it simple - this is an MVP
2. User-space commands only
3. Test everything
4. Document your changes

## License

MIT - Free to use and modify

---

*Built with ❤️ by Luminous Dynamics*
*Making NixOS accessible to everyone through natural conversation*