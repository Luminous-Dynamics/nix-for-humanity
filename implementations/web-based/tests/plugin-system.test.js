/**
 * Plugin System Tests
 * Comprehensive test suite for the plugin architecture
 */

import { PluginSystem } from '../js/plugin-system';
import { PluginManager } from '../js/plugin-manager';
import { validatePlugin, sanitizePath } from '../backend/utils/security';

describe('PluginSystem', () => {
    let pluginSystem;

    beforeEach(() => {
        // Reset localStorage
        localStorage.clear();
        
        // Create plugin system instance
        pluginSystem = new PluginSystem();
        
        // Mock DOM elements
        document.body.innerHTML = `
            <div class="dashboard"></div>
            <div class="toolbar"></div>
            <nav class="menu">
                <div class="menu-item" data-menu="tools">
                    <ul class="submenu"></ul>
                </div>
            </nav>
        `;
    });

    afterEach(() => {
        // Cleanup
        if (pluginSystem) {
            pluginSystem.getAllPlugins().forEach(plugin => {
                pluginSystem.unloadPlugin(plugin.id);
            });
        }
    });

    describe('Plugin Registration', () => {
        it('should register a valid plugin', async () => {
            const testPlugin = {
                id: 'test-plugin',
                name: 'Test Plugin',
                version: '1.0.0',
                author: 'Test Author',
                permissions: ['ui', 'storage'],
                init: jest.fn(),
                cleanup: jest.fn()
            };

            await pluginSystem.registerPlugin(testPlugin);
            const registered = pluginSystem.getPluginInfo('test-plugin');

            expect(registered).toBeDefined();
            expect(registered.id).toBe('test-plugin');
            expect(registered.name).toBe('Test Plugin');
        });

        it('should reject plugin with invalid ID', async () => {
            const invalidPlugin = {
                id: 'Invalid ID!',
                name: 'Invalid Plugin',
                version: '1.0.0',
                author: 'Test',
                init: jest.fn()
            };

            await expect(pluginSystem.registerPlugin(invalidPlugin))
                .rejects.toThrow('Invalid plugin ID');
        });

        it('should reject plugin without required fields', async () => {
            const incompletePlugin = {
                id: 'incomplete',
                name: 'Incomplete Plugin'
                // Missing version, author, init
            };

            await expect(pluginSystem.registerPlugin(incompletePlugin))
                .rejects.toThrow();
        });

        it('should reject duplicate plugin IDs', async () => {
            const plugin1 = {
                id: 'duplicate',
                name: 'Plugin 1',
                version: '1.0.0',
                author: 'Test',
                init: jest.fn()
            };

            const plugin2 = {
                id: 'duplicate',
                name: 'Plugin 2',
                version: '1.0.0',
                author: 'Test',
                init: jest.fn()
            };

            await pluginSystem.registerPlugin(plugin1);
            await expect(pluginSystem.registerPlugin(plugin2))
                .rejects.toThrow('Plugin duplicate is already registered');
        });
    });

    describe('Plugin Loading', () => {
        it('should load a plugin successfully', async () => {
            const testPlugin = {
                id: 'loadable',
                name: 'Loadable Plugin',
                version: '1.0.0',
                author: 'Test',
                permissions: ['ui'],
                init: jest.fn(async (api) => {
                    expect(api).toBeDefined();
                    expect(api.ui).toBeDefined();
                })
            };

            await pluginSystem.registerPlugin(testPlugin);
            await pluginSystem.loadPlugin('loadable');

            expect(testPlugin.init).toHaveBeenCalled();
            expect(pluginSystem.getPluginInfo('loadable').loaded).toBe(true);
        });

        it('should provide correct API based on permissions', async () => {
            let providedAPI;
            
            const testPlugin = {
                id: 'api-test',
                name: 'API Test Plugin',
                version: '1.0.0',
                author: 'Test',
                permissions: ['ui', 'storage', 'events'],
                init: jest.fn(async (api) => {
                    providedAPI = api;
                })
            };

            await pluginSystem.registerPlugin(testPlugin);
            await pluginSystem.loadPlugin('api-test');

            expect(providedAPI.ui).toBeDefined();
            expect(providedAPI.storage).toBeDefined();
            expect(providedAPI.events).toBeDefined();
            expect(providedAPI.notifications).toBeUndefined(); // Not requested
        });

        it('should handle plugin load errors gracefully', async () => {
            const errorPlugin = {
                id: 'error-plugin',
                name: 'Error Plugin',
                version: '1.0.0',
                author: 'Test',
                init: jest.fn(async () => {
                    throw new Error('Plugin initialization failed');
                })
            };

            await pluginSystem.registerPlugin(errorPlugin);
            await expect(pluginSystem.loadPlugin('error-plugin'))
                .rejects.toThrow('Plugin initialization failed');
            
            expect(pluginSystem.getPluginInfo('error-plugin').loaded).toBe(false);
        });
    });

    describe('Plugin Hooks', () => {
        it('should register and execute hooks', async () => {
            const hookHandler = jest.fn();
            
            const hookPlugin = {
                id: 'hook-plugin',
                name: 'Hook Plugin',
                version: '1.0.0',
                author: 'Test',
                init: jest.fn(),
                hooks: {
                    beforePackageInstall: hookHandler
                }
            };

            await pluginSystem.registerPlugin(hookPlugin);
            await pluginSystem.loadPlugin('hook-plugin');

            // Execute hook
            await pluginSystem.executeHook('beforePackageInstall', { package: 'test' });
            
            expect(hookHandler).toHaveBeenCalledWith({ package: 'test' });
        });

        it('should execute multiple hooks in order', async () => {
            const results = [];
            
            const plugin1 = {
                id: 'hook-1',
                name: 'Hook 1',
                version: '1.0.0',
                author: 'Test',
                init: jest.fn(),
                hooks: {
                    testHook: async () => results.push(1)
                }
            };

            const plugin2 = {
                id: 'hook-2',
                name: 'Hook 2',
                version: '1.0.0',
                author: 'Test',
                init: jest.fn(),
                hooks: {
                    testHook: async () => results.push(2)
                }
            };

            await pluginSystem.registerPlugin(plugin1);
            await pluginSystem.registerPlugin(plugin2);
            await pluginSystem.loadPlugin('hook-1');
            await pluginSystem.loadPlugin('hook-2');

            await pluginSystem.executeHook('testHook');
            
            expect(results).toEqual([1, 2]);
        });
    });

    describe('Plugin Sandboxing', () => {
        it('should prevent access to dangerous globals', async () => {
            const maliciousPlugin = {
                id: 'malicious',
                name: 'Malicious Plugin',
                version: '1.0.0',
                author: 'Evil',
                init: jest.fn(async (api) => {
                    // Try to access dangerous globals
                    expect(window.require).toBeUndefined();
                    expect(window.process).toBeUndefined();
                    expect(window.global).toBeUndefined();
                })
            };

            await pluginSystem.registerPlugin(maliciousPlugin);
            await pluginSystem.loadPlugin('malicious');
            
            expect(maliciousPlugin.init).toHaveBeenCalled();
        });

        it('should isolate plugin storage', async () => {
            const plugin1 = {
                id: 'storage-1',
                name: 'Storage 1',
                version: '1.0.0',
                author: 'Test',
                permissions: ['storage'],
                init: jest.fn(async (api) => {
                    api.storage.set('key', 'value1');
                })
            };

            const plugin2 = {
                id: 'storage-2',
                name: 'Storage 2',
                version: '1.0.0',
                author: 'Test',
                permissions: ['storage'],
                init: jest.fn(async (api) => {
                    // Should not see plugin1's data
                    expect(api.storage.get('key')).toBeNull();
                    api.storage.set('key', 'value2');
                })
            };

            await pluginSystem.registerPlugin(plugin1);
            await pluginSystem.registerPlugin(plugin2);
            await pluginSystem.loadPlugin('storage-1');
            await pluginSystem.loadPlugin('storage-2');

            // Verify isolation
            const api1 = pluginSystem.createPluginAPI('storage-1', ['storage']);
            const api2 = pluginSystem.createPluginAPI('storage-2', ['storage']);
            
            expect(api1.storage.get('key')).toBe('value1');
            expect(api2.storage.get('key')).toBe('value2');
        });
    });

    describe('Plugin UI Integration', () => {
        it('should add dashboard widget', async () => {
            const widgetPlugin = {
                id: 'widget-plugin',
                name: 'Widget Plugin',
                version: '1.0.0',
                author: 'Test',
                permissions: ['ui'],
                init: jest.fn(async (api) => {
                    api.ui.addDashboardWidget({
                        id: 'test-widget',
                        title: 'Test Widget',
                        content: '<div>Test Content</div>'
                    });
                })
            };

            await pluginSystem.registerPlugin(widgetPlugin);
            await pluginSystem.loadPlugin('widget-plugin');

            const widget = document.querySelector('.plugin-widget[data-widget-id="test-widget"]');
            expect(widget).toBeTruthy();
            expect(widget.querySelector('.widget-header h3').textContent).toBe('Test Widget');
        });

        it('should add toolbar button', async () => {
            const buttonPlugin = {
                id: 'button-plugin',
                name: 'Button Plugin',
                version: '1.0.0',
                author: 'Test',
                permissions: ['ui'],
                init: jest.fn(async (api) => {
                    api.ui.addToolbarButton({
                        id: 'test-button',
                        icon: 'icon-test',
                        tooltip: 'Test Button',
                        action: jest.fn()
                    });
                })
            };

            await pluginSystem.registerPlugin(buttonPlugin);
            await pluginSystem.loadPlugin('button-plugin');

            const button = document.querySelector('.toolbar button[data-plugin-button="test-button"]');
            expect(button).toBeTruthy();
            expect(button.getAttribute('title')).toBe('Test Button');
        });

        it('should add menu item', async () => {
            const menuPlugin = {
                id: 'menu-plugin',
                name: 'Menu Plugin',
                version: '1.0.0',
                author: 'Test',
                permissions: ['ui'],
                init: jest.fn(async (api) => {
                    api.ui.addMenuItem('tools', {
                        label: 'Test Menu Item',
                        icon: 'icon-test',
                        action: jest.fn()
                    });
                })
            };

            await pluginSystem.registerPlugin(menuPlugin);
            await pluginSystem.loadPlugin('menu-plugin');

            const menuItem = document.querySelector('.menu-item[data-menu="tools"] .submenu .plugin-menu-item');
            expect(menuItem).toBeTruthy();
            expect(menuItem.textContent).toContain('Test Menu Item');
        });
    });

    describe('Plugin Unloading', () => {
        it('should cleanup plugin resources on unload', async () => {
            const cleanupPlugin = {
                id: 'cleanup-test',
                name: 'Cleanup Test',
                version: '1.0.0',
                author: 'Test',
                permissions: ['ui'],
                widgets: [],
                init: jest.fn(async function(api) {
                    // Store reference to track cleanup
                    this.widgets.push(api.ui.addDashboardWidget({
                        id: 'cleanup-widget',
                        title: 'Cleanup Widget',
                        content: '<div>Will be removed</div>'
                    }));
                }),
                cleanup: jest.fn()
            };

            await pluginSystem.registerPlugin(cleanupPlugin);
            await pluginSystem.loadPlugin('cleanup-test');

            // Verify widget exists
            expect(document.querySelector('[data-widget-id="cleanup-widget"]')).toBeTruthy();

            // Unload plugin
            await pluginSystem.unloadPlugin('cleanup-test');

            // Verify cleanup
            expect(cleanupPlugin.cleanup).toHaveBeenCalled();
            expect(document.querySelector('[data-widget-id="cleanup-widget"]')).toBeFalsy();
            expect(pluginSystem.getPluginInfo('cleanup-test').loaded).toBe(false);
        });

        it('should remove event listeners on unload', async () => {
            const eventHandler = jest.fn();
            
            const eventPlugin = {
                id: 'event-test',
                name: 'Event Test',
                version: '1.0.0',
                author: 'Test',
                permissions: ['events'],
                init: jest.fn(async (api) => {
                    api.events.on('test-event', eventHandler);
                }),
                cleanup: jest.fn()
            };

            await pluginSystem.registerPlugin(eventPlugin);
            await pluginSystem.loadPlugin('event-test');

            // Emit event - should be handled
            pluginSystem.events.emit('test-event', { data: 'test' });
            expect(eventHandler).toHaveBeenCalledWith({ data: 'test' });

            // Unload plugin
            await pluginSystem.unloadPlugin('event-test');

            // Emit event again - should not be handled
            eventHandler.mockClear();
            pluginSystem.events.emit('test-event', { data: 'test2' });
            expect(eventHandler).not.toHaveBeenCalled();
        });
    });

    describe('Plugin Persistence', () => {
        it('should save and restore enabled plugins', async () => {
            const plugin1 = {
                id: 'persist-1',
                name: 'Persist 1',
                version: '1.0.0',
                author: 'Test',
                init: jest.fn()
            };

            const plugin2 = {
                id: 'persist-2',
                name: 'Persist 2',
                version: '1.0.0',
                author: 'Test',
                init: jest.fn()
            };

            await pluginSystem.registerPlugin(plugin1);
            await pluginSystem.registerPlugin(plugin2);
            
            pluginSystem.setPluginEnabled('persist-1', true);
            pluginSystem.setPluginEnabled('persist-2', false);

            // Create new instance to test persistence
            const newPluginSystem = new PluginSystem();
            
            expect(newPluginSystem.getEnabledPlugins()).toContain('persist-1');
            expect(newPluginSystem.getEnabledPlugins()).not.toContain('persist-2');
        });
    });
});

