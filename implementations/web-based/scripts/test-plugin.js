#!/usr/bin/env node
/**
 * Plugin Testing Tool
 * Test plugins in isolation before installation
 */

const fs = require('fs').promises;
const path = require('path');
const vm = require('vm');
const { validatePlugin } = require('../backend/utils/security');

// Mock API for testing
const createMockAPI = (pluginId) => ({
    ui: {
        addDashboardWidget: (options) => {
            console.log(`[UI] Adding dashboard widget: ${options.id}`);
            return options.id;
        },
        addToolbarButton: (options) => {
            console.log(`[UI] Adding toolbar button: ${options.id}`);
            return options.id;
        },
        addMenuItem: (menu, options) => {
            console.log(`[UI] Adding menu item to ${menu}: ${options.label}`);
            return `${menu}-item`;
        },
        showModal: (options) => {
            console.log(`[UI] Showing modal: ${options.title}`);
        },
        removeWidget: (widgetId) => {
            console.log(`[UI] Removing widget: ${widgetId}`);
        }
    },
    
    storage: {
        data: new Map(),
        get: function(key) {
            const value = this.data.get(`${pluginId}:${key}`);
            console.log(`[Storage] Get ${key}: ${value}`);
            return value;
        },
        set: function(key, value) {
            console.log(`[Storage] Set ${key}:`, value);
            this.data.set(`${pluginId}:${key}`, value);
        },
        remove: function(key) {
            console.log(`[Storage] Remove ${key}`);
            this.data.delete(`${pluginId}:${key}`);
        },
        clear: function() {
            console.log(`[Storage] Clear all data`);
            for (const key of this.data.keys()) {
                if (key.startsWith(`${pluginId}:`)) {
                    this.data.delete(key);
                }
            }
        }
    },
    
    notifications: {
        show: (message, type = 'info', duration = 3000) => {
            console.log(`[Notification] ${type.toUpperCase()}: ${message} (${duration}ms)`);
        }
    },
    
    settings: {
        schema: {},
        values: {},
        listeners: [],
        define: function(schema) {
            console.log('[Settings] Defining schema:', schema);
            this.schema = schema;
        },
        get: function(key) {
            return this.values[key];
        },
        set: function(key, value) {
            console.log(`[Settings] Set ${key}:`, value);
            const oldValue = this.values[key];
            this.values[key] = value;
            this.listeners.forEach(listener => listener(key, value, oldValue));
        },
        onChanged: function(callback) {
            console.log('[Settings] Registered change listener');
            this.listeners.push(callback);
        }
    },
    
    events: {
        listeners: new Map(),
        on: function(event, handler) {
            console.log(`[Events] Listening to: ${event}`);
            if (!this.listeners.has(event)) {
                this.listeners.set(event, []);
            }
            this.listeners.get(event).push(handler);
        },
        off: function(event, handler) {
            console.log(`[Events] Removing listener for: ${event}`);
            if (this.listeners.has(event)) {
                const handlers = this.listeners.get(event);
                const index = handlers.indexOf(handler);
                if (index > -1) {
                    handlers.splice(index, 1);
                }
            }
        },
        emit: function(event, data) {
            console.log(`[Events] Emitting: ${event}`, data);
            if (this.listeners.has(event)) {
                this.listeners.get(event).forEach(handler => handler(data));
            }
        }
    }
});

