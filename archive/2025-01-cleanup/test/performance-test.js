#!/usr/bin/env node

// Performance and Load Testing for NixOS GUI
// Tests system under various load conditions

const https = require('https');
const WebSocket = require('ws');
const { performance } = require('perf_hooks');

// Ignore self-signed certificates for testing
process.env["NODE_TLS_REJECT_UNAUTHORIZED"] = 0;

// Test configuration
const config = {
    baseUrl: 'https://localhost:8443',
    wsUrl: 'wss://localhost:8443',
    testDuration: 30000, // 30 seconds
    concurrentUsers: 10,
    requestsPerSecond: 5,
    username: 'admin',
    password: 'testpass'
};

// Test results
const results = {
    requests: [],
    errors: [],
    websockets: [],
    startTime: null,
    endTime: null
};

// Colors for output
const colors = {
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    reset: '\x1b[0m'
};

// Helper functions
function log(message, color = 'reset') {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

function makeRequest(path, options = {}) {
    return new Promise((resolve, reject) => {
        const startTime = performance.now();
        
        const url = new URL(path, config.baseUrl);
        const reqOptions = {
            method: options.method || 'GET',
            headers: options.headers || {},
            rejectUnauthorized: false
        };
        
        const req = https.request(url, reqOptions, (res) => {
            let data = '';
            
            res.on('data', chunk => {
                data += chunk;
            });
            
            res.on('end', () => {
                const endTime = performance.now();
                const duration = endTime - startTime;
                
                results.requests.push({
                    path,
                    method: reqOptions.method,
                    status: res.statusCode,
                    duration,
                    timestamp: new Date()
                });
                
                resolve({
                    status: res.statusCode,
                    data,
                    duration,
                    headers: res.headers
                });
            });
        });
        
        req.on('error', (error) => {
            results.errors.push({
                path,
                error: error.message,
                timestamp: new Date()
            });
            reject(error);
        });
        
        if (options.body) {
            req.write(options.body);
        }
        
        req.end();
    });
}

// Get authentication token
async function authenticate() {
    log('🔐 Authenticating...', 'blue');
    
    try {
        const response = await makeRequest('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: config.username,
                password: config.password
            })
        });
        
        if (response.status === 200) {
            const data = JSON.parse(response.data);
            log('✅ Authentication successful', 'green');
            return data.token;
        } else {
            throw new Error(`Authentication failed: ${response.status}`);
        }
    } catch (error) {
        log(`❌ Authentication error: ${error.message}`, 'red');
        return null;
    }
}

// Test API endpoints
async function testAPIPerformance(token) {
    log('\n📊 Testing API Performance...', 'blue');
    
    const endpoints = [
        { path: '/api/health', method: 'GET' },
        { path: '/api/packages/search', method: 'POST', body: { query: 'test' } },
        { path: '/api/system/stats', method: 'GET' },
        { path: '/api/services', method: 'GET' },
        { path: '/api/configuration', method: 'GET' }
    ];
    
    const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
    
    // Warm-up requests
    log('Warming up...', 'yellow');
    for (const endpoint of endpoints) {
        await makeRequest(endpoint.path, {
            method: endpoint.method,
            headers,
            body: endpoint.body ? JSON.stringify(endpoint.body) : undefined
        }).catch(() => {});
    }
    
    // Performance test
    log('Running performance tests...', 'yellow');
    const testPromises = [];
    
    for (let i = 0; i < config.concurrentUsers; i++) {
        testPromises.push((async () => {
            const userResults = [];
            const startTime = Date.now();
            
            while (Date.now() - startTime < config.testDuration) {
                for (const endpoint of endpoints) {
                    try {
                        const result = await makeRequest(endpoint.path, {
                            method: endpoint.method,
                            headers,
                            body: endpoint.body ? JSON.stringify(endpoint.body) : undefined
                        });
                        userResults.push(result);
                    } catch (error) {
                        // Error already logged
                    }
                    
                    // Rate limiting
                    await new Promise(resolve => setTimeout(resolve, 1000 / config.requestsPerSecond));
                }
            }
            
            return userResults;
        })());
    }
    
    await Promise.all(testPromises);
}

