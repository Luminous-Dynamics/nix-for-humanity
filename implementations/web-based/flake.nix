{
  description = "NixOS GUI - Web-based graphical interface for NixOS system management";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }: 
    let
      systems = [ "x86_64-linux" "aarch64-linux" ];
    in
    {
      # NixOS module
      nixosModules = {
        default = import ./nixos-module;
        nixos-gui = import ./nixos-module;
      };

      # Overlay
      overlays.default = final: prev: {
        nixos-gui = final.callPackage ./nixos-module/package.nix { };
      };
      
    } // flake-utils.lib.eachSystem systems (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ self.overlays.default ];
        };
      in
      {
        # Package
        packages = {
          default = pkgs.nixos-gui;
          nixos-gui = pkgs.nixos-gui;
        };

        # Development shell
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            nodejs_20
            nodePackages.npm
            nodePackages.node-gyp
            python3
            gcc
            pkg-config
            dbus
            systemd
            
            # Development tools
            nodePackages.typescript
            nodePackages.eslint
            nodePackages.prettier
            nodePackages.jest
          ];

          shellHook = ''
            echo "NixOS GUI Development Environment"
            echo "================================"
            echo "Run 'npm install' to install dependencies"
            echo "Run 'npm run dev' to start development server"
            echo "Run 'npm test' to run tests"
            echo "Run 'npm run build' to build for production"
            echo ""
            echo "To test the NixOS module:"
            echo "  nix build .#nixosConfigurations.test.config.system.build.vm"
            echo "  ./result/bin/run-nixos-vm"
          '';
        };

        # Apps
        apps = {
          default = {
            type = "app";
            program = "${self.packages.${system}.nixos-gui}/bin/nixos-gui";
          };
          
          nixos-gui-cli = {
            type = "app";
            program = "${self.packages.${system}.nixos-gui}/bin/nixos-gui-cli";
          };
        };
      }) // {
        # Test configuration
        nixosConfigurations.test = nixpkgs.lib.nixosSystem {
          system = "x86_64-linux";
          modules = [
            self.nixosModules.default
            ({ pkgs, ... }: {
              # Minimal test configuration
              boot.loader.grub.device = "nodev";
              fileSystems."/" = {
                device = "none";
                fsType = "tmpfs";
              };
              
              # Enable NixOS GUI
              services.nixos-gui = {
                enable = true;
                openFirewall = true;
              };
              
              # Test user
              users.users.test = {
                isNormalUser = true;
                extraGroups = [ "wheel" "nixos-gui" ];
                password = "test";
              };
              
              # Enable X11 for testing
              services.xserver = {
                enable = true;
                displayManager.lightdm.enable = true;
                desktopManager.xfce.enable = true;
              };
              
              # VM settings
              virtualisation = {
                memorySize = 2048;
                diskSize = 8192;
                graphics = true;
              };
              
              system.stateVersion = "24.05";
            })
          ];
        };
      };
}