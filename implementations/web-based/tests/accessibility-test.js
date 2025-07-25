/**
 * Accessibility Testing for NixOS GUI v2
 * Tests WCAG 2.1 AA compliance
 */

const puppeteer = require('puppeteer');
const { AxePuppeteer } = require('@axe-core/puppeteer');

async function runAccessibilityTests() {
    console.log('🔍 Running Accessibility Tests...\n');
    
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    
    // Test at different viewport sizes
    const viewports = [
        { name: 'Desktop', width: 1920, height: 1080 },
        { name: 'Tablet', width: 768, height: 1024 },
        { name: 'Mobile', width: 375, height: 667 }
    ];
    
    const results = [];
    
    for (const viewport of viewports) {
        console.log(`Testing ${viewport.name} (${viewport.width}x${viewport.height})...`);
        
        await page.setViewport(viewport);
        await page.goto('file://' + __dirname + '/../index.html');
        
        // Run axe accessibility tests
        const axeResults = await new AxePuppeteer(page).analyze();
        
        // Test keyboard navigation
        const keyboardTests = await testKeyboardNavigation(page);
        
        // Test screen reader compatibility
        const screenReaderTests = await testScreenReader(page);
        
        results.push({
            viewport: viewport.name,
            violations: axeResults.violations,
            keyboardTests,
            screenReaderTests
        });
    }
    
    await browser.close();
    
    // Generate report
    generateReport(results);
}

async function testKeyboardNavigation(page) {
    const tests = [];
    
    // Test 1: Tab navigation
    await page.keyboard.press('Tab');
    const focusedElement = await page.evaluate(() => document.activeElement.id);
    tests.push({
        name: 'Tab to search box',
        passed: focusedElement === 'searchBox',
        actual: focusedElement
    });
    
    // Test 2: Enter key submission
    await page.type('#searchBox', 'test command');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(100);
    
    const responseVisible = await page.evaluate(() => {
        const response = document.getElementById('response');
        return response.classList.contains('visible');
    });
    tests.push({
        name: 'Enter key processes command',
        passed: responseVisible
    });
    
    // Test 3: Escape key clears
    await page.keyboard.press('Escape');
    const inputCleared = await page.evaluate(() => {
        return document.getElementById('searchBox').value === '';
    });
    tests.push({
        name: 'Escape key clears input',
        passed: inputCleared
    });
    
    // Test 4: Focus indicators
    const focusVisible = await page.evaluate(() => {
        const style = window.getComputedStyle(document.activeElement);
        return style.outlineStyle !== 'none';
    });
    tests.push({
        name: 'Focus indicators visible',
        passed: focusVisible
    });
    
    return tests;
}

async function testScreenReader(page) {
    const tests = [];
    
    // Test ARIA labels
    const ariaLabels = await page.evaluate(() => {
        const elements = document.querySelectorAll('[aria-label]');
        return Array.from(elements).map(el => ({
            element: el.tagName + '#' + el.id,
            label: el.getAttribute('aria-label')
        }));
    });
    
    tests.push({
        name: 'ARIA labels present',
        passed: ariaLabels.length >= 2,
        count: ariaLabels.length,
        labels: ariaLabels
    });
    
    // Test landmark roles
    const landmarks = await page.evaluate(() => {
        const main = document.querySelector('[role="main"], main');
        return { hasMain: !!main };
    });
    
    tests.push({
        name: 'Landmark roles',
        passed: landmarks.hasMain
    });
    
    // Test live regions for dynamic content
    const liveRegions = await page.evaluate(() => {
        const response = document.getElementById('response');
        const status = document.getElementById('status');
        return {
            responseHasLive: response.getAttribute('aria-live') !== null,
            statusHasLive: status.getAttribute('aria-live') !== null
        };
    });
    
    tests.push({
        name: 'Live regions for dynamic content',
        passed: liveRegions.responseHasLive || liveRegions.statusHasLive,
        details: liveRegions
    });
    
    return tests;
}

function generateReport(results) {
    console.log('\n📊 Accessibility Test Report\n');
    console.log('================================\n');
    
    let totalViolations = 0;
    let totalKeyboardPassed = 0;
    let totalKeyboardTests = 0;
    
    results.forEach(result => {
        console.log(`📱 ${result.viewport}`);
        console.log('-------------------');
        
        // Violations
        if (result.violations.length === 0) {
            console.log('✅ No accessibility violations found!');
        } else {
            console.log(`❌ ${result.violations.length} violations found:`);
            result.violations.forEach(violation => {
                console.log(`   - ${violation.description}`);
                console.log(`     Impact: ${violation.impact}`);
                console.log(`     Elements: ${violation.nodes.length}`);
            });
        }
        totalViolations += result.violations.length;
        
        // Keyboard tests
        console.log('\n⌨️  Keyboard Navigation:');
        result.keyboardTests.forEach(test => {
            console.log(`   ${test.passed ? '✅' : '❌'} ${test.name}`);
            if (!test.passed && test.actual !== undefined) {
                console.log(`     Expected: searchBox, Got: ${test.actual}`);
            }
            if (test.passed) totalKeyboardPassed++;
            totalKeyboardTests++;
        });
        
        // Screen reader tests
        console.log('\n🔊 Screen Reader:');
        result.screenReaderTests.forEach(test => {
            console.log(`   ${test.passed ? '✅' : '❌'} ${test.name}`);
            if (test.count !== undefined) {
                console.log(`     Found: ${test.count} labels`);
            }
        });
        
        console.log('\n');
    });
    
    // Summary
    console.log('📈 Summary');
    console.log('----------');
    console.log(`Total Violations: ${totalViolations}`);
    console.log(`Keyboard Tests: ${totalKeyboardPassed}/${totalKeyboardTests} passed`);
    console.log(`WCAG 2.1 AA Compliance: ${totalViolations === 0 ? '✅ PASS' : '❌ FAIL'}`);
    
    // Recommendations
    if (totalViolations > 0) {
        console.log('\n💡 Recommendations:');
        console.log('1. Fix all high-impact violations first');
        console.log('2. Add missing ARIA labels');
        console.log('3. Ensure all interactive elements are keyboard accessible');
        console.log('4. Test with actual screen readers (NVDA, JAWS, VoiceOver)');
    }
}

// Run tests if called directly
if (require.main === module) {
    runAccessibilityTests().catch(console.error);
}

module.exports = { runAccessibilityTests };