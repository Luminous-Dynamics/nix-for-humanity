#!/usr/bin/env python3
"""
Build comprehensive NixOS dataset for HRM training
Generates 1000+ examples from real NixOS patterns
"""

import json
import random
import re
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, asdict

@dataclass
class NixOSExample:
    """Training example for HRM"""
    input_query: str
    task_type: str  # dependency, config, error, optimization
    reasoning_steps: List[str]
    expected_output: str
    constraints: List[str]
    metadata: Dict[str, Any]

class NixOSDatasetBuilder:
    """Build comprehensive training dataset for HRM"""
    
    def __init__(self, output_dir: str = "data/nixos-hrm-training"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Common NixOS packages for examples
        self.packages = [
            "firefox", "chromium", "brave", "vscode", "vim", "neovim", "emacs",
            "python311", "python312", "nodejs_18", "nodejs_20", "rustc", "cargo",
            "gcc", "clang", "git", "docker", "podman", "postgresql", "mysql",
            "nginx", "apache", "redis", "mongodb", "elasticsearch", "grafana",
            "prometheus", "kde", "gnome", "xfce", "i3", "sway", "hyprland"
        ]
        
        # Common services
        self.services = [
            "nginx", "postgresql", "mysql", "redis", "docker", "ssh", 
            "firewall", "networking", "printing", "bluetooth", "audio"
        ]
        
        # Common errors
        self.error_patterns = [
            "attribute '{pkg}' missing",
            "collision between '{pkg1}' and '{pkg2}'",
            "undefined variable '{var}'",
            "permission denied",
            "out of disk space",
            "failed to build '{pkg}'"
        ]
    
    def generate_dependency_examples(self, count: int = 250) -> List[NixOSExample]:
        """Generate dependency resolution examples"""
        examples = []
        
        for i in range(count):
            # Pick random packages for conflict
            pkg1, pkg2 = random.sample(self.packages, 2)
            
            # Generate variations
            variations = [
                {
                    "query": f"install {pkg1} and {pkg2} but they conflict",
                    "solution": f"nixpkgs.overlays = [(self: super: {{ {pkg1} = super.{pkg1}.overrideAttrs (old: {{ meta.priority = 5; }}); }})];",
                    "steps": [
                        f"Identify conflict between {pkg1} and {pkg2}",
                        "Check if packages provide same files",
                        "Create overlay to set priority",
                        "Apply overlay in configuration"
                    ]
                },
                {
                    "query": f"resolve collision between {pkg1} and {pkg2}",
                    "solution": f"environment.systemPackages = [ (pkgs.{pkg1}.override {{ enableFeature = false; }}) pkgs.{pkg2} ];",
                    "steps": [
                        "Analyze collision cause",
                        "Identify conflicting files",
                        "Use override to disable conflicting feature",
                        "Install both packages safely"
                    ]
                },
                {
                    "query": f"both {pkg1} and {pkg2} provide same binary",
                    "solution": f"programs.{pkg1}.enable = true; # Use NixOS module instead",
                    "steps": [
                        "Check if NixOS modules exist",
                        "Use module for primary package",
                        "Alternative package via nix-shell"
                    ]
                }
            ]
            
            variant = random.choice(variations)
            
            examples.append(NixOSExample(
                input_query=variant["query"],
                task_type="dependency",
                reasoning_steps=variant["steps"],
                expected_output=variant["solution"],
                constraints=["must_coexist", "no_conflicts", "maintain_functionality"],
                metadata={"packages": [pkg1, pkg2], "example_id": f"dep_{i:04d}"}
            ))
        
        return examples
    
    def generate_configuration_examples(self, count: int = 250) -> List[NixOSExample]:
        """Generate configuration examples"""
        examples = []
        
        for i in range(count):
            service = random.choice(self.services)
            
            variations = [
                {
                    "query": f"setup {service} with SSL",
                    "config": self._generate_service_config(service, ssl=True),
                    "steps": [
                        f"Enable {service} service",
                        "Configure SSL certificates",
                        "Set up firewall rules",
                        "Enable auto-start"
                    ]
                },
                {
                    "query": f"configure {service} for production",
                    "config": self._generate_service_config(service, production=True),
                    "steps": [
                        f"Enable {service} with hardening",
                        "Configure resource limits",
                        "Set up monitoring",
                        "Enable backups"
                    ]
                },
                {
                    "query": f"setup development environment with {service}",
                    "config": self._generate_dev_config(service),
                    "steps": [
                        f"Configure {service} for development",
                        "Disable strict security",
                        "Enable debug logging",
                        "Set up hot reload"
                    ]
                }
            ]
            
            variant = random.choice(variations)
            
            examples.append(NixOSExample(
                input_query=variant["query"],
                task_type="configuration",
                reasoning_steps=variant["steps"],
                expected_output=variant["config"],
                constraints=["secure", "performant", "maintainable"],
                metadata={"service": service, "example_id": f"conf_{i:04d}"}
            ))
        
        return examples
    
    def generate_error_examples(self, count: int = 250) -> List[NixOSExample]:
        """Generate error diagnosis examples"""
        examples = []
        
        for i in range(count):
            error_template = random.choice(self.error_patterns)
            pkg = random.choice(self.packages)
            
            if "{pkg1}" in error_template:
                pkg1, pkg2 = random.sample(self.packages, 2)
                error = error_template.format(pkg1=pkg1, pkg2=pkg2)
            else:
                error = error_template.format(pkg=pkg, var=f"var_{i}")
            
            # Generate appropriate fix
            if "missing" in error:
                fix = f"nix-channel --update && nix-env -iA nixpkgs.{pkg}"
                steps = [
                    "Package not found in current channel",
                    "Channel might be outdated",
                    "Update channel",
                    "Install package from updated channel"
                ]
            elif "collision" in error:
                fix = "Set package priority in overlay"
                steps = [
                    "Two packages provide same file",
                    "Check file conflicts",
                    "Create overlay with priority",
                    "Rebuild configuration"
                ]
            elif "undefined" in error:
                fix = "Define variable in let binding or imports"
                steps = [
                    "Variable not in scope",
                    "Check if import missing",
                    "Add proper import or definition",
                    "Verify syntax"
                ]
            else:
                fix = "Check system resources and permissions"
                steps = [
                    "System-level issue detected",
                    "Check disk space",
                    "Verify permissions",
                    "Resolve underlying cause"
                ]
            
            examples.append(NixOSExample(
                input_query=f"error: {error}",
                task_type="error",
                reasoning_steps=steps,
                expected_output=fix,
                constraints=["find_root_cause", "provide_fix", "prevent_recurrence"],
                metadata={"error_type": error.split(':')[0], "example_id": f"err_{i:04d}"}
            ))
        
        return examples
    
    def generate_optimization_examples(self, count: int = 250) -> List[NixOSExample]:
        """Generate optimization examples"""
        examples = []
        
        optimization_goals = [
            "boot time", "disk usage", "memory usage", "build time",
            "battery life", "network performance", "compilation speed"
        ]
        
        for i in range(count):
            goal = random.choice(optimization_goals)
            
            if goal == "boot time":
                solution = """
boot.loader.timeout = 1;
boot.initrd.availableKernelModules = [ "necessary_only" ];
systemd.services."slow-service".enable = false;"""
                steps = [
                    "Reduce bootloader timeout",
                    "Minimize initrd modules",
                    "Disable unnecessary services",
                    "Optimize systemd dependencies"
                ]
            elif goal == "disk usage":
                solution = """
nix.gc = {
  automatic = true;
  dates = "weekly";
  options = "--delete-older-than 7d";
};
nix.optimise.automatic = true;"""
                steps = [
                    "Enable automatic garbage collection",
                    "Delete old generations",
                    "Optimize nix store",
                    "Remove unnecessary packages"
                ]
            elif goal == "memory usage":
                solution = """
boot.kernel.sysctl = {
  "vm.swappiness" = 10;
  "vm.vfs_cache_pressure" = 50;
};
zramSwap.enable = true;"""
                steps = [
                    "Tune kernel memory parameters",
                    "Enable zram compression",
                    "Reduce swappiness",
                    "Optimize cache pressure"
                ]
            else:
                solution = f"# Optimize {goal}"
                steps = [
                    f"Analyze {goal} bottlenecks",
                    "Identify optimization opportunities",
                    "Apply targeted improvements",
                    "Measure results"
                ]
            
            examples.append(NixOSExample(
                input_query=f"optimize nixos for {goal}",
                task_type="optimization",
                reasoning_steps=steps,
                expected_output=solution,
                constraints=["improve_performance", "maintain_stability", "preserve_functionality"],
                metadata={"goal": goal, "example_id": f"opt_{i:04d}"}
            ))
        
        return examples
    
    def _generate_service_config(self, service: str, ssl: bool = False, production: bool = False) -> str:
        """Generate service configuration"""
        configs = {
            "nginx": f"""
services.nginx = {{
  enable = true;
  {'recommendedTlsSettings = true;' if ssl else ''}
  {'recommendedProxySettings = true;' if production else ''}
  virtualHosts."example.com" = {{
    {'enableACME = true; forceSSL = true;' if ssl else ''}
    locations."/" = {{
      proxyPass = "http://localhost:3000";
    }};
  }};
}};""",
            "postgresql": f"""
services.postgresql = {{
  enable = true;
  package = pkgs.postgresql_15;
  {'enableTCPIP = true;' if production else ''}
  authentication = pkgs.lib.mkOverride 10 ''
    local all all trust
    {'host all all 0.0.0.0/0 md5' if production else ''}
  '';
}};""",
            "docker": f"""
virtualisation.docker = {{
  enable = true;
  {'enableOnBoot = true;' if production else ''}
  {'autoPrune.enable = true;' if production else ''}
}};"""
        }
        
        return configs.get(service, f"services.{service}.enable = true;")
    
    def _generate_dev_config(self, service: str) -> str:
        """Generate development configuration"""
        return f"""
# Development environment with {service}
services.{service}.enable = true;
services.{service}.package = pkgs.{service};

environment.systemPackages = with pkgs; [
  git vim curl wget
  nodejs python3 rustc
];

# Development settings
services.{service}.extraConfig = ''
  log_level = debug
  reload_on_change = true
'';"""
    
    def build_complete_dataset(self) -> Path:
        """Build complete dataset with all categories"""
        print("🏗️ Building Comprehensive NixOS Dataset for HRM Training")
        print("=" * 60)
        
        all_examples = []
        
        # Generate examples for each category
        print("\n📦 Generating dependency examples...")
        dependency_examples = self.generate_dependency_examples(250)
        all_examples.extend(dependency_examples)
        print(f"  ✓ Generated {len(dependency_examples)} dependency examples")
        
        print("\n🔧 Generating configuration examples...")
        config_examples = self.generate_configuration_examples(250)
        all_examples.extend(config_examples)
        print(f"  ✓ Generated {len(config_examples)} configuration examples")
        
        print("\n🔍 Generating error diagnosis examples...")
        error_examples = self.generate_error_examples(250)
        all_examples.extend(error_examples)
        print(f"  ✓ Generated {len(error_examples)} error examples")
        
        print("\n⚡ Generating optimization examples...")
        optimization_examples = self.generate_optimization_examples(250)
        all_examples.extend(optimization_examples)
        print(f"  ✓ Generated {len(optimization_examples)} optimization examples")
        
        # Shuffle for training
        random.shuffle(all_examples)
        
        # Split into train/val/test
        total = len(all_examples)
        train_size = int(0.8 * total)  # 80% train
        val_size = int(0.1 * total)    # 10% validation
        # Remaining 10% for test
        
        train_examples = all_examples[:train_size]
        val_examples = all_examples[train_size:train_size + val_size]
        test_examples = all_examples[train_size + val_size:]
        
        # Save datasets
        datasets = {
            "train": train_examples,
            "validation": val_examples,
            "test": test_examples
        }
        
        for split_name, examples in datasets.items():
            output_file = self.output_dir / f"nixos_{split_name}.json"
            
            # Convert to dict format
            data = []
            for example in examples:
                data.append({
                    "input": example.input_query,
                    "task_type": example.task_type,
                    "reasoning_steps": example.reasoning_steps,
                    "output": example.expected_output,
                    "constraints": example.constraints,
                    "metadata": example.metadata
                })
            
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"\n📁 Saved {split_name} dataset: {output_file}")
            print(f"   Examples: {len(examples)}")
        
        # Create summary
        summary = {
            "total_examples": total,
            "train_examples": len(train_examples),
            "val_examples": len(val_examples),
            "test_examples": len(test_examples),
            "task_distribution": {
                "dependency": sum(1 for e in all_examples if e.task_type == "dependency"),
                "configuration": sum(1 for e in all_examples if e.task_type == "configuration"),
                "error": sum(1 for e in all_examples if e.task_type == "error"),
                "optimization": sum(1 for e in all_examples if e.task_type == "optimization")
            }
        }
        
        summary_file = self.output_dir / "dataset_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("\n" + "=" * 60)
        print("✅ Dataset Generation Complete!")
        print(f"📊 Total examples: {total}")
        print(f"📁 Output directory: {self.output_dir}")
        print("\n📈 Distribution:")
        for task, count in summary["task_distribution"].items():
            print(f"   {task}: {count} ({count/total*100:.1f}%)")
        
        return self.output_dir

def main():
    """Build the dataset"""
    builder = NixOSDatasetBuilder()
    dataset_dir = builder.build_complete_dataset()
    
    print("\n🎯 Next Steps:")
    print("1. Review generated examples for quality")
    print("2. Set up PyTorch training pipeline")
    print("3. Train HRM model on this dataset")
    print(f"4. Dataset location: {dataset_dir}")

if __name__ == "__main__":
    main()