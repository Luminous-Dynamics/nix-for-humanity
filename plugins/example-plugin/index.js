/**
 * Example NixOS GUI Plugin
 * Demonstrates the plugin API capabilities
 */

class ExamplePlugin {
  constructor(api) {
    this.api = api;
    this.refreshInterval = null;
    this.widgetId = null;
  }

  /**
   * Plugin initialization
   */
  async initialize() {
    console.log('Example Plugin initializing...');

    // Register menu item
    await this.api.ui.registerMenuItem({
      label: 'Example Plugin',
      icon: 'puzzle-piece',
      action: 'showExampleDialog'
    });

    // Add dashboard widget
    this.widgetId = await this.api.ui.addWidget({
      title: 'Example Widget',
      component: this.createWidgetComponent(),
      size: 'small',
      refreshInterval: 60000
    });

    // Register settings
    await this.api.ui.registerSettings({
      title: 'Example Plugin Settings',
      description: 'Configure the example plugin behavior',
      schema: {
        refreshInterval: {
          type: 'number',
          label: 'Refresh Interval',
          description: 'How often to update the widget (ms)',
          min: 10000,
          max: 3600000,
          default: 60000
        },
        showNotifications: {
          type: 'boolean',
          label: 'Show Notifications',
          description: 'Display notifications for events',
          default: true
        }
      }
    });

    // Subscribe to events
    this.api.events.on('packages.installed', this.onPackageInstalled.bind(this));
    this.api.events.on('services.statusChanged', this.onServiceStatusChanged.bind(this));

    // Load saved data
    const savedData = await this.api.storage.get('widgetData');
    if (savedData) {
      console.log('Loaded saved data:', savedData);
    }

    // Start periodic updates
    this.startPeriodicUpdates();

    // Show welcome notification
    const settings = await this.api.storage.get('settings') || {};
    if (settings.showNotifications !== false) {
      await this.api.ui.notify('Example Plugin loaded successfully!', {
        type: 'success',
        duration: 3000
      });
    }
  }

  /**
   * Plugin cleanup
   */
  async cleanup() {
    console.log('Example Plugin cleaning up...');
    
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  }

  /**
   * Create widget component
   */
  createWidgetComponent() {
    return {
      template: `
        <div class="example-widget">
          <h3>System Stats</h3>
          <div class="stats">
            <div class="stat">
              <span class="label">Packages:</span>
              <span class="value" id="package-count">Loading...</span>
            </div>
            <div class="stat">
              <span class="label">Last Update:</span>
              <span class="value" id="last-update">Never</span>
            </div>
          </div>
          <button onclick="ExamplePlugin.refresh()">Refresh</button>
        </div>
      `,
      styles: `
        .example-widget {
          padding: 1rem;
        }
        .stats {
          margin: 1rem 0;
        }
        .stat {
          display: flex;
          justify-content: space-between;
          margin: 0.5rem 0;
        }
        .label {
          font-weight: bold;
        }
        .value {
          color: #666;
        }
      `,
      scripts: {
        refresh: () => this.updateWidget()
      }
    };
  }

  /**
   * Start periodic widget updates
   */
  async startPeriodicUpdates() {
    const settings = await this.api.storage.get('settings') || {};
    const interval = settings.refreshInterval || 60000;

    this.refreshInterval = setInterval(() => {
      this.updateWidget();
    }, interval);

    // Initial update
    this.updateWidget();
  }

  /**
   * Update widget data
   */
  async updateWidget() {
    try {
      // Search for installed packages
      const packages = await this.api.system.searchPackages('');
      const packageCount = packages.length;

      // Update widget data
      const widgetData = {
        packageCount,
        lastUpdate: new Date().toLocaleTimeString()
      };

      // Save data
      await this.api.storage.set('widgetData', widgetData);

      // Emit event for UI update
      this.api.events.emit('widget.update', {
        widgetId: this.widgetId,
        data: widgetData
      });

      console.log('Widget updated:', widgetData);
    } catch (error) {
      console.error('Failed to update widget:', error);
    }
  }

  /**
   * Handle package installation events
   */
  async onPackageInstalled(event) {
    const settings = await this.api.storage.get('settings') || {};
    
    if (settings.showNotifications) {
      await this.api.ui.notify(`Package installed: ${event.data.packageName}`, {
        type: 'info',
        duration: 5000,
        actions: [
          {
            label: 'View Details',
            action: () => this.showPackageDetails(event.data.packageName)
          }
        ]
      });
    }

    // Update widget
    this.updateWidget();
  }

  /**
   * Handle service status changes
   */
  async onServiceStatusChanged(event) {
    const { serviceName, oldStatus, newStatus } = event.data;
    
    // Log status change
    const log = await this.api.storage.get('serviceLog') || [];
    log.push({
      timestamp: Date.now(),
      service: serviceName,
      oldStatus,
      newStatus
    });

    // Keep only last 100 entries
    if (log.length > 100) {
      log.splice(0, log.length - 100);
    }

    await this.api.storage.set('serviceLog', log);
  }

  /**
   * Show package details
   */
  async showPackageDetails(packageName) {
    // This would integrate with the UI to show a dialog
    console.log('Showing details for package:', packageName);
  }

  /**
   * Handle menu action
   */
  async showExampleDialog() {
    await this.api.ui.notify('Example dialog would appear here', {
      type: 'info',
      duration: 3000
    });
  }
}

// Export plugin class
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ExamplePlugin;
}