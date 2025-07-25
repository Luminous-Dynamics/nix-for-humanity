// AI Configuration Assistant
// Natural language interface for NixOS configuration

class AIAssistant {
    constructor(apiUrl) {
        this.apiUrl = apiUrl;
        this.conversation = [];
        this.configPatterns = this.loadConfigPatterns();
        this.isProcessing = false;
    }

    async init() {
        console.log('🤖 Initializing AI Configuration Assistant...');
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Load previous conversation if exists
        this.loadConversation();
        
        // Display welcome message
        this.addMessage('assistant', 'Hello! I can help you configure NixOS using natural language. Try asking me to:', [
            '• "Enable Docker with GPU support"',
            '• "Set up a Python development environment"',
            '• "Configure automatic backups"',
            '• "Enable SSH access"',
            '• "Install and configure PostgreSQL"'
        ]);
        
        console.log('✨ AI Assistant ready');
    }

    loadConfigPatterns() {
        // Common configuration patterns and their NixOS equivalents
        return {
            // Services
            'docker': {
                patterns: ['docker', 'container', 'containerization'],
                configs: {
                    basic: {
                        code: 'virtualisation.docker.enable = true;',
                        description: 'Enable Docker service'
                    },
                    withGpu: {
                        code: `virtualisation.docker.enable = true;
hardware.nvidia.docker.enable = true;`,
                        description: 'Enable Docker with NVIDIA GPU support'
                    }
                },
                packages: ['docker', 'docker-compose']
            },
            
            'ssh': {
                patterns: ['ssh', 'remote access', 'openssh'],
                configs: {
                    basic: {
                        code: 'services.openssh.enable = true;',
                        description: 'Enable SSH server'
                    },
                    secure: {
                        code: `services.openssh = {
  enable = true;
  settings = {
    PasswordAuthentication = false;
    PermitRootLogin = "no";
  };
};`,
                        description: 'Enable SSH with key-only authentication'
                    }
                },
                packages: ['openssh']
            },
            
            'postgres': {
                patterns: ['postgres', 'postgresql', 'database'],
                configs: {
                    basic: {
                        code: `services.postgresql = {
  enable = true;
  package = pkgs.postgresql_15;
};`,
                        description: 'Enable PostgreSQL database server'
                    }
                },
                packages: ['postgresql']
            },
            
            // Development environments
            'python': {
                patterns: ['python', 'python development', 'pip'],
                configs: {
                    basic: {
                        code: `environment.systemPackages = with pkgs; [
  python3
  python3Packages.pip
  python3Packages.virtualenv
];`,
                        description: 'Python development environment'
                    }
                },
                packages: ['python3', 'python3-pip']
            },
            
            'nodejs': {
                patterns: ['node', 'nodejs', 'javascript', 'npm'],
                configs: {
                    basic: {
                        code: `environment.systemPackages = with pkgs; [
  nodejs_20
  nodePackages.npm
  nodePackages.yarn
];`,
                        description: 'Node.js development environment'
                    }
                },
                packages: ['nodejs', 'yarn']
            },
            
            // System features
            'firewall': {
                patterns: ['firewall', 'security', 'ports'],
                configs: {
                    basic: {
                        code: `networking.firewall = {
  enable = true;
  allowedTCPPorts = [ 80 443 ];
};`,
                        description: 'Enable firewall with web ports'
                    }
                }
            },
            
            'backup': {
                patterns: ['backup', 'backups', 'snapshot'],
                configs: {
                    basic: {
                        code: `services.borgbackup.jobs.main = {
  paths = [ "/home" "/etc" ];
  repo = "/backup/borg";
  startAt = "daily";
};`,
                        description: 'Daily backup configuration'
                    }
                },
                packages: ['borgbackup']
            }
        };
    }

