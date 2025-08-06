# 🐍 Python Development on NixOS: A Journey of Understanding

*From "Why doesn't pip work?" to "This is so much better than pip!"*

## The Mental Model: Python in the Land of Immutability

Before we dive into HOW, let's understand WHY. NixOS treats software differently than other systems, and once you grasp this mental model, Python development becomes not just possible, but delightful.

### The Three Pillars of NixOS

1. **Immutability**: The system is read-only by design
2. **Isolation**: Every package lives in its own world
3. **Declarativity**: You describe what you want, not how to get it

Traditional Python development with pip fights against all three pillars. But there's a better way - actually, three increasingly powerful ways!

## Your Journey: Three Levels of Mastery

### 🌉 Level 1: The Pragmatic Bridge
*"I just need to get work done"*

### 🏗️ Level 2: The Declarative Application
*"I want reproducible environments"*

### 🚀 Level 3: The Professional Ecosystem
*"I'm building for production"*

Let's explore each level in depth.

---

## 🌉 Level 1: The Pragmatic Bridge

*For developers who need to maintain compatibility with the pip ecosystem while working on NixOS*

### Understanding the Bridge

At this level, we create a bridge between NixOS's purity and Python's traditional workflow. We use `nix-shell` to provide system dependencies, then create a traditional virtual environment inside.

### The Workflow

```bash
# Step 1: Create a shell.nix that provides Python and system dependencies
cat > shell.nix << 'EOF'
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Python and pip
    python311
    python311Packages.pip
    python311Packages.virtualenv
    
    # System dependencies your Python packages might need
    postgresql  # for psycopg2
    gcc         # for packages that compile C extensions
    stdenv      # standard build environment
  ];
  
  shellHook = ''
    echo "🐍 Python development environment ready!"
    echo "Create a virtual environment with: python -m venv .venv"
    echo "Activate it with: source .venv/bin/activate"
  '';
}
EOF

# Step 2: Enter the Nix shell
nix-shell

# Step 3: Create and use a virtual environment (inside nix-shell)
python -m venv .venv
source .venv/bin/activate

# Step 4: Now pip works normally!
pip install -r requirements.txt
pip install django pandas numpy
```

### Why This Works

- **Nix provides**: Python interpreter, system libraries, build tools
- **Venv provides**: Isolated Python package environment
- **You get**: Familiar pip workflow that actually works

### Best Practices at Level 1

1. **Always work inside nix-shell**: It provides the foundation
2. **Use requirements.txt**: Keep dependencies tracked
3. **Document system deps**: Add them to shell.nix
4. **Version control shell.nix**: Others can reproduce your environment

### Common Patterns

```bash
# For data science projects
pkgs.mkShell {
  buildInputs = with pkgs; [
    python311
    python311Packages.pip
    python311Packages.virtualenv
    
    # Data science system deps
    blas
    lapack
    gfortran
    pkg-config
  ];
}

# For web development
pkgs.mkShell {
  buildInputs = with pkgs; [
    python311
    python311Packages.pip
    python311Packages.virtualenv
    
    # Web dev system deps
    postgresql
    redis
    nodejs  # for frontend assets
  ];
}
```

### Limitations and When to Level Up

This approach is perfect for:
- ✅ Development and experimentation
- ✅ Working with requirements.txt from other projects
- ✅ Quick prototypes

Consider Level 2 when:
- ❌ You need truly reproducible builds
- ❌ You're sharing code with a team
- ❌ You want to eliminate "works on my machine"

---

## 🏗️ Level 2: The Declarative Application

*For developers who want reproducibility and are ready to embrace the Nix way*

### Understanding Declarative Python

At this level, we stop fighting NixOS and start working with it. Instead of imperatively installing packages, we declare our entire Python environment.

### The Workflow

