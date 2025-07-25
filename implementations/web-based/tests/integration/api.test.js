/**
 * API Integration Tests
 * Tests the complete API flow with backend and database
 */

const request = require('supertest');
const { app, server } = require('../../backend/server');
const db = require('../../backend/services/database');
const auth = require('../../backend/services/auth');
const redis = require('../../backend/services/redis');

// Mock the helper service
jest.mock('../../backend/services/helper', () => ({
    executeCommand: jest.fn(),
    searchPackages: jest.fn(),
    installPackage: jest.fn(),
    removePackage: jest.fn(),
    listServices: jest.fn(),
    manageService: jest.fn(),
    getSystemInfo: jest.fn()
}));

const helper = require('../../backend/services/helper');

describe('API Integration Tests', () => {
    let authToken;
    let refreshToken;
    let testUser;
    
    beforeAll(async () => {
        // Initialize database
        await db.init(':memory:');
        
        // Create test user
        testUser = {
            username: 'testuser',
            groups: ['wheel', 'nixos-gui']
        };
        
        // Generate auth tokens
        const tokens = auth.generateTokens(testUser);
        authToken = tokens.accessToken;
        refreshToken = tokens.refreshToken;
    });
    
    afterAll(async () => {
        // Clean up
        await db.close();
        await redis.quit();
        server.close();
    });
    
    beforeEach(() => {
        // Reset mocks
        jest.clearAllMocks();
    });
    
    describe('Authentication Flow', () => {
        it('should authenticate user and return tokens', async () => {
            // Mock PAM authentication
            jest.spyOn(auth, 'authenticate').mockResolvedValue({
                success: true,
                user: testUser
            });
            
            const response = await request(app)
                .post('/api/auth/login')
                .send({
                    username: 'testuser',
                    password: 'testpass'
                });
            
            expect(response.status).toBe(200);
            expect(response.body).toMatchObject({
                success: true,
                data: {
                    user: {
                        username: 'testuser',
                        groups: ['wheel', 'nixos-gui']
                    },
                    accessToken: expect.any(String),
                    refreshToken: expect.any(String)
                }
            });
        });
        
        it('should refresh access token', async () => {
            const response = await request(app)
                .post('/api/auth/refresh')
                .send({
                    refreshToken
                });
            
            expect(response.status).toBe(200);
            expect(response.body).toMatchObject({
                success: true,
                data: {
                    accessToken: expect.any(String)
                }
            });
        });
        
        it('should logout and invalidate tokens', async () => {
            const response = await request(app)
                .post('/api/auth/logout')
                .set('Authorization', `Bearer ${authToken}`)
                .send({
                    refreshToken
                });
            
            expect(response.status).toBe(200);
            
            // Verify token is invalidated
            const verifyResponse = await request(app)
                .get('/api/auth/verify')
                .set('Authorization', `Bearer ${authToken}`);
            
            expect(verifyResponse.status).toBe(401);
        });
    });
    
    describe('Package Management', () => {
        it('should search for packages', async () => {
            helper.searchPackages.mockResolvedValue({
                success: true,
                packages: [
                    {
                        name: 'firefox',
                        version: '120.0',
                        description: 'Web browser'
                    },
                    {
                        name: 'firefox-esr',
                        version: '115.0',
                        description: 'Web browser (ESR)'
                    }
                ]
            });
            
            const response = await request(app)
                .get('/api/packages/search?q=firefox')
                .set('Authorization', `Bearer ${authToken}`);
            
            expect(response.status).toBe(200);
            expect(response.body.data.packages).toHaveLength(2);
            expect(helper.searchPackages).toHaveBeenCalledWith('firefox');
        });
        
        it('should install a package', async () => {
            helper.installPackage.mockResolvedValue({
                success: true,
                message: 'Package installed successfully'
            });
            
            const response = await request(app)
                .post('/api/packages/install')
                .set('Authorization', `Bearer ${authToken}`)
                .send({
                    package: 'vim'
                });
            
            expect(response.status).toBe(200);
            expect(helper.installPackage).toHaveBeenCalledWith('vim');
            
            // Verify audit log
            const logs = await db.getAuditLogs({ action: 'package.install' });
            expect(logs).toHaveLength(1);
            expect(logs[0]).toMatchObject({
                user: 'testuser',
                action: 'package.install',
                resource: 'vim'
            });
        });
        
        it('should handle package installation errors', async () => {
            helper.installPackage.mockRejectedValue(
                new Error('Package not found')
            );
            
            const response = await request(app)
                .post('/api/packages/install')
                .set('Authorization', `Bearer ${authToken}`)
                .send({
                    package: 'nonexistent'
                });
            
            expect(response.status).toBe(500);
            expect(response.body.error.message).toContain('Package not found');
        });
    });
    
    describe('Service Management', () => {
        it('should list all services', async () => {
            helper.listServices.mockResolvedValue({
                success: true,
                services: [
                    {
                        name: 'nginx',
                        enabled: true,
                        active: true,
                        description: 'Web server'
                    },
                    {
                        name: 'sshd',
                        enabled: true,
                        active: true,
                        description: 'SSH daemon'
                    }
                ]
            });
            
            const response = await request(app)
                .get('/api/services')
                .set('Authorization', `Bearer ${authToken}`);
            
            expect(response.status).toBe(200);
            expect(response.body.data.services).toHaveLength(2);
        });
        
        it('should start a service', async () => {
            helper.manageService.mockResolvedValue({
                success: true,
                message: 'Service started'
            });
            
            const response = await request(app)
                .post('/api/services/nginx/start')
                .set('Authorization', `Bearer ${authToken}`);
            
            expect(response.status).toBe(200);
            expect(helper.manageService).toHaveBeenCalledWith('nginx', 'start');
            
            // Verify audit log
            const logs = await db.getAuditLogs({ action: 'service.start' });
            expect(logs).toHaveLength(1);
        });
    });
    
    describe('Configuration Management', () => {
        it('should get configuration file', async () => {
            const mockConfig = `{ pkgs, ... }: {
                services.nginx.enable = true;
            }`;
            
            helper.executeCommand.mockResolvedValue({
                success: true,
                output: mockConfig
            });
            
            const response = await request(app)
                .get('/api/config')
                .set('Authorization', `Bearer ${authToken}`);
            
            expect(response.status).toBe(200);
            expect(response.body.data.content).toBe(mockConfig);
        });
        
        it('should validate configuration', async () => {
            helper.executeCommand.mockResolvedValue({
                success: true,
                output: 'Configuration is valid'
            });
            
            const response = await request(app)
                .post('/api/config/validate')
                .set('Authorization', `Bearer ${authToken}`)
                .send({
                    content: '{ pkgs, ... }: { }'
                });
            
            expect(response.status).toBe(200);
            expect(response.body.data.valid).toBe(true);
        });
    });
    
    describe('System Operations', () => {
        it('should get system information', async () => {
            helper.getSystemInfo.mockResolvedValue({
                success: true,
                info: {
                    nixosVersion: '23.11',
                    kernel: '6.1.0',
                    uptime: '5 days',
                    memory: {
                        total: 16384,
                        used: 8192,
                        free: 8192
                    }
                }
            });
            
            const response = await request(app)
                .get('/api/system/info')
                .set('Authorization', `Bearer ${authToken}`);
            
            expect(response.status).toBe(200);
            expect(response.body.data.info).toMatchObject({
                nixosVersion: '23.11',
                kernel: '6.1.0'
            });
        });
        
        it('should rebuild system', async () => {
            helper.executeCommand.mockResolvedValue({
                success: true,
                output: 'System rebuilt successfully'
            });
            
            const response = await request(app)
                .post('/api/system/rebuild')
                .set('Authorization', `Bearer ${authToken}`)
                .send({
                    switch: true
                });
            
            expect(response.status).toBe(200);
            expect(helper.executeCommand).toHaveBeenCalledWith(
                'nixos-rebuild',
                ['switch'],
                expect.any(Object)
            );
        });
    });
    
    describe('Authorization', () => {
        it('should deny access without token', async () => {
            const response = await request(app)
                .get('/api/packages/search?q=vim');
            
            expect(response.status).toBe(401);
        });
        
        it('should deny access with invalid token', async () => {
            const response = await request(app)
                .get('/api/packages/search?q=vim')
                .set('Authorization', 'Bearer invalid-token');
            
            expect(response.status).toBe(401);
        });
        
        it('should deny admin operations to non-admin users', async () => {
            // Create non-admin user
            const regularUser = {
                username: 'regular',
                groups: ['users']
            };
            
            const tokens = auth.generateTokens(regularUser);
            
            const response = await request(app)
                .post('/api/system/rebuild')
                .set('Authorization', `Bearer ${tokens.accessToken}`)
                .send({
                    switch: true
                });
            
            expect(response.status).toBe(403);
            expect(response.body.error.code).toBe('FORBIDDEN');
        });
    });
    
    describe('Rate Limiting', () => {
        it('should rate limit API requests', async () => {
            // Make multiple requests quickly
            const promises = [];
            for (let i = 0; i < 150; i++) {
                promises.push(
                    request(app)
                        .get('/api/packages/search?q=test')
                        .set('Authorization', `Bearer ${authToken}`)
                );
            }
            
            const responses = await Promise.all(promises);
            
            // Some requests should be rate limited
            const rateLimited = responses.filter(r => r.status === 429);
            expect(rateLimited.length).toBeGreaterThan(0);
            
            // Rate limit message should be present
            expect(rateLimited[0].body.error.message).toContain('Too many requests');
        });
    });
    
    describe('Error Handling', () => {
        it('should handle database errors gracefully', async () => {
            // Force database error
            jest.spyOn(db, 'query').mockRejectedValueOnce(
                new Error('Database connection lost')
            );
            
            const response = await request(app)
                .get('/api/audit')
                .set('Authorization', `Bearer ${authToken}`);
            
            expect(response.status).toBe(500);
            expect(response.body.error.code).toBe('INTERNAL_ERROR');
            expect(response.body.error.message).not.toContain('Database');
        });
        
        it('should handle helper service errors', async () => {
            helper.searchPackages.mockRejectedValue(
                new Error('Helper service unavailable')
            );
            
            const response = await request(app)
                .get('/api/packages/search?q=vim')
                .set('Authorization', `Bearer ${authToken}`);
            
            expect(response.status).toBe(503);
            expect(response.body.error.code).toBe('SERVICE_UNAVAILABLE');
        });
    });
    
    describe('WebSocket Integration', () => {
        const io = require('socket.io-client');
        let socket;
        
        beforeEach((done) => {
            socket = io('http://localhost:8080', {
                auth: {
                    token: authToken
                }
            });
            
            socket.on('connect', done);
        });
        
        afterEach(() => {
            if (socket.connected) {
                socket.disconnect();
            }
        });
        
        it('should connect with valid token', (done) => {
            expect(socket.connected).toBe(true);
            done();
        });
        
        it('should receive system events', (done) => {
            socket.on('system.event', (event) => {
                expect(event).toMatchObject({
                    type: 'package.installed',
                    data: {
                        package: 'vim'
                    }
                });
                done();
            });
            
            // Trigger an event
            request(app)
                .post('/api/packages/install')
                .set('Authorization', `Bearer ${authToken}`)
                .send({ package: 'vim' })
                .end(() => {});
        });
    });
});

