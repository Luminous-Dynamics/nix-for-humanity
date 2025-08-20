#!/usr/bin/env python3
"""Analyze and document the current import structure."""

import ast
import os
from pathlib import Path
from collections import defaultdict
import json

def analyze_imports():
    """Analyze all imports in the codebase."""
    
    print("🔍 Analyzing Import Structure\n")
    
    src_dir = Path('src/luminous_nix')
    
    # Track imports and exports
    imports_by_file = {}
    exports_by_file = {}
    undefined_imports = []
    circular_risks = []
    
    # First pass: collect all class and function definitions
    definitions = defaultdict(set)
    
    for py_file in src_dir.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue
            
        try:
            with open(py_file) as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Find all definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    definitions[str(py_file)].add(('class', node.name))
                elif isinstance(node, ast.FunctionDef):
                    definitions[str(py_file)].add(('function', node.name))
                elif isinstance(node, ast.AsyncFunctionDef):
                    definitions[str(py_file)].add(('async_function', node.name))
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
    
    # Second pass: analyze imports
    for py_file in src_dir.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue
        
        try:
            with open(py_file) as f:
                content = f.read()
            
            tree = ast.parse(content)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append({
                            'from': module,
                            'import': alias.name,
                            'as': alias.asname
                        })
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            'import': alias.name,
                            'as': alias.asname
                        })
            
            imports_by_file[str(py_file.relative_to('src'))] = imports
            
            # Check for undefined imports
            for imp in imports:
                if imp.get('from', '').startswith('.'):
                    # Relative import
                    from_module = imp['from']
                    import_name = imp['import']
                    
                    # Try to resolve the import
                    current_dir = py_file.parent
                    if from_module == '.':
                        target_file = current_dir / f"{import_name}.py"
                        target_init = current_dir / import_name / "__init__.py"
                    else:
                        levels = from_module.count('.')
                        target_dir = current_dir
                        for _ in range(levels):
                            target_dir = target_dir.parent
                        module_parts = from_module.strip('.').split('.')
                        for part in module_parts:
                            target_dir = target_dir / part
                        target_file = target_dir.with_suffix('.py')
                        target_init = target_dir / "__init__.py"
                    
                    # Check if import exists
                    found = False
                    for target in [target_file, target_init]:
                        if target.exists() and str(target) in definitions:
                            for def_type, def_name in definitions[str(target)]:
                                if def_name == import_name or import_name == '*':
                                    found = True
                                    break
                    
                    if not found and import_name != '*':
                        undefined_imports.append({
                            'file': str(py_file.relative_to('src')),
                            'import': import_name,
                            'from': from_module
                        })
            
        except Exception as e:
            print(f"Error analyzing {py_file}: {e}")
    
    # Check for circular import risks
    for file1, imports1 in imports_by_file.items():
        for imp in imports1:
            if imp.get('from', '').startswith('.'):
                # This file imports from another
                # Check if that other file imports from this one
                for file2, imports2 in imports_by_file.items():
                    if file1 != file2:
                        for imp2 in imports2:
                            if imp2.get('from', '').startswith('.'):
                                # Simple check - could be more sophisticated
                                if file1.replace('.py', '') in imp2.get('from', ''):
                                    circular_risks.append({
                                        'file1': file1,
                                        'file2': file2,
                                        'import1': imp,
                                        'import2': imp2
                                    })
    
    # Generate report
    report = {
        'total_files': len(imports_by_file),
        'undefined_imports': undefined_imports,
        'circular_risks': circular_risks[:10],  # First 10
        'problem_files': [],
        'statistics': {
            'total_imports': sum(len(imps) for imps in imports_by_file.values()),
            'relative_imports': sum(1 for imps in imports_by_file.values() for imp in imps if imp.get('from', '').startswith('.')),
            'undefined_count': len(undefined_imports)
        }
    }
    
    # Find problem files
    problem_counts = defaultdict(int)
    for undef in undefined_imports:
        problem_counts[undef['file']] += 1
    
    report['problem_files'] = [
        {'file': file, 'undefined_imports': count}
        for file, count in sorted(problem_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    ]
    
    return report

def print_report(report):
    """Print a readable report."""
    
    print("📊 Import Analysis Report")
    print("=" * 60)
    
    print(f"\nTotal files analyzed: {report['total_files']}")
    print(f"Total imports: {report['statistics']['total_imports']}")
    print(f"Relative imports: {report['statistics']['relative_imports']}")
    print(f"Undefined imports: {report['statistics']['undefined_count']}")
    
    if report['problem_files']:
        print("\n❌ Top Problem Files:")
        for pf in report['problem_files']:
            print(f"  - {pf['file']}: {pf['undefined_imports']} undefined imports")
    
    if report['undefined_imports']:
        print(f"\n❌ Sample Undefined Imports (first 10):")
        for ui in report['undefined_imports'][:10]:
            print(f"  - {ui['file']}: Cannot import '{ui['import']}' from '{ui['from']}'")
    
    if report['circular_risks']:
        print(f"\n⚠️  Potential Circular Imports:")
        seen = set()
        for cr in report['circular_risks']:
            pair = tuple(sorted([cr['file1'], cr['file2']]))
            if pair not in seen:
                seen.add(pair)
                print(f"  - {cr['file1']} ↔️ {cr['file2']}")
    
    # Save full report
    with open('metrics/import_analysis.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Full report saved to metrics/import_analysis.json")

def suggest_fixes(report):
    """Suggest fixes for import problems."""
    
    print("\n\n🔧 Suggested Fixes:")
    print("=" * 60)
    
    print("\n1. Create Missing Exports:")
    
    # Group by module
    missing_by_module = defaultdict(set)
    for ui in report['undefined_imports']:
        if ui['from'].startswith('.'):
            module = ui['file'].rsplit('/', 1)[0] + '/' + ui['from'].strip('.').replace('.', '/') + '.py'
            missing_by_module[module].add(ui['import'])
    
    for module, missing in list(missing_by_module.items())[:5]:
        print(f"\n   In {module}, add:")
        for item in missing:
            print(f"   - {item}")
    
    print("\n2. Fix Circular Dependencies:")
    print("   - Move shared types to a separate 'types.py' module")
    print("   - Use TYPE_CHECKING imports for type hints only")
    print("   - Consider dependency injection instead of direct imports")
    
    print("\n3. Standardize Import Patterns:")
    print("   - Use absolute imports from 'luminous_nix' for clarity")
    print("   - Keep relative imports only for same-package imports")
    print("   - Create clear __init__.py exports")

if __name__ == '__main__':
    report = analyze_imports()
    print_report(report)
    suggest_fixes(report)