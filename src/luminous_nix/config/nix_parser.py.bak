"""
Nix Configuration Parser using Tree-sitter
Enables safe, intelligent modification of NixOS configurations
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import tree_sitter
from tree_sitter_nix import language as nix_language


@dataclass
class NixNode:
    """Represents a node in the Nix AST"""
    type: str
    text: str
    start_pos: Tuple[int, int]
    end_pos: Tuple[int, int]
    children: List['NixNode']
    parent: Optional['NixNode'] = None
    
    def find_child(self, node_type: str) -> Optional['NixNode']:
        """Find first child of given type"""
        for child in self.children:
            if child.type == node_type:
                return child
        return None
    
    def find_all(self, node_type: str) -> List['NixNode']:
        """Find all descendants of given type"""
        results = []
        if self.type == node_type:
            results.append(self)
        for child in self.children:
            results.extend(child.find_all(node_type))
        return results


class NixConfigParser:
    """
    Safe NixOS configuration parser using Tree-sitter
    
    Features:
    - Parse existing configurations
    - Understand structure and dependencies
    - Make surgical modifications
    - Prevent conflicts
    - Maintain formatting
    """
    
    def __init__(self):
        """Initialize the parser with Nix language"""
        # New API for tree-sitter
        self.parser = tree_sitter.Parser(nix_language())
        self.tree = None
        self.source_code = None
        self.config_path = None
        
    def parse_file(self, config_path: str) -> bool:
        """Parse a Nix configuration file"""
        try:
            self.config_path = Path(config_path)
            self.source_code = self.config_path.read_text()
            
            # Parse with tree-sitter
            tree = self.parser.parse(bytes(self.source_code, "utf8"))
            self.tree = tree
            
            return not tree.root_node.has_error
        except Exception as e:
            print(f"Error parsing {config_path}: {e}")
            return False
    
    def parse_string(self, nix_code: str) -> bool:
        """Parse Nix code from string"""
        try:
            self.source_code = nix_code
            tree = self.parser.parse(bytes(nix_code, "utf8"))
            self.tree = tree
            return not tree.root_node.has_error
        except Exception as e:
            print(f"Error parsing Nix code: {e}")
            return False
    
    def _node_to_dict(self, node) -> NixNode:
        """Convert tree-sitter node to our NixNode"""
        children = [self._node_to_dict(child) for child in node.children]
        
        # Get text for this node
        start_byte = node.start_byte
        end_byte = node.end_byte
        text = self.source_code[start_byte:end_byte] if self.source_code else ""
        
        nix_node = NixNode(
            type=node.type,
            text=text,
            start_pos=(node.start_point[0], node.start_point[1]),
            end_pos=(node.end_point[0], node.end_point[1]),
            children=children
        )
        
        # Set parent references
        for child in nix_node.children:
            child.parent = nix_node
            
        return nix_node
    
    def get_ast(self) -> Optional[NixNode]:
        """Get the abstract syntax tree as NixNode"""
        if not self.tree:
            return None
        return self._node_to_dict(self.tree.root_node)
    
    def find_system_packages(self) -> List[str]:
        """Find all system packages in the configuration"""
        packages = []
        
        if not self.tree:
            return packages
        
        # For now, use a simpler approach without queries
        # Tree-sitter-nix might not have full query support yet
        ast = self.get_ast()
        if ast:
            # Find all nodes that look like package lists
            for node in ast.find_all("list"):
                # Check if this is within systemPackages context
                if "systemPackages" in str(node.text):
                    # Extract package names from the list
                    import re
                    pkg_matches = re.findall(r'\b([a-zA-Z0-9_-]+)\b', node.text)
                    for pkg in pkg_matches:
                        if pkg not in ['with', 'pkgs', 'in', 'let']:
                            packages.append(pkg)
        
        return packages
    
    def find_services(self) -> Dict[str, bool]:
        """Find all services and their enabled status"""
        services = {}
        
        if not self.tree:
            return services
        
        # Look for services.*.enable patterns
        ast = self.get_ast()
        if not ast:
            return services
        
        # Find all service configurations
        for node in ast.find_all("binding"):
            if "services" in node.text and "enable" in node.text:
                # Extract service name and status
                match = re.search(r'services\.(\w+)\.enable\s*=\s*(true|false)', node.text)
                if match:
                    service_name = match.group(1)
                    enabled = match.group(2) == "true"
                    services[service_name] = enabled
        
        return services
    
    def has_package(self, package_name: str) -> bool:
        """Check if a package is already in systemPackages"""
        packages = self.find_system_packages()
        return package_name in packages
    
    def has_service(self, service_name: str) -> bool:
        """Check if a service is already configured"""
        services = self.find_services()
        return service_name in services
    
    def add_package_safely(self, package_name: str) -> Optional[str]:
        """
        Add a package to systemPackages safely
        Returns modified configuration or None if failed
        """
        if not self.source_code:
            return None
        
        # Check if already exists
        if self.has_package(package_name):
            print(f"Package {package_name} already in configuration")
            return self.source_code
        
        # Find systemPackages list
        lines = self.source_code.split('\n')
        modified_lines = []
        in_packages = False
        package_added = False
        
        for i, line in enumerate(lines):
            if 'environment.systemPackages' in line:
                in_packages = True
                modified_lines.append(line)
            elif in_packages and '];' in line and not package_added:
                # Add package before closing bracket
                indent = len(line) - len(line.lstrip())
                if i > 0 and lines[i-1].strip():
                    # Add after last package
                    modified_lines.insert(-1, ' ' * (indent + 2) + package_name)
                package_added = True
                modified_lines.append(line)
                in_packages = False
            else:
                modified_lines.append(line)
        
        return '\n'.join(modified_lines)
    
    def add_service_safely(self, service_name: str, config: Dict[str, Any]) -> Optional[str]:
        """
        Add or update a service configuration safely
        Returns modified configuration or None if failed
        """
        if not self.source_code:
            return None
        
        # Check if service already exists
        if self.has_service(service_name):
            print(f"Service {service_name} already configured")
            # Could update existing config here
            return self.source_code
        
        # Generate service configuration
        service_config = f"\n  # {service_name} service\n"
        service_config += f"  services.{service_name} = {{\n"
        
        for key, value in config.items():
            if isinstance(value, bool):
                value_str = "true" if value else "false"
            elif isinstance(value, str):
                value_str = f'"{value}"'
            elif isinstance(value, list):
                value_str = "[ " + " ".join(f'"{v}"' if isinstance(v, str) else str(v) for v in value) + " ]"
            else:
                value_str = str(value)
            
            service_config += f"    {key} = {value_str};\n"
        
        service_config += "  };\n"
        
        # Find where to insert (before the last closing brace)
        lines = self.source_code.split('\n')
        
        # Find the last closing brace
        insert_index = -1
        for i in range(len(lines) - 1, -1, -1):
            if '}' in lines[i]:
                insert_index = i
                break
        
        if insert_index > 0:
            lines.insert(insert_index, service_config)
            return '\n'.join(lines)
        
        return None
    
    def validate_syntax(self, nix_code: str) -> Tuple[bool, List[str]]:
        """
        Validate Nix syntax and return errors if any
        """
        errors = []
        
        # Parse the code
        tree = self.parser.parse(bytes(nix_code, "utf8"))
        
        if tree.root_node.has_error:
            # Find error nodes
            def find_errors(node, error_list):
                if node.type == "ERROR" or node.is_missing:
                    error_list.append(f"Syntax error at line {node.start_point[0] + 1}")
                for child in node.children:
                    find_errors(child, error_list)
            
            find_errors(tree.root_node, errors)
        
        return len(errors) == 0, errors
    
    def extract_imports(self) -> List[str]:
        """Extract all imports from the configuration"""
        imports = []
        
        if not self.tree:
            return imports
        
        ast = self.get_ast()
        if not ast:
            return imports
        
        # Find imports
        for node in ast.find_all("binding"):
            if "imports" in node.text:
                # Extract import paths
                match = re.findall(r'[./][\w/.]+\.nix', node.text)
                imports.extend(match)
        
        return imports
    
    def get_config_structure(self) -> Dict[str, Any]:
        """
        Get high-level structure of the configuration
        Useful for understanding what's already configured
        """
        structure = {
            "imports": self.extract_imports(),
            "packages": self.find_system_packages(),
            "services": self.find_services(),
            "has_hardware_config": False,
            "has_bootloader": False,
            "has_networking": False,
            "has_users": False,
        }
        
        if self.source_code:
            structure["has_hardware_config"] = "hardware-configuration.nix" in self.source_code
            structure["has_bootloader"] = "boot.loader" in self.source_code
            structure["has_networking"] = "networking.hostName" in self.source_code
            structure["has_users"] = "users.users" in self.source_code
        
        return structure


class SafeConfigModifier:
    """
    High-level interface for safe NixOS configuration modifications
    """
    
    def __init__(self, config_path: str = "/etc/nixos/configuration.nix"):
        self.parser = NixConfigParser()
        self.config_path = Path(config_path)
        self.backup_path = None
        
    def load_config(self) -> bool:
        """Load and parse the configuration"""
        if not self.config_path.exists():
            print(f"Configuration not found: {self.config_path}")
            return False
        
        return self.parser.parse_file(str(self.config_path))
    
    def backup_config(self) -> Path:
        """Create a backup of the current configuration"""
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_path = self.config_path.parent / f"{self.config_path.name}.backup_{timestamp}"
        shutil.copy(self.config_path, self.backup_path)
        
        return self.backup_path
    
    def add_package(self, package_name: str, dry_run: bool = True) -> bool:
        """
        Add a package to the configuration
        
        Args:
            package_name: Name of the package to add
            dry_run: If True, don't actually modify the file
        
        Returns:
            True if successful
        """
        if not self.parser.source_code:
            if not self.load_config():
                return False
        
        # Check if package already exists
        if self.parser.has_package(package_name):
            print(f"✅ Package '{package_name}' already in configuration")
            return True
        
        # Generate modified configuration
        modified = self.parser.add_package_safely(package_name)
        
        if not modified:
            print(f"❌ Failed to add package '{package_name}'")
            return False
        
        # Validate syntax
        valid, errors = self.parser.validate_syntax(modified)
        
        if not valid:
            print(f"❌ Syntax errors after modification:")
            for error in errors:
                print(f"   {error}")
            return False
        
        if dry_run:
            print(f"✅ Would add package '{package_name}' (dry run)")
            print("\nPreview of changes:")
            print("-" * 40)
            # Show diff
            import difflib
            diff = difflib.unified_diff(
                self.parser.source_code.splitlines(keepends=True),
                modified.splitlines(keepends=True),
                fromfile="configuration.nix",
                tofile="configuration.nix (modified)"
            )
            print(''.join(diff))
            return True
        
        # Actually write the file
        self.backup_config()
        self.config_path.write_text(modified)
        print(f"✅ Added package '{package_name}' to configuration")
        print(f"   Backup saved to: {self.backup_path}")
        
        return True
    
    def add_service(self, service_name: str, config: Dict[str, Any], dry_run: bool = True) -> bool:
        """
        Add or configure a service
        
        Args:
            service_name: Name of the service
            config: Service configuration dictionary
            dry_run: If True, don't actually modify the file
        
        Returns:
            True if successful
        """
        if not self.parser.source_code:
            if not self.load_config():
                return False
        
        # Check if service already exists
        if self.parser.has_service(service_name):
            print(f"✅ Service '{service_name}' already configured")
            return True
        
        # Generate modified configuration
        modified = self.parser.add_service_safely(service_name, config)
        
        if not modified:
            print(f"❌ Failed to add service '{service_name}'")
            return False
        
        # Validate syntax
        valid, errors = self.parser.validate_syntax(modified)
        
        if not valid:
            print(f"❌ Syntax errors after modification:")
            for error in errors:
                print(f"   {error}")
            return False
        
        if dry_run:
            print(f"✅ Would configure service '{service_name}' (dry run)")
            return True
        
        # Actually write the file
        self.backup_config()
        self.config_path.write_text(modified)
        print(f"✅ Configured service '{service_name}'")
        print(f"   Backup saved to: {self.backup_path}")
        
        return True
    
    def analyze_config(self) -> Dict[str, Any]:
        """Analyze the current configuration"""
        if not self.parser.source_code:
            if not self.load_config():
                return {}
        
        return self.parser.get_config_structure()


# Example usage
if __name__ == "__main__":
    # Test the parser
    modifier = SafeConfigModifier()
    
    # Analyze current config
    print("🔍 Analyzing configuration...")
    structure = modifier.analyze_config()
    
    print(f"\n📦 Packages: {len(structure.get('packages', []))}")
    for pkg in structure.get('packages', [])[:5]:
        print(f"   - {pkg}")
    
    print(f"\n🔧 Services: {len(structure.get('services', {}))}")
    for svc, enabled in list(structure.get('services', {}).items())[:5]:
        status = "✅" if enabled else "❌"
        print(f"   {status} {svc}")
    
    # Test adding a package (dry run)
    print("\n🧪 Testing package addition (dry run)...")
    modifier.add_package("htop", dry_run=True)