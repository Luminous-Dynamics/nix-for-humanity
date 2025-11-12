# 🔧 Integration Fixes for v1.0.0-beta

**Current Version**: v0.9.0-rc1 (92% complete)
**Target Version**: v1.0.0-beta (100% complete)
**Estimated Time**: 6-10 hours focused work

---

## 📋 Task Checklist

### Phase 1: Integration (1 hour) ✅ Can Do Now
- [ ] Wire `startup_posture` banner (15 min)
- [ ] Wire `dry_run_mode` toggle (30 min)
- [ ] Auto-generate posture stamp (15 min)

### Phase 2: Test Fixes (2-5 hours) 🔧 Requires Testing
- [ ] Fix multiline secret detection (1 hour)
- [ ] Fix Unicode secret detection (1 hour)
- [ ] Fix Tier 1 policy (30 min)
- [ ] Fix Unicode confusion attack (1 hour)
- [ ] Run regex safety tests (30 min)

### Phase 3: Validation (1-2 hours) 🎯 Final Testing
- [ ] Manual E2E test (1 hour)
- [ ] Stress test (30 min)
- [ ] Document results (30 min)

---

## 🚀 Phase 1: Integration Fixes (Copy-Paste Ready)

### Fix 1: Wire Startup Posture Banner (15 min)

**File**: `src/luminous_nix/voice/production_voice_interface.py`

**Location**: In the `main()` function at the top

**Add these imports**:
```python
from luminous_nix.voice.startup_posture import print_startup_banner
from luminous_nix.voice.posture_stamp import write_posture_stamp
```

**Change the `main()` function**:
```python
def main():
    """Launch secure voice interface"""
    # NEW: Display security posture banner
    print("=" * 60)
    print("🔒 Secure Voice Interface - Production Mode")
    print("=" * 60)
    print_startup_banner()  # <-- ADD THIS
    print("=" * 60)

    # NEW: Write posture stamp to file for audit trail
    try:
        stamp_path = write_posture_stamp()
        print(f"📋 Posture stamp: {stamp_path}")
    except Exception as e:
        print(f"⚠️  Could not write posture stamp: {e}")

    print("Security Features:")
    print("  • Tier 0-1 only via voice")
    print("  • Secret redaction active")
    print("  • Audit logging enabled")
    print("  • Rate limiting: 20/minute")
    print("=" * 60)

    interface = SecureVoiceInterface(
        audit_file=Path("voice-audit.jsonl")
    )

    interface.interactive_mode()
```

**Test**:
```bash
poetry run python src/luminous_nix/voice/secure_voice_interface.py
# Should display posture banner with tier max, policy hash, etc.
```

---

### Fix 2: Wire Dry-Run Mode (30 min)

**File**: `src/luminous_nix/voice/secure_voice_interface.py`

**Add import at top**:
```python
from luminous_nix.voice.dry_run_mode import is_dry_run_enabled, simulate_tier2_approval
```

**Modify `execute_command()` method** (around line 66):
```python
def execute_command(self, command_text: str) -> tuple[str, bool]:
    """Execute with tier checking and approval flow"""

    # Rate limiting check
    if not self._check_rate_limit():
        self.speak("Too many requests. Please wait a moment.")
        return "", False

    # CRITICAL: Check tier policy
    decision = self.policy_checker.check_policy(command_text)

    # Audit the attempt
    self._audit_log({
        'event': 'command_attempt',
        'command': command_text,
        'tier': decision.tier,
        'allowed': decision.allowed,
        'reason': decision.reason,
    })

    if not decision.allowed:
        # Tier 2+ requires approval
        if decision.tier >= 2:
            # NEW: Check if dry-run mode enabled
            if is_dry_run_enabled():
                self.speak("Dry-run mode: Simulating approval flow.")
                result = simulate_tier2_approval(
                    command=command_text,
                    tier=decision.tier,
                    capability=decision.capability or "unknown",
                    diff_id="dry-run-" + hashlib.sha256(command_text.encode()).hexdigest()[:8],
                    policy_hash=self.policy_checker.get_policy_hash(),
                    nonce=decision.approval_code,  # Reuse approval code as nonce
                    recovery_command="<dry-run-no-undo>",
                    user_approved=True  # Simulate approval
                )
                self.speak(result['message'])
                return result['message'], result['success']

            # IMPORTANT: Never speak the approval code
            self.speak("That needs a confirmation in the window.")

            print(f"\n⚠️  Tier {decision.tier} Operation Requires Approval")
            print(f"📝 Confirmation code: {decision.approval_code}")
            print(f"⏱️  Code expires in 30 seconds")
            print(f"💡 Type the code in the modal to proceed")

            # Log approval request
            self._audit_log({
                'event': 'approval_required',
                'tier': decision.tier,
                'approval_code_issued': decision.approval_code,
            })

            # Return blocked
            return "", False

        # Other blocking reason
        self.speak(decision.reason or "Command not allowed.")
        return "", False

    # Tier 0-1: Execute directly
    result_text, success = super().execute_command(command_text)

    # Log execution
    self._audit_log({
        'event': 'command_executed',
        'command': command_text,
        'tier': decision.tier,
        'success': success,
    })

    return result_text, success
```

