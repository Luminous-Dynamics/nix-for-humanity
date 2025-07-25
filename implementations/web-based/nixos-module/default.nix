{ config, lib, pkgs, ... }:

with lib;

let
  cfg = config.services.nixos-gui;
  
  nixos-gui = pkgs.callPackage ./package.nix { };
  
  # Configuration file for the GUI
  configFile = pkgs.writeText "nixos-gui-config.json" (builtins.toJSON {
    port = cfg.port;
    host = cfg.host;
    ssl = cfg.ssl.enable;
    wsPort = cfg.wsPort;
    logLevel = cfg.logLevel;
    allowedGroups = cfg.allowedGroups;
    features = cfg.features;
  });
  
  # Systemd service file
  nixos-gui-service = pkgs.writeText "nixos-gui.service" ''
    [Unit]
    Description=NixOS GUI - Web-based system management interface
    After=network.target
    
    [Service]
    Type=simple
    User=${cfg.user}
    Group=${cfg.group}
    WorkingDirectory=${nixos-gui}
    Environment="NODE_ENV=production"
    Environment="CONFIG_FILE=${configFile}"
    ExecStart=${pkgs.nodejs}/bin/node ${nixos-gui}/backend/server.js
    Restart=on-failure
    RestartSec=10
    
    # Security hardening
    NoNewPrivileges=true
    PrivateTmp=true
    ProtectSystem=strict
    ProtectHome=read-only
    ReadWritePaths=/etc/nixos
    
    [Install]
    WantedBy=multi-user.target
  '';
  
  # Helper service for privileged operations
  nixos-gui-helper-service = pkgs.writeText "nixos-gui-helper.service" ''
    [Unit]
    Description=NixOS GUI Helper - Privileged operations handler
    After=network.target
    
    [Service]
    Type=simple
    User=root
    Group=root
    WorkingDirectory=${nixos-gui}
    ExecStart=${nixos-gui}/backend/nixos-gui-helper
    Restart=on-failure
    RestartSec=10
    
    # Security hardening
    NoNewPrivileges=true
    PrivateTmp=true
    ProtectSystem=strict
    ProtectHome=true
    
    [Install]
    WantedBy=multi-user.target
  '';

