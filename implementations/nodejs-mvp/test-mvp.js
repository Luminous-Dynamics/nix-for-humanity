#!/usr/bin/env node
// Quick test script for Nix for Humanity MVP

const http = require('http');

function testCommand(input) {
  const data = JSON.stringify({
    input: input,
    context: {
      sessionId: 'test-session'
    }
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
  console.log('🧪 Testing Nix for Humanity MVP\n');

  const testCases = [
    'search firefox',
    'show me what\'s installed',
    'system info',
    'check system health',
    'tell me about nodejs'
  ];

  for (const input of testCases) {
    try {
      console.log(`Testing: "${input}"`);
      const response = await testCommand(input);
      console.log(`✅ Success: ${response.success}`);
      console.log(`📝 Message: ${response.message}`);
      if (response.data) {
        console.log(`📊 Data:`, JSON.stringify(response.data, null, 2));
      }
      console.log('---\n');
    } catch (error) {
      console.log(`❌ Error: ${error.message}\n`);
    }
  }
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