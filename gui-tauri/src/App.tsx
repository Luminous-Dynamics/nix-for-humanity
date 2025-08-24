import { createSignal, onMount, createEffect } from 'solid-js';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import './components/web-components.js';

// Layout configurations
const LAYOUTS = {
  simple: {
    name: "Simple",
    grid: "auto 1fr / 1fr",
    components: ['search-bar', 'results-list']
  },
  dashboard: {
    name: "Dashboard",
    grid: "auto 1fr auto / 1fr",
    components: ['search-bar', 'results-list', 'consciousness-monitor']
  },
  split: {
    name: "Split View",
    grid: "auto 1fr / 1fr 1fr",
    components: ['search-bar', 'results-list', 'consciousness-monitor']
  },
  minimal: {
    name: "Minimal",
    grid: "1fr / 1fr",
    components: ['search-bar']
  }
};

// Theme presets
const THEMES = {
  default: {
    name: "Default",
    tokens: {
      '--bg-primary': '#1a1a2e',
      '--bg-secondary': '#0f3460',
      '--text-primary': '#eee',
      '--text-secondary': '#666',
      '--accent-color': '#0f4c75',
      '--border-color': '#16213e',
      '--radius-lg': '12px',
      '--spacing-md': '16px'
    }
  },
  light: {
    name: "Light",
    tokens: {
      '--bg-primary': '#ffffff',
      '--bg-secondary': '#f5f5f5',
      '--text-primary': '#333',
      '--text-secondary': '#666',
      '--accent-color': '#007acc',
      '--border-color': '#ddd',
      '--radius-lg': '8px',
      '--spacing-md': '16px'
    }
  },
  highContrast: {
    name: "High Contrast",
    tokens: {
      '--bg-primary': '#000000',
      '--bg-secondary': '#111111',
      '--text-primary': '#ffffff',
      '--text-secondary': '#aaa',
      '--accent-color': '#00ff00',
      '--border-color': '#444',
      '--radius-lg': '0px',
      '--spacing-md': '20px'
    }
  },
  sacred: {
    name: "Sacred Geometry",
    tokens: {
      '--bg-primary': '#0a0e27',
      '--bg-secondary': '#151935',
      '--text-primary': '#c9d1ff',
      '--text-secondary': '#7a88cf',
      '--accent-color': '#6366f1',
      '--border-color': '#2a3352',
      '--radius-lg': '16px',
      '--spacing-md': '24px'
    }
  }
};

