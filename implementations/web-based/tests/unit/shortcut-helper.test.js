/**
 * Unit Tests for Shortcut Helper
 */

import { ShortcutHelper } from '../../js/shortcut-helper';

describe('ShortcutHelper', () => {
    let shortcutHelper;
    let mockLocalStorage;
    
    beforeEach(() => {
        // Set up DOM
        document.body.innerHTML = `
            <div id="app">
                <input id="search-input" type="text" />
                <button id="save-button">Save</button>
                <div class="modal" id="test-modal">
                    <button class="close-button">Close</button>
                </div>
                <div class="shortcuts-panel" style="display:none;">
                    <h2>Keyboard Shortcuts</h2>
                    <div class="shortcuts-list"></div>
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
        
        shortcutHelper = new ShortcutHelper();
    });
    
    afterEach(() => {
        jest.clearAllMocks();
        // Remove event listeners
        shortcutHelper.destroy();
    });
    
    describe('Initialization', () => {
        it('should initialize with default shortcuts', () => {
            expect(shortcutHelper.shortcuts.size).toBeGreaterThan(0);
            expect(shortcutHelper.shortcuts.has('?')).toBe(true);
            expect(shortcutHelper.shortcuts.has('Escape')).toBe(true);
        });
        
        it('should set up event listeners', () => {
            const addEventListenerSpy = jest.spyOn(document, 'addEventListener');
            
            shortcutHelper.init();
            
            expect(addEventListenerSpy).toHaveBeenCalledWith(
                'keydown',
                expect.any(Function),
                expect.any(Object)
            );
        });
        
        it('should load custom shortcuts from localStorage', () => {
            mockLocalStorage.getItem.mockReturnValue(JSON.stringify({
                'Ctrl+S': {
                    description: 'Save',
                    handler: 'save'
                }
            }));
            
            const helper = new ShortcutHelper();
            helper.init();
            
            expect(helper.shortcuts.has('Ctrl+S')).toBe(true);
        });
    });
    
    describe('Shortcut Registration', () => {
        beforeEach(() => {
            shortcutHelper.init();
        });
        
        it('should register new shortcuts', () => {
            const handler = jest.fn();
            
            shortcutHelper.register('Ctrl+K', {
                description: 'Open search',
                handler,
                context: 'global'
            });
            
            expect(shortcutHelper.shortcuts.has('Ctrl+K')).toBe(true);
            expect(shortcutHelper.shortcuts.get('Ctrl+K').handler).toBe(handler);
        });
        
        it('should prevent duplicate registration', () => {
            const handler1 = jest.fn();
            const handler2 = jest.fn();
            
            shortcutHelper.register('Ctrl+K', {
                description: 'First handler',
                handler: handler1
            });
            
            // Should warn and not override
            const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
            
            shortcutHelper.register('Ctrl+K', {
                description: 'Second handler',
                handler: handler2
            });
            
            expect(consoleSpy).toHaveBeenCalledWith(
                expect.stringContaining('already registered')
            );
            expect(shortcutHelper.shortcuts.get('Ctrl+K').handler).toBe(handler1);
            
            consoleSpy.mockRestore();
        });
        
        it('should allow force override', () => {
            const handler1 = jest.fn();
            const handler2 = jest.fn();
            
            shortcutHelper.register('Ctrl+K', {
                description: 'First handler',
                handler: handler1
            });
            
            shortcutHelper.register('Ctrl+K', {
                description: 'Second handler',
                handler: handler2,
                override: true
            });
            
            expect(shortcutHelper.shortcuts.get('Ctrl+K').handler).toBe(handler2);
        });
        
        it('should unregister shortcuts', () => {
            const handler = jest.fn();
            
            shortcutHelper.register('Ctrl+K', {
                description: 'Test',
                handler
            });
            
            shortcutHelper.unregister('Ctrl+K');
            
            expect(shortcutHelper.shortcuts.has('Ctrl+K')).toBe(false);
        });
    });
    
    describe('Key Event Handling', () => {
        beforeEach(() => {
            shortcutHelper.init();
        });
        
        it('should handle simple key shortcuts', () => {
            const handler = jest.fn();
            
            shortcutHelper.register('k', {
                description: 'Test',
                handler
            });
            
            const event = new KeyboardEvent('keydown', { key: 'k' });
            document.dispatchEvent(event);
            
            expect(handler).toHaveBeenCalledWith(event);
        });
        
        it('should handle modifier key combinations', () => {
            const handler = jest.fn();
            
            shortcutHelper.register('Ctrl+Shift+K', {
                description: 'Test combo',
                handler
            });
            
            const event = new KeyboardEvent('keydown', {
                key: 'K',
                ctrlKey: true,
                shiftKey: true
            });
            document.dispatchEvent(event);
            
            expect(handler).toHaveBeenCalled();
        });
        
        it('should handle special keys', () => {
            const handler = jest.fn();
            
            shortcutHelper.register('Enter', {
                description: 'Submit',
                handler
            });
            
            const event = new KeyboardEvent('keydown', { key: 'Enter' });
            document.dispatchEvent(event);
            
            expect(handler).toHaveBeenCalled();
        });
        
        it('should prevent default when configured', () => {
            const handler = jest.fn();
            
            shortcutHelper.register('Ctrl+S', {
                description: 'Save',
                handler,
                preventDefault: true
            });
            
            const event = new KeyboardEvent('keydown', {
                key: 's',
                ctrlKey: true,
                cancelable: true
            });
            const preventDefaultSpy = jest.spyOn(event, 'preventDefault');
            
            document.dispatchEvent(event);
            
            expect(preventDefaultSpy).toHaveBeenCalled();
        });
    });
    
    describe('Context Handling', () => {
        beforeEach(() => {
            shortcutHelper.init();
        });
        
        it('should respect global context', () => {
            const handler = jest.fn();
            
            shortcutHelper.register('g', {
                description: 'Global shortcut',
                handler,
                context: 'global'
            });
            
            // Focus on input
            document.getElementById('search-input').focus();
            
            const event = new KeyboardEvent('keydown', { key: 'g' });
            document.dispatchEvent(event);
            
            // Should not trigger in input
            expect(handler).not.toHaveBeenCalled();
            
            // Blur input
            document.getElementById('search-input').blur();
            document.dispatchEvent(event);
            
            // Should trigger when not in input
            expect(handler).toHaveBeenCalled();
        });
        
        it('should handle specific contexts', () => {
            const handler = jest.fn();
            
            shortcutHelper.register('d', {
                description: 'Dashboard shortcut',
                handler,
                context: 'dashboard'
            });
            
            shortcutHelper.setContext('packages');
            
            const event = new KeyboardEvent('keydown', { key: 'd' });
            document.dispatchEvent(event);
            
            // Should not trigger in wrong context
            expect(handler).not.toHaveBeenCalled();
            
            shortcutHelper.setContext('dashboard');
            document.dispatchEvent(event);
            
            // Should trigger in correct context
            expect(handler).toHaveBeenCalled();
        });
        
        it('should handle input field shortcuts', () => {
            const handler = jest.fn();
            
            shortcutHelper.register('Tab', {
                description: 'Autocomplete',
                handler,
                context: 'input',
                preventDefault: true
            });
            
            const input = document.getElementById('search-input');
            input.focus();
            
            const event = new KeyboardEvent('keydown', {
                key: 'Tab',
                target: input
            });
            Object.defineProperty(event, 'target', {
                value: input,
                writable: true
            });
            
            document.dispatchEvent(event);
            
            expect(handler).toHaveBeenCalledWith(event);
        });
    });
    
    describe('Shortcut Groups', () => {
        beforeEach(() => {
            shortcutHelper.init();
        });
        
        it('should register shortcut groups', () => {
            const navigationShortcuts = {
                'Alt+1': { description: 'Go to Dashboard', handler: jest.fn() },
                'Alt+2': { description: 'Go to Packages', handler: jest.fn() },
                'Alt+3': { description: 'Go to Services', handler: jest.fn() }
            };
            
            shortcutHelper.registerGroup('navigation', navigationShortcuts);
            
            expect(shortcutHelper.shortcuts.has('Alt+1')).toBe(true);
            expect(shortcutHelper.shortcuts.has('Alt+2')).toBe(true);
            expect(shortcutHelper.shortcuts.has('Alt+3')).toBe(true);
            expect(shortcutHelper.groups.has('navigation')).toBe(true);
        });
        
        it('should enable/disable groups', () => {
            const handler = jest.fn();
            
            shortcutHelper.registerGroup('test', {
                't': { description: 'Test', handler }
            });
            
            shortcutHelper.disableGroup('test');
            
            const event = new KeyboardEvent('keydown', { key: 't' });
            document.dispatchEvent(event);
            
            expect(handler).not.toHaveBeenCalled();
            
            shortcutHelper.enableGroup('test');
            document.dispatchEvent(event);
            
            expect(handler).toHaveBeenCalled();
        });
    });
    
    describe('Help Panel', () => {
        beforeEach(() => {
            shortcutHelper.init();
        });
        
        it('should show help panel on ?', () => {
            const event = new KeyboardEvent('keydown', { key: '?' });
            document.dispatchEvent(event);
            
            const panel = document.querySelector('.shortcuts-panel');
            expect(panel.style.display).not.toBe('none');
        });
        
        it('should populate shortcuts list', () => {
            shortcutHelper.register('Ctrl+S', {
                description: 'Save document',
                category: 'File'
            });
            
            shortcutHelper.showHelp();
            
            const list = document.querySelector('.shortcuts-list');
            expect(list.textContent).toContain('Ctrl+S');
            expect(list.textContent).toContain('Save document');
        });
        
        it('should categorize shortcuts', () => {
            shortcutHelper.register('Ctrl+S', {
                description: 'Save',
                category: 'File'
            });
            
            shortcutHelper.register('Ctrl+O', {
                description: 'Open',
                category: 'File'
            });
            
            shortcutHelper.register('Ctrl+F', {
                description: 'Find',
                category: 'Edit'
            });
            
            shortcutHelper.showHelp();
            
            const categories = document.querySelectorAll('.shortcut-category');
            expect(categories.length).toBeGreaterThanOrEqual(2);
        });
        
        it('should close help panel on Escape', () => {
            shortcutHelper.showHelp();
            
            const event = new KeyboardEvent('keydown', { key: 'Escape' });
            document.dispatchEvent(event);
            
            const panel = document.querySelector('.shortcuts-panel');
            expect(panel.style.display).toBe('none');
        });
    });
    
    describe('Customization', () => {
        beforeEach(() => {
            shortcutHelper.init();
        });
        
        it('should allow custom key mappings', () => {
            const handler = jest.fn();
            
            shortcutHelper.register('j', {
                description: 'Next item',
                handler
            });
            
            // Remap to different key
            shortcutHelper.remap('j', 'ArrowDown');
            
            // Old key should not work
            let event = new KeyboardEvent('keydown', { key: 'j' });
            document.dispatchEvent(event);
            expect(handler).not.toHaveBeenCalled();
            
            // New key should work
            event = new KeyboardEvent('keydown', { key: 'ArrowDown' });
            document.dispatchEvent(event);
            expect(handler).toHaveBeenCalled();
        });
        
        it('should save custom mappings', () => {
            shortcutHelper.remap('j', 'ArrowDown');
            
            expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
                'shortcut_mappings',
                expect.any(String)
            );
        });
        
        it('should reset to defaults', () => {
            const handler = jest.fn();
            
            shortcutHelper.register('custom', {
                description: 'Custom shortcut',
                handler
            });
            
            shortcutHelper.resetToDefaults();
            
            expect(shortcutHelper.shortcuts.has('custom')).toBe(false);
            expect(shortcutHelper.shortcuts.has('?')).toBe(true); // Default preserved
        });
    });
    
    describe('Conflict Detection', () => {
        beforeEach(() => {
            shortcutHelper.init();
        });
        
        it('should detect conflicts', () => {
            shortcutHelper.register('Ctrl+S', {
                description: 'Save',
                handler: jest.fn()
            });
            
            const conflicts = shortcutHelper.checkConflicts('Ctrl+S');
            
            expect(conflicts.length).toBe(1);
            expect(conflicts[0].description).toBe('Save');
        });
        
        it('should handle OS-specific shortcuts', () => {
            // Mock Mac OS
            Object.defineProperty(navigator, 'platform', {
                value: 'MacIntel',
                writable: true
            });
            
            shortcutHelper.register('Cmd+S', {
                description: 'Save on Mac',
                handler: jest.fn(),
                platform: 'mac'
            });
            
            shortcutHelper.register('Ctrl+S', {
                description: 'Save on Windows/Linux',
                handler: jest.fn(),
                platform: 'win,linux'
            });
            
            const event = new KeyboardEvent('keydown', {
                key: 's',
                metaKey: true // Cmd key on Mac
            });
            
            const handler = shortcutHelper.getHandler(event);
            expect(handler.description).toBe('Save on Mac');
        });
    });
    
    describe('Chaining and Sequences', () => {
        beforeEach(() => {
            shortcutHelper.init();
        });
        
        it('should support key sequences', async () => {
            const handler = jest.fn();
            
            shortcutHelper.register('g g', {
                description: 'Go to top',
                handler,
                sequence: true
            });
            
            // First g
            let event = new KeyboardEvent('keydown', { key: 'g' });
            document.dispatchEvent(event);
            
            // Should not trigger yet
            expect(handler).not.toHaveBeenCalled();
            
            // Second g within timeout
            event = new KeyboardEvent('keydown', { key: 'g' });
            document.dispatchEvent(event);
            
            expect(handler).toHaveBeenCalled();
        });
        
        it('should timeout sequences', async () => {
            const handler = jest.fn();
            
            shortcutHelper.register('g g', {
                description: 'Go to top',
                handler,
                sequence: true,
                timeout: 500
            });
            
            // First g
            let event = new KeyboardEvent('keydown', { key: 'g' });
            document.dispatchEvent(event);
            
            // Wait for timeout
            await new Promise(resolve => setTimeout(resolve, 600));
            
            // Second g after timeout
            event = new KeyboardEvent('keydown', { key: 'g' });
            document.dispatchEvent(event);
            
            // Should not trigger
            expect(handler).not.toHaveBeenCalled();
        });
    });
    
    describe('Accessibility', () => {
        beforeEach(() => {
            shortcutHelper.init();
        });
        
        it('should provide screen reader announcements', () => {
            const announcement = document.createElement('div');
            announcement.setAttribute('aria-live', 'polite');
            announcement.id = 'shortcut-announcement';
            document.body.appendChild(announcement);
            
            shortcutHelper.announce('Save command executed');
            
            expect(announcement.textContent).toBe('Save command executed');
        });
        
        it('should not interfere with screen reader shortcuts', () => {
            const handler = jest.fn();
            
            shortcutHelper.register('h', {
                description: 'Help',
                handler,
                skipWhenScreenReader: true
            });
            
            // Mock screen reader active
            shortcutHelper.isScreenReaderActive = () => true;
            
            const event = new KeyboardEvent('keydown', { key: 'h' });
            document.dispatchEvent(event);
            
            expect(handler).not.toHaveBeenCalled();
        });
    });
    
    describe('Performance', () => {
        it('should handle many shortcuts efficiently', () => {
            // Register many shortcuts
            for (let i = 0; i < 100; i++) {
                shortcutHelper.register(`Alt+${i}`, {
                    description: `Shortcut ${i}`,
                    handler: jest.fn()
                });
            }
            
            const startTime = performance.now();
            
            // Dispatch events
            for (let i = 0; i < 10; i++) {
                const event = new KeyboardEvent('keydown', {
                    key: String(i),
                    altKey: true
                });
                document.dispatchEvent(event);
            }
            
            const endTime = performance.now();
            const duration = endTime - startTime;
            
            // Should process quickly
            expect(duration).toBeLessThan(50);
        });
    });
});