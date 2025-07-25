/**
 * NixOS GUI Plugin Runtime
 * Provides the actual implementation of plugin API calls
 */

import EventEmitter from 'events';
import fetch from 'node-fetch';
import { promises as fs } from 'fs';
import path from 'path';

export class PluginRuntime extends EventEmitter {
  constructor(pluginManager) {
    super();
    this.pluginManager = pluginManager;
    this.storage = new PluginStorage();
    this.uiRegistry = new UIRegistry();
    this.eventBus = new EventEmitter();
    this.httpWhitelist = new Set([
      'api.github.com',
      'registry.npmjs.org',
      'nixos.org',
      'cache.nixos.org'
    ]);
  }

  /**
   * UI Operations
   */
  ui = {
    registerMenuItem: async ({ pluginId, ...config }) => {
      const menuId = `${pluginId}-menu-${Date.now()}`;
      
      this.uiRegistry.registerMenuItem({
        id: menuId,
        pluginId,
        label: config.label,
        icon: config.icon,
        action: config.action,
        parent: config.parent || 'plugins',
        order: config.order || 100
      });

      this.emit('ui.menuItemRegistered', { pluginId, menuId });
      return menuId;
    },

    addWidget: async ({ pluginId, ...config }) => {
      const widgetId = `${pluginId}-widget-${Date.now()}`;
      
      this.uiRegistry.registerWidget({
        id: widgetId,
        pluginId,
        title: config.title,
        component: config.component,
        size: config.size || 'medium',
        position: config.position,
        refreshInterval: config.refreshInterval
      });

      this.emit('ui.widgetAdded', { pluginId, widgetId });
      return widgetId;
    },

    notify: async ({ pluginId, message, ...options }) => {
      const notification = {
        id: `${pluginId}-notif-${Date.now()}`,
        pluginId,
        message,
        type: options.type || 'info',
        duration: options.duration || 5000,
        actions: options.actions || []
      };

      this.emit('ui.notification', notification);
      return notification.id;
    },

    registerSettings: async ({ pluginId, ...config }) => {
      const settingsId = `${pluginId}-settings`;
      
      this.uiRegistry.registerSettings({
        id: settingsId,
        pluginId,
        title: config.title,
        description: config.description,
        schema: config.schema,
        defaults: config.defaults
      });

      this.emit('ui.settingsRegistered', { pluginId, settingsId });
      return settingsId;
    }
  };

  /**
   * System Operations
   */
  system = {
    searchPackages: async ({ query }) => {
      // Integration with package manager
      const response = await this._executeSystemCommand('nix-search', [query]);
      return this._parsePackageResults(response);
    },

    getServiceStatus: async ({ serviceName }) => {
      // Check if service name is safe
      if (!/^[a-zA-Z0-9-]+$/.test(serviceName)) {
        throw new Error('Invalid service name');
      }

      const response = await this._executeSystemCommand('systemctl', ['status', serviceName]);
      return this._parseServiceStatus(response);
    },

    getConfig: async ({ path }) => {
      // Validate config path
      const allowedPaths = [
        'services',
        'environment.systemPackages',
        'users',
        'networking'
      ];

      const isAllowed = allowedPaths.some(allowed => path.startsWith(allowed));
      if (!isAllowed) {
        throw new Error(`Access to config path '${path}' not allowed`);
      }

      // Read from configuration
      return this._readConfigValue(path);
    },

    exec: async ({ command, args, pluginId }) => {
      // Check if command is whitelisted for plugin
      const plugin = this.pluginManager.getPlugin(pluginId);
      const allowedCommands = plugin?.manifest?.allowedCommands || [];

      if (!allowedCommands.includes(command)) {
        throw new Error(`Command '${command}' not allowed for plugin ${pluginId}`);
      }

      // Execute with restrictions
      return await this._executeRestrictedCommand(command, args, pluginId);
    }
  };

  /**
   * Storage Operations
   */
  storage = {
    get: async ({ pluginId, key }) => {
      return await this.storage.get(pluginId, key);
    },

    set: async ({ pluginId, key, value }) => {
      return await this.storage.set(pluginId, key, value);
    },

    remove: async ({ pluginId, key }) => {
      return await this.storage.remove(pluginId, key);
    },

    keys: async ({ pluginId }) => {
      return await this.storage.keys(pluginId);
    }
  };

  /**
   * Event Operations
   */
  events = {
    on: ({ pluginId, event, handler }) => {
      const wrappedHandler = (...args) => {
        try {
          handler(...args);
        } catch (error) {
          console.error(`Event handler error in plugin ${pluginId}:`, error);
        }
      };

      this.eventBus.on(event, wrappedHandler);

      // Return unsubscribe function
      return () => {
        this.eventBus.off(event, wrappedHandler);
      };
    },

    emit: ({ pluginId, event, data }) => {
      // Emit with plugin context
      this.eventBus.emit(event, {
        pluginId,
        timestamp: Date.now(),
        data
      });
    }
  };

