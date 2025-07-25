#!/usr/bin/env bash

# Generate SSL certificates for HTTPS
# July 22, 2025

set -e

echo "🔐 Generating SSL certificates for NixOS GUI..."
echo "==========================================="

# Create SSL directory
SSL_DIR="$(dirname "$0")/../ssl"
mkdir -p "$SSL_DIR"

# Certificate details
COUNTRY="US"
STATE="Sacred"
LOCALITY="Digital"
ORGANIZATION="NixOS-GUI"
COMMON_NAME="localhost"

# Generate private key and certificate
echo "📝 Creating self-signed certificate..."

openssl req -x509 \
    -newkey rsa:4096 \
    -keyout "$SSL_DIR/key.pem" \
    -out "$SSL_DIR/cert.pem" \
    -days 365 \
    -nodes \
    -subj "/C=$COUNTRY/ST=$STATE/L=$LOCALITY/O=$ORGANIZATION/CN=$COMMON_NAME" \
    -addext "subjectAltName = DNS:localhost, IP:127.0.0.1, IP:::1"

# Set proper permissions
chmod 600 "$SSL_DIR/key.pem"
chmod 644 "$SSL_DIR/cert.pem"

echo ""
echo "✅ SSL certificates generated successfully!"
echo ""
echo "📁 Certificate location:"
echo "   Certificate: $SSL_DIR/cert.pem"
echo "   Private Key: $SSL_DIR/key.pem"
echo ""
echo "⚠️  These are self-signed certificates for development."
echo "   Browsers will show a security warning."
echo "   For production, use certificates from Let's Encrypt."
echo ""

# Optionally generate Diffie-Hellman parameters for extra security
read -p "Generate DH parameters for enhanced security? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔐 Generating DH parameters (this may take a while)..."
    openssl dhparam -out "$SSL_DIR/dhparam.pem" 2048
    chmod 644 "$SSL_DIR/dhparam.pem"
    echo "✅ DH parameters generated"
fi

echo ""
echo "🌟 SSL setup complete! Your HTTPS server is ready."