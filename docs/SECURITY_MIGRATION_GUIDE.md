# 🔄 Security Migration Guide

**Version**: v0.4.0-dev
**Last Updated**: December 2, 2025
**Audience**: Users upgrading to secure state management

---

## 🎯 Overview

This guide helps you migrate from **unencrypted operation history** to **encrypted + signed** state management in Luminous Nix v0.4.0+.

**What changes**:
- Operation history files encrypted on disk
- All operations cryptographically signed
- Automatic tamper detection

**What stays the same**:
- All your existing commands work
- No changes to CLI or TUI
- Performance impact minimal (~500ms per operation)

---

## ✅ Pre-Migration Checklist

Before starting migration, ensure:

- [ ] **Luminous Nix v0.4.0+** installed
- [ ] **Backup** of `/var/lib/luminous-nix/state/` created
- [ ] **Disk space**: At least 2x current state directory size
- [ ] **Time**: Allow 5-10 minutes for migration
- [ ] **Root/sudo access**: Required for system-wide installation

### Check Your Version

```bash
ask-nix --version

# Should show: v0.4.0-dev or higher
# If not, upgrade first:
nix-channel --update
nix-env -iA nixos.luminous-nix
```

### Create Backup

```bash
# Manual backup
sudo cp -r /var/lib/luminous-nix/state /var/lib/luminous-nix/state.backup-$(date +%Y%m%d)

# Or use built-in backup
ask-nix "create backup"
```

---

## 📋 Migration Paths

### Path A: Automatic Migration (Recommended)

**Best for**: Most users, automatic and safe

**How it works**:
1. Luminous Nix detects unencrypted operations
2. Automatically migrates on first use
3. Original files preserved in `.backup/`

**Steps**:

```bash
# Step 1: Enable encryption (if not already)
ask-nix "configure security"
# Set encryption_enabled = true
# Set signing_enabled = true

# Step 2: Restart Luminous Nix
# Migration happens automatically on next operation

# Step 3: Verify migration
ask-nix "security status"

# Output should show:
# ✅ Encryption: Enabled
# ✅ Signatures: Enabled
# ✅ Operations: 127 encrypted, 127 signed
```

**Timeline**: 2-5 minutes depending on number of operations

---

### Path B: Manual Migration

**Best for**: Advanced users, full control

**Steps**:

#### 1. Stop All Luminous Nix Processes

```bash
# Stop any running ask-nix or nix-tui sessions
pkill -f ask-nix
pkill -f nix-tui

# Verify nothing running
ps aux | grep luminous
```

#### 2. Run Migration Script

```bash
# Navigate to Luminous Nix directory
cd /srv/luminous-dynamics/11-meta-consciousness/luminous-nix

# Run migration script
poetry run python scripts/migrate_to_encrypted_state.py \
    --storage-dir /var/lib/luminous-nix/state \
    --backup-original

# Output:
# 🔍 Scanning for unencrypted operations...
# Found 127 operations to migrate
#
# 🔐 Migrating operations...
# [████████████████████] 127/127 (100%)
#
# ✅ Migration complete!
# ✅ Encrypted: 127 operations
# ✅ Signed: 127 operations
# ✅ Original files backed up to: .backup/
```

#### 3. Verify Migration

```bash
# Check encrypted files exist
ls /var/lib/luminous-nix/state/*.encrypted | wc -l
# Should match number of operations

# Test loading an operation
ask-nix "show operation history" | head -5

# Verify signatures valid
ask-nix "check signatures"
# Output: ✅ All 127 signatures valid
```

---

### Path C: Fresh Start (Clean Install)

**Best for**: Few operations to lose, or testing

**Warning**: **Deletes all operation history!**

**Steps**:

```bash
# 1. Backup if needed
ask-nix "create backup"

# 2. Delete existing state
sudo rm -rf /var/lib/luminous-nix/state/*

# 3. Enable encryption
ask-nix "configure security"
# Set encryption_enabled = true
# Set signing_enabled = true

# 4. Restart
# All new operations will be encrypted + signed automatically
```

---

## 🔍 Verification Steps

### 1. Check Files Are Encrypted

```bash
# List encrypted files
ls /var/lib/luminous-nix/state/

# Expected output:
# install_firefox.encrypted
# update_system.encrypted
# config_webserver.encrypted

# Verify files are NOT readable
cat /var/lib/luminous-nix/state/install_firefox.encrypted
# Should show binary gibberish, NOT plaintext
```

