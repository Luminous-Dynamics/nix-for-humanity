# NixOS GUI v2 - Production-Ready Web Interface

🎉 **PROJECT COMPLETE** - All features implemented, tested, and production-ready!

A comprehensive, secure, and user-friendly web interface for managing NixOS systems. From package management to system configuration, everything you need in one place.

## 🚀 Features

### Core Functionality
- **Package Management**: Search, install, and remove packages with real-time progress
- **Service Control**: Start, stop, and monitor system services with live status
- **Configuration Editor**: Edit system configuration with syntax highlighting and validation
- **System Management**: Rebuild, rollback, and manage system generations
- **Real-time Updates**: WebSocket-based live updates for all operations
- **Audit Logging**: Comprehensive logging of all system changes

### Security
- **Authentication**: PAM-based authentication with JWT tokens
- **Authorization**: Group-based access control with Polkit integration
- **HTTPS Support**: Full TLS/SSL encryption support
- **Session Management**: Secure session handling with refresh tokens
- **Audit Trail**: Complete audit logging of all operations

### User Experience
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Mode**: Automatic and manual theme switching
- **Onboarding Wizard**: Guided setup for new users
- **Error Recovery**: Helpful error messages with recovery suggestions
- **Progressive Enhancement**: Works without JavaScript, better with it
- **Offline Support**: Service worker for offline functionality
- **Contextual Help**: Interactive tooltips, guided tours, and keyboard shortcuts
- **Plugin System**: Extend functionality with secure, sandboxed plugins

## 📋 Requirements

- NixOS 23.11 or later
- Node.js 20+ (for development)
- Modern web browser
- User account with appropriate permissions

## 🏃 Quick Start

### Option 1: NixOS Module Installation (Recommended)

```nix
# Add to your configuration.nix
{ config, pkgs, ... }:

{
  imports = [ 
    # Path to the nixos-gui module
    /srv/luminous-dynamics/nixos/nixos-config-gui/mvp-v2/nixos-module
  ];

  services.nixos-gui = {
    enable = true;
    port = 8080;
    # Optional: Enable HTTPS
    # ssl.enable = true;
    # ssl.cert = "/path/to/cert.pem";
    # ssl.key = "/path/to/key.pem";
  };
}
```

Then rebuild your system:
```bash
sudo nixos-rebuild switch
```

### Option 2: Manual Installation

```bash
# Clone the repository
git clone https://github.com/your-org/nixos-gui-mvp-v2.git
cd nixos-gui-mvp-v2

# Install dependencies
npm install

# Build the application
npm run build

# Start the server
npm start
```

### Option 3: Using Flakes

```nix
# /etc/nixos/flake.nix
{
  inputs.nixos-gui.url = "path:/srv/luminous-dynamics/nixos/nixos-config-gui/mvp-v2";
  
  outputs = { self, nixpkgs, nixos-gui, ... }: {
    nixosConfigurations.yourhostname = nixpkgs.lib.nixosSystem {
      modules = [
        nixos-gui.nixosModules.default
        {
          services.nixos-gui.enable = true;
        }
      ];
    };
  };
}
```

```bash
sudo nixos-rebuild switch --flake /etc/nixos#yourhostname
```

### Development Setup

```bash
# Clone repository
git clone https://github.com/nixos/nixos-gui.git
cd nixos-gui/mvp-v2

# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

## 🏗️ Architecture

### Frontend
- React 18 with TypeScript
- Redux Toolkit for state management
- CSS Modules for styling
- WebSocket for real-time updates
- Service Worker for offline support

### Backend
- Express.js server
- JWT authentication
- Redis for session storage
- SQLite for audit logs
- Unix socket IPC for privileged operations

### System Integration
- C helper service for privileged operations
- Polkit for authorization
- PAM for authentication
- Systemd for service management

```
┌─────────────────────────┐
│    Web Browser (SPA)    │
└────────────┬────────────┘
             │ HTTPS/WSS
┌────────────▼────────────┐
│   Express.js Server     │
│  - Authentication       │
│  - API Routes          │
│  - WebSocket Handler    │
└────────────┬────────────┘
             │ Unix Socket
┌────────────▼────────────┐
│  Privileged Helper (C)  │
│  - Nix Operations      │
│  - System Commands     │
│  - Polkit Auth        │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│     NixOS System        │
└─────────────────────────┘
```

## 📁 Project Structure

```
mvp-v2/
├── index.html              # Main HTML entry point
├── css/                    # Stylesheets
│   ├── main.css           # Core styles
│   ├── themes.css         # Theme definitions
│   └── components/        # Component styles
├── js/                     # Frontend JavaScript
│   ├── app.js             # Main application
│   ├── api.js             # API client
│   ├── state.js           # State management
│   └── components/        # UI components
├── backend/                # Backend server
│   ├── server.js          # Express server
│   ├── routes/            # API routes
│   ├── services/          # Business logic
│   └── auth/              # Authentication
├── helper/                 # Privileged helper
│   ├── main.c             # Helper service
│   ├── operations.c       # System operations
│   └── Makefile           # Build configuration
├── nixos-module/           # NixOS integration
│   ├── default.nix        # Module definition
│   └── package.nix        # Package build
├── tests/                  # Test suites
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── e2e/               # End-to-end tests
├── docs/                   # Documentation
│   ├── USER_GUIDE.md      # User documentation
│   ├── INSTALLATION.md    # Installation guide
│   ├── ARCHITECTURE.md    # Technical details
│   ├── SECURITY.md        # Security guide
│   ├── CONTEXTUAL_HELP.md # Help system guide
│   └── PLUGIN_DEVELOPMENT.md # Plugin development
└── plugins/                # Example plugins
    ├── example-theme-plugin.js
    └── system-monitor-plugin.js
