# 🚀 Luminous Nix v0.5.1: Real Backend is Now Default!

## 🎯 The Simplification Release

**v0.5.1 makes the real NixOS backend the default - no environment variable needed!**

## ✨ Major Change: Real by Default

### Before (v0.5.0)
```bash
# Had to explicitly enable real backend
export LUMINOUS_USE_REAL_BACKEND=true
ask-nix "search vim"
```

### Now (v0.5.1) 
```bash
# Just works with real backend!
ask-nix "search vim"
```

## 🔧 Technical Changes

- **Default behavior reversed**: Real backend is now default
- **New override variable**: `LUMINOUS_USE_MOCK_BACKEND=true` (for testing only)
- **Simplified user experience**: No configuration needed for real functionality

## 📊 Backward Compatibility

- ✅ **Fully backward compatible**
- Old `LUMINOUS_USE_REAL_BACKEND` variable is ignored (no longer needed)
- Mock backend still available for testing with new variable

## 🚀 Usage

### Standard Usage (Real Backend - Default)
```bash
# No environment variables needed!
ask-nix help
ask-nix "search firefox"
ask-nix "install vim"

# Still recommended to use dry-run for safety
export LUMINOUS_DRY_RUN=true
ask-nix "remove package"
```

### Testing with Mock Backend (Optional)
```bash
# Only for developers/testing
export LUMINOUS_USE_MOCK_BACKEND=true
ask-nix "test command"
```

## 📦 Installation

```bash
# Upgrade existing installation
pip install --upgrade luminous-nix==0.5.1

# Fresh install
pip install luminous-nix==0.5.1
```

## 🎭 Philosophy

*"Make the right thing the easy thing"*

Users shouldn't need to configure anything to get real functionality. The tool should just work.

## 📈 User Experience Improvement

| Aspect | v0.5.0 | v0.5.1 |
|--------|--------|--------|
| Setup Required | Export variable | None |
| Default Behavior | Mock | Real |
| User Friction | Medium | Zero |
| Documentation Needed | Yes | Minimal |

## 🚀 What's Next

- **v0.5.2**: Remove mock backend entirely (simplify codebase)
- **v0.5.3**: Improve design and user experience

---

**The bottom line**: v0.5.1 removes friction - the tool now "just works" with real NixOS commands by default.

*Released: 2025-01-27*  
*Zero Configuration Required!* 🎉