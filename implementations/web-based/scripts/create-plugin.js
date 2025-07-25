#!/usr/bin/env node
/**
 * Plugin Creation Tool
 * Generates a new plugin from template
 */

const fs = require('fs').promises;
const path = require('path');
const readline = require('readline');
const { generatePluginId } = require('../backend/utils/security');

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

const question = (prompt) => new Promise((resolve) => {
    rl.question(prompt, resolve);
});

const PLUGIN_TEMPLATE = `/**
 * {{name}}
 * {{description}}
 * 
 * @author {{author}}
 * @version {{version}}
 * @license {{license}}
 */

const plugin = {
    // Plugin metadata
    id: '{{id}}',
    name: '{{name}}',
    version: '{{version}}',
    author: '{{author}}',
    description: '{{description}}',
    homepage: '{{homepage}}',
    license: '{{license}}',
    
    // Required permissions
    permissions: [{{permissions}}],
    
    // Plugin state
    initialized: false,
    
    /**
     * Initialize plugin
     * @param {Object} api - Plugin API
     */
    async init(api) {
        console.log('{{name}} plugin initializing...');
        
        this.api = api;
        this.initialized = true;
        
        // Setup plugin
        await this.setup();
        
        // Add UI elements
        this.addUI();
        
        // Setup event listeners
        this.setupEventListeners();
        
        console.log('{{name}} plugin initialized successfully');
    },
    
    /**
     * Setup plugin
     */
    async setup() {
        // Load saved settings
        const settings = this.api.storage.get('settings');
        if (settings) {
            this.settings = settings;
        } else {
            this.settings = this.getDefaultSettings();
            this.api.storage.set('settings', this.settings);
        }
        
        // Define settings schema
        if (this.api.settings) {
            this.api.settings.define(this.getSettingsSchema());
        }
    },
    
    /**
     * Get default settings
     */
    getDefaultSettings() {
        return {
            enabled: true,
            // Add your default settings here
        };
    },
    
    /**
     * Get settings schema
     */
    getSettingsSchema() {
        return {
            'enabled': {
                type: 'boolean',
                label: 'Enable {{name}}',
                description: 'Enable or disable the plugin',
                default: true
            },
            // Add more settings here
        };
    },
    
    /**
     * Add UI elements
     */
    addUI() {
        {{#if hasUI}}
        // Add dashboard widget
        if (this.api.ui) {
            this.addDashboardWidget();
            this.addToolbarButton();
            this.addMenuItem();
        }
        {{/if}}
    },
    
    {{#if hasUI}}
    /**
     * Add dashboard widget
     */
    addDashboardWidget() {
        this.widgetId = '{{id}}-widget';
        
        this.api.ui.addDashboardWidget({
            id: this.widgetId,
            title: '{{name}}',
            content: \`
                <div class="{{id}}-widget">
                    <p>{{name}} is active!</p>
                    <button id="{{id}}-action">Action</button>
                </div>
            \`,
            render: (container) => {
                // Add event listeners to widget
                const button = container.querySelector('#{{id}}-action');
                if (button) {
                    button.addEventListener('click', () => this.handleAction());
                }
            }
        });
    },
    
    /**
     * Add toolbar button
     */
    addToolbarButton() {
        this.api.ui.addToolbarButton({
            id: '{{id}}-button',
            icon: 'icon-package',
            tooltip: '{{name}}',
            action: () => this.showPluginModal()
        });
    },
    
    /**
     * Add menu item
     */
    addMenuItem() {
        this.api.ui.addMenuItem('tools', {
            label: '{{name}}',
            icon: 'icon-package',
            action: () => this.showPluginModal()
        });
    },
    
    /**
     * Show plugin modal
     */
    showPluginModal() {
        this.api.ui.showModal({
            title: '{{name}}',
            content: \`
                <div class="{{id}}-modal">
                    <h3>{{name}} Settings</h3>
                    <p>Configure your plugin here.</p>
                </div>
            \`,
            buttons: [
                {
                    label: 'Save',
                    action: () => this.saveSettings(),
                    primary: true
                },
                {
                    label: 'Cancel',
                    action: 'close'
                }
            ]
        });
    },
    
    /**
     * Handle action button click
     */
    handleAction() {
        if (this.api.notifications) {
            this.api.notifications.show('Action performed!', 'success');
        }
        
        // Add your action logic here
    },
    
    /**
     * Save settings
     */
    saveSettings() {
        // Save settings logic
        this.api.storage.set('settings', this.settings);
        
        if (this.api.notifications) {
            this.api.notifications.show('Settings saved', 'success');
        }
    },
    {{/if}}
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        {{#if hasEvents}}
        if (this.api.events) {
            // Listen for system events
            this.api.events.on('theme-changed', (theme) => {
                this.handleThemeChange(theme);
            });
            
            // Add more event listeners as needed
        }
        
        // Listen for settings changes
        if (this.api.settings) {
            this.api.settings.onChanged((key, value) => {
                this.handleSettingChange(key, value);
            });
        }
        {{/if}}
    },
    
    {{#if hasEvents}}
    /**
     * Handle theme change
     */
    handleThemeChange(theme) {
        console.log('Theme changed to:', theme);
        // Update plugin UI based on theme
    },
    
    /**
     * Handle setting change
     */
    handleSettingChange(key, value) {
        console.log(\`Setting \${key} changed to \${value}\`);
        this.settings[key] = value;
        
        // React to setting changes
        if (key === 'enabled') {
            if (value) {
                this.enable();
            } else {
                this.disable();
            }
        }
    },
    
    /**
     * Enable plugin functionality
     */
    enable() {
        console.log('{{name}} enabled');
        // Enable plugin features
    },
    
    /**
     * Disable plugin functionality
     */
    disable() {
        console.log('{{name}} disabled');
        // Disable plugin features
    },
    {{/if}}
    
    {{#if hasHooks}}
    /**
     * System hooks
     */
    hooks: {
        /**
         * Called before system rebuild
         */
        beforeSystemRebuild: async (data) => {
            console.log('System rebuild starting...');
            // Add pre-rebuild logic
        },
        
        /**
         * Called after system rebuild
         */
        afterSystemRebuild: async (data) => {
            console.log('System rebuild completed');
            // Add post-rebuild logic
        },
        
        /**
         * Called after package installation
         */
        afterPackageInstall: async (data) => {
            console.log('Package installed:', data.package);
            // React to package installation
        },
        
        /**
         * Called after package removal
         */
        afterPackageRemove: async (data) => {
            console.log('Package removed:', data.package);
            // React to package removal
        }
    },
    {{/if}}
    
    /**
     * Cleanup plugin
     */
    cleanup() {
        console.log('{{name}} cleaning up...');
        
        {{#if hasUI}}
        // Remove UI elements
        if (this.api.ui && this.widgetId) {
            this.api.ui.removeWidget(this.widgetId);
        }
        {{/if}}
        
        {{#if hasEvents}}
        // Remove event listeners
        if (this.api.events) {
            this.api.events.off('theme-changed', this.handleThemeChange);
        }
        {{/if}}
        
        // Save final state
        if (this.api.storage) {
            this.api.storage.set('lastCleanup', Date.now());
        }
        
        this.initialized = false;
        console.log('{{name}} cleanup complete');
    }
};

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = plugin;
}
`;