describe('API Security Tests', () => {
    let authToken;
    
    beforeAll(async () => {
        const tokens = auth.generateTokens({
            username: 'testuser',
            groups: ['wheel']
        });
        authToken = tokens.accessToken;
    });
    
    describe('Input Validation', () => {
        it('should reject invalid package names', async () => {
            const response = await request(app)
                .post('/api/packages/install')
                .set('Authorization', `Bearer ${authToken}`)
                .send({
                    package: '../../../etc/passwd'
                });
            
            expect(response.status).toBe(400);
            expect(response.body.error.code).toBe('VALIDATION_ERROR');
        });
        
        it('should reject invalid service names', async () => {
            const response = await request(app)
                .post('/api/services/../../evil/start')
                .set('Authorization', `Bearer ${authToken}`);
            
            expect(response.status).toBe(400);
        });
        
        it('should sanitize search queries', async () => {
            const response = await request(app)
                .get('/api/packages/search?q=<script>alert("xss")</script>')
                .set('Authorization', `Bearer ${authToken}`);
            
            expect(response.status).toBe(200);
            // Verify the query was sanitized
            expect(helper.searchPackages).toHaveBeenCalledWith(
                expect.not.stringContaining('<script>')
            );
        });
    });
    
    describe('CSRF Protection', () => {
        it('should reject requests without CSRF token', async () => {
            const response = await request(app)
                .post('/api/system/rebuild')
                .set('Authorization', `Bearer ${authToken}`)
                .send({ switch: true });
            
            // CSRF token should be required for state-changing operations
            expect(response.status).toBe(403);
        });
    });
});

