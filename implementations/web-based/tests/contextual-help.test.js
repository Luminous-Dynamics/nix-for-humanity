const { ContextualHelp } = require('../js/components/contextual-help');
const { JSDOM } = require('jsdom');

// Set up DOM environment
const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', {
  url: 'http://localhost',
  pretendToBeVisual: true,
  resources: 'usable'
});

global.window = dom.window;
global.document = dom.window.document;
global.localStorage = {
  store: {},
  getItem(key) { return this.store[key] || null; },
  setItem(key, value) { this.store[key] = value; },
  removeItem(key) { delete this.store[key]; },
  clear() { this.store = {}; }
};

describe('ContextualHelp', () => {
  let contextualHelp;

  beforeEach(() => {
    document.body.innerHTML = '';
    localStorage.clear();
    contextualHelp = new ContextualHelp();
  });

  afterEach(() => {
    // Clean up
    if (contextualHelp.container) {
      contextualHelp.container.remove();
    }
  });

  describe('Initialization', () => {
    test('should create tooltip container', () => {
      const container = document.querySelector('.contextual-help-container');
      expect(container).toBeTruthy();
      expect(container.getAttribute('role')).toBe('tooltip');
      expect(container.getAttribute('aria-hidden')).toBe('true');
    });

    test('should load default options', () => {
      expect(contextualHelp.options.position).toBe('auto');
      expect(contextualHelp.options.delay).toBe(500);
      expect(contextualHelp.options.theme).toBe('dark');
    });

    test('should merge custom options', () => {
      const customHelp = new ContextualHelp({
        theme: 'light',
        delay: 1000
      });
      
      expect(customHelp.options.theme).toBe('light');
      expect(customHelp.options.delay).toBe(1000);
      expect(customHelp.options.position).toBe('auto'); // Default preserved
    });
  });

  describe('Registration', () => {
    test('should register elements with help content', () => {
      document.body.innerHTML = `
        <button class="test-btn">Test Button</button>
        <input class="test-input" />
      `;

      contextualHelp.register('.test-btn', 'package-install');
      contextualHelp.register('.test-input', 'package-search');

      const btn = document.querySelector('.test-btn');
      const input = document.querySelector('.test-input');

      expect(contextualHelp.tooltips.has(btn)).toBe(true);
      expect(contextualHelp.tooltips.has(input)).toBe(true);
      expect(btn.getAttribute('aria-describedby')).toBeTruthy();
    });

    test('should add help indicator when specified', () => {
      document.body.innerHTML = '<button class="test-btn">Test</button>';
      
      contextualHelp.register('.test-btn', 'package-install', {
        showIndicator: true
      });

      const indicator = document.querySelector('.help-indicator');
      expect(indicator).toBeTruthy();
      expect(indicator.textContent).toBe('?');
    });
  });

  describe('Tooltip Display', () => {
    test('should show tooltip with correct content', () => {
      const element = document.createElement('button');
      document.body.appendChild(element);

      contextualHelp.show(element, 'package-install');

      const tooltip = document.querySelector('.tooltip-content');
      expect(tooltip).toBeTruthy();
      expect(tooltip.textContent).toContain('Install Package');
      expect(contextualHelp.container.classList.contains('active')).toBe(true);
    });

    test('should hide tooltip', () => {
      const element = document.createElement('button');
      document.body.appendChild(element);

      contextualHelp.show(element, 'package-install');
      contextualHelp.hide();

      expect(contextualHelp.container.classList.contains('active')).toBe(false);
      expect(contextualHelp.activeTooltip).toBeNull();
    });

    test('should position tooltip correctly', () => {
      const element = document.createElement('button');
      element.style.position = 'fixed';
      element.style.left = '100px';
      element.style.top = '100px';
      element.style.width = '100px';
      element.style.height = '40px';
      document.body.appendChild(element);

      // Mock getBoundingClientRect
      element.getBoundingClientRect = jest.fn(() => ({
        left: 100,
        top: 100,
        right: 200,
        bottom: 140,
        width: 100,
        height: 40
      }));

      contextualHelp.container.getBoundingClientRect = jest.fn(() => ({
        width: 200,
        height: 100
      }));

      contextualHelp.show(element, 'package-install', { position: 'bottom' });

      expect(contextualHelp.container.style.transform).toContain('translate');
      expect(contextualHelp.container.getAttribute('data-position')).toBe('bottom');
    });
  });

  describe('Event Handling', () => {
    test('should show tooltip on mouse enter after delay', async () => {
      document.body.innerHTML = '<button class="test-btn">Test</button>';
      const btn = document.querySelector('.test-btn');
      
      contextualHelp.register('.test-btn', 'package-install');

      const mouseEnterEvent = new window.MouseEvent('mouseenter', {
        bubbles: true,
        target: btn
      });

      btn.dispatchEvent(mouseEnterEvent);

      // Should not show immediately
      expect(contextualHelp.activeTooltip).toBeNull();

      // Wait for delay
      await new Promise(resolve => setTimeout(resolve, 600));

      expect(contextualHelp.activeTooltip).toBeTruthy();
    });

    test('should cancel show on mouse leave', async () => {
      document.body.innerHTML = '<button class="test-btn">Test</button>';
      const btn = document.querySelector('.test-btn');
      
      contextualHelp.register('.test-btn', 'package-install');

      btn.dispatchEvent(new window.MouseEvent('mouseenter', { bubbles: true }));
      
      // Leave before delay
      await new Promise(resolve => setTimeout(resolve, 100));
      btn.dispatchEvent(new window.MouseEvent('mouseleave', { bubbles: true }));

      // Wait for original delay
      await new Promise(resolve => setTimeout(resolve, 500));

      expect(contextualHelp.activeTooltip).toBeNull();
    });

    test('should show tooltip on focus', () => {
      document.body.innerHTML = '<input class="test-input" />';
      const input = document.querySelector('.test-input');
      
      contextualHelp.register('.test-input', 'package-search');

      input.dispatchEvent(new window.FocusEvent('focus', { bubbles: true }));

      expect(contextualHelp.activeTooltip).toBeTruthy();
    });

    test('should hide tooltip on blur', () => {
      document.body.innerHTML = '<input class="test-input" />';
      const input = document.querySelector('.test-input');
      
      contextualHelp.register('.test-input', 'package-search');

      input.dispatchEvent(new window.FocusEvent('focus', { bubbles: true }));
      input.dispatchEvent(new window.FocusEvent('blur', { bubbles: true }));

      expect(contextualHelp.activeTooltip).toBeNull();
    });

    test('should hide tooltip on escape key', () => {
      const element = document.createElement('button');
      document.body.appendChild(element);

      contextualHelp.show(element, 'package-install');
      
      document.dispatchEvent(new window.KeyboardEvent('keydown', {
        key: 'Escape',
        bubbles: true
      }));

      expect(contextualHelp.activeTooltip).toBeNull();
    });
  });

  describe('Tooltip Content', () => {
    test('should build complete tooltip content', () => {
      const helpContent = {
        title: 'Test Title',
        content: 'Test content',
        tips: ['Tip 1', 'Tip 2'],
        warnings: ['Warning 1'],
        shortcuts: [
          { key: 'Ctrl+S', description: 'Save' }
        ],
        related: ['package-remove']
      };

      const html = contextualHelp.buildTooltipContent(helpContent);

      expect(html).toContain('Test Title');
      expect(html).toContain('Test content');
      expect(html).toContain('Tip 1');
      expect(html).toContain('Warning 1');
      expect(html).toContain('Ctrl+S');
      expect(html).toContain('data-help-id="package-remove"');
    });

    test('should handle partial content', () => {
      const helpContent = {
        content: 'Just some text'
      };

      const html = contextualHelp.buildTooltipContent(helpContent);

      expect(html).toContain('Just some text');
      expect(html).not.toContain('tooltip-title');
      expect(html).not.toContain('tooltip-tips');
    });
  });

  describe('Preferences', () => {
    test('should save preferences', () => {
      contextualHelp.options.theme = 'light';
      contextualHelp.options.animations = false;
      
      contextualHelp.savePreferences();

      const saved = JSON.parse(localStorage.getItem('contextual-help-prefs'));
      expect(saved.theme).toBe('light');
      expect(saved.animations).toBe(false);
    });

    test('should load preferences on init', () => {
      localStorage.setItem('contextual-help-prefs', JSON.stringify({
        theme: 'light',
        delay: 1000
      }));

      const newHelp = new ContextualHelp();
      
      expect(newHelp.options.theme).toBe('light');
      expect(newHelp.options.delay).toBe(1000);
    });
  });
});

