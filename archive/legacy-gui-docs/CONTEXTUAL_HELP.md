# Contextual Help System

## Overview

The NixOS GUI includes a comprehensive contextual help system that provides:
- **Tooltips** with detailed information about UI elements
- **Interactive Tours** to guide users through features
- **Keyboard Shortcuts** with a searchable cheatsheet
- **Context-sensitive Help** based on the current page

## Features

### 1. Smart Tooltips

Tooltips appear when hovering over or focusing on UI elements:

```javascript
// Register an element for help
contextualHelp.register('.package-install-btn', 'package-install');

// Show custom tooltip
contextualHelp.show(element, {
    title: 'Custom Help',
    content: 'This is custom help content',
    tips: ['Tip 1', 'Tip 2'],
    warnings: ['Be careful!']
});
```

#### Tooltip Features:
- **Auto-positioning** - Tooltips position themselves to stay visible
- **Rich Content** - Support for titles, tips, warnings, shortcuts
- **Related Topics** - Links to related help content
- **Keyboard Support** - F1 shows help for focused element

### 2. Interactive Tours

Guide users through complex workflows:

```javascript
// Start a tour
contextualHelp.tourManager.start('first-time');

// Available tours:
- 'first-time' - Welcome tour for new users
- 'package-management' - Package management walkthrough
- 'configuration-editor' - Configuration editing guide
- 'service-management' - Service management tutorial
- 'system-generations' - Generations and rollback guide
```

#### Tour Features:
- **Step-by-step Guidance** - Highlight elements and explain functionality
- **Progress Tracking** - Shows current step and total steps
- **Skip/Previous/Next** - Full navigation control
- **Auto-resume** - Remembers where user left off
- **Completion Tracking** - Marks completed tours

### 3. Keyboard Shortcuts

Comprehensive keyboard shortcut system:

```javascript
// Register a shortcut
contextualHelp.shortcuts.register('ctrl+k', 'Quick search', () => {
    document.querySelector('.search-input').focus();
});

// Show cheatsheet
contextualHelp.shortcuts.toggleCheatsheet();
```

#### Default Shortcuts:

**General:**
- `/` - Focus search
- `?` - Show keyboard shortcuts
- `F1` - Show help for focused element
- `Escape` - Close dialogs/tooltips

**Navigation:**
- `g h` - Go to home
- `g p` - Go to packages
- `g s` - Go to services
- `g c` - Go to configuration

**Actions:**
- `Ctrl+S` - Save configuration
- `Ctrl+Z` - Undo
- `Ctrl+Y` - Redo
- `Ctrl+Shift+D` - Toggle dark mode

### 4. Help Menu Integration

The help menu provides quick access to all help features:

```html
<!-- Help menu button in UI -->
<button class="help-menu-trigger" title="Help (F1)">
    <i class="icon-help-circle"></i>
</button>
```

Menu includes:
- Keyboard shortcuts reference
- Interactive tours
- Documentation links
- Troubleshooting tools
- About information

## Usage

### For Developers

#### Adding Help to New Elements

```javascript
// In your component
contextualHelp.register('.my-button', 'my-button-help', {
    showIndicator: true,  // Shows (?) indicator
    position: 'top',      // Force position
    delay: 1000          // Custom delay
});

// Add help content
const helpContent = {
    'my-button-help': {
        title: 'My Button',
        content: 'This button does something special',
        tips: [
            'Click to activate',
            'Right-click for options'
        ],
        shortcuts: [
            { key: 'Ctrl+B', description: 'Activate button' }
        ],
        related: ['other-help-id']
    }
};
```

#### Creating Custom Tours

```javascript
const customTour = {
    name: 'My Feature Tour',
    description: 'Learn about my feature',
    steps: [
        {
            target: '.my-feature',
            title: 'Welcome',
            content: 'This is my feature',
            position: 'center'
        },
        {
            target: '.my-button',
            title: 'Action Button',
            content: 'Click here to perform action',
            position: 'bottom',
            action: () => {
                // Optional: Run code during step
                console.log('Step shown');
            }
        }
    ]
};

// Register tour
contextualHelp.tourManager.tours['my-tour'] = customTour;

// Start tour
contextualHelp.tourManager.start('my-tour');
```

