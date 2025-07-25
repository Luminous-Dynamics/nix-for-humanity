# Tauri IPC Architecture

## Overview

Nix for Humanity uses Tauri's IPC (Inter-Process Communication) bridge to safely execute NixOS commands from the frontend.

## Architecture Flow

```
┌─────────────────────────────────────────┐
│           Frontend (WebView)             │
│                                         │
│  User Input → NLP Engine → Command     │
│       ↓                        ↓        │
│  "install firefox"    { command: "nix", │
│                        args: ["-iA"...] }│
└────────────────┬───────────────────────┘
                 │ IPC Bridge
                 ↓ invoke()
┌─────────────────────────────────────────┐
│           Backend (Rust)                 │
│                                         │
│  Command Validation → Sandboxing →     │
│  Execution → Result                     │
│                                         │
│  Whitelisted commands only              │
│  Capability-based permissions           │
└─────────────────────────────────────────┘
```

## IPC Commands

### 1. `execute_nix_command`
Execute a validated NixOS command.

**Frontend:**
```typescript
const result = await invoke('execute_nix_command', {
  command: {
    command: 'nix-env',
    args: ['-iA', 'nixpkgs.firefox'],
    dry_run: false
  }
});
```

**Backend:**
```rust
#[tauri::command]
async fn execute_nix_command(command: NixCommand) -> Result<CommandResult, String>
```

### 2. `search_packages`
Search for packages in nixpkgs.

**Frontend:**
```typescript
const packages = await invoke('search_packages', { 
  query: 'firefox' 
});
```

### 3. `get_system_info`
Get NixOS system information.

**Frontend:**
```typescript
const info = await invoke('get_system_info');
// Returns: { os: "NixOS", version: "...", architecture: "x86_64" }
```

## Security Model

### Command Whitelisting
Only these commands can be executed:
- `nix`, `nix-env` - Package management
- `nixos-rebuild` - System updates
- `nix-channel` - Channel management
- `nix-collect-garbage` - Maintenance
- `systemctl`, `journalctl` - Service management
- `nixos-version` - Information queries

### Capability Validation
Each command is validated against:
1. Whitelist check
2. Argument validation
3. Permission requirements
4. Risk assessment

### Sandboxing
Commands execute with:
- Limited filesystem access
- No network access (unless required)
- Timeout enforcement
- Resource limits

## Error Handling

Errors are categorized and translated:

```typescript
// Backend error
Err("Command 'rm' is not allowed")

// Frontend receives
{
  success: false,
  error: "That command isn't supported for safety reasons"
}
```

## Development Testing

Use the demo page to test IPC:
1. Run `npm run tauri:dev`
2. Open developer tools (Ctrl+Shift+I)
3. Test commands in the demo interface
4. Check console for IPC messages

## Adding New Commands

1. Add to whitelist in `src-tauri/src/main.rs`
2. Create handler function with `#[tauri::command]`
3. Add to `tauri::generate_handler![]`
4. Update frontend types
5. Test with demo page

## Performance Considerations

- IPC calls are async - always use await
- Large outputs are automatically chunked
- Long-running commands should stream progress
- Timeouts default to 30s, configurable per command

---

*Remember: The IPC bridge is the security boundary. Never trust frontend input without validation.*