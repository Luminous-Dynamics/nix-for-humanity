/**
 * NixOS GUI Plugin API
 * Provides a secure, sandboxed environment for extending GUI functionality
 */

export class PluginAPI {
  constructor(pluginId, sandbox) {
    this.pluginId = pluginId;
    this.sandbox = sandbox;
    this.version = '1.0.0';
    this.permissions = new Set();
  }

  /**
   * Core API Methods available to plugins
   */
  
  // UI Integration
  ui = {
    /**
     * Register a new menu item
     * @param {Object} config Menu item configuration
     * @returns {string} Menu item ID
     */
    registerMenuItem: (config) => {
      this._checkPermission('ui.menu');
      return this.sandbox.execute('ui.registerMenuItem', {
        pluginId: this.pluginId,
        ...config
      });
    },

    /**
     * Add a dashboard widget
     * @param {Object} config Widget configuration
     * @returns {string} Widget ID
     */
    addWidget: (config) => {
      this._checkPermission('ui.widget');
      return this.sandbox.execute('ui.addWidget', {
        pluginId: this.pluginId,
        ...config
      });
    },

    /**
     * Show a notification
     * @param {string} message Notification message
     * @param {Object} options Notification options
     */
    notify: (message, options = {}) => {
      this._checkPermission('ui.notify');
      return this.sandbox.execute('ui.notify', {
        pluginId: this.pluginId,
        message,
        ...options
      });
    },

    /**
     * Register a settings panel
     * @param {Object} config Settings configuration
     */
    registerSettings: (config) => {
      this._checkPermission('ui.settings');
      return this.sandbox.execute('ui.registerSettings', {
        pluginId: this.pluginId,
        ...config
      });
    }
  };

  // System Integration
  system = {
    /**
     * Search for packages
     * @param {string} query Search query
     * @returns {Promise<Array>} Search results
     */
    searchPackages: async (query) => {
      this._checkPermission('system.packages.read');
      return this.sandbox.execute('system.searchPackages', { query });
    },

    /**
     * Get service status
     * @param {string} serviceName Service name
     * @returns {Promise<Object>} Service status
     */
    getServiceStatus: async (serviceName) => {
      this._checkPermission('system.services.read');
      return this.sandbox.execute('system.getServiceStatus', { serviceName });
    },

    /**
     * Read configuration value
     * @param {string} path Configuration path
     * @returns {Promise<any>} Configuration value
     */
    getConfig: async (path) => {
      this._checkPermission('system.config.read');
      return this.sandbox.execute('system.getConfig', { path });
    },

    /**
     * Execute a system command (restricted)
     * @param {string} command Command to execute
     * @param {Array} args Command arguments
     * @returns {Promise<Object>} Command result
     */
    exec: async (command, args = []) => {
      this._checkPermission('system.exec');
      return this.sandbox.execute('system.exec', {
        command,
        args,
        pluginId: this.pluginId
      });
    }
  };

  // Data Storage
  storage = {
    /**
     * Get plugin-specific storage value
     * @param {string} key Storage key
     * @returns {Promise<any>} Stored value
     */
    get: async (key) => {
      this._checkPermission('storage.read');
      return this.sandbox.execute('storage.get', {
        pluginId: this.pluginId,
        key
      });
    },

    /**
     * Set plugin-specific storage value
     * @param {string} key Storage key
     * @param {any} value Value to store
     */
    set: async (key, value) => {
      this._checkPermission('storage.write');
      return this.sandbox.execute('storage.set', {
        pluginId: this.pluginId,
        key,
        value
      });
    },

    /**
     * Remove storage value
     * @param {string} key Storage key
     */
    remove: async (key) => {
      this._checkPermission('storage.write');
      return this.sandbox.execute('storage.remove', {
        pluginId: this.pluginId,
        key
      });
    },

    /**
     * List all keys
     * @returns {Promise<Array>} Storage keys
     */
    keys: async () => {
      this._checkPermission('storage.read');
      return this.sandbox.execute('storage.keys', {
        pluginId: this.pluginId
      });
    }
  };

  // Event System
  events = {
    /**
     * Subscribe to system events
     * @param {string} event Event name
     * @param {Function} handler Event handler
     * @returns {Function} Unsubscribe function
     */
    on: (event, handler) => {
      this._checkPermission('events.subscribe');
      return this.sandbox.execute('events.on', {
        pluginId: this.pluginId,
        event,
        handler
      });
    },

    /**
     * Emit a custom event
     * @param {string} event Event name
     * @param {any} data Event data
     */
    emit: (event, data) => {
      this._checkPermission('events.emit');
      return this.sandbox.execute('events.emit', {
        pluginId: this.pluginId,
        event: `plugin:${this.pluginId}:${event}`,
        data
      });
    }
  };

  // HTTP Client
  http = {
    /**
     * Make HTTP request (sandboxed)
     * @param {string} url Request URL
     * @param {Object} options Request options
     * @returns {Promise<Object>} Response
     */
    request: async (url, options = {}) => {
      this._checkPermission('http.request');
      return this.sandbox.execute('http.request', {
        pluginId: this.pluginId,
        url,
        options
      });
    }
  };

  // Hooks System
  hooks = {
    /**
     * Register a hook
     * @param {string} hookName Hook name
     * @param {Function} handler Hook handler
     */
    register: (hookName, handler) => {
      this._checkPermission('hooks.register');
      return this.sandbox.execute('hooks.register', {
        pluginId: this.pluginId,
        hookName,
        handler
      });
    }
  };

