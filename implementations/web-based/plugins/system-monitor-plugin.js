/**
 * System Monitor Plugin
 * Adds enhanced system monitoring capabilities
 */

const plugin = {
    id: 'system-monitor',
    name: 'System Monitor',
    version: '1.0.0',
    author: 'NixOS GUI Team',
    description: 'Enhanced system monitoring with real-time metrics and alerts',
    permissions: ['ui', 'storage', 'notifications', 'events'],
    
    metrics: {
        cpu: { current: 0, history: [] },
        memory: { current: 0, history: [] },
        disk: { current: 0, history: [] },
        network: { rx: 0, tx: 0, history: [] }
    },
    
    updateInterval: null,
    chartElements: {},
    
    async init(api) {
        console.log('System Monitor plugin initializing...');
        
        this.api = api;
        
        // Load saved preferences
        this.loadPreferences();
        
        // Add monitoring widgets
        this.addMonitoringWidgets();
        
        // Add toolbar button
        this.addToolbarButton();
        
        // Start monitoring
        this.startMonitoring();
        
        // Set up alerts
        this.setupAlerts();
    },
    
    loadPreferences() {
        const prefs = this.api.storage.get('monitor-preferences');
        if (prefs) {
            this.preferences = JSON.parse(prefs);
        } else {
            this.preferences = {
                updateInterval: 5000,
                showCpu: true,
                showMemory: true,
                showDisk: true,
                showNetwork: true,
                cpuAlert: 80,
                memoryAlert: 90,
                diskAlert: 95
            };
        }
    },
    
    addMonitoringWidgets() {
        // CPU Monitor Widget
        if (this.preferences.showCpu) {
            this.api.ui.addDashboardWidget({
                id: 'cpu-monitor',
                title: 'CPU Usage',
                content: `
                    <div class="monitor-widget">
                        <div class="metric-display">
                            <span class="metric-value" id="cpu-value">0</span>
                            <span class="metric-unit">%</span>
                        </div>
                        <canvas id="cpu-chart" width="300" height="100"></canvas>
                        <div class="metric-details" id="cpu-details">
                            <span>Cores: Loading...</span>
                        </div>
                    </div>
                `,
                render: (container) => {
                    this.chartElements.cpu = container.querySelector('#cpu-chart');
                    this.initChart('cpu');
                }
            });
        }
        
        // Memory Monitor Widget
        if (this.preferences.showMemory) {
            this.api.ui.addDashboardWidget({
                id: 'memory-monitor',
                title: 'Memory Usage',
                content: `
                    <div class="monitor-widget">
                        <div class="metric-display">
                            <span class="metric-value" id="memory-value">0</span>
                            <span class="metric-unit">%</span>
                        </div>
                        <canvas id="memory-chart" width="300" height="100"></canvas>
                        <div class="metric-details" id="memory-details">
                            <span>Total: Loading...</span>
                        </div>
                    </div>
                `,
                render: (container) => {
                    this.chartElements.memory = container.querySelector('#memory-chart');
                    this.initChart('memory');
                }
            });
        }
        
        // Disk Usage Widget
        if (this.preferences.showDisk) {
            this.api.ui.addDashboardWidget({
                id: 'disk-monitor',
                title: 'Disk Usage',
                content: `
                    <div class="monitor-widget">
                        <div class="disk-usage-bars" id="disk-bars">
                            Loading disk information...
                        </div>
                    </div>
                `
            });
        }
        
        // Network Monitor Widget
        if (this.preferences.showNetwork) {
            this.api.ui.addDashboardWidget({
                id: 'network-monitor',
                title: 'Network Activity',
                content: `
                    <div class="monitor-widget">
                        <div class="network-stats">
                            <div class="network-stat">
                                <i class="icon-arrow-down"></i>
                                <span id="network-rx">0 B/s</span>
                            </div>
                            <div class="network-stat">
                                <i class="icon-arrow-up"></i>
                                <span id="network-tx">0 B/s</span>
                            </div>
                        </div>
                        <canvas id="network-chart" width="300" height="100"></canvas>
                    </div>
                `,
                render: (container) => {
                    this.chartElements.network = container.querySelector('#network-chart');
                    this.initChart('network');
                }
            });
        }
        
        // Add custom styles
        this.addStyles();
    },
    
    addToolbarButton() {
        this.api.ui.addToolbarButton({
            id: 'system-monitor-button',
            icon: 'icon-activity',
            tooltip: 'System Monitor',
            action: () => this.showDetailedMonitor()
        });
    },
    
    startMonitoring() {
        // Initial update
        this.updateMetrics();
        
        // Set up interval
        this.updateInterval = setInterval(() => {
            this.updateMetrics();
        }, this.preferences.updateInterval);
    },
    
    async updateMetrics() {
        try {
            // Fetch system metrics (would be real API call)
            const response = await fetch('/api/system/metrics');
            const data = await response.json();
            
            // Update CPU
            this.metrics.cpu.current = data.cpu.usage;
            this.metrics.cpu.history.push(data.cpu.usage);
            if (this.metrics.cpu.history.length > 60) {
                this.metrics.cpu.history.shift();
            }
            this.updateDisplay('cpu', data.cpu);
            
            // Update Memory
            this.metrics.memory.current = data.memory.percentage;
            this.metrics.memory.history.push(data.memory.percentage);
            if (this.metrics.memory.history.length > 60) {
                this.metrics.memory.history.shift();
            }
            this.updateDisplay('memory', data.memory);
            
            // Update Disk
            this.updateDiskDisplay(data.disk);
            
            // Update Network
            this.metrics.network.rx = data.network.rx_rate;
            this.metrics.network.tx = data.network.tx_rate;
            this.metrics.network.history.push({
                rx: data.network.rx_rate,
                tx: data.network.tx_rate
            });
            if (this.metrics.network.history.length > 60) {
                this.metrics.network.history.shift();
            }
            this.updateNetworkDisplay(data.network);
            
            // Check alerts
            this.checkAlerts();
            
        } catch (error) {
            console.error('Failed to update metrics:', error);
        }
    },
    
    updateDisplay(metric, data) {
        const valueElement = document.getElementById(`${metric}-value`);
        const detailsElement = document.getElementById(`${metric}-details`);
        
        if (valueElement) {
            valueElement.textContent = Math.round(this.metrics[metric].current);
            
            // Update color based on usage
            const value = this.metrics[metric].current;
            if (value > 80) {
                valueElement.style.color = '#f44336';
            } else if (value > 60) {
                valueElement.style.color = '#ff9800';
            } else {
                valueElement.style.color = '#4caf50';
            }
        }
        
        if (detailsElement) {
            if (metric === 'cpu') {
                detailsElement.innerHTML = `
                    <span>Cores: ${data.cores}</span>
                    <span>Load: ${data.loadAverage.join(', ')}</span>
                `;
            } else if (metric === 'memory') {
                detailsElement.innerHTML = `
                    <span>Total: ${this.formatBytes(data.total)}</span>
                    <span>Used: ${this.formatBytes(data.used)}</span>
                `;
            }
        }
        
        // Update chart
        this.updateChart(metric);
    },
    
    updateDiskDisplay(diskData) {
        const container = document.getElementById('disk-bars');
        if (!container) return;
        
        container.innerHTML = diskData.map(disk => `
            <div class="disk-item">
                <div class="disk-label">
                    <span>${disk.mount}</span>
                    <span>${this.formatBytes(disk.used)} / ${this.formatBytes(disk.total)}</span>
                </div>
                <div class="disk-bar">
                    <div class="disk-bar-fill" style="width: ${disk.percentage}%; background: ${
                        disk.percentage > 90 ? '#f44336' : 
                        disk.percentage > 70 ? '#ff9800' : '#4caf50'
                    }"></div>
                </div>
            </div>
        `).join('');
    },
    
    updateNetworkDisplay(networkData) {
        const rxElement = document.getElementById('network-rx');
        const txElement = document.getElementById('network-tx');
        
        if (rxElement) {
            rxElement.textContent = this.formatBytes(networkData.rx_rate) + '/s';
        }
        if (txElement) {
            txElement.textContent = this.formatBytes(networkData.tx_rate) + '/s';
        }
        
        this.updateChart('network');
    },
    
    initChart(type) {
        const canvas = this.chartElements[type];
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        ctx.strokeStyle = '#4a9eff';
        ctx.lineWidth = 2;
    },
    
    updateChart(type) {
        const canvas = this.chartElements[type];
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Draw grid
        ctx.strokeStyle = '#333';
        ctx.lineWidth = 1;
        ctx.beginPath();
        for (let i = 0; i < 5; i++) {
            const y = (height / 4) * i;
            ctx.moveTo(0, y);
            ctx.lineTo(width, y);
        }
        ctx.stroke();
        
        // Draw data
        const data = type === 'network' ? 
            this.metrics.network.history.map(h => (h.rx + h.tx) / 2) :
            this.metrics[type].history;
            
        if (data.length > 1) {
            ctx.strokeStyle = '#4a9eff';
            ctx.lineWidth = 2;
            ctx.beginPath();
            
            const stepX = width / (data.length - 1);
            data.forEach((value, index) => {
                const x = index * stepX;
                const y = height - (value / 100) * height;
                
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            
            ctx.stroke();
        }
    },
    
    setupAlerts() {
        this.api.events.on('metrics-updated', () => {
            this.checkAlerts();
        });
    },
    
    checkAlerts() {
        // CPU Alert
        if (this.metrics.cpu.current > this.preferences.cpuAlert) {
            this.api.notifications.show(
                `High CPU usage: ${Math.round(this.metrics.cpu.current)}%`,
                'warning'
            );
        }
        
        // Memory Alert
        if (this.metrics.memory.current > this.preferences.memoryAlert) {
            this.api.notifications.show(
                `High memory usage: ${Math.round(this.metrics.memory.current)}%`,
                'warning'
            );
        }
    },
    
    showDetailedMonitor() {
        // This would open a detailed monitoring view
        this.api.ui.showModal({
            title: 'System Monitor',
            content: `
                <div class="detailed-monitor">
                    <h3>Detailed system metrics coming soon...</h3>
                    <p>This would show comprehensive system monitoring data.</p>
                </div>
            `,
            buttons: [
                {
                    label: 'Close',
                    action: 'close'
                }
            ]
        });
    },
    
    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .monitor-widget {
                padding: 16px;
            }
            .metric-display {
                text-align: center;
                margin-bottom: 16px;
            }
            .metric-value {
                font-size: 36px;
                font-weight: bold;
                transition: color 0.3s;
            }
            .metric-unit {
                font-size: 18px;
                color: var(--text-secondary);
            }
            .metric-details {
                display: flex;
                justify-content: space-between;
                font-size: 13px;
                color: var(--text-secondary);
                margin-top: 12px;
            }
            .disk-item {
                margin-bottom: 12px;
            }
            .disk-label {
                display: flex;
                justify-content: space-between;
                font-size: 13px;
                margin-bottom: 4px;
            }
            .disk-bar {
                height: 8px;
                background: var(--bg-tertiary);
                border-radius: 4px;
                overflow: hidden;
            }
            .disk-bar-fill {
                height: 100%;
                transition: width 0.3s;
            }
            .network-stats {
                display: flex;
                justify-content: space-around;
                margin-bottom: 16px;
            }
            .network-stat {
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 16px;
            }
            .network-stat i {
                color: var(--primary-color);
            }
        `;
        document.head.appendChild(style);
        this.styleElement = style;
    },
    
    hooks: {
        afterSystemRebuild: async () => {
            // Reset metrics after system rebuild
            this.metrics = {
                cpu: { current: 0, history: [] },
                memory: { current: 0, history: [] },
                disk: { current: 0, history: [] },
                network: { rx: 0, tx: 0, history: [] }
            };
        }
    },
    
    cleanup() {
        console.log('System Monitor plugin cleaning up...');
        
        // Stop monitoring
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        // Remove styles
        if (this.styleElement) {
            this.styleElement.remove();
        }
        
        // Save preferences
        this.api.storage.set('monitor-preferences', JSON.stringify(this.preferences));
    }
};