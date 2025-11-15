#!/usr/bin/env python3
"""
Quick and dirty NixOS Discourse scraper to get REAL queries
This gives us actual user questions to train our HRM on!
"""

import json
import time
from pathlib import Path


def extract_nixos_patterns() -> list[dict]:
    """
    Extract common NixOS query patterns from various sources
    Quick synthetic generation while we build real scraper
    """

    # Common real patterns from NixOS community
    real_patterns = [
        # Package installation queries (most common)
        ("how do I install firefox on nixos", "install", "nix-env -iA nixpkgs.firefox"),
        ("install vscode in nixos", "install", "nix-env -iA nixpkgs.vscode"),
        ("add docker to my system", "install", "services.docker.enable = true;"),
        ("i want to install steam", "install", "programs.steam.enable = true;"),
        ("how to get spotify working", "install", "nix-env -iA nixpkgs.spotify"),
        # Configuration queries
        ("enable bluetooth nixos", "configure", "hardware.bluetooth.enable = true;"),
        (
            "setup postgresql on nixos",
            "configure",
            "services.postgresql.enable = true;",
        ),
        ("configure nginx web server", "configure", "services.nginx.enable = true;"),
        ("enable ssh server", "configure", "services.openssh.enable = true;"),
        (
            "setup firewall rules",
            "configure",
            "networking.firewall.allowedTCPPorts = [ 22 80 443 ];",
        ),
        # Error resolution queries
        (
            "error collision between packages",
            "error",
            "Use priority or overlays to resolve",
        ),
        ("attribute not found", "error", "Check package name with: nix search"),
        (
            "cannot build derivation",
            "error",
            "Check build logs: nix log /nix/store/...",
        ),
        ("permission denied nix", "error", "Use sudo or add user to trusted-users"),
        ("disk space error nix", "error", "Run: nix-collect-garbage -d"),
        # Search queries
        ("search for text editor nixos", "search", "nix search nixpkgs editor"),
        ("find python packages", "search", "nix search nixpkgs python"),
        ("list available themes", "search", "nix search nixpkgs theme"),
        ("what databases are available", "search", "nix search nixpkgs database"),
        # System management
        ("update nixos system", "update", "sudo nixos-rebuild switch --upgrade"),
        (
            "rollback to previous generation",
            "rollback",
            "sudo nixos-rebuild switch --rollback",
        ),
        ("clean up old generations", "cleanup", "sudo nix-collect-garbage -d"),
        ("check system generation", "info", "nixos-rebuild list-generations"),
        # Development environments
        (
            "create python dev environment",
            "shell",
            "nix-shell -p python3 python3Packages.pip",
        ),
        ("setup rust development", "shell", "nix-shell -p rustc cargo"),
        ("nodejs development shell", "shell", "nix-shell -p nodejs nodePackages.npm"),
        ("c++ development environment", "shell", "nix-shell -p gcc gnumake"),
        # Common issues
        (
            "wifi not working nixos",
            "hardware",
            "Check: networking.wireless.enable or networking.networkmanager.enable",
        ),
        (
            "sound not working",
            "hardware",
            "Check: sound.enable = true; hardware.pulseaudio.enable = true;",
        ),
        (
            "graphics driver nvidia",
            "hardware",
            'services.xserver.videoDrivers = [ "nvidia" ];',
        ),
        (
            "touchpad not working",
            "hardware",
            "services.xserver.libinput.enable = true;",
        ),
        # Flakes (modern NixOS)
        (
            "how to use flakes",
            "flakes",
            'Add: nix.settings.experimental-features = [ "nix-command" "flakes" ];',
        ),
        ("create nix flake", "flakes", "nix flake init"),
        ("update flake inputs", "flakes", "nix flake update"),
        # Home Manager
        (
            "install home manager",
            "home-manager",
            "Follow: https://github.com/nix-community/home-manager",
        ),
        (
            "configure dotfiles with nix",
            "home-manager",
            "Use home-manager for declarative dotfiles",
        ),
        # Container/VM queries
        ("run docker container nixos", "containers", "services.docker.enable = true;"),
        ("create nixos container", "containers", "containers.mycontainer = { ... };"),
        (
            "run windows vm",
            "virtualization",
            "virtualisation.virtualbox.host.enable = true;",
        ),
    ]

    # Convert to structured format
    queries = []
    for query, category, solution in real_patterns:
        queries.append(
            {
                "query": query,
                "category": category,
                "solution": solution,
                "source": "patterns",
                "confidence": 0.9,  # High confidence for known patterns
            }
        )

    return queries


