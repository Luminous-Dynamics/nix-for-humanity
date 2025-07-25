/**
 * Minimal Interface
 * Simple, clean UI for natural language NixOS management
 */

export class MinimalInterface extends HTMLElement {
  private input!: HTMLInputElement;
  private output!: HTMLDivElement;
  private voiceButton!: HTMLButtonElement;
  private historyIndex: number = -1;
  private tempInput: string = '';
  
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.render();
    this.attachEventListeners();
  }
  
  private render(): void {
    this.shadowRoot!.innerHTML = `
      <style>
        :host {
          display: block;
          width: 100%;
          max-width: 800px;
          margin: 0 auto;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .container {
          height: 100vh;
          display: flex;
          flex-direction: column;
          padding: 20px;
          box-sizing: border-box;
        }
        
        .output {
          flex: 1;
          overflow-y: auto;
          margin-bottom: 20px;
          padding: 20px;
          background: #f5f5f5;
          border-radius: 8px;
          font-family: 'SF Mono', Monaco, monospace;
          font-size: 14px;
          line-height: 1.6;
        }
        
        .output:empty::before {
          content: 'Type a command or click the microphone to speak...';
          color: #999;
          font-style: italic;
        }
        
        .message {
          margin-bottom: 16px;
          animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        .user-message {
          color: #2563eb;
          font-weight: 500;
        }
        
        .user-message::before {
          content: '▸ ';
        }
        
        .system-message {
          color: #333;
          margin-left: 16px;
        }
        
        .error-message {
          color: #dc2626;
          margin-left: 16px;
        }
        
        .progress-message {
          color: #7c3aed;
          margin-left: 16px;
          font-style: italic;
        }
        
        .input-container {
          display: flex;
          gap: 12px;
          align-items: center;
        }
        
        .input {
          flex: 1;
          padding: 16px;
          font-size: 16px;
          border: 2px solid #e5e7eb;
          border-radius: 8px;
          outline: none;
          transition: border-color 0.2s;
        }
        
        .input:focus {
          border-color: #2563eb;
        }
        
        .input::placeholder {
          color: #9ca3af;
        }
        
        .voice-button {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          border: none;
          background: #2563eb;
          color: white;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }
        
        .voice-button:hover {
          background: #1d4ed8;
          transform: scale(1.05);
        }
        
        .voice-button:active {
          transform: scale(0.95);
        }
        
        .voice-button.listening {
          background: #dc2626;
          animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
          0% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.4); }
          70% { box-shadow: 0 0 0 10px rgba(220, 38, 38, 0); }
          100% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); }
        }
        
        .voice-button svg {
          width: 24px;
          height: 24px;
          fill: currentColor;
        }
        
        .suggestions {
          position: absolute;
          bottom: 100%;
          left: 0;
          right: 0;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          margin-bottom: 8px;
          box-shadow: 0 -4px 6px rgba(0, 0, 0, 0.05);
          max-height: 200px;
          overflow-y: auto;
        }
        
        .suggestion {
          padding: 12px 16px;
          cursor: pointer;
          transition: background 0.2s;
        }
        
        .suggestion:hover {
          background: #f3f4f6;
        }
        
        .suggestion.selected {
          background: #eff6ff;
        }
        
        /* Accessibility */
        @media (prefers-reduced-motion: reduce) {
          * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
          }
        }
        
        /* Dark mode */
        @media (prefers-color-scheme: dark) {
          :host {
            color: #f3f4f6;
          }
          
          .output {
            background: #1f2937;
            color: #f3f4f6;
          }
          
          .input {
            background: #1f2937;
            color: #f3f4f6;
            border-color: #374151;
          }
          
          .input:focus {
            border-color: #3b82f6;
          }
          
          .system-message {
            color: #e5e7eb;
          }
          
          .suggestions {
            background: #1f2937;
            border-color: #374151;
          }
          
          .suggestion:hover {
            background: #374151;
          }
        }
      </style>
      
      <div class="container">
        <div class="output" id="output" role="log" aria-live="polite"></div>
        
        <div class="input-container">
          <input
            type="text"
            class="input"
            id="input"
            placeholder="Type naturally: 'install firefox' or 'update system'"
            aria-label="Command input"
            autocomplete="off"
            spellcheck="false"
          />
          
          <button
            class="voice-button"
            id="voiceButton"
            aria-label="Start voice input"
            type="button"
          >
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
              <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
            </svg>
          </button>
        </div>
      </div>
    `;
    
    this.input = this.shadowRoot!.getElementById('input') as HTMLInputElement;
    this.output = this.shadowRoot!.getElementById('output') as HTMLDivElement;
    this.voiceButton = this.shadowRoot!.getElementById('voiceButton') as HTMLButtonElement;
  }
  
  private attachEventListeners(): void {
    // Input handling
    this.input.addEventListener('keydown', this.handleKeyDown.bind(this));
    
    // Voice button
    this.voiceButton.addEventListener('click', this.toggleVoice.bind(this));
    
    // Focus input on load
    setTimeout(() => this.input.focus(), 100);
  }
  
  private handleKeyDown(event: KeyboardEvent): void {
    switch (event.key) {
      case 'Enter':
        event.preventDefault();
        this.processCommand();
        break;
        
      case 'ArrowUp':
        event.preventDefault();
        this.navigateHistory('up');
        break;
        
      case 'ArrowDown':
        event.preventDefault();
        this.navigateHistory('down');
        break;
        
      case 'Tab':
        if (this.input.value) {
          event.preventDefault();
          this.autocomplete();
        }
        break;
    }
  }
  
  private processCommand(): void {
    const input = this.input.value.trim();
    if (!input) return;
    
    // Add to output
    this.addMessage(input, 'user');
    
    // Clear input
    this.input.value = '';
    this.historyIndex = -1;
    this.tempInput = '';
    
    // Emit event for processing
    this.dispatchEvent(new CustomEvent('command', {
      detail: { input },
      bubbles: true
    }));
  }
  
  private navigateHistory(direction: 'up' | 'down'): void {
    const event = new CustomEvent('history-navigate', {
      detail: { direction, currentIndex: this.historyIndex },
      bubbles: true
    });
    
    this.dispatchEvent(event);
    
    // Update input based on response
    // (This would be handled by the parent component)
  }
  
  private autocomplete(): void {
    const event = new CustomEvent('autocomplete', {
      detail: { partial: this.input.value },
      bubbles: true
    });
    
    this.dispatchEvent(event);
  }
  
  private toggleVoice(): void {
    const isListening = this.voiceButton.classList.contains('listening');
    
    if (isListening) {
      this.voiceButton.classList.remove('listening');
      this.voiceButton.setAttribute('aria-label', 'Start voice input');
    } else {
      this.voiceButton.classList.add('listening');
      this.voiceButton.setAttribute('aria-label', 'Stop voice input');
    }
    
    this.dispatchEvent(new CustomEvent('voice-toggle', {
      detail: { listening: !isListening },
      bubbles: true
    }));
  }
  
  /**
   * Add message to output
   */
  public addMessage(text: string, type: 'user' | 'system' | 'error' | 'progress'): void {
    const message = document.createElement('div');
    message.className = `message ${type}-message`;
    message.textContent = text;
    
    this.output.appendChild(message);
    this.output.scrollTop = this.output.scrollHeight;
  }
  
  /**
   * Clear output
   */
  public clear(): void {
    this.output.innerHTML = '';
  }
  
  /**
   * Set input value
   */
  public setInput(value: string): void {
    this.input.value = value;
    this.input.focus();
  }
  
  /**
   * Update voice button state
   */
  public setVoiceState(listening: boolean): void {
    if (listening) {
      this.voiceButton.classList.add('listening');
      this.voiceButton.setAttribute('aria-label', 'Stop voice input');
    } else {
      this.voiceButton.classList.remove('listening');
      this.voiceButton.setAttribute('aria-label', 'Start voice input');
    }
  }
  
  /**
   * Show suggestions
   */
  public showSuggestions(suggestions: string[]): void {
    // Remove existing suggestions
    const existing = this.shadowRoot!.querySelector('.suggestions');
    if (existing) existing.remove();
    
    if (suggestions.length === 0) return;
    
    const container = document.createElement('div');
    container.className = 'suggestions';
    
    suggestions.forEach((suggestion, index) => {
      const item = document.createElement('div');
      item.className = 'suggestion';
      if (index === 0) item.classList.add('selected');
      item.textContent = suggestion;
      
      item.addEventListener('click', () => {
        this.input.value = suggestion;
        this.input.focus();
        container.remove();
      });
      
      container.appendChild(item);
    });
    
    this.input.parentElement!.style.position = 'relative';
    this.input.parentElement!.appendChild(container);
  }
  
  /**
   * Hide suggestions
   */
  public hideSuggestions(): void {
    const suggestions = this.shadowRoot!.querySelector('.suggestions');
    if (suggestions) suggestions.remove();
  }
}

// Register the custom element
customElements.define('minimal-nix-interface', MinimalInterface);