"""
NixOS Context Generator

Automatically generates NixOS-specific solutions for general IT tasks.
This enables dual-answer mode: show both general approach AND the NixOS way.
"""

from typing import Optional, Dict
from .routing.query_router import Domain


class NixOSContextGenerator:
    """
    Generates NixOS-specific context for general IT queries.

    When a user asks a general IT question, this provides the NixOS way
    to accomplish the same task, enabling automatic dual-answer mode.
    """

    def __init__(self):
        """Initialize with common NixOS patterns"""

        # Map common tasks to NixOS approaches
        self.patterns = {
            # Web Servers
            'nginx': {
                'general': 'Install nginx with package manager',
                'nixos': '''services.nginx = {
  enable = true;
  virtualHosts."example.com" = {
    root = "/var/www/example";
  };
};''',
                'description': 'Nginx web server'
            },
            'apache': {
                'general': 'Install Apache HTTP Server',
                'nixos': '''services.httpd = {
  enable = true;
  virtualHosts."example.com" = {
    documentRoot = "/var/www/example";
  };
};''',
                'description': 'Apache web server'
            },

            # Databases
            'postgresql': {
                'general': 'Install PostgreSQL database',
                'nixos': '''services.postgresql = {
  enable = true;
  ensureDatabases = [ "mydb" ];
  authentication = pkgs.lib.mkOverride 10 \'\'
    local all all trust
  \'\';
};''',
                'description': 'PostgreSQL database'
            },
            'mysql': {
                'general': 'Install MySQL/MariaDB database',
                'nixos': '''services.mysql = {
  enable = true;
  package = pkgs.mariadb;
  ensureDatabases = [ "mydb" ];
};''',
                'description': 'MySQL/MariaDB database'
            },
            'mongodb': {
                'general': 'Install MongoDB database',
                'nixos': '''services.mongodb = {
  enable = true;
  bind_ip = "127.0.0.1";
};''',
                'description': 'MongoDB database'
            },

            # Programming Languages & Runtimes
            'python': {
                'general': 'Install Python interpreter',
                'nixos': '''# In configuration.nix:
environment.systemPackages = [ pkgs.python311 ];

# Or for development (flake.nix):
{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  outputs = { nixpkgs, ... }: {
    devShells.default = nixpkgs.legacyPackages.x86_64-linux.mkShell {
      buildInputs = [ nixpkgs.legacyPackages.x86_64-linux.python311 ];
    };
  };
}''',
                'description': 'Python development'
            },
            'nodejs': {
                'general': 'Install Node.js runtime',
                'nixos': '''# In configuration.nix:
environment.systemPackages = [ pkgs.nodejs_20 ];

# Or for development (flake.nix):
{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  outputs = { nixpkgs, ... }: {
    devShells.default = nixpkgs.legacyPackages.x86_64-linux.mkShell {
      buildInputs = with pkgs; [ nodejs_20 yarn ];
    };
  };
}''',
                'description': 'Node.js development'
            },

            # DevOps Tools
            'docker': {
                'general': 'Install Docker container runtime',
                'nixos': '''virtualisation.docker = {
  enable = true;
};

# Add your user to docker group:
users.users.youruser.extraGroups = [ "docker" ];''',
                'description': 'Docker containers'
            },
            'kubernetes': {
                'general': 'Install Kubernetes (k8s)',
                'nixos': '''services.kubernetes = {
  roles = ["master" "node"];
  masterAddress = "localhost";
};''',
                'description': 'Kubernetes cluster'
            },

            # Development Tools
            'git': {
                'general': 'Install Git version control',
                'nixos': '''environment.systemPackages = [ pkgs.git ];

# Configure globally:
programs.git = {
  enable = true;
  config = {
    user.name = "Your Name";
    user.email = "you@example.com";
  };
};''',
                'description': 'Git version control'
            },
            'vim': {
                'general': 'Install Vim editor',
                'nixos': '''programs.vim = {
  enable = true;
  defaultEditor = true;
};''',
                'description': 'Vim text editor'
            },
            'vscode': {
                'general': 'Install VS Code editor',
                'nixos': '''environment.systemPackages = [ pkgs.vscode ];

# Or with extensions:
programs.vscode = {
  enable = true;
  extensions = with pkgs.vscode-extensions; [
    ms-python.python
    ms-vscode.cpptools
  ];
};''',
                'description': 'VS Code editor'
            },
        }

    def can_provide_nixos_context(self, query: str, domain: Domain) -> bool:
        """
        Determine if we can provide helpful NixOS context for this query.

        Args:
            query: User's query
            domain: Detected domain

        Returns:
            True if we have relevant NixOS context to provide
        """
        query_lower = query.lower()

        # Check for installation/setup keywords
        setup_keywords = ['install', 'setup', 'configure', 'set up', 'enable',
                         'start', 'run', 'deploy', 'add', 'get']
        has_setup_intent = any(kw in query_lower for kw in setup_keywords)

        if not has_setup_intent:
            return False

        # Check if we have a pattern for this
        for tool in self.patterns.keys():
            if tool in query_lower:
                return True

        return False

    def generate_nixos_context(self, query: str, general_answer: str = "") -> Optional[str]:
        """
        Generate NixOS-specific context for a general IT query.

        Args:
            query: User's query
            general_answer: The general (non-NixOS) answer provided

        Returns:
            NixOS-specific answer, or None if not applicable
        """
        query_lower = query.lower()

        # Find matching pattern
        matched_pattern = None
        matched_tool = None

        for tool, pattern in self.patterns.items():
            if tool in query_lower:
                matched_pattern = pattern
                matched_tool = tool
                break

        if not matched_pattern:
            return None

        # Generate NixOS-specific answer
        nixos_answer = f"""**{matched_pattern['description'].title()} on NixOS:**

Add to `/etc/nixos/configuration.nix`:

```nix
{matched_pattern['nixos']}
```

Then apply:
```bash
sudo nixos-rebuild switch
```

**Why NixOS?** This declarative approach means:
- ✅ Configuration is version controlled
- ✅ Easy to replicate on other machines
- ✅ Rollback if something breaks
- ✅ No manual package management
"""

        return nixos_answer

    def get_dual_answer_format(self, general_answer: str, nixos_answer: str) -> str:
        """
        Format a dual answer showing both general and NixOS approaches.

        Args:
            general_answer: General IT answer
            nixos_answer: NixOS-specific answer

        Returns:
            Beautifully formatted dual answer
        """
        return f"""💻 **General Approach**

{general_answer}

---

🔷 **The NixOS Way**

{nixos_answer}

---

💡 **Tip**: You can disable dual-answers with `/settings` if you prefer just one approach!
"""


def get_context_generator() -> NixOSContextGenerator:
    """Get singleton instance of NixOS context generator"""
    global _context_generator
    if _context_generator is None:
        _context_generator = NixOSContextGenerator()
    return _context_generator


# Singleton instance
_context_generator = None