```nix
# python-env.nix - Your entire Python environment as code
{ pkgs ? import <nixpkgs> {} }:

let
  myPython = pkgs.python311.withPackages (ps: with ps; [
    # Web framework
    django
    
    # Data science
    pandas
    numpy
    matplotlib
    jupyter
    
    # Utilities
    requests
    pytest
    black
    
    # Any other packages you need
  ]);
in
pkgs.mkShell {
  buildInputs = [
    myPython
    # Other tools
    pkgs.git
    pkgs.ruff
  ];
  
  shellHook = ''
    echo "🚀 Declarative Python environment loaded!"
    echo "All packages are already available - no pip needed!"
    echo "Run 'python' to start coding"
  '';
}
```

### Using Flakes (The Modern Way)

```nix
# flake.nix - Even more reproducible
{
  description = "My Python project";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        
        pythonEnv = pkgs.python311.withPackages (ps: with ps; [
          fastapi
          uvicorn
          sqlalchemy
          pytest
          # Your packages here
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [ pythonEnv ];
        };
        
        # You can even build a deployable package!
        packages.default = pkgs.writeScriptBin "my-app" ''
          #!${pythonEnv}/bin/python
          ${builtins.readFile ./main.py}
        '';
      });
}
```

### Why This Is Better

1. **Reproducible**: Anyone with this file gets the exact same environment
2. **Fast**: No downloading/installing - packages are cached
3. **Clean**: No package conflicts, ever
4. **Shareable**: Commit one file, entire team has same setup

### Jupyter Notebooks Done Right

```nix
# jupyter-env.nix
{ pkgs ? import <nixpkgs> {} }:

let
  myPython = pkgs.python311.withPackages (ps: with ps; [
    jupyter
    ipykernel
    pandas
    numpy
    matplotlib
    seaborn
    scikit-learn
  ]);
in
pkgs.mkShell {
  buildInputs = [ myPython ];
  
  shellHook = ''
    jupyter lab
  '';
}
```

### Handling Missing Packages

Sometimes a package isn't in nixpkgs yet:

```nix
# Building a custom package
let
  myPackage = ps: ps.buildPythonPackage rec {
    pname = "my-special-package";
    version = "1.0.0";
    
    src = ps.fetchPypi {
      inherit pname version;
      sha256 = "...";  # nix-prefetch-url
    };
    
    propagatedBuildInputs = with ps; [
      requests
      numpy
    ];
  };
  
  pythonWithMyPackage = pkgs.python311.withPackages (ps: [
    (myPackage ps)
    ps.pytest
  ]);
in
# ... use pythonWithMyPackage
```

### When to Level Up

This approach is excellent for:
- ✅ Team projects
- ✅ Reproducible research
- ✅ Deployment preparation

Consider Level 3 when:
- 🚀 You need to track exact versions
- 🚀 You're building for production
- 🚀 You want automated dependency updates

---

## 🚀 Level 3: The Professional Ecosystem

*For teams building production Python applications*

### Understanding Professional Python on NixOS

At this level, we combine the best of both worlds: Python's rich ecosystem tools (Poetry, pip-tools) with Nix's reproducibility guarantees.

### Poetry2nix: The Best of Both Worlds

```nix
# flake.nix using poetry2nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    poetry2nix.url = "github:nix-community/poetry2nix";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, poetry2nix, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        poetry2nixLib = poetry2nix.lib.mkPoetry2Nix { inherit pkgs; };
        
        myApp = poetry2nixLib.mkPoetryApplication {
          projectDir = self;
          # Custom overrides for problematic packages
          overrides = poetry2nixLib.defaultPoetryOverrides.extend
            (self: super: {
              # Example: Fix for packages that need special handling
              pillow = super.pillow.overridePythonAttrs (old: {
                buildInputs = old.buildInputs ++ [ pkgs.libjpeg ];
              });
            });
        };
      in
      {
        packages.default = myApp;
        
        devShells.default = pkgs.mkShell {
          inputsFrom = [ myApp ];
          buildInputs = with pkgs; [
            poetry
            black
            mypy
            ruff
          ];
        };
        
        # Docker image for deployment
        packages.docker = pkgs.dockerTools.buildLayeredImage {
          name = "my-python-app";
          contents = [ myApp ];
          config.Cmd = [ "${myApp}/bin/my-app" ];
        };
      });
}
```

