/**
 * Unit Tests for Error Handler
 */

import { ErrorHandler } from '../../js/error-handler';

describe('ErrorHandler', () => {
    let errorHandler;
    let mockShowNotification;
    
    beforeEach(() => {
        errorHandler = new ErrorHandler();
        
        // Mock window functions
        mockShowNotification = jest.fn();
        window.showNotification = mockShowNotification;
        
        // Mock console methods
        console.error = jest.fn();
        console.warn = jest.fn();
        
        // Mock DOM elements
        document.body.innerHTML = `
            <div id="error-container"></div>
            <div id="status" class="hidden">
                <span id="statusText"></span>
            </div>
        `;
    });
    
    afterEach(() => {
        jest.clearAllMocks();
    });
    
    describe('Error Handling', () => {
        it('should handle generic errors', () => {
            const error = new Error('Test error');
            
            errorHandler.handleError(error);
            
            expect(console.error).toHaveBeenCalledWith('Error:', error);
            expect(mockShowNotification).toHaveBeenCalledWith({
                message: expect.stringContaining('An error occurred'),
                type: 'error',
                duration: 5000
            });
        });
        
        it('should handle network errors', () => {
            const error = new Error('Network request failed');
            
            errorHandler.handleError(error);
            
            const notification = mockShowNotification.mock.calls[0][0];
            expect(notification.message).toContain('Network error');
            expect(notification.actions).toBeDefined();
        });
        
        it('should handle authentication errors', () => {
            const error = new Error('401');
            error.code = 'UNAUTHORIZED';
            
            errorHandler.handleError(error);
            
            const notification = mockShowNotification.mock.calls[0][0];
            expect(notification.message).toContain('session has expired');
            expect(notification.actions[0].label).toBe('Login');
        });
        
        it('should handle validation errors', () => {
            const error = {
                code: 'VALIDATION_ERROR',
                message: 'Invalid input',
                details: {
                    field: 'username',
                    reason: 'Username is required'
                }
            };
            
            errorHandler.handleError(error);
            
            expect(mockShowNotification).toHaveBeenCalledWith({
                message: 'Invalid input: Username is required',
                type: 'error',
                duration: 5000
            });
        });
        
        it('should handle rate limit errors', () => {
            const error = {
                code: 'RATE_LIMITED',
                retryAfter: 60
            };
            
            errorHandler.handleError(error);
            
            const notification = mockShowNotification.mock.calls[0][0];
            expect(notification.message).toContain('Too many requests');
            expect(notification.message).toContain('60 seconds');
        });
    });
    
    describe('Error Context', () => {
        it('should include context in error messages', () => {
            const error = new Error('Failed to load');
            const context = { operation: 'package.install', package: 'vim' };
            
            errorHandler.handleError(error, context);
            
            expect(console.error).toHaveBeenCalledWith('Error:', error, 'Context:', context);
        });
        
        it('should handle package installation errors', () => {
            const error = new Error('Installation failed');
            const context = { operation: 'package.install', package: 'firefox' };
            
            errorHandler.handleError(error, context);
            
            const notification = mockShowNotification.mock.calls[0][0];
            expect(notification.message).toContain('Failed to install firefox');
        });
        
        it('should handle service management errors', () => {
            const error = new Error('Service operation failed');
            const context = { operation: 'service.start', service: 'nginx' };
            
            errorHandler.handleError(error, context);
            
            const notification = mockShowNotification.mock.calls[0][0];
            expect(notification.message).toContain('Failed to start nginx');
        });
    });
    
    describe('Recovery Suggestions', () => {
        it('should suggest recovery for network errors', () => {
            const error = new Error('Network request failed');
            
            errorHandler.handleError(error);
            
            const notification = mockShowNotification.mock.calls[0][0];
            const retryAction = notification.actions.find(a => a.label === 'Retry');
            expect(retryAction).toBeDefined();
        });
        
        it('should suggest recovery for permission errors', () => {
            const error = {
                code: 'FORBIDDEN',
                message: 'Permission denied'
            };
            
            errorHandler.handleError(error);
            
            const notification = mockShowNotification.mock.calls[0][0];
            expect(notification.message).toContain('administrator privileges');
        });
        
        it('should provide disk space recovery', () => {
            const error = new Error('No space left on device');
            
            errorHandler.handleError(error);
            
            const notification = mockShowNotification.mock.calls[0][0];
            expect(notification.message).toContain('Insufficient disk space');
            expect(notification.actions[0].label).toBe('Clean System');
        });
    });
    
    describe('Error UI', () => {
        it('should show inline error messages', () => {
            const container = document.getElementById('error-container');
            
            errorHandler.showInlineError(container, 'Invalid configuration');
            
            const errorDiv = container.querySelector('.error-message');
            expect(errorDiv).toBeTruthy();
            expect(errorDiv.textContent).toContain('Invalid configuration');
        });
        
        it('should show field validation errors', () => {
            const input = document.createElement('input');
            input.id = 'test-input';
            document.body.appendChild(input);
            
            errorHandler.showFieldError('test-input', 'This field is required');
            
            expect(input.classList.contains('error')).toBe(true);
            const errorMsg = document.querySelector('.field-error');
            expect(errorMsg.textContent).toBe('This field is required');
        });
        
        it('should clear field errors', () => {
            const input = document.createElement('input');
            input.id = 'test-input';
            input.classList.add('error');
            document.body.appendChild(input);
            
            errorHandler.clearFieldError('test-input');
            
            expect(input.classList.contains('error')).toBe(false);
        });
    });
    
    describe('Error Logging', () => {
        it('should log errors with severity', () => {
            const error = new Error('Critical error');
            error.severity = 'critical';
            
            errorHandler.handleError(error);
            
            expect(console.error).toHaveBeenCalledWith(
                expect.stringContaining('[CRITICAL]'),
                error
            );
        });
        
        it('should track error frequency', () => {
            const error1 = new Error('Repeated error');
            const error2 = new Error('Repeated error');
            
            errorHandler.handleError(error1);
            errorHandler.handleError(error2);
            
            // Should throttle repeated errors
            expect(mockShowNotification).toHaveBeenCalledTimes(1);
        });
        
        it('should send critical errors to monitoring', () => {
            const mockSendError = jest.fn();
            errorHandler.sendErrorToMonitoring = mockSendError;
            
            const error = new Error('Critical system error');
            error.severity = 'critical';
            
            errorHandler.handleError(error);
            
            expect(mockSendError).toHaveBeenCalledWith(error);
        });
    });
    
    describe('Global Error Handling', () => {
        it('should handle unhandled promise rejections', () => {
            const event = new Event('unhandledrejection');
            event.reason = new Error('Unhandled promise');
            
            window.dispatchEvent(event);
            
            expect(console.error).toHaveBeenCalled();
            expect(mockShowNotification).toHaveBeenCalled();
        });
        
        it('should handle global errors', () => {
            const error = new Error('Global error');
            const event = new ErrorEvent('error', {
                error,
                message: error.message,
                filename: 'app.js',
                lineno: 100,
                colno: 50
            });
            
            window.dispatchEvent(event);
            
            expect(console.error).toHaveBeenCalledWith(
                expect.stringContaining('Global error'),
                expect.objectContaining({
                    filename: 'app.js',
                    line: 100,
                    column: 50
                })
            );
        });
    });
    
    describe('Error Recovery', () => {
        it('should attempt automatic recovery for transient errors', async () => {
            const mockOperation = jest.fn()
                .mockRejectedValueOnce(new Error('Temporary failure'))
                .mockResolvedValueOnce({ success: true });
            
            const result = await errorHandler.withRetry(mockOperation, {
                maxRetries: 3,
                delay: 100
            });
            
            expect(result.success).toBe(true);
            expect(mockOperation).toHaveBeenCalledTimes(2);
        });
        
        it('should not retry non-retryable errors', async () => {
            const mockOperation = jest.fn()
                .mockRejectedValue(new Error('FORBIDDEN'));
            
            await expect(errorHandler.withRetry(mockOperation)).rejects.toThrow('FORBIDDEN');
            expect(mockOperation).toHaveBeenCalledTimes(1);
        });
    });
});