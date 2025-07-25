import { setupAccessibility } from './utils/accessibility';
import { NaturalLanguageInput } from './components/NaturalLanguageInput';
import { ResponseDisplay } from './components/ResponseDisplay';

// Register custom elements
customElements.define('natural-language-input', NaturalLanguageInput);
customElements.define('response-display', ResponseDisplay);

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
  console.log('🚀 Nix for Humanity starting...');
  
  // Set up accessibility features
  setupAccessibility();
  
  // Replace loading state with app
  const app = document.getElementById('app');
  if (!app) return;
  
  app.classList.remove('loading');
  app.innerHTML = `
    <div class="nfh-container">
      <header>
        <h1>Nix for Humanity</h1>
        <p class="tagline">Control NixOS with natural language</p>
      </header>
      
      <main id="main">
        <natural-language-input></natural-language-input>
        <response-display></response-display>
      </main>
      
      <footer>
        <p>Press <kbd>Ctrl+/</kbd> for help • Built with 💙 by Luminous-Dynamics</p>
      </footer>
    </div>
  `;
  
  console.log('✅ Nix for Humanity ready');
});

// Handle errors gracefully
window.addEventListener('error', (event) => {
  console.error('Application error:', event.error);
  
  // Show user-friendly error
  const errorDiv = document.createElement('div');
  errorDiv.className = 'error';
  errorDiv.innerHTML = `
    <h2>Something went wrong</h2>
    <p>Please refresh the page or contact support if the issue persists.</p>
  `;
  
  const app = document.getElementById('app');
  if (app) {
    app.innerHTML = '';
    app.appendChild(errorDiv);
  }
});

// Export for Tauri
export {};