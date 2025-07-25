/**
 * NixOS GUI Plugin Validator
 * Validates plugin structure, manifest, and security
 */

import fs from 'fs/promises';
import path from 'path';
import semver from 'semver';

/**
 * Validate a plugin before loading
 * @param {string} pluginPath Path to plugin directory
 * @param {Object} manifest Plugin manifest
 * @returns {Object} Validation result
 */
export async function validatePlugin(pluginPath, manifest) {
  const errors = [];
  const warnings = [];

  // Validate manifest structure
  const manifestValidation = validateManifest(manifest);
  errors.push(...manifestValidation.errors);
  warnings.push(...manifestValidation.warnings);

  // Validate plugin files
  const fileValidation = await validatePluginFiles(pluginPath, manifest);
  errors.push(...fileValidation.errors);
  warnings.push(...fileValidation.warnings);

  // Validate permissions
  const permissionValidation = validatePermissions(manifest.permissions || []);
  errors.push(...permissionValidation.errors);
  warnings.push(...permissionValidation.warnings);

  // Validate dependencies
  const dependencyValidation = validateDependencies(manifest.dependencies || {});
  errors.push(...dependencyValidation.errors);
  warnings.push(...dependencyValidation.warnings);

  // Security validation
  const securityValidation = await validateSecurity(pluginPath, manifest);
  errors.push(...securityValidation.errors);
  warnings.push(...securityValidation.warnings);

  return {
    valid: errors.length === 0,
    errors,
    warnings
  };
}

/**
 * Validate plugin manifest
 */
function validateManifest(manifest) {
  const errors = [];
  const warnings = [];

  // Required fields
  const requiredFields = ['id', 'name', 'version', 'description', 'author'];
  for (const field of requiredFields) {
    if (!manifest[field]) {
      errors.push(`Missing required field: ${field}`);
    }
  }

  // Validate ID format
  if (manifest.id && !/^[a-z0-9-]+$/.test(manifest.id)) {
    errors.push('Plugin ID must contain only lowercase letters, numbers, and hyphens');
  }

  // Validate version
  if (manifest.version && !semver.valid(manifest.version)) {
    errors.push('Invalid version format. Use semantic versioning (e.g., 1.0.0)');
  }

  // Validate GUI compatibility
  if (manifest.guiVersion) {
    if (!semver.validRange(manifest.guiVersion)) {
      errors.push('Invalid guiVersion range');
    }
  } else {
    warnings.push('No guiVersion specified. Plugin may not be compatible with all GUI versions');
  }

  // Validate homepage URL
  if (manifest.homepage && !isValidUrl(manifest.homepage)) {
    warnings.push('Invalid homepage URL');
  }

  // Validate license
  if (!manifest.license) {
    warnings.push('No license specified');
  }

  // Validate categories
  if (manifest.categories) {
    const validCategories = [
      'system', 'network', 'development', 'productivity',
      'monitoring', 'security', 'customization', 'integration'
    ];
    
    for (const category of manifest.categories) {
      if (!validCategories.includes(category)) {
        warnings.push(`Unknown category: ${category}`);
      }
    }
  }

  return { errors, warnings };
}

/**
 * Validate plugin files
 */
async function validatePluginFiles(pluginPath, manifest) {
  const errors = [];
  const warnings = [];

  try {
    // Check main entry point
    const mainFile = manifest.main || 'index.js';
    const mainPath = path.join(pluginPath, mainFile);
    
    try {
      await fs.access(mainPath);
    } catch {
      errors.push(`Main entry point not found: ${mainFile}`);
    }

    // Check for required files
    const requiredFiles = ['plugin.json'];
    for (const file of requiredFiles) {
      try {
        await fs.access(path.join(pluginPath, file));
      } catch {
        errors.push(`Required file not found: ${file}`);
      }
    }

    // Check for README
    try {
      await fs.access(path.join(pluginPath, 'README.md'));
    } catch {
      warnings.push('No README.md file found');
    }

    // Check file sizes
    const stats = await fs.stat(pluginPath);
    const maxSize = 10 * 1024 * 1024; // 10MB
    
    const totalSize = await getDirectorySize(pluginPath);
    if (totalSize > maxSize) {
      errors.push(`Plugin size (${(totalSize / 1024 / 1024).toFixed(2)}MB) exceeds maximum (10MB)`);
    }

    // Check for suspicious files
    const suspiciousExtensions = ['.exe', '.dll', '.so', '.dylib', '.bin'];
    const files = await walkDirectory(pluginPath);
    
    for (const file of files) {
      const ext = path.extname(file).toLowerCase();
      if (suspiciousExtensions.includes(ext)) {
        errors.push(`Suspicious file found: ${path.relative(pluginPath, file)}`);
      }
    }

  } catch (error) {
    errors.push(`Failed to validate plugin files: ${error.message}`);
  }

  return { errors, warnings };
}

/**
 * Validate permissions
 */
