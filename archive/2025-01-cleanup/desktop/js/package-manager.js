// Package Manager Component
// Handles package search, installation, and management

class PackageManager {
    constructor(apiUrl) {
        this.apiUrl = apiUrl;
        this.searchResults = [];
        this.installedPackages = [];
        this.isSearching = false;
    }

    async init() {
        console.log('📦 Initializing Package Manager...');
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Load installed packages
        await this.loadInstalledPackages();
        
        // Initialize smart suggestions
        this.initializeSuggestions();
        
        console.log('✨ Package Manager ready');
    }

    setupEventListeners() {
        const searchInput = document.getElementById('package-search');
        const searchBtn = document.getElementById('search-btn');
        
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.searchPackages();
                }
            });
            
            // Debounced auto-search
            let debounceTimer;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(debounceTimer);
                if (e.target.value.length > 2) {
                    debounceTimer = setTimeout(() => {
                        this.searchPackages();
                    }, 500);
                }
            });
        }
        
        if (searchBtn) {
            searchBtn.addEventListener('click', () => this.searchPackages());
        }
    }

    async searchPackages() {
        const searchInput = document.getElementById('package-search');
        if (!searchInput || this.isSearching) return;
        
        const query = searchInput.value.trim();
        if (!query) return;
        
        this.isSearching = true;
        this.updateSearchUI('searching');
        
        // Track search for smart suggestions
        if (window.smartSuggestions) {
            window.smartSuggestions.trackAction('search', { query });
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/api/packages/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });
            
            if (response.ok) {
                const results = await response.json();
                this.displaySearchResults(results);
                
                // Update suggestions based on results
                if (window.smartSuggestions) {
                    window.smartSuggestions.displaySuggestions();
                }
            } else {
                throw new Error('Search failed');
            }
        } catch (error) {
            console.error('Package search error:', error);
            this.updateSearchUI('error', 'Failed to search packages');
        } finally {
            this.isSearching = false;
        }
    }

    displaySearchResults(results) {
        const container = document.getElementById('search-results');
        if (!container) return;
        
        this.searchResults = results;
        
        if (results.length === 0) {
            container.innerHTML = '<p class="no-results">No packages found</p>';
            return;
        }
        
        container.innerHTML = `
            <h3>Search Results (${results.length})</h3>
            <div class="package-grid">
                ${results.map(pkg => this.renderPackageCard(pkg)).join('')}
            </div>
        `;
        
        // Add event listeners to package cards
        container.querySelectorAll('.install-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const packageName = e.target.dataset.package;
                this.installPackage(packageName);
            });
        });
    }

    renderPackageCard(pkg) {
        const isInstalled = this.installedPackages.some(p => p.name === pkg.name);
        
        return `
            <div class="package-card ${isInstalled ? 'installed' : ''}">
                <div class="package-header">
                    <h4 class="package-name">${pkg.name}</h4>
                    <span class="package-version">${pkg.version || 'latest'}</span>
                </div>
                <p class="package-description">${pkg.description || 'No description available'}</p>
                <div class="package-actions">
                    ${isInstalled ? 
                        '<span class="installed-badge">✓ Installed</span>' :
                        `<button class="sacred-btn install-btn" data-package="${pkg.name}">Install</button>`
                    }
                    <button class="sacred-btn secondary" onclick="window.nixosGUI.packageManager.showPackageDetails('${pkg.name}')">Details</button>
                </div>
            </div>
        `;
    }

    async installPackage(packageName) {
        console.log(`Installing package: ${packageName}`);
        
        // Sacred pause before installation
        window.sacredPause(async () => {
            try {
                // Update UI
                this.updatePackageUI(packageName, 'installing');
                
                const response = await fetch(`${this.apiUrl}/api/packages/install`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ package: packageName })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    
                    // Track installation for suggestions
                    if (window.smartSuggestions) {
                        window.smartSuggestions.trackAction('install', { package: packageName });
                    }
                    
                    // Update UI
                    this.updatePackageUI(packageName, 'installed');
                    window.updateStatus(`Successfully installed ${packageName}`);
                    
                    // Refresh installed packages list
                    await this.loadInstalledPackages();
                    
                    // Show related suggestions
                    if (window.smartSuggestions) {
                        window.smartSuggestions.displaySuggestions();
                    }
                } else {
                    throw new Error('Installation failed');
                }
            } catch (error) {
                console.error('Installation error:', error);
                this.updatePackageUI(packageName, 'error');
                window.updateStatus(`Failed to install ${packageName}`);
            }
        });
    }

    async loadInstalledPackages() {
        try {
            const response = await fetch(`${this.apiUrl}/api/packages/installed`);
            if (response.ok) {
                this.installedPackages = await response.json();
                this.displayInstalledPackages();
            }
        } catch (error) {
            console.error('Failed to load installed packages:', error);
        }
    }

    displayInstalledPackages() {
        const container = document.getElementById('installed-list');
        if (!container) return;
        
        if (this.installedPackages.length === 0) {
            container.innerHTML = '<p class="no-packages">No packages installed</p>';
            return;
        }
        
        container.innerHTML = this.installedPackages.map(pkg => `
            <div class="installed-package">
                <span class="package-name">${pkg.name}</span>
                <span class="package-version">${pkg.version}</span>
                <button class="remove-btn" onclick="window.nixosGUI.packageManager.removePackage('${pkg.name}')">Remove</button>
            </div>
        `).join('');
    }

    async removePackage(packageName) {
        if (!confirm(`Are you sure you want to remove ${packageName}?`)) return;
        
        try {
            const response = await fetch(`${this.apiUrl}/api/packages/remove`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ package: packageName })
            });
            
            if (response.ok) {
                window.updateStatus(`Successfully removed ${packageName}`);
                await this.loadInstalledPackages();
                
                // Re-run search to update UI
                if (this.searchResults.length > 0) {
                    this.displaySearchResults(this.searchResults);
                }
            } else {
                throw new Error('Removal failed');
            }
        } catch (error) {
            console.error('Package removal error:', error);
            window.updateStatus(`Failed to remove ${packageName}`);
        }
    }

    async showPackageDetails(packageName) {
        try {
            const response = await fetch(`${this.apiUrl}/api/packages/details/${packageName}`);
            if (response.ok) {
                const details = await response.json();
                this.displayPackageDetails(details);
            }
        } catch (error) {
            console.error('Failed to load package details:', error);
        }
    }

    displayPackageDetails(details) {
        // Create modal or expand card to show details
        const modal = document.createElement('div');
        modal.className = 'package-details-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>${details.name}</h3>
                <p>${details.description}</p>
                <div class="details-info">
                    <p><strong>Version:</strong> ${details.version}</p>
                    <p><strong>License:</strong> ${details.license || 'Unknown'}</p>
                    <p><strong>Homepage:</strong> <a href="${details.homepage}" target="_blank">${details.homepage}</a></p>
                </div>
                <button class="sacred-btn" onclick="this.closest('.package-details-modal').remove()">Close</button>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    updateSearchUI(state, message = '') {
        const container = document.getElementById('search-results');
        if (!container) return;
        
        switch (state) {
            case 'searching':
                container.innerHTML = '<div class="searching">🔍 Searching packages...</div>';
                break;
            case 'error':
                container.innerHTML = `<div class="error">${message}</div>`;
                break;
        }
    }

    updatePackageUI(packageName, state) {
        const button = document.querySelector(`[data-package="${packageName}"]`);
        if (!button) return;
        
        switch (state) {
            case 'installing':
                button.textContent = 'Installing...';
                button.disabled = true;
                break;
            case 'installed':
                button.parentElement.innerHTML = '<span class="installed-badge">✓ Installed</span>';
                break;
            case 'error':
                button.textContent = 'Failed';
                button.disabled = false;
                break;
        }
    }

    initializeSuggestions() {
        // Popular packages for quick access
        const popularPackages = ['git', 'vim', 'firefox', 'vscode', 'docker'];
        const container = document.getElementById('search-results');
        
        if (container && !this.searchResults.length) {
            container.innerHTML = `
                <h3>Popular Packages</h3>
                <div class="popular-packages">
                    ${popularPackages.map(pkg => `
                        <button class="package-chip" onclick="document.getElementById('package-search').value='${pkg}'; window.nixosGUI.packageManager.searchPackages()">
                            ${pkg}
                        </button>
                    `).join('')}
                </div>
            `;
        }
    }
}

