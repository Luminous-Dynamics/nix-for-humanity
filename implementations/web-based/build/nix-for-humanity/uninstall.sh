#!/usr/bin/env bash
# Nix for Humanity uninstaller

set -e

echo "🧹 Uninstalling Nix for Humanity..."

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)" 
   exit 1
fi

# Stop and disable service
echo "Stopping service..."
systemctl stop nix-for-humanity || true
systemctl disable nix-for-humanity || true

# Remove service file
rm -f /etc/systemd/system/nix-for-humanity.service
systemctl daemon-reload

# Remove files
echo "Removing files..."
rm -rf /opt/nix-for-humanity
rm -rf /var/lib/nix-for-humanity

# Remove user (optional)
read -p "Remove nix-humanity user? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    userdel nix-humanity || true
fi

echo "✅ Nix for Humanity uninstalled successfully!"
