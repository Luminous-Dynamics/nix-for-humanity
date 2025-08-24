[Show HN] I built a natural language interface for NixOS in 2 weeks using AI

Hey r/NixOS!

I just released Luminous Nix - a natural language interface that makes NixOS accessible to everyone. Instead of learning Nix syntax, just say what you want:

- `ask-nix "install firefox"` 
- `ask-nix "create web server config"`
- `ask-nix fix` - AI diagnoses and fixes your broken config!

The cool part: This was built in 2 weeks using Claude Code (Anthropic's AI pair programmer) for ~$200/month. It's proof that solo developers + AI can build production software faster than ever.

Features:
- 2-minute setup wizard
- Sub-10 second response times 
- 10 adaptive personas (from Grandma to Power User)
- NixOS Doctor that actually fixes issues
- Works completely offline after setup

It's alpha but it works! Would love feedback from the community.

GitHub: https://github.com/Luminous-Dynamics/luminous-nix

One-line install:
```
curl -L https://raw.githubusercontent.com/Luminous-Dynamics/luminous-nix/main/install.sh | sh
```
