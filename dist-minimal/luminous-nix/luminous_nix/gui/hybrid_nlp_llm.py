"""
🧠 Hybrid NLP+LLM Intent Understanding System
Combines rule-based NLP with LLM intelligence for optimal accuracy and performance
"""

import hashlib
import json
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

# For LLM integration
try:
    import ollama

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Warning: Ollama not available - using fallback")

try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


@dataclass
class IntentConfidence:
    """Confidence scores for parsed intent"""

    overall: float  # 0-1 confidence score
    action: float
    interface_type: float
    components: float
    style: float
    source: str  # "nlp", "llm", "hybrid"


@dataclass
class EnhancedIntent:
    """Enhanced intent with richer understanding"""

    # Core intent
    action: str
    interface_type: str
    target: str

    # Detailed understanding
    components_needed: list[dict[str, Any]]
    layout_suggestion: str
    style_preferences: dict[str, Any]
    data_requirements: list[str]
    interactions: list[str]
    constraints: list[str]

    # Meta information
    confidence: IntentConfidence
    ambiguities: list[str]
    suggestions: list[str]
    context_used: bool


class IntentParser(ABC):
    """Abstract base for intent parsers"""

    @abstractmethod
    def parse(self, request: str, context: dict | None = None) -> EnhancedIntent:
        pass


