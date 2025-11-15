"""
Ollama integration for AI-powered natural language understanding
"""

import json
import os
import subprocess
from typing import Any


class OllamaClient:
    """Client for interacting with Ollama AI models"""

    def __init__(self):
        """Initialize Ollama client with BEST models for each task"""
        # Optimized model selection based on what we have:
        # - gemma3:12b (8.1GB) - BEST for complex reasoning
        # - mistral:7b (4.4GB) - EXCELLENT general purpose
        # - gemma3:4b (3.3GB) - Good balance of speed/quality
        # - qwen2.5:3b (1.9GB) - Fast and smart
        # - gemma3:1b (815MB) - Quick responses
        # - tinyllama:1.1b (637MB) - Optimized for conversation

        self.models = {
            # Task-specific optimal models
            "conversation": "mistral:7b",  # BEST for natural conversation (4.4GB)
            "expert": "gemma3:12b",  # BEST for complex questions (8.1GB)
            "coder": "gemma3:4b",  # Good for code/config (3.3GB)
            "general": "qwen2.5:3b",  # Fast general purpose (1.9GB)
            "quick": "tinyllama:1.1b",  # Quick responses (637MB)
            "empathy": "gemma3:1b",  # User support (815MB)
            "nixos": "nixos-commands:latest",  # NixOS specific (291MB)
            "tiny": "qwen:0.5b",  # Ultra-fast fallback (394MB)
        }

        # Default to conversation model for best experience
        self.default_model = self.models["conversation"]
        self.timeout = 15  # Reasonable timeout for quality responses

    def is_available(self) -> bool:
        """Check if Ollama is installed and running"""
        try:
            # Try to list models - this is a quick check
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=2
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _select_default_model(self) -> str:
        """Select best model based on system resources"""
        # For now, use the quick NixOS model as default
        # In future, could check available RAM/GPU
        return self.models.get("quick", "qwen:0.5b")

    def _select_model_for_query(self, query: str) -> str:
        """Select the BEST model based on query type"""
        query_lower = query.lower()

        # Conversational queries - use best conversational model
        if any(
            word in query_lower
            for word in [
                "best",
                "recommend",
                "should i",
                "what do you think",
                "suggest",
            ]
        ):
            return self.models[
                "conversation"
            ]  # mistral:7b for intelligent conversation

        # Complex reasoning - use the most powerful model
        if any(
            word in query_lower
            for word in ["explain", "how does", "why", "compare", "difference between"]
        ):
            return self.models["expert"]  # gemma3:12b for deep reasoning

        # Code/config queries - use specialized coder
        if any(
            word in query_lower
            for word in [
                "config",
                "configuration",
                "code",
                "script",
                "flake",
                "nix expression",
            ]
        ):
            return self.models["coder"]  # gemma3:4b for code understanding

        # NixOS specific - use specialized model
        if any(
            word in query_lower
            for word in ["nixos", "nix-env", "nix profile", "nixpkgs"]
        ):
            return self.models["nixos"]  # nixos-commands:latest

        # Quick actions - use fast model
        if any(word in query_lower for word in ["install", "remove", "list", "search"]):
            return self.models["quick"]  # tinyllama for speed

        # Error/help queries - use empathetic model
        if any(
            word in query_lower
            for word in ["error", "help", "broken", "not working", "failed"]
        ):
            return self.models["empathy"]  # gemma3:1b for supportive responses

        # System queries - use expert
        if any(
            word in query_lower
            for word in ["kernel", "driver", "boot", "systemd", "hardware"]
        ):
            return self.models["expert"]  # gemma3:12b for technical depth

        # Default to general purpose model for good balance
        return self.models["general"]  # qwen2.5:3b

    def ask(
        self, prompt: str, model: str | None = None, context: dict | None = None
    ) -> str | None:
        """
        Ask Ollama a question and get a response

        Args:
            prompt: The question or command to process
            model: Optional specific model to use
            context: Optional context about the user/system

        Returns:
            The AI response or None if failed
        """
        # Select model if not specified
        if not model:
            model = self._select_model_for_query(prompt)

        # Build the full prompt with context
        full_prompt = self._build_prompt(prompt, context)

        try:
            # Use ollama run command for simplicity
            result = subprocess.run(
                ["ollama", "run", model, full_prompt],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode == 0 and result.stdout:
                return result.stdout.strip()
            # Fallback to simpler model if failed
            if model != self.models["tiny"]:
                return self.ask(prompt, model=self.models["tiny"], context=context)
            return None

        except subprocess.TimeoutExpired:
            print("⏱️ AI response timed out, trying faster model...")
            if model != self.models["tiny"]:
                return self.ask(prompt, model=self.models["tiny"], context=context)
            return None

        except Exception as e:
            if os.environ.get("LUMINOUS_VERBOSE"):
                print(f"❌ Ollama error: {e}")
            return None

    def _build_prompt(self, prompt: str, context: dict | None = None) -> str:
        """Build a contextualized prompt for better AI responses"""

        # System prompt optimized for NixOS assistance
        full_prompt = """You are Luminous Nix, an intelligent NixOS assistant.
You help users with package management, system configuration, and troubleshooting.
Be conversational, helpful, and informative.

When users ask about "best" options, provide comparisons and recommendations.
For example, if asked about browsers, explain the options (Firefox, Chromium, Brave) with pros/cons.

"""

        # Add persona context if specified
        if context and "persona" in context:
            persona_prompts = {
                "grandma": "Explain things simply and gently, avoiding technical jargon. ",
                "developer": "Provide technical details and code examples. ",
                "beginner": "Explain step by step with clear examples. ",
                "expert": "Be concise and technical. ",
            }
            full_prompt += persona_prompts.get(context["persona"], "")

        # Add the user's question
        full_prompt += f"User: {prompt}\n\nAssistant: "

        return full_prompt

    def parse_intent(self, query: str) -> dict[str, Any]:
        """
        Use AI to understand the user's intent

        Returns:
            Dictionary with:
            - intent: The primary intent (install, search, configure, etc.)
            - entities: Extracted entities (package names, etc.)
            - confidence: How confident the AI is
            - suggestion: What to do next
        """
        # Skip AI for now since it's not properly trained
        # Just use our improved basic parsing
        return self._basic_intent_parsing(query)

        # Original AI code (disabled until model is trained):
        # prompt = f"""Analyze this NixOS query and return JSON with: intent, entities, confidence, suggestion.
        # Query: {query}
        #
        # Example response:
        # {{"intent": "install", "entities": ["firefox"], "confidence": 0.9, "suggestion": "Install Firefox browser"}}
        #
        # Response:"""
        #
        # response = self.ask(prompt, model=self.models["tiny"])
        #
        # if response:
        #     try:
        #         # Try to parse JSON from response
        #         import re
        #
        #         json_match = re.search(r"\{.*\}", response, re.DOTALL)
        #         if json_match:
        #             return json.loads(json_match.group())
        #     except:
        #         pass
        #
        # # Fallback to basic parsing
        # return self._basic_intent_parsing(query)

    def _basic_intent_parsing(self, query: str) -> dict[str, Any]:
        """Fallback basic intent parsing without AI"""
        query_lower = query.lower()

        if "install" in query_lower:
            return {
                "intent": "install",
                "entities": self._extract_package_name(query_lower, "install"),
                "confidence": 0.7,
                "suggestion": "Install package",
            }
        if "search" in query_lower or "find" in query_lower:
            return {
                "intent": "search",
                "entities": self._extract_search_term(query_lower),
                "confidence": 0.7,
                "suggestion": "Search for packages",
            }
        if "remove" in query_lower or "uninstall" in query_lower:
            return {
                "intent": "remove",
                "entities": self._extract_package_name(query_lower, "remove"),
                "confidence": 0.7,
                "suggestion": "Remove package",
            }
        return {
            "intent": "unknown",
            "entities": [],
            "confidence": 0.3,
            "suggestion": "Please clarify what you want to do",
        }

    def _extract_package_name(self, query: str, action: str) -> list[str]:
        """Extract package name from query"""
        query_lower = query.lower()

        # Check for common descriptions FIRST - before word extraction
        # This catches phrases anywhere in the query
        if "web browser" in query_lower or (
            "browser" in query_lower and "web" not in ["how", "do", "i"]
        ):
            return ["firefox"]
        elif "text editor" in query_lower or (
            "editor" in query_lower and "text" not in ["how", "do", "i"]
        ):
            return ["vim"]
        elif "terminal" in query_lower:
            return ["alacritty"]
        elif "video player" in query_lower:
            return ["vlc"]
        elif "music player" in query_lower:
            return ["spotify"]
        elif "pdf reader" in query_lower or "pdf viewer" in query_lower:
            return ["zathura"]
        elif "image editor" in query_lower or "photo editor" in query_lower:
            return ["gimp"]
        elif "file manager" in query_lower:
            return ["ranger"]
        elif "password manager" in query_lower:
            return ["bitwarden"]
        elif "ide" in query_lower:
            return ["vscode"]
        elif "email" in query_lower and "client" in query_lower:
            return ["thunderbird"]

        # If no description matches, try word extraction
        words = query.split()
        packages = []

        # Find the action word
        if action in words:
            idx = words.index(action)
            # Get everything after the action word
            remaining = words[idx + 1 :]

            # Filter out articles and common words
            ignore = {
                "a",
                "an",
                "the",
                "some",
                "for",
                "to",
                "please",
                "how",
                "do",
                "i",
                "can",
                "you",
            }

            # Build the remaining text and check again for descriptions
            remaining_text = " ".join(remaining).lower()
            if "text editor" in remaining_text:
                return ["vim"]
            elif "web browser" in remaining_text:
                return ["firefox"]
            elif "video player" in remaining_text:
                return ["vlc"]
            elif "music player" in remaining_text:
                return ["spotify"]

            # Otherwise take the first non-ignored word
            for word in remaining:
                if word not in ignore:
                    packages.append(word)
                    break  # Take first non-ignored word

        return packages

    def _extract_search_term(self, query: str) -> list[str]:
        """Extract search terms from query"""
        words = query.split()
        search_words = {"search", "find", "look", "for"}
        terms = [w for w in words if w not in search_words and len(w) > 2]
        return terms[:3]  # Return up to 3 terms

    def explain_error(self, error_message: str) -> str | None:
        """Use AI to explain an error message in simple terms"""
        prompt = f"""Explain this NixOS error in simple terms and suggest a solution:
Error: {error_message}

Provide a brief, helpful explanation and solution."""

        return self.ask(prompt, model=self.models.get("empathy", self.models["tiny"]))

    def suggest_packages(self, description: str) -> list[str] | None:
        """Use AI to suggest packages based on a description"""
        prompt = f"""Suggest NixOS packages for: {description}
List up to 5 relevant package names, one per line."""

        response = self.ask(
            prompt, model=self.models.get("coder", self.models["quick"])
        )

        if response:
            # Extract package names from response
            lines = response.strip().split("\n")
            packages = []
            for line in lines:
                # Clean up the line and extract package name
                line = line.strip().strip("- ").strip("* ")
                if line and not line.startswith("#"):
                    # Take first word as package name
                    parts = line.split()
                    if parts:
                        packages.append(parts[0])
            return packages[:5]
        return None


class SocraticOllama(OllamaClient):
    """Socratic questioning mode for Ollama - asks clarifying questions"""

    def ask_clarifying_question(self, query: str, category: str) -> str | None:
        """Generate a clarifying question based on the query"""

        prompt = f"""The user wants to {query} related to {category}.
Generate a helpful clarifying question to better understand their needs.
Keep it simple and friendly. One question only.

Example: "What kind of {category} would work best for you?"

Question:"""

        response = self.ask(
            prompt, model=self.models.get("empathy", self.models["tiny"])
        )
        return response.strip() if response else None

    def generate_options(self, category: str) -> dict[str, str] | None:
        """Generate options for a category"""

        prompt = f"""Generate 4 options for choosing a {category} on NixOS.
Format as JSON with number keys and description values.

Example:
{{"1": "Fast and minimal", "2": "Feature-rich", "3": "Privacy-focused", "4": "Developer-oriented"}}

Options:"""

        response = self.ask(prompt, model=self.models.get("quick", self.models["tiny"]))

        if response:
            try:
                import re

                json_match = re.search(r"\{.*\}", response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except:
                pass

        # Fallback options
        return {
            "1": "Simple and easy",
            "2": "Powerful and flexible",
            "3": "Lightweight and fast",
            "4": "Full-featured",
        }
