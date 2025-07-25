/**
 * Test Helpers and Utilities
 * Shared functions for testing NixOS GUI
 */

const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);
const fs = require('fs').promises;
const path = require('path');

/**
 * Test Environment Setup
 */
class TestEnvironment {
    constructor() {
        this.testProfile = null;
        this.originalPath = process.env.PATH;
        this.tempDir = null;
    }

    /**
     * Set up isolated test environment
     */
    async setup() {
        // Create temporary directory for test artifacts
        this.tempDir = await fs.mkdtemp('/tmp/nixos-gui-test-');
        
        // Create a test Nix profile to avoid polluting user profile
        this.testProfile = path.join(this.tempDir, 'test-profile');
        process.env.NIX_PROFILE = this.testProfile;
        
        // Ensure Nix is available
        await this.checkNixAvailability();
        
        console.log(`Test environment set up in ${this.tempDir}`);
    }

    /**
     * Clean up test environment
     */
    async teardown() {
        // Restore original environment
        process.env.PATH = this.originalPath;
        delete process.env.NIX_PROFILE;
        
        // Clean up temporary directory
        if (this.tempDir) {
            try {
                await fs.rm(this.tempDir, { recursive: true, force: true });
            } catch (error) {
                console.warn(`Failed to clean up ${this.tempDir}:`, error);
            }
        }
    }

    /**
     * Check if Nix is available
     */
    async checkNixAvailability() {
        try {
            const { stdout } = await execAsync('nix --version');
            return stdout.includes('nix');
        } catch (error) {
            throw new Error('Nix is not available. Please install Nix to run integration tests.');
        }
    }
}

/**
 * Mock Nix Operations for Unit Tests
 */
class MockNixOperations {
    constructor() {
        this.packages = new Map([
            ['hello', {
                name: 'hello',
                version: '2.12.1',
                description: 'A program that produces a familiar, friendly greeting'
            }],
            ['firefox', {
                name: 'firefox',
                version: '121.0',
                description: 'Mozilla Firefox web browser'
            }],
            ['git', {
                name: 'git',
                version: '2.42.0',
                description: 'Distributed version control system'
            }]
        ]);
        
        this.installedPackages = new Set();
    }

    async search(query) {
        const results = [];
        for (const [name, pkg] of this.packages) {
            if (name.includes(query.toLowerCase()) || 
                pkg.description.toLowerCase().includes(query.toLowerCase())) {
                results.push(pkg);
            }
        }
        return results;
    }

    async install(packageName) {
        if (!this.packages.has(packageName)) {
            throw new Error(`Package '${packageName}' not found`);
        }
        
        this.installedPackages.add(packageName);
        return { success: true, package: packageName };
    }

    async remove(packageName) {
        if (!this.installedPackages.has(packageName)) {
            throw new Error(`Package '${packageName}' is not installed`);
        }
        
        this.installedPackages.delete(packageName);
        return { success: true, package: packageName };
    }

    async listInstalled() {
        return Array.from(this.installedPackages).map(name => this.packages.get(name));
    }
}

/**
 * Test Data Generators
 */
