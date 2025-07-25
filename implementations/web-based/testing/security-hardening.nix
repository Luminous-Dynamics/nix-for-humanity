# Security Hardening Configuration for Nix for Humanity
# Based on 2024/2025 NixOS security best practices

{ config, lib, pkgs, ... }:

{
  # Core security settings
  security = {
    # Sandbox configuration
    sandbox = {
      enable = true;
      # Avoid exposing nix-daemon in sandbox (CVE-2024 risk)
      extraSandboxPaths = lib.mkForce [];
    };
    
    # Polkit rules for our application
    polkit = {
      enable = true;
      extraConfig = ''
        // Allow testuser to query system info only
        polkit.addRule(function(action, subject) {
          if (action.id == "org.freedesktop.systemd1.manage-units" &&
              action.lookup("unit") == "nix-for-humanity.service" &&
              subject.user == "testuser") {
            return polkit.Result.YES;
          }
        });
        
        // Deny all nix-daemon access from containers
        polkit.addRule(function(action, subject) {
          if (action.id.indexOf("org.nixos.nix-daemon") === 0 &&
              subject.user == "testuser") {
            return polkit.Result.NO;
          }
        });
      '';
    };
    
    # AppArmor for additional sandboxing
    apparmor = {
      enable = true;
      packages = [ pkgs.apparmor-profiles ];
    };
    
    # Audit framework
    auditd.enable = true;
    audit = {
      enable = true;
      rules = [
        # Monitor nix-daemon access
        "-w /nix/var/nix/daemon-socket -p rwxa -k nix-daemon-access"
        # Monitor our app
        "-w /opt/nix-for-humanity -p r -k nix-humanity-access"
      ];
    };
  };
  
  # Systemd hardening for our service
  systemd.services.nix-for-humanity = {
    serviceConfig = {
      # User/Group isolation
      DynamicUser = true;
      User = "nix-humanity";
      Group = "nix-humanity";
      
      # Filesystem isolation
      PrivateTmp = true;
      PrivateDevices = true;
      ProtectSystem = "strict";
      ProtectHome = true;
      ProtectKernelTunables = true;
      ProtectKernelModules = true;
      ProtectControlGroups = true;
      ProtectClock = true;
      ProtectHostname = true;
      ProtectKernelLogs = true;
      ProtectProc = "invisible";
      ProcSubset = "pid";
      
      # Namespacing
      PrivateUsers = true;
      PrivateIPC = true;
      RestrictNamespaces = true;
      UMask = "0077";
      
      # Network isolation (if not needed)
      # PrivateNetwork = true;
      RestrictAddressFamilies = [ "AF_INET" "AF_INET6" "AF_UNIX" ];
      IPAddressDeny = "any";
      IPAddressAllow = [ "localhost" "10.0.0.0/8" "172.16.0.0/12" "192.168.0.0/16" ];
      
      # Capability restrictions
      NoNewPrivileges = true;
      RestrictSUIDSGID = true;
      RemoveIPC = true;
      CapabilityBoundingSet = "";
      AmbientCapabilities = "";
      
      # System call filtering
      SystemCallFilter = [
        "@system-service"
        "~@privileged"
        "~@mount"
        "~@reboot"
        "~@swap"
        "~@resources"
        "~@cpu-emulation"
        "~@obsolete"
        "~@debug"
        "~@raw-io"
      ];
      SystemCallArchitectures = "native";
      
      # Execution restrictions
      MemoryDenyWriteExecute = true;
      RestrictRealtime = true;
      LockPersonality = true;
      
      # Resource limits
      LimitNOFILE = 1024;
      LimitNPROC = 64;
      LimitMEMLOCK = 0;
      TasksMax = 16;
      MemoryMax = "256M";
      CPUQuota = "20%";
      
      # Mount restrictions
      MountFlags = "private";
      TemporaryFileSystem = [ "/tmp:size=50M" ];
      BindReadOnlyPaths = [
        "/nix/store"
        "-/etc/resolv.conf"
        "-/etc/hosts"
        "-/etc/localtime"
      ];
      
      # Device access
      DevicePolicy = "closed";
      DeviceAllow = [];
      
      # Security modules
      SELinuxContext = "system_u:system_r:container_t:s0";
      AppArmorProfile = "nix-for-humanity";
      SmackProcessLabel = "nix-for-humanity";
    };
  };
  
  # Container security (if using NixOS containers)
  containers.nix-humanity-test = {
    # Use unprivileged containers
    ephemeral = true;
    privateNetwork = true;
    enableTun = false;
    
    # Restrict capabilities
    additionalCapabilities = [];
    dropCapabilities = [ "ALL" ];
    
    # Resource limits
    allowedDevices = [];
    
    bindMounts = {
      "/opt/nix-for-humanity" = {
        hostPath = "/opt/nix-for-humanity";
        isReadOnly = true;
      };
    };
    
    config = { config, pkgs, ... }: {
      # Minimal container config
      boot.isContainer = true;
      networking.useDHCP = false;
      
      # No root access
      users.users.root.hashedPassword = "!";
      
      # Minimal packages
      environment.systemPackages = [ pkgs.nodejs_20 ];
    };
  };
  
  # Firewall rules
  networking.firewall = {
    enable = true;
    
    # Strict default policy
    rejectPackets = true;
    logRefusedConnections = true;
    logRefusedPackets = true;
    
    # Only allow our service port from localhost
    extraCommands = ''
      # Flush existing rules
      iptables -F nixos-fw
      
      # Default policies
      iptables -P INPUT DROP
      iptables -P FORWARD DROP
      iptables -P OUTPUT ACCEPT
      
      # Allow loopback
      iptables -A nixos-fw -i lo -j ACCEPT
      
      # Allow established connections
      iptables -A nixos-fw -m state --state ESTABLISHED,RELATED -j ACCEPT
      
      # Allow our service only from localhost
      iptables -A nixos-fw -p tcp -s 127.0.0.1 --dport 3456 -j ACCEPT
      
      # Log and drop everything else
      iptables -A nixos-fw -j LOG --log-prefix "nixos-fw-dropped: "
      iptables -A nixos-fw -j DROP
    '';
  };
  
  # Monitoring and alerting
  services.prometheus = {
    enable = true;
    port = 9090;
    
    scrapeConfigs = [
      {
        job_name = "nix-humanity";
        static_configs = [{
          targets = [ "localhost:3456" ];
        }];
      }
    ];
    
    rules = [
      ''
        groups:
        - name: security
          rules:
          - alert: HighMemoryUsage
            expr: process_resident_memory_bytes{job="nix-humanity"} > 268435456
            annotations:
              summary: "Nix for Humanity using too much memory"
          
          - alert: TooManyConnections  
            expr: http_connections{job="nix-humanity"} > 100
            annotations:
              summary: "Possible DoS attack"
      ''
    ];
  };
}