class RuleBasedNLP(IntentParser):
    """Fast rule-based NLP for common patterns"""

    def __init__(self):
        # Compile regex patterns for performance
        self.patterns = {
            "actions": {
                "create": re.compile(
                    r"\b(create|make|build|generate|design|construct)\b", re.I
                ),
                "show": re.compile(r"\b(show|display|present|view|see|list)\b", re.I),
                "modify": re.compile(
                    r"\b(change|modify|update|edit|adjust|alter)\b", re.I
                ),
                "analyze": re.compile(
                    r"\b(analyze|inspect|examine|review|check)\b", re.I
                ),
            },
            "interfaces": {
                "dashboard": re.compile(
                    r"\b(dashboard|overview|summary|panel|monitor)\b", re.I
                ),
                "form": re.compile(
                    r"\b(form|input|entry|submission|questionnaire)\b", re.I
                ),
                "editor": re.compile(r"\b(editor|writer|composer|ide|notepad)\b", re.I),
                "list": re.compile(r"\b(list|table|grid|catalog|directory)\b", re.I),
                "chart": re.compile(
                    r"\b(chart|graph|plot|visualization|diagram)\b", re.I
                ),
            },
            "styles": {
                "dark": re.compile(r"\b(dark|night|black)\s*(theme|mode)?\b", re.I),
                "minimal": re.compile(r"\b(minimal|simple|clean|basic|zen)\b", re.I),
                "playful": re.compile(
                    r"\b(fun|playful|colorful|animated|vibrant)\b", re.I
                ),
            },
            "components": {
                "button": re.compile(r"\b(button|btn|action|submit|click)\b", re.I),
                "input": re.compile(r"\b(input|field|textbox|textarea|entry)\b", re.I),
                "chart": re.compile(r"\b(chart|graph|metric|gauge|sparkline)\b", re.I),
                "table": re.compile(r"\b(table|grid|spreadsheet|data)\b", re.I),
            },
        }

        # Common templates for quick matching
        self.templates = {
            "dashboard": {
                "components": ["metrics_display", "chart", "status_indicator"],
                "layout": "grid",
                "typical_request": ["dashboard", "monitoring", "overview"],
            },
            "form": {
                "components": ["input_field", "label", "submit_button"],
                "layout": "vertical",
                "typical_request": ["form", "input", "collect", "submit"],
            },
            "editor": {
                "components": ["text_area", "toolbar", "status_bar"],
                "layout": "vertical_split",
                "typical_request": ["editor", "write", "document", "text"],
            },
        }

    def parse(self, request: str, context: dict | None = None) -> EnhancedIntent:
        """Parse using rule-based approach"""

        request_lower = request.lower()

        # Extract components using patterns
        action = self._extract_action(request_lower)
        interface_type = self._extract_interface_type(request_lower)
        components = self._extract_components(request_lower)
        style = self._extract_style(request_lower)

        # Calculate confidence based on matches
        confidence = self._calculate_confidence(action, interface_type, components)

        # Build enhanced intent
        return EnhancedIntent(
            action=action,
            interface_type=interface_type,
            target=self._extract_target(request_lower),
            components_needed=components,
            layout_suggestion=self._suggest_layout(interface_type, components),
            style_preferences=style,
            data_requirements=self._extract_data_requirements(request_lower),
            interactions=self._extract_interactions(request_lower),
            constraints=self._extract_constraints(request_lower),
            confidence=confidence,
            ambiguities=self._identify_ambiguities(request_lower),
            suggestions=[],
            context_used=context is not None,
        )

    def _extract_action(self, text: str) -> str:
        """Extract primary action from text"""
        for action, pattern in self.patterns["actions"].items():
            if pattern.search(text):
                return action
        return "create"  # default

    def _extract_interface_type(self, text: str) -> str:
        """Extract interface type"""
        for itype, pattern in self.patterns["interfaces"].items():
            if pattern.search(text):
                return itype

        # Check templates
        for template_name, template in self.templates.items():
            if any(keyword in text for keyword in template["typical_request"]):
                return template_name

        return "general"

    def _extract_components(self, text: str) -> list[dict[str, Any]]:
        """Extract needed components"""
        components = []

        for comp_type, pattern in self.patterns["components"].items():
            if pattern.search(text):
                components.append(
                    {"type": comp_type, "properties": {}, "priority": "high"}
                )

        # Add template-based components
        interface_type = self._extract_interface_type(text)
        if interface_type in self.templates:
            for comp in self.templates[interface_type]["components"]:
                if not any(c["type"] == comp for c in components):
                    components.append(
                        {"type": comp, "properties": {}, "priority": "medium"}
                    )

        return components

    def _extract_style(self, text: str) -> dict[str, Any]:
        """Extract style preferences"""
        style = {}

        for style_type, pattern in self.patterns["styles"].items():
            if pattern.search(text):
                style[style_type] = True

        # Extract specific mentions
        if "real-time" in text or "realtime" in text:
            style["updates"] = "realtime"
        if "responsive" in text:
            style["responsive"] = True

        return style

    def _suggest_layout(self, interface_type: str, components: list) -> str:
        """Suggest appropriate layout"""
        if interface_type in self.templates:
            return self.templates[interface_type]["layout"]

        # Heuristics based on component count
        if len(components) == 1:
            return "centered"
        if len(components) <= 3:
            return "vertical"
        return "grid"

    def _extract_target(self, text: str) -> str:
        """Extract what the interface is for"""
        patterns = [
            r"for\s+(\w+(?:\s+\w+){0,2})",
            r"to\s+(\w+(?:\s+\w+){0,2})",
            r"showing\s+(\w+(?:\s+\w+){0,2})",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        return ""

    def _extract_data_requirements(self, text: str) -> list[str]:
        """Extract data needs"""
        requirements = []

        data_keywords = ["data", "metrics", "statistics", "logs", "records", "files"]
        for keyword in data_keywords:
            if keyword in text:
                requirements.append(keyword)

        return requirements

    def _extract_interactions(self, text: str) -> list[str]:
        """Extract interaction patterns"""
        interactions = []

        interaction_keywords = {
            "click": ["click", "tap", "press"],
            "drag": ["drag", "move", "reorder"],
            "type": ["type", "input", "enter"],
            "hover": ["hover", "mouseover"],
            "scroll": ["scroll", "pan"],
        }

        for interaction, keywords in interaction_keywords.items():
            if any(kw in text for kw in keywords):
                interactions.append(interaction)

        return interactions

    def _extract_constraints(self, text: str) -> list[str]:
        """Extract constraints and limitations"""
        constraints = []

        if "without" in text or "no " in text:
            constraints.append("exclusions")
        if "only" in text or "just" in text:
            constraints.append("limitations")
        if "must" in text or "should" in text:
            constraints.append("requirements")

        return constraints

    def _calculate_confidence(
        self, action: str, interface_type: str, components: list
    ) -> IntentConfidence:
        """Calculate confidence scores"""

        action_conf = 0.9 if action != "create" else 0.6  # Default is less confident
        interface_conf = 0.9 if interface_type != "general" else 0.4
        components_conf = min(
            0.9, 0.3 * len(components)
        )  # More components = more confident

        overall = (action_conf + interface_conf + components_conf) / 3

        return IntentConfidence(
            overall=overall,
            action=action_conf,
            interface_type=interface_conf,
            components=components_conf,
            style=0.7,  # Fixed for now
            source="nlp",
        )

    def _identify_ambiguities(self, text: str) -> list[str]:
        """Identify ambiguous parts"""
        ambiguities = []

        if len(text.split()) < 3:
            ambiguities.append("Very short request")

        vague_words = ["something", "thing", "stuff", "whatever"]
        if any(word in text for word in vague_words):
            ambiguities.append("Vague terminology")

        return ambiguities


class LLMParser(IntentParser):
    """LLM-based intent parser for complex understanding"""

    def __init__(self, model: str = "mistral", use_openai: bool = False):
        self.model = model
        self.use_openai = use_openai and OPENAI_AVAILABLE

        # Cache for responses
        self.cache = {}

        # System prompt for intent parsing
        self.system_prompt = """You are an expert UI/UX designer helping to understand user interface requests.
        
Given a natural language request for an interface, extract:
1. Primary action (create, show, modify, analyze)
2. Interface type (dashboard, form, editor, list, chart, etc.)
3. Specific components needed (with properties)
4. Layout suggestion
5. Style preferences
6. Data requirements
7. Interactions needed
8. Any constraints

Respond in JSON format with these exact keys:
{
    "action": "string",
    "interface_type": "string",
    "target": "string",
    "components_needed": [{"type": "string", "properties": {}, "priority": "high|medium|low"}],
    "layout_suggestion": "string",
    "style_preferences": {},
    "data_requirements": [],
    "interactions": [],
    "constraints": [],
    "ambiguities": [],
    "suggestions": []
}

Be specific and actionable. If the request is vague, make reasonable assumptions and note them in ambiguities."""

    def parse(self, request: str, context: dict | None = None) -> EnhancedIntent:
        """Parse using LLM"""

        # Check cache
        cache_key = hashlib.md5(f"{request}{context}".encode()).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            # Prepare prompt with context
            prompt = self._prepare_prompt(request, context)

            # Get LLM response
            response = self._query_llm(prompt)

            # Parse JSON response
            parsed = json.loads(response)

            # Build enhanced intent
            intent = EnhancedIntent(
                action=parsed.get("action", "create"),
                interface_type=parsed.get("interface_type", "general"),
                target=parsed.get("target", ""),
                components_needed=parsed.get("components_needed", []),
                layout_suggestion=parsed.get("layout_suggestion", "auto"),
                style_preferences=parsed.get("style_preferences", {}),
                data_requirements=parsed.get("data_requirements", []),
                interactions=parsed.get("interactions", []),
                constraints=parsed.get("constraints", []),
                confidence=IntentConfidence(
                    overall=0.85,  # LLM generally high confidence
                    action=0.9,
                    interface_type=0.85,
                    components=0.8,
                    style=0.8,
                    source="llm",
                ),
                ambiguities=parsed.get("ambiguities", []),
                suggestions=parsed.get("suggestions", []),
                context_used=context is not None,
            )

            # Cache result
            self.cache[cache_key] = intent
            return intent

        except Exception as e:
            print(f"LLM parsing failed: {e}")
            # Return a basic intent on failure
            return self._fallback_intent(request)

    def _prepare_prompt(self, request: str, context: dict | None) -> str:
        """Prepare prompt for LLM"""

        prompt = f"User request: {request}"

        if context:
            prompt += "\n\nContext:\n"
            prompt += f"- User expertise: {context.get('expertise_level', 'unknown')}\n"
            prompt += f"- Device: {context.get('device_type', 'unknown')}\n"
            prompt += f"- Previous requests: {context.get('history', [])[-3:]}\n"

        return prompt

    def _query_llm(self, prompt: str) -> str:
        """Query the LLM"""

        if self.use_openai:
            return self._query_openai(prompt)
        if OLLAMA_AVAILABLE:
            return self._query_ollama(prompt)
        # Fallback to mock response
        return self._mock_llm_response(prompt)

    def _query_ollama(self, prompt: str) -> str:
        """Query Ollama"""

        response = ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            format="json",
        )

        return response["message"]["content"]

    def _query_openai(self, prompt: str) -> str:
        """Query OpenAI"""

        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )

        return response.choices[0].message.content

    def _mock_llm_response(self, prompt: str) -> str:
        """Mock LLM response for testing"""

        # Simple mock based on keywords
        response = {
            "action": "create",
            "interface_type": "dashboard"
            if "dashboard" in prompt.lower()
            else "general",
            "target": "user interface",
            "components_needed": [
                {"type": "display", "properties": {}, "priority": "high"}
            ],
            "layout_suggestion": "grid",
            "style_preferences": {"modern": True},
            "data_requirements": [],
            "interactions": ["click"],
            "constraints": [],
            "ambiguities": [],
            "suggestions": ["Consider adding more specific requirements"],
        }

        return json.dumps(response)

    def _fallback_intent(self, request: str) -> EnhancedIntent:
        """Fallback intent when LLM fails"""

        return EnhancedIntent(
            action="create",
            interface_type="general",
            target="interface",
            components_needed=[],
            layout_suggestion="auto",
            style_preferences={},
            data_requirements=[],
            interactions=[],
            constraints=[],
            confidence=IntentConfidence(
                overall=0.3,
                action=0.3,
                interface_type=0.3,
                components=0.3,
                style=0.3,
                source="fallback",
            ),
            ambiguities=["LLM parsing failed"],
            suggestions=["Try rephrasing your request"],
            context_used=False,
        )


