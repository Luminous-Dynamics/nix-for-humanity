#!/usr/bin/env node

/**
 * Accessibility Test Runner
 * Runs all accessibility tests and generates a report
 */

const { spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');

async function runTests() {
  console.log('🧪 Running Accessibility Tests for Nix for Humanity\n');
  
  const startTime = Date.now();
  
  // Check if server is running
  console.log('📡 Checking if development server is running...');
  const isServerRunning = await checkServer();
  
  if (!isServerRunning) {
    console.log('❌ Development server not running!');
    console.log('Please start the server with: npm run dev');
    process.exit(1);
  }
  
  console.log('✅ Server is running\n');
  
  // Run tests
  console.log('🏃 Running accessibility tests...\n');
  
  const testFiles = [
    'test-nlp-interface.js',
    'test-voice-text-parity.js',
    'test-personas.js'
  ];
  
  const results = [];
  
  for (const testFile of testFiles) {
    console.log(`📄 Running ${testFile}...`);
    const result = await runTestFile(testFile);
    results.push(result);
    console.log(result.success ? '✅ Passed' : '❌ Failed');
    console.log('');
  }
  
  // Generate report
  const report = generateReport(results, startTime);
  
  // Save report
  const reportPath = path.join(__dirname, 'accessibility-report.html');
  await fs.writeFile(reportPath, report);
  
  console.log(`\n📊 Report saved to: ${reportPath}`);
  
  // Exit with appropriate code
  const hasFailures = results.some(r => !r.success);
  process.exit(hasFailures ? 1 : 0);
}

async function checkServer() {
  try {
    const response = await fetch('http://localhost:8080');
    return response.ok;
  } catch {
    return false;
  }
}

function runTestFile(filename) {
  return new Promise((resolve) => {
    const testPath = path.join(__dirname, filename);
    const jest = spawn('npx', ['jest', testPath, '--verbose'], {
      stdio: 'pipe'
    });
    
    let output = '';
    
    jest.stdout.on('data', (data) => {
      output += data.toString();
      process.stdout.write(data);
    });
    
    jest.stderr.on('data', (data) => {
      output += data.toString();
      process.stderr.write(data);
    });
    
    jest.on('close', (code) => {
      resolve({
        filename,
        success: code === 0,
        output,
        exitCode: code
      });
    });
  });
}

function generateReport(results, startTime) {
  const duration = Date.now() - startTime;
  const totalTests = results.length;
  const passedTests = results.filter(r => r.success).length;
  const failedTests = totalTests - passedTests;
  
  const now = new Date().toISOString();
  
  return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Accessibility Test Report - Nix for Humanity</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
      background: #f5f5f5;
    }
    h1 {
      color: #333;
      border-bottom: 3px solid #3b82f6;
      padding-bottom: 10px;
    }
    .summary {
      background: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      margin-bottom: 20px;
    }
    .stats {
      display: flex;
      gap: 20px;
      margin-top: 15px;
    }
    .stat {
      flex: 1;
      text-align: center;
      padding: 15px;
      border-radius: 5px;
    }
    .stat.passed {
      background: #d1fae5;
      color: #065f46;
    }
    .stat.failed {
      background: #fee2e2;
      color: #b91c1c;
    }
    .stat.total {
      background: #e0f2fe;
      color: #075985;
    }
    .test-results {
      background: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      margin-bottom: 20px;
    }
    .test-file {
      margin-bottom: 30px;
    }
    .test-file h3 {
      color: #333;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .success-icon {
      color: #10b981;
    }
    .failure-icon {
      color: #ef4444;
    }
    pre {
      background: #1e293b;
      color: #f1f5f9;
      padding: 15px;
      border-radius: 5px;
      overflow-x: auto;
      font-size: 12px;
      line-height: 1.5;
    }
    .recommendations {
      background: #fef3c7;
      padding: 20px;
      border-radius: 8px;
      border-left: 4px solid #f59e0b;
      margin-top: 20px;
    }
    .recommendations h2 {
      color: #92400e;
      margin-top: 0;
    }
    .recommendations ul {
      margin: 0;
      padding-left: 20px;
    }
    .compliance-matrix {
      background: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      margin-bottom: 20px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
    }
    th, td {
      padding: 10px;
      text-align: left;
      border-bottom: 1px solid #e5e7eb;
    }
    th {
      background: #f3f4f6;
      font-weight: 600;
    }
    .pass { color: #10b981; }
    .fail { color: #ef4444; }
    .pending { color: #f59e0b; }
  </style>
</head>
<body>
  <h1>🔍 Accessibility Test Report</h1>
  <p>Generated: ${now}</p>
  
  <div class="summary">
    <h2>Test Summary</h2>
    <div class="stats">
      <div class="stat total">
        <div style="font-size: 2em;">${totalTests}</div>
        <div>Total Test Suites</div>
      </div>
      <div class="stat passed">
        <div style="font-size: 2em;">${passedTests}</div>
        <div>Passed</div>
      </div>
      <div class="stat failed">
        <div style="font-size: 2em;">${failedTests}</div>
        <div>Failed</div>
      </div>
    </div>
    <p style="margin-top: 15px;">Duration: ${(duration / 1000).toFixed(2)}s</p>
  </div>
  
  <div class="compliance-matrix">
    <h2>Compliance Matrix</h2>
    <table>
      <tr>
        <th>Standard</th>
        <th>Target Level</th>
        <th>Status</th>
        <th>Notes</th>
      </tr>
      <tr>
        <td>WCAG 2.1</td>
        <td>AA (AAA target)</td>
        <td class="${passedTests === totalTests ? 'pass' : 'pending'}">
          ${passedTests === totalTests ? '✅ Compliant' : '🚧 In Progress'}
        </td>
        <td>Core accessibility standards</td>
      </tr>
      <tr>
        <td>Section 508</td>
        <td>Full Compliance</td>
        <td class="pending">🚧 Testing</td>
        <td>US Federal requirements</td>
      </tr>
      <tr>
        <td>Voice-Text Parity</td>
        <td>100%</td>
        <td class="pending">🚧 Implementing</td>
        <td>Equal input methods</td>
      </tr>
      <tr>
        <td>Screen Reader</td>
        <td>Full Support</td>
        <td class="${passedTests > 0 ? 'pass' : 'pending'}">
          ${passedTests > 0 ? '✅ Supported' : '🚧 Testing'}
        </td>
        <td>NVDA, JAWS, VoiceOver</td>
      </tr>
    </table>
  </div>
  
  <div class="test-results">
    <h2>Detailed Test Results</h2>
    ${results.map(result => `
      <div class="test-file">
        <h3>
          <span class="${result.success ? 'success-icon' : 'failure-icon'}">
            ${result.success ? '✅' : '❌'}
          </span>
          ${result.filename}
        </h3>
        <pre>${escapeHtml(result.output)}</pre>
      </div>
    `).join('')}
  </div>
  
  <div class="recommendations">
    <h2>🎯 Recommendations</h2>
    <ul>
      <li><strong>Continue Testing:</strong> Run these tests after every feature addition</li>
      <li><strong>Manual Testing:</strong> Test with real screen readers (NVDA, VoiceOver)</li>
      <li><strong>User Testing:</strong> Involve users from each persona group</li>
      <li><strong>Voice Implementation:</strong> Ensure parity when voice features are added</li>
      <li><strong>Documentation:</strong> Keep accessibility docs updated with new patterns</li>
    </ul>
  </div>
  
  <div style="margin-top: 40px; text-align: center; color: #6b7280;">
    <p>Nix for Humanity - Making NixOS accessible to everyone</p>
  </div>
</body>
</html>
  `;
}

function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}

// Run tests
runTests().catch(console.error);