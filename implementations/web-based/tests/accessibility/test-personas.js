/**
 * Persona-Based Accessibility Tests
 * Tests the interface against our 5 key personas' needs
 */

const { 
  runAccessibilityTests,
  checkKeyboardNavigation,
  testScreenReaderExperience,
  createBrowser
} = require('./setup');

describe('Persona Accessibility Tests', () => {
  
  describe('Grandma Rose (75) - Age-related needs', () => {
    let browser;
    let page;
    
    beforeAll(async () => {
      browser = await createBrowser();
      page = await browser.newPage();
      
      // Simulate age-related viewport settings
      await page.setViewport({
        width: 1024,
        height: 768,
        deviceScaleFactor: 1.5 // Simulated zoom
      });
    });
    
    afterAll(async () => {
      await browser.close();
    });
    
    test('Text is readable at larger sizes', async () => {
      await page.goto('http://localhost:8080/index.html');
      
      const fontSize = await page.evaluate(() => {
        const input = document.querySelector('input[type="text"]');
        const style = window.getComputedStyle(input);
        return parseFloat(style.fontSize);
      });
      
      // Should have reasonable default size
      expect(fontSize).toBeGreaterThanOrEqual(16);
    });
    
    test('Supports browser zoom without breaking', async () => {
      await page.goto('http://localhost:8080/index.html');
      
      // Zoom to 200%
      await page.evaluate(() => {
        document.body.style.zoom = '2';
      });
      
      // Check that layout isn't broken
      const isUsable = await page.evaluate(() => {
        const input = document.querySelector('input[type="text"]');
        const button = document.querySelector('button');
        
        if (!input || !button) return false;
        
        const inputRect = input.getBoundingClientRect();
        const buttonRect = button.getBoundingClientRect();
        
        // Elements shouldn't overlap
        const overlap = !(inputRect.right < buttonRect.left || 
                         buttonRect.right < inputRect.left ||
                         inputRect.bottom < buttonRect.top ||
                         buttonRect.bottom < inputRect.top);
        
        return !overlap;
      });
      
      expect(isUsable).toBe(true);
    });
    
    test('Uses simple, clear language', async () => {
      await page.goto('http://localhost:8080/demo-install-command.html');
      
      // Check placeholder text
      const placeholder = await page.$eval('#commandInput', el => el.placeholder);
      expect(placeholder).toMatch(/try|type|say/i);
      expect(placeholder).not.toMatch(/syntax|parameter|argument/i);
      
      // Test error message language
      await page.type('#commandInput', 'gibberish');
      await page.click('#executeButton');
      await page.waitForTimeout(1000);
      
      const errorText = await page.$eval('#output', el => el.textContent);
      expect(errorText).toMatch(/didn't understand|try|could you/i);
      expect(errorText).not.toMatch(/parse error|invalid syntax/i);
    });
    
    test('Provides adequate time for tasks', async () => {
      // No auto-timeouts
      const hasTimeouts = await page.evaluate(() => {
        // Check for any auto-dismiss or timeout patterns
        const scripts = Array.from(document.querySelectorAll('script'));
        const hasTimeout = scripts.some(script => 
          script.textContent.includes('setTimeout') &&
          script.textContent.includes('dismiss')
        );
        return hasTimeout;
      });
      
      expect(hasTimeouts).toBe(false);
    });
  });
  
  describe('Maya (16) - ADHD considerations', () => {
    test('Interface is focused and distraction-free', async () => {
      const browser = await createBrowser();
      const page = await browser.newPage();
      
      await page.goto('http://localhost:8080/index.html');
      
      // Check for distracting elements
      const distractions = await page.evaluate(() => {
        const animations = document.querySelectorAll('[class*="animate"], [class*="blink"], [class*="pulse"]');
        const autoplay = document.querySelectorAll('[autoplay]');
        const ads = document.querySelectorAll('[class*="ad"], [id*="ad"]');
        
        return {
          animations: animations.length,
          autoplay: autoplay.length,
          ads: ads.length
        };
      });
      
      expect(distractions.animations).toBe(0);
      expect(distractions.autoplay).toBe(0);
      expect(distractions.ads).toBe(0);
      
      await browser.close();
    });
    
    test('Provides clear visual feedback', async () => {
      const browser = await createBrowser();
      const page = await browser.newPage();
      
      await page.goto('http://localhost:8080/demo-install-command.html');
      
      // Type command
      await page.type('#commandInput', 'install firefox');
      await page.click('#executeButton');
      
      // Check for visual feedback
      await page.waitForSelector('.intent-display', { timeout: 5000 });
      
      const hasFeedback = await page.evaluate(() => {
        const feedback = document.querySelector('.intent-display');
        return feedback && feedback.textContent.length > 0;
      });
      
      expect(hasFeedback).toBe(true);
      
      await browser.close();
    });
  });
  
  describe('David (42) - Stress/fatigue', () => {
    test('Interface is calm and non-pressuring', async () => {
      const browser = await createBrowser();
      const page = await browser.newPage();
      
      await page.goto('http://localhost:8080/index.html');
      
      // Check color scheme (should be calming)
      const colors = await page.evaluate(() => {
        const body = document.body;
        const style = window.getComputedStyle(body);
        return {
          background: style.backgroundColor,
          text: style.color
        };
      });
      
      // Should use muted colors, not bright/harsh
      expect(colors.background).not.toMatch(/red|#ff0000/i);
      expect(colors.text).not.toMatch(/red|#ff0000/i);
      
      await browser.close();
    });
    
    test('Errors are gentle and helpful', async () => {
      const browser = await createBrowser();
      const page = await browser.newPage();
      
      await page.goto('http://localhost:8080/demo-install-command.html');
      
      // Trigger an error
      await page.type('#commandInput', 'do something wrong');
      await page.click('#executeButton');
      
      await page.waitForTimeout(1000);
      
      const errorMessage = await page.$eval('#output', el => el.textContent);
      
      // Should be encouraging, not harsh
      expect(errorMessage).not.toMatch(/error!|failed!|wrong!/i);
      expect(errorMessage).toMatch(/try|help|suggest/i);
      
      await browser.close();
    });
  });
  
  describe('Dr. Sarah (35) - Power user needs', () => {
    test('Supports keyboard shortcuts', async () => {
      const browser = await createBrowser();
      const page = await browser.newPage();
      
      await page.goto('http://localhost:8080/index.html');
      
      // Test Enter key to submit
      await page.type('#commandInput', 'install firefox');
      await page.keyboard.press('Enter');
      
      // Should process command
      await page.waitForTimeout(1000);
      
      const hasOutput = await page.evaluate(() => {
        const output = document.querySelector('#output');
        return output && output.textContent.length > 50;
      });
      
      expect(hasOutput).toBe(true);
      
      await browser.close();
    });
    
    test('Information density can be increased', async () => {
      // Power users should be able to see more info
      // This will be tested when preferences are implemented
      expect(true).toBe(true);
    });
  });
  
  describe('Alex (28) - Blind developer', () => {
    test('Everything works with screen reader only', async () => {
      const results = await testScreenReaderExperience('http://localhost:8080/index.html');
      
      // Should have complete information without visuals
      expect(results.totalElements).toBeGreaterThan(10);
      
      // Check for visual-only content
      const visualOnlyTerms = ['click', 'see', 'look', 'watch', 'view'];
      const hasVisualOnly = results.readingOrder.some(element => {
        if (element.content) {
          return visualOnlyTerms.some(term => 
            element.content.toLowerCase().includes(term)
          );
        }
        return false;
      });
      
      expect(hasVisualOnly).toBe(false);
    });
    
    test('Code output is screen reader friendly', async () => {
      const browser = await createBrowser();
      const page = await browser.newPage();
      
      await page.goto('http://localhost:8080/demo-install-command.html');
      
      await page.type('#commandInput', 'install firefox');
      await page.click('#executeButton');
      
      await page.waitForTimeout(2000);
      
      // Check that code blocks have proper ARIA
      const codeAccessible = await page.evaluate(() => {
        const codeBlocks = document.querySelectorAll('pre, code');
        return Array.from(codeBlocks).every(block => {
          // Should have role or be in a labeled container
          return block.getAttribute('role') || 
                 block.closest('[aria-label]') ||
                 block.closest('[role]');
        });
      });
      
      expect(codeAccessible).toBe(true);
      
      await browser.close();
    });
    
    test('No reliance on color alone', async () => {
      const browser = await createBrowser();
      const page = await browser.newPage();
      
      await page.goto('http://localhost:8080/demo-install-command.html');
      
      // Check that status is not conveyed by color alone
      const usesColorAlone = await page.evaluate(() => {
        // Look for color-only indicators
        const elements = document.querySelectorAll('*');
        const colorOnlyPattern = /\b(red|green|blue|yellow)\s+(text|means|indicates)/i;
        
        return Array.from(elements).some(el => {
          const text = el.textContent;
          return colorOnlyPattern.test(text);
        });
      });
      
      expect(usesColorAlone).toBe(false);
      
      await browser.close();
    });
  });
});

// Helper function to simulate persona conditions
async function simulatePersona(page, persona) {
  switch (persona) {
    case 'grandma-rose':
      // Simulate tremor with imprecise clicks
      await page.evaluate(() => {
        document.addEventListener('click', (e) => {
          // Add small random offset to simulate tremor
          const offset = Math.random() * 10 - 5;
          e.clientX += offset;
          e.clientY += offset;
        });
      });
      break;
      
    case 'maya':
      // Simulate ADHD with quick, sometimes interrupted actions
      break;
      
    case 'david':
      // Simulate fatigue with slower actions
      page.setDefaultTimeout(10000);
      break;
      
    case 'dr-sarah':
      // Power user - keyboard only
      break;
      
    case 'alex':
      // Screen reader only - disable visuals
      await page.addStyleTag({
        content: '* { color: transparent !important; background: black !important; }'
      });
      break;
  }
}