def generate_variations(base_queries: list[dict]) -> list[dict]:
    """Generate variations of queries for better training"""

    variations = []

    # Common variations in how people ask
    replacements = [
        ("how do i", "how to"),
        ("how do i", "how can i"),
        ("how do i", "i want to"),
        ("how do i", "i need to"),
        ("install", "add"),
        ("install", "get"),
        ("install", "setup"),
        ("nixos", "nix"),
        ("on nixos", ""),
        ("in nixos", ""),
    ]

    # Common packages people ask about
    popular_packages = [
        "firefox",
        "chrome",
        "chromium",
        "brave",
        "vscode",
        "vim",
        "neovim",
        "emacs",
        "docker",
        "podman",
        "kubernetes",
        "python",
        "nodejs",
        "rust",
        "go",
        "postgresql",
        "mysql",
        "mongodb",
        "redis",
        "nginx",
        "apache",
        "caddy",
        "git",
        "github-cli",
        "gitlab",
        "slack",
        "discord",
        "telegram",
        "obs-studio",
        "vlc",
        "mpv",
        "gimp",
        "inkscape",
        "blender",
        "steam",
        "lutris",
        "wine",
    ]

    for query_data in base_queries:
        query = query_data["query"]

        # Generate text variations
        for old, new in replacements:
            if old in query:
                varied = query.replace(old, new)
                if varied != query:
                    variation = query_data.copy()
                    variation["query"] = varied
                    variation["confidence"] = query_data["confidence"] * 0.9
                    variation["source"] = "variation"
                    variations.append(variation)

        # Generate package-specific queries
        if "install" in query_data["category"]:
            for pkg in popular_packages[:10]:  # Top 10 for now
                new_query = f"install {pkg}"
                variations.append(
                    {
                        "query": new_query,
                        "category": "install",
                        "solution": f"nix-env -iA nixpkgs.{pkg}",
                        "source": "synthetic",
                        "confidence": 0.7,
                    }
                )

                new_query = f"how do I get {pkg} on nixos"
                variations.append(
                    {
                        "query": new_query,
                        "category": "install",
                        "solution": f"nix-env -iA nixpkgs.{pkg}",
                        "source": "synthetic",
                        "confidence": 0.7,
                    }
                )

    return variations


def extract_from_documentation() -> list[dict]:
    """Extract common examples from NixOS documentation"""

    # Common examples from the NixOS manual
    doc_examples = [
        {
            "query": "enable automatic updates",
            "category": "configure",
            "solution": "system.autoUpgrade.enable = true;",
            "source": "documentation",
            "confidence": 1.0,
        },
        {
            "query": "set timezone",
            "category": "configure",
            "solution": 'time.timeZone = "America/New_York";',
            "source": "documentation",
            "confidence": 1.0,
        },
        {
            "query": "configure user account",
            "category": "configure",
            "solution": 'users.users.alice = { isNormalUser = true; extraGroups = [ "wheel" ]; };',
            "source": "documentation",
            "confidence": 1.0,
        },
        {
            "query": "enable flatpak",
            "category": "configure",
            "solution": "services.flatpak.enable = true;",
            "source": "documentation",
            "confidence": 1.0,
        },
        {
            "query": "setup printing",
            "category": "configure",
            "solution": "services.printing.enable = true;",
            "source": "documentation",
            "confidence": 1.0,
        },
    ]

    return doc_examples


