/**
 * Unit Tests for Plugin System
 */

import { PluginSystem } from '../../js/plugin-system';

describe('PluginSystem', () => {
    let pluginSystem;
    let mockLocalStorage;
    
    beforeEach(() => {
        // Set up DOM
        document.body.innerHTML = `
            <div id="app">
                <div class="dashboard">
                    <div class="plugin-widgets"></div>
                </div>
                <nav class="toolbar">
                    <div class="toolbar-plugins"></div>
                </nav>
                <div class="menu">
                    <ul class="menu-items"></ul>
                </div>
            </div>
        `;
        
        // Mock localStorage
        mockLocalStorage = {
            getItem: jest.fn(),
            setItem: jest.fn(),
            removeItem: jest.fn()
        };
        Object.defineProperty(window, 'localStorage', {
            value: mockLocalStorage,
            writable: true
        });
        
        // Mock fetch
        global.fetch = jest.fn();
        
        pluginSystem = new PluginSystem();
    });
    
    afterEach(() => {
        jest.clearAllMocks();
        pluginSystem.destroy();
    });
    
    describe('Initialization', () => {
        it('should initialize with default configuration', () => {
            expect(pluginSystem.plugins).toEqual(new Map());
            expect(pluginSystem.hooks).toEqual(new Map());
            expect(pluginSystem.sandboxes).toEqual(new Map());
        });
        
        it('should load plugins from storage on init', async () => {
            mockLocalStorage.getItem.mockReturnValue(JSON.stringify([
                {
                    id: 'test-plugin',
                    enabled: true,
                    source: 'console.log("Test plugin")'
                }
            ]));
            
            await pluginSystem.init();
            
            expect(pluginSystem.plugins.size).toBe(1);
            expect(pluginSystem.plugins.has('test-plugin')).toBe(true);
        });
        
        it('should create sandbox environments', () => {
            const sandbox = pluginSystem.createSandbox('test');
            
            expect(sandbox).toBeDefined();
            expect(sandbox.api).toBeDefined();
            expect(sandbox.context).toBeDefined();
        });
    });
    
    describe('Plugin Loading', () => {
        it('should load plugin from file', async () => {
            const pluginCode = `
                Plugin.register({
                    id: 'hello-world',
                    name: 'Hello World',
                    version: '1.0.0',
                    init() {
                        console.log('Hello from plugin!');
                    }
                });
            `;
            
            const file = new File([pluginCode], 'hello-world.js', {
                type: 'text/javascript'
            });
            
            await pluginSystem.loadPlugin(file);
            
            expect(pluginSystem.plugins.has('hello-world')).toBe(true);
            const plugin = pluginSystem.plugins.get('hello-world');
            expect(plugin.name).toBe('Hello World');
            expect(plugin.version).toBe('1.0.0');
        });
        
        it('should load plugin from URL', async () => {
            fetch.mockResolvedValueOnce({
                ok: true,
                text: () => Promise.resolve(`
                    Plugin.register({
                        id: 'remote-plugin',
                        name: 'Remote Plugin',
                        version: '1.0.0'
                    });
                `)
            });
            
            await pluginSystem.loadPluginFromUrl('https://example.com/plugin.js');
            
            expect(fetch).toHaveBeenCalledWith('https://example.com/plugin.js');
            expect(pluginSystem.plugins.has('remote-plugin')).toBe(true);
        });
        
        it('should validate plugin structure', async () => {
            const invalidPlugin = `
                Plugin.register({
                    // Missing required fields
                    name: 'Invalid'
                });
            `;
            
            await expect(pluginSystem.loadPluginCode(invalidPlugin))
                .rejects.toThrow('Invalid plugin');
        });
        
        it('should prevent duplicate plugin IDs', async () => {
            const plugin1 = `
                Plugin.register({
                    id: 'duplicate',
                    name: 'Plugin 1',
                    version: '1.0.0'
                });
            `;
            
            const plugin2 = `
                Plugin.register({
                    id: 'duplicate',
                    name: 'Plugin 2',
                    version: '2.0.0'
                });
            `;
            
            await pluginSystem.loadPluginCode(plugin1);
            
            await expect(pluginSystem.loadPluginCode(plugin2))
                .rejects.toThrow('already loaded');
        });
    });
    
    describe('Plugin Validation', () => {
        it('should detect dangerous code patterns', async () => {
            const dangerousPlugin = `
                Plugin.register({
                    id: 'dangerous',
                    name: 'Dangerous Plugin',
                    version: '1.0.0',
                    init() {
                        require('child_process').exec('rm -rf /');
                    }
                });
            `;
            
            await expect(pluginSystem.loadPluginCode(dangerousPlugin))
                .rejects.toThrow('dangerous patterns');
        });
        
        it('should enforce size limits', async () => {
            const largePlugin = 'x'.repeat(1024 * 1024 + 1); // 1MB + 1 byte
            
            await expect(pluginSystem.loadPluginCode(largePlugin))
                .rejects.toThrow('size limit');
        });
        
        it('should validate permissions', async () => {
            const plugin = `
                Plugin.register({
                    id: 'permissions-test',
                    name: 'Permissions Test',
                    version: '1.0.0',
                    permissions: ['ui', 'storage', 'invalid-permission']
                });
            `;
            
            await expect(pluginSystem.loadPluginCode(plugin))
                .rejects.toThrow('Invalid permission');
        });
    });
    
    describe('Plugin Lifecycle', () => {
        const testPlugin = `
            Plugin.register({
                id: 'lifecycle-test',
                name: 'Lifecycle Test',
                version: '1.0.0',
                init() {
                    this.initialized = true;
                    return { status: 'initialized' };
                },
                activate() {
                    this.activated = true;
                },
                deactivate() {
                    this.deactivated = true;
                },
                destroy() {
                    this.destroyed = true;
                }
            });
        `;
        
        beforeEach(async () => {
            await pluginSystem.loadPluginCode(testPlugin);
        });
        
        it('should initialize plugins', async () => {
            const result = await pluginSystem.initializePlugin('lifecycle-test');
            
            expect(result.status).toBe('initialized');
            const plugin = pluginSystem.plugins.get('lifecycle-test');
            expect(plugin.instance.initialized).toBe(true);
        });
        
        it('should activate plugins', async () => {
            await pluginSystem.initializePlugin('lifecycle-test');
            await pluginSystem.activatePlugin('lifecycle-test');
            
            const plugin = pluginSystem.plugins.get('lifecycle-test');
            expect(plugin.enabled).toBe(true);
            expect(plugin.instance.activated).toBe(true);
        });
        
        it('should deactivate plugins', async () => {
            await pluginSystem.initializePlugin('lifecycle-test');
            await pluginSystem.activatePlugin('lifecycle-test');
            await pluginSystem.deactivatePlugin('lifecycle-test');
            
            const plugin = pluginSystem.plugins.get('lifecycle-test');
            expect(plugin.enabled).toBe(false);
            expect(plugin.instance.deactivated).toBe(true);
        });
        
        it('should unload plugins', async () => {
            await pluginSystem.initializePlugin('lifecycle-test');
            await pluginSystem.unloadPlugin('lifecycle-test');
            
            expect(pluginSystem.plugins.has('lifecycle-test')).toBe(false);
            expect(pluginSystem.sandboxes.has('lifecycle-test')).toBe(false);
        });
    });
    
    describe('Plugin API', () => {
        const apiTestPlugin = `
            const results = {};
            
            Plugin.register({
                id: 'api-test',
                name: 'API Test',
                version: '1.0.0',
                permissions: ['ui', 'storage', 'events'],
                
                async init(api) {
                    // UI API
                    results.widgetId = await api.ui.addDashboardWidget({
                        title: 'Test Widget',
                        content: '<div>Hello</div>'
                    });
                    
                    // Storage API
                    await api.storage.set('test-key', 'test-value');
                    results.storageValue = await api.storage.get('test-key');
                    
                    // Events API
                    api.events.on('test-event', (data) => {
                        results.eventData = data;
                    });
                    
                    return results;
                }
            });
        `;
        
        it('should provide UI API', async () => {
            await pluginSystem.loadPluginCode(apiTestPlugin);
            const results = await pluginSystem.initializePlugin('api-test');
            
            expect(results.widgetId).toBeDefined();
            
            // Check widget was added to DOM
            const widget = document.querySelector(`[data-plugin-widget="${results.widgetId}"]`);
            expect(widget).toBeTruthy();
            expect(widget.textContent).toContain('Test Widget');
        });
        
        it('should provide Storage API', async () => {
            await pluginSystem.loadPluginCode(apiTestPlugin);
            const results = await pluginSystem.initializePlugin('api-test');
            
            expect(results.storageValue).toBe('test-value');
            
            // Check localStorage was used with namespacing
            expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
                expect.stringContaining('plugin:api-test:test-key'),
                '"test-value"'
            );
        });
        
        it('should provide Events API', async () => {
            await pluginSystem.loadPluginCode(apiTestPlugin);
            const results = await pluginSystem.initializePlugin('api-test');
            
            // Emit event
            pluginSystem.emitEvent('test-event', { message: 'Hello' });
            
            expect(results.eventData).toEqual({ message: 'Hello' });
        });
        
        it('should enforce API permissions', async () => {
            const noPermPlugin = `
                Plugin.register({
                    id: 'no-perm',
                    name: 'No Permissions',
                    version: '1.0.0',
                    permissions: [], // No permissions
                    
                    init(api) {
                        // Try to use UI API without permission
                        api.ui.addDashboardWidget({ title: 'Test' });
                    }
                });
            `;
            
            await pluginSystem.loadPluginCode(noPermPlugin);
            
            await expect(pluginSystem.initializePlugin('no-perm'))
                .rejects.toThrow('Permission denied: ui');
        });
    });
    
    describe('Hook System', () => {
        it('should register and execute hooks', async () => {
            const hookPlugin = `
                Plugin.register({
                    id: 'hook-plugin',
                    name: 'Hook Plugin',
                    version: '1.0.0',
                    
                    init(api) {
                        api.hooks.register('beforePackageInstall', async (data) => {
                            data.modified = true;
                            return data;
                        });
                    }
                });
            `;
            
            await pluginSystem.loadPluginCode(hookPlugin);
            await pluginSystem.initializePlugin('hook-plugin');
            
            const result = await pluginSystem.executeHook('beforePackageInstall', {
                package: 'vim'
            });
            
            expect(result.package).toBe('vim');
            expect(result.modified).toBe(true);
        });
        
        it('should execute hooks in priority order', async () => {
            const results = [];
            
            pluginSystem.registerHook('test-hook', () => {
                results.push('low');
            }, 10);
            
            pluginSystem.registerHook('test-hook', () => {
                results.push('high');
            }, 100);
            
            pluginSystem.registerHook('test-hook', () => {
                results.push('medium');
            }, 50);
            
            await pluginSystem.executeHook('test-hook');
            
            expect(results).toEqual(['high', 'medium', 'low']);
        });
        
        it('should handle hook errors gracefully', async () => {
            pluginSystem.registerHook('error-hook', () => {
                throw new Error('Hook error');
            });
            
            pluginSystem.registerHook('error-hook', () => {
                return { success: true };
            });
            
            const result = await pluginSystem.executeHook('error-hook', {});
            
            expect(result.success).toBe(true);
        });
    });
    
    describe('Sandbox Security', () => {
        it('should prevent access to global objects', async () => {
            const maliciousPlugin = `
                Plugin.register({
                    id: 'malicious',
                    name: 'Malicious',
                    version: '1.0.0',
                    
                    init() {
                        // Try to access Node.js globals
                        const fs = require('fs');
                        const process = global.process;
                        return { fs, process };
                    }
                });
            `;
            
            await pluginSystem.loadPluginCode(maliciousPlugin);
            
            await expect(pluginSystem.initializePlugin('malicious'))
                .rejects.toThrow();
        });
        
        it('should limit execution time', async () => {
            const infinitePlugin = `
                Plugin.register({
                    id: 'infinite',
                    name: 'Infinite Loop',
                    version: '1.0.0',
                    
                    init() {
                        while(true) {
                            // Infinite loop
                        }
                    }
                });
            `;
            
            await pluginSystem.loadPluginCode(infinitePlugin);
            
            await expect(pluginSystem.initializePlugin('infinite'))
                .rejects.toThrow('execution timeout');
        });
        
        it('should limit memory usage', async () => {
            const memoryHogPlugin = `
                Plugin.register({
                    id: 'memory-hog',
                    name: 'Memory Hog',
                    version: '1.0.0',
                    
                    init() {
                        const huge = [];
                        for(let i = 0; i < 1000000; i++) {
                            huge.push(new Array(1000).fill('x'));
                        }
                        return huge;
                    }
                });
            `;
            
            await pluginSystem.loadPluginCode(memoryHogPlugin);
            
            await expect(pluginSystem.initializePlugin('memory-hog'))
                .rejects.toThrow('memory limit');
        });
    });
    
    describe('Plugin Communication', () => {
        it('should allow inter-plugin communication', async () => {
            const plugin1 = `
                Plugin.register({
                    id: 'sender',
                    name: 'Sender',
                    version: '1.0.0',
                    permissions: ['events'],
                    
                    init(api) {
                        api.plugins.send('receiver', 'hello', { from: 'sender' });
                    }
                });
            `;
            
            const plugin2 = `
                Plugin.register({
                    id: 'receiver',
                    name: 'Receiver',
                    version: '1.0.0',
                    permissions: ['events'],
                    
                    init(api) {
                        this.messages = [];
                        api.plugins.on('hello', (data) => {
                            this.messages.push(data);
                        });
                    }
                });
            `;
            
            await pluginSystem.loadPluginCode(plugin2);
            await pluginSystem.initializePlugin('receiver');
            
            await pluginSystem.loadPluginCode(plugin1);
            await pluginSystem.initializePlugin('sender');
            
            const receiver = pluginSystem.plugins.get('receiver');
            expect(receiver.instance.messages).toContainEqual({ from: 'sender' });
        });
        
        it('should check communication permissions', async () => {
            const unauthorizedPlugin = `
                Plugin.register({
                    id: 'unauthorized',
                    name: 'Unauthorized',
                    version: '1.0.0',
                    permissions: [], // No permissions
                    
                    init(api) {
                        api.plugins.send('target', 'message', {});
                    }
                });
            `;
            
            await pluginSystem.loadPluginCode(unauthorizedPlugin);
            
            await expect(pluginSystem.initializePlugin('unauthorized'))
                .rejects.toThrow('Permission denied');
        });
    });
    
    describe('Plugin Updates', () => {
        it('should check for updates', async () => {
            fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({
                    'test-plugin': {
                        version: '2.0.0',
                        url: 'https://example.com/test-plugin-2.0.0.js'
                    }
                })
            });
            
            const plugin = `
                Plugin.register({
                    id: 'test-plugin',
                    name: 'Test Plugin',
                    version: '1.0.0',
                    updateUrl: 'https://example.com/updates.json'
                });
            `;
            
            await pluginSystem.loadPluginCode(plugin);
            const updates = await pluginSystem.checkForUpdates();
            
            expect(updates['test-plugin']).toBeDefined();
            expect(updates['test-plugin'].version).toBe('2.0.0');
        });
        
        it('should update plugins', async () => {
            // Mock update check
            fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({
                    'test-plugin': {
                        version: '2.0.0',
                        url: 'https://example.com/test-plugin-2.0.0.js'
                    }
                })
            });
            
            // Mock plugin download
            fetch.mockResolvedValueOnce({
                ok: true,
                text: () => Promise.resolve(`
                    Plugin.register({
                        id: 'test-plugin',
                        name: 'Test Plugin',
                        version: '2.0.0'
                    });
                `)
            });
            
            const oldPlugin = `
                Plugin.register({
                    id: 'test-plugin',
                    name: 'Test Plugin',
                    version: '1.0.0',
                    updateUrl: 'https://example.com/updates.json'
                });
            `;
            
            await pluginSystem.loadPluginCode(oldPlugin);
            await pluginSystem.updatePlugin('test-plugin');
            
            const plugin = pluginSystem.plugins.get('test-plugin');
            expect(plugin.version).toBe('2.0.0');
        });
    });
    
    describe('Plugin Persistence', () => {
        it('should save plugin state', async () => {
            const plugin = `
                Plugin.register({
                    id: 'persistent',
                    name: 'Persistent Plugin',
                    version: '1.0.0',
                    permissions: ['storage'],
                    
                    init(api) {
                        api.storage.set('counter', 0);
                    }
                });
            `;
            
            await pluginSystem.loadPluginCode(plugin);
            await pluginSystem.initializePlugin('persistent');
            
            pluginSystem.saveState();
            
            expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
                'nixos-gui-plugins',
                expect.any(String)
            );
        });
        
        it('should restore plugin state', async () => {
            mockLocalStorage.getItem.mockReturnValue(JSON.stringify([
                {
                    id: 'restored',
                    name: 'Restored Plugin',
                    version: '1.0.0',
                    enabled: true,
                    source: `
                        Plugin.register({
                            id: 'restored',
                            name: 'Restored Plugin',
                            version: '1.0.0'
                        });
                    `
                }
            ]));
            
            await pluginSystem.restoreState();
            
            expect(pluginSystem.plugins.has('restored')).toBe(true);
            expect(pluginSystem.plugins.get('restored').enabled).toBe(true);
        });
    });
});