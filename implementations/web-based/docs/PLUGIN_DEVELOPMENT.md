# Plugin Development Guide

## Overview

The NixOS GUI plugin system allows developers to extend the functionality of the application through a secure, sandboxed plugin architecture. Plugins can add new UI elements, respond to system events, and integrate with NixOS operations.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Plugin Structure](#plugin-structure)
3. [Plugin API](#plugin-api)
4. [Security Model](#security-model)
5. [Best Practices](#best-practices)
6. [Examples](#examples)
7. [Publishing Plugins](#publishing-plugins)

## Getting Started

### Basic Plugin Template

```javascript
/**
 * My Awesome Plugin
 * Description of what your plugin does
 */

const plugin = {
    // Required fields
    id: 'my-awesome-plugin',
    name: 'My Awesome Plugin',
    version: '1.0.0',
    author: 'Your Name',
    description: 'A brief description of your plugin',
    
    // Required permissions
    permissions: ['ui', 'storage'],
    
    // Optional metadata
    homepage: 'https://github.com/username/my-awesome-plugin',
    repository: 'https://github.com/username/my-awesome-plugin',
    license: 'MIT',
    
    // Required: Plugin initialization
    async init(api) {
        console.log('My Awesome Plugin initializing...');
        
        // Your plugin code here
        this.api = api;
        
        // Add UI elements
        this.addUI();
        
        // Setup event listeners
        this.setupEvents();
    },
    
    // Optional: Cleanup when plugin is disabled
    cleanup() {
        console.log('My Awesome Plugin cleaning up...');
        // Remove event listeners, UI elements, etc.
    },
    
    // Optional: Hook into system events
    hooks: {
        beforeSystemRebuild: async (data) => {
            // Do something before system rebuild
        },
        afterPackageInstall: async (data) => {
            // Do something after package installation
        }
    },
    
    // Plugin methods
    addUI() {
        // Add dashboard widget
        this.api.ui.addDashboardWidget({
            id: 'my-widget',
            title: 'My Widget',
            content: '<div>Widget content</div>',
            render: (container) => {
                // Optional: Additional rendering logic
            }
        });
    },
    
    setupEvents() {
        // Listen for events
        this.api.events.on('theme-changed', (theme) => {
            console.log('Theme changed to:', theme);
        });
    }
};
```

## Plugin Structure

### Required Fields

- **id**: Unique identifier (lowercase, alphanumeric with hyphens)
- **name**: Human-readable name
- **version**: Semantic version (e.g., "1.0.0")
- **author**: Plugin author name
- **init**: Async initialization function

### Optional Fields

- **description**: Brief description of the plugin
- **permissions**: Array of required permissions
- **homepage**: Plugin homepage URL
- **repository**: Source code repository URL
- **license**: License identifier (e.g., "MIT", "GPL-3.0")
- **cleanup**: Cleanup function called when plugin is disabled
- **hooks**: Object containing system hook handlers

## Plugin API

The plugin API provides controlled access to system functionality based on requested permissions.

### UI API (`permissions: ['ui']`)

#### addDashboardWidget(options)
Add a widget to the main dashboard.

```javascript
api.ui.addDashboardWidget({
    id: 'unique-widget-id',
    title: 'Widget Title',
    content: '<div>HTML content</div>',
    render: (container) => {
        // Optional: Called after widget is added to DOM
        // Use for setting up interactive elements
    }
});
```

#### addToolbarButton(options)
Add a button to the main toolbar.

```javascript
api.ui.addToolbarButton({
    id: 'unique-button-id',
    icon: 'icon-class-name',
    tooltip: 'Button tooltip',
    action: () => {
        // Button click handler
    }
});
```

#### addMenuItem(menu, options)
Add an item to a menu.

```javascript
api.ui.addMenuItem('tools', {
    label: 'My Menu Item',
    icon: 'icon-class-name',
    action: () => {
        // Menu item click handler
    }
});
```

Available menus: `'file'`, `'edit'`, `'view'`, `'tools'`, `'help'`

#### showModal(options)
Display a modal dialog.

```javascript
api.ui.showModal({
    title: 'Modal Title',
    content: '<div>Modal content</div>',
    buttons: [
        {
            label: 'OK',
            action: 'close',
            primary: true
        },
        {
            label: 'Cancel',
            action: () => {
                // Custom handler
            }
        }
    ]
});
```

#### removeWidget(widgetId)
Remove a previously added widget.

```javascript
api.ui.removeWidget('my-widget-id');
```

### Storage API (`permissions: ['storage']`)

Plugin-specific persistent storage (isolated per plugin).

#### get(key)
Retrieve a stored value.

```javascript
const value = api.storage.get('my-key');
```

#### set(key, value)
Store a value.

```javascript
api.storage.set('my-key', { data: 'value' });
```

#### remove(key)
Remove a stored value.

```javascript
api.storage.remove('my-key');
```

#### clear()
Clear all plugin storage.

```javascript
api.storage.clear();
```

### Notifications API (`permissions: ['notifications']`)

#### show(message, type, duration)
Display a notification.

```javascript
api.notifications.show('Operation completed!', 'success', 3000);
```

Types: `'info'`, `'success'`, `'warning'`, `'error'`

### Settings API (`permissions: ['settings']`)

#### define(schema)
Define plugin settings.

```javascript
api.settings.define({
    'auto-refresh': {
        type: 'boolean',
        label: 'Auto Refresh',
        description: 'Automatically refresh data',
        default: true
    },
    'refresh-interval': {
        type: 'number',
        label: 'Refresh Interval',
        description: 'Refresh interval in seconds',
        default: 60,
        min: 10,
        max: 300
    }
});
```

#### get(key)
Get a setting value.

```javascript
const autoRefresh = api.settings.get('auto-refresh');
```

#### set(key, value)
Set a setting value.

```javascript
api.settings.set('auto-refresh', false);
```

#### onChanged(callback)
Listen for setting changes.

```javascript
api.settings.onChanged((key, value) => {
    console.log(`Setting ${key} changed to ${value}`);
});
```

### Events API (`permissions: ['events']`)

#### on(event, handler)
Listen for system events.

```javascript
api.events.on('package-installed', (data) => {
    console.log('Package installed:', data.package);
});
```

#### off(event, handler)
Remove event listener.

```javascript
api.events.off('package-installed', myHandler);
```

#### emit(event, data)
Emit custom events.

```javascript
api.events.emit('my-custom-event', { foo: 'bar' });
```

### System Events

- `theme-changed`: Theme was changed
- `package-installed`: Package was installed
- `package-removed`: Package was removed
- `service-started`: Service was started
- `service-stopped`: Service was stopped
- `config-changed`: Configuration was modified
- `system-rebuild`: System rebuild completed

## Security Model

### Sandboxed Execution

Plugins run in a sandboxed environment with restricted access:

- No access to Node.js modules (`require`, `fs`, `child_process`, etc.)
- No access to system globals (`process`, `__dirname`, etc.)
- No direct file system access
- No network requests (use provided APIs)
- No eval or dynamic code execution

### Permissions

Plugins must declare required permissions. Available permissions:

- **ui**: Access to UI modification APIs
- **storage**: Access to persistent storage
- **notifications**: Show notifications
- **settings**: Define and access plugin settings
- **events**: Listen to and emit events

### Code Validation

All plugins undergo validation before installation:

1. Static code analysis for dangerous patterns
2. Metadata validation
3. Permission verification
4. Size limits (10MB maximum)

## Best Practices

### 1. Minimize Permissions
Only request permissions you actually need.

```javascript
// Good: Only request what you use
permissions: ['ui', 'storage']

// Bad: Requesting everything
permissions: ['ui', 'storage', 'notifications', 'settings', 'events']
```

### 2. Handle Errors Gracefully

```javascript
async init(api) {
    try {
        await this.loadData();
        this.setupUI();
    } catch (error) {
        console.error('Plugin initialization failed:', error);
        api.notifications.show('Plugin failed to initialize', 'error');
    }
}
```

### 3. Clean Up Resources

```javascript
cleanup() {
    // Remove event listeners
    this.api.events.off('my-event', this.myHandler);
    
    // Clear intervals/timeouts
    if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
    }
    
    // Remove UI elements
    this.api.ui.removeWidget(this.widgetId);
}
```

### 4. Use Semantic Versioning

Follow semantic versioning for your plugin versions:
- MAJOR.MINOR.PATCH (e.g., 1.2.3)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### 5. Provide Clear Metadata

```javascript
const plugin = {
    id: 'system-monitor-plus',
    name: 'System Monitor Plus',
    version: '2.1.0',
    author: 'Jane Developer',
    description: 'Enhanced system monitoring with real-time graphs and alerts',
    homepage: 'https://github.com/jane/system-monitor-plus',
    license: 'MIT'
};
```

## Examples

### Example 1: Simple Dashboard Widget

```javascript
const plugin = {
    id: 'hello-world',
    name: 'Hello World',
    version: '1.0.0',
    author: 'Tutorial',
    permissions: ['ui'],
    
    async init(api) {
        api.ui.addDashboardWidget({
            id: 'hello-widget',
            title: 'Hello',
            content: `
                <div style="padding: 20px; text-align: center;">
                    <h3>Hello, NixOS!</h3>
                    <p>Current time: <span id="time"></span></p>
                </div>
            `,
            render: (container) => {
                const updateTime = () => {
                    const timeSpan = container.querySelector('#time');
                    if (timeSpan) {
                        timeSpan.textContent = new Date().toLocaleTimeString();
                    }
                };
                
                updateTime();
                setInterval(updateTime, 1000);
            }
        });
    }
};
```

### Example 2: Package Statistics

```javascript
const plugin = {
    id: 'package-stats',
    name: 'Package Statistics',
    version: '1.0.0',
    author: 'Example',
    permissions: ['ui', 'storage', 'events'],
    
    stats: {
        installed: 0,
        removed: 0
    },
    
    async init(api) {
        this.api = api;
        
        // Load saved stats
        const saved = api.storage.get('stats');
        if (saved) {
            this.stats = saved;
        }
        
        // Add widget
        this.addStatsWidget();
        
        // Listen for events
        api.events.on('package-installed', () => {
            this.stats.installed++;
            this.updateStats();
        });
        
        api.events.on('package-removed', () => {
            this.stats.removed++;
            this.updateStats();
        });
    },
    
    addStatsWidget() {
        this.api.ui.addDashboardWidget({
            id: 'package-stats',
            title: 'Package Statistics',
            content: `
                <div class="package-stats">
                    <div class="stat">
                        <span class="label">Installed:</span>
                        <span class="value" id="installed">0</span>
                    </div>
                    <div class="stat">
                        <span class="label">Removed:</span>
                        <span class="value" id="removed">0</span>
                    </div>
                </div>
            `,
            render: () => this.updateStats()
        });
    },
    
    updateStats() {
        // Update UI
        const installed = document.getElementById('installed');
        const removed = document.getElementById('removed');
        
        if (installed) installed.textContent = this.stats.installed;
        if (removed) removed.textContent = this.stats.removed;
        
        // Save stats
        this.api.storage.set('stats', this.stats);
    },
    
    cleanup() {
        // Event listeners are automatically cleaned up
    }
};
```

### Example 3: System Hooks

```javascript
const plugin = {
    id: 'rebuild-notifier',
    name: 'Rebuild Notifier',
    version: '1.0.0',
    author: 'Example',
    permissions: ['notifications', 'storage'],
    
    hooks: {
        beforeSystemRebuild: async (data) => {
            // Save timestamp
            this.api.storage.set('lastRebuildStart', Date.now());
            
            // Show notification
            this.api.notifications.show(
                'System rebuild starting...',
                'info'
            );
        },
        
        afterSystemRebuild: async (data) => {
            const startTime = this.api.storage.get('lastRebuildStart');
            const duration = Date.now() - startTime;
            const minutes = Math.round(duration / 60000);
            
            this.api.notifications.show(
                `System rebuild completed in ${minutes} minutes`,
                'success',
                5000
            );
        }
    },
    
    async init(api) {
        this.api = api;
        console.log('Rebuild Notifier plugin loaded');
    }
};
```

## Publishing Plugins

### 1. Package Your Plugin

Create a single JavaScript file containing your plugin code.

```bash
# Minify for production (optional)
terser my-plugin.js -o my-plugin.min.js
```

### 2. Create Plugin Manifest

Create a `manifest.json` file:

```json
{
    "id": "my-awesome-plugin",
    "name": "My Awesome Plugin",
    "version": "1.0.0",
    "author": "Your Name",
    "description": "A brief description",
    "homepage": "https://github.com/username/my-awesome-plugin",
    "downloadUrl": "https://github.com/username/my-awesome-plugin/releases/download/v1.0.0/my-awesome-plugin.js",
    "sha256": "...",
    "minNixosGuiVersion": "1.0.0",
    "maxNixosGuiVersion": "2.0.0"
}
```

### 3. Submit to Plugin Repository

1. Fork the [nixos-gui-plugins](https://github.com/nixos-gui/plugins) repository
2. Add your manifest to `plugins/` directory
3. Submit a pull request

### 4. Plugin Guidelines

- Provide clear documentation
- Include screenshots/demos
- Respond to user issues
- Follow semantic versioning
- Test on multiple NixOS versions
- Keep plugin size reasonable

## Debugging

### Enable Debug Mode

```javascript
const plugin = {
    debug: true, // Enable debug logging
    
    async init(api) {
        if (this.debug) {
            console.log('Plugin initializing with API:', api);
        }
    }
};
```

### Common Issues

1. **Plugin not loading**: Check browser console for errors
2. **Missing permissions**: Ensure all required permissions are declared
3. **UI not updating**: Make sure DOM elements exist before modifying
4. **Events not firing**: Verify event names and handler binding

## Support

- GitHub Issues: [nixos-gui/issues](https://github.com/nixos-gui/nixos-gui/issues)
- Plugin Repository: [nixos-gui/plugins](https://github.com/nixos-gui/plugins)
- Documentation: [nixos-gui.org/plugins](https://nixos-gui.org/plugins)

---

Happy plugin development! 🎉