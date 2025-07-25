# 🔍 Accessibility Testing Framework

## Overview

This directory contains comprehensive accessibility tests for Nix for Humanity, ensuring our natural language interface is truly accessible to everyone.

## Test Structure

```
accessibility/
├── setup.js                    # Test framework setup
├── run-a11y-tests.js          # Main test runner
├── test-nlp-interface.js      # WCAG compliance tests
├── test-voice-text-parity.js  # Input method equality tests
├── test-personas.js           # Persona-based testing
└── README.md                  # This file
```

## Running Tests

### Quick Start
```bash
# Install dependencies
npm install

# Start development server (required)
npm run dev

# In another terminal, run accessibility tests
npm run test:a11y
```

### Individual Test Suites
```bash
# Run specific test file
npx jest tests/accessibility/test-nlp-interface.js

# Watch mode for development
npm run test:a11y:watch

# Generate and open HTML report
npm run test:a11y:report
```

## Test Coverage

### 1. WCAG 2.1 Compliance (`test-nlp-interface.js`)
- **Level AA**: Minimum requirement (must pass)
- **Level AAA**: Target goal
- Tests include:
  - Color contrast ratios
  - Keyboard navigation
  - Screen reader compatibility
  - Focus indicators
  - Error handling

### 2. Voice-Text Parity (`test-voice-text-parity.js`)
- Ensures both input methods are equally supported
- No preference given to either voice or text
- Same features available through both methods
- Equal prominence in UI

### 3. Persona Testing (`test-personas.js`)
Tests against our 5 key personas:

#### Grandma Rose (75)
- Large text support
- Simple language
- Tremor tolerance
- No time pressure

#### Maya (16) - ADHD
- Minimal distractions
- Clear visual feedback
- Quick interactions
- Structured flow

#### David (42) - Stress/Fatigue
- Calm interface
- Gentle errors
- Easy recovery
- Predictable behavior

#### Dr. Sarah (35) - Power User
- Keyboard shortcuts
- Information density
- Efficient navigation
- Customization

#### Alex (28) - Blind Developer
- 100% screen reader
- No visual dependencies
- Keyboard-only navigation
- Code-aware output

## Key Testing Principles

### 1. Automated First, Manual Second
- Automated tests catch obvious issues
- Manual testing validates user experience
- Both are required for full coverage

### 2. Real User Conditions
- Test with actual screen readers (NVDA, VoiceOver)
- Simulate real disabilities (tremor, low vision)
- Use persona-based scenarios

### 3. Continuous Testing
- Run after every feature addition
- Part of CI/CD pipeline
- Regular manual audits

## Accessibility Standards

### Required Compliance
- **WCAG 2.1 Level AA**: Minimum standard
- **Section 508**: US Federal requirement
- **EN 301 549**: European standard
- **ADA**: Americans with Disabilities Act

### Testing Tools Used
- **axe-core**: Automated WCAG testing
- **Puppeteer**: Browser automation
- **Jest**: Test framework
- **Manual tools**: NVDA, VoiceOver, keyboard testing

## Common Issues and Fixes

### Issue: Low Color Contrast
```css
/* Bad */
color: #888;
background: #f0f0f0;

/* Good - 4.5:1 minimum */
color: #595959;
background: #ffffff;
```

### Issue: Missing ARIA Labels
```html
<!-- Bad -->
<button>X</button>

<!-- Good -->
<button aria-label="Close dialog">X</button>
```

### Issue: Keyboard Traps
```javascript
// Bad - No escape
modal.addEventListener('keydown', (e) => {
  e.preventDefault();
});

// Good - Allow escape
modal.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeModal();
  }
});
```

## Manual Testing Checklist

### Screen Reader Testing
- [ ] Test with NVDA on Windows
- [ ] Test with VoiceOver on macOS
- [ ] Test with Orca on Linux
- [ ] All content is announced
- [ ] Reading order makes sense
- [ ] Interactive elements have labels

### Keyboard Testing
- [ ] Tab through entire interface
- [ ] No keyboard traps
- [ ] All features accessible
- [ ] Focus indicators visible
- [ ] Logical tab order

### Visual Testing
- [ ] Zoom to 200% - still usable
- [ ] High contrast mode works
- [ ] Color blind safe
- [ ] Motion can be disabled

### Voice Interface Testing
- [ ] Works with background noise
- [ ] Handles accents
- [ ] Text alternative always available
- [ ] Visual feedback for voice

## Reporting Issues

### Found an Accessibility Issue?

1. **Document it**:
   - Which persona is affected?
   - What WCAG criterion fails?
   - Steps to reproduce
   - Expected vs actual behavior

2. **Prioritize it**:
   - **Critical**: Blocks entire feature
   - **Major**: Significant barrier
   - **Minor**: Inconvenience

3. **Fix it**:
   - Write failing test first
   - Implement fix
   - Verify with manual testing
   - Update documentation

## Resources

### Guidelines
- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [WebAIM Resources](https://webaim.org/resources/)

### Tools
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [WAVE Browser Extension](https://wave.webaim.org/extension/)
- [NVDA Screen Reader](https://www.nvaccess.org/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)

## Future Enhancements

### Planned
- [ ] Automated screen reader testing
- [ ] Voice command testing automation
- [ ] Multi-language accessibility
- [ ] Gesture testing for mobile

### Under Consideration
- [ ] Eye tracking support
- [ ] Brain-computer interface
- [ ] Haptic feedback testing
- [ ] AR/VR accessibility

---

*Remember: If someone cannot use our system, we have failed in our mission.*

**Accessibility is not a feature. It's a fundamental right.**