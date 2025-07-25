{ config, lib, pkgs, ... }:

with lib;

let
  cfg = config.services.nixos-gui;
  
  # Package definition
  nixos-gui = pkgs.stdenv.mkDerivation rec {
    pname = "nixos-gui";
    version = "0.1.0";
    
    src = ./.;
    
    buildInputs = with pkgs; [
      nodejs_20
      nodePackages.npm
    ];
    
    installPhase = ''
      mkdir -p $out/{bin,lib/nixos-gui,share/nixos-gui}
      
      # Copy backend and frontend
      cp -r backend $out/lib/nixos-gui/
      cp -r frontend $out/share/nixos-gui/
      cp package.json $out/lib/nixos-gui/
      
      # Install dependencies
      cd $out/lib/nixos-gui
      npm install --production
      
      # Create wrapper script
      cat > $out/bin/nixos-gui-server << EOF
      #!${pkgs.bash}/bin/bash
      export NODE_ENV=production
      export NIXOS_GUI_ROOT=$out
      cd $out/lib/nixos-gui
      exec ${pkgs.nodejs_20}/bin/node backend/src/secure-server.js "\$@"
      EOF
      
      chmod +x $out/bin/nixos-gui-server
    '';
  };
  
  # Configuration file template
  configFile = pkgs.writeText "nixos-gui.env" ''
    NODE_ENV=production
    HTTP_PORT=${toString cfg.httpPort}
    HTTPS_PORT=${toString cfg.httpsPort}
    HOST=${cfg.host}
    JWT_SECRET=${cfg.jwtSecret}
    SESSION_SECRET=${cfg.sessionSecret}
    SSL_CERT=${cfg.ssl.certFile}
    SSL_KEY=${cfg.ssl.keyFile}
    DB_PATH=${cfg.dataDir}/db.sqlite
    CACHE_ENABLED=${if cfg.cache.enable then "true" else "false"}
    ${optionalString (cfg.cache.redis != null) "REDIS_URL=${cfg.cache.redis}"}
  '';
