"""
POML Bridge v2 - Aligned with Microsoft POML Specification

This improved bridge properly handles POML syntax including:
- Template variables with {{ }}
- Let bindings for reusable content
- Proper component hierarchy
- Multi-modal inputs (images, documents)
"""

import xml.etree.ElementTree as ET
import json
import logging
import re
from typing import Dict, Any, Optional, List
from pathlib import Path


class POMLProcessor:
    """
    Process POML files according to Microsoft specification.
    
    Key features:
    - Template variable substitution
    - Let binding evaluation
    - Component extraction
    - Example parsing
    """
    
    def __init__(self, poml_path: str = None):
        """Initialize the POML processor"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        if poml_path is None:
            # Default to v2 transform prompt
            poml_path = Path(__file__).parent / "transform_prompt_v2.poml"
        
        self.poml_path = poml_path
        self.poml_content = None
        self.variables = {}
        self.load_poml()
        
        self.logger.info(f"📜 POML Processor initialized with: {self.poml_path}")
    
    def load_poml(self):
        """Load POML file content"""
        try:
            with open(self.poml_path, 'r') as f:
                self.poml_content = f.read()
            self.logger.info("✅ POML document loaded")
        except Exception as e:
            self.logger.error(f"Failed to load POML: {e}")
            raise
    
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process POML with given context variables.
        
        Args:
            context: Dictionary of variables to substitute
            
        Returns:
            Dictionary containing prompt and metadata
        """
        # Parse XML
        root = ET.fromstring(self.poml_content)
        
        # Extract metadata first
        metadata = self._extract_metadata(root)
        
        # Process let bindings
        self._process_let_bindings(root)
        
        # Extract components
        components = {
            'role': self._extract_component(root, 'role'),
            'task': self._extract_component(root, 'task'),
            'human_message': self._extract_component(root, 'HumanMessage'),
            'instructions': self._extract_component(root, 'stepwise-instructions'),
            'examples': self._extract_examples(root),
            'output_format': self._extract_component(root, 'output-format'),
            'hints': self._extract_hints(root)
        }
        
        # Build prompt
        prompt = self._build_prompt(components, context)
        
        # Return both prompt and metadata
        return {
            'prompt_generated': prompt,
            'success': True,
            **metadata  # Include all metadata fields
        }
    
    def _extract_metadata(self, root) -> Dict[str, Any]:
        """Extract metadata from POML template"""
        metadata = {}
        metadata_elem = root.find('.//metadata')
        
        if metadata_elem is not None:
            # Extract each metadata field
            for field in metadata_elem:
                field_name = field.tag
                field_value = field.text.strip() if field.text else ""
                
                # Convert types appropriately
                if field_name == 'requires_speed':
                    metadata[field_name] = field_value.lower() == 'true'
                elif field_name == 'temperature':
                    try:
                        metadata[field_name] = float(field_value)
                    except:
                        metadata[field_name] = 0.7  # Default
                else:
                    metadata[field_name] = field_value
        else:
            # Default metadata if not specified
            metadata = {
                'task_type': 'conversation',
                'complexity': 'medium',
                'requires_speed': False,
                'temperature': 0.7
            }
        
        return metadata
    
    def _process_let_bindings(self, root):
        """Process <let> variable definitions"""
        for let_elem in root.findall('.//let'):
            name = let_elem.get('name')
            
            # Check for external source
            if let_elem.get('src'):
                # Load from external file
                src_path = Path(self.poml_path).parent / let_elem.get('src')
                try:
                    with open(src_path, 'r') as f:
                        if src_path.suffix == '.json':
                            self.variables[name] = json.load(f)
                        else:
                            self.variables[name] = f.read()
                except Exception as e:
                    self.logger.warning(f"Could not load {src_path}: {e}")
            else:
                # Use text content
                self.variables[name] = let_elem.text.strip() if let_elem.text else ""
    
    def _extract_component(self, root, tag_name: str) -> str:
        """Extract text from a component"""
        elem = root.find(f'.//{tag_name}')
        if elem is None:
            return ""
        
        # Process element content
        content = self._element_to_text(elem)
        
        # Substitute variables
        content = self._substitute_variables(content)
        
        return content
    
    def _extract_examples(self, root) -> List[Dict[str, str]]:
        """Extract examples from POML"""
        examples = []
        
        for example in root.findall('.//example'):
            input_elem = example.find('input')
            output_elem = example.find('output')
            
            if input_elem is not None and output_elem is not None:
                examples.append({
                    'input': input_elem.text.strip() if input_elem.text else "",
                    'output': output_elem.text.strip() if output_elem.text else ""
                })
        
        return examples
    
    def _extract_hints(self, root) -> List[str]:
        """Extract hints from POML"""
        hints = []
        
        for hint in root.findall('.//hint'):
            if hint.text:
                hints.append(hint.text.strip())
        
        return hints
    
    def _element_to_text(self, elem) -> str:
        """Convert XML element to text, preserving structure"""
        if elem.text:
            text = elem.text.strip()
        else:
            text = ""
        
        # Process child elements
        for child in elem:
            if child.tag == 'list':
                # Handle lists
                items = []
                for item in child.findall('item'):
                    if item.text:
                        items.append(f"• {item.text.strip()}")
                text += "\n" + "\n".join(items)
            
            elif child.tag == 'document':
                # Handle document references
                src = child.get('src', 'document')
                text += f"\n{{{{{src}}}}}"
            
            elif child.tag == 'p':
                # Handle paragraphs
                if child.text:
                    text += f"\n{child.text.strip()}"
                
                # Check for 'for' attribute (loops)
                if child.get('for'):
                    loop_expr = child.get('for')
                    text += f"\n[Loop: {loop_expr}]"
            
            elif child.tag == 'h3':
                # Handle headers
                if child.text:
                    text += f"\n\n### {child.text.strip()}"
            
            else:
                # Recursively process other elements
                child_text = self._element_to_text(child)
                if child_text:
                    text += f"\n{child_text}"
        
        return text
    
    def _substitute_variables(self, text: str, context: Dict[str, Any] = None) -> str:
        """Substitute {{ variable }} placeholders"""
        if context is None:
            context = {}
        
        # Combine stored variables with context
        all_vars = {**self.variables, **context}
        
        # Find all {{ variable }} patterns
        pattern = r'\{\{\s*([^}]+)\s*\}\}'
        
        def replacer(match):
            var_expr = match.group(1).strip()
            
            # Simple variable lookup
            if var_expr in all_vars:
                value = all_vars[var_expr]
                if isinstance(value, str):
                    return value
                else:
                    return json.dumps(value, indent=2)
            
            # Keep original if not found
            return match.group(0)
        
        return re.sub(pattern, replacer, text)
    
    def _build_prompt(self, components: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build final prompt from components"""
        prompt_parts = []
        
        # System role
        if components['role']:
            role_text = self._substitute_variables(components['role'], context)
            prompt_parts.append(f"### System Role\n{role_text}")
        
        # Task
        if components['task']:
            task_text = self._substitute_variables(components['task'], context)
            prompt_parts.append(f"### Task\n{task_text}")
        
        # Human message / context
        if components['human_message']:
            msg_text = self._substitute_variables(components['human_message'], context)
            prompt_parts.append(f"### Context\n{msg_text}")
        
        # Instructions
        if components['instructions']:
            prompt_parts.append(f"### Instructions\n{components['instructions']}")
        
        # Examples
        if components['examples']:
            prompt_parts.append("### Examples")
            for i, example in enumerate(components['examples'], 1):
                prompt_parts.append(f"\n**Example {i}:**")
                prompt_parts.append(f"Input: {example['input']}")
                prompt_parts.append(f"Output:\n```json\n{example['output']}\n```")
        
        # Output format
        if components['output_format']:
            prompt_parts.append(f"### Output Format\n{components['output_format']}")
        
        # Hints
        if components['hints']:
            prompt_parts.append("### Important Notes")
            for hint in components['hints']:
                prompt_parts.append(f"• {hint}")
        
        return "\n\n".join(prompt_parts)


class POMLOrchestrator:
    """
    Orchestrate complex POML workflows.
    
    This aligns with POML's vision of process orchestration,
    not just prompt generation.
    """
    
    def __init__(self):
        """Initialize the orchestrator"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.processors = {}
        
    def register_prompt(self, name: str, poml_path: str):
        """Register a POML prompt for use"""
        self.processors[name] = POMLProcessor(poml_path)
        self.logger.info(f"📝 Registered POML prompt: {name}")
    
    def execute(self, prompt_name: str, context: Dict[str, Any]) -> str:
        """Execute a registered POML prompt with context"""
        if prompt_name not in self.processors:
            raise ValueError(f"Unknown prompt: {prompt_name}")
        
        processor = self.processors[prompt_name]
        return processor.process(context)
    
    def create_workflow(self, steps: List[Dict[str, Any]]):
        """
        Create a multi-step POML workflow.
        
        Each step can:
        - Execute a POML prompt
        - Process results
        - Feed into next step
        """
        workflow_results = []
        context = {}
        
        for step in steps:
            step_name = step.get('name', 'unnamed')
            prompt_name = step.get('prompt')
            step_context = {**context, **step.get('context', {})}
            
            self.logger.info(f"🔄 Executing workflow step: {step_name}")
            
            # Execute prompt
            if prompt_name:
                result = self.execute(prompt_name, step_context)
                workflow_results.append({
                    'step': step_name,
                    'result': result
                })
                
                # Update context for next step
                if step.get('output_key'):
                    context[step['output_key']] = result
        
        return workflow_results


def test_poml_v2():
    """Test the improved POML processor"""
    print("📜 Testing POML v2 Processor")
    print("=" * 60)
    
    # Initialize processor
    processor = POMLProcessor()
    print("✅ Processor initialized")
    
    # Test context
    context = {
        'understanding_json': json.dumps({
            'packages': ['vim', 'git'],
            'services': ['ssh'],
            'complexity': 0.3
        }, indent=2),
        'user_intention': 'install firefox',
        'username': 'nixuser'
    }
    
    # Process POML
    prompt = processor.process(context)
    print("\n📝 Generated Prompt (first 800 chars):")
    print(prompt[:800] + "...")
    
    # Test orchestrator
    print("\n🎯 Testing Orchestrator")
    orchestrator = POMLOrchestrator()
    orchestrator.register_prompt('transform', 
                                Path(__file__).parent / 'transform_prompt_v2.poml')
    
    result = orchestrator.execute('transform', context)
    print(f"✅ Orchestrator executed successfully")
    
    print("\n✨ POML v2 test complete!")


if __name__ == "__main__":
    test_poml_v2()