### For Users

#### Getting Help

1. **Hover** over any UI element to see tooltips
2. **Press F1** while focused on an element for detailed help
3. **Press ?** to see all keyboard shortcuts
4. **Click Help Menu** for tours and documentation

#### Taking Tours

Tours are available for major features:
1. Click Help menu → Interactive Tour
2. Follow the highlighted steps
3. Use Previous/Next to navigate
4. Skip to end if needed

## Configuration

### User Preferences

Preferences are saved in localStorage:

```javascript
// Get current preferences
const prefs = JSON.parse(localStorage.getItem('contextual-help-prefs'));

// Update preferences
contextualHelp.options.theme = 'light';
contextualHelp.options.animations = false;
contextualHelp.savePreferences();
```

Available options:
- `theme` - 'dark' or 'light'
- `delay` - Tooltip show delay (ms)
- `hideDelay` - Tooltip hide delay (ms)
- `animations` - Enable/disable animations
- `position` - Default position ('auto', 'top', 'bottom', 'left', 'right')

### Accessibility

The help system is fully accessible:
- **Keyboard Navigation** - All features keyboard accessible
- **Screen Reader Support** - Proper ARIA labels and announcements
- **Focus Management** - Logical focus flow
- **High Contrast** - Supports high contrast mode
- **Reduced Motion** - Respects prefers-reduced-motion

## Extending the System

### Adding Help Content

1. Create help content in `js/help/help-content.js`:
```javascript
export const myHelpContent = {
    'feature-x': {
        title: 'Feature X',
        content: 'Description...',
        tips: ['Tip 1'],
        warnings: ['Warning 1']
    }
};
```

2. Merge with main database:
```javascript
contextualHelp.helpDatabase = {
    ...contextualHelp.helpDatabase,
    ...myHelpContent
};
```

### Custom Tooltip Themes

Add CSS for custom themes:

```css
.contextual-help-container.theme-custom .tooltip-content {
    background: #your-color;
    color: #your-text-color;
    /* Custom styles */
}
```

Use custom theme:
```javascript
contextualHelp.options.theme = 'custom';
```

## Best Practices

1. **Consistent Help IDs** - Use descriptive, consistent IDs
2. **Concise Content** - Keep tooltips brief and actionable
3. **Progressive Disclosure** - Basic info in tooltip, details in tours
4. **Context Awareness** - Provide relevant help based on user state
5. **Testing** - Test tours with real users
6. **Maintenance** - Update help when features change

## Troubleshooting

### Tooltips Not Showing

1. Check element is registered: `contextualHelp.tooltips.has(element)`
2. Verify help ID exists in database
3. Check for CSS conflicts
4. Ensure JavaScript is loaded

### Tours Not Working

1. Verify target elements exist
2. Check tour ID is registered
3. Look for console errors
4. Ensure no modals blocking

### Keyboard Shortcuts Conflicts

1. Check for duplicate registrations
2. Verify context restrictions
3. Test in different browsers
4. Check for system shortcut conflicts

## API Reference

### ContextualHelp Class

```javascript
// Main instance
const help = new ContextualHelp(options);

// Methods
help.register(selector, helpId, options)
help.show(element, content, options)
help.hide()
help.generateTooltipId()
help.loadPreferences()
help.savePreferences()
```

### TourManager Class

```javascript
// Access via
const tours = contextualHelp.tourManager;

// Methods
tours.start(tourId)
tours.next()
tours.previous()
tours.end()
tours.showStep(stepIndex)
```

### ShortcutHelper Class

```javascript
// Access via
const shortcuts = contextualHelp.shortcuts;

// Methods
shortcuts.register(keys, description, handler, options)
shortcuts.toggleCheatsheet()
shortcuts.handleKeydown(event)
```