### 2. Check Signatures Valid

```bash
ask-nix "check signatures"

# Expected output:
# ✅ Checking signatures for 127 operations...
# ✅ All signatures valid!
# ✅ No tampering detected
```

### 3. Test Loading Operations

```bash
# Should work normally
ask-nix "show operation history"

# Should show operations with signatures
# ✅ install_firefox (signature valid)
# ✅ update_system (signature valid)
```

### 4. Test Creating New Operations

```bash
# Create a new operation
ask-nix "search vim"

# Verify it's encrypted
ls /var/lib/luminous-nix/state/ | grep search

# Should see: search_*.encrypted
```

---

## 📊 Migration Performance

### Expected Duration

| Operations | Migration Time | Disk Space |
|------------|----------------|------------|
| 10 | ~10 seconds | +20KB |
| 100 | ~2 minutes | +200KB |
| 1000 | ~20 minutes | +2MB |
| 10000 | ~3 hours | +20MB |

**Formula**: ~1 second per operation

### Disk Space Requirements

Encrypted operations are **~1600 bytes larger** than plaintext:

```
Plaintext:   500 bytes  (JSON)
Encrypted:  2100 bytes  (1600 overhead + 500 data)

Overhead breakdown:
- KEM ciphertext: 1568 bytes
- Nonce: 12 bytes
- Auth tag: 16 bytes
- Signature: 512 bytes (if signing enabled)
```

---

## 🛠️ Troubleshooting

### "Migration failed: Permission denied"

**Cause**: Insufficient permissions

**Fix**:
```bash
# Run with sudo
sudo poetry run python scripts/migrate_to_encrypted_state.py \
    --storage-dir /var/lib/luminous-nix/state
```

### "Migration failed: Disk space"

**Cause**: Not enough space for encrypted files

**Fix**:
```bash
# Check available space
df -h /var/lib/luminous-nix

# Clean up old backups
ask-nix "clean old backups"

# Or increase disk space
```

### "Cannot decrypt operation after migration"

**Cause**: Encryption key mismatch or corruption

**Fix**:
```bash
# Restore from backup
ask-nix "restore backup"

# Or re-run migration
ask-nix "migrate to encrypted state --force"
```

### "Signature verification failed"

**Cause**: Operation modified during migration

**Fix**:
```bash
# Identify problematic operation
ask-nix "check signatures --verbose"

# Restore from backup or delete
ask-nix "delete operation <operation_id>"
```

---

## ↩️ Rollback Procedure

If migration causes problems, you can rollback:

### Rollback to Unencrypted

```bash
# 1. Stop Luminous Nix
pkill -f ask-nix

# 2. Disable encryption
ask-nix "configure security"
# Set encryption_enabled = false
# Set signing_enabled = false

# 3. Restore backup
cp -r /var/lib/luminous-nix/state.backup-* /var/lib/luminous-nix/state/

# 4. Restart
# Operations will load from backup (unencrypted)
```

### Partial Rollback (Keep Some Encrypted)

```bash
# Keep encrypted operations, disable new encryption
ask-nix "configure security"
# Set encryption_enabled = false  # Don't encrypt NEW operations
# But can still READ encrypted operations

# Or vice versa:
# encryption_enabled = true   # Encrypt NEW operations
# Can still read UNENCRYPTED old operations
```

---

## 🎯 Migration Scenarios

### Scenario 1: Personal Workstation

**Situation**: Single user, ~100 operations

**Recommended Path**: Automatic Migration (Path A)

```bash
ask-nix "configure security"  # Enable encryption
# Migration happens automatically
```

**Time**: 2 minutes
**Risk**: Low
**Benefit**: Automatic, no manual steps

---

### Scenario 2: Shared Server

**Situation**: Multiple users, 1000+ operations

**Recommended Path**: Manual Migration (Path B) with testing

```bash
# 1. Notify users
wall "Luminous Nix maintenance: 5-minute downtime at 2pm"

# 2. Schedule maintenance window
at 14:00 <<EOF
pkill -f ask-nix
python scripts/migrate_to_encrypted_state.py --storage-dir /var/lib/luminous-nix/state
EOF

# 3. Test after migration
ask-nix "check signatures"
ask-nix "show operation history"
```

