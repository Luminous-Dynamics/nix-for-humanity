#!/usr/bin/env node

/**
 * Safe Test Script for Nix for Humanity
 * Tests the complete pipeline with safe operations only
 */

const NLPService = require('./implementations/nlp/nlp-service');
const EnhancedCommandExecutor = require('./implementations/core/command-executor-enhanced');
const { ValidationService } = require('./implementations/security/validation-service');
const ErrorHandler = require('./implementations/security/error-handler');

async function runSafeTests() {
  console.log('🧪 Nix for Humanity - Safe Execution Tests\n');
  
  // Initialize services
  const nlp = new NLPService();
  const executor = new EnhancedCommandExecutor();
  const validator = new ValidationService();
  const errorHandler = new ErrorHandler();
  
  // Test cases (all safe - search/dry-run only)
  const testCases = [
    {
      name: 'Search for package',
      input: 'search for firefox',
      safe: true
    },
    {
      name: 'Natural language search',
      input: 'find me a web browser',
      safe: true
    },
    {
      name: 'Install with dry-run',
      input: 'install hello',
      options: { dryRun: true },
      safe: true
    },
    {
      name: 'Complex natural language',
      input: 'i need something to edit text files',
      safe: true
    },
    {
      name: 'Typo correction',
      input: 'install firfox',
      options: { dryRun: true },
      safe: true
    }
  ];
  
  for (const testCase of testCases) {
    console.log(`\n📝 Test: ${testCase.name}`);
    console.log(`   Input: "${testCase.input}"`);
    
    try {
      // Step 1: Process natural language
      console.log('   🧠 Processing natural language...');
      const intent = await nlp.processInput(testCase.input);
      console.log(`   ✓ Intent: ${intent.type} (confidence: ${(intent.confidence * 100).toFixed(1)}%)`);
      
      if (intent.entities?.packages?.length > 0) {
        console.log(`   ✓ Package: ${intent.entities.packages[0]}`);
      }
      
      // Step 2: Build command
      console.log('   🔨 Building command...');
      let command;
      
      switch (intent.type) {
        case 'search':
          command = {
            command: 'nix',
            args: ['search', 'nixpkgs', intent.entities?.packages?.[0] || intent.matches?.query || 'firefox']
          };
          break;
          
        case 'install':
          const pkg = intent.entities?.packages?.[0] || intent.matches?.package || 'hello';
          command = {
            command: 'nix',
            args: ['search', 'nixpkgs', pkg] // Search instead of install for safety
          };
          console.log(`   ℹ️  Using search instead of install for safety`);
          break;
          
        default:
          console.log(`   ⚠️  Unknown intent: ${intent.type}`);
          continue;
      }
      
      // Step 3: Validate command
      console.log('   🛡️  Validating command...');
      const validated = validator.sanitizeCommand(command.command, command.args);
      console.log(`   ✓ Command: ${validated.command} ${validated.args.join(' ')}`);
      
      // Step 4: Execute safely
      console.log('   🚀 Executing (safe mode)...');
      const startTime = Date.now();
      
      const result = await executor.execute(validated, {
        ...testCase.options,
        onProgress: (progress) => {
          if (progress.type === 'start') {
            console.log(`   ⏱️  ${progress.message}`);
          } else if (progress.message) {
            console.log(`   📊 ${progress.message}`);
          }
        }
      });
      
      const duration = Date.now() - startTime;
      
      if (result.success) {
        console.log(`   ✅ Success! (${duration}ms)`);
        
        // Parse and display search results
        if (command.args.includes('search')) {
          try {
            const packages = JSON.parse(result.output);
            const packageNames = Object.keys(packages).slice(0, 3);
            if (packageNames.length > 0) {
              console.log(`   📦 Found packages:`);
              packageNames.forEach(name => {
                const shortName = name.replace(/.*\./, '');
                console.log(`      - ${shortName}`);
              });
            }
          } catch (e) {
            // Not JSON, just show a snippet
            const lines = result.output.split('\n').filter(l => l.trim()).slice(0, 3);
            lines.forEach(line => console.log(`      ${line.substring(0, 60)}...`));
          }
        }
      } else {
        console.log(`   ❌ Failed: ${result.error}`);
        
        // Show user-friendly error
        const userError = errorHandler.handle(new Error(result.error), {
          operation: intent.type,
          target: intent.entities?.packages?>[0]
        });
        
        console.log(`   💡 ${userError.message}`);
        if (userError.suggestion) {
          console.log(`   💡 ${userError.suggestion}`);
        }
      }
      
    } catch (error) {
      console.log(`   ❌ Error: ${error.message}`);
    }
  }
  
  console.log('\n\n✨ Safe tests completed!\n');
  console.log('Next steps:');
  console.log('1. Test with actual package installation (in a VM or with explicit confirmation)');
  console.log('2. Test timeout handling with large packages');
  console.log('3. Test progress monitoring with real operations');
  console.log('4. Integrate with the secure server\n');
}

// Run tests
runSafeTests().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});