# Accessibility Requirements - Critical Reference

## Non-Negotiable Requirements

### 1. Screen Reader Support (MUST HAVE)
- **NVDA**: Full compatibility on Windows
- **JAWS**: Full compatibility on Windows  
- **VoiceOver**: Full compatibility on macOS
- **Orca**: Full compatibility on Linux

#### Implementation Checklist
- [ ] All interactive elements have labels
- [ ] ARIA live regions for dynamic updates
- [ ] Proper heading hierarchy (h1-h6)
- [ ] Landmark roles (main, nav, etc.)
- [ ] Skip navigation links
- [ ] Form labels associated correctly
- [ ] Error messages announced
- [ ] Progress updates announced

### 2. Keyboard Navigation (MUST HAVE)
```javascript
// Every feature must be keyboard accessible
const keyboardPatterns = {
  'Tab': 'Next element',
  'Shift+Tab': 'Previous element',
  'Enter/Space': 'Activate',
  'Escape': 'Cancel/Close',
  'Arrow keys': 'Navigate within',
  'Home/End': 'First/Last',
  'PageUp/PageDown': 'Scroll'
};
```

#### No Keyboard Traps
- User can tab in AND out
- Escape always works
- Clear focus indicators
- Logical tab order

### 3. Voice Interface Accessibility

#### For Speech Impairments
- **Text alternative always available**
- Configurable recognition sensitivity
- Support for speech patterns:
  - Stuttering
  - Slow speech  
  - Accents
  - Impediments

#### For Hearing Impairments
- Visual feedback for all audio
- Captions for voice responses
- Visual progress indicators
- No audio-only information

### 4. Visual Accessibility

#### High Contrast Support
```css
/* Minimum contrast ratios */
:root {
  /* WCAG AA: 4.5:1 for normal text */
  /* WCAG AA: 3:1 for large text */
  /* WCAG AAA: 7:1 for normal text */
  /* WCAG AAA: 4.5:1 for large text */
}

/* Respect system preferences */
@media (prefers-contrast: high) {
  /* High contrast styles */
}

@media (prefers-reduced-motion) {
  /* Disable animations */
}
```

#### Color Blindness
- Never rely on color alone
- Use patterns, icons, text
- Test with simulators

### 5. Motor Accessibility

#### Large Touch Targets
- Minimum 44x44px (iOS standard)
- 48x48px preferred (Android)
- Adequate spacing between

#### Gesture Alternatives
- Every gesture has keyboard equivalent
- No complex gestures required
- Time limits adjustable/disabled
- No precision timing required

### 6. Cognitive Accessibility

#### Simple Language
```javascript
// BAD: Technical jargon
"Error: EACCES permission denied"

// GOOD: Plain language
"I need permission to do that"
```

#### Clear Flow
- One task at a time
- Clear next steps
- No time pressure
- Undo always available

#### Reduced Cognitive Load
- Hide advanced options
- Progressive disclosure
- Consistent patterns
- Clear feedback

## Testing Requirements

### Automated Testing
```javascript
// Every component must pass
describe('Accessibility', () => {
  it('has no accessibility violations', async () => {
    const results = await axe(component);
    expect(results.violations).toHaveLength(0);
  });
  
  it('is keyboard navigable', async () => {
    // Tab through all elements
    // Verify focus order
    // Check keyboard activation
  });
  
  it('works with screen reader', async () => {
    // Check announcements
    // Verify labels
    // Test live regions
  });
});
```

### Manual Testing Protocol
1. **Screen Reader Testing**
   - Test with NVDA
   - Test with VoiceOver
   - Verify all content readable
   - Check announcement order

2. **Keyboard Testing**
   - Unplug mouse
   - Complete all tasks
   - Verify no traps
   - Check focus visibility

3. **Voice Testing**
   - Test with background noise
   - Test with accents
   - Test with speech impediments
   - Verify text alternatives

## The Five Personas - Accessibility Needs

### Grandma Rose (75) - Age-related changes
- Larger text needed
- High contrast essential
- Slower speech preferred
- Simple language required
- Tremor tolerance needed

### Maya (16) - ADHD considerations  
- Quick interactions
- Visual feedback
- Minimal distractions
- Clear structure
- Keyboard shortcuts

### David (42) - Stress/fatigue
- Clear, calm interface
- No time pressure
- Error recovery
- Simple choices
- Predictable behavior

### Dr. Sarah (35) - Efficiency needs
- Keyboard power user
- Screen reader compatible
- Customizable interface
- Dense information OK
- Quick navigation

### Alex (28) - Blind developer
- 100% screen reader
- Keyboard only
- No visual cues
- Audio feedback
- Code-aware reader

## Accessibility Statements

### Required Announcements
```javascript
// Pattern for screen reader announcements
const announcePattern = {
  action: "Installing Firefox",
  progress: "50% complete",
  completion: "Firefox installed successfully",
  error: "Could not install Firefox. Network error.",
  suggestion: "Try again or install offline"
};
```

### Status Messages
- Use ARIA live regions
- Polite for info
- Assertive for errors
- Clear and concise
- Action-oriented

## Legal Compliance

### Standards to Meet
- **WCAG 2.1 Level AA** (minimum)
- **WCAG 2.1 Level AAA** (target)
- **Section 508** (US Federal)
- **EN 301 549** (European)
- **ADA** (Americans with Disabilities Act)

### Documentation Required
- Accessibility Statement
- VPAT (Voluntary Product Accessibility Template)
- Known limitations
- Contact for issues

## Common Pitfalls to Avoid

### ❌ DON'T
- Disable right-click
- Override browser zoom
- Use placeholder as label
- Auto-play media
- Create keyboard traps
- Use color alone
- Require hover
- Assume abilities

### ✅ DO
- Support all input methods
- Respect user preferences
- Provide alternatives
- Test with real users
- Listen to feedback
- Fix issues quickly
- Document limitations
- Exceed minimums

## Resources and Tools

### Testing Tools
- axe DevTools
- WAVE
- Lighthouse
- NVDA (free)
- Color contrast analyzers
- Keyboard navigation tester

### Guidelines
- WCAG Quick Reference
- ARIA Authoring Practices
- Inclusive Components
- A11y Project Checklist

---

*Remember: Accessibility is not a feature. It's a fundamental right.*

**If someone cannot use our system, we have failed in our mission.**