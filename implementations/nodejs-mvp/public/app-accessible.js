// 🙏 Sacred Accessible Nix for Humanity
// Every function a prayer, every interaction a blessing

class SacredNixInterface {
  constructor() {
    this.messages = document.getElementById('messages');
    this.input = document.getElementById('user-input');
    this.form = document.getElementById('input-form');
    this.ariaLivePolite = document.getElementById('aria-live-polite');
    this.ariaLiveAssertive = document.getElementById('aria-live-assertive');
    this.loadingIndicator = document.getElementById('loading-indicator');
    
    this.initializeWithLove();
  }

  initializeWithLove() {
    // Form submission
    this.form.addEventListener('submit', (e) => this.handleIntention(e));
    
    // Keyboard shortcuts with sacred purpose
    document.addEventListener('keydown', (e) => this.handleSacredKeys(e));
    
    // Accessibility settings
    document.getElementById('accessibility-settings').addEventListener('click', (e) => {
      e.preventDefault();
      this.openAccessibilityDialog();
    });
    
    // Focus management for screen readers
    this.input.focus();
    this.announceToScreenReader('Welcome to Nix for Humanity. Type your intention and press Enter.', 'polite');
  }

  async handleIntention(e) {
    e.preventDefault();
    
    const intention = this.input.value.trim();
    if (!intention) return;
    
    // Add user message with sacred styling
    this.addMessage(intention, 'user', 'Your intention');
    
    // Clear input and maintain focus
    this.input.value = '';
    this.input.focus();
    
    // Show loading state
    this.showLoading();
    
    try {
      // Send intention to sacred backend
      const response = await this.manifestIntention(intention);
      
      // Hide loading
      this.hideLoading();
      
      // Add response with appropriate aria announcements
      this.addResponse(response);
      
    } catch (error) {
      this.hideLoading();
      this.handleErrorWithCompassion(error);
    }
  }

