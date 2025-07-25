// Main Application Controller
// Sacred initialization for consciousness-first NixOS GUI

class NixOSGUI {
    constructor() {
        this.currentTab = 'packages';
        this.websocket = null;
        this.coherenceLevel = 0.88;
        this.config = {
            apiUrl: window.location.protocol === 'https:' 
                ? 'https://' + window.location.hostname + ':8443'
                : 'http://' + window.location.hostname + ':8080',
            wsUrl: window.location.protocol === 'https:'
                ? 'wss://' + window.location.hostname + ':8443'
                : 'ws://' + window.location.hostname + ':8080'
        };
        
        // Initialize managers
        this.packageManager = null;
        this.serviceManager = null;
        this.configEditor = null;
        this.healthDashboard = null;
        this.aiAssistant = null;
        this.suggestions = null;
    }

    async init() {
        console.log('🌟 Initializing NixOS GUI with consciousness-first principles...');
        
        // Check authentication first
        if (!window.authManager.isAuthenticated()) {
            console.log('🔐 Authentication required');
            return;
        }
        
        // Set up tab navigation
        this.setupTabNavigation();
        
        // Initialize WebSocket connection with auth
        await this.initWebSocket();
        
        // Initialize feature managers
        await this.initializeManagers();
        
        // Start coherence monitoring
        this.startCoherenceMonitoring();
        
        // Update status
        this.updateStatus('connection-status', 'Connected');
        this.updateStatus('last-action', 'System initialized');
        
        // Display current user
        if (window.authManager.user) {
            const userDisplay = document.createElement('div');
            userDisplay.className = 'user-display';
            userDisplay.innerHTML = `
                <span>User: ${window.authManager.user.username}</span>
                <button onclick="window.authManager.logout()" class="logout-btn">Logout</button>
            `;
            document.querySelector('.sacred-header').appendChild(userDisplay);
        }
        
        console.log('✨ NixOS GUI ready. We flow together.');
    }

