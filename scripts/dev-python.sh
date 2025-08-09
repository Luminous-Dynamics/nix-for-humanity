#!/usr/bin/env bash
# Minimal Python development environment for slow connections

echo "🐍 Starting minimal Python environment..."
echo "This avoids downloading large packages"
echo

# Enter a shell with just Python and pip
exec nix-shell -p python313 python313Packages.pip --run "
echo '✅ Python $(python3 --version) ready!'
echo
echo 'Available commands:'
echo '  python3 - Python interpreter'
echo '  pip - Package installer'
echo
echo 'To test Nix for Humanity:'
echo '  cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity'
echo '  ./test-phase-0.sh'
echo
bash
"