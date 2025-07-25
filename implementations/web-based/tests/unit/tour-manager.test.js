/**
 * Unit Tests for Tour Manager
 */

import { TourManager } from '../../js/tour-manager';

describe('TourManager', () => {
    let tourManager;
    let mockLocalStorage;
    
    beforeEach(() => {
        // Set up DOM
        document.body.innerHTML = `
            <div id="app">
                <header>
                    <nav class="main-nav">
                        <a href="/dashboard" class="nav-item">Dashboard</a>
                        <a href="/packages" class="nav-item">Packages</a>
                        <a href="/services" class="nav-item">Services</a>
                    </nav>
                </header>
                <main>
                    <div class="dashboard" id="dashboard">
                        <h1>Dashboard</h1>
                        <div class="stats-card">System Stats</div>
                    </div>
                    <div class="package-search" id="package-search" style="display:none;">
                        <input type="text" placeholder="Search packages..." />
                        <button class="search-button">Search</button>
                    </div>
                </main>
            </div>
        `;
        
        // Mock localStorage
        mockLocalStorage = {
            getItem: jest.fn(),
            setItem: jest.fn(),
            removeItem: jest.fn()
        };
        Object.defineProperty(window, 'localStorage', {
            value: mockLocalStorage,
            writable: true
        });
        
        // Mock window functions
        window.scrollTo = jest.fn();
        window.requestAnimationFrame = jest.fn(cb => setTimeout(cb, 0));
        
        tourManager = new TourManager();
    });
    
    afterEach(() => {
        jest.clearAllMocks();
        // Clean up tour elements
        document.querySelectorAll('.tour-overlay, .tour-step').forEach(el => el.remove());
    });
    
    describe('Tour Configuration', () => {
        it('should load default tours', () => {
            expect(tourManager.tours).toHaveProperty('welcome');
            expect(tourManager.tours).toHaveProperty('packages');
            expect(tourManager.tours).toHaveProperty('services');
        });
        
        it('should register custom tours', () => {
            const customTour = {
                id: 'custom',
                name: 'Custom Tour',
                steps: [
                    {
                        element: '.custom-element',
                        title: 'Custom Step',
                        content: 'This is a custom step'
                    }
                ]
            };
            
            tourManager.registerTour(customTour);
            
            expect(tourManager.tours.custom).toBeDefined();
            expect(tourManager.tours.custom.name).toBe('Custom Tour');
        });
        
        it('should validate tour structure', () => {
            const invalidTour = {
                id: 'invalid',
                // Missing required fields
            };
            
            expect(() => {
                tourManager.registerTour(invalidTour);
            }).toThrow('Invalid tour configuration');
        });
    });
    
    describe('Tour Lifecycle', () => {
        beforeEach(() => {
            tourManager.tours = {
                welcome: {
                    id: 'welcome',
                    name: 'Welcome Tour',
                    steps: [
                        {
                            element: '.dashboard',
                            title: 'Welcome to NixOS GUI',
                            content: 'This is your dashboard'
                        },
                        {
                            element: '.stats-card',
                            title: 'System Statistics',
                            content: 'View your system stats here'
                        }
                    ]
                }
            };
        });
        
        it('should start a tour', async () => {
            const started = await tourManager.startTour('welcome');
            
            expect(started).toBe(true);
            expect(tourManager.currentTour).toBe('welcome');
            expect(tourManager.currentStep).toBe(0);
            
            // Check overlay created
            const overlay = document.querySelector('.tour-overlay');
            expect(overlay).toBeTruthy();
            
            // Check step displayed
            const stepElement = document.querySelector('.tour-step');
            expect(stepElement).toBeTruthy();
            expect(stepElement.textContent).toContain('Welcome to NixOS GUI');
        });
        
        it('should handle missing tour', async () => {
            const started = await tourManager.startTour('nonexistent');
            
            expect(started).toBe(false);
            expect(tourManager.currentTour).toBeNull();
        });
        
        it('should end tour', async () => {
            await tourManager.startTour('welcome');
            
            tourManager.endTour();
            
            expect(tourManager.currentTour).toBeNull();
            expect(tourManager.currentStep).toBe(0);
            
            // Check elements removed
            const overlay = document.querySelector('.tour-overlay');
            const step = document.querySelector('.tour-step');
            expect(overlay).toBeFalsy();
            expect(step).toBeFalsy();
        });
    });
    
    describe('Step Navigation', () => {
        beforeEach(async () => {
            tourManager.tours = {
                multi: {
                    id: 'multi',
                    name: 'Multi-step Tour',
                    steps: [
                        {
                            element: '.dashboard',
                            title: 'Step 1',
                            content: 'First step'
                        },
                        {
                            element: '.stats-card',
                            title: 'Step 2',
                            content: 'Second step'
                        },
                        {
                            element: '.main-nav',
                            title: 'Step 3',
                            content: 'Third step'
                        }
                    ]
                }
            };
            
            await tourManager.startTour('multi');
        });
        
        it('should navigate to next step', () => {
            expect(tourManager.currentStep).toBe(0);
            
            tourManager.nextStep();
            
            expect(tourManager.currentStep).toBe(1);
            const stepElement = document.querySelector('.tour-step');
            expect(stepElement.textContent).toContain('Step 2');
        });
        
        it('should navigate to previous step', () => {
            tourManager.nextStep();
            tourManager.nextStep();
            expect(tourManager.currentStep).toBe(2);
            
            tourManager.previousStep();
            
            expect(tourManager.currentStep).toBe(1);
            const stepElement = document.querySelector('.tour-step');
            expect(stepElement.textContent).toContain('Step 2');
        });
        
        it('should end tour at last step', () => {
            tourManager.nextStep();
            tourManager.nextStep();
            
            // Should be on last step
            expect(tourManager.currentStep).toBe(2);
            
            // Next should end tour
            tourManager.nextStep();
            
            expect(tourManager.currentTour).toBeNull();
        });
        
        it('should go to specific step', () => {
            tourManager.goToStep(2);
            
            expect(tourManager.currentStep).toBe(2);
            const stepElement = document.querySelector('.tour-step');
            expect(stepElement.textContent).toContain('Step 3');
        });
    });
    
    describe('Step Positioning', () => {
        beforeEach(() => {
            // Mock getBoundingClientRect
            Element.prototype.getBoundingClientRect = jest.fn(function() {
                if (this.classList.contains('dashboard')) {
                    return {
                        top: 100,
                        left: 50,
                        bottom: 300,
                        right: 500,
                        width: 450,
                        height: 200
                    };
                }
                return {
                    top: 0,
                    left: 0,
                    bottom: 100,
                    right: 100,
                    width: 100,
                    height: 100
                };
            });
            
            // Mock window dimensions
            Object.defineProperty(window, 'innerHeight', {
                value: 800,
                writable: true
            });
            Object.defineProperty(window, 'innerWidth', {
                value: 1200,
                writable: true
            });
        });
        
        it('should position step near target element', async () => {
            tourManager.tours = {
                position: {
                    id: 'position',
                    name: 'Position Test',
                    steps: [{
                        element: '.dashboard',
                        title: 'Test',
                        content: 'Test positioning',
                        position: 'bottom'
                    }]
                }
            };
            
            await tourManager.startTour('position');
            
            const step = document.querySelector('.tour-step');
            const style = window.getComputedStyle(step);
            
            // Should be positioned below the element
            expect(parseInt(style.top)).toBeGreaterThan(300);
        });
        
        it('should adjust position near viewport edges', async () => {
            // Mock element near bottom
            Element.prototype.getBoundingClientRect = jest.fn(() => ({
                top: 700,
                left: 100,
                bottom: 750,
                right: 200,
                width: 100,
                height: 50
            }));
            
            tourManager.tours = {
                edge: {
                    id: 'edge',
                    name: 'Edge Test',
                    steps: [{
                        element: '.dashboard',
                        title: 'Test',
                        content: 'Test edge positioning',
                        position: 'bottom'
                    }]
                }
            };
            
            await tourManager.startTour('edge');
            
            const step = document.querySelector('.tour-step');
            // Should be positioned above when too close to bottom
            expect(step.classList.contains('position-top')).toBe(true);
        });
    });
    
    describe('Tour Progress', () => {
        beforeEach(() => {
            tourManager.tours = {
                progress: {
                    id: 'progress',
                    name: 'Progress Tour',
                    steps: Array(5).fill(null).map((_, i) => ({
                        element: '.dashboard',
                        title: `Step ${i + 1}`,
                        content: `Content ${i + 1}`
                    }))
                }
            };
        });
        
        it('should show progress indicator', async () => {
            await tourManager.startTour('progress');
            
            const progress = document.querySelector('.tour-progress');
            expect(progress).toBeTruthy();
            expect(progress.textContent).toContain('1 of 5');
        });
        
        it('should update progress on navigation', async () => {
            await tourManager.startTour('progress');
            
            tourManager.nextStep();
            tourManager.nextStep();
            
            const progress = document.querySelector('.tour-progress');
            expect(progress.textContent).toContain('3 of 5');
        });
        
        it('should show progress dots', async () => {
            await tourManager.startTour('progress');
            
            const dots = document.querySelectorAll('.tour-progress-dot');
            expect(dots.length).toBe(5);
            expect(dots[0].classList.contains('active')).toBe(true);
            
            tourManager.nextStep();
            
            expect(dots[0].classList.contains('active')).toBe(false);
            expect(dots[1].classList.contains('active')).toBe(true);
        });
    });
    
    describe('Tour Persistence', () => {
        it('should save tour progress', async () => {
            await tourManager.startTour('welcome');
            tourManager.nextStep();
            
            expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
                'tour_progress',
                expect.stringContaining('"welcome"')
            );
        });
        
        it('should resume tour from saved progress', async () => {
            mockLocalStorage.getItem.mockReturnValue(
                JSON.stringify({
                    tourId: 'welcome',
                    step: 1,
                    completed: []
                })
            );
            
            tourManager.resumeTour();
            
            expect(tourManager.currentTour).toBe('welcome');
            expect(tourManager.currentStep).toBe(1);
        });
        
        it('should track completed tours', async () => {
            await tourManager.startTour('welcome');
            
            // Complete tour
            while (tourManager.currentTour) {
                tourManager.nextStep();
            }
            
            expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
                'completed_tours',
                expect.stringContaining('"welcome"')
            );
        });
        
        it('should not auto-start completed tours', async () => {
            mockLocalStorage.getItem.mockImplementation(key => {
                if (key === 'completed_tours') {
                    return JSON.stringify(['welcome']);
                }
                return null;
            });
            
            const started = await tourManager.autoStart('welcome');
            
            expect(started).toBe(false);
        });
    });
    
    describe('Tour Actions', () => {
        it('should execute step actions', async () => {
            const actionSpy = jest.fn();
            
            tourManager.tours = {
                actions: {
                    id: 'actions',
                    name: 'Actions Tour',
                    steps: [{
                        element: '.dashboard',
                        title: 'Action Step',
                        content: 'Step with action',
                        onShow: actionSpy
                    }]
                }
            };
            
            await tourManager.startTour('actions');
            
            expect(actionSpy).toHaveBeenCalledWith(
                document.querySelector('.dashboard')
            );
        });
        
        it('should handle step validation', async () => {
            tourManager.tours = {
                validation: {
                    id: 'validation',
                    name: 'Validation Tour',
                    steps: [
                        {
                            element: '.dashboard',
                            title: 'Step 1',
                            content: 'First step',
                            canProceed: () => false
                        },
                        {
                            element: '.stats-card',
                            title: 'Step 2',
                            content: 'Second step'
                        }
                    ]
                }
            };
            
            await tourManager.startTour('validation');
            
            const nextButton = document.querySelector('.tour-next');
            expect(nextButton.disabled).toBe(true);
            
            // Update validation
            tourManager.tours.validation.steps[0].canProceed = () => true;
            tourManager.updateStep();
            
            expect(nextButton.disabled).toBe(false);
        });
    });
    
    describe('Tour Customization', () => {
        it('should apply custom themes', async () => {
            tourManager.tours = {
                themed: {
                    id: 'themed',
                    name: 'Themed Tour',
                    theme: 'dark',
                    steps: [{
                        element: '.dashboard',
                        title: 'Dark Theme',
                        content: 'Dark themed tour'
                    }]
                }
            };
            
            await tourManager.startTour('themed');
            
            const overlay = document.querySelector('.tour-overlay');
            const step = document.querySelector('.tour-step');
            
            expect(overlay.classList.contains('theme-dark')).toBe(true);
            expect(step.classList.contains('theme-dark')).toBe(true);
        });
        
        it('should support custom controls', async () => {
            tourManager.tours = {
                custom: {
                    id: 'custom',
                    name: 'Custom Controls',
                    showSkip: false,
                    showProgress: false,
                    steps: [{
                        element: '.dashboard',
                        title: 'Custom',
                        content: 'Custom controls',
                        buttons: {
                            next: 'Continue',
                            previous: 'Go Back'
                        }
                    }]
                }
            };
            
            await tourManager.startTour('custom');
            
            const skipButton = document.querySelector('.tour-skip');
            const progress = document.querySelector('.tour-progress');
            const nextButton = document.querySelector('.tour-next');
            
            expect(skipButton).toBeFalsy();
            expect(progress).toBeFalsy();
            expect(nextButton.textContent).toBe('Continue');
        });
    });
    
    describe('Keyboard Navigation', () => {
        beforeEach(async () => {
            await tourManager.startTour('welcome');
        });
        
        it('should navigate with arrow keys', () => {
            const event = new KeyboardEvent('keydown', { key: 'ArrowRight' });
            document.dispatchEvent(event);
            
            expect(tourManager.currentStep).toBe(1);
            
            const leftEvent = new KeyboardEvent('keydown', { key: 'ArrowLeft' });
            document.dispatchEvent(leftEvent);
            
            expect(tourManager.currentStep).toBe(0);
        });
        
        it('should close with Escape key', () => {
            const event = new KeyboardEvent('keydown', { key: 'Escape' });
            document.dispatchEvent(event);
            
            expect(tourManager.currentTour).toBeNull();
        });
        
        it('should skip with s key', () => {
            const endSpy = jest.spyOn(tourManager, 'endTour');
            
            const event = new KeyboardEvent('keydown', { key: 's' });
            document.dispatchEvent(event);
            
            expect(endSpy).toHaveBeenCalled();
        });
    });
    
    describe('Tour Analytics', () => {
        it('should track tour events', async () => {
            const trackingSpy = jest.fn();
            tourManager.setAnalytics(trackingSpy);
            
            await tourManager.startTour('welcome');
            
            expect(trackingSpy).toHaveBeenCalledWith('tour_started', {
                tourId: 'welcome',
                totalSteps: 2
            });
            
            tourManager.nextStep();
            
            expect(trackingSpy).toHaveBeenCalledWith('tour_step', {
                tourId: 'welcome',
                step: 1,
                totalSteps: 2
            });
            
            tourManager.endTour();
            
            expect(trackingSpy).toHaveBeenCalledWith('tour_ended', {
                tourId: 'welcome',
                completed: false,
                lastStep: 1
            });
        });
    });
});