/**
 * Contextual Help System for NixOS GUI
 * Provides tooltips, tours, and inline help
 */

import { marked } from 'marked';

export class HelpSystem {
  constructor(options = {}) {
    this.options = {
      enableTooltips: true,
      enableTours: true,
      enableSearch: true,
      enableShortcuts: true,
      animationDuration: 200,
      tooltipDelay: 500,
      ...options
    };

    this.helpDatabase = new Map();
    this.tours = new Map();
    this.shortcuts = new Map();
    this.activeTooltip = null;
    this.activeTour = null;
    this.searchIndex = [];

    this.init();
  }

  async init() {
    // Load help content
    await this.loadHelpContent();
    
    // Initialize components
    if (this.options.enableTooltips) {
      this.initTooltips();
    }
    
    if (this.options.enableShortcuts) {
      this.initShortcuts();
    }

    // Create help UI elements
    this.createHelpUI();
    
    // Register global help toggle
    this.registerGlobalHelp();
  }

  async loadHelpContent() {
    try {
      const response = await fetch('/help/content.json');
      const content = await response.json();
      
      // Load help items
      content.items.forEach(item => {
        this.helpDatabase.set(item.id, item);
        this.searchIndex.push({
          id: item.id,
          title: item.title,
          content: item.content,
          tags: item.tags || []
        });
      });

      // Load tours
      content.tours.forEach(tour => {
        this.tours.set(tour.id, tour);
      });

      // Load shortcuts
      content.shortcuts.forEach(shortcut => {
        this.shortcuts.set(shortcut.key, shortcut);
      });
    } catch (error) {
      console.error('Failed to load help content:', error);
    }
  }

  /**
   * Initialize tooltip system
   */
  initTooltips() {
    // Create tooltip container
    this.tooltipContainer = document.createElement('div');
    this.tooltipContainer.className = 'help-tooltip';
    this.tooltipContainer.style.cssText = `
      position: absolute;
      z-index: 10000;
      display: none;
      max-width: 300px;
      padding: 8px 12px;
      background: rgba(0, 0, 0, 0.9);
      color: white;
      border-radius: 4px;
      font-size: 14px;
      line-height: 1.4;
      pointer-events: none;
      transition: opacity ${this.options.animationDuration}ms;
    `;
    document.body.appendChild(this.tooltipContainer);

    // Add event listeners
    document.addEventListener('mouseover', this.handleMouseOver.bind(this));
    document.addEventListener('mouseout', this.handleMouseOut.bind(this));
    document.addEventListener('mousemove', this.handleMouseMove.bind(this));
  }

  handleMouseOver(event) {
    const helpId = event.target.getAttribute('data-help');
    if (!helpId) return;

    // Clear existing timeout
    if (this.tooltipTimeout) {
      clearTimeout(this.tooltipTimeout);
    }

    // Show tooltip after delay
    this.tooltipTimeout = setTimeout(() => {
      this.showTooltip(helpId, event.target);
    }, this.options.tooltipDelay);
  }

  handleMouseOut(event) {
    if (this.tooltipTimeout) {
      clearTimeout(this.tooltipTimeout);
    }
    this.hideTooltip();
  }

  handleMouseMove(event) {
    if (this.activeTooltip) {
      this.positionTooltip(event.clientX, event.clientY);
    }
  }

  showTooltip(helpId, element) {
    const help = this.helpDatabase.get(helpId);
    if (!help) return;

    this.activeTooltip = help;
    this.tooltipContainer.innerHTML = help.tooltip || help.content;
    this.tooltipContainer.style.display = 'block';
    this.tooltipContainer.style.opacity = '0';

    // Position tooltip
    const rect = element.getBoundingClientRect();
    this.positionTooltip(rect.left + rect.width / 2, rect.top);

    // Fade in
    requestAnimationFrame(() => {
      this.tooltipContainer.style.opacity = '1';
    });
  }

  hideTooltip() {
    this.tooltipContainer.style.opacity = '0';
    setTimeout(() => {
      this.tooltipContainer.style.display = 'none';
      this.activeTooltip = null;
    }, this.options.animationDuration);
  }

  positionTooltip(x, y) {
    const tooltip = this.tooltipContainer;
    const padding = 10;
    
    // Calculate position
    let left = x - tooltip.offsetWidth / 2;
    let top = y - tooltip.offsetHeight - padding;

    // Adjust for viewport boundaries
    if (left < padding) left = padding;
    if (left + tooltip.offsetWidth > window.innerWidth - padding) {
      left = window.innerWidth - tooltip.offsetWidth - padding;
    }
    
    if (top < padding) {
      top = y + padding; // Show below instead
    }

    tooltip.style.left = `${left}px`;
    tooltip.style.top = `${top}px`;
  }

