import { invoke } from '@tauri-apps/api/tauri'
import { appWindow } from '@tauri-apps/api/window'
import './styles/main.css'

// Sacred initialization
async function initializeSacredSpace() {
    console.log('🌟 Initializing consciousness-first environment...')
    
    try {
        // Set initial intention
        const intention = await invoke('set_intention', {
            text: 'Mindful system management',
            durationMinutes: 60
        })
        console.log('✨ Intention set:', intention)
        
        // Get initial coherence level
        const coherence = await invoke('get_coherence_level')
        console.log('🧘 Coherence level:', coherence)
        
        // Initialize the UI
        await initializeUI()
    } catch (error) {
        console.error('Failed to initialize sacred space:', error)
    }
}

async function initializeUI() {
    const app = document.getElementById('app')
    
    app.innerHTML = `
        <div class="consciousness-container">
            <header class="sacred-header">
                <h1>NixOS Sacred Configuration</h1>
                <div class="coherence-indicator" id="coherence">
                    <span class="coherence-label">Field Coherence:</span>
                    <span class="coherence-value">0.786</span>
                </div>
            </header>
            
            <nav class="sacred-nav">
                <button class="nav-item active" data-view="dashboard">
                    <span class="icon">🏠</span>
                    Dashboard
                </button>
                <button class="nav-item" data-view="configuration">
                    <span class="icon">⚙️</span>
                    Configuration
                </button>
                <button class="nav-item" data-view="packages">
                    <span class="icon">📦</span>
                    Packages
                </button>
                <button class="nav-item" data-view="services">
                    <span class="icon">🔧</span>
                    Services
                </button>
                <button class="nav-item" data-view="sacred">
                    <span class="icon">🧘</span>
                    Sacred Space
                </button>
            </nav>
            
            <main class="content-area" id="content">
                <!-- Dynamic content will be loaded here -->
            </main>
            
            <footer class="sacred-footer">
                <div class="sacred-pause-reminder">
                    Next sacred pause in <span id="pause-timer">25:00</span>
                </div>
                <div class="system-status">
                    <span id="status">✨ System harmonized</span>
                </div>
            </footer>
        </div>
    `
    
    // Set up navigation
    setupNavigation()
    
    // Load initial view
    await loadView('dashboard')
    
    // Start sacred timers
    startSacredTimers()
}

function setupNavigation() {
    const navButtons = document.querySelectorAll('.nav-item')
    
    navButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            // Update active state
            navButtons.forEach(b => b.classList.remove('active'))
            button.classList.add('active')
            
            // Load the view
            const view = button.dataset.view
            await loadView(view)
        })
    })
}

async function loadView(viewName) {
    const content = document.getElementById('content')
    
    // Show loading state
    content.innerHTML = `
        <div class="loading">
            <div class="loader-small"></div>
            <span>Loading ${viewName}...</span>
        </div>
    `
    
    try {
        switch (viewName) {
            case 'dashboard':
                await loadDashboard()
                break
            case 'configuration':
                await loadConfiguration()
                break
            case 'packages':
                await loadPackages()
                break
            case 'services':
                await loadServices()
                break
            case 'sacred':
                await loadSacredSpace()
                break
        }
    } catch (error) {
        content.innerHTML = `
            <div class="error">
                <h2>Error loading ${viewName}</h2>
                <p>${error.message}</p>
            </div>
        `
    }
}

async function loadDashboard() {
    const systemInfo = await invoke('get_system_info')
    const content = document.getElementById('content')
    
    content.innerHTML = `
        <div class="dashboard">
            <h2>System Overview</h2>
            
            <div class="info-grid">
                <div class="info-card">
                    <h3>System</h3>
                    <p>Hostname: ${systemInfo.hostname}</p>
                    <p>NixOS: ${systemInfo.nixos_version}</p>
                    <p>Kernel: ${systemInfo.kernel_version}</p>
                </div>
                
                <div class="info-card">
                    <h3>Resources</h3>
                    <p>CPU Usage: ${systemInfo.cpu_usage.toFixed(1)}%</p>
                    <p>Memory: ${(systemInfo.used_memory / 1024 / 1024 / 1024).toFixed(1)} / ${(systemInfo.total_memory / 1024 / 1024 / 1024).toFixed(1)} GB</p>
                    <p>Uptime: ${formatUptime(systemInfo.uptime)}</p>
                </div>
                
                <div class="info-card">
                    <h3>Consciousness</h3>
                    <p>Coherence: 0.786</p>
                    <p>Flow State: Active</p>
                    <p>Sacred Pauses: 3 today</p>
                </div>
            </div>
            
            <div class="quick-actions">
                <h3>Quick Actions</h3>
                <button class="action-btn" onclick="rebuildSystem()">
                    🔄 Rebuild System
                </button>
                <button class="action-btn" onclick="updateChannel()">
                    📡 Update Channel
                </button>
                <button class="action-btn" onclick="garbageCollect()">
                    🗑️ Garbage Collect
                </button>
            </div>
        </div>
    `
}

async function loadConfiguration() {
    const config = await invoke('read_nixos_config')
    const content = document.getElementById('content')
    
    content.innerHTML = `
        <div class="configuration">
            <h2>NixOS Configuration</h2>
            
            <div class="config-info">
                <p>📍 Path: ${config.path}</p>
                <p>📄 Type: ${config.is_flake ? 'Flake' : 'Traditional'}</p>
            </div>
            
            <div class="editor-container">
                <div class="editor-toolbar">
                    <button onclick="validateConfig()">✓ Validate</button>
                    <button onclick="saveConfig()">💾 Save</button>
                    <button onclick="reloadConfig()">🔄 Reload</button>
                </div>
                <textarea id="config-editor" class="config-editor">${config.content}</textarea>
            </div>
        </div>
    `
}

