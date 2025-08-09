#!/usr/bin/env python3
"""
from typing import List
Polish error messages for v1.0 - Make them educational and helpful
"""

import os
import re
from pathlib import Path

# Educational error message templates
EDUCATIONAL_TEMPLATES = {
    # Package not found errors
    "PACKAGE_NOT_FOUND": {
        "message": "I couldn't find the package '{package}' in the NixOS repositories.",
        "education": """
🎓 **Understanding NixOS Packages**

NixOS packages are stored in channels (repositories). Sometimes a package:
- Has a different name than expected (e.g., 'neovim' instead of 'nvim')
- Is in a different channel (unstable vs stable)
- Requires special attributes (e.g., 'python3Packages.numpy')
""",
        "suggestions": [
            "Search for similar packages: `nix search nixpkgs {query}`",
            "Check the exact name at: https://search.nixos.org",
            "Try variations: '{package}', '{package}-bin', '{package}Packages'",
            "For Python packages: `python3Packages.{package}`",
            "For Node packages: `nodePackages.{package}`"
        ],
        "next_steps": "Would you like me to search for packages similar to '{package}'?"
    },
    
    # Permission denied errors
    "PERMISSION_ERROR": {
        "message": "This operation requires administrator privileges.",
        "education": """
🎓 **Understanding NixOS Permissions**

NixOS has two types of operations:
1. **User operations** - Install packages for your user only
2. **System operations** - Modify the system configuration

System operations need 'sudo' because they affect all users.
""",
        "suggestions": [
            "For system-wide changes: Add 'sudo' before the command",
            "For user-only installation: Use `nix profile install` instead",
            "Check if you're in the 'wheel' group for sudo access",
            "Consider using Home Manager for user-specific configs"
        ],
        "next_steps": "Should I show you both user and system installation methods?"
    },
    
    # Network errors
    "NETWORK_ERROR": {
        "message": "I'm having trouble connecting to the NixOS package servers.",
        "education": """
🎓 **How NixOS Downloads Packages**

NixOS fetches packages from binary caches:
- Main cache: cache.nixos.org
- Community cache: cachix.org
- Your network needs to reach these servers
""",
        "suggestions": [
            "Check your internet connection: `ping 8.8.8.8`",
            "Test NixOS cache: `curl -I https://cache.nixos.org`",
            "Try again - could be temporary",
            "Check proxy settings if behind a firewall",
            "Use `--offline` for already-downloaded packages"
        ],
        "next_steps": "Would you like me to help diagnose your network connection?"
    },
    
    # Configuration syntax errors
    "CONFIG_SYNTAX_ERROR": {
        "message": "There's a syntax error in your NixOS configuration.",
        "education": """
🎓 **NixOS Configuration Language**

NixOS uses the Nix language, which is:
- **Functional** - Everything is an expression
- **Pure** - No side effects
- **Lazy** - Only evaluates what's needed

Common syntax rules:
- Statements end with `;`
- Lists use `[ ]`
- Sets (objects) use `{ }`
- Strings can use `"` or `''`
""",
        "suggestions": [
            "Check for missing semicolons (;)",
            "Ensure all brackets match: { }, [ ], ( )",
            "Verify string quotes are closed",
            "Use `nixos-rebuild test` to validate",
            "Try `nix-instantiate --parse` to check syntax"
        ],
        "next_steps": "Would you like me to help identify the syntax issue?"
    },
    
    # Disk space errors
    "DISK_SPACE_ERROR": {
        "message": "Not enough disk space to complete this operation.",
        "education": """
🎓 **NixOS Storage Management**

NixOS keeps all package versions in /nix/store:
- Old versions are kept for rollbacks
- This provides safety but uses disk space
- Garbage collection removes unused packages
""",
        "suggestions": [
            "Free space: `sudo nix-collect-garbage -d`",
            "Check disk usage: `df -h`",
            "See Nix store size: `du -sh /nix/store`",
            "Remove old generations: `sudo nix-collect-garbage --delete-older-than 7d`",
            "Consider moving /nix to a larger partition"
        ],
        "next_steps": "Would you like me to help you free up disk space safely?"
    },
    
    # Channel errors
    "CHANNEL_ERROR": {
        "message": "There's an issue with your NixOS channels.",
        "education": """
🎓 **Understanding NixOS Channels**

Channels are like package repositories:
- **stable** - Well-tested, updated ~6 months
- **unstable** - Latest packages, updated daily
- You can mix channels for flexibility
""",
        "suggestions": [
            "Update channels: `sudo nix-channel --update`",
            "List channels: `sudo nix-channel --list`",
            "Add nixos-unstable: `sudo nix-channel --add https://nixos.org/channels/nixos-unstable`",
            "Check channel status: `nix-channel --list`",
            "Rebuild after channel changes: `sudo nixos-rebuild switch`"
        ],
        "next_steps": "Should I help you manage your channels?"
    },
    
    # Build errors
    "BUILD_ERROR": {
        "message": "The package failed to build from source.",
        "education": """
🎓 **NixOS Build System**

Sometimes NixOS builds packages from source when:
- No binary cache is available
- You've modified the package
- You're using an overlay

This requires development tools and can take time.
""",
        "suggestions": [
            "Check if a binary is available: `nix-env -qa {package}`",
            "Look for build logs: `nix log {derivation}`",
            "Try a different version or channel",
            "Ensure build dependencies are available",
            "Consider using a binary cache: cachix"
        ],
        "next_steps": "Would you like to see the detailed build error?"
    },
    
    # Service errors
    "SERVICE_ERROR": {
        "message": "The service '{service}' encountered an error.",
        "education": """
🎓 **NixOS Services**

Services in NixOS are:
- Defined declaratively in configuration.nix
- Managed by systemd
- Can have complex dependencies

Service states: active, failed, inactive
""",
        "suggestions": [
            "Check service status: `systemctl status {service}`",
            "View service logs: `journalctl -u {service} -e`",
            "Restart service: `sudo systemctl restart {service}`",
            "Check configuration: `nixos-option services.{service}`",
            "Validate config: `sudo nixos-rebuild test`"
        ],
        "next_steps": "Would you like me to help diagnose the service issue?"
    }
}