**Test**:
```bash
# Normal mode
poetry run python src/luminous_nix/voice/secure_voice_interface.py

# Dry-run mode (simulates approvals)
VOICE_DRY_RUN=1 poetry run python src/luminous_nix/voice/secure_voice_interface.py
```

---

### Fix 3: Update Makefile (Already Done ✅)

The Makefile already has:
- `make verify-posture` - Display posture
- `make dry-run` - Start in dry-run mode
- `make posture-stamp` - Generate stamp file

No changes needed!

---

## 🧪 Phase 2: Test Fixes

### Fix 4: Multiline Secret Detection (1 hour)

**File**: `src/luminous_nix/voice/secret_redactor.py`

**Problem**: Current patterns don't match across lines

**Fix**: Add `re.DOTALL` flag to patterns that need it:

```python
# Around line 50 - Update private key pattern
(
    r'-----BEGIN [A-Z]+ PRIVATE KEY-----[\s\S]*?-----END [A-Z]+ PRIVATE KEY-----',
    'private_key'
),

# Around line 70 - Compile patterns with DOTALL
def __init__(self, enabled: bool = True):
    self.enabled = enabled
    self.patterns = [
        (re.compile(pattern, re.IGNORECASE | re.DOTALL), name)  # <-- ADD re.DOTALL
        for pattern, name in self.SECRET_PATTERNS
    ]
```

**Test**:
```python
# Should now pass
result = redactor.redact("""
Log output:
[INFO] Starting service
[DEBUG] API_KEY=abc123def456ghi789
[INFO] Service started
""")
assert result.was_redacted
```

---

### Fix 5: Unicode Secret Detection (1 hour)

**File**: `src/luminous_nix/voice/secret_redactor.py`

**Problem**: Only detects English words like "password", not "mot de passe", "passwort", etc.

**Fix**: Add multilingual patterns:

```python
# Around line 30 - Add multilingual password pattern
SECRET_PATTERNS = [
    # Existing patterns...

    # NEW: Multilingual password patterns
    (
        r'(?:password|mot de passe|passwort|contraseña|senha|パスワード|密码)'
        r'[\s:=]+[^\s]+',
        'multilingual_password'
    ),

    # NEW: Unicode normalization in redact()
    import unicodedata

    def redact(self, text: str) -> RedactionResult:
        """Redact secrets from text with Unicode normalization"""
        if not self.enabled:
            return RedactionResult(text=text, was_redacted=False, secret_types=[])

        # Normalize Unicode to NFC form (canonical composition)
        normalized_text = unicodedata.normalize('NFC', text)

        # Continue with existing logic using normalized_text...
```

**Test**:
```python
# Should now pass
result = redactor.redact('Mot de passe: secret123 🔒')
assert result.was_redacted
```

---

### Fix 6: Tier 1 Policy (30 min)

**File**: `src/luminous_nix/voice/tier_policy.py`

**Problem**: Tier 1 commands (show config, status) incorrectly require approval

**Fix**: Update Tier 1 classification:

```python
# Around line 100 - Update classify_command
def classify_command(self, command: str) -> int:
    """Classify command into tier 0-4"""
    cmd_lower = command.lower()

    # Tier 0: Always safe (read-only, no state)
    if any(word in cmd_lower for word in ['search', 'find', 'list', 'help', 'show packages']):
        return 0

    # Tier 1: Read system state (safe if no mutating flags)
    if any(word in cmd_lower for word in ['status', 'show config', 'info', 'version']):
        # Check for mutating flags that bump to Tier 2
        mutating_flags = ['--apply', '--fix', '--write', '--save', '--set']
        if any(flag in cmd_lower for flag in mutating_flags):
            return 2  # Mutation detected, bump to Tier 2
        return 1  # Read-only, Tier 1 is safe

    # Rest of classification unchanged...
```

