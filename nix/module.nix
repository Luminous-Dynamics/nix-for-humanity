{ config, lib, pkgs, ... }:

with lib;

let
  cfg = config.programs.luminous-nix;
in {
  options.programs.luminous-nix = {
    enable = mkEnableOption "Luminous Nix - Natural language NixOS interface";
    
    package = mkOption {
      type = types.package;
      default = pkgs.luminous-nix;
      description = "The luminous-nix package to use";
    };
    
    extensions = mkOption {
      type = types.listOf (types.enum [ "voice" "learning" "ai" ]);
      default = [];
      description = "Extensions to enable";
    };
  };
  
  config = mkIf cfg.enable {
    environment.systemPackages = [ cfg.package ];
    
    # Set up shell aliases
    environment.shellAliases = {
      nix = "ask-nix";
    };
  };
}
