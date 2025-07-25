// Main entry point for Tauri frontend
import { invoke } from '@tauri-apps/api/core';
import { NixInterface } from '@nlp/index';
import { TauriNixInterface } from '@nlp/tauri-nix-interface';
import { TauriSacredInterface } from '@nlp/tauri-sacred-interface';
import './style.css';

// Initialize the app
async function initializeApp() {
  const app = document.getElementById('app');
  if (!app) return;

  // Check if we're running in Tauri
  const isTauri = window.__TAURI__ !== undefined;

  app.innerHTML = `
    <div class="nfh-container">
      <header>
        <h1>Nix for Humanity</h1>
        <p class="tagline">Speak naturally to your computer</p>
        ${isTauri ? '<p class="status">Running in Tauri Desktop Mode</p>' : ''}
      </header>
      
      <main id="main">
        <div class="input-container">
          <label for="natural-input" class="sr-only">Type or speak your command</label>
          <input 
            type="text" 
            id="natural-input"
            class="natural-input"
            placeholder="Type what you want (e.g., 'install firefox')"
            aria-label="Natural language input"
            autocomplete="off"
          />
          
          <button 
            id="voice-button"
            class="voice-button"
            aria-label="Start voice input"
            title="Click to speak"
          >
            🎤
          </button>
        </div>
        
        <div id="output" class="output" role="log" aria-live="polite">
          <!-- Command results appear here -->
        </div>
      </main>
      
      <footer>
        <p>Built with love by Luminous-Dynamics | Privacy-first, local processing</p>
      </footer>
    </div>
  `;

  // Initialize NLP interface - use Sacred Tauri version if in Tauri, otherwise regular
  const nlpInterface = isTauri ? new TauriSacredInterface() : new NixInterface();
  
  // Set up input handlers
  const input = document.getElementById('natural-input') as HTMLInputElement;
  const output = document.getElementById('output') as HTMLDivElement;
  const voiceButton = document.getElementById('voice-button') as HTMLButtonElement;

  // Handle text input
  input.addEventListener('keypress', async (e) => {
    if (e.key === 'Enter' && input.value.trim()) {
      const userInput = input.value.trim();
      input.value = '';
      
      // Show user input
      addOutput(`You: ${userInput}`, 'user');
      
      try {
        // Process through NLP (TauriSacredInterface handles execution if in Tauri)
        const result = await nlpInterface.processInput(userInput);
        
        // Handle sacred response
        if (result.requiresConfirmation) {
          // Show confirmation dialog
          addOutput(`⚠️ ${result.response}`, 'warning');
          addOutput(`Command: ${result.command}`, 'preview');
          
          // Create confirmation UI
          const confirmDiv = document.createElement('div');
          confirmDiv.className = 'confirmation-prompt';
          confirmDiv.innerHTML = `
            <p>Do you want to proceed?</p>
            <button id="confirm-yes" class="btn-confirm">Yes, proceed</button>
            <button id="confirm-no" class="btn-cancel">Cancel</button>
          `;
          output.appendChild(confirmDiv);
          
          // Handle confirmation
          document.getElementById('confirm-yes')?.addEventListener('click', async () => {
            confirmDiv.remove();
            addOutput('Proceeding with command...', 'info');
            
            if (isTauri && result.intent) {
              const execResult = await nlpInterface.executeConfirmed(result.intent);
              addOutput(`Nix: ${execResult.response}`, 'system');
              if (execResult.mantra) {
                addOutput(`✨ ${execResult.mantra}`, 'mantra');
              }
            }
          });
          
          document.getElementById('confirm-no')?.addEventListener('click', () => {
            confirmDiv.remove();
            addOutput('Command cancelled.', 'info');
          });
        } else {
          // Normal response
          addOutput(`Nix: ${result.response}`, 'system');
          
          // Show sacred mantra if present
          if (result.mantra) {
            addOutput(`✨ ${result.mantra}`, 'mantra');
          }
          
          // In web mode, show what would be executed
          if (!isTauri && result.command) {
            addOutput(`Would execute: ${result.command.command} ${result.command.args.join(' ')}`, 'preview');
          }
        }
      } catch (error) {
        addOutput(`Error: ${error}`, 'error');
      }
    }
  });

  // Voice input handler (placeholder for now)
  voiceButton.addEventListener('click', () => {
    addOutput('Voice input coming soon! For now, please type your commands.', 'info');
  });

  function addOutput(text: string, type: 'user' | 'system' | 'result' | 'error' | 'info' | 'preview' | 'warning' | 'mantra') {
    const entry = document.createElement('div');
    entry.className = `output-entry output-${type}`;
    entry.textContent = text;
    output.appendChild(entry);
    output.scrollTop = output.scrollHeight;
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeApp);
} else {
  initializeApp();
}

// Export for Tauri
declare global {
  interface Window {
    __TAURI__?: any;
  }
}