// Test WebSocket performance
async function testWebSocketPerformance(token) {
    log('\n🔌 Testing WebSocket Performance...', 'blue');
    
    const wsPromises = [];
    
    for (let i = 0; i < config.concurrentUsers; i++) {
        wsPromises.push(new Promise((resolve) => {
            const ws = new WebSocket(config.wsUrl, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            const wsResults = {
                connected: false,
                messages: 0,
                errors: 0,
                startTime: performance.now()
            };
            
            ws.on('open', () => {
                wsResults.connected = true;
                ws.send(JSON.stringify({
                    type: 'subscribe',
                    data: { stream: 'system-stats' }
                }));
            });
            
            ws.on('message', () => {
                wsResults.messages++;
            });
            
            ws.on('error', () => {
                wsResults.errors++;
            });
            
            ws.on('close', () => {
                wsResults.duration = performance.now() - wsResults.startTime;
                results.websockets.push(wsResults);
                resolve();
            });
            
            // Close after test duration
            setTimeout(() => {
                ws.close();
            }, config.testDuration);
        }));
    }
    
    await Promise.all(wsPromises);
}

// Analyze results
function analyzeResults() {
    log('\n📈 Analyzing Results...', 'blue');
    
    // API Performance
    const validRequests = results.requests.filter(r => r.status === 200);
    const failedRequests = results.requests.filter(r => r.status !== 200);
    
    const avgResponseTime = validRequests.reduce((sum, r) => sum + r.duration, 0) / validRequests.length;
    const maxResponseTime = Math.max(...validRequests.map(r => r.duration));
    const minResponseTime = Math.min(...validRequests.map(r => r.duration));
    
    // Response time percentiles
    const sortedTimes = validRequests.map(r => r.duration).sort((a, b) => a - b);
    const p50 = sortedTimes[Math.floor(sortedTimes.length * 0.5)];
    const p95 = sortedTimes[Math.floor(sortedTimes.length * 0.95)];
    const p99 = sortedTimes[Math.floor(sortedTimes.length * 0.99)];
    
    // WebSocket Performance
    const connectedWS = results.websockets.filter(ws => ws.connected).length;
    const totalMessages = results.websockets.reduce((sum, ws) => sum + ws.messages, 0);
    
    // Calculate requests per second
    const testDurationSeconds = (results.endTime - results.startTime) / 1000;
    const requestsPerSecond = results.requests.length / testDurationSeconds;
    
    // Print results
    console.log('\n' + '='.repeat(50));
    log('📊 Performance Test Results', 'green');
    console.log('='.repeat(50));
    
    console.log('\n🔗 API Performance:');
    console.log(`  Total Requests: ${results.requests.length}`);
    console.log(`  Successful: ${validRequests.length} (${((validRequests.length / results.requests.length) * 100).toFixed(1)}%)`);
    console.log(`  Failed: ${failedRequests.length}`);
    console.log(`  Errors: ${results.errors.length}`);
    console.log(`  Requests/Second: ${requestsPerSecond.toFixed(2)}`);
    
    console.log('\n⏱️  Response Times:');
    console.log(`  Average: ${avgResponseTime.toFixed(2)}ms`);
    console.log(`  Min: ${minResponseTime.toFixed(2)}ms`);
    console.log(`  Max: ${maxResponseTime.toFixed(2)}ms`);
    console.log(`  50th percentile: ${p50.toFixed(2)}ms`);
    console.log(`  95th percentile: ${p95.toFixed(2)}ms`);
    console.log(`  99th percentile: ${p99.toFixed(2)}ms`);
    
    console.log('\n🔌 WebSocket Performance:');
    console.log(`  Total Connections: ${results.websockets.length}`);
    console.log(`  Successful Connections: ${connectedWS}`);
    console.log(`  Total Messages Received: ${totalMessages}`);
    console.log(`  Avg Messages/Connection: ${(totalMessages / connectedWS).toFixed(2)}`);
    
    // Performance grades
    console.log('\n🏆 Performance Grades:');
    
    if (avgResponseTime < 100) {
        log('  Response Time: A+ (Excellent)', 'green');
    } else if (avgResponseTime < 200) {
        log('  Response Time: A (Very Good)', 'green');
    } else if (avgResponseTime < 500) {
        log('  Response Time: B (Good)', 'yellow');
    } else {
        log('  Response Time: C (Needs Improvement)', 'red');
    }
    
    const successRate = (validRequests.length / results.requests.length) * 100;
    if (successRate > 99) {
        log('  Reliability: A+ (Excellent)', 'green');
    } else if (successRate > 95) {
        log('  Reliability: A (Very Good)', 'green');
    } else if (successRate > 90) {
        log('  Reliability: B (Good)', 'yellow');
    } else {
        log('  Reliability: C (Needs Improvement)', 'red');
    }
    
    console.log('\n' + '='.repeat(50));
}

// Main test runner
async function runPerformanceTests() {
    log('🚀 NixOS GUI Performance Test Suite', 'blue');
    log('===================================', 'blue');
    log(`Test Duration: ${config.testDuration / 1000}s`);
    log(`Concurrent Users: ${config.concurrentUsers}`);
    log(`Requests/Second: ${config.requestsPerSecond}`);
    
    results.startTime = Date.now();
    
    // Authenticate
    const token = await authenticate();
    if (!token) {
        log('❌ Cannot continue without authentication', 'red');
        return;
    }
    
    // Run tests
    await testAPIPerformance(token);
    await testWebSocketPerformance(token);
    
    results.endTime = Date.now();
    
    // Analyze and display results
    analyzeResults();
    
    // Save detailed results
    const fs = require('fs');
    const resultsFile = `performance-results-${new Date().toISOString().replace(/:/g, '-')}.json`;
    fs.writeFileSync(resultsFile, JSON.stringify(results, null, 2));
    log(`\n📁 Detailed results saved to: ${resultsFile}`, 'green');
}

// Run the tests
runPerformanceTests().catch(error => {
    log(`\n❌ Test failed: ${error.message}`, 'red');
    process.exit(1);
});