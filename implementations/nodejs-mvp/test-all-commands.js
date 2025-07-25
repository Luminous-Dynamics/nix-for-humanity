#!/usr/bin/env node
// Test all 10 MVP commands

const http = require('http');

function testCommand(input) {
  const data = JSON.stringify({
    input: input,
    context: { sessionId: 'test-all' }
  });

  const options = {
    hostname: 'localhost',
    port: 3456,
    path: '/api/nlp/process',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': data.length
    }
  };

  return new Promise((resolve, reject) => {
    const req = http.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        try {
          const response = JSON.parse(body);
          resolve(response);
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

async function runTests() {
  console.log('🧪 Testing All 10 MVP Commands\n');

  const testCases = [
    // Original 5 commands
    { input: 'search firefox', expected: 'search' },
    { input: 'show me what\'s installed', expected: 'list' },
    { input: 'system info', expected: 'info' },
    { input: 'check system health', expected: 'check' },
    { input: 'tell me about nodejs', expected: 'info' },
    
    // New 5 commands
    { input: 'install vim', expected: 'install' },
    { input: 'remove firefox', expected: 'remove' },
    { input: 'update everything', expected: 'update' },
    { input: 'show me updates', expected: 'list-updates' },
    { input: 'clean up my system', expected: 'garbage-collect' }
  ];

  let passed = 0;
  let failed = 0;

  for (const test of testCases) {
    try {
      console.log(`\n📝 Testing: "${test.input}"`);
      const response = await testCommand(test.input);
      
      const actualIntent = response.intent?.action || 'unknown';
      const success = response.success && actualIntent === test.expected;
      
      if (success) {
        console.log(`✅ Success: ${response.message}`);
        if (response.data) {
          console.log(`📊 Data:`, JSON.stringify(response.data, null, 2));
        }
        passed++;
      } else {
        console.log(`❌ Failed: Expected ${test.expected}, got ${actualIntent}`);
        console.log(`📝 Response: ${response.message}`);
        failed++;
      }
    } catch (error) {
      console.log(`❌ Error: ${error.message}`);
      failed++;
    }
  }

  console.log(`\n📊 Results: ${passed}/${testCases.length} tests passed`);
  console.log(`✅ Passed: ${passed}`);
  console.log(`❌ Failed: ${failed}`);
  
  process.exit(failed === 0 ? 0 : 1);
}

// Check if server is running
const req = http.get('http://localhost:3456/api/health', (res) => {
  if (res.statusCode === 200) {
    console.log('✅ Server is running\n');
    runTests();
  }
}).on('error', () => {
  console.log('❌ Server is not running. Start it with: npm start');
  process.exit(1);
});