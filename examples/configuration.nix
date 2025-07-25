# Example NixOS configuration with NixOS GUI
# Add this to your /etc/nixos/configuration.nix or as a module

{ config, pkgs, ... }:

{
  imports = [
    # Your existing imports
    ./hardware-configuration.nix
    
    # Import NixOS GUI module
    # Option 1: From flake
    # inputs.nixos-gui.nixosModules.default
    
    # Option 2: From local path
    # /path/to/nixos-gui/nixos-module.nix
  ];

  # Basic configuration
  services.nixos-gui = {
    enable = true;
    
    # Generate secure secrets with:
    # openssl rand -hex 64
    jwtSecret = "your-secure-jwt-secret-here";
    sessionSecret = "your-secure-session-secret-here";
    
    # Network configuration
    host = "0.0.0.0";  # Listen on all interfaces
    httpPort = 8080;
    httpsPort = 8443;
    openFirewall = true;
    
    # SSL configuration
    ssl = {
      enable = true;
      # For production, use Let's Encrypt:
      # certFile = "/var/lib/acme/nixos-gui.example.com/cert.pem";
      # keyFile = "/var/lib/acme/nixos-gui.example.com/key.pem";
      
      # For development/testing:
      autoGenerate = true;
    };
    
    # Authentication
    authentication = {
      enable = true;
      initialAdminPassword = "changeme";  # Change on first login!
      allowedGroups = [ "wheel" "nixos-gui-users" ];
    };
    
    # Performance
    cache = {
      enable = true;
      # Optionally use external Redis
      # redis = "redis://localhost:6379";
    };
    
    # Features
    features = {
      aiAssistant = true;
      smartSuggestions = true;
      systemMonitoring = true;
      consciousnessFirst = true;  # Sacred features
    };
  };
  
  # Optional: Create a dedicated user group
  users.groups.nixos-gui-users = {};
  
  # Optional: Add users to the group
  users.users.alice = {
    isNormalUser = true;
    extraGroups = [ "wheel" "nixos-gui-users" ];
  };
  
  # Optional: Use with nginx reverse proxy
  services.nginx = {
    enable = true;
    recommendedProxySettings = true;
    recommendedTlsSettings = true;
    
    virtualHosts."nixos-gui.example.com" = {
      enableACME = true;
      forceSSL = true;
      
      locations."/" = {
        proxyPass = "http://localhost:8080";
        proxyWebsockets = true;
      };
    };
  };
  
  # Optional: Firewall rules (if not using openFirewall)
  # networking.firewall.allowedTCPPorts = [ 80 443 ];
}

# ===== Flake-based Configuration =====
# If using flakes, your flake.nix should look like:
#
# {
#   inputs = {
#     nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
#     nixos-gui.url = "github:Luminous-Dynamics/nixos-gui";
#   };
#   
#   outputs = { self, nixpkgs, nixos-gui }: {
#     nixosConfigurations.mysystem = nixpkgs.lib.nixosSystem {
#       system = "x86_64-linux";
#       modules = [
#         ./configuration.nix
#         nixos-gui.nixosModules.default
#       ];
#     };
#   };
# }