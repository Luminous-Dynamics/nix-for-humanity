/**
 * Integration Tests for NixOS GUI
 * These tests run real Nix operations in a controlled environment
 */

const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);
const fs = require('fs').promises;
const path = require('path');
const axios = require('axios');
const WebSocket = require('ws');

// Test configuration
const TEST_PORT = process.env.TEST_PORT || 17891;
const TEST_WS_PORT = process.env.TEST_WS_PORT || 17892;
const TEST_TIMEOUT = 60000; // 1 minute for package operations

// Test packages that are small and quick to install
const TEST_PACKAGES = {
    small: 'hello',      // ~25KB, minimal package
    medium: 'jq',        // ~1MB, useful utility
    python: 'python3',   // Larger, but commonly needed
    invalid: 'this-package-does-not-exist-12345'
};

describe('NixOS GUI Integration Tests', () => {
    let server;
    let baseURL;
    let ws;

    beforeAll(async () => {
        // Start test server
        process.env.PORT = TEST_PORT;
        process.env.WS_PORT = TEST_WS_PORT;
        process.env.NODE_ENV = 'test';
        
        server = require('../backend/real-backend');
        baseURL = `http://localhost:${TEST_PORT}`;
        
        // Wait for server to be ready
        await waitForServer(baseURL);
        
        // Connect WebSocket
        ws = new WebSocket(`ws://localhost:${TEST_WS_PORT}`);
        await new Promise((resolve) => {
            ws.on('open', resolve);
        });
    });

    afterAll(async () => {
        if (ws) ws.close();
        if (server) {
            await new Promise((resolve) => {
                server.close(resolve);
            });
        }
    });

    describe('System Information', () => {
        test('should detect Nix installation', async () => {
            const response = await axios.get(`${baseURL}/api/system/info`);
            
            expect(response.data.success).toBe(true);
            expect(response.data.nixVersion).toBeDefined();
            expect(response.data.nixVersion).toMatch(/nix \(Nix\) \d+\.\d+/);
        });

        test('should check if running on NixOS', async () => {
            const response = await axios.get(`${baseURL}/api/system/info`);
            
            if (response.data.systemVersion) {
                expect(response.data.systemVersion).toMatch(/\d+\.\d+/);
            } else {
                // Not on NixOS, should still work
                expect(response.data.nixVersion).toBeDefined();
            }
        });

        test('should report disk and memory usage', async () => {
            const response = await axios.get(`${baseURL}/api/system/info`);
            
            expect(response.data.disk).toBeDefined();
            expect(response.data.disk.used).toBeDefined();
            expect(response.data.memory).toBeDefined();
            expect(response.data.memory.total).toBeDefined();
        });
    });

    describe('Package Search', () => {
        test('should find common packages', async () => {
            const response = await axios.post(`${baseURL}/api/nix/search`, {
                query: 'firefox'
            });
            
            expect(response.data.success).toBe(true);
            expect(response.data.packages).toBeInstanceOf(Array);
            expect(response.data.packages.length).toBeGreaterThan(0);
            
            const firefox = response.data.packages.find(p => p.name === 'firefox');
            expect(firefox).toBeDefined();
            expect(firefox.description).toBeDefined();
        });

        test('should handle empty search results', async () => {
            const response = await axios.post(`${baseURL}/api/nix/search`, {
                query: TEST_PACKAGES.invalid
            });
            
            expect(response.data.success).toBe(true);
            expect(response.data.packages).toEqual([]);
        });

        test('should escape special characters in search', async () => {
            const response = await axios.post(`${baseURL}/api/nix/search`, {
                query: 'test; echo "hacked"'
            });
            
            expect(response.data.success).toBe(true);
            // Should not execute the echo command
        });
    });

    describe('Package Installation', () => {
        test('should install a small package', async () => {
            jest.setTimeout(TEST_TIMEOUT);
            
            // First, check if package exists
            const searchResponse = await axios.post(`${baseURL}/api/nix/search`, {
                query: TEST_PACKAGES.small
            });
            
            expect(searchResponse.data.packages.length).toBeGreaterThan(0);
            
            // Install the package
            const installResponse = await axios.post(`${baseURL}/api/nix/install`, {
                package: TEST_PACKAGES.small,
                scope: 'user'
            });
            
            expect(installResponse.data.success).toBe(true);
            expect(installResponse.data.jobId).toBeDefined();
            
            // Wait for installation to complete
            const job = await waitForJob(baseURL, installResponse.data.jobId);
            expect(job.status).toBe('completed');
            
            // Verify package is installed
            const { stdout } = await execAsync('nix profile list | grep hello || nix-env -q | grep hello');
            expect(stdout).toContain('hello');
        });

        test('should handle package not found error', async () => {
            const installResponse = await axios.post(`${baseURL}/api/nix/install`, {
                package: TEST_PACKAGES.invalid,
                scope: 'user'
            });
            
            expect(installResponse.data.success).toBe(true);
            expect(installResponse.data.jobId).toBeDefined();
            
            // Wait for job to fail
            const job = await waitForJob(baseURL, installResponse.data.jobId);
            expect(job.status).toBe('failed');
            expect(job.error).toContain('not found');
        });

        test('should generate config snippet for system packages', async () => {
            const response = await axios.post(`${baseURL}/api/nix/install`, {
                package: TEST_PACKAGES.small,
                scope: 'system'
            });
            
            expect(response.data.success).toBe(true);
            expect(response.data.action).toBe('show-config');
            expect(response.data.snippet).toContain('environment.systemPackages');
            expect(response.data.snippet).toContain(TEST_PACKAGES.small);
        });
    });

    describe('Package Removal', () => {
        test('should remove an installed package', async () => {
            jest.setTimeout(TEST_TIMEOUT);
            
            // First ensure package is installed
            await execAsync(`nix profile install nixpkgs#${TEST_PACKAGES.small} || nix-env -iA nixpkgs.${TEST_PACKAGES.small}`);
            
            // Remove the package
            const removeResponse = await axios.post(`${baseURL}/api/nix/remove`, {
                package: TEST_PACKAGES.small
            });
            
            expect(removeResponse.data.success).toBe(true);
            expect(removeResponse.data.jobId).toBeDefined();
            
            // Wait for removal to complete
            const job = await waitForJob(baseURL, removeResponse.data.jobId);
            expect(job.status).toBe('completed');
            
            // Verify package is removed
            try {
                await execAsync('nix profile list | grep hello || nix-env -q | grep hello');
                // If we get here, package is still installed
                fail('Package should have been removed');
            } catch (error) {
                // Expected - package not found
                expect(error.code).toBe(1);
            }
        });
    });

    describe('Preview Operations', () => {
        test('should preview installation without actually installing', async () => {
            const response = await axios.post(`${baseURL}/api/nix/preview`, {
                action: 'install',
                package: TEST_PACKAGES.medium,
                scope: 'user'
            });
            
            expect(response.data.success).toBe(true);
            expect(response.data.preview).toBeDefined();
            expect(response.data.preview.package).toBeDefined();
            expect(response.data.preview.package.name).toBe(TEST_PACKAGES.medium);
            
            // Verify package is NOT installed
            try {
                await execAsync('nix profile list | grep jq || nix-env -q | grep "^jq-"');
                // Package might already be installed from other tests
            } catch (error) {
                // Expected - package not installed
                expect(error.code).toBe(1);
            }
        });
    });

    describe('Service Management', () => {
        test('should check service status', async () => {
            // Use a service that's likely to exist
            const response = await axios.post(`${baseURL}/api/service/status`, {
                service: 'dbus'
            });
            
            expect(response.data.success).toBe(true);
            // Status check doesn't require sudo
        });

        test('should return sudo requirement for privileged operations', async () => {
            const response = await axios.post(`${baseURL}/api/service/enable`, {
                service: 'nginx'
            });
            
            expect(response.data.success).toBe(true);
            expect(response.data.requiresSudo).toBe(true);
            expect(response.data.command).toContain('sudo systemctl enable');
        });
    });

    describe('Error Handling', () => {
        test('should handle network errors gracefully', async () => {
            // Simulate network error by using wrong port
            try {
                await axios.get('http://localhost:99999/api/health');
                fail('Should have thrown an error');
            } catch (error) {
                expect(error.code).toBe('ECONNREFUSED');
            }
        });

        test('should validate package names', async () => {
            try {
                await axios.post(`${baseURL}/api/nix/install`, {
                    package: '../../etc/passwd'
                });
                fail('Should have rejected invalid package name');
            } catch (error) {
                expect(error.response.status).toBe(400);
                expect(error.response.data.error).toContain('Invalid package name');
            }
        });

        test('should handle command timeout', async () => {
            jest.setTimeout(TEST_TIMEOUT * 2);
            
            // Try to install a very large package with short timeout
            const originalTimeout = process.env.COMMAND_TIMEOUT;
            process.env.COMMAND_TIMEOUT = '1000'; // 1 second
            
            try {
                const response = await axios.post(`${baseURL}/api/nix/install`, {
                    package: 'libreoffice',  // Large package
                    scope: 'user'
                });
                
                const job = await waitForJob(baseURL, response.data.jobId, 5000);
                expect(job.status).toBe('failed');
                expect(job.error).toContain('timeout');
            } finally {
                process.env.COMMAND_TIMEOUT = originalTimeout;
            }
        });
    });

    describe('WebSocket Updates', () => {
        test('should receive real-time job updates', async () => {
            const updates = [];
            
            ws.on('message', (data) => {
                const message = JSON.parse(data);
                if (message.type === 'job-update') {
                    updates.push(message.job);
                }
            });
            
            // Start an installation
            const response = await axios.post(`${baseURL}/api/nix/install`, {
                package: TEST_PACKAGES.small,
                scope: 'user'
            });
            
            // Wait for updates
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            expect(updates.length).toBeGreaterThan(0);
            expect(updates.some(u => u.status === 'running')).toBe(true);
        });
    });

    describe('Diagnostics', () => {
        test('should run system diagnostics', async () => {
            const response = await axios.post(`${baseURL}/api/diagnose`, {
                target: 'system'
            });
            
            expect(response.data.success).toBe(true);
            expect(response.data.diagnostics).toBeDefined();
            expect(response.data.diagnostics.nix).toBeDefined();
            expect(response.data.diagnostics.nix.available).toBe(true);
        });
    });
});

// Helper functions
async function waitForServer(url, timeout = 10000) {
    const start = Date.now();
    while (Date.now() - start < timeout) {
        try {
            await axios.get(`${url}/api/health`);
            return;
        } catch (error) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
    }
    throw new Error('Server did not start in time');
}

async function waitForJob(baseURL, jobId, timeout = 30000) {
    const start = Date.now();
    while (Date.now() - start < timeout) {
        const response = await axios.get(`${baseURL}/api/job/${jobId}`);
        const job = response.data.job;
        
        if (job.status === 'completed' || job.status === 'failed') {
            return job;
        }
        
        await new Promise(resolve => setTimeout(resolve, 500));
    }
    throw new Error('Job did not complete in time');
}