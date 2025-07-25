# NixOS GUI Development Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Environment](#development-environment)
3. [Project Structure](#project-structure)
4. [Architecture Overview](#architecture-overview)
5. [Development Workflow](#development-workflow)
6. [Testing](#testing)
7. [Code Style](#code-style)
8. [Building & Packaging](#building--packaging)
9. [Debugging](#debugging)
10. [Contributing](#contributing)

## Getting Started

### Prerequisites

- NixOS or Linux with Nix installed
- Node.js 20+ (provided by Nix shell)
- Git
- Basic knowledge of:
  - JavaScript/TypeScript
  - React and Redux
  - Express.js
  - NixOS concepts

### Initial Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nixos/nixos-gui.git
   cd nixos-gui/mvp-v2
   ```

2. **Enter development environment:**
   ```bash
   nix develop
   # or if not using flakes
   nix-shell
   ```

3. **Install dependencies:**
   ```bash
   npm install
   ```

4. **Start development servers:**
   ```bash
   # Terminal 1: Backend
   npm run dev:backend

   # Terminal 2: Frontend
   npm run dev:frontend

   # Or both with:
   npm run dev
   ```

5. **Open browser:**
   Navigate to http://localhost:3000

## Development Environment

### Nix Shell

The project includes a `shell.nix` for consistent development environment:

```nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Node.js and package managers
    nodejs_20
    nodePackages.npm
    nodePackages.pnpm
    
    # Build tools
    gcc
    gnumake
    pkg-config
    
    # Development tools
    nodePackages.typescript
    nodePackages.eslint
    nodePackages.prettier
    
    # Testing tools
    nodePackages.jest
    chromium
    
    # System integration
    pam
    polkit
    
    # Utilities
    jq
    httpie
    websocat
  ];
  
  shellHook = ''
    echo "NixOS GUI Development Environment"
    echo "Node.js: $(node --version)"
    echo "npm: $(npm --version)"
    echo ""
    echo "Available commands:"
    echo "  npm run dev       - Start development servers"
    echo "  npm test         - Run tests"
    echo "  npm run build    - Build for production"
    echo "  npm run lint     - Check code style"
  '';
}
```

### VS Code Configuration

Recommended extensions (`.vscode/extensions.json`):
```json
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "jnoortheen.nix-ide",
    "bradlc.vscode-tailwindcss",
    "ritwickdey.liveserver"
  ]
}
```

Settings (`.vscode/settings.json`):
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "eslint.validate": ["javascript", "typescript"],
  "typescript.tsdk": "node_modules/typescript/lib"
}
```

## Project Structure

```
mvp-v2/
├── index.html                 # Main HTML entry
├── package.json              # Dependencies and scripts
├── tsconfig.json            # TypeScript configuration
├── webpack.config.js        # Webpack configuration
├── .eslintrc.js            # ESLint rules
├── .prettierrc             # Prettier configuration
│
├── css/                    # Stylesheets
│   ├── main.css           # Core styles
│   ├── themes.css         # Theme definitions
│   └── components/        # Component-specific styles
│
├── js/                     # Frontend source
│   ├── app.js            # Application entry
│   ├── api.js            # API client
│   ├── state.js          # Redux store
│   ├── router.js         # Route definitions
│   ├── components/       # React components
│   ├── hooks/            # Custom React hooks
│   ├── utils/            # Utility functions
│   └── types/            # TypeScript types
│
├── backend/               # Backend source
│   ├── server.js         # Express server
│   ├── config.js         # Configuration
│   ├── routes/           # API route handlers
│   ├── services/         # Business logic
│   ├── auth/             # Authentication
│   ├── middleware/       # Express middleware
│   ├── models/           # Data models
│   └── utils/            # Backend utilities
│
├── helper/                # C helper source
│   ├── main.c           # Helper entry point
│   ├── operations.c     # System operations
│   ├── auth.c           # Polkit integration
│   ├── ipc.c            # IPC communication
│   └── Makefile         # Build configuration
│
├── tests/                 # Test suites
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   ├── e2e/             # End-to-end tests
│   └── fixtures/        # Test data
│
├── nixos-module/         # NixOS integration
│   ├── default.nix      # Module definition
│   ├── package.nix      # Package build
│   └── tests.nix        # NixOS tests
│
└── docs/                 # Documentation
    └── *.md             # Various docs
```

## Architecture Overview

### Frontend Architecture

```
┌─────────────────────────────────────────────┐
│                  App.js                      │
│         (Main Application Entry)             │
└───────────────┬─────────────────────────────┘
                │
        ┌───────┴───────┐
        │               │
┌───────▼─────┐ ┌───────▼─────┐
│   Router    │ │    Store     │
│  (Routes)   │ │   (Redux)    │
└───────┬─────┘ └───────┬─────┘
        │               │
        └───────┬───────┘
                │
    ┌───────────┴───────────┐
    │                       │
┌───▼────┐  ┌────────┐  ┌──▼─────┐
│ Pages  │  │ Shared │  │  API   │
│        │  │ Comps  │  │ Client │
└────────┘  └────────┘  └────────┘
```

### Backend Architecture

```
┌─────────────────────────────────────────────┐
│               Server.js                      │
│         (Express Application)                │
└───────────────┬─────────────────────────────┘
                │
        ┌───────┴───────┐
        │               │
┌───────▼─────┐ ┌───────▼─────┐
│ Middleware  │ │   Routes     │
│   Stack     │ │  Handlers    │
└───────┬─────┘ └───────┬─────┘
        │               │
        └───────┬───────┘
                │
    ┌───────────┴───────────┐
    │                       │
┌───▼────┐  ┌────────┐  ┌──▼─────┐
│Services│  │ Models │  │ Helper │
│        │  │        │  │  IPC   │
└────────┘  └────────┘  └────────┘
```

## Development Workflow

### Feature Development

1. **Create feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Implement feature:**
   - Write component/service code
   - Add tests
   - Update documentation

3. **Test locally:**
   ```bash
   npm test
   npm run test:e2e
   ```

4. **Submit PR:**
   - Ensure CI passes
   - Request review
   - Address feedback

### Component Development

Example React component structure:

```typescript
// js/components/PackageList.tsx
import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchPackages } from '../store/packagesSlice';
import { Package } from '../types';

interface PackageListProps {
  category?: string;
  onSelect?: (pkg: Package) => void;
}

export const PackageList: React.FC<PackageListProps> = ({ 
  category, 
  onSelect 
}) => {
  const dispatch = useDispatch();
  const { packages, loading, error } = useSelector(state => state.packages);
  
  useEffect(() => {
    dispatch(fetchPackages({ category }));
  }, [category, dispatch]);
  
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  
  return (
    <div className="package-list">
      {packages.map(pkg => (
        <PackageItem 
          key={pkg.name}
          package={pkg}
          onClick={() => onSelect?.(pkg)}
        />
      ))}
    </div>
  );
};
```

### API Development

Example Express route:

```typescript
// backend/routes/packages.ts
import { Router } from 'express';
import { authenticate } from '../middleware/auth';
import { validateRequest } from '../middleware/validation';
import { packageService } from '../services/packageService';

const router = Router();

router.get(
  '/packages',
  authenticate,
  async (req, res, next) => {
    try {
      const { page = 1, limit = 50, search } = req.query;
      
      const result = await packageService.list({
        page: Number(page),
        limit: Number(limit),
        search: String(search || '')
      });
      
      res.json({
        success: true,
        data: result
      });
    } catch (error) {
      next(error);
    }
  }
);

router.post(
  '/packages/install',
  authenticate,
  authorize('packages.write'),
  validateRequest(installPackageSchema),
  async (req, res, next) => {
    try {
      const { package: pkgName } = req.body;
      
      const job = await packageService.install(pkgName, req.user);
      
      res.json({
        success: true,
        data: { jobId: job.id }
      });
      
      // Emit progress via WebSocket
      req.app.ws.emit('job.started', job);
    } catch (error) {
      next(error);
    }
  }
);

export default router;
```

## Testing

### Unit Tests

```typescript
// tests/unit/packageService.test.ts
import { packageService } from '../../backend/services/packageService';

describe('PackageService', () => {
  describe('search', () => {
    it('should find packages by name', async () => {
      const results = await packageService.search('firefox');
      
      expect(results).toHaveLength(1);
      expect(results[0].name).toBe('firefox');
    });
    
    it('should handle empty search', async () => {
      const results = await packageService.search('');
      
      expect(results).toHaveLength(0);
    });
  });
});
```

### Integration Tests

```typescript
// tests/integration/api.test.ts
import request from 'supertest';
import app from '../../backend/app';

describe('API Integration', () => {
  let authToken: string;
  
  beforeAll(async () => {
    const res = await request(app)
      .post('/api/auth/login')
      .send({ username: 'test', password: 'test123' });
    
    authToken = res.body.data.accessToken;
  });
  
  describe('GET /api/packages', () => {
    it('should return package list', async () => {
      const res = await request(app)
        .get('/api/packages')
        .set('Authorization', `Bearer ${authToken}`);
      
      expect(res.status).toBe(200);
      expect(res.body.success).toBe(true);
      expect(res.body.data.packages).toBeInstanceOf(Array);
    });
  });
});
```

### E2E Tests

```typescript
// tests/e2e/packageInstall.test.ts
import { test, expect } from '@playwright/test';

test.describe('Package Installation', () => {
  test('should install package successfully', async ({ page }) => {
    // Login
    await page.goto('http://localhost:3000');
    await page.fill('[name="username"]', 'admin');
    await page.fill('[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    
    // Search for package
    await page.fill('[placeholder="Search packages..."]', 'firefox');
    await page.waitForSelector('.package-item');
    
    // Install package
    await page.click('button:has-text("Install")');
    
    // Wait for installation
    await page.waitForSelector('.notification:has-text("installed successfully")', {
      timeout: 60000
    });
  });
});
```

### Running Tests

```bash
# All tests
npm test

# Unit tests only
npm run test:unit

# Integration tests
npm run test:integration

# E2E tests (requires running app)
npm run test:e2e

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage
```

## Code Style

### ESLint Configuration

```javascript
// .eslintrc.js
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended'
  ],
  rules: {
    'indent': ['error', 2],
    'quotes': ['error', 'single'],
    'semi': ['error', 'always'],
    'no-unused-vars': 'off',
    '@typescript-eslint/no-unused-vars': ['error'],
    'react/prop-types': 'off'
  }
};
```

### Prettier Configuration

```json
// .prettierrc
{
  "singleQuote": true,
  "trailingComma": "es5",
  "tabWidth": 2,
  "semi": true,
  "printWidth": 80
}
```

### Pre-commit Hooks

```json
// package.json
{
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged"
    }
  },
  "lint-staged": {
    "*.{js,ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{css,md}": "prettier --write"
  }
}
```

## Building & Packaging

### Development Build

```bash
# Build frontend
npm run build:frontend

# Build backend
npm run build:backend

# Build helper
npm run build:helper

# Build all
npm run build
```

### Production Build

```bash
# Create optimized build
npm run build:production

# Output structure
dist/
├── frontend/
│   ├── index.html
│   ├── js/
│   ├── css/
│   └── assets/
├── backend/
│   ├── server.js
│   └── ...
└── helper/
    └── nixos-gui-helper
```

### Nix Package Build

```bash
# Build Nix package
nix build .#nixos-gui

# Test in VM
nix build .#checks.x86_64-linux.vm-test
./result/bin/run-nixos-vm
```

## Debugging

### Frontend Debugging

1. **Browser DevTools:**
   - React Developer Tools
   - Redux DevTools
   - Network tab for API calls

2. **Debug Configuration (VS Code):**
   ```json
   {
     "type": "chrome",
     "request": "launch",
     "name": "Debug Frontend",
     "url": "http://localhost:3000",
     "webRoot": "${workspaceFolder}",
     "sourceMaps": true
   }
   ```

### Backend Debugging

1. **Node.js Inspector:**
   ```bash
   # Start with inspector
   node --inspect backend/server.js
   
   # Or use npm script
   npm run debug:backend
   ```

2. **Debug Configuration (VS Code):**
   ```json
   {
     "type": "node",
     "request": "launch",
     "name": "Debug Backend",
     "program": "${workspaceFolder}/backend/server.js",
     "envFile": "${workspaceFolder}/.env.development"
   }
   ```

### Helper Debugging

```bash
# Build with debug symbols
make -C helper debug

# Run with gdb
gdb ./helper/nixos-gui-helper

# Or use valgrind for memory issues
valgrind --leak-check=full ./helper/nixos-gui-helper
```

### Common Issues

1. **WebSocket Connection Failed:**
   - Check if backend is running
   - Verify CORS settings
   - Check browser console

2. **Authentication Errors:**
   - Verify PAM configuration
   - Check user groups
   - Review auth logs

3. **Permission Denied:**
   - Check Polkit rules
   - Verify helper permissions
   - Review audit logs

## Contributing

### Contribution Process

1. **Find an issue:**
   - Check existing issues
   - Discuss new features
   - Ask for assignment

2. **Development:**
   - Follow code style
   - Write tests
   - Update docs

3. **Submit PR:**
   - Clear description
   - Link to issue
   - Screenshots if UI

4. **Review process:**
   - Address feedback
   - Keep PR updated
   - Be patient

### Commit Messages

Follow conventional commits:

```
type(scope): subject

body

footer
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style
- `refactor`: Refactoring
- `test`: Tests
- `chore`: Maintenance

Example:
```
feat(packages): add package search functionality

- Implement fuzzy search algorithm
- Add search UI component
- Include search API endpoint

Closes #123
```

### Documentation

- Update relevant docs
- Add JSDoc comments
- Include examples
- Keep README current

### Community

- Be respectful
- Help others
- Share knowledge
- Celebrate wins

## Resources

### Official Documentation
- [NixOS Manual](https://nixos.org/manual/nixos/stable/)
- [Nix Pills](https://nixos.org/guides/nix-pills/)
- [React Documentation](https://react.dev/)
- [Redux Toolkit](https://redux-toolkit.js.org/)

### Tools
- [NixOS Search](https://search.nixos.org/)
- [Nix Package Versions](https://lazamar.co.uk/nix-versions/)
- [Can I Use](https://caniuse.com/)

### Community
- [NixOS Discourse](https://discourse.nixos.org/)
- [NixOS Reddit](https://reddit.com/r/NixOS)
- [Matrix Chat](https://matrix.to/#/#nixos:nixos.org)

Happy coding! 🚀