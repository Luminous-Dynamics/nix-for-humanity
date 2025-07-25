export class ResponseDisplay extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    this.render();
    this.setupEventListeners();
  }

  private render() {
    this.shadowRoot!.innerHTML = `
      <style>
        :host {
          display: block;
          margin: 2rem 0;
          min-height: 200px;
        }
        
        .response-container {
          max-width: 600px;
          margin: 0 auto;
          padding: 1rem;
          background: #f9f9f9;
          border-radius: 8px;
          min-height: 150px;
        }
        
        .response-message {
          font-size: 1.1rem;
          line-height: 1.6;
          color: #333;
        }
        
        .response-action {
          margin-top: 1rem;
          padding: 0.75rem;
          background: #e8f4fd;
          border-left: 4px solid #4a90e2;
          border-radius: 4px;
          font-family: monospace;
          font-size: 0.95rem;
        }
        
        .response-error {
          color: #e74c3c;
          background: #ffeee8;
          border-left-color: #e74c3c;
        }
        
        .response-success {
          color: #27ae60;
          background: #eafaf1;
          border-left-color: #27ae60;
        }
        
        .loading {
          text-align: center;
          color: #666;
        }
        
        .loading::after {
          content: '...';
          animation: dots 1.5s steps(4, end) infinite;
        }
        
        @keyframes dots {
          0%, 20% { content: ''; }
          40% { content: '.'; }
          60% { content: '..'; }
          80%, 100% { content: '...'; }
        }
        
        .empty-state {
          text-align: center;
          color: #999;
          padding: 2rem;
        }
      </style>
      
      <div class="response-container">
        <div class="empty-state">
          <p>👋 Hi! I'm ready to help with NixOS.</p>
          <p>Type or speak what you need.</p>
        </div>
      </div>
    `;
  }

  private setupEventListeners() {
    // Listen for NLP results
    document.addEventListener('nlp-result', (e: CustomEvent) => {
      this.displayResult(e.detail);
    });

    // Listen for errors
    document.addEventListener('nlp-error', (e: CustomEvent) => {
      this.displayError(e.detail);
    });
  }

  private displayResult(result: any) {
    const container = this.shadowRoot!.querySelector('.response-container')!;
    
    // Show loading state briefly
    container.innerHTML = '<div class="loading">Processing</div>';
    
    setTimeout(() => {
      let html = '';
      
      // Main response message
      html += `<div class="response-message">${this.getResponseMessage(result)}</div>`;
      
      // Show action if any
      if (result.action) {
        const actionClass = result.success ? 'response-success' : 'response-action';
        html += `<div class="${actionClass}">${result.action}</div>`;
      }
      
      // Show suggestions if needed
      if (result.needsClarification) {
        html += `<div class="response-message">${result.clarificationPrompt}</div>`;
      }
      
      container.innerHTML = html;
      
      // Announce to screen readers
      this.announceToScreenReader(this.getResponseMessage(result));
    }, 500);
  }

  private displayError(error: any) {
    const container = this.shadowRoot!.querySelector('.response-container')!;
    container.innerHTML = `
      <div class="response-message response-error">
        😕 Sorry, I encountered an error: ${error.message || error}
      </div>
    `;
    
    this.announceToScreenReader(`Error: ${error.message || error}`);
  }

  private getResponseMessage(result: any): string {
    switch (result.action) {
      case 'install_package':
        const pkg = result.entities[0]?.value || 'the package';
        return `I'll install ${pkg} for you...`;
        
      case 'remove_package':
        return `Removing ${result.entities[0]?.value || 'the package'}...`;
        
      case 'update_system':
        return 'Updating your system...';
        
      case 'search_packages':
        return `Searching for packages related to "${result.entities[0]?.value}"...`;
        
      case 'get_help':
        return 'Here\'s how I can help:';
        
      case 'troubleshoot':
        return `Let me help diagnose the issue with ${result.entities[0]?.value || 'your system'}...`;
        
      case 'unknown':
        return 'I didn\'t understand that. Could you rephrase it? For example: "install firefox" or "update system"';
        
      default:
        return 'Processing your request...';
    }
  }

  private announceToScreenReader(message: string) {
    // Create a live region for screen reader announcements
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.style.position = 'absolute';
    announcement.style.left = '-10000px';
    announcement.textContent = message;
    
    document.body.appendChild(announcement);
    
    // Remove after announcement
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  }
}