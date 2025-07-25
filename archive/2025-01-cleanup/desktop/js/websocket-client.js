// WebSocket Client for Real-time System Updates
// Handles live system stats, rebuild progress, and coherence updates

class WebSocketClient {
    constructor(url) {
        this.url = url;
        this.ws = null;
        this.reconnectInterval = 5000;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.handlers = new Map();
        this.isConnected = false;
        
        // Register default handlers
        this.registerDefaultHandlers();
    }

    connect() {
        return new Promise((resolve, reject) => {
            try {
                this.ws = new WebSocket(this.url);
                
                this.ws.onopen = () => {
                    console.log('✨ WebSocket connected to sacred stream');
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                    this.emit('connection', { status: 'connected' });
                    resolve();
                };
                
                this.ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        this.handleMessage(data);
                    } catch (error) {
                        console.error('Failed to parse WebSocket message:', error);
                    }
                };
                
                this.ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    this.emit('error', { error });
                };
                
                this.ws.onclose = () => {
                    console.log('WebSocket disconnected');
                    this.isConnected = false;
                    this.emit('connection', { status: 'disconnected' });
                    this.attemptReconnect();
                };
            } catch (error) {
                reject(error);
            }
        });
    }

    registerDefaultHandlers() {
        // System stats handler
        this.on('system-stats', (data) => {
            // Update global stats display
            if (window.nixosGUI && window.nixosGUI.healthDashboard) {
                window.nixosGUI.healthDashboard.updateStats(data);
            }
        });
        
        // Coherence updates
        this.on('coherence-update', (data) => {
            if (window.nixosGUI) {
                window.nixosGUI.updateCoherence(data.level);
            }
        });
        
        // Service status updates
        this.on('service-status', (data) => {
            if (window.nixosGUI && window.nixosGUI.serviceManager) {
                window.nixosGUI.serviceManager.updateServiceStatus(data);
            }
        });
    }

    handleMessage(data) {
        const { type, payload } = data;
        
        if (this.handlers.has(type)) {
            const handlers = this.handlers.get(type);
            handlers.forEach(handler => {
                try {
                    handler(payload);
                } catch (error) {
                    console.error(`Error in handler for ${type}:`, error);
                }
            });
        }
    }

    on(event, handler) {
        if (!this.handlers.has(event)) {
            this.handlers.set(event, []);
        }
        this.handlers.get(event).push(handler);
    }

    off(event, handler) {
        if (this.handlers.has(event)) {
            const handlers = this.handlers.get(event);
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }

    emit(event, data) {
        this.handleMessage({ type: event, payload: data });
    }

    send(type, data) {
        if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type, data }));
        } else {
            console.warn('WebSocket not connected, queuing message');
            // Could implement message queue here
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting reconnect ${this.reconnectAttempts}/${this.maxReconnectAttempts}...`);
            
            setTimeout(() => {
                this.connect().catch(error => {
                    console.error('Reconnection failed:', error);
                });
            }, this.reconnectInterval);
        } else {
            console.error('Max reconnection attempts reached');
            this.emit('connection', { status: 'failed' });
        }
    }

    // Subscribe to specific data streams
    subscribe(stream) {
        this.send('subscribe', { stream });
    }

    unsubscribe(stream) {
        this.send('unsubscribe', { stream });
    }

    close() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
            this.isConnected = false;
        }
    }
}

// Create global WebSocket instance
window.wsClient = null;

// Initialize WebSocket when needed
window.initWebSocket = async function(url) {
    // Get auth token
    const token = window.authManager?.token;
    if (!token) {
        console.error('No auth token available for WebSocket');
        return null;
    }
    
    if (!window.wsClient) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const port = window.location.protocol === 'https:' ? '8443' : '8080';
        const wsUrl = url || `${protocol}//${window.location.hostname}:${port}`;
        
        window.wsClient = new WebSocketClient(wsUrl);
        
        // Add auth token to connection
        window.wsClient.authToken = token;
        
        try {
            await window.wsClient.connect();
            
            // Subscribe to default streams
            window.wsClient.subscribe('system-stats');
            window.wsClient.subscribe('service-status');
            
            return window.wsClient;
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
            return null;
        }
    }
    return window.wsClient;
};