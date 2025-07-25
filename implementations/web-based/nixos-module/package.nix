{ lib
, stdenv
, fetchFromGitHub
, nodejs
, nodePackages
, makeWrapper
, python3
, gcc
, pkg-config
, dbus
, systemd
}:

let
  # Helper binary for privileged operations
  nixos-gui-helper = stdenv.mkDerivation {
    pname = "nixos-gui-helper";
    version = "2.0.0";
    
    src = ../backend/helper;
    
    nativeBuildInputs = [ gcc pkg-config ];
    buildInputs = [ dbus systemd ];
    
    buildPhase = ''
      gcc -O2 -Wall -o nixos-gui-helper nixos-gui-helper.c \
        $(pkg-config --cflags --libs dbus-1 systemd)
    '';
    
    installPhase = ''
      mkdir -p $out/bin
      cp nixos-gui-helper $out/bin/
      chmod 4755 $out/bin/nixos-gui-helper  # setuid root
    '';
  };

in stdenv.mkDerivation rec {
  pname = "nixos-gui";
  version = "2.0.0";
  
  src = lib.cleanSource ../..;
  
  nativeBuildInputs = [
    nodejs
    nodePackages.npm
    makeWrapper
    python3
  ];
  
  buildInputs = [
    nodejs
  ];
  
  # Skip npm install in build phase, we'll handle it differently
  dontNpmInstall = true;
  
  buildPhase = ''
    # Install npm dependencies
    export HOME=$TMPDIR
    npm ci --production
    
    # Build frontend assets
    npm run build
    
    # Create production bundle
    mkdir -p dist
    cp -r backend dist/
    cp -r public dist/
    cp package.json dist/
    cp package-lock.json dist/
    
    # Copy only production node_modules
    cp -r node_modules dist/
    
    # Remove development dependencies
    cd dist
    npm prune --production
    cd ..
  '';
  
  installPhase = ''
    # Create output directories
    mkdir -p $out/share/nixos-gui
    mkdir -p $out/bin
    mkdir -p $out/libexec
    
    # Copy application files
    cp -r dist/* $out/share/nixos-gui/
    
    # Install helper binary
    cp ${nixos-gui-helper}/bin/nixos-gui-helper $out/libexec/
    
    # Create wrapper script
    makeWrapper ${nodejs}/bin/node $out/bin/nixos-gui \
      --add-flags "$out/share/nixos-gui/backend/server.js" \
      --set NODE_ENV "production" \
      --set NIXOS_GUI_ROOT "$out/share/nixos-gui" \
      --prefix PATH : ${lib.makeBinPath [ 
        "/run/current-system/sw"
        systemd
      ]}
    
    # Create CLI helper script
    cat > $out/bin/nixos-gui-cli <<EOF
    #!/usr/bin/env bash
    exec ${nodejs}/bin/node $out/share/nixos-gui/backend/cli.js "\$@"
    EOF
    chmod +x $out/bin/nixos-gui-cli
    
    # Desktop file for GUI applications menu
    mkdir -p $out/share/applications
    cat > $out/share/applications/nixos-gui.desktop <<EOF
    [Desktop Entry]
    Type=Application
    Name=NixOS GUI
    Comment=Graphical system management for NixOS
    Icon=nixos
    Exec=xdg-open http://localhost:8080
    Categories=System;Settings;
    Terminal=false
    EOF
    
    # Systemd service files
    mkdir -p $out/lib/systemd/system
    
    cat > $out/lib/systemd/system/nixos-gui.service <<EOF
    [Unit]
    Description=NixOS GUI - Web-based system management interface
    After=network.target
    
    [Service]
    Type=simple
    Environment="NODE_ENV=production"
    ExecStart=$out/bin/nixos-gui
    Restart=on-failure
    RestartSec=10
    User=nixos-gui
    Group=nixos-gui
    
    # Security
    NoNewPrivileges=true
    PrivateTmp=true
    ProtectSystem=strict
    ProtectHome=read-only
    ReadWritePaths=/etc/nixos /var/lib/nixos-gui
    
    [Install]
    WantedBy=multi-user.target
    EOF
    
    cat > $out/lib/systemd/system/nixos-gui-helper.service <<EOF
    [Unit]
    Description=NixOS GUI Helper - Privileged operations handler
    After=network.target
    
    [Service]
    Type=simple
    ExecStart=$out/libexec/nixos-gui-helper
    Restart=on-failure
    RestartSec=10
    User=root
    Group=root
    
    # Security
    NoNewPrivileges=true
    PrivateTmp=true
    ProtectSystem=strict
    ProtectHome=true
    ReadWritePaths=/etc/nixos /nix/var
    
    [Install]
    WantedBy=multi-user.target
    EOF
    
    # Polkit rules
    mkdir -p $out/share/polkit-1/rules.d
    cat > $out/share/polkit-1/rules.d/nixos-gui.rules <<EOF
    polkit.addRule(function(action, subject) {
      if (action.id.indexOf("org.nixos.gui.") === 0) {
        if (subject.isInGroup("wheel") || subject.isInGroup("nixos-gui")) {
          return polkit.Result.YES;
        }
      }
    });
    EOF
    
    # Documentation
    mkdir -p $out/share/doc/nixos-gui
    cp README.md $out/share/doc/nixos-gui/
    cp LICENSE $out/share/doc/nixos-gui/
  '';
  
  meta = with lib; {
    description = "Web-based graphical interface for NixOS system management";
    longDescription = ''
      NixOS GUI provides an intuitive web interface for managing NixOS systems.
      Features include package management, service configuration, system updates,
      and generation management. Designed with security and ease of use in mind.
    '';
    homepage = "https://github.com/nixos/nixos-gui";
    license = licenses.mit;
    maintainers = with maintainers; [ ];
    platforms = platforms.linux;
    mainProgram = "nixos-gui";
  };
}