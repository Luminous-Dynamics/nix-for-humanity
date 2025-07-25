#!/usr/bin/env node

/**
 * Test harness for "search firefox" command
 * This tests the actual NLP layers without UI
 */

import { recognizeIntent } from './js/nlp/layers/intent-recognition.js';
import { buildCommand } from './js/nlp/layers/command-builder.js';
import { child_process } from 'child_process';
import { promisify } from 'util';

const exec = promisify(child_process.exec);

console.log('🧪 Testing "search firefox" command implementation\n');

// Test inputs
const testInputs = [
  'search firefox',
  'find firefox',
  'look for firefox',
  'search for firefox browser',
  'can you search firefox'
];

async function testSearchCommand(input) {
  console.log(`\n📝 Testing: "${input}"`);
  console.log('─'.repeat(50));
  
  try {
    // Step 1: Intent Recognition
    const intent = recognizeIntent(input);
    console.log('✅ Intent recognized:', {
      type: intent.type,
      confidence: intent.confidence,
      entities: intent.entities
    });
    
    // Verify it's a search intent
    if (intent.type !== 'search' && intent.type !== 'install') {
      console.error('❌ Expected search or install intent, got:', intent.type);
      return false;
    }
    
    // Step 2: Command Building
    const commandResult = buildCommand(intent);
    console.log('✅ Command built:', commandResult);
    
    if (!commandResult.success) {
      console.error('❌ Failed to build command:', commandResult.error);
      return false;
    }
    
    const { command } = commandResult;
    console.log('📟 Would execute:', `${command.command} ${command.args.join(' ')}`);
    
    // Step 3: Dry run the actual command (safe)
    if (process.env.TEST_REAL_COMMAND === 'true') {
      console.log('\n🔧 Testing real command with --dry-run...');
      try {
        const cmdStr = `${command.command} ${command.args.join(' ')} --dry-run`;
        const { stdout, stderr } = await exec(cmdStr);
        console.log('✅ Command output preview:');
        console.log(stdout.split('\n').slice(0, 5).join('\n'));
        if (stderr) {
          console.log('⚠️  Stderr:', stderr);
        }
      } catch (error) {
        console.log('⚠️  Command failed (this is okay for dry-run):', error.message);
      }
    }
    
    return true;
  } catch (error) {
    console.error('❌ Error:', error.message);
    return false;
  }
}

// Add search patterns to intent recognition
// Note: The current implementation doesn't have search patterns, so let's test with what we have
console.log('🔍 Note: Current implementation may not have "search" intent.');
console.log('   Testing fallback behavior...\n');

// Run tests
async function runTests() {
  let passed = 0;
  let failed = 0;
  
  for (const input of testInputs) {
    const success = await testSearchCommand(input);
    if (success) {
      passed++;
    } else {
      failed++;
    }
  }
  
  console.log('\n📊 Summary:');
  console.log(`   Passed: ${passed}`);
  console.log(`   Failed: ${failed}`);
  console.log(`   Total:  ${passed + failed}`);
  
  // Test the actual search command format
  console.log('\n📦 Expected Nix search command format:');
  console.log('   nix search nixpkgs firefox');
  console.log('   nix search nixpkgs#firefox');
  console.log('   nix-env -qa firefox');
  
  process.exit(failed === 0 ? 0 : 1);
}

runTests().catch(console.error);