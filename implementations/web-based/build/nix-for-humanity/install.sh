#!/usr/bin/env bash
# Nix for Humanity installer

set -e

echo "🌟 Installing Nix for Humanity..."

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)" 
   exit 1
fi

# Install location
INSTALL_DIR="/opt/nix-for-humanity"
DATA_DIR="/var/lib/nix-for-humanity"
SERVICE_FILE="/etc/systemd/system/nix-for-humanity.service"

# Create user
if ! id -u nix-humanity >/dev/null 2>&1; then
    echo "Creating nix-humanity user..."
    useradd -r -s /bin/false -d /var/lib/nix-for-humanity nix-humanity
fi

# Create directories
echo "Creating directories..."
mkdir -p "$INSTALL_DIR" "$DATA_DIR"

# Copy files
echo "Copying files..."
cp -r * "$INSTALL_DIR/"
chown -R nix-humanity:nix-humanity "$INSTALL_DIR" "$DATA_DIR"

# Install systemd service
echo "Installing systemd service..."
cp scripts/nix-for-humanity.service "$SERVICE_FILE"
systemctl daemon-reload

# Install dependencies
echo "Installing Node.js dependencies..."
cd "$INSTALL_DIR"
npm install --production

# Enable and start service
echo "Starting service..."
systemctl enable nix-for-humanity
systemctl start nix-for-humanity

# Print status
echo
echo "✅ Nix for Humanity installed successfully!"
echo
echo "Service status:"
systemctl status nix-for-humanity --no-pager
echo
echo "Access the interface at: http://localhost:3456"
echo
echo "To view logs: journalctl -u nix-for-humanity -f"
echo "To stop: systemctl stop nix-for-humanity"
echo "To uninstall: /opt/nix-for-humanity/uninstall.sh"
