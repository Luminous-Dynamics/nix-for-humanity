# 🧠 Learning System Data

This directory contains databases and data files for the Nix for Humanity learning system.

## Databases

- **nixos_knowledge.db** - Core NixOS knowledge base
- **nixos_knowledge_modern.db** - Modern Nix commands knowledge
- **trinity_rag.db** - Sacred Trinity RAG system data
- **package_cache.db** - Package search cache for performance
- **search_history.db** - Search history and patterns
- **command_learning.db** - Command usage learning data

## Privacy

All data is stored locally and never transmitted. User privacy is paramount.

## Backup

These databases contain learned patterns and should be backed up regularly but not committed to version control due to their size and changing nature.

## Maintenance

Run `scripts/clean-learning-data.sh` periodically to remove old entries and optimize databases.