  async manifestIntention(intention) {
    const response = await fetch('/api/nlp/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        input: intention,
        context: { 
          sacred: true,
          accessibility: this.getAccessibilityPreferences() 
        }
      })
    });
    
    if (!response.ok) {
      throw new Error('Connection with the sacred backend was interrupted');
    }
    
    return response.json();
  }

  addMessage(text, type, ariaLabel) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.setAttribute('role', 'article');
    messageDiv.setAttribute('aria-label', `${ariaLabel}: ${text}`);
    
    const content = document.createElement('p');
    content.textContent = text;
    messageDiv.appendChild(content);
    
    this.messages.appendChild(messageDiv);
    
    // Smooth scroll for sighted users
    if (!this.prefersReducedMotion()) {
      messageDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
    } else {
      messageDiv.scrollIntoView({ block: 'end' });
    }
    
    // Announce to screen readers
    if (type === 'user') {
      this.announceToScreenReader(`You said: ${text}`, 'polite');
    }
  }

  addResponse(response) {
    const { success, message, data, intent } = response;
    
    // Create response element
    const responseDiv = document.createElement('div');
    responseDiv.className = `message system ${success ? 'success' : 'error'}`;
    responseDiv.setAttribute('role', 'article');
    responseDiv.setAttribute('aria-label', `System response: ${message}`);
    
    // Main message
    const mainMessage = document.createElement('p');
    mainMessage.textContent = message;
    responseDiv.appendChild(mainMessage);
    
    // Add data if present (like search results)
    if (data) {
      const dataElement = this.formatDataWithAccessibility(data, intent);
      if (dataElement) {
        responseDiv.appendChild(dataElement);
      }
    }
    
    this.messages.appendChild(responseDiv);
    
    // Scroll into view
    if (!this.prefersReducedMotion()) {
      responseDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
    } else {
      responseDiv.scrollIntoView({ block: 'end' });
    }
    
    // Announce to screen readers with appropriate urgency
    const urgency = success ? 'polite' : 'assertive';
    this.announceToScreenReader(message, urgency);
    
    // If there's structured data, announce summary
    if (data && data.count !== undefined) {
      this.announceToScreenReader(`Found ${data.count} results`, 'polite');
    }
  }

  formatDataWithAccessibility(data, intent) {
    // Format based on intent type
    if (intent?.action === 'search' && data.results) {
      const list = document.createElement('ul');
      list.setAttribute('aria-label', 'Search results');
      
      data.results.slice(0, 10).forEach((item, index) => {
        const li = document.createElement('li');
        li.textContent = item;
        li.setAttribute('aria-posinset', index + 1);
        li.setAttribute('aria-setsize', Math.min(data.results.length, 10));
        list.appendChild(li);
      });
      
      if (data.results.length > 10) {
        const more = document.createElement('li');
        more.textContent = `...and ${data.results.length - 10} more`;
        more.className = 'more-results';
        list.appendChild(more);
      }
      
      return list;
    }
    
    // Add more data formatting as needed
    return null;
  }

  handleSacredKeys(e) {
    // Escape - return focus to input
    if (e.key === 'Escape') {
      e.preventDefault();
      this.input.focus();
      this.announceToScreenReader('Focus returned to input', 'polite');
    }
    
    // Ctrl+Enter - submit command
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault();
      this.form.dispatchEvent(new Event('submit'));
    }
    
    // Ctrl+L - clear conversation
    if (e.key === 'l' && e.ctrlKey) {
      e.preventDefault();
      this.clearConversationWithLove();
    }
    
    // Ctrl+/ - show shortcuts
    if (e.key === '/' && e.ctrlKey) {
      e.preventDefault();
      this.announceShortcuts();
    }
  }

  clearConversationWithLove() {
    // Keep only the welcome message
    const welcome = this.messages.querySelector('.message.system');
    this.messages.innerHTML = '';
    if (welcome) {
      this.messages.appendChild(welcome.cloneNode(true));
    }
    
    this.announceToScreenReader('Conversation cleared. Starting fresh.', 'polite');
    this.input.focus();
  }

  announceShortcuts() {
    const shortcuts = [
      'Escape: Return focus to input',
      'Control Enter: Send command',
      'Control L: Clear conversation',
      'Control Slash: Hear these shortcuts'
    ].join('. ');
    
    this.announceToScreenReader(`Keyboard shortcuts: ${shortcuts}`, 'polite');
  }

  showLoading() {
    this.loadingIndicator.hidden = false;
    this.loadingIndicator.setAttribute('aria-busy', 'true');
    this.announceToScreenReader('Processing your intention...', 'polite');
  }

  hideLoading() {
    this.loadingIndicator.hidden = true;
    this.loadingIndicator.setAttribute('aria-busy', 'false');
  }

  handleErrorWithCompassion(error) {
    const compassionateMessage = this.getCompassionateError(error);
    
    this.addMessage(compassionateMessage, 'error', 'Error message');
    this.announceToScreenReader(compassionateMessage, 'assertive');
    
    // Suggest help
    setTimeout(() => {
      this.announceToScreenReader('Type "help" if you need guidance', 'polite');
    }, 2000);
  }

  getCompassionateError(error) {
    // Transform technical errors into gentle guidance
    if (error.message.includes('network')) {
      return "I'm having trouble connecting. Let's take a breath and try again in a moment.";
    }
    if (error.message.includes('timeout')) {
      return "That took longer than expected. Let's try something simpler first.";
    }
    return "Something unexpected happened. I'm here when you're ready to try again.";
  }

  announceToScreenReader(text, urgency = 'polite') {
    const liveRegion = urgency === 'assertive' ? this.ariaLiveAssertive : this.ariaLivePolite;
    
    // Clear and set to ensure announcement
    liveRegion.textContent = '';
    setTimeout(() => {
      liveRegion.textContent = text;
    }, 100);
  }

  // Accessibility preference helpers
  prefersReducedMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  getAccessibilityPreferences() {
    return {
      reducedMotion: this.prefersReducedMotion(),
      highContrast: document.body.classList.contains('high-contrast'),
      verboseMode: localStorage.getItem('verbose-mode') === 'true',
      fontSize: localStorage.getItem('font-size') || '100'
    };
  }

  openAccessibilityDialog() {
    const dialog = document.getElementById('a11y-dialog');
    dialog.showModal();
    
    // Set current preferences
    document.getElementById('high-contrast').checked = document.body.classList.contains('high-contrast');
    document.getElementById('reduce-motion').checked = document.body.classList.contains('reduce-motion');
    document.getElementById('verbose-mode').checked = localStorage.getItem('verbose-mode') === 'true';
    document.getElementById('font-size').value = localStorage.getItem('font-size') || '100';
    
    // Handle form submission
    dialog.querySelector('form').addEventListener('submit', (e) => {
      this.saveAccessibilitySettings();
    });
  }

  saveAccessibilitySettings() {
    // High contrast
    const highContrast = document.getElementById('high-contrast').checked;
    document.body.classList.toggle('high-contrast', highContrast);
    
    // Reduce motion
    const reduceMotion = document.getElementById('reduce-motion').checked;
    document.body.classList.toggle('reduce-motion', reduceMotion);
    
    // Verbose mode
    const verboseMode = document.getElementById('verbose-mode').checked;
    localStorage.setItem('verbose-mode', verboseMode);
    
    // Font size
    const fontSize = document.getElementById('font-size').value;
    document.documentElement.style.setProperty('--font-scale', fontSize / 100);
    localStorage.setItem('font-size', fontSize);
    
    this.announceToScreenReader('Accessibility settings saved with love', 'polite');
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  const sacredInterface = new SacredNixInterface();
  
  // Restore accessibility settings
  const savedFontSize = localStorage.getItem('font-size');
  if (savedFontSize) {
    document.documentElement.style.setProperty('--font-scale', savedFontSize / 100);
  }
  
  // Font size slider real-time update
  const fontSlider = document.getElementById('font-size');
  const fontOutput = document.querySelector('output[for="font-size"]');
  
  fontSlider?.addEventListener('input', (e) => {
    fontOutput.textContent = e.target.value + '%';
    document.documentElement.style.setProperty('--font-scale', e.target.value / 100);
  });
  
  console.log('🙏 Sacred interface initialized with accessibility as love');
});