async function loadPackages() {
    const content = document.getElementById('content')
    
    content.innerHTML = `
        <div class="packages">
            <h2>Package Management</h2>
            
            <div class="search-container">
                <input 
                    type="text" 
                    id="package-search" 
                    class="search-input" 
                    placeholder="Search packages..."
                    onkeyup="searchPackages(event)"
                >
                <button onclick="searchPackages()">🔍 Search</button>
            </div>
            
            <div id="search-results" class="search-results">
                <!-- Results will appear here -->
            </div>
            
            <div class="installed-packages">
                <h3>Installed Packages</h3>
                <div id="installed-list" class="package-list">
                    Loading installed packages...
                </div>
            </div>
        </div>
    `
    
    // Load installed packages
    loadInstalledPackages()
}

async function loadServices() {
    const services = await invoke('list_services')
    const content = document.getElementById('content')
    
    const serviceCards = services.map(service => `
        <div class="service-card ${service.active ? 'active' : 'inactive'}">
            <div class="service-header">
                <h4>${service.name}</h4>
                <span class="service-status">${service.active ? '🟢 Active' : '🔴 Inactive'}</span>
            </div>
            <div class="service-controls">
                <button onclick="toggleService('${service.name}', ${!service.active})">
                    ${service.active ? 'Stop' : 'Start'}
                </button>
                <button onclick="restartService('${service.name}')">Restart</button>
            </div>
        </div>
    `).join('')
    
    content.innerHTML = `
        <div class="services">
            <h2>System Services</h2>
            <div class="services-grid">
                ${serviceCards}
            </div>
        </div>
    `
}

async function loadSacredSpace() {
    const coherence = await invoke('get_coherence_level')
    const content = document.getElementById('content')
    
    content.innerHTML = `
        <div class="sacred-space">
            <h2>Sacred Development Space</h2>
            
            <div class="coherence-display">
                <div class="coherence-circle">
                    <svg viewBox="0 0 200 200">
                        <circle cx="100" cy="100" r="90" fill="none" stroke="#333" stroke-width="2"/>
                        <circle 
                            cx="100" cy="100" r="90" 
                            fill="none" 
                            stroke="#00ff88" 
                            stroke-width="4"
                            stroke-dasharray="${coherence.value * 565.5} 565.5"
                            transform="rotate(-90 100 100)"
                        />
                    </svg>
                    <div class="coherence-text">${(coherence.value * 100).toFixed(0)}%</div>
                </div>
                <p>Field Coherence Level</p>
            </div>
            
            <div class="sacred-controls">
                <button class="sacred-btn" onclick="setSacredIntention()">
                    🎯 Set Intention
                </button>
                <button class="sacred-btn" onclick="takeSacredPause()">
                    🧘 Sacred Pause
                </button>
                <button class="sacred-btn" onclick="viewFieldHistory()">
                    📊 Field History
                </button>
            </div>
            
            <div class="wisdom-quote">
                <p>"The machine is not separate from the sacred. The digital is not separate from the divine."</p>
            </div>
        </div>
    `
}

// Helper functions
function formatUptime(seconds) {
    const days = Math.floor(seconds / 86400)
    const hours = Math.floor((seconds % 86400) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    
    if (days > 0) {
        return `${days}d ${hours}h ${minutes}m`
    } else if (hours > 0) {
        return `${hours}h ${minutes}m`
    } else {
        return `${minutes}m`
    }
}

function startSacredTimers() {
    // Sacred pause countdown
    let pauseTime = 25 * 60 // 25 minutes in seconds
    
    setInterval(() => {
        pauseTime--
        if (pauseTime <= 0) {
            // Trigger sacred pause notification
            invoke('trigger_sacred_pause')
            pauseTime = 25 * 60 // Reset
        }
        
        const minutes = Math.floor(pauseTime / 60)
        const seconds = pauseTime % 60
        document.getElementById('pause-timer').textContent = 
            `${minutes}:${seconds.toString().padStart(2, '0')}`
    }, 1000)
}

// Global functions for onclick handlers
window.rebuildSystem = async () => {
    if (confirm('This will rebuild your NixOS configuration. Continue?')) {
        try {
            await invoke('rebuild_nixos_config')
            alert('System rebuild initiated!')
        } catch (error) {
            alert(`Rebuild failed: ${error}`)
        }
    }
}

window.searchPackages = async (event) => {
    if (event && event.key !== 'Enter') return
    
    const query = document.getElementById('package-search').value
    if (!query) return
    
    const results = await invoke('search_packages', { query, limit: 20 })
    const resultsDiv = document.getElementById('search-results')
    
    resultsDiv.innerHTML = results.packages.map(pkg => `
        <div class="package-result">
            <h4>${pkg.name}</h4>
            <p>${pkg.description || 'No description available'}</p>
            <button onclick="installPackage('${pkg.attribute}')">Install</button>
        </div>
    `).join('')
}

window.installPackage = async (attribute) => {
    if (confirm(`Install package: ${attribute}?`)) {
        try {
            await invoke('install_package', { attribute })
            alert('Package installed successfully!')
        } catch (error) {
            alert(`Installation failed: ${error}`)
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initializeSacredSpace)