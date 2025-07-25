/**
 * Simple Development Logger
 * Provides consistent logging across the application
 */

// Log levels
const LogLevel = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3
};

// Get log level from environment or default to INFO
const currentLogLevel = (() => {
  if (typeof process !== 'undefined' && process.env?.LOG_LEVEL) {
    return LogLevel[process.env.LOG_LEVEL.toUpperCase()] || LogLevel.INFO;
  }
  // Browser environment - check localStorage
  if (typeof window !== 'undefined' && window.localStorage) {
    const level = window.localStorage.getItem('NFH_LOG_LEVEL');
    return level ? LogLevel[level.toUpperCase()] || LogLevel.INFO : LogLevel.INFO;
  }
  return LogLevel.INFO;
})();

// Color codes for browser console
const colors = {
  DEBUG: 'color: #888',
  INFO: 'color: #2196F3',
  WARN: 'color: #FF9800',
  ERROR: 'color: #F44336'
};

// Emoji indicators
const emojis = {
  DEBUG: '🔍',
  INFO: '💡',
  WARN: '⚠️',
  ERROR: '❌'
};

class Logger {
  constructor(module) {
    this.module = module;
  }

  debug(...args) {
    this._log(LogLevel.DEBUG, 'DEBUG', args);
  }

  info(...args) {
    this._log(LogLevel.INFO, 'INFO', args);
  }

  warn(...args) {
    this._log(LogLevel.WARN, 'WARN', args);
  }

  error(...args) {
    this._log(LogLevel.ERROR, 'ERROR', args);
  }

  // Log with timing
  time(label) {
    if (currentLogLevel <= LogLevel.DEBUG) {
      console.time(`[${this.module}] ${label}`);
    }
  }

  timeEnd(label) {
    if (currentLogLevel <= LogLevel.DEBUG) {
      console.timeEnd(`[${this.module}] ${label}`);
    }
  }

  // Log a group of related messages
  group(label) {
    if (currentLogLevel <= LogLevel.INFO) {
      console.group(`${emojis.INFO} [${this.module}] ${label}`);
    }
  }

  groupEnd() {
    if (currentLogLevel <= LogLevel.INFO) {
      console.groupEnd();
    }
  }

  _log(level, levelName, args) {
    if (level < currentLogLevel) return;

    const timestamp = new Date().toISOString();
    const prefix = `[${timestamp}] ${emojis[levelName]} [${this.module}]`;

    // Node.js environment
    if (typeof process !== 'undefined' && process.stdout) {
      console.log(prefix, ...args);
    } 
    // Browser environment
    else if (typeof window !== 'undefined') {
      console.log(`%c${prefix}`, colors[levelName], ...args);
    }
  }
}

// Factory function to create loggers
export function createLogger(module) {
  return new Logger(module);
}

// Set log level (for browser)
export function setLogLevel(level) {
  if (typeof window !== 'undefined' && window.localStorage) {
    window.localStorage.setItem('NFH_LOG_LEVEL', level);
    // Reload to apply new level
    if (confirm('Reload page to apply new log level?')) {
      window.location.reload();
    }
  }
}

// Development helpers
export const devLog = {
  // Log intent recognition process
  logIntent(input, intent) {
    const logger = createLogger('IntentRecognition');
    logger.group(`Processing: "${input}"`);
    logger.debug('Raw input:', input);
    logger.debug('Recognized intent:', intent);
    logger.debug('Confidence:', intent.confidence);
    logger.debug('Entities:', intent.entities);
    logger.groupEnd();
  },

  // Log command building process
  logCommand(intent, command) {
    const logger = createLogger('CommandBuilder');
    logger.group('Building command');
    logger.debug('Intent:', intent);
    logger.debug('Built command:', command);
    logger.debug('Full command:', `${command.command} ${command.args.join(' ')}`);
    logger.groupEnd();
  },

  // Log execution process
  logExecution(command, result) {
    const logger = createLogger('CommandExecutor');
    logger.group('Executing command');
    logger.debug('Command:', command);
    if (result.success) {
      logger.info('✅ Success:', result.output);
    } else {
      logger.error('❌ Failed:', result.error);
    }
    logger.debug('Duration:', `${result.duration}ms`);
    logger.groupEnd();
  },

  // Log errors with context
  logError(error, context) {
    const logger = createLogger('ErrorHandler');
    logger.group('Error occurred');
    logger.error('Error:', error.message || error);
    logger.error('Stack:', error.stack);
    logger.debug('Context:', context);
    logger.groupEnd();
  }
};

// Default logger for general use
export const logger = createLogger('NixForHumanity');