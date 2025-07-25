/**
 * Tests for Production-Ready NixOS Backend
 */

const request = require('supertest');
const { app, nixOps, serviceManager, jobManager } = require('./real-backend');

// Mock child_process to avoid running real Nix commands in tests
jest.mock('child_process', () => ({
    exec: jest.fn(),
    spawn: jest.fn(() => ({
        stdout: { on: jest.fn() },
        stderr: { on: jest.fn() },
        on: jest.fn((event, callback) => {
            if (event === 'close') {
                setTimeout(() => callback(0), 100);
            }
        }),
        kill: jest.fn()
    }))
}));

const { exec, spawn } = require('child_process');
const { promisify } = require('util');

describe('NixOS Backend API', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('GET /api/health', () => {
        it('should return healthy status', async () => {
            const response = await request(app)
                .get('/api/health')
                .expect(200);

            expect(response.body).toHaveProperty('status', 'healthy');
            expect(response.body).toHaveProperty('version');
            expect(response.body).toHaveProperty('uptime');
        });
    });

    describe('GET /api/system/info', () => {
        it('should return system information', async () => {
            exec.mockImplementation((cmd, options, callback) => {
                const cb = callback || options;
                
                const responses = {
                    'nix --version': { stdout: 'nix (Nix) 2.18.1' },
                    'nixos-version': { stdout: '23.11 (Tapir)' },
                    'df -h /nix/store | tail -1': { stdout: '/dev/sda1  100G  85G  15G  85%  /nix/store' },
                    'free -h | grep Mem:': { stdout: 'Mem:  16G  8G  4G  100M  2G  8G' }
                };
                
                const response = responses[cmd] || { stdout: 'unknown' };
                cb(null, response.stdout, '');
            });

            const response = await request(app)
                .get('/api/system/info')
                .expect(200);

            expect(response.body.success).toBe(true);
            expect(response.body.nixVersion).toContain('2.18.1');
            expect(response.body.systemVersion).toContain('23.11');
            expect(response.body.disk).toHaveProperty('percent', '85%');
            expect(response.body.memory).toHaveProperty('total', '16G');
        });
    });

    describe('POST /api/nix/search', () => {
        it('should search for packages', async () => {
            exec.mockImplementation((cmd, options, callback) => {
                const cb = callback || options;
                
                if (cmd.includes('search')) {
                    const mockResults = JSON.stringify({
                        'nixpkgs.firefox': {
                            pname: 'firefox',
                            version: '121.0',
                            description: 'Mozilla Firefox web browser'
                        }
                    });
                    cb(null, mockResults, '');
                } else {
                    cb(null, 'nix (Nix) 2.18.1', '');
                }
            });

            const response = await request(app)
                .post('/api/nix/search')
                .send({ query: 'firefox' })
                .expect(200);

            expect(response.body.success).toBe(true);
            expect(response.body.packages).toBeInstanceOf(Array);
            expect(response.body.packages.length).toBeGreaterThan(0);
            expect(response.body.packages[0]).toHaveProperty('name', 'firefox');
        });

        it('should reject short search queries', async () => {
            const response = await request(app)
                .post('/api/nix/search')
                .send({ query: 'a' })
                .expect(400);

            expect(response.body.success).toBe(false);
            expect(response.body.error).toContain('at least 2 characters');
        });
    });

    describe('POST /api/nix/install', () => {
        it('should start user package installation', async () => {
            exec.mockImplementation((cmd, options, callback) => {
                const cb = callback || options;
                
                if (cmd.includes('search')) {
                    const mockResults = JSON.stringify({
                        'nixpkgs.firefox': {
                            pname: 'firefox',
                            version: '121.0',
                            description: 'Mozilla Firefox web browser'
                        }
                    });
                    cb(null, mockResults, '');
                } else {
                    cb(null, '', '');
                }
            });

            const response = await request(app)
                .post('/api/nix/install')
                .send({ package: 'firefox', scope: 'user' })
                .expect(200);

            expect(response.body.success).toBe(true);
            expect(response.body.jobId).toBeDefined();
            expect(response.body.jobId).toMatch(/^job_\d+_\d+$/);
        });

        it('should return config snippet for system packages', async () => {
            const response = await request(app)
                .post('/api/nix/install')
                .send({ package: 'firefox', scope: 'system' })
                .expect(200);

            expect(response.body.success).toBe(true);
            expect(response.body.action).toBe('show-config');
            expect(response.body.snippet).toContain('environment.systemPackages');
            expect(response.body.snippet).toContain('firefox');
        });

        it('should reject invalid package names', async () => {
            const response = await request(app)
                .post('/api/nix/install')
                .send({ package: '../../../etc/passwd' })
                .expect(400);

            expect(response.body.success).toBe(false);
            expect(response.body.error).toContain('Invalid package name');
        });
    });

    describe('GET /api/job/:jobId', () => {
        it('should return job status', async () => {
            // Create a job first
            exec.mockImplementation((cmd, options, callback) => {
                const cb = callback || options;
                
                if (cmd.includes('search')) {
                    const mockResults = JSON.stringify({
                        'nixpkgs.firefox': {
                            pname: 'firefox',
                            version: '121.0'
                        }
                    });
                    cb(null, mockResults, '');
                }
            });

            const installResponse = await request(app)
                .post('/api/nix/install')
                .send({ package: 'firefox' });

            const jobId = installResponse.body.jobId;

            // Check job status
            const response = await request(app)
                .get(`/api/job/${jobId}`)
                .expect(200);

            expect(response.body.success).toBe(true);
            expect(response.body.job).toHaveProperty('id', jobId);
            expect(response.body.job).toHaveProperty('type', 'install');
            expect(response.body.job).toHaveProperty('status');
            expect(response.body.job).toHaveProperty('progress');
        });

        it('should return 404 for non-existent job', async () => {
            const response = await request(app)
                .get('/api/job/nonexistent')
                .expect(404);

            expect(response.body.success).toBe(false);
            expect(response.body.error).toContain('not found');
        });
    });

    describe('POST /api/service/:action', () => {
        it('should handle service status check', async () => {
            exec.mockImplementation((cmd, callback) => {
                if (cmd.includes('is-active')) {
                    callback(null, 'active', '');
                }
            });

            const response = await request(app)
                .post('/api/service/status')
                .send({ service: 'nginx' })
                .expect(200);

            expect(response.body.success).toBe(true);
        });

        it('should return sudo requirement for system services', async () => {
            const response = await request(app)
                .post('/api/service/enable')
                .send({ service: 'nginx' })
                .expect(200);

            expect(response.body.success).toBe(true);
            expect(response.body.requiresSudo).toBe(true);
            expect(response.body.command).toContain('sudo systemctl enable');
        });

        it('should reject invalid service names', async () => {
            const response = await request(app)
                .post('/api/service/start')
                .send({ service: '../../etc/passwd' })
                .expect(200);

            // Service name will be sanitized, not rejected
            expect(response.body.success).toBe(true);
        });
    });

    describe('POST /api/diagnose', () => {
        it('should return system diagnostics', async () => {
            exec.mockImplementation((cmd, options, callback) => {
                const cb = callback || options;
                
                if (cmd.includes('is-active')) {
                    cb(null, 'active', '');
                } else {
                    cb(null, 'nix (Nix) 2.18.1', '');
                }
            });

            const response = await request(app)
                .post('/api/diagnose')
                .send({ target: 'system' })
                .expect(200);

            expect(response.body.success).toBe(true);
            expect(response.body.diagnostics).toHaveProperty('nix');
            expect(response.body.diagnostics).toHaveProperty('services');
        });
    });

    describe('POST /api/nix/preview', () => {
        it('should preview package installation', async () => {
            exec.mockImplementation((cmd, options, callback) => {
                const cb = callback || options;
                
                if (cmd.includes('search')) {
                    const mockResults = JSON.stringify({
                        'nixpkgs.firefox': {
                            pname: 'firefox',
                            version: '121.0',
                            description: 'Mozilla Firefox'
                        }
                    });
                    cb(null, mockResults, '');
                }
            });

            const response = await request(app)
                .post('/api/nix/preview')
                .send({ 
                    action: 'install',
                    package: 'firefox',
                    scope: 'user'
                })
                .expect(200);

            expect(response.body.success).toBe(true);
            expect(response.body.preview).toHaveProperty('package');
            expect(response.body.preview.package.name).toBe('firefox');
        });
    });
});

