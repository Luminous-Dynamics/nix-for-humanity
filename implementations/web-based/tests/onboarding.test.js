/**
 * Onboarding Wizard Tests
 */

import { OnboardingWizard } from '../js/onboarding-wizard';

describe('OnboardingWizard', () => {
    let wizard;
    let mockLocalStorage;

    beforeEach(() => {
        // Mock DOM
        document.body.innerHTML = '';
        
        // Mock localStorage
        mockLocalStorage = {
            data: {},
            getItem: jest.fn((key) => mockLocalStorage.data[key]),
            setItem: jest.fn((key, value) => {
                mockLocalStorage.data[key] = value;
            }),
            removeItem: jest.fn((key) => {
                delete mockLocalStorage.data[key];
            })
        };
        
        Object.defineProperty(window, 'localStorage', {
            value: mockLocalStorage,
            writable: true
        });

        // Mock authManager
        window.authManager = {
            accessToken: 'test-token'
        };

        wizard = new OnboardingWizard();
    });

    afterEach(() => {
        document.body.innerHTML = '';
        jest.clearAllMocks();
    });

    describe('Initialization', () => {
        test('should create wizard instance', () => {
            expect(wizard).toBeDefined();
            expect(wizard.currentStep).toBe(0);
            expect(wizard.completed).toBe(false);
            expect(wizard.steps).toHaveLength(5);
        });

        test('should not start if already completed', async () => {
            mockLocalStorage.data['nixos-gui-onboarding-completed'] = 'true';
            
            await wizard.start();
            
            expect(document.querySelector('.onboarding-modal')).toBeNull();
        });

        test('should start if not completed', async () => {
            await wizard.start();
            
            const modal = document.querySelector('.onboarding-modal');
            expect(modal).toBeTruthy();
            expect(modal.classList.contains('active')).toBe(true);
        });

        test('should start if forced via URL parameter', async () => {
            mockLocalStorage.data['nixos-gui-onboarding-completed'] = 'true';
            
            // Mock URL params
            delete window.location;
            window.location = { search: '?onboarding=true' };
            
            await wizard.start();
            
            expect(document.querySelector('.onboarding-modal')).toBeTruthy();
        });
    });

    describe('Navigation', () => {
        beforeEach(async () => {
            await wizard.start();
        });

        test('should navigate to next step', async () => {
            expect(wizard.currentStep).toBe(0);
            
            await wizard.nextStep();
            
            expect(wizard.currentStep).toBe(1);
        });

        test('should navigate to previous step', () => {
            wizard.currentStep = 2;
            wizard.previousStep();
            
            expect(wizard.currentStep).toBe(1);
        });

        test('should not go back from first step', () => {
            wizard.currentStep = 0;
            wizard.previousStep();
            
            expect(wizard.currentStep).toBe(0);
        });

        test('should disable back button on first step', () => {
            wizard.render();
            
            const backBtn = document.getElementById('onboarding-back');
            expect(backBtn.disabled).toBe(true);
        });

        test('should change next button to finish on last step', () => {
            wizard.currentStep = wizard.steps.length - 1;
            wizard.render();
            
            const nextBtn = document.getElementById('onboarding-next');
            expect(nextBtn.textContent).toBe('Finish');
        });
    });

    describe('Progress', () => {
        beforeEach(async () => {
            await wizard.start();
        });

        test('should update progress bar', () => {
            const progressFill = document.querySelector('.progress-fill');
            
            // First step (20%)
            expect(progressFill.style.width).toBe('20%');
            
            // Move to step 3 (60%)
            wizard.currentStep = 2;
            wizard.render();
            expect(progressFill.style.width).toBe('60%');
        });

        test('should update step indicator', () => {
            const indicator = document.querySelector('.step-indicator');
            
            expect(indicator.textContent).toBe('Step 1 of 5');
            
            wizard.currentStep = 3;
            wizard.render();
            expect(indicator.textContent).toBe('Step 4 of 5');
        });
    });

    describe('Skip functionality', () => {
        beforeEach(async () => {
            await wizard.start();
        });

        test('should confirm before skipping', () => {
            window.confirm = jest.fn(() => false);
            
            wizard.skip();
            
            expect(window.confirm).toHaveBeenCalledWith(
                'Are you sure you want to skip the setup wizard? You can run it again from the help menu.'
            );
            expect(document.querySelector('.onboarding-modal')).toBeTruthy();
        });

        test('should close wizard when skip is confirmed', () => {
            window.confirm = jest.fn(() => true);
            
            wizard.skip();
            
            expect(wizard.modal.classList.contains('active')).toBe(false);
        });
    });

    describe('Preferences', () => {
        beforeEach(async () => {
            await wizard.start();
            wizard.currentStep = 2; // Preferences step
            wizard.render();
        });

        test('should save theme preference', () => {
            const darkRadio = document.querySelector('input[name="theme"][value="dark"]');
            darkRadio.checked = true;
            
            wizard.saveStepData();
            
            expect(wizard.preferences.theme).toBe('dark');
        });

        test('should save notification preference', () => {
            const notifCheckbox = document.getElementById('notifications-enabled');
            notifCheckbox.checked = false;
            
            wizard.saveStepData();
            
            expect(wizard.preferences.notifications).toBe(false);
        });

        test('should save auto-update preference', () => {
            const autoUpdateCheckbox = document.getElementById('auto-update');
            autoUpdateCheckbox.checked = true;
            
            wizard.saveStepData();
            
            expect(wizard.preferences.autoUpdate).toBe(true);
        });
    });

    describe('Permissions validation', () => {
        beforeEach(async () => {
            await wizard.start();
            wizard.currentStep = 1; // Permissions step
            wizard.render();
        });

        test('should validate permissions successfully', async () => {
            global.fetch = jest.fn(() =>
                Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({
                        hasAllPermissions: true
                    })
                })
            );
            
            const result = await wizard.validatePermissions();
            
            expect(result).toBe(true);
            expect(document.querySelector('.permission-list').style.display).toBe('block');
        });

        test('should handle missing permissions', async () => {
            global.fetch = jest.fn(() =>
                Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({
                        hasAllPermissions: false
                    })
                })
            );
            
            const result = await wizard.validatePermissions();
            
            expect(result).toBe(false);
            expect(document.querySelector('.permission-error').style.display).toBe('block');
        });

        test('should handle permission check error', async () => {
            global.fetch = jest.fn(() => Promise.reject(new Error('Network error')));
            
            const result = await wizard.validatePermissions();
            
            expect(result).toBe(false);
            expect(document.getElementById('permission-status').textContent).toContain('Failed to check permissions');
        });
    });

    describe('Completion', () => {
        beforeEach(async () => {
            await wizard.start();
            global.fetch = jest.fn(() =>
                Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({})
                })
            );
        });

        test('should save preferences on completion', async () => {
            wizard.preferences = {
                theme: 'dark',
                notifications: true,
                autoUpdate: false
            };
            
            await wizard.complete();
            
            expect(global.fetch).toHaveBeenCalledWith('/api/user/preferences', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer test-token'
                },
                body: JSON.stringify(wizard.preferences)
            });
        });

        test('should mark as completed in localStorage', async () => {
            await wizard.complete();
            
            expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
                'nixos-gui-onboarding-completed',
                'true'
            );
        });

        test('should show success message', async () => {
            await wizard.complete();
            
            const successMsg = document.querySelector('.success-message');
            expect(successMsg).toBeTruthy();
            expect(successMsg.textContent).toContain('Setup complete!');
        });

        test('should set completed flag', async () => {
            expect(wizard.completed).toBe(false);
            
            await wizard.complete();
            
            expect(wizard.completed).toBe(true);
        });
    });

    describe('Keyboard navigation', () => {
        beforeEach(async () => {
            await wizard.start();
        });

        test('should navigate with Enter key', () => {
            const event = new KeyboardEvent('keydown', { key: 'Enter' });
            wizard.nextStep = jest.fn();
            
            wizard.handleKeyboard(event);
            
            expect(wizard.nextStep).toHaveBeenCalled();
        });

        test('should not navigate with Enter on buttons', () => {
            const event = new KeyboardEvent('keydown', { 
                key: 'Enter',
                target: { type: 'button' }
            });
            wizard.nextStep = jest.fn();
            
            wizard.handleKeyboard(event);
            
            expect(wizard.nextStep).not.toHaveBeenCalled();
        });

        test('should skip with Escape key', () => {
            const event = new KeyboardEvent('keydown', { key: 'Escape' });
            wizard.skip = jest.fn();
            
            wizard.handleKeyboard(event);
            
            expect(wizard.skip).toHaveBeenCalled();
        });
    });

    describe('Step content', () => {
        beforeEach(async () => {
            await wizard.start();
        });

        test('should render welcome step', () => {
            const content = wizard.renderWelcomeStep();
            
            expect(content).toContain('Welcome to NixOS GUI');
            expect(content).toContain('Package Management');
            expect(content).toContain('System Configuration');
        });

        test('should render permissions step', () => {
            const content = wizard.renderPermissionsStep();
            
            expect(content).toContain('System Permissions');
            expect(content).toContain('User Groups');
            expect(content).toContain('Polkit Rules');
        });

        test('should render preferences step', () => {
            const content = wizard.renderPreferencesStep();
            
            expect(content).toContain('Your Preferences');
            expect(content).toContain('Theme');
            expect(content).toContain('Notifications');
        });

        test('should render features step', () => {
            const content = wizard.renderFeaturesStep();
            
            expect(content).toContain('Key Features');
            expect(content).toContain('Quick Search');
            expect(content).toContain('Keyboard Shortcuts');
        });

        test('should render complete step', () => {
            const content = wizard.renderCompleteStep();
            
            expect(content).toContain('You\'re All Set!');
            expect(content).toContain('What would you like to do first?');
        });
    });
});