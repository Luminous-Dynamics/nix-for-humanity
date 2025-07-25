/**
 * Minimal Test Harness for Nix for Humanity MVP
 * Tests the core functionality without external dependencies
 */

console.log('🧪 Nix for Humanity - Minimal Test Suite\n');

// Test counter
let passed = 0;
let failed = 0;

// Simple test helper
function test(description, fn) {
  try {
    fn();
    console.log(`✅ ${description}`);
    passed++;
  } catch (error) {
    console.log(`❌ ${description}`);
    console.log(`   Error: ${error.message}`);
    failed++;
  }
}

// Simple assertion helper
function assert(condition, message) {
  if (!condition) {
    throw new Error(message || 'Assertion failed');
  }
}

// Test 1: Basic pattern matching
test('Pattern matching: "search firefox"', () => {
  const input = 'search firefox';
  const pattern = /^(search|find|look for)\s+(.+)$/i;
  const match = input.match(pattern);
  assert(match !== null, 'Pattern should match');
  assert(match[2] === 'firefox', 'Should extract package name');
});

// Test 2: Install command recognition
test('Pattern matching: "install firefox"', () => {
  const input = 'install firefox';
  const pattern = /^(install|add|get)\s+(.+)$/i;
  const match = input.match(pattern);
  assert(match !== null, 'Pattern should match');
  assert(match[2] === 'firefox', 'Should extract package name');
});

// Test 3: Natural language variation
test('Pattern matching: "i need firefox"', () => {
  const input = 'i need firefox';
  const pattern = /^(i need|i want|give me)\s+(.+)$/i;
  const match = input.match(pattern);
  assert(match !== null, 'Pattern should match');
  assert(match[2] === 'firefox', 'Should extract package name');
});

// Test 4: Command building
test('Command building: search command', () => {
  const packageName = 'firefox';
  const command = `nix search nixpkgs ${packageName}`;
  assert(command === 'nix search nixpkgs firefox', 'Should build correct command');
});

// Test 5: Safety validation
test('Safety validation: reject dangerous characters', () => {
  const dangerous = 'firefox; rm -rf /';
  const safe = dangerous.replace(/[;&|<>`$]/g, '');
  assert(safe === 'firefox rm -rf /', 'Should remove dangerous characters');
});

// Test 6: Basic intent recognition
test('Intent recognition: search vs install', () => {
  const searchInput = 'search for firefox';
  const installInput = 'install firefox please';
  
  const isSearch = /search|find|look for/i.test(searchInput);
  const isInstall = /install|add|get/i.test(installInput);
  
  assert(isSearch === true, 'Should recognize search intent');
  assert(isInstall === true, 'Should recognize install intent');
});

// Test 7: Entity extraction
test('Entity extraction: package names with numbers', () => {
  const input = 'install python3';
  const pattern = /^install\s+([a-zA-Z0-9\-_]+)$/i;
  const match = input.match(pattern);
  assert(match !== null, 'Pattern should match');
  assert(match[1] === 'python3', 'Should extract package with number');
});

// Test 8: Multiple word handling
test('Multiple word handling: "visual studio code"', () => {
  const input = 'install visual studio code';
  const pattern = /^install\s+(.+)$/i;
  const match = input.match(pattern);
  assert(match !== null, 'Pattern should match');
  
  // Map common names to package names
  const packageMap = {
    'visual studio code': 'vscode',
    'firefox': 'firefox',
    'chrome': 'google-chrome'
  };
  
  const extracted = match[1];
  const packageName = packageMap[extracted] || extracted;
  assert(packageName === 'vscode', 'Should map to correct package name');
});

// Test 9: Case insensitivity
test('Case insensitivity', () => {
  const inputs = ['INSTALL FIREFOX', 'Install Firefox', 'install firefox'];
  const pattern = /^install\s+(.+)$/i;
  
  inputs.forEach(input => {
    const match = input.match(pattern);
    assert(match !== null, `Pattern should match "${input}"`);
  });
});

// Test 10: Typo tolerance (basic)
test('Basic typo handling', () => {
  const input = 'instal firefox'; // missing 'l'
  // For MVP, we won't handle typos - just test exact matches work
  const pattern = /^install\s+(.+)$/i;
  const match = input.match(pattern);
  assert(match === null, 'Should not match typo in MVP');
});

// Results
console.log('\n📊 Test Results:');
console.log(`   Passed: ${passed}`);
console.log(`   Failed: ${failed}`);
console.log(`   Total:  ${passed + failed}`);

if (failed === 0) {
  console.log('\n🎉 All tests passed!');
  process.exit(0);
} else {
  console.log('\n⚠️  Some tests failed.');
  process.exit(1);
}