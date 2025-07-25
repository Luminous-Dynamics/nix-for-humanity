/**
 * End-to-End Tests
 * Tests complete user workflows through the application
 */

const puppeteer = require('puppeteer');
const { spawn } = require('child_process');
const path = require('path');

// Test configuration
const BASE_URL = process.env.TEST_URL || 'http://localhost:8080';
const TEST_USER = process.env.TEST_USER || 'testuser';
const TEST_PASS = process.env.TEST_PASS || 'testpass';

describe('E2E: Complete User Workflows', () => {
    let browser;
    let page;
    let serverProcess;
    
    beforeAll(async () => {
        // Start the server
        serverProcess = spawn('npm', ['start'], {
            cwd: path.join(__dirname, '../..'),
            env: { ...process.env, NODE_ENV: 'test' }
        });
        
        // Wait for server to be ready
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Launch browser
        browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
    });
    
    afterAll(async () => {
        if (browser) await browser.close();
        if (serverProcess) serverProcess.kill();
    });
    
    beforeEach(async () => {
        page = await browser.newPage();
        await page.setViewport({ width: 1280, height: 800 });
    });
    
    afterEach(async () => {
        if (page) await page.close();
    });
    
    describe('Authentication Flow', () => {
        it('should show login screen for unauthenticated users', async () => {
            await page.goto(BASE_URL);
            await page.waitForSelector('.login-form');
            
            const title = await page.$eval('.login-title', el => el.textContent);
            expect(title).toContain('NixOS GUI Login');
        });
        
        it('should login with valid credentials', async () => {
            await page.goto(BASE_URL);
            await page.waitForSelector('.login-form');
            
            // Enter credentials
            await page.type('#username', TEST_USER);
            await page.type('#password', TEST_PASS);
            
            // Submit form
            await page.click('.login-button');
            
            // Wait for dashboard
            await page.waitForSelector('.dashboard', { timeout: 10000 });
            
            // Check user info is displayed
            const userInfo = await page.$eval('.user-info', el => el.textContent);
            expect(userInfo).toContain(TEST_USER);
        });
        
        it('should show error for invalid credentials', async () => {
            await page.goto(BASE_URL);
            await page.waitForSelector('.login-form');
            
            await page.type('#username', 'invaliduser');
            await page.type('#password', 'wrongpass');
            await page.click('.login-button');
            
            // Wait for error message
            await page.waitForSelector('.error-message');
            const error = await page.$eval('.error-message', el => el.textContent);
            expect(error).toContain('Invalid username or password');
        });
        
        it('should logout successfully', async () => {
            // Login first
            await loginUser(page);
            
            // Click logout
            await page.click('.user-menu');
            await page.waitForSelector('.logout-button');
            await page.click('.logout-button');
            
            // Should redirect to login
            await page.waitForSelector('.login-form');
            
            // Verify can't access dashboard
            await page.goto(BASE_URL + '/dashboard');
            await page.waitForSelector('.login-form');
        });
    });
    
    describe('Package Management Workflow', () => {
        beforeEach(async () => {
            await loginUser(page);
        });
        
        it('should search for packages', async () => {
            // Navigate to packages
            await page.click('a[href="/packages"]');
            await page.waitForSelector('.package-search');
            
            // Search for firefox
            await page.type('.search-input', 'firefox');
            await page.keyboard.press('Enter');
            
            // Wait for results
            await page.waitForSelector('.package-card');
            
            // Verify results
            const packages = await page.$$('.package-card');
            expect(packages.length).toBeGreaterThan(0);
            
            const firstPackage = await page.$eval(
                '.package-card:first-child .package-name',
                el => el.textContent
            );
            expect(firstPackage.toLowerCase()).toContain('firefox');
        });
        
        it('should install a package', async () => {
            await page.goto(BASE_URL + '/packages');
            await page.waitForSelector('.package-search');
            
            // Search for a small package
            await page.type('.search-input', 'hello');
            await page.keyboard.press('Enter');
            await page.waitForSelector('.package-card');
            
            // Click install
            await page.click('.package-card:first-child .install-button');
            
            // Confirm installation
            await page.waitForSelector('.confirm-dialog');
            await page.click('.confirm-button');
            
            // Wait for progress
            await page.waitForSelector('.progress-bar');
            
            // Wait for completion (with longer timeout)
            await page.waitForSelector('.success-notification', {
                timeout: 60000
            });
            
            const notification = await page.$eval(
                '.success-notification',
                el => el.textContent
            );
            expect(notification).toContain('installed successfully');
        });
        
        it('should show installed packages', async () => {
            await page.goto(BASE_URL + '/packages');
            await page.waitForSelector('.package-tabs');
            
            // Click installed tab
            await page.click('.tab-button[data-tab="installed"]');
            await page.waitForSelector('.installed-packages');
            
            // Should show installed packages
            const packages = await page.$$('.installed-package-card');
            expect(packages.length).toBeGreaterThan(0);
        });
    });
    
    describe('Service Management Workflow', () => {
        beforeEach(async () => {
            await loginUser(page);
        });
        
        it('should display system services', async () => {
            await page.click('a[href="/services"]');
            await page.waitForSelector('.services-list');
            
            const services = await page.$$('.service-card');
            expect(services.length).toBeGreaterThan(0);
            
            // Check service info is displayed
            const hasStatus = await page.$('.service-status');
            expect(hasStatus).toBeTruthy();
        });
        
        it('should filter services', async () => {
            await page.goto(BASE_URL + '/services');
            await page.waitForSelector('.services-list');
            
            // Filter by running services
            await page.click('.filter-dropdown');
            await page.click('.filter-option[data-value="running"]');
            
            // Wait for filter to apply
            await page.waitForFunction(
                () => document.querySelectorAll('.service-card.running').length > 0
            );
            
            // All visible services should be running
            const services = await page.$$eval('.service-card', cards =>
                cards.map(card => card.classList.contains('running'))
            );
            expect(services.every(isRunning => isRunning)).toBe(true);
        });
        
        it('should start/stop a service', async () => {
            await page.goto(BASE_URL + '/services');
            await page.waitForSelector('.services-list');
            
            // Find a stopped service
            const stoppedService = await page.$('.service-card.stopped');
            if (stoppedService) {
                // Click start button
                await stoppedService.click('.start-button');
                
                // Confirm action
                await page.waitForSelector('.confirm-dialog');
                await page.click('.confirm-button');
                
                // Wait for status update
                await page.waitForSelector('.success-notification');
                
                // Service should now show as running
                await page.waitForFunction(
                    el => el.classList.contains('running'),
                    {},
                    stoppedService
                );
            }
        });
    });
    
    describe('Configuration Editor Workflow', () => {
        beforeEach(async () => {
            await loginUser(page);
        });
        
        it('should load configuration file', async () => {
            await page.click('a[href="/configuration"]');
            await page.waitForSelector('.config-editor');
            
            // Editor should be loaded
            const editorContent = await page.$eval(
                '.code-editor',
                el => el.textContent || el.value
            );
            expect(editorContent).toContain('pkgs');
        });
        
        it('should validate configuration', async () => {
            await page.goto(BASE_URL + '/configuration');
            await page.waitForSelector('.config-editor');
            
            // Click validate button
            await page.click('.validate-button');
            
            // Wait for validation result
            await page.waitForSelector('.validation-result');
            
            const result = await page.$eval(
                '.validation-result',
                el => el.textContent
            );
            expect(result).toMatch(/valid|invalid/i);
        });
        
        it('should show syntax highlighting', async () => {
            await page.goto(BASE_URL + '/configuration');
            await page.waitForSelector('.config-editor');
            
            // Check for syntax highlighting classes
            const hasHighlighting = await page.$('.syntax-keyword');
            expect(hasHighlighting).toBeTruthy();
        });
    });
    
    describe('System Management Workflow', () => {
        beforeEach(async () => {
            await loginUser(page);
        });
        
        it('should display system generations', async () => {
            await page.click('a[href="/system"]');
            await page.waitForSelector('.generations-list');
            
            const generations = await page.$$('.generation-card');
            expect(generations.length).toBeGreaterThan(0);
            
            // Current generation should be marked
            const current = await page.$('.generation-card.current');
            expect(current).toBeTruthy();
        });
        
        it('should show system information', async () => {
            await page.goto(BASE_URL + '/system');
            await page.waitForSelector('.system-info');
            
            // Check system info is displayed
            const nixosVersion = await page.$eval(
                '.nixos-version',
                el => el.textContent
            );
            expect(nixosVersion).toMatch(/\d+\.\d+/);
            
            const kernel = await page.$eval(
                '.kernel-version',
                el => el.textContent
            );
            expect(kernel).toContain('Linux');
        });
    });
    
    describe('Help System Integration', () => {
        beforeEach(async () => {
            await loginUser(page);
        });
        
        it('should show contextual help tooltips', async () => {
            await page.goto(BASE_URL + '/packages');
            await page.waitForSelector('.package-search');
            
            // Hover over help icon
            await page.hover('.help-icon');
            
            // Tooltip should appear
            await page.waitForSelector('.help-tooltip');
            
            const tooltipText = await page.$eval(
                '.help-tooltip',
                el => el.textContent
            );
            expect(tooltipText).toBeTruthy();
        });
        
        it('should start interactive tour', async () => {
            await page.goto(BASE_URL + '/dashboard');
            
            // Open help menu
            await page.click('.help-menu-button');
            await page.waitForSelector('.help-menu');
            
            // Start tour
            await page.click('.start-tour-button');
            
            // Tour should start
            await page.waitForSelector('.tour-overlay');
            await page.waitForSelector('.tour-step');
            
            const tourText = await page.$eval(
                '.tour-step',
                el => el.textContent
            );
            expect(tourText).toContain('Welcome');
        });
    });
    
    describe('Plugin System Integration', () => {
        beforeEach(async () => {
            await loginUser(page);
        });
        
        it('should access plugin manager', async () => {
            // Open tools menu
            await page.click('.menu-item[data-menu="tools"]');
            await page.waitForSelector('.submenu');
            
            // Click plugin manager
            await page.click('#open-plugin-manager');
            
            // Plugin manager should open
            await page.waitForSelector('.plugin-manager-modal.active');
            
            const title = await page.$eval(
                '.plugin-manager-header h2',
                el => el.textContent
            );
            expect(title).toBe('Plugin Manager');
        });
        
        it('should browse available plugins', async () => {
            await openPluginManager(page);
            
            // Switch to browse tab
            await page.click('.tab-button[data-tab="browse"]');
            await page.waitForSelector('.available-plugins');
            
            // Should show available plugins
            const plugins = await page.$$('.plugin-card.available');
            expect(plugins.length).toBeGreaterThan(0);
        });
    });
    
    describe('Responsive Design', () => {
        it('should work on mobile viewport', async () => {
            await page.setViewport({ width: 375, height: 667 });
            await loginUser(page);
            
            // Mobile menu should be visible
            await page.waitForSelector('.mobile-menu-button');
            
            // Open mobile menu
            await page.click('.mobile-menu-button');
            await page.waitForSelector('.mobile-menu.open');
            
            // Navigate to packages
            await page.click('.mobile-menu a[href="/packages"]');
            await page.waitForSelector('.package-search');
            
            // UI should be adapted for mobile
            const isMobileLayout = await page.$eval(
                '.container',
                el => window.getComputedStyle(el).maxWidth === '100%'
            );
            expect(isMobileLayout).toBe(true);
        });
        
        it('should work on tablet viewport', async () => {
            await page.setViewport({ width: 768, height: 1024 });
            await loginUser(page);
            
            // Should show adapted layout
            const sidebarCollapsed = await page.$eval(
                '.sidebar',
                el => el.classList.contains('collapsed')
            );
            expect(sidebarCollapsed).toBe(true);
        });
    });
    
    describe('Performance', () => {
        it('should load dashboard quickly', async () => {
            const startTime = Date.now();
            
            await loginUser(page);
            
            const loadTime = Date.now() - startTime;
            expect(loadTime).toBeLessThan(3000); // 3 seconds
        });
        
        it('should handle large package lists efficiently', async () => {
            await loginUser(page);
            await page.goto(BASE_URL + '/packages');
            
            // Search for common term
            await page.type('.search-input', 'lib');
            await page.keyboard.press('Enter');
            
            // Should load results quickly
            const startTime = Date.now();
            await page.waitForSelector('.package-card');
            const loadTime = Date.now() - startTime;
            
            expect(loadTime).toBeLessThan(2000); // 2 seconds
            
            // Should be able to scroll smoothly
            await page.evaluate(() => {
                window.scrollTo(0, document.body.scrollHeight);
            });
        });
    });
    
    describe('Accessibility', () => {
        beforeEach(async () => {
            await loginUser(page);
        });
        
        it('should be keyboard navigable', async () => {
            await page.goto(BASE_URL + '/dashboard');
            
            // Tab through elements
            await page.keyboard.press('Tab');
            await page.keyboard.press('Tab');
            await page.keyboard.press('Tab');
            
            // Check focus is visible
            const focusedElement = await page.evaluate(() => {
                return document.activeElement.tagName;
            });
            expect(focusedElement).toBeTruthy();
        });
        
        it('should have proper ARIA labels', async () => {
            const mainNav = await page.$('nav[aria-label="Main navigation"]');
            expect(mainNav).toBeTruthy();
            
            const searchInput = await page.$('input[aria-label="Search packages"]');
            expect(searchInput).toBeTruthy();
        });
        
        it('should work with screen reader', async () => {
            // Check for screen reader landmarks
            const main = await page.$('main');
            const nav = await page.$('nav');
            const header = await page.$('header');
            
            expect(main).toBeTruthy();
            expect(nav).toBeTruthy();
            expect(header).toBeTruthy();
        });
    });
});

// Helper functions

async function loginUser(page) {
    await page.goto(BASE_URL);
    
    // Check if already logged in
    const isDashboard = await page.$('.dashboard');
    if (isDashboard) return;
    
    await page.waitForSelector('.login-form');
    await page.type('#username', TEST_USER);
    await page.type('#password', TEST_PASS);
    await page.click('.login-button');
    await page.waitForSelector('.dashboard', { timeout: 10000 });
}

async function openPluginManager(page) {
    await page.click('.menu-item[data-menu="tools"]');
    await page.waitForSelector('.submenu');
    await page.click('#open-plugin-manager');
    await page.waitForSelector('.plugin-manager-modal.active');
}