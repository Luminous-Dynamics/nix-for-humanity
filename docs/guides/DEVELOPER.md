# Developer Guide

## Table of Contents
- [Getting Started](#getting-started)
- [Architecture Overview](#architecture-overview)
- [Development Setup](#development-setup)
- [Code Structure](#code-structure)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Contributing](#contributing)
- [Code Style](#code-style)
- [Debugging](#debugging)
- [Release Process](#release-process)

## Getting Started

Welcome to NixOS GUI development! This guide will help you contribute to the project.

### Prerequisites

- NixOS or Nix package manager
- Git
- Basic knowledge of:
  - JavaScript/Node.js
  - HTML/CSS
  - NixOS concepts
  - SystemD services

### Quick Start

```bash
# Clone the repository
git clone https://github.com/nixos/nixos-gui.git
cd nixos-gui

# Enter development shell
nix-shell

# Install dependencies
make install

# Start development servers
make dev

# Run tests
make test
```

## Architecture Overview

NixOS GUI follows a modular architecture:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Browser   │────▶│  Web Server  │────▶│   Backend   │
│  (Frontend) │     │   (Express)  │     │    (API)    │
└─────────────┘     └──────────────┘     └─────────────┘
                            │                     │
                            ▼                     ▼
                    ┌──────────────┐     ┌─────────────┐
                    │    Static    │     │   Helper    │
                    │    Assets    │     │  (Polkit)   │
                    └──────────────┘     └─────────────┘
```

### Key Components

1. **Frontend**: Vanilla JS with Web Components
2. **Backend**: Node.js with Express
3. **Helper**: Privileged operations via Polkit
4. **Database**: SQLite for persistence
5. **Communication**: REST API + WebSockets

## Development Setup

### Using Nix Shell

The `shell.nix` provides a complete development environment:

```nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    nodejs-18_x
    nodePackages.npm
    nodePackages.node-gyp
    python3
    gcc
    gnumake
    sqlite
    jq
  ];

  shellHook = ''
    echo "NixOS GUI Development Environment"
    echo "================================="
    echo "Commands:"
    echo "  make dev    - Start development servers"
    echo "  make test   - Run test suite"
    echo "  make lint   - Run linters"
    echo "  make build  - Build for production"
    
    # Set up environment
    export NODE_ENV=development
    export DEBUG=nixos-gui:*
  '';
}
```

### Manual Setup

If not using Nix:

```bash
# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install system dependencies
sudo apt-get install -y build-essential sqlite3

# Install project dependencies
npm install
```

## Code Structure

```
nixos-gui/
├── backend/
│   ├── src/
│   │   ├── api/           # REST API endpoints
│   │   ├── auth/          # Authentication logic
│   │   ├── config/        # Configuration management
│   │   ├── db/            # Database models
│   │   ├── helpers/       # Utility functions
│   │   ├── middleware/    # Express middleware
│   │   ├── services/      # Business logic
│   │   └── ws/            # WebSocket handlers
│   ├── tests/             # Backend tests
│   └── package.json
├── frontend/
│   ├── css/               # Stylesheets
│   ├── js/
│   │   ├── components/    # Web Components
│   │   ├── lib/           # Utility libraries
│   │   ├── pages/         # Page controllers
│   │   └── app.js         # Main application
│   ├── views/             # HTML templates
│   └── assets/            # Images, fonts
├── helper/                # Polkit helper (C)
├── nixos-module/          # NixOS integration
├── tests/                 # Integration tests
├── docs/                  # Documentation
└── scripts/               # Build/deploy scripts
```

### Key Files

- `backend/src/server.js` - Main server entry point
- `frontend/js/app.js` - Frontend application bootstrap
- `helper/nixos-gui-helper.c` - Privileged operations
- `nixos-module/default.nix` - NixOS module definition

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Follow the coding standards and ensure:
- Code is well-documented
- Tests are added/updated
- No linting errors

### 3. Test Locally

```bash
# Run unit tests
make test-unit

# Run integration tests
make test-integration

# Run all tests
make test

# Test specific component
npm test -- --grep "PackageManager"
```

### 4. Commit Changes

Use conventional commits:

```bash
git commit -m "feat: add package search functionality

- Implement fuzzy search algorithm
- Add search result highlighting
- Cache search results for performance

Closes #123"
```

Commit types:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Build/tooling changes

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a pull request with:
- Clear description
- Link to related issues
- Screenshots (if UI changes)
- Test instructions

## Testing

### Unit Tests

Located in `*/tests/` directories:

```javascript
// Example test
describe('PackageManager', () => {
  it('should search packages', async () => {
    const packages = await packageManager.search('firefox');
    expect(packages).to.have.length.above(0);
    expect(packages[0]).to.have.property('name');
  });
});
```

### Integration Tests

Test full workflows:

```javascript
// tests/integration/package-install.test.js
it('should install package through API', async () => {
  // Login
  const token = await login('testuser', 'testpass');
  
  // Search
  const searchRes = await api.get('/packages/search?q=hello');
  
  // Install
  const installRes = await api.post('/packages/install', {
    package: 'hello'
  });
  
  expect(installRes.status).to.equal(200);
});
```

### E2E Tests

Using Playwright:

```javascript
// tests/e2e/package-workflow.spec.js
test('install package workflow', async ({ page }) => {
  await page.goto('http://localhost:8080');
  await page.fill('#username', 'testuser');
  await page.fill('#password', 'testpass');
  await page.click('#login');
  
  await page.click('[data-tab="packages"]');
  await page.fill('#package-search', 'hello');
  await page.click('.package-item:first-child .install-btn');
  
  await expect(page.locator('.notification')).toContainText('installed');
});
```

### Test Coverage

Maintain >80% coverage:

```bash
# Generate coverage report
make coverage

# View report
open coverage/index.html
```

## Contributing

### Code Style

We use ESLint and Prettier:

```javascript
// .eslintrc.js
module.exports = {
  extends: ['eslint:recommended'],
  env: {
    node: true,
    es2020: true,
    browser: true
  },
  rules: {
    'indent': ['error', 2],
    'quotes': ['error', 'single'],
    'semi': ['error', 'always']
  }
};
```

Run linting:
```bash
make lint
make lint-fix  # Auto-fix issues
```

### Documentation

- All functions must have JSDoc comments
- API endpoints need OpenAPI annotations
- Complex logic requires inline comments
- Update relevant docs for features

Example:
```javascript
/**
 * Search for NixOS packages
 * @param {string} query - Search query
 * @param {Object} options - Search options
 * @param {number} options.limit - Result limit
 * @param {boolean} options.fuzzy - Enable fuzzy search
 * @returns {Promise<Package[]>} Matching packages
 */
async function searchPackages(query, options = {}) {
  // Implementation
}
```

### Performance

- Profile before optimizing
- Lazy load where possible
- Cache expensive operations
- Use pagination for lists

## Debugging

### Backend Debugging

```bash
# Enable debug logs
DEBUG=nixos-gui:* npm run dev

# Use Node.js inspector
node --inspect backend/src/server.js

# Connect Chrome DevTools to chrome://inspect
```

### Frontend Debugging

```javascript
// Enable debug mode
localStorage.setItem('debug', 'true');

// Use debug utility
import { debug } from './lib/debug.js';
const log = debug('component:package-manager');
log('Searching packages:', query);
```

### Common Issues

1. **Permission Errors**
   ```bash
   # Check polkit rules
   pkaction --verbose --action-id org.nixos.gui.manage
   ```

2. **Database Locked**
   ```bash
   # Kill stale processes
   fuser -k /var/lib/nixos-gui/db.sqlite
   ```

3. **Port Already in Use**
   ```bash
   # Find process using port
   lsof -i :8080
   ```

## Release Process

### 1. Version Bump

```bash
# Patch release (1.2.3 -> 1.2.4)
npm version patch

# Minor release (1.2.3 -> 1.3.0)
npm version minor

# Major release (1.2.3 -> 2.0.0)
npm version major
```

### 2. Update Changelog

```markdown
## [1.3.0] - 2024-01-20

### Added
- Package search functionality
- Dark mode support

### Fixed
- Memory leak in WebSocket handler
- Race condition in config updates

### Changed
- Improved error messages
- Updated dependencies
```

### 3. Create Release

```bash
# Tag release
git tag -a v1.3.0 -m "Release version 1.3.0"

# Push tags
git push origin main --tags

# Create GitHub release
gh release create v1.3.0 --notes-file CHANGELOG.md
```

### 4. Update Nix Package

Update `default.nix`:
```nix
{
  version = "1.3.0";
  src = fetchFromGitHub {
    owner = "nixos";
    repo = "nixos-gui";
    rev = "v1.3.0";
    sha256 = "..."; # Update hash
  };
}
```

## Additional Resources

### Project Links
- [GitHub Repository](https://github.com/nixos/nixos-gui)
- [Issue Tracker](https://github.com/nixos/nixos-gui/issues)
- [Wiki](https://github.com/nixos/nixos-gui/wiki)
- [Matrix Chat](https://matrix.to/#/#nixos-gui:nixos.org)

### Learning Resources
- [NixOS Manual](https://nixos.org/manual/nixos/stable/)
- [Express.js Guide](https://expressjs.com/en/guide/routing.html)
- [Web Components](https://developer.mozilla.org/en-US/docs/Web/Web_Components)
- [Polkit Documentation](https://www.freedesktop.org/software/polkit/docs/latest/)

### Tools
- [Nix Pills](https://nixos.org/guides/nix-pills/) - Learn Nix
- [Chrome DevTools](https://developer.chrome.com/docs/devtools/)
- [VS Code Nix Extension](https://marketplace.visualstudio.com/items?itemName=bbenoist.Nix)

Happy coding! 🚀