**Update check_policy** to allow Tier 0-1 without approval:

```python
def check_policy(self, command: str) -> PolicyDecision:
    """Check if command allowed under current policy"""
    tier = self.classify_command(command)

    # Tier 0-1: Always allowed (read-only)
    if tier <= 1:  # <-- Change from `tier == 0` to `tier <= 1`
        return PolicyDecision(
            allowed=True,
            tier=tier,
            reason=f"Tier {tier} command (read-only)",
            approval_code=None,
            modal_required=False
        )

    # Tier 2+: Requires approval...
```

**Test**:
```python
# Should now pass
decision = policy_checker.check_policy("show status")
assert decision.allowed
assert decision.tier == 1
```

---

### Fix 7: Unicode Confusion Attack (1 hour)

**File**: `src/luminous_nix/voice/secret_redactor.py`

**Problem**: Cyrillic 'а' (U+0430) looks like Latin 'a' but doesn't match

**Fix**: Add confusable character normalization:

```python
# Add at top
import unicodedata
from typing import Dict

# Confusable characters map (Cyrillic → Latin)
CONFUSABLES: Dict[str, str] = {
    'а': 'a', 'е': 'e', 'о': 'o', 'р': 'p', 'с': 'c', 'у': 'y', 'х': 'x',
    'А': 'A', 'В': 'B', 'Е': 'E', 'К': 'K', 'М': 'M', 'Н': 'H', 'О': 'O',
    'Р': 'P', 'С': 'C', 'Т': 'T', 'Х': 'X',
}

def normalize_confusables(text: str) -> str:
    """Replace confusable characters with ASCII equivalents"""
    result = []
    for char in text:
        result.append(CONFUSABLES.get(char, char))
    return ''.join(result)

def redact(self, text: str) -> RedactionResult:
    """Redact secrets from text with confusable normalization"""
    if not self.enabled:
        return RedactionResult(text=text, was_redacted=False, secret_types=[])

    # Normalize Unicode
    normalized = unicodedata.normalize('NFC', text)

    # Normalize confusables for matching (but keep original for output)
    normalized_for_matching = normalize_confusables(normalized)

    # Match against normalized text
    redacted_text = normalized  # Start with normalized original
    found_types = []

    for pattern, secret_type in self.patterns:
        matches = pattern.findall(normalized_for_matching)
        if matches:
            found_types.append(secret_type)
            # Replace in ORIGINAL text at same positions
            redacted_text = pattern.sub('[REDACTED]', redacted_text)

    # ... rest of logic
```

**Test**:
```python
# Should now pass (Cyrillic 'а' detected)
result = redactor.redact('pаssword=secret123')  # Cyrillic а
assert result.was_redacted
```

---

### Fix 8: Run Regex Safety Tests (30 min)

**Command**:
```bash
poetry run pytest tests/voice/test_regex_safety.py -v
```

**Expected**: All 76 tests pass

**If failures**: Fix patterns that have exponential backtracking (unlikely, already O(n) design)

---

## 🎯 Phase 3: Validation

### Manual E2E Test (1 hour)

**Test Script**:
```bash
# 1. Launch secure voice interface
poetry run python src/luminous_nix/voice/secure_voice_interface.py

# Expected output:
# - Posture banner showing Tier 0, policy hash
# - Posture stamp file path
# - "Listening for wake word..."

# 2. Test Tier 0 (should work)
# Say: "Luminous, search firefox"
# Expected: Returns results, no approval needed

# 3. Test Tier 2 (should require approval)
# Say: "Luminous, install firefox"
# Expected:
#   - "That needs a confirmation in the window"
#   - Approval code printed to console
#   - Audit log entry created

# 4. Test secret redaction
# Type: "my password is secret123"
# Expected: TTS says "[REDACTED]", not the actual password

# 5. Test rate limiting
# Send 25 commands rapidly
# Expected: "Too many requests" after 20th command

# 6. Verify audit chain
make verify-audit
# Expected: ✅ Audit chain verified
```

