/**
 * 🚀 Quick Setup Helpers
 * One-line integration for existing projects
 */

import { SetupCeremony } from './SetupCeremony';
import { createBridge, NixOSGuiIntegration } from './NixOSGuiBridge';
import { createSetupCeremonyStore } from './StateManager';
import { ComponentFactory } from './components/ModularComponents';

/**
 * Quick setup for instant integration
 * @param containerId - ID of the HTML element to mount into
 * @param config - Optional configuration
 * @returns Integration instance for further customization
 */
export function quickSetup(
  containerId: string,
  config?: {
    nixosGuiUrl?: string;
    luminousNixUrl?: string;
    useWebSocket?: boolean;
    theme?: 'dark' | 'light' | 'high-contrast';
    startingStage?: string;
  }
): NixOSGuiIntegration {
  // Get container
  const container = document.getElementById(containerId);
  if (!container) {
    throw new Error(`Container element with ID '${containerId}' not found`);
  }

  // Apply theme if specified
  if (config?.theme) {
    document.body.setAttribute('data-theme', config.theme);
  }

  // Create bridge with config
  const bridge = createBridge({
    nixosGuiUrl: config?.nixosGuiUrl,
    luminousNixUrl: config?.luminousNixUrl,
    useWebSocket: config?.useWebSocket
  });

  // Create integration
  const integration = new NixOSGuiIntegration(bridge);

  // Inject styles
  injectStyles();

  // Create and start ceremony
  const ceremony = new SetupCeremony(container, bridge);
  
  if (config?.startingStage) {
    // Jump to specific stage if requested
    ceremony.goToStage(config.startingStage);
  } else {
    // Start from beginning
    ceremony.start();
  }

  // Return integration for further customization
  return integration;
}

/**
 * Setup wizard for guided integration
 * Shows a configuration UI before starting
 */
export async function setupWizard(containerId: string): Promise<void> {
  const container = document.getElementById(containerId);
  if (!container) {
    throw new Error(`Container element with ID '${containerId}' not found`);
  }

  // Inject styles first
  injectStyles();

  // Create wizard UI
  container.innerHTML = `
    <div class="setup-wizard">
      <h2>🌟 Luminous Nix Setup Wizard</h2>
      <p>Configure your setup experience</p>
      
      <div class="wizard-form">
        <div class="form-group">
          <label>Theme:</label>
          <select id="wizard-theme">
            <option value="dark">Dark (Default)</option>
            <option value="light">Light</option>
            <option value="high-contrast">High Contrast</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>Backend URL (nixos-gui):</label>
          <input type="text" id="wizard-nixos-url" value="http://localhost:8080" />
        </div>
        
        <div class="form-group">
          <label>Luminous Nix URL:</label>
          <input type="text" id="wizard-luminous-url" value="http://localhost:8888" />
        </div>
        
        <div class="form-group">
          <label>
            <input type="checkbox" id="wizard-websocket" checked />
            Enable real-time updates (WebSocket)
          </label>
        </div>
        
        <div class="form-group">
          <label>Starting Stage:</label>
          <select id="wizard-stage">
            <option value="">Welcome (Default)</option>
            <option value="profile">Profile Selection</option>
            <option value="packages">Package Selection</option>
            <option value="review">Review & Install</option>
          </select>
        </div>
        
        <div class="wizard-actions">
          <button id="wizard-start" class="btn-primary">Start Setup Ceremony</button>
          <button id="wizard-test" class="btn-secondary">Test Connection</button>
        </div>
        
        <div id="wizard-status" class="wizard-status"></div>
      </div>
    </div>
  `;

  // Add styles for wizard
  const wizardStyles = `
    <style>
      .setup-wizard {
        max-width: 600px;
        margin: 0 auto;
        padding: 2rem;
        background: var(--bg-secondary, #24283b);
        border-radius: 1rem;
        color: var(--text-primary, #c0caf5);
      }
      
      .setup-wizard h2 {
        color: var(--primary, #64ffda);
        margin-bottom: 1rem;
      }
      
      .wizard-form {
        margin-top: 2rem;
      }
      
      .form-group {
        margin-bottom: 1.5rem;
      }
      
      .form-group label {
        display: block;
        margin-bottom: 0.5rem;
        color: var(--text-secondary, #9aa5ce);
      }
      
      .form-group input[type="text"],
      .form-group select {
        width: 100%;
        padding: 0.5rem;
        background: var(--bg-primary, #1a1b26);
        border: 1px solid var(--bg-tertiary, #292e42);
        border-radius: 0.25rem;
        color: var(--text-primary, #c0caf5);
      }
      
      .form-group input[type="checkbox"] {
        margin-right: 0.5rem;
      }
      
      .wizard-actions {
        display: flex;
        gap: 1rem;
        margin-top: 2rem;
      }
      
      .wizard-status {
        margin-top: 1rem;
        padding: 1rem;
        border-radius: 0.25rem;
        display: none;
      }
      
      .wizard-status.success {
        display: block;
        background: var(--success, #9ece6a);
        color: var(--text-inverse, #1a1b26);
      }
      
      .wizard-status.error {
        display: block;
        background: var(--error, #f7768e);
        color: var(--text-inverse, #1a1b26);
      }
    </style>
  `;
  
  // Inject wizard styles
  const styleElement = document.createElement('div');
  styleElement.innerHTML = wizardStyles;
  document.head.appendChild(styleElement.firstElementChild!);

  // Setup event handlers
  document.getElementById('wizard-start')?.addEventListener('click', () => {
    const config = {
      theme: (document.getElementById('wizard-theme') as HTMLSelectElement).value as any,
      nixosGuiUrl: (document.getElementById('wizard-nixos-url') as HTMLInputElement).value,
      luminousNixUrl: (document.getElementById('wizard-luminous-url') as HTMLInputElement).value,
      useWebSocket: (document.getElementById('wizard-websocket') as HTMLInputElement).checked,
      startingStage: (document.getElementById('wizard-stage') as HTMLSelectElement).value || undefined
    };

    // Clear wizard and start ceremony
    container.innerHTML = '';
    quickSetup(containerId, config);
  });

  document.getElementById('wizard-test')?.addEventListener('click', async () => {
    const statusEl = document.getElementById('wizard-status')!;
    statusEl.className = 'wizard-status';
    statusEl.textContent = 'Testing connection...';
    statusEl.style.display = 'block';

    try {
      const nixosUrl = (document.getElementById('wizard-nixos-url') as HTMLInputElement).value;
      const luminousUrl = (document.getElementById('wizard-luminous-url') as HTMLInputElement).value;

      // Test connections
      const [nixosResponse, luminousResponse] = await Promise.allSettled([
        fetch(`${nixosUrl}/api/health`),
        fetch(`${luminousUrl}/api/health`)
      ]);

      let success = true;
      let message = '';

      if (nixosResponse.status === 'fulfilled' && nixosResponse.value.ok) {
        message += '✅ nixos-gui backend connected\n';
      } else {
        message += '❌ nixos-gui backend not reachable\n';
        success = false;
      }

      if (luminousResponse.status === 'fulfilled' && luminousResponse.value.ok) {
        message += '✅ Luminous Nix backend connected\n';
      } else {
        message += '⚠️ Luminous Nix backend not reachable (will use fallback)\n';
      }

      statusEl.className = success ? 'wizard-status success' : 'wizard-status error';
      statusEl.textContent = message;
    } catch (error) {
      statusEl.className = 'wizard-status error';
      statusEl.textContent = `Error: ${error}`;
    }
  });
}

