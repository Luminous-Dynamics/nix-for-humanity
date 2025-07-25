/**
 * Accessibility Testing Setup
 * Configures axe-core and other a11y testing tools
 */

const { AxePuppeteer } = require('@axe-core/puppeteer');
const puppeteer = require('puppeteer');

/**
 * Create browser instance for testing
 */
async function createBrowser() {
  return await puppeteer.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage'
    ]
  });
}

/**
 * Run accessibility tests on a page
 */
async function runAccessibilityTests(url) {
  const browser = await createBrowser();
  const page = await browser.newPage();
  
  try {
    await page.goto(url, { waitUntil: 'networkidle2' });
    
    // Run axe accessibility tests
    const results = await new AxePuppeteer(page)
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze();
    
    await browser.close();
    return results;
  } catch (error) {
    await browser.close();
    throw error;
  }
}

/**
 * Format violations for readable output
 */
function formatViolations(violations) {
  if (!violations || violations.length === 0) {
    return 'No accessibility violations found! ✅';
  }
  
  return violations.map(violation => {
    const impact = violation.impact.toUpperCase();
    const elements = violation.nodes.length;
    
    return `
${impact} - ${violation.description}
Rule: ${violation.id}
Help: ${violation.help}
Affected elements: ${elements}
${violation.nodes.map(node => `  - ${node.target.join(' ')}`).join('\n')}
    `.trim();
  }).join('\n\n');
}

/**
 * Check keyboard navigation
 */
async function checkKeyboardNavigation(url) {
  const browser = await createBrowser();
  const page = await browser.newPage();
  
  try {
    await page.goto(url, { waitUntil: 'networkidle2' });
    
    // Track focus order
    const focusOrder = [];
    
    // Tab through all focusable elements
    let previousActiveElement = null;
    let tabCount = 0;
    const maxTabs = 50; // Prevent infinite loops
    
    while (tabCount < maxTabs) {
      await page.keyboard.press('Tab');
      
      const activeElement = await page.evaluate(() => {
        const el = document.activeElement;
        if (!el) return null;
        
        return {
          tagName: el.tagName,
          id: el.id,
          className: el.className,
          text: el.textContent?.trim().substring(0, 50),
          ariaLabel: el.getAttribute('aria-label'),
          role: el.getAttribute('role'),
          href: el.href,
          type: el.type
        };
      });
      
      // Check if we've cycled back to the start
      if (previousActiveElement && 
          JSON.stringify(activeElement) === JSON.stringify(previousActiveElement)) {
        break;
      }
      
      if (activeElement) {
        focusOrder.push(activeElement);
      }
      
      previousActiveElement = activeElement;
      tabCount++;
    }
    
    await browser.close();
    
    return {
      focusableElements: focusOrder.length,
      focusOrder: focusOrder,
      hasKeyboardTrap: tabCount >= maxTabs
    };
  } catch (error) {
    await browser.close();
    throw error;
  }
}

/**
 * Test with screen reader simulation
 */
async function testScreenReaderExperience(url) {
  const browser = await createBrowser();
  const page = await browser.newPage();
  
  try {
    await page.goto(url, { waitUntil: 'networkidle2' });
    
    // Get all text content in reading order
    const readingOrder = await page.evaluate(() => {
      const elements = [];
      const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT,
        {
          acceptNode: (node) => {
            // Skip hidden elements
            if (node.nodeType === Node.ELEMENT_NODE) {
              const style = window.getComputedStyle(node);
              if (style.display === 'none' || style.visibility === 'hidden') {
                return NodeFilter.FILTER_REJECT;
              }
            }
            
            // Skip empty text nodes
            if (node.nodeType === Node.TEXT_NODE && !node.textContent.trim()) {
              return NodeFilter.FILTER_REJECT;
            }
            
            return NodeFilter.FILTER_ACCEPT;
          }
        }
      );
      
      let node;
      while (node = walker.nextNode()) {
        if (node.nodeType === Node.TEXT_NODE) {
          elements.push({
            type: 'text',
            content: node.textContent.trim()
          });
        } else if (node.nodeType === Node.ELEMENT_NODE) {
          const tagName = node.tagName.toLowerCase();
          const ariaLabel = node.getAttribute('aria-label');
          const role = node.getAttribute('role');
          
          if (ariaLabel || role || ['button', 'a', 'input', 'select', 'textarea'].includes(tagName)) {
            elements.push({
              type: 'interactive',
              tagName: tagName,
              ariaLabel: ariaLabel,
              role: role,
              text: node.textContent.trim().substring(0, 50)
            });
          }
        }
      }
      
      return elements;
    });
    
    // Check for ARIA live regions
    const liveRegions = await page.evaluate(() => {
      const regions = [];
      const liveElements = document.querySelectorAll('[aria-live]');
      
      liveElements.forEach(el => {
        regions.push({
          ariaLive: el.getAttribute('aria-live'),
          role: el.getAttribute('role'),
          text: el.textContent.trim()
        });
      });
      
      return regions;
    });
    
    await browser.close();
    
    return {
      readingOrder: readingOrder,
      liveRegions: liveRegions,
      totalElements: readingOrder.length
    };
  } catch (error) {
    await browser.close();
    throw error;
  }
}

module.exports = {
  createBrowser,
  runAccessibilityTests,
  formatViolations,
  checkKeyboardNavigation,
  testScreenReaderExperience
};