describe('Plugin Security', () => {
    describe('validatePlugin', () => {
        it('should validate correct plugin structure', () => {
            const validPlugin = {
                code: `
                    const plugin = {
                        id: 'test',
                        name: 'Test Plugin',
                        version: '1.0.0',
                        author: 'Test Author',
                        init: async function(api) {
                            console.log('Plugin initialized');
                        }
                    };
                `,
                metadata: {
                    id: 'test',
                    name: 'Test Plugin',
                    version: '1.0.0',
                    author: 'Test Author',
                    permissions: ['ui', 'storage']
                }
            };

            const result = validatePlugin(validPlugin);
            expect(result.valid).toBe(true);
        });

        it('should reject plugin with dangerous code patterns', () => {
            const dangerousPlugin = {
                code: `
                    const plugin = {
                        id: 'dangerous',
                        name: 'Dangerous Plugin',
                        init: async function(api) {
                            const fs = require('fs');
                            fs.readFileSync('/etc/passwd');
                        }
                    };
                `,
                metadata: {
                    id: 'dangerous',
                    name: 'Dangerous Plugin',
                    version: '1.0.0',
                    author: 'Evil'
                }
            };

            const result = validatePlugin(dangerousPlugin);
            expect(result.valid).toBe(false);
            expect(result.error).toContain('dangerous code pattern');
        });

        it('should reject plugin with invalid permissions', () => {
            const invalidPermPlugin = {
                code: `const plugin = { id: 'test', name: 'Test', init: function() {} };`,
                metadata: {
                    id: 'test',
                    name: 'Test',
                    version: '1.0.0',
                    author: 'Test',
                    permissions: ['ui', 'hack-system', 'storage']
                }
            };

            const result = validatePlugin(invalidPermPlugin);
            expect(result.valid).toBe(false);
            expect(result.error).toContain('Invalid permission');
        });
    });

    describe('sanitizePath', () => {
        it('should allow valid paths within base directory', () => {
            const basePath = '/etc/nixos-gui/plugins';
            const validPath = 'my-plugin/config.json';
            
            const result = sanitizePath(validPath, basePath);
            expect(result).toBe('/etc/nixos-gui/plugins/my-plugin/config.json');
        });

        it('should reject path traversal attempts', () => {
            const basePath = '/etc/nixos-gui/plugins';
            const maliciousPath = '../../../etc/passwd';
            
            const result = sanitizePath(maliciousPath, basePath);
            expect(result).toBeNull();
        });

        it('should reject absolute paths', () => {
            const basePath = '/etc/nixos-gui/plugins';
            const absolutePath = '/etc/passwd';
            
            const result = sanitizePath(absolutePath, basePath);
            expect(result).toBeNull();
        });
    });
});

