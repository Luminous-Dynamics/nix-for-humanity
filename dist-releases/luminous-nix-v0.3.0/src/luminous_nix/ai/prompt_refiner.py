#!/usr/bin/env python3
"""
Prompt Refinement System

This module improves AI prompts to reduce hallucinations and increase accuracy.
It uses:
- Context injection from the corpus
- Fact verification
- Response validation
- Confidence scoring
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

from rich.console import Console


class PromptType(Enum):
    """Types of prompts we handle"""
    INSTALL_PACKAGE = "install_package"
    CONFIGURE_SERVICE = "configure_service"
    TROUBLESHOOT = "troubleshoot"
    EXPLAIN = "explain"
    GENERATE_CONFIG = "generate_config"
    GENERAL_QUESTION = "general_question"


@dataclass
class RefinedPrompt:
    """A refined prompt with context and constraints"""
    original: str
    refined: str
    context: List[str]
    constraints: List[str]
    examples: List[str]
    confidence: float
    prompt_type: PromptType
    
    def to_ollama_format(self) -> str:
        """Convert to format for Ollama"""
        prompt = f"""You are a NixOS expert assistant. IMPORTANT: Only provide accurate, verified information about NixOS.

CONTEXT:
{chr(10).join(self.context)}

CONSTRAINTS:
{chr(10).join(f'• {c}' for c in self.constraints)}

USER QUESTION: {self.refined}

{f"EXAMPLES:{chr(10)}{chr(10).join(self.examples)}" if self.examples else ""}

Please provide an accurate, helpful response. If you're not certain about something, say so."""
        
        return prompt


