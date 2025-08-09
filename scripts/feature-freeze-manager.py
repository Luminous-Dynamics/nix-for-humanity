#!/usr/bin/env python3
"""
from typing import List, Dict
Feature Freeze Manager - Enforce focus on stability over new features
Helps resist scope creep during the improvement phase
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set

class FeatureFreezeManager:
    """Manage feature freeze to ensure focus on quality."""
    
    def __init__(self):
        self.freeze_file = Path(".feature-freeze.json")
        self.freeze_data = self.load_freeze_data()
        
    def load_freeze_data(self) -> Dict:
        """Load or create feature freeze configuration."""
        if self.freeze_file.exists():
            with open(self.freeze_file, 'r') as f:
                return json.load(f)
        
        # Create default freeze configuration
        return {
            "freeze_start": datetime.now().isoformat(),
            "freeze_end": (datetime.now() + timedelta(weeks=6)).isoformat(),
            "allowed_changes": [
                "bug fixes",
                "test improvements", 
                "documentation updates",
                "performance optimization",
                "reliability improvements",
                "code cleanup"
            ],
            "blocked_patterns": [
                "new feature",
                "add support for",
                "implement new",
                "create new capability",
                "introduce"
            ],
            "exceptions": [],
            "baseline_features": self.scan_current_features()
        }
    
    def scan_current_features(self) -> Dict[str, str]:
        """Scan codebase for current feature set."""
        features = {}
        
        # Scan for feature indicators
        feature_files = [
            "frontends/voice",
            "frontends/tui", 
            "frontends/gui",
            "features/personas",
            "features/learning",
            "features/federation"
        ]
        
        for feature_path in feature_files:
            if os.path.exists(feature_path):
                # Calculate hash of directory
                dir_hash = self.hash_directory(feature_path)
                features[feature_path] = dir_hash
        
        return features
    
    def hash_directory(self, path: str) -> str:
        """Create hash of directory contents."""
        hasher = hashlib.md5()
        
        for root, dirs, files in os.walk(path):
            # Skip hidden and cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in sorted(files):
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'rb') as f:
                            hasher.update(f.read())
                    except Exception:
                        # TODO: Add proper error handling
                        pass  # Silent for now, should log error
        
        return hasher.hexdigest()
    
    def check_commit_message(self, message: str) -> tuple[bool, str]:
        """Check if commit message indicates new feature."""
        message_lower = message.lower()
        
        # Check for blocked patterns
        for pattern in self.freeze_data["blocked_patterns"]:
            if pattern in message_lower:
                return False, f"Feature freeze active! Commit message contains '{pattern}'"
        
        # Check for allowed patterns
        for allowed in self.freeze_data["allowed_changes"]:
            if allowed in message_lower:
                return True, "Commit allowed: " + allowed
        
        # Default suspicious
        return False, "Feature freeze active! Please clarify if this is a bug fix or new feature"
    
    def check_file_changes(self, changed_files: List[str]) -> tuple[bool, List[str]]:
        """Check if file changes indicate new features."""
        violations = []
        
        for file in changed_files:
            # Check for new feature directories
            if any(part in file for part in ['new_feature', 'v2', 'experimental', 'alpha']):
                violations.append(f"Suspicious path: {file}")
            
            # Check for new frontend
            if file.startswith('frontends/') and not any(
                file.startswith(f'frontends/{known}/') 
                for known in ['cli', 'tui', 'voice']
            ):
                violations.append(f"New frontend detected: {file}")
            
            # Check for feature expansion
            if 'features/' in file and file.endswith('.py'):
                feature_dir = file.split('/')[1]
                if feature_dir not in self.freeze_data["baseline_features"]:
                    violations.append(f"New feature module: {file}")
        
        return len(violations) == 0, violations
    
    def create_pre_commit_hook(self):
        """Create git pre-commit hook to enforce freeze."""
        hook_content = '''#!/usr/bin/env python3
"""
Pre-commit hook to enforce feature freeze.
Prevents accidental feature additions during stability phase.
"""

import subprocess
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.feature_freeze_manager import FeatureFreezeManager

def main():
    # Get commit message
    with open(sys.argv[1], 'r') as f:
        commit_msg = f.read()
    
    # Check feature freeze
    manager = FeatureFreezeManager()
    
    # Check commit message
    allowed, reason = manager.check_commit_message(commit_msg)
    if not allowed:
        print(f"\\n🚫 COMMIT BLOCKED: {reason}")
        print("\\n📋 During feature freeze, only these changes are allowed:")
        for change in manager.freeze_data["allowed_changes"]:
            print(f"  - {change}")
        print("\\nTo override (not recommended):")
        print("  git commit --no-verify")
        return 1
    
    # Get changed files
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only'],
        capture_output=True,
        text=True
    )
    changed_files = result.stdout.strip().split('\\n')
    
    # Check files
    files_ok, violations = manager.check_file_changes(changed_files)
    if not files_ok:
        print("\\n🚫 COMMIT BLOCKED: New features detected during freeze")
        for violation in violations:
            print(f"  - {violation}")
        print("\\nFocus on stability improvements only!")
        return 1
    
    print(f"✅ Commit allowed: {reason}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
'''
        
        # Create hooks directory
        os.makedirs('.git/hooks', exist_ok=True)
        
        # Write hook
        hook_path = '.git/hooks/prepare-commit-msg'
        with open(hook_path, 'w') as f:
            f.write(hook_content)
        
        # Make executable
        os.chmod(hook_path, 0o755)
        
        print("✅ Created git pre-commit hook")
    
    def generate_focus_report(self):
        """Generate report on what to focus on."""
        report = f"""
