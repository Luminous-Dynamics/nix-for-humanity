# NLP Intent Patterns - Core Library

## Text-First Pattern Recognition

All patterns are designed for text input first, with voice variations considered as optional enhancements.

### Package Management Intents

#### Install Package
```yaml
Patterns:
  - "install {package}"
  - "i need {package}"
  - "get me {package}"
  - "add {package}"
  - "setup {package}"
  - "i want to use {package}"
  - "put {package} on my computer"
  - "download {package}"
  
Variations:
  - "install that {category} program" → clarify
  - "get me something to {action}" → suggest options
  - "install the thing for {purpose}" → intelligent guess

Entities:
  - package: string (validate against nixpkgs)
  - category: enum [browser, editor, game, development, media]
  - action: verb phrase
  - purpose: noun phrase
```

#### Remove Package
```yaml
Patterns:
  - "remove {package}"
  - "uninstall {package}"
  - "delete {package}"
  - "get rid of {package}"
  - "i don't need {package} anymore"
  - "take off {package}"
  
Edge Cases:
  - "remove everything" → safety check
  - "clean up" → suggest old generations
  - "free space" → removal suggestions
```

#### Update System
```yaml
Patterns:
  - "update"
  - "update system"
  - "update everything"
  - "upgrade"
  - "get latest"
  - "check for updates"
  - "make everything current"
  - "refresh system"
```

### System Configuration Intents

#### Network Management
```yaml
WiFi Patterns:
  - "connect to wifi"
  - "wifi not working"
  - "no internet"
  - "can't get online"
  - "network is broken"
  - "connect to {ssid}"
  
Network Config:
  - "use dns {server}"
  - "change network settings"
  - "set static ip"
  - "enable ethernet"
```

#### Service Management
```yaml
Start Service:
  - "start {service}"
  - "turn on {service}"
  - "enable {service}"
  - "run {service}"
  - "launch {service}"
  
Stop Service:
  - "stop {service}"
  - "turn off {service}"
  - "disable {service}"
  - "kill {service}"
  
Service Queries:
  - "what's running"
  - "show services"
  - "is {service} on"
```

### Troubleshooting Intents

#### Generic Problems
```yaml
Patterns:
  - "something is wrong"
  - "it's not working"
  - "help"
  - "fix this"
  - "nothing works"
  - "computer is broken"
  
Response: Diagnostic questions
```

#### Specific Issues
```yaml
Audio:
  - "no sound"
  - "can't hear anything"
  - "audio not working"
  - "speakers broken"
  - "microphone not working"
  
Display:
  - "screen too bright/dark"
  - "can't see anything"
  - "display broken"
  - "wrong resolution"
  - "external monitor not working"
  
Performance:
  - "computer is slow"
  - "everything is laggy"
  - "takes forever"
  - "freezing up"
  - "using too much memory"
```

### User Management Intents

#### Account Operations
```yaml
Create User:
  - "add user {name}"
  - "create account for {name}"
  - "new user {name}"
  - "let {name} use computer"
  
Modify User:
  - "make {name} admin"
  - "give {name} sudo"
  - "change {name} password"
  - "remove {name} access"
```

### Development Environment Intents

#### Language Setup
```yaml
Python:
  - "setup python"
  - "i want to code in python"
  - "need python development"
  - "install python stuff"
  → Install: python3, pip, virtualenv, common tools

JavaScript:
  - "setup javascript"
  - "need node"
  - "web development"
  → Install: nodejs, npm/yarn, common tools

Rust:
  - "setup rust"
  - "rust development"
  → Install: rustc, cargo, rust-analyzer
```

### Query Intents

#### System Information
```yaml
Patterns:
  - "show system info"
  - "what version"
  - "disk space"
  - "memory usage"
  - "cpu usage"
  - "what's installed"
  - "list packages"
```

#### Configuration Queries
```yaml
Patterns:
  - "show configuration"
  - "what changed"
  - "current settings"
  - "show my setup"
```

### Recovery Intents

#### Rollback Operations
```yaml
Patterns:
  - "undo last change"
  - "go back"
  - "revert"
  - "previous version"
  - "it was working yesterday"
  - "undo everything from today"
```

## Context-Aware Patterns

### Pronouns and References
```yaml
After Search:
  - "install it" → install last searched
  - "the first one" → first option
  - "that one" → last mentioned
  
After Error:
  - "try again" → retry last command
  - "fix it" → run diagnostic
  - "why" → explain error
```

### Multi-Turn Conversations
```yaml
Installation Flow:
  User: "I need to edit photos"
  Nix: "I found GIMP, Krita, and Inkscape. Which would you like?"
  User: "the first one"
  Nix: "Installing GIMP..."
  
Troubleshooting Flow:
  User: "Internet not working"
  Nix: "Let me check... NetworkManager is running. Can you see WiFi networks?"
  User: "no"
  Nix: "Checking WiFi hardware..."
```

## Ambiguity Resolution

### Clarification Patterns
```yaml
Multiple Matches:
  User: "install code"
  Nix: "Do you mean VS Code (code editor) or something else?"
  
Category Query:
  User: "install browser"
  Nix: "Popular browsers: Firefox, Chromium, Brave. Which would you prefer?"
  
Purpose Query:
  User: "something for music"
  Nix: "Do you want to play music (VLC, Rhythmbox) or create music (Ardour, LMMS)?"
```

## Error Recovery Patterns

### Common Confusion
```yaml
Package Not Found:
  User: "install photoshop"
  Nix: "Photoshop isn't available, but GIMP is a great alternative. Should I install it?"
  
Permission Denied:
  User: "install firefox"
  Nix: "I need administrator permission. Can you enter your password?"
  
Already Installed:
  User: "install firefox"
  Nix: "Firefox is already installed! Would you like to update it instead?"
```

## Personality and Tone

### Friendly Responses
```yaml
Success:
  - "All done! {package} is ready to use."
  - "Great! I've installed {package} for you."
  - "{package} is installed and waiting for you."
  
Working:
  - "On it! Installing {package}..."
  - "Let me get that for you..."
  - "Setting up {package} now..."
  
Errors:
  - "Hmm, I ran into a problem. Let me explain..."
  - "Something went wrong, but we can fix it..."
  - "I couldn't do that because..."
```

---

*These patterns form the foundation. The system learns new patterns from user interactions.*