describe('Performance Tests', () => {
    let authToken;
    
    beforeAll(async () => {
        const tokens = auth.generateTokens({
            username: 'perfuser',
            groups: ['wheel']
        });
        authToken = tokens.accessToken;
    });
    
    it('should handle concurrent requests efficiently', async () => {
        const startTime = Date.now();
        
        // Make 50 concurrent requests
        const promises = [];
        for (let i = 0; i < 50; i++) {
            promises.push(
                request(app)
                    .get('/api/packages/search?q=test' + i)
                    .set('Authorization', `Bearer ${authToken}`)
            );
        }
        
        const responses = await Promise.all(promises);
        const endTime = Date.now();
        
        // All should succeed
        const successful = responses.filter(r => r.status === 200);
        expect(successful.length).toBeGreaterThan(40);
        
        // Should complete within reasonable time
        const duration = endTime - startTime;
        expect(duration).toBeLessThan(5000); // 5 seconds
    });
    
    it('should cache repeated requests', async () => {
        // First request
        const start1 = Date.now();
        const response1 = await request(app)
            .get('/api/system/info')
            .set('Authorization', `Bearer ${authToken}`);
        const duration1 = Date.now() - start1;
        
        // Second request (should be cached)
        const start2 = Date.now();
        const response2 = await request(app)
            .get('/api/system/info')
            .set('Authorization', `Bearer ${authToken}`);
        const duration2 = Date.now() - start2;
        
        expect(response1.status).toBe(200);
        expect(response2.status).toBe(200);
        expect(response1.body).toEqual(response2.body);
        
        // Cached request should be faster
        expect(duration2).toBeLessThan(duration1 / 2);
    });
});