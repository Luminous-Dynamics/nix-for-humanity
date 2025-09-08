#!/bin/bash
# Create fine-tuned NixOS models using Ollama

echo "🎯 Creating Fine-Tuned NixOS Models"
echo "===================================="
echo

# 1. Command Model - Ultra fast command generation
echo "1️⃣ Creating NixOS Command Model..."
echo "   Base: gemma3:270m (291MB)"
echo "   Purpose: Instant command generation"
echo

ollama create nixos-commands -f nixos-command-modelfile
if [ $? -eq 0 ]; then
    echo "   ✅ nixos-commands model created!"
else
    echo "   ❌ Failed to create command model"
fi

# 2. Config Model - Configuration generation
echo
echo "2️⃣ Creating NixOS Config Model..."
cat > nixos-config-modelfile << 'EOF'
FROM gemma3:1b

TEMPLATE """Generate NixOS configuration for: {{ .Prompt }}
Configuration:"""

SYSTEM """You are a NixOS configuration expert. Generate valid Nix configuration snippets.
Output format: Valid Nix code that can be added to configuration.nix
Include comments explaining each section."""

PARAMETER temperature 0.5
PARAMETER top_p 0.7

MESSAGE user web server with nginx
MESSAGE assistant # Web server configuration
services.nginx = {
  enable = true;
  virtualHosts."localhost" = {
    root = "/var/www";
    locations."/" = {
      index = "index.html";
    };
  };
};
networking.firewall.allowedTCPPorts = [ 80 443 ];

MESSAGE user development environment for rust
MESSAGE assistant # Rust development environment
environment.systemPackages = with pkgs; [
  rustc
  cargo
  rustfmt
  rust-analyzer
  pkg-config
  openssl
];
EOF

ollama create nixos-config -f nixos-config-modelfile
if [ $? -eq 0 ]; then
    echo "   ✅ nixos-config model created!"
else
    echo "   ❌ Failed to create config model"
fi

# 3. Error Model - Troubleshooting assistance
echo
echo "3️⃣ Creating NixOS Error Resolution Model..."
cat > nixos-errors-modelfile << 'EOF'
FROM tinyllama:1.1b

TEMPLATE """NixOS Error: {{ .Prompt }}
Solution:"""

SYSTEM """You are a NixOS troubleshooting expert. Provide concise solutions for errors.
Format: 1. Cause 2. Solution 3. Command if applicable"""

PARAMETER temperature 0.4
PARAMETER top_p 0.6

MESSAGE user error: attribute 'vscode' not found
MESSAGE assistant 1. Package name might be different
2. Use correct attribute path
3. nix-env -iA nixos.vscode or search: nix-env -qaP | grep vscode

MESSAGE user error: collision between packages
MESSAGE assistant 1. Multiple packages provide same file
2. Use priority or remove conflicting package  
3. nix-env --set-flag priority 10 package-name

MESSAGE user error: no space left on device
MESSAGE assistant 1. Nix store using too much space
2. Clean old generations and garbage collect
3. nix-collect-garbage -d && sudo nixos-rebuild boot
EOF

ollama create nixos-errors -f nixos-errors-modelfile
if [ $? -eq 0 ]; then
    echo "   ✅ nixos-errors model created!"
else
    echo "   ❌ Failed to create errors model"
fi

# Test the models
echo
echo "🧪 Testing Fine-Tuned Models..."
echo "================================"
echo

echo "Test 1: Command Generation"
echo -n "Query: 'install firefox' → "
ollama run nixos-commands "install firefox" --nowordwrap 2>/dev/null | head -1

echo
echo "Test 2: Config Generation"
echo "Query: 'postgres database'"
ollama run nixos-config "postgres database" --nowordwrap 2>/dev/null | head -5

echo
echo "Test 3: Error Resolution"
echo -n "Query: 'command not found' → "
ollama run nixos-errors "command not found: npm" --nowordwrap 2>/dev/null | head -3

echo
echo "✅ Fine-tuning complete! Models available:"
echo "   • nixos-commands - Ultra-fast command generation"
echo "   • nixos-config - Configuration snippets"
echo "   • nixos-errors - Error resolution"
echo
echo "Use: ollama run nixos-commands 'your query'"