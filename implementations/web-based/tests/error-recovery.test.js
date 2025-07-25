/**
 * Error Recovery Integration Tests
 * Tests the error handling system with real-world scenarios
 */

const puppeteer = require('puppeteer');
const axios = require('axios');
const { TestEnvironment, NetworkHelpers, WaitHelpers } = require('./test-helpers');

describe('Error Recovery System', () => {
    let browser;
    let page;
    let testEnv;
    let serverProcess;
    const baseURL = 'http://localhost:18891';

    beforeAll(async () => {
        testEnv = new TestEnvironment();
        await testEnv.setup();

        // Start test server
        serverProcess = require('child_process').spawn('node', [
            '../backend/real-backend.js'
        ], {
            env: { ...process.env, PORT: '18891', WS_PORT: '18892' },
            cwd: __dirname
        });

        // Wait for server
        await NetworkHelpers.waitForServer(`${baseURL}/api/health`);

        // Launch browser
        browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
    });

    afterAll(async () => {
        if (browser) await browser.close();
        if (serverProcess) serverProcess.kill();
        await testEnv.teardown();
    });

    beforeEach(async () => {
        page = await browser.newPage();
        await page.goto(`${baseURL}/index.html`);
        
        // Wait for app to load
        await page.waitForSelector('.app-container', { timeout: 5000 });
    });

    afterEach(async () => {
        if (page) await page.close();
    });

    describe('Network Error Recovery', () => {
        test('should detect and offer recovery for network errors', async () => {
            // Intercept network requests
            await page.setRequestInterception(true);
            
            page.on('request', (request) => {
                if (request.url().includes('/api/nix/search')) {
                    request.abort('failed');
                } else {
                    request.continue();
                }
            });

            // Trigger a search that will fail
            await page.type('#search-input', 'firefox');
            await page.click('#search-button');

            // Wait for error dialog
            await page.waitForSelector('.error-dialog', { timeout: 5000 });

            // Check error message
            const errorMessage = await page.$eval('.error-message', el => el.textContent);
            expect(errorMessage).toContain('network');

            // Check recovery options
            const recoveryOptions = await page.$$eval('.strategy-btn', 
                buttons => buttons.map(btn => btn.textContent)
            );
            
            expect(recoveryOptions).toContain('Check Internet Connection');
            expect(recoveryOptions).toContain('Retry Operation');
            expect(recoveryOptions).toContain('Use Offline Mode');

            // Try retry operation
            await page.setRequestInterception(false);
            await page.click('.strategy-btn:first-child');
            
            // Should show success
            await page.waitForSelector('.strategy-result.success', { timeout: 5000 });
        });

        test('should handle complete network failure gracefully', async () => {
            // Kill the backend server
            serverProcess.kill();
            
            // Try to search
            await page.type('#search-input', 'test');
            await page.click('#search-button');

            // Should show error dialog
            await page.waitForSelector('.error-dialog', { timeout: 5000 });
            
            // Should suggest checking connection
            const suggestions = await page.$eval('.error-suggestion', el => el.textContent);
            expect(suggestions).toContain('connection');
        });
    });

    describe('Package Not Found Recovery', () => {
        test('should suggest similar packages for typos', async () => {
            // Search for misspelled package
            await page.type('#search-input', 'fierfoxx'); // Misspelled firefox
            await page.click('#search-button');

            // If no results, try to install anyway
            await page.click('#install-button');

            // Wait for error
            await page.waitForSelector('.error-dialog', { timeout: 10000 });

            // Should offer to search similar
            const recoveryOptions = await page.$$eval('.strategy-btn',
                buttons => buttons.map(btn => btn.textContent)
            );
            
            expect(recoveryOptions).toContain('Search Similar Packages');

            // Click search similar
            const searchSimilarBtn = await page.$('.strategy-btn');
            await searchSimilarBtn.click();

            // Should show suggestions
            await page.waitForSelector('.result-suggestions', { timeout: 5000 });
            const suggestions = await page.$eval('.result-suggestions', el => el.textContent);
            expect(suggestions).toContain('firefox');
        });

        test('should provide helpful tips for package naming', async () => {
            // Try to install a package with wrong naming convention
            await page.evaluate(() => {
                window.errorHandler.handleError(
                    new Error('Package not found: python-3.11'),
                    'install',
                    { packageName: 'python-3.11' }
                );
            });

            await page.waitForSelector('.error-dialog');

            // Click "Check Package Name" strategy
            const buttons = await page.$$('.strategy-btn');
            for (const button of buttons) {
                const text = await button.evaluate(el => el.textContent);
                if (text.includes('Check Package Name')) {
                    await button.click();
                    break;
                }
            }

            // Should show naming tips
            await page.waitForSelector('.result-tips');
            const tips = await page.$eval('.result-tips', el => el.textContent);
            expect(tips).toContain('case-sensitive');
            expect(tips).toContain('version numbers');
        });
    });

    describe('Permission Error Recovery', () => {
        test('should suggest sudo for system operations', async () => {
            // Try system package installation
            await page.evaluate(() => {
                window.errorHandler.handleError(
                    new Error('Permission denied: /nix/store'),
                    'install',
                    { originalCommand: 'nix-env -i firefox' }
                );
            });

            await page.waitForSelector('.error-dialog');

            // Should show permission error
            const errorTitle = await page.$eval('.error-header h2', el => el.textContent);
            expect(errorTitle).toContain('Permission Error');

            // Should suggest sudo
            const buttons = await page.$$('.strategy-btn');
            const sudoButton = buttons.find(async (btn) => {
                const text = await btn.evaluate(el => el.textContent);
                return text.includes('Use Sudo');
            });
            expect(sudoButton).toBeDefined();

            // Click sudo suggestion
            await sudoButton.click();
            
            // Should show sudo command
            await page.waitForSelector('.result-command');
            const command = await page.$eval('.result-command code', el => el.textContent);
            expect(command).toContain('sudo');
        });
    });

    describe('Disk Space Error Recovery', () => {
        test('should provide cleanup commands for disk space', async () => {
            // Simulate disk space error
            await page.evaluate(() => {
                window.errorHandler.handleError(
                    new Error('No space left on device'),
                    'install'
                );
            });

            await page.waitForSelector('.error-dialog');

            // Click "Clean Nix Store" strategy
            const cleanButton = await page.$('.strategy-btn');
            await cleanButton.click();

            // Should show cleanup commands
            await page.waitForSelector('.result-commands');
            const commands = await page.$$eval('.result-command code',
                codes => codes.map(code => code.textContent)
            );
            
            expect(commands).toContain('nix-collect-garbage -d');
            expect(commands).toContain('nix-store --optimize');

            // Test copy button
            const copyButton = await page.$('.result-command button');
            await copyButton.click();
            
            // Check clipboard (in real browser)
            // const clipboard = await page.evaluate(() => navigator.clipboard.readText());
            // expect(clipboard).toContain('nix-collect-garbage');
        });
    });

    describe('Configuration Error Recovery', () => {
        test('should offer rollback for configuration errors', async () => {
            // Simulate configuration error
            await page.evaluate(() => {
                window.errorHandler.handleError(
                    new Error('error: syntax error, unexpected end of file'),
                    'rebuild',
                    { file: '/etc/nixos/configuration.nix' }
                );
            });

            await page.waitForSelector('.error-dialog');

            // Should identify as configuration error
            const errorTitle = await page.$eval('.error-header h2', el => el.textContent);
            expect(errorTitle).toContain('Configuration Error');

            // Should offer rollback
            const recoveryOptions = await page.$$eval('.strategy-btn',
                buttons => buttons.map(btn => btn.textContent)
            );
            
            expect(recoveryOptions).toContain('Restore Previous Config');
            expect(recoveryOptions).toContain('Validate Configuration');
            expect(recoveryOptions).toContain('Check Syntax');

            // Click validate
            const validateBtn = await page.$x("//button[contains(text(), 'Validate')]")[0];
            await validateBtn.click();

            // Should show validation command
            await page.waitForSelector('.result-command');
            const command = await page.$eval('.result-command code', el => el.textContent);
            expect(command).toContain('nixos-rebuild dry-build');
        });
    });

    describe('Error History', () => {
        test('should track and display error history', async () => {
            // Generate multiple errors
            const errors = [
                { message: 'Network error 1', source: 'api' },
                { message: 'Package not found', source: 'install' },
                { message: 'Permission denied', source: 'service' }
            ];

            for (const error of errors) {
                await page.evaluate((err) => {
                    window.errorHandler.handleError(
                        new Error(err.message),
                        err.source
                    );
                }, error);
                
                // Close each error dialog
                await page.waitForSelector('.error-dialog');
                await page.click('.close-btn');
                await page.waitForSelector('.error-dialog', { hidden: true });
            }

            // Open error history
            await page.evaluate(() => {
                window.errorHandler.showErrorHistory();
            });

            await page.waitForSelector('.error-history-dialog');

            // Check all errors are listed
            const historyEntries = await page.$$('.history-entry');
            expect(historyEntries.length).toBe(3);

            // Check error messages
            const messages = await page.$$eval('.entry-message',
                elements => elements.map(el => el.textContent)
            );
            
            expect(messages).toContain('Network error 1');
            expect(messages).toContain('Package not found');
            expect(messages).toContain('Permission denied');

            // Test export functionality
            await page.click('button:has-text("Export History")');
            // In real browser, this would trigger download
        });

        test('should persist error history across sessions', async () => {
            // Create an error
            await page.evaluate(() => {
                window.errorHandler.handleError(
                    new Error('Persistent error test'),
                    'test'
                );
            });

            // Reload page
            await page.reload();
            await page.waitForSelector('.app-container');

            // Check history is still there
            await page.evaluate(() => {
                window.errorHandler.showErrorHistory();
            });

            await page.waitForSelector('.error-history-dialog');
            const messages = await page.$$eval('.entry-message',
                elements => elements.map(el => el.textContent)
            );
            
            expect(messages).toContain('Persistent error test');
        });
    });

    describe('Error Recovery UX', () => {
        test('should show loading state during recovery', async () => {
            // Trigger error with recovery
            await page.evaluate(() => {
                window.errorHandler.handleError(
                    new Error('Test error'),
                    'test'
                );
            });

            await page.waitForSelector('.error-dialog');

            // Mock slow recovery action
            await page.evaluate(() => {
                const originalAction = window.errorHandler.recoveryStrategies.get('generic')
                    .strategies[0].action;
                
                window.errorHandler.recoveryStrategies.get('generic')
                    .strategies[0].action = async () => {
                        await new Promise(resolve => setTimeout(resolve, 2000));
                        return originalAction();
                    };
            });

            // Click recovery button
            const button = await page.$('.strategy-btn');
            await button.click();

            // Should show loading state
            await page.waitForSelector('.strategy-result.loading');
            const loadingText = await page.$eval('.loading', el => el.textContent);
            expect(loadingText).toContain('Working');

            // Should eventually complete
            await page.waitForSelector('.strategy-result.success', { timeout: 5000 });
        });

        test('should handle recovery failure gracefully', async () => {
            // Create error with failing recovery
            await page.evaluate(() => {
                window.errorHandler.addRecoveryStrategy('test-fail', {
                    canRecover: () => true,
                    strategies: [{
                        name: 'Failing Recovery',
                        action: async () => {
                            throw new Error('Recovery failed');
                        }
                    }]
                });

                window.errorHandler.handleError(
                    new Error('Test error'),
                    'test'
                );
            });

            await page.waitForSelector('.error-dialog');

            // Click failing recovery
            const button = await page.$x("//button[contains(text(), 'Failing Recovery')]")[0];
            await button.click();

            // Should show failure state
            await page.waitForSelector('.strategy-result.failure');
            const failureText = await page.$eval('.strategy-result.failure', el => el.textContent);
            expect(failureText).toContain('Strategy execution failed');
        });
    });
});