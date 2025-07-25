# 🧪 NixOS GUI - Comprehensive Testing Guide

This guide covers all aspects of testing the NixOS GUI to ensure quality, reliability, and security.

## 📋 Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Test Categories](#test-categories)
3. [Running Tests](#running-tests)
4. [Writing Tests](#writing-tests)
5. [Test Infrastructure](#test-infrastructure)
6. [CI/CD Integration](#cicd-integration)
7. [Manual Testing](#manual-testing)

## Testing Philosophy

### Core Principles

1. **Test Real Behavior**: Mock as little as possible
2. **Fast Feedback**: Tests should run quickly
3. **Comprehensive Coverage**: Aim for >80% coverage
4. **Meaningful Tests**: Quality over quantity
5. **Maintainable**: Easy to update and understand

### Testing Pyramid

```
         /\
        /  \  E2E Tests (10%)
       /----\  - Full system tests
      /      \  - Critical user paths
     /--------\  Integration Tests (30%)
    /          \  - API tests
   /------------\  - Service tests
  /              \  Unit Tests (60%)
 /________________\  - Component logic
                      - Utility functions
```

## Test Categories

### 1. Unit Tests

**What**: Individual functions and components
**Tools**: Jest, Testing Library
**Location**: `*.test.js` files

```javascript
// Example: /backend/src/utils/validation.test.js
describe('validatePackageName', () => {
  test('accepts valid package names', () => {
    expect(validatePackageName('firefox')).toBe(true);
    expect(validatePackageName('git-2.34')).toBe(true);
  });

  test('rejects invalid package names', () => {
    expect(validatePackageName('')).toBe(false);
    expect(validatePackageName('package with spaces')).toBe(false);
    expect(validatePackageName('../../../etc/passwd')).toBe(false);
  });
});
```

### 2. Integration Tests

**What**: API endpoints and service interactions
**Tools**: Supertest, Jest
**Location**: `/tests/integration/`

```javascript
// Example: /tests/integration/packages.test.js
describe('Package API', () => {
  let app;
  let token;

  beforeAll(async () => {
    app = await createTestApp();
    token = await getAuthToken();
  });

  test('GET /api/packages/search', async () => {
    const response = await request(app)
      .get('/api/packages/search?q=firefox')
      .set('Authorization', `Bearer ${token}`)
      .expect(200);

    expect(response.body).toHaveProperty('results');
    expect(response.body.results).toBeInstanceOf(Array);
  });

  test('POST /api/packages/install', async () => {
    const response = await request(app)
      .post('/api/packages/install')
      .set('Authorization', `Bearer ${token}`)
      .send({ package: 'htop' })
      .expect(202);

    expect(response.body).toHaveProperty('jobId');
  });
});
```

### 3. End-to-End Tests

**What**: Complete user workflows
**Tools**: Playwright, Cypress
**Location**: `/tests/e2e/`

```javascript
// Example: /tests/e2e/install-package.spec.js
describe('Install Package Workflow', () => {
  beforeEach(async () => {
    await page.goto('http://localhost:8080');
    await login(page, 'testuser', 'testpass');
  });

  test('user can search and install a package', async () => {
    // Search for package
    await page.click('[data-testid="package-search"]');
    await page.type('[data-testid="package-search"]', 'firefox');
    await page.waitForSelector('[data-testid="search-results"]');

    // Click install
    await page.click('[data-testid="install-firefox"]');
    
    // Confirm installation
    await page.click('[data-testid="confirm-install"]');
    
    // Wait for success
    await page.waitForSelector('[data-testid="install-success"]');
    
    // Verify in installed list
    await page.click('[data-testid="installed-tab"]');
    await expect(page).toHaveText('firefox');
  });
});
```

### 4. Performance Tests

**What**: Load times, response times, resource usage
**Tools**: Lighthouse, k6
**Location**: `/tests/performance/`

```javascript
// Example: /tests/performance/load-test.js
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 20 },
    { duration: '1m', target: 100 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
  },
};

export default function() {
  let response = http.get('http://localhost:8080/api/packages');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
}
```

### 5. Security Tests

**What**: Vulnerability scanning, penetration testing
**Tools**: OWASP ZAP, npm audit
**Location**: `/tests/security/`

```bash
#!/bin/bash
# Example: /tests/security/security-scan.sh

echo "Running security tests..."

# Dependency vulnerabilities
npm audit --production

# OWASP ZAP scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:8080 -r security-report.html

# Check for secrets
truffleHog --regex --entropy=True .

# SQL injection tests
sqlmap -u "http://localhost:8080/api/packages/search?q=test" \
  --batch --random-agent
```

## Running Tests

### Quick Start

```bash
# Run all tests
npm test

# Run specific test suites
npm run test:unit
npm run test:integration
npm run test:e2e

# Run with coverage
npm run test:coverage

# Watch mode for development
npm run test:watch
```

### Test Scripts

```json
{
  "scripts": {
    "test": "npm run test:unit && npm run test:integration",
    "test:unit": "jest --testPathPattern=src",
    "test:integration": "jest --testPathPattern=tests/integration",
    "test:e2e": "playwright test",
    "test:performance": "k6 run tests/performance/load-test.js",
    "test:security": "./tests/security/security-scan.sh",
    "test:coverage": "jest --coverage --coverageReporters=text-lcov | coveralls",
    "test:watch": "jest --watch",
    "test:debug": "node --inspect-brk ./node_modules/.bin/jest --runInBand"
  }
}
```

### Environment Setup

```bash
# .env.test
NODE_ENV=test
DATABASE_URL=sqlite::memory:
REDIS_URL=redis://localhost:6379/1
LOG_LEVEL=error
JWT_SECRET=test-secret-key
PAM_SERVICE=test-pam
```

## Writing Tests

### Test Structure

```javascript
// Follow AAA pattern: Arrange, Act, Assert
describe('Feature Name', () => {
  // Setup
  let testData;
  
  beforeEach(() => {
    testData = createTestData();
  });
  
  afterEach(() => {
    cleanup();
  });

  describe('Sub-feature', () => {
    test('should do something specific', () => {
      // Arrange
      const input = 'test-value';
      
      // Act
      const result = functionUnderTest(input);
      
      // Assert
      expect(result).toBe('expected-value');
    });
  });
});
```

### Testing Best Practices

1. **Descriptive Names**
```javascript
// Bad
test('test1', () => {});

// Good
test('should return user details when valid ID provided', () => {});
```

2. **Single Responsibility**
```javascript
// Bad - testing multiple things
test('user API', () => {
  expect(createUser()).toBeTruthy();
  expect(updateUser()).toBeTruthy();
  expect(deleteUser()).toBeTruthy();
});

// Good - one test per behavior
test('should create user with valid data', () => {});
test('should update existing user', () => {});
test('should delete user by ID', () => {});
```

3. **Test Data Builders**
```javascript
// Create reusable test data
const createTestUser = (overrides = {}) => ({
  username: 'testuser',
  email: 'test@example.com',
  groups: ['wheel'],
  ...overrides
});

test('should authenticate admin user', () => {
  const admin = createTestUser({ groups: ['wheel', 'admin'] });
  expect(authenticate(admin)).toBe(true);
});
```

4. **Async Testing**
```javascript
// Use async/await for clarity
test('should fetch packages', async () => {
  const packages = await packageService.search('firefox');
  expect(packages).toHaveLength(3);
});

// Test error cases
test('should handle API errors', async () => {
  mockAPI.fail();
  await expect(packageService.install('bad-package'))
    .rejects.toThrow('Installation failed');
});
```

## Test Infrastructure

### Mock Services

```javascript
// /tests/mocks/nix-daemon.js
class MockNixDaemon {
  constructor() {
    this.packages = new Map();
  }

  async search(query) {
    // Return predictable test data
    return Array.from(this.packages.values())
      .filter(pkg => pkg.name.includes(query));
  }

  async install(packageName) {
    // Simulate installation
    await delay(100);
    this.packages.set(packageName, {
      name: packageName,
      version: '1.0.0',
      installed: true
    });
  }
}
```

### Test Fixtures

```javascript
// /tests/fixtures/packages.json
{
  "firefox": {
    "name": "firefox",
    "version": "120.0.0",
    "description": "Mozilla Firefox web browser",
    "homepage": "https://firefox.com"
  },
  "chromium": {
    "name": "chromium",
    "version": "119.0.0",
    "description": "Open source web browser",
    "homepage": "https://chromium.org"
  }
}
```

### Test Database

```javascript
// /tests/utils/test-db.js
export async function setupTestDatabase() {
  const db = new Database(':memory:');
  await db.exec(readFileSync('schema.sql', 'utf8'));
  await db.exec(readFileSync('tests/fixtures/test-data.sql', 'utf8'));
  return db;
}

export async function cleanupDatabase(db) {
  await db.close();
}
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      redis:
        image: redis
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run unit tests
        run: npm run test:unit
      
      - name: Run integration tests
        run: npm run test:integration
      
      - name: Run E2E tests
        run: |
          npm run build
          npm start &
          npx wait-on http://localhost:8080
          npm run test:e2e
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Test Reports

```javascript
// jest.config.js
module.exports = {
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  reporters: [
    'default',
    ['jest-junit', {
      outputDirectory: 'test-results',
      outputName: 'junit.xml'
    }]
  ]
};
```

## Manual Testing

### Test Plan Template

```markdown
## Feature: Package Installation

### Prerequisites
- User logged in with admin privileges
- Network connection available

### Test Cases

#### TC001: Search for Package
1. Click on Packages tab
2. Enter "firefox" in search box
3. Press Enter
**Expected**: Firefox appears in results

#### TC002: Install Package
1. Complete TC001
2. Click Install button
3. Confirm installation
**Expected**: Progress bar shows, success message appears

#### TC003: Verify Installation
1. Complete TC002
2. Navigate to Installed tab
**Expected**: Firefox listed as installed
```

### Exploratory Testing

Focus areas for manual exploration:

1. **Edge Cases**
   - Very long package names
   - Special characters in search
   - Rapid clicking
   - Network interruptions

2. **User Experience**
   - Keyboard navigation
   - Screen reader compatibility
   - Mobile responsiveness
   - Dark mode

3. **Performance**
   - Large result sets
   - Concurrent operations
   - Memory usage over time
   - Cache behavior

### Bug Reporting Template

```markdown
## Bug Report

**Summary**: Brief description

**Steps to Reproduce**:
1. Step one
2. Step two
3. Step three

**Expected Result**: What should happen

**Actual Result**: What actually happens

**Environment**:
- OS: NixOS 23.11
- Browser: Firefox 120
- GUI Version: 1.0.0

**Screenshots**: [Attach if applicable]

**Additional Context**: Any other relevant information
```

## Testing Checklist

### Before Release

- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Security scan clean
- [ ] Performance benchmarks met
- [ ] Manual testing completed
- [ ] Accessibility tested
- [ ] Cross-browser tested
- [ ] Documentation updated
- [ ] Changelog updated

### Test Coverage Goals

- Unit Tests: >90% coverage
- Integration Tests: All API endpoints
- E2E Tests: Critical user paths
- Performance: <2s page load
- Security: No high/critical issues

## Debugging Tests

### Debug Mode

```bash
# Run single test in debug mode
node --inspect-brk ./node_modules/.bin/jest path/to/test.js

# Use Chrome DevTools
chrome://inspect
```

### Troubleshooting

**Tests timing out**:
- Increase timeout: `jest.setTimeout(10000)`
- Check for missing await
- Verify mock responses

**Flaky tests**:
- Add explicit waits
- Mock time-dependent code
- Isolate test data

**Coverage gaps**:
- Run coverage report: `npm run test:coverage`
- Focus on critical paths
- Add edge case tests

---

Remember: Good tests enable confident changes. Invest in testing to move fast without breaking things!