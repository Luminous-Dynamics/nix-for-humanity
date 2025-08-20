"""
Grandma Mode - Making NixOS REAL for non-technical users

This is focused on ONE persona: Grandma Rose (75)
- No technical jargon
- Clear confirmations
- Actually works (not dry-run)
- Explains everything simply
- Prevents mistakes
"""

import subprocess
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass


@dataclass
class GrandmaResponse:
    """Response formatted for Grandma Rose"""
    success: bool
    message: str  # What Grandma sees
    technical: Optional[str] = None  # Hidden technical details
    needs_confirmation: bool = False
    suggestions: List[str] = None


class GrandmaMode:
    """
    Real, working NixOS operations for non-technical users.
    
    Philosophy:
    - Everything must ACTUALLY WORK
    - No technical terms in messages
    - Prevent destructive mistakes
    - Explain like talking to your grandmother
    - Test every operation for real
    """
    
    def __init__(self):
        self.last_search_results = []
        self.commonly_used_programs = {
            'firefox': 'Web browser for the internet',
            'thunderbird': 'Email program',
            'libreoffice': 'Office suite (like Microsoft Word)',
            'vlc': 'Video player for movies',
            'gimp': 'Photo editing (like Photoshop)',
            'zoom': 'Video calling',
            'spotify': 'Music streaming',
            'skype': 'Video calling (older)',
            'chromium': 'Another web browser',
            'gedit': 'Simple text editor'
        }
        
    def install_program(self, program_name: str, confirm: bool = False) -> GrandmaResponse:
        """
        ACTUALLY install a program (not dry-run!)
        
        This is REAL - it will modify the system.
        """
        # Translate common terms to package names
        package = self._translate_to_package_name(program_name)
        
        # Check if already installed first
        if self._is_installed(package):
            return GrandmaResponse(
                success=True,
                message=f"Good news! {program_name} is already installed on your computer. You can use it right now!",
                technical=f"Package {package} already in profile"
            )
        
        # Safety check - require confirmation for actual installation
        if not confirm:
            return GrandmaResponse(
                success=False,
                message=f"I found {program_name}! To install it, I need your permission. This will add new software to your computer. Is that okay?",
                needs_confirmation=True,
                technical=f"Would run: nix-env -iA nixos.{package}"
            )
        
        # ACTUAL INSTALLATION (This is REAL!)
        try:
            print(f"🌟 Installing {program_name}... This might take a minute...")
            
            cmd = f"nix-env -iA nixos.{package}"
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes max
            )
            
            if result.returncode == 0:
                return GrandmaResponse(
                    success=True,
                    message=f"✅ Perfect! {program_name} is now installed on your computer. You can find it in your applications menu!",
                    technical=result.stdout,
                    suggestions=[
                        f"Look for {program_name} in your applications",
                        "You might need to log out and back in to see it",
                        "Try searching for it in the menu"
                    ]
                )
            else:
                # Installation failed - explain simply
                if "not found" in result.stderr:
                    return GrandmaResponse(
                        success=False,
                        message=f"I couldn't find a program called {program_name}. Would you like me to search for something similar?",
                        technical=result.stderr,
                        suggestions=self._suggest_alternatives(program_name)
                    )
                else:
                    return GrandmaResponse(
                        success=False,
                        message="Something went wrong with the installation. Don't worry, nothing was changed. Would you like to try again?",
                        technical=result.stderr
                    )
                    
        except subprocess.TimeoutExpired:
            return GrandmaResponse(
                success=False,
                message="The installation is taking longer than expected. This sometimes happens with large programs. Would you like to keep waiting?",
                technical="Installation timeout after 120 seconds"
            )
        except Exception as e:
            return GrandmaResponse(
                success=False,
                message="I encountered a problem. Don't worry, your computer is fine. Let's try again in a moment.",
                technical=str(e)
            )
    
    def search_programs(self, search_term: str) -> GrandmaResponse:
        """
        Search for programs in a Grandma-friendly way
        """
        try:
            # First check common programs
            friendly_results = []
            for pkg, description in self.commonly_used_programs.items():
                if search_term.lower() in pkg.lower() or search_term.lower() in description.lower():
                    friendly_results.append(f"• {pkg}: {description}")
            
            if friendly_results:
                return GrandmaResponse(
                    success=True,
                    message=f"Here are some programs that match '{search_term}':\n\n" + "\n".join(friendly_results[:5]),
                    suggestions=["To install one, just tell me: 'install [program name]'"]
                )
            
            # If not in common programs, do real search
            cmd = f"nix search nixpkgs {search_term} --json 2>/dev/null | head -1000"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout:
                import json
                try:
                    packages = json.loads(result.stdout)
                    if packages:
                        # Format results for Grandma
                        simple_results = []
                        for name, info in list(packages.items())[:5]:
                            pkg_name = name.split('.')[-1]
                            desc = info.get('description', 'A computer program')
                            # Simplify technical descriptions
                            desc = self._simplify_description(desc)
                            simple_results.append(f"• {pkg_name}: {desc}")
                        
                        self.last_search_results = simple_results
                        
                        return GrandmaResponse(
                            success=True,
                            message=f"I found these programs for '{search_term}':\n\n" + "\n".join(simple_results),
                            suggestions=["To install one, just tell me: 'install [program name]'"]
                        )
                except:
                    pass
            
            return GrandmaResponse(
                success=False,
                message=f"I couldn't find any programs matching '{search_term}'. Try searching for something else, or tell me what you want to do (like 'browse the internet' or 'edit photos').",
                suggestions=self._suggest_by_use_case(search_term)
            )
            
        except Exception as e:
            return GrandmaResponse(
                success=False,
                message="I had trouble searching. Let's try again with different words.",
                technical=str(e)
            )
    
    def remove_program(self, program_name: str, confirm: bool = False) -> GrandmaResponse:
        """
        ACTUALLY remove a program (with safety checks)
        """
        package = self._translate_to_package_name(program_name)
        
        # Check if installed
        if not self._is_installed(package):
            return GrandmaResponse(
                success=True,
                message=f"{program_name} is not installed on your computer, so there's nothing to remove!",
                technical=f"Package {package} not in profile"
            )
        
        # Safety check
        if not confirm:
            return GrandmaResponse(
                success=False,
                message=f"Are you sure you want to remove {program_name}? This will delete it from your computer. You can always install it again later if you change your mind.",
                needs_confirmation=True,
                technical=f"Would run: nix-env -e {package}"
            )
        
        # ACTUAL REMOVAL
        try:
            cmd = f"nix-env -e {package}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return GrandmaResponse(
                    success=True,
                    message=f"✅ Done! {program_name} has been removed from your computer. If you want it back later, just ask me to install it again.",
                    technical=result.stdout
                )
            else:
                return GrandmaResponse(
                    success=False,
                    message=f"I couldn't remove {program_name}. It might be needed by your system. It's safe to leave it installed.",
                    technical=result.stderr
                )
                
        except Exception as e:
            return GrandmaResponse(
                success=False,
                message="Something went wrong, but don't worry - nothing was changed.",
                technical=str(e)
            )
    
    def list_installed(self) -> GrandmaResponse:
        """
        Show installed programs in a friendly way
        """
        try:
            cmd = "nix-env -q"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout:
                # Parse and categorize programs
                programs = result.stdout.strip().split('\n')
                
                # Categorize for Grandma
                categories = {
                    'Internet': [],
                    'Office': [],
                    'Media': [],
                    'System Tools': [],
                    'Other': []
                }
                
                for prog in programs[:30]:  # Limit to first 30 to not overwhelm
                    clean_name = prog.split('-')[0]  # Remove version numbers
                    
                    # Simple categorization
                    if any(x in clean_name.lower() for x in ['firefox', 'chrome', 'browser', 'email', 'thunder']):
                        categories['Internet'].append(clean_name)
                    elif any(x in clean_name.lower() for x in ['office', 'writer', 'calc', 'word']):
                        categories['Office'].append(clean_name)
                    elif any(x in clean_name.lower() for x in ['video', 'audio', 'music', 'player', 'vlc']):
                        categories['Media'].append(clean_name)
                    elif any(x in clean_name.lower() for x in ['git', 'vim', 'emacs', 'compiler']):
                        categories['System Tools'].append(clean_name)
                    else:
                        categories['Other'].append(clean_name)
                
                # Format message
                message = "Here are the programs installed on your computer:\n"
                for category, progs in categories.items():
                    if progs:
                        message += f"\n{category}:\n"
                        for p in progs[:5]:  # Max 5 per category
                            message += f"  • {p}\n"
                
                if len(programs) > 30:
                    message += f"\n...and {len(programs) - 30} more technical programs"
                
                return GrandmaResponse(
                    success=True,
                    message=message,
                    suggestions=["To remove any program, just tell me: 'remove [program name]'"]
                )
            else:
                return GrandmaResponse(
                    success=True,
                    message="You don't have any extra programs installed yet. Your computer has all the basic system programs it needs to run.",
                    suggestions=["Try installing Firefox for web browsing: 'install firefox'"]
                )
                
        except Exception as e:
            return GrandmaResponse(
                success=False,
                message="I couldn't check your programs right now. Try again in a moment.",
                technical=str(e)
            )
    
    def _is_installed(self, package: str) -> bool:
        """Check if a package is actually installed"""
        try:
            result = subprocess.run(f"nix-env -q | grep -i {package}", shell=True, capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def _translate_to_package_name(self, friendly_name: str) -> str:
        """Translate friendly names to actual package names"""
        translations = {
            'browser': 'firefox',
            'internet': 'firefox',
            'email': 'thunderbird',
            'office': 'libreoffice',
            'word': 'libreoffice',
            'excel': 'libreoffice',
            'photos': 'gimp',
            'pictures': 'gimp',
            'music': 'spotify',
            'movies': 'vlc',
            'videos': 'vlc',
            'zoom': 'zoom-us',
            'text editor': 'gedit',
            'notepad': 'gedit'
        }
        
        lower = friendly_name.lower()
        return translations.get(lower, lower)
    
    def _simplify_description(self, desc: str) -> str:
        """Make technical descriptions grandma-friendly"""
        if len(desc) > 60:
            desc = desc[:60] + "..."
        
        # Replace technical terms
        replacements = {
            'CLI': 'text-based',
            'GUI': 'visual',
            'IDE': 'programming tool',
            'daemon': 'background program',
            'library': 'support program',
            'framework': 'foundation',
            'terminal': 'text window'
        }
        
        for tech, simple in replacements.items():
            desc = desc.replace(tech, simple)
        
        return desc
    
    def _suggest_alternatives(self, program: str) -> List[str]:
        """Suggest alternatives when a program isn't found"""
        suggestions = []
        
        if 'browse' in program.lower() or 'internet' in program.lower():
            suggestions.append("Try 'install firefox' for web browsing")
        elif 'email' in program.lower():
            suggestions.append("Try 'install thunderbird' for email")
        elif 'office' in program.lower() or 'word' in program.lower():
            suggestions.append("Try 'install libreoffice' for documents")
        elif 'photo' in program.lower() or 'image' in program.lower():
            suggestions.append("Try 'install gimp' for photo editing")
        elif 'video' in program.lower() or 'movie' in program.lower():
            suggestions.append("Try 'install vlc' for videos")
        
        return suggestions
    
    def _suggest_by_use_case(self, search: str) -> List[str]:
        """Suggest programs based on what user wants to do"""
        use_cases = {
            'browse': ["Try searching for 'firefox' or 'chromium'"],
            'email': ["Try searching for 'thunderbird' or 'evolution'"],
            'write': ["Try searching for 'libreoffice' or 'gedit'"],
            'watch': ["Try searching for 'vlc' or 'mpv'"],
            'listen': ["Try searching for 'spotify' or 'rhythmbox'"],
            'edit': ["Try searching for 'gimp' for photos or 'kdenlive' for videos"],
            'call': ["Try searching for 'zoom' or 'skype'"]
        }
        
        for key, suggestions in use_cases.items():
            if key in search.lower():
                return suggestions
        
        return ["Try describing what you want to do, like 'browse internet' or 'edit photos'"]