class HybridNLPLLM:
    """Hybrid system combining NLP and LLM for optimal performance"""

    def __init__(
        self,
        use_llm: bool = True,
        llm_threshold: float = 0.6,
        cache_enabled: bool = True,
    ):
        self.nlp_parser = RuleBasedNLP()
        self.llm_parser = LLMParser() if use_llm else None
        self.llm_threshold = llm_threshold  # Confidence below this triggers LLM
        self.cache_enabled = cache_enabled

        # Performance tracking
        self.stats = {"nlp_only": 0, "llm_used": 0, "hybrid": 0, "cache_hits": 0}

        # Response cache
        self.cache = {} if cache_enabled else None

    def parse(self, request: str, context: dict | None = None) -> EnhancedIntent:
        """Parse using hybrid approach"""

        start_time = time.time()

        # Check cache
        if self.cache_enabled:
            cache_key = hashlib.md5(f"{request}{context}".encode()).hexdigest()
            if cache_key in self.cache:
                self.stats["cache_hits"] += 1
                return self.cache[cache_key]

        # Step 1: Always try NLP first (fast)
        nlp_intent = self.nlp_parser.parse(request, context)

        # Step 2: Decide if LLM is needed
        needs_llm = self._should_use_llm(nlp_intent, request)

        if not needs_llm or not self.llm_parser:
            # NLP is sufficient
            self.stats["nlp_only"] += 1
            final_intent = nlp_intent
        else:
            # Step 3: Use LLM for complex cases
            llm_intent = self.llm_parser.parse(request, context)

            # Step 4: Merge results
            final_intent = self._merge_intents(nlp_intent, llm_intent)
            self.stats["llm_used"] += 1

        # Add performance metadata
        final_intent.parse_time = (time.time() - start_time) * 1000

        # Cache result
        if self.cache_enabled:
            self.cache[cache_key] = final_intent

        return final_intent

    def _should_use_llm(self, nlp_intent: EnhancedIntent, request: str) -> bool:
        """Determine if LLM is needed"""

        # Use LLM if:
        # 1. NLP confidence is low
        if nlp_intent.confidence.overall < self.llm_threshold:
            return True

        # 2. Request has ambiguities
        if nlp_intent.ambiguities:
            return True

        # 3. Request is complex (long or many clauses)
        if len(request.split()) > 15 or request.count(",") > 2:
            return True

        # 4. No components identified
        if not nlp_intent.components_needed:
            return True

        return False

    def _merge_intents(
        self, nlp_intent: EnhancedIntent, llm_intent: EnhancedIntent
    ) -> EnhancedIntent:
        """Merge NLP and LLM intents intelligently"""

        # Start with LLM intent (usually more comprehensive)
        merged = llm_intent

        # But prefer NLP for certain fast extractions
        if nlp_intent.confidence.action > llm_intent.confidence.action:
            merged.action = nlp_intent.action

        # Combine components from both
        all_components = nlp_intent.components_needed + llm_intent.components_needed
        # Deduplicate by type
        seen_types = set()
        unique_components = []
        for comp in all_components:
            if comp["type"] not in seen_types:
                unique_components.append(comp)
                seen_types.add(comp["type"])
        merged.components_needed = unique_components

        # Merge style preferences
        merged.style_preferences = {
            **nlp_intent.style_preferences,
            **llm_intent.style_preferences,
        }

        # Update confidence to reflect hybrid approach
        merged.confidence = IntentConfidence(
            overall=(nlp_intent.confidence.overall + llm_intent.confidence.overall) / 2
            + 0.1,  # Bonus for hybrid
            action=max(nlp_intent.confidence.action, llm_intent.confidence.action),
            interface_type=max(
                nlp_intent.confidence.interface_type,
                llm_intent.confidence.interface_type,
            ),
            components=max(
                nlp_intent.confidence.components, llm_intent.confidence.components
            ),
            style=(nlp_intent.confidence.style + llm_intent.confidence.style) / 2,
            source="hybrid",
        )

        self.stats["hybrid"] += 1

        return merged

    def get_stats(self) -> dict:
        """Get performance statistics"""
        total = sum(self.stats.values()) - self.stats["cache_hits"]

        if total == 0:
            return self.stats

        return {
            **self.stats,
            "nlp_percentage": (self.stats["nlp_only"] / total) * 100,
            "llm_percentage": (self.stats["llm_used"] / total) * 100,
            "cache_hit_rate": (
                self.stats["cache_hits"] / (total + self.stats["cache_hits"])
            )
            * 100,
        }

    def optimize_threshold(self, feedback_data: list[tuple[str, bool]]):
        """Optimize LLM threshold based on feedback"""

        # Analyze when LLM improved results vs when it was unnecessary
        # Adjust threshold accordingly
        # This is a simplified version - real implementation would use ML

        successful_nlp = []
        needed_llm = []

        for request, was_successful in feedback_data:
            nlp_intent = self.nlp_parser.parse(request)

            if was_successful and nlp_intent.confidence.overall > 0.7:
                successful_nlp.append(nlp_intent.confidence.overall)
            elif not was_successful and nlp_intent.confidence.overall < 0.7:
                needed_llm.append(nlp_intent.confidence.overall)

        if successful_nlp and needed_llm:
            # Find optimal threshold
            self.llm_threshold = (min(successful_nlp) + max(needed_llm)) / 2
            print(f"Optimized LLM threshold to: {self.llm_threshold:.2f}")


