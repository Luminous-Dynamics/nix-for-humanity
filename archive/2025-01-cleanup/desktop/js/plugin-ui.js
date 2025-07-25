/**
 * Frontend UI for plugin system
 * Handles plugin management interface and integration
 */

export class PluginUI {
  constructor(api) {
    this.api = api;
    this.plugins = new Map();
    this.widgets = new Map();
    this.menuItems = new Map();
    this.ws = null;
  }

  /**
   * Initialize plugin UI
   */
  async initialize() {
    // Load plugin list
    await this.loadPlugins();
    
    // Set up WebSocket connection
    this.connectWebSocket();
    
    // Set up UI elements
    this.setupPluginManager();
    
    // Load UI elements from active plugins
    await this.loadPluginUIElements();
  }

  /**
   * Connect to plugin WebSocket
   */
  connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    this.ws = new WebSocket(`${protocol}//${window.location.host}/plugins`);

    this.ws.onopen = () => {
      console.log('Plugin WebSocket connected');
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handlePluginEvent(data);
    };

    this.ws.onerror = (error) => {
      console.error('Plugin WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('Plugin WebSocket disconnected');
      // Reconnect after delay
      setTimeout(() => this.connectWebSocket(), 5000);
    };
  }

  /**
   * Handle plugin events from WebSocket
   */
  handlePluginEvent(event) {
    switch (event.type) {
      case 'notification':
        this.showNotification(event.data);
        break;
        
      case 'widget.update':
        this.updateWidget(event.data);
        break;
        
      case 'plugin.loaded':
        this.onPluginLoaded(event.data);
        break;
        
      case 'plugin.unloaded':
        this.onPluginUnloaded(event.data);
        break;
        
      default:
        console.log('Unknown plugin event:', event);
    }
  }

  /**
   * Load plugin list
   */
  async loadPlugins() {
    try {
      const response = await this.api.get('/api/plugins');
      const { plugins } = response;
      
      this.plugins.clear();
      plugins.forEach(plugin => {
        this.plugins.set(plugin.id, plugin);
      });
      
      this.renderPluginList();
    } catch (error) {
      console.error('Failed to load plugins:', error);
    }
  }

  /**
   * Load UI elements from plugins
   */
  async loadPluginUIElements() {
    try {
      const response = await this.api.get('/api/plugins/ui/elements');
      const { menuItems, widgets } = response;
      
      // Add menu items
      menuItems.forEach(item => {
        this.addMenuItem(item);
      });
      
      // Add widgets
      widgets.forEach(widget => {
        this.addWidget(widget);
      });
    } catch (error) {
      console.error('Failed to load plugin UI elements:', error);
    }
  }

  /**
   * Set up plugin manager UI
   */
  setupPluginManager() {
    // Add plugins tab
    const tab = document.createElement('div');
    tab.className = 'tab';
    tab.innerHTML = `
      <input type="radio" name="tabs" id="plugins-tab">
      <label for="plugins-tab">
        <i class="icon-puzzle"></i>
        Plugins
      </label>
      <div class="tab-content" id="plugins-content">
        <div class="plugins-manager">
          <div class="plugins-header">
            <h2>Plugin Manager</h2>
            <button class="btn btn-primary" onclick="pluginUI.showInstallDialog()">
              <i class="icon-plus"></i> Install Plugin
            </button>
          </div>
          <div class="plugins-list" id="plugins-list">
            <!-- Plugin list will be rendered here -->
          </div>
        </div>
      </div>
    `;
    
    document.querySelector('.tabs').appendChild(tab);
  }

  /**
   * Render plugin list
   */
  renderPluginList() {
    const listEl = document.getElementById('plugins-list');
    if (!listEl) return;

    const pluginsHtml = Array.from(this.plugins.values()).map(plugin => `
      <div class="plugin-item ${plugin.enabled ? 'enabled' : 'disabled'}" data-plugin-id="${plugin.id}">
        <div class="plugin-header">
          <h3>${plugin.name}</h3>
          <span class="plugin-version">v${plugin.version}</span>
        </div>
        <p class="plugin-description">${plugin.description || 'No description'}</p>
        <div class="plugin-meta">
          <span class="plugin-author">by ${plugin.author}</span>
          <span class="plugin-status status-${plugin.status}">${plugin.status}</span>
        </div>
        <div class="plugin-actions">
          ${plugin.enabled ? `
            <button class="btn btn-sm" onclick="pluginUI.disablePlugin('${plugin.id}')">
              Disable
            </button>
            <button class="btn btn-sm" onclick="pluginUI.showSettings('${plugin.id}')">
              Settings
            </button>
          ` : `
            <button class="btn btn-sm btn-primary" onclick="pluginUI.enablePlugin('${plugin.id}')">
              Enable
            </button>
          `}
          <button class="btn btn-sm btn-danger" onclick="pluginUI.uninstallPlugin('${plugin.id}')">
            Uninstall
          </button>
        </div>
      </div>
    `).join('');

    listEl.innerHTML = pluginsHtml || '<p class="empty-state">No plugins installed</p>';
  }

