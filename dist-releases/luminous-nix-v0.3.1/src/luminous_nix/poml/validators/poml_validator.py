#!/usr/bin/env python3
"""
POML Validator - Validate and test POML templates
Ensures compliance with POML 2.0 spec and Luminous Nix style guide
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import re
import yaml
import json


class ValidationLevel(Enum):
    """Validation severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    STYLE = "style"


@dataclass
class ValidationIssue:
    """Represents a validation issue"""
    level: ValidationLevel
    message: str
    line: Optional[int] = None
    element: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Complete validation result"""
    is_valid: bool
    issues: List[ValidationIssue]
    stats: Dict[str, Any]
    
    @property
    def error_count(self) -> int:
        return len([i for i in self.issues if i.level == ValidationLevel.ERROR])
    
    @property
    def warning_count(self) -> int:
        return len([i for i in self.issues if i.level == ValidationLevel.WARNING])


class POMLValidator:
    """
    Validates POML templates for correctness and style compliance
    """
    
    # Required elements
    REQUIRED_METADATA = ['title', 'description', 'author', 'version']
    REQUIRED_SECTIONS = ['metadata', 'prompt']
    
    # Valid model hints
    VALID_MODELS = [
        'gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo',
        'claude-2', 'claude-3', 'claude-2-5 seconds',
        'mistral-7b', 'mistral-8x7b', 'mistral-large',
        'llama-2-7b', 'llama-2-13b', 'llama-2-70b',
        'codellama-7b', 'codellama-13b', 'codellama-34b',
        'starcoder', 'starcoder-15b',
        'falcon-7b', 'falcon-40b'
    ]
    
    # Security patterns to check
    SECURITY_PATTERNS = [
        (r'password\s*[:=]', "Potential password exposure"),
        (r'api[_-]?key\s*[:=]', "Potential API key exposure"),
        (r'token\s*[:=]', "Potential token exposure"),
        (r'/home/[^/]+', "Hardcoded home directory path"),
        (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', "Potential IP address exposure"),
    ]
    
    def __init__(self, style_guide_path: Optional[Path] = None):
        """Initialize validator with optional style guide"""
        self.style_guide = self._load_style_guide(style_guide_path)
        
    def validate_file(self, poml_file: Path) -> ValidationResult:
        """Validate a POML file"""
        try:
            # Parse XML
            tree = ET.parse(poml_file)
            root = tree.getroot()
            
            # Collect issues
            issues = []
            
            # Structural validation
            issues.extend(self._validate_structure(root))
            
            # Metadata validation
            issues.extend(self._validate_metadata(root))
            
            # Variables validation
            issues.extend(self._validate_variables(root))
            
            # Prompt validation
            issues.extend(self._validate_prompt(root))
            
            # Security validation
            issues.extend(self._validate_security(poml_file))
            
            # Style validation
            issues.extend(self._validate_style(root, poml_file))
            
            # Performance validation
            issues.extend(self._validate_performance(root))
            
            # Calculate statistics
            stats = self._calculate_stats(root, poml_file)
            
            # Determine overall validity
            has_errors = any(i.level == ValidationLevel.ERROR for i in issues)
            
            return ValidationResult(
                is_valid=not has_errors,
                issues=issues,
                stats=stats
            )
            
        except ET.ParseError as e:
            return ValidationResult(
                is_valid=False,
                issues=[ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message=f"XML parsing error: {e}",
                    line=e.position[0] if hasattr(e, 'position') else None
                )],
                stats={}
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                issues=[ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message=f"Validation error: {e}"
                )],
                stats={}
            )
    
    def _validate_structure(self, root: ET.Element) -> List[ValidationIssue]:
        """Validate overall POML structure"""
        issues = []
        
        # Check POML version
        if 'version' not in root.attrib:
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message="POML version not specified",
                element="poml",
                suggestion='Add version="2.0" to root element'
            ))
        elif root.attrib['version'] not in ['2.0', '2.1']:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                message=f"POML version {root.attrib['version']} may not be fully supported",
                element="poml"
            ))
        
        # Check required sections
        for section in self.REQUIRED_SECTIONS:
            if root.find(section) is None:
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message=f"Required section '{section}' is missing",
                    suggestion=f"Add <{section}>...</{section}> section"
                ))
        
        return issues
    
    def _validate_metadata(self, root: ET.Element) -> List[ValidationIssue]:
        """Validate metadata section"""
        issues = []
        metadata = root.find('metadata')
        
        if metadata is None:
            return issues
        
        # Check required metadata fields
        for field in self.REQUIRED_METADATA:
            element = metadata.find(field)
            if element is None:
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message=f"Required metadata field '{field}' is missing",
                    element="metadata"
                ))
            elif not element.text or not element.text.strip():
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message=f"Metadata field '{field}' is empty",
                    element=f"metadata/{field}"
                ))
        
        # Validate version format
        version = metadata.find('version')
        if version is not None and version.text:
            if not re.match(r'^\d+\.\d+\.\d+(-.*)?$', version.text.strip()):
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message="Version should follow semantic versioning (x.y.z)",
                    element="metadata/version",
                    suggestion="Use format like '1.0.0' or '1.0.0-beta'"
                ))
        
        # Validate model hints
        model_hints = metadata.find('model-hints')
        if model_hints is not None:
            models = model_hints.find('preferred-models')
            if models is not None and models.text:
                model_list = [m.strip() for m in models.text.split(',')]
                unknown = [m for m in model_list if m not in self.VALID_MODELS]
                if unknown:
                    issues.append(ValidationIssue(
                        level=ValidationLevel.INFO,
                        message=f"Unknown models: {', '.join(unknown)}",
                        element="metadata/model-hints/preferred-models"
                    ))
            
            # Validate temperature
            temp = model_hints.find('temperature')
            if temp is not None and temp.text:
                try:
                    temp_val = float(temp.text)
                    if not 0 <= temp_val <= 2:
                        issues.append(ValidationIssue(
                            level=ValidationLevel.WARNING,
                            message=f"Temperature {temp_val} outside normal range [0, 2]",
                            element="metadata/model-hints/temperature"
                        ))
                except ValueError:
                    issues.append(ValidationIssue(
                        level=ValidationLevel.ERROR,
                        message="Temperature must be a number",
                        element="metadata/model-hints/temperature"
                    ))
        
        return issues
    
    def _validate_variables(self, root: ET.Element) -> List[ValidationIssue]:
        """Validate variables section"""
        issues = []
        variables = root.find('variables')
        
        if variables is None:
            return issues
        
        variable_names = set()
        for let in variables.findall('let'):
            name = let.get('name')
            if not name:
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message="Variable without name attribute",
                    element="variables/let"
                ))
                continue
            
            # Check for duplicates
            if name in variable_names:
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message=f"Duplicate variable name: {name}",
                    element=f"variables/let[@name='{name}']"
                ))
            variable_names.add(name)
            
            # Check naming convention (snake_case)
            if not re.match(r'^[a-z][a-z0-9_]*$', name):
                issues.append(ValidationIssue(
                    level=ValidationLevel.STYLE,
                    message=f"Variable '{name}' should use snake_case",
                    element=f"variables/let[@name='{name}']"
                ))
            
            # Check for template syntax
            if let.text and '{{' in let.text:
                # Validate template syntax
                if not re.match(r'.*\{\{\s*\w+.*\}\}.*', let.text):
                    issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        message=f"Potentially malformed template in variable '{name}'",
                        element=f"variables/let[@name='{name}']"
                    ))
        
        return issues
    
    def _validate_prompt(self, root: ET.Element) -> List[ValidationIssue]:
        """Validate prompt section"""
        issues = []
        prompt = root.find('prompt')
        
        if prompt is None:
            return issues
        
        # Check for system prompt
        system = prompt.find('system')
        if system is None:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                message="No system prompt defined",
                element="prompt",
                suggestion="Add <system> element with role description"
            ))
        
        # Check for instructions
        instructions = prompt.find('stepwise-instructions')
        if instructions is None:
            issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                message="No stepwise instructions defined",
                element="prompt",
                suggestion="Consider adding <stepwise-instructions> for clarity"
            ))
        else:
            # Validate steps
            steps = instructions.findall('step')
            step_ids = set()
            for step in steps:
                step_id = step.get('id')
                if not step_id:
                    issues.append(ValidationIssue(
                        level=ValidationLevel.ERROR,
                        message="Step without id attribute",
                        element="stepwise-instructions/step"
                    ))
                elif step_id in step_ids:
                    issues.append(ValidationIssue(
                        level=ValidationLevel.ERROR,
                        message=f"Duplicate step id: {step_id}",
                        element=f"stepwise-instructions/step[@id='{step_id}']"
                    ))
                step_ids.add(step_id)
        
        # Check for examples
        examples = prompt.find('examples')
        if examples is None:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                message="No examples provided",
                element="prompt",
                suggestion="Add <examples> section with input/output pairs"
            ))
        
        # Check for output format
        output_format = prompt.find('output-format')
        if output_format is None:
            issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                message="No output format specified",
                element="prompt",
                suggestion="Add <output-format> to specify expected structure"
            ))
        
        # Check for error handling
        error_handling = prompt.find('error-handling')
        if error_handling is None:
            issues.append(ValidationIssue(
                level=ValidationLevel.INFO,
                message="No error handling defined",
                element="prompt",
                suggestion="Consider adding <error-handling> for robustness"
            ))
        
        return issues
    
    def _validate_security(self, poml_file: Path) -> List[ValidationIssue]:
        """Validate security concerns"""
        issues = []
        
        # Read file content
        content = poml_file.read_text()
        
        # Check for security patterns
        for pattern, message in self.SECURITY_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # Find line number
                line_num = content[:match.start()].count('\n') + 1
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message=f"Security concern: {message}",
                    line=line_num,
                    suggestion="Remove or sanitize sensitive information"
                ))
        
        return issues
    
    def _validate_style(self, root: ET.Element, poml_file: Path) -> List[ValidationIssue]:
        """Validate style guide compliance"""
        issues = []
        
        # Check file naming convention
        if not re.match(r'^[a-z][a-z0-9_]*\.poml$', poml_file.name):
            issues.append(ValidationIssue(
                level=ValidationLevel.STYLE,
                message=f"File name '{poml_file.name}' should use snake_case",
                suggestion="Rename to snake_case.poml format"
            ))
        
        # Check indentation (should be 2 spaces)
        content = poml_file.read_text()
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if line and not line.startswith(' ' * (len(line) - len(line.lstrip()))):
                if '\t' in line:
                    issues.append(ValidationIssue(
                        level=ValidationLevel.STYLE,
                        message="Use spaces instead of tabs",
                        line=i
                    ))
        
        return issues
    
    def _validate_performance(self, root: ET.Element) -> List[ValidationIssue]:
        """Validate performance considerations"""
        issues = []
        
        # Check max tokens
        metadata = root.find('metadata')
        if metadata:
            model_hints = metadata.find('model-hints')
            if model_hints:
                max_tokens = model_hints.find('max-tokens')
                if max_tokens is not None and max_tokens.text:
                    try:
                        tokens = int(max_tokens.text)
                        if tokens > 4000:
                            issues.append(ValidationIssue(
                                level=ValidationLevel.WARNING,
                                message=f"High max_tokens value ({tokens}) may increase costs",
                                element="metadata/model-hints/max-tokens",
                                suggestion="Consider if this many tokens are necessary"
                            ))
                    except ValueError:
                        pass
        
        # Check cache settings
        prompt = root.find('prompt')
        if prompt:
            cache = prompt.find('cache')
            if cache is not None:
                duration = cache.get('duration')
                if duration:
                    try:
                        dur = int(duration)
                        if dur > 86400:  # 24 hours
                            issues.append(ValidationIssue(
                                level=ValidationLevel.INFO,
                                message=f"Long cache duration ({dur} seconds)",
                                element="prompt/cache"
                            ))
                    except ValueError:
                        pass
        
        return issues
    
    def _calculate_stats(self, root: ET.Element, poml_file: Path) -> Dict[str, Any]:
        """Calculate template statistics"""
        stats = {
            'file_size': poml_file.stat().st_size,
            'line_count': len(poml_file.read_text().split('\n')),
            'variable_count': len(root.findall('.//variables/let')),
            'step_count': len(root.findall('.//step')),
            'example_count': len(root.findall('.//example')),
            'has_error_handling': root.find('.//error-handling') is not None,
            'has_cache': root.find('.//cache') is not None,
            'has_conditionals': root.find('.//if') is not None,
            'has_loops': root.find('.//foreach') is not None,
        }
        
        return stats
    
    def _load_style_guide(self, style_guide_path: Optional[Path]) -> Dict:
        """Load style guide configuration"""
        if not style_guide_path or not style_guide_path.exists():
            return {}
        
        # Load style guide (could be YAML or JSON)
        try:
            if style_guide_path.suffix == '.yaml':
                import yaml
                return yaml.safe_load(style_guide_path.read_text())
            elif style_guide_path.suffix == '.json':
                import json
                return json.loads(style_guide_path.read_text())
        except Exception:
            return {}
        
        return {}
    
    def validate_directory(self, directory: Path) -> Dict[Path, ValidationResult]:
        """Validate all POML files in a directory"""
        results = {}
        
        for poml_file in directory.rglob('*.poml'):
            results[poml_file] = self.validate_file(poml_file)
        
        return results
    
    def print_report(self, result: ValidationResult, file_path: Optional[Path] = None):
        """Print validation report"""
        if file_path:
            print(f"\n📄 Validation Report: {file_path}")
        
        if result.is_valid:
            print("✅ VALID")
        else:
            print("❌ INVALID")
        
        # Print issues by level
        for level in ValidationLevel:
            level_issues = [i for i in result.issues if i.level == level]
            if level_issues:
                print(f"\n{level.value.upper()}S ({len(level_issues)}):")
                for issue in level_issues:
                    location = ""
                    if issue.line:
                        location = f"Line {issue.line}: "
                    elif issue.element:
                        location = f"{issue.element}: "
                    
                    print(f"  {location}{issue.message}")
                    if issue.suggestion:
                        print(f"    💡 {issue.suggestion}")
        
        # Print statistics
        if result.stats:
            print("\n📊 Statistics:")
            for key, value in result.stats.items():
                print(f"  {key}: {value}")
        
        print(f"\nSummary: {result.error_count} errors, {result.warning_count} warnings")


def main():
    """CLI interface for POML validator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate POML templates')
    parser.add_argument('path', type=Path, help='POML file or directory to validate')
    parser.add_argument('--style-guide', type=Path, help='Path to style guide config')
    parser.add_argument('--quiet', action='store_true', help='Only show errors')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    validator = POMLValidator(args.style_guide)
    
    if args.path.is_file():
        result = validator.validate_file(args.path)
        if args.json:
            import json
            print(json.dumps({
                'valid': result.is_valid,
                'errors': result.error_count,
                'warnings': result.warning_count,
                'issues': [
                    {
                        'level': i.level.value,
                        'message': i.message,
                        'line': i.line,
                        'element': i.element
                    }
                    for i in result.issues
                ],
                'stats': result.stats
            }, indent=2))
        else:
            validator.print_report(result, args.path)
    else:
        results = validator.validate_directory(args.path)
        total_errors = 0
        total_warnings = 0
        
        for file_path, result in results.items():
            if not args.quiet or not result.is_valid:
                validator.print_report(result, file_path)
                total_errors += result.error_count
                total_warnings += result.warning_count
        
        print(f"\n📊 Total: {len(results)} files validated")
        print(f"   {total_errors} total errors, {total_warnings} total warnings")


if __name__ == '__main__':
    main()