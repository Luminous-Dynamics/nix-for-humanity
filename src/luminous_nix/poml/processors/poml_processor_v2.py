#!/usr/bin/env python3
"""
POML Processor v2 - Enhanced processor for POML templates

This processor handles loading, variable substitution, conditional logic,
and execution of POML templates with full v2.0 feature support.
"""

import json
import logging
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class POMLFeature(Enum):
    """POML v2.0 features"""

    CONDITIONALS = "conditionals"
    LOOPS = "loops"
    CACHE = "cache"
    PARALLEL = "parallel"
    ERROR_HANDLING = "error_handling"
    ORCHESTRATION = "orchestration"


@dataclass
class POMLContext:
    """Context for POML template execution"""

    variables: dict[str, Any]
    persona: Optional[str] = None
    session_history: list[dict] = None
    cache_enabled: bool = True

    def __post_init__(self):
        if self.session_history is None:
            self.session_history = []


@dataclass
class POMLResult:
    """Result from POML template execution"""

    prompt: str
    metadata: dict[str, Any]
    model_hints: dict[str, Any]
    cache_settings: Optional[dict[str, Any]]
    features_used: list[POMLFeature]


class POMLProcessor:
    """
    Advanced POML processor with full v2.0 support
    """

    def __init__(self, template_dir: Path = None):
        """Initialize processor with template directory"""
        self.logger = logging.getLogger(__name__)

        # Default template directory
        if template_dir is None:
            template_dir = Path(__file__).parent.parent / "templates"

        self.template_dir = template_dir
        self.template_cache = {}

        # Track loaded templates
        self.loaded_templates = set()

        self.logger.info(
            f"POML Processor v2 initialized with templates from {template_dir}"
        )

    def load_template(self, template_name: str) -> ET.Element:
        """Load a POML template by name"""

        # Check cache first
        if template_name in self.template_cache:
            return self.template_cache[template_name]

        # Look for template file
        template_path = self.template_dir / f"{template_name}.poml"
        if not template_path.exists():
            # Try without .poml extension
            template_path = self.template_dir / template_name
            if not template_path.exists():
                raise FileNotFoundError(f"Template not found: {template_name}")

        # Parse XML
        try:
            tree = ET.parse(template_path)
            root = tree.getroot()

            # Cache the template
            self.template_cache[template_name] = root
            self.loaded_templates.add(template_name)

            self.logger.info(f"Loaded POML template: {template_name}")
            return root

        except ET.ParseError as e:
            raise ValueError(f"Failed to parse POML template {template_name}: {e}")

    def process_template(self, template_name: str, context: POMLContext) -> POMLResult:
        """Process a POML template with given context"""

        # Load template
        template = self.load_template(template_name)

        # Track features used
        features_used = []

        # Extract metadata
        metadata = self._extract_metadata(template)

        # Extract model hints
        model_hints = self._extract_model_hints(template)

        # Process variables
        resolved_vars = self._process_variables(template, context.variables)

        # Build the prompt
        prompt_elem = template.find("prompt")
        if prompt_elem is None:
            raise ValueError(f"Template {template_name} missing prompt section")

        # Process the prompt with all features
        prompt_text = self._build_prompt(
            prompt_elem, resolved_vars, context, features_used
        )

        # Extract cache settings
        cache_settings = self._extract_cache_settings(prompt_elem)
        if cache_settings:
            features_used.append(POMLFeature.CACHE)

        return POMLResult(
            prompt=prompt_text,
            metadata=metadata,
            model_hints=model_hints,
            cache_settings=cache_settings,
            features_used=features_used,
        )

    def _extract_metadata(self, template: ET.Element) -> dict[str, Any]:
        """Extract metadata from template"""
        metadata = {}
        metadata_elem = template.find("metadata")

        if metadata_elem is not None:
            for child in metadata_elem:
                if child.text:
                    metadata[child.tag] = child.text.strip()

        return metadata

    def _extract_model_hints(self, template: ET.Element) -> dict[str, Any]:
        """Extract model hints from template"""
        hints = {}
        metadata_elem = template.find("metadata")

        if metadata_elem is not None:
            hints_elem = metadata_elem.find("model-hints")
            if hints_elem is not None:
                for child in hints_elem:
                    if child.text:
                        # Handle different types
                        if child.tag == "temperature" or child.tag == "max-tokens":
                            try:
                                hints[child.tag.replace("-", "_")] = float(child.text)
                            except ValueError:
                                hints[child.tag.replace("-", "_")] = child.text
                        elif child.tag == "preferred-models":
                            hints["preferred_models"] = [
                                m.strip() for m in child.text.split(",")
                            ]
                        else:
                            hints[child.tag.replace("-", "_")] = child.text.strip()

        return hints

    def _process_variables(
        self, template: ET.Element, context_vars: dict[str, Any]
    ) -> dict[str, Any]:
        """Process and resolve variables"""
        resolved = dict(context_vars)  # Start with context variables

        variables_elem = template.find("variables")
        if variables_elem is not None:
            for let_elem in variables_elem.findall("let"):
                name = let_elem.get("name")
                if not name:
                    continue

                # Process variable value
                value_text = let_elem.text or ""

                # Handle template syntax
                value = self._substitute_variables(value_text, resolved)

                # Handle defaults
                if "|" in value and "default:" in value:
                    # Extract default value
                    parts = value.split("|")
                    var_part = parts[0].strip()
                    default_part = parts[1].strip()

                    if "default:" in default_part:
                        default_val = default_part.split("default:")[1].strip()
                        # Remove quotes if present
                        default_val = default_val.strip("\"'")

                        # Use default if variable not in context
                        if var_part == "{{}}" or not var_part:
                            value = default_val

                resolved[name] = value

        return resolved

    def _substitute_variables(self, text: str, variables: dict[str, Any]) -> str:
        """Substitute variables in text"""

        # Handle {{ variable }} syntax
        def replacer(match):
            var_name = match.group(1).strip()

            # Handle nested access (e.g., {{ user.name }})
            if "." in var_name:
                parts = var_name.split(".")
                value = variables.get(parts[0])
                for part in parts[1:]:
                    if isinstance(value, dict):
                        value = value.get(part)
                    else:
                        value = None
                        break
            else:
                value = variables.get(var_name, match.group(0))

            # Convert to string
            if value is not None:
                if isinstance(value, (dict, list)):
                    return json.dumps(value)
                return str(value)

            return match.group(0)  # Return original if not found

        return re.sub(r"\{\{\s*([^}]+)\s*\}\}", replacer, text)

    def _build_prompt(
        self,
        prompt_elem: ET.Element,
        variables: dict[str, Any],
        context: POMLContext,
        features_used: list[POMLFeature],
    ) -> str:
        """Build the complete prompt from prompt element"""

        sections = []

        # Process system prompt
        system_elem = prompt_elem.find("system")
        if system_elem is not None:
            system_text = self._process_element(
                system_elem, variables, context, features_used
            )
            if system_text:
                sections.append(f"System: {system_text}")

        # Process stepwise instructions
        instructions_elem = prompt_elem.find("stepwise-instructions")
        if instructions_elem is not None:
            instructions = self._process_instructions(
                instructions_elem, variables, context, features_used
            )
            if instructions:
                sections.append(f"Instructions:\n{instructions}")

        # Process examples
        examples_elem = prompt_elem.find("examples")
        if examples_elem is not None:
            examples = self._process_examples(examples_elem, variables)
            if examples:
                sections.append(f"Examples:\n{examples}")

        # Process output format
        output_elem = prompt_elem.find("output-format")
        if output_elem is not None:
            output_format = self._process_element(
                output_elem, variables, context, features_used
            )
            if output_format:
                sections.append(f"Output Format:\n{output_format}")

        # Process hints
        hint_elem = prompt_elem.find("hint")
        if hint_elem is not None:
            hint = self._process_element(hint_elem, variables, context, features_used)
            if hint:
                sections.append(f"Hint: {hint}")

        # Add user query if in variables
        if "query" in variables or "user_request" in variables:
            query = variables.get("query") or variables.get("user_request")
            sections.insert(0, f"User Query: {query}")

        return "\n\n".join(sections)

    def _process_element(
        self,
        element: ET.Element,
        variables: dict[str, Any],
        context: POMLContext,
        features_used: list[POMLFeature],
    ) -> str:
        """Process an element with conditionals and variable substitution"""

        # Handle conditional elements
        if element.tag == "if":
            features_used.append(POMLFeature.CONDITIONALS)
            condition = element.get("condition")
            if self._evaluate_condition(condition, variables, context):
                return self._process_children(
                    element, variables, context, features_used
                )
            return ""

        elif element.tag == "elseif":
            features_used.append(POMLFeature.CONDITIONALS)
            condition = element.get("condition")
            if self._evaluate_condition(condition, variables, context):
                return self._process_children(
                    element, variables, context, features_used
                )
            return ""

        elif element.tag == "else":
            features_used.append(POMLFeature.CONDITIONALS)
            return self._process_children(element, variables, context, features_used)

        elif element.tag == "foreach":
            features_used.append(POMLFeature.LOOPS)
            return self._process_foreach(element, variables, context, features_used)

        else:
            # Process text content and children
            text_parts = []

            if element.text:
                text_parts.append(
                    self._substitute_variables(element.text.strip(), variables)
                )

            # Process child elements
            for child in element:
                child_text = self._process_element(
                    child, variables, context, features_used
                )
                if child_text:
                    text_parts.append(child_text)

                # Add tail text after child
                if child.tail:
                    text_parts.append(
                        self._substitute_variables(child.tail.strip(), variables)
                    )

            return " ".join(text_parts)

    def _process_children(
        self,
        element: ET.Element,
        variables: dict[str, Any],
        context: POMLContext,
        features_used: list[POMLFeature],
    ) -> str:
        """Process all children of an element"""
        parts = []

        for child in element:
            text = self._process_element(child, variables, context, features_used)
            if text:
                parts.append(text)

        # Also include direct text
        if element.text:
            parts.insert(0, self._substitute_variables(element.text.strip(), variables))

        return " ".join(parts)

    def _evaluate_condition(
        self, condition: str, variables: dict[str, Any], context: POMLContext
    ) -> bool:
        """Evaluate a conditional expression"""

        if not condition:
            return False

        # Substitute variables in condition
        condition = self._substitute_variables(condition, variables)

        # Add context variables for evaluation
        eval_context = dict(variables)
        eval_context["persona"] = context.persona

        try:
            # Safe evaluation (limited to comparisons and basic logic)
            # This is a simplified evaluator - in production use ast.literal_eval
            # or a proper expression parser

            # Handle simple equality checks
            if "==" in condition:
                parts = condition.split("==")
                left = parts[0].strip().strip("\"'")
                right = parts[1].strip().strip("\"'")
                return left == right

            elif "!=" in condition:
                parts = condition.split("!=")
                left = parts[0].strip().strip("\"'")
                right = parts[1].strip().strip("\"'")
                return left != right

            elif " in " in condition:
                parts = condition.split(" in ")
                item = parts[0].strip().strip("\"'")
                container = parts[1].strip()
                # Safely evaluate container
                if container in eval_context:
                    return item in str(eval_context[container])

            # Default to false for safety
            return False

        except Exception as e:
            self.logger.warning(f"Failed to evaluate condition '{condition}': {e}")
            return False

    def _process_foreach(
        self,
        element: ET.Element,
        variables: dict[str, Any],
        context: POMLContext,
        features_used: list[POMLFeature],
    ) -> str:
        """Process a foreach loop"""

        items_name = element.get("items")
        as_name = element.get("as", "item")

        if not items_name or items_name not in variables:
            return ""

        items = variables.get(items_name, [])
        if not isinstance(items, (list, tuple)):
            items = [items]

        results = []
        for item in items:
            # Create loop variable
            loop_vars = dict(variables)
            loop_vars[as_name] = item

            # Process loop body
            loop_result = self._process_children(
                element, loop_vars, context, features_used
            )
            if loop_result:
                results.append(loop_result)

        return "\n".join(results)

    def _process_instructions(
        self,
        element: ET.Element,
        variables: dict[str, Any],
        context: POMLContext,
        features_used: list[POMLFeature],
    ) -> str:
        """Process stepwise instructions"""

        steps = []
        for step in element.findall("step"):
            step_id = step.get("id", "")
            step_text = self._process_element(step, variables, context, features_used)

            if step_text:
                if step_id:
                    steps.append(f"- [{step_id}] {step_text}")
                else:
                    steps.append(f"- {step_text}")

        return "\n".join(steps)

    def _process_examples(self, element: ET.Element, variables: dict[str, Any]) -> str:
        """Process examples section"""

        examples = []
        for example in element.findall("example"):
            input_elem = example.find("input")
            output_elem = example.find("output")

            if input_elem is not None and output_elem is not None:
                input_text = self._substitute_variables(
                    (input_elem.text or "").strip(), variables
                )
                output_text = self._substitute_variables(
                    (output_elem.text or "").strip(), variables
                )

                examples.append(f"Input: {input_text}\nOutput: {output_text}")

        return "\n\n".join(examples)

    def _extract_cache_settings(
        self, prompt_elem: ET.Element
    ) -> Optional[dict[str, Any]]:
        """Extract cache settings from prompt"""

        cache_elem = prompt_elem.find("cache")
        if cache_elem is not None:
            settings = {}

            # Check if caching is enabled
            enabled = cache_elem.get("enabled", "true").lower() == "true"
            if not enabled:
                return None

            # Get cache parameters
            if cache_elem.get("duration"):
                settings["duration"] = int(cache_elem.get("duration"))

            if cache_elem.get("key"):
                settings["key"] = cache_elem.get("key")

            if cache_elem.get("invalidate-on"):
                settings["invalidate_on"] = cache_elem.get("invalidate-on")

            return settings

        return None

    def list_available_templates(self) -> list[str]:
        """List all available POML templates"""

        templates = []

        if self.template_dir.exists():
            for poml_file in self.template_dir.glob("*.poml"):
                templates.append(poml_file.stem)

        return sorted(templates)

    def get_template_info(self, template_name: str) -> dict[str, Any]:
        """Get information about a template without processing it"""

        template = self.load_template(template_name)

        info = {
            "name": template_name,
            "metadata": self._extract_metadata(template),
            "model_hints": self._extract_model_hints(template),
            "variables": [],
            "features": [],
        }

        # Extract variable names
        variables_elem = template.find("variables")
        if variables_elem is not None:
            for let_elem in variables_elem.findall("let"):
                name = let_elem.get("name")
                if name:
                    info["variables"].append(name)

        # Detect features
        if template.find(".//if") is not None:
            info["features"].append("conditionals")
        if template.find(".//foreach") is not None:
            info["features"].append("loops")
        if template.find(".//cache") is not None:
            info["features"].append("caching")
        if template.find(".//parallel") is not None:
            info["features"].append("parallel")

        return info


def main():
    """Test the POML processor"""

    # Initialize processor
    processor = POMLProcessor()

    # List available templates
    templates = processor.list_available_templates()
    print(f"Available templates: {templates}")

    # Test with a sample context
    context = POMLContext(
        variables={
            "user_request": "install firefox",
            "available_intents": [
                "install_package",
                "remove_package",
                "search_package",
            ],
            "persona": "developer",
        },
        persona="developer",
    )

    # Process a template
    try:
        result = processor.process_template("intent_classification", context)
        print(f"\nProcessed prompt:\n{result.prompt}")
        print(f"\nModel hints: {result.model_hints}")
        print(f"Features used: {result.features_used}")
    except FileNotFoundError:
        print("Template not found - this is expected in testing")


if __name__ == "__main__":
    main()
