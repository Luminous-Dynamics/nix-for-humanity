/**
 * Web Components for Luminous Nix GUI
 * True modularity - these work in any framework!
 */

// ========== Base Component Class ==========
class LuminousComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.aiInterface = {
      id: this.generateId(),
      type: this.constructor.name,
      capabilities: [],
      state: {}
    };
  }

  generateId() {
    return `${this.constructor.name}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  connectedCallback() {
    this.render();
    this.registerWithAI();
    this.setupEventListeners();
  }

  registerWithAI() {
    // Register this component with the AI control system
    window.__TAURI__?.invoke('register_component', {
      id: this.aiInterface.id,
      type: this.aiInterface.type,
      capabilities: this.aiInterface.capabilities,
      state: this.aiInterface.state
    });
  }

  updateState(newState) {
    this.aiInterface.state = { ...this.aiInterface.state, ...newState };
    window.__TAURI__?.invoke('set_component_state', {
      id: this.aiInterface.id,
      new_state: this.aiInterface.state
    });
  }

  render() {
    // Override in subclasses
  }

  setupEventListeners() {
    // Override in subclasses
  }
}

// ========== Search Bar Component ==========
class SearchBar extends LuminousComponent {
  constructor() {
    super();
    this.aiInterface.capabilities = ['type', 'clear', 'search', 'voice'];
    this.aiInterface.state = { value: '', suggestions: [], voiceActive: false };
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          padding: var(--spacing-md, 16px);
        }
        .search-container {
          display: flex;
          align-items: center;
          background: var(--bg-primary, #1a1a2e);
          border: 2px solid var(--border-color, #16213e);
          border-radius: var(--radius-lg, 12px);
          padding: 12px;
          transition: all 0.3s ease;
        }
        .search-container:focus-within {
          border-color: var(--accent-color, #0f4c75);
          box-shadow: 0 0 20px rgba(15, 76, 117, 0.3);
        }
        input {
          flex: 1;
          background: transparent;
          border: none;
          color: var(--text-primary, #eee);
          font-size: 16px;
          outline: none;
        }
        input::placeholder {
          color: var(--text-secondary, #666);
        }
        button {
          background: transparent;
          border: none;
          color: var(--text-secondary, #666);
          cursor: pointer;
          padding: 8px;
          transition: color 0.2s;
        }
        button:hover {
          color: var(--text-primary, #eee);
        }
        button.active {
          color: var(--accent-color, #0f4c75);
        }
        .suggestions {
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          background: var(--bg-secondary, #0f3460);
          border-radius: 8px;
          margin-top: 8px;
          max-height: 200px;
          overflow-y: auto;
          opacity: 0;
          transform: translateY(-10px);
          transition: all 0.2s;
          pointer-events: none;
        }
        .suggestions.show {
          opacity: 1;
          transform: translateY(0);
          pointer-events: all;
        }
        .suggestion {
          padding: 12px;
          cursor: pointer;
          transition: background 0.2s;
        }
        .suggestion:hover {
          background: rgba(255,255,255,0.1);
        }
      </style>
      
      <div class="search-container">
        <button id="voice-btn" aria-label="Voice search">
          🎤
        </button>
        <input 
          type="text" 
          placeholder="Ask me anything... (e.g., 'install firefox')"
          id="search-input"
          aria-label="Search"
        />
        <button id="search-btn" aria-label="Search">
          🔍
        </button>
      </div>
      
      <div class="suggestions" id="suggestions"></div>
    `;
  }

  setupEventListeners() {
    const input = this.shadowRoot.getElementById('search-input');
    const voiceBtn = this.shadowRoot.getElementById('voice-btn');
    const searchBtn = this.shadowRoot.getElementById('search-btn');
    const suggestions = this.shadowRoot.getElementById('suggestions');

    // Input handling
    input.addEventListener('input', (e) => {
      this.updateState({ value: e.target.value });
      this.fetchSuggestions(e.target.value);
    });

    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.performSearch();
      }
    });

    // Voice button
    voiceBtn.addEventListener('click', () => {
      this.toggleVoice();
    });

    // Search button
    searchBtn.addEventListener('click', () => {
      this.performSearch();
    });
  }

  async fetchSuggestions(query) {
    if (!query) {
      this.shadowRoot.getElementById('suggestions').classList.remove('show');
      return;
    }

    // Would call actual API
    const mockSuggestions = [
      'install firefox',
      'install neovim',
      'install nodejs'
    ].filter(s => s.includes(query));

    this.updateState({ suggestions: mockSuggestions });
    this.renderSuggestions(mockSuggestions);
  }

  renderSuggestions(suggestions) {
    const container = this.shadowRoot.getElementById('suggestions');
    container.innerHTML = suggestions.map(s => 
      `<div class="suggestion">${s}</div>`
    ).join('');
    
    container.classList.toggle('show', suggestions.length > 0);
    
    // Add click handlers
    container.querySelectorAll('.suggestion').forEach(el => {
      el.addEventListener('click', () => {
        this.shadowRoot.getElementById('search-input').value = el.textContent;
        this.updateState({ value: el.textContent });
        container.classList.remove('show');
        this.performSearch();
      });
    });
  }

  async performSearch() {
    const query = this.aiInterface.state.value;
    if (!query) return;

    const result = await window.__TAURI__?.invoke('perform_action', {
      action: 'search',
      params: { query }
    });

    this.dispatchEvent(new CustomEvent('search', {
      detail: { query, result },
      bubbles: true
    }));
  }

  toggleVoice() {
    const active = !this.aiInterface.state.voiceActive;
    this.updateState({ voiceActive: active });
    
    const btn = this.shadowRoot.getElementById('voice-btn');
    btn.classList.toggle('active', active);
    
    if (active) {
      // Start voice recognition
      console.log('Voice input activated');
    } else {
      // Stop voice recognition
      console.log('Voice input deactivated');
    }
  }

  // AI Interface Methods
  aiType(text) {
    const input = this.shadowRoot.getElementById('search-input');
    input.value = text;
    this.updateState({ value: text });
  }

  aiClear() {
    const input = this.shadowRoot.getElementById('search-input');
    input.value = '';
    this.updateState({ value: '', suggestions: [] });
  }

  aiSearch() {
    this.performSearch();
  }
}

