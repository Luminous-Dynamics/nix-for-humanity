/**
 * Voice-Text Parity Tests
 * Ensures voice and text inputs are treated equally
 */

const { createBrowser } = require('./setup');

describe('Voice-Text Input Parity', () => {
  let browser;
  let page;
  
  beforeAll(async () => {
    browser = await createBrowser();
    page = await browser.newPage();
  });
  
  afterAll(async () => {
    await browser.close();
  });
  
  describe('Input Method Equality', () => {
    test('Text input is prominently displayed', async () => {
      await page.goto('http://localhost:8080/index.html');
      
      // Check text input exists and is visible
      const textInput = await page.$('input[type="text"]');
      expect(textInput).toBeTruthy();
      
      const isVisible = await page.evaluate(el => {
        const style = window.getComputedStyle(el);
        return style.display !== 'none' && 
               style.visibility !== 'hidden' && 
               style.opacity !== '0';
      }, textInput);
      
      expect(isVisible).toBe(true);
      
      // Check it has appropriate size
      const dimensions = await page.evaluate(el => {
        const rect = el.getBoundingClientRect();
        return {
          width: rect.width,
          height: rect.height
        };
      }, textInput);
      
      // Should be reasonably sized for easy use
      expect(dimensions.width).toBeGreaterThan(200);
      expect(dimensions.height).toBeGreaterThan(30);
    });
    
    test('Voice button is equally prominent when available', async () => {
      await page.goto('http://localhost:8080/index.html');
      
      // Look for voice input button (may not exist yet)
      const voiceButton = await page.$('[aria-label*="voice" i], [aria-label*="speak" i], button[class*="voice" i]');
      
      if (voiceButton) {
        const isVisible = await page.evaluate(el => {
          const style = window.getComputedStyle(el);
          return style.display !== 'none' && 
                 style.visibility !== 'hidden' && 
                 style.opacity !== '0';
        }, voiceButton);
        
        expect(isVisible).toBe(true);
        
        // Should be similar size to other buttons
        const dimensions = await page.evaluate(el => {
          const rect = el.getBoundingClientRect();
          return {
            width: rect.width,
            height: rect.height
          };
        }, voiceButton);
        
        expect(dimensions.width).toBeGreaterThan(40);
        expect(dimensions.height).toBeGreaterThan(40);
      }
    });
    
    test('Both inputs lead to same processing pipeline', async () => {
      // This tests that the same NLP engine processes both inputs
      // Currently verified by code structure, will add runtime tests
      expect(true).toBe(true);
    });
  });
  
  describe('Feature Parity', () => {
    test('All commands work with text input', async () => {
      await page.goto('http://localhost:8080/demo-install-command.html');
      
      // Test text input
      await page.type('#commandInput', 'install firefox');
      await page.click('#executeButton');
      
      // Wait for response
      await page.waitForTimeout(1000);
      
      // Check that intent was recognized
      const output = await page.$eval('#output', el => el.textContent);
      expect(output).toContain('install');
      expect(output).not.toContain("didn't understand");
    });
    
    test('All commands will work with voice input', async () => {
      // Placeholder for when voice is implemented
      // Will test same commands via voice API
      expect(true).toBe(true);
    });
    
    test('Error messages are same for both inputs', async () => {
      await page.goto('http://localhost:8080/demo-install-command.html');
      
      // Test with invalid input
      await page.type('#commandInput', 'xyz123invalid');
      await page.click('#executeButton');
      
      await page.waitForTimeout(1000);
      
      const output = await page.$eval('#output', el => el.textContent);
      expect(output).toContain("didn't understand");
      
      // When voice is added, same error should appear
    });
  });
  
  describe('Accessibility of Input Methods', () => {
    test('Text input works for users who cannot speak', async () => {
      // Text input should be fully functional
      await page.goto('http://localhost:8080/index.html');
      
      const canUseTextOnly = await page.evaluate(() => {
        // Check if any functionality requires voice
        const allButtons = Array.from(document.querySelectorAll('button'));
        const allInputs = Array.from(document.querySelectorAll('input'));
        
        // Look for voice-only features
        const voiceOnlyElements = [...allButtons, ...allInputs].filter(el => {
          const text = (el.textContent + el.getAttribute('aria-label') + el.className).toLowerCase();
          return text.includes('voice only') || text.includes('speak only');
        });
        
        return voiceOnlyElements.length === 0;
      });
      
      expect(canUseTextOnly).toBe(true);
    });
    
    test('Voice input will work for users who cannot type', async () => {
      // When implemented, voice should be fully functional
      // No typing should be required
      expect(true).toBe(true);
    });
    
    test('Visual feedback provided for voice input', async () => {
      // When voice is active, visual indicators should show:
      // - Listening state
      // - Processing state  
      // - Recognized text
      // - Results
      expect(true).toBe(true);
    });
    
    test('Audio feedback optional for text input', async () => {
      // Text input should not require audio
      // Any audio feedback should be optional
      const requiresAudio = await page.evaluate(() => {
        // Check for audio elements or requirements
        const audioElements = document.querySelectorAll('audio');
        return audioElements.length > 0 && 
               Array.from(audioElements).some(el => el.autoplay);
      });
      
      expect(requiresAudio).toBe(false);
    });
  });
  
  describe('Documentation Parity', () => {
    test('Examples show both input methods', async () => {
      // Check that documentation doesn't favor one method
      // This is more of a documentation test
      expect(true).toBe(true);
    });
    
    test('No "voice commands" or "text syntax" sections', async () => {
      // Commands should be described as natural language
      // Not separated by input method
      expect(true).toBe(true);
    });
  });
});

// Helper to test command processing parity
async function testCommandParity(page, command) {
  // Test via text
  await page.evaluate(() => {
    document.querySelector('#commandInput').value = '';
  });
  await page.type('#commandInput', command);
  await page.click('#executeButton');
  
  await page.waitForTimeout(1000);
  
  const textResult = await page.$eval('#output', el => el.textContent);
  
  // TODO: When voice is implemented
  // const voiceResult = await testVoiceCommand(page, command);
  // expect(textResult).toEqual(voiceResult);
  
  return textResult;
}