    setupTabNavigation() {
        const tabs = document.querySelectorAll('.nav-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabName = e.target.dataset.tab;
                this.switchTab(tabName);
            });
        });
    }

    switchTab(tabName) {
        // Sacred pause before switching context
        this.sacredPause(() => {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.add('hidden');
            });
            
            // Remove active class from all tabs
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            const selectedContent = document.getElementById(`${tabName}-tab`);
            if (selectedContent) {
                selectedContent.classList.remove('hidden');
            }
            
            // Mark tab as active
            const selectedTab = document.querySelector(`[data-tab="${tabName}"]`);
            if (selectedTab) {
                selectedTab.classList.add('active');
            }
            
            this.currentTab = tabName;
            this.updateStatus('last-action', `Switched to ${tabName}`);
            
            // Initialize tab-specific features
            this.initializeTabFeatures(tabName);
        });
    }

    sacredPause(callback) {
        // Implement consciousness-first pause
        const pauseIndicator = document.getElementById('sacred-pause');
        pauseIndicator.textContent = 'Pausing...';
        pauseIndicator.classList.add('sacred-pause-active');
        
        setTimeout(() => {
            callback();
            pauseIndicator.textContent = 'Active';
            pauseIndicator.classList.remove('sacred-pause-active');
        }, 300); // Brief pause to prevent accidental actions
    }

    async initWebSocket() {
        try {
            this.websocket = new WebSocket(this.config.wsUrl);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected');
                this.updateStatus('connection-status', 'Connected');
            };
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateStatus('connection-status', 'Error');
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket disconnected');
                this.updateStatus('connection-status', 'Disconnected');
                // Attempt reconnection after 5 seconds
                setTimeout(() => this.initWebSocket(), 5000);
            };
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
            // Continue without WebSocket - graceful degradation
        }
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'system-stats':
                if (this.healthDashboard) {
                    this.healthDashboard.updateStats(data.data);
                }
                break;
            case 'coherence-update':
                this.updateCoherence(data.coherence);
                break;
            case 'rebuild-progress':
                this.handleRebuildProgress(data.progress);
                break;
            default:
                console.log('Unknown WebSocket message type:', data.type);
        }
    }

    async initializeManagers() {
        // These will be initialized on-demand when tabs are accessed
        console.log('Managers ready for lazy initialization');
    }

    async initializeTabFeatures(tabName) {
        switch (tabName) {
            case 'packages':
                if (!this.packageManager) {
                    this.packageManager = new PackageManager(this.config.apiUrl);
                    await this.packageManager.init();
                }
                break;
            case 'services':
                if (!this.serviceManager) {
                    this.serviceManager = new ServiceManager(this.config.apiUrl);
                    await this.serviceManager.init();
                }
                break;
            case 'configuration':
                if (!this.configEditor) {
                    this.configEditor = new ConfigEditor(this.config.apiUrl);
                    await this.configEditor.init();
                }
                break;
            case 'system':
                if (!this.healthDashboard) {
                    this.healthDashboard = new HealthDashboard(this.websocket);
                    await this.healthDashboard.init();
                }
                break;
            case 'assistant':
                if (!this.aiAssistant) {
                    this.aiAssistant = new AIAssistant(this.config.apiUrl);
                    await this.aiAssistant.init();
                }
                break;
        }
    }

    startCoherenceMonitoring() {
        // Simulate coherence monitoring
        setInterval(() => {
            // Gentle fluctuation for visual feedback
            const baseCoherence = 0.88;
            const fluctuation = (Math.sin(Date.now() / 3000) * 0.02);
            this.coherenceLevel = (baseCoherence + fluctuation).toFixed(2);
            this.updateCoherence(this.coherenceLevel);
        }, 1000);
    }

    updateCoherence(level) {
        const coherenceValue = document.getElementById('coherence-value');
        if (coherenceValue) {
            coherenceValue.textContent = level;
            
            // Update color based on coherence level
            if (level > 0.9) {
                coherenceValue.style.color = '#00ff88';
            } else if (level > 0.7) {
                coherenceValue.style.color = '#00bfa5';
            } else {
                coherenceValue.style.color = '#ff9800';
            }
        }
    }

    updateStatus(elementId, status) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = status;
        }
    }

    handleRebuildProgress(progress) {
        // Update UI with rebuild progress
        this.updateStatus('last-action', `Rebuilding: ${progress}%`);
        
        if (this.configEditor) {
            this.configEditor.updateRebuildProgress(progress);
        }
    }

    // Global error handler with consciousness-first approach
    handleError(error, context) {
        console.error(`Error in ${context}:`, error);
        
        // Gentle error notification
        this.updateStatus('last-action', `Issue in ${context} - taking a sacred pause`);
        
        // Give user time to read the error
        this.sacredPause(() => {
            this.updateStatus('last-action', 'Ready');
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    // Initialize auth manager first
    await window.authManager.init();
    
    // Set up auth change listener
    window.authManager.onAuthChange = (authenticated) => {
        if (authenticated) {
            // Initialize main app when authenticated
            window.nixosGUI = new NixOSGUI();
            window.nixosGUI.init().catch(error => {
                console.error('Failed to initialize NixOS GUI:', error);
            });
        } else {
            // Clean up when logged out
            if (window.nixosGUI) {
                window.nixosGUI = null;
            }
        }
    };
    
    // If already authenticated, initialize immediately
    if (window.authManager.isAuthenticated()) {
        window.nixosGUI = new NixOSGUI();
        window.nixosGUI.init().catch(error => {
            console.error('Failed to initialize NixOS GUI:', error);
        });
    }
});

// Global helper functions
window.updateStatus = (status) => {
    if (window.nixosGUI) {
        window.nixosGUI.updateStatus('last-action', status);
    }
};

window.sacredPause = (callback) => {
    if (window.nixosGUI) {
        window.nixosGUI.sacredPause(callback);
    } else {
        setTimeout(callback, 300);
    }
};