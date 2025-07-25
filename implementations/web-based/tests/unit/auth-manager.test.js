/**
 * Unit Tests for Auth Manager
 */

import { AuthManager } from '../../js/auth-manager';

describe('AuthManager', () => {
    let authManager;
    let mockLocalStorage;
    let mockFetch;
    
    beforeEach(() => {
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
        
        // Mock fetch
        mockFetch = jest.fn();
        global.fetch = mockFetch;
        
        // Mock window.location
        delete window.location;
        window.location = {
            href: 'http://localhost:8080/dashboard',
            pathname: '/dashboard',
            reload: jest.fn()
        };
        
        authManager = new AuthManager();
    });
    
    afterEach(() => {
        jest.clearAllMocks();
        authManager.destroy();
    });
    
    describe('Initialization', () => {
        it('should initialize with default state', () => {
            expect(authManager.isAuthenticated()).toBe(false);
            expect(authManager.currentUser).toBeNull();
            expect(authManager.tokens).toEqual({
                access: null,
                refresh: null
            });
        });
        
        it('should restore session from localStorage', () => {
            mockLocalStorage.getItem.mockImplementation(key => {
                if (key === 'auth_tokens') {
                    return JSON.stringify({
                        access: 'valid-access-token',
                        refresh: 'valid-refresh-token'
                    });
                }
                if (key === 'auth_user') {
                    return JSON.stringify({
                        username: 'testuser',
                        groups: ['wheel']
                    });
                }
                return null;
            });
            
            authManager.init();
            
            expect(authManager.isAuthenticated()).toBe(true);
            expect(authManager.currentUser.username).toBe('testuser');
        });
        
        it('should set up token refresh timer', () => {
            jest.useFakeTimers();
            
            mockLocalStorage.getItem.mockReturnValue(JSON.stringify({
                access: 'token',
                refresh: 'refresh-token'
            }));
            
            authManager.init();
            
            expect(setTimeout).toHaveBeenCalled();
            
            jest.useRealTimers();
        });
    });
    
    describe('Authentication', () => {
        it('should login with valid credentials', async () => {
            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({
                    success: true,
                    data: {
                        user: {
                            username: 'testuser',
                            groups: ['wheel', 'users']
                        },
                        accessToken: 'new-access-token',
                        refreshToken: 'new-refresh-token'
                    }
                })
            });
            
            const result = await authManager.login('testuser', 'password');
            
            expect(result.success).toBe(true);
            expect(authManager.isAuthenticated()).toBe(true);
            expect(authManager.currentUser.username).toBe('testuser');
            expect(authManager.tokens.access).toBe('new-access-token');
            
            // Check tokens saved
            expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
                'auth_tokens',
                expect.stringContaining('new-access-token')
            );
        });
        
        it('should handle login failure', async () => {
            mockFetch.mockResolvedValueOnce({
                ok: false,
                status: 401,
                json: () => Promise.resolve({
                    success: false,
                    error: {
                        message: 'Invalid credentials'
                    }
                })
            });
            
            const result = await authManager.login('testuser', 'wrongpass');
            
            expect(result.success).toBe(false);
            expect(result.error).toContain('Invalid credentials');
            expect(authManager.isAuthenticated()).toBe(false);
        });
        
        it('should handle network errors', async () => {
            mockFetch.mockRejectedValueOnce(new Error('Network error'));
            
            const result = await authManager.login('testuser', 'password');
            
            expect(result.success).toBe(false);
            expect(result.error).toContain('Network error');
        });
        
        it('should validate input', async () => {
            const result1 = await authManager.login('', 'password');
            expect(result1.success).toBe(false);
            expect(result1.error).toContain('Username is required');
            
            const result2 = await authManager.login('user', '');
            expect(result2.success).toBe(false);
            expect(result2.error).toContain('Password is required');
        });
    });
    
    describe('Logout', () => {
        beforeEach(() => {
            // Set up authenticated state
            authManager.tokens = {
                access: 'access-token',
                refresh: 'refresh-token'
            };
            authManager.currentUser = {
                username: 'testuser',
                groups: ['wheel']
            };
        });
        
        it('should logout successfully', async () => {
            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({ success: true })
            });
            
            await authManager.logout();
            
            expect(authManager.isAuthenticated()).toBe(false);
            expect(authManager.currentUser).toBeNull();
            expect(authManager.tokens.access).toBeNull();
            
            // Check localStorage cleared
            expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('auth_tokens');
            expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('auth_user');
            
            // Check logout API called
            expect(mockFetch).toHaveBeenCalledWith(
                '/api/auth/logout',
                expect.objectContaining({
                    method: 'POST',
                    headers: expect.objectContaining({
                        'Authorization': 'Bearer access-token'
                    })
                })
            );
        });
        
        it('should clear state even if API fails', async () => {
            mockFetch.mockRejectedValueOnce(new Error('API Error'));
            
            await authManager.logout();
            
            expect(authManager.isAuthenticated()).toBe(false);
            expect(mockLocalStorage.removeItem).toHaveBeenCalled();
        });
        
        it('should emit logout event', async () => {
            const logoutHandler = jest.fn();
            authManager.on('logout', logoutHandler);
            
            await authManager.logout();
            
            expect(logoutHandler).toHaveBeenCalled();
        });
    });
    
    describe('Token Management', () => {
        beforeEach(() => {
            authManager.tokens = {
                access: 'old-access-token',
                refresh: 'refresh-token'
            };
            authManager.currentUser = {
                username: 'testuser'
            };
        });
        
        it('should refresh access token', async () => {
            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({
                    success: true,
                    data: {
                        accessToken: 'new-access-token'
                    }
                })
            });
            
            const result = await authManager.refreshToken();
            
            expect(result).toBe(true);
            expect(authManager.tokens.access).toBe('new-access-token');
            expect(mockLocalStorage.setItem).toHaveBeenCalled();
        });
        
        it('should handle refresh token failure', async () => {
            mockFetch.mockResolvedValueOnce({
                ok: false,
                status: 401
            });
            
            const logoutSpy = jest.spyOn(authManager, 'logout');
            
            const result = await authManager.refreshToken();
            
            expect(result).toBe(false);
            expect(logoutSpy).toHaveBeenCalled();
        });
        
        it('should auto-refresh before expiry', async () => {
            jest.useFakeTimers();
            
            // Mock token with 1 hour expiry
            const token = createMockJWT({ exp: Date.now() / 1000 + 3600 });
            authManager.tokens.access = token;
            
            const refreshSpy = jest.spyOn(authManager, 'refreshToken')
                .mockResolvedValue(true);
            
            authManager.scheduleTokenRefresh();
            
            // Fast forward to 5 minutes before expiry
            jest.advanceTimersByTime(55 * 60 * 1000);
            
            expect(refreshSpy).toHaveBeenCalled();
            
            jest.useRealTimers();
        });
        
        it('should decode JWT tokens', () => {
            const payload = {
                sub: 'testuser',
                exp: Date.now() / 1000 + 3600,
                groups: ['wheel']
            };
            
            const token = createMockJWT(payload);
            const decoded = authManager.decodeToken(token);
            
            expect(decoded.sub).toBe('testuser');
            expect(decoded.groups).toContain('wheel');
        });
    });
    
    describe('Authorization', () => {
        beforeEach(() => {
            authManager.currentUser = {
                username: 'testuser',
                groups: ['users', 'nixos-gui']
            };
        });
        
        it('should check user permissions', () => {
            expect(authManager.hasPermission('read')).toBe(true);
            expect(authManager.hasPermission('admin')).toBe(false);
        });
        
        it('should check group membership', () => {
            expect(authManager.hasGroup('users')).toBe(true);
            expect(authManager.hasGroup('wheel')).toBe(false);
        });
        
        it('should check admin status', () => {
            expect(authManager.isAdmin()).toBe(false);
            
            authManager.currentUser.groups.push('wheel');
            expect(authManager.isAdmin()).toBe(true);
        });
        
        it('should validate required permissions', () => {
            const canRead = authManager.requirePermission('read');
            expect(canRead).toBe(true);
            
            const canAdmin = authManager.requirePermission('admin');
            expect(canAdmin).toBe(false);
        });
    });
    
    describe('Request Interceptor', () => {
        it('should add auth headers to requests', async () => {
            authManager.tokens.access = 'test-token';
            
            const request = authManager.createAuthRequest('/api/test', {
                method: 'GET'
            });
            
            expect(request.headers['Authorization']).toBe('Bearer test-token');
        });
        
        it('should handle 401 responses', async () => {
            authManager.tokens.access = 'expired-token';
            authManager.tokens.refresh = 'refresh-token';
            
            // First request fails with 401
            mockFetch.mockResolvedValueOnce({
                ok: false,
                status: 401
            });
            
            // Token refresh succeeds
            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({
                    success: true,
                    data: { accessToken: 'new-token' }
                })
            });
            
            // Retry succeeds
            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({ data: 'success' })
            });
            
            const result = await authManager.authenticatedFetch('/api/test');
            
            expect(mockFetch).toHaveBeenCalledTimes(3);
            expect(result.data).toBe('success');
        });
        
        it('should not retry after refresh failure', async () => {
            authManager.tokens.access = 'expired-token';
            
            // First request fails
            mockFetch.mockResolvedValueOnce({
                ok: false,
                status: 401
            });
            
            // Token refresh fails
            mockFetch.mockResolvedValueOnce({
                ok: false,
                status: 401
            });
            
            const logoutSpy = jest.spyOn(authManager, 'logout');
            
            try {
                await authManager.authenticatedFetch('/api/test');
            } catch (error) {
                expect(error.message).toContain('Authentication failed');
            }
            
            expect(logoutSpy).toHaveBeenCalled();
        });
    });
    
    describe('Session Management', () => {
        it('should detect session expiry', () => {
            const expiredToken = createMockJWT({
                exp: Date.now() / 1000 - 3600 // Expired 1 hour ago
            });
            
            authManager.tokens.access = expiredToken;
            
            expect(authManager.isSessionExpired()).toBe(true);
        });
        
        it('should handle session timeout', async () => {
            jest.useFakeTimers();
            
            authManager.currentUser = { username: 'testuser' };
            authManager.tokens.access = 'token';
            
            const timeoutHandler = jest.fn();
            authManager.on('session-timeout', timeoutHandler);
            
            authManager.startSessionTimer(1000); // 1 second timeout
            
            jest.advanceTimersByTime(1001);
            
            expect(timeoutHandler).toHaveBeenCalled();
            expect(authManager.isAuthenticated()).toBe(false);
            
            jest.useRealTimers();
        });
        
        it('should reset session timer on activity', () => {
            jest.useFakeTimers();
            
            authManager.currentUser = { username: 'testuser' };
            authManager.startSessionTimer(5000);
            
            // Activity after 2 seconds
            jest.advanceTimersByTime(2000);
            authManager.resetSessionTimer();
            
            // Should not timeout after original 5 seconds
            jest.advanceTimersByTime(3001);
            expect(authManager.isAuthenticated()).toBe(true);
            
            // Should timeout after new 5 seconds
            jest.advanceTimersByTime(2000);
            expect(authManager.isAuthenticated()).toBe(false);
            
            jest.useRealTimers();
        });
    });
    
    describe('Events', () => {
        it('should emit login event', async () => {
            const loginHandler = jest.fn();
            authManager.on('login', loginHandler);
            
            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({
                    success: true,
                    data: {
                        user: { username: 'testuser' },
                        accessToken: 'token',
                        refreshToken: 'refresh'
                    }
                })
            });
            
            await authManager.login('testuser', 'password');
            
            expect(loginHandler).toHaveBeenCalledWith({
                user: expect.objectContaining({ username: 'testuser' })
            });
        });
        
        it('should emit auth-error event', async () => {
            const errorHandler = jest.fn();
            authManager.on('auth-error', errorHandler);
            
            mockFetch.mockRejectedValueOnce(new Error('Network error'));
            
            await authManager.login('testuser', 'password');
            
            expect(errorHandler).toHaveBeenCalledWith({
                error: expect.stringContaining('Network error')
            });
        });
        
        it('should emit token-refreshed event', async () => {
            const refreshHandler = jest.fn();
            authManager.on('token-refreshed', refreshHandler);
            
            authManager.tokens.refresh = 'refresh-token';
            
            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({
                    success: true,
                    data: { accessToken: 'new-token' }
                })
            });
            
            await authManager.refreshToken();
            
            expect(refreshHandler).toHaveBeenCalled();
        });
    });
    
    describe('Security', () => {
        it('should sanitize user input', async () => {
            mockFetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve({
                    success: true,
                    data: {
                        user: { username: 'testuser' },
                        accessToken: 'token',
                        refreshToken: 'refresh'
                    }
                })
            });
            
            await authManager.login('<script>alert("xss")</script>', 'password');
            
            const [, options] = mockFetch.mock.calls[0];
            const body = JSON.parse(options.body);
            
            expect(body.username).not.toContain('<script>');
        });
        
        it('should clear sensitive data on destroy', () => {
            authManager.tokens = {
                access: 'token',
                refresh: 'refresh'
            };
            authManager.currentUser = { username: 'user' };
            
            authManager.destroy();
            
            expect(authManager.tokens.access).toBeNull();
            expect(authManager.tokens.refresh).toBeNull();
            expect(authManager.currentUser).toBeNull();
        });
        
        it('should use secure cookie settings in production', () => {
            const originalEnv = process.env.NODE_ENV;
            process.env.NODE_ENV = 'production';
            
            const cookieOptions = authManager.getCookieOptions();
            
            expect(cookieOptions.secure).toBe(true);
            expect(cookieOptions.sameSite).toBe('strict');
            expect(cookieOptions.httpOnly).toBe(true);
            
            process.env.NODE_ENV = originalEnv;
        });
    });
});

// Helper function to create mock JWT
function createMockJWT(payload) {
    const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
    const body = btoa(JSON.stringify(payload));
    const signature = 'mock-signature';
    return `${header}.${body}.${signature}`;
}