describe('TourManager', () => {
  let contextualHelp;
  let tourManager;

  beforeEach(() => {
    document.body.innerHTML = `
      <div class="dashboard">Dashboard</div>
      <button data-page="packages">Packages</button>
      <button data-page="services">Services</button>
    `;
    localStorage.clear();
    contextualHelp = new ContextualHelp();
    tourManager = contextualHelp.tourManager;
  });

  afterEach(() => {
    if (tourManager.overlay) {
      tourManager.overlay.remove();
    }
  });

  test('should start tour', () => {
    tourManager.start('first-time');

    expect(tourManager.currentTour).toBeTruthy();
    expect(tourManager.currentStep).toBe(0);
    expect(document.querySelector('.tour-overlay')).toBeTruthy();
    expect(document.querySelector('.tour-tooltip')).toBeTruthy();
  });

  test('should show tour step', () => {
    tourManager.start('first-time');

    const tooltip = document.querySelector('.tour-tooltip');
    expect(tooltip.textContent).toContain('Dashboard Overview');
    expect(tooltip.textContent).toContain('1 / 5');
  });

  test('should navigate between steps', () => {
    tourManager.start('first-time');

    // Go to next step
    const nextBtn = document.querySelector('.tour-next');
    nextBtn.click();

    expect(tourManager.currentStep).toBe(1);
    const tooltip = document.querySelector('.tour-tooltip');
    expect(tooltip.textContent).toContain('Package Management');
  });

  test('should skip tour', () => {
    tourManager.start('first-time');

    const skipBtn = document.querySelector('.tour-skip');
    skipBtn.click();

    expect(tourManager.currentTour).toBeNull();
    expect(document.querySelector('.tour-overlay')).toBeNull();
  });

  test('should mark tour as completed', () => {
    tourManager.start('first-time');
    tourManager.end();

    const completed = JSON.parse(localStorage.getItem('completed-tours') || '[]');
    expect(completed).toContain('Welcome to NixOS GUI');
  });
});