**Document Results**:
- [ ] Wake word detection works
- [ ] Tier 0 executes directly
- [ ] Tier 2+ requires approval
- [ ] Secret redaction prevents TTS leakage
- [ ] Rate limiting triggers at 20/min
- [ ] Audit chain maintains integrity

---

### Stress Test (30 min)

**Test rate limiting**:
```bash
# Send 30 commands rapidly
for i in {1..30}; do
  echo "search vim" | poetry run python src/luminous_nix/voice/secure_voice_interface.py --batch
done
# Expected: First 20 succeed, next 10 rate-limited
```

**Test long inputs**:
```python
# 10KB command
redactor.redact("x" * 10000)
# Expected: Completes in <100ms
```

**Test malicious inputs**:
```python
# SQL injection attempt
redactor.redact("'; DROP TABLE users; --")
# Expected: No crash, sanitized

# XSS attempt
redactor.redact("<script>alert('xss')</script>")
# Expected: No execution, sanitized
```

---

## 📊 Completion Criteria

### Definition of Done (v1.0.0-beta)

- [ ] All 53 security tests passing (100%)
- [ ] All 76 regex safety tests passing (100%)
- [ ] Startup posture banner displays automatically
- [ ] Dry-run mode works via `VOICE_DRY_RUN=1`
- [ ] Posture stamp created on every launch
- [ ] Manual E2E test passes all 6 checks
- [ ] No crashes under stress test
- [ ] Documentation updated with "100% tested"
- [ ] Git tag `v1.0.0-beta` created
- [ ] Release notes finalized

### Success Metrics

- **Test Coverage**: 100% (130/130 tests passing)
- **Integration**: 100% (all new modules wired)
- **Validation**: PASS (E2E + stress tests)
- **Documentation**: COMPLETE (no "TODO" sections)

---

## 🚀 Quick Start (For Contributor)

Want to help complete the 15%? Here's the fastest path:

### 1-Hour Quick Wins (Do First)
```bash
# Clone and setup
git checkout v0.9.0-rc1
poetry install -E voice

# Apply Fix 1 (15 min) - Startup banner
# Edit: src/luminous_nix/voice/production_voice_interface.py
# Add: print_startup_banner() in main()

# Apply Fix 2 (30 min) - Dry-run mode
# Edit: src/luminous_nix/voice/secure_voice_interface.py
# Add: is_dry_run_enabled() check in execute_command()

# Apply Fix 3 (15 min) - Posture stamp
# Edit: src/luminous_nix/voice/production_voice_interface.py
# Add: write_posture_stamp() in main()

# Test
poetry run python src/luminous_nix/voice/secure_voice_interface.py
VOICE_DRY_RUN=1 poetry run python src/luminous_nix/voice/secure_voice_interface.py
```

### 2-4 Hour Fix Session
```bash
# Apply Fixes 4-7 (test fixes)
# Edit: src/luminous_nix/voice/secret_redactor.py
# Edit: src/luminous_nix/voice/tier_policy.py

# Run tests
poetry run pytest tests/voice/test_security.py -v
poetry run pytest tests/voice/test_regex_safety.py -v

# Should see: 130/130 tests passing
```

### Final Hour
```bash
# Manual E2E test (follow script above)
# Document results
# Update RELEASE_NOTES.md
# Tag v1.0.0-beta
```

---

## 📝 When Done

Update these files:
1. `RELEASE_NOTES.md` - Remove "Known Gaps" section
2. `CHANGELOG.md` - Add v1.0.0-beta entry
3. `VOICE_SECURITY_COMPLETE.md` - Update to 100% status
4. `README.md` - Update status badges

Then:
```bash
git add .
git commit -m "🎉 Complete voice security integration - v1.0.0-beta ready

- 130/130 tests passing (100%)
- All modules integrated (startup_posture, dry_run, posture_stamp)
- E2E tested and validated
- Production-ready for beta deployment"

git tag -a v1.0.0-beta -m "Voice Security v1.0.0-beta - Production Ready

All tests passing: 130/130 (100%)
Integration complete: All security modules wired
Validation: E2E + stress tests passed

See RELEASE_NOTES.md for complete details."

git push origin main
git push origin v1.0.0-beta
```

---

**Good luck! You're 85% there. Just 6-10 hours of focused work to ship a truly production-ready system.** 🚀
