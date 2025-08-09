# 🚀 Phase 1 Implementation Plan - Essential System Commands

*Immediate next steps for expanding Nix for Humanity*

## 🎯 Phase 1 Goals
Add the most commonly needed system administration commands that users struggle with in NixOS.

## 📋 Priority Command List

### 1. Network Commands (Week 1)
These are the most requested features based on common NixOS pain points.

#### Must Have:
- `show network` / `network status` - Display current network configuration
- `show ip` / `what's my ip` - Show IP addresses  
- `connect wifi [SSID]` - Configure WiFi connection
- `list wifi` / `scan wifi` - Show available networks
- `internet working?` / `test connection` - Connectivity check

#### Nice to Have:
- `enable/disable wifi` - Toggle wireless
- `configure dns` - DNS settings
- `show ports` - List open ports

### 2. Service Management (Week 1)
Critical for system administration.

#### Must Have:
- `start [service]` - Start a service
- `stop [service]` - Stop a service  
- `restart [service]` - Restart a service
- `service status [name]` - Check service status
- `list services` - Show all services
- `enable [service]` - Enable service at boot
- `disable [service]` - Disable service at boot

#### Nice to Have:
- `show logs [service]` - View service logs
- `failed services` - List failed units

### 3. User Management (Week 2)
Essential for multi-user systems.

#### Must Have:
- `create user [name]` - Add new user
- `list users` - Show system users
- `add [user] to [group]` - Group management
- `change password [user]` - Update password

#### Nice to Have:
- `delete user [name]` - Remove user
- `user info [name]` - Show user details
- `grant sudo [user]` - Add to wheel group

### 4. Storage Commands (Week 2)
Help users understand their disk usage.

#### Must Have:
- `disk usage` / `disk space` - Show storage info
- `what's using space` - Analyze disk usage
- `clean disk` - Suggest cleanup options
- `mount [device]` - Mount USB/drives
- `unmount [device]` - Safely unmount

#### Nice to Have:
- `find large files` - Locate big files
- `check filesystem` - Run fsck
- `list drives` - Show all drives

## 🛠️ Implementation Details

### For Each Command Group:

1. **Intent Patterns**
   ```python
   # Example for network commands
   self.network_status_patterns = [
       r'\b(show|check|what\'s?)\s+(my\s+)?(network|internet|connection)',
       r'\bnetwork\s+status',
       r'\bam\s+I\s+connected',
       r'\binternet\s+working',
   ]
   ```

2. **Executor Methods**
   ```python
   async def _execute_network_status(self) -> Result:
       """Show network configuration and status"""
       # Use nmcli or ip commands
       # Handle both NetworkManager and systemd-networkd
       # Provide user-friendly output
   ```

3. **Knowledge Base Entries**
   ```python
   ('network_status', 'network', 'Show network configuration',
    'nmcli device status && ip addr show',
    'Shows active network interfaces and IP addresses',
    'connect_wifi,test_connection'),
   ```

4. **Help Documentation**
   Update help text to include new categories:
   - 🌐 Network & Connectivity
   - ⚙️ Service Management  
   - 👤 User Management
   - 💾 Storage & Disks

### Safety Considerations

1. **Destructive Operations**
   - Always confirm before: stopping critical services, deleting users, unmounting
   - Provide clear warnings about consequences
   - Suggest safer alternatives when available

2. **Permission Handling**
   - Clearly indicate when sudo is needed
   - Explain why elevated permissions are required
   - Provide non-sudo alternatives where possible

3. **Error Recovery**
   - Provide rollback instructions
   - Suggest troubleshooting steps
   - Link to relevant documentation

### Testing Requirements

For each new command:
1. Unit test for intent recognition (5+ variations)
2. Mock test for executor logic
3. Integration test with real commands (where safe)
4. Error handling test cases
5. Help text visibility test

### User Experience Enhancements

1. **Progressive Disclosure**
   - Simple commands work immediately
   - Advanced options available through conversation
   - Educational explanations on request

2. **Smart Suggestions**
   - After `disk usage`: suggest `garbage collect` if low
   - After `failed services`: offer to show logs
   - After `network status`: offer connectivity test

3. **Context Awareness**
   ```python
   # Remember recent commands
   "restart it" -> restart last mentioned service
   "check its status" -> status of last service
   "connect to it" -> connect to last mentioned network
   ```

## 📅 Timeline

### Week 1: Network & Services
- Day 1-2: Implement network status commands
- Day 3-4: Add WiFi management
- Day 4-5: Implement service management
- Day 5: Testing and refinement

### Week 2: Users & Storage  
- Day 1-2: User management commands
- Day 3-4: Storage and disk commands
- Day 4-5: Integration testing
- Day 5: Documentation update

### Week 3: Polish & Release
- Day 1-2: Error handling improvements
- Day 3: Performance optimization
- Day 4: User documentation
- Day 5: Release preparation

## 🎯 Success Criteria

1. **Functionality**
   - All 20+ core commands working
   - 90%+ intent recognition accuracy
   - Proper error handling for all commands

2. **Safety**
   - No data loss from commands
   - Clear warnings for dangerous operations
   - Confirmation for destructive actions

3. **Usability**
   - Commands feel natural to say
   - Help text is comprehensive
   - Error messages are helpful

4. **Performance**
   - Commands execute within 2 seconds
   - No UI freezing during operations
   - Smooth progress indication

## 🚀 Getting Started

1. Create feature branch: `feat/phase-1-system-commands`
2. Add IntentType enums for new categories
3. Implement network commands first (highest priority)
4. Add comprehensive tests for each command
5. Update documentation and help text
6. Submit PR with full test coverage

---

*"Making system administration as natural as conversation - one command at a time."*