def enhance_error_handler():
    """Enhance the error handler with educational messages"""
    error_handler_path = Path("backend/core/error_handler.py")
    
    # Read the current file
    with open(error_handler_path, 'r') as f:
        content = f.read()
    
    # Find the _get_user_friendly_info method
    method_start = content.find("def _get_user_friendly_info")
    if method_start == -1:
        print("❌ Could not find _get_user_friendly_info method")
        return
    
    # Create enhanced version
    enhanced_method = '''    def _get_user_friendly_info(self, exception: Exception, category: ErrorCategory) -> tuple[str, List[str]]:
        """
        Get user-friendly error message and suggestions
        Enhanced with educational content for v1.0
        """
        error_str = str(exception).lower()
        
        # Check for specific error patterns
        if category == ErrorCategory.NIXOS:
            if "not found" in error_str or "attribute" in error_str:
                # Extract package name if possible
                package_match = re.search(r"attribute ['\"]?(\\w+)['\"]?", str(exception))
                package = package_match.group(1) if package_match else "the package"
                
                template = EDUCATIONAL_TEMPLATES["PACKAGE_NOT_FOUND"]
                return (
                    template["message"].format(package=package),
                    template["suggestions"] + ["\\n🎓 " + template["education"]]
                )
            elif "hash mismatch" in error_str:
                return (
                    "Package integrity check failed. This usually means the package definition changed.",
                    [
                        "Update your channels: sudo nix-channel --update",
                        "Try again - this is often temporary",
                        "Clear cache if persistent: nix-collect-garbage",
                        "\\n🎓 NixOS verifies all packages with cryptographic hashes for security"
                    ]
                )
                
        elif category == ErrorCategory.PERMISSION:
            template = EDUCATIONAL_TEMPLATES["PERMISSION_ERROR"]
            return (
                template["message"],
                template["suggestions"] + ["\\n🎓 " + template["education"]]
            )
            
        elif category == ErrorCategory.NETWORK:
            template = EDUCATIONAL_TEMPLATES["NETWORK_ERROR"]
            return (
                template["message"],
                template["suggestions"] + ["\\n🎓 " + template["education"]]
            )
            
        elif category == ErrorCategory.SYSTEM:
            if "no space left" in error_str or "disk full" in error_str:
                template = EDUCATIONAL_TEMPLATES["DISK_SPACE_ERROR"]
                return (
                    template["message"],
                    template["suggestions"] + ["\\n🎓 " + template["education"]]
                )
                
        elif category == ErrorCategory.CONFIGURATION:
            if "syntax" in error_str or "parse" in error_str:
                template = EDUCATIONAL_TEMPLATES["CONFIG_SYNTAX_ERROR"]
                return (
                    template["message"],
                    template["suggestions"] + ["\\n🎓 " + template["education"]]
                )
        
        # Check pattern matching for any category
        for pattern, info in self.NIXOS_ERROR_PATTERNS.items():
            if re.search(pattern, error_str, re.IGNORECASE):
                # Add educational note to suggestions
                enhanced_suggestions = info['suggestions'].copy()
                if info['category'] == ErrorCategory.NIXOS:
                    enhanced_suggestions.append("\\n🎓 Learn more at: https://nixos.org/manual/")
                return info['user_message'], enhanced_suggestions
                
        # Default messages with educational hints
        default_messages = {
            ErrorCategory.SECURITY: (
                "Security check failed for safety reasons", 
                ["Verify the source is trusted", "Check for typos in commands", "\\n🎓 NixOS prioritizes security"]
            ),
            ErrorCategory.VALIDATION: (
                "The input doesn't match what I expected",
                ["Check the command format", "Use 'help' to see examples", "\\n🎓 Proper syntax helps me help you better"]
            ),
            ErrorCategory.USER: (
                "I couldn't understand that request",
                ["Try rephrasing more simply", "Use 'help' for examples", "\\n🎓 I'm still learning natural language"]
            ),
            ErrorCategory.INTERNAL: (
                "Something went wrong on my end",
                ["Try again in a moment", "Report this if it persists", "\\n🎓 Even AI assistants have hiccups sometimes"]
            )
        }
        
        return default_messages.get(
            category, 
            ("An unexpected error occurred", ["Try again or ask for help", "\\n🎓 Learning from errors makes us better"])
        )'''
    
    # Add the educational templates as a class variable
    class_start = content.find("class ErrorHandler:")
    if class_start == -1:
        print("❌ Could not find ErrorHandler class")
        return
        
    # Insert educational templates
    insert_pos = content.find("NIXOS_ERROR_PATTERNS = {", class_start)
    if insert_pos == -1:
        print("❌ Could not find NIXOS_ERROR_PATTERNS")
        return
    
    # Add import for re if not present
    if "import re" not in content:
        import_pos = content.find("from typing import")
        content = content[:import_pos] + "import re\n" + content[import_pos:]
    
    # Replace the method
    method_end = content.find("\n    def ", method_start + 1)
    if method_end == -1:
        method_end = len(content)
    
    # Get current method
    current_method = content[method_start:method_end]
    
    # Check if already enhanced
    if "EDUCATIONAL_TEMPLATES" in current_method:
        print("✅ Error handler already enhanced")
        return
    
    # Create the full enhanced content
    enhanced_content = content[:method_start] + enhanced_method + content[method_end:]
    
    # Write back
    with open(error_handler_path, 'w') as f:
        f.write(enhanced_content)
    
    print("✅ Enhanced error handler with educational messages")

