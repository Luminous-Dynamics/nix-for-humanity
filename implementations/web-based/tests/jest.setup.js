/**
 * Jest Setup File
 * Global configuration and setup for all tests
 */

// Increase timeout for integration tests
jest.setTimeout(30000);

// Set up global test environment variables
process.env.NODE_ENV = 'test';
process.env.LOG_LEVEL = 'error'; // Reduce noise during tests

// Mock console methods to reduce noise
const originalConsoleError = console.error;
const originalConsoleWarn = console.warn;

global.console = {
    ...console,
    error: jest.fn((...args) => {
        // Only show actual errors, not expected ones
        if (!args[0]?.includes('Expected') && !args[0]?.includes('handled')) {
            originalConsoleError(...args);
        }
    }),
    warn: jest.fn((...args) => {
        // Suppress warnings during tests
        if (process.env.DEBUG_TESTS) {
            originalConsoleWarn(...args);
        }
    })
};

// Global cleanup handlers
const cleanup = [];

global.registerCleanup = (fn) => {
    cleanup.push(fn);
};

// Cleanup after all tests
afterAll(async () => {
    for (const fn of cleanup) {
        await fn();
    }
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection in tests:', reason);
    // Fail the test
    throw reason;
});

// Add custom matchers
expect.extend({
    toBeValidPackageName(received) {
        const valid = /^[a-zA-Z0-9][a-zA-Z0-9._-]*$/.test(received);
        return {
            pass: valid,
            message: () =>
                `Expected "${received}" to ${valid ? 'not ' : ''}be a valid package name`
        };
    },
    
    toBeWithinRange(received, floor, ceiling) {
        const pass = received >= floor && received <= ceiling;
        return {
            pass,
            message: () =>
                `Expected ${received} to ${pass ? 'not ' : ''}be within range ${floor} - ${ceiling}`
        };
    }
});