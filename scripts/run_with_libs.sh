#!/usr/bin/env bash
#
# Run Python scripts with proper C++ library support for databases
# This is needed for DuckDB and Kùzu on NixOS
#

echo "🌟 Running with NixOS library support..."
nix-shell -p stdenv.cc.cc.lib --run "poetry run python $@"