async function createPlugin() {
    console.log('🔌 NixOS GUI Plugin Creator\n');
    
    try {
        // Gather plugin information
        const info = {};
        
        info.name = await question('Plugin name: ');
        info.description = await question('Description: ');
        info.author = await question('Author name: ');
        info.homepage = await question('Homepage URL (optional): ');
        info.license = await question('License (default: MIT): ') || 'MIT';
        info.version = '1.0.0';
        
        // Generate plugin ID
        const suggestedId = info.name.toLowerCase().replace(/[^a-z0-9]+/g, '-');
        info.id = await question(`Plugin ID (default: ${suggestedId}): `) || suggestedId;
        
        // Select permissions
        console.log('\nSelect permissions (comma-separated):');
        console.log('Available: ui, storage, notifications, settings, events');
        const perms = await question('Permissions: ');
        info.permissions = perms.split(',').map(p => `'${p.trim()}'`).join(', ');
        
        // Feature flags
        info.hasUI = perms.includes('ui');
        info.hasEvents = perms.includes('events');
        info.hasHooks = await question('Include system hooks? (y/n): ').then(r => r.toLowerCase() === 'y');
        
        // Generate plugin code
        let pluginCode = PLUGIN_TEMPLATE;
        
        // Replace placeholders
        Object.entries(info).forEach(([key, value]) => {
            const regex = new RegExp(`{{${key}}}`, 'g');
            pluginCode = pluginCode.replace(regex, value);
        });
        
        // Handle conditionals
        pluginCode = pluginCode.replace(/{{#if (\w+)}}([\s\S]*?){{\/if}}/g, (match, condition, content) => {
            return info[condition] ? content : '';
        });
        
        // Output file
        const outputDir = await question('Output directory (default: ./): ') || './';
        const outputPath = path.join(outputDir, `${info.id}.js`);
        
        // Write plugin file
        await fs.writeFile(outputPath, pluginCode);
        
        console.log(`\n✅ Plugin created successfully: ${outputPath}`);
        
        // Create test file?
        const createTest = await question('\nCreate test file? (y/n): ');
        if (createTest.toLowerCase() === 'y') {
            await createTestFile(info, outputDir);
        }
        
        // Create README?
        const createReadme = await question('Create README? (y/n): ');
        if (createReadme.toLowerCase() === 'y') {
            await createReadmeFile(info, outputDir);
        }
        
        console.log('\n🎉 Plugin setup complete!');
        console.log('\nNext steps:');
        console.log('1. Test your plugin: npm run test-plugin ' + info.id);
        console.log('2. Install locally: cp ' + outputPath + ' ~/.config/nixos-gui/plugins/');
        console.log('3. Share with community: https://github.com/nixos-gui/plugins');
        
    } catch (error) {
        console.error('Error creating plugin:', error);
    } finally {
        rl.close();
    }
}

async function createTestFile(info, outputDir) {
    const testTemplate = `/**
 * Tests for ${info.name}
 */

import { ${info.id} } from './${info.id}';

describe('${info.name} Plugin', () => {
    let plugin;
    let mockAPI;
    
    beforeEach(() => {
        plugin = { ...${info.id} };
        
        // Mock API
        mockAPI = {
            ui: {
                addDashboardWidget: jest.fn(),
                addToolbarButton: jest.fn(),
                addMenuItem: jest.fn(),
                showModal: jest.fn(),
                removeWidget: jest.fn()
            },
            storage: {
                get: jest.fn(),
                set: jest.fn(),
                remove: jest.fn(),
                clear: jest.fn()
            },
            notifications: {
                show: jest.fn()
            },
            settings: {
                define: jest.fn(),
                get: jest.fn(),
                set: jest.fn(),
                onChanged: jest.fn()
            },
            events: {
                on: jest.fn(),
                off: jest.fn(),
                emit: jest.fn()
            }
        };
    });
    
    describe('Initialization', () => {
        it('should initialize successfully', async () => {
            await plugin.init(mockAPI);
            
            expect(plugin.initialized).toBe(true);
            expect(plugin.api).toBe(mockAPI);
        });
        
        it('should have correct metadata', () => {
            expect(plugin.id).toBe('${info.id}');
            expect(plugin.name).toBe('${info.name}');
            expect(plugin.version).toBe('${info.version}');
            expect(plugin.author).toBe('${info.author}');
        });
        
        it('should request correct permissions', () => {
            expect(plugin.permissions).toContain(${info.permissions || "'ui'"});
        });
    });
    
    ${info.hasUI ? `
    describe('UI Integration', () => {
        it('should add dashboard widget', async () => {
            await plugin.init(mockAPI);
            
            expect(mockAPI.ui.addDashboardWidget).toHaveBeenCalledWith(
                expect.objectContaining({
                    id: '${info.id}-widget',
                    title: '${info.name}'
                })
            );
        });
        
        it('should add toolbar button', async () => {
            await plugin.init(mockAPI);
            
            expect(mockAPI.ui.addToolbarButton).toHaveBeenCalledWith(
                expect.objectContaining({
                    id: '${info.id}-button',
                    tooltip: '${info.name}'
                })
            );
        });
    });
    ` : ''}
    
    describe('Settings', () => {
        it('should load default settings', async () => {
            mockAPI.storage.get.mockReturnValue(null);
            
            await plugin.init(mockAPI);
            
            expect(mockAPI.storage.set).toHaveBeenCalledWith(
                'settings',
                expect.objectContaining({
                    enabled: true
                })
            );
        });
        
        it('should define settings schema', async () => {
            await plugin.init(mockAPI);
            
            expect(mockAPI.settings.define).toHaveBeenCalledWith(
                expect.objectContaining({
                    'enabled': expect.any(Object)
                })
            );
        });
    });
    
    describe('Cleanup', () => {
        it('should cleanup resources', async () => {
            await plugin.init(mockAPI);
            plugin.cleanup();
            
            expect(plugin.initialized).toBe(false);
            ${info.hasUI ? "expect(mockAPI.ui.removeWidget).toHaveBeenCalled();" : ""}
        });
    });
});
`;
    
    const testPath = path.join(outputDir, `${info.id}.test.js`);
    await fs.writeFile(testPath, testTemplate);
    console.log(`✅ Test file created: ${testPath}`);
}

async function createReadmeFile(info, outputDir) {
    const readmeTemplate = `# ${info.name}

${info.description}

## Installation

### Via Plugin Manager
1. Open NixOS GUI
2. Go to Tools → Plugin Manager
3. Search for "${info.name}"
4. Click Install

### Manual Installation
\`\`\`bash
# User installation
cp ${info.id}.js ~/.config/nixos-gui/plugins/

# System-wide installation
sudo cp ${info.id}.js /etc/nixos-gui/plugins/
\`\`\`

## Features

- Feature 1
- Feature 2
- Feature 3

## Configuration

The plugin can be configured through the settings panel or by editing the configuration directly.

### Available Settings

- **Enabled**: Enable or disable the plugin
- Add more settings documentation here

## Usage

Describe how to use your plugin here.

## Development

### Building
\`\`\`bash
npm run build
\`\`\`

### Testing
\`\`\`bash
npm test
\`\`\`

## License

${info.license}

## Author

${info.author}${info.homepage ? `

## Links

- [Homepage](${info.homepage})` : ''}
`;
    
    const readmePath = path.join(outputDir, 'README.md');
    await fs.writeFile(readmePath, readmeTemplate);
    console.log(`✅ README created: ${readmePath}`);
}

// Run if called directly
if (require.main === module) {
    createPlugin();
}