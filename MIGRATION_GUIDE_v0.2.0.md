# 📚 Migration Guide: v0.1.0-alpha → v0.2.0-beta

## Overview

Upgrading from v0.1.0-alpha to v0.2.0-beta is straightforward but brings massive improvements. This guide helps you migrate smoothly to the new neural-powered version.

## 🎯 Key Changes

### What's Different

| Component | v0.1.0-alpha | v0.2.0-beta | Migration Impact |
|-----------|--------------|-------------|------------------|
| **HRM** | Simulation/patterns | Real neural network | Automatic - no changes needed |
| **Cache** | None | 3-tier SQLite cache | Created on first run |
| **Training** | No data | 87 real queries | Included in package |
| **Feedback** | None | Active collection | Optional prompts |
| **Config** | Manual | Auto-configured | Less setup needed |

### Breaking Changes

**None!** v0.2.0-beta is fully backward compatible. All v0.1.0 commands still work.

## 📦 Migration Steps

### Step 1: Backup (Optional)
```bash
# Backup your v0.1.0 installation if desired
cp -r luminous-nix luminous-nix-v0.1.0-backup
```

### Step 2: Download v0.2.0-beta
```bash
# Get the new version
wget https://github.com/Luminous-Dynamics/luminous-nix/releases/download/v0.2.0-beta/luminous-nix-v0.2.0-beta.tar.gz

# Extract (can overwrite v0.1.0 or install separately)
tar -xzf luminous-nix-v0.2.0-beta.tar.gz
```

### Step 3: Run Migration
```bash
cd luminous-nix

# The deploy script handles everything
./deploy.sh

# This will:
# - Update dependencies
# - Initialize the cache
# - Load the neural model
# - Set up feedback collection
```

### Step 4: Test
```bash
# Verify the upgrade
nix-ask "version"
# Should show: v0.2.0-beta

# Test accuracy improvement
nix-ask "install firefox"
# Should be faster and more accurate

# Run beta test (optional)
./test_beta.py
# Should show ~80% accuracy
```

## 🆕 New Features to Try

### 1. Cached Responses (Instant!)
```bash
# First query: ~4ms
nix-ask "install vim"

# Second identical query: <0.1ms (from cache!)
nix-ask "install vim"
```

### 2. Uncertainty Admission
```bash
# The model now admits when unsure
nix-ask "configure quantum blockchain AI"
# Response: "I'm not confident about this. Here's my best guess..."
```

### 3. What-If Analysis
```bash
# Ask hypothetical questions
nix-ask "what if I use flakes instead of channels"
# Provides analysis of trade-offs
```

### 4. Feedback Collection
```bash
# Low-confidence queries ask for feedback
nix-ask "complex unusual query"
# "🤔 I'm not very confident. Did it work? (y/n/skip)"
# Your response trains the model!
```

## 🔧 Configuration Changes

### Cache Location
v0.2.0 adds a cache database at:
```
cache/hrm_cache.db      # SQLite cache
data/feedback.jsonl     # Feedback collection
models/hrm_simple_best.pt # Neural model
```

### Environment Variables (Optional)
```bash
# Adjust cache size (default 100 queries in memory)
export LUMINOUS_CACHE_SIZE=200

# Disable feedback prompts
export LUMINOUS_NO_FEEDBACK=1

# Increase verbosity
export LUMINOUS_VERBOSE=1
```

## 📊 Performance Improvements

After upgrading, you should see:

| Metric | v0.1.0 | v0.2.0 | Improvement |
|--------|--------|--------|-------------|
| **First Query** | 10-50ms | 3-5ms | 3-10x faster |
| **Cached Query** | N/A | <0.1ms | ∞ |
| **Accuracy** | ~40% | 80% | 2x better |
| **Memory Usage** | 100MB | 150MB | +50MB for cache/model |

## 🐛 Troubleshooting

### Issue: Old commands not working
```bash
# Clear cache and reinitialize
rm -rf cache/
poetry run python -c "from luminous_nix.cache.sqlite_cache_enhanced import ThreeTierCache; c = ThreeTierCache(); c.preload_common_queries()"
```

### Issue: Model not loading
```bash
# Retrain the model
poetry run python scripts/train_hrm_neural_fixed.py
```

### Issue: Import errors
```bash
# Ensure you're in the nix environment
nix develop  # or nix-shell
poetry install
```

### Issue: Slower than v0.1.0
This is expected for first-time queries! v0.1.0 had fake <1ms times. v0.2.0's 3-5ms is real. However, cached queries are truly <0.1ms.

## 🎯 Optimization Tips

### 1. Warm the Cache
```bash
# Preload common queries for instant responses
poetry run python -c "
from luminous_nix.cache.sqlite_cache_enhanced import ThreeTierCache
cache = ThreeTierCache()
cache.preload_common_queries()
print('Cache warmed!')
"
```

### 2. Provide Feedback
Help improve accuracy:
```bash
# When prompted "Did this work?"
# Answer honestly - this trains the model
```

### 3. Submit Problem Queries
If something consistently fails:
```bash
# Report at: https://github.com/Luminous-Dynamics/luminous-nix/issues
# Include the query and expected result
```

## 🔄 Rollback (If Needed)

To revert to v0.1.0-alpha:
```bash
# If you backed up
rm -rf luminous-nix
mv luminous-nix-v0.1.0-backup luminous-nix

# Or download v0.1.0 again
wget [v0.1.0-alpha URL]
tar -xzf luminous-nix-v0.1.0-alpha.tar.gz
```

## 📈 What's Next

After migrating to v0.2.0-beta:

1. **Use it naturally** - Every query improves the model
2. **Provide feedback** - Help reach 90% accuracy
3. **Report issues** - Help identify edge cases
4. **Try new features** - Explore uncertainty and what-if analysis

## 🙏 Thank You!

Thank you for being an early adopter! Your usage of v0.1.0-alpha provided valuable insights that made v0.2.0-beta possible. Your continued use will help us reach v1.0 with 95%+ accuracy.

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/Luminous-Dynamics/luminous-nix/issues)
- **Discussion**: [GitHub Discussions](https://github.com/Luminous-Dynamics/luminous-nix/discussions)
- **Quick Help**: Run `nix-ask "help"` with v0.2.0

---

*"From simulation to neural reality - welcome to the future of NixOS management!"*