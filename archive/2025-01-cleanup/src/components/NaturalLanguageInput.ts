import { invoke } from '@tauri-apps/api/tauri';

export class NaturalLanguageInput extends HTMLElement {
  private isListening = false;
  private recognition: any = null;

  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    this.render();
    this.setupEventListeners();
    this.initializeSpeechRecognition();
  }

  private render() {
    this.shadowRoot!.innerHTML = `
      <style>
        :host {
          display: block;
          margin: 2rem 0;
        }
        
        .input-container {
          position: relative;
          width: 100%;
          max-width: 600px;
          margin: 0 auto;
        }
        
        input {
          width: 100%;
          padding: 1rem 3.5rem 1rem 1rem;
          font-size: 1.1rem;
          border: 2px solid #ddd;
          border-radius: 8px;
          transition: border-color 0.3s;
        }
        
        input:focus {
          outline: none;
          border-color: #4a90e2;
        }
        
        .voice-button {
          position: absolute;
          right: 0.5rem;
          top: 50%;
          transform: translateY(-50%);
          width: 2.5rem;
          height: 2.5rem;
          border: none;
          border-radius: 50%;
          background: #f0f0f0;
          cursor: pointer;
          transition: all 0.3s;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.2rem;
        }
        
        .voice-button:hover {
          background: #e0e0e0;
        }
        
        .voice-button.listening {
          background: #e74c3c;
          color: white;
          animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
          0% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0.7); }
          70% { box-shadow: 0 0 0 10px rgba(231, 76, 60, 0); }
          100% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0); }
        }
        
        .suggestions {
          margin-top: 0.5rem;
          font-size: 0.9rem;
          color: #666;
          text-align: center;
        }
      </style>
      
      <div class="input-container">
        <input
          type="text"
          id="nlp-input"
          placeholder="Type or speak: 'install firefox' or 'update system'"
          aria-label="Natural language command input"
          autocomplete="off"
          spellcheck="false"
        />
        <button
          class="voice-button"
          id="voice-button"
          aria-label="Start voice input"
          title="Click to speak"
        >
          🎤
        </button>
      </div>
      
      <div class="suggestions">
        Try: "install firefox", "my wifi isn't working", "update everything"
      </div>
    `;
  }

  private setupEventListeners() {
    const input = this.shadowRoot!.getElementById('nlp-input') as HTMLInputElement;
    const voiceButton = this.shadowRoot!.getElementById('voice-button') as HTMLButtonElement;

    // Text input handling
    input.addEventListener('keypress', async (e) => {
      if (e.key === 'Enter') {
        const text = input.value.trim();
        if (text) {
          await this.processInput(text);
          input.value = '';
        }
      }
    });

    // Voice button handling
    voiceButton.addEventListener('click', () => {
      this.toggleVoiceRecognition();
    });
  }

  private initializeSpeechRecognition() {
    // Check if Web Speech API is available
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = false;
      this.recognition.interimResults = true;
      this.recognition.lang = 'en-US';

      this.recognition.onstart = () => {
        this.isListening = true;
        this.updateVoiceButton();
      };

      this.recognition.onend = () => {
        this.isListening = false;
        this.updateVoiceButton();
      };

      this.recognition.onresult = (event: any) => {
        const input = this.shadowRoot!.getElementById('nlp-input') as HTMLInputElement;
        const transcript = Array.from(event.results)
          .map((result: any) => result[0].transcript)
          .join('');
        
        input.value = transcript;

        // Process if final result
        if (event.results[event.results.length - 1].isFinal) {
          this.processInput(transcript);
        }
      };

      this.recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        this.isListening = false;
        this.updateVoiceButton();
      };
    }
  }

  private toggleVoiceRecognition() {
    if (!this.recognition) {
      alert('Voice input is not supported in your browser. Please type your command instead.');
      return;
    }

    if (this.isListening) {
      this.recognition.stop();
    } else {
      this.recognition.start();
    }
  }

  private updateVoiceButton() {
    const voiceButton = this.shadowRoot!.getElementById('voice-button') as HTMLButtonElement;
    if (this.isListening) {
      voiceButton.classList.add('listening');
      voiceButton.textContent = '🔴';
      voiceButton.title = 'Click to stop';
    } else {
      voiceButton.classList.remove('listening');
      voiceButton.textContent = '🎤';
      voiceButton.title = 'Click to speak';
    }
  }

  private async processInput(text: string) {
    try {
      // Send to Rust backend for processing
      const result = await invoke('process_natural_language', { input: text });
      
      // Emit event with result
      this.dispatchEvent(new CustomEvent('nlp-result', {
        detail: result,
        bubbles: true,
        composed: true
      }));
    } catch (error) {
      console.error('Failed to process input:', error);
      this.dispatchEvent(new CustomEvent('nlp-error', {
        detail: error,
        bubbles: true,
        composed: true
      }));
    }
  }
}