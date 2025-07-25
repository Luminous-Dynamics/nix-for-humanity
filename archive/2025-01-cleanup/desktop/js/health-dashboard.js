// System Health Dashboard
// Real-time visualization of system metrics with consciousness-first design

class HealthDashboard {
    constructor(websocket) {
        this.websocket = websocket;
        this.charts = {};
        this.metrics = {
            cpu: { history: [], max: 100 },
            memory: { history: [], max: 100 },
            disk: { history: [], max: 100 },
            network: { history: [], max: 1000 } // KB/s
        };
        this.maxDataPoints = 60; // 5 minutes at 5-second intervals
        this.isInitialized = false;
    }

    async init() {
        console.log('🌟 Initializing Health Dashboard...');
        
        // Set up canvas contexts
        this.setupCharts();
        
        // Subscribe to system stats via WebSocket
        if (this.websocket) {
            this.websocket.on('system-stats', (data) => {
                this.updateStats(data);
            });
            this.websocket.subscribe('system-stats');
        }
        
        // Start with a manual fetch
        await this.fetchCurrentStats();
        
        this.isInitialized = true;
        console.log('✨ Health Dashboard ready');
    }

    setupCharts() {
        const chartTypes = ['cpu', 'memory', 'disk', 'network'];
        
        chartTypes.forEach(type => {
            const canvas = document.getElementById(`${type}-chart`);
            if (canvas) {
                const ctx = canvas.getContext('2d');
                this.charts[type] = {
                    canvas,
                    ctx,
                    width: canvas.width,
                    height: canvas.height
                };
                
                // Set canvas size
                canvas.width = 250;
                canvas.height = 100;
                
                // Initial draw
                this.drawChart(type);
            }
        });
    }

    async fetchCurrentStats() {
        try {
            const response = await fetch(`${window.nixosGUI.config.apiUrl}/api/system/stats`);
            if (response.ok) {
                const stats = await response.json();
                this.updateStats(stats);
            }
        } catch (error) {
            console.error('Failed to fetch system stats:', error);
        }
    }

    updateStats(stats) {
        // Update CPU
        if (stats.cpu) {
            this.updateMetric('cpu', stats.cpu.usage || 0);
            this.updateValue('cpu-value', `${Math.round(stats.cpu.usage || 0)}%`);
        }
        
        // Update Memory
        if (stats.memory) {
            const memoryPercent = (stats.memory.used / stats.memory.total) * 100;
            this.updateMetric('memory', memoryPercent);
            this.updateValue('memory-value', `${Math.round(memoryPercent)}%`);
        }
        
        // Update Disk
        if (stats.disk) {
            const diskPercent = (stats.disk.used / stats.disk.total) * 100;
            this.updateMetric('disk', diskPercent);
            this.updateValue('disk-value', `${Math.round(diskPercent)}%`);
        }
        
        // Update Network
        if (stats.network) {
            const networkKBps = (stats.network.rx + stats.network.tx) / 1024;
            this.updateMetric('network', networkKBps);
            this.updateValue('network-value', `${networkKBps.toFixed(1)} KB/s`);
        }
        
        // Update coherence based on system health
        this.updateSystemCoherence(stats);
    }

    updateMetric(type, value) {
        const metric = this.metrics[type];
        
        // Add new value
        metric.history.push({
            value: value,
            timestamp: Date.now()
        });
        
        // Keep only recent data points
        if (metric.history.length > this.maxDataPoints) {
            metric.history.shift();
        }
        
        // Redraw chart
        this.drawChart(type);
    }

