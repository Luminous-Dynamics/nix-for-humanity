"""
Semantic Natural Language Understanding for package discovery
Maps natural language queries to actual package names and categories
"""

import re
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Set
from difflib import SequenceMatcher
import json
from pathlib import Path


@dataclass
class SemanticIntent:
    """Represents the semantic understanding of a user query"""
    query: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    action: str = "search"  # search, install, remove, etc.
    modifiers: List[str] = None  # GUI, CLI, lightweight, etc.
    confidence: float = 0.0
    suggested_packages: List[str] = None
    
    def __post_init__(self):
        if self.modifiers is None:
            self.modifiers = []
        if self.suggested_packages is None:
            self.suggested_packages = []


class SemanticUnderstanding:
    """
    Advanced NLU for understanding what users really want
    Maps natural descriptions to actual package names
    """
    
    def __init__(self):
        """Initialize with semantic knowledge base"""
        self.category_map = self._build_category_map()
        self.synonym_map = self._build_synonym_map()
        self.action_patterns = self._build_action_patterns()
        self.modifier_patterns = self._build_modifier_patterns()
        
        # Cache for learned mappings
        self.learned_mappings = {}
        self.cache_file = Path.home() / ".cache" / "luminous-nix" / "semantic_mappings.json"
        self._load_learned_mappings()
        
        # Performance tracking
        self.stats = {
            "queries_processed": 0,
            "category_matches": 0,
            "synonym_matches": 0,
            "learned_matches": 0,
            "fuzzy_matches": 0
        }
    
    def _build_category_map(self) -> Dict[str, Dict]:
        """Build comprehensive category mappings"""
        return {
            "editor": {
                "keywords": ["edit", "code", "text", "write", "programming", "ide", "develop"],
                "subcategories": {
                    "terminal": ["vim", "neovim", "emacs", "nano", "micro", "helix"],
                    "gui": ["vscode", "sublime-text", "atom", "kate", "gedit"],
                    "ide": ["idea-ultimate", "eclipse", "netbeans", "android-studio"]
                },
                "common_packages": ["vim", "neovim", "vscode", "emacs", "nano"]
            },
            
            "browser": {
                "keywords": ["browse", "web", "internet", "surf", "online", "website"],
                "subcategories": {
                    "mainstream": ["firefox", "chromium", "google-chrome", "brave"],
                    "privacy": ["tor-browser", "librewolf", "ungoogled-chromium"],
                    "terminal": ["lynx", "w3m", "elinks"]
                },
                "common_packages": ["firefox", "chromium", "brave", "google-chrome"]
            },
            
            "terminal": {
                "keywords": ["terminal", "console", "shell", "command", "cli", "tty"],
                "subcategories": {
                    "emulator": ["alacritty", "kitty", "wezterm", "konsole", "gnome-terminal"],
                    "multiplexer": ["tmux", "screen", "zellij"],
                    "shell": ["zsh", "fish", "bash", "nushell"]
                },
                "common_packages": ["alacritty", "kitty", "tmux", "zsh"]
            },
            
            "development": {
                "keywords": ["develop", "program", "code", "compile", "build", "debug"],
                "subcategories": {
                    "python": ["python3", "python311", "python312", "poetry", "pipenv"],
                    "javascript": ["nodejs", "npm", "yarn", "deno", "bun"],
                    "rust": ["rustc", "cargo", "rustup"],
                    "c": ["gcc", "clang", "cmake", "make"],
                    "java": ["jdk", "openjdk", "maven", "gradle"]
                },
                "common_packages": ["git", "gcc", "python3", "nodejs", "rustc"]
            },
            
            "multimedia": {
                "keywords": ["video", "audio", "music", "media", "play", "watch", "listen"],
                "subcategories": {
                    "video": ["vlc", "mpv", "mplayer", "obs-studio", "kdenlive"],
                    "audio": ["audacity", "spotify", "rhythmbox", "cmus"],
                    "image": ["gimp", "inkscape", "krita", "imagemagick"]
                },
                "common_packages": ["vlc", "mpv", "spotify", "gimp", "audacity"]
            },
            
            "productivity": {
                "keywords": ["office", "document", "spreadsheet", "presentation", "pdf"],
                "subcategories": {
                    "office": ["libreoffice", "onlyoffice", "wps-office"],
                    "pdf": ["okular", "evince", "zathura", "mupdf"],
                    "notes": ["obsidian", "joplin", "notion", "logseq"]
                },
                "common_packages": ["libreoffice", "okular", "obsidian", "thunderbird"]
            },
            
            "communication": {
                "keywords": ["chat", "message", "email", "call", "video", "social"],
                "subcategories": {
                    "chat": ["discord", "slack", "telegram-desktop", "signal-desktop"],
                    "email": ["thunderbird", "evolution", "mutt", "aerc"],
                    "video": ["zoom", "teams", "skype", "jitsi-meet"]
                },
                "common_packages": ["discord", "slack", "thunderbird", "telegram-desktop"]
            },
            
            "system": {
                "keywords": ["system", "monitor", "manage", "control", "admin", "configure"],
                "subcategories": {
                    "monitor": ["htop", "btop", "glances", "nethogs"],
                    "file": ["ranger", "nnn", "mc", "thunar", "dolphin"],
                    "backup": ["rsync", "borg", "restic", "timeshift"]
                },
                "common_packages": ["htop", "neofetch", "rsync", "tree", "ncdu"]
            },
            
            "security": {
                "keywords": ["security", "vpn", "encrypt", "password", "firewall", "antivirus"],
                "subcategories": {
                    "vpn": ["openvpn", "wireguard", "mullvad-vpn", "nordvpn"],
                    "password": ["keepassxc", "bitwarden", "pass", "gopass"],
                    "encryption": ["gnupg", "veracrypt", "cryptsetup"]
                },
                "common_packages": ["keepassxc", "bitwarden", "openvpn", "gnupg"]
            },
            
            "gaming": {
                "keywords": ["game", "play", "steam", "gaming", "emulator"],
                "subcategories": {
                    "platform": ["steam", "lutris", "heroic", "bottles"],
                    "emulator": ["retroarch", "dolphin-emu", "pcsx2", "yuzu"],
                    "tools": ["mangohud", "gamemode", "antimicrox"]
                },
                "common_packages": ["steam", "lutris", "discord", "obs-studio"]
            }
        }
    
    def _build_synonym_map(self) -> Dict[str, List[str]]:
        """Build synonym mappings for common terms"""
        return {
            # Actions
            "get": ["install", "add", "setup"],
            "remove": ["uninstall", "delete", "purge"],
            "find": ["search", "look for", "locate"],
            "update": ["upgrade", "refresh"],
            
            # Software types
            "editor": ["ide", "text editor", "code editor"],
            "browser": ["web browser", "internet browser"],
            "terminal": ["console", "command line", "shell"],
            "music player": ["audio player", "media player"],
            "video player": ["movie player", "media player"],
            
            # Descriptors
            "fast": ["quick", "speedy", "lightweight"],
            "simple": ["easy", "basic", "minimal"],
            "powerful": ["advanced", "professional", "full-featured"],
            "free": ["open source", "libre", "foss"],
            
            # Common software
            "photoshop": ["image editor", "photo editor"],
            "word": ["document editor", "word processor"],
            "excel": ["spreadsheet", "calc"],
            "powerpoint": ["presentation", "slides"]
        }
    
    def _build_action_patterns(self) -> List[Tuple[re.Pattern, str]]:
        """Build patterns to detect user actions"""
        return [
            (re.compile(r'\b(install|add|get|setup|put)\b', re.I), "install"),
            (re.compile(r'\b(remove|uninstall|delete|purge)\b', re.I), "remove"),
            (re.compile(r'\b(search|find|look|what|which|list)\b', re.I), "search"),
            (re.compile(r'\b(update|upgrade|refresh)\b', re.I), "update"),
            (re.compile(r'\b(info|information|about|describe)\b', re.I), "info"),
            (re.compile(r'\b(configure|config|setup|settings)\b', re.I), "configure")
        ]
    
    def _build_modifier_patterns(self) -> List[Tuple[re.Pattern, str]]:
        """Build patterns to detect modifiers"""
        return [
            (re.compile(r'\b(gui|graphical|visual|desktop)\b', re.I), "gui"),
            (re.compile(r'\b(cli|terminal|console|command.?line)\b', re.I), "cli"),
            (re.compile(r'\b(light|lightweight|minimal|simple|fast)\b', re.I), "lightweight"),
            (re.compile(r'\b(professional|advanced|powerful|full)\b', re.I), "advanced"),
            (re.compile(r'\b(free|open.?source|foss|libre)\b', re.I), "opensource"),
            (re.compile(r'\b(privacy|private|secure|encrypted)\b', re.I), "privacy")
        ]
    
    def understand(self, query: str) -> SemanticIntent:
        """
        Understand the semantic intent of a natural language query
        
        Examples:
        - "I need something to edit code" -> vim, neovim, vscode
        - "install a web browser" -> firefox, chromium, brave
        - "music player for terminal" -> cmus, ncmpcpp, moc
        """
        start_time = time.time()
        self.stats["queries_processed"] += 1
        
        # Normalize query
        query_lower = query.lower().strip()
        
        # Create intent object
        intent = SemanticIntent(query=query)
        
        # Extract action
        intent.action = self._extract_action(query_lower)
        
        # Extract modifiers
        intent.modifiers = self._extract_modifiers(query_lower)
        
        # Check learned mappings first
        if query_lower in self.learned_mappings:
            self.stats["learned_matches"] += 1
            learned = self.learned_mappings[query_lower]
            intent.category = learned.get("category")
            intent.suggested_packages = learned.get("packages", [])
            intent.confidence = 0.95
            return intent
        
        # Find category match
        category_match = self._find_category(query_lower)
        if category_match:
            self.stats["category_matches"] += 1
            intent.category = category_match["category"]
            intent.subcategory = category_match.get("subcategory")
            intent.suggested_packages = self._get_packages_for_category(
                category_match, intent.modifiers
            )
            intent.confidence = category_match["confidence"]
            return intent
        
        # Check synonyms
        synonym_match = self._check_synonyms(query_lower)
        if synonym_match:
            self.stats["synonym_matches"] += 1
            # Recursively understand the synonym
            return self.understand(synonym_match)
        
        # Fuzzy matching as last resort
        fuzzy_matches = self._fuzzy_match_packages(query_lower)
        if fuzzy_matches:
            self.stats["fuzzy_matches"] += 1
            intent.suggested_packages = fuzzy_matches[:5]
            intent.confidence = 0.6
            return intent
        
        # No match found
        intent.confidence = 0.0
        return intent
    
    def _extract_action(self, query: str) -> str:
        """Extract the intended action from query"""
        for pattern, action in self.action_patterns:
            if pattern.search(query):
                return action
        return "search"  # Default action
    
    def _extract_modifiers(self, query: str) -> List[str]:
        """Extract modifiers from query"""
        modifiers = []
        for pattern, modifier in self.modifier_patterns:
            if pattern.search(query):
                modifiers.append(modifier)
        return modifiers
    
    def _find_category(self, query: str) -> Optional[Dict]:
        """Find the best matching category for the query"""
        best_match = None
        best_score = 0
        
        for category_name, category_data in self.category_map.items():
            # Check keywords
            score = 0
            for keyword in category_data["keywords"]:
                if keyword in query:
                    score += len(keyword) / len(query)  # Longer matches score higher
            
            # Check subcategories
            subcategory_match = None
            for subcat_name, packages in category_data.get("subcategories", {}).items():
                if subcat_name in query:
                    score += 0.5
                    subcategory_match = subcat_name
                    break
            
            if score > best_score:
                best_score = score
                best_match = {
                    "category": category_name,
                    "subcategory": subcategory_match,
                    "confidence": min(score, 1.0),
                    "data": category_data
                }
        
        return best_match if best_score > 0.1 else None
    
    def _get_packages_for_category(
        self, category_match: Dict, modifiers: List[str]
    ) -> List[str]:
        """Get relevant packages for a category match"""
        category_data = category_match["data"]
        packages = []
        
        # If subcategory matched, prioritize those packages
        if category_match.get("subcategory"):
            subcat_packages = category_data["subcategories"].get(
                category_match["subcategory"], []
            )
            packages.extend(subcat_packages)
        
        # Apply modifiers to filter packages
        if modifiers:
            filtered = self._apply_modifiers(category_data, modifiers)
            packages.extend(filtered)
        
        # Add common packages if not enough results
        if len(packages) < 3:
            packages.extend(category_data.get("common_packages", []))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_packages = []
        for pkg in packages:
            if pkg not in seen:
                seen.add(pkg)
                unique_packages.append(pkg)
        
        return unique_packages[:10]  # Return top 10
    
    def _apply_modifiers(
        self, category_data: Dict, modifiers: List[str]
    ) -> List[str]:
        """Apply modifiers to filter packages"""
        filtered = []
        
        for modifier in modifiers:
            if modifier == "gui" and "gui" in category_data.get("subcategories", {}):
                filtered.extend(category_data["subcategories"]["gui"])
            elif modifier == "cli" and "terminal" in category_data.get("subcategories", {}):
                filtered.extend(category_data["subcategories"]["terminal"])
            elif modifier == "lightweight":
                # Prefer minimal packages
                for subcat, pkgs in category_data.get("subcategories", {}).items():
                    if "terminal" in subcat or "minimal" in subcat:
                        filtered.extend(pkgs)
            elif modifier == "privacy":
                # Prefer privacy-focused packages
                for subcat, pkgs in category_data.get("subcategories", {}).items():
                    if "privacy" in subcat:
                        filtered.extend(pkgs)
        
        return filtered
    
    def _check_synonyms(self, query: str) -> Optional[str]:
        """Check if query contains synonyms and return expanded version"""
        for term, synonyms in self.synonym_map.items():
            for synonym in synonyms:
                if synonym in query:
                    # Replace synonym with standard term
                    return query.replace(synonym, term)
        return None
    
    def _fuzzy_match_packages(self, query: str) -> List[str]:
        """Fuzzy match against known package names"""
        # Get all known packages from categories
        all_packages = set()
        for category_data in self.category_map.values():
            all_packages.update(category_data.get("common_packages", []))
            for packages in category_data.get("subcategories", {}).values():
                all_packages.update(packages)
        
        # Calculate similarity scores
        matches = []
        for package in all_packages:
            similarity = SequenceMatcher(None, query, package.lower()).ratio()
            if similarity > 0.6:  # 60% similarity threshold
                matches.append((package, similarity))
        
        # Sort by similarity
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return [pkg for pkg, _ in matches]
    
    def learn_mapping(
        self, query: str, selected_package: str, category: Optional[str] = None
    ):
        """Learn from user selections to improve future understanding"""
        query_lower = query.lower().strip()
        
        if query_lower not in self.learned_mappings:
            self.learned_mappings[query_lower] = {
                "packages": [],
                "category": category,
                "count": 0
            }
        
        mapping = self.learned_mappings[query_lower]
        
        # Update packages list
        if selected_package not in mapping["packages"]:
            mapping["packages"].insert(0, selected_package)
            # Keep only top 5 packages
            mapping["packages"] = mapping["packages"][:5]
        
        # Update category if provided
        if category:
            mapping["category"] = category
        
        # Increment usage count
        mapping["count"] += 1
        
        # Save learned mappings
        self._save_learned_mappings()
    
    def _load_learned_mappings(self):
        """Load learned mappings from disk"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    self.learned_mappings = json.load(f)
            except:
                self.learned_mappings = {}
    
    def _save_learned_mappings(self):
        """Save learned mappings to disk"""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w") as f:
                json.dump(self.learned_mappings, f, indent=2)
        except:
            pass  # Silent fail
    
    def get_stats(self) -> Dict:
        """Get usage statistics"""
        total = self.stats["queries_processed"]
        if total == 0:
            return self.stats
        
        return {
            **self.stats,
            "category_rate": (self.stats["category_matches"] / total * 100),
            "synonym_rate": (self.stats["synonym_matches"] / total * 100),
            "learned_rate": (self.stats["learned_matches"] / total * 100),
            "fuzzy_rate": (self.stats["fuzzy_matches"] / total * 100)
        }
    
    def suggest_query_improvements(self, query: str) -> List[str]:
        """Suggest better ways to phrase the query"""
        suggestions = []
        query_lower = query.lower()
        
        # Check if query is too vague
        if len(query_lower.split()) < 2:
            suggestions.append(f"Try being more specific: '{query} for terminal' or '{query} with GUI'")
        
        # Suggest category keywords
        matched_categories = []
        for cat_name, cat_data in self.category_map.items():
            for keyword in cat_data["keywords"]:
                if keyword in query_lower:
                    matched_categories.append(cat_name)
                    break
        
        if not matched_categories:
            suggestions.append("Try using category terms like: editor, browser, terminal, development")
        
        # Suggest modifiers
        has_modifiers = any(
            pattern.search(query_lower) for pattern, _ in self.modifier_patterns
        )
        if not has_modifiers:
            suggestions.append("Add modifiers like: lightweight, GUI, terminal, advanced")
        
        return suggestions[:3]  # Return top 3 suggestions


class SmartPackageSearch:
    """
    High-level interface combining semantic understanding with cache
    """
    
    def __init__(self, cache=None):
        """Initialize with optional cache backend"""
        self.semantic = SemanticUnderstanding()
        self.cache = cache
    
    def search(self, query: str) -> Tuple[List[Dict], float, str]:
        """
        Smart search with semantic understanding
        
        Returns: (results, elapsed_ms, method)
        """
        start_time = time.time()
        
        # Get semantic understanding
        intent = self.semantic.understand(query)
        
        # If high confidence, use suggested packages
        if intent.confidence > 0.8 and intent.suggested_packages:
            results = []
            for pkg_name in intent.suggested_packages:
                # Try to get from cache if available
                if self.cache:
                    pkg_info = self._get_package_info(pkg_name)
                    if pkg_info:
                        results.append(pkg_info)
                else:
                    # Return basic info
                    results.append({
                        "name": pkg_name,
                        "version": "latest",
                        "description": f"Package suggested for: {intent.category}"
                    })
            
            elapsed_ms = (time.time() - start_time) * 1000
            return (results, elapsed_ms, "semantic")
        
        # Fall back to regular search with original query
        if self.cache:
            return self.cache.search_hybrid(query)
        else:
            # Return empty if no cache
            elapsed_ms = (time.time() - start_time) * 1000
            return ([], elapsed_ms, "no-cache")
    
    def _get_package_info(self, package_name: str) -> Optional[Dict]:
        """Get package info from cache or return basic info"""
        if hasattr(self.cache, 'l1_cache') and package_name in self.cache.l1_cache:
            return self.cache.l1_cache[package_name]
        
        # Return basic info
        return {
            "name": package_name,
            "version": "latest",
            "description": "Recommended package"
        }
    
    def learn_from_selection(self, query: str, selected_package: str):
        """Learn from user's package selection"""
        # Determine category from selection
        category = None
        for cat_name, cat_data in self.semantic.category_map.items():
            all_packages = cat_data.get("common_packages", [])
            for packages in cat_data.get("subcategories", {}).values():
                all_packages.extend(packages)
            
            if selected_package in all_packages:
                category = cat_name
                break
        
        # Learn the mapping
        self.semantic.learn_mapping(query, selected_package, category)
    
    def get_suggestions(self, query: str) -> List[str]:
        """Get query improvement suggestions"""
        return self.semantic.suggest_query_improvements(query)