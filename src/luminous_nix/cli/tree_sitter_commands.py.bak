"""
Tree-sitter Integration Commands for CLI
Provides commands for code analysis, shell migration, and config modification
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from ..parsers.multi_language_parser import MultiLanguageAnalyzer, analyze_and_generate
from ..parsers.shell_script_migrator import ShellToNixMigrator
from ..config.safe_nix_modifier import SafeNixConfigModifier, NixConfigIntegration
from ..config.config_generator import ConfigGenerator


class TreeSitterCommands:
    """Commands for Tree-sitter based features"""
    
    def __init__(self):
        self.language_analyzer = MultiLanguageAnalyzer()
        self.shell_migrator = ShellToNixMigrator()
        self.config_modifier = SafeNixConfigModifier()
        self.config_generator = ConfigGenerator()
    
    def analyze_project(self, project_path: str, output_format: str = "text") -> Dict[str, Any]:
        """
        Analyze a project and generate Nix configuration
        
        Args:
            project_path: Path to the project
            output_format: Output format (text, json, nix)
        
        Returns:
            Analysis results
        """
        try:
            result = analyze_and_generate(project_path)
            
            if output_format == "json":
                return {"success": True, "data": result}
            elif output_format == "nix":
                return {"success": True, "nix_config": result["nix_config"]}
            else:
                # Text format for CLI display
                return {
                    "success": True,
                    "message": self._format_project_analysis(result)
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def migrate_script(self, script_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Migrate a shell script to Nix configuration
        
        Args:
            script_path: Path to shell script
            output_dir: Optional output directory for generated files
        
        Returns:
            Migration results
        """
        try:
            result = self.shell_migrator.migrate_script(script_path, output_dir)
            
            if result["success"]:
                message = self._format_migration_result(result)
                return {"success": True, "message": message, "data": result}
            else:
                warnings = result["analysis"]["warnings"]
                return {
                    "success": False,
                    "message": f"Migration failed: Script too complex",
                    "warnings": warnings
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def modify_config(self, action: str, target: str, config_path: str = "/etc/nixos/configuration.nix",
                     dry_run: bool = True) -> Dict[str, Any]:
        """
        Safely modify NixOS configuration
        
        Args:
            action: Action to perform (add-package, add-service, analyze)
            target: Package or service name
            config_path: Path to configuration file
            dry_run: If True, preview changes without applying
        
        Returns:
            Modification results
        """
        try:
            self.config_modifier.config_path = Path(config_path)
            
            if action == "analyze":
                if not self.config_modifier.load_config():
                    return {"success": False, "error": "Could not load configuration"}
                
                analysis = self.config_modifier.analyze()
                return {
                    "success": True,
                    "message": self._format_config_analysis(analysis)
                }
            
            elif action == "add-package":
                if not self.config_modifier.load_config():
                    return {"success": False, "error": "Could not load configuration"}
                
                result = self.config_modifier.add_package(target, dry_run=dry_run)
                if result:
                    mode = "Would add" if dry_run else "Added"
                    return {
                        "success": True,
                        "message": f"{mode} package '{target}' to configuration",
                        "preview": result if dry_run else None
                    }
                else:
                    return {"success": False, "error": f"Failed to add package '{target}'"}
            
            elif action == "add-service":
                if not self.config_modifier.load_config():
                    return {"success": False, "error": "Could not load configuration"}
                
                result = self.config_modifier.add_service(target, {"enable": True}, dry_run=dry_run)
                if result:
                    mode = "Would enable" if dry_run else "Enabled"
                    return {
                        "success": True,
                        "message": f"{mode} service '{target}'",
                        "preview": result if dry_run else None
                    }
                else:
                    return {"success": False, "error": f"Failed to enable service '{target}'"}
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_config(self, template: str = "minimal", **kwargs) -> Dict[str, Any]:
        """
        Generate a new NixOS configuration from template
        
        Args:
            template: Template name (minimal, desktop, development)
            **kwargs: Template variables
        
        Returns:
            Generated configuration
        """
        try:
            config = self.config_generator.generate_config(template, **kwargs)
            return {
                "success": True,
                "config": config,
                "message": f"Generated {template} configuration"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def suggest_packages(self, description: str) -> Dict[str, Any]:
        """
        Suggest packages based on description
        
        Args:
            description: What the user wants to do
        
        Returns:
            Package suggestions
        """
        try:
            suggestions = self.config_generator.suggest_packages(description)
            if suggestions:
                return {
                    "success": True,
                    "suggestions": suggestions,
                    "message": f"Found {len(suggestions)} matching packages"
                }
            else:
                return {
                    "success": True,
                    "suggestions": [],
                    "message": "No matching packages found"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _format_project_analysis(self, result: Dict[str, Any]) -> str:
        """Format project analysis for display"""
        analysis = result["analysis"]
        lines = []
        
        lines.append(f"🔍 Project Analysis Complete")
        lines.append(f"Language: {analysis['language']}")
        
        if analysis['framework']:
            lines.append(f"Framework: {analysis['framework']}")
        
        if analysis['build_system']:
            lines.append(f"Build System: {analysis['build_system']}")
        
        if analysis['entry_point']:
            lines.append(f"Entry Point: {analysis['entry_point']}")
        
        lines.append(f"Confidence: {analysis['confidence']:.0%}")
        
        if analysis['dependencies']:
            lines.append(f"\n📦 Dependencies ({len(analysis['dependencies'])}):")
            for dep in analysis['dependencies'][:5]:
                lines.append(f"  - {dep}")
            if len(analysis['dependencies']) > 5:
                lines.append(f"  ... and {len(analysis['dependencies']) - 5} more")
        
        if result['suggested_packages']:
            lines.append(f"\n💡 Suggested Nix Packages:")
            for pkg in result['suggested_packages']:
                lines.append(f"  - {pkg}")
        
        if result['improvements']:
            lines.append(f"\n📈 Suggested Improvements:")
            for imp in result['improvements']:
                lines.append(f"  - {imp}")
        
        return "\n".join(lines)
    
    def _format_migration_result(self, result: Dict[str, Any]) -> str:
        """Format migration result for display"""
        lines = []
        analysis = result["analysis"]
        
        lines.append("✅ Migration successful!")
        
        if analysis["packages_needed"]:
            lines.append(f"\n📦 Packages needed ({len(analysis['packages_needed'])}):")
            for pkg in analysis["packages_needed"][:10]:
                lines.append(f"  - {pkg}")
        
        if analysis["services_configured"]:
            lines.append(f"\n🔧 Services configured:")
            for service in analysis["services_configured"]:
                lines.append(f"  - {service}")
        
        if analysis["warnings"]:
            lines.append(f"\n⚠️  Warnings:")
            for warning in analysis["warnings"]:
                lines.append(f"  - {warning}")
        
        if result.get("config_file"):
            lines.append(f"\n📝 NixOS config saved to: {result['config_file']}")
        
        if result.get("derivation_file"):
            lines.append(f"📝 Nix derivation saved to: {result['derivation_file']}")
        
        return "\n".join(lines)
    
    def _format_config_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format configuration analysis for display"""
        lines = []
        
        lines.append("📊 Configuration Analysis:")
        lines.append(f"  Packages: {len(analysis.get('packages', []))}")
        lines.append(f"  Services: {len(analysis.get('services', {}))}")
        lines.append(f"  Lines: {analysis.get('lines', 0)}")
        
        if analysis.get('packages'):
            lines.append("\n📦 Installed Packages:")
            for pkg in analysis['packages'][:10]:
                lines.append(f"  - {pkg}")
            if len(analysis['packages']) > 10:
                lines.append(f"  ... and {len(analysis['packages']) - 10} more")
        
        if analysis.get('services'):
            lines.append("\n🔧 Configured Services:")
            for svc, config in list(analysis['services'].items())[:5]:
                enabled = config.get('enable', False)
                status = "✅" if enabled else "❌"
                lines.append(f"  {status} {svc}")
        
        return "\n".join(lines)


# Integration with the main CLI
def handle_tree_sitter_command(args) -> int:
    """
    Handle Tree-sitter related commands from the CLI
    
    Args:
        args: Parsed command line arguments
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    commands = TreeSitterCommands()
    
    # Determine which subcommand to run
    if hasattr(args, 'tree_command'):
        if args.tree_command == 'analyze':
            # Analyze a project
            result = commands.analyze_project(
                args.path,
                output_format=args.format
            )
            
            if result["success"]:
                if args.format == "json":
                    print(json.dumps(result["data"], indent=2))
                elif args.format == "nix":
                    print(result["nix_config"])
                else:
                    print(result["message"])
                return 0
            else:
                print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
                return 1
        
        elif args.tree_command == 'migrate':
            # Migrate a shell script
            result = commands.migrate_script(
                args.script,
                output_dir=args.output
            )
            
            if result["success"]:
                print(result["message"])
                if args.output and result.get("data", {}).get("nix_config"):
                    print("\n📄 Generated NixOS Configuration:")
                    print("-" * 40)
                    print(result["data"]["nix_config"])
                return 0
            else:
                print(f"Error: {result.get('message', 'Migration failed')}", file=sys.stderr)
                if result.get("warnings"):
                    print("\nWarnings:", file=sys.stderr)
                    for warning in result["warnings"]:
                        print(f"  - {warning}", file=sys.stderr)
                return 1
        
        elif args.tree_command == 'modify':
            # Modify NixOS configuration
            result = commands.modify_config(
                args.action,
                args.target,
                config_path=args.config,
                dry_run=args.dry_run
            )
            
            if result["success"]:
                print(result["message"])
                if result.get("preview") and args.dry_run:
                    # Show diff preview in dry-run mode
                    print("\n📝 Preview of changes:")
                    print("-" * 40)
                    # The preview is already formatted by the modifier
                return 0
            else:
                print(f"Error: {result.get('error', 'Modification failed')}", file=sys.stderr)
                return 1
        
        elif args.tree_command == 'generate':
            # Generate configuration from template
            kwargs = {}
            if args.hostname:
                kwargs['hostname'] = args.hostname
            if args.username:
                kwargs['username'] = args.username
            
            result = commands.generate_config(args.template, **kwargs)
            
            if result["success"]:
                print(result["message"])
                print("\n" + result["config"])
                return 0
            else:
                print(f"Error: {result.get('error', 'Generation failed')}", file=sys.stderr)
                return 1
        
        elif args.tree_command == 'suggest':
            # Suggest packages
            result = commands.suggest_packages(args.description)
            
            if result["success"]:
                print(result["message"])
                if result["suggestions"]:
                    print("\n💡 Suggested packages:")
                    for pkg in result["suggestions"]:
                        print(f"  - {pkg}")
                return 0
            else:
                print(f"Error: {result.get('error', 'Suggestion failed')}", file=sys.stderr)
                return 1
    
    return 0


def add_tree_sitter_parser(subparsers):
    """Add Tree-sitter command parser to argparse subparsers"""
    
    # Main tree-sitter command
    tree_parser = subparsers.add_parser(
        'tree',
        help='Tree-sitter based code analysis and migration tools'
    )
    
    tree_subparsers = tree_parser.add_subparsers(
        dest='tree_command',
        help='Tree-sitter subcommands'
    )
    
    # Analyze project command
    analyze_parser = tree_subparsers.add_parser(
        'analyze',
        help='Analyze a project and generate Nix configuration'
    )
    analyze_parser.add_argument(
        'path',
        help='Path to the project directory'
    )
    analyze_parser.add_argument(
        '-f', '--format',
        choices=['text', 'json', 'nix'],
        default='text',
        help='Output format'
    )
    
    # Migrate shell script command
    migrate_parser = tree_subparsers.add_parser(
        'migrate',
        help='Migrate a shell script to NixOS configuration'
    )
    migrate_parser.add_argument(
        'script',
        help='Path to the shell script'
    )
    migrate_parser.add_argument(
        '-o', '--output',
        help='Output directory for generated files'
    )
    
    # Modify configuration command
    modify_parser = tree_subparsers.add_parser(
        'modify',
        help='Safely modify NixOS configuration'
    )
    modify_parser.add_argument(
        'action',
        choices=['analyze', 'add-package', 'add-service'],
        help='Action to perform'
    )
    modify_parser.add_argument(
        'target',
        nargs='?',
        help='Package or service name (not needed for analyze)'
    )
    modify_parser.add_argument(
        '-c', '--config',
        default='/etc/nixos/configuration.nix',
        help='Path to configuration file'
    )
    modify_parser.add_argument(
        '--apply',
        dest='dry_run',
        action='store_false',
        help='Apply changes (default is dry-run)'
    )
    
    # Generate configuration command
    generate_parser = tree_subparsers.add_parser(
        'generate',
        help='Generate NixOS configuration from template'
    )
    generate_parser.add_argument(
        'template',
        choices=['minimal', 'desktop', 'development'],
        help='Template to use'
    )
    generate_parser.add_argument(
        '--hostname',
        help='System hostname'
    )
    generate_parser.add_argument(
        '--username',
        help='Primary user name'
    )
    
    # Suggest packages command
    suggest_parser = tree_subparsers.add_parser(
        'suggest',
        help='Suggest packages based on description'
    )
    suggest_parser.add_argument(
        'description',
        help='What you want to do (e.g., "edit text", "browse web")'
    )
    
    return tree_parser