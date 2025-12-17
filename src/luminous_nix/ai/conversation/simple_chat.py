"""
Simple Conversational AI - Proof of Concept
Integrates all existing AI components with full context awareness

This is the main conversational interface that:
- Gathers complete system and user context
- Routes queries to appropriate AI components
- Maintains conversation history
- Recommends flakes as default approach
- Adapts responses to user skill level
"""

import sys
import os
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

# Import context managers
from ..context.system_context import SystemContextGatherer, SystemContext
from ..context.user_context import UserContextManager, UserContext, SkillLevel

# Import query routing
from ..routing.query_router import QueryRouter, Domain, RouteResult

# Import NixOS context generation for dual-answer mode
from ..nixos_context_generator import NixOSContextGenerator

# Import self-healing agent for automatic issue fixing
from ..self_healing import get_self_healing_agent

# Import anticipatory intelligence for predicting next steps
from ..anticipatory import get_anticipatory_intelligence

# Import cognitive modeling for tracking user understanding
from ..cognitive_model import get_cognitive_model

# Import Socratic teaching for building deep understanding
from ..socratic_teacher import get_socratic_teacher

# Import meta-learning for personalized teaching
from ..meta_learning import get_meta_learning_engine

# 🌟 LAYER 5: Import user profiling and adaptive engagement
from ..user_profiler import (
    get_user_profiler, UserProfile, UserArchetype,
    TechnicalLevel, EngagementMode
)
from ..adaptive_engagement import (
    get_adaptive_engagement_engine, EngagementStrategy
)

# Import AI components (with graceful fallbacks)
try:
    from ..error_resolver import ErrorResolver
    ERROR_RESOLVER_AVAILABLE = True
except ImportError:
    ERROR_RESOLVER_AVAILABLE = False
    print("⚠️  Error resolver not available")

try:
    from ..config_generator import AIConfigGenerator
    CONFIG_GEN_AVAILABLE = True
except ImportError:
    CONFIG_GEN_AVAILABLE = False
    print("⚠️  Config generator not available")

try:
    from ..package_recommender import PackageRecommender
    PACKAGE_REC_AVAILABLE = True
except ImportError:
    PACKAGE_REC_AVAILABLE = False
    print("⚠️  Package recommender not available")

try:
    from ..command_explainer import CommandExplainer
    CMD_EXPLAINER_AVAILABLE = True
except ImportError:
    CMD_EXPLAINER_AVAILABLE = False
    print("⚠️  Command explainer not available")

try:
    # Import from core (has understand_query method we need)
    from ...core.ai_orchestrator import AIOrchestrator
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    try:
        # Fallback to ai/orchestrator (has process method instead)
        from ..orchestrator import AIOrchestrator
        ORCHESTRATOR_AVAILABLE = True
    except ImportError:
        ORCHESTRATOR_AVAILABLE = False
        print("⚠️  AI orchestrator not available")

console = Console()


class FlakeRecommender:
    """Recommends flakes and explains benefits based on context"""

    def should_recommend_flake(self, query: str, user_context: UserContext,
                               system_context: SystemContext) -> bool:
        """Determine if we should recommend flakes"""
        # If user already uses flakes, no need to recommend
        if system_context.has_flake_nix:
            return False

        # If user disabled flake preference
        if not user_context.prefers_flakes:
            return False

        # Recommend flakes for:
        flake_triggers = [
            'dev environment', 'development', 'project setup',
            'new project', 'create', 'setup', 'configure',
            'flake', 'reproducible'
        ]

        return any(trigger in query.lower() for trigger in flake_triggers)

    def get_flake_recommendation(self, query: str, skill_level: SkillLevel) -> str:
        """Get flake recommendation adapted to skill level"""
        if skill_level == SkillLevel.BEGINNER:
            return """

💡 **Flake Recommendation**: I notice you're not using flakes yet.

Flakes are the modern way to manage NixOS with these benefits:
- **Reproducible**: Lock exact versions of all dependencies
- **Portable**: Share configs easily with others
- **Faster**: Better caching and evaluation
- **Cleaner**: Self-contained, no channel management

Would you like me to help you migrate to flakes? (Just say "yes" or "explain flakes more")
"""
        elif skill_level == SkillLevel.INTERMEDIATE:
            return """

💡 **Tip**: Consider using flakes for this! Benefits:
- Reproducible builds with flake.lock
- Better dev environments with `nix develop`
- Easier sharing and composition
- Modern Nix CLI (`nix build`, `nix run`, etc.)

I can generate a flake.nix for you. Interested? (yes/no)
"""
        else:  # Advanced/Expert
            return """

💡 Flakes would be ideal here - `flake.nix` with inputs/outputs, locked deps, and `nix develop`.
Want a template?
"""


