{ pkgs ? import <nixpkgs> {} }:

let
  poetry2nix = import (fetchTarball {
    url = "https://github.com/nix-community/poetry2nix/archive/main.tar.gz";
  }) {
    inherit pkgs;
  };
  
in poetry2nix.mkPoetryEnv {
  projectDir = ./.;
  python = pkgs.python311;
  preferWheels = true;
  
  overrides = poetry2nix.defaultPoetryOverrides.extend
    (self: super: {
      # Use wheels for Data Trinity databases
      duckdb = super.duckdb.override {
        preferWheel = true;
      };
      chromadb = super.chromadb.override {
        preferWheel = true;
      };
      kuzu = super.kuzu.override {
        preferWheel = true;
      };
    });
}