  /**
   * Enable a plugin
   */
  async enablePlugin(pluginId) {
    try {
      await this.api.post(`/api/plugins/${pluginId}/enable`);
      await this.loadPlugins();
      this.showNotification({
        message: 'Plugin enabled successfully',
        type: 'success'
      });
    } catch (error) {
      this.showNotification({
        message: `Failed to enable plugin: ${error.message}`,
        type: 'error'
      });
    }
  }

  /**
   * Disable a plugin
   */
  async disablePlugin(pluginId) {
    try {
      await this.api.post(`/api/plugins/${pluginId}/disable`);
      await this.loadPlugins();
      this.showNotification({
        message: 'Plugin disabled successfully',
        type: 'success'
      });
    } catch (error) {
      this.showNotification({
        message: `Failed to disable plugin: ${error.message}`,
        type: 'error'
      });
    }
  }

  /**
   * Uninstall a plugin
   */
  async uninstallPlugin(pluginId) {
    if (!confirm(`Are you sure you want to uninstall the plugin "${pluginId}"?`)) {
      return;
    }

    try {
      await this.api.delete(`/api/plugins/${pluginId}`);
      await this.loadPlugins();
      this.showNotification({
        message: 'Plugin uninstalled successfully',
        type: 'success'
      });
    } catch (error) {
      this.showNotification({
        message: `Failed to uninstall plugin: ${error.message}`,
        type: 'error'
      });
    }
  }

  /**
   * Show plugin settings
   */
  async showSettings(pluginId) {
    const plugin = this.plugins.get(pluginId);
    if (!plugin) return;

    try {
      const response = await this.api.get(`/api/plugins/${pluginId}/settings`);
      const { settings } = response;

      const dialog = this.createDialog({
        title: `${plugin.name} Settings`,
        content: this.renderSettingsForm(plugin, settings),
        buttons: [
          {
            label: 'Save',
            primary: true,
            action: async () => {
              const newSettings = this.getSettingsFromForm();
              await this.saveSettings(pluginId, newSettings);
              dialog.close();
            }
          },
          {
            label: 'Cancel',
            action: () => dialog.close()
          }
        ]
      });
    } catch (error) {
      this.showNotification({
        message: `Failed to load settings: ${error.message}`,
        type: 'error'
      });
    }
  }

  /**
   * Show install plugin dialog
   */
  showInstallDialog() {
    const dialog = this.createDialog({
      title: 'Install Plugin',
      content: `
        <div class="install-plugin-form">
          <div class="form-group">
            <label>Plugin URL or Path</label>
            <input type="text" id="plugin-source" placeholder="https://example.com/plugin.tar.gz">
          </div>
          <div class="form-group">
            <label>Or browse plugin marketplace</label>
            <button class="btn btn-secondary" onclick="pluginUI.browseMarketplace()">
              Browse Marketplace
            </button>
          </div>
        </div>
      `,
      buttons: [
        {
          label: 'Install',
          primary: true,
          action: async () => {
            const source = document.getElementById('plugin-source').value;
            if (source) {
              await this.installPlugin(source);
              dialog.close();
            }
          }
        },
        {
          label: 'Cancel',
          action: () => dialog.close()
        }
      ]
    });
  }

  /**
   * Install a plugin
   */
  async installPlugin(source) {
    try {
      const isUrl = source.startsWith('http://') || source.startsWith('https://');
      const payload = isUrl ? { packageUrl: source } : { packagePath: source };
      
      await this.api.post('/api/plugins/install', payload);
      await this.loadPlugins();
      
      this.showNotification({
        message: 'Plugin installed successfully',
        type: 'success'
      });
    } catch (error) {
      this.showNotification({
        message: `Failed to install plugin: ${error.message}`,
        type: 'error'
      });
    }
  }

