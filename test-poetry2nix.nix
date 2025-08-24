# Test poetry2nix after removing mkdocstrings
{ pkgs ? import <nixpkgs> {} }:

let
  poetry2nix = pkgs.poetry2nix;
  
  # Test building the environment
  poetryEnv = poetry2nix.mkPoetryEnv {
    projectDir = ./.;
    python = pkgs.python311;
    preferWheels = true;
  };
in
{
  inherit poetryEnv;
  
  # Test that we can build it
  test = pkgs.runCommand "test-poetry2nix" {} ''
    echo "Testing poetry2nix environment..."
    ${poetryEnv}/bin/python --version
    echo "SUCCESS: Poetry2nix environment builds!"
    touch $out
  '';
}