"""
Manifest Validator - The First Guardian at the Gate

This module validates plugin manifests against our sacred schema,
ensuring every plugin honors the constitutional law of our ecosystem.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from jsonschema import validate, ValidationError, Draft7Validator
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of manifest validation"""
    valid: bool
    errors: List[str]
    warnings: List[str]
    manifest_data: Optional[Dict] = None
    
    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0
    
    def to_dict(self) -> Dict:
        return {
            'valid': self.valid,
            'errors': self.errors,
            'warnings': self.warnings,
            'has_warnings': self.has_warnings
        }


class ManifestValidator:
    """
    The Guardian of our plugin ecosystem.
    Validates that every plugin manifest adheres to our sacred principles.
    """
    
    def __init__(self, schema_path: Optional[Path] = None):
        """Initialize with the sacred schema"""
        if schema_path is None:
            # Default to our standard schema location
            schema_path = Path(__file__).parent.parent.parent.parent / "schemas" / "plugin-manifest.schema.json"
        
        self.schema_path = schema_path
        self.schema = self._load_schema()
        self.validator = Draft7Validator(self.schema)
        
    def _load_schema(self) -> Dict:
        """Load the JSON Schema that defines our constitutional law"""
        if not self.schema_path.exists():
            raise FileNotFoundError(
                f"Sacred schema not found at {self.schema_path}. "
                "The constitutional law must exist before plugins can be validated."
            )
        
        with open(self.schema_path, 'r') as f:
            return json.load(f)
    
    def validate_manifest(self, manifest_path: Path) -> ValidationResult:
        """
        Validate a plugin manifest file.
        
        This is the primary interface - it reads a manifest.yaml file
        and confirms it adheres to our sacred schema.
        """
        errors = []
        warnings = []
        manifest_data = None
        
        # Check if manifest exists
        if not manifest_path.exists():
            return ValidationResult(
                valid=False,
                errors=[f"Manifest file not found: {manifest_path}"],
                warnings=warnings
            )
        
        # Load the manifest
        try:
            with open(manifest_path, 'r') as f:
                if manifest_path.suffix == '.yaml' or manifest_path.suffix == '.yml':
                    manifest_data = yaml.safe_load(f)
                elif manifest_path.suffix == '.json':
                    manifest_data = json.load(f)
                else:
                    errors.append(f"Unsupported manifest format: {manifest_path.suffix}")
                    return ValidationResult(valid=False, errors=errors, warnings=warnings)
        except Exception as e:
            errors.append(f"Failed to parse manifest: {e}")
            return ValidationResult(valid=False, errors=errors, warnings=warnings)
        
        # Validate against schema
        try:
            validate(instance=manifest_data, schema=self.schema)
        except ValidationError as e:
            # Convert schema errors to human-readable format
            error_path = " -> ".join(str(x) for x in e.absolute_path)
            if error_path:
                errors.append(f"Invalid value at {error_path}: {e.message}")
            else:
                errors.append(f"Schema validation failed: {e.message}")
            return ValidationResult(
                valid=False, 
                errors=errors, 
                warnings=warnings,
                manifest_data=manifest_data
            )
        
        # Additional semantic validations beyond schema
        warnings.extend(self._semantic_validation(manifest_data))
        
        return ValidationResult(
            valid=True,
            errors=errors,
            warnings=warnings,
            manifest_data=manifest_data
        )
    
    def _semantic_validation(self, manifest: Dict) -> List[str]:
        """
        Perform additional semantic validations beyond JSON Schema.
        
        These are recommendations and best practices that don't
        invalidate the manifest but suggest improvements.
        """
        warnings = []
        
        # Check if description truly explains the sacred purpose
        description = manifest.get('plugin', {}).get('description', '')
        if len(description) < 50:
            warnings.append(
                "Plugin description seems brief. Consider explaining "
                "the sacred purpose this plugin serves in more detail."
            )
        
        # Check if ethical boundaries are meaningful
        boundaries = manifest.get('consciousness', {}).get('ethical_boundaries', [])
        if len(boundaries) < 2:
            warnings.append(
                "Consider adding more ethical boundaries to clearly "
                "define what this plugin will never do."
            )
        
        # Check resource limits
        limits = manifest.get('boundaries', {}).get('resource_limits', {})
        if not limits:
            warnings.append(
                "No resource limits defined. Consider setting explicit "
                "memory and CPU constraints for better citizenship."
            )
        
        # Check for minimal permissions
        required_perms = manifest.get('capabilities', {}).get('permissions', {}).get('required', [])
        if 'filesystem.write' in required_perms and 'filesystem.read' not in required_perms:
            warnings.append(
                "Plugin requires write but not read permissions. "
                "This is unusual and may indicate an error."
            )
        
        # Check data policy alignment with consciousness principles
        principle = manifest.get('consciousness', {}).get('governing_principle')
        data_sharing = manifest.get('boundaries', {}).get('data_policy', {}).get('sharing')
        
        if principle == 'preserve_privacy' and data_sharing != 'never':
            warnings.append(
                "Plugin claims to preserve privacy but doesn't commit to "
                "never sharing data. Consider aligning data policy with principle."
            )
        
        return warnings
    
    def validate_all_in_directory(self, directory: Path) -> Dict[str, ValidationResult]:
        """
        Validate all plugin manifests in a directory.
        
        This is useful for validating an entire plugin repository.
        """
        results = {}
        
        # Look for all manifest files
        for manifest_path in directory.rglob('manifest.yaml'):
            plugin_dir = manifest_path.parent
            plugin_name = plugin_dir.name
            results[plugin_name] = self.validate_manifest(manifest_path)
        
        for manifest_path in directory.rglob('manifest.yml'):
            plugin_dir = manifest_path.parent
            plugin_name = plugin_dir.name
            if plugin_name not in results:  # Don't double-validate
                results[plugin_name] = self.validate_manifest(manifest_path)
        
        return results
    
    def print_validation_report(self, result: ValidationResult, plugin_name: str = "Plugin"):
        """
        Print a beautiful, human-readable validation report.
        """
        if result.valid:
            print(f"✅ {plugin_name} manifest is valid!")
            
            if result.has_warnings:
                print(f"\n⚠️  {len(result.warnings)} recommendations for improvement:")
                for warning in result.warnings:
                    print(f"   • {warning}")
            else:
                print("🌟 No warnings - this manifest perfectly honors our principles!")
        else:
            print(f"❌ {plugin_name} manifest validation failed!")
            print(f"\n🚨 {len(result.errors)} errors found:")
            for error in result.errors:
                print(f"   • {error}")
            
            if result.has_warnings:
                print(f"\n⚠️  {len(result.warnings)} additional recommendations:")
                for warning in result.warnings:
                    print(f"   • {warning}")
        
        # Print consciousness alignment if valid
        if result.valid and result.manifest_data:
            principle = result.manifest_data.get('consciousness', {}).get('governing_principle')
            promise = result.manifest_data.get('consciousness', {}).get('sacred_promise')
            
            print(f"\n🕊️ Consciousness Alignment:")
            print(f"   Principle: {principle}")
            print(f"   Promise: {promise}")


# CLI interface for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python manifest_validator.py <path_to_manifest.yaml>")
        sys.exit(1)
    
    manifest_path = Path(sys.argv[1])
    validator = ManifestValidator()
    
    print(f"🔍 Validating manifest: {manifest_path}")
    print("=" * 60)
    
    result = validator.validate_manifest(manifest_path)
    validator.print_validation_report(result, manifest_path.stem)
    
    sys.exit(0 if result.valid else 1)