  /**
   * Create help UI components
   */
  createHelpUI() {
    // Help button
    this.createHelpButton();
    
    // Help panel
    this.createHelpPanel();
    
    // Search interface
    if (this.options.enableSearch) {
      this.createSearchInterface();
    }

    // Tour controls
    if (this.options.enableTours) {
      this.createTourControls();
    }
  }

  createHelpButton() {
    this.helpButton = document.createElement('button');
    this.helpButton.className = 'help-button';
    this.helpButton.innerHTML = '?';
    this.helpButton.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: #1976d2;
      color: white;
      border: none;
      font-size: 20px;
      cursor: pointer;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      z-index: 9999;
      transition: transform 0.2s;
    `;
    
    this.helpButton.addEventListener('click', () => {
      this.toggleHelpPanel();
    });
    
    document.body.appendChild(this.helpButton);
  }

  createHelpPanel() {
    this.helpPanel = document.createElement('div');
    this.helpPanel.className = 'help-panel';
    this.helpPanel.style.cssText = `
      position: fixed;
      top: 0;
      right: -400px;
      width: 400px;
      height: 100%;
      background: white;
      box-shadow: -2px 0 8px rgba(0,0,0,0.2);
      z-index: 9998;
      transition: right 0.3s;
      overflow-y: auto;
    `;

    this.helpPanel.innerHTML = `
      <div class="help-panel-header" style="padding: 20px; border-bottom: 1px solid #ddd;">
        <h2 style="margin: 0 0 10px 0;">Help & Documentation</h2>
        <button class="help-close" style="position: absolute; top: 20px; right: 20px; 
                background: none; border: none; font-size: 24px; cursor: pointer;">×</button>
      </div>
      <div class="help-panel-content" style="padding: 20px;">
        <div class="help-search"></div>
        <div class="help-categories"></div>
        <div class="help-tours"></div>
        <div class="help-shortcuts"></div>
      </div>
    `;

    document.body.appendChild(this.helpPanel);

    // Close button
    this.helpPanel.querySelector('.help-close').addEventListener('click', () => {
      this.hideHelpPanel();
    });
  }

  toggleHelpPanel() {
    if (this.helpPanel.style.right === '0px') {
      this.hideHelpPanel();
    } else {
      this.showHelpPanel();
    }
  }

  showHelpPanel() {
    this.helpPanel.style.right = '0px';
    this.helpButton.style.transform = 'rotate(180deg)';
    this.populateHelpPanel();
  }

  hideHelpPanel() {
    this.helpPanel.style.right = '-400px';
    this.helpButton.style.transform = 'rotate(0deg)';
  }

  populateHelpPanel() {
    // Populate categories
    const categories = this.getHelpCategories();
    const categoriesHtml = categories.map(cat => `
      <div class="help-category" style="margin-bottom: 20px;">
        <h3 style="margin-bottom: 10px;">${cat.name}</h3>
        <ul style="list-style: none; padding: 0;">
          ${cat.items.map(item => `
            <li style="margin-bottom: 5px;">
              <a href="#" class="help-link" data-help-id="${item.id}" 
                 style="color: #1976d2; text-decoration: none;">
                ${item.title}
              </a>
            </li>
          `).join('')}
        </ul>
      </div>
    `).join('');
    
    this.helpPanel.querySelector('.help-categories').innerHTML = categoriesHtml;

    // Add click handlers
    this.helpPanel.querySelectorAll('.help-link').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        this.showHelpItem(link.getAttribute('data-help-id'));
      });
    });

    // Populate tours
    if (this.tours.size > 0) {
      const toursHtml = `
        <h3>Interactive Tours</h3>
        <ul style="list-style: none; padding: 0;">
          ${Array.from(this.tours.values()).map(tour => `
            <li style="margin-bottom: 10px;">
              <button class="tour-button" data-tour-id="${tour.id}"
                      style="width: 100%; padding: 10px; text-align: left; 
                             background: #f5f5f5; border: 1px solid #ddd; 
                             border-radius: 4px; cursor: pointer;">
                <strong>${tour.name}</strong><br>
                <small>${tour.description}</small>
              </button>
            </li>
          `).join('')}
        </ul>
      `;
      
      this.helpPanel.querySelector('.help-tours').innerHTML = toursHtml;
      
      // Add tour click handlers
      this.helpPanel.querySelectorAll('.tour-button').forEach(button => {
        button.addEventListener('click', () => {
          this.startTour(button.getAttribute('data-tour-id'));
          this.hideHelpPanel();
        });
      });
    }

    // Populate shortcuts
    this.populateShortcuts();
  }

  getHelpCategories() {
    const categories = new Map();
    
    this.helpDatabase.forEach(item => {
      const category = item.category || 'General';
      if (!categories.has(category)) {
        categories.set(category, []);
      }
      categories.get(category).push(item);
    });

    return Array.from(categories.entries()).map(([name, items]) => ({
      name,
      items
    }));
  }

  showHelpItem(helpId) {
    const help = this.helpDatabase.get(helpId);
    if (!help) return;

    // Create help modal
    const modal = document.createElement('div');
    modal.className = 'help-modal';
    modal.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 600px;
      max-width: 90%;
      max-height: 80vh;
      background: white;
      border-radius: 8px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
      z-index: 10001;
      overflow: hidden;
    `;

    modal.innerHTML = `
      <div class="help-modal-header" style="padding: 20px; border-bottom: 1px solid #ddd;">
        <h2 style="margin: 0;">${help.title}</h2>
        <button class="modal-close" style="position: absolute; top: 20px; right: 20px;
                background: none; border: none; font-size: 24px; cursor: pointer;">×</button>
      </div>
      <div class="help-modal-content" style="padding: 20px; overflow-y: auto; max-height: 60vh;">
        ${marked(help.content)}
        ${help.example ? `
          <h3>Example</h3>
          <pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto;">
${help.example}</pre>
        ` : ''}
        ${help.related ? `
          <h3>Related Topics</h3>
          <ul>
            ${help.related.map(id => {
              const related = this.helpDatabase.get(id);
              return related ? `
                <li><a href="#" class="help-link" data-help-id="${id}">${related.title}</a></li>
              ` : '';
            }).join('')}
          </ul>
        ` : ''}
      </div>
    `;

    // Add backdrop
    const backdrop = document.createElement('div');
    backdrop.className = 'help-backdrop';
    backdrop.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0,0,0,0.5);
      z-index: 10000;
    `;

    document.body.appendChild(backdrop);
    document.body.appendChild(modal);

    // Close handlers
    const closeModal = () => {
      modal.remove();
      backdrop.remove();
    };

    modal.querySelector('.modal-close').addEventListener('click', closeModal);
    backdrop.addEventListener('click', closeModal);

    // Handle related links
    modal.querySelectorAll('.help-link').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        closeModal();
        this.showHelpItem(link.getAttribute('data-help-id'));
      });
    });
  }

  /**
   * Interactive tour system
   */
  startTour(tourId) {
    const tour = this.tours.get(tourId);
    if (!tour || this.activeTour) return;

    this.activeTour = {
      tour,
      currentStep: 0
    };

    this.showTourStep();
  }

  showTourStep() {
    if (!this.activeTour) return;

    const { tour, currentStep } = this.activeTour;
    const step = tour.steps[currentStep];

    // Find target element
    const target = document.querySelector(step.selector);
    if (!target) {
      console.error(`Tour target not found: ${step.selector}`);
      this.nextTourStep();
      return;
    }

    // Create tour popover
    const popover = document.createElement('div');
    popover.className = 'tour-popover';
    popover.style.cssText = `
      position: absolute;
      z-index: 10002;
      background: white;
      border-radius: 8px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
      padding: 20px;
      max-width: 400px;
    `;

    popover.innerHTML = `
      <h3 style="margin: 0 0 10px 0;">${step.title}</h3>
      <p style="margin: 0 0 15px 0;">${step.content}</p>
      <div class="tour-controls" style="display: flex; justify-content: space-between;">
        <button class="tour-skip" style="background: none; border: none; 
                color: #666; cursor: pointer;">Skip Tour</button>
        <div>
          <span style="color: #666; margin-right: 10px;">
            ${currentStep + 1} / ${tour.steps.length}
          </span>
          ${currentStep > 0 ? `
            <button class="tour-prev" style="margin-right: 10px; padding: 5px 15px;
                    background: #f5f5f5; border: 1px solid #ddd; 
                    border-radius: 4px; cursor: pointer;">Previous</button>
          ` : ''}
          <button class="tour-next" style="padding: 5px 15px; background: #1976d2;
                  color: white; border: none; border-radius: 4px; cursor: pointer;">
            ${currentStep < tour.steps.length - 1 ? 'Next' : 'Finish'}
          </button>
        </div>
      </div>
    `;

    // Highlight target
    target.classList.add('tour-highlight');
    target.style.position = 'relative';
    target.style.zIndex = '10001';

    // Position popover
    const rect = target.getBoundingClientRect();
    document.body.appendChild(popover);
    
    const popoverRect = popover.getBoundingClientRect();
    let top = rect.bottom + 10;
    let left = rect.left;

    // Adjust position
    if (top + popoverRect.height > window.innerHeight) {
      top = rect.top - popoverRect.height - 10;
    }
    if (left + popoverRect.width > window.innerWidth) {
      left = window.innerWidth - popoverRect.width - 10;
    }

    popover.style.top = `${top}px`;
    popover.style.left = `${left}px`;

    // Add event handlers
    popover.querySelector('.tour-skip').addEventListener('click', () => {
      this.endTour();
    });

    popover.querySelector('.tour-next').addEventListener('click', () => {
      this.nextTourStep();
    });

    const prevButton = popover.querySelector('.tour-prev');
    if (prevButton) {
      prevButton.addEventListener('click', () => {
        this.prevTourStep();
      });
    }

    // Store popover reference
    this.activeTour.popover = popover;

    // Scroll to element
    target.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  nextTourStep() {
    if (!this.activeTour) return;

    this.clearTourStep();
    this.activeTour.currentStep++;

    if (this.activeTour.currentStep >= this.activeTour.tour.steps.length) {
      this.endTour();
    } else {
      this.showTourStep();
    }
  }

  prevTourStep() {
    if (!this.activeTour || this.activeTour.currentStep === 0) return;

    this.clearTourStep();
    this.activeTour.currentStep--;
    this.showTourStep();
  }

  clearTourStep() {
    if (!this.activeTour) return;

    // Remove popover
    if (this.activeTour.popover) {
      this.activeTour.popover.remove();
    }

    // Remove highlights
    document.querySelectorAll('.tour-highlight').forEach(el => {
      el.classList.remove('tour-highlight');
      el.style.position = '';
      el.style.zIndex = '';
    });
  }

  endTour() {
    this.clearTourStep();
    this.activeTour = null;

    // Show completion message
    this.showNotification('Tour completed!', 'success');
  }

  /**
   * Keyboard shortcuts
   */
  initShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Check if in input field
      if (e.target.matches('input, textarea, select')) return;

      const key = this.getShortcutKey(e);
      const shortcut = this.shortcuts.get(key);

      if (shortcut) {
        e.preventDefault();
        this.executeShortcut(shortcut);
      }
    });
  }

  getShortcutKey(event) {
    const parts = [];
    if (event.ctrlKey) parts.push('ctrl');
    if (event.altKey) parts.push('alt');
    if (event.shiftKey) parts.push('shift');
    if (event.metaKey) parts.push('meta');
    parts.push(event.key.toLowerCase());
    return parts.join('+');
  }

  executeShortcut(shortcut) {
    switch (shortcut.action) {
      case 'help':
        this.toggleHelpPanel();
        break;
      case 'search':
        this.focusSearch();
        break;
      case 'tour':
        this.startTour(shortcut.tourId);
        break;
      case 'navigate':
        window.location.hash = shortcut.target;
        break;
      default:
        // Custom action
        if (shortcut.callback) {
          shortcut.callback();
        }
    }
  }

  populateShortcuts() {
    const shortcutsHtml = `
      <h3>Keyboard Shortcuts</h3>
      <table style="width: 100%; border-collapse: collapse;">
        ${Array.from(this.shortcuts.entries()).map(([key, shortcut]) => `
          <tr>
            <td style="padding: 5px; border-bottom: 1px solid #eee;">
              <kbd style="background: #f5f5f5; padding: 2px 6px; 
                   border-radius: 3px; font-family: monospace;">
                ${key.replace(/\+/g, ' + ')}
              </kbd>
            </td>
            <td style="padding: 5px; border-bottom: 1px solid #eee;">
              ${shortcut.description}
            </td>
          </tr>
        `).join('')}
      </table>
    `;

    this.helpPanel.querySelector('.help-shortcuts').innerHTML = shortcutsHtml;
  }

  /**
   * Search functionality
   */
  createSearchInterface() {
    const searchHtml = `
      <div class="help-search-box" style="margin-bottom: 20px;">
        <input type="search" class="help-search-input" placeholder="Search help..."
               style="width: 100%; padding: 10px; border: 1px solid #ddd; 
                      border-radius: 4px; font-size: 14px;">
        <div class="help-search-results" style="margin-top: 10px; display: none;"></div>
      </div>
    `;

    this.helpPanel.querySelector('.help-search').innerHTML = searchHtml;

    const searchInput = this.helpPanel.querySelector('.help-search-input');
    const searchResults = this.helpPanel.querySelector('.help-search-results');

    // Debounced search
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        this.performSearch(e.target.value, searchResults);
      }, 300);
    });
  }

  performSearch(query, resultsContainer) {
    if (!query || query.length < 2) {
      resultsContainer.style.display = 'none';
      return;
    }

    const results = this.searchIndex.filter(item => {
      const searchText = `${item.title} ${item.content} ${item.tags.join(' ')}`.toLowerCase();
      return searchText.includes(query.toLowerCase());
    });

    if (results.length === 0) {
      resultsContainer.innerHTML = '<p style="color: #666;">No results found</p>';
    } else {
      resultsContainer.innerHTML = `
        <ul style="list-style: none; padding: 0; margin: 0;">
          ${results.slice(0, 10).map(item => `
            <li style="margin-bottom: 10px; padding-bottom: 10px; 
                       border-bottom: 1px solid #eee;">
              <a href="#" class="search-result-link" data-help-id="${item.id}"
                 style="color: #1976d2; text-decoration: none;">
                <strong>${this.highlightMatch(item.title, query)}</strong>
              </a>
              <div style="color: #666; font-size: 12px; margin-top: 4px;">
                ${this.truncateText(item.content, 100)}
              </div>
            </li>
          `).join('')}
        </ul>
      `;

      // Add click handlers
      resultsContainer.querySelectorAll('.search-result-link').forEach(link => {
        link.addEventListener('click', (e) => {
          e.preventDefault();
          this.showHelpItem(link.getAttribute('data-help-id'));
          resultsContainer.style.display = 'none';
        });
      });
    }

    resultsContainer.style.display = 'block';
  }

  highlightMatch(text, query) {
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
  }

  truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  }

  focusSearch() {
    this.showHelpPanel();
    setTimeout(() => {
      const searchInput = this.helpPanel.querySelector('.help-search-input');
      if (searchInput) searchInput.focus();
    }, 300);
  }

  /**
   * Global help mode
   */
  registerGlobalHelp() {
    // F1 for help
    document.addEventListener('keydown', (e) => {
      if (e.key === 'F1') {
        e.preventDefault();
        this.toggleHelpPanel();
      }
    });

    // Alt+Shift+H for help mode
    document.addEventListener('keydown', (e) => {
      if (e.altKey && e.shiftKey && e.key === 'H') {
        e.preventDefault();
        this.toggleHelpMode();
      }
    });
  }

  toggleHelpMode() {
    document.body.classList.toggle('help-mode');
    
    if (document.body.classList.contains('help-mode')) {
      this.showNotification('Help mode activated. Click any element to see help.', 'info');
      document.addEventListener('click', this.helpModeClick);
    } else {
      this.showNotification('Help mode deactivated.', 'info');
      document.removeEventListener('click', this.helpModeClick);
    }
  }

  helpModeClick = (e) => {
    e.preventDefault();
    e.stopPropagation();

    const helpId = e.target.getAttribute('data-help') || 
                   e.target.closest('[data-help]')?.getAttribute('data-help');

    if (helpId) {
      this.showHelpItem(helpId);
    } else {
      this.showNotification('No help available for this element.', 'warning');
    }
  };

  /**
   * Utility methods
   */
  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `help-notification help-notification-${type}`;
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 15px 20px;
      background: ${type === 'success' ? '#4caf50' : type === 'warning' ? '#ff9800' : '#2196f3'};
      color: white;
      border-radius: 4px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      z-index: 10003;
      animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
      notification.style.animation = 'slideOut 0.3s ease-in';
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }

  /**
   * Public API
   */
  addHelpItem(id, helpData) {
    this.helpDatabase.set(id, helpData);
    this.searchIndex.push({
      id,
      title: helpData.title,
      content: helpData.content,
      tags: helpData.tags || []
    });
  }

  addTour(id, tourData) {
    this.tours.set(id, tourData);
  }

  addShortcut(key, shortcutData) {
    this.shortcuts.set(key, shortcutData);
  }

  showHelp(helpId) {
    this.showHelpItem(helpId);
  }

  startGuidedTour(tourId) {
    this.startTour(tourId);
  }
}

// Export for use
export default HelpSystem;