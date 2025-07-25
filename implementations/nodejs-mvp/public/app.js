// 🌟 Nix for Humanity - Client-side JavaScript

class NixForHumanity {
  constructor() {
    this.messagesEl = document.getElementById('messages');
    this.inputEl = document.getElementById('user-input');
    this.formEl = document.getElementById('input-form');
    
    this.formEl.addEventListener('submit', (e) => this.handleSubmit(e));
    
    // Load any saved session
    this.sessionId = this.getSessionId();
  }

  getSessionId() {
    let id = localStorage.getItem('nfh-session-id');
    if (!id) {
      id = 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('nfh-session-id', id);
    }
    return id;
  }

  async handleSubmit(e) {
    e.preventDefault();
    
    const input = this.inputEl.value.trim();
    if (!input) return;
    
    // Show user message
    this.addMessage(input, 'user');
    
    // Clear input
    this.inputEl.value = '';
    
    // Show loading
    const loadingId = this.showLoading();
    
    try {
      // Send to API
      const response = await this.processInput(input);
      
      // Remove loading
      this.removeLoading(loadingId);
      
      // Show response
      this.showResponse(response);
      
    } catch (error) {
      this.removeLoading(loadingId);
      this.addMessage('Sorry, something went wrong. Please try again.', 'error');
      console.error('Error:', error);
    }
  }

  async processInput(input) {
    const response = await fetch('/api/nlp/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        input,
        context: {
          sessionId: this.sessionId
        }
      })
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    return response.json();
  }

  showResponse(response) {
    if (response.success) {
      // Show main message
      this.addMessage(response.message, 'system');
      
      // Show data if available
      if (response.data) {
        if (response.data.packages && response.data.packages.length > 0) {
          const packageList = response.data.packages
            .map(p => `• ${p}`)
            .join('\n');
          this.addMessage(`Found packages:\n${packageList}`, 'system');
        } else if (response.data.info) {
          this.addMessage(response.data.info, 'system');
        }
      }
    } else {
      // Show error message
      this.addMessage(response.message || 'Command failed', 'error');
      
      // Show suggestions if available
      if (response.suggestions && response.suggestions.length > 0) {
        const suggestionHtml = `
          <p>Try one of these:</p>
          <ul>
            ${response.suggestions.map(s => `<li>${s}</li>`).join('')}
          </ul>
        `;
        this.addMessage(suggestionHtml, 'system', true);
      }
    }
  }

  addMessage(content, type = 'system', isHtml = false) {
    const messageEl = document.createElement('div');
    messageEl.className = `message ${type}`;
    
    if (isHtml) {
      messageEl.innerHTML = content;
    } else {
      // Handle newlines
      const lines = content.split('\n');
      lines.forEach((line, i) => {
        if (line.trim()) {
          const p = document.createElement('p');
          p.textContent = line;
          messageEl.appendChild(p);
        }
      });
    }
    
    this.messagesEl.appendChild(messageEl);
    this.scrollToBottom();
  }

  showLoading() {
    const loadingEl = document.createElement('div');
    loadingEl.className = 'message system';
    loadingEl.id = 'loading-' + Date.now();
    loadingEl.innerHTML = '<span class="loading"></span> Processing...';
    
    this.messagesEl.appendChild(loadingEl);
    this.scrollToBottom();
    
    return loadingEl.id;
  }

  removeLoading(loadingId) {
    const loadingEl = document.getElementById(loadingId);
    if (loadingEl) {
      loadingEl.remove();
    }
  }

  scrollToBottom() {
    this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new NixForHumanity();
});

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
  // Ctrl+L to clear messages
  if (e.ctrlKey && e.key === 'l') {
    e.preventDefault();
    const messages = document.getElementById('messages');
    messages.innerHTML = `
      <div class="message system">
        <p>👋 Chat cleared. How can I help you with NixOS?</p>
      </div>
    `;
  }
});