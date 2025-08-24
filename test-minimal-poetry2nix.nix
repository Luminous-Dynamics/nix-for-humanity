{ pkgs ? import <nixpkgs> {} }:

let
  poetry2nix = import (fetchTarball {
    url = "https://github.com/nix-community/poetry2nix/archive/2024.11.79136.tar.gz";
    sha256 = "11vr09q9pnfr0kpi3r8idj96yfil42snq6xvd2ka0lxsj0dh6jn9";
  }) {
    inherit pkgs;
  };
  
in poetry2nix.mkPoetryEnv {
  projectDir = ./.;
  python = pkgs.python311;
  preferWheels = true;
}
