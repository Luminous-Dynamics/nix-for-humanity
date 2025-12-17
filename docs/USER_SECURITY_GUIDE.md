# 🔐 User Security Guide: How Luminous Nix Protects Your Data

**Version**: v0.4.0-dev
**Last Updated**: December 2, 2025
**Audience**: End users, system administrators

---

## 🎯 Overview

Luminous Nix protects your system operation history with **military-grade encryption** and **cryptographic signatures**. This guide explains what protection you have and how to use it.

**TL;DR**: Your data is automatically encrypted and protected. You don't need to do anything special - it just works! 🛡️

---

## 🔒 What's Protected?

Every operation you perform with Luminous Nix is recorded and protected:

- **Package installations** - What you installed and when
- **Configuration changes** - System modifications you made
- **Search queries** - What you looked for
- **Error history** - Problems you encountered and how they were fixed

### Why This Matters

Your system history contains sensitive information:
- **Passwords** - Might appear in configuration files
- **API keys** - Could be in package configurations
- **Personal data** - User names, file paths, preferences
- **System internals** - Architecture, vulnerabilities, attack surface

**Luminous Nix encrypts all of this by default.** Even if someone gets access to your disk, they can't read your operation history.

---

## 🛡️ Three Layers of Protection

### Layer 1: Post-Quantum Encryption 🔐

**What**: All operation data is encrypted with Kyber-1024, a quantum-resistant algorithm

**Why**: Traditional encryption (RSA, AES) will be broken by quantum computers in 10-15 years. We use algorithms that will remain secure even against quantum attacks.

**How it works**:
1. Luminous Nix generates an encryption key automatically
2. Every operation is encrypted before saving to disk
3. Only Luminous Nix can decrypt your data

**What you see**:
```bash
$ ls /var/lib/luminous-nix/state/
install_firefox.encrypted
config_webserver.encrypted
```

The `.encrypted` files are unreadable without the encryption key.

### Layer 2: Cryptographic Signatures ✍️

**What**: Every operation is digitally signed to detect tampering

**Why**: Even if encrypted, someone could modify your operation history. Signatures prevent this.

**How it works**:
1. Luminous Nix creates a unique "fingerprint" of each operation
2. This fingerprint is signed with a private key
3. Any modification to the operation breaks the signature
4. Tampered operations are automatically rejected

**What you see**:
```bash
$ ask-nix "show operation history"
✅ install_firefox (signature valid)
✅ update_system (signature valid)
❌ config_webserver (signature invalid - file has been modified!)
```

### Layer 3: Encrypted Backups 💾

**What**: Regular backups of your operation history, also encrypted

**Why**: Protects against data loss from disk failures, system crashes, or accidental deletion

**How it works**:
1. Luminous Nix creates periodic backups automatically
2. Backups are encrypted tar archives
3. Can be restored to recover your history

**What you see**:
```bash
$ ls /var/lib/luminous-nix/backups/
backup_2025-12-02_14-30.tar.gz.encrypted
backup_2025-12-01_14-30.tar.gz.encrypted
```

---

## 🚀 Using Security Features

### Automatic Protection (Default)

**You don't need to do anything!** Security is enabled by default:

```bash
# All these commands automatically use encryption + signing
ask-nix "install firefox"
ask-nix "update system"
ask-nix "generate web server config"
```

Your data is protected automatically.

### Checking Security Status

```bash
# Check if encryption is enabled
ask-nix "security status"

# Output:
# ✅ Encryption: Enabled (Kyber-1024)
# ✅ Signatures: Enabled (RSA-4096)
# ✅ Last Backup: 2 hours ago
# ✅ Operations: 127 encrypted, 127 signed
```

### Manual Backup

```bash
# Create backup now
ask-nix "create backup"

# Output:
# ✅ Backup created: /var/lib/luminous-nix/backups/backup_2025-12-02_15-45.tar.gz.encrypted
# 📦 Size: 2.3 MB (127 operations)
# 🔐 Encrypted: Yes
```

### Restoring from Backup

```bash
# List available backups
ask-nix "list backups"

# Restore specific backup
ask-nix "restore backup backup_2025-12-02_15-45.tar.gz.encrypted"

# Output:
# ✅ Restored 127 operations
# ✅ All signatures verified
# 🎉 Your operation history has been recovered!
```

---

## ⚙️ Advanced Configuration

### Disabling Encryption (Not Recommended)

If you need to disable encryption for some reason:

```bash
# Edit configuration
ask-nix "configure security"

# Set encryption_enabled = false
# Set signing_enabled = false

# WARNING: This makes your data readable by anyone!
```

**⚠️ Only do this if**:
- You're in a completely isolated test environment
- You understand the security risks
- You have a specific reason (like debugging)

### Custom Key Location

By default, keys are stored in `/var/lib/luminous-nix/keys/`. To change this:

```bash
# Edit configuration
ask-nix "configure security"

# Set key_storage_dir = "/custom/path/to/keys"
```

**Important**: Back up your keys! If you lose them, you can't decrypt your data.

### Key Rotation

For maximum security, rotate your encryption keys periodically:

```bash
# Rotate encryption key (recommended every 90 days)
ask-nix "rotate encryption key"

# Output:
# 🔑 Generating new encryption key...
# 🔄 Re-encrypting 127 operations with new key...
# ✅ Key rotation complete!
# 🗑️  Old key archived to: /var/lib/luminous-nix/keys/archive/
```

---

## 🔍 Security FAQ

