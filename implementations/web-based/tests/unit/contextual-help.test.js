/**
 * Unit Tests for Contextual Help System
 */

import { ContextualHelp } from '../../js/contextual-help';

describe('ContextualHelp', () => {
    let contextualHelp;
    let mockContainer;
    
    beforeEach(() => {
        // Set up DOM
        document.body.innerHTML = `
            <div id="test-container">
                <div data-help="packages.search">
                    <input id="search-input" />
                    <button class="help-icon" aria-label="Help"></button>
                </div>
                <div data-help="services.manage">
                    <div class="service-card">
                        <button class="start-button">Start</button>
                    </div>
                </div>
            </div>
        `;
        
        mockContainer = document.getElementById('test-container');
        contextualHelp = new ContextualHelp();
        
        // Mock window functions
        window.requestAnimationFrame = jest.fn(cb => setTimeout(cb, 0));
    });
    
    afterEach(() => {
        jest.clearAllMocks();
        // Clean up any remaining tooltips
        document.querySelectorAll('.help-tooltip').forEach(el => el.remove());
    });
    
    describe('Initialization', () => {
        it('should initialize with default options', () => {
            expect(contextualHelp.options.delay).toBe(500);
            expect(contextualHelp.options.position).toBe('top');
        });
        
        it('should accept custom options', () => {
            const customHelp = new ContextualHelp({
                delay: 1000,
                position: 'bottom',
                theme: 'dark'
            });
            
            expect(customHelp.options.delay).toBe(1000);
            expect(customHelp.options.position).toBe('bottom');
            expect(customHelp.options.theme).toBe('dark');
        });
        
        it('should find all help elements', () => {
            contextualHelp.init();
            
            const helpElements = mockContainer.querySelectorAll('[data-help]');
            expect(helpElements.length).toBe(2);
        });
    });
    
    describe('Tooltip Display', () => {
        beforeEach(() => {
            contextualHelp.init();
        });
        
        it('should show tooltip on hover', async () => {
            const helpIcon = mockContainer.querySelector('.help-icon');
            
            const mouseEnter = new MouseEvent('mouseenter');
            helpIcon.dispatchEvent(mouseEnter);
            
            // Wait for delay
            await new Promise(resolve => setTimeout(resolve, 600));
            
            const tooltip = document.querySelector('.help-tooltip');
            expect(tooltip).toBeTruthy();
            expect(tooltip.classList.contains('visible')).toBe(true);
        });
        
        it('should hide tooltip on mouse leave', async () => {
            const helpIcon = mockContainer.querySelector('.help-icon');
            
            // Show tooltip
            helpIcon.dispatchEvent(new MouseEvent('mouseenter'));
            await new Promise(resolve => setTimeout(resolve, 600));
            
            // Hide tooltip
            helpIcon.dispatchEvent(new MouseEvent('mouseleave'));
            await new Promise(resolve => setTimeout(resolve, 100));
            
            const tooltip = document.querySelector('.help-tooltip');
            expect(tooltip).toBeFalsy();
        });
        
        it('should not show tooltip if hover is too brief', async () => {
            const helpIcon = mockContainer.querySelector('.help-icon');
            
            helpIcon.dispatchEvent(new MouseEvent('mouseenter'));
            // Leave before delay
            await new Promise(resolve => setTimeout(resolve, 200));
            helpIcon.dispatchEvent(new MouseEvent('mouseleave'));
            
            await new Promise(resolve => setTimeout(resolve, 400));
            
            const tooltip = document.querySelector('.help-tooltip');
            expect(tooltip).toBeFalsy();
        });
    });
    
    describe('Help Content', () => {
        it('should load help content from registry', async () => {
            contextualHelp.helpContent = {
                'packages.search': {
                    title: 'Search Packages',
                    content: 'Use this field to search for NixOS packages.',
                    tips: ['Try searching by category', 'Use wildcards for broader search']
                }
            };
            
            contextualHelp.init();
            const helpIcon = mockContainer.querySelector('.help-icon');
            
            helpIcon.dispatchEvent(new MouseEvent('mouseenter'));
            await new Promise(resolve => setTimeout(resolve, 600));
            
            const tooltip = document.querySelector('.help-tooltip');
            expect(tooltip.textContent).toContain('Search Packages');
            expect(tooltip.textContent).toContain('Use this field to search');
        });
        
        it('should show fallback for missing content', async () => {
            contextualHelp.helpContent = {};
            contextualHelp.init();
            
            const helpIcon = mockContainer.querySelector('.help-icon');
            helpIcon.dispatchEvent(new MouseEvent('mouseenter'));
            await new Promise(resolve => setTimeout(resolve, 600));
            
            const tooltip = document.querySelector('.help-tooltip');
            expect(tooltip.textContent).toContain('No help available');
        });
        
        it('should support markdown content', async () => {
            contextualHelp.helpContent = {
                'packages.search': {
                    title: 'Search Help',
                    content: '**Bold text** and *italic text*',
                    markdown: true
                }
            };
            
            contextualHelp.init();
            const helpIcon = mockContainer.querySelector('.help-icon');
            
            helpIcon.dispatchEvent(new MouseEvent('mouseenter'));
            await new Promise(resolve => setTimeout(resolve, 600));
            
            const tooltip = document.querySelector('.help-tooltip');
            expect(tooltip.innerHTML).toContain('<strong>Bold text</strong>');
            expect(tooltip.innerHTML).toContain('<em>italic text</em>');
        });
    });
    
    describe('Tooltip Positioning', () => {
        beforeEach(() => {
            contextualHelp.init();
            
            // Mock getBoundingClientRect
            Element.prototype.getBoundingClientRect = jest.fn(() => ({
                top: 100,
                left: 100,
                bottom: 120,
                right: 150,
                width: 50,
                height: 20
            }));
        });
        
        it('should position tooltip above element by default', async () => {
            const helpIcon = mockContainer.querySelector('.help-icon');
            
            helpIcon.dispatchEvent(new MouseEvent('mouseenter'));
            await new Promise(resolve => setTimeout(resolve, 600));
            
            const tooltip = document.querySelector('.help-tooltip');
            const style = window.getComputedStyle(tooltip);
            
            // Should be positioned above
            expect(parseInt(style.top)).toBeLessThan(100);
        });
        
        it('should adjust position near viewport edges', async () => {
            // Mock element near top
            Element.prototype.getBoundingClientRect = jest.fn(() => ({
                top: 10,
                left: 100,
                bottom: 30,
                right: 150,
                width: 50,
                height: 20
            }));
            
            const helpIcon = mockContainer.querySelector('.help-icon');
            helpIcon.dispatchEvent(new MouseEvent('mouseenter'));
            await new Promise(resolve => setTimeout(resolve, 600));
            
            const tooltip = document.querySelector('.help-tooltip');
            // Should be positioned below when too close to top
            expect(tooltip.classList.contains('bottom')).toBe(true);
        });
    });
    
    describe('Keyboard Support', () => {
        beforeEach(() => {
            contextualHelp.init();
        });
        
        it('should show tooltip on focus', async () => {
            const helpIcon = mockContainer.querySelector('.help-icon');
            helpIcon.focus();
            
            await new Promise(resolve => setTimeout(resolve, 600));
            
            const tooltip = document.querySelector('.help-tooltip');
            expect(tooltip).toBeTruthy();
        });
        
        it('should hide tooltip on blur', async () => {
            const helpIcon = mockContainer.querySelector('.help-icon');
            
            helpIcon.focus();
            await new Promise(resolve => setTimeout(resolve, 600));
            
            helpIcon.blur();
            await new Promise(resolve => setTimeout(resolve, 100));
            
            const tooltip = document.querySelector('.help-tooltip');
            expect(tooltip).toBeFalsy();
        });
        
        it('should hide tooltip on Escape key', async () => {
            const helpIcon = mockContainer.querySelector('.help-icon');
            
            helpIcon.focus();
            await new Promise(resolve => setTimeout(resolve, 600));
            
            const escapeEvent = new KeyboardEvent('keydown', { key: 'Escape' });
            document.dispatchEvent(escapeEvent);
            
            await new Promise(resolve => setTimeout(resolve, 100));
            
            const tooltip = document.querySelector('.help-tooltip');
            expect(tooltip).toBeFalsy();
        });
    });
    
    describe('Dynamic Content', () => {
        it('should support dynamic help content', async () => {
            contextualHelp.helpContent = {
                'packages.search': {
                    title: 'Search Help',
                    content: (element) => {
                        const input = element.querySelector('input');
                        return `Current value: "${input.value || 'empty'}"`;
                    }
                }
            };
            
            contextualHelp.init();
            
            const searchInput = mockContainer.querySelector('#search-input');
            searchInput.value = 'firefox';
            
            const helpIcon = mockContainer.querySelector('.help-icon');
            helpIcon.dispatchEvent(new MouseEvent('mouseenter'));
            await new Promise(resolve => setTimeout(resolve, 600));
            
            const tooltip = document.querySelector('.help-tooltip');
            expect(tooltip.textContent).toContain('Current value: "firefox"');
        });
        
        it('should update content on context change', async () => {
            let context = 'default';
            
            contextualHelp.helpContent = {
                'services.manage': {
                    title: 'Service Help',
                    content: () => `Context: ${context}`
                }
            };
            
            contextualHelp.init();
            
            const serviceCard = mockContainer.querySelector('.service-card');
            const helpIcon = document.createElement('button');
            helpIcon.className = 'help-icon';
            serviceCard.appendChild(helpIcon);
            
            // First show
            helpIcon.dispatchEvent(new MouseEvent('mouseenter'));
            await new Promise(resolve => setTimeout(resolve, 600));
            
            let tooltip = document.querySelector('.help-tooltip');
            expect(tooltip.textContent).toContain('Context: default');
            
            // Hide and change context
            helpIcon.dispatchEvent(new MouseEvent('mouseleave'));
            await new Promise(resolve => setTimeout(resolve, 100));
            
            context = 'updated';
            
            // Show again
            helpIcon.dispatchEvent(new MouseEvent('mouseenter'));
            await new Promise(resolve => setTimeout(resolve, 600));
            
            tooltip = document.querySelector('.help-tooltip');
            expect(tooltip.textContent).toContain('Context: updated');
        });
    });
    
    describe('API Methods', () => {
        beforeEach(() => {
            contextualHelp.init();
        });
        
        it('should register new help content', () => {
            contextualHelp.register('custom.help', {
                title: 'Custom Help',
                content: 'This is custom help content'
            });
            
            expect(contextualHelp.helpContent['custom.help']).toBeDefined();
            expect(contextualHelp.helpContent['custom.help'].title).toBe('Custom Help');
        });
        
        it('should show help programmatically', async () => {
            contextualHelp.helpContent = {
                'packages.search': {
                    title: 'Search Help',
                    content: 'Search content'
                }
            };
            
            const element = mockContainer.querySelector('[data-help="packages.search"]');
            contextualHelp.showHelp(element);
            
            await new Promise(resolve => setTimeout(resolve, 100));
            
            const tooltip = document.querySelector('.help-tooltip');
            expect(tooltip).toBeTruthy();
            expect(tooltip.textContent).toContain('Search Help');
        });
        
        it('should hide all tooltips', async () => {
            const helpIcon = mockContainer.querySelector('.help-icon');
            
            helpIcon.dispatchEvent(new MouseEvent('mouseenter'));
            await new Promise(resolve => setTimeout(resolve, 600));
            
            contextualHelp.hideAll();
            
            await new Promise(resolve => setTimeout(resolve, 100));
            
            const tooltip = document.querySelector('.help-tooltip');
            expect(tooltip).toBeFalsy();
        });
        
        it('should destroy and clean up', () => {
            const helpIcon = mockContainer.querySelector('.help-icon');
            const mouseEnterSpy = jest.fn();
            helpIcon.addEventListener('mouseenter', mouseEnterSpy);
            
            contextualHelp.destroy();
            
            helpIcon.dispatchEvent(new MouseEvent('mouseenter'));
            
            // Should not create tooltip after destroy
            setTimeout(() => {
                const tooltip = document.querySelector('.help-tooltip');
                expect(tooltip).toBeFalsy();
            }, 600);
        });
    });
    
    describe('Accessibility', () => {
        beforeEach(() => {
            contextualHelp.init();
        });
        
        it('should have proper ARIA attributes', async () => {
            const helpIcon = mockContainer.querySelector('.help-icon');
            
            expect(helpIcon.getAttribute('aria-label')).toBe('Help');
            
            helpIcon.dispatchEvent(new MouseEvent('mouseenter'));
            await new Promise(resolve => setTimeout(resolve, 600));
            
            const tooltip = document.querySelector('.help-tooltip');
            expect(tooltip.getAttribute('role')).toBe('tooltip');
            expect(tooltip.getAttribute('aria-live')).toBe('polite');
        });
        
        it('should announce tooltip content to screen readers', async () => {
            contextualHelp.helpContent = {
                'packages.search': {
                    title: 'Search Help',
                    content: 'Search for packages',
                    announcement: 'Help available: Search for packages'
                }
            };
            
            const helpIcon = mockContainer.querySelector('.help-icon');
            helpIcon.dispatchEvent(new MouseEvent('mouseenter'));
            await new Promise(resolve => setTimeout(resolve, 600));
            
            const tooltip = document.querySelector('.help-tooltip');
            expect(tooltip.getAttribute('aria-label'))
                .toContain('Help available: Search for packages');
        });
    });
    
    describe('Performance', () => {
        it('should debounce rapid hover events', async () => {
            const showSpy = jest.spyOn(contextualHelp, 'showTooltip');
            contextualHelp.init();
            
            const helpIcon = mockContainer.querySelector('.help-icon');
            
            // Rapid hover events
            for (let i = 0; i < 10; i++) {
                helpIcon.dispatchEvent(new MouseEvent('mouseenter'));
                helpIcon.dispatchEvent(new MouseEvent('mouseleave'));
            }
            
            await new Promise(resolve => setTimeout(resolve, 700));
            
            // Should not show tooltip for rapid hovers
            expect(showSpy).not.toHaveBeenCalled();
        });
        
        it('should handle multiple tooltips efficiently', () => {
            // Add many help elements
            for (let i = 0; i < 100; i++) {
                const div = document.createElement('div');
                div.setAttribute('data-help', `help.${i}`);
                div.innerHTML = '<button class="help-icon">?</button>';
                mockContainer.appendChild(div);
            }
            
            const startTime = performance.now();
            contextualHelp.init();
            const initTime = performance.now() - startTime;
            
            // Should initialize quickly even with many elements
            expect(initTime).toBeLessThan(50);
        });
    });
});