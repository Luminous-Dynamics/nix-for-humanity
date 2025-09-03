#!/usr/bin/env python3
"""
Demo: Nix Flake Creation from Natural Language
Shows the powerful flake management capabilities
"""

import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from luminous_nix.core.flake_manager import FlakeManager


def print_separator():
    """Print a visual separator."""
    print("\n" + "=" * 70 + "\n")


def demo_flake_creation():
    """Demonstrate flake creation capabilities."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║         Luminous Nix - Flake Creation Demo                  ║
║    Natural Language → Development Environment Magic         ║
╚══════════════════════════════════════════════════════════════╝
    """)

    manager = FlakeManager()

    # Demo examples
    examples = [
        {
            "title": "🐍 Python Web Development",
            "query": "python web app with django postgresql redis and testing tools",
            "highlights": ["Django framework", "PostgreSQL database", "Redis cache", "Testing setup"]
        },
        {
            "title": "🦀 Rust Systems Programming", 
            "query": "rust cli tool with clap and serde for json processing",
            "highlights": ["Rust toolchain", "Clap for CLI", "Serde for JSON", "Cargo tools"]
        },
        {
            "title": "📦 Node.js Full Stack",
            "query": "nodejs react app with typescript jest and docker",
            "highlights": ["Node.js 18", "TypeScript", "Jest testing", "Docker support"]
        },
        {
            "title": "🐹 Go Microservices",
            "query": "go microservice with gin gorm and kubernetes tools",
            "highlights": ["Go compiler", "Gin framework", "GORM ORM", "Cloud native"]
        },
    ]

    for example in examples:
        print_separator()
        print(f"🎯 {example['title']}")
        print(f"📝 Natural Language: '{example['query']}'")
        print()

        # Parse the intent
        intent = manager.parse_intent(example['query'])
        
        print("🧠 AI Understanding:")
        print(f"  • Language: {intent['language']}")
        print(f"  • Packages: {', '.join(intent['packages']) if intent['packages'] else 'Auto-detected'}")
        print(f"  • Features: {', '.join(intent['features']) if intent['features'] else 'Standard dev tools'}")
        if intent['frameworks']:
            print(f"  • Frameworks: {', '.join(intent['frameworks'])}")
        
        # Generate flake content preview
        print("\n📄 Generated flake.nix (Preview):")
        print("```nix")
        flake_content = manager._generate_flake(intent)
        # Show first 15 lines
        lines = flake_content.split('\n')[:15]
        for line in lines:
            print(line)
        print(f"... ({len(flake_content.split('\n')) - 15} more lines)")
        print("```")
        
        print("\n✨ What You Get:")
        for highlight in example['highlights']:
            print(f"  ✓ {highlight}")

    print_separator()
    print("""
🚀 Real-World Usage:

1. Create a new project:
   $ mkdir my-project && cd my-project
   $ ask-nix flake create "python data science with jupyter pandas"

2. Enter development environment:
   $ nix develop
   
3. All tools instantly available!
   - No manual installation
   - Reproducible everywhere
   - Share with just the flake.nix file

🎉 Convert existing projects:
   $ ask-nix flake convert    # Converts shell.nix → flake.nix

📚 Show templates:
   $ ask-nix flake templates  # See all available templates

🔍 Get language-specific help:
   $ ask-nix flake language python  # Python-specific examples
    """)


def demo_project_detection():
    """Show automatic project type detection."""
    print_separator()
    print("🔍 Automatic Project Detection Demo")
    print()
    
    manager = FlakeManager()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        
        # Simulate different project types
        project_files = {
            "Python": "requirements.txt",
            "Node.js": "package.json",
            "Rust": "Cargo.toml",
            "Go": "go.mod",
        }
        
        for lang, file in project_files.items():
            # Create indicator file
            (project_path / file).touch()
            
            # Detect type
            detected = manager._detect_project_type(project_path)
            print(f"  📁 Found {file} → Detected: {detected.capitalize()} project")
            
            # Clean up
            (project_path / file).unlink()
    
    print("\n💡 Tip: Luminous Nix automatically detects your project type!")


def demo_conversion():
    """Show shell.nix to flake.nix conversion."""
    print_separator()
    print("🔄 Legacy to Modern Conversion")
    print()
    
    print("Before (shell.nix):")
    print("```nix")
    print("""{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = with pkgs; [
    python311
    poetry
    postgresql
  ];
}""")
    print("```")
    
    print("\n↓ ask-nix flake convert ↓\n")
    
    print("After (flake.nix):")
    print("```nix")
    print("""{
  description = "Python development environment";
  
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python311
            poetry
            postgresql
          ];
        };
      });
}""")
    print("```")
    
    print("\n✅ Benefits of flakes:")
    print("  • Locked dependencies (flake.lock)")
    print("  • No channel configuration needed")
    print("  • Shareable with just a Git URL")
    print("  • Built-in CI/CD support")


if __name__ == "__main__":
    try:
        demo_flake_creation()
        demo_project_detection()
        demo_conversion()
        
        print_separator()
        print("""
🌟 Summary: Flake Management Complete!

Luminous Nix makes Nix flakes accessible:
• Natural language → Working environments
• Automatic project detection
• Legacy conversion support
• Rich template library
• No Nix expertise required!

The future of development environments is here,
and it speaks your language! 🚀
        """)
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()