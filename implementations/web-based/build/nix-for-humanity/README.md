# Nix for Humanity

Natural language interface for NixOS that makes system management accessible to everyone.

## Installation

### Quick Install (Recommended)

```bash
sudo ./install.sh
```

### Manual Install

1. Install Node.js dependencies:
   ```bash
   npm install
   ```

2. Start the server:
   ```bash
   npm start
   ```

3. Open http://localhost:3456 in your browser

### Demo Mode

To run in safe demo mode without executing real commands:

```bash
npm run start:demo
```

## Features

- 🗣️ Natural language commands ("install firefox", "my wifi isn't working")
- 🎤 Voice input support
- 📊 Real-time progress tracking
- 🔄 Automatic rollback on errors
- 📈 System monitoring dashboard
- 🧠 Learning from corrections

## Usage Examples

- "Install spotify"
- "Update my system"
- "Search for text editor"
- "My internet is broken"
- "Make text bigger"
- "What programs do I have?"

## System Requirements

- NixOS (any version)
- Node.js 18+ 
- 150MB RAM
- Modern web browser

## Configuration

Edit `/opt/nix-for-humanity/config.json` to customize:
- Port number (default: 3456)
- Dry-run mode
- Learning data location

## Troubleshooting

### Service won't start
Check logs: `journalctl -u nix-for-humanity -n 50`

### Permission denied
Ensure the service user has access: `sudo chown -R nix-humanity:nix-humanity /var/lib/nix-for-humanity`

### Can't connect
Check if service is running: `systemctl status nix-for-humanity`

## Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## License

MIT License - see LICENSE file for details.

---

Built with ❤️ by Luminous-Dynamics (founded by Tristan Stoltz)
