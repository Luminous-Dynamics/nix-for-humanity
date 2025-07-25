/**
 * User-Friendly Error Handler for Nix for Humanity
 * Translates technical errors into helpful guidance
 */

class ErrorHandler {
  constructor() {
    // Map technical errors to user-friendly messages
    this.errorMappings = {
      // Package errors
      'ENOENT': {
        message: 'Package not found',
        suggestion: 'Try searching with "search {package}" to find the correct name',
        recoverable: true
      },
      'attribute .* missing': {
        message: "I couldn't find that package",
        suggestion: 'The package name might be different. Try searching for it first',
        recoverable: true
      },
      'Permission denied': {
        message: 'I need administrator privileges for that',
        suggestion: 'This operation requires sudo access. Please authenticate when prompted',
        recoverable: true
      },
      'EACCES': {
        message: 'Permission denied',
        suggestion: 'This operation requires administrator privileges',
        recoverable: true
      },
      'No space left': {
        message: "Your disk is full",
        suggestion: 'Try running "clean up" to free some space',
        recoverable: true
      },
      'ENETUNREACH': {
        message: 'Cannot reach the package repository',
        suggestion: 'Check your internet connection and try again',
        recoverable: true
      },
      'ETIMEDOUT': {
        message: 'The operation is taking too long',
        suggestion: 'The server might be slow. Please try again in a few moments',
        recoverable: true
      },
      'already installed': {
        message: 'That package is already installed',
        suggestion: 'Would you like to update it instead?',
        recoverable: true
      },
      'collision between': {
        message: 'Package conflict detected',
        suggestion: 'Two packages are trying to install the same file. This usually happens with similar programs',
        recoverable: false
      },
      'infinite recursion': {
        message: 'Configuration error detected',
        suggestion: 'There\'s a circular dependency in your configuration. Please check for packages that depend on each other',
        recoverable: false
      },
      'syntax error': {
        message: 'Configuration syntax error',
        suggestion: 'There\'s a formatting error in your configuration file. Check for missing semicolons or brackets',
        recoverable: false
      },
      'command not found': {
        message: "I don't recognize that command",
        suggestion: 'Try rephrasing your request or type "help" for examples',
        recoverable: true
      }
    };

    // Context-aware error messages
    this.contextualErrors = {
      install: {
        failed: 'I couldn\'t install {package}',
        suggestion: 'This might be due to network issues or the package name being incorrect'
      },
      remove: {
        failed: 'I couldn\'t remove {package}',
        suggestion: 'Make sure the package is actually installed'
      },
      update: {
        failed: 'I couldn\'t update the system',
        suggestion: 'Check your internet connection and available disk space'
      },
      service: {
        failed: 'I couldn\'t {operation} the {service} service',
        suggestion: 'Make sure the service exists and you have the right permissions'
      }
    };

    // Friendly explanations for common scenarios
    this.explanations = {
      firstTime: 'Looks like this is your first time doing this. Let me help you through it',
      needsAuth: 'This operation needs administrator access to keep your system safe',
      willTakeTime: 'This might take a few minutes. I\'ll let you know when it\'s done',
      safetyCheck: 'I\'m checking if this is safe to do first',
      learningMoment: 'Here\'s what happened and how we can fix it'
    };
  }

  // Main error handling method
  handle(error, context = {}) {
    // Log original error for debugging
    console.error('Original error:', error);

    // Extract error details
    const errorMessage = error.message || error.toString();
    const errorCode = error.code || '';
    
    // Try to find a user-friendly translation
    let userError = this.translateError(errorMessage, errorCode);
    
    // Add context if available
    if (context.operation && context.target) {
      userError = this.addContext(userError, context);
    }

    // Add recovery options
    userError.recovery = this.getRecoveryOptions(error, context);

    // Add learning opportunity if applicable
    if (this.isLearningOpportunity(error)) {
      userError.learning = this.getLearningContent(error, context);
    }

    return userError;
  }

  // Translate technical errors to user-friendly messages
  translateError(message, code) {
    // Check exact code match first
    if (code && this.errorMappings[code]) {
      return { ...this.errorMappings[code] };
    }

    // Check pattern matching
    for (const [pattern, mapping] of Object.entries(this.errorMappings)) {
      if (message.match(new RegExp(pattern, 'i'))) {
        return { ...mapping };
      }
    }

    // Default user-friendly error
    return {
      message: "Something went wrong",
      suggestion: "I encountered an unexpected issue. Let's try a different approach",
      recoverable: true,
      technical: message // Include technical details for advanced users
    };
  }

  // Add context to error messages
  addContext(error, context) {
    const { operation, target } = context;
    
    if (this.contextualErrors[operation]) {
      error.message = this.contextualErrors[operation].failed
        .replace('{package}', target)
        .replace('{service}', target)
        .replace('{operation}', operation);
      
      if (!error.suggestion) {
        error.suggestion = this.contextualErrors[operation].suggestion;
      }
    }

    return error;
  }

