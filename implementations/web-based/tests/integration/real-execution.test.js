/**
 * Real Command Execution Tests
 * Tests actual NixOS command execution in a safe environment
 */

const { nixWrapper } = require('../../js/nlp/nix-wrapper');
const { intentEngine } = require('../../js/nlp/intent-engine');

describe('Real NixOS Command Execution', () => {
  // Only run these tests when explicitly enabled
  const RUN_REAL_TESTS = process.env.RUN_REAL_EXECUTION_TESTS === 'true';
  
  beforeAll(() => {
    if (!RUN_REAL_TESTS) {
      console.log('Skipping real execution tests. Set RUN_REAL_EXECUTION_TESTS=true to run.');
    }
  });
  
  describe('Safe Query Commands', () => {
    test.skipIf(!RUN_REAL_TESTS)('should list installed packages', async () => {
      const intent = {
        type: 'query',
        confidence: 0.95,
        entities: []
      };
      
      const command = nixWrapper.intentToCommand(intent);
      expect(command).toBeTruthy();
      expect(command.command).toBe('nix-env');
      expect(command.args).toContain('-q');
      
      // Execute real command
      const result = await nixWrapper.execute(command);
      expect(result.success).toBe(true);
      expect(result.output).toBeTruthy();
      expect(result.naturalLanguageResponse).toContain('packages installed');
    });
    
    test.skipIf(!RUN_REAL_TESTS)('should check system logs', async () => {
      const intent = {
        type: 'logs',
        confidence: 0.9,
        entities: [
          { type: 'timeframe', value: 'recent', confidence: 0.85 }
        ]
      };
      
      const command = nixWrapper.intentToCommand(intent);
      expect(command).toBeTruthy();
      expect(command.command).toBe('journalctl');
      
      // Execute real command
      const result = await nixWrapper.execute(command);
      expect(result.success).toBe(true);
      expect(result.output).toBeTruthy();
    });
    
    test.skipIf(!RUN_REAL_TESTS)('should check service status', async () => {
      const intent = {
        type: 'service',
        confidence: 0.92,
        entities: [
          { type: 'action', value: 'status', confidence: 0.9 },
          { type: 'service', value: 'NetworkManager', confidence: 0.88 }
        ]
      };
      
      const command = nixWrapper.intentToCommand(intent);
      expect(command).toBeTruthy();
      expect(command.command).toBe('systemctl');
      expect(command.args).toContain('status');
      expect(command.args).toContain('NetworkManager');
      
      // Execute real command
      const result = await nixWrapper.execute(command);
      expect(result.success).toBe(true);
      expect(result.naturalLanguageResponse).toContain('status of NetworkManager');
    });
  });
  
  describe('Destructive Commands (Safety Tests)', () => {
    test('should reject dangerous commands', async () => {
      // Try to create a command that would delete files
      const dangerousCommand = {
        command: 'rm',
        args: ['-rf', '/tmp/test'],
        requiresSudo: false,
        description: 'Delete test directory'
      };
      
      // This should be rejected by safety validator
      const result = await nixWrapper.execute(dangerousCommand);
      expect(result.success).toBe(false);
      expect(result.error).toContain('safety');
    });
    
    test('should handle permission denied gracefully', async () => {
      // Try to modify system without sudo
      const intent = {
        type: 'service',
        confidence: 0.9,
        entities: [
          { type: 'action', value: 'stop', confidence: 0.9 },
          { type: 'service', value: 'test-service', confidence: 0.85 }
        ]
      };
      
      const command = nixWrapper.intentToCommand(intent);
      // Force it to not use sudo for testing
      command.requiresSudo = false;
      
      const result = await nixWrapper.execute(command);
      // Should fail due to permissions
      expect(result.success).toBe(false);
    });
  });
  
  describe('Command Output Parsing', () => {
    test.skipIf(!RUN_REAL_TESTS)('should parse package list output', async () => {
      const intent = {
        type: 'query',
        confidence: 0.95,
        entities: []
      };
      
      const command = nixWrapper.intentToCommand(intent);
      const result = await nixWrapper.execute(command);
      
      if (result.success && result.output) {
        // Output should be parseable package list
        const lines = result.output.split('\n').filter(line => line.trim());
        lines.forEach(line => {
          // Each line should look like a package
          expect(line).toMatch(/^[a-zA-Z0-9-]+-[\d.]+/);
        });
      }
    });
  });
  
  describe('Natural Language Integration', () => {
    test.skipIf(!RUN_REAL_TESTS)('should handle "show me what\'s installed"', async () => {
      const input = "show me what's installed";
      const intent = intentEngine.recognize(input);
      const command = nixWrapper.intentToCommand(intent);
      const result = await nixWrapper.execute(command);
      
      expect(result.success).toBe(true);
      expect(result.naturalLanguageResponse).toMatch(/You have \d+ packages installed/);
    });
    
    test.skipIf(!RUN_REAL_TESTS)('should handle "check if nginx is running"', async () => {
      const input = "check if nginx is running";
      const intent = intentEngine.recognize(input);
      const command = nixWrapper.intentToCommand(intent);
      const result = await nixWrapper.execute(command);
      
      expect(result.success).toBeDefined();
      expect(result.naturalLanguageResponse).toContain('nginx');
    });
  });
});

// Test utilities for manual testing
if (require.main === module) {
  async function testRealExecution() {
    console.log('Testing real NixOS command execution...\n');
    
    // Test 1: List packages
    console.log('1. Listing installed packages:');
    const listIntent = intentEngine.recognize("show me what's installed");
    const listCommand = nixWrapper.intentToCommand(listIntent);
    const listResult = await nixWrapper.execute(listCommand);
    console.log('Result:', listResult.naturalLanguageResponse);
    console.log('Success:', listResult.success);
    console.log('---\n');
    
    // Test 2: Check logs
    console.log('2. Checking recent logs:');
    const logsIntent = intentEngine.recognize("show me recent logs");
    const logsCommand = nixWrapper.intentToCommand(logsIntent);
    const logsResult = await nixWrapper.execute(logsCommand);
    console.log('Result:', logsResult.naturalLanguageResponse);
    console.log('Output preview:', logsResult.output.substring(0, 200) + '...');
    console.log('---\n');
    
    // Test 3: Service status
    console.log('3. Checking NetworkManager status:');
    const serviceIntent = intentEngine.recognize("is NetworkManager running");
    const serviceCommand = nixWrapper.intentToCommand(serviceIntent);
    const serviceResult = await nixWrapper.execute(serviceCommand);
    console.log('Result:', serviceResult.naturalLanguageResponse);
    console.log('Success:', serviceResult.success);
  }
  
  // Run manual test
  testRealExecution().catch(console.error);
}