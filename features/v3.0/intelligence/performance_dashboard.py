#!/usr/bin/env python3
"""
from typing import Dict
Performance Monitoring Dashboard for Nix for Humanity
Real-time visualization of backend performance metrics
"""

from flask import Flask, render_template_string, jsonify
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import time
from typing import Dict, Any, List

app = Flask(__name__)

# HTML template for the dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Nix for Humanity - Performance Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .metric-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }
        .metric-label {
            color: #666;
            margin-bottom: 10px;
        }
        .chart-container {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .status-good { color: #10b981; }
        .status-warning { color: #f59e0b; }
        .status-bad { color: #ef4444; }
        .refresh-info {
            text-align: right;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Nix for Humanity - Performance Dashboard</h1>
        <p>Real-time monitoring of enhanced backend performance</p>
    </div>
    
    <div class="refresh-info">
        Auto-refreshes every 5 seconds | Last update: <span id="last-update">-</span>
    </div>
    
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-label">Average Response Time</div>
            <div class="metric-value" id="avg-response">-</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-label">Operations/Hour</div>
            <div class="metric-value" id="ops-per-hour">-</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-label">Cache Hit Rate</div>
            <div class="metric-value" id="cache-hit-rate">-</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-label">Success Rate</div>
            <div class="metric-value" id="success-rate">-</div>
        </div>
    </div>
    
    <div class="chart-container">
        <h3>Response Time Trend (Last Hour)</h3>
        <canvas id="responseTimeChart"></canvas>
    </div>
    
    <div class="chart-container">
        <h3>Operation Types Distribution</h3>
        <canvas id="operationTypesChart"></canvas>
    </div>
    
    <div class="chart-container">
        <h3>Performance by Operation</h3>
        <canvas id="performanceByOpChart"></canvas>
    </div>

    <script>
        // Initialize charts
        const responseTimeCtx = document.getElementById('responseTimeChart').getContext('2d');
        const responseTimeChart = new Chart(responseTimeCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Response Time (ms)',
                    data: [],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Response Time (ms)'
                        }
                    }
                }
            }
        });
        
        const operationTypesCtx = document.getElementById('operationTypesChart').getContext('2d');
        const operationTypesChart = new Chart(operationTypesCtx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#667eea',
                        '#764ba2',
                        '#f093fb',
                        '#4facfe',
                        '#00f2fe',
                        '#43e97b'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
        
        const performanceByOpCtx = document.getElementById('performanceByOpChart').getContext('2d');
        const performanceByOpChart = new Chart(performanceByOpCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Average Time (ms)',
                    data: [],
                    backgroundColor: '#667eea'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Average Time (ms)'
                        }
                    }
                }
            }
        });
        
        // Update function
        async function updateDashboard() {
            try {
                const response = await fetch('/api/metrics');
                const data = await response.json();
                
                // Update metric cards
                document.getElementById('avg-response').textContent = 
                    data.avg_response_time ? `${data.avg_response_time.toFixed(2)}ms` : '-';
                    
                document.getElementById('ops-per-hour').textContent = 
                    data.operations_per_hour || '-';
                    
                document.getElementById('cache-hit-rate').textContent = 
                    data.cache_hit_rate ? `${(data.cache_hit_rate * 100).toFixed(1)}%` : '-';
                    
                document.getElementById('success-rate').textContent = 
                    data.success_rate ? `${(data.success_rate * 100).toFixed(1)}%` : '-';
                
                // Color code success rate
                const successRate = data.success_rate || 0;
                const successElement = document.getElementById('success-rate');
                successElement.className = 'metric-value ' + 
                    (successRate >= 0.95 ? 'status-good' : 
                     successRate >= 0.90 ? 'status-warning' : 'status-bad');
                
                // Update response time chart
                if (data.response_time_history) {
                    responseTimeChart.data.labels = data.response_time_history.labels;
                    responseTimeChart.data.datasets[0].data = data.response_time_history.values;
                    responseTimeChart.update();
                }
                
                // Update operation types chart
                if (data.operation_distribution) {
                    operationTypesChart.data.labels = Object.keys(data.operation_distribution);
                    operationTypesChart.data.datasets[0].data = Object.values(data.operation_distribution);
                    operationTypesChart.update();
                }
                
                // Update performance by operation chart
                if (data.performance_by_operation) {
                    performanceByOpChart.data.labels = Object.keys(data.performance_by_operation);
                    performanceByOpChart.data.datasets[0].data = Object.values(data.performance_by_operation);
                    performanceByOpChart.update();
                }
                
                // Update timestamp
                document.getElementById('last-update').textContent = 
                    new Date().toLocaleTimeString();
                    
            } catch (error) {
                console.error('Error updating dashboard:', error);
            }
        }
        
        // Initial update and set interval
        updateDashboard();
        setInterval(updateDashboard, 5000);
    </script>
