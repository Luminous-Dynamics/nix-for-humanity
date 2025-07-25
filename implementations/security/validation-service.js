/**
 * Input Validation Service for Nix for Humanity
 * Comprehensive validation and sanitization for all user inputs
 */

const Joi = require('joi');

class ValidationService {
  constructor() {
    // Define validation schemas
    this.schemas = {
      // Natural language input
      nlpInput: Joi.object({
        text: Joi.string()
          .min(1)
          .max(500)
          .trim()
          .replace(/[<>]/g, '') // Basic XSS prevention
          .required(),
        context: Joi.object({
          previousCommand: Joi.string().optional(),
          userId: Joi.string().alphanum().optional(),
          sessionId: Joi.string().uuid().optional()
        }).optional()
      }),

      // Voice input metadata
      voiceInput: Joi.object({
        audio: Joi.binary().max(10 * 1024 * 1024).required(), // 10MB max
        format: Joi.string().valid('webm', 'ogg', 'wav').required(),
        sampleRate: Joi.number().min(8000).max(48000).required(),
        duration: Joi.number().max(60).required() // 60 seconds max
      }),

      // Package operations
      packageOperation: Joi.object({
        operation: Joi.string()
          .valid('install', 'remove', 'update', 'search', 'info')
          .required(),
        package: Joi.string()
          .pattern(/^[a-zA-Z0-9][a-zA-Z0-9-_.]*$/)
          .max(100)
          .required(),
        options: Joi.object({
          dryRun: Joi.boolean().default(false),
          force: Joi.boolean().default(false),
          version: Joi.string().optional()
        }).optional()
      }),

      // Service operations
      serviceOperation: Joi.object({
        operation: Joi.string()
          .valid('start', 'stop', 'restart', 'enable', 'disable', 'status')
          .required(),
        service: Joi.string()
          .pattern(/^[a-zA-Z0-9][a-zA-Z0-9-_.]*$/)
          .max(100)
          .required()
      }),

      // Configuration changes
      configOperation: Joi.object({
        path: Joi.string()
          .pattern(/^[a-zA-Z0-9-_./]+$/)
          .max(200)
          .required(),
        operation: Joi.string()
          .valid('read', 'write', 'append')
          .required(),
        content: Joi.string()
          .max(10000)
          .when('operation', {
            is: Joi.valid('write', 'append'),
            then: Joi.required()
          })
      }),

      // Authentication
      loginRequest: Joi.object({
        username: Joi.string()
          .alphanum()
          .min(3)
          .max(30)
          .required(),
        password: Joi.string()
          .min(8)
          .max(128)
          .required()
      }),

      // User registration
      registerRequest: Joi.object({
        username: Joi.string()
          .alphanum()
          .min(3)
          .max(30)
          .required(),
        password: Joi.string()
          .min(8)
          .max(128)
          .pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/) // At least one lowercase, uppercase, and digit
          .required(),
        confirmPassword: Joi.string()
          .valid(Joi.ref('password'))
          .required(),
        email: Joi.string()
          .email()
          .optional()
      }),

      // System query
      systemQuery: Joi.object({
        type: Joi.string()
          .valid('info', 'status', 'logs', 'processes', 'network', 'storage')
          .required(),
        filter: Joi.string()
          .max(100)
          .optional()
      })
    };

    // Command sanitization patterns
    this.dangerousPatterns = [
      // Shell injection patterns
      /[;&|`$]/g,
      /\$\{.*\}/g,
      /\$\(.*\)/g,
      /`.*`/g,
      
      // Path traversal
      /\.\.\//g,
      /\.\.$/,
      
      // SQL injection keywords (shouldn't be in Nix commands)
      /\b(union|select|drop|insert|update|delete)\b.*\b(from|where|table)\b/i,
      
      // Script injection
      /<script[^>]*>.*?<\/script>/gi,
      /javascript:/gi,
      /on\w+\s*=/gi
    ];
  }

  // Validate input against schema
  validate(data, schemaName) {
    const schema = this.schemas[schemaName];
    if (!schema) {
      throw new Error(`Unknown validation schema: ${schemaName}`);
    }

    const { error, value } = schema.validate(data, {
      abortEarly: false,
      stripUnknown: true
    });

    if (error) {
      const errors = error.details.map(detail => ({
        field: detail.path.join('.'),
        message: detail.message,
        type: detail.type
      }));
      
      throw new ValidationError('Validation failed', errors);
    }

    return value;
  }

  // Sanitize command arguments
  sanitizeCommand(command, args = []) {
    // Validate command is in whitelist
    const allowedCommands = [
      'nix', 'nix-env', 'nixos-rebuild', 'nix-channel',
      'systemctl', 'journalctl'
    ];

    if (!allowedCommands.includes(command)) {
      throw new Error(`Command '${command}' is not allowed`);
    }

    // Sanitize each argument
    const sanitizedArgs = args.map(arg => {
      // Convert to string and trim
      let sanitized = String(arg).trim();

      // Check for dangerous patterns
      for (const pattern of this.dangerousPatterns) {
        if (pattern.test(sanitized)) {
          throw new Error(`Dangerous pattern detected in argument: ${arg}`);
        }
      }

      // Remove any remaining shell metacharacters
      sanitized = sanitized.replace(/[;&|`$<>\\]/g, '');