describe('ShortcutHelper', () => {
  let contextualHelp;
  let shortcuts;

  beforeEach(() => {
    document.body.innerHTML = '';
    contextualHelp = new ContextualHelp();
    shortcuts = contextualHelp.shortcuts;
  });

  test('should register shortcuts', () => {
    shortcuts.register('ctrl+k', 'Test shortcut', jest.fn());
    
    expect(shortcuts.shortcuts.has('ctrl+k')).toBe(true);
    expect(shortcuts.shortcuts.get('ctrl+k').description).toBe('Test shortcut');
  });

  test('should handle keyboard shortcuts', () => {
    const handler = jest.fn();
    shortcuts.register('ctrl+s', 'Save', handler);

    const event = new window.KeyboardEvent('keydown', {
      key: 's',
      ctrlKey: true,
      bubbles: true
    });

    shortcuts.handleKeydown(event);

    expect(handler).toHaveBeenCalledWith(event);
  });

  test('should show cheatsheet', () => {
    shortcuts.toggleCheatsheet();

    const cheatsheet = document.querySelector('.shortcut-cheatsheet');
    expect(cheatsheet.classList.contains('visible')).toBe(true);
    expect(shortcuts.cheatsheetVisible).toBe(true);
  });

  test('should hide cheatsheet on toggle', () => {
    shortcuts.toggleCheatsheet(); // Show
    shortcuts.toggleCheatsheet(); // Hide

    const cheatsheet = document.querySelector('.shortcut-cheatsheet');
    expect(cheatsheet.classList.contains('visible')).toBe(false);
    expect(shortcuts.cheatsheetVisible).toBe(false);
  });

  test('should build cheatsheet content', () => {
    const html = shortcuts.buildCheatsheetContent();

    expect(html).toContain('Keyboard Shortcuts');
    expect(html).toContain('Global');
    expect(html).toContain('<kbd>/</kbd>');
    expect(html).toContain('Focus search');
  });

  test('should check context correctly', () => {
    // Mock location hash
    Object.defineProperty(window, 'location', {
      value: { hash: '#/packages' },
      writable: true
    });

    expect(shortcuts.isInContext('packages')).toBe(true);
    expect(shortcuts.isInContext('services')).toBe(false);
  });
});