function App() {
  const [currentLayout, setCurrentLayout] = createSignal('dashboard');
  const [currentTheme, setCurrentTheme] = createSignal('default');
  const [components, setComponents] = createSignal([]);
  const [userProfile, setUserProfile] = createSignal(null);
  const [searchResults, setSearchResults] = createSignal([]);
  const [isAIControlled, setIsAIControlled] = createSignal(false);

  // Initialize
  onMount(async () => {
    // Load components from backend
    const loadedComponents = await invoke('get_components');
    setComponents(loadedComponents);

    // Apply default theme
    applyTheme(THEMES.default.tokens);

    // Listen for AI control events
    await listen('ai-control', (event) => {
      handleAIControl(event.payload);
    });

    // Listen for search events from components
    document.addEventListener('search', async (e) => {
      const { query } = e.detail;
      const results = await performSearch(query);
      setSearchResults(results);
      
      // Update results list component
      const resultsList = document.querySelector('results-list');
      if (resultsList) {
        resultsList.aiSetResults(results);
      }
    });

    // Listen for action events
    document.addEventListener('action', async (e) => {
      const { action, package: pkg, result } = e.detail;
      console.log(`Action performed: ${action} on ${pkg}`, result);
      
      // Show notification
      if (result?.success) {
        await showNotification(`${action} successful for ${pkg}`);
      }
    });

    // Start interaction recording
    startInteractionRecording();
  });

  // Apply theme
  const applyTheme = (tokens) => {
    Object.entries(tokens).forEach(([key, value]) => {
      document.documentElement.style.setProperty(key, value);
    });
    
    invoke('customize_theme', { tokens });
  };

  // Switch layout
  const switchLayout = (layoutName) => {
    setCurrentLayout(layoutName);
    const layout = LAYOUTS[layoutName];
    
    // Update grid
    const container = document.getElementById('component-container');
    if (container) {
      container.style.gridTemplate = layout.grid;
    }

    invoke('switch_layout', { layout_id: layoutName });
  };

  // Perform search
  const performSearch = async (query) => {
    const result = await invoke('perform_action', {
      action: 'search',
      params: { query }
    });
    
    return result.results || [];
  };

  // Show notification
  const showNotification = async (message) => {
    // Would use Tauri's notification API
    console.log(`Notification: ${message}`);
  };

  // Handle AI control
  const handleAIControl = (command) => {
    setIsAIControlled(true);
    
    switch (command.type) {
      case 'click':
        const element = document.getElementById(command.target);
        element?.click();
        break;
      
      case 'type':
        const input = document.querySelector(`#${command.target} input`);
        if (input) {
          input.value = command.text;
          input.dispatchEvent(new Event('input'));
        }
        break;
      
      case 'switch_layout':
        switchLayout(command.layout);
        break;
      
      case 'change_theme':
        setCurrentTheme(command.theme);
        applyTheme(THEMES[command.theme].tokens);
        break;
    }
    
    setTimeout(() => setIsAIControlled(false), 500);
  };

  // Record interactions for learning
  const startInteractionRecording = () => {
    const recordInteraction = (type, details) => {
      invoke('record_interaction', {
        interaction: {
          timestamp: Date.now(),
          type,
          details,
          success: true
        }
      });
    };

    // Record clicks
    document.addEventListener('click', (e) => {
      if (e.target.closest('button, .clickable')) {
        recordInteraction('click', {
          target: e.target.id || e.target.className
        });
      }
    });

    // Record searches
    document.addEventListener('search', (e) => {
      recordInteraction('search', e.detail);
    });
  };

  return (
    <div class="app">
      <header class="app-header">
        <div class="logo">
          <span class="logo-icon">🌟</span>
          <h1>Luminous Nix</h1>
          <span class="tagline">Consciousness-First NixOS</span>
        </div>
        
        <div class="controls">
          <div class="layout-selector">
            <label>Layout:</label>
            <select 
              value={currentLayout()} 
              onChange={(e) => switchLayout(e.target.value)}
            >
              {Object.entries(LAYOUTS).map(([key, layout]) => (
                <option value={key}>{layout.name}</option>
              ))}
            </select>
          </div>
          
          <div class="theme-selector">
            <label>Theme:</label>
            <select 
              value={currentTheme()} 
              onChange={(e) => {
                setCurrentTheme(e.target.value);
                applyTheme(THEMES[e.target.value].tokens);
              }}
            >
              {Object.entries(THEMES).map(([key, theme]) => (
                <option value={key}>{theme.name}</option>
              ))}
            </select>
          </div>
          
          {isAIControlled() && (
            <div class="ai-indicator">
              <span class="pulse">🤖</span> AI Control Active
            </div>
          )}
        </div>
      </header>

      <main 
        id="component-container" 
        class="component-container"
        style={`display: grid; grid-template: ${LAYOUTS[currentLayout()].grid};`}
      >
        {LAYOUTS[currentLayout()].components.map(component => {
          switch(component) {
            case 'search-bar':
              return <search-bar></search-bar>;
            case 'results-list':
              return <results-list></results-list>;
            case 'consciousness-monitor':
              return <consciousness-monitor></consciousness-monitor>;
            default:
              return null;
          }
        })}
      </main>

      <footer class="app-footer">
        <div class="status">
          <span class="status-indicator">●</span> Connected
        </div>
        <div class="info">
          Components: {components().length} | 
          Layout: {LAYOUTS[currentLayout()].name} | 
          Theme: {THEMES[currentTheme()].name}
        </div>
      </footer>

      <style>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        body {
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          background: var(--bg-primary);
          color: var(--text-primary);
          min-height: 100vh;
          display: flex;
          flex-direction: column;
        }

        .app {
          display: flex;
          flex-direction: column;
          min-height: 100vh;
        }

        .app-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 24px;
          background: var(--bg-secondary);
          border-bottom: 1px solid var(--border-color);
        }

        .logo {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .logo-icon {
          font-size: 28px;
        }

        .logo h1 {
          font-size: 24px;
          font-weight: 600;
        }

        .tagline {
          font-size: 12px;
          color: var(--text-secondary);
          margin-left: 8px;
        }

        .controls {
          display: flex;
          gap: 24px;
          align-items: center;
        }

        .layout-selector,
        .theme-selector {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .layout-selector label,
        .theme-selector label {
          font-size: 14px;
          color: var(--text-secondary);
        }

        select {
          background: var(--bg-primary);
          color: var(--text-primary);
          border: 1px solid var(--border-color);
          padding: 6px 12px;
          border-radius: 6px;
          font-size: 14px;
          cursor: pointer;
        }

        .ai-indicator {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 16px;
          background: rgba(99, 102, 241, 0.1);
          border: 1px solid rgba(99, 102, 241, 0.3);
          border-radius: 8px;
          font-size: 14px;
        }

        .pulse {
          animation: pulse 1s infinite;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        .component-container {
          flex: 1;
          padding: 24px;
          gap: 24px;
        }

        .app-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 24px;
          background: var(--bg-secondary);
          border-top: 1px solid var(--border-color);
          font-size: 12px;
          color: var(--text-secondary);
        }

        .status {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .status-indicator {
          color: #10b981;
        }

        .info {
          display: flex;
          gap: 16px;
        }
      `}</style>
    </div>
  );
}

export default App;