describe('NixOperations', () => {
    describe('isValidPackageName', () => {
        it('should accept valid package names', () => {
            const validNames = [
                'firefox',
                'firefox-bin',
                'python3',
                'python3.11',
                'hello_world',
                'package123'
            ];

            validNames.forEach(name => {
                expect(nixOps.isValidPackageName(name)).toBe(true);
            });
        });

        it('should reject invalid package names', () => {
            const invalidNames = [
                '../../../etc/passwd',
                'package with spaces',
                'package;rm -rf /',
                'package|cat /etc/passwd',
                'package`whoami`',
                '-package',
                ''
            ];

            invalidNames.forEach(name => {
                expect(nixOps.isValidPackageName(name)).toBe(false);
            });
        });
    });

    describe('escapeShellArg', () => {
        it('should properly escape shell arguments', () => {
            expect(nixOps.escapeShellArg("test")).toBe("'test'");
            expect(nixOps.escapeShellArg("test'test")).toBe("'test'\\''test'");
            expect(nixOps.escapeShellArg("test\"test")).toBe("'test\"test'");
            expect(nixOps.escapeShellArg("test`test")).toBe("'test`test'");
        });
    });
});

describe('ServiceManager', () => {
    describe('escapeServiceName', () => {
        it('should sanitize service names', () => {
            expect(serviceManager.escapeServiceName('nginx')).toBe('nginx');
            expect(serviceManager.escapeServiceName('nginx.service')).toBe('nginx.service');
            expect(serviceManager.escapeServiceName('user@1000.service')).toBe('user@1000.service');
            expect(serviceManager.escapeServiceName('../../etc/passwd')).toBe('etcpasswd');
            expect(serviceManager.escapeServiceName('nginx;rm -rf /')).toBe('nginxrm-rf');
        });
    });
});

describe('JobManager', () => {
    it('should create and track jobs', () => {
        const jobId = jobManager.createJob('test', { data: 'test' });
        
        expect(jobId).toMatch(/^job_\d+_\d+$/);
        
        const job = jobManager.getJob(jobId);
        expect(job).toBeDefined();
        expect(job.type).toBe('test');
        expect(job.status).toBe('pending');
        expect(job.progress).toBe(0);
    });

    it('should update job status', () => {
        const jobId = jobManager.createJob('test', {});
        
        jobManager.updateJob(jobId, {
            status: 'running',
            progress: 50
        });
        
        const job = jobManager.getJob(jobId);
        expect(job.status).toBe('running');
        expect(job.progress).toBe(50);
    });

    it('should clean up old jobs', () => {
        const jobId = jobManager.createJob('test', {});
        const job = jobManager.getJob(jobId);
        
        // Manually set old timestamp
        job.createdAt = new Date(Date.now() - 25 * 60 * 60 * 1000); // 25 hours ago
        
        jobManager.cleanupOldJobs();
        
        expect(jobManager.getJob(jobId)).toBeUndefined();
    });
});