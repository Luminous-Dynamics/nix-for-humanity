/**
 * Performance End-to-End Tests
 * Tests application performance metrics and thresholds
 */

const puppeteer = require('puppeteer');
const lighthouse = require('lighthouse');
const { spawn } = require('child_process');
const path = require('path');

const BASE_URL = process.env.TEST_URL || 'http://localhost:8080';

describe('E2E: Performance Tests', () => {
    let browser;
    let serverProcess;
    
    beforeAll(async () => {
        // Start server
        serverProcess = spawn('npm', ['start'], {
            cwd: path.join(__dirname, '../..'),
            env: { ...process.env, NODE_ENV: 'production' }
        });
        
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
    });
    
    afterAll(async () => {
        if (browser) await browser.close();
        if (serverProcess) serverProcess.kill();
    });
    
    describe('Core Web Vitals', () => {
        it('should meet performance metrics', async () => {
            const { lhr } = await lighthouse(BASE_URL, {
                port: (new URL(browser.wsEndpoint())).port,
                output: 'json',
                logLevel: 'error',
                onlyCategories: ['performance']
            });
            
            const metrics = {
                FCP: lhr.audits['first-contentful-paint'].numericValue,
                LCP: lhr.audits['largest-contentful-paint'].numericValue,
                CLS: lhr.audits['cumulative-layout-shift'].numericValue,
                TBT: lhr.audits['total-blocking-time'].numericValue
            };
            
            // Performance thresholds
            expect(metrics.FCP).toBeLessThan(1800); // 1.8s
            expect(metrics.LCP).toBeLessThan(2500); // 2.5s
            expect(metrics.CLS).toBeLessThan(0.1);  // 0.1
            expect(metrics.TBT).toBeLessThan(300);  // 300ms
            
            // Overall score
            expect(lhr.categories.performance.score).toBeGreaterThan(0.8);
        });
    });
    
    describe('Resource Loading', () => {
        let page;
        
        beforeEach(async () => {
            page = await browser.newPage();
            await page.setCacheEnabled(false);
        });
        
        afterEach(async () => {
            await page.close();
        });
        
        it('should load critical resources efficiently', async () => {
            const resourceTimings = [];
            
            page.on('response', response => {
                const url = response.url();
                const timing = response.timing();
                if (timing) {
                    resourceTimings.push({
                        url,
                        duration: timing.receiveHeadersEnd - timing.requestTime
                    });
                }
            });
            
            await page.goto(BASE_URL);
            await page.waitForSelector('.login-form');
            
            // Check critical resource loading times
            const cssFiles = resourceTimings.filter(r => r.url.endsWith('.css'));
            const jsFiles = resourceTimings.filter(r => r.url.endsWith('.js'));
            
            // CSS should load quickly
            cssFiles.forEach(file => {
                expect(file.duration).toBeLessThan(500);
            });
            
            // JS bundles should be reasonable size
            jsFiles.forEach(file => {
                expect(file.duration).toBeLessThan(1000);
            });
        });
        
        it('should implement resource hints', async () => {
            await page.goto(BASE_URL);
            
            // Check for preload hints
            const preloadLinks = await page.$$eval(
                'link[rel="preload"]',
                links => links.map(link => ({
                    href: link.href,
                    as: link.as
                }))
            );
            
            expect(preloadLinks.length).toBeGreaterThan(0);
            
            // Check for dns-prefetch
            const dnsPrefetch = await page.$$('link[rel="dns-prefetch"]');
            expect(dnsPrefetch.length).toBeGreaterThan(0);
        });
    });
    
    describe('JavaScript Performance', () => {
        let page;
        
        beforeEach(async () => {
            page = await browser.newPage();
        });
        
        afterEach(async () => {
            await page.close();
        });
        
        it('should minimize main thread blocking', async () => {
            const metrics = await page.evaluateOnNewDocument(() => {
                window.performanceMetrics = {
                    longTasks: []
                };
                
                new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        window.performanceMetrics.longTasks.push({
                            duration: entry.duration,
                            startTime: entry.startTime
                        });
                    }
                }).observe({ entryTypes: ['longtask'] });
            });
            
            await page.goto(BASE_URL);
            await page.waitForSelector('.login-form');
            
            // Interact with the page
            await page.type('#username', 'testuser');
            await page.type('#password', 'testpass');
            
            const longTasks = await page.evaluate(() => window.performanceMetrics.longTasks);
            
            // Should have minimal long tasks
            expect(longTasks.length).toBeLessThan(5);
            
            // No extremely long tasks
            longTasks.forEach(task => {
                expect(task.duration).toBeLessThan(200);
            });
        });
        
        it('should have efficient event handlers', async () => {
            await page.goto(BASE_URL);
            await page.waitForSelector('.login-form');
            
            // Measure input responsiveness
            const inputDelay = await page.evaluate(async () => {
                const input = document.querySelector('#username');
                const delays = [];
                
                for (let i = 0; i < 10; i++) {
                    const start = performance.now();
                    input.value += 'a';
                    input.dispatchEvent(new Event('input'));
                    await new Promise(resolve => requestAnimationFrame(resolve));
                    delays.push(performance.now() - start);
                }
                
                return delays;
            });
            
            // Input should be responsive
            const avgDelay = inputDelay.reduce((a, b) => a + b) / inputDelay.length;
            expect(avgDelay).toBeLessThan(16); // 60fps
        });
    });
    
    describe('Memory Management', () => {
        let page;
        
        beforeEach(async () => {
            page = await browser.newPage();
        });
        
        afterEach(async () => {
            await page.close();
        });
        
        it('should not have memory leaks', async () => {
            await page.goto(BASE_URL);
            await loginUser(page);
            
            // Get initial memory
            const initialMetrics = await page.metrics();
            const initialHeap = initialMetrics.JSHeapUsedSize;
            
            // Navigate through app multiple times
            for (let i = 0; i < 10; i++) {
                await page.goto(BASE_URL + '/packages');
                await page.waitForSelector('.package-search');
                await page.goto(BASE_URL + '/services');
                await page.waitForSelector('.services-list');
                await page.goto(BASE_URL + '/dashboard');
                await page.waitForSelector('.dashboard');
            }
            
            // Force garbage collection
            await page.evaluate(() => {
                if (window.gc) window.gc();
            });
            
            // Check memory hasn't grown excessively
            const finalMetrics = await page.metrics();
            const finalHeap = finalMetrics.JSHeapUsedSize;
            const heapGrowth = (finalHeap - initialHeap) / initialHeap;
            
            expect(heapGrowth).toBeLessThan(0.5); // Less than 50% growth
        });
        
        it('should clean up event listeners', async () => {
            await page.goto(BASE_URL);
            await loginUser(page);
            
            // Count event listeners
            const getListenerCount = () => page.evaluate(() => {
                let count = 0;
                const allElements = document.querySelectorAll('*');
                allElements.forEach(element => {
                    const listeners = getEventListeners(element);
                    Object.keys(listeners).forEach(event => {
                        count += listeners[event].length;
                    });
                });
                return count;
            });
            
            const initialCount = await getListenerCount();
            
            // Open and close modals multiple times
            for (let i = 0; i < 5; i++) {
                await page.click('.help-menu-button');
                await page.waitForSelector('.help-menu');
                await page.keyboard.press('Escape');
                await page.waitForSelector('.help-menu', { hidden: true });
            }
            
            const finalCount = await getListenerCount();
            
            // Listener count should not grow significantly
            expect(finalCount).toBeLessThan(initialCount * 1.2);
        });
    });
    
    describe('Network Performance', () => {
        let page;
        
        beforeEach(async () => {
            page = await browser.newPage();
        });
        
        afterEach(async () => {
            await page.close();
        });
        
        it('should minimize API calls', async () => {
            const apiCalls = [];
            
            page.on('request', request => {
                if (request.url().includes('/api/')) {
                    apiCalls.push({
                        url: request.url(),
                        method: request.method()
                    });
                }
            });
            
            await page.goto(BASE_URL);
            await loginUser(page);
            
            // Navigate to dashboard
            await page.goto(BASE_URL + '/dashboard');
            await page.waitForSelector('.dashboard');
            
            // Should batch API calls efficiently
            const duplicateCalls = apiCalls.filter((call, index) => 
                apiCalls.findIndex(c => c.url === call.url && c.method === call.method) !== index
            );
            
            expect(duplicateCalls.length).toBe(0);
        });
        
        it('should implement caching effectively', async () => {
            await page.setCacheEnabled(true);
            await page.goto(BASE_URL);
            await loginUser(page);
            
            const requests = [];
            page.on('request', request => {
                requests.push({
                    url: request.url(),
                    fromCache: request.response()?.fromCache() || false
                });
            });
            
            // Load dashboard twice
            await page.goto(BASE_URL + '/dashboard');
            await page.waitForSelector('.dashboard');
            
            requests.length = 0; // Clear first load
            
            await page.reload();
            await page.waitForSelector('.dashboard');
            
            // Many resources should be from cache
            const cachedRequests = requests.filter(r => r.fromCache);
            const cacheRatio = cachedRequests.length / requests.length;
            
            expect(cacheRatio).toBeGreaterThan(0.7); // 70% cache hit rate
        });
    });
    
    describe('Lazy Loading', () => {
        let page;
        
        beforeEach(async () => {
            page = await browser.newPage();
        });
        
        afterEach(async () => {
            await page.close();
        });
        
        it('should lazy load non-critical resources', async () => {
            const loadedChunks = new Set();
            
            page.on('response', response => {
                const url = response.url();
                if (url.includes('.chunk.js')) {
                    loadedChunks.add(url);
                }
            });
            
            await page.goto(BASE_URL);
            await loginUser(page);
            
            const initialChunks = loadedChunks.size;
            
            // Navigate to different sections
            await page.goto(BASE_URL + '/packages');
            await page.waitForSelector('.package-search');
            
            const afterPackages = loadedChunks.size;
            expect(afterPackages).toBeGreaterThan(initialChunks);
            
            // Open plugin manager
            await page.click('.menu-item[data-menu="tools"]');
            await page.waitForSelector('.submenu');
            await page.click('#open-plugin-manager');
            await page.waitForSelector('.plugin-manager-modal');
            
            const afterPlugins = loadedChunks.size;
            expect(afterPlugins).toBeGreaterThan(afterPackages);
        });
        
        it('should implement code splitting effectively', async () => {
            const bundleSizes = [];
            
            page.on('response', async response => {
                const url = response.url();
                if (url.endsWith('.js')) {
                    const buffer = await response.buffer();
                    bundleSizes.push({
                        url: url.split('/').pop(),
                        size: buffer.length
                    });
                }
            });
            
            await page.goto(BASE_URL);
            await page.waitForSelector('.login-form');
            
            // Main bundle should be reasonably sized
            const mainBundle = bundleSizes.find(b => b.url.includes('main'));
            expect(mainBundle.size).toBeLessThan(200 * 1024); // 200KB
            
            // Should have multiple smaller chunks
            const chunks = bundleSizes.filter(b => b.url.includes('chunk'));
            expect(chunks.length).toBeGreaterThan(3);
            
            // Chunks should be small
            chunks.forEach(chunk => {
                expect(chunk.size).toBeLessThan(100 * 1024); // 100KB
            });
        });
    });
    
    describe('Animation Performance', () => {
        let page;
        
        beforeEach(async () => {
            page = await browser.newPage();
            await page.setViewport({ width: 1280, height: 800 });
        });
        
        afterEach(async () => {
            await page.close();
        });
        
        it('should maintain 60fps during animations', async () => {
            await page.goto(BASE_URL);
            await loginUser(page);
            
            // Monitor frame rate
            const frameMetrics = await page.evaluate(async () => {
                const frames = [];
                let lastTime = performance.now();
                
                const measureFrames = () => {
                    const currentTime = performance.now();
                    const delta = currentTime - lastTime;
                    frames.push(1000 / delta); // FPS
                    lastTime = currentTime;
                    
                    if (frames.length < 60) {
                        requestAnimationFrame(measureFrames);
                    }
                };
                
                // Trigger animations
                const modal = document.createElement('div');
                modal.className = 'modal fade-in';
                document.body.appendChild(modal);
                
                requestAnimationFrame(measureFrames);
                
                // Wait for measurement
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                return frames;
            });
            
            // Calculate average FPS
            const avgFPS = frameMetrics.reduce((a, b) => a + b) / frameMetrics.length;
            expect(avgFPS).toBeGreaterThan(50);
            
            // Check for frame drops
            const droppedFrames = frameMetrics.filter(fps => fps < 30);
            expect(droppedFrames.length).toBeLessThan(5);
        });
    });
});

// Helper function
async function loginUser(page) {
    const isDashboard = await page.$('.dashboard');
    if (isDashboard) return;
    
    await page.waitForSelector('.login-form');
    await page.type('#username', 'testuser');
    await page.type('#password', 'testpass');
    await page.click('.login-button');
    await page.waitForSelector('.dashboard', { timeout: 10000 });
}