# Feature Freeze Focus Report

**Freeze Period**: {self.freeze_data['freeze_start'][:10]} to {self.freeze_data['freeze_end'][:10]}

## 🎯 What to Focus On

### 1. Bug Fixes (Highest Priority)
- Fix install/remove command reliability
- Resolve search functionality issues  
- Address timeout problems
- Fix error messages

### 2. Test Coverage
- Replace mocks with real tests
- Add integration tests
- Create performance benchmarks
- Test all user paths

### 3. Performance
- Implement native Python-Nix API fully
- Optimize slow operations
- Reduce memory usage
- Improve startup time

### 4. Documentation
- Update README to reflect reality
- Fix incorrect examples
- Document actual features
- Add troubleshooting guides

### 5. Code Quality
- Consolidate duplicate code
- Fix import paths
- Remove dead code
- Improve error handling

## 🚫 What NOT to Do

### Blocked Activities:
- ❌ Adding new features
- ❌ Starting new interfaces
- ❌ Implementing new personas
- ❌ Adding new dependencies
- ❌ Creating new modules

### Exceptions:
If you absolutely must add something new, document why in `.feature-freeze.json` exceptions.

## 📊 Current Status

**Baseline Features Tracked**: {len(self.freeze_data['baseline_features'])}

**Remember**: Every hour spent on new features is an hour not spent making existing features work properly.

## 🎯 Success Criteria

By end of freeze, we should have:
- ✅ 95%+ test coverage
- ✅ All basic commands working reliably
- ✅ Performance targets met
- ✅ Documentation matches reality
- ✅ No critical bugs

Stay focused! 🎯
"""
        
        with open('FEATURE_FREEZE_FOCUS.md', 'w') as f:
            f.write(report)
        
        print("📄 Generated FEATURE_FREEZE_FOCUS.md")
    
    def save_freeze_data(self):
        """Save freeze configuration."""
        with open(self.freeze_file, 'w') as f:
            json.dump(self.freeze_data, f, indent=2)
    
    def enforce_freeze(self):
        """Main enforcement routine."""
        print("🧊 Enforcing Feature Freeze")
        print("=" * 50)
        
        # Save configuration
        self.save_freeze_data()
        
        # Create git hook
        self.create_pre_commit_hook()
        
        # Generate focus report
        self.generate_focus_report()
        
        # Show summary
        freeze_end = datetime.fromisoformat(self.freeze_data['freeze_end'])
        days_remaining = (freeze_end - datetime.now()).days
        
        print(f"\n📅 Feature freeze active for {days_remaining} more days")
        print("\n✅ Allowed changes:")
        for change in self.freeze_data["allowed_changes"]:
            print(f"  - {change}")
        
        print("\n🚫 Blocked patterns in commits:")
        for pattern in self.freeze_data["blocked_patterns"]:
            print(f"  - '{pattern}'")
        
        print("\n📋 See FEATURE_FREEZE_FOCUS.md for detailed guidance")
        print("\n🎯 Remember: Stability > Features!")

def main():
    """Enforce feature freeze."""
    manager = FeatureFreezeManager()
    manager.enforce_freeze()

if __name__ == "__main__":
    main()