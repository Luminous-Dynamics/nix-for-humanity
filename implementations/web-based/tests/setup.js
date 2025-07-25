/**
 * Jest Setup File
 * Configure test environment and global mocks
 */

// Add custom matchers
expect.extend({
    toBeWithinRange(received, floor, ceiling) {
        const pass = received >= floor && received <= ceiling;
        if (pass) {
            return {
                message: () => `expected ${received} not to be within range ${floor} - ${ceiling}`,
                pass: true,
            };
        } else {
            return {
                message: () => `expected ${received} to be within range ${floor} - ${ceiling}`,
                pass: false,
            };
        }
    },
});

// Mock browser APIs
global.ResizeObserver = jest.fn().mockImplementation(() => ({
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn(),
}));

global.IntersectionObserver = jest.fn().mockImplementation(() => ({
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn(),
}));

// Mock requestAnimationFrame
global.requestAnimationFrame = jest.fn((cb) => setTimeout(cb, 0));
global.cancelAnimationFrame = jest.fn((id) => clearTimeout(id));

// Mock Web APIs
global.Worker = jest.fn().mockImplementation(() => ({
    postMessage: jest.fn(),
    terminate: jest.fn(),
}));

// Mock performance API
global.performance = {
    now: jest.fn(() => Date.now()),
    mark: jest.fn(),
    measure: jest.fn(),
    getEntriesByType: jest.fn(() => []),
    getEntriesByName: jest.fn(() => []),
};

// Mock crypto API
global.crypto = {
    getRandomValues: jest.fn((arr) => {
        for (let i = 0; i < arr.length; i++) {
            arr[i] = Math.floor(Math.random() * 256);
        }
        return arr;
    }),
    subtle: {
        digest: jest.fn(),
        encrypt: jest.fn(),
        decrypt: jest.fn(),
    },
};

// Mock WebSocket
global.WebSocket = jest.fn().mockImplementation(() => ({
    send: jest.fn(),
    close: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
}));

// Mock notifications
global.Notification = jest.fn().mockImplementation(() => ({
    close: jest.fn(),
}));
global.Notification.permission = 'granted';
global.Notification.requestPermission = jest.fn().mockResolvedValue('granted');

// Mock service worker
global.navigator.serviceWorker = {
    register: jest.fn().mockResolvedValue({}),
    ready: Promise.resolve({}),
};

// Mock matchMedia
global.matchMedia = jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
}));

// Mock console methods for cleaner test output
const originalConsole = { ...console };
global.console = {
    ...originalConsole,
    error: jest.fn((...args) => {
        // Only show actual errors, not expected ones
        if (!args[0]?.includes?.('Expected')) {
            originalConsole.error(...args);
        }
    }),
    warn: jest.fn((...args) => {
        // Only show actual warnings
        if (!args[0]?.includes?.('Expected')) {
            originalConsole.warn(...args);
        }
    }),
    log: jest.fn(),
    info: jest.fn(),
    debug: jest.fn(),
};

// Set up DOM environment
beforeEach(() => {
    // Clear all mocks
    jest.clearAllMocks();
    
    // Reset document body
    document.body.innerHTML = '';
    
    // Reset document head
    document.head.innerHTML = '';
    
    // Add common elements
    const root = document.createElement('div');
    root.id = 'app';
    document.body.appendChild(root);
});

// Clean up after each test
afterEach(() => {
    // Clear all timers
    jest.clearAllTimers();
    
    // Clear all event listeners
    document.removeEventListener('click', jest.fn());
    document.removeEventListener('keydown', jest.fn());
    
    // Clear localStorage
    if (global.localStorage) {
        global.localStorage.clear();
    }
    
    // Clear sessionStorage
    if (global.sessionStorage) {
        global.sessionStorage.clear();
    }
});

// Helper function to wait for async updates
global.waitFor = (callback, options = {}) => {
    const { timeout = 1000, interval = 50 } = options;
    
    return new Promise((resolve, reject) => {
        const startTime = Date.now();
        
        const check = () => {
            try {
                callback();
                resolve();
            } catch (error) {
                if (Date.now() - startTime >= timeout) {
                    reject(error);
                } else {
                    setTimeout(check, interval);
                }
            }
        };
        
        check();
    });
};

// Helper to create mock fetch responses
global.createFetchResponse = (data, options = {}) => {
    return Promise.resolve({
        ok: options.ok !== false,
        status: options.status || 200,
        statusText: options.statusText || 'OK',
        headers: new Map(Object.entries(options.headers || {})),
        json: () => Promise.resolve(data),
        text: () => Promise.resolve(JSON.stringify(data)),
        blob: () => Promise.resolve(new Blob([JSON.stringify(data)])),
    });
};

// Helper to trigger events
global.triggerEvent = (element, eventType, options = {}) => {
    const event = new Event(eventType, { bubbles: true, ...options });
    Object.assign(event, options);
    element.dispatchEvent(event);
};

// Add test utilities to window
if (typeof window !== 'undefined') {
    window.testUtils = {
        flushPromises: () => new Promise(resolve => setImmediate(resolve)),
        tick: (ms = 0) => new Promise(resolve => setTimeout(resolve, ms)),
    };
}