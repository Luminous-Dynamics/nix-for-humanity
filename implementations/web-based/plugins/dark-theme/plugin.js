/**
 * Dark Theme Plugin for Nix for Humanity
 * A beautiful, calming dark interface
 */

(function() {
    const { NixForHumanity, plugin } = window.__currentPluginContext;
    
    // Plugin initialization
    console.log(`🌙 Dark Theme Plugin v${plugin.version} loading...`);
    
    // Define the dark theme
    const darkTheme = {
        name: 'Dark Elegance',
        colors: {
            background: '#0a0a0a',
            surface: 'rgba(255, 255, 255, 0.05)',
            primary: '#3b82f6',
            secondary: '#8b5cf6',
            success: '#10b981',
            error: '#ef4444',
            text: '#ffffff',
            textSecondary: 'rgba(255, 255, 255, 0.7)'
        },
        styles: `
            body {
                background: #0a0a0a;
                color: #ffffff;
                transition: all 0.3s ease;
            }
            
            .search-box {
                background: rgba(255, 255, 255, 0.05);
                border-color: rgba(255, 255, 255, 0.1);
                color: #ffffff;
            }
            
            .search-box:focus {
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
            
            .action-button {
                background: rgba(59, 130, 246, 0.1);
                border-color: #3b82f6;
            }
            
            .action-button:hover {
                background: rgba(59, 130, 246, 0.2);
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            }
            
            /* Smooth animations */
            * {
                transition: background-color 0.3s ease, 
                           border-color 0.3s ease,
                           transform 0.2s ease;
            }
            
            /* Glow effects */
            .listen-indicator.listening {
                box-shadow: 0 0 30px rgba(59, 130, 246, 0.5);
            }
            
            /* Elegant scrollbars */
            ::-webkit-scrollbar {
                width: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: rgba(255, 255, 255, 0.05);
            }
            
            ::-webkit-scrollbar-thumb {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: rgba(255, 255, 255, 0.3);
            }
        `
    };
    
    // Apply theme on load
    function applyTheme() {
        // Get stored settings
        const accentColor = NixForHumanity.storage.get('accentColor') || '#3b82f6';
        const animations = NixForHumanity.storage.get('animations') !== false;
        
        // Create or update style element
        let styleEl = document.getElementById('dark-theme-styles');
        if (!styleEl) {
            styleEl = document.createElement('style');
            styleEl.id = 'dark-theme-styles';
            document.head.appendChild(styleEl);
        }
        
        // Apply theme with custom accent color
        let styles = darkTheme.styles.replace(/#3b82f6/g, accentColor);
        
        // Disable animations if requested
        if (!animations) {
            styles += `
                * {
                    animation: none !important;
                    transition: none !important;
                }
            `;
        }
        
        styleEl.textContent = styles;
        
        // Notify UI system
        NixForHumanity.ui.setTheme('dark-elegance');
    }
    
    // Hook into UI ready event
    NixForHumanity.hook('onUIReady', () => {
        console.log('🌙 Applying Dark Theme...');
        applyTheme();
        
        // Add theme toggle button
        NixForHumanity.ui.showActions([{
            label: '🌙 Dark Theme Applied',
            description: 'Click to customize',
            action: () => showThemeSettings()
        }]);
        
        return true;
    });
    
    // Settings panel
    function showThemeSettings() {
        const currentAccent = NixForHumanity.storage.get('accentColor') || '#3b82f6';
        const animationsEnabled = NixForHumanity.storage.get('animations') !== false;
        
        // Create settings UI
        const settingsHTML = `
            <div style="padding: 1rem;">
                <h3>Dark Theme Settings</h3>
                <div style="margin: 1rem 0;">
                    <label>Accent Color:</label>
                    <input type="color" id="theme-accent" value="${currentAccent}" 
                           style="margin-left: 1rem; cursor: pointer;">
                </div>
                <div style="margin: 1rem 0;">
                    <label>
                        <input type="checkbox" id="theme-animations" 
                               ${animationsEnabled ? 'checked' : ''}>
                        Enable Animations
                    </label>
                </div>
            </div>
        `;
        
        NixForHumanity.ui.showMessage(settingsHTML, 'info');
        
        // Handle changes
        document.getElementById('theme-accent').addEventListener('change', (e) => {
            NixForHumanity.storage.set('accentColor', e.target.value);
            applyTheme();
            NixForHumanity.ui.celebrate('success');
        });
        
        document.getElementById('theme-animations').addEventListener('change', (e) => {
            NixForHumanity.storage.set('animations', e.target.checked);
            applyTheme();
        });
    }
    
    // Hook into theme change requests
    NixForHumanity.hook('onThemeChange', (theme) => {
        if (theme !== 'dark-elegance') {
            // Remove our styles if another theme is selected
            const styleEl = document.getElementById('dark-theme-styles');
            if (styleEl) {
                styleEl.remove();
            }
        }
        return theme;
    });
    
    // Success celebration enhancement
    NixForHumanity.hook('onSuccess', (data) => {
        // Add extra sparkle to success messages
        const accentColor = NixForHumanity.storage.get('accentColor') || '#3b82f6';
        
        // Create celebration effect
        const celebration = document.createElement('div');
        celebration.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 3rem;
            animation: celebrate 1s ease-out;
            pointer-events: none;
            z-index: 9999;
        `;
        celebration.textContent = '✨';
        document.body.appendChild(celebration);
        
        setTimeout(() => celebration.remove(), 1000);
        
        return data;
    });
    
    console.log('🌙 Dark Theme Plugin loaded successfully!');
})();