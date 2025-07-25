/**
 * Example Theme Plugin
 * Adds custom themes to NixOS GUI
 */

const plugin = {
    id: 'theme-switcher',
    name: 'Theme Switcher',
    version: '1.0.0',
    author: 'NixOS GUI Team',
    description: 'Adds additional themes and theme switching capabilities',
    permissions: ['ui', 'storage', 'settings'],
    
    themes: {
        'nord': {
            name: 'Nord',
            colors: {
                '--bg-primary': '#2e3440',
                '--bg-secondary': '#3b4252',
                '--bg-tertiary': '#434c5e',
                '--text-primary': '#eceff4',
                '--text-secondary': '#d8dee9',
                '--primary-color': '#88c0d0',
                '--primary-hover': '#8fbcbb',
                '--success-color': '#a3be8c',
                '--error-color': '#bf616a',
                '--warning-color': '#ebcb8b',
                '--border-color': '#4c566a'
            }
        },
        'dracula': {
            name: 'Dracula',
            colors: {
                '--bg-primary': '#282a36',
                '--bg-secondary': '#44475a',
                '--bg-tertiary': '#6272a4',
                '--text-primary': '#f8f8f2',
                '--text-secondary': '#f8f8f2cc',
                '--primary-color': '#bd93f9',
                '--primary-hover': '#ff79c6',
                '--success-color': '#50fa7b',
                '--error-color': '#ff5555',
                '--warning-color': '#f1fa8c',
                '--border-color': '#6272a4'
            }
        },
        'solarized-dark': {
            name: 'Solarized Dark',
            colors: {
                '--bg-primary': '#002b36',
                '--bg-secondary': '#073642',
                '--bg-tertiary': '#586e75',
                '--text-primary': '#839496',
                '--text-secondary': '#657b83',
                '--primary-color': '#268bd2',
                '--primary-hover': '#2aa198',
                '--success-color': '#859900',
                '--error-color': '#dc322f',
                '--warning-color': '#b58900',
                '--border-color': '#586e75'
            }
        }
    },
    
    async init(api) {
        console.log('Theme Switcher plugin initializing...');
        
        // Store API reference
        this.api = api;
        
        // Load saved theme
        const savedTheme = api.storage.get('selected-theme');
        if (savedTheme && this.themes[savedTheme]) {
            this.applyTheme(savedTheme);
        }
        
        // Add theme menu
        this.addThemeMenu();
        
        // Add settings
        this.registerSettings();
        
        // Add dashboard widget
        this.addThemeWidget();
    },
    
    applyTheme(themeName) {
        const theme = this.themes[themeName];
        if (!theme) return;
        
        // Apply CSS variables
        const root = document.documentElement;
        Object.entries(theme.colors).forEach(([key, value]) => {
            root.style.setProperty(key, value);
        });
        
        // Save preference
        this.api.storage.set('selected-theme', themeName);
        
        // Show notification
        this.api.notifications.show(`Theme changed to ${theme.name}`, 'success');
    },
    
    addThemeMenu() {
        // Add menu item
        this.api.ui.addMenuItem('tools', {
            label: 'Themes',
            icon: 'icon-palette',
            action: () => this.showThemeSelector()
        });
    },
    
    showThemeSelector() {
        const modal = document.createElement('div');
        modal.className = 'theme-selector-modal';
        modal.innerHTML = `
            <div class="theme-selector-content">
                <h3>Select Theme</h3>
                <div class="theme-grid">
                    ${Object.entries(this.themes).map(([key, theme]) => `
                        <div class="theme-option" data-theme="${key}">
                            <div class="theme-preview">
                                <div class="preview-bar" style="background: ${theme.colors['--bg-primary']}"></div>
                                <div class="preview-bar" style="background: ${theme.colors['--bg-secondary']}"></div>
                                <div class="preview-bar" style="background: ${theme.colors['--primary-color']}"></div>
                            </div>
                            <span>${theme.name}</span>
                        </div>
                    `).join('')}
                </div>
                <button class="close-modal">Close</button>
            </div>
        `;
        
        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .theme-selector-modal {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10001;
            }
            .theme-selector-content {
                background: var(--bg-primary);
                padding: 24px;
                border-radius: 8px;
                max-width: 500px;
                width: 90%;
            }
            .theme-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 16px;
                margin: 20px 0;
            }
            .theme-option {
                cursor: pointer;
                text-align: center;
                padding: 12px;
                border-radius: 8px;
                transition: background 0.2s;
            }
            .theme-option:hover {
                background: var(--bg-secondary);
            }
            .theme-preview {
                display: flex;
                height: 40px;
                border-radius: 4px;
                overflow: hidden;
                margin-bottom: 8px;
            }
            .preview-bar {
                flex: 1;
            }
        `;
        document.head.appendChild(style);
        
        // Add event listeners
        modal.querySelectorAll('.theme-option').forEach(option => {
            option.addEventListener('click', () => {
                const theme = option.dataset.theme;
                this.applyTheme(theme);
                modal.remove();
                style.remove();
            });
        });
        
        modal.querySelector('.close-modal').addEventListener('click', () => {
            modal.remove();
            style.remove();
        });
        
        document.body.appendChild(modal);
    },
    
    registerSettings() {
        this.api.settings.define({
            'auto-theme': {
                type: 'boolean',
                label: 'Auto Theme',
                description: 'Automatically switch theme based on time of day',
                default: false
            },
            'day-theme': {
                type: 'select',
                label: 'Day Theme',
                description: 'Theme to use during daytime',
                options: Object.keys(this.themes),
                default: 'default'
            },
            'night-theme': {
                type: 'select',
                label: 'Night Theme',
                description: 'Theme to use during nighttime',
                options: Object.keys(this.themes),
                default: 'nord'
            }
        });
        
        // Watch for setting changes
        this.api.settings.onChanged((key, value) => {
            if (key === 'auto-theme' && value) {
                this.startAutoTheme();
            }
        });
    },
    
    addThemeWidget() {
        this.api.ui.addDashboardWidget({
            id: 'theme-status',
            title: 'Theme',
            content: `
                <div class="theme-widget">
                    <p>Current theme: <strong id="current-theme">Default</strong></p>
                    <button id="quick-theme-switch">Switch Theme</button>
                </div>
            `,
            render: (container) => {
                const currentTheme = this.api.storage.get('selected-theme') || 'default';
                container.querySelector('#current-theme').textContent = 
                    this.themes[currentTheme]?.name || 'Default';
                
                container.querySelector('#quick-theme-switch').addEventListener('click', () => {
                    this.showThemeSelector();
                });
            }
        });
    },
    
    startAutoTheme() {
        const checkTime = () => {
            const hour = new Date().getHours();
            const isNight = hour < 6 || hour >= 20;
            
            if (isNight) {
                const nightTheme = this.api.settings.get('night-theme');
                this.applyTheme(nightTheme);
            } else {
                const dayTheme = this.api.settings.get('day-theme');
                this.applyTheme(dayTheme);
            }
        };
        
        // Check immediately
        checkTime();
        
        // Check every hour
        setInterval(checkTime, 3600000);
    },
    
    hooks: {
        onDashboardLoad: async () => {
            console.log('Dashboard loaded - theme plugin active');
        }
    },
    
    cleanup() {
        console.log('Theme Switcher plugin cleaning up...');
        // Remove any custom styles or event listeners if needed
    }
};