</body>
</html>
"""


class MetricsDashboard:
    """Collect and serve performance metrics"""
    
    def __init__(self):
        self.db_path = Path.home() / '.nix-humanity' / 'metrics.db'
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics from the database"""
        metrics = {}
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                # Average response time (last hour)
                cursor = conn.execute("""
                    SELECT AVG(value) 
                    FROM metrics 
                    WHERE name LIKE 'operation.%.duration'
                    AND timestamp > ?
                """, (time.time() - 3600,))
                
                avg_response = cursor.fetchone()[0]
                metrics['avg_response_time'] = avg_response * 1000 if avg_response else 0
                
                # Operations per hour
                cursor = conn.execute("""
                    SELECT COUNT(*) 
                    FROM metrics 
                    WHERE name LIKE 'operation.%'
                    AND timestamp > ?
                """, (time.time() - 3600,))
                
                metrics['operations_per_hour'] = cursor.fetchone()[0]
                
                # Cache hit rate
                cursor = conn.execute("""
                    SELECT 
                        SUM(CASE WHEN name LIKE '%.hit' THEN value ELSE 0 END) as hits,
                        SUM(CASE WHEN name LIKE '%.miss' THEN value ELSE 0 END) as misses
                    FROM metrics 
                    WHERE name LIKE 'cache.%'
                    AND timestamp > ?
                """, (time.time() - 3600,))
                
                row = cursor.fetchone()
                hits, misses = row[0] or 0, row[1] or 0
                total = hits + misses
                metrics['cache_hit_rate'] = hits / total if total > 0 else 0
                
                # Success rate
                cursor = conn.execute("""
                    SELECT 
                        SUM(CASE WHEN name LIKE '%.success' THEN value ELSE 0 END) as success,
                        SUM(CASE WHEN name LIKE '%.failure' THEN value ELSE 0 END) as failure
                    FROM metrics 
                    WHERE name LIKE 'operation.%'
                    AND timestamp > ?
                """, (time.time() - 3600,))
                
                row = cursor.fetchone()
                success, failure = row[0] or 0, row[1] or 0
                total = success + failure
                metrics['success_rate'] = success / total if total > 0 else 1.0
                
                # Response time history (last hour, 5-minute buckets)
                history_labels = []
                history_values = []
                
                for i in range(12):  # 12 x 5-minute buckets
                    bucket_start = time.time() - (i + 1) * 300
                    bucket_end = time.time() - i * 300
                    
                    cursor = conn.execute("""
                        SELECT AVG(value) 
                        FROM metrics 
                        WHERE name LIKE 'operation.%.duration'
                        AND timestamp > ? AND timestamp <= ?
                    """, (bucket_start, bucket_end))
                    
                    avg_val = cursor.fetchone()[0]
                    if avg_val:
                        history_labels.insert(0, f"-{(i+1)*5}min")
                        history_values.insert(0, avg_val * 1000)
                        
                metrics['response_time_history'] = {
                    'labels': history_labels,
                    'values': history_values
                }
                
                # Operation type distribution
                cursor = conn.execute("""
                    SELECT 
                        SUBSTR(name, 11, INSTR(SUBSTR(name, 11), '.') - 1) as operation,
                        COUNT(*) as count
                    FROM metrics 
                    WHERE name LIKE 'operation.%.duration'
                    AND timestamp > ?
                    GROUP BY operation
                """, (time.time() - 3600,))
                
                operation_dist = {}
                for row in cursor:
                    if row[0]:  # Filter out empty operations
                        operation_dist[row[0]] = row[1]
                        
                metrics['operation_distribution'] = operation_dist
                
                # Performance by operation type
                cursor = conn.execute("""
                    SELECT 
                        SUBSTR(name, 11, INSTR(SUBSTR(name, 11), '.') - 1) as operation,
                        AVG(value) * 1000 as avg_time
                    FROM metrics 
                    WHERE name LIKE 'operation.%.duration'
                    AND timestamp > ?
                    GROUP BY operation
                """, (time.time() - 3600,))
                
                perf_by_op = {}
                for row in cursor:
                    if row[0]:  # Filter out empty operations
                        perf_by_op[row[0]] = round(row[1], 2)
                        
                metrics['performance_by_operation'] = perf_by_op
                
        except Exception as e:
            print(f"Error reading metrics: {e}")
            
        return metrics


# Initialize dashboard
dashboard = MetricsDashboard()


@app.route('/')
def index():
    """Serve the dashboard HTML"""
    return render_template_string(DASHBOARD_TEMPLATE)


@app.route('/api/metrics')
def api_metrics():
    """API endpoint for metrics data"""
    return jsonify(dashboard.get_metrics())


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


if __name__ == '__main__':
    print("🚀 Starting Nix for Humanity Performance Dashboard")
    print("📊 Access at: http://localhost:9090")
    print("Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=9090, debug=False)