async function testPlugin(pluginPath) {
    console.log('🧪 NixOS GUI Plugin Tester\n');
    console.log(`Testing plugin: ${pluginPath}\n`);
    
    try {
        // Read plugin file
        const pluginCode = await fs.readFile(pluginPath, 'utf8');
        
        // Extract metadata for validation
        const metadata = extractMetadata(pluginCode);
        
        console.log('📋 Plugin Metadata:');
        console.log(`  ID: ${metadata.id}`);
        console.log(`  Name: ${metadata.name}`);
        console.log(`  Version: ${metadata.version}`);
        console.log(`  Author: ${metadata.author}`);
        console.log(`  Permissions: ${metadata.permissions.join(', ')}`);
        console.log('');
        
        // Validate plugin
        console.log('🔍 Validating plugin...');
        const validation = validatePlugin({
            code: pluginCode,
            metadata: metadata
        });
        
        if (!validation.valid) {
            console.error('❌ Validation failed:', validation.error);
            process.exit(1);
        }
        
        console.log('✅ Validation passed\n');
        
        // Create sandbox
        console.log('📦 Creating sandbox environment...\n');
        const sandbox = {
            console: {
                log: (...args) => console.log('[Plugin]', ...args),
                error: (...args) => console.error('[Plugin]', ...args),
                warn: (...args) => console.warn('[Plugin]', ...args),
                info: (...args) => console.info('[Plugin]', ...args)
            },
            setTimeout,
            setInterval,
            clearTimeout,
            clearInterval,
            Date,
            Math,
            JSON,
            plugin: {}
        };
        
        // Execute plugin in sandbox
        const script = new vm.Script(pluginCode);
        const context = vm.createContext(sandbox);
        script.runInContext(context);
        
        const plugin = sandbox.plugin;
        
        // Create mock API
        const mockAPI = createMockAPI(plugin.id);
        
        // Filter API based on permissions
        const filteredAPI = {};
        if (plugin.permissions) {
            plugin.permissions.forEach(perm => {
                if (mockAPI[perm]) {
                    filteredAPI[perm] = mockAPI[perm];
                }
            });
        }
        
        // Test initialization
        console.log('🚀 Initializing plugin...\n');
        await plugin.init(filteredAPI);
        console.log('\n✅ Plugin initialized successfully\n');
        
        // Test hooks if available
        if (plugin.hooks) {
            console.log('🪝 Testing hooks...\n');
            
            for (const [hook, handler] of Object.entries(plugin.hooks)) {
                console.log(`Executing hook: ${hook}`);
                await handler({ test: true });
                console.log('');
            }
        }
        
        // Simulate some events
        if (filteredAPI.events) {
            console.log('📡 Simulating events...\n');
            
            filteredAPI.events.emit('theme-changed', 'dark');
            filteredAPI.events.emit('package-installed', { package: 'test-package' });
            filteredAPI.events.emit('service-started', { service: 'test-service' });
            console.log('');
        }
        
        // Test settings changes
        if (filteredAPI.settings) {
            console.log('⚙️ Testing settings...\n');
            
            filteredAPI.settings.set('enabled', false);
            filteredAPI.settings.set('enabled', true);
            console.log('');
        }
        
        // Test cleanup
        console.log('🧹 Testing cleanup...\n');
        if (plugin.cleanup) {
            plugin.cleanup();
            console.log('\n✅ Plugin cleaned up successfully\n');
        }
        
        // Performance metrics
        console.log('📊 Performance Metrics:');
        console.log(`  Code size: ${(pluginCode.length / 1024).toFixed(2)} KB`);
        console.log(`  Memory usage: ~${(process.memoryUsage().heapUsed / 1024 / 1024).toFixed(2)} MB`);
        
        // Summary
        console.log('\n✨ Plugin test completed successfully!');
        console.log('\nThe plugin appears to be working correctly.');
        console.log('You can now install it to your NixOS GUI instance.');
        
    } catch (error) {
        console.error('\n❌ Plugin test failed:', error.message);
        console.error('\nStack trace:', error.stack);
        process.exit(1);
    }
}

function extractMetadata(code) {
    const metadata = {
        id: 'unknown',
        name: 'Unknown Plugin',
        version: '0.0.0',
        author: 'Unknown',
        permissions: []
    };
    
    // Extract fields using regex
    const patterns = {
        id: /id:\s*['"`]([^'"`]+)['"`]/,
        name: /name:\s*['"`]([^'"`]+)['"`]/,
        version: /version:\s*['"`]([^'"`]+)['"`]/,
        author: /author:\s*['"`]([^'"`]+)['"`]/,
        permissions: /permissions:\s*\[([^\]]+)\]/
    };
    
    for (const [field, pattern] of Object.entries(patterns)) {
        const match = code.match(pattern);
        if (match) {
            if (field === 'permissions') {
                metadata[field] = match[1]
                    .split(',')
                    .map(p => p.trim().replace(/['"`]/g, ''))
                    .filter(p => p);
            } else {
                metadata[field] = match[1];
            }
        }
    }
    
    return metadata;
}

// CLI usage
if (require.main === module) {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.log('Usage: test-plugin <plugin-file>');
        console.log('Example: test-plugin my-plugin.js');
        process.exit(1);
    }
    
    const pluginPath = path.resolve(args[0]);
    testPlugin(pluginPath);
}