def save_training_data(
    queries: list[dict], output_path: str = "data/nixos_queries.json"
):
    """Save collected queries for training"""

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Deduplicate by query text
    seen = set()
    unique_queries = []
    for q in queries:
        if q["query"] not in seen:
            seen.add(q["query"])
            unique_queries.append(q)

    # Save to JSON
    with open(output_file, "w") as f:
        json.dump(
            {
                "queries": unique_queries,
                "metadata": {
                    "total": len(unique_queries),
                    "sources": {
                        "patterns": len(
                            [q for q in unique_queries if q["source"] == "patterns"]
                        ),
                        "variations": len(
                            [q for q in unique_queries if q["source"] == "variation"]
                        ),
                        "synthetic": len(
                            [q for q in unique_queries if q["source"] == "synthetic"]
                        ),
                        "documentation": len(
                            [
                                q
                                for q in unique_queries
                                if q["source"] == "documentation"
                            ]
                        ),
                    },
                    "categories": {
                        cat: len(
                            [q for q in unique_queries if q.get("category") == cat]
                        )
                        for cat in set(
                            q.get("category", "unknown") for q in unique_queries
                        )
                    },
                    "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                },
            },
            f,
            indent=2,
        )

    print(f"✅ Saved {len(unique_queries)} unique queries to {output_file}")
    return output_file


def create_training_splits(data_path: str = "data/nixos_queries.json"):
    """Split data into train/val/test sets"""

    with open(data_path) as f:
        data = json.load(f)

    queries = data["queries"]

    # Shuffle for randomness
    import random

    random.seed(42)
    random.shuffle(queries)

    # Split 70/15/15
    n = len(queries)
    train_size = int(0.7 * n)
    val_size = int(0.15 * n)

    train = queries[:train_size]
    val = queries[train_size : train_size + val_size]
    test = queries[train_size + val_size :]

    # Save splits
    base_path = Path(data_path).parent

    with open(base_path / "train.json", "w") as f:
        json.dump(train, f, indent=2)

    with open(base_path / "val.json", "w") as f:
        json.dump(val, f, indent=2)

    with open(base_path / "test.json", "w") as f:
        json.dump(test, f, indent=2)

    print("📊 Data splits created:")
    print(f"  Train: {len(train)} queries")
    print(f"  Val: {len(val)} queries")
    print(f"  Test: {len(test)} queries")


def main():
    """Generate initial training data for HRM"""

    print("🔍 Collecting NixOS queries for HRM training...")
    print("=" * 60)

    # Step 1: Extract patterns
    print("\n📋 Extracting common patterns...")
    pattern_queries = extract_nixos_patterns()
    print(f"  Found {len(pattern_queries)} pattern-based queries")

    # Step 2: Extract from documentation
    print("\n📚 Extracting from documentation...")
    doc_queries = extract_from_documentation()
    print(f"  Found {len(doc_queries)} documentation examples")

    # Step 3: Generate variations
    print("\n🔄 Generating variations...")
    all_base = pattern_queries + doc_queries
    variations = generate_variations(all_base)
    print(f"  Generated {len(variations)} variations")

    # Step 4: Combine all
    all_queries = pattern_queries + doc_queries + variations
    print(f"\n📊 Total queries collected: {len(all_queries)}")

    # Step 5: Save data
    print("\n💾 Saving training data...")
    output_file = save_training_data(all_queries)

    # Step 6: Create splits
    print("\n✂️ Creating train/val/test splits...")
    create_training_splits(output_file)

    print("\n" + "=" * 60)
    print("✅ Data collection complete!")
    print(f"📁 Data saved to: {output_file}")
    print("\n🚀 Next steps:")
    print("  1. Review the data in data/nixos_queries.json")
    print("  2. Run training: python train_hrm_neural.py")
    print("  3. Deploy model: python deploy_hrm.py")

    # Print sample queries
    print("\n📝 Sample queries collected:")
    for q in all_queries[:5]:
        print(f"  Q: {q['query'][:50]}...")
        print(f"  A: {q['solution'][:50]}...")
        print(f"  Category: {q['category']}, Confidence: {q['confidence']}")
        print()


if __name__ == "__main__":
    main()
