"""
POML Bridge - Connecting Python Body to POML Soul

This module allows our Python-based Declarative Agent to use
POML-defined prompts, making the agent's reasoning transparent,
auditable, and governable.
"""

import xml.etree.ElementTree as ET
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path


class POMLBridge:
    """
    Bridge between Python execution and POML prompt definitions.
    
    This is the sacred connection that allows our agent's body (Python)
    to be guided by its soul (POML).
    """
    
    def __init__(self, poml_path: str = None):
        """Initialize the POML bridge"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        if poml_path is None:
            # Default to the transform prompt
            poml_path = Path(__file__).parent / "transform_prompt.poml"
        
        self.poml_path = poml_path
        self.poml_tree = None
        self.load_poml()
        
        self.logger.info(f"🌉 POML Bridge initialized with: {self.poml_path}")
    
    def load_poml(self):
        """Load and parse the POML file"""
        try:
            self.poml_tree = ET.parse(self.poml_path)
            self.logger.info("✅ POML document loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load POML: {e}")
            raise
    
    def build_prompt(self, user_intention: str, understanding: Dict[str, Any]) -> str:
        """
        Build a prompt from POML template with actual values.
        
        This transforms the constitutional POML into an actual prompt
        that can be sent to an LLM.
        """
        if not self.poml_tree:
            raise RuntimeError("POML not loaded")
        
        root = self.poml_tree.getroot()
        
        # Extract the system role
        system_role = self._extract_system_role(root)
        
        # Extract the user role template
        user_template = self._extract_user_template(root)
        
        # Replace variables with actual values
        prompt = self._substitute_variables(user_template, {
            'user_intention': user_intention,
            'understanding.json': json.dumps(understanding, indent=2)
        })
        
        # Combine system and user prompts
        full_prompt = f"{system_role}\n\n{prompt}"
        
        return full_prompt
    
    def _extract_system_role(self, root) -> str:
        """Extract the system role definition from POML"""
        system_elements = root.findall(".//role[@name='system']")
        
        if not system_elements:
            return "You are a helpful assistant."
        
        system_text = []
        for element in system_elements[0]:
            text = self._element_to_text(element)
            if text:
                system_text.append(text)
        
        return "\n\n".join(system_text)
    
    def _extract_user_template(self, root) -> str:
        """Extract the user role template from POML"""
        user_elements = root.findall(".//role[@name='user']")
        
        if not user_elements:
            return ""
        
        user_text = []
        for element in user_elements[0]:
            text = self._element_to_text(element)
            if text:
                user_text.append(text)
        
        return "\n\n".join(user_text)
    
    def _element_to_text(self, element) -> str:
        """Convert a POML element to text"""
        text_parts = []
        
        # Handle different element types
        if element.tag == 'identity':
            text_parts.append(element.text.strip() if element.text else "")
        
        elif element.tag == 'capabilities':
            text_parts.append("Capabilities:")
            text_parts.append(element.text.strip() if element.text else "")
        
        elif element.tag == 'context':
            for section in element.findall('section'):
                title = section.find('title')
                if title is not None and title.text:
                    text_parts.append(f"**{title.text}**")
                
                # Handle document references
                doc = section.find('document')
                if doc is not None:
                    ref = doc.get('ref', 'document')
                    text_parts.append(f"{{{{{ref}}}}}")
                
                # Handle variables
                var = section.find('variable')
                if var is not None:
                    name = var.get('name', 'variable')
                    text_parts.append(f'"{{{{{name}}}}}"')
        
        elif element.tag == 'task':
            text_parts.append("Your Task:")
            for step in element.findall('step'):
                number = step.get('number', '')
                step_text = step.text.strip() if step.text else ""
                text_parts.append(f"{number}. {step_text}")
        
        elif element.tag == 'output_format':
            text_parts.append("Output Format:")
            text_parts.append(element.text.strip() if element.text else "")
            
            # Include schema if present
            schema = element.find('schema')
            if schema is not None and schema.text:
                text_parts.append("```json")
                text_parts.append(schema.text.strip())
                text_parts.append("```")
        
        return "\n".join(text_parts)
    
    def _substitute_variables(self, template: str, values: Dict[str, Any]) -> str:
        """Replace template variables with actual values"""
        result = template
        
        for key, value in values.items():
            placeholder = f"{{{{{key}}}}}"
            if isinstance(value, str):
                result = result.replace(placeholder, value)
            else:
                result = result.replace(placeholder, json.dumps(value, indent=2))
        
        return result
    
    def parse_response(self, llm_response: str) -> Dict[str, Any]:
        """
        Parse the LLM's response according to POML output schema.
        
        Extracts the JSON from the LLM's response and validates it.
        """
        try:
            # Try to extract JSON from the response
            # Handle case where LLM includes markdown code blocks
            if "```json" in llm_response:
                start = llm_response.index("```json") + 7
                end = llm_response.index("```", start)
                json_str = llm_response[start:end].strip()
            else:
                # Assume the entire response is JSON
                json_str = llm_response.strip()
            
            # Parse the JSON
            result = json.loads(json_str)
            
            # Validate required fields
            if 'transformations' not in result:
                result['transformations'] = []
            if 'confidence' not in result:
                result['confidence'] = 0.5
            if 'safety_score' not in result:
                result['safety_score'] = 0.5
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to parse LLM response: {e}")
            # Return a safe default
            return {
                'transformations': [],
                'confidence': 0.0,
                'safety_score': 0.0,
                'error': str(e)
            }
    
    def get_examples(self) -> list:
        """Extract examples from the POML for testing/validation"""
        if not self.poml_tree:
            return []
        
        root = self.poml_tree.getroot()
        examples = []
        
        for example in root.findall(".//example"):
            intention = example.get('intention', '')
            output = example.find('output')
            
            if output is not None and output.text:
                try:
                    output_json = json.loads(output.text.strip())
                    examples.append({
                        'intention': intention,
                        'expected_output': output_json
                    })
                except json.JSONDecodeError:
                    pass
        
        return examples
    
    def get_governance_principles(self) -> Dict[str, str]:
        """Extract governance principles from the POML"""
        if not self.poml_tree:
            return {}
        
        root = self.poml_tree.getroot()
        principles = {}
        
        governance = root.find(".//governance")
        if governance is not None:
            for principle in governance.findall("principle"):
                name = principle.get('name', 'unknown')
                text = principle.text.strip() if principle.text else ""
                principles[name] = text
        
        return principles


def test_poml_bridge():
    """Test the POML bridge with sample data"""
    print("🌉 Testing POML Bridge")
    print("=" * 60)
    
    # Initialize bridge
    bridge = POMLBridge()
    print("✅ Bridge initialized")
    
    # Test understanding
    understanding = {
        'path': '/etc/nixos/configuration.nix',
        'packages': ['vim', 'git'],
        'services': [],
        'complexity': 0.2
    }
    
    # Build prompt
    prompt = bridge.build_prompt("install firefox", understanding)
    print("\n📝 Generated Prompt (first 500 chars):")
    print(prompt[:500] + "...")
    
    # Get examples
    examples = bridge.get_examples()
    print(f"\n📚 Found {len(examples)} examples in POML")
    
    # Get governance
    principles = bridge.get_governance_principles()
    print(f"\n⚖️ Governance Principles:")
    for name, text in principles.items():
        print(f"  • {name}: {text}")
    
    print("\n✨ POML Bridge test complete!")


if __name__ == "__main__":
    test_poml_bridge()