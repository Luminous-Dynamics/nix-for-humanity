# 🔌 NixOS GUI Plugin Development Guide

This guide covers everything you need to know to create plugins for NixOS GUI.

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Plugin Structure](#plugin-structure)
3. [Plugin API](#plugin-api)
4. [Development Workflow](#development-workflow)
5. [Best Practices](#best-practices)
6. [Publishing Plugins](#publishing-plugins)

## Getting Started

### Prerequisites

- NixOS GUI v1.2 or later
- Node.js 18+ (for development)
- Basic JavaScript knowledge
- Understanding of NixOS concepts

### Quick Start

1. **Generate a new plugin**:
   ```bash
   npx create-nixos-gui-plugin my-plugin
   cd my-plugin
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development**:
   ```bash
   npm run dev
   ```

## Plugin Structure

### Required Files

```
my-plugin/
├── plugin.json         # Plugin manifest (required)
├── index.js           # Main entry point (required)
├── README.md          # Documentation (recommended)
├── LICENSE            # License file (recommended)
├── package.json       # NPM metadata (optional)
└── assets/            # Static assets (optional)
    ├── icon.png       # Plugin icon
    └── styles.css     # Custom styles
```

### Plugin Manifest (plugin.json)

```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "description": "A plugin that does amazing things",
  "author": {
    "name": "Your Name",
    "email": "you@example.com",
    "url": "https://yoursite.com"
  },
  "homepage": "https://github.com/you/my-plugin",
  "repository": "https://github.com/you/my-plugin.git",
  "bugs": "https://github.com/you/my-plugin/issues",
  "license": "MIT",
  "main": "index.js",
  "guiVersion": "^1.2.0",
  "categories": ["productivity", "customization"],
  "keywords": ["nixos", "gui", "plugin"],
  "permissions": [
    "ui.menu",
    "system.packages.read"
  ],
  "dependencies": {
    "gui": "^1.2.0",
    "plugins": {
      "dependency-plugin": "^1.0.0"
    }
  },
  "settings": {
    "apiKey": {
      "type": "string",
      "label": "API Key",
      "description": "Your API key for external service",
      "required": false,
      "secret": true
    }
  }
}
```

### Main Plugin File (index.js)

```javascript
class MyPlugin {
  constructor(api) {
    this.api = api;
    this.config = {};
  }

  async initialize() {
    // Plugin initialization
    console.log('My Plugin is starting...');
    
    // Load configuration
    this.config = await this.api.storage.get('config') || {};
    
    // Set up UI elements
    await this.setupUI();
    
    // Subscribe to events
    this.setupEventHandlers();
  }

  async cleanup() {
    // Clean up resources
    console.log('My Plugin is stopping...');
  }

  async setupUI() {
    // Add menu item
    await this.api.ui.registerMenuItem({
      label: 'My Plugin',
      icon: 'star',
      action: () => this.showMainDialog()
    });
  }

  setupEventHandlers() {
    // Listen to system events
    this.api.events.on('packages.updated', (event) => {
      console.log('Packages updated:', event);
    });
  }

  async showMainDialog() {
    await this.api.ui.notify('Hello from My Plugin!', {
      type: 'info'
    });
  }
}

module.exports = MyPlugin;
```

## Plugin API

### Core APIs

#### UI API

```javascript
// Register menu item
await api.ui.registerMenuItem({
  label: 'My Menu Item',
  icon: 'cog',
  parent: 'tools',        // Menu parent
  order: 100,            // Sort order
  action: 'myAction'     // Action ID or function
});

// Add dashboard widget
const widgetId = await api.ui.addWidget({
  title: 'My Widget',
  component: widgetComponent,
  size: 'medium',        // small, medium, large
  position: {x: 0, y: 0},
  refreshInterval: 60000
});

// Show notification
await api.ui.notify('Operation complete!', {
  type: 'success',       // info, success, warning, error
  duration: 5000,
  actions: [{
    label: 'View Details',
    action: () => showDetails()
  }]
});

// Register settings panel
await api.ui.registerSettings({
  title: 'My Plugin Settings',
  schema: settingsSchema,
  defaults: defaultSettings
});
```

#### System API

```javascript
// Search packages
const results = await api.system.searchPackages('firefox');

// Get service status
const status = await api.system.getServiceStatus('nginx');

// Read configuration
const sshConfig = await api.system.getConfig('services.openssh');

// Execute command (requires permission and whitelist)
const result = await api.system.exec('date', ['+%Y-%m-%d']);
```

#### Storage API

```javascript
// Save data
await api.storage.set('userPreferences', {
  theme: 'dark',
  autoRefresh: true
});

// Load data
const prefs = await api.storage.get('userPreferences');

// Remove data
await api.storage.remove('tempData');

// List all keys
const keys = await api.storage.keys();
```

#### Events API

```javascript
// Subscribe to events
const unsubscribe = api.events.on('packages.installed', (event) => {
  console.log(`Package ${event.data.name} installed`);
});

// Emit custom events
api.events.emit('my-plugin:data-updated', {
  timestamp: Date.now(),
  changes: ['item1', 'item2']
});

// Unsubscribe
unsubscribe();
```

#### HTTP API

```javascript
// Make HTTP request (restricted to whitelisted domains)
const response = await api.http.request('https://api.example.com/data', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer token'
  }
});

console.log(response.data);
```

### Advanced APIs

#### Widget Components

```javascript
const widgetComponent = {
  // HTML template
  template: `
    <div class="my-widget">
      <h3>{{title}}</h3>
      <div id="content">Loading...</div>
      <button onclick="MyPlugin.refresh()">Refresh</button>
    </div>
  `,
  
  // CSS styles
  styles: `
    .my-widget {
      padding: 1rem;
      background: var(--widget-bg);
    }
    .my-widget h3 {
      margin: 0 0 1rem 0;
    }
  `,
  
  // JavaScript behaviors
  scripts: {
    refresh: async () => {
      const data = await loadData();
      updateWidget(data);
    }
  }
};
```

#### Hook System

```javascript
// Register pre/post hooks
api.hooks.register('config.beforeSave', async (config) => {
  // Validate or modify config before save
  if (config.dangerousOption) {
    throw new Error('Dangerous option detected!');
  }
  return config;
});

api.hooks.register('packages.afterInstall', async (result) => {
  // Perform actions after package installation
  await api.ui.notify(`Installed: ${result.package}`);
});
```

## Development Workflow

### Local Development

1. **Create development link**:
   ```bash
   cd my-plugin
   npm link
   cd ~/.config/nixos-gui/plugins
   npm link my-plugin
   ```

2. **Enable development mode**:
   ```bash
   nixos-gui --dev --plugin-dev=my-plugin
   ```

3. **Hot reload**:
   The GUI will automatically reload your plugin when files change.

### Testing

```javascript
// test/plugin.test.js
const { createTestAPI } = require('@nixos-gui/plugin-test-utils');
const MyPlugin = require('../index.js');

describe('MyPlugin', () => {
  let plugin;
  let api;

  beforeEach(() => {
    api = createTestAPI();
    plugin = new MyPlugin(api);
  });

  test('initializes successfully', async () => {
    await plugin.initialize();
    expect(api.ui.registerMenuItem).toHaveBeenCalled();
  });

  test('handles package events', async () => {
    await plugin.initialize();
    api.events.emit('packages.updated', { count: 5 });
    // Assert expected behavior
  });
});
```

### Debugging

```javascript
// Enable debug logging
if (process.env.DEBUG) {
  console.debug('[MyPlugin]', 'Debug message');
}

// Use browser DevTools
api.ui.openDevTools();

// Inspect plugin state
api.debug.inspectPlugin('my-plugin');
```

## Best Practices

### 1. Security

- **Never trust user input** - Always validate and sanitize
- **Use minimal permissions** - Only request what you need
- **Avoid eval()** - No dynamic code execution
- **Validate URLs** - Check against whitelist
- **Encrypt sensitive data** - Use the storage encryption API

### 2. Performance

- **Lazy load resources** - Load only when needed
- **Debounce updates** - Avoid excessive refreshes
- **Use caching** - Cache expensive operations
- **Clean up resources** - Remove listeners in cleanup()
- **Batch operations** - Group multiple updates

### 3. User Experience

- **Provide feedback** - Show loading states
- **Handle errors gracefully** - Never crash the GUI
- **Follow GUI conventions** - Consistent look and feel
- **Respect user preferences** - Dark mode, reduced motion
- **Document features** - Clear README and help text

### 4. Code Quality

```javascript
// Use async/await for clarity
async function loadData() {
  try {
    const data = await api.storage.get('data');
    return data || defaultData;
  } catch (error) {
    console.error('Failed to load data:', error);
    return defaultData;
  }
}

// Handle errors properly
try {
  await riskyOperation();
} catch (error) {
  await api.ui.notify('Operation failed', {
    type: 'error',
    details: error.message
  });
}

// Clean up resources
class MyPlugin {
  constructor(api) {
    this.api = api;
    this.intervals = [];
    this.subscriptions = [];
  }

  async cleanup() {
    // Clear intervals
    this.intervals.forEach(clearInterval);
    
    // Unsubscribe from events
    this.subscriptions.forEach(unsub => unsub());
  }
}
```

## Publishing Plugins

### 1. Prepare for Release

```bash
# Run tests
npm test

# Build plugin
npm run build

# Update version
npm version patch
```

### 2. Package Plugin

```bash
# Create plugin archive
tar -czf my-plugin-1.0.0.tar.gz \
  --exclude node_modules \
  --exclude .git \
  my-plugin/
```

### 3. Publish to Registry

```bash
# Publish to NixOS GUI plugin registry
nixos-gui-plugin publish my-plugin-1.0.0.tar.gz
```

### 4. Create GitHub Release

```yaml
# .github/workflows/release.yml
name: Release Plugin

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build plugin
        run: npm run build
      - name: Create release
        uses: softprops/action-gh-release@v1
        with:
          files: '*.tar.gz'
```

### 5. Submit to Plugin Store

1. Fork the [plugin registry](https://github.com/nixos/nixos-gui-plugins)
2. Add your plugin metadata
3. Submit pull request
4. Wait for review

## Plugin Examples

### System Monitor Plugin

```javascript
class SystemMonitorPlugin {
  async initialize() {
    // Add CPU/Memory widget
    this.widgetId = await this.api.ui.addWidget({
      title: 'System Monitor',
      component: this.createMonitorWidget(),
      size: 'large',
      refreshInterval: 5000
    });

    // Start monitoring
    this.startMonitoring();
  }

  createMonitorWidget() {
    return {
      template: `
        <div class="system-monitor">
          <canvas id="cpu-chart"></canvas>
          <canvas id="memory-chart"></canvas>
        </div>
      `,
      scripts: {
        updateCharts: (cpuData, memData) => {
          // Update chart visualizations
        }
      }
    };
  }
}
```

### Git Integration Plugin

```javascript
class GitPlugin {
  async initialize() {
    // Add Git menu
    await this.api.ui.registerMenuItem({
      label: 'Git Operations',
      icon: 'git',
      submenu: [
        { label: 'Commit Config', action: () => this.commitConfig() },
        { label: 'Push to Remote', action: () => this.pushChanges() },
        { label: 'View History', action: () => this.showHistory() }
      ]
    });

    // Watch for config changes
    this.api.events.on('config.changed', () => {
      this.checkGitStatus();
    });
  }
}
```

## Resources

- [Plugin API Reference](/docs/PLUGIN_API.md)
- [Example Plugins](https://github.com/nixos/nixos-gui-plugins)
- [Plugin Template](https://github.com/nixos/plugin-template)
- [Community Forum](https://discourse.nixos.org/c/nixos-gui-plugins)

---

Happy plugin development! 🚀