    updateValue(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
            
            // Add visual feedback for high values
            const numericValue = parseFloat(value);
            if (numericValue > 80) {
                element.style.color = '#ff6b6b';
            } else if (numericValue > 60) {
                element.style.color = '#ffd93d';
            } else {
                element.style.color = '#6bcf7f';
            }
        }
    }

    drawChart(type) {
        const chart = this.charts[type];
        const metric = this.metrics[type];
        
        if (!chart || !chart.ctx) return;
        
        const ctx = chart.ctx;
        const width = chart.width;
        const height = chart.height;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Set styling
        ctx.strokeStyle = this.getChartColor(type);
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        
        // Draw grid
        this.drawGrid(ctx, width, height);
        
        // Draw data
        if (metric.history.length > 1) {
            ctx.beginPath();
            
            metric.history.forEach((point, index) => {
                const x = (index / (this.maxDataPoints - 1)) * width;
                const y = height - (point.value / metric.max) * height;
                
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            
            ctx.stroke();
            
            // Draw gradient fill
            const gradient = ctx.createLinearGradient(0, 0, 0, height);
            gradient.addColorStop(0, this.getChartColor(type) + '40');
            gradient.addColorStop(1, this.getChartColor(type) + '00');
            
            ctx.fillStyle = gradient;
            ctx.fill();
        }
    }

    drawGrid(ctx, width, height) {
        ctx.strokeStyle = '#233554';
        ctx.lineWidth = 0.5;
        
        // Horizontal lines
        for (let i = 0; i <= 4; i++) {
            const y = (i / 4) * height;
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(width, y);
            ctx.stroke();
        }
        
        // Vertical lines
        for (let i = 0; i <= 6; i++) {
            const x = (i / 6) * width;
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, height);
            ctx.stroke();
        }
    }

    getChartColor(type) {
        const colors = {
            cpu: '#4a9eff',
            memory: '#7c4dff',
            disk: '#00bfa5',
            network: '#ff6b6b'
        };
        return colors[type] || '#4a9eff';
    }

    updateSystemCoherence(stats) {
        // Calculate overall system health coherence
        let totalLoad = 0;
        let factors = 0;
        
        if (stats.cpu && stats.cpu.usage !== undefined) {
            totalLoad += stats.cpu.usage;
            factors++;
        }
        
        if (stats.memory && stats.memory.used && stats.memory.total) {
            totalLoad += (stats.memory.used / stats.memory.total) * 100;
            factors++;
        }
        
        if (stats.disk && stats.disk.used && stats.disk.total) {
            totalLoad += (stats.disk.used / stats.disk.total) * 100;
            factors++;
        }
        
        if (factors > 0) {
            const avgLoad = totalLoad / factors;
            const coherence = (1 - (avgLoad / 100)) * 0.5 + 0.5; // Scale to 0.5-1.0
            
            // Send coherence update
            if (window.nixosGUI) {
                window.nixosGUI.updateCoherence(coherence.toFixed(2));
            }
        }
    }

    // Get current system health summary
    getHealthSummary() {
        const summary = {
            status: 'healthy',
            issues: [],
            recommendations: []
        };
        
        // Check CPU
        const cpuLatest = this.metrics.cpu.history.slice(-1)[0];
        if (cpuLatest && cpuLatest.value > 80) {
            summary.status = 'warning';
            summary.issues.push('High CPU usage detected');
            summary.recommendations.push('Consider closing unused applications');
        }
        
        // Check Memory
        const memLatest = this.metrics.memory.history.slice(-1)[0];
        if (memLatest && memLatest.value > 85) {
            summary.status = 'warning';
            summary.issues.push('High memory usage detected');
            summary.recommendations.push('Consider upgrading RAM or closing memory-intensive applications');
        }
        
        // Check Disk
        const diskLatest = this.metrics.disk.history.slice(-1)[0];
        if (diskLatest && diskLatest.value > 90) {
            summary.status = 'critical';
            summary.issues.push('Low disk space');
            summary.recommendations.push('Clean up old generations with `nix-collect-garbage -d`');
        }
        
        return summary;
    }

    // Export metrics for analysis
    exportMetrics() {
        const exportData = {
            timestamp: new Date().toISOString(),
            metrics: this.metrics,
            summary: this.getHealthSummary()
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `system-health-${new Date().toISOString()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
}

// Helper function to create mini sparkline charts
window.createSparkline = function(canvasId, data, color = '#4a9eff') {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width || 100;
    const height = canvas.height || 30;
    
    ctx.clearRect(0, 0, width, height);
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.5;
    
    if (data.length > 1) {
        ctx.beginPath();
        data.forEach((value, index) => {
            const x = (index / (data.length - 1)) * width;
            const y = height - (value / 100) * height;
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        ctx.stroke();
    }
};