  // Get recovery options based on error type
  getRecoveryOptions(error, context) {
    const options = [];

    // Network errors
    if (error.code === 'ENETUNREACH' || error.code === 'ETIMEDOUT') {
      options.push({
        action: 'retry',
        description: 'Try again',
        command: context.originalCommand
      });
      options.push({
        action: 'check-network',
        description: 'Check network status',
        command: 'show network status'
      });
    }

    // Permission errors
    if (error.code === 'EACCES' || error.message.includes('Permission denied')) {
      options.push({
        action: 'authenticate',
        description: 'Try with administrator privileges',
        command: `sudo ${context.originalCommand}`
      });
    }

    // Package not found
    if (error.message.includes('not found') || error.message.includes('missing')) {
      options.push({
        action: 'search',
        description: 'Search for similar packages',
        command: `search ${context.target || 'package'}`
      });
      options.push({
        action: 'list',
        description: 'Show installed packages',
        command: 'list installed'
      });
    }

    // Disk space
    if (error.message.includes('No space left')) {
      options.push({
        action: 'cleanup',
        description: 'Free up disk space',
        command: 'clean up old versions'
      });
      options.push({
        action: 'check-space',
        description: 'Check disk usage',
        command: 'show disk usage'
      });
    }

    // Always provide help option
    options.push({
      action: 'help',
      description: 'Get help with this issue',
      command: 'help'
    });

    return options;
  }

  // Determine if this error is a learning opportunity
  isLearningOpportunity(error) {
    const learningErrors = [
      'not found',
      'missing',
      'syntax error',
      'collision',
      'recursion'
    ];

    return learningErrors.some(pattern => 
      error.message.toLowerCase().includes(pattern)
    );
  }

  // Get educational content for the error
  getLearningContent(error, context) {
    const content = {
      title: 'Learning Moment',
      explanation: '',
      tips: []
    };

    if (error.message.includes('not found')) {
      content.explanation = 'Package names in NixOS are sometimes different from other systems';
      content.tips = [
        'Use "search" to find the exact package name',
        'Package names are case-sensitive',
        'Some packages have prefixes like "python3-" or "perl-"'
      ];
    } else if (error.message.includes('collision')) {
      content.explanation = 'Package collisions happen when two packages try to install the same file';
      content.tips = [
        'You might have two similar programs installed',
        'Try removing one before installing the other',
        'Some packages have "-full" or "-minimal" variants'
      ];
    } else if (error.message.includes('syntax')) {
      content.explanation = 'NixOS configuration uses a specific syntax';
      content.tips = [
        'Every statement should end with a semicolon',
        'Lists use square brackets [ ]',
        'Attributes use curly braces { }'
      ];
    }

    return content;
  }

  // Format error for different output types
  format(error, outputType = 'text') {
    switch (outputType) {
      case 'voice':
        return this.formatForVoice(error);
      case 'json':
        return JSON.stringify(error, null, 2);
      case 'html':
        return this.formatForHTML(error);
      default:
        return this.formatForText(error);
    }
  }

  // Format error for voice output
  formatForVoice(error) {
    let voice = error.message;
    
    if (error.suggestion) {
      voice += `. ${error.suggestion}`;
    }
    
    if (error.recovery && error.recovery.length > 0) {
      voice += `. Would you like me to ${error.recovery[0].description}?`;
    }
    
    return voice;
  }

  // Format error for text output
  formatForText(error) {
    let text = `❌ ${error.message}\n`;
    
    if (error.suggestion) {
      text += `\n💡 ${error.suggestion}\n`;
    }
    
    if (error.recovery && error.recovery.length > 0) {
      text += '\n🔧 What you can do:\n';
      error.recovery.forEach((option, index) => {
        text += `   ${index + 1}. ${option.description}\n`;
        if (option.command) {
          text += `      → ${option.command}\n`;
        }
      });
    }
    
    if (error.learning) {
      text += `\n📚 ${error.learning.title}: ${error.learning.explanation}\n`;
      if (error.learning.tips.length > 0) {
        text += '   Tips:\n';
        error.learning.tips.forEach(tip => {
          text += `   • ${tip}\n`;
        });
      }
    }
    
    if (error.technical && process.env.DEBUG) {
      text += `\n🔍 Technical details: ${error.technical}\n`;
    }
    
    return text;
  }

  // Format error for HTML output
  formatForHTML(error) {
    let html = '<div class="error-message">';
    html += `<h3 class="error-title">❌ ${this.escapeHtml(error.message)}</h3>`;
    
    if (error.suggestion) {
      html += `<p class="error-suggestion">💡 ${this.escapeHtml(error.suggestion)}</p>`;
    }
    
    if (error.recovery && error.recovery.length > 0) {
      html += '<div class="error-recovery">';
      html += '<h4>🔧 What you can do:</h4>';
      html += '<ul>';
      error.recovery.forEach(option => {
        html += '<li>';
        html += this.escapeHtml(option.description);
        if (option.command) {
          html += ` <code>${this.escapeHtml(option.command)}</code>`;
        }
        html += '</li>';
      });
      html += '</ul>';
      html += '</div>';
    }
    
    if (error.learning) {
      html += '<div class="error-learning">';
      html += `<h4>📚 ${this.escapeHtml(error.learning.title)}</h4>`;
      html += `<p>${this.escapeHtml(error.learning.explanation)}</p>`;
      if (error.learning.tips.length > 0) {
        html += '<ul>';
        error.learning.tips.forEach(tip => {
          html += `<li>${this.escapeHtml(tip)}</li>`;
        });
        html += '</ul>';
      }
      html += '</div>';
    }
    
    html += '</div>';
    return html;
  }

  // Escape HTML to prevent XSS
  escapeHtml(text) {
    const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#x27;',
      '/': '&#x2F;'
    };
    return text.replace(/[&<>"'/]/g, char => map[char]);
  }
}

module.exports = ErrorHandler;