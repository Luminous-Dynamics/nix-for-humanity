/**
 * NixOS GUI Plugin Manager
 * Handles plugin lifecycle, loading, and management
 */

import { PluginAPI, PluginSandbox } from './plugin-api.js';
import { validatePlugin } from './plugin-validator.js';
import { PluginRuntime } from './plugin-runtime.js';
import path from 'path';
import fs from 'fs/promises';
import crypto from 'crypto';

export class PluginManager {
  constructor(config = {}) {
    this.config = {
      pluginsDir: config.pluginsDir || './plugins',
      enabledPlugins: config.enabledPlugins || [],
      autoLoad: config.autoLoad !== false,
      maxPlugins: config.maxPlugins || 50,
      ...config
    };
    
    this.plugins = new Map();
    this.runtime = new PluginRuntime(this);
    this.hooks = new Map();
    this.initialized = false;
  }

  /**
   * Initialize the plugin manager
   */
  async initialize() {
    if (this.initialized) return;

    // Create plugins directory if it doesn't exist
    await fs.mkdir(this.config.pluginsDir, { recursive: true });

    // Load enabled plugins
    if (this.config.autoLoad) {
      await this.loadEnabledPlugins();
    }

    this.initialized = true;
    await this.executeHook('system.initialized');
  }

  /**
   * Load all enabled plugins
   */
  async loadEnabledPlugins() {
    const pluginDirs = await fs.readdir(this.config.pluginsDir);
    
    for (const pluginDir of pluginDirs) {
      if (this.config.enabledPlugins.includes(pluginDir)) {
        try {
          await this.loadPlugin(pluginDir);
        } catch (error) {
          console.error(`Failed to load plugin ${pluginDir}:`, error);
        }
      }
    }
  }

  /**
   * Load a specific plugin
   * @param {string} pluginId Plugin identifier
   */
  async loadPlugin(pluginId) {
    if (this.plugins.has(pluginId)) {
      throw new Error(`Plugin ${pluginId} is already loaded`);
    }

    if (this.plugins.size >= this.config.maxPlugins) {
      throw new Error(`Maximum number of plugins (${this.config.maxPlugins}) reached`);
    }

    const pluginPath = path.join(this.config.pluginsDir, pluginId);
    
    // Load plugin manifest
    const manifestPath = path.join(pluginPath, 'plugin.json');
    const manifestContent = await fs.readFile(manifestPath, 'utf8');
    const manifest = JSON.parse(manifestContent);

    // Validate plugin
    const validation = await validatePlugin(pluginPath, manifest);
    if (!validation.valid) {
      throw new Error(`Plugin validation failed: ${validation.errors.join(', ')}`);
    }

    // Create plugin instance
    const plugin = {
      id: pluginId,
      manifest,
      path: pluginPath,
      status: 'loading',
      instance: null,
      sandbox: null,
      api: null,
      checksum: await this._calculateChecksum(pluginPath)
    };

    // Create sandbox and API
    plugin.sandbox = new PluginSandbox(plugin, this.runtime);
    plugin.api = new PluginAPI(pluginId, plugin.sandbox);
    plugin.api.grantPermissions(manifest.permissions || []);

    // Load plugin code
    const mainFile = path.join(pluginPath, manifest.main || 'index.js');
    const PluginClass = await this._loadPluginModule(mainFile);

    // Instantiate plugin
    plugin.instance = new PluginClass(plugin.api);

    // Initialize plugin
    if (typeof plugin.instance.initialize === 'function') {
      await plugin.instance.initialize();
    }

    // Store plugin
    this.plugins.set(pluginId, plugin);
    plugin.status = 'active';

    // Execute loaded hook
    await this.executeHook('plugin.loaded', { pluginId });

    console.log(`Plugin ${pluginId} loaded successfully`);
    return plugin;
  }

