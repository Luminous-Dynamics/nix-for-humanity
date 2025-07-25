// Authentication Manager
// Handles login, logout, and token management

class AuthManager {
    constructor() {
        this.token = localStorage.getItem('nixos-gui-token');
        this.user = null;
        this.onAuthChange = null;
    }

    async init() {
        console.log('🔐 Initializing Authentication Manager...');
        
        // Verify existing token if present
        if (this.token) {
            await this.verifyToken();
        }
        
        // Show login screen if not authenticated
        if (!this.isAuthenticated()) {
            this.showLoginScreen();
        }
    }

    isAuthenticated() {
        return !!this.token && !!this.user;
    }

    getAuthHeaders() {
        return this.token ? { 'Authorization': `Bearer ${this.token}` } : {};
    }

    async verifyToken() {
        if (!this.token) return false;
        
        try {
            const response = await fetch(`${window.nixosGUI.config.apiUrl}/api/auth/verify`, {
                headers: this.getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                this.user = data.user;
                return true;
            } else {
                this.clearAuth();
                return false;
            }
        } catch (error) {
            console.error('Token verification failed:', error);
            this.clearAuth();
            return false;
        }
    }

    async login(username, password) {
        try {
            const response = await fetch(`${window.nixosGUI.config.apiUrl}/api/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.token = data.token;
                this.user = data.user;
                
                // Save token
                localStorage.setItem('nixos-gui-token', this.token);
                
                // Notify listeners
                if (this.onAuthChange) {
                    this.onAuthChange(true);
                }
                
                // Hide login screen
                this.hideLoginScreen();
                
                // Initialize WebSocket with auth
                if (window.wsClient) {
                    window.wsClient.close();
                }
                await window.initWebSocket();
                
                return true;
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Login failed');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.showError(error.message);
            return false;
        }
    }

    async logout() {
        try {
            await fetch(`${window.nixosGUI.config.apiUrl}/api/auth/logout`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });
        } catch (error) {
            console.error('Logout error:', error);
        }
        
        this.clearAuth();
        this.showLoginScreen();
        
        if (this.onAuthChange) {
            this.onAuthChange(false);
        }
    }

    clearAuth() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('nixos-gui-token');
        
        // Close WebSocket
        if (window.wsClient) {
            window.wsClient.close();
        }
    }

    showLoginScreen() {
        // Hide main app
        const app = document.getElementById('app');
        if (app) {
            app.style.display = 'none';
        }
        
        // Create login screen if it doesn't exist
        let loginScreen = document.getElementById('login-screen');
        if (!loginScreen) {
            loginScreen = this.createLoginScreen();
            document.body.appendChild(loginScreen);
        }
        
        loginScreen.style.display = 'flex';
        
        // Focus username field
        setTimeout(() => {
            document.getElementById('login-username')?.focus();
        }, 100);
    }

    hideLoginScreen() {
        const loginScreen = document.getElementById('login-screen');
        if (loginScreen) {
            loginScreen.style.display = 'none';
        }
        
        const app = document.getElementById('app');
        if (app) {
            app.style.display = 'flex';
        }
        
        // Reinitialize the app
        if (window.nixosGUI) {
            window.nixosGUI.init();
        }
    }

    createLoginScreen() {
        const screen = document.createElement('div');
        screen.id = 'login-screen';
        screen.className = 'login-screen';
        screen.innerHTML = `
            <div class="login-container">
                <div class="login-header">
                    <h1>NixOS GUI</h1>
                    <p class="login-subtitle">Consciousness-First Configuration</p>
                </div>
                
                <form id="login-form" class="login-form">
                    <div class="form-group">
                        <label for="login-username">Username</label>
                        <input 
                            type="text" 
                            id="login-username" 
                            class="sacred-input" 
                            required
                            autocomplete="username"
                        />
                    </div>
                    
                    <div class="form-group">
                        <label for="login-password">Password</label>
                        <input 
                            type="password" 
                            id="login-password" 
                            class="sacred-input" 
                            required
                            autocomplete="current-password"
                        />
                    </div>
                    
                    <div id="login-error" class="login-error hidden"></div>
                    
                    <button type="submit" class="sacred-btn primary login-btn">
                        Login
                    </button>
                </form>
                
                <div class="login-footer">
                    <p class="security-note">
                        🔒 Secure connection required<br>
                        📝 Demo: admin / any-password
                    </p>
                </div>
            </div>
        `;
        
        // Add event listener
        setTimeout(() => {
            const form = document.getElementById('login-form');
            if (form) {
                form.addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.handleLogin();
                });
            }
        }, 0);
        
        return screen;
    }

    async handleLogin() {
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;
        
        if (!username || !password) {
            this.showError('Please enter username and password');
            return;
        }
        
        // Show loading state
        const button = document.querySelector('.login-btn');
        const originalText = button.textContent;
        button.textContent = 'Logging in...';
        button.disabled = true;
        
        const success = await this.login(username, password);
        
        if (!success) {
            button.textContent = originalText;
            button.disabled = false;
        }
    }

    showError(message) {
        const errorDiv = document.getElementById('login-error');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.classList.remove('hidden');
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                errorDiv.classList.add('hidden');
            }, 5000);
        }
    }

    // API request wrapper with authentication
    async authenticatedFetch(url, options = {}) {
        const authHeaders = this.getAuthHeaders();
        
        const response = await fetch(url, {
            ...options,
            headers: {
                ...options.headers,
                ...authHeaders
            }
        });
        
        if (response.status === 401 || response.status === 403) {
            // Token expired or invalid
            this.clearAuth();
            this.showLoginScreen();
            throw new Error('Authentication required');
        }
        
        return response;
    }
}

// Login screen styles
const authStyles = document.createElement('style');
authStyles.textContent = `
.login-screen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, var(--sacred-bg) 0%, #0d1420 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
}

.login-container {
    background: var(--sacred-bg-light);
    border: 1px solid var(--sacred-border);
    border-radius: 12px;
    padding: var(--sacred-space-xl);
    width: 100%;
    max-width: 400px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.login-header {
    text-align: center;
    margin-bottom: var(--sacred-space-xl);
}

.login-header h1 {
    font-size: 2rem;
    font-weight: 300;
    background: linear-gradient(135deg, var(--sacred-primary), var(--sacred-secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: var(--sacred-space-sm);
}

.login-subtitle {
    color: var(--sacred-text-dim);
    font-size: 0.95rem;
}

.login-form {
    margin-bottom: var(--sacred-space-lg);
}

.form-group {
    margin-bottom: var(--sacred-space-md);
}

.form-group label {
    display: block;
    margin-bottom: var(--sacred-space-xs);
    color: var(--sacred-text-dim);
    font-size: 0.9rem;
}

.login-btn {
    width: 100%;
    padding: var(--sacred-space-md);
    font-size: 1rem;
}

.login-error {
    background: rgba(255, 107, 107, 0.1);
    border: 1px solid rgba(255, 107, 107, 0.3);
    color: #ff6b6b;
    padding: var(--sacred-space-sm);
    border-radius: 4px;
    margin-bottom: var(--sacred-space-md);
    text-align: center;
    font-size: 0.9rem;
}

.login-footer {
    text-align: center;
}

.security-note {
    color: var(--sacred-text-dim);
    font-size: 0.85rem;
    line-height: 1.5;
}

/* Sacred login animation */
@keyframes sacred-glow {
    0%, 100% { box-shadow: 0 0 20px rgba(74, 158, 255, 0.2); }
    50% { box-shadow: 0 0 30px rgba(74, 158, 255, 0.4); }
}

.login-container:focus-within {
    animation: sacred-glow 3s infinite;
}
`;
document.head.appendChild(authStyles);

// Create global auth manager
window.authManager = new AuthManager();