def add_educational_templates():
    """Add educational templates to error handler module"""
    error_handler_path = Path("backend/core/error_handler.py")
    
    with open(error_handler_path, 'r') as f:
        content = f.read()
    
    # Add after imports
    import_end = content.rfind("logger = logging.getLogger(__name__)")
    if import_end == -1:
        print("❌ Could not find logger initialization")
        return
    
    # Create templates string
    templates_str = f"\n\n# Educational error message templates for v1.0\nEDUCATIONAL_TEMPLATES = {str(EDUCATIONAL_TEMPLATES)}\n\n"
    
    # Insert after logger
    insert_pos = content.find("\n", import_end) + 1
    enhanced_content = content[:insert_pos] + templates_str + content[insert_pos:]
    
    # Write back
    with open(error_handler_path, 'w') as f:
        f.write(enhanced_content)
    
    print("✅ Added educational templates to error handler")

def main():
    """Main function to polish error messages"""
    print("🎨 Polishing error messages for v1.0...")
    print("=" * 60)
    
    # First add templates
    add_educational_templates()
    
    # Then enhance the method
    enhance_error_handler()
    
    print("\n✅ Error messages polished!")
    print("\nEnhancements:")
    print("- Educational explanations for common errors")
    print("- Step-by-step recovery suggestions")
    print("- Links to documentation where relevant")
    print("- Friendly, encouraging tone")
    print("- Context-aware help offers")

if __name__ == "__main__":
    main()