  /**
   * Unload a plugin
   * @param {string} pluginId Plugin identifier
   */
  async unloadPlugin(pluginId) {
    const plugin = this.plugins.get(pluginId);
    if (!plugin) {
      throw new Error(`Plugin ${pluginId} not found`);
    }

    // Execute unloading hook
    await this.executeHook('plugin.unloading', { pluginId });

    // Call plugin cleanup
    if (plugin.instance && typeof plugin.instance.cleanup === 'function') {
      try {
        await plugin.instance.cleanup();
      } catch (error) {
        console.error(`Error during plugin cleanup:`, error);
      }
    }

    // Remove plugin hooks
    this._removePluginHooks(pluginId);

    // Remove from registry
    this.plugins.delete(pluginId);

    // Execute unloaded hook
    await this.executeHook('plugin.unloaded', { pluginId });

    console.log(`Plugin ${pluginId} unloaded`);
  }

  /**
   * Reload a plugin
   * @param {string} pluginId Plugin identifier
   */
  async reloadPlugin(pluginId) {
    if (this.plugins.has(pluginId)) {
      await this.unloadPlugin(pluginId);
    }
    return await this.loadPlugin(pluginId);
  }

  /**
   * Enable a plugin
   * @param {string} pluginId Plugin identifier
   */
  async enablePlugin(pluginId) {
    if (!this.config.enabledPlugins.includes(pluginId)) {
      this.config.enabledPlugins.push(pluginId);
      await this._saveConfig();
    }
    
    if (!this.plugins.has(pluginId)) {
      await this.loadPlugin(pluginId);
    }
  }

  /**
   * Disable a plugin
   * @param {string} pluginId Plugin identifier
   */
  async disablePlugin(pluginId) {
    const index = this.config.enabledPlugins.indexOf(pluginId);
    if (index > -1) {
      this.config.enabledPlugins.splice(index, 1);
      await this._saveConfig();
    }
    
    if (this.plugins.has(pluginId)) {
      await this.unloadPlugin(pluginId);
    }
  }

  /**
   * Get plugin information
   * @param {string} pluginId Plugin identifier
   * @returns {Object} Plugin information
   */
  getPlugin(pluginId) {
    const plugin = this.plugins.get(pluginId);
    if (!plugin) return null;

    return {
      id: plugin.id,
      name: plugin.manifest.name,
      version: plugin.manifest.version,
      description: plugin.manifest.description,
      author: plugin.manifest.author,
      status: plugin.status,
      permissions: plugin.manifest.permissions,
      checksum: plugin.checksum
    };
  }

  /**
   * List all plugins
   * @returns {Array} List of plugin information
   */
  listPlugins() {
    return Array.from(this.plugins.values()).map(plugin => ({
      id: plugin.id,
      name: plugin.manifest.name,
      version: plugin.manifest.version,
      status: plugin.status,
      enabled: this.config.enabledPlugins.includes(plugin.id)
    }));
  }

  /**
   * Install a plugin from package
   * @param {string} packagePath Path to plugin package
   * @returns {string} Installed plugin ID
   */
  async installPlugin(packagePath) {
    // Extract plugin ID from package
    const tempDir = path.join(this.config.pluginsDir, '.temp', crypto.randomBytes(8).toString('hex'));
    await fs.mkdir(tempDir, { recursive: true });

    try {
      // Extract package (assuming tar.gz)
      await this._extractPackage(packagePath, tempDir);

      // Load manifest
      const manifestPath = path.join(tempDir, 'plugin.json');
      const manifest = JSON.parse(await fs.readFile(manifestPath, 'utf8'));

      // Validate plugin
      const validation = await validatePlugin(tempDir, manifest);
      if (!validation.valid) {
        throw new Error(`Plugin validation failed: ${validation.errors.join(', ')}`);
      }

      // Check for conflicts
      const pluginId = manifest.id;
      const targetPath = path.join(this.config.pluginsDir, pluginId);
      
      if (await this._fileExists(targetPath)) {
        throw new Error(`Plugin ${pluginId} already exists`);
      }

      // Move to plugins directory
      await fs.rename(tempDir, targetPath);

      // Execute installed hook
      await this.executeHook('plugin.installed', { pluginId });

      return pluginId;
    } finally {
      // Cleanup temp directory
      try {
        await fs.rm(tempDir, { recursive: true, force: true });
      } catch {}
    }
  }

