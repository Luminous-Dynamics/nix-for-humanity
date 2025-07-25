# Minimal NixOS GUI configuration
# Quick setup for testing

{ config, pkgs, ... }:

{
  # Import the module
  imports = [ ../nixos-module.nix ];

  # Minimal configuration
  services.nixos-gui = {
    enable = true;
    
    # IMPORTANT: Generate your own secrets!
    # openssl rand -hex 64
    jwtSecret = "CHANGE-THIS-SECRET-b4f5e8d3a2c1f9e7b6d4a8c3e2f1d9b8a7c5e3d2b1f9e8d7c6b5a4d3c2b1a0";
    sessionSecret = "CHANGE-THIS-TOO-e9f8d7c6b5a4e3d2c1b0a9f8e7d6c5b4a3e2d1c0b9a8f7e6d5c4b3a2e1d0c9";
    
    # Open firewall for local testing
    openFirewall = true;
    
    # Auto-generate self-signed certificates
    ssl.autoGenerate = true;
  };
}

# To test this configuration:
# 1. Save as test-nixos-gui.nix
# 2. Run: sudo nixos-rebuild test -I nixos-config=./test-nixos-gui.nix
# 3. Access: https://localhost:8443
# 4. Login: admin / changeme