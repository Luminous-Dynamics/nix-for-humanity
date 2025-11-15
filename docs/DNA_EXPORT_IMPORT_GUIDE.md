# 🧬 DNA Export/Import/Breed Guide

*Share, combine, and evolve your NixOS configurations genetically*

## 📤 DNA Export - Share Your Configuration Genetics

Export your configuration's DNA for sharing with others or backing up your system's genetic profile.

### Basic Export
```bash
# Export to JSON (default)
ask-nix dna export /etc/nixos/configuration.nix --output my-config.json

# Export to different formats
ask-nix dna export config.nix --format yaml --output config.yaml
ask-nix dna export config.nix --format nix --output config.nix.dna
ask-nix dna export config.nix --format compressed --output config.dna.gz

# Include raw configuration (for complete backup)
ask-nix dna export config.nix --include-raw --output backup.json
```

### Export Formats

#### JSON Format (Default)
```json
{
  "version": "1.0.0",
  "exported_at": "2025-09-04T22:54:27.466239",
  "source_system": "luminous (Linux 6.16.0)",
  "dna": {
    "fingerprint": "768da5d4304c8545",
    "profile_type": "developer",
    "complexity_score": 45.2,
    "genes": [...]
  }
}
```

#### Nix Format
```nix
# DNA Configuration Export
# Fingerprint: 768da5d4304c8545
# Profile: developer
{
  dna = {
    fingerprint = "768da5d4304c8545";
    profile = "developer";
    genes = [...];
  };
}
```

#### Compressed Format
- Base64-encoded gzipped JSON
- Smallest file size for sharing
- Ideal for embedding in documents

## 📥 DNA Import - Apply Shared Genetics

Import configuration DNA from others to learn from their setups.

### Basic Import
```bash
# Import and inspect DNA
ask-nix dna import shared-config.json

# Import and apply to your configuration
ask-nix dna import shared-config.json --apply /etc/nixos/configuration.nix

# Import without validation (for different NixOS versions)
ask-nix dna import config.json --no-validate

# Keep your custom settings when applying
ask-nix dna import config.json --apply config.nix --preserve-custom
```

### Import Output
```
🧬 DNA Import Successful

📍 Fingerprint: 768da5d4304c8545
🏷️ Profile: developer
📊 Complexity: 45.2/100
🌱 Evolution: mature
🖥️ Source: friend-laptop (Linux 6.15.0)
📝 Description: Optimized development configuration
🏷️ Tags: rust, docker, neovim
```

## 🧬 DNA Breeding - Create Hybrid Configurations

Combine two configurations to create offspring with the best traits from both parents.

### Basic Breeding
```bash
# Breed two configurations
ask-nix dna breed parent1.nix parent2.nix

# Breed with visualization
ask-nix dna breed desktop.nix server.nix --visualize

# Save offspring DNA
ask-nix dna breed config1.nix config2.nix --output offspring.json

# Choose breeding strategy
ask-nix dna breed a.nix b.nix --strategy hybrid_vigor
```

### Breeding Strategies

#### best_of_both (Default)
Selects the best genes from each parent based on prevalence and impact.
```bash
ask-nix dna breed desktop.nix gaming.nix --strategy best_of_both
```
- ✅ Most stable offspring
- ✅ Proven gene combinations
- ✅ Lower mutation rate

#### hybrid_vigor
Maximizes genetic diversity by combining unique traits from both parents.
```bash
ask-nix dna breed minimal.nix complex.nix --strategy hybrid_vigor
```
- ✅ Maximum diversity
- ✅ Novel combinations
- ⚠️ Higher mutation rate
- 🧪 May discover new optimizations

#### selective
Allows weighted selection of traits from each parent.
```bash
ask-nix dna breed secure.nix fast.nix --strategy selective
```
- ✅ Controlled breeding
- ✅ Predictable results
- 📊 Custom trait weights

#### random_mix
Randomly combines genes for experimental configurations.
```bash
ask-nix dna breed old.nix new.nix --strategy random_mix
```
- 🎲 Unpredictable results
- 🧪 Maximum experimentation
- ⚠️ Requires testing
- 💡 May find unexpected synergies

### Breeding Output Example
```
🧬 Breeding Configuration DNA

👨 Parent 1: desktop-config.nix
👩 Parent 2: server-config.nix
🧪 Strategy: hybrid_vigor

👶 Offspring Created!

📍 Fingerprint: 9b554f0f1f8bd0f2
🏷️ Profile: hybrid
📊 Complexity: 52.3/100
🧬 Gene Count: 47
🌈 Diversity: 85.0%
💪 Fitness: 90.0%

🔄 Mutations:
  • hybrid_vigor
  • diverse_genetics
  • enhanced_performance

     🧬 Configuration DNA Helix 🧬
     ══════════════════════════
     │    A═══T    │
     │   G≡≡≡C     │
     │  C···G      │
     ...
```

