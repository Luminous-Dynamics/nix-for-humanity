# Example flake.nix with Nix for Humanity voice interface
{
  description = "My NixOS configuration with voice-controlled Nix";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    
    # Add Nix for Humanity
    nix-humanity = {
      url = "github:Luminous-Dynamics/nix-for-humanity";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, nix-humanity, ... }@inputs: {
    nixosConfigurations = {
      myhost = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        
        modules = [
          # Hardware configuration
          ./hardware-configuration.nix
          
          # Import Nix for Humanity voice module
          nix-humanity.nixosModules.voice
          
          # Your configuration
          ({ config, pkgs, ... }: {
            # Basic system configuration
            networking.hostName = "myhost";
            
            # Enable Nix for Humanity voice interface
            services.nixForHumanity.voice = {
              enable = true;
              
              # Choose your preferred settings
              whisperModel = "base";           # Good balance of speed/accuracy
              piperVoice = "en_US-amy-medium"; # Clear, natural voice
              
              # Customize if needed
              wakeWord = "hey computer";       # Star Trek style!
              speechRate = 1.1;                # Slightly faster
              
              # Auto-download models
              autoDownloadModels = true;
            };
            
            # Audio configuration
            sound.enable = true;
            services.pipewire = {
              enable = true;
              alsa.enable = true;
              pulse.enable = true;
            };
            
            # Install Nix for Humanity tools
            environment.systemPackages = [
              nix-humanity.packages.${pkgs.system}.nix-for-humanity
              nix-humanity.packages.${pkgs.system}.ask-nix-guru
            ];
            
            # User configuration
            users.users.myuser = {
              isNormalUser = true;
              extraGroups = [ "wheel" "audio" ];
            };
          })
        ];
      };
    };
  };
}