class SimpleChat:
    """
    Simple conversational AI that integrates all existing components.

    Features:
    - Full context awareness (system + user)
    - Multi-turn conversation memory
    - Flake-first recommendations
    - Skill-adaptive responses
    - All existing AI features integrated
    """

    def __init__(self):
        console.print("[bold cyan]🚀 Initializing Luminous Nix AI...[/bold cyan]")

        # Initialize context gatherers
        try:
            self.system_context = SystemContextGatherer().gather()
            console.print("  ✓ System context gathered")
        except Exception as e:
            console.print(f"  [yellow]⚠ System context limited: {e}[/yellow]")
            # Create minimal context
            from dataclasses import dataclass
            @dataclass
            class MinimalContext:
                hostname: str = "unknown"
                nixos_version: str = "unknown"
                channel_or_flake: str = "unknown"
                has_flake_nix: bool = False
                has_configuration_nix: bool = False
                def to_context_string(self) -> str:
                    return "System context unavailable"
            self.system_context = MinimalContext()

        self.user_manager = UserContextManager()
        self.user_context = self.user_manager.get_context()
        console.print("  ✓ User profile loaded")

        # Initialize AI components (with graceful fallback)
        self.components_available = {
            'orchestrator': False,
            'error_resolver': False,
            'config_gen': False,
            'package_rec': False,
            'cmd_explainer': False
        }

        if ORCHESTRATOR_AVAILABLE:
            try:
                self.orchestrator = AIOrchestrator()
                self.components_available['orchestrator'] = True
                console.print("  ✓ AI orchestrator ready")
            except Exception as e:
                console.print(f"  [yellow]⚠ Orchestrator init failed: {e}[/yellow]")

        if ERROR_RESOLVER_AVAILABLE:
            try:
                self.error_resolver = ErrorResolver()
                self.components_available['error_resolver'] = True
                console.print("  ✓ Error resolver ready")
            except Exception as e:
                console.print(f"  [yellow]⚠ Error resolver init failed: {e}[/yellow]")

        if CONFIG_GEN_AVAILABLE:
            try:
                self.config_gen = AIConfigGenerator()
                self.components_available['config_gen'] = True
                console.print("  ✓ Config generator ready")
            except Exception as e:
                console.print(f"  [yellow]⚠ Config generator init failed: {e}[/yellow]")

        if PACKAGE_REC_AVAILABLE:
            try:
                self.recommender = PackageRecommender()
                self.components_available['package_rec'] = True
                console.print("  ✓ Package recommender ready")
            except Exception as e:
                console.print(f"  [yellow]⚠ Package recommender init failed: {e}[/yellow]")

        if CMD_EXPLAINER_AVAILABLE:
            try:
                self.explainer = CommandExplainer()
                self.components_available['cmd_explainer'] = True
                console.print("  ✓ Command explainer ready")
            except Exception as e:
                console.print(f"  [yellow]⚠ Command explainer init failed: {e}[/yellow]")

        self.flake_recommender = FlakeRecommender()

        # Initialize query router for smart domain routing
        self.query_router = QueryRouter()
        console.print("  ✓ Query router initialized")

        # Initialize NixOS context generator for dual-answer mode
        self.nixos_context_gen = NixOSContextGenerator()

        # Initialize self-healing agent for automatic issue fixing
        self.self_healing = get_self_healing_agent(verbose=False)
        console.print("  ✓ Self-healing agent active")

        # Initialize anticipatory intelligence for predictive assistance
        self.anticipatory = get_anticipatory_intelligence()
        console.print("  ✓ Anticipatory intelligence ready")

        # Initialize cognitive modeling for understanding tracking
        self.cognitive = get_cognitive_model()
        console.print("  ✓ Cognitive modeling active")

        # Initialize Socratic teaching for deep understanding
        self.socratic = get_socratic_teacher()
        self.active_teaching_session = None  # Track active teaching session
        console.print("  ✓ Socratic teaching ready")

        # Initialize meta-learning for personalized teaching
        self.meta_learning = get_meta_learning_engine("default_user")
        console.print("  ✓ Meta-learning engine active")

        # 🧠 LAYER 4: Connect meta-learning to Socratic teacher
        self.socratic.set_meta_learning(self.meta_learning)
        console.print("  ✓ Personalized teaching enabled")

        # 🌟 LAYER 5: Initialize user profiling and adaptive engagement
        self.user_profiler = get_user_profiler()
        self.user_profile = self.user_profiler.load_profile()
        self.adaptive_engagement = get_adaptive_engagement_engine()

        if not self.user_profile:
            console.print("  [yellow]⚠ No user profile found - onboarding recommended[/yellow]")
            console.print("  [dim]Say '/onboarding' to personalize your experience![/dim]")
        else:
            console.print(f"  ✓ User profile loaded: {self.user_profile.archetype.value.title()} mode")
            console.print(f"  [dim]Engagement: {self.user_profile.engagement_mode.value}[/dim]")

        # Conversation history (for multi-turn context)
        self.history: List[Dict[str, str]] = []

        console.print("[green]✅ AI System Ready[/green]\n")

    def chat_loop(self):
        """Main interactive chat loop"""
        # Show welcome message with context
        self._show_welcome()

        console.print()  # Add spacing

        while True:
            try:
                # Get user input with conversational prompt
                user_input = console.input("[bold green]▶[/bold green] ").strip()

                if not user_input:
                    continue

                # Handle exit commands
                if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye', 'q']:
                    farewells = [
                        "Happy hacking! 🌊",
                        "Take care! Feel free to come back anytime.",
                        "See you later! 👋",
                        "Goodbye! May your builds be reproducible! 🚀"
                    ]
                    import random
                    console.print(f"\n[bold cyan]🤖[/bold cyan] {random.choice(farewells)}\n")
                    break

                # Handle special commands
                if user_input.startswith('/'):
                    self._handle_command(user_input)
                    continue

                # 🎓 REVOLUTIONARY: Check if we're in an active teaching session
                if self.active_teaching_session:
                    response, teaching_complete, understood = self.socratic.respond_to_teaching(
                        user_input, session_id="main"
                    )
                    console.print(Markdown(response))

                    if teaching_complete:
                        # 🧠 LAYER 4: Record teaching attempt in meta-learning
                        session = self.socratic.get_active_session("main")
                        if session:
                            teaching_mode = session.steps[session.current_step - 1].mode.value if session.current_step > 0 else "question"
                            time_taken = 30.0  # Estimated from session

                            self.meta_learning.record_teaching_attempt(
                                concept_id=session.concept_id,
                                teaching_mode=teaching_mode,
                                user_response=user_input,
                                understood=understood,
                                time_taken=time_taken,
                                hints_needed=0,  # Could track this in session
                                examples_shown=sum(1 for step in session.steps if step.mode.value == "example")
                            )

                        self.active_teaching_session = None
                        console.print("[green]✨ Teaching session complete! You can continue chatting or start a new lesson.[/green]")

                    continue  # Stay in teaching mode

                # 🎓 REVOLUTIONARY: Detect "teach me about X" queries
                teach_trigger = self._detect_teaching_request(user_input)
                if teach_trigger:
                    message, success = self.socratic.start_teaching(teach_trigger, session_id="main")
                    if success:
                        self.active_teaching_session = teach_trigger
                        console.print(Markdown(message))
                    else:
                        console.print(Markdown(message))
                    continue

                # Record command
                self.user_manager.record_command(user_input)

                # Add to history
                self.history.append({"role": "user", "content": user_input})

                # Process query with full context
                response = self._handle_query(user_input)

                # 🧠 REVOLUTIONARY: Record interaction in cognitive model
                learning_opportunities = self.cognitive.record_interaction(user_input, success=True)

                # Add learning opportunities to response if appropriate
                if learning_opportunities and self.user_context.skill_level.value != 'expert':
                    # Show top learning opportunity for non-experts
                    top_opp = learning_opportunities[0]
                    if top_opp.readiness > 0.5:  # Only show if user is ready
                        learning_note = f"\n\n💡 **Learning Moment**: I notice you might be ready to learn about **{top_opp.concept.name}**. {top_opp.teaching_approach}\n\n_Say 'teach me about {top_opp.concept.name.lower()}' if you're interested!_"
                        response = f"{response}{learning_note}"

                # Display response with conversational formatting
                console.print(f"\n[bold cyan]🤖[/bold cyan] {response}\n")

                # Add response to history
                self.history.append({"role": "assistant", "content": response})

                # Record success (for now - later we can detect failures)
                self.user_manager.record_success()

            except KeyboardInterrupt:
                console.print("\n\n[bold cyan]🤖[/bold cyan] Take care! Happy hacking! 🌊\n")
                break
            except Exception as e:
                console.print(f"\n[bold red]❌ Oops:[/bold red] {e}\n")
                console.print("[dim]Don't worry, we can try again![/dim]\n")
                self.user_manager.record_failure()

    def _show_welcome(self):
        """Show welcome message with system context"""
        # Get friendly system description
        system_ver = getattr(self.system_context, 'nixos_version', 'Unknown')
        channel_or_flake = getattr(self.system_context, 'channel_or_flake', 'Unknown')

        if 'flake' in channel_or_flake.lower():
            system_desc = "using modern flakes 🚀"
        else:
            system_desc = "using traditional channels"

        # Get skill-appropriate greeting
        greetings = {
            SkillLevel.BEGINNER: "I'm here to help you with NixOS and general IT questions! I specialize in NixOS but can help with programming, DevOps, networking, and more. Just chat naturally!",
            SkillLevel.INTERMEDIATE: "Ready to help with NixOS and IT tasks! I'm a NixOS specialist but can assist with general IT questions too.",
            SkillLevel.ADVANCED: "Let's get your system configured! NixOS expert here, with general IT knowledge too.",
            SkillLevel.EXPERT: "Ready for advanced work! NixOS specialist + general IT assistant."
        }

        greeting = greetings.get(self.user_context.skill_level, greetings[SkillLevel.BEGINNER])

        welcome = f"""
[bold cyan]🤖 Hi! I'm your Luminous Nix AI Assistant[/bold cyan]

I can see you're running NixOS [bold]{system_ver}[/bold], {system_desc}

{greeting}

[bold green]Just chat naturally - examples:[/bold green]
[dim]NixOS-specific:
• "I need to install Firefox on NixOS"
• "How do I set up a NixOS flake for Python?"
• "Help me debug this nixos-rebuild error"

General IT:
• "How do I write async Python?"
• "Explain Docker networking"
• "Best practices for PostgreSQL indexing"[/dim]

[dim]Say '/help' to see special features, or just start chatting! Type 'exit' when done.[/dim]
"""
        console.print(Panel(welcome, border_style="cyan"))

    def _handle_command(self, command: str):
        """Handle special /commands"""
        if command == '/help':
            help_text = """
**Available Commands:**
- `/help` - Show this help
- `/context` - Show system & user context
- `/clear` - Clear conversation history
- `/skill [level]` - Set skill level (beginner/intermediate/advanced/expert)
- `/flakes on|off` - Toggle flake preference
- `/history` - Show conversation history
- `/status` - Show AI component status
- `/knowledge` - Show your NixOS knowledge map
- `/learning-profile` - Show your personalized learning profile
- `/teach [concept]` - Start Socratic teaching session
- `/stop-teaching` - Exit current teaching session
- **🌟 `/onboarding`** - Take onboarding quiz to personalize experience
- **🌟 `/profile`** - Show your user profile and preferences
- `exit` - Exit chat

**🎓 Socratic Teaching:**
You can also just say "teach me about [concept]" to start a teaching session!
Available concepts: declarative, generations, flakes, modules

**🌟 Layer 5 - User Experience Intelligence:**
Complete the onboarding to get an experience tailored to YOU!
Archetypes: Learner, Pragmatist, Explorer, Creator
"""
            console.print(Markdown(help_text))

        elif command == '/context':
            try:
                context_info = f"""
**System Context:**
{self.system_context.to_context_string()}

**User Context:**
{self.user_context.to_context_string()}
"""
                console.print(Markdown(context_info))
            except Exception as e:
                console.print(f"[red]Error showing context: {e}[/red]")

        elif command == '/clear':
            self.history = []
            console.print("[green]✅ Conversation history cleared[/green]")

        elif command.startswith('/skill'):
            parts = command.split()
            if len(parts) > 1:
                level = parts[1].lower()
                if level in ['beginner', 'intermediate', 'advanced', 'expert']:
                    self.user_context.skill_level = SkillLevel(level)
                    self.user_manager.save()
                    console.print(f"[green]✅ Skill level set to: {level}[/green]")
                else:
                    console.print("[red]Invalid skill level. Use: beginner, intermediate, advanced, or expert[/red]")
            else:
                console.print(f"[cyan]Current skill level: {self.user_context.skill_level.value}[/cyan]")

        elif command.startswith('/flakes'):
            parts = command.split()
            if len(parts) > 1:
                preference = parts[1].lower()
                if preference == 'on':
                    self.user_context.prefers_flakes = True
                    self.user_manager.save()
                    console.print("[green]✅ Flake recommendations enabled[/green]")
                elif preference == 'off':
                    self.user_context.prefers_flakes = False
                    self.user_manager.save()
                    console.print("[yellow]Flake recommendations disabled[/yellow]")
            else:
                status = "enabled" if self.user_context.prefers_flakes else "disabled"
                console.print(f"[cyan]Flake recommendations: {status}[/cyan]")

        elif command == '/history':
            if not self.history:
                console.print("[dim]No conversation history yet[/dim]")
            else:
                console.print("\n[bold]Conversation History:[/bold]")
                for i, msg in enumerate(self.history, 1):
                    role = msg['role'].title()
                    content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                    console.print(f"{i}. [cyan]{role}:[/cyan] {content}")

        elif command == '/status':
            console.print("\n[bold]AI Component Status:[/bold]")
            for component, available in self.components_available.items():
                status = "[green]✓ Available[/green]" if available else "[red]✗ Unavailable[/red]"
                console.print(f"  {component}: {status}")

        elif command == '/knowledge':
            # Show cognitive model knowledge summary
            summary = self.cognitive.get_knowledge_summary()

            knowledge_text = f"""
🧠 **Your NixOS Knowledge Map**

**Overall Progress**: {summary['overall_confidence']:.0%} across {summary['total_concepts']} core concepts

**Knowledge Breakdown**:
- 🌟 Expert: {summary['expert']} concepts
- ⭐ Intermediate: {summary['intermediate']} concepts
- ✨ Basic: {summary['basic']} concepts
- 📚 Not Yet Learned: {summary['unknown']} concepts
"""

            if summary['expert_concepts']:
                knowledge_text += f"\n**Expert Level** ({len(summary['expert_concepts'])}):\n"
                knowledge_text += ", ".join(summary['expert_concepts'][:10])

            if summary['intermediate_concepts']:
                knowledge_text += f"\n\n**Intermediate Level** ({len(summary['intermediate_concepts'])}):\n"
                knowledge_text += ", ".join(summary['intermediate_concepts'][:10])

            if summary['basic_concepts']:
                knowledge_text += f"\n\n**Basic Level** ({len(summary['basic_concepts'])}):\n"
                knowledge_text += ", ".join(summary['basic_concepts'][:10])

            if summary['ready_to_learn']:
                knowledge_text += f"\n\n💡 **Ready to Learn** ({len(summary['ready_to_learn'])}):\n"
                knowledge_text += ", ".join(summary['ready_to_learn'][:5])
                knowledge_text += "\n\n_Say 'teach me about [concept]' to learn more!_"

            console.print(Markdown(knowledge_text))

        elif command == '/learning-profile':
            # 🧠 LAYER 4: Show meta-learning profile
            profile = self.meta_learning.get_learning_profile()

            profile_text = f"""
🎓 **Your Learning Profile**

**Primary Learning Style**: {profile['primary_learning_style'].title()}
**Teaching Interactions**: {profile['teaching_history']['total_attempts']}
**Recent Effectiveness**: {profile['teaching_history']['recent_effectiveness']:.0%}
**Learning Trend**: {profile['teaching_history']['improvement_trend'].title()}

**Learning Preferences**:
- Example Count: {profile['preferences']['example_count_needed']}
- Learning Pace: {profile['preferences']['learning_pace'].title()}
- Prefers Practice: {"✓" if profile['preferences']['prefers_practice'] else "✗"}
- Confidence: {profile['preferences']['confidence']:.0%}
"""

            if profile['discovered_patterns']:
                profile_text += f"\n**Discovered Patterns** ({len(profile['discovered_patterns'])}):\n"
                for pattern in profile['discovered_patterns'][:3]:
                    profile_text += f"- {pattern['description']}\n"
                    profile_text += f"  _Confidence: {pattern['confidence']:.0%} | {pattern['recommendation']}_\n\n"

            profile_text += "\n_Your learning profile helps me teach you more effectively!_"

            console.print(Markdown(profile_text))

        elif command.startswith('/teach'):
            # Start a Socratic teaching session
            parts = command.split()
            if len(parts) > 1:
                concept = parts[1].lower()
                message, success = self.socratic.start_teaching(concept, session_id="main")
                if success:
                    self.active_teaching_session = concept
                    console.print(Markdown(message))
                    console.print("[dim]💡 Respond to the questions to learn! Say '/stop-teaching' to exit.[/dim]")
                else:
                    console.print(Markdown(message))
            else:
                console.print("[yellow]Usage: /teach [concept][/yellow]")
                console.print("[dim]Available concepts: declarative, generations, flakes, modules[/dim]")

        elif command == '/stop-teaching':
            if self.active_teaching_session:
                self.active_teaching_session = None
                console.print("[green]✅ Teaching session ended. You can continue chatting normally![/green]")
            else:
                console.print("[yellow]No active teaching session to stop.[/yellow]")

        elif command == '/onboarding':
            # 🌟 LAYER 5: Start onboarding process
            self._run_onboarding()

        elif command == '/profile':
            # 🌟 LAYER 5: Show user profile
            if not self.user_profile:
                console.print("[yellow]⚠ No user profile found. Run '/onboarding' to create one![/yellow]")
            else:
                self._show_user_profile()

    def _handle_query(self, query: str) -> str:
        """
        Route query to appropriate AI component with full context.
        Uses smart domain routing to determine if query is NixOS-specific
        or general IT assistance.
        """

        # Step 1: Extract recent domains from conversation history
        recent_domains = self._extract_recent_domains()
        if os.getenv("DEBUG_ROUTING"):
            print(f"[DEBUG] Extracted recent domains: {[d.value for d in recent_domains] if recent_domains else 'None'}")
            print(f"[DEBUG] History length: {len(self.history)}")

        # Step 2: Use QueryRouter to determine domain with conversation context
        route = self.query_router.route(query, conversation_context=recent_domains)

        # Step 2.5: Store domain in the last history entry (the user's query)
        if self.history and self.history[-1]['role'] == 'user':
            self.history[-1]['domain'] = route.domain

        # Step 3: Display domain transparency (what mode we're in)
        domain_indicator = self._get_domain_indicator(route)

        # Step 3: Check if we should recommend flakes (only for NixOS queries)
        flake_rec = None
        if route.domain == Domain.NIXOS and self.user_context.prefers_flakes:
            if self.flake_recommender.should_recommend_flake(
                query, self.user_context, self.system_context
            ):
                flake_rec = self.flake_recommender.get_flake_recommendation(
                    query, self.user_context.skill_level
                )

        # Step 4: Route to appropriate handler
        if route.domain == Domain.NIXOS:
            # NixOS-specific query - use specialist components
            response = self._handle_nixos_query(query, route)
        else:
            # General IT query - use general AI with context
            response = self._handle_general_it_query(query, route)

            # Offer NixOS-specific context if applicable
            if route.should_offer_nixos_context:
                nixos_offer = self._get_nixos_context_offer()
                response = f"{response}\n\n{nixos_offer}"

        # Step 5: Add domain indicator and flake recommendation
        final_response = f"{domain_indicator}{response}"

        if flake_rec:
            final_response = f"{final_response}\n{flake_rec}"

        return final_response

    def _get_domain_indicator(self, route: RouteResult) -> str:
        """Get domain indicator for transparency"""
        emoji = self.query_router.get_domain_emoji(route.domain)
        display_name = self.query_router.get_domain_display_name(route.domain)

        # Only show indicator for non-NixOS queries (to avoid clutter for main use case)
        if route.domain != Domain.NIXOS:
            # Show confidence if low (indicates uncertainty)
            if route.confidence < 0.5:
                confidence_indicator = f" - [yellow]Low Confidence ({route.confidence:.0%})[/yellow]"
                clarification_hint = "\n[dim italic]💡 I'm not entirely sure about the domain. Feel free to clarify if my answer seems off-topic![/dim italic]\n\n"
            elif route.confidence < 0.7:
                confidence_indicator = f" - [dim]({route.confidence:.0%})[/dim]"
                clarification_hint = ""
            else:
                confidence_indicator = ""
                clarification_hint = ""

            return f"[dim]{emoji} [{display_name} Mode]{confidence_indicator}[/dim]{clarification_hint}\n\n"
        return ""

    def _get_nixos_context_offer(self) -> str:
        """Offer to show NixOS-specific solution"""
        return (
            "💡 [dim]Want to see how to set this up specifically on NixOS? "
            "Just say 'show me the NixOS way'![/dim]"
        )

    def _handle_nixos_query(self, query: str, route: RouteResult) -> str:
        """Handle NixOS-specific queries using specialist components"""

        # Use existing pattern-based routing for NixOS queries
        query_lower = query.lower()

        # 1. Error Resolution
        if any(word in query_lower for word in ['error', 'failed', 'broken', 'issue', 'problem']):
            if self.components_available['error_resolver']:
                return self._resolve_error(query)
            else:
                return self._fallback_response(query, "error resolution")

        # 2. Configuration Generation
        elif any(word in query_lower for word in ['setup', 'configure', 'create', 'generate', 'enable', 'install']):
            if self.components_available['config_gen']:
                return self._generate_config(query)
            else:
                return self._fallback_response(query, "configuration generation")

        # 3. Package Recommendations
        elif any(word in query_lower for word in ['recommend', 'alternative', 'similar', 'suggest', 'find']):
            if self.components_available['package_rec']:
                return self._recommend_packages(query)
            else:
                return self._fallback_response(query, "package recommendations")

        # 4. Command Explanation
        elif any(word in query_lower for word in ['what does', 'explain', 'how does', 'what is']):
            if self.components_available['cmd_explainer']:
                return self._explain_command(query)
            else:
                return self._fallback_response(query, "command explanation")

        # 5. General NixOS query - use orchestrator
        else:
            if self.components_available['orchestrator']:
                return self._general_query(query)
            else:
                return self._fallback_response(query, "general assistance")

    def _handle_general_it_query(self, query: str, route: RouteResult) -> str:
        """
        Handle general IT queries using general knowledge AI.
        These queries are not NixOS-specific.

        Automatically provides dual-answer mode: shows both general approach
        AND the NixOS way when applicable.
        """

        # For now, route all general IT queries through the orchestrator
        # In the future, we can add specialized handlers for each domain
        if self.components_available['orchestrator']:
            # Build domain-aware context for better answers
            domain_prompts = {
                Domain.PROGRAMMING: """
You are a programming expert. Provide:
- Clear code examples with explanations
- Language-specific best practices
- Common pitfalls and how to avoid them
- Practical, working solutions
""",
                Domain.DEVOPS: """
You are a DevOps specialist. Focus on:
- Production-ready solutions and best practices
- Scalability and reliability considerations
- Real-world operational concerns
- Container orchestration and CI/CD
""",
                Domain.NETWORKING: """
You are a networking engineer. Provide:
- Configuration examples with explanations
- Troubleshooting steps and diagnostics
- Security considerations
- Performance optimization tips
""",
                Domain.DATABASE: """
You are a database consultant. Focus on:
- Query optimization and indexing strategies
- Schema design best practices
- Data integrity and ACID properties
- Performance tuning and monitoring
""",
                Domain.SECURITY: """
You are a security advisor. Emphasize:
- Security best practices and standards
- Potential vulnerabilities and mitigations
- Defense in depth strategies
- Real-world threat scenarios
""",
                Domain.GENERAL: """
You are a knowledgeable IT assistant. Provide:
- Clear, practical guidance
- Step-by-step instructions when helpful
- Multiple approaches if relevant
"""
            }

            prompt_style = domain_prompts.get(route.domain, domain_prompts[Domain.GENERAL])

            # Build rich context
            context_hint = f"""
QUERY DOMAIN: {route.domain.value.upper()}
ROUTING CONFIDENCE: {route.confidence:.1%}

RESPONSE GUIDELINES:
{prompt_style}

USER SKILL LEVEL: {self.user_context.skill_level.value}
ADAPT TO: {"Provide detailed explanations" if self.user_context.skill_level.value == "beginner" else "Be concise and technical"}
"""

            # Get general answer
            general_answer = self._general_query(query, extra_context=context_hint)

            # Check if dual-answer mode is enabled for this user
            # (Default OFF for beginners, ON for advanced users)
            dual_answer_enabled = self.user_context.preferences.get('dual_answer_mode', False)

            # Check if we can provide NixOS-specific context (dual-answer mode)
            if dual_answer_enabled and self.nixos_context_gen.can_provide_nixos_context(query, route.domain):
                nixos_answer = self.nixos_context_gen.generate_nixos_context(query, general_answer)

                if nixos_answer:
                    # Format as dual answer
                    return self.nixos_context_gen.get_dual_answer_format(general_answer, nixos_answer)

            # Return just general answer if dual-answer disabled or no NixOS context available
            return general_answer
        else:
            return self._fallback_general_it_response(query, route)

    def _resolve_error(self, query: str) -> str:
        """Resolve error with context awareness"""
        try:
            result = self.error_resolver.resolve(query)

            # Adapt response based on skill level
            if self.user_context.skill_level == SkillLevel.BEGINNER:
                # Add extra explanation for beginners
                result = f"📍 **Error Analysis**\n\n{result}\n\n💡 **Tip**: I can walk you through this step-by-step. Just ask!"

            return result
        except Exception as e:
            return f"I tried to analyze that error but encountered an issue: {e}\n\nCould you provide more details?"

    def _generate_config(self, query: str) -> str:
        """Generate configuration with flake preference and anticipatory suggestions"""
        try:
            # Check if user prefers flakes
            if self.user_context.prefers_flakes and not self.system_context.has_flake_nix:
                # Add note about flakes
                traditional = self.config_gen.generate(query)
                flake_note = "\n\n💡 **Flake Version Available**: I can generate a `flake.nix` for this instead. Say 'make it a flake' if you'd like that."
                response = traditional + flake_note
            else:
                response = self.config_gen.generate(query)

            # 🔮 REVOLUTIONARY: Predict what user needs next
            # Check if we should anticipate next steps
            anticipation = self.anticipatory.anticipate_next_steps(query, "configured this")

            if anticipation:
                # Add anticipatory suggestions to response
                anticipation_text = self.anticipatory.format_anticipation(anticipation)
                response = f"{response}\n{anticipation_text}"

            return response
        except Exception as e:
            return f"I had trouble generating that configuration: {e}\n\nCould you describe what you need in more detail?"

    def _recommend_packages(self, query: str) -> str:
        """Recommend packages"""
        try:
            return self.recommender.recommend(query)
        except Exception as e:
            return f"I had trouble finding recommendations: {e}\n\nTry searching with: nix search nixpkgs <term>"

    def _explain_command(self, query: str) -> str:
        """Explain command"""
        try:
            return self.explainer.explain(query)
        except Exception as e:
            return f"I had trouble explaining that: {e}\n\nWhat specific part would you like me to clarify?"

    def _general_query(self, query: str, extra_context: str = "") -> str:
        """Handle general query with orchestrator"""

        # 🚀 REVOLUTIONARY: Auto-heal before processing query
        # This ensures Ollama is running, starting it automatically if needed
        ready, error = self.self_healing.auto_heal_before_query(query, needs_ollama=True)

        if not ready:
            # Couldn't auto-fix - tell user what happened
            return f"""I tried to start Ollama for you, but ran into an issue.

{error}

Once Ollama is running, I'll be able to help with this question!
For NixOS-specific questions, I can help right now without Ollama."""

        # Build context string for AI
        try:
            context = f"""
{self.system_context.to_context_string()}
{self.user_context.to_context_string()}

Recent conversation:
{self._format_recent_history()}

{extra_context}
"""

            # Call orchestrator's answer_query method (not understand_query which is for intent detection)
            result = self.orchestrator.answer_query(query, context=context)

            # Handle AIResponse object correctly
            if hasattr(result, 'result'):
                response_data = result.result
                # If it's a dict with response key
                if isinstance(response_data, dict):
                    if 'response' in response_data:
                        return response_data['response']
                    # Otherwise format the dict nicely
                    return str(response_data)
                # If it's a string or other type
                return str(response_data)

            # Fallback to string representation
            return str(result)
        except Exception as e:
            import traceback
            print(f"General query error: {e}")
            traceback.print_exc()
            return self._fallback_response(query, "general assistance")

    def _fallback_response(self, query: str, feature: str) -> str:
        """Fallback when component unavailable"""
        return f"""
I'd like to help with {feature}, but that component isn't available right now.

Here's what I can suggest:
1. Check if all dependencies are installed
2. Try running: `nixos-rebuild switch` if you've updated your config
3. Search NixOS manual: https://nixos.org/manual/

Your query was: "{query}"

What else can I help you with?
"""

    def _fallback_general_it_response(self, query: str, route: RouteResult) -> str:
        """Fallback for general IT queries when orchestrator unavailable"""
        domain_name = self.query_router.get_domain_display_name(route.domain)

        return f"""
I recognize this as a {domain_name.lower()} question, but my general knowledge AI isn't available right now.

Your query: "{query}"

Here are some suggestions:
1. For NixOS-specific help, try rephrasing with "nixos" or "nix"
2. Check online documentation for {domain_name.lower()}
3. Try asking a more specific NixOS-related question

What can I help you with?
"""

    def _detect_teaching_request(self, query: str) -> Optional[str]:
        """
        Detect if user is requesting to learn a concept.

        Returns concept_id if teaching requested, None otherwise.
        """
        query_lower = query.lower()

        # Teaching triggers
        teach_phrases = [
            'teach me about', 'teach me', 'learn about', 'explain',
            'what is', 'what are', 'how does', 'how do'
        ]

        # Available concepts in Socratic teacher
        available_concepts = {
            'declarative': ['declarative', 'declarative configuration', 'declarative config'],
            'generations': ['generation', 'generations', 'rollback', 'system generation'],
            'flakes': ['flake', 'flakes', 'flake.nix'],
            'modules': ['module', 'modules', 'nixos module', 'modular']
        }

        # Check if query contains a teaching trigger
        has_trigger = any(phrase in query_lower for phrase in teach_phrases)

        if not has_trigger:
            return None

        # Find which concept they want to learn
        for concept_id, keywords in available_concepts.items():
            if any(keyword in query_lower for keyword in keywords):
                return concept_id

        return None

    def _extract_recent_domains(self, n=5) -> List[Domain]:
        """
        Extract recent domains from conversation history.

        Args:
            n: Number of recent interactions to consider

        Returns:
            List of recent domains (most recent last)
        """
        if not self.history:
            return []

        recent_domains = []
        for msg in self.history[-n:]:
            if msg['role'] == 'user' and 'domain' in msg:
                recent_domains.append(msg['domain'])

        return recent_domains

    def _format_recent_history(self, n=3) -> str:
        """Format recent conversation history"""
        if not self.history:
            return "(No previous conversation)"

        recent = self.history[-n:]
        formatted = []
        for msg in recent:
            role = msg['role'].title()
            content = msg['content'][:200]  # Truncate long messages
            formatted.append(f"{role}: {content}")

        return "\n".join(formatted)

    def _run_onboarding(self):
        """
        🌟 LAYER 5: Run onboarding questionnaire to create user profile.

        This is revolutionary - we LEARN about each user rather than assuming.
        """
        console.print("\n[bold cyan]🌟 Welcome to Luminous Nix Onboarding![/bold cyan]\n")
        console.print("""
This quick questionnaire helps me understand YOU better so I can provide
an experience tailored to your goals, style, and preferences.

There are no wrong answers - just be honest about what you want!
""")

        # Get questions
        questions = self.user_profiler.get_onboarding_questions()
        responses = {}

        for i, q in enumerate(questions, 1):
            console.print(f"\n[bold]Question {i}/{len(questions)}:[/bold]")
            console.print(f"{q.question}\n")

            # Display options
            for idx, option in enumerate(q.options):
                console.print(f"  {idx + 1}. {option}")

            # Get user choice
            while True:
                try:
                    choice = console.input("\n[bold green]Your choice (1-4):[/bold green] ").strip()
                    choice_idx = int(choice) - 1

                    if 0 <= choice_idx < len(q.options):
                        responses[q.id] = choice_idx
                        break
                    else:
                        console.print("[yellow]Please enter a number between 1 and 4[/yellow]")
                except ValueError:
                    console.print("[yellow]Please enter a valid number[/yellow]")

        # Generate profile from responses
        console.print("\n[cyan]🔮 Analyzing your responses...[/cyan]\n")
        self.user_profile = self.user_profiler.generate_initial_profile(responses)

        # Show results
        console.print("[green]✅ Profile created successfully![/green]\n")
        self._show_user_profile()

        console.print("\n[dim]💡 Your profile will help me adapt to your style. You can always")
        console.print("re-run onboarding with '/onboarding' or view your profile with '/profile'[/dim]\n")

    def _show_user_profile(self):
        """🌟 LAYER 5: Display user profile"""
        if not self.user_profile:
            console.print("[yellow]No profile found.[/yellow]")
            return

        archetype_descriptions = {
            UserArchetype.LEARNER: "You want to understand NixOS deeply. I'll provide detailed explanations, teaching moments, and help you build lasting knowledge.",
            UserArchetype.PRAGMATIST: "You want a working system without fuss. I'll be concise, efficient, and focus on getting things done quickly.",
            UserArchetype.EXPLORER: "You want to discover what's possible. I'll show you alternatives, options, and interesting possibilities you might not know about.",
            UserArchetype.CREATOR: "You want to build custom solutions. I'll collaborate with you as a technical peer, providing tools and deep technical knowledge."
        }

        engagement_descriptions = {
            EngagementMode.FULL_TEACHING: "Detailed explanations with educational content",
            EngagementMode.JUST_DO_IT: "Minimal talk, maximum action",
            EngagementMode.SHOWCASE_POSSIBILITIES: "Show options and alternatives",
            EngagementMode.COLLABORATIVE_DEV: "Technical peer collaboration",
            EngagementMode.ADAPTIVE: "Adapts based on context"
        }

        profile_md = f"""
## 🌟 Your User Profile

**Archetype**: **{self.user_profile.archetype.value.title()}**
{archetype_descriptions.get(self.user_profile.archetype, "")}

**Technical Level**: {self.user_profile.technical_level.value.title()}
**Engagement Mode**: {engagement_descriptions.get(self.user_profile.engagement_mode, "Adaptive")}

**Your Preferences**:
- 📚 Wants learning content: {"✓ Yes" if self.user_profile.wants_learning else "✗ No"}
- ⚡ Prefers automation: {"✓ Yes" if self.user_profile.prefers_automation else "✗ No"}
- 🔍 Interested in alternatives: {"✓ Yes" if self.user_profile.interested_in_alternatives else "✗ No"}
- 🛠️ Interested in customization: {"✓ Yes" if self.user_profile.interested_in_customization else "✗ No"}
"""

        if self.user_profile.primary_goals:
            profile_md += "\n**Your Goals**:\n"
            for goal in self.user_profile.primary_goals:
                status = "✓" if goal.completed else "○"
                profile_md += f"- {status} {goal.description} (Priority: {goal.priority}/5)\n"

        if self.user_profile.learning_style:
            profile_md += f"\n**Learning Style**: {self.user_profile.learning_style.title()} (from Layer 4 meta-learning)"

        profile_md += f"""

**Profile Stats**:
- Sessions: {self.user_profile.sessions_count}
- Archetype Confidence: {self.user_profile.archetype_confidence:.0%}
- Technical Level Confidence: {self.user_profile.technical_level_confidence:.0%}
- Onboarding Complete: {"✓" if self.user_profile.onboarding_complete else "✗"}
"""

        console.print(Panel(Markdown(profile_md), border_style="cyan", title="[bold]Your Profile[/bold]"))


# Entry point
def main():
    """Main entry point for chat mode"""
    try:
        chat = SimpleChat()
        chat.chat_loop()
    except Exception as e:
        console.print(f"\n[bold red]Fatal error:[/bold red] {e}\n")
        import traceback
        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