## 🔬 DNA Compatibility Check

Check if two DNA packages can be safely combined.

```bash
# Check compatibility
ask-nix dna compatibility config1.json config2.json
```

Output:
```
🧬 DNA Compatibility Check

✅ Compatible
📊 Similarity: 65%
🧬 Shared Genes: 23
1️⃣ Unique to First: 12
2️⃣ Unique to Second: 18
💍 Breeding Potential: 35%
```

## 🎯 Practical Use Cases

### 1. Team Configuration Sharing
```bash
# Team lead exports optimized config
ask-nix dna export /etc/nixos/configuration.nix --output team-dna.json

# Team members import and apply
ask-nix dna import team-dna.json --apply /etc/nixos/configuration.nix
```

### 2. Configuration Backup
```bash
# Export with raw config for complete backup
ask-nix dna export config.nix --include-raw --format compressed --output backup.dna.gz

# Restore from backup
ask-nix dna import backup.dna.gz --apply new-config.nix
```

### 3. Creating Specialized Hybrids
```bash
# Combine gaming and development configs
ask-nix dna breed gaming.nix dev.nix --strategy hybrid_vigor --output gamedev.json

# Apply the hybrid
ask-nix dna import gamedev.json --apply /etc/nixos/configuration.nix
```

### 4. Configuration Evolution
```bash
# Export current DNA
ask-nix dna export config.nix --output gen1.json

# Make changes and export again
# ... edit configuration ...
ask-nix dna export config.nix --output gen2.json

# Breed old and new for best of both
ask-nix dna breed gen1.json gen2.json --output evolved.json
```

## 🔐 Privacy & Security

### What's Included in DNA Export
- ✅ Configuration patterns (genes)
- ✅ System profile type
- ✅ Complexity metrics
- ✅ Evolution history
- ❌ Passwords or secrets
- ❌ User-specific data
- ❌ Network credentials
- ❌ Private keys

### Safe Sharing
DNA exports contain only structural information about your configuration:
- Package selections
- Service enablement patterns
- System preferences
- Optimization settings

No sensitive data is ever included in DNA exports.

## 🧪 Advanced Features

### Multi-Generation Breeding
```bash
# Create multiple generations
ask-nix dna breed parent1.nix parent2.nix --output gen1.json
ask-nix dna breed gen1.json parent3.nix --output gen2.json
ask-nix dna breed gen2.json parent4.nix --output gen3.json

# Track evolution
ask-nix dna lineage gen3.json
```

### Configuration DNA Banks
Share your DNA with the community:
```bash
# Export for sharing
ask-nix dna export config.nix --format compressed --output my-dna.gz

# Share on GitHub, forums, etc.
# Others can import and learn from your configuration
```

### Automated Breeding Pipeline
```bash
#!/bin/bash
# Breed all configs in a directory
for config1 in configs/*.nix; do
  for config2 in configs/*.nix; do
    if [ "$config1" != "$config2" ]; then
      name1=$(basename $config1 .nix)
      name2=$(basename $config2 .nix)
      ask-nix dna breed $config1 $config2 \
        --output "offspring/${name1}-${name2}.json"
    fi
  done
done
```

## 📊 Understanding Breeding Metrics

### Fitness Score (0-100%)
- **80-100%**: Excellent - highly optimized offspring
- **60-80%**: Good - solid configuration
- **40-60%**: Average - needs optimization
- **Below 40%**: Poor - reconsider breeding strategy

### Diversity Score (0-100%)
- **80-100%**: Very diverse - many different gene types
- **60-80%**: Good diversity - balanced configuration
- **40-60%**: Moderate - some specialization
- **Below 40%**: Low diversity - highly specialized

### Mutation Rate (0.0-1.0)
- **0.0-0.1**: Stable - few changes from parents
- **0.1-0.2**: Normal - healthy evolution
- **0.2-0.3**: Active - significant changes
- **Above 0.3**: Experimental - many new patterns

## 🌟 Best Practices

### For Exporting
1. Export regularly to track evolution
2. Use compressed format for sharing
3. Include raw config only for backups
4. Add descriptions and tags for context

### For Importing
1. Always validate compatibility first
2. Test in VM before applying to main system
3. Keep backups before applying DNA
4. Preserve custom settings when appropriate

### For Breeding
1. Start with similar parent configurations
2. Use hybrid_vigor for maximum innovation
3. Test offspring in isolated environments
4. Track multiple generations for best results

## 🎉 Summary

Configuration DNA export/import/breeding brings genetic algorithms to NixOS configuration management:

- **Share** configurations as genetic profiles
- **Learn** from community DNA
- **Combine** the best traits from multiple sources
- **Evolve** your configuration over time
- **Discover** new optimization patterns

Your configuration is now a living organism that can reproduce, evolve, and share its best traits with others!

---

*v0.6.1 - Configuration genetics for the NixOS ecosystem*