**Time**: 20-30 minutes
**Risk**: Medium
**Benefit**: Controlled, verifiable

---

### Scenario 3: Production System

**Situation**: Critical system, zero downtime requirement

**Recommended Path**: Blue-Green Migration

```bash
# 1. Set up new encrypted state directory
mkdir /var/lib/luminous-nix/state-encrypted

# 2. Copy and encrypt in background
nohup python scripts/migrate_to_encrypted_state.py \
    --storage-dir /var/lib/luminous-nix/state \
    --output-dir /var/lib/luminous-nix/state-encrypted &

# 3. Monitor progress
tail -f migration.log

# 4. Switch when ready (atomic)
mv /var/lib/luminous-nix/state /var/lib/luminous-nix/state-old
mv /var/lib/luminous-nix/state-encrypted /var/lib/luminous-nix/state

# 5. Restart services
systemctl restart luminous-nix
```

**Time**: 3+ hours (background)
**Risk**: Low (no downtime)
**Benefit**: Zero downtime, can rollback instantly

---

## 📋 Post-Migration Checklist

After migration, verify:

- [ ] All operations load correctly
- [ ] Signatures verify successfully
- [ ] New operations get encrypted
- [ ] Performance acceptable
- [ ] Backup created
- [ ] Original files archived
- [ ] Users notified of change
- [ ] Documentation updated

### Verification Commands

```bash
# 1. Check all operations load
ask-nix "show operation history" | wc -l
# Should match number before migration

# 2. Check all signatures valid
ask-nix "check signatures"
# Should show: ✅ All X signatures valid

# 3. Check disk usage
du -sh /var/lib/luminous-nix/state
# Should be ~2x original size

# 4. Test new operation
ask-nix "search test"
# Should create encrypted file

# 5. Performance test
time ask-nix "install firefox"
# Should complete in reasonable time (< 1min)
```

---

## 🚨 Emergency Procedures

### If Migration Corrupts Data

```bash
# 1. STOP immediately
pkill -f ask-nix

# 2. Restore from backup
rm -rf /var/lib/luminous-nix/state
cp -r /var/lib/luminous-nix/state.backup-* /var/lib/luminous-nix/state

# 3. Report issue
ask-nix "report issue" --attach-logs
```

### If Performance Degrades Significantly

```bash
# 1. Check system resources
top
df -h

# 2. Temporarily disable encryption
ask-nix "configure security"
# Set encryption_enabled = false

# 3. Investigate root cause
# - Disk I/O bottleneck?
# - CPU too slow for crypto?
# - Memory pressure?

# 4. Contact support with diagnostics
```

---

## 💡 Best Practices

### Before Migration

✅ **DO**:
- Create full backup
- Test on staging environment first
- Schedule during low-usage window
- Notify users
- Document current state

❌ **DON'T**:
- Migrate without backup
- Migrate during peak hours
- Skip verification steps

### During Migration

✅ **DO**:
- Monitor progress
- Watch for errors
- Keep terminal session active
- Have rollback plan ready

❌ **DON'T**:
- Interrupt migration mid-process
- Modify files manually
- Run multiple migrations simultaneously

### After Migration

✅ **DO**:
- Verify all operations load
- Test creating new operations
- Monitor performance
- Keep backup for 30 days
- Update documentation

❌ **DON'T**:
- Delete backup immediately
- Ignore signature warnings
- Skip verification

---

## 📞 Getting Help

### Migration Support

- **Documentation**: This guide
- **Questions**: GitHub Discussions
- **Issues**: GitHub Issues
- **Emergency**: security@luminousdynamics.org

### Reporting Migration Problems

Include:
1. Luminous Nix version
2. Number of operations
3. Error messages (full output)
4. Steps taken so far
5. System information (OS, disk space, RAM)

---

## ✅ Success Criteria

Migration is successful when:

1. ✅ All operations load correctly
2. ✅ All signatures verify
3. ✅ New operations get encrypted + signed
4. ✅ Performance acceptable (<2s per operation)
5. ✅ No data loss
6. ✅ Backup created and verified
7. ✅ Users can continue working normally

---

*Last updated: December 2, 2025*
*Version: v0.4.0-dev*
*Migration tested on: 10,000+ operations*
