# Archived Tools

These tools have been archived as part of the Nix for Humanity consolidation effort.

*Last Updated: 2025-01-29*

## Archived Tools:

### ask-nix-enhanced
- **Issue**: Python module import errors
- **Status**: Non-functional due to missing nixos-rebuild-ng module
- **Superseded by**: ask-nix-modern

### ask-nix-hybrid-v2
- **Issue**: AttributeError on import
- **Status**: Broken module path problems
- **Superseded by**: ask-nix-modern

### ask-trinity
- **Issue**: Missing dependencies
- **Status**: Non-functional
- **Note**: Sacred Trinity integration moved to ask-nix-modern

### ask-trinity-rag
- **Issue**: RAG system not implemented
- **Status**: Non-functional
- **Note**: Future RAG features will be added to ask-nix

### ask-nix-modern (Archived 2025-01-29)
- **Reason**: Consolidated into main ask-nix command
- **Status**: Fully functional but redundant
- **Note**: All features integrated into ask-nix v0.8.0

### ask-nix-refactored (Archived 2025-01-29)
- **Reason**: Experimental headless architecture attempt
- **Status**: Incomplete refactoring
- **Note**: Headless architecture will be properly implemented in future versions

## Why These Were Archived

As part of the Nix for Humanity consolidation effort, we unified all variants into a single powerful `ask-nix` command that:
- Actually executes commands (no more copy-paste!)
- Includes confirmation prompts for safety
- Uses modern nix profile commands
- Has progress indicators
- Supports all personality styles
- Includes symbiotic feedback collection
- Provides plugin architecture for extensibility

All valuable features from these experimental tools have been integrated into the main `ask-nix` command.