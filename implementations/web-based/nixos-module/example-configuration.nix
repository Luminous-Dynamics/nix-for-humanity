# Example NixOS configuration with NixOS GUI enabled
{ config, pkgs, ... }:

{
  imports = [
    # Your hardware configuration
    ./hardware-configuration.nix
    
    # NixOS GUI module
    ./nixos-gui/nixos-module
  ];

  # Basic configuration
  networking.hostName = "my-nixos-system";
  time.timeZone = "America/New_York";

  # Enable NixOS GUI with default settings
  services.nixos-gui = {
    enable = true;
    
    # Optional: Change the port (default is 8080)
    # port = 8080;
    
    # Optional: Enable SSL
    # ssl = {
    #   enable = true;
    #   cert = "/path/to/cert.pem";
    #   key = "/path/to/key.pem";
    # };
    
    # Optional: Configure allowed groups (defaults to wheel and nixos-gui)
    # allowedGroups = [ "wheel" "nixos-gui" "admin" ];
    
    # Optional: Open firewall ports (for remote access)
    # openFirewall = true;
    
    # Optional: Configure nginx reverse proxy
    # nginx = {
    #   enable = true;
    #   virtualHost = "nixos-gui.example.com";
    # };
    
    # Optional: Disable specific features
    # features = {
    #   packageManagement = true;
    #   serviceManagement = true;
    #   configurationEdit = true;
    #   systemRebuild = true;
    #   generationManagement = true;
    #   auditLogging = true;
    # };
    
    # Optional: Set log level (error, warn, info, debug)
    # logLevel = "info";
  };

  # Create a dedicated admin user for NixOS GUI
  users.users.nixadmin = {
    isNormalUser = true;
    description = "NixOS GUI Administrator";
    extraGroups = [ "wheel" "nixos-gui" ];
    # Set password with: passwd nixadmin
  };

  # Or add existing users to the nixos-gui group
  # users.users.myuser.extraGroups = [ "nixos-gui" ];

  # Enable the X11 windowing system (if you want desktop access)
  services.xserver.enable = true;
  
  # Enable a desktop environment (optional)
  services.xserver.displayManager.lightdm.enable = true;
  services.xserver.desktopManager.xfce.enable = true;

  # Configure nginx if using reverse proxy
  # services.nginx = {
  #   enable = true;
  #   recommendedGzipSettings = true;
  #   recommendedOptimisation = true;
  #   recommendedProxySettings = true;
  #   recommendedTlsSettings = true;
  #   
  #   virtualHosts."nixos-gui.example.com" = {
  #     enableACME = true;
  #     forceSSL = true;
  #   };
  # };

  # System packages
  environment.systemPackages = with pkgs; [
    firefox  # To access the GUI
    vim
    git
  ];

  # This value determines the NixOS release with which your system is compatible
  system.stateVersion = "24.05";
}