# Welcome to Luminous Nix

<div align="center">

**Transform NixOS from command-line complexity into natural conversation**

[![Version](https://img.shields.io/badge/version-0.3.1-blue.svg)](https://github.com/Luminous-Dynamics/luminous-nix/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-alpha-yellow.svg)](UNIFIED_VISION_AND_REALITY.md)

</div>

## What is Luminous Nix?

Luminous Nix is a natural language interface for NixOS that makes system management as simple as having a conversation. Instead of memorizing complex commands, just tell Nix what you want in plain English.

<div class="grid cards" markdown>

-   :material-rocket-launch-outline: **Quick Start**

    ---

    Get running in 5 minutes with our step-by-step guide

    [:octicons-arrow-right-24: Get started](QUICKSTART.md)

-   :material-chat-processing: **Natural Language**

    ---

    Use plain English instead of complex commands

    [:octicons-arrow-right-24: Learn more](user/basic-usage.md)

-   :material-school: **Educational**

    ---

    Learn NixOS naturally as you use it

    [:octicons-arrow-right-24: How it works](features/working/error-translation.md)

-   :material-speedometer: **Lightning Fast**

    ---

    10x-1500x performance with native Python-Nix API

    [:octicons-arrow-right-24: Performance](features/FEATURE_STATUS.md#performance)

</div>

## Try It Now

=== "Package Management"

    ```bash
    # Install software
    ask-nix "install firefox"
    
    # Search by description
    ask-nix "find video editors"
    
    # Remove packages
    ask-nix "uninstall vim"
    ```

=== "System Management"

    ```bash
    # Update system
    ask-nix "update my system"
    
    # Clean up
    ask-nix "garbage collect"
    
    # Check health
    ask-nix "system status"
    ```

=== "Configuration"

    ```bash
    # Enable services
    ask-nix "enable docker"
    
    # Generate configs
    ask-nix "create nginx config"
    
    # Development setup
    ask-nix "setup python environment"
    ```

## Features at a Glance

| Feature | Status | Description |
|---------|--------|-------------|
| Natural Language Commands | 🟢 Ready | Use plain English for all operations |
| Smart Package Discovery | 🟢 Ready | Find packages by what they do |
| Beautiful TUI | 🟢 Ready | Visual terminal interface |
| Educational Errors | 🟢 Ready | Learn from mistakes |
| Voice Interface | 🟡 Beta | Hands-free operation |
| Learning System | 🟡 Beta | Adapts to your usage |

[View complete feature status →](features/FEATURE_STATUS.md)

## The Trinity Development Model

Luminous Nix is built using a unique collaborative approach that enables solo developers to achieve team-level productivity:

<div class="grid" markdown>

:fontawesome-solid-person: **Human**
: Vision, testing, and real-world validation

:material-cloud: **Cloud AI**
: Architecture, implementation, rapid iteration

:material-chip: **Local LLM**
: NixOS expertise and best practices

</div>

This innovative model proves that consciousness-first technology can be both sacred and practical.

## Get Started

Ready to transform how you use NixOS?

<div class="tx-hero__buttons" markdown>

[Quick Start Guide](QUICKSTART.md){ .md-button .md-button--primary }
[View on GitHub](https://github.com/Luminous-Dynamics/luminous-nix){ .md-button }

</div>

## Join the Community

- :material-github: [GitHub Discussions](https://github.com/Luminous-Dynamics/luminous-nix/discussions)
- :material-bug: [Report Issues](https://github.com/Luminous-Dynamics/luminous-nix/issues)
- :material-book-open-variant: [Documentation](user/README.md)
- :material-account-group: [Contributing](CONTRIBUTING.md)

---

!!! info "Alpha Software"

    Luminous Nix is currently in alpha. While core features work well, expect rough edges and help us improve by reporting issues!

!!! tip "Philosophy"

    Interested in the consciousness-first computing philosophy behind Luminous Nix? Explore our [philosophical foundations](philosophy/CONSCIOUSNESS_FIRST_COMPUTING.md).