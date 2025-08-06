# 🤖 AI Licensing Advisor for Nix for Humanity

## Overview

The AI Licensing Advisor is a critical component of Nix for Humanity that helps users navigate the complex legal landscape of AI model licensing. As the NixOS AI ecosystem analysis states: **"Model choice has legal implications that could affect entire businesses."**

## Why This Matters

Many AI models have complex licensing terms that can:
- 🚫 Prohibit commercial use entirely
- ⚠️ Require open-sourcing your entire application (GPL/AGPL)
- 📝 Mandate specific attribution or usage restrictions
- 💰 Impose user limits for commercial deployment
- 🔒 Create legal liabilities for your organization

## Features

### 1. Model License Lookup
Query specific AI models to understand their licensing terms:
```bash
ask-nix-ai-aware "What's the license for Llama 2?"
ask-nix-ai-aware "Can I use Mistral-7B commercially?"
ask-nix-ai-aware "Tell me about Stable Diffusion licensing"
```

### 2. Use Case Recommendations
Get model recommendations based on your intended use:
```bash
ask-nix-ai-aware "Which AI model for a commercial SaaS?"
ask-nix-ai-aware "What models are safe for my startup?"
ask-nix-ai-aware "Recommend models for proprietary software"
```

### 3. License Compatibility Checking
Understand how different licenses interact:
```bash
ask-nix-ai-aware "Is MIT compatible with GPL?"
ask-nix-ai-aware "Can I mix Apache and AGPL code?"
```

### 4. Commercial Safety Analysis
Get clear guidance on commercial viability:
```bash
ask-nix-ai-aware "Is YOLO v8 safe for commercial use?"
ask-nix-ai-aware "Can I use MusicGen in my app?"
```

## License Categories

### ✅ Commercial-Friendly (Safe)
- **MIT**: Most permissive, minimal obligations
- **Apache-2.0**: Patent protection, attribution required
- **BSD-3-Clause**: Similar to MIT with no-endorsement clause

### ⚠️ Conditional Commercial Use
- **Llama-2**: Commercial OK if <700M monthly active users
- **OpenRAIL-M**: Use-based restrictions (no harmful use)
- **Gemma**: Requires attribution, specific terms

### 🔄 Copyleft (Share-Alike Required)
- **GPL-3.0**: Must open-source entire application
- **AGPL-3.0**: Must share source even for SaaS/API use
- **CC-BY-SA**: Derivatives must use same license

### ❌ Non-Commercial Only
- **CC-BY-NC**: No commercial use allowed
- **Research licenses**: Academic/research use only
- **Custom restrictive**: Various proprietary restrictions

## Common Warnings

### 1. The AGPL Trap for SaaS
```
⚠️ AGPL-licensed models (like YOLO v8) require you to:
- Open-source your ENTIRE application
- Even if users only access it via API/web
- This is often a deal-breaker for commercial SaaS
```

### 2. The Llama User Limit
```
⚠️ Llama models have a 700M monthly active user limit
- Fine for most startups
- Problematic for large-scale consumer apps
- Requires license renegotiation if exceeded
```

### 3. Dataset vs Model Licensing
```
⚠️ A model may have different licenses for:
- The model weights (what you deploy)
- The training dataset (may have restrictions)
- The code (may be separate)
Always check all three!
```

## Integration with NixOS

The advisor is integrated into the standard `ask-nix` workflow:

```bash
# Install an AI model package
ask-nix-ai-aware "How do I install ollama?"

# Then check its licensing
ask-nix-ai-aware "What models in ollama are commercial-safe?"
```

## Examples by Use Case

### For Startups
```bash
ask-nix-ai-aware "Which LLMs are safe for a startup?"
# Recommends: Mistral-7B, Falcon-7B (Apache-2.0)
# Warns about: Llama (MAU limit), AGPL models
```

### For Open Source Projects
```bash
ask-nix-ai-aware "Which AI models for an MIT-licensed project?"
# Recommends: Any MIT/Apache/BSD licensed models
# Warns about: GPL (viral), non-commercial licenses
```

### For Enterprise SaaS
```bash
ask-nix-ai-aware "Which models for enterprise SaaS deployment?"
# Recommends: Apache-2.0 models, MIT models
# Strongly warns about: AGPL (source disclosure)
```

### For Research
```bash
ask-nix-ai-aware "Which models for academic research?"
# Recommends: All models (even non-commercial)
# Notes: Widest selection available
```

## Best Practices

1. **Always Check Before Deploying**
   ```bash
   ask-nix-ai-aware "Check license for [model-name]"
   ```

2. **Consider Your Use Case**
   - Commercial? Avoid NC (non-commercial) licenses
   - SaaS? Avoid AGPL unless you'll open-source
   - Proprietary? Avoid GPL/copyleft licenses

3. **Document Your Compliance**
   - Keep records of which models you use
   - Maintain required attributions
   - Monitor for license changes

4. **Have a Fallback Plan**
   - Know alternative models with better licenses
   - Be prepared to swap models if needed
   - Consider license costs in architecture decisions

## Quick Reference

### Safe for Commercial Use
- ✅ Mistral models (Apache-2.0)
- ✅ Falcon models (Apache-2.0)  
- ✅ GPT-2 (MIT)
- ✅ BERT variants (Apache-2.0)
- ✅ Whisper (MIT)

### Conditional/Restricted
- ⚠️ Llama models (<700M MAU)
- ⚠️ Stable Diffusion (OpenRAIL-M restrictions)
- ⚠️ Gemma (attribution required)

### Avoid for Commercial/Proprietary
- ❌ YOLO v8 (AGPL - requires source disclosure)
- ❌ MusicGen (CC-BY-NC - non-commercial only)
- ❌ Research-only models

## Getting Help

```bash
# General AI licensing help
ask-nix-ai-aware "Help with AI licensing"

# Specific model inquiry
ask-nix-ai-aware "Is [model-name] safe for [use-case]?"

# License comparison
ask-nix-ai-aware "Compare licenses: MIT vs Apache vs GPL"
```

## Remember

> "In the AI age, your model choice is also a legal choice. Choose wisely."

The AI Licensing Advisor helps ensure your AI deployment doesn't become a legal liability. When in doubt, ask first!