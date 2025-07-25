#!/usr/bin/env node
/**
 * Quick Security Check for Nix for Humanity
 * Run this before VM testing to catch obvious issues
 */

const fs = require('fs');
const path = require('path');

console.log('🔒 Nix for Humanity - Quick Security Check\n');

const issues = [];
const warnings = [];
const passed = [];

// Check 1: Command whitelist in nix-executor.js
console.log('Checking command whitelist...');
try {
    const executorCode = fs.readFileSync(
        path.join(__dirname, '../backend/nix-executor.js'), 
        'utf8'
    );
    
    if (executorCode.includes('allowedCommands')) {
        const whitelist = executorCode.match(/allowedCommands\s*=\s*\[([\s\S]*?)\]/);
        if (whitelist) {
            const commands = whitelist[1].match(/'([^']+)'/g) || [];
            const dangerous = ['rm', 'sudo', 'chmod', 'chown', 'dd', 'mkfs'];
            const found = dangerous.filter(cmd => 
                commands.some(allowed => allowed.includes(cmd))
            );
            
            if (found.length > 0) {
                issues.push(`Dangerous commands in whitelist: ${found.join(', ')}`);
            } else {
                passed.push('Command whitelist looks safe');
            }
        }
    } else {
        issues.push('No command whitelist found!');
    }
} catch (e) {
    issues.push('Could not check nix-executor.js');
}

// Check 2: Dangerous flag prevention
console.log('Checking dangerous flag prevention...');
try {
    const executorCode = fs.readFileSync(
        path.join(__dirname, '../backend/nix-executor.js'), 
        'utf8'
    );
    
    if (executorCode.includes('dangerousFlags')) {
        passed.push('Dangerous flag checking implemented');
    } else {
        warnings.push('No explicit dangerous flag checking found');
    }
} catch (e) {
    warnings.push('Could not verify flag checking');
}

// Check 3: Sandbox configuration
console.log('Checking sandbox configuration...');
try {
    const files = [
        'nix-executor.js',
        'realtime-server.js',
        'system-monitor.js'
    ];
    
    let sandboxIssues = false;
    files.forEach(file => {
        try {
            const code = fs.readFileSync(
                path.join(__dirname, '../backend/', file), 
                'utf8'
            );
            
            if (code.includes('/tmp/daemon') || 
                code.includes('extra-sandbox-paths')) {
                issues.push(`${file} may expose sandbox paths`);
                sandboxIssues = true;
            }
        } catch (e) {
            // File might not exist
        }
    });
    
    if (!sandboxIssues) {
        passed.push('No sandbox exposure detected');
    }
} catch (e) {
    warnings.push('Could not check sandbox configuration');
}

// Check 4: Input validation
console.log('Checking input validation...');
try {
    const patterns = fs.readFileSync(
        path.join(__dirname, '../js/nlp/intent-patterns.ts'), 
        'utf8'
    );
    
    // Check for command injection patterns
    const dangerousPatterns = [';', '&&', '||', '`', '$', '>', '<', '|'];
    const hasValidation = dangerousPatterns.some(pattern => 
        patterns.includes(`'${pattern}'`) || patterns.includes(`"${pattern}"`)
    );
    
    if (!hasValidation) {
        warnings.push('No explicit command injection pattern checking');
    } else {
        passed.push('Input validation patterns found');
    }
} catch (e) {
    warnings.push('Could not check intent patterns');
}

// Check 5: Resource limits
console.log('Checking resource limits...');
try {
    const serverCode = fs.readFileSync(
        path.join(__dirname, '../backend/realtime-server.js'), 
        'utf8'
    );
    
    if (!serverCode.includes('rateLimit') && !serverCode.includes('rate-limit')) {
        issues.push('No rate limiting found in server');
    } else {
        passed.push('Rate limiting implemented');
    }
} catch (e) {
    warnings.push('Could not check rate limiting');
}

// Check 6: Error message leakage
console.log('Checking error handling...');
try {
    const backendFiles = fs.readdirSync(path.join(__dirname, '../backend/'))
        .filter(f => f.endsWith('.js'));
    
    let stackTraceLeaks = 0;
    backendFiles.forEach(file => {
        try {
            const code = fs.readFileSync(
                path.join(__dirname, '../backend/', file), 
                'utf8'
            );
            
            if (code.includes('error.stack') && !code.includes('console.error')) {
                stackTraceLeaks++;
                warnings.push(`${file} may leak stack traces to users`);
            }
        } catch (e) {
            // Skip
        }
    });
    
    if (stackTraceLeaks === 0) {
        passed.push('No stack trace leakage detected');
    }
} catch (e) {
    warnings.push('Could not check error handling');
}

// Check 7: Secrets in code
console.log('Checking for hardcoded secrets...');
try {
    const allFiles = [
        ...fs.readdirSync(path.join(__dirname, '../')).filter(f => f.endsWith('.js')),
        ...fs.readdirSync(path.join(__dirname, '../backend/')).filter(f => f.endsWith('.js'))
    ];
    
    const secretPatterns = [
        /api[_-]?key\s*[:=]\s*["'][^"']+["']/gi,
        /password\s*[:=]\s*["'][^"']+["']/gi,
        /secret\s*[:=]\s*["'][^"']+["']/gi,
        /token\s*[:=]\s*["'][^"']+["']/gi
    ];
    
    let secretsFound = false;
    allFiles.forEach(file => {
        try {
            const code = fs.readFileSync(
                path.join(__dirname, '../', file), 
                'utf8'
            );
            
            secretPatterns.forEach(pattern => {
                if (pattern.test(code)) {
                    issues.push(`Possible hardcoded secret in ${file}`);
                    secretsFound = true;
                }
            });
        } catch (e) {
            // Skip
        }
    });
    
    if (!secretsFound) {
        passed.push('No hardcoded secrets found');
    }
} catch (e) {
    warnings.push('Could not check for secrets');
}

// Summary
console.log('\n📊 Security Check Summary\n');

if (passed.length > 0) {
    console.log('✅ Passed Checks:');
    passed.forEach(p => console.log(`   - ${p}`));
    console.log();
}

if (warnings.length > 0) {
    console.log('⚠️  Warnings:');
    warnings.forEach(w => console.log(`   - ${w}`));
    console.log();
}

if (issues.length > 0) {
    console.log('❌ Critical Issues:');
    issues.forEach(i => console.log(`   - ${i}`));
    console.log();
}

// Generate simple config for testing
const testConfig = {
    security: {
        dryRun: true,
        commandWhitelist: ['nix-env', 'nix', 'nix-channel'],
        maxConcurrent: 5,
        rateLimit: {
            window: 60000,
            max: 100
        },
        sandbox: {
            enabled: true,
            extraPaths: []
        }
    }
};

fs.writeFileSync(
    path.join(__dirname, 'recommended-test-config.json'),
    JSON.stringify(testConfig, null, 2)
);

// Exit status
if (issues.length > 0) {
    console.log('❌ FAIL: Critical security issues found!');
    console.log('Fix these before running VM tests.\n');
    process.exit(1);
} else if (warnings.length > 0) {
    console.log('⚠️  PASS WITH WARNINGS');
    console.log('Review warnings before production use.\n');
    process.exit(0);
} else {
    console.log('✅ PASS: No critical security issues found!');
    console.log('Ready for VM testing.\n');
    process.exit(0);
}