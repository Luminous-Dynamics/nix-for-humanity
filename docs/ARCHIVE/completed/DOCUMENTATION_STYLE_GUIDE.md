# 📝 Documentation Style Guide - Nix for Humanity

*Ensuring consistency across all documentation*

## Core Messaging

### Project Name
- **Always use**: "Nix for Humanity"
- **Never use**: "NixOS GUI", "GUI for NixOS", "NixOS Assistant"

### What We Are
- **Primary**: "context-aware natural language interface for NixOS"
- **Alternative**: "natural language NixOS management"
- **Simple**: "speak or type naturally to manage NixOS"
- **Never say**: "GUI application", "voice assistant", "graphical interface" (without context)

### Core Concept
We are building a system where users express their intent in natural language (typed or spoken), and the system understands and acts. Visual elements provide feedback and confirmation but are not the primary interface.

## Language Guidelines

### Input Methods
- **Correct**: "type or speak", "natural language input", "your own words"
- **Incorrect**: "voice commands", "text commands", "GUI input"
- **Note**: Always present typing and speaking as equal options

### Visual Elements
When mentioning visual elements, always clarify their supportive role:
- ✅ "visual feedback shows progress"
- ✅ "see a preview before execution"
- ✅ "visual elements support your natural language"
- ❌ "click the button"
- ❌ "navigate the GUI"
- ❌ "graphical interface" (without context)

### Intelligence Features
- **Use**: "learns your patterns", "adapts to your workflow", "operational intelligence"
- **Avoid**: "AI-powered" (too vague), "smart" (overused)
- **Explain**: Always give concrete examples of learning

## Tone and Voice

### Friendly and Approachable
- Use "you" and "your"
- Short sentences
- Active voice
- Concrete examples

### Examples
- ✅ "Just type 'install firefox' and watch it work"
- ❌ "The system facilitates package installation through natural language processing"

### Accessibility Language
- "Works for everyone" not "handicap accessible"
- "Screen reader compatible" not "blind-friendly"
- "Multiple input methods" not "disabled access"

## Formatting Standards

### Headers
```markdown
# Main Title - With Project Name
## Major Sections
### Subsections
#### Minor Points
```

### Code Examples
Always show natural language first:
```
You type: "install firefox"
System shows: Command preview, progress bar, confirmation
Equivalent to: nix-env -iA nixpkgs.firefox
```

### Feature Lists
Use checkmarks for completed, construction for in-progress:
- ✅ Natural language understanding
- 🚧 Voice input integration
- ❌ Not yet implemented

## Common Patterns

### Installation Instructions
```markdown
## Quick Start

### Try it now (no installation needed):
\```bash
nix run github:Luminous-Dynamics/nix-for-humanity
\```

### Install permanently:
\```bash
nix profile install github:Luminous-Dynamics/nix-for-humanity
\```
```

### Feature Descriptions
Pattern: What you can do → How it helps → Example

```markdown
### Smart Timing
The system learns when you prefer to do maintenance tasks. If you try to update during work hours, it can defer to your usual maintenance window. For example, "update system" on Friday afternoon might suggest Monday morning instead.
```

### Comparisons
Always show natural language vs traditional:
```markdown
**Instead of memorizing:**
`nix-env -iA nixpkgs.firefox`

**Just say:**
"install firefox"
```

## Documentation Types

### README.md Files
- Start with what the user gets
- Show examples immediately
- Installation in under 5 steps
- Link to deeper documentation

### User Guides
- Task-oriented structure
- Step-by-step instructions
- Screenshots only when necessary
- Emphasize natural language

### Technical Documentation
- Clear architecture diagrams
- Implementation details
- API references
- Security considerations

### Vision Documents
- Inspiring but concrete
- User-focused benefits
- Real-world examples
- Future possibilities

## Quality Checklist

Before publishing any documentation:

- [ ] Uses "Nix for Humanity" consistently
- [ ] Describes natural language interface correctly
- [ ] Shows typing and speaking as equal options
- [ ] Explains visual elements as supportive
- [ ] Includes concrete examples
- [ ] Accessible language throughout
- [ ] No GUI-first terminology
- [ ] Clear next steps for readers

## Examples of Good Documentation

### Good Opening
```markdown
# Nix for Humanity - Natural Language NixOS Management

Manage your NixOS system using natural language. Just type or speak what you want to do - no command memorization needed.
```

### Good Feature Description
```markdown
## Learns Your Preferences

Nix for Humanity remembers how you like to work. If you always install development tools together, it will suggest the complete set. If you prefer configuration.nix over imperative commands, it adapts its suggestions.

Example:
- You: "install python"
- System: "I'll add Python to configuration.nix with your usual data science packages (numpy, pandas, jupyter). OK?"
```

### Good Troubleshooting
```markdown
## When Things Don't Work

### "Command not understood"
Try rephrasing naturally. Instead of "pkg install firefox", say "install firefox" or "I need firefox".

The system learns from corrections and will understand better next time.
```

## Prohibited Patterns

Never use these patterns:
- "Click here" (use "select" or "choose")
- "GUI interface" (redundant and wrong focus)
- "Voice-first" (equal input methods)
- "Command syntax" (it's natural language)
- "Revolutionary GUI" (it's not a GUI)

## Living Document

This style guide evolves as we learn what works best for users. When in doubt:
1. Be consistent with existing docs
2. Focus on user success
3. Emphasize natural language
4. Keep it simple

---

*"Good documentation is like a conversation with a knowledgeable friend."*