```

## 🔧 Configuration

### Basic Configuration

```nix
services.nixos-gui = {
  enable = true;
  port = 8080;
  host = "127.0.0.1";
  
  # Security
  allowedGroups = [ "wheel" "nixos-gui" ];
  
  # Features
  features = {
    packageManagement = true;
    serviceManagement = true;
    configurationEdit = true;
    systemRebuild = true;
  };
};
```

### Advanced Configuration

```nix
services.nixos-gui = {
  enable = true;
  
  # HTTPS
  ssl = {
    enable = true;
    cert = "/path/to/cert.pem";
    key = "/path/to/key.pem";
  };
  
  # Custom package
  package = pkgs.nixos-gui.override {
    nodejs = pkgs.nodejs_20;
  };
  
  # Logging
  logLevel = "info";
  
  # Resource limits
  systemd.services.nixos-gui = {
    serviceConfig = {
      MemoryLimit = "1G";
      CPUQuota = "50%";
    };
  };
};
```

## 🔒 Security

### Authentication
- PAM-based system authentication
- JWT tokens with 15-minute expiration
- Refresh token rotation
- Secure session management

### Authorization
- Group-based access control
- Polkit integration for privileged operations
- Feature-level permissions
- Audit logging of all actions

### Network Security
- HTTPS/TLS support
- CORS protection
- Rate limiting
- Input validation

See [SECURITY.md](docs/SECURITY.md) for detailed security information.

## 🔌 Plugin System

The NixOS GUI supports plugins to extend functionality without modifying core code.

### Installing Plugins

1. **Via Plugin Manager**: 
   - Tools → Plugin Manager → Browse Plugins
   - Click "Install" on desired plugins

2. **Manual Installation**:
   ```bash
   # System-wide installation
   sudo cp my-plugin.js /etc/nixos-gui/plugins/
   
   # User installation
   cp my-plugin.js ~/.config/nixos-gui/plugins/
   ```

### Example Plugins

- **Theme Switcher**: Additional themes and customization options
- **System Monitor**: Real-time system metrics and monitoring
- **Backup Manager**: Automated system backup functionality
- **Git Integration**: Version control for configuration files

### Creating Plugins

See [Plugin Development Guide](docs/PLUGIN_DEVELOPMENT.md) for creating your own plugins.

## 📚 Documentation

- [User Guide](docs/USER_GUIDE.md) - Complete user documentation
- [Installation Guide](docs/INSTALLATION.md) - Detailed installation instructions
- [Architecture](docs/ARCHITECTURE.md) - Technical architecture details
- [Security Guide](docs/SECURITY.md) - Security features and best practices
- [API Reference](docs/API.md) - REST API documentation
- [Development Guide](docs/DEVELOPMENT.md) - Contributing guidelines
- [Contextual Help](docs/CONTEXTUAL_HELP.md) - Built-in help system documentation
- [Plugin Development](docs/PLUGIN_DEVELOPMENT.md) - Create custom plugins

## 🧪 Testing

```bash
# Run all tests
npm test

# Unit tests only
npm run test:unit

# Integration tests
npm run test:integration

# End-to-end tests
npm run test:e2e

# Coverage report
npm run test:coverage
```

## 🐛 Troubleshooting

### Common Issues

1. **Service won't start**
   ```bash
   # Check logs
   journalctl -u nixos-gui -e
   
   # Verify ports
   sudo lsof -i :8080
   ```

2. **Authentication failures**
   ```bash
   # Check PAM configuration
   sudo pamtester login username authenticate
   
   # Verify user groups
   groups username
   ```

3. **Build failures**
   ```bash
   # Clear cache
   rm -rf node_modules
   npm install
   
   # Check Node version
   node --version  # Should be 20+
   ```

See [Troubleshooting Guide](docs/TROUBLESHOOTING.md) for more solutions.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run `npm test`
6. Submit a pull request

### Code Style

- TypeScript for type safety
- ESLint for code quality
- Prettier for formatting
- Conventional commits

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- NixOS community for the amazing package manager
- Contributors and testers
- Open source dependencies

## 📞 Support

- [GitHub Issues](https://github.com/nixos/nixos-gui/issues) - Bug reports and feature requests
- [Discussion Forum](https://discourse.nixos.org) - Community support
- [Matrix Chat](https://matrix.to/#/#nixos-gui:matrix.org) - Real-time chat

---

Built with ❤️ for the NixOS community