in {
  options.services.nixos-gui = {
    enable = mkEnableOption "NixOS GUI - Web-based system management interface";
    
    package = mkOption {
      type = types.package;
      default = nixos-gui;
      defaultText = literalExpression "pkgs.nixos-gui";
      description = "The NixOS GUI package to use.";
    };
    
    user = mkOption {
      type = types.str;
      default = "nixos-gui";
      description = "User account under which NixOS GUI runs.";
    };
    
    group = mkOption {
      type = types.str;
      default = "nixos-gui";
      description = "Group under which NixOS GUI runs.";
    };
    
    host = mkOption {
      type = types.str;
      default = "127.0.0.1";
      description = "Host address to bind to.";
    };
    
    port = mkOption {
      type = types.port;
      default = 8080;
      description = "Port for the web interface.";
    };
    
    wsPort = mkOption {
      type = types.port;
      default = 8081;
      description = "Port for WebSocket connections.";
    };
    
    ssl = {
      enable = mkOption {
        type = types.bool;
        default = false;
        description = "Enable SSL/TLS.";
      };
      
      cert = mkOption {
        type = types.nullOr types.path;
        default = null;
        description = "Path to SSL certificate file.";
      };
      
      key = mkOption {
        type = types.nullOr types.path;
        default = null;
        description = "Path to SSL key file.";
      };
    };
    
    allowedGroups = mkOption {
      type = types.listOf types.str;
      default = [ "wheel" "nixos-gui" ];
      description = "Groups allowed to access NixOS GUI.";
    };
    
    logLevel = mkOption {
      type = types.enum [ "error" "warn" "info" "debug" ];
      default = "info";
      description = "Logging level.";
    };
    
    features = {
      packageManagement = mkOption {
        type = types.bool;
        default = true;
        description = "Enable package management features.";
      };
      
      serviceManagement = mkOption {
        type = types.bool;
        default = true;
        description = "Enable service management features.";
      };
      
      configurationEdit = mkOption {
        type = types.bool;
        default = true;
        description = "Enable configuration editing features.";
      };
      
      systemRebuild = mkOption {
        type = types.bool;
        default = true;
        description = "Enable system rebuild features.";
      };
      
      generationManagement = mkOption {
        type = types.bool;
        default = true;
        description = "Enable generation management features.";
      };
      
      auditLogging = mkOption {
        type = types.bool;
        default = true;
        description = "Enable audit logging.";
      };
    };
    
    openFirewall = mkOption {
      type = types.bool;
      default = false;
      description = "Open firewall ports for NixOS GUI.";
    };
    
    nginx = {
      enable = mkOption {
        type = types.bool;
        default = false;
        description = "Configure nginx reverse proxy for NixOS GUI.";
      };
      
      virtualHost = mkOption {
        type = types.str;
        default = "nixos-gui.local";
        description = "Virtual host name for nginx.";
      };
    };
  };
  
  config = mkIf cfg.enable {
    # Create user and group
    users.users = optionalAttrs (cfg.user == "nixos-gui") {
      nixos-gui = {
        isSystemUser = true;
        group = cfg.group;
        description = "NixOS GUI service user";
        home = "/var/lib/nixos-gui";
        createHome = true;
      };
    };
    
    users.groups = optionalAttrs (cfg.group == "nixos-gui") {
      nixos-gui = { };
    };
    
    # Ensure the user is in required groups
    users.users.${cfg.user}.extraGroups = [ "systemd-journal" ];
    
    # Install the package
    environment.systemPackages = [ cfg.package ];
    
    # Create systemd services
    systemd.services.nixos-gui = {
      description = "NixOS GUI - Web-based system management interface";
      after = [ "network.target" ];
      wantedBy = [ "multi-user.target" ];
      
      serviceConfig = {
        Type = "simple";
        User = cfg.user;
        Group = cfg.group;
        WorkingDirectory = "${cfg.package}/share/nixos-gui";
        ExecStart = "${pkgs.nodejs}/bin/node ${cfg.package}/share/nixos-gui/backend/server.js";
        Restart = "on-failure";
        RestartSec = 10;
        
        # Environment
        Environment = [
          "NODE_ENV=production"
          "CONFIG_FILE=${configFile}"
          "PORT=${toString cfg.port}"
          "WS_PORT=${toString cfg.wsPort}"
        ];
        
        # Security hardening
        NoNewPrivileges = true;
        PrivateTmp = true;
        ProtectSystem = "strict";
        ProtectHome = "read-only";
        ReadWritePaths = [ "/etc/nixos" "/var/lib/nixos-gui" ];
        
        # Capabilities for binding to ports < 1024 if needed
        AmbientCapabilities = mkIf (cfg.port < 1024) [ "CAP_NET_BIND_SERVICE" ];
      };
    };
    
    systemd.services.nixos-gui-helper = {
      description = "NixOS GUI Helper - Privileged operations handler";
      after = [ "network.target" ];
      wantedBy = [ "multi-user.target" ];
      
      serviceConfig = {
        Type = "simple";
        User = "root";
        Group = "root";
        ExecStart = "${cfg.package}/libexec/nixos-gui-helper";
        Restart = "on-failure";
        RestartSec = 10;
        
        # Security hardening
        NoNewPrivileges = true;
        PrivateTmp = true;
        ProtectSystem = "strict";
        ProtectHome = true;
        ReadWritePaths = [ "/etc/nixos" "/nix/var" ];
      };
    };
    
    # Configure polkit rules
    security.polkit.extraConfig = ''
      polkit.addRule(function(action, subject) {
        if (action.id.indexOf("org.nixos.gui.") === 0) {
          var allowedGroups = ${builtins.toJSON cfg.allowedGroups};
          for (var i = 0; i < allowedGroups.length; i++) {
            if (subject.isInGroup(allowedGroups[i])) {
              return polkit.Result.YES;
            }
          }
        }
      });
    '';
    
    # Open firewall ports if requested
    networking.firewall = mkIf cfg.openFirewall {
      allowedTCPPorts = [ cfg.port cfg.wsPort ];
    };
    
    # Configure nginx if requested
    services.nginx = mkIf cfg.nginx.enable {
      enable = true;
      virtualHosts.${cfg.nginx.virtualHost} = {
        locations."/" = {
          proxyPass = "http://${cfg.host}:${toString cfg.port}";
          proxyWebsockets = true;
          extraConfig = ''
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            
            # Timeouts for long operations
            proxy_read_timeout 300s;
            proxy_send_timeout 300s;
          '';
        };
        
        locations."/ws" = {
          proxyPass = "http://${cfg.host}:${toString cfg.wsPort}";
          proxyWebsockets = true;
        };
      };
    };
    
    # Create state directory
    systemd.tmpfiles.rules = [
      "d /var/lib/nixos-gui 0750 ${cfg.user} ${cfg.group} -"
      "d /var/lib/nixos-gui/logs 0750 ${cfg.user} ${cfg.group} -"
      "d /var/lib/nixos-gui/data 0750 ${cfg.user} ${cfg.group} -"
    ];
  };
}