  /**
   * Uninstall a plugin
   * @param {string} pluginId Plugin identifier
   */
  async uninstallPlugin(pluginId) {
    // Unload if loaded
    if (this.plugins.has(pluginId)) {
      await this.unloadPlugin(pluginId);
    }

    // Remove from enabled list
    await this.disablePlugin(pluginId);

    // Delete plugin directory
    const pluginPath = path.join(this.config.pluginsDir, pluginId);
    await fs.rm(pluginPath, { recursive: true, force: true });

    // Execute uninstalled hook
    await this.executeHook('plugin.uninstalled', { pluginId });
  }

  /**
   * Register a hook handler
   * @param {string} hookName Hook name
   * @param {Function} handler Hook handler
   * @param {string} pluginId Plugin ID (optional)
   */
  registerHook(hookName, handler, pluginId = null) {
    if (!this.hooks.has(hookName)) {
      this.hooks.set(hookName, []);
    }
    
    this.hooks.get(hookName).push({
      handler,
      pluginId,
      priority: 50
    });
  }

  /**
   * Execute hooks for an event
   * @param {string} hookName Hook name
   * @param {any} data Hook data
   * @returns {Array} Results from all handlers
   */
  async executeHook(hookName, data = {}) {
    const handlers = this.hooks.get(hookName) || [];
    const results = [];

    // Sort by priority (higher first)
    handlers.sort((a, b) => b.priority - a.priority);

    for (const { handler, pluginId } of handlers) {
      try {
        const result = await handler(data);
        results.push({ pluginId, result });
      } catch (error) {
        console.error(`Hook error in ${pluginId || 'system'}:`, error);
      }
    }

    return results;
  }

  /**
   * Load plugin module safely
   * @private
   */
  async _loadPluginModule(modulePath) {
    // Create isolated context for plugin loading
    const moduleContent = await fs.readFile(modulePath, 'utf8');
    
    // Wrap in function to isolate scope
    const wrappedModule = `
      (function(exports, require, module, __filename, __dirname) {
        ${moduleContent}
        return module.exports || exports.default || exports;
      })
    `;

    // Create safe require function
    const safeRequire = (id) => {
      // Only allow specific modules
      const allowedModules = ['events', 'util', 'path'];
      if (allowedModules.includes(id)) {
        return require(id);
      }
      throw new Error(`Module '${id}' is not allowed in plugins`);
    };

    // Execute module
    const moduleExports = {};
    const module = { exports: moduleExports };
    const moduleFunction = eval(wrappedModule);
    
    return moduleFunction(
      moduleExports,
      safeRequire,
      module,
      modulePath,
      path.dirname(modulePath)
    );
  }

  /**
   * Calculate plugin checksum
   * @private
   */
  async _calculateChecksum(pluginPath) {
    const hash = crypto.createHash('sha256');
    const files = await this._walkDirectory(pluginPath);
    
    for (const file of files.sort()) {
      const content = await fs.readFile(file);
      hash.update(content);
    }
    
    return hash.digest('hex');
  }

  /**
   * Walk directory recursively
   * @private
   */
  async _walkDirectory(dir, files = []) {
    const entries = await fs.readdir(dir, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        await this._walkDirectory(fullPath, files);
      } else {
        files.push(fullPath);
      }
    }
    
    return files;
  }

  /**
   * Remove all hooks registered by a plugin
   * @private
   */
  _removePluginHooks(pluginId) {
    for (const [hookName, handlers] of this.hooks.entries()) {
      const filtered = handlers.filter(h => h.pluginId !== pluginId);
      if (filtered.length === 0) {
        this.hooks.delete(hookName);
      } else {
        this.hooks.set(hookName, filtered);
      }
    }
  }

  /**
   * Check if file exists
   * @private
   */
  async _fileExists(path) {
    try {
      await fs.access(path);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Extract plugin package
   * @private
   */
  async _extractPackage(packagePath, targetDir) {
    const { exec } = require('child_process');
    const { promisify } = require('util');
    const execAsync = promisify(exec);
    
    await execAsync(`tar -xzf ${packagePath} -C ${targetDir}`);
  }

  /**
   * Save configuration
   * @private
   */
  async _saveConfig() {
    // In production, this would save to a persistent configuration
    // For now, we'll just emit an event
    await this.executeHook('config.changed', {
      enabledPlugins: this.config.enabledPlugins
    });
  }
}