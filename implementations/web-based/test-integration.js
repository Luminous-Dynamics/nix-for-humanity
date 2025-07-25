#!/usr/bin/env node

/**
 * Integration test for search command
 * Tests the full flow without UI
 */

import { recognizeIntent } from './js/nlp/layers/intent-recognition.js';
import { buildCommand } from './js/nlp/layers/command-builder.js';

console.log('🧪 Integration Test: "search firefox" command\n');

function testSearchFlow(input) {
  console.log(`\nTesting: "${input}"`);
  console.log('─'.repeat(50));
  
  try {
    // Step 1: Intent Recognition
    const intent = recognizeIntent(input);
    console.log('1️⃣ Intent Recognition:');
    console.log(`   Type: ${intent.type}`);
    console.log(`   Confidence: ${intent.confidence}`);
    console.log(`   Entities:`, intent.entities);
    
    // Step 2: Command Building
    const commandResult = buildCommand(intent);
    console.log('\n2️⃣ Command Building:');
    console.log(`   Success: ${commandResult.success}`);
    
    if (commandResult.success && commandResult.command) {
      const { command } = commandResult;
      console.log(`   Command: ${command.command}`);
      console.log(`   Args: ${command.args.join(' ')}`);
      console.log(`   Full: ${command.command} ${command.args.join(' ')}`);
      console.log(`   Description: ${command.description}`);
      console.log(`   Requires sudo: ${command.requiresSudo}`);
      console.log(`   Requires confirmation: ${command.requiresConfirmation}`);
    } else {
      console.log(`   Error: ${commandResult.error}`);
      console.log(`   Suggestion: ${commandResult.suggestion}`);
    }
    
    return commandResult.success;
  } catch (error) {
    console.error('❌ Error:', error.message);
    console.error(error.stack);
    return false;
  }
}

// Test various search inputs
const testCases = [
  'search firefox',
  'find firefox',
  'look for firefox',
  'search for firefox',
  'can you search firefox',
  'show me firefox packages',
  'what packages are available for python'
];

console.log('Running integration tests...\n');

let passed = 0;
let failed = 0;

for (const testCase of testCases) {
  if (testSearchFlow(testCase)) {
    passed++;
  } else {
    failed++;
  }
}

console.log('\n' + '═'.repeat(50));
console.log('📊 Test Results:');
console.log(`   ✅ Passed: ${passed}`);
console.log(`   ❌ Failed: ${failed}`);
console.log(`   📝 Total:  ${passed + failed}`);

// Show expected output
console.log('\n📦 Expected Command:');
console.log('   nix search nixpkgs firefox');
console.log('\n💡 This command will search the nixpkgs repository for packages');
console.log('   matching "firefox" and display available options.');

process.exit(failed === 0 ? 0 : 1);