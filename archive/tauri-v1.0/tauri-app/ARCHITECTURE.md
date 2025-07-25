# 🏗️ Nix for Humanity - Tauri Architecture

## Overview

This is the REAL implementation of Nix for Humanity using Tauri for secure, native desktop integration.

## Tech Stack

### Frontend (UI Layer)
- **Framework**: Vanilla TypeScript (can add Svelte later)
- **Styling**: Modern CSS with variables
- **Voice**: Web Speech API → Whisper.cpp (future)
- **State**: Simple event-driven architecture

### Backend (Rust Layer)
- **Framework**: Tauri 2.0
- **Security**: Command sandboxing
- **Database**: SQLite for learning system
- **NixOS**: Direct system integration

### Scalable Module Architecture

```
nix-for-humanity/
├── src/                      # Frontend (TypeScript)
│   ├── nlp/                  # Natural Language Processing
│   │   ├── intent.ts         # Intent recognition
│   │   ├── entities.ts       # Entity extraction
│   │   ├── context.ts        # Context management
│   │   └── patterns/         # Language patterns
│   ├── ui/                   # User Interface
│   │   ├── components/       # Reusable components
│   │   ├── voice.ts          # Voice integration
│   │   └── feedback.ts       # Visual feedback
│   ├── learning/             # Learning System
│   │   ├── patterns.ts       # User patterns
│   │   ├── preferences.ts    # Preference tracking
│   │   └── adaptation.ts     # Behavior adaptation
│   └── main.ts               # Entry point
│
├── src-tauri/                # Backend (Rust)
│   ├── src/
│   │   ├── commands/         # Tauri commands
│   │   │   ├── nix.rs        # NixOS operations
│   │   │   ├── system.rs     # System info
│   │   │   └── learning.rs   # Learning system
│   │   ├── security/         # Security layer
│   │   │   ├── sandbox.rs    # Command sandboxing
│   │   │   ├── validator.rs  # Input validation
│   │   │   └── permissions.rs # Permission system
│   │   ├── database/         # Data layer
│   │   │   ├── schema.rs     # SQLite schema
│   │   │   ├── learning.rs   # Learning storage
│   │   │   └── history.rs    # Command history
│   │   └── main.rs           # Rust entry point
│   └── Cargo.toml
│
├── shared/                   # Shared types
│   └── types.ts              # TypeScript/Rust shared types
│
└── plugins/                  # Plugin system (future)
    └── README.md
```

## Key Design Principles

### 1. Security First
- All NixOS commands run in Rust sandbox
- No direct shell execution from JavaScript
- Whitelist-only command approach
- User must approve dangerous operations

### 2. Modular & Scalable
- Each NLP intent is a separate module
- Plugins can add new capabilities
- Database migrations for evolution
- Clean separation of concerns

### 3. Performance
- Rust backend for speed
- Lazy loading of NLP models
- Efficient IPC communication
- Local-first architecture

### 4. Privacy
- All data stays local
- No network calls required
- User owns their data
- Easy export/deletion

## Development Workflow

### Frontend (TypeScript)
```bash
npm run dev        # Hot reload development
npm run build      # Production build
npm test           # Run tests
```

### Backend (Rust)
```bash
cargo check        # Fast type checking
cargo test         # Run tests
cargo build        # Development build
cargo build --release # Production build
```

### Full App
```bash
npm run tauri:dev  # Run full app in development
npm run tauri:build # Build installable app
```

## IPC Communication

### TypeScript → Rust
```typescript
// Frontend
import { invoke } from '@tauri-apps/api/core';

const result = await invoke('process_nlp_command', {
  input: "install firefox",
  context: currentContext
});
```

### Rust → TypeScript
```rust
// Backend
#[tauri::command]
async fn process_nlp_command(
    input: String,
    context: Context
) -> Result<CommandResult, Error> {
    // Secure processing here
}
```

## Installation for Testing

### Development (Your NixOS System)
```bash
# Install Tauri prerequisites
nix-shell -p pkg-config openssl gtk3 webkitgtk libsoup

# Run in development
npm install
npm run tauri:dev
```

### Production
```nix
# flake.nix
{
  inputs.nix-for-humanity.url = "github:luminous-dynamics/nix-for-humanity";
  
  # In your system config
  environment.systemPackages = [
    inputs.nix-for-humanity.packages.${system}.default
  ];
}
```

## Next Implementation Steps

1. **Core IPC Bridge** - TypeScript ↔ Rust communication
2. **Secure Executor** - Sandbox for NixOS commands
3. **Intent System** - Modular intent recognition
4. **Learning Database** - SQLite schema
5. **Basic UI** - Minimal working interface

This architecture will scale from 10 commands to 1000+ while maintaining security and performance.