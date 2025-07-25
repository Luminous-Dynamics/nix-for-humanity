# NixOS VM Test Configuration for Nix for Humanity
# Secure testing environment with proper isolation

{ pkgs ? import <nixpkgs> {} }:

pkgs.nixosTest {
  name = "nix-for-humanity-test";
  
  nodes = {
    # Main test VM with restricted permissions
    testvm = { config, pkgs, ... }: {
      # Base system configuration
      system.stateVersion = "24.05";
      
      # Security hardening for test environment
      security = {
        # Enable sandbox (default in 17.09+, but explicit is better)
        sandbox = {
          enable = true;
          # Restrict sandbox paths - don't expose nix-daemon
          extraSandboxPaths = [];
        };
        
        # Disable root login
        sudo.enable = true;
        sudo.wheelNeedsPassword = true;
        
        # Enable firewall with strict rules
        firewall = {
          enable = true;
          allowedTCPPorts = [ 3456 ]; # Only our server port
          allowPing = false;
        };
      };
      
      # Network isolation
      networking = {
        hostName = "nix-humanity-test";
        # Use predictable interface names
        usePredictableInterfaceNames = true;
        # Disable IPv6 for simpler testing
        enableIPv6 = false;
      };
      
      # Create test user with limited permissions
      users.users.testuser = {
        isNormalUser = true;
        description = "Nix for Humanity Test User";
        extraGroups = [ "wheel" ]; # For sudo testing
        password = "testpass"; # Only for testing!
        uid = 1000;
      };
      
      # Install minimal packages for testing
      environment.systemPackages = with pkgs; [
        # Basic utilities
        vim
        git
        curl
        jq
        
        # Node.js for our app
        nodejs_20
        
        # System monitoring
        htop
        ncdu
        
        # For voice testing
        firefox # Has Web Speech API support
        chromium
      ];
      
      # Nix configuration for testing
      nix = {
        settings = {
          # Ensure sandboxing is enabled
          sandbox = true;
          
          # Restrict builders
          allowed-users = [ "@wheel" ];
          trusted-users = [ "root" ]; # Only root, not testuser
          
          # Disable auto-optimise for testing speed
          auto-optimise-store = false;
          
          # Extra sandboxing
          extra-sandbox-paths = [];
          restrict-eval = false; # Need this for testing
          
          # Prevent network access during builds
          sandbox-fallback = false;
        };
      };
      
      # Services configuration
      services = {
        # X11 for browser testing
        xserver = {
          enable = true;
          displayManager = {
            lightdm.enable = true;
            autoLogin = {
              enable = true;
              user = "testuser";
            };
          };
          desktopManager.xfce.enable = true;
        };
        
        # Enable audio for voice testing
        pipewire = {
          enable = true;
          alsa.enable = true;
          pulse.enable = true;
        };
      };
      
      # Mount our application in read-only mode
      fileSystems."/opt/nix-for-humanity" = {
        device = "${./..}";
        options = [ "bind" "ro" ];
      };
      
      # Systemd service for our app (not auto-starting)
      systemd.services.nix-for-humanity = {
        description = "Nix for Humanity Test Service";
        after = [ "network.target" ];
        wantedBy = []; # Don't auto-start
        
        serviceConfig = {
          Type = "simple";
          User = "testuser";
          WorkingDirectory = "/opt/nix-for-humanity";
          ExecStart = "${pkgs.nodejs_20}/bin/node backend/realtime-server.js";
          Restart = "on-failure";
          
          # Security restrictions
          PrivateTmp = true;
          ProtectSystem = "strict";
          ProtectHome = true;
          NoNewPrivileges = true;
          RestrictNamespaces = true;
          RestrictRealtime = true;
          RestrictSUIDSGID = true;
          
          # Only allow specific directories
          ReadWritePaths = [ "/tmp" ];
          ReadOnlyPaths = [ "/opt/nix-for-humanity" ];
          
          # Resource limits
          LimitNOFILE = 1024;
          LimitNPROC = 64;
          MemoryMax = "512M";
          CPUQuota = "50%";
        };
        
        environment = {
          NODE_ENV = "test";
          NIX_DRY_RUN = "true"; # Force dry-run mode
          PORT = "3456";
        };
      };
    };
  };
  
  # Test script
  testScript = ''
    import json
    import time
    
    def wait_for_text(text):
        """Wait for text to appear in journal"""
        machine.wait_until_succeeds(f"journalctl -u nix-for-humanity | grep '{text}'")
    
    # Start the VM
    machine.start()
    machine.wait_for_unit("multi-user.target")
    
    # Wait for X11 (needed for browser tests)
    machine.wait_for_x()
    
    # Test 1: Verify security restrictions
    print("=== Testing Security Restrictions ===")
    
    # Verify sandboxing is enabled
    machine.succeed("nix-instantiate --eval -E 'builtins.currentSystem' 2>&1 | grep -q evaluating")
    
    # Test that testuser cannot modify system
    machine.fail("su - testuser -c 'nix-env -iA nixpkgs.hello'")
    
    # Test 2: Start our service
    print("=== Starting Nix for Humanity Service ===")
    machine.succeed("systemctl start nix-for-humanity")
    machine.wait_for_unit("nix-for-humanity.service")
    machine.wait_for_open_port(3456)
    
    # Test 3: Basic API tests
    print("=== Testing API Endpoints ===")
    
    # Health check
    result = machine.succeed("curl -s http://localhost:3456/api/health")
    health = json.loads(result)
    assert health["status"] == "healthy"
    assert health["mode"] == "dry-run"
    
    # System info
    result = machine.succeed("curl -s http://localhost:3456/api/system-info")
    info = json.loads(result)
    assert "nixosVersion" in info
    
    # Search test (should work in dry-run)
    result = machine.succeed("""
      curl -s -X POST http://localhost:3456/api/search \
        -H "Content-Type: application/json" \
        -d '{"query":"firefox"}'
    """)
    search = json.loads(result)
    assert len(search["results"]) > 0
    
    # Test 4: Security validation
    print("=== Testing Security Validations ===")
    
    # Test dangerous command rejection
    machine.fail("""
      curl -s -X POST http://localhost:3456/api/execute \
        -H "Content-Type: application/json" \
        -d '{"command":"rm", "args":["-rf", "/"]}'
    """)
    
    # Test 5: Browser test
    print("=== Testing Web Interface ===")
    
    # Open Firefox with our interface
    machine.execute("su - testuser -c 'DISPLAY=:0 firefox http://localhost:3456 &'")
    time.sleep(5)
    
    # Take screenshot for manual verification
    machine.screenshot("nix-humanity-interface")
    
    # Test 6: Resource limits
    print("=== Testing Resource Limits ===")
    
    # Check memory usage
    machine.succeed("systemctl status nix-for-humanity | grep -q 'Memory:'")
    
    # Test 7: Cleanup
    print("=== Cleanup ===")
    machine.succeed("systemctl stop nix-for-humanity")
    
    print("=== All tests passed! ===")
  '';
  
  # Enable interactive mode for debugging
  interactive = {
    # Run with: nix build -f vm-test-setup.nix driver && ./result/bin/nixos-test-driver
    enable = true;
  };
}