describe('PluginManager UI', () => {
    let pluginSystem;
    let pluginManager;

    beforeEach(() => {
        localStorage.clear();
        pluginSystem = new PluginSystem();
        pluginManager = new PluginManager(pluginSystem);
        
        document.body.innerHTML = '<div id="app"></div>';
        pluginManager.init();
    });

    it('should create plugin manager modal', () => {
        const modal = document.querySelector('.plugin-manager-modal');
        expect(modal).toBeTruthy();
        expect(modal.querySelector('.plugin-manager-header')).toBeTruthy();
        expect(modal.querySelector('.plugin-tabs')).toBeTruthy();
    });

    it('should switch between tabs', () => {
        const browseTab = document.querySelector('.tab-button[data-tab="browse"]');
        browseTab.click();

        expect(browseTab.classList.contains('active')).toBe(true);
        expect(document.querySelector('.tab-content[data-tab="browse"]').classList.contains('active')).toBe(true);
        expect(document.querySelector('.tab-content[data-tab="installed"]').classList.contains('active')).toBe(false);
    });

    it('should open and close plugin manager', () => {
        const modal = document.querySelector('.plugin-manager-modal');
        
        pluginManager.open();
        expect(modal.classList.contains('active')).toBe(true);
        
        pluginManager.close();
        expect(modal.classList.contains('active')).toBe(false);
    });

    it('should search plugins', async () => {
        // Add test plugins
        await pluginSystem.registerPlugin({
            id: 'search-test-1',
            name: 'Search Test One',
            version: '1.0.0',
            author: 'Test',
            description: 'This is a test plugin for searching',
            init: jest.fn()
        });

        await pluginSystem.registerPlugin({
            id: 'search-test-2',
            name: 'Another Plugin',
            version: '1.0.0',
            author: 'Test',
            description: 'This should not match',
            init: jest.fn()
        });

        await pluginManager.loadPluginList();

        const searchInput = document.querySelector('.plugin-search-input');
        searchInput.value = 'Search Test';
        searchInput.dispatchEvent(new Event('input'));

        const visibleCards = Array.from(document.querySelectorAll('.plugin-card'))
            .filter(card => card.style.display !== 'none');

        expect(visibleCards.length).toBe(1);
        expect(visibleCards[0].querySelector('h4').textContent).toBe('Search Test One');
    });
});