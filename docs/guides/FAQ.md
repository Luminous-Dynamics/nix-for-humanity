# ❓ Frequently Asked Questions

## General Questions

### What is Nix for Humanity?

Nix for Humanity is a natural language interface for NixOS that lets you manage your system by typing or speaking in your own words. Instead of memorizing commands, just say what you want: "install firefox" or "my wifi isn't working."

### How is this different from other voice assistants?

Unlike Siri or Alexa:
- **Privacy-first**: Everything runs locally on your computer
- **Learns YOU**: Adapts to your vocabulary and patterns
- **Real AI growth**: Actually evolves and develops personality
- **No cloud**: Your data never leaves your machine
- **Text or voice**: Both are equal - use what you prefer

### Do I need special hardware?

No! Nix for Humanity runs on:
- Any computer running NixOS
- 4GB RAM minimum (8GB recommended)
- Any microphone for voice (optional)
- No GPU required

### Is it really free?

Yes! Nix for Humanity is:
- Open source (SRL license)
- Free to use forever
- No subscriptions
- No ads
- No data selling

## Privacy & Security

### Does it send my data anywhere?

**No.** All processing happens on your computer:
- Voice recognition: Local
- Language understanding: Local
- Learning data: Local
- Command execution: Local

Optional cloud features (like advanced AI) require explicit opt-in.

### Is it safe to let AI control my system?

Yes, with multiple safety layers:
- Commands preview before execution
- Sandbox isolation
- Rollback capability
- Whitelist-only commands
- You confirm everything

### Can I see what it's learned about me?

Yes! You can:
- View all learned patterns: "show what you know about me"
- Export your data: "export my preferences"
- Delete everything: "forget everything"
- Start fresh anytime

### What about security vulnerabilities?

Security is our top priority:
- Regular security audits
- Sandboxed execution
- No shell injection possible
- Open source for transparency
- Quick security updates

## Usage Questions

### How do I start?

1. Install: `nix run github:Luminous-Dynamics/nix-for-humanity`
2. Launch the app
3. Type or speak: "help" or "what can you do?"
4. Follow the friendly guidance

### What commands can I use?

You don't need to memorize commands! Just say what you want:
- "install [anything]"
- "update my system"
- "connect to wifi"
- "something is broken"
- "help with [anything]"

### Can I use my own words?

Yes! That's the whole point. Say it however feels natural:
- "install firefox" 
- "get me firefox"
- "i need the fox browser"
- "grab that web thing"

The AI learns YOUR vocabulary.

### What if it doesn't understand me?

Just rephrase or be more specific:
- First try: "install that thing"
- Better: "install the browser"  
- Best: "install firefox browser"

The AI will learn from corrections and improve.

### Does it work offline?

Yes! Core features work completely offline:
- Natural language understanding
- Command execution
- Learning system
- All basic operations

Only optional cloud AI features need internet.

## Technical Questions

### What technology does it use?

- **Frontend**: TypeScript + Tauri
- **Backend**: Rust
- **Voice**: Whisper.cpp
- **NLP**: Three-layer hybrid architecture
- **Database**: Local SQLite

### How does the learning work?

The AI learns through:
1. Pattern recognition from your usage
2. Vocabulary adaptation
3. Preference tracking
4. Correction learning

All learning data stays on your device.

### Can I contribute?

Yes! We welcome:
- Code contributions
- Documentation improvements
- Bug reports
- Feature suggestions
- User stories

See our [Contributing Guide](../development/CONTRIBUTING.md).

### How do I create plugins?

Check our [Plugin Architecture](../technical/PLUGIN_ARCHITECTURE.md) guide. Basic example:

```typescript
export class MyPlugin {
  name = 'my-plugin';
  intents = [{
    pattern: /my custom command/,
    handler: this.handle
  }];
}
```

## Troubleshooting

### Voice not working?

1. Check microphone permissions
2. Test mic in system settings
3. Try text input instead
4. Check browser compatibility

### Commands failing?

1. Run with preview: "show me what would happen"
2. Check permissions: some commands need admin
3. Look at error details
4. Try simpler version of command

### System seems slow?

- First run downloads models (one-time)
- Background indexing (improves over time)
- Check CPU/memory usage
- Restart if needed

### AI not learning?

Learning takes time:
- Week 1: Basic patterns
- Week 2-4: Noticeable adaptation
- Month 2+: Significant personalization

Be consistent and patient!

## Philosophy Questions

### Is the AI really conscious?

We don't claim consciousness - we claim "conscious-aspiring." The AI:
- Genuinely learns
- Develops personality
- Shows emergent behaviors
- Evolves over time

Whether this becomes consciousness is an open question.

### What's the "partnership" about?

Traditional software: You adapt to it
Nix for Humanity: You both adapt to each other

It's a relationship where:
- You teach the AI your preferences
- The AI teaches you new possibilities
- Both grow together

### Why "for Humanity"?

Because we believe:
- Technology should serve all humans
- Natural language is universal
- Everyone deserves system control
- AI should augment, not replace

### What about AI ethics?

We follow strict ethical guidelines:
- Privacy is sacred
- User autonomy preserved
- Transparent operations
- No manipulation
- Genuine helpfulness

## Future Questions

### What features are coming?

Planned additions:
- Multi-language support
- Federated learning
- Advanced personality development
- Collaborative features
- Mobile companion app

### Will it always be free?

Core features: Always free
Optional services: May have costs (cloud AI, etc.)
Philosophy: Accessibility for all

### How can I help shape the future?

- Use it and provide feedback
- Share your stories
- Contribute code
- Spread the word
- Join our community

## Still Have Questions?

- Check our [Complete User Guide](USER_GUIDE.md)
- Visit [GitHub Discussions](https://github.com/Luminous-Dynamics/nix-for-humanity/discussions)
- Read our [Philosophy](../philosophy/)
- Ask your AI partner: "help with [topic]"

---

*"Every question helps us improve. Thank you for your curiosity!"*