/**
 * Inject required styles if not already present
 */
function injectStyles(): void {
  if (document.getElementById('setup-ceremony-styles')) {
    return; // Already injected
  }

  const link = document.createElement('link');
  link.id = 'setup-ceremony-styles';
  link.rel = 'stylesheet';
  
  // Try multiple possible paths
  const possiblePaths = [
    '/styles/SetupCeremony.css',
    './styles/SetupCeremony.css',
    '../styles/SetupCeremony.css',
    'node_modules/@luminous-nix/setup-ceremony/styles/SetupCeremony.css'
  ];

  // Try to find the correct path
  for (const path of possiblePaths) {
    // We'll use the first one for now, but in production this would test each
    link.href = path;
    break;
  }

  document.head.appendChild(link);

  // Also inject minimal inline styles as fallback
  const fallbackStyles = document.createElement('style');
  fallbackStyles.id = 'setup-ceremony-fallback-styles';
  fallbackStyles.textContent = `
    /* Fallback styles if CSS file not found */
    :root {
      --primary: #64ffda;
      --secondary: #7aa2f7;
      --bg-primary: #1a1b26;
      --bg-secondary: #24283b;
      --text-primary: #c0caf5;
      --text-secondary: #9aa5ce;
    }
    
    .ceremony-container {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--bg-primary);
      color: var(--text-primary);
      padding: 2rem;
      min-height: 100vh;
    }
    
    .btn-primary {
      background: var(--primary);
      color: var(--bg-primary);
      padding: 0.75rem 1.5rem;
      border: none;
      border-radius: 0.5rem;
      cursor: pointer;
      font-weight: 500;
    }
    
    .btn-secondary {
      background: var(--bg-secondary);
      color: var(--text-primary);
      padding: 0.75rem 1.5rem;
      border: 1px solid var(--primary);
      border-radius: 0.5rem;
      cursor: pointer;
    }
  `;
  document.head.appendChild(fallbackStyles);
}

/**
 * Create a single component
 */
export function createComponent(
  type: string,
  props: any,
  container?: HTMLElement
): any {
  let component;
  
  switch (type) {
    case 'ProfileCard':
      component = ComponentFactory.createProfileCard(
        props.profile,
        props.selected,
        props.onSelect
      );
      break;
    case 'PackageSelector':
      component = ComponentFactory.createPackageSelector(
        props.packages,
        props.category,
        props
      );
      break;
    case 'NaturalLanguageInput':
      component = ComponentFactory.createNaturalLanguageInput(props);
      break;
    case 'ConflictResolver':
      component = ComponentFactory.createConflictResolver(
        props.conflicts,
        props.onResolve
      );
      break;
    default:
      throw new Error(`Unknown component type: ${type}`);
  }
  
  if (container) {
    component.mount(container);
  }
  
  return component;
}

// Auto-initialize if data attribute is present
if (typeof window !== 'undefined' && document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    const autoSetup = document.querySelector('[data-luminous-nix-setup]');
    if (autoSetup) {
      const containerId = autoSetup.id || 'ceremony-container';
      const config = autoSetup.getAttribute('data-config');
      
      if (config === 'wizard') {
        setupWizard(containerId);
      } else {
        quickSetup(containerId, config ? JSON.parse(config) : undefined);
      }
    }
  });
}