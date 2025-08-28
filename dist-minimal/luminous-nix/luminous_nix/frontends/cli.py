"""
Simple CLI interface for Luminous Nix - Making basic commands work
"""

import os
import subprocess
import sys

# Try to import Ollama integration
try:
    from luminous_nix.ai.ollama_client import OllamaClient, SocraticOllama

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Import search cache for better performance
try:
    from luminous_nix.core.search_cache import SearchCache

    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

# Import robust architecture components
try:
    from luminous_nix.core.command_executor import (
        CommandExecutor,
        CommandStatus,
        CommandType,
    )
    from luminous_nix.core.conversation_state import ConversationState
    from luminous_nix.core.error_recovery import ErrorRecovery

    ARCHITECTURE_AVAILABLE = True
except ImportError:
    ARCHITECTURE_AVAILABLE = False

# Import intent pipeline and plugin system
try:
    from luminous_nix.core.intent_pipeline import Intent, IntentRecognitionPipeline
    from luminous_nix.core.plugin_system import PluginManager

    ADVANCED_FEATURES = True
except ImportError:
    ADVANCED_FEATURES = False


class UnifiedNixAssistant:
    """Basic Nix assistant that actually works with real commands"""

    def __init__(self):
        # Read flags from environment (set by bin/ask-nix)
        self.dry_run = os.environ.get("LUMINOUS_DRY_RUN", "").lower() == "true"
        self.skip_confirmation = (
            os.environ.get("LUMINOUS_SKIP_CONFIRM", "").lower() == "true"
        )
        self.execute_mode = os.environ.get("LUMINOUS_EXECUTE", "").lower() == "true"
        self.quiet_mode = os.environ.get("LUMINOUS_QUIET", "").lower() == "true"
        self.verbose_level = int(os.environ.get("LUMINOUS_VERBOSE", "0"))
        self.ask_mode = os.environ.get("LUMINOUS_ASK_MODE", "").lower() == "true"
        self.persona = os.environ.get("LUMINOUS_PERSONA", "friendly")
        self.ai_enabled = os.environ.get("LUMINOUS_AI_ENABLED", "").lower() == "true"

        # Voice support
        self.voice_enabled = (
            os.environ.get("LUMINOUS_VOICE_ENABLED", "").lower() == "true"
        )
        self.speak_responses = (
            os.environ.get("LUMINOUS_SPEAK_RESPONSES", "").lower() == "true"
        )
        self.continuous_listen = (
            os.environ.get("LUMINOUS_CONTINUOUS_LISTEN", "").lower() == "true"
        )
        
        # Initialize REAL backend
        self.real_backend = None
        try:
            from luminous_nix.core.backend_real import RealNixBackend
            self.real_backend = RealNixBackend()
            if self.verbose_level > 0:
                print("✅ Real NixOS backend initialized")
        except ImportError as e:
            if self.verbose_level > 0:
                print(f"⚠️ Could not initialize real backend: {e}")

        # Visual/progress settings
        self.visual_mode = not self.quiet_mode
        self.show_progress = not self.quiet_mode
        self.personality = self.persona

        # Initialize AI clients if available and enabled
        self.ollama = None
        self.socratic = None
        if OLLAMA_AVAILABLE and (self.ai_enabled or self.ask_mode):
            try:
                self.ollama = OllamaClient()
                self.socratic = SocraticOllama()
                if self.verbose_level > 0:
                    print("🤖 AI assistance enabled")
            except Exception as e:
                if self.verbose_level > 0:
                    print(f"⚠️ Could not initialize AI: {e}")

        # Initialize search cache for better performance
        self.search_cache = None
        if CACHE_AVAILABLE:
            try:
                self.search_cache = SearchCache()
                if self.verbose_level > 1:
                    print("💾 Search cache enabled")
            except Exception as e:
                if self.verbose_level > 0:
                    print(f"⚠️ Could not initialize cache: {e}")

        # Initialize robust architecture components
        self.command_executor = None
        self.error_recovery = None
        self.conversation_state = None

        if ARCHITECTURE_AVAILABLE:
            try:
                # Initialize command executor for robust execution
                self.command_executor = CommandExecutor()
                self.command_executor.dry_run = self.dry_run
                self.command_executor.confirm_callback = (
                    self._confirm_command if not self.skip_confirmation else None
                )

                # Initialize error recovery for intelligent error handling
                self.error_recovery = ErrorRecovery()

                # Initialize conversation state for multi-turn conversations
                self.conversation_state = ConversationState()

                if self.verbose_level > 1:
                    print("🔧 Robust architecture enabled")
            except Exception as e:
                if self.verbose_level > 0:
                    print(f"⚠️ Could not initialize robust architecture: {e}")

        # Initialize voice interface
        self.voice_interface = None
        if self.voice_enabled or self.speak_responses:
            try:
                from luminous_nix.voice.voice_interface import VoiceInterface

                self.voice_interface = VoiceInterface(verbose=self.verbose_level > 0)
                if self.verbose_level > 0:
                    print("🎙️ Voice interface enabled")
            except Exception as e:
                if self.verbose_level > 0:
                    print(f"⚠️ Could not initialize voice interface: {e}")

        # Initialize advanced features with secure intent recognition
        self.intent_pipeline = None
        self.plugin_manager = None

        # Try to use secure intent recognition first
        try:
            from luminous_nix.core.secure_intent_integration import (
                create_secure_pipeline_for_cli,
            )

            self.intent_pipeline = create_secure_pipeline_for_cli(
                verbose=self.verbose_level > 0,
                security_level=os.environ.get("LUMINOUS_SECURITY_LEVEL", "medium"),
            )
            if self.verbose_level > 0:
                security_level = self.intent_pipeline.security_level
                print(
                    f"🔐 Secure intent recognition enabled (security: {security_level})"
                )
        except ImportError:
            # Fall back to old intent pipeline if secure version not available
            if ADVANCED_FEATURES:
                try:
                    # Initialize intent recognition pipeline
                    self.intent_pipeline = IntentRecognitionPipeline()
                    if self.verbose_level > 0:
                        print("🎯 Basic intent recognition enabled")
                except Exception as e:
                    if self.verbose_level > 0:
                        print(f"⚠️ Could not initialize intent pipeline: {e}")
        except Exception as e:
            if self.verbose_level > 0:
                print(f"⚠️ Could not initialize secure intent recognition: {e}")

        # Initialize plugin manager if available
        if ADVANCED_FEATURES:
            try:
                # Initialize plugin manager
                self.plugin_manager = PluginManager()
                self.plugin_manager.load_config()  # Load saved plugin configuration

                if self.verbose_level > 1:
                    loaded_plugins = self.plugin_manager.list_plugins()
                    if loaded_plugins:
                        print(
                            f"📦 Loaded plugins: {', '.join(p.name for p in loaded_plugins)}"
                        )
            except Exception as e:
                if self.verbose_level > 0:
                    print(f"⚠️ Could not initialize plugin manager: {e}")

    def set_personality(self, personality: str):
        """Set the response personality"""
        self.personality = personality

    def _confirm_command(self, command) -> bool:
        """Confirmation callback for command executor"""
        response = input(f"Execute: {command.description}? (y/N): ")
        return response.lower() == "y"

    def _execute_intent(self, intent_result):
        """Execute based on recognized intent"""
        # Handle both IntentType and Intent enums
        intent = intent_result.primary_intent

        # If we get IntentType from secure pipeline, convert to Intent
        if hasattr(intent, "value"):
            # Map between IntentType and Intent enum values
            intent_mapping = {
                "install_package": "install",
                "remove_package": "remove",
                "search_package": "search",
                "update_system": "update",
                "list_installed": "list",
                "garbage_collect": "garbage_collect",
                "create_shell": "create_shell",
                "help": "help",
                "rollback": "rollback",
                "diagnose": "diagnose",
            }

            # Try to get Intent enum by mapped value
            try:
                intent_value = intent.value
                mapped_value = intent_mapping.get(intent_value, intent_value)
                # Find corresponding Intent enum
                for intent_enum in Intent:
                    if intent_enum.value == mapped_value:
                        intent = intent_enum
                        break
            except:
                pass

        entities = intent_result.entities

        # Extract package/term from entities - improved logic
        package = None
        term = None

        # Filter out common mis-extracted words and use highest confidence entity
        best_package = None
        best_package_confidence = 0

        for entity in entities:
            if entity.type == "package":
                # Skip words that are likely not package names
                if entity.value.lower() in {
                    "install",
                    "remove",
                    "update",
                    "search",
                    "find",
                    "get",
                    "add",
                    "delete",
                    "i",
                    "want",
                    "to",
                    "need",
                    "please",
                    "can",
                    "you",
                    "help",
                    "me",
                    "a",
                    "an",
                    "the",
                }:
                    continue
                # Use the entity with highest confidence
                if entity.confidence > best_package_confidence:
                    best_package = entity.value
                    best_package_confidence = entity.confidence
            elif entity.type in ["term", "query"]:
                term = entity.value

        package = best_package

        # Map intent to action
        if intent == Intent.INSTALL:
            if package:
                if self.command_executor:
                    self._install_package_robust(package)
                else:
                    self._install_package(package)
            else:
                print("❌ Please specify what to install")

        elif intent == Intent.REMOVE:
            if package:
                if self.command_executor:
                    self._remove_package_robust(package)
                else:
                    self._remove_package(package)
            else:
                print("❌ Please specify what to remove")

        elif intent == Intent.SEARCH:
            if term or package:
                self._search_packages(term or package)
            else:
                print("❌ Please specify what to search for")

        elif intent == Intent.UPDATE:
            self._handle_update("")

        elif intent == Intent.LIST:
            self._handle_list_installed()

        elif intent == Intent.ROLLBACK:
            if self.command_executor:
                result = self.command_executor.rollback()
                if result.success():
                    print("✅ Successfully rolled back!")
                else:
                    print(f"❌ Rollback failed: {result.stderr}")
            else:
                self._handle_rollback()

        elif intent == Intent.HELP:
            self._show_help()

        elif intent == Intent.GARBAGE_COLLECT:
            self._handle_garbage_collect()

        elif intent == Intent.CREATE_SHELL:
            if package:
                self._create_dev_shell(package)
            else:
                print("❌ Please specify what kind of development environment")

        elif intent == Intent.DIAGNOSE:
            self._handle_diagnose(intent_result.original_query)

        else:
            print(f"🚧 Intent '{intent.value}' recognized but not yet implemented")

        # Update conversation state
        if self.conversation_state:
            self.conversation_state.add_turn(
                query=intent_result.original_query,
                response=f"Executed {intent.value} command",
                intent=intent.value,
                entities={e.type: e.value for e in entities},
                success=True,
            )

    def _ask_for_feedback(self, query: str, recognized_intent):
        """Ask user for feedback on intent recognition (for learning)."""
        # Only ask occasionally, not every time
        import random

        if random.random() > 0.1:  # Ask 10% of the time
            return

        try:
            response = (
                input("\n💭 Was that the right action? (y/n/skip): ").lower().strip()
            )
            if response == "n":
                self._handle_incorrect_intent(query, recognized_intent)
        except (KeyboardInterrupt, EOFError):
            pass  # User doesn't want to provide feedback

    def _handle_incorrect_intent(self, query: str, wrong_intent):
        """Handle when intent was incorrectly recognized."""
        if not hasattr(self.intent_pipeline, "learn_correction"):
            return

        print("\n🤔 What did you actually want to do?")
        print("  1. Install a package")
        print("  2. Search for packages")
        print("  3. Update system")
        print("  4. Configure something")
        print("  5. Get help")
        print("  6. Other")

        try:
            choice = input("Enter number (or press Enter to skip): ").strip()

            # Map choice to intent type
            from luminous_nix.core.intents import IntentType

            intent_map = {
                "1": IntentType.INSTALL_PACKAGE,
                "2": IntentType.SEARCH_PACKAGES,
                "3": IntentType.UPDATE_SYSTEM,
                "4": IntentType.CONFIGURATION,
                "5": IntentType.HELP,
            }

            if choice in intent_map:
                correct_intent = intent_map[choice]
                # Teach the system
                success = self.intent_pipeline.learn_correction(
                    query, correct_intent, user_id=os.environ.get("USER", "unknown")
                )
                if success:
                    print("✅ Thanks! I'll remember that for next time.")
                else:
                    print("📝 Thanks for the feedback!")
        except (KeyboardInterrupt, EOFError):
            pass  # User cancelled

    def answer(self, query: str):
        """Process natural language query and execute appropriate Nix command"""
        query_lower = query.lower().strip()
        context = {}

        # If we have conversation state, add this turn and resolve pronouns
        if self.conversation_state:
            # Get context for this query
            context = self.conversation_state.get_context_for_query(query)

            # Resolve pronouns if present
            query_resolved = self.conversation_state.resolve_pronouns(query)
            if query_resolved != query:
                if self.verbose_level > 0:
                    print(f"📝 Resolved: '{query}' → '{query_resolved}'")
                query = query_resolved
                query_lower = query.lower().strip()

            # Check if clarification is needed
            clarification = self.conversation_state.get_clarification_needed()
            if clarification:
                print(f"❓ {clarification}")
                if not self.skip_confirmation:
                    response = input("Your answer: ")
                    query = f"{query} {response}"
                    query_lower = query.lower().strip()

        # Check if it's a plugin command first
        if self.plugin_manager:
            # Check if query matches a plugin command
            parts = query.split()
            if parts and parts[0] in self.plugin_manager.commands:
                try:
                    # Trigger pre-command hook
                    self.plugin_manager.trigger_hook("pre_command", query=query)

                    # Execute plugin command
                    result = self.plugin_manager.execute_command(parts[0], *parts[1:])
                    print(result)

                    # Trigger post-command hook
                    self.plugin_manager.trigger_hook(
                        "post_command", query=query, result=result
                    )

                    # Update conversation state
                    if self.conversation_state:
                        self.conversation_state.add_turn(
                            query=query,
                            response=str(result),
                            intent="plugin_command",
                            entities={"command": parts[0]},
                            success=True,
                        )
                    return
                except Exception as e:
                    print(f"❌ Plugin command failed: {e}")
                    return

        # Use intent pipeline if available
        if self.intent_pipeline:
            intent_result = self.intent_pipeline.recognize(query, context)

            # Check if the input was blocked for security reasons
            if hasattr(intent_result, "metadata") and intent_result.metadata.get(
                "security_block"
            ):
                print(
                    f"🚫 {intent_result.suggestions[0] if intent_result.suggestions else 'Input blocked for security reasons'}"
                )
                block_reason = intent_result.metadata.get("block_reason", "unknown")
                if block_reason == "RATE_LIMITED":
                    print("⏱️ Please wait a moment before trying again.")
                elif block_reason in ["MALICIOUS_INPUT", "ADVERSARIAL_INPUT"]:
                    print("⚠️ For security reasons, this input cannot be processed.")
                return

            if self.verbose_level > 0:
                print(
                    f"🎯 Intent: {intent_result.primary_intent.value} (confidence: {intent_result.confidence:.2f})"
                )
                if intent_result.entities:
                    print(
                        f"📝 Entities: {', '.join(f'{e.type}={e.value}' for e in intent_result.entities)}"
                    )

            # Trigger intent_recognized hook
            if self.plugin_manager:
                self.plugin_manager.trigger_hook(
                    "intent_recognized", intent=intent_result
                )

            # If high confidence, execute based on intent
            if intent_result.confidence > 0.7:
                self._execute_intent(intent_result)
                # Ask for feedback if learning is enabled
                if (
                    hasattr(self.intent_pipeline, "learn_correction")
                    and not self.skip_confirmation
                ):
                    self._ask_for_feedback(query, intent_result.primary_intent)
                return
            if intent_result.confidence > 0.5:
                # Medium confidence - ask for confirmation
                if intent_result.suggestions:
                    print(f"🤔 {intent_result.suggestions[0]}")
                    if not self.skip_confirmation:
                        response = input("Is this correct? (y/N): ")
                        if response.lower() == "y":
                            self._execute_intent(intent_result)
                            return
                        # Learn from the correction
                        self._handle_incorrect_intent(
                            query, intent_result.primary_intent
                        )
                        return

        # Try AI understanding if enabled
        if self.ollama and self.ai_enabled:
            intent_data = self.ollama.parse_intent(query)
            if intent_data.get("confidence", 0) > 0.6:
                if self.verbose_level > 0:
                    print(
                        f"🤖 AI understands: {intent_data.get('suggestion', 'Processing...')}"
                    )

                # Route based on AI-detected intent
                if intent_data["intent"] == "install":
                    entities = intent_data.get("entities", [])
                    if entities:
                        self._install_package_robust(entities[0])
                        return
                elif intent_data["intent"] == "search":
                    entities = intent_data.get("entities", [])
                    if entities:
                        self._search_packages(" ".join(entities))
                        return
                elif intent_data["intent"] == "remove":
                    entities = intent_data.get("entities", [])
                    if entities:
                        self._remove_package_robust(entities[0])
                        return

        # Fallback to pattern matching
        intent = None
        entities = {}
        success = True
        response = ""

        if "list" in query_lower and (
            "installed" in query_lower or "packages" in query_lower
        ) or "what's installed" in query_lower or "show installed" in query_lower:
            intent = "list"
            self._handle_list_installed()
        elif (
            "search" in query_lower
            or "find" in query_lower
            or "look for" in query_lower
        ):
            intent = "search"
            self._handle_search(query_lower)
        elif "install" in query_lower:
            intent = "install"
            self._handle_install(query_lower)
        elif (
            "remove" in query_lower
            or "uninstall" in query_lower
            or "delete" in query_lower
        ):
            intent = "remove"
            self._handle_remove(query_lower)
        elif "update" in query_lower or "upgrade" in query_lower:
            intent = "update"
            self._handle_update(query_lower)
        elif (
            "rollback" in query_lower
            or "previous" in query_lower
            or "undo" in query_lower
        ):
            intent = "rollback"
            if self.command_executor and self.command_executor.get_history():
                # Use command executor's rollback
                result = self.command_executor.rollback()
                if result.success():
                    print("✅ Successfully rolled back!")
                    response = "Rolled back to previous state"
                else:
                    print(f"❌ Rollback failed: {result.stderr}")
                    response = f"Rollback failed: {result.stderr}"
                    success = False
            else:
                self._handle_rollback()
        elif "create" in query_lower and (
            "shell" in query_lower
            or "environment" in query_lower
            or "dev" in query_lower
        ):
            intent = "create_shell"
            # Extract language from query
            languages = [
                "python",
                "javascript",
                "typescript",
                "rust",
                "go",
                "java",
                "c",
                "cpp",
                "c++",
                "haskell",
                "ruby",
            ]
            found_language = None
            for lang in languages:
                if lang in query_lower:
                    found_language = lang
                    break
            if found_language:
                self._create_dev_shell(found_language)
            else:
                print("❌ Please specify a language for the development environment")
                print(
                    "Supported: python, javascript, typescript, rust, go, java, c, cpp, haskell, ruby"
                )
        elif ("garbage" in query_lower and "collect" in query_lower) or (
            "clean" in query_lower
            and ("up" in query_lower or "disk" in query_lower or "space" in query_lower)
        ):
            intent = "garbage_collect"
            self._handle_garbage_collect()
        elif (
            "diagnose" in query_lower
            or "troubleshoot" in query_lower
            or "fix" in query_lower
            or ("something" in query_lower and "wrong" in query_lower)
        ):
            intent = "diagnose"
            self._handle_diagnose(query_lower)
        elif "help" in query_lower or query_lower == "":
            intent = "help"
            self._show_help()
        else:
            # Try AI for complex queries
            if self.ollama:
                print(f"🤔 Let me think about: '{query}'")
                response = self.ollama.ask(query, context={"persona": self.persona})
                if response:
                    print(f"\n💡 {response}")
                else:
                    self._show_unknown_command_help(query)
                    success = False
            else:
                self._show_unknown_command_help(query)
                success = False

        # Update conversation state if we have it
        if self.conversation_state and intent:
            self.conversation_state.add_turn(
                query=query,
                response=response or f"Executed {intent} command",
                intent=intent,
                entities=entities,
                success=success,
            )

            # Suggest next action
            suggestion = self.conversation_state.suggest_next_action()
            if suggestion and success:
                print(f"\n💡 {suggestion}")

    def _show_unknown_command_help(self, query: str):
        """Show help for unknown commands"""
        print(f"🤔 I'm not sure how to handle: '{query}'")
        print("\nTry commands like:")
        print("  • install firefox")
        print("  • search text editor")
        print("  • list installed packages")
        print("  • update system")

        # Suggest enabling AI if not enabled
        if not self.ai_enabled and OLLAMA_AVAILABLE:
            print("\n💡 Tip: Use --ai flag for smarter understanding")

    def _handle_install(self, query: str):
        """Handle package installation"""
        # Debug logging
        if self.verbose_level >= 2:
            pass  # Debug removed for production

        # Extract package name - improved approach
        words = query.split()
        package = None

        # Method 1: Find word after "install"
        if "install" in words:
            idx = words.index("install")
            if idx + 1 < len(words):
                package = words[idx + 1]
                # Skip if package is a common word that's not a package name
                if package in {
                    "i",
                    "want",
                    "to",
                    "need",
                    "please",
                    "can",
                    "you",
                    "help",
                    "me",
                    "a",
                    "an",
                    "the",
                }:
                    package = None

        # Method 2: If no package found, try to find likely package names
        if not package:
            ignore_words = {
                "i",
                "want",
                "to",
                "need",
                "please",
                "can",
                "you",
                "help",
                "me",
                "install",
                "a",
                "an",
                "the",
            }
            packages = [w for w in words if w not in ignore_words]
            if packages:
                package = packages[0]

        # Method 3: Use intent recognition if available
        if not package and hasattr(self, "intent_pipeline"):
            from luminous_nix.core.intent_pipeline import IntentRecognitionPipeline

            pipeline = IntentRecognitionPipeline()
            result = pipeline.recognize(query)

            # Find package entities with highest confidence
            package_entities = [e for e in result.entities if e.type == "package"]
            if package_entities:
                # Sort by confidence and avoid "install" as package name
                package_entities = sorted(
                    package_entities, key=lambda x: x.confidence, reverse=True
                )
                for entity in package_entities:
                    if entity.value.lower() != "install":
                        package = entity.value
                        break

        # Execute installation if package found
        if package:
            # Use robust method if available
            if self.command_executor:
                self._install_package_robust(package)
            else:
                self._install_package(package)
        else:
            print("❌ Please specify what to install")
            print("Example: install firefox")

    def _handle_search(self, query: str):
        """Handle package search"""
        # Extract search term
        words = query.split()
        search_keywords = {"search", "find", "look", "for"}

        # Find the search term after keywords
        search_term = None
        for i, word in enumerate(words):
            if word in search_keywords and i + 1 < len(words):
                # Get everything after the search keyword
                search_term = " ".join(words[i + 1 :])
                break

        if not search_term:
            # Use all words except common ones
            ignore_words = {
                "i",
                "want",
                "to",
                "need",
                "please",
                "can",
                "you",
                "help",
                "me",
                "a",
                "an",
                "the",
            }
            search_words = [
                w for w in words if w not in ignore_words and w not in search_keywords
            ]
            if search_words:
                search_term = " ".join(search_words)

        if search_term:
            # Socratic mode: ask for clarification
            if self.ask_mode and search_term in ["editor", "browser", "terminal"]:
                self._ask_clarification_search(search_term)
            else:
                self._search_packages(search_term)
        else:
            print("❌ Please specify what to search for")
            print("Example: search text editor")

    def _ask_clarification_search(self, category: str):
        """Ask clarifying questions for better search results"""
        questions = {
            "editor": {
                "question": "What kind of editor are you looking for?",
                "options": {
                    "1": ("Simple text editing", "nano gedit"),
                    "2": ("Code development", "vim neovim emacs vscode"),
                    "3": ("Markdown writing", "typora obsidian marktext"),
                    "4": ("Terminal-based", "vim neovim nano micro"),
                },
            },
            "browser": {
                "question": "What type of browser would you prefer?",
                "options": {
                    "1": ("Fast and minimal", "qutebrowser surf"),
                    "2": ("Privacy-focused", "firefox tor-browser librewolf"),
                    "3": ("Feature-rich", "firefox chromium brave"),
                    "4": ("Developer-oriented", "chromium firefox-devedition"),
                },
            },
            "terminal": {
                "question": "What kind of terminal experience do you want?",
                "options": {
                    "1": ("Simple and fast", "alacritty foot"),
                    "2": ("Feature-rich", "kitty wezterm"),
                    "3": ("Traditional", "gnome-terminal konsole"),
                    "4": ("Minimalist", "st urxvt"),
                },
            },
        }

        if category in questions:
            q = questions[category]
            print(f"\n🤔 {q['question']}")
            for key, (desc, _) in q["options"].items():
                print(f"  {key}. {desc}")
            print("  5. Show all options")

            if not self.skip_confirmation:
                try:
                    choice = input("\nYour choice (1-5): ").strip()
                    if choice in q["options"]:
                        _, search_terms = q["options"][choice]
                        self._search_packages(search_terms)
                    else:
                        self._search_packages(category)
                except (KeyboardInterrupt, EOFError):
                    self._search_packages(category)
            else:
                self._search_packages(category)

    def _handle_remove(self, query: str):
        """Handle package removal"""
        words = query.split()
        remove_keywords = {"remove", "uninstall", "delete"}

        package = None
        for i, word in enumerate(words):
            if word in remove_keywords and i + 1 < len(words):
                package = words[i + 1]
                break

        if package:
            # Use robust method if available
            if self.command_executor:
                self._remove_package_robust(package)
            else:
                self._remove_package(package)
        else:
            print("❌ Please specify what to remove")
            print("Example: remove firefox")

    def _handle_update(self, query: str):
        """Handle system update"""
        print("🔄 Updating NixOS system...")

        if self.dry_run:
            print("[DRY RUN] Would run: sudo nixos-rebuild switch --upgrade")
            return

        if not self.skip_confirmation:
            response = input("This will update your entire system. Continue? (y/N): ")
            if response.lower() != "y":
                print("❌ Update cancelled")
                return

        try:
            # First update channels
            print("📦 Updating channels...")
            subprocess.run(["sudo", "nix-channel", "--update"], check=True)

            print("🔨 Rebuilding system...")
            subprocess.run(["sudo", "nixos-rebuild", "switch", "--upgrade"], check=True)
            print("✅ System updated successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Update failed: {e}")
            print("Try running: sudo nixos-rebuild switch --upgrade")

    def _handle_list_installed(self):
        """List installed packages"""
        
        # Use real backend if available
        if self.real_backend:
            from luminous_nix.core.intents import Intent, IntentType
            
            intent = Intent(
                type=IntentType.LIST_INSTALLED,
                entities={},
                confidence=1.0,
                raw_text="list"
            )
            
            response = self.real_backend.process(intent)
            print(response.text)
            return
        
        print("📦 Installed packages:\n")

        # Try user packages first
        user_packages = []
        try:
            result = subprocess.run(
                ["nix-env", "-q"],
                capture_output=True,
                text=True,
                check=False,  # Don't fail if no user packages
            )
            if result.returncode == 0 and result.stdout:
                user_packages = result.stdout.strip().split("\n")
        except Exception:
            pass

        # Show user packages
        if user_packages:
            print("👤 User packages:")
            for pkg in user_packages:
                print(f"  • {pkg}")
            print(f"  Total: {len(user_packages)} packages\n")
        else:
            print("👤 No user packages installed (nix-env -q returned empty)\n")

        # Show system packages location
        print("💻 System packages:")
        try:
            # List a sample of system packages
            result = subprocess.run(
                ["ls", "/run/current-system/sw/bin"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout:
                binaries = result.stdout.strip().split("\n")
                # Show first 10 as sample
                print(
                    f"  Found {len(binaries)} executables in system (showing first 10):"
                )
                for binary in binaries[:10]:
                    print(f"  • {binary}")
                if len(binaries) > 10:
                    print(f"  ... and {len(binaries) - 10} more")
            else:
                print("  Check: /run/current-system/sw/")
        except Exception as e:
            print(f"  Unable to list system packages: {e}")

        print(
            "\n💡 Tip: Use 'nix-env -q' for user packages, check configuration.nix for system packages"
        )

    def _handle_rollback(self):
        """Rollback to previous generation"""
        print("⏪ Rolling back to previous generation...")

        if self.dry_run:
            print("[DRY RUN] Would run: sudo nixos-rebuild switch --rollback")
            return

        if not self.skip_confirmation:
            response = input("This will rollback your system. Continue? (y/N): ")
            if response.lower() != "y":
                print("❌ Rollback cancelled")
                return

        try:
            subprocess.run(
                ["sudo", "nixos-rebuild", "switch", "--rollback"], check=True
            )
            print("✅ Rolled back successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Rollback failed: {e}")

    def _install_package_robust(self, package: str):
        """Install a package using robust architecture"""
        if self.command_executor:
            # Create install command
            cmd = self.command_executor.create_command(
                CommandType.INSTALL, [package], description=f"Install {package}"
            )

            # Execute with preview
            result = self.command_executor.execute(cmd, preview_first=True)

            # Handle result - Check for PREVIEWED status as success in dry-run mode
            if result.success() or (
                self.dry_run and result.status == CommandStatus.PREVIEWED
            ):
                # In dry-run mode, show what would be done
                if self.dry_run:
                    print(f"📋 Preview: Installing {package}")
                    if result.stdout:
                        # Format the output nicely
                        lines = result.stdout.strip().split("\n")
                        for line in lines:
                            if line.startswith("Would execute:") or line.startswith("Description:"):
                                print(f"  {line}")
                            else:
                                print(f"  {line}")
                    print(f"\n✅ [DRY RUN] Would install {package}")
                else:
                    print(f"✅ {package} installed successfully!")

                # Update conversation state
                if self.conversation_state:
                    self.conversation_state.add_turn(
                        query=f"install {package}",
                        response=f"{'Would install' if self.dry_run else 'Successfully installed'} {package}",
                        intent="install",
                        entities={"package": package},
                        success=True,
                    )

                    # Suggest next action
                    suggestion = self.conversation_state.suggest_next_action()
                    if suggestion:
                        print(f"\n💡 {suggestion}")
            else:
                # Use error recovery only for actual errors, not dry-run previews
                if self.error_recovery and result.stderr:
                    context = self.error_recovery.analyze_error(
                        result.stderr, cmd.to_string()
                    )

                    # Explain the error
                    print(self.error_recovery.explain_error(context))

                    # Attempt recovery
                    success, msg = self.error_recovery.attempt_recovery(
                        context, auto_fix=False, verbose=self.verbose_level > 0
                    )
                    print(msg)

                    # Update conversation state
                    if self.conversation_state:
                        self.conversation_state.add_turn(
                            query=f"install {package}",
                            response=result.stderr or "Installation failed",
                            intent="install",
                            entities={"package": package},
                            success=False,
                        )
                else:
                    print(f"❌ Failed to install {package}")
                    print(f"Error: {result.stderr}")
        else:
            # Fallback to original method
            self._install_package(package)

    def _install_package(self, package: str):
        """Install a specific package (fallback method)"""
        
        # Use real backend if available
        if self.real_backend:
            from luminous_nix.core.intents import Intent, IntentType
            
            intent = Intent(
                type=IntentType.INSTALL_PACKAGE,
                entities={'package': package},
                confidence=1.0,
                raw_text=f"install {package}"
            )
            
            response = self.real_backend.process(intent)
            if response.success:
                print(f"✅ {response.text}")
            else:
                print(f"❌ {response.text}")
            return
        
        # Original fallback implementation
        print(f"📦 Installing {package}...")

        if self.dry_run:
            print(f"[DRY RUN] Would run: nix profile install nixpkgs#{package}")
            return

        if not self.skip_confirmation:
            response = input(f"Install {package}? (y/N): ")
            if response.lower() != "y":
                print("❌ Installation cancelled")
                return

        try:
            # Check for profile compatibility first
            profile_check = subprocess.run(
                ["nix", "profile", "list"], capture_output=True, text=True
            )

            # If profile list fails with incompatibility error, handle it
            if (
                profile_check.returncode != 0
                and "incompatible with 'nix-env'" in profile_check.stderr
            ):
                # Try automatic migration
                from luminous_nix.cli.profile_migration import auto_migrate_profile

                print(
                    "\n🔄 Detected profile incompatibility - starting automatic migration..."
                )

                # Run migration (non-interactive if skip_confirmation is set)
                success = auto_migrate_profile(interactive=not self.skip_confirmation)

                if not success:
                    print("\n❌ Profile migration failed")
                    print(
                        "Please resolve the profile issue manually before installing packages"
                    )
                    return

                print("\n✅ Profile migrated! Continuing with installation...")
                # Fall through to install the package

            # If profile is compatible, proceed with installation
            subprocess.run(
                ["nix", "profile", "install", f"nixpkgs#{package}"],
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"✅ {package} installed successfully!")

        except subprocess.CalledProcessError as e:
            # Handle other errors
            if "already installed" in str(e.stderr):
                print(f"ℹ️  {package} is already installed")
            elif "Package.*not found" in str(e.stderr):
                print(f"❌ Package '{package}' not found")
                print("\nSearching for similar packages...")
                self._search_packages(package)
            else:
                print(f"❌ Failed to install {package}")
                print(f"Error: {e.stderr if e.stderr else 'Unknown error'}")
                print(f"\nTry searching first: ask-nix search {package}")

    def _remove_package_robust(self, package: str):
        """Remove a package using robust architecture"""
        if self.command_executor:
            # Create remove command
            cmd = self.command_executor.create_command(
                CommandType.REMOVE, [package], description=f"Remove {package}"
            )

            # Execute with preview
            result = self.command_executor.execute(cmd, preview_first=True)

            # Handle result - Check for PREVIEWED status as success in dry-run mode
            if result.success() or (
                self.dry_run and result.status == CommandStatus.PREVIEWED
            ):
                # In dry-run mode, show what would be done
                if self.dry_run:
                    print(f"📋 Preview: Removing {package}")
                    if result.stdout:
                        # Format the output nicely
                        lines = result.stdout.strip().split("\n")
                        for line in lines:
                            if line.startswith("Would execute:") or line.startswith("Description:"):
                                print(f"  {line}")
                            else:
                                print(f"  {line}")
                    print(f"\n✅ [DRY RUN] Would remove {package}")
                else:
                    print(f"✅ {package} removed successfully!")

                # Update conversation state
                if self.conversation_state:
                    self.conversation_state.add_turn(
                        query=f"remove {package}",
                        response=f"{'Would remove' if self.dry_run else 'Successfully removed'} {package}",
                        intent="remove",
                        entities={"package": package},
                        success=True,
                    )
            else:
                # Use error recovery only for actual errors, not dry-run previews
                if self.error_recovery and result.stderr:
                    context = self.error_recovery.analyze_error(
                        result.stderr, cmd.to_string()
                    )

                    # Explain the error
                    print(self.error_recovery.explain_error(context))

                    # Attempt recovery
                    success, msg = self.error_recovery.attempt_recovery(
                        context, auto_fix=False, verbose=self.verbose_level > 0
                    )
                    print(msg)

                    # Update conversation state
                    if self.conversation_state:
                        self.conversation_state.add_turn(
                            query=f"remove {package}",
                            response=result.stderr or "Removal failed",
                            intent="remove",
                            entities={"package": package},
                            success=False,
                        )
                else:
                    print(f"❌ Failed to remove {package}")
                    print(f"Error: {result.stderr}")
        else:
            # Fallback to original method
            self._remove_package(package)

    def _remove_package(self, package: str):
        """Remove a specific package (fallback method)"""
        print(f"🗑️ Removing {package}...")

        if self.dry_run:
            print(f"[DRY RUN] Would run: nix profile remove {package}")
            return

        if not self.skip_confirmation:
            response = input(f"Remove {package}? (y/N): ")
            if response.lower() != "y":
                print("❌ Removal cancelled")
                return

        try:
            # First, list profiles to find the package number
            result = subprocess.run(
                ["nix", "profile", "list"], capture_output=True, text=True, check=True
            )

            # Find the package in the profile list
            package_num = None
            for line in result.stdout.splitlines():
                if package in line:
                    # Extract the profile number (first field)
                    package_num = line.split()[0]
                    break

            if package_num:
                # Remove by profile number
                subprocess.run(["nix", "profile", "remove", package_num], check=True)
                print(f"✅ {package} removed successfully!")
            else:
                print(f"❌ Package {package} not found in profile")
                print("Run 'nix profile list' to see installed packages")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to remove {package}: {e}")

    def _search_packages(self, term: str):
        """Search for packages"""
        
        # Use real backend if available
        if self.real_backend:
            from luminous_nix.core.intents import Intent, IntentType
            
            intent = Intent(
                type=IntentType.SEARCH_PACKAGE,
                entities={'package': term},
                confidence=1.0,
                raw_text=f"search {term}"
            )
            
            response = self.real_backend.process(intent)
            print(response.text)
            return

        # Try cache first if available
        if self.search_cache:
            try:
                results = self.search_cache.search_with_cache(term, timeout=5)
                if results:
                    print(f"\n📦 Found {len(results)} packages matching '{term}':\n")
                    for pkg in results[:10]:
                        name = pkg.get("name", "unknown")
                        desc = pkg.get("description", "")[:60]
                        if desc and len(pkg.get("description", "")) > 60:
                            desc += "..."
                        print(f"  • {name}: {desc}")
                    if len(results) > 10:
                        print(f"  ... and {len(results) - 10} more")
                    return
                print(f"No packages found matching '{term}'")
                return
            except Exception as e:
                if self.verbose_level > 0:
                    print(f"Cache search failed: {e}, falling back to direct search")

        # Fallback to direct search
        print(f"🔍 Searching for '{term}'...")

        try:
            # Use nix search with cache for speed
            result = subprocess.run(
                ["nix", "search", "nixpkgs", term, "--use-cache"],
                capture_output=True,
                text=True,
                timeout=10,  # Reduced timeout since we're using cache
            )

            if result.returncode == 0 and result.stdout:
                print(f"\n📦 Found packages matching '{term}':\n")
                # Parse the search results (simplified)
                lines = result.stdout.strip().split("\n")
                count = 0
                for line in lines:
                    if line.startswith("* "):
                        count += 1
                        # Extract package name
                        parts = line.split("(")
                        if parts:
                            pkg_info = parts[0].replace("* ", "").strip()
                            print(f"  • {pkg_info}")

                if count == 0:
                    # Fallback to showing raw output
                    print(result.stdout)
                else:
                    print(f"\nFound {count} packages")
            else:
                # Fallback to nix-env search
                result = subprocess.run(
                    ["nix-env", "-qaP", f".*{term}.*"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.stdout:
                    lines = result.stdout.strip().split("\n")[:10]  # Show first 10
                    print(f"\n📦 Found packages matching '{term}':\n")
                    for line in lines:
                        parts = line.split()
                        if len(parts) >= 2:
                            print(f"  • {parts[0]} ({parts[1]})")

                    if len(result.stdout.strip().split("\n")) > 10:
                        print(
                            f"  ... and {len(result.stdout.strip().split('\n')) - 10} more"
                        )
                else:
                    print(f"No packages found matching '{term}'")

        except subprocess.TimeoutExpired:
            print("❌ Search timed out. Try a more specific term.")
        except Exception as e:
            print(f"❌ Search failed: {e}")

    def _show_help(self):
        """Show help message"""
        if self.personality == "friendly":
            print("\n💡 Here's what I can help you with:")
        else:
            print("\nAvailable commands:")

        print(
            """
  • install <package>    - Install a package
  • search <term>        - Search for packages  
  • remove <package>     - Remove a package
  • list installed       - Show installed packages
  • update system        - Update NixOS
  • rollback             - Go back to previous generation
  • garbage collect      - Free up disk space
  • create shell         - Create development environment
  • diagnose             - Troubleshoot problems
  • help                 - Show this help

Examples:
  ask-nix "install firefox"
  ask-nix "search markdown editor"
  ask-nix "what's installed?"
  ask-nix "update my system"
  ask-nix "clean up disk space"
  ask-nix "create python development shell"
"""
        )

        # Show plugin commands if available
        if self.plugin_manager:
            plugin_commands = self.plugin_manager.get_all_commands()
            if plugin_commands:
                print("\n📦 Plugin Commands:")
                for name, cmd in plugin_commands.items():
                    print(f"  • {name} - {cmd.description}")

    def _handle_garbage_collect(self):
        """Handle garbage collection"""
        print("🧹 Cleaning up Nix store...")

        if self.dry_run:
            print("[DRY RUN] Would run: nix-collect-garbage -d")
            return

        if not self.skip_confirmation:
            response = input(
                "This will delete old packages and generations. Continue? (y/N): "
            )
            if response.lower() != "y":
                print("❌ Cleanup cancelled")
                return

        try:
            # Run garbage collection
            result = subprocess.run(
                ["nix-collect-garbage", "-d"], capture_output=True, text=True
            )

            if result.returncode == 0:
                print("✅ Cleanup complete!")
                # Try to extract how much was freed
                for line in result.stdout.split("\n"):
                    if "freed" in line.lower():
                        print(f"💾 {line}")
            else:
                print(f"❌ Cleanup failed: {result.stderr}")
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")

    def _create_dev_shell(self, language: str):
        """Create a development shell for a language"""
        print(f"🛠️ Creating {language} development environment...")

        # Map common language names to nix packages
        language_map = {
            "python": "python3 python3Packages.pip python3Packages.virtualenv",
            "javascript": "nodejs nodePackages.npm",
            "typescript": "nodejs nodePackages.npm nodePackages.typescript",
            "rust": "rustc cargo",
            "go": "go",
            "java": "jdk",
            "c": "gcc gnumake",
            "cpp": "gcc gnumake",
            "c++": "gcc gnumake",
            "haskell": "ghc cabal-install",
            "ruby": "ruby bundler",
        }

        packages = language_map.get(language.lower())
        if not packages:
            print(f"❓ I don't know how to create a {language} environment")
            print("Supported: " + ", ".join(language_map.keys()))
            return

        print(f"📦 Packages: {packages}")

        if self.dry_run:
            print(f"[DRY RUN] Would run: nix-shell -p {packages}")
            return

        try:
            # Create and enter shell
            subprocess.run(
                ["nix-shell", "-p"] + packages.split(),
                check=False,  # Don't fail if user exits
            )
        except Exception as e:
            print(f"❌ Failed to create shell: {e}")

    def _handle_diagnose(self, query: str):
        """Handle diagnostic/troubleshooting requests"""
        print("🔍 Diagnosing system...")

        # Run some basic checks
        checks = []

        # Check disk space
        try:
            result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "%" in line and "/" in line:
                        usage = int(line.split()[-2].rstrip("%"))
                        if usage > 90:
                            checks.append(("❌", f"Disk usage critical: {usage}%"))
                        elif usage > 80:
                            checks.append(("⚠️", f"Disk usage high: {usage}%"))
                        else:
                            checks.append(("✅", f"Disk usage OK: {usage}%"))
        except:
            pass

        # Check nixos-rebuild status
        try:
            result = subprocess.run(
                ["systemctl", "status", "nixos-rebuild.service"],
                capture_output=True,
                text=True,
            )
            if "active (running)" in result.stdout:
                checks.append(("🔄", "NixOS rebuild in progress"))
            elif "failed" in result.stdout:
                checks.append(("❌", "Last NixOS rebuild failed"))
            else:
                checks.append(("✅", "NixOS rebuild status OK"))
        except:
            pass

        # Check for broken packages
        try:
            result = subprocess.run(
                ["nix-store", "--verify", "--check-contents"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if "error" in result.stderr.lower():
                checks.append(("❌", "Some packages may be corrupted"))
            else:
                checks.append(("✅", "Package store integrity OK"))
        except:
            pass

        # Display results
        print("\n📊 System Status:")
        for icon, message in checks:
            print(f"  {icon} {message}")

        # Offer suggestions based on problems found
        problems = [msg for icon, msg in checks if icon in ["❌", "⚠️"]]
        if problems:
            print("\n💡 Suggestions:")
            if any("Disk usage" in p for p in problems):
                print("  • Run 'garbage collect' to free space")
            if any("rebuild failed" in p for p in problems):
                print("  • Check system logs: journalctl -xe")
            if any("corrupted" in p for p in problems):
                print("  • Run 'nix-store --repair-path' on broken paths")


# For backward compatibility
if __name__ == "__main__":
    assistant = UnifiedNixAssistant()
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        assistant.answer(query)
    else:
        print("Please provide a command")
        assistant._show_help()
