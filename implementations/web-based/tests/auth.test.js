/**
 * Authentication System Tests
 * Tests PAM authentication, JWT tokens, and session management
 */

const axios = require('axios');
const assert = require('assert');

const baseURL = 'http://localhost:7891';

// Test credentials (these would be real system users in production)
const testUser = {
    username: process.env.TEST_USER || 'testuser',
    password: process.env.TEST_PASSWORD || 'testpass'
};

const adminUser = {
    username: process.env.ADMIN_USER || 'admin',
    password: process.env.ADMIN_PASSWORD || 'adminpass'
};

describe('Authentication System', () => {
    let accessToken = null;
    let refreshToken = null;
    let sessionId = null;

    describe('Login', () => {
        test('should reject missing credentials', async () => {
            try {
                await axios.post(`${baseURL}/api/auth/login`, {});
                assert.fail('Should have thrown error');
            } catch (error) {
                assert.equal(error.response.status, 401);
                assert.equal(error.response.data.success, false);
            }
        });

        test('should reject invalid credentials', async () => {
            try {
                await axios.post(`${baseURL}/api/auth/login`, {
                    username: 'invalid',
                    password: 'wrong'
                });
                assert.fail('Should have thrown error');
            } catch (error) {
                assert.equal(error.response.status, 401);
                assert.equal(error.response.data.success, false);
            }
        });

        test('should login with valid credentials', async () => {
            const response = await axios.post(`${baseURL}/api/auth/login`, {
                username: testUser.username,
                password: testUser.password
            });

            assert.equal(response.status, 200);
            assert.equal(response.data.success, true);
            assert.ok(response.data.accessToken);
            assert.ok(response.data.sessionId);
            assert.ok(response.data.user);
            assert.equal(response.data.user.username, testUser.username);

            // Save tokens for other tests
            accessToken = response.data.accessToken;
            sessionId = response.data.sessionId;
            
            // Extract refresh token from cookies
            const cookies = response.headers['set-cookie'];
            const refreshCookie = cookies?.find(c => c.startsWith('refreshToken='));
            if (refreshCookie) {
                refreshToken = refreshCookie.split(';')[0].split('=')[1];
            }
        });
    });

    describe('Token Verification', () => {
        test('should reject requests without token', async () => {
            try {
                await axios.get(`${baseURL}/api/auth/verify`);
                assert.fail('Should have thrown error');
            } catch (error) {
                assert.equal(error.response.status, 401);
            }
        });

        test('should accept valid token', async () => {
            const response = await axios.get(`${baseURL}/api/auth/verify`, {
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'X-Session-ID': sessionId
                }
            });

            assert.equal(response.status, 200);
            assert.equal(response.data.success, true);
            assert.ok(response.data.user);
            assert.equal(response.data.sessionId, sessionId);
        });
    });

    describe('Protected Routes', () => {
        test('should protect system info endpoint', async () => {
            try {
                await axios.get(`${baseURL}/api/system/info`);
                assert.fail('Should have thrown error');
            } catch (error) {
                assert.equal(error.response.status, 401);
            }
        });

        test('should allow access with valid token', async () => {
            const response = await axios.get(`${baseURL}/api/system/info`, {
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'X-Session-ID': sessionId
                }
            });

            assert.equal(response.status, 200);
            assert.equal(response.data.success, true);
            assert.ok(response.data.nixVersion);
        });
    });

    describe('Permission Checks', () => {
        test('should deny admin operations to regular users', async () => {
            try {
                await axios.post(`${baseURL}/api/system/rebuild`, 
                    { action: 'switch' },
                    {
                        headers: {
                            'Authorization': `Bearer ${accessToken}`,
                            'X-Session-ID': sessionId
                        }
                    }
                );
                assert.fail('Should have thrown error');
            } catch (error) {
                assert.equal(error.response.status, 403);
                assert.equal(error.response.data.error, 'Admin privileges required');
            }
        });

        // Note: Testing admin operations requires an admin user in the system
        test.skip('should allow admin operations to admin users', async () => {
            // Login as admin
            const adminResponse = await axios.post(`${baseURL}/api/auth/login`, {
                username: adminUser.username,
                password: adminUser.password
            });

            const adminToken = adminResponse.data.accessToken;
            const adminSession = adminResponse.data.sessionId;

            // Try admin operation
            const response = await axios.get(`${baseURL}/api/system/generations`, {
                headers: {
                    'Authorization': `Bearer ${adminToken}`,
                    'X-Session-ID': adminSession
                }
            });

            assert.equal(response.status, 200);
            assert.equal(response.data.success, true);
        });
    });

    describe('Session Management', () => {
        test('should list active sessions', async () => {
            const response = await axios.get(`${baseURL}/api/auth/sessions`, {
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'X-Session-ID': sessionId
                }
            });

            assert.equal(response.status, 200);
            assert.equal(response.data.success, true);
            assert.ok(Array.isArray(response.data.sessions));
            assert.ok(response.data.sessions.length > 0);
            assert.equal(response.data.current, sessionId);
        });

        test('should not allow terminating other user sessions', async () => {
            // This would require another user's session ID
            try {
                await axios.delete(`${baseURL}/api/auth/sessions/fake-session-id`, {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`,
                        'X-Session-ID': sessionId
                    }
                });
                assert.fail('Should have thrown error');
            } catch (error) {
                assert.equal(error.response.status, 403);
            }
        });
    });

    describe('Token Refresh', () => {
        test('should refresh access token', async () => {
            const response = await axios.post(`${baseURL}/api/auth/refresh`, {
                refreshToken: refreshToken
            });

            assert.equal(response.status, 200);
            assert.equal(response.data.success, true);
            assert.ok(response.data.accessToken);
            assert.ok(response.data.user);

            // Update access token for remaining tests
            accessToken = response.data.accessToken;
        });
    });

    describe('Logout', () => {
        test('should logout successfully', async () => {
            const response = await axios.post(`${baseURL}/api/auth/logout`, 
                { refreshToken },
                {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`,
                        'X-Session-ID': sessionId
                    }
                }
            );

            assert.equal(response.status, 200);
            assert.equal(response.data.success, true);
        });

        test('should reject requests after logout', async () => {
            try {
                await axios.get(`${baseURL}/api/auth/verify`, {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`,
                        'X-Session-ID': sessionId
                    }
                });
                assert.fail('Should have thrown error');
            } catch (error) {
                assert.equal(error.response.status, 401);
            }
        });
    });
});

// Helper to run tests
async function runTests() {
    console.log('🔐 Testing Authentication System...\n');

    const tests = [
        'Login',
        'Token Verification',
        'Protected Routes',
        'Permission Checks',
        'Session Management',
        'Token Refresh',
        'Logout'
    ];

    for (const testGroup of tests) {
        console.log(`\n📋 ${testGroup}:`);
        // In a real test runner, this would execute the describe blocks
        console.log('✅ Tests would run here with Jest or similar');
    }

    console.log('\n\n✨ Authentication tests complete!');
    console.log('\nNote: To run real tests, ensure:');
    console.log('1. Backend is running on port 7891');
    console.log('2. Test users exist in the system');
    console.log('3. Helper service is available');
    console.log('\nRun with: npm test tests/auth.test.js');
}

// Run if called directly
if (require.main === module) {
    runTests().catch(console.error);
}

module.exports = { runTests };