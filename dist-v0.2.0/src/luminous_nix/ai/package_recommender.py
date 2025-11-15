"""
Package Recommendation System for NixOS
Uses LLM to suggest alternatives, similar packages, and complementary tools
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PackageRecommendation:
    """Represents a package recommendation"""

    name: str
    description: str
    reason: str
    similarity_score: float
    category: str
    use_case: str


@dataclass
class RecommendationSet:
    """Set of recommendations for a query"""

    alternatives: List[PackageRecommendation]  # Direct alternatives
    similar: List[PackageRecommendation]  # Similar functionality
    complementary: List[PackageRecommendation]  # Works well with
    upgrade_path: List[PackageRecommendation]  # Better/modern options
    explanation: str


class PackageRecommender:
    """
    Intelligent package recommendation system for NixOS
    Suggests alternatives, similar tools, and complementary packages
    """

    def __init__(self):
        # Package categories and relationships
        self.package_graph = {
            # Text Editors
            "vim": {
                "category": "text-editor",
                "alternatives": ["neovim", "emacs", "nano", "helix"],
                "complementary": ["tmux", "fzf", "ripgrep", "ctags"],
                "upgrade": ["neovim"],
                "tags": ["terminal", "modal", "programming"],
            },
            "neovim": {
                "category": "text-editor",
                "alternatives": ["vim", "emacs", "helix", "kakoune"],
                "complementary": [
                    "tmux",
                    "fzf",
                    "ripgrep",
                    "tree-sitter",
                    "language-servers",
                ],
                "tags": ["terminal", "modal", "modern", "lua", "programming"],
            },
            "vscode": {
                "category": "text-editor",
                "alternatives": ["vscodium", "sublime", "atom", "intellij-idea"],
                "complementary": ["git", "docker", "nodejs"],
                "tags": ["gui", "electron", "microsoft", "extensions"],
            },
            "emacs": {
                "category": "text-editor",
                "alternatives": ["vim", "neovim", "spacemacs"],
                "complementary": ["org-mode", "magit", "projectile"],
                "tags": ["lisp", "extensible", "gui", "terminal"],
            },
            # Web Browsers
            "firefox": {
                "category": "browser",
                "alternatives": ["chromium", "brave", "vivaldi", "librewolf"],
                "complementary": ["bitwarden", "ublock-origin", "thunderbird"],
                "tags": ["privacy", "open-source", "mozilla"],
            },
            "chromium": {
                "category": "browser",
                "alternatives": ["firefox", "brave", "ungoogled-chromium"],
                "complementary": ["bitwarden", "ublock-origin"],
                "tags": ["google", "chromium-based", "fast"],
            },
            "brave": {
                "category": "browser",
                "alternatives": ["firefox", "librewolf", "chromium"],
                "complementary": ["bitwarden"],
                "tags": ["privacy", "chromium-based", "crypto", "ad-blocking"],
            },
            # Terminal Emulators
            "alacritty": {
                "category": "terminal",
                "alternatives": ["kitty", "wezterm", "foot", "termite"],
                "complementary": ["tmux", "zsh", "starship"],
                "tags": ["gpu-accelerated", "rust", "fast", "minimal"],
            },
            "kitty": {
                "category": "terminal",
                "alternatives": ["alacritty", "wezterm", "foot"],
                "complementary": ["tmux", "fish", "starship"],
                "tags": ["gpu-accelerated", "features", "images", "tabs"],
            },
            # Shells
            "zsh": {
                "category": "shell",
                "alternatives": ["bash", "fish", "nushell", "elvish"],
                "complementary": ["oh-my-zsh", "starship", "fzf", "zoxide"],
                "tags": ["customizable", "plugins", "completion"],
            },
            "fish": {
                "category": "shell",
                "alternatives": ["zsh", "nushell", "elvish"],
                "complementary": ["starship", "fisher", "fzf", "zoxide"],
                "tags": ["user-friendly", "autosuggestions", "modern"],
            },
            # Development Tools
            "git": {
                "category": "vcs",
                "alternatives": ["mercurial", "fossil"],
                "complementary": ["gh", "lazygit", "tig", "git-lfs", "pre-commit"],
                "tags": ["version-control", "distributed", "essential"],
            },
            "docker": {
                "category": "container",
                "alternatives": ["podman", "lxc", "systemd-nspawn"],
                "complementary": ["docker-compose", "lazydocker", "dive", "kubectl"],
                "tags": ["containers", "virtualization", "devops"],
            },
            "podman": {
                "category": "container",
                "alternatives": ["docker", "lxc"],
                "complementary": ["buildah", "skopeo", "podman-compose"],
                "tags": ["containers", "rootless", "daemonless", "redhat"],
            },
            # File Managers
            "ranger": {
                "category": "file-manager",
                "alternatives": ["lf", "nnn", "vifm", "midnight-commander"],
                "complementary": ["fzf", "ripgrep", "bat", "eza"],
                "tags": ["terminal", "vim-like", "python", "preview"],
            },
            "lf": {
                "category": "file-manager",
                "alternatives": ["ranger", "nnn", "vifm"],
                "complementary": ["fzf", "ripgrep", "bat", "eza"],
                "tags": ["terminal", "fast", "go", "minimal"],
            },
            # System Monitors
            "htop": {
                "category": "monitor",
                "alternatives": ["btop", "gtop", "bottom", "glances"],
                "complementary": ["iotop", "nethogs", "ncdu"],
                "upgrade": ["btop"],
                "tags": ["system", "processes", "terminal", "interactive"],
            },
            "btop": {
                "category": "monitor",
                "alternatives": ["htop", "bottom", "ytop"],
                "complementary": ["nvtop", "iotop", "nethogs"],
                "tags": ["system", "beautiful", "terminal", "modern"],
            },
            # Media Players
            "vlc": {
                "category": "media",
                "alternatives": ["mpv", "mplayer", "celluloid"],
                "complementary": ["youtube-dl", "ffmpeg", "handbrake"],
                "tags": ["video", "audio", "gui", "versatile"],
            },
            "mpv": {
                "category": "media",
                "alternatives": ["vlc", "mplayer", "celluloid"],
                "complementary": ["youtube-dl", "ffmpeg", "mpv-mpris"],
                "tags": ["video", "minimal", "scriptable", "fast"],
            },
            # Package Managers
            "flatpak": {
                "category": "package-manager",
                "alternatives": ["appimage", "snap"],
                "complementary": ["flatseal", "flatpak-builder"],
                "tags": ["sandboxed", "cross-distro", "gui-apps"],
            },
            # Productivity
            "obsidian": {
                "category": "notes",
                "alternatives": ["logseq", "notion", "joplin", "org-mode"],
                "complementary": ["syncthing", "pandoc"],
                "tags": ["markdown", "knowledge-base", "graph", "proprietary"],
            },
            "logseq": {
                "category": "notes",
                "alternatives": ["obsidian", "roam", "dendron", "org-mode"],
                "complementary": ["syncthing", "git"],
                "tags": ["markdown", "graph", "open-source", "outliner"],
            },
        }

        # Category-based recommendations
        self.category_suggestions = {
            "text-editor": ["Language servers", "Linters", "Formatters"],
            "browser": ["Password managers", "Ad blockers", "Privacy tools"],
            "terminal": ["Shell enhancements", "Multiplexers", "Prompt tools"],
            "shell": ["Prompt themes", "Plugin managers", "Completion tools"],
            "vcs": ["Merge tools", "Diff tools", "Hooks"],
            "container": ["Orchestration", "Registries", "Monitoring"],
            "file-manager": ["Search tools", "Preview tools", "Batch rename"],
            "monitor": ["Network monitors", "Disk analyzers", "Log viewers"],
            "media": ["Codecs", "Converters", "Downloaders"],
            "notes": ["Sync tools", "Converters", "Backup solutions"],
        }

    def recommend(
        self, package: str, context: Optional[Dict] = None
    ) -> RecommendationSet:
        """
        Generate recommendations for a package
        """
        package_lower = package.lower()

        # Check if we have data for this package
        if package_lower in self.package_graph:
            return self._recommend_known_package(package_lower, context)
        else:
            return self._recommend_unknown_package(package_lower, context)

    def _recommend_known_package(
        self, package: str, context: Optional[Dict]
    ) -> RecommendationSet:
        """Generate recommendations for a known package"""
        pkg_data = self.package_graph[package]

        # Get alternatives
        alternatives = []
        for alt in pkg_data.get("alternatives", []):
            if alt in self.package_graph:
                alt_data = self.package_graph[alt]
                reason = self._generate_comparison(package, alt)
                alternatives.append(
                    PackageRecommendation(
                        name=alt,
                        description=self._get_description(alt),
                        reason=reason,
                        similarity_score=self._calculate_similarity(package, alt),
                        category=alt_data.get("category", "unknown"),
                        use_case=self._determine_use_case(alt),
                    )
                )

        # Get similar packages (from same category)
        similar = []
        my_category = pkg_data.get("category")
        if my_category:
            for pkg, data in self.package_graph.items():
                if pkg != package and data.get("category") == my_category:
                    if pkg not in pkg_data.get("alternatives", []):
                        similar.append(
                            PackageRecommendation(
                                name=pkg,
                                description=self._get_description(pkg),
                                reason=f"Similar {my_category} tool",
                                similarity_score=0.6,
                                category=my_category,
                                use_case=self._determine_use_case(pkg),
                            )
                        )

        # Get complementary packages
        complementary = []
        for comp in pkg_data.get("complementary", []):
            complementary.append(
                PackageRecommendation(
                    name=comp,
                    description=self._get_description(comp),
                    reason=f"Works well with {package}",
                    similarity_score=0.0,  # Not similar, but complementary
                    category=self._guess_category(comp),
                    use_case=f"Enhances {package} functionality",
                )
            )

        # Get upgrade path if available
        upgrade_path = []
        for upgrade in pkg_data.get("upgrade", []):
            upgrade_path.append(
                PackageRecommendation(
                    name=upgrade,
                    description=self._get_description(upgrade),
                    reason=f"Modern replacement for {package}",
                    similarity_score=0.9,
                    category=my_category,
                    use_case=f"Better version of {package}",
                )
            )

        explanation = self._generate_explanation(
            package, alternatives, similar, complementary
        )

        return RecommendationSet(
            alternatives=sorted(
                alternatives, key=lambda x: x.similarity_score, reverse=True
            )[:5],
            similar=sorted(similar, key=lambda x: x.similarity_score, reverse=True)[:5],
            complementary=complementary[:5],
            upgrade_path=upgrade_path,
            explanation=explanation,
        )

    def _recommend_unknown_package(
        self, package: str, context: Optional[Dict]
    ) -> RecommendationSet:
        """Generate recommendations for an unknown package using fuzzy matching"""
        # Try to find similar package names
        similar_names = self._find_similar_names(package)

        if similar_names:
            # Recommend based on the most similar known package
            best_match = similar_names[0]
            recs = self._recommend_known_package(best_match, context)
            recs.explanation = f"Package '{package}' not found. Showing recommendations based on similar package '{best_match}'."
            return recs

        # Try to guess category from name
        category = self._guess_category_from_name(package)
        if category:
            return self._recommend_by_category(category, package)

        # Generic recommendations
        return RecommendationSet(
            alternatives=[],
            similar=[],
            complementary=[],
            upgrade_path=[],
            explanation=f"Package '{package}' is not in our database. Try searching with: nix search nixpkgs {package}",
        )

    def _find_similar_names(self, package: str) -> List[str]:
        """Find packages with similar names"""
        similar = []
        package_lower = package.lower()

        for known_pkg in self.package_graph:
            # Check if one contains the other
            if package_lower in known_pkg or known_pkg in package_lower:
                similar.append(known_pkg)
            # Check edit distance for short names
            elif (
                len(package) < 10 and self._edit_distance(package_lower, known_pkg) <= 2
            ):
                similar.append(known_pkg)

        return similar

    def _edit_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._edit_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def _calculate_similarity(self, pkg1: str, pkg2: str) -> float:
        """Calculate similarity score between two packages"""
        data1 = self.package_graph.get(pkg1, {})
        data2 = self.package_graph.get(pkg2, {})

        score = 0.0

        # Same category = high similarity
        if data1.get("category") == data2.get("category"):
            score += 0.5

        # Shared tags
        tags1 = set(data1.get("tags", []))
        tags2 = set(data2.get("tags", []))
        if tags1 and tags2:
            overlap = len(tags1 & tags2) / len(tags1 | tags2)
            score += overlap * 0.3

        # Listed as alternatives
        if pkg2 in data1.get("alternatives", []):
            score += 0.2

        return min(score, 1.0)

    def _generate_comparison(self, pkg1: str, pkg2: str) -> str:
        """Generate comparison text between two packages"""
        data1 = self.package_graph.get(pkg1, {})
        data2 = self.package_graph.get(pkg2, {})

        tags1 = set(data1.get("tags", []))
        tags2 = set(data2.get("tags", []))

        unique_to_2 = tags2 - tags1

        if unique_to_2:
            features = list(unique_to_2)[:2]
            return f"Alternative with {', '.join(features)}"
        else:
            return f"Similar alternative to {pkg1}"

    def _get_description(self, package: str) -> str:
        """Get package description"""
        descriptions = {
            "neovim": "Vim-fork focused on extensibility and usability",
            "vim": "Highly configurable text editor",
            "emacs": "Extensible, customizable text editor",
            "vscode": "Code editor with rich extension ecosystem",
            "firefox": "Privacy-focused web browser",
            "chromium": "Open-source web browser",
            "brave": "Privacy-focused browser with ad blocking",
            "alacritty": "GPU-accelerated terminal emulator",
            "kitty": "Feature-rich GPU terminal emulator",
            "tmux": "Terminal multiplexer",
            "zsh": "Powerful shell with many features",
            "fish": "User-friendly command line shell",
            "git": "Distributed version control system",
            "docker": "Container platform",
            "podman": "Daemonless container engine",
            "htop": "Interactive process viewer",
            "btop": "Beautiful resource monitor",
            "ranger": "Console file manager with VI key bindings",
            "lf": "Terminal file manager written in Go",
            "vlc": "Multimedia player and framework",
            "mpv": "Minimalist command line media player",
            "obsidian": "Knowledge base and note-taking app",
            "logseq": "Privacy-first, open-source knowledge base",
        }
        return descriptions.get(package, f"Package: {package}")

    def _determine_use_case(self, package: str) -> str:
        """Determine primary use case for a package"""
        data = self.package_graph.get(package, {})
        category = data.get("category", "")

        use_cases = {
            "text-editor": "Code editing and text manipulation",
            "browser": "Web browsing and internet access",
            "terminal": "Command-line interface",
            "shell": "Command interpretation and scripting",
            "vcs": "Version control and collaboration",
            "container": "Application containerization",
            "file-manager": "File navigation and management",
            "monitor": "System resource monitoring",
            "media": "Media playback and editing",
            "notes": "Note-taking and knowledge management",
        }

        return use_cases.get(category, "General purpose")

    def _guess_category(self, package: str) -> str:
        """Guess category from package name"""
        categories = {
            "editor": "text-editor",
            "vim": "text-editor",
            "emacs": "text-editor",
            "browser": "browser",
            "firefox": "browser",
            "chrome": "browser",
            "terminal": "terminal",
            "term": "terminal",
            "shell": "shell",
            "sh": "shell",
            "git": "vcs",
            "docker": "container",
            "podman": "container",
            "monitor": "monitor",
            "top": "monitor",
            "player": "media",
            "vlc": "media",
            "mpv": "media",
        }

        package_lower = package.lower()
        for keyword, category in categories.items():
            if keyword in package_lower:
                return category

        return "unknown"

    def _guess_category_from_name(self, package: str) -> Optional[str]:
        """Try to determine category from package name patterns"""
        patterns = {
            r".*editor|vim|emacs|code": "text-editor",
            r".*browser|firefox|chrome": "browser",
            r".*terminal|term|console": "terminal",
            r".*shell|bash|zsh|fish": "shell",
            r".*git|svn|hg": "vcs",
            r".*docker|podman|container": "container",
            r".*file.*manager|ranger|mc": "file-manager",
            r".*monitor|htop|top|ps": "monitor",
            r".*player|vlc|mpv|video|audio": "media",
            r".*notes|obsidian|logseq": "notes",
        }

        package_lower = package.lower()
        for pattern, category in patterns.items():
            if re.match(pattern, package_lower):
                return category

        return None

    def _recommend_by_category(
        self, category: str, original_query: str
    ) -> RecommendationSet:
        """Recommend packages from a specific category"""
        packages = []
        for pkg, data in self.package_graph.items():
            if data.get("category") == category:
                packages.append(
                    PackageRecommendation(
                        name=pkg,
                        description=self._get_description(pkg),
                        reason=f"Popular {category}",
                        similarity_score=0.5,
                        category=category,
                        use_case=self._determine_use_case(pkg),
                    )
                )

        return RecommendationSet(
            alternatives=packages[:5],
            similar=[],
            complementary=[],
            upgrade_path=[],
            explanation=f"Showing popular {category} packages. Original query '{original_query}' not found.",
        )

    def _generate_explanation(
        self, package: str, alternatives, similar, complementary
    ) -> str:
        """Generate explanation text for recommendations"""
        explanations = []

        if alternatives:
            explanations.append(f"Direct alternatives to {package}")

        if similar:
            explanations.append(f"Similar tools in the same category")

        if complementary:
            explanations.append(f"Tools that enhance {package}")

        if not explanations:
            return f"No specific recommendations found for {package}"

        return f"Recommendations include: {', '.join(explanations)}"

    def format_recommendations(self, recommendations: RecommendationSet) -> str:
        """Format recommendations for display"""
        output = []

        output.append(f"📊 **Package Recommendations**")
        output.append(f"💡 {recommendations.explanation}")

        if recommendations.upgrade_path:
            output.append("\n🚀 **Recommended Upgrade**:")
            for rec in recommendations.upgrade_path:
                output.append(f"  • {rec.name} - {rec.reason}")
                output.append(f"    {rec.description}")

        if recommendations.alternatives:
            output.append("\n🔄 **Alternatives**:")
            for rec in recommendations.alternatives[:3]:
                output.append(
                    f"  • {rec.name} ({rec.similarity_score:.0%} similar) - {rec.reason}"
                )
                output.append(f"    {rec.description}")

        if recommendations.complementary:
            output.append("\n🤝 **Works Well With**:")
            for rec in recommendations.complementary[:3]:
                output.append(f"  • {rec.name} - {rec.reason}")

        if recommendations.similar:
            output.append("\n🔍 **Similar Packages**:")
            for rec in recommendations.similar[:3]:
                output.append(f"  • {rec.name} - {rec.description}")

        return "\n".join(output)


# Integration point for CLI
def recommend_packages(package: str, context: Optional[Dict] = None) -> str:
    """
    Main entry point for package recommendations
    Returns formatted recommendations for the user
    """
    recommender = PackageRecommender()
    recommendations = recommender.recommend(package, context)
    return recommender.format_recommendations(recommendations)