const TestData = {
    /**
     * Generate a valid package object
     */
    package(overrides = {}) {
        return {
            name: 'test-package',
            version: '1.0.0',
            description: 'A test package',
            size: 1024 * 1024, // 1MB
            ...overrides
        };
    },

    /**
     * Generate a job object
     */
    job(overrides = {}) {
        return {
            id: `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            type: 'install',
            status: 'pending',
            progress: 0,
            createdAt: new Date(),
            metadata: {},
            ...overrides
        };
    },

    /**
     * Generate an error object
     */
    error(overrides = {}) {
        return {
            message: 'Test error',
            code: 'TEST_ERROR',
            details: {},
            ...overrides
        };
    }
};

/**
 * Assertion Helpers
 */
const Assertions = {
    /**
     * Assert that a package object has required fields
     */
    assertValidPackage(pkg) {
        expect(pkg).toHaveProperty('name');
        expect(pkg).toHaveProperty('version');
        expect(pkg).toHaveProperty('description');
        expect(typeof pkg.name).toBe('string');
        expect(typeof pkg.version).toBe('string');
        expect(typeof pkg.description).toBe('string');
    },

    /**
     * Assert that a job object has required fields
     */
    assertValidJob(job) {
        expect(job).toHaveProperty('id');
        expect(job).toHaveProperty('type');
        expect(job).toHaveProperty('status');
        expect(job).toHaveProperty('progress');
        expect(job).toHaveProperty('createdAt');
        expect(['pending', 'running', 'completed', 'failed']).toContain(job.status);
        expect(job.progress).toBeGreaterThanOrEqual(0);
        expect(job.progress).toBeLessThanOrEqual(100);
    },

    /**
     * Assert that an API response is successful
     */
    assertSuccessResponse(response) {
        expect(response).toHaveProperty('success', true);
        expect(response).not.toHaveProperty('error');
    },

    /**
     * Assert that an API response is an error
     */
    assertErrorResponse(response, expectedError = null) {
        expect(response).toHaveProperty('success', false);
        expect(response).toHaveProperty('error');
        if (expectedError) {
            expect(response.error).toContain(expectedError);
        }
    }
};

/**
 * Wait Helpers
 */
const WaitHelpers = {
    /**
     * Wait for a condition to be true
     */
    async waitFor(condition, timeout = 5000, interval = 100) {
        const start = Date.now();
        while (Date.now() - start < timeout) {
            if (await condition()) {
                return true;
            }
            await new Promise(resolve => setTimeout(resolve, interval));
        }
        throw new Error('Timeout waiting for condition');
    },

    /**
     * Wait for a promise with timeout
     */
    async withTimeout(promise, timeout = 5000) {
        const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => reject(new Error('Operation timed out')), timeout);
        });
        return Promise.race([promise, timeoutPromise]);
    }
};

/**
 * Network Helpers
 */
const NetworkHelpers = {
    /**
     * Find an available port
     */
    async findAvailablePort(startPort = 8000) {
        const net = require('net');
        
        for (let port = startPort; port < startPort + 1000; port++) {
            const available = await new Promise((resolve) => {
                const server = net.createServer();
                server.listen(port, () => {
                    server.close(() => resolve(true));
                });
                server.on('error', () => resolve(false));
            });
            
            if (available) return port;
        }
        
        throw new Error('No available ports found');
    },

    /**
     * Wait for a server to be ready
     */
    async waitForServer(url, timeout = 10000) {
        const axios = require('axios');
        const start = Date.now();
        
        while (Date.now() - start < timeout) {
            try {
                await axios.get(url);
                return true;
            } catch (error) {
                await new Promise(resolve => setTimeout(resolve, 100));
            }
        }
        
        throw new Error(`Server at ${url} did not start in time`);
    }
};

/**
 * File System Helpers
 */
const FileHelpers = {
    /**
     * Create a temporary test file
     */
    async createTempFile(content = '', extension = '.txt') {
        const tempDir = await fs.mkdtemp('/tmp/test-');
        const filePath = path.join(tempDir, `test${extension}`);
        await fs.writeFile(filePath, content);
        return filePath;
    },

    /**
     * Clean up test files
     */
    async cleanupPath(filePath) {
        try {
            const stat = await fs.stat(filePath);
            if (stat.isDirectory()) {
                await fs.rm(filePath, { recursive: true, force: true });
            } else {
                await fs.unlink(filePath);
            }
        } catch (error) {
            // Ignore errors if file doesn't exist
        }
    }
};

module.exports = {
    TestEnvironment,
    MockNixOperations,
    TestData,
    Assertions,
    WaitHelpers,
    NetworkHelpers,
    FileHelpers
};