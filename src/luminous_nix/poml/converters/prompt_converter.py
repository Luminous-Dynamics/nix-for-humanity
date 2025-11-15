#!/usr/bin/env python3
"""
Prompt Converter - Convert existing string prompts to POML format

This tool identifies and converts existing string-based prompts
in the codebase to proper POML templates following the style guide.
"""

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class PromptLocation:
    """Represents a prompt found in the codebase"""

    file_path: Path
    line_number: int
    prompt_text: str
    context_type: str  # 'system', 'user', 'classification', etc.
    variables: list[str]  # Variables found in the prompt


class PromptToPomlConverter:
    """Convert string prompts to POML templates"""

    def __init__(self, output_dir: Path):
        """Initialize converter with output directory"""
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Track conversions
        self.conversions = []

    def find_prompts_in_file(self, file_path: Path) -> list[PromptLocation]:
        """Find all prompts in a Python file"""
        prompts = []

        try:
            content = file_path.read_text()
            lines = content.split("\n")

            # Patterns to find prompts
            patterns = [
                (r'prompt\s*=\s*["\']', "general"),
                (r'system_prompt\s*=\s*["\']', "system"),
                (r'user_prompt\s*=\s*["\']', "user"),
                (r'PROMPT\s*=\s*["\']', "constant"),
                (r'f""".*You are.*"""', "system"),
                (r'""".*Classify.*"""', "classification"),
            ]

            for i, line in enumerate(lines, 1):
                for pattern, context_type in patterns:
                    if re.search(pattern, line):
                        # Extract the full prompt (handle multi-line)
                        prompt_text = self._extract_prompt(lines, i - 1)
                        if prompt_text:
                            # Find variables
                            variables = self._extract_variables(prompt_text)

                            prompts.append(
                                PromptLocation(
                                    file_path=file_path,
                                    line_number=i,
                                    prompt_text=prompt_text,
                                    context_type=context_type,
                                    variables=variables,
                                )
                            )

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return prompts

    def _extract_prompt(self, lines: list[str], start_idx: int) -> Optional[str]:
        """Extract full prompt text (handles multi-line strings)"""
        prompt = []
        in_string = False
        string_delimiter = None

        for i in range(start_idx, min(start_idx + 50, len(lines))):
            line = lines[i]

            # Check for string start
            if not in_string:
                # Look for triple quotes
                if '"""' in line or "'''" in line:
                    string_delimiter = '"""' if '"""' in line else "'''"
                    in_string = True
                    # Extract content after opening quotes
                    parts = line.split(string_delimiter)
                    if len(parts) > 1:
                        prompt.append(parts[1])
                    if len(parts) > 2:  # Closing quotes on same line
                        return parts[1]
                # Look for single quotes
                elif '"' in line or "'" in line:
                    # Extract string content
                    match = re.search(r'["\']([^"\']+)["\']', line)
                    if match:
                        return match.group(1)
            else:
                # Look for closing delimiter
                if string_delimiter in line:
                    parts = line.split(string_delimiter)
                    prompt.append(parts[0])
                    return "\n".join(prompt)
                else:
                    prompt.append(line)

        return "\n".join(prompt) if prompt else None

    def _extract_variables(self, prompt_text: str) -> list[str]:
        """Extract variables from prompt text"""
        variables = []

        # f-string style: {variable}
        f_string_vars = re.findall(r"\{(\w+)\}", prompt_text)
        variables.extend(f_string_vars)

        # Template style: {{ variable }}
        template_vars = re.findall(r"\{\{\s*(\w+)\s*\}\}", prompt_text)
        variables.extend(template_vars)

        return list(set(variables))

    def convert_to_poml(self, prompt_location: PromptLocation) -> ET.Element:
        """Convert a prompt to POML format"""

        # Create root POML element
        root = ET.Element("poml")
        root.set("version", "2.0")
        root.set("xmlns", "http://schemas.microsoft.com/poml/2024")

        # Add metadata
        metadata = ET.SubElement(root, "metadata")
        ET.SubElement(metadata, "title").text = self._generate_title(prompt_location)
        ET.SubElement(metadata, "description").text = self._generate_description(
            prompt_location
        )
        ET.SubElement(metadata, "author").text = "Luminous Nix Team (Auto-converted)"
        ET.SubElement(metadata, "version").text = "1.0.0"

        # Add model hints based on context
        model_hints = ET.SubElement(metadata, "model-hints")
        self._add_model_hints(model_hints, prompt_location)

        # Add variables if found
        if prompt_location.variables:
            variables = ET.SubElement(root, "variables")
            for var in prompt_location.variables:
                let = ET.SubElement(variables, "let")
                let.set("name", var)
                let.text = f"{{{{ {var} }}}}"

        # Add prompt section
        prompt = ET.SubElement(root, "prompt")

        # Determine prompt structure based on context
        if prompt_location.context_type in ["system", "general"]:
            self._add_system_prompt(prompt, prompt_location)

        # Add structured content
        self._add_structured_content(prompt, prompt_location)

        # Add examples if applicable
        if "example" in prompt_location.prompt_text.lower():
            self._add_examples(prompt, prompt_location)

        # Add output format
        self._add_output_format(prompt, prompt_location)

        return root

    def _generate_title(self, prompt_location: PromptLocation) -> str:
        """Generate a title for the POML template"""
        # Extract from file name and context
        file_name = prompt_location.file_path.stem

        if "intent" in file_name.lower():
            return "Intent Recognition"
        elif "error" in file_name.lower():
            return "Error Resolution"
        elif "ollama" in file_name.lower():
            return "NixOS Assistant Query"
        else:
            return f'{file_name.replace("_", " ").title()} Prompt'

    def _generate_description(self, prompt_location: PromptLocation) -> str:
        """Generate description based on prompt content"""
        prompt_text = prompt_location.prompt_text.lower()

        if "classify" in prompt_text or "intent" in prompt_text:
            return "Classify user intent for NixOS operations"
        elif "error" in prompt_text:
            return "Analyze and resolve NixOS errors"
        elif "package" in prompt_text:
            return "Process NixOS package management queries"
        else:
            return "Process NixOS-related queries"

    def _add_model_hints(
        self, model_hints: ET.Element, prompt_location: PromptLocation
    ):
        """Add appropriate model hints based on prompt context"""
        prompt_text = prompt_location.prompt_text.lower()

        # Determine best models
        if "classify" in prompt_text or "json" in prompt_text:
            # Classification needs lower temperature
            ET.SubElement(
                model_hints, "preferred-models"
            ).text = "gpt-3.5-turbo, mistral-7b"
            ET.SubElement(model_hints, "temperature").text = "0.3"
            ET.SubElement(model_hints, "max-tokens").text = "500"
        elif "explain" in prompt_text:
            # Explanations need more tokens
            ET.SubElement(model_hints, "preferred-models").text = "gpt-4, claude-3"
            ET.SubElement(model_hints, "temperature").text = "0.7"
            ET.SubElement(model_hints, "max-tokens").text = "1500"
        else:
            # General purpose
            ET.SubElement(
                model_hints, "preferred-models"
            ).text = "gpt-3.5-turbo, mistral-7b, llama-2"
            ET.SubElement(model_hints, "temperature").text = "0.5"
            ET.SubElement(model_hints, "max-tokens").text = "1000"

    def _add_system_prompt(self, prompt: ET.Element, prompt_location: PromptLocation):
        """Add system prompt section"""
        system = ET.SubElement(prompt, "system")

        # Extract system portion from prompt
        if "You are" in prompt_location.prompt_text:
            # Extract the "You are..." portion
            match = re.search(r"You are[^.]*\.", prompt_location.prompt_text)
            if match:
                system.text = match.group(0)
            else:
                system.text = "You are a helpful NixOS assistant."
        else:
            # Default system prompt based on context
            if "intent" in prompt_location.file_path.stem:
                system.text = (
                    "You are an intent classification expert for NixOS operations."
                )
            else:
                system.text = "You are a helpful NixOS assistant."

    def _add_structured_content(
        self, prompt: ET.Element, prompt_location: PromptLocation
    ):
        """Add structured content (stepwise instructions, etc.)"""
        prompt_text = prompt_location.prompt_text

        # Look for numbered lists or structured instructions
        if re.search(r"\d+\.|\-\s+", prompt_text):
            instructions = ET.SubElement(prompt, "stepwise-instructions")

            # Extract steps
            steps = re.findall(r"(?:\d+\.|[-*])\s*([^\n]+)", prompt_text)
            for i, step_text in enumerate(steps, 1):
                step = ET.SubElement(instructions, "step")
                step.set("id", f"step_{i}")
                step.text = step_text.strip()

    def _add_examples(self, prompt: ET.Element, prompt_location: PromptLocation):
        """Extract and add examples from prompt"""
        examples_elem = ET.SubElement(prompt, "examples")

        # Look for example patterns
        example_matches = re.findall(
            r'["\']([^"\']+)["\'].*->.*["\']([^"\']+)["\']', prompt_location.prompt_text
        )

        for input_text, output_text in example_matches:
            example = ET.SubElement(examples_elem, "example")
            ET.SubElement(example, "input").text = input_text
            ET.SubElement(example, "output").text = output_text

    def _add_output_format(self, prompt: ET.Element, prompt_location: PromptLocation):
        """Add output format specification"""
        prompt_text = prompt_location.prompt_text

        # Check if JSON output is expected
        if "json" in prompt_text.lower() or "{" in prompt_text:
            output_format = ET.SubElement(prompt, "output-format")

            # Try to extract JSON schema
            json_match = re.search(r"\{[^}]+\}", prompt_text, re.DOTALL)
            if json_match:
                output_format.text = json_match.group(0)
            else:
                output_format.text = "Structured JSON response"

    def save_poml(self, poml_element: ET.Element, name: str) -> Path:
        """Save POML element to file"""
        # Create file path
        file_path = self.output_dir / f"{name}.poml"

        # Pretty print
        self._indent(poml_element)

        # Create tree and write
        tree = ET.ElementTree(poml_element)
        tree.write(file_path, encoding="utf-8", xml_declaration=True)

        # Add proper formatting (ET doesn't preserve formatting well)
        content = file_path.read_text()
        formatted_content = content.replace("><", ">\n<")
        file_path.write_text(formatted_content)

        return file_path

    def _indent(self, elem, level=0):
        """Add pretty printing to XML"""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                self._indent(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def convert_file(self, file_path: Path) -> list[Path]:
        """Convert all prompts in a file to POML"""
        converted = []

        # Find prompts
        prompts = self.find_prompts_in_file(file_path)

        for i, prompt_loc in enumerate(prompts):
            # Convert to POML
            poml = self.convert_to_poml(prompt_loc)

            # Generate name
            name = f"{file_path.stem}_{i+1}"

            # Save POML
            saved_path = self.save_poml(poml, name)
            converted.append(saved_path)

            # Track conversion
            self.conversions.append(
                {
                    "original_file": str(prompt_loc.file_path),
                    "line_number": prompt_loc.line_number,
                    "poml_file": str(saved_path),
                    "variables": prompt_loc.variables,
                }
            )

            print(
                f"✅ Converted prompt at {file_path.name}:{prompt_loc.line_number} -> {saved_path.name}"
            )

        return converted

    def generate_report(self) -> str:
        """Generate conversion report"""
        report = [
            "# POML Conversion Report",
            f"Total prompts converted: {len(self.conversions)}",
            "",
            "## Conversions:",
        ]

        for conv in self.conversions:
            report.append(
                f"- {conv['original_file']}:{conv['line_number']} -> {conv['poml_file']}"
            )
            if conv["variables"]:
                report.append(f"  Variables: {', '.join(conv['variables'])}")

        return "\n".join(report)


def main():
    """Convert all prompts in the codebase to POML"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert string prompts to POML format"
    )
    parser.add_argument("source", type=Path, help="Source file or directory")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("converted_prompts"),
        help="Output directory",
    )
    parser.add_argument(
        "--report", action="store_true", help="Generate conversion report"
    )

    args = parser.parse_args()

    converter = PromptToPomlConverter(args.output)

    if args.source.is_file():
        converted = converter.convert_file(args.source)
        print(f"\n✨ Converted {len(converted)} prompts from {args.source.name}")
    else:
        # Convert all Python files in directory
        for py_file in args.source.rglob("*.py"):
            converter.convert_file(py_file)

        print(f"\n✨ Total conversions: {len(converter.conversions)}")

    if args.report:
        report = converter.generate_report()
        report_path = args.output / "conversion_report.md"
        report_path.write_text(report)
        print(f"\n📄 Report saved to {report_path}")


if __name__ == "__main__":
    main()
