#!/usr/bin/env node

// 🧪 Test Sacred NixOS Commands
// Ensures every command follows the NixOS way

const SacredIntentEngine = require('./services/intent-engine-sacred');

const testCommands = [
  // Package Management
  { input: "install firefox", expected: "nix-env -iA nixpkgs.firefox" },
  { input: "remove firefox", expected: "nix-env -e firefox" },
  { input: "search for text editor", expected: "nix search nixpkgs text editor" },
  { input: "what's installed", expected: "nix-env -q" },
  { input: "tell me about vim", expected: "nix-env -qa --description vim" },
  
  // System Updates
  { input: "update everything", expected: "nixos-rebuild switch --upgrade" },
  { input: "check for updates", expected: "sudo nix-channel --update" },
  { input: "show updates", expected: "sudo nix-channel --update && nix-env -u --dry-run" },
  
  // System Maintenance
  { input: "clean up system", expected: "sudo nix-collect-garbage -d" },
  { input: "optimize store", expected: "nix-store --optimise" },
  
  // Services
  { input: "start nginx", expected: "systemctl start nginx" },
  { input: "stop nginx", expected: "systemctl stop nginx" },
  { input: "restart nginx", expected: "systemctl restart nginx" },
  { input: "nginx status", expected: "systemctl status nginx" },
  { input: "list services", expected: "systemctl list-units --type=service --state=active" },
  
  // Configuration
  { input: "edit config", expected: "sudo nano /etc/nixos/configuration.nix" },
  { input: "rebuild system", expected: "sudo nixos-rebuild switch" },
  { input: "test config", expected: "sudo nixos-rebuild test" },
  
  // System Info
  { input: "system info", expected: "nixos-version && uname -a" },
  { input: "disk usage", expected: "df -h" },
  { input: "memory usage", expected: "free -h" },
  { input: "cpu usage", expected: "top -bn1 | head -20" },
  
  // Network
  { input: "show ip address", expected: "ip addr show" },
  { input: "network status", expected: "ping -c 3 8.8.8.8" },
  { input: "list connections", expected: "ss -tunap" },
  
  // File System
  { input: "where am i", expected: "pwd" },
  { input: "list files", expected: "ls -la" },
  { input: "go to home", expected: "cd ~" },
  { input: "create folder test", expected: "mkdir -p test" },
  
  // User Management
  { input: "who am i", expected: "whoami && groups" },
  { input: "list users", expected: 'cat /etc/passwd | grep "/home" | cut -d: -f1' },
  
  // Power Management
  { input: "reboot", expected: "sudo reboot" },
  { input: "shutdown", expected: "sudo shutdown -h now" },
  { input: "suspend", expected: "systemctl suspend" },
  
  // Time & Date
  { input: "what time", expected: 'date +"%I:%M %p"' },
  { input: "what date", expected: 'date +"%A, %B %d, %Y"' },
  { input: "uptime", expected: "uptime -p" }
];

async function testNixOSCommands() {
  console.log("🧪 Testing Sacred NixOS Commands...\n");
  
  const engine = new SacredIntentEngine();
  let passed = 0;
  let failed = 0;
  
  for (const test of testCommands) {
    const result = await engine.recognize(test.input);
    
    // Extract base command (without parameters)
    const baseCommand = result.command || 'internal:' + result.action;
    
    // For commands with parameters, check if the base matches
    const commandMatches = test.expected.startsWith(baseCommand) || 
                          baseCommand === test.expected;
    
    if (commandMatches && result.confidence > 0.5) {
      console.log(`✅ "${test.input}"`);
      console.log(`   → ${baseCommand}${result.package ? ' ' + result.package : ''}`);
      console.log(`   ✨ ${result.mantra}\n`);
      passed++;
    } else {
      console.log(`❌ "${test.input}"`);
      console.log(`   Expected: ${test.expected}`);
      console.log(`   Got: ${baseCommand} (confidence: ${result.confidence})`);
      if (result.suggestions) {
        console.log(`   💡 Suggestions: ${result.suggestions.join(', ')}`);
      }
      console.log();
      failed++;
    }
  }
  
  console.log("\n📊 Test Results:");
  console.log(`   ✅ Passed: ${passed}`);
  console.log(`   ❌ Failed: ${failed}`);
  console.log(`   📈 Success Rate: ${Math.round(passed / testCommands.length * 100)}%`);
  
  // Test NixOS-specific edge cases
  console.log("\n🔍 Testing NixOS-Specific Edge Cases:");
  
  const edgeCases = [
    { input: "install firefox-esr", desc: "Package variants" },
    { input: "garbage collect keep 7 days", desc: "Time-based cleanup" },
    { input: "rebuild with rollback", desc: "Rollback capability" },
    { input: "show system generations", desc: "Generation management" }
  ];
  
  for (const edge of edgeCases) {
    const result = await engine.recognize(edge.input);
    console.log(`\n🧩 ${edge.desc}: "${edge.input}"`);
    console.log(`   Intent: ${result.action || 'unknown'}`);
    console.log(`   Confidence: ${result.confidence}`);
    if (result.suggestions) {
      console.log(`   Suggestions: ${result.suggestions.join(', ')}`);
    }
  }
  
  console.log("\n✨ Sacred NixOS command testing complete!");
  console.log("🙏 May your commands always honor the declarative way.\n");
}

// Run tests
testNixOSCommands().catch(console.error);