### Mach-nix: When You Need pip Compatibility

```nix
# Using mach-nix for complex requirements
let
  mach-nix = import (builtins.fetchGit {
    url = "https://github.com/DavHau/mach-nix";
    rev = "latest";
  }) {};
  
  myPython = mach-nix.mkPython {
    requirements = builtins.readFile ./requirements.txt;
    
    # Pin specific versions
    packagesExtra = [
      "tensorflow==2.10.0"
    ];
    
    # System dependencies
    providers = {
      numpy = "nixpkgs";
      tensorflow = "wheel";
    };
  };
in
pkgs.mkShell {
  buildInputs = [ myPython ];
}
```

### Production Deployment Patterns

```nix
# Complete application with service
{
  # The Python application
  myApp = poetry2nixLib.mkPoetryApplication {
    projectDir = ./.;
    preferWheels = true;  # Faster builds
  };
  
  # SystemD service
  systemd.services.my-python-app = {
    description = "My Python Application";
    wantedBy = [ "multi-user.target" ];
    
    serviceConfig = {
      ExecStart = "${myApp}/bin/my-app";
      Restart = "always";
      User = "myapp";
      
      # Security hardening
      PrivateTmp = true;
      ProtectSystem = "strict";
      ProtectHome = true;
    };
  };
  
  # NixOS module
  services.my-python-app = {
    enable = mkEnableOption "My Python Application";
    port = mkOption {
      type = types.port;
      default = 8000;
    };
  };
}
```

### CI/CD with Nix

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: cachix/install-nix-action@v22
      - uses: cachix/cachix-action@v12
        with:
          name: my-cache
      
      - run: nix build
      - run: nix flake check
      - run: nix develop -c pytest
```

---

## 🎓 Quick Reference: Which Level Is Right for You?

| Criteria | Level 1 | Level 2 | Level 3 |
|----------|---------|---------|---------|
| **Setup Complexity** | Low | Medium | High |
| **pip Compatibility** | Full | None | Via tools |
| **Reproducibility** | Partial | High | Perfect |
| **Team Sharing** | Hard | Easy | Automatic |
| **Production Ready** | No | Maybe | Yes |
| **Learning Curve** | Gentle | Moderate | Steep |

## 🌟 The Journey Forward

### Starting Your Journey

1. **Begin with Level 1** if you're new to NixOS
2. **Experiment with Level 2** for your next project
3. **Adopt Level 3** when you need production guarantees

### Key Insights to Remember

- **NixOS isn't broken, it's different**: Once you understand why, everything clicks
- **Each level has its place**: Use the right tool for the job
- **The journey is worth it**: Each level unlocks new capabilities
- **You're not alone**: The NixOS Python community is helpful and growing

### Resources for Your Journey

- **Level 1**: [nix.dev Python tutorial](https://nix.dev/tutorials/python)
- **Level 2**: [NixOS Wiki Python](https://nixos.wiki/wiki/Python)
- **Level 3**: [poetry2nix documentation](https://github.com/nix-community/poetry2nix)

## 🚀 Conclusion: From Confusion to Clarity

Remember when you first asked "Why doesn't pip work on NixOS?" Now you understand not just the "why" but the "how" of something better. You've learned that:

1. **Level 1** gives you a pragmatic bridge to get started
2. **Level 2** shows you the power of declarative environments
3. **Level 3** enables professional, production-grade workflows

The journey from `pip install` to `nix develop` isn't just about different commands - it's about a fundamentally better way to manage Python environments. One that's reproducible, shareable, and conflict-free.

Welcome to Python development on NixOS. Once you experience it, you'll never want to go back.

---

*"In NixOS, we don't fight the system. We understand it, embrace it, and discover it's actually better than what we left behind."* 🌊