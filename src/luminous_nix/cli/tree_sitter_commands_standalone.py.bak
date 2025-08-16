"""
Standalone Tree-sitter Commands (no click dependency)
This is a copy that doesn't depend on the main CLI module
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Import parsers directly from their modules
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nix_for_humanity.parsers.multi_language_parser import MultiLanguageAnalyzer, analyze_and_generate
from nix_for_humanity.parsers.shell_script_migrator import ShellToNixMigrator
from nix_for_humanity.config.safe_nix_modifier import SafeNixConfigModifier, NixConfigIntegration
from nix_for_humanity.config.config_generator import ConfigGenerator


class TreeSitterCommands:
    """Commands for Tree-sitter based features"""
    
    def __init__(self):
        self.language_analyzer = MultiLanguageAnalyzer()
        self.shell_migrator = ShellToNixMigrator()
        self.config_modifier = SafeNixConfigModifier()
        self.config_generator = ConfigGenerator()
    
    def analyze_project(self, project_path: str, output_format: str = "text") -> Dict[str, Any]:
        """Analyze a project and generate Nix configuration"""
        try:
            result = analyze_and_generate(project_path)
            
            if output_format == "json":
                return {"success": True, "data": result}
            elif output_format == "nix":
                return {"success": True, "nix_config": result["nix_config"]}
            else:
                return {
                    "success": True,
                    "message": self._format_project_analysis(result)
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def migrate_script(self, script_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Migrate a shell script to Nix configuration"""
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
        """Safely modify NixOS configuration"""
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
        """Generate a new NixOS configuration from template"""
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
        """Suggest packages based on description"""
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