/**
 * Integration code for help system
 * Add this to your main app.js
 */

import HelpSystem from './help/help-system.js';

// Initialize help system
export function initializeHelp() {
  const helpSystem = new HelpSystem({
    enableTooltips: true,
    enableTours: true,
    enableSearch: true,
    enableShortcuts: true,
    tooltipDelay: 500
  });

  // Make help system globally available
  window.nixosHelp = helpSystem;

  // Add data-help attributes to UI elements
  addHelpAttributes();

  // Start onboarding tour for first-time users
  checkFirstTimeUser();

  return helpSystem;
}

/**
 * Add help attributes to UI elements
 */
function addHelpAttributes() {
  // Dashboard elements
  document.querySelector('.dashboard')?.setAttribute('data-help', 'dashboard-overview');
  
  // Package management
  document.querySelector('.package-search')?.setAttribute('data-help', 'package-search');
  document.querySelector('.package-install-btn')?.setAttribute('data-help', 'package-install');
  
  // Configuration
  document.querySelector('.config-editor')?.setAttribute('data-help', 'config-editor');
  document.querySelector('.config-validate-btn')?.setAttribute('data-help', 'config-validate');
  
  // Services
  document.querySelector('.service-list')?.setAttribute('data-help', 'service-control');
  document.querySelector('.service-logs')?.setAttribute('data-help', 'service-logs');
  
  // Generations
  document.querySelector('.generation-list')?.setAttribute('data-help', 'generation-overview');
  document.querySelector('.generation-switch-btn')?.setAttribute('data-help', 'generation-switch');
}

/**
 * Check if first-time user and show tour
 */
function checkFirstTimeUser() {
  const hasSeenTour = localStorage.getItem('nixos-gui:tour-completed');
  
  if (!hasSeenTour) {
    // Show welcome message
    setTimeout(() => {
      if (confirm('Welcome to NixOS GUI! Would you like a quick tour?')) {
        window.nixosHelp.startGuidedTour('first-time');
        
        // Mark tour as seen when completed
        const originalEndTour = window.nixosHelp.endTour;
        window.nixosHelp.endTour = function() {
          originalEndTour.call(this);
          localStorage.setItem('nixos-gui:tour-completed', 'true');
        };
      } else {
        localStorage.setItem('nixos-gui:tour-completed', 'skipped');
      }
    }, 1000);
  }
}

/**
 * Context-sensitive help
 */
export function showContextHelp(context) {
  const helpMap = {
    'package-not-found': 'troubleshoot-package-search',
    'build-failed': 'troubleshoot-build-error',
    'service-failed': 'service-troubleshoot',
    'config-invalid': 'config-validate',
    'permission-denied': 'security-permissions'
  };

  const helpId = helpMap[context];
  if (helpId) {
    window.nixosHelp.showHelp(helpId);
  }
}

/**
 * Add help menu to navigation
 */
export function addHelpMenu() {
  const nav = document.querySelector('.main-navigation');
  if (!nav) return;

  const helpMenu = document.createElement('div');
  helpMenu.className = 'help-menu';
  helpMenu.innerHTML = `
    <button class="help-menu-btn" aria-label="Help Menu">
      <span>Help</span>
      <span class="help-menu-arrow">▼</span>
    </button>
    <div class="help-menu-dropdown">
      <a href="#" data-help-action="tour-first-time">
        <i class="icon-tour"></i> Take a Tour
      </a>
      <a href="#" data-help-action="shortcuts">
        <i class="icon-keyboard"></i> Keyboard Shortcuts
      </a>
      <a href="#" data-help-action="search">
        <i class="icon-search"></i> Search Help
      </a>
      <div class="help-menu-divider"></div>
      <a href="#" data-help-action="docs">
        <i class="icon-book"></i> Documentation
      </a>
      <a href="#" data-help-action="support">
        <i class="icon-support"></i> Get Support
      </a>
    </div>
  `;

  nav.appendChild(helpMenu);

  // Add event handlers
  helpMenu.querySelector('.help-menu-btn').addEventListener('click', (e) => {
    e.stopPropagation();
    helpMenu.classList.toggle('active');
  });

  helpMenu.querySelectorAll('[data-help-action]').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const action = item.getAttribute('data-help-action');
      handleHelpAction(action);
      helpMenu.classList.remove('active');
    });
  });

  // Close on outside click
  document.addEventListener('click', () => {
    helpMenu.classList.remove('active');
  });
}

/**
 * Handle help menu actions
 */
function handleHelpAction(action) {
  switch (action) {
    case 'tour-first-time':
      window.nixosHelp.startGuidedTour('first-time');
      break;
    
    case 'shortcuts':
      window.nixosHelp.showHelpPanel();
      // Scroll to shortcuts section
      setTimeout(() => {
        document.querySelector('.help-shortcuts')?.scrollIntoView();
      }, 300);
      break;
    
    case 'search':
      window.nixosHelp.focusSearch();
      break;
    
    case 'docs':
      window.open('/docs/', '_blank');
      break;
    
    case 'support':
      window.open('https://discourse.nixos.org/', '_blank');
      break;
  }
}

/**
 * Add smart tooltips to form fields
 */
export function addSmartTooltips() {
  // Configuration editor
  const configFields = {
    'services.nginx.enable': 'Enable the Nginx web server',
    'networking.hostName': 'Set the system hostname',
    'time.timeZone': 'Set system timezone (e.g., "America/New_York")',
    'users.users': 'Define system users and their properties'
  };

  Object.entries(configFields).forEach(([field, tooltip]) => {
    const element = document.querySelector(`[data-config-field="${field}"]`);
    if (element) {
      element.setAttribute('data-help-tooltip', tooltip);
    }
  });
}

/**
 * Integrate with error handling
 */
export function integrateHelpWithErrors() {
  // Override error display to include help
  const originalShowError = window.showError;
  
  window.showError = function(error) {
    // Call original error handler
    if (originalShowError) {
      originalShowError(error);
    }

    // Add help button to error
    const errorElement = document.querySelector('.error-message');
    if (errorElement && !errorElement.querySelector('.error-help-btn')) {
      const helpBtn = document.createElement('button');
      helpBtn.className = 'error-help-btn';
      helpBtn.textContent = 'Get Help';
      helpBtn.onclick = () => showContextHelp(error.type || 'general-error');
      errorElement.appendChild(helpBtn);
    }
  };
}

/**
 * Tutorial mode for specific features
 */
export function startFeatureTutorial(feature) {
  const tutorials = {
    'package-install': {
      steps: [
        { selector: '.package-search', content: 'First, search for the package' },
        { selector: '.search-results', content: 'Review the search results' },
        { selector: '.install-btn', content: 'Click Install to add the package' },
        { selector: '.confirm-dialog', content: 'Confirm the installation' }
      ]
    },
    'config-edit': {
      steps: [
        { selector: '.config-editor', content: 'Edit your configuration here' },
        { selector: '.validate-btn', content: 'Always validate before applying' },
        { selector: '.diff-view', content: 'Review changes in diff view' },
        { selector: '.apply-btn', content: 'Apply changes to system' }
      ]
    }
  };

  const tutorial = tutorials[feature];
  if (tutorial) {
    // Create temporary tour
    window.nixosHelp.addTour(`tutorial-${feature}`, {
      name: `${feature} Tutorial`,
      description: 'Step-by-step guide',
      steps: tutorial.steps
    });
    
    window.nixosHelp.startGuidedTour(`tutorial-${feature}`);
  }
}

// Export help system instance for use in other modules
export const helpSystem = initializeHelp();