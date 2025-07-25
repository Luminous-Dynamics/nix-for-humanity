# 📦 Installing Nix for Humanity via Flake

## Quick Install

### Try it out without installing:
```bash
nix run github:Luminous-Dynamics/nix-for-humanity
```

### Install to your profile:
```bash
nix profile install github:Luminous-Dynamics/nix-for-humanity
```

## NixOS Configuration

Add to your `flake.nix`:

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    nix-for-humanity.url = "github:Luminous-Dynamics/nix-for-humanity";
  };

  outputs = { self, nixpkgs, nix-for-humanity, ... }: {
    nixosConfigurations.yourhost = nixpkgs.lib.nixosSystem {
      modules = [
        ./configuration.nix
        nix-for-humanity.nixosModules.default
        {
          programs.nix-for-humanity.enable = true;
        }
      ];
    };
  };
}
```

## Home Manager

Add to your Home Manager configuration:

```nix
{
  inputs = {
    home-manager.url = "github:nix-community/home-manager";
    nix-for-humanity.url = "github:Luminous-Dynamics/nix-for-humanity";
  };

  # In your home configuration:
  home.packages = [ nix-for-humanity.packages.${system}.default ];
  
  # Or use the module:
  imports = [ nix-for-humanity.homeManagerModules.default ];
  programs.nix-for-humanity.enable = true;
}
```

## Development

Clone and enter development shell:

```bash
git clone https://github.com/Luminous-Dynamics/nix-for-humanity
cd nix-for-humanity
nix develop

# Now you can run:
npm install
npm run tauri:dev
```

## Building from Source

```bash
nix build github:Luminous-Dynamics/nix-for-humanity
./result/bin/nix-for-humanity
```

## Traditional Installation (non-flake)

If you're not using flakes:

```bash
nix-env -iA nixpkgs.nix-for-humanity
```

(Once we get it into nixpkgs!)

---

*Remember: Nix for Humanity uses natural language - just tell it what you want!*