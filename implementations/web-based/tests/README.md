# NixOS GUI Test Suite

Comprehensive test coverage for the NixOS GUI application, including unit tests, integration tests, and end-to-end tests.

## Test Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── auth-manager.test.js
│   ├── contextual-help.test.js
│   ├── error-handler.test.js
│   ├── plugin-system.test.js
│   ├── shortcut-helper.test.js
│   └── tour-manager.test.js
├── integration/             # Integration tests for API and services
│   └── api.test.js
├── e2e/                    # End-to-end tests for complete workflows
│   ├── full-flow.test.js
│   └── performance.test.js
├── setup.js                # Jest setup and configuration
└── README.md              # This file
```

## Running Tests

### Run All Tests
```bash
npm test
# or
./scripts/run-tests.sh
```

### Run Specific Test Suites
```bash
# Unit tests only
npm run test:unit

# Integration tests only
npm run test:integration

# E2E tests only
npm run test:e2e

# All tests with coverage
npm run test:coverage
```

### Watch Mode (for development)
```bash
npm run test:watch
```

### Generate Coverage Report
```bash
npm run test:coverage
# View report: open coverage/lcov-report/index.html
```

## Test Categories

### Unit Tests
- **Purpose**: Test individual components in isolation
- **Scope**: Single functions, classes, or modules
- **Dependencies**: Mocked
- **Speed**: Fast (< 100ms per test)

#### Components Tested:
- **ErrorHandler**: Error handling, recovery suggestions, UI updates
- **ContextualHelp**: Tooltip display, content loading, positioning
- **TourManager**: Tour lifecycle, step navigation, persistence
- **ShortcutHelper**: Key bindings, conflict detection, customization
- **PluginSystem**: Plugin loading, validation, sandboxing, API
- **AuthManager**: Authentication, token management, authorization

### Integration Tests
- **Purpose**: Test interaction between multiple components
- **Scope**: API endpoints, service integration
- **Dependencies**: Some real, some mocked
- **Speed**: Medium (100ms - 1s per test)

#### Areas Tested:
- Authentication flow with backend
- Package management operations
- Service control and monitoring
- Configuration file handling
- WebSocket communication
- Rate limiting and security

### End-to-End Tests
- **Purpose**: Test complete user workflows
- **Scope**: Full application features
- **Dependencies**: Real browser and server
- **Speed**: Slow (1s - 10s per test)

#### Workflows Tested:
- Complete authentication flow
- Package search, install, and removal
- Service management operations
- Configuration editing and validation
- Help system interaction
- Plugin installation and usage
- Performance metrics (Core Web Vitals)

## Test Coverage

Current coverage thresholds:
- **Statements**: 70%
- **Branches**: 70%
- **Functions**: 70%
- **Lines**: 70%

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Clear Names**: Use descriptive test names that explain what is being tested
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Mock External Dependencies**: Don't make real API calls in unit tests
5. **Test Edge Cases**: Include error scenarios and boundary conditions
6. **Keep Tests Fast**: Optimize slow tests or move to E2E suite
7. **Maintain Tests**: Update tests when features change