function validatePermissions(permissions) {
  const errors = [];
  const warnings = [];

  const validPermissions = [
    // UI permissions
    'ui.menu',
    'ui.widget',
    'ui.notify',
    'ui.settings',
    
    // System permissions
    'system.packages.read',
    'system.packages.write',
    'system.services.read',
    'system.services.write',
    'system.config.read',
    'system.config.write',
    'system.exec',
    
    // Storage permissions
    'storage.read',
    'storage.write',
    
    // Event permissions
    'events.subscribe',
    'events.emit',
    
    // Network permissions
    'http.request',
    
    // Hook permissions
    'hooks.register',
    
    // Wildcard
    '*'
  ];

  for (const permission of permissions) {
    if (!validPermissions.includes(permission)) {
      errors.push(`Invalid permission: ${permission}`);
    }
  }

  // Warn about dangerous permissions
  const dangerousPermissions = ['system.exec', 'system.config.write', '*'];
  const requested = permissions.filter(p => dangerousPermissions.includes(p));
  
  if (requested.length > 0) {
    warnings.push(`Plugin requests dangerous permissions: ${requested.join(', ')}`);
  }

  // Check for redundant permissions
  if (permissions.includes('*') && permissions.length > 1) {
    warnings.push('Wildcard permission (*) makes other permissions redundant');
  }

  return { errors, warnings };
}

/**
 * Validate dependencies
 */
function validateDependencies(dependencies) {
  const errors = [];
  const warnings = [];

  // Check GUI version compatibility
  if (dependencies.gui) {
    if (!semver.validRange(dependencies.gui)) {
      errors.push('Invalid GUI version range in dependencies');
    }
  }

  // Check plugin dependencies
  if (dependencies.plugins) {
    for (const [pluginId, version] of Object.entries(dependencies.plugins)) {
      if (!/^[a-z0-9-]+$/.test(pluginId)) {
        errors.push(`Invalid plugin dependency ID: ${pluginId}`);
      }
      
      if (!semver.validRange(version)) {
        errors.push(`Invalid version range for plugin dependency ${pluginId}: ${version}`);
      }
    }
  }

  // Check system dependencies
  if (dependencies.system) {
    const validSystemDeps = ['systemd', 'polkit', 'dbus'];
    
    for (const dep of dependencies.system) {
      if (!validSystemDeps.includes(dep)) {
        warnings.push(`Unknown system dependency: ${dep}`);
      }
    }
  }

  return { errors, warnings };
}

/**
 * Security validation
 */
async function validateSecurity(pluginPath, manifest) {
  const errors = [];
  const warnings = [];

  try {
    // Check for eval usage
    const jsFiles = await findFilesByExtension(pluginPath, '.js');
    
    for (const file of jsFiles) {
      const content = await fs.readFile(file, 'utf8');
      
      // Check for dangerous patterns
      const dangerousPatterns = [
        /\beval\s*\(/g,
        /new\s+Function\s*\(/g,
        /\brequire\s*\(\s*[^'"]/g, // Dynamic require
        /child_process/g,
        /\bfs\b\.(?:unlink|rmdir|rm)/g, // File deletion
        /process\.exit/g
      ];
      
      for (const pattern of dangerousPatterns) {
        if (pattern.test(content)) {
          warnings.push(`Potentially dangerous code pattern in ${path.relative(pluginPath, file)}: ${pattern}`);
        }
      }
      
      // Check for network requests to suspicious domains
      const urlPattern = /https?:\/\/[^\s'"]+/g;
      const urls = content.match(urlPattern) || [];
      
      for (const url of urls) {
        if (!isValidUrl(url) || isSuspiciousUrl(url)) {
          warnings.push(`Suspicious URL found: ${url}`);
        }
      }
    }

    // Validate file permissions
    const files = await walkDirectory(pluginPath);
    
    for (const file of files) {
      const stats = await fs.stat(file);
      
      // Check for executable files
      if (stats.mode & 0o111) {
        errors.push(`Executable file found: ${path.relative(pluginPath, file)}`);
      }
    }

  } catch (error) {
    errors.push(`Security validation failed: ${error.message}`);
  }

  return { errors, warnings };
}

/**
 * Helper: Check if URL is valid
 */
function isValidUrl(url) {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Helper: Check if URL is suspicious
 */
function isSuspiciousUrl(url) {
  const suspiciousPatterns = [
    /^https?:\/\/localhost/,
    /^https?:\/\/127\./,
    /^https?:\/\/192\.168\./,
    /^https?:\/\/10\./,
    /\.onion$/,
    /^https?:\/\/[^/]+:\d{4,}/  // Non-standard ports
  ];
  
  return suspiciousPatterns.some(pattern => pattern.test(url));
}

/**
 * Helper: Get directory size
 */
async function getDirectorySize(dir) {
  let size = 0;
  const files = await walkDirectory(dir);
  
  for (const file of files) {
    const stats = await fs.stat(file);
    size += stats.size;
  }
  
  return size;
}

/**
 * Helper: Walk directory recursively
 */
async function walkDirectory(dir, files = []) {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      await walkDirectory(fullPath, files);
    } else {
      files.push(fullPath);
    }
  }
  
  return files;
}

/**
 * Helper: Find files by extension
 */
async function findFilesByExtension(dir, extension) {
  const allFiles = await walkDirectory(dir);
  return allFiles.filter(file => path.extname(file) === extension);
}