// Add package manager styles
const pmStyle = document.createElement('style');
pmStyle.textContent = `
.package-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: var(--sacred-space-md);
    margin-top: var(--sacred-space-md);
}

.package-card {
    background: var(--sacred-bg);
    border: 1px solid var(--sacred-border);
    border-radius: 8px;
    padding: var(--sacred-space-md);
    transition: var(--sacred-transition);
}

.package-card:hover {
    border-color: var(--sacred-primary);
    box-shadow: 0 2px 8px rgba(74, 158, 255, 0.1);
}

.package-card.installed {
    border-color: var(--sacred-accent);
}

.package-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: var(--sacred-space-sm);
}

.package-name {
    color: var(--sacred-primary);
    margin: 0;
}

.package-version {
    color: var(--sacred-text-dim);
    font-size: 0.9em;
}

.package-description {
    color: var(--sacred-text-dim);
    font-size: 0.9em;
    margin: var(--sacred-space-sm) 0;
}

.package-actions {
    display: flex;
    gap: var(--sacred-space-sm);
    align-items: center;
}

.installed-badge {
    color: var(--sacred-accent);
    font-weight: 500;
}

.installed-package {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--sacred-space-sm);
    border-bottom: 1px solid var(--sacred-border);
}

.remove-btn {
    background: none;
    border: 1px solid var(--sacred-border);
    color: var(--sacred-text-dim);
    padding: 4px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85em;
}

.remove-btn:hover {
    border-color: #ff6b6b;
    color: #ff6b6b;
}

.popular-packages {
    display: flex;
    flex-wrap: wrap;
    gap: var(--sacred-space-sm);
    margin-top: var(--sacred-space-sm);
}

.package-chip {
    background: var(--sacred-bg-light);
    border: 1px solid var(--sacred-border);
    color: var(--sacred-text);
    padding: var(--sacred-space-xs) var(--sacred-space-md);
    border-radius: 20px;
    cursor: pointer;
    transition: var(--sacred-transition);
}

.package-chip:hover {
    border-color: var(--sacred-primary);
    color: var(--sacred-primary);
}

.package-details-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: var(--sacred-bg-light);
    border: 1px solid var(--sacred-border);
    border-radius: 12px;
    padding: var(--sacred-space-lg);
    max-width: 600px;
    width: 90%;
}

.searching {
    text-align: center;
    padding: var(--sacred-space-xl);
    color: var(--sacred-text-dim);
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% { opacity: 0.6; }
    50% { opacity: 1; }
    100% { opacity: 0.6; }
}
`;
document.head.appendChild(pmStyle);