  /**
   * HTTP Operations
   */
  http = {
    request: async ({ pluginId, url, options = {} }) => {
      // Parse and validate URL
      const urlObj = new URL(url);
      
      // Check whitelist
      if (!this.httpWhitelist.has(urlObj.hostname)) {
        // Check if plugin has explicit permission
        const plugin = this.pluginManager.getPlugin(pluginId);
        const allowedHosts = plugin?.manifest?.allowedHosts || [];
        
        if (!allowedHosts.includes(urlObj.hostname)) {
          throw new Error(`HTTP request to ${urlObj.hostname} not allowed`);
        }
      }

      // Add timeout
      const timeout = options.timeout || 30000;
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      try {
        const response = await fetch(url, {
          ...options,
          signal: controller.signal,
          headers: {
            'User-Agent': `NixOS-GUI-Plugin/${pluginId}`,
            ...options.headers
          }
        });

        clearTimeout(timeoutId);

        return {
          ok: response.ok,
          status: response.status,
          statusText: response.statusText,
          headers: Object.fromEntries(response.headers),
          data: await response.json()
        };
      } catch (error) {
        clearTimeout(timeoutId);
        throw error;
      }
    }
  };

  /**
   * Hook Operations
   */
  hooks = {
    register: ({ pluginId, hookName, handler }) => {
      this.pluginManager.registerHook(hookName, handler, pluginId);
    }
  };

  /**
   * Audit logging
   */
  audit = {
    log: (action, details) => {
      this.emit('audit.log', {
        timestamp: new Date().toISOString(),
        action,
        details
      });
    }
  };

  /**
   * Private helper methods
   */

  async _executeSystemCommand(command, args) {
    // This would integrate with the privileged helper
    // For now, return mock data
    return { stdout: '', stderr: '', code: 0 };
  }

  _parsePackageResults(response) {
    // Parse nix search results
    return [];
  }

  _parseServiceStatus(response) {
    // Parse systemctl status output
    return {
      active: true,
      running: true,
      enabled: true,
      description: 'Service description'
    };
  }

  async _readConfigValue(path) {
    // Read from NixOS configuration
    // This would integrate with configuration management
    return null;
  }

  async _executeRestrictedCommand(command, args, pluginId) {
    // Execute command with restrictions
    // - Limited execution time
    // - Resource limits
    // - Sandboxed environment
    return { stdout: '', stderr: '', code: 0 };
  }
}

/**
 * Plugin Storage Implementation
 */
class PluginStorage {
  constructor() {
    this.storageDir = './plugin-storage';
    this.cache = new Map();
  }

  async _ensureDir(pluginId) {
    const dir = path.join(this.storageDir, pluginId);
    await fs.mkdir(dir, { recursive: true });
    return dir;
  }

  async get(pluginId, key) {
    const cacheKey = `${pluginId}:${key}`;
    
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    try {
      const dir = await this._ensureDir(pluginId);
      const filePath = path.join(dir, `${key}.json`);
      const data = await fs.readFile(filePath, 'utf8');
      const value = JSON.parse(data);
      
      this.cache.set(cacheKey, value);
      return value;
    } catch (error) {
      if (error.code === 'ENOENT') {
        return null;
      }
      throw error;
    }
  }

  async set(pluginId, key, value) {
    const cacheKey = `${pluginId}:${key}`;
    const dir = await this._ensureDir(pluginId);
    const filePath = path.join(dir, `${key}.json`);
    
    await fs.writeFile(filePath, JSON.stringify(value, null, 2));
    this.cache.set(cacheKey, value);
  }

  async remove(pluginId, key) {
    const cacheKey = `${pluginId}:${key}`;
    const dir = await this._ensureDir(pluginId);
    const filePath = path.join(dir, `${key}.json`);
    
    try {
      await fs.unlink(filePath);
      this.cache.delete(cacheKey);
    } catch (error) {
      if (error.code !== 'ENOENT') {
        throw error;
      }
    }
  }

  async keys(pluginId) {
    const dir = await this._ensureDir(pluginId);
    
    try {
      const files = await fs.readdir(dir);
      return files
        .filter(f => f.endsWith('.json'))
        .map(f => f.slice(0, -5));
    } catch {
      return [];
    }
  }
}

/**
 * UI Registry for managing plugin UI elements
 */
class UIRegistry {
  constructor() {
    this.menuItems = new Map();
    this.widgets = new Map();
    this.settings = new Map();
  }

  registerMenuItem(config) {
    this.menuItems.set(config.id, config);
  }

  registerWidget(config) {
    this.widgets.set(config.id, config);
  }

  registerSettings(config) {
    this.settings.set(config.id, config);
  }

  getMenuItems(pluginId = null) {
    if (pluginId) {
      return Array.from(this.menuItems.values())
        .filter(item => item.pluginId === pluginId);
    }
    return Array.from(this.menuItems.values());
  }

  getWidgets(pluginId = null) {
    if (pluginId) {
      return Array.from(this.widgets.values())
        .filter(widget => widget.pluginId === pluginId);
    }
    return Array.from(this.widgets.values());
  }

  removePluginUI(pluginId) {
    // Remove all UI elements for a plugin
    for (const [id, item] of this.menuItems) {
      if (item.pluginId === pluginId) {
        this.menuItems.delete(id);
      }
    }

    for (const [id, widget] of this.widgets) {
      if (widget.pluginId === pluginId) {
        this.widgets.delete(id);
      }
    }

    for (const [id, setting] of this.settings) {
      if (setting.pluginId === pluginId) {
        this.settings.delete(id);
      }
    }
  }
}