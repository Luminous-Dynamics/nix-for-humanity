/**
 * Jest configuration for accessibility tests
 */

module.exports = {
  displayName: 'Accessibility Tests',
  testEnvironment: 'node',
  testMatch: [
    '<rootDir>/tests/accessibility/test-*.js'
  ],
  setupFilesAfterEnv: [
    '<rootDir>/tests/accessibility/setup.js'
  ],
  testTimeout: 30000, // Puppeteer tests need more time
  verbose: true,
  reporters: [
    'default',
    ['jest-html-reporter', {
      pageTitle: 'Nix for Humanity - Accessibility Test Report',
      outputPath: 'tests/accessibility/jest-report.html',
      includeFailureMsg: true,
      includeConsoleLog: true
    }]
  ]
};