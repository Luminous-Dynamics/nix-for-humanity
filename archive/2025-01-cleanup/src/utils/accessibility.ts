// Accessibility utilities for Nix for Humanity

export function setupAccessibility() {
  // Set up keyboard navigation
  setupKeyboardNavigation();
  
  // Set up focus management
  setupFocusManagement();
  
  // Set up high contrast mode detection
  setupHighContrastDetection();
  
  // Set up reduced motion preferences
  setupReducedMotion();
}

function setupKeyboardNavigation() {
  // Global keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + / for help
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
      e.preventDefault();
      showHelp();
    }
    
    // Escape to cancel current operation
    if (e.key === 'Escape') {
      cancelCurrentOperation();
    }
    
    // Ctrl/Cmd + K to focus input
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      focusInput();
    }
  });
}

function setupFocusManagement() {
  // Ensure focus is visible
  document.documentElement.style.setProperty('--focus-outline', '2px solid #4a90e2');
  
  // Add focus-visible polyfill styles
  const style = document.createElement('style');
  style.textContent = `
    :focus {
      outline: var(--focus-outline);
      outline-offset: 2px;
    }
    
    :focus:not(:focus-visible) {
      outline: none;
    }
    
    :focus-visible {
      outline: var(--focus-outline);
      outline-offset: 2px;
    }
  `;
  document.head.appendChild(style);
}

function setupHighContrastDetection() {
  // Check for high contrast preference
  const highContrastQuery = window.matchMedia('(prefers-contrast: high)');
  
  function updateHighContrast(e: MediaQueryListEvent | MediaQueryList) {
    if (e.matches) {
      document.documentElement.classList.add('high-contrast');
    } else {
      document.documentElement.classList.remove('high-contrast');
    }
  }
  
  // Initial check
  updateHighContrast(highContrastQuery);
  
  // Listen for changes
  highContrastQuery.addEventListener('change', updateHighContrast);
}

function setupReducedMotion() {
  // Check for reduced motion preference
  const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  
  function updateReducedMotion(e: MediaQueryListEvent | MediaQueryList) {
    if (e.matches) {
      document.documentElement.classList.add('reduced-motion');
      // Disable all animations
      document.documentElement.style.setProperty('--animation-duration', '0.01ms');
    } else {
      document.documentElement.classList.remove('reduced-motion');
      document.documentElement.style.setProperty('--animation-duration', '300ms');
    }
  }
  
  // Initial check
  updateReducedMotion(reducedMotionQuery);
  
  // Listen for changes
  reducedMotionQuery.addEventListener('change', updateReducedMotion);
}

function showHelp() {
  // Create help dialog
  const helpDialog = document.createElement('dialog');
  helpDialog.setAttribute('role', 'dialog');
  helpDialog.setAttribute('aria-labelledby', 'help-title');
  helpDialog.innerHTML = `
    <h2 id="help-title">Nix for Humanity Help</h2>
    <h3>Keyboard Shortcuts</h3>
    <ul>
      <li><kbd>Ctrl/Cmd + K</kbd> - Focus input</li>
      <li><kbd>Ctrl/Cmd + /</kbd> - Show this help</li>
      <li><kbd>Escape</kbd> - Cancel operation</li>
      <li><kbd>Tab</kbd> - Navigate forward</li>
      <li><kbd>Shift + Tab</kbd> - Navigate backward</li>
    </ul>
    <h3>Natural Language Examples</h3>
    <ul>
      <li>"install firefox" - Install a package</li>
      <li>"update system" - Update NixOS</li>
      <li>"my wifi isn't working" - Troubleshoot</li>
      <li>"help" - Get assistance</li>
    </ul>
    <button onclick="this.closest('dialog').close()">Close (Escape)</button>
  `;
  
  document.body.appendChild(helpDialog);
  helpDialog.showModal();
  
  // Clean up on close
  helpDialog.addEventListener('close', () => {
    document.body.removeChild(helpDialog);
  });
}

function cancelCurrentOperation() {
  // Emit cancel event
  document.dispatchEvent(new CustomEvent('operation-cancelled'));
}

function focusInput() {
  // Find and focus the main input
  const input = document.querySelector('natural-language-input');
  if (input) {
    const shadowInput = input.shadowRoot?.querySelector('input');
    shadowInput?.focus();
  }
}

// Utility to announce messages to screen readers
export function announce(message: string, priority: 'polite' | 'assertive' = 'polite') {
  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', priority);
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only'; // Visually hidden
  announcement.textContent = message;
  
  document.body.appendChild(announcement);
  
  // Remove after announcement
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
}

// Check if user prefers reduced motion
export function prefersReducedMotion(): boolean {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

// Check if user prefers high contrast
export function prefersHighContrast(): boolean {
  return window.matchMedia('(prefers-contrast: high)').matches;
}