  /**
   * Add menu item from plugin
   */
  addMenuItem(item) {
    const menu = document.querySelector(`.menu-${item.parent || 'plugins'}`);
    if (!menu) return;

    const menuItem = document.createElement('li');
    menuItem.className = 'plugin-menu-item';
    menuItem.dataset.pluginId = item.pluginId;
    menuItem.innerHTML = `
      <a href="#" onclick="pluginUI.executeAction('${item.pluginId}', '${item.action}')">
        <i class="icon-${item.icon || 'puzzle'}"></i>
        ${item.label}
      </a>
    `;

    menu.appendChild(menuItem);
    this.menuItems.set(item.id, menuItem);
  }

  /**
   * Add widget from plugin
   */
  addWidget(widget) {
    const dashboard = document.querySelector('.dashboard-widgets');
    if (!dashboard) return;

    const widgetEl = document.createElement('div');
    widgetEl.className = `widget widget-${widget.size || 'medium'} plugin-widget`;
    widgetEl.dataset.widgetId = widget.id;
    widgetEl.dataset.pluginId = widget.pluginId;
    widgetEl.innerHTML = `
      <div class="widget-header">
        <h3>${widget.title}</h3>
        <button class="widget-close" onclick="pluginUI.removeWidget('${widget.id}')">×</button>
      </div>
      <div class="widget-content">
        ${widget.component.template || '<p>Loading...</p>'}
      </div>
    `;

    // Add custom styles
    if (widget.component.styles) {
      const style = document.createElement('style');
      style.textContent = widget.component.styles;
      widgetEl.appendChild(style);
    }

    dashboard.appendChild(widgetEl);
    this.widgets.set(widget.id, widgetEl);

    // Set up refresh interval
    if (widget.refreshInterval) {
      setInterval(() => {
        this.refreshWidget(widget.id);
      }, widget.refreshInterval);
    }
  }

  /**
   * Update widget content
   */
  updateWidget(data) {
    const widget = this.widgets.get(data.widgetId);
    if (!widget) return;

    const content = widget.querySelector('.widget-content');
    if (content && data.data) {
      // Update widget with new data
      if (data.data.html) {
        content.innerHTML = data.data.html;
      } else {
        // Update specific elements
        Object.entries(data.data).forEach(([key, value]) => {
          const el = content.querySelector(`#${key}`);
          if (el) el.textContent = value;
        });
      }
    }
  }

  /**
   * Execute plugin action
   */
  async executeAction(pluginId, action) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'plugin.action',
        pluginId,
        action,
        params: {}
      }));
    }
  }

  /**
   * Show notification
   */
  showNotification(data) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${data.type || 'info'}`;
    notification.innerHTML = `
      <div class="notification-content">
        <p>${data.message}</p>
        ${data.actions ? data.actions.map(action => `
          <button class="notification-action" onclick="pluginUI.handleNotificationAction('${action.action}')">
            ${action.label}
          </button>
        `).join('') : ''}
      </div>
      <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;

    document.body.appendChild(notification);

    // Auto-remove after duration
    if (data.duration !== 0) {
      setTimeout(() => {
        notification.remove();
      }, data.duration || 5000);
    }
  }

  /**
   * Helper: Create dialog
   */
  createDialog(options) {
    const dialog = document.createElement('div');
    dialog.className = 'dialog-overlay';
    dialog.innerHTML = `
      <div class="dialog">
        <div class="dialog-header">
          <h3>${options.title}</h3>
          <button class="dialog-close" onclick="this.closest('.dialog-overlay').remove()">×</button>
        </div>
        <div class="dialog-content">
          ${options.content}
        </div>
        <div class="dialog-footer">
          ${options.buttons.map(btn => `
            <button class="btn ${btn.primary ? 'btn-primary' : ''}">${btn.label}</button>
          `).join('')}
        </div>
      </div>
    `;

    // Set up button actions
    const buttons = dialog.querySelectorAll('.dialog-footer button');
    options.buttons.forEach((btn, index) => {
      buttons[index].onclick = btn.action;
    });

    document.body.appendChild(dialog);

    return {
      close: () => dialog.remove()
    };
  }
}

// Create global instance
window.pluginUI = new PluginUI(window.api);