in
{
  ###### Interface
  
  options.services.nixos-gui = {
    enable = mkEnableOption "NixOS GUI - Consciousness-First Configuration Interface";
    
    package = mkOption {
      type = types.package;
      default = nixos-gui;
      defaultText = literalExpression "nixos-gui";
      description = "The NixOS GUI package to use";
    };
    
    user = mkOption {
      type = types.str;
      default = "nixos-gui";
      description = "User account under which nixos-gui runs";
    };
    
    group = mkOption {
      type = types.str;
      default = "nixos-gui";
      description = "Group under which nixos-gui runs";
    };
    
    dataDir = mkOption {
      type = types.path;
      default = "/var/lib/nixos-gui";
      description = "Directory for storing application data";
    };
    
    httpPort = mkOption {
      type = types.port;
      default = 8080;
      description = "HTTP port (redirects to HTTPS)";
    };
    
    httpsPort = mkOption {
      type = types.port;
      default = 8443;
      description = "HTTPS port for secure connections";
    };
    
    host = mkOption {
      type = types.str;
      default = "localhost";
      description = "Hostname to bind to";
    };
    
    openFirewall = mkOption {
      type = types.bool;
      default = false;
      description = "Whether to open firewall ports";
    };
    
    ssl = {
      enable = mkOption {
        type = types.bool;
        default = true;
        description = "Enable HTTPS";
      };
      
      certFile = mkOption {
        type = types.path;
        example = "/var/lib/acme/nixos-gui.example.com/cert.pem";
        description = "Path to SSL certificate file";
      };
      
      keyFile = mkOption {
        type = types.path;
        example = "/var/lib/acme/nixos-gui.example.com/key.pem";
        description = "Path to SSL private key file";
      };
      
      autoGenerate = mkOption {
        type = types.bool;
        default = true;
        description = "Auto-generate self-signed certificates if files don't exist";
      };
    };
    
    authentication = {
      enable = mkOption {
        type = types.bool;
        default = true;
        description = "Enable authentication";
      };
      
      initialAdminPassword = mkOption {
        type = types.str;
        default = "changeme";
        description = "Initial admin password (change on first login)";
      };
      
      allowedGroups = mkOption {
        type = types.listOf types.str;
        default = [ "wheel" ];
        description = "System groups allowed to access the GUI";
      };
    };
    
    cache = {
      enable = mkOption {
        type = types.bool;
        default = true;
        description = "Enable caching for better performance";
      };
      
      redis = mkOption {
        type = types.nullOr types.str;
        default = null;
        example = "redis://localhost:6379";
        description = "Redis URL for distributed caching (optional)";
      };
    };
    
    jwtSecret = mkOption {
      type = types.str;
      description = "JWT secret for token signing (generate with: openssl rand -hex 64)";
    };
    
    sessionSecret = mkOption {
      type = types.str;
      description = "Session secret (generate with: openssl rand -hex 64)";
    };
    
    features = {
      aiAssistant = mkOption {
        type = types.bool;
        default = true;
        description = "Enable AI configuration assistant";
      };
      
      smartSuggestions = mkOption {
        type = types.bool;
        default = true;
        description = "Enable smart package suggestions";
      };
      
      systemMonitoring = mkOption {
        type = types.bool;
        default = true;
        description = "Enable real-time system monitoring";
      };
      
      consciousnessFirst = mkOption {
        type = types.bool;
        default = true;
        description = "Enable consciousness-first UI features";
      };
    };
  };
  
  ###### Implementation
  
  config = mkIf cfg.enable {
    # Create user and group
    users.users.${cfg.user} = {
      isSystemUser = true;
      group = cfg.group;
      description = "NixOS GUI service user";
      home = cfg.dataDir;
      createHome = true;
    };
    
    users.groups.${cfg.group} = {};
    
    # Ensure data directory exists
    systemd.tmpfiles.rules = [
      "d '${cfg.dataDir}' 0750 ${cfg.user} ${cfg.group} - -"
      "d '${cfg.dataDir}/ssl' 0700 ${cfg.user} ${cfg.group} - -"
    ];
    
    # Generate SSL certificates if needed
    systemd.services.nixos-gui-ssl = mkIf (cfg.ssl.enable && cfg.ssl.autoGenerate) {
      description = "Generate SSL certificates for NixOS GUI";
      wantedBy = [ "nixos-gui.service" ];
      before = [ "nixos-gui.service" ];
      serviceConfig = {
        Type = "oneshot";
        User = cfg.user;
        Group = cfg.group;
      };
      script = ''
        if [ ! -f "${cfg.ssl.certFile}" ] || [ ! -f "${cfg.ssl.keyFile}" ]; then
          echo "Generating self-signed SSL certificates..."
          ${pkgs.openssl}/bin/openssl req -x509 \
            -newkey rsa:4096 \
            -keyout ${cfg.dataDir}/ssl/key.pem \
            -out ${cfg.dataDir}/ssl/cert.pem \
            -days 365 \
            -nodes \
            -subj "/C=US/ST=Sacred/L=Digital/O=NixOS-GUI/CN=${cfg.host}"
          
          # Update config to use generated certs
          ln -sf ${cfg.dataDir}/ssl/cert.pem ${cfg.ssl.certFile}
          ln -sf ${cfg.dataDir}/ssl/key.pem ${cfg.ssl.keyFile}
        fi
      '';
    };
    
    # Main service
    systemd.services.nixos-gui = {
      description = "NixOS GUI - Consciousness-First Configuration Interface";
      wantedBy = [ "multi-user.target" ];
      after = [ "network.target" ] 
        ++ optional (cfg.cache.redis != null) "redis.service"
        ++ optional cfg.ssl.autoGenerate "nixos-gui-ssl.service";
      
      environment = {
        NODE_ENV = "production";
        NIXOS_GUI_STATIC = "${cfg.package}/share/nixos-gui";
      };
      
      serviceConfig = {
        Type = "notify";
        ExecStart = "${cfg.package}/bin/nixos-gui-server";
        Restart = "always";
        RestartSec = 10;
        User = cfg.user;
        Group = cfg.group;
        
        # Security hardening
        NoNewPrivileges = true;
        PrivateTmp = true;
        ProtectSystem = "strict";
        ProtectHome = true;
        ReadWritePaths = [ 
          cfg.dataDir 
          "/etc/nixos"  # For configuration management
          "/nix/var"    # For package operations
        ];
        
        # Capabilities for privileged operations
        AmbientCapabilities = [ "CAP_SYS_ADMIN" ];
        CapabilityBoundingSet = [ "CAP_SYS_ADMIN" ];
        
        # Resource limits
        LimitNOFILE = 65536;
        
        # Environment file
        EnvironmentFile = configFile;
      };
      
      preStart = ''
        # Initialize database if needed
        if [ ! -f "${cfg.dataDir}/db.sqlite" ]; then
          echo "Initializing database..."
          # Database initialization would go here
        fi
      '';
    };
    
    # Open firewall if requested
    networking.firewall = mkIf cfg.openFirewall {
      allowedTCPPorts = [ cfg.httpPort cfg.httpsPort ];
    };
    
    # Nginx reverse proxy (optional but recommended)
    services.nginx = mkIf (config.services.nginx.enable) {
      virtualHosts."nixos-gui.${cfg.host}" = {
        forceSSL = cfg.ssl.enable;
        enableACME = false;  # Use our own certs
        sslCertificate = cfg.ssl.certFile;
        sslCertificateKey = cfg.ssl.keyFile;
        
        locations."/" = {
          proxyPass = "http://localhost:${toString cfg.httpPort}";
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
            
            # Timeouts for long-running operations
            proxy_read_timeout 300s;
            proxy_send_timeout 300s;
          '';
        };
      };
    };
    
    # Optional Redis service
    services.redis.servers.nixos-gui = mkIf (cfg.cache.enable && cfg.cache.redis == null) {
      enable = true;
      port = 6380;  # Non-default port to avoid conflicts
      settings = {
        maxmemory = "128mb";
        maxmemory-policy = "allkeys-lru";
      };
    };
  };
}