### Q: Is my data really secure?

**A**: Yes! We use:
- **Kyber-1024**: NIST-standardized post-quantum encryption
- **RSA-4096 with PSS**: Industry-standard signatures
- **AES-256-GCM**: For hybrid encryption mode

These are the same algorithms used by:
- Government agencies
- Banks and financial institutions
- Secure messaging apps (Signal, WhatsApp)

### Q: What if I lose my encryption key?

**A**: **You cannot recover your data without the encryption key.** This is by design - it's what makes the encryption secure.

**To prevent this**:
1. Let Luminous Nix manage keys automatically
2. Back up `/var/lib/luminous-nix/keys/` to secure external storage
3. Never delete the keys directory

### Q: Can I disable encryption for better performance?

**A**: Encryption adds about ~500ms per operation. For most users, this is imperceptible.

**Only disable if**:
- You're on very old hardware (pre-2010)
- You're doing automated testing with thousands of operations
- You understand and accept the security risks

### Q: Does encryption protect against...

| Threat | Protected? | How |
|--------|-----------|-----|
| **Disk theft** | ✅ Yes | Data encrypted, unreadable without key |
| **File access** | ✅ Yes | Even with file access, can't decrypt |
| **Tampering** | ✅ Yes | Signatures detect modifications |
| **Quantum computers** | ✅ Yes | Using quantum-resistant algorithms |
| **Memory dump** | ⚠️ Partial | Data decrypted in memory during use |
| **Keylogger** | ❌ No | Encryption doesn't protect input |
| **Physical access** | ⚠️ Partial | Full disk encryption still recommended |

### Q: How does this compare to other tools?

| Feature | Luminous Nix | Traditional Tools |
|---------|--------------|-------------------|
| **Encryption** | ✅ Default | ❌ Usually not available |
| **Signatures** | ✅ Automatic | ❌ Not included |
| **PQC** | ✅ Yes | ❌ No |
| **Backups** | ✅ Encrypted | ⚠️ Often plaintext |
| **Tamper detection** | ✅ Automatic | ❌ No |

---

## 📊 Performance Impact

### Typical Performance

| Operation | Without Security | With Security | Overhead |
|-----------|------------------|---------------|----------|
| **Package search** | 200ms | 200ms | 0ms |
| **Package install** | 30s | 30.5s | ~500ms |
| **Config generation** | 500ms | 1000ms | ~500ms |
| **System rebuild** | 2min | 2min | ~500ms |

**Bottom line**: Security adds about 500ms overhead, which is negligible for most operations.

### Cold Path vs Hot Path

- **Hot path** (package search, execution): No encryption overhead
- **Cold path** (saving results): Encryption happens here

This means your interactive experience is unchanged, but saving results takes slightly longer.

---

## 🛠️ Troubleshooting

### "Operation signature verification failed"

**What it means**: An operation was modified after being signed

**Possible causes**:
1. Disk corruption
2. Manual file modification
3. Software bug
4. Malicious tampering

**What to do**:
```bash
# Check disk health
sudo smartctl -a /dev/sda

# Restore from backup
ask-nix "restore backup"

# If persistent, report bug
ask-nix "report issue"
```

### "Cannot decrypt operation"

**What it means**: Encryption key doesn't match

**Possible causes**:
1. Wrong key file
2. Corrupted key
3. Key rotation in progress

**What to do**:
```bash
# Check key location
ask-nix "show key location"

# Try archived keys
ask-nix "list archived keys"

# Restore from backup
ask-nix "restore backup"
```

### "Encryption taking too long"

**What it means**: System is slow or under load

**What to do**:
```bash
# Check system load
top

# Temporarily disable if needed
ask-nix "configure security" # Set encryption_enabled = false

# Re-enable after task
ask-nix "configure security" # Set encryption_enabled = true
```

---

## 🎓 Best Practices

### ✅ DO:
- Let Luminous Nix manage keys automatically
- Keep security features enabled
- Back up your keys to secure external storage
- Rotate keys every 90 days
- Use full disk encryption for maximum protection

### ❌ DON'T:
- Disable encryption unless absolutely necessary
- Delete the keys directory
- Share your keys
- Store keys on the same disk as encrypted data
- Modify encrypted files manually

---

## 🚨 Security Incident Response

If you suspect your system has been compromised:

1. **Immediately**:
   ```bash
   ask-nix "check signatures"  # Verify all operations
   ```

2. **If tampering detected**:
   ```bash
   ask-nix "restore backup"    # Restore from known-good backup
   ask-nix "rotate all keys"   # Generate new keys
   ```

3. **Review**:
   ```bash
   ask-nix "show operation history"  # Look for suspicious activity
   ```

4. **Report**:
   ```bash
   ask-nix "report security incident"
   ```

---

## 📚 Additional Resources

- **Developer Guide**: See `docs/DEVELOPER_SECURITY_GUIDE.md` for technical details
- **Migration Guide**: See `docs/MIGRATION_GUIDE.md` for upgrading from unencrypted data
- **Security Architecture**: See `docs/SECURITY_ARCHITECTURE.md` for in-depth technical documentation

---

## 🆘 Getting Help

- **Questions**: Open discussion on GitHub
- **Bugs**: Report issue with `ask-nix "report issue"`
- **Security concerns**: Email security@luminousdynamics.org (PGP key available)

---

**Remember**: Security is automatic and transparent. You don't need to think about it - Luminous Nix handles it for you! 🛡️

*Last updated: December 2, 2025*