      // Validate length
      if (sanitized.length > 1000) {
        throw new Error('Argument too long');
      }

      return sanitized;
    });

    return { command, args: sanitizedArgs };
  }

  // Validate NixOS package name
  validatePackageName(name) {
    // Package names in Nix can contain letters, numbers, dots, hyphens, and underscores
    const pattern = /^[a-zA-Z0-9][a-zA-Z0-9-_.]*$/;
    
    if (!pattern.test(name)) {
      throw new Error(`Invalid package name: ${name}`);
    }

    // Check length
    if (name.length > 100) {
      throw new Error('Package name too long');
    }

    // Check for suspicious patterns
    const suspicious = [
      'rm', 'delete', 'format', 'wipe',
      '../', '..\\', '${', '$('
    ];

    for (const pattern of suspicious) {
      if (name.includes(pattern)) {
        throw new Error(`Suspicious pattern in package name: ${pattern}`);
      }
    }

    return name;
  }

  // Validate service name
  validateServiceName(name) {
    // Service names are more restrictive
    const pattern = /^[a-zA-Z0-9][a-zA-Z0-9-_.@]*$/;
    
    if (!pattern.test(name)) {
      throw new Error(`Invalid service name: ${name}`);
    }

    if (name.length > 100) {
      throw new Error('Service name too long');
    }

    return name;
  }

  // Validate file path (for configuration)
  validateFilePath(path) {
    // Only allow paths within /etc/nixos/
    if (!path.startsWith('/etc/nixos/')) {
      throw new Error('Configuration files must be in /etc/nixos/');
    }

    // No path traversal
    if (path.includes('..')) {
      throw new Error('Path traversal not allowed');
    }

    // Must end with .nix
    if (!path.endsWith('.nix')) {
      throw new Error('Configuration files must have .nix extension');
    }

    return path;
  }

  // Sanitize user-facing output
  sanitizeOutput(text) {
    // Remove ANSI escape codes
    const ansiRegex = /[\u001b\u009b][[()#;?]*(?:[0-9]{1,4}(?:;[0-9]{0,4})*)?[0-9A-ORZcf-nqry=><]/g;
    text = text.replace(ansiRegex, '');

    // Limit length
    if (text.length > 10000) {
      text = text.substring(0, 10000) + '\n... (truncated)';
    }

    // Remove any potential script injections
    text = text.replace(/<script[^>]*>.*?<\/script>/gi, '');
    text = text.replace(/javascript:/gi, '');

    return text;
  }

  // Rate limiting check (should be used with Redis in production)
  checkRateLimit(userId, operation, limits = {}) {
    // Default limits
    const defaultLimits = {
      nlpInput: { requests: 60, window: 60 }, // 60 requests per minute
      packageOperation: { requests: 10, window: 300 }, // 10 installs per 5 minutes
      serviceOperation: { requests: 20, window: 60 }, // 20 service ops per minute
      configOperation: { requests: 5, window: 300 } // 5 config changes per 5 minutes
    };

    const limit = limits[operation] || defaultLimits[operation] || { requests: 100, window: 60 };

    // In production, this would check Redis
    // For now, just return true
    return {
      allowed: true,
      remaining: limit.requests,
      resetAt: new Date(Date.now() + limit.window * 1000)
    };
  }
}

// Custom validation error class
class ValidationError extends Error {
  constructor(message, errors) {
    super(message);
    this.name = 'ValidationError';
    this.errors = errors;
  }

  toJSON() {
    return {
      name: this.name,
      message: this.message,
      errors: this.errors
    };
  }
}

module.exports = { ValidationService, ValidationError };