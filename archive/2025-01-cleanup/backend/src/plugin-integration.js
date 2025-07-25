/**
 * Backend integration for plugin system
 * Connects the plugin manager with the Express server
 */

import { PluginManager } from '../../plugin-system/plugin-manager.js';
import express from 'express';
import path from 'path';

export function setupPluginRoutes(app, config) {
  const router = express.Router();
  
  // Initialize plugin manager
  const pluginManager = new PluginManager({
    pluginsDir: config.pluginsDir || path.join(process.cwd(), 'plugins'),
    enabledPlugins: config.enabledPlugins || [],
    autoLoad: true
  });

  // Initialize on startup
  app.locals.pluginManager = pluginManager;
  
  pluginManager.initialize().catch(error => {
    console.error('Failed to initialize plugin manager:', error);
  });

  // Middleware to check plugin permissions
  const checkPluginPermission = (permission) => {
    return (req, res, next) => {
      if (!req.user) {
        return res.status(401).json({ error: 'Authentication required' });
      }
      
      if (!req.user.groups.includes('wheel') && !req.user.groups.includes('nixos-gui-admin')) {
        return res.status(403).json({ error: 'Insufficient permissions' });
      }
      
      next();
    };
  };

  /**
   * List all plugins
   */
  router.get('/plugins', async (req, res) => {
    try {
      const plugins = pluginManager.listPlugins();
      res.json({ plugins });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  /**
   * Get plugin details
   */
  router.get('/plugins/:pluginId', async (req, res) => {
    try {
      const plugin = pluginManager.getPlugin(req.params.pluginId);
      if (!plugin) {
        return res.status(404).json({ error: 'Plugin not found' });
      }
      res.json({ plugin });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  /**
   * Enable a plugin
   */
  router.post('/plugins/:pluginId/enable', checkPluginPermission('plugins.manage'), async (req, res) => {
    try {
      await pluginManager.enablePlugin(req.params.pluginId);
      res.json({ success: true, message: 'Plugin enabled' });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  /**
   * Disable a plugin
   */
  router.post('/plugins/:pluginId/disable', checkPluginPermission('plugins.manage'), async (req, res) => {
    try {
      await pluginManager.disablePlugin(req.params.pluginId);
      res.json({ success: true, message: 'Plugin disabled' });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  /**
   * Install a plugin
   */
  router.post('/plugins/install', checkPluginPermission('plugins.install'), async (req, res) => {
    try {
      const { packageUrl, packagePath } = req.body;
      
      if (!packageUrl && !packagePath) {
        return res.status(400).json({ error: 'Package URL or path required' });
      }

      // Download package if URL provided
      let localPath = packagePath;
      if (packageUrl) {
        localPath = await downloadPlugin(packageUrl);
      }

      const pluginId = await pluginManager.installPlugin(localPath);
      res.json({ success: true, pluginId, message: 'Plugin installed' });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  /**
   * Uninstall a plugin
   */
  router.delete('/plugins/:pluginId', checkPluginPermission('plugins.install'), async (req, res) => {
    try {
      await pluginManager.uninstallPlugin(req.params.pluginId);
      res.json({ success: true, message: 'Plugin uninstalled' });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  /**
   * Get plugin settings
   */
  router.get('/plugins/:pluginId/settings', async (req, res) => {
    try {
      const settings = await pluginManager.runtime.storage.get({
        pluginId: req.params.pluginId,
        key: 'settings'
      });
      res.json({ settings: settings || {} });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  /**
   * Update plugin settings
   */
  router.put('/plugins/:pluginId/settings', checkPluginPermission('plugins.configure'), async (req, res) => {
    try {
      await pluginManager.runtime.storage.set({
        pluginId: req.params.pluginId,
        key: 'settings',
        value: req.body.settings
      });
      res.json({ success: true, message: 'Settings updated' });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  /**
   * Plugin UI elements endpoint
   */
  router.get('/plugins/ui/elements', async (req, res) => {
    try {
      const menuItems = pluginManager.runtime.uiRegistry.getMenuItems();
      const widgets = pluginManager.runtime.uiRegistry.getWidgets();
      
      res.json({
        menuItems,
        widgets
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });

  /**
   * WebSocket handler for plugin events
   */
  app.locals.setupPluginWebSocket = (io) => {
    // Plugin event namespace
    const pluginNS = io.of('/plugins');
    
    pluginNS.on('connection', (socket) => {
      console.log('Plugin WebSocket connected');

      // Subscribe to plugin events
      const handlers = {
        'ui.notification': (data) => {
          socket.emit('notification', data);
        },
        'ui.widgetUpdate': (data) => {
          socket.emit('widget.update', data);
        },
        'plugin.loaded': (data) => {
          socket.emit('plugin.loaded', data);
        },
        'plugin.unloaded': (data) => {
          socket.emit('plugin.unloaded', data);
        }
      };

      // Register handlers
      Object.entries(handlers).forEach(([event, handler]) => {
        pluginManager.runtime.on(event, handler);
      });

      // Cleanup on disconnect
      socket.on('disconnect', () => {
        Object.entries(handlers).forEach(([event, handler]) => {
          pluginManager.runtime.off(event, handler);
        });
      });

      // Handle plugin actions
      socket.on('plugin.action', async (data) => {
        try {
          const { pluginId, action, params } = data;
          
          // Verify plugin exists and is active
          const plugin = pluginManager.plugins.get(pluginId);
          if (!plugin || plugin.status !== 'active') {
            return socket.emit('plugin.error', {
              error: 'Plugin not available'
            });
          }

          // Execute action
          if (typeof plugin.instance[action] === 'function') {
            const result = await plugin.instance[action](params);
            socket.emit('plugin.result', { action, result });
          } else {
            socket.emit('plugin.error', {
              error: `Action '${action}' not found`
            });
          }
        } catch (error) {
          socket.emit('plugin.error', {
            error: error.message
          });
        }
      });
    });
  };

  // Mount plugin routes
  app.use('/api', router);

  // Static assets for plugins
  app.use('/plugins/assets', express.static(path.join(config.pluginsDir, 'assets')));

  return pluginManager;
}

/**
 * Download plugin from URL
 */
async function downloadPlugin(url) {
  const https = require('https');
  const fs = require('fs');
  const os = require('os');
  const path = require('path');
  
  const tempFile = path.join(os.tmpdir(), `plugin-${Date.now()}.tar.gz`);
  
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(tempFile);
    
    https.get(url, (response) => {
      response.pipe(file);
      
      file.on('finish', () => {
        file.close();
        resolve(tempFile);
      });
    }).on('error', (error) => {
      fs.unlink(tempFile, () => {});
      reject(error);
    });
  });
}

/**
 * Plugin development middleware
 */
export function pluginDevMiddleware(config) {
  return async (req, res, next) => {
    if (config.pluginDev && req.path.startsWith('/plugin-dev')) {
      // Serve plugin files directly in development
      const pluginPath = req.path.replace('/plugin-dev/', '');
      const filePath = path.join(config.pluginsDir, config.pluginDev, pluginPath);
      
      try {
        res.sendFile(filePath);
      } catch (error) {
        res.status(404).send('Plugin file not found');
      }
    } else {
      next();
    }
  };
}