// ========== Results List Component ==========
class ResultsList extends LuminousComponent {
  constructor() {
    super();
    this.aiInterface.capabilities = ['display', 'select', 'clear', 'sort'];
    this.aiInterface.state = { results: [], selectedIndex: -1 };
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          padding: var(--spacing-md, 16px);
        }
        .results-container {
          background: var(--bg-primary, #1a1a2e);
          border-radius: var(--radius-lg, 12px);
          overflow: hidden;
        }
        .result-item {
          padding: 16px;
          border-bottom: 1px solid var(--border-color, #16213e);
          cursor: pointer;
          transition: background 0.2s;
        }
        .result-item:hover {
          background: rgba(255,255,255,0.05);
        }
        .result-item.selected {
          background: var(--accent-bg, rgba(15, 76, 117, 0.2));
          border-left: 3px solid var(--accent-color, #0f4c75);
        }
        .result-title {
          font-size: 18px;
          color: var(--text-primary, #eee);
          margin-bottom: 4px;
        }
        .result-description {
          font-size: 14px;
          color: var(--text-secondary, #666);
        }
        .result-actions {
          margin-top: 8px;
          display: flex;
          gap: 8px;
        }
        .action-btn {
          padding: 4px 12px;
          background: var(--accent-color, #0f4c75);
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
          transition: background 0.2s;
        }
        .action-btn:hover {
          background: var(--accent-hover, #0a3a5c);
        }
        .empty-state {
          padding: 48px;
          text-align: center;
          color: var(--text-secondary, #666);
        }
      </style>
      
      <div class="results-container" id="results"></div>
    `;

    this.renderResults();
  }

  renderResults() {
    const container = this.shadowRoot.getElementById('results');
    const { results, selectedIndex } = this.aiInterface.state;

    if (!results || results.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <p>No results yet. Try searching for something!</p>
        </div>
      `;
      return;
    }

    container.innerHTML = results.map((result, index) => `
      <div class="result-item ${index === selectedIndex ? 'selected' : ''}" 
           data-index="${index}">
        <div class="result-title">${result.name}</div>
        <div class="result-description">${result.description}</div>
        <div class="result-actions">
          <button class="action-btn" data-action="install" data-package="${result.name}">
            Install
          </button>
          <button class="action-btn" data-action="info" data-package="${result.name}">
            More Info
          </button>
        </div>
      </div>
    `).join('');

    this.attachResultListeners();
  }

  attachResultListeners() {
    const container = this.shadowRoot.getElementById('results');
    
    // Click on result
    container.querySelectorAll('.result-item').forEach(item => {
      item.addEventListener('click', () => {
        const index = parseInt(item.dataset.index);
        this.selectResult(index);
      });
    });

    // Action buttons
    container.querySelectorAll('.action-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const action = btn.dataset.action;
        const packageName = btn.dataset.package;
        this.performAction(action, packageName);
      });
    });
  }

  selectResult(index) {
    this.updateState({ selectedIndex: index });
    this.renderResults();
  }

  async performAction(action, packageName) {
    const result = await window.__TAURI__?.invoke('perform_action', {
      action,
      params: { package: packageName }
    });

    this.dispatchEvent(new CustomEvent('action', {
      detail: { action, package: packageName, result },
      bubbles: true
    }));
  }

  // AI Interface Methods
  aiSelect(index) {
    this.selectResult(index);
  }

  aiClear() {
    this.updateState({ results: [], selectedIndex: -1 });
    this.renderResults();
  }

  aiSetResults(results) {
    this.updateState({ results, selectedIndex: -1 });
    this.renderResults();
  }
}

// ========== Consciousness Monitor Component ==========
class ConsciousnessMonitor extends LuminousComponent {
  constructor() {
    super();
    this.aiInterface.capabilities = ['monitor', 'adapt'];
    this.aiInterface.state = { 
      coherence: 0.5,
      cognitiveLoad: 0.3,
      flowState: 0,
      adaptations: []
    };
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          padding: var(--spacing-sm, 8px);
        }
        .monitor {
          background: var(--bg-secondary, #0f3460);
          border-radius: var(--radius-md, 8px);
          padding: 12px;
          font-size: 12px;
        }
        .metric {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }
        .metric-label {
          color: var(--text-secondary, #666);
        }
        .metric-value {
          color: var(--text-primary, #eee);
        }
        .metric-bar {
          flex: 1;
          height: 4px;
          background: rgba(255,255,255,0.1);
          border-radius: 2px;
          margin: 0 8px;
          overflow: hidden;
        }
        .metric-fill {
          height: 100%;
          background: var(--accent-color, #0f4c75);
          transition: width 0.3s ease;
        }
        .adaptations {
          margin-top: 12px;
          padding-top: 12px;
          border-top: 1px solid rgba(255,255,255,0.1);
        }
        .adaptation {
          color: var(--text-secondary, #666);
          font-size: 11px;
          margin-bottom: 4px;
        }
      </style>
      
      <div class="monitor">
        <div class="metric">
          <span class="metric-label">Coherence</span>
          <div class="metric-bar">
            <div class="metric-fill" style="width: ${this.aiInterface.state.coherence * 100}%"></div>
          </div>
          <span class="metric-value">${(this.aiInterface.state.coherence * 100).toFixed(0)}%</span>
        </div>
        
        <div class="metric">
          <span class="metric-label">Cognitive Load</span>
          <div class="metric-bar">
            <div class="metric-fill" style="width: ${this.aiInterface.state.cognitiveLoad * 100}%"></div>
          </div>
          <span class="metric-value">${(this.aiInterface.state.cognitiveLoad * 100).toFixed(0)}%</span>
        </div>
        
        <div class="metric">
          <span class="metric-label">Flow State</span>
          <div class="metric-bar">
            <div class="metric-fill" style="width: ${this.aiInterface.state.flowState * 100}%"></div>
          </div>
          <span class="metric-value">${(this.aiInterface.state.flowState * 100).toFixed(0)}%</span>
        </div>
        
        <div class="adaptations" id="adaptations"></div>
      </div>
    `;

    this.startMonitoring();
  }

  startMonitoring() {
    // Simulate biometric monitoring
    setInterval(() => {
      const state = {
        coherence: 0.5 + Math.sin(Date.now() / 10000) * 0.3,
        cognitiveLoad: 0.3 + Math.sin(Date.now() / 8000) * 0.2,
        flowState: Math.max(0, Math.sin(Date.now() / 15000))
      };

      this.updateMetrics(state);
      this.checkAdaptations(state);
    }, 1000);
  }

  updateMetrics(state) {
    this.updateState(state);
    
    // Update visual bars
    this.shadowRoot.querySelectorAll('.metric-fill').forEach((bar, index) => {
      const values = [state.coherence, state.cognitiveLoad, state.flowState];
      bar.style.width = `${values[index] * 100}%`;
    });

    // Update text values
    this.shadowRoot.querySelectorAll('.metric-value').forEach((val, index) => {
      const values = [state.coherence, state.cognitiveLoad, state.flowState];
      val.textContent = `${(values[index] * 100).toFixed(0)}%`;
    });
  }

  async checkAdaptations(state) {
    const adaptations = await window.__TAURI__?.invoke('adapt_to_user_state', {
      user_state: state
    });

    if (adaptations && Object.keys(adaptations).length > 0) {
      this.applyAdaptations(adaptations);
    }
  }

  applyAdaptations(adaptations) {
    const container = this.shadowRoot.getElementById('adaptations');
    const messages = [];

    if (adaptations.layout) {
      messages.push(`Switched to ${adaptations.layout} layout`);
      document.body.dataset.layout = adaptations.layout;
    }

    if (adaptations.font_size_increase) {
      messages.push(`Increased font size by ${adaptations.font_size_increase}x`);
      document.documentElement.style.fontSize = `${16 * adaptations.font_size_increase}px`;
    }

    container.innerHTML = messages.map(msg => 
      `<div class="adaptation">• ${msg}</div>`
    ).join('');

    this.updateState({ adaptations: messages });
  }
}

// ========== Register Components ==========
customElements.define('search-bar', SearchBar);
customElements.define('results-list', ResultsList);
customElements.define('consciousness-monitor', ConsciousnessMonitor);

// Export for use in frameworks
export { SearchBar, ResultsList, ConsciousnessMonitor, LuminousComponent };