class PromptRefiner:
    """
    Refines prompts to reduce hallucinations
    
    Features:
    - Adds relevant context from corpus
    - Injects constraints to prevent hallucination
    - Provides examples for better understanding
    - Validates responses
    """
    
    def __init__(self, corpus_dir: str = "corpus"):
        """Initialize the refiner"""
        self.corpus_dir = Path(corpus_dir)
        self.console = Console()
        
        # Load corpus data
        self.documents = self._load_corpus_documents()
        self.qa_pairs = self._load_qa_pairs()
        
        # Pattern matchers for intent detection
        self.patterns = {
            PromptType.INSTALL_PACKAGE: [
                r"install\s+(\w+)",
                r"add\s+(\w+)",
                r"get\s+(\w+)",
                r"setup\s+(\w+)"
            ],
            PromptType.CONFIGURE_SERVICE: [
                r"enable\s+(\w+)",
                r"configure\s+(\w+)",
                r"setup\s+(\w+)\s+service",
                r"start\s+(\w+)"
            ],
            PromptType.TROUBLESHOOT: [
                r"error",
                r"fail",
                r"not working",
                r"broken",
                r"fix"
            ],
            PromptType.EXPLAIN: [
                r"what is",
                r"how does",
                r"explain",
                r"tell me about"
            ],
            PromptType.GENERATE_CONFIG: [
                r"generate.*config",
                r"create.*configuration",
                r"write.*nix"
            ]
        }
    
    def refine_prompt(self, user_input: str) -> RefinedPrompt:
        """Refine a user prompt to reduce hallucinations"""
        
        # Detect prompt type
        prompt_type = self._detect_prompt_type(user_input)
        
        # Get relevant context
        context = self._get_relevant_context(user_input, prompt_type)
        
        # Generate constraints
        constraints = self._generate_constraints(prompt_type)
        
        # Find relevant examples
        examples = self._find_examples(user_input, prompt_type)
        
        # Refine the prompt
        refined = self._refine_text(user_input, prompt_type)
        
        # Calculate confidence
        confidence = self._calculate_confidence(user_input, context, examples)
        
        return RefinedPrompt(
            original=user_input,
            refined=refined,
            context=context,
            constraints=constraints,
            examples=examples,
            confidence=confidence,
            prompt_type=prompt_type
        )
    
    def _load_corpus_documents(self) -> List[Dict[str, Any]]:
        """Load corpus documents"""
        documents = []
        
        docs_file = self.corpus_dir / "documents.jsonl"
        if docs_file.exists():
            with open(docs_file, 'r') as f:
                for line in f:
                    documents.append(json.loads(line))
        
        return documents
    
    def _load_qa_pairs(self) -> List[Dict[str, Any]]:
        """Load Q&A pairs"""
        qa_pairs = []
        
        qa_file = self.corpus_dir / "qa_pairs.jsonl"
        if qa_file.exists():
            with open(qa_file, 'r') as f:
                for line in f:
                    qa_pairs.append(json.loads(line))
        
        return qa_pairs
    
    def _detect_prompt_type(self, user_input: str) -> PromptType:
        """Detect the type of prompt"""
        
        user_input_lower = user_input.lower()
        
        for prompt_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input_lower):
                    return prompt_type
        
        return PromptType.GENERAL_QUESTION
    
    def _get_relevant_context(self, user_input: str, prompt_type: PromptType) -> List[str]:
        """Get relevant context from corpus"""
        
        context = []
        user_input_lower = user_input.lower()
        
        # Always add NixOS basics
        context.append("NixOS is a Linux distribution built on the Nix package manager. Configuration is declarative in configuration.nix.")
        
        # Add type-specific context
        if prompt_type == PromptType.INSTALL_PACKAGE:
            context.append("Packages can be installed with: nix-env -iA nixos.package, or added to environment.systemPackages in configuration.nix")
            
            # Find specific package info
            for doc in self.documents:
                if doc.get("metadata", {}).get("category") == "packages":
                    for keyword in doc.get("metadata", {}).get("keywords", []):
                        if keyword in user_input_lower:
                            context.append(doc["text"])
                            break
        
        elif prompt_type == PromptType.CONFIGURE_SERVICE:
            context.append("Services are configured in configuration.nix under the 'services' attribute set.")
            
            # Find specific service info
            for doc in self.documents:
                if doc.get("metadata", {}).get("category") == "services":
                    if any(keyword in user_input_lower for keyword in doc.get("metadata", {}).get("keywords", [])):
                        context.append(doc["text"])
        
        elif prompt_type == PromptType.TROUBLESHOOT:
            context.append("Common troubleshooting: Check nixos-rebuild test for errors, view logs with journalctl, check disk space with df -h")
        
        return context[:5]  # Limit context to avoid overwhelming
    
    def _generate_constraints(self, prompt_type: PromptType) -> List[str]:
        """Generate constraints to prevent hallucination"""
        
        constraints = [
            "Only provide commands and configurations that actually work in NixOS",
            "If unsure about exact syntax, provide the general pattern",
            "Do not invent package names or options that don't exist",
            "Stick to standard NixOS practices and patterns"
        ]
        
        if prompt_type == PromptType.INSTALL_PACKAGE:
            constraints.append("Only suggest packages that exist in nixpkgs")
            constraints.append("Always show both nix-env and configuration.nix methods")
        
        elif prompt_type == PromptType.CONFIGURE_SERVICE:
            constraints.append("Only reference real NixOS service options")
            constraints.append("Always mention that changes require nixos-rebuild switch")
        
        elif prompt_type == PromptType.GENERATE_CONFIG:
            constraints.append("Generate valid Nix syntax only")
            constraints.append("Include comments explaining each section")
        
        return constraints
    
    def _find_examples(self, user_input: str, prompt_type: PromptType) -> List[str]:
        """Find relevant examples from corpus"""
        
        examples = []
        
        # Search Q&A pairs for similar questions
        for qa in self.qa_pairs:
            if self._similarity(user_input, qa["instruction"]) > 0.5:
                examples.append(f"Q: {qa['instruction']}\nA: {qa['output']}")
                if len(examples) >= 2:
                    break
        
        # Add type-specific examples
        if prompt_type == PromptType.INSTALL_PACKAGE and not examples:
            examples.append("Q: How do I install firefox?\nA: Run: nix-env -iA nixos.firefox\nOr add to configuration.nix: environment.systemPackages = with pkgs; [ firefox ];")
        
        elif prompt_type == PromptType.CONFIGURE_SERVICE and not examples:
            examples.append("Q: How do I enable SSH?\nA: Add to configuration.nix:\nservices.openssh.enable = true;\nThen run: sudo nixos-rebuild switch")
        
        return examples[:3]
    
    def _refine_text(self, user_input: str, prompt_type: PromptType) -> str:
        """Refine the user's text for clarity"""
        
        refined = user_input
        
        # Add clarifications based on type
        if prompt_type == PromptType.INSTALL_PACKAGE:
            if "install" not in user_input.lower():
                refined = f"How do I install {user_input} on NixOS?"
        
        elif prompt_type == PromptType.CONFIGURE_SERVICE:
            if "enable" not in user_input.lower() and "configure" not in user_input.lower():
                refined = f"How do I configure {user_input} service on NixOS?"
        
        # Ensure it's a clear question
        if not refined.endswith("?") and prompt_type in [PromptType.EXPLAIN, PromptType.GENERAL_QUESTION]:
            refined += "?"
        
        return refined
    
    def _calculate_confidence(self, user_input: str, context: List[str], examples: List[str]) -> float:
        """Calculate confidence in our ability to answer accurately"""
        
        confidence = 0.5  # Base confidence
        
        # Increase confidence if we have relevant context
        if context:
            confidence += 0.2 * min(len(context) / 3, 1.0)
        
        # Increase confidence if we have examples
        if examples:
            confidence += 0.2 * min(len(examples) / 2, 1.0)
        
        # Decrease confidence for vague queries
        vague_terms = ["something", "stuff", "thing", "whatever", "somehow"]
        if any(term in user_input.lower() for term in vague_terms):
            confidence -= 0.2
        
        # Increase confidence for specific package/service names
        known_packages = ["firefox", "vim", "git", "python", "nodejs", "docker"]
        if any(pkg in user_input.lower() for pkg in known_packages):
            confidence += 0.1
        
        return max(0.1, min(1.0, confidence))
    
    def _similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity calculation"""
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def validate_response(self, response: str, prompt_type: PromptType) -> Dict[str, Any]:
        """Validate an AI response for accuracy"""
        
        validation = {
            "valid": True,
            "issues": [],
            "suggestions": []
        }
        
        # Check for common hallucination patterns
        hallucination_patterns = [
            r"nix-env -i\s+[A-Z]",  # Capital letters in package names (unusual)
            r"services\.\w+\.\w+\.\w+\.\w+",  # Too deeply nested options
            r"/etc/nix/.*\.conf",  # Wrong config paths
            r"sudo nix-env",  # nix-env shouldn't need sudo
        ]
        
        for pattern in hallucination_patterns:
            if re.search(pattern, response):
                validation["valid"] = False
                validation["issues"].append(f"Suspicious pattern detected: {pattern}")
        
        # Check for required elements based on type
        if prompt_type == PromptType.INSTALL_PACKAGE:
            if "nix-env -iA" not in response and "environment.systemPackages" not in response:
                validation["suggestions"].append("Should mention installation methods")
        
        elif prompt_type == PromptType.CONFIGURE_SERVICE:
            if "nixos-rebuild" not in response:
                validation["suggestions"].append("Should mention nixos-rebuild switch")
        
        # Check for impossible claims
        impossible_claims = [
            "will automatically",
            "installs everything",
            "no configuration needed",
            "works on all systems"
        ]
        
        for claim in impossible_claims:
            if claim in response.lower():
                validation["issues"].append(f"Overly broad claim: '{claim}'")
                validation["valid"] = False
        
        return validation


class SmartOllamaClient:
    """
    Smarter Ollama client with prompt refinement
    """
    
    def __init__(self):
        """Initialize the smart client"""
        self.refiner = PromptRefiner()
        self.console = Console()
        
        # Try to import Ollama
        try:
            from ..ollama_integration import ollama_client
            self.ollama = ollama_client
        except ImportError:
            self.ollama = None
    
    def ask(self, question: str, validate: bool = True) -> Dict[str, Any]:
        """Ask a question with refined prompting"""
        
        # Refine the prompt
        refined_prompt = self.refiner.refine_prompt(question)
        
        # Show confidence
        if refined_prompt.confidence < 0.5:
            self.console.print(f"[yellow]⚠ Low confidence ({refined_prompt.confidence:.0%}) - answer may be less accurate[/yellow]")
        
        # Get response from Ollama
        if self.ollama and self.ollama.is_available():
            response = self.ollama.generate(
                refined_prompt.to_ollama_format(),
                model="mistral"
            )
            
            answer = response.get("response", "")
            
            # Validate if requested
            if validate:
                validation = self.refiner.validate_response(answer, refined_prompt.prompt_type)
                
                if not validation["valid"]:
                    self.console.print("[red]⚠ Response may contain inaccuracies[/red]")
                    for issue in validation["issues"]:
                        self.console.print(f"  • {issue}")
                
                return {
                    "question": question,
                    "answer": answer,
                    "confidence": refined_prompt.confidence,
                    "validation": validation,
                    "context_used": len(refined_prompt.context) > 0
                }
            
            return {
                "question": question,
                "answer": answer,
                "confidence": refined_prompt.confidence,
                "context_used": len(refined_prompt.context) > 0
            }
        
        else:
            # Fallback to corpus-based answer
            for qa in self.refiner.qa_pairs:
                if self.refiner._similarity(question, qa["instruction"]) > 0.7:
                    return {
                        "question": question,
                        "answer": qa["output"],
                        "confidence": 0.8,
                        "source": "corpus"
                    }
            
            return {
                "question": question,
                "answer": "I don't have enough information to answer that accurately.",
                "confidence": 0.0
            }


def main():
    """Test the prompt refiner"""
    client = SmartOllamaClient()
    
    test_questions = [
        "How do I install Firefox?",
        "Enable SSH service",
        "My build is failing",
        "What is NixOS?",
        "Create a web server configuration"
    ]
    
    for question in test_questions:
        print(f"\n📝 Question: {question}")
        result = client.ask(question)
        print(f"🤖 Answer: {result['answer'][:200]}...")
        print(f"📊 Confidence: {result.get('confidence', 0):.0%}")
        
        if result.get("validation") and not result["validation"]["valid"]:
            print("⚠️  Validation issues detected!")


if __name__ == "__main__":
    main()