    setupEventListeners() {
        const input = document.getElementById('assistant-input');
        const sendBtn = document.getElementById('assistant-send');
        
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.processUserInput();
                }
            });
        }
        
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.processUserInput());
        }
    }

    async processUserInput() {
        const input = document.getElementById('assistant-input');
        if (!input || !input.value.trim() || this.isProcessing) return;
        
        const userMessage = input.value.trim();
        input.value = '';
        
        // Add user message to conversation
        this.addMessage('user', userMessage);
        
        // Process the request
        this.isProcessing = true;
        this.showTypingIndicator();
        
        try {
            const response = await this.interpretRequest(userMessage);
            this.removeTypingIndicator();
            this.handleResponse(response);
        } catch (error) {
            console.error('Failed to process request:', error);
            this.removeTypingIndicator();
            this.addMessage('assistant', 'I encountered an error processing your request. Please try again.');
        } finally {
            this.isProcessing = false;
        }
    }

    async interpretRequest(userMessage) {
        const lowerMessage = userMessage.toLowerCase();
        
        // Check for configuration patterns
        for (const [key, pattern] of Object.entries(this.configPatterns)) {
            if (pattern.patterns.some(p => lowerMessage.includes(p))) {
                // Determine specific configuration variant
                const variant = this.determineVariant(lowerMessage, pattern);
                return {
                    type: 'config',
                    service: key,
                    variant: variant,
                    config: pattern.configs[variant],
                    packages: pattern.packages || []
                };
            }
        }
        
        // Check for package installation requests
        if (lowerMessage.includes('install') || lowerMessage.includes('add')) {
            const packageName = this.extractPackageName(lowerMessage);
            if (packageName) {
                return {
                    type: 'package',
                    action: 'install',
                    package: packageName
                };
            }
        }
        
        // Check for general queries
        if (lowerMessage.includes('help') || lowerMessage.includes('what can')) {
            return {
                type: 'help'
            };
        }
        
        // Default response for unrecognized requests
        return {
            type: 'unknown',
            suggestions: this.getSuggestions(lowerMessage)
        };
    }

    determineVariant(message, pattern) {
        // Determine which configuration variant to use based on context
        if (message.includes('gpu') && pattern.configs.withGpu) {
            return 'withGpu';
        }
        if (message.includes('secure') && pattern.configs.secure) {
            return 'secure';
        }
        return 'basic';
    }

    extractPackageName(message) {
        // Simple extraction - in production, use proper NLP
        const match = message.match(/install\s+(\S+)|add\s+(\S+)/i);
        return match ? (match[1] || match[2]) : null;
    }

    getSuggestions(message) {
        // Provide helpful suggestions based on keywords
        const suggestions = [];
        
        if (message.includes('dev') || message.includes('development')) {
            suggestions.push('Set up Python development environment');
            suggestions.push('Set up Node.js development environment');
        }
        
        if (message.includes('server')) {
            suggestions.push('Enable SSH access');
            suggestions.push('Configure PostgreSQL database');
        }
        
        return suggestions;
    }

    handleResponse(response) {
        switch (response.type) {
            case 'config':
                this.handleConfigResponse(response);
                break;
            case 'package':
                this.handlePackageResponse(response);
                break;
            case 'help':
                this.showHelp();
                break;
            case 'unknown':
                this.handleUnknownResponse(response);
                break;
        }
    }

    handleConfigResponse(response) {
        const { service, config, packages } = response;
        
        const message = `I'll help you configure ${service}. Here's the NixOS configuration:`;
        const codeBlock = `\`\`\`nix
${config.code}
\`\`\``;
        
        this.addMessage('assistant', message);
        this.addCodeBlock(config.code, config.description);
        
        if (packages && packages.length > 0) {
            this.addMessage('assistant', `This configuration will also ensure these packages are installed: ${packages.join(', ')}`);
        }
        
        // Add action buttons
        this.addActionButtons([
            {
                text: 'Apply to Configuration',
                action: () => this.applyConfiguration(config.code)
            },
            {
                text: 'Copy Code',
                action: () => this.copyToClipboard(config.code)
            }
        ]);
    }

    handlePackageResponse(response) {
        if (response.action === 'install') {
            this.addMessage('assistant', `I'll help you install ${response.package}. Searching for the package...`);
            
            // Trigger package search
            if (window.nixosGUI && window.nixosGUI.packageManager) {
                window.nixosGUI.switchTab('packages');
                setTimeout(() => {
                    document.getElementById('package-search').value = response.package;
                    document.getElementById('search-btn').click();
                }, 500);
            }
        }
    }

    showHelp() {
        this.addMessage('assistant', 'I can help you with:', [
            '**Services Configuration:**',
            '• Docker/Containers',
            '• SSH Server',
            '• PostgreSQL Database',
            '• Web Servers (Nginx, Apache)',
            '',
            '**Development Environments:**',
            '• Python',
            '• Node.js/JavaScript',
            '• Rust',
            '• Go',
            '',
            '**System Configuration:**',
            '• Firewall rules',
            '• User management',
            '• Automatic backups',
            '• System updates',
            '',
            'Just describe what you want in natural language!'
        ]);
    }

    handleUnknownResponse(response) {
        let message = "I'm not sure how to help with that specific request.";
        
        if (response.suggestions && response.suggestions.length > 0) {
            message += " Did you mean:";
            this.addMessage('assistant', message, response.suggestions.map(s => `• ${s}`));
        } else {
            this.addMessage('assistant', message + " Try asking about services, packages, or development environments.");
        }
    }

    async applyConfiguration(code) {
        try {
            // Switch to configuration tab
            window.nixosGUI.switchTab('configuration');
            
            // Add code to configuration
            setTimeout(() => {
                const editor = document.getElementById('config-editor');
                if (editor) {
                    // Add code at appropriate position
                    const currentConfig = editor.value;
                    const insertPosition = this.findInsertPosition(currentConfig);
                    
                    const newConfig = 
                        currentConfig.slice(0, insertPosition) + 
                        '\n  # Added by AI Assistant\n  ' + 
                        code + '\n' +
                        currentConfig.slice(insertPosition);
                    
                    editor.value = newConfig;
                    
                    // Highlight the added section
                    editor.focus();
                    editor.setSelectionRange(insertPosition, insertPosition + code.length + 30);
                    
                    this.addMessage('assistant', '✅ Configuration added! Review the changes in the Configuration tab.');
                }
            }, 500);
        } catch (error) {
            console.error('Failed to apply configuration:', error);
            this.addMessage('assistant', '❌ Failed to apply configuration. Please try manually.');
        }
    }

    findInsertPosition(config) {
        // Find appropriate position to insert new configuration
        // Look for the end of the main configuration block
        const lines = config.split('\n');
        let braceCount = 0;
        let position = 0;
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            position += line.length + 1; // +1 for newline
            
            if (line.includes('{')) braceCount++;
            if (line.includes('}')) braceCount--;
            
            // Insert before the last closing brace
            if (braceCount === 1 && lines[i + 1] && lines[i + 1].trim() === '}') {
                return position;
            }
        }
        
        // Fallback: insert before the last line
        return config.lastIndexOf('\n');
    }

    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.addMessage('assistant', '✅ Code copied to clipboard!');
        }).catch(() => {
            this.addMessage('assistant', '❌ Failed to copy to clipboard.');
        });
    }

    addMessage(sender, text, listItems = null) {
        const messagesContainer = document.getElementById('assistant-messages');
        if (!messagesContainer) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `assistant-message ${sender}`;
        
        let content = `<strong>${sender === 'user' ? 'You' : 'Assistant'}:</strong> ${text}`;
        
        if (listItems) {
            content += '<br>' + listItems.join('<br>');
        }
        
        messageDiv.innerHTML = content;
        messagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Save conversation
        this.saveConversation();
    }

    addCodeBlock(code, description) {
        const messagesContainer = document.getElementById('assistant-messages');
        if (!messagesContainer) return;
        
        const codeDiv = document.createElement('div');
        codeDiv.className = 'code-block';
        codeDiv.innerHTML = `
            <div class="code-description">${description}</div>
            <pre><code>${this.escapeHtml(code)}</code></pre>
        `;
        
        messagesContainer.appendChild(codeDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    addActionButtons(actions) {
        const messagesContainer = document.getElementById('assistant-messages');
        if (!messagesContainer) return;
        
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'assistant-actions';
        
        actions.forEach(action => {
            const button = document.createElement('button');
            button.className = 'sacred-btn secondary';
            button.textContent = action.text;
            button.onclick = action.action;
            actionsDiv.appendChild(button);
        });
        
        messagesContainer.appendChild(actionsDiv);
    }

    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'typing-indicator';
        indicator.className = 'typing-indicator';
        indicator.innerHTML = '<span></span><span></span><span></span>';
        
        const messagesContainer = document.getElementById('assistant-messages');
        if (messagesContainer) {
            messagesContainer.appendChild(indicator);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    saveConversation() {
        // Save conversation to localStorage for persistence
        try {
            const messages = Array.from(document.querySelectorAll('.assistant-message')).map(el => ({
                sender: el.classList.contains('user') ? 'user' : 'assistant',
                content: el.innerHTML
            }));
            
            localStorage.setItem('nixos-gui-conversation', JSON.stringify(messages));
        } catch (error) {
            console.error('Failed to save conversation:', error);
        }
    }

    loadConversation() {
        try {
            const saved = localStorage.getItem('nixos-gui-conversation');
            if (saved) {
                const messages = JSON.parse(saved);
                const container = document.getElementById('assistant-messages');
                if (container && messages.length > 0) {
                    // Clear welcome message
                    container.innerHTML = '';
                    
                    // Restore messages
                    messages.forEach(msg => {
                        const messageDiv = document.createElement('div');
                        messageDiv.className = `assistant-message ${msg.sender}`;
                        messageDiv.innerHTML = msg.content;
                        container.appendChild(messageDiv);
                    });
                }
            }
        } catch (error) {
            console.error('Failed to load conversation:', error);
        }
    }
}

// Add typing indicator styles
const style = document.createElement('style');
style.textContent = `
.typing-indicator {
    display: flex;
    align-items: center;
    margin: 10px 0;
}

.typing-indicator span {
    height: 8px;
    width: 8px;
    background-color: var(--sacred-text-dim);
    border-radius: 50%;
    display: inline-block;
    margin: 0 2px;
    animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typing {
    0%, 60%, 100% {
        transform: translateY(0);
        opacity: 0.7;
    }
    30% {
        transform: translateY(-10px);
        opacity: 1;
    }
}

.code-block {
    background: var(--sacred-bg);
    border: 1px solid var(--sacred-border);
    border-radius: 8px;
    padding: var(--sacred-space-md);
    margin: var(--sacred-space-sm) 0;
}

.code-description {
    color: var(--sacred-text-dim);
    font-size: 0.9em;
    margin-bottom: var(--sacred-space-sm);
}

.code-block pre {
    margin: 0;
    overflow-x: auto;
}

.code-block code {
    color: var(--sacred-primary);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9em;
}

.assistant-actions {
    display: flex;
    gap: var(--sacred-space-sm);
    margin: var(--sacred-space-sm) 0;
}

.assistant-message.user {
    background: var(--sacred-bg);
    padding: var(--sacred-space-sm);
    border-radius: 8px;
    margin-bottom: var(--sacred-space-sm);
}
`;
document.head.appendChild(style);