# Example usage and testing
if __name__ == "__main__":
    # Initialize hybrid system
    hybrid = HybridNLPLLM(use_llm=True, llm_threshold=0.6)

    # Test cases
    test_requests = [
        # Simple (should use NLP only)
        "Create a simple button",
        "Show me a list of items",
        # Moderate (might use NLP only)
        "Build a dashboard with dark theme",
        "Create a form for user registration",
        # Complex (should trigger LLM)
        "I need a sophisticated development environment with a file browser on the left, code editor in the center with syntax highlighting for multiple languages, terminal at the bottom, and a debugging panel on the right that shows variables and call stack",
        # Ambiguous (should trigger LLM)
        "Make something cool",
        "I want to see my stuff",
        # Conversational (should trigger LLM)
        "Can you create an interface that helps me track my daily tasks and reminds me of important deadlines?",
    ]

    print("🧠 HYBRID NLP+LLM TESTING")
    print("=" * 60)

    for request in test_requests:
        print(f"\n📝 Request: {request[:50]}...")

        intent = hybrid.parse(request)

        print(f"   Source: {intent.confidence.source}")
        print(f"   Confidence: {intent.confidence.overall:.2f}")
        print(f"   Action: {intent.action}")
        print(f"   Type: {intent.interface_type}")
        print(f"   Components: {len(intent.components_needed)}")

        if intent.ambiguities:
            print(f"   ⚠️ Ambiguities: {intent.ambiguities}")

        if hasattr(intent, "parse_time"):
            print(f"   ⏱️ Parse time: {intent.parse_time:.2f}ms")

    # Show statistics
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE STATISTICS")
    print("=" * 60)

    stats = hybrid.get_stats()
    for key, value in stats.items():
        if "percentage" in key or "rate" in key:
            print(f"{key}: {value:.1f}%")
        else:
            print(f"{key}: {value}")
