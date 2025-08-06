# 📁 Project Reorganization Plan

## Current Problem

The project root has become cluttered with many loose files that should be organized into appropriate directories. This makes it difficult to:
- Find relevant documentation
- Understand project structure
- Maintain clean version control
- Onboard new contributors

## Proposed Directory Structure

```
nix-for-humanity/
├── docs/                    # All documentation (already exists)
│   ├── ACTIVE/             # Current operational docs
│   ├── VISION/             # Future-looking docs
│   └── ARCHIVE/            # Historical docs
├── src/                     # Source code (already exists)
├── bin/                     # Executable scripts (already exists)
├── scripts/                 # Development/utility scripts (already exists)
├── tests/                   # Test files (already exists)
├── implementations/         # Implementation variants (already exists)
├── packages/               # Modular packages (already exists)
├── results/                 # Test results and reports (NEW)
├── learning/               # Learning system data (NEW)
├── config/                 # Configuration files (already exists)
├── examples/               # Example usage (already exists)
├── .github/                # GitHub specific files (NEW)
├── README.md               # Main readme
├── CHANGELOG.md            # Version history
├── CONTRIBUTING.md         # Contribution guide
├── LICENSE                 # License file
└── package.json            # NPM configuration
```

## Files to Reorganize

### 1. Move to `docs/ACTIVE/current/`
These are current status and planning documents:
- EXECUTE_COMMAND_DOCUMENTATION.md
- LEARNING_SYSTEM_DESIGN.md
- LEARNING_SYSTEM_ACTIVATED.md
- PERSONA_TEST_RESULTS_ANALYSIS.md
- USER_INPUT_MECHANISMS_DESIGN.md
- NEXT_ACTIONS_SUMMARY.md
- LEARNING_INTEGRATION_COMPLETE.md
- LEARNING_HOOKS_FINAL_SUMMARY.md

### 2. Move to `docs/ACTIVE/guides/`
User-facing documentation:
- WORKING_COMMANDS.md
- QUICK_REFERENCE.md
- USER_GUIDE_SIMPLE.md
- FEEDBACK_QUICKSTART.md
- TEST_NOW.md
- MANUAL_TESTING_GUIDE.md

### 3. Move to `docs/ACTIVE/development/`
Developer documentation:
- IMPLEMENTATION_PLAN.md
- IMPLEMENTATION_COMPLETE.md
- COMMAND_EXECUTOR_ANALYSIS.md
- NLP_INTEGRATION_COMPLETE.md
- BRIDGING_VISION_AND_REALITY.md
- NLP_TO_EXECUTION_BRIDGE.md
- INTELLIGENT_CACHING_IMPLEMENTATION.md
- UNIFIED_COMMAND_MIGRATION.md

### 4. Move to `docs/ARCHIVE/completed/`
Completed work summaries:
- PHASE_2_COMPLETION_REPORT.md
- PERSONA_TESTING_COMPLETE.md
- EXECUTION_BRIDGE_COMPLETE.md
- PRIVACY_ENHANCEMENTS_COMPLETE.md
- GITHUB_SETUP_COMPLETE.md
- DOCUMENTATION_REORGANIZATION_COMPLETE.md

### 5. Move to `results/`
Test results and analysis:
- persona_test_results_20250728_142941.json
- feedback_20250728_111304.json
- TEST_EXECUTE_FLAG_RESULTS.md
- FEEDBACK_RESULTS.md

### 6. Move to `learning/`
Learning system databases:
- nixos_knowledge.db
- nixos_knowledge_modern.db
- trinity_rag.db
- package_cache.db
- search_history.db
- command_learning.db

### 7. Move to `scripts/test/`
Test scripts:
- test-execute-commands.sh
- test-personas.py
- test-personas.js
- test-all-commands.sh
- test-all-core-commands.sh
- test-nlp-integration.js
- test-working-install.sh
- test-search-command.sh
- test-real-execution.sh
- test-safe-execution.js
- test-dry-run.js
- test_execution.py

### 8. Move to `scripts/demo/`
Demo scripts:
- demo-nlp.js
- demo-working-command.sh
- demo-unified-cli.sh
- demo-nlp-features.js
- demo-real-execution.sh
- start-demo.sh
- start-demo-direct.sh

### 9. Move to `.github/`
GitHub specific files:
- GITHUB_PUSH_CHECKLIST.md
- GITHUB_ISSUES_TO_CREATE.md (from docs)
- CODE_OF_CONDUCT.md

### 10. Shell Configuration Files (Keep in root)
These need to stay in root for Nix:
- shell.nix
- shell-minimal.nix
- shell-rust.nix
- shell-complete.nix
- flake.nix

### 11. Build/Config Files (Keep in root)
Standard locations expected by tools:
- package.json
- tsconfig.json
- vite.config.js
- Dockerfile
- docker-compose.yml
- Makefile

## Implementation Steps

### Step 1: Create New Directories
```bash
mkdir -p results learning scripts/test scripts/demo .github
```

### Step 2: Move Files in Batches
```bash
# Move test results
mv persona_test_results_*.json feedback_*.json results/
mv TEST_EXECUTE_FLAG_RESULTS.md FEEDBACK_RESULTS.md results/

# Move learning databases
mv *.db learning/

# Move test scripts
mv test-*.sh test-*.js test-*.py test_*.py scripts/test/

# Move demo scripts
mv demo-*.js demo-*.sh start-demo*.sh scripts/demo/

# Move current docs
mv EXECUTE_COMMAND_DOCUMENTATION.md LEARNING_SYSTEM_*.md PERSONA_TEST_*.md USER_INPUT_*.md NEXT_ACTIONS_*.md docs/ACTIVE/current/

# Move guides
mv WORKING_COMMANDS.md QUICK_REFERENCE.md USER_GUIDE_SIMPLE.md FEEDBACK_QUICKSTART.md TEST_NOW.md MANUAL_TESTING_GUIDE.md docs/ACTIVE/guides/

# Move dev docs
mv IMPLEMENTATION_*.md COMMAND_EXECUTOR_*.md NLP_*.md BRIDGING_*.md INTELLIGENT_*.md UNIFIED_*.md docs/ACTIVE/development/

# Move completed docs
mv PHASE_2_*.md PERSONA_TESTING_COMPLETE.md EXECUTION_BRIDGE_COMPLETE.md PRIVACY_*.md GITHUB_SETUP_COMPLETE.md DOCUMENTATION_REORGANIZATION_COMPLETE.md docs/ARCHIVE/completed/

# Move GitHub files
mv GITHUB_*.md CODE_OF_CONDUCT.md .github/
```

### Step 3: Update References
Update any internal references in documentation and scripts to point to new locations.

### Step 4: Update .gitignore
```
# Add to .gitignore
learning/*.db
results/*.json
```

### Step 5: Create Index Files
Create README.md files in key directories to explain their contents:
- results/README.md
- learning/README.md
- scripts/test/README.md
- scripts/demo/README.md

## Benefits

1. **Cleaner Root**: Only essential files in project root
2. **Logical Organization**: Related files grouped together
3. **Easier Navigation**: Clear directory structure
4. **Better Git History**: Organized commits by directory
5. **Improved Onboarding**: New contributors can find things easily

## Timeline

This reorganization should take about 30-45 minutes to complete carefully, ensuring all references are updated.

---

*"A well-organized project is a joy to work with and a gift to future contributors."*