  /**
   * Check if plugin has required permission
   * @private
   */
  _checkPermission(permission) {
    if (!this.permissions.has(permission) && !this.permissions.has('*')) {
      throw new Error(`Plugin ${this.pluginId} lacks permission: ${permission}`);
    }
  }

  /**
   * Grant permissions to plugin
   * @param {Array<string>} permissions Permission list
   */
  grantPermissions(permissions) {
    permissions.forEach(p => this.permissions.add(p));
  }
}

/**
 * Plugin Sandbox - Isolates plugin execution
 */
export class PluginSandbox {
  constructor(plugin, runtime) {
    this.plugin = plugin;
    this.runtime = runtime;
    this.context = this._createContext();
  }

  /**
   * Execute a sandboxed operation
   * @param {string} operation Operation name
   * @param {Object} params Operation parameters
   * @returns {Promise<any>} Operation result
   */
  async execute(operation, params) {
    // Validate operation
    if (!this._isAllowedOperation(operation)) {
      throw new Error(`Operation not allowed: ${operation}`);
    }

    // Log for audit
    this.runtime.audit.log('plugin.operation', {
      pluginId: this.plugin.id,
      operation,
      params: this._sanitizeParams(params)
    });

    // Execute in sandbox
    try {
      const handler = this._getOperationHandler(operation);
      return await handler(params);
    } catch (error) {
      this.runtime.audit.log('plugin.error', {
        pluginId: this.plugin.id,
        operation,
        error: error.message
      });
      throw error;
    }
  }

  /**
   * Create isolated context for plugin
   * @private
   */
  _createContext() {
    return {
      // Safe globals
      console: this._createSafeConsole(),
      setTimeout: (fn, delay) => this._safeTimeout(fn, delay),
      setInterval: (fn, delay) => this._safeInterval(fn, delay),
      
      // Restricted globals
      fetch: undefined,
      XMLHttpRequest: undefined,
      process: undefined,
      require: undefined,
      __dirname: undefined,
      __filename: undefined
    };
  }

  /**
   * Create safe console for plugin
   * @private
   */
  _createSafeConsole() {
    const prefix = `[Plugin: ${this.plugin.id}]`;
    return {
      log: (...args) => console.log(prefix, ...args),
      warn: (...args) => console.warn(prefix, ...args),
      error: (...args) => console.error(prefix, ...args),
      info: (...args) => console.info(prefix, ...args)
    };
  }

  /**
   * Safe timeout implementation
   * @private
   */
  _safeTimeout(fn, delay) {
    const maxDelay = 300000; // 5 minutes max
    const safeDelay = Math.min(delay, maxDelay);
    return setTimeout(() => {
      try {
        fn();
      } catch (error) {
        this.context.console.error('Timeout error:', error);
      }
    }, safeDelay);
  }

  /**
   * Safe interval implementation
   * @private
   */
  _safeInterval(fn, delay) {
    const minDelay = 1000; // 1 second minimum
    const safeDelay = Math.max(delay, minDelay);
    return setInterval(() => {
      try {
        fn();
      } catch (error) {
        this.context.console.error('Interval error:', error);
      }
    }, safeDelay);
  }

  /**
   * Check if operation is allowed
   * @private
   */
  _isAllowedOperation(operation) {
    const allowedOperations = [
      'ui.registerMenuItem',
      'ui.addWidget',
      'ui.notify',
      'ui.registerSettings',
      'system.searchPackages',
      'system.getServiceStatus',
      'system.getConfig',
      'system.exec',
      'storage.get',
      'storage.set',
      'storage.remove',
      'storage.keys',
      'events.on',
      'events.emit',
      'http.request',
      'hooks.register'
    ];
    return allowedOperations.includes(operation);
  }

  /**
   * Get operation handler
   * @private
   */
  _getOperationHandler(operation) {
    const handlers = {
      'ui.registerMenuItem': (params) => this.runtime.ui.registerMenuItem(params),
      'ui.addWidget': (params) => this.runtime.ui.addWidget(params),
      'ui.notify': (params) => this.runtime.ui.notify(params),
      'ui.registerSettings': (params) => this.runtime.ui.registerSettings(params),
      'system.searchPackages': (params) => this.runtime.system.searchPackages(params),
      'system.getServiceStatus': (params) => this.runtime.system.getServiceStatus(params),
      'system.getConfig': (params) => this.runtime.system.getConfig(params),
      'system.exec': (params) => this.runtime.system.exec(params),
      'storage.get': (params) => this.runtime.storage.get(params),
      'storage.set': (params) => this.runtime.storage.set(params),
      'storage.remove': (params) => this.runtime.storage.remove(params),
      'storage.keys': (params) => this.runtime.storage.keys(params),
      'events.on': (params) => this.runtime.events.on(params),
      'events.emit': (params) => this.runtime.events.emit(params),
      'http.request': (params) => this.runtime.http.request(params),
      'hooks.register': (params) => this.runtime.hooks.register(params)
    };
    return handlers[operation];
  }

  /**
   * Sanitize parameters for logging
   * @private
   */
  _sanitizeParams(params) {
    const sanitized = { ...params };
    // Remove sensitive data
    if (sanitized.password) sanitized.password = '[REDACTED]';
    if (sanitized.token) sanitized.token = '[REDACTED]';
    if (sanitized.secret) sanitized.secret = '[REDACTED]';
    return sanitized;
  }
}