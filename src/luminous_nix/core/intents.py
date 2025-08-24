"""Unified intent recognition system."""

# === Merged from migration ===

"""
from typing import Dict, Optional
Intent recognition for natural language processing

This module handles the recognition of user intent from natural language input.
Uses a hybrid approach: pattern matching for speed, embeddings for flexibility.
"""

import re
import os
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, List
from pathlib import Path

# Import Response and Command for re-export
from ..api.schema import Command
from .responses import Response


class IntentType(Enum):
    """Types of intents we can recognize"""
    INSTALL_PACKAGE = "install_package"
    UPDATE_SYSTEM = "update_system"
    SEARCH_PACKAGE = "search_package"
    ROLLBACK = "rollback"
    CONFIGURE = "configure"
    EXPLAIN = "explain"
    HELP = "help"
    REMOVE_PACKAGE = "remove_package"
    GARBAGE_COLLECT = "garbage_collect"
    LIST_GENERATIONS = "list_generations"
    SWITCH_GENERATION = "switch_generation"
    REBUILD = "rebuild"
    EDIT_CONFIG = "edit_config"
    VALIDATE_CONFIG = "validate_config"
    SHOW_CONFIG = "show_config"
    GENERATE_CONFIG = "generate_config"
    CHECK_STATUS = "check_status"
    LIST_INSTALLED = "list_installed"
    # Network management
    SHOW_NETWORK = "show_network"
    SHOW_IP = "show_ip"
    CONNECT_WIFI = "connect_wifi"
    LIST_WIFI = "list_wifi"
    TEST_CONNECTION = "test_connection"
    # Service management
    START_SERVICE = "start_service"
    STOP_SERVICE = "stop_service"
    RESTART_SERVICE = "restart_service"
    SERVICE_STATUS = "service_status"
    LIST_SERVICES = "list_services"
    ENABLE_SERVICE = "enable_service"
    DISABLE_SERVICE = "disable_service"
    SERVICE_LOGS = "service_logs"
    # User management
    CREATE_USER = "create_user"
    LIST_USERS = "list_users"
    ADD_USER_TO_GROUP = "add_user_to_group"
    CHANGE_PASSWORD = "change_password"
    GRANT_SUDO = "grant_sudo"
    # Storage management
    DISK_USAGE = "disk_usage"
    ANALYZE_DISK = "analyze_disk"
    MOUNT_DEVICE = "mount_device"
    UNMOUNT_DEVICE = "unmount_device"
    FIND_LARGE_FILES = "find_large_files"
    # Flake management
    CREATE_FLAKE = "create_flake"
    VALIDATE_FLAKE = "validate_flake"
    CONVERT_FLAKE = "convert_flake"
    SHOW_FLAKE_INFO = "show_flake_info"
    # Package discovery
    DISCOVER_PACKAGE = "discover_package"
    FIND_BY_COMMAND = "find_by_command"
    BROWSE_CATEGORIES = "browse_categories"
    SHOW_POPULAR = "show_popular"
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """Represents a recognized intent"""
    type: IntentType
    entities: Dict[str, Any]
    confidence: float
    raw_text: str


class IntentRecognizer:
    """Fast, local intent recognition"""
    
    def __init__(self):
        """Initialize the intent recognizer"""
        self._load_patterns()
        self._load_embeddings()
        
    def _load_patterns(self):
        """Load regex patterns for intent matching"""
        # Install patterns
        self.install_patterns = [
            r'\b(install|add|get|need|want|set up)\s+(\S+)',
            r'\b(can you|please|could you)\s+(install|add|get)\s+(\S+)',
            r'\bI\s+(need|want|would like)\s+(\S+)',
        ]
        
        # Update patterns
        self.update_patterns = [
            r'\b(update|upgrade|refresh)\s+(my\s+)?(system|nixos)',
            r'\b(system|nixos)\s+(update|upgrade)',
            r'\bupdate\s+everything\b',
            r'\bupgrade\s+all\b',
        ]
        
        # Search patterns
        self.search_patterns = [
            r'\b(search|find|look for|is there)\s+(.*?)(\s+package)?$',
            r'\bwhat\s+(packages?|programs?)\s+(.*?)\?',
            r'\b(available|exists?)\s+(.*?)(\s+package)?$',
        ]
        
        # Rollback patterns
        self.rollback_patterns = [
            r'\b(rollback|roll back|revert|undo|go back)',
            r'\b(previous|last|old)\s+(generation|version|state)',
            r'\bundo\s+(update|upgrade|changes)',
        ]
        
        # Configure patterns
        self.configure_patterns = [
            r'\b(configure|config|set up|enable)\s+(\S+)',
            r'\b(how\s+to|help\s+me)\s+(configure|set up|enable)\s+(\S+)',
        ]
        
        # Explain patterns
        self.explain_patterns = [
            r'\b(what|explain|tell me about)\s+(is|are|about)?\s*(.+?)\?*$',
            r'\b(how\s+does?|how\s+to)\s+(.+?)\s+(work|works?)\?*$',
        ]
        
        # Help patterns
        self.help_patterns = [
            r'^help$',
            r'\bhelp\s*me\b',
            r'\bwhat\s+can\s+you\s+do\b',
            r'\bwhat\s+can\s+I\s+(say|ask)\b',
            r'\bhow\s+do\s+I\s+use\s+(this|you)\b',
            r'\bshow\s+me\s+commands\b',
            r'\blist\s+(of\s+)?commands\b',
        ]
        
        # Remove/uninstall patterns
        self.remove_patterns = [
            r'\b(remove|uninstall|delete)\s+(\S+)',
            r'\b(can you|please|could you)\s+(remove|uninstall|delete)\s+(\S+)',
            r'\bget\s+rid\s+of\s+(\S+)',
            r'\bI\s+don\'?t\s+want\s+(\S+)\s+anymore',
        ]
        
        # Garbage collection patterns
        self.garbage_collect_patterns = [
            r'\b(garbage\s+collect|gc|clean\s+up|cleanup|free\s+space|free\s+disk)',
            r'\b(delete|remove)\s+(old|unused)\s+(packages?|generations?)',
            r'\bdelete\s+old\s+packages?\b',  # More specific pattern
            r'\bclean\s+(up\s+)?my\s+(system|disk|space)',
            r'\bhow\s+much\s+space\s+can\s+I\s+free',
        ]
        
        # List generations patterns
        self.list_generations_patterns = [
            r'\b(list|show|view)\s+(system\s+)?generations?',
            r'\bwhat\s+generations?\s+(do\s+I\s+have|are\s+available)',
            r'\bwhat\s+generations\s+do\s+I\s+have\b',  # More specific
            r'\bshow\s+me\s+(my\s+)?generations?',
            r'\bhistory\s+of\s+(my\s+)?system',
        ]
        
        # Switch generation patterns
        self.switch_generation_patterns = [
            r'\b(switch|change|go)\s+(to|back\s+to)\s+generation\s+(\d+)',
            r'\bgo\s+back\s+to\s+generation\s+(\d+)',  # More specific
            r'\buse\s+generation\s+(\d+)',
            r'\bboot\s+(into|to)\s+generation\s+(\d+)',
        ]
        
        # Rebuild patterns (without updating)
        self.rebuild_patterns = [
            r'\b(rebuild|apply)\s+(my\s+)?(configuration|config|changes|system)',
            r'\b(nixos-)?rebuild\s+(switch|boot|test)',
            r'\brebuild\s+my\s+system\b',
            r'\bapply\s+changes?\b',
            r'\bactivate\s+(my\s+)?(configuration|config)',
            r'^rebuild$',  # Match just "rebuild" by itself
        ]
        
        # Edit configuration patterns
        self.edit_config_patterns = [
            r'\b(edit|modify|change|open)\s+(my\s+)?(configuration|config)',
            r'\b(configuration|config)\s+file',
            r'\bopen\s+configuration\.nix',
            r'\bwhere\s+is\s+(my\s+)?config',
        ]
        
        # Show configuration patterns
        self.show_config_patterns = [
            r'\b(show|view|display|see)\s+(my\s+)?(configuration|config)',
            r'\bwhat\'?s\s+in\s+(my\s+)?(configuration|config)',
            r'\bcat\s+configuration\.nix',
            r'\bread\s+(my\s+)?config',
        ]
        
        # Generate configuration patterns
        self.generate_config_patterns = [
            r'\b(generate|create|make|build)\s+(a\s+)?(configuration|config)\s+(for\s+)?(.+)',
            r'\b(make|build|create)\s+me\s+a\s+(.+)\s+(configuration|config|system)',
            r'\b(configuration|config)\s+for\s+(.+)',
            r'\bi\s+want\s+a\s+(.+)\s+(server|desktop|system)',
            r'\b(setup|configure)\s+(.+)\s+for\s+me',
        ]
        
        # Flake patterns
        self.create_flake_patterns = [
            r'\b(create|make|generate|build)\s+(a\s+)?flake(\s+for\s+)?(.+)?',
            r'\b(create|make|generate)\s+(a\s+)?(.+?)\s+(dev|development)\s+(environment|shell|flake)',
            r'\bflake\s+for\s+(.+)',
            r'\b(python|rust|node|javascript|go|java|c\+\+)\s+(dev|development)\s+(environment|shell)',
            r'\bdev\s+(environment|shell)\s+for\s+(.+)',
        ]
        
        self.validate_flake_patterns = [
            r'\b(validate|check|verify)\s+(the\s+)?flake',
            r'\bflake\s+(validate|check|verify)',
            r'\bis\s+(the\s+)?flake\s+(valid|ok|correct)',
        ]
        
        self.convert_flake_patterns = [
            r'\b(convert|migrate)\s+(to\s+)?flake',
            r'\bconvert\s+(shell\.nix|default\.nix)\s+to\s+flake',
            r'\bmake\s+this\s+a\s+flake',
            r'\bflakify',
        ]
        
        self.show_flake_info_patterns = [
            r'\b(show|display|info)\s+(flake\s+)?info',
            r'\bflake\s+(info|information|details)',
            r'\bwhat\'?s\s+in\s+(the\s+)?flake',
            r'\bdescribe\s+(the\s+)?flake',
        ]
        
        # Check status patterns
        self.check_status_patterns = [
            r'\b(check|show|what\'?s)\s+(system\s+)?status',
            r'\bsystem\s+info(rmation)?',
            r'\bhow\s+is\s+my\s+system(\s+doing)?',
            r'\bhealth\s+check',
            r'\bsystem\s+health',
        ]
        
        # List installed patterns
        self.list_installed_patterns = [
            r'\b(list|show|what)\s+(packages?\s+)?(are\s+)?installed',
            r'\bwhat\s+packages\s+are\s+installed\b',  # More specific
            r'\bwhat\s+do\s+I\s+have\s+installed\b',   # More specific
            r'\bshow\s+(me\s+)?my\s+packages',
            r'\binstalled\s+packages?',
        ]
        
        # Network patterns
        self.show_network_patterns = [
            r'\b(show|check|display|view)\s+(my\s+)?(network|internet|connection)(\s+status)?',
            r'\bnetwork\s+status',
            r'\bnetwork\s+info(rmation)?',
            r'\bconnection\s+status',
            r'\binternet\s+status',
        ]
        
        self.show_ip_patterns = [
            r'\b(show|what\'?s?|display|get)\s+(my\s+)?ip(\s+address)?',
            r'\bip\s+address',
            r'\bmy\s+ip\s+is',
            r'\bwhat\s+is\s+my\s+ip',
            r'\bshow\s+network\s+interfaces?',
        ]
        
        self.connect_wifi_patterns = [
            r'\bconnect\s+(to\s+)?(wifi|wireless)(\s+(.+))?',
            r'\bjoin\s+(wifi|wireless)(\s+(.+))?',
            r'\bconnect\s+to\s+(.+)\s+(wifi|network)',
            r'\bwifi\s+connect\s+(.+)',
        ]
        
        self.list_wifi_patterns = [
            r'\b(list|show|scan|find|search)\s+(available\s+)?(wifi|wireless)(\s+networks?)?',
            r'\bwifi\s+scan',
            r'\bwhat\s+wifi\s+(is\s+)?available',
            r'\bnearby\s+(wifi|networks?)',
        ]
        
        self.test_connection_patterns = [
            r'\b(test|check)\s+(internet|network|connection|connectivity)',
            r'\b(is\s+)?(internet|network)\s+working',
            r'\bam\s+i\s+(online|connected)',
            r'\bping\s+test',
            r'\bconnection\s+test',
        ]
        
        # User management patterns
        self.create_user_patterns = [
            r'\b(create|add|new)\s+(user|account)\s+(\S+)',
            r'\b(create|add)\s+(\S+)\s+user',
            r'\buser\s+add\s+(\S+)',
            r'\buseradd\s+(\S+)',
            r'\bmake\s+a?\s?new\s+user\s+(?:named\s+)?(\S+)',
        ]
        
        self.list_users_patterns = [
            r'\b(list|show|display)\s+(all\s+)?users?',
            r'\bwho\s+are\s+the\s+users',
            r'\bshow\s+me\s+(all\s+)?users',
            r'\busers?\s+list',
            r'\bget\s+users?',
        ]
        
        self.add_user_to_group_patterns = [
            r'\badd\s+(\S+)\s+to\s+(?:the\s+)?(\S+)\s+group',
            r'\badd\s+user\s+(\S+)\s+to\s+group\s+(\S+)',
            r'\bmake\s+(\S+)\s+(?:a\s+)?member\s+of\s+(\S+)',
            r'\bgrant\s+(\S+)\s+access\s+to\s+(\S+)\s+group',
            r'\busermod\s+.*?-[aG].*?(\S+)\s+(\S+)',
        ]
        
        self.change_password_patterns = [
            r'\b(change|reset|set)\s+password\s+(?:for\s+)?(\S+)',
            r'\b(change|reset|set)\s+(\S+)(?:\'s)?\s+password',
            r'\bpassword\s+(change|reset)\s+(?:for\s+)?(\S+)',
            r'\bpasswd\s+(\S+)',
            r'\bnew\s+password\s+for\s+(\S+)',
        ]
        
        self.grant_sudo_patterns = [
            r'\b(grant|give)\s+(\S+)\s+sudo(?:\s+access)?',
            r'\bmake\s+(\S+)\s+(?:a\s+)?sudo(?:er)?',
            r'\badd\s+(\S+)\s+to\s+sudo(?:ers)?',
            r'\b(\S+)\s+needs?\s+sudo(?:\s+access)?',
            r'\benable\s+sudo\s+for\s+(\S+)',
        ]
        
        # Storage management patterns
        self.disk_usage_patterns = [
            r'\b(disk|storage)\s+(usage|space|free)',
            r'\bhow\s+much\s+(disk|storage)\s+(?:space)?',
            r'\bshow\s+(disk|storage)\s+space',
            r'\bdf\b',
            r'\bfree\s+space',
            r'\bspace\s+left',
        ]
        
        self.analyze_disk_patterns = [
            r'\bwhat\'?s?\s+(?:is\s+)?(?:taking|using)\s+(?:up\s+)?(?:disk\s+)?space',
            r'\b(analyze|check)\s+disk\s+usage',
            r'\bfind\s+(?:what\'?s?\s+)?(?:using|taking)\s+space',
            r'\bdisk\s+space\s+analysis',
            r'\bdu\s+-h',
        ]
        
        self.mount_device_patterns = [
            r'\bmount\s+(\S+)(?:\s+(?:to|at|on)\s+(\S+))?',
            r'\battach\s+(\S+)(?:\s+(?:to|at)\s+(\S+))?',
            r'\bmount\s+(?:the\s+)?(?:usb|drive|disk|device)\s+(\S+)',
            r'\bconnect\s+(?:the\s+)?(?:usb|drive|disk)\s+(\S+)',
        ]
        
        self.unmount_device_patterns = [
            r'\b(unmount|umount)\s+(\S+)',
            r'\b(disconnect|detach|eject)\s+(\S+)',
            r'\b(unmount|umount)\s+(?:the\s+)?(?:usb|drive|disk|device)',
            r'\bsafely\s+remove\s+(\S+)',
            r'\beject\s+(\S+)',
        ]
        
        self.find_large_files_patterns = [
            r'\bfind\s+(?:the\s+)?(?:large|big|huge)\s+files?',
            r'\bwhat\s+files?\s+(?:are|is)\s+(?:taking|using)\s+(?:the\s+)?most\s+space',
            r'\b(?:show|list)\s+(?:the\s+)?(?:largest|biggest)\s+files?',
            r'\btop\s+(?:\d+\s+)?(?:large|big)\s+files?',
            r'\bspace\s+hogs',
        ]
        
        # Service patterns
        self.start_service_patterns = [
            r'\bstart\s+(service\s+)?(\S+)(\s+service)?',
            r'\b(systemctl\s+)?start\s+(\S+)',
            r'\bturn\s+on\s+(\S+)(\s+service)?',
            r'\benable\s+and\s+start\s+(\S+)',
        ]
        
        self.stop_service_patterns = [
            r'\bstop\s+(service\s+)?(\S+)(\s+service)?',
            r'\b(systemctl\s+)?stop\s+(\S+)',
            r'\bturn\s+off\s+(\S+)(\s+service)?',
            r'\bshutdown\s+(\S+)(\s+service)?',
        ]
        
        self.restart_service_patterns = [
            r'\brestart\s+(service\s+)?(\S+)(\s+service)?',
            r'\b(systemctl\s+)?restart\s+(\S+)',
            r'\breload\s+(\S+)(\s+service)?',
            r'\breset\s+(\S+)(\s+service)?',
        ]
        
        self.service_status_patterns = [
            r'\b(service\s+)?status\s+(of\s+)?(\S+)(\s+service)?',
            r'\b(systemctl\s+)?status\s+(\S+)',
            r'\bis\s+(\S+)\s+(service\s+)?running',
            r'\bcheck\s+(\S+)\s+(service\s+)?status',
            r'\b(\S+)\s+service\s+status',
        ]
        
        self.list_services_patterns = [
            r'\b(list|show)\s+(all\s+)?services?',
            r'\bwhat\s+services\s+are\s+running',
            r'\bshow\s+running\s+services',
            r'\bsystemctl\s+list',
            r'\bactive\s+services',
        ]
        
        self.enable_service_patterns = [
            r'\benable\s+(service\s+)?(\S+)(\s+service)?',
            r'\b(systemctl\s+)?enable\s+(\S+)',
            r'\bauto[\s-]?start\s+(\S+)(\s+service)?',
            r'\bstart\s+(\S+)\s+on\s+boot',
        ]
        
        self.disable_service_patterns = [
            r'\bdisable\s+(service\s+)?(\S+)(\s+service)?',
            r'\b(systemctl\s+)?disable\s+(\S+)',
            r'\bdon\'?t\s+auto[\s-]?start\s+(\S+)',
            r'\bprevent\s+(\S+)\s+from\s+starting',
        ]
        
        self.service_logs_patterns = [
            r'\b(show|view|display)\s+(service\s+)?logs?\s+(for\s+)?(\S+)',
            r'\b(\S+)\s+(service\s+)?logs?',
            r'\bjournalctl\s+.*?(\S+)',
            r'\blogs?\s+(of|for)\s+(\S+)(\s+service)?',
        ]
        
        # Common package aliases
        self.package_aliases = {
            'firefox': 'firefox',
            'chrome': 'google-chrome', 
            'chromium': 'chromium',
            'vscode': 'vscode',
            'code': 'vscode',
            'vim': 'vim',
            'neovim': 'neovim',
            'nvim': 'neovim',
            'emacs': 'emacs',
            'python': 'python3',
            'python3': 'python311',
            'nodejs': 'nodejs',
            'node': 'nodejs',
            'npm': 'nodejs',
            'docker': 'docker',
            'git': 'git',
            'htop': 'htop',
            'tmux': 'tmux',
            'zsh': 'zsh',
            'fish': 'fish',
            'rust': 'rustc',
            'cargo': 'cargo',
            'rustc': 'rustc',
            'go': 'go',
            'golang': 'go',
            'java': 'openjdk',
            'jdk': 'openjdk',
        }
        
    def _load_embeddings(self):
        """Load embeddings for semantic matching (placeholder)"""
        # In a full implementation, we'd load pre-computed embeddings
        # For now, we'll rely on pattern matching
        self._embeddings_loaded = False
        
    async def recognize(self, text: str, context: Dict[str, Any]) -> Intent:
        """
        Recognize intent from natural language
        
        Args:
            text: The user's input text
            context: Additional context (user history, preferences, etc.)
            
        Returns:
            Recognized Intent
        """
        # 1. Normalize text
        normalized = self._normalize(text)
        
        # 2. Try pattern matching first (fast)
        if intent := self._match_patterns(normalized):
            return intent
            
        # 3. Use embeddings for semantic matching (if available)
        if self._embeddings_loaded:
            if intent := await self._semantic_match(normalized):
                return intent
                
        # 4. Unknown intent
        return Intent(
            type=IntentType.UNKNOWN,
            entities={},
            confidence=0.1,  # Low confidence for unknown
            raw_text=text
        )
        
    def _normalize(self, text: str) -> str:
        """Normalize input text"""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove punctuation at the end
        text = text.rstrip('.,!?;:')
        
        return text
        
    def _match_patterns(self, text: str) -> Optional[Intent]:
        """Fast regex-based pattern matching"""
        
        # Check help patterns first (highest priority)
        for pattern in self.help_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    type=IntentType.HELP,
                    entities={},
                    confidence=0.95,
                    raw_text=text
                )
        
        # Check switch generation patterns (specific with numbers)
        for pattern in self.switch_generation_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                # Extract generation number
                generation_num = None
                for group in match.groups():
                    if group and group.isdigit():
                        generation_num = int(group)
                        break
                        
                if generation_num is not None:
                    return Intent(
                        type=IntentType.SWITCH_GENERATION,
                        entities={'generation': generation_num},
                        confidence=0.9,
                        raw_text=text
                    )
        
        # Check garbage collection patterns
        for pattern in self.garbage_collect_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    type=IntentType.GARBAGE_COLLECT,
                    entities={},
                    confidence=0.85,
                    raw_text=text
                )
                
        # Check list generations patterns
        for pattern in self.list_generations_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    type=IntentType.LIST_GENERATIONS,
                    entities={},
                    confidence=0.9,
                    raw_text=text
                )
                
        # Check rebuild patterns
        for pattern in self.rebuild_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                # Extract rebuild type if specified
                rebuild_type = 'switch'  # default
                if 'boot' in text.lower():
                    rebuild_type = 'boot'
                elif 'test' in text.lower():
                    rebuild_type = 'test'
                    
                return Intent(
                    type=IntentType.REBUILD,
                    entities={'rebuild_type': rebuild_type},
                    confidence=0.85,
                    raw_text=text
                )
                
        # Check edit config patterns
        for pattern in self.edit_config_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    type=IntentType.EDIT_CONFIG,
                    entities={},
                    confidence=0.9,
                    raw_text=text
                )
                
        # Check show config patterns
        for pattern in self.show_config_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    type=IntentType.SHOW_CONFIG,
                    entities={},
                    confidence=0.9,
                    raw_text=text
                )
                
        # Check generate config patterns
        for pattern in self.generate_config_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                # Extract what kind of configuration they want
                description = None
                groups = match.groups()
                # The description is usually in the last non-empty group
                for group in reversed(groups):
                    if group and group not in ['a', 'for', 'configuration', 'config', 'system']:
                        description = group.strip()
                        break
                
                return Intent(
                    type=IntentType.GENERATE_CONFIG,
                    entities={'description': description or text},
                    confidence=0.85,
                    raw_text=text
                )
                
        # Check flake patterns
        for pattern in self.create_flake_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                # Extract description for the flake
                description = None
                groups = match.groups()
                for group in reversed(groups):
                    if group and group not in ['create', 'make', 'generate', 'build', 'a', 'flake', 'for', 'dev', 'development', 'environment', 'shell']:
                        description = group.strip()
                        break
                
                return Intent(
                    type=IntentType.CREATE_FLAKE,
                    entities={'description': description or text},
                    confidence=0.85,
                    raw_text=text
                )
        
        for pattern in self.validate_flake_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    type=IntentType.VALIDATE_FLAKE,
                    entities={},
                    confidence=0.9,
                    raw_text=text
                )
        
        for pattern in self.convert_flake_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    type=IntentType.CONVERT_FLAKE,
                    entities={},
                    confidence=0.9,
                    raw_text=text
                )
        
        for pattern in self.show_flake_info_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    type=IntentType.SHOW_FLAKE_INFO,
                    entities={},
                    confidence=0.9,
                    raw_text=text
                )
                
        # Check status patterns
        for pattern in self.check_status_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    type=IntentType.CHECK_STATUS,
                    entities={},
                    confidence=0.85,
                    raw_text=text
                )
        
        # Check network patterns
        for pattern in self.show_network_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    type=IntentType.SHOW_NETWORK,
                    entities={},
                    confidence=0.9,
                    raw_text=text
                )
        
        for pattern in self.show_ip_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    type=IntentType.SHOW_IP,
                    entities={},
                    confidence=0.9,
                    raw_text=text
                )
        
        for pattern in self.connect_wifi_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                # Extract SSID from various pattern groups
                ssid = None
                for group in match.groups():
                    if group and group not in ['to', 'wifi', 'wireless', 'network']:
                        ssid = group.strip()
                        break
                
                return Intent(
                    type=IntentType.CONNECT_WIFI,
                    entities={'ssid': ssid} if ssid else {},
                    confidence=0.85,
                    raw_text=text
                )
        
        for pattern in self.list_wifi_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    type=IntentType.LIST_WIFI,
                    entities={},
                    confidence=0.9,
                    raw_text=text
                )
        
        for pattern in self.test_connection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    type=IntentType.TEST_CONNECTION,
                    entities={},
                    confidence=0.9,
                    raw_text=text
                )
        
        # Check service patterns
        for pattern in self.start_service_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                # Extract service name
                service = None
                for group in match.groups():
                    if group and group not in ['service', 'systemctl', 'start', 'on', 'and']:
                        service = group.strip()
                        break
                
                if service:
                    return Intent(
                        type=IntentType.START_SERVICE,
                        entities={'service': service},
                        confidence=0.9,
                        raw_text=text
                    )
        
        for pattern in self.stop_service_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                # Extract service name
                service = None
                for group in match.groups():
                    if group and group not in ['service', 'systemctl', 'stop', 'off']:
                        service = group.strip()
                        break
                
                if service:
                    return Intent(
                        type=IntentType.STOP_SERVICE,
                        entities={'service': service},
                        confidence=0.9,
                        raw_text=text
                    )
        
        for pattern in self.restart_service_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                # Extract service name
                service = None
                for group in match.groups():
                    if group and group not in ['service', 'systemctl', 'restart', 'reload']:
                        service = group.strip()
                        break
                
                if service:
                    return Intent(
                        type=IntentType.RESTART_SERVICE,
                        entities={'service': service},
                        confidence=0.9,
                        raw_text=text
                    )
        
        for pattern in self.service_status_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                # Extract service name
                service = None
                for group in match.groups():
                    if group and group not in ['service', 'systemctl', 'status', 'of', 'is', 'running', 'check']:
                        service = group.strip()
                        break
                
                if service:
                    return Intent(
                        type=IntentType.SERVICE_STATUS,
                        entities={'service': service},
                        confidence=0.9,
                        raw_text=text
                    )
        
        for pattern in self.list_services_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    type=IntentType.LIST_SERVICES,
                    entities={},
                    confidence=0.9,
                    raw_text=text
                )
        
        for pattern in self.enable_service_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                # Extract service name
                service = None
                for group in match.groups():
                    if group and group not in ['service', 'systemctl', 'enable', 'auto', 'start', 'on', 'boot']:
                        service = group.strip()
                        break
                
                if service:
                    return Intent(
                        type=IntentType.ENABLE_SERVICE,
                        entities={'service': service},
                        confidence=0.9,
                        raw_text=text
                    )
        
        for pattern in self.disable_service_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                # Extract service name
                service = None
                for group in match.groups():
                    if group and group not in ['service', 'systemctl', 'disable', 'don\'t', 'auto', 'start', 'prevent', 'from', 'starting']:
                        service = group.strip()
                        break
                
                if service:
                    return Intent(
                        type=IntentType.DISABLE_SERVICE,
                        entities={'service': service},
                        confidence=0.9,
                        raw_text=text
                    )
        
        for pattern in self.service_logs_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                # Extract service name
                service = None
                for group in match.groups():
                    if group and group not in ['show', 'view', 'display', 'service', 'logs', 'log', 'for', 'of', 'journalctl']:
                        service = group.strip()
                        break
                
                if service:
                    return Intent(
                        type=IntentType.SERVICE_LOGS,
                        entities={'service': service},
                        confidence=0.85,
                        raw_text=text
                    )
        
        # Check user management patterns
        for pattern in self.create_user_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                # Extract username
                username = None
                for group in match.groups():
                    if group and group not in ['create', 'add', 'new', 'user', 'account', 'make', 'a', 'named']:
                        username = group.strip()
                        break
                
                if username:
                    return Intent(
                        type=IntentType.CREATE_USER,
                        entities={'username': username},
                        confidence=0.9,
                        raw_text=text
                    )
        
        for pattern in self.list_users_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    type=IntentType.LIST_USERS,
                    entities={},
                    confidence=0.9,
                    raw_text=text
                )
        
        for pattern in self.add_user_to_group_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                # Extract username and group
                username = None
                group = None
                groups = match.groups()
                if len(groups) >= 2:
                    # Filter out common words
                    for i, g in enumerate(groups):
                        if g and g not in ['add', 'to', 'the', 'user', 'group', 'make', 'a', 'member', 'of', 'grant', 'access']:
                            if not username:
                                username = g.strip()
                            elif not group:
                                group = g.strip()
                                break
                
                if username and group:
                    return Intent(
                        type=IntentType.ADD_USER_TO_GROUP,
                        entities={'username': username, 'group': group},
                        confidence=0.9,
                        raw_text=text
                    )
        
        for pattern in self.change_password_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                # Extract username
                username = None
                for group in match.groups():
                    if group and group not in ['change', 'reset', 'set', 'password', 'for', '\'s', 'new']:
                        username = group.strip()
                        break
                
                if username:
                    return Intent(
                        type=IntentType.CHANGE_PASSWORD,
                        entities={'username': username},
                        confidence=0.9,
                        raw_text=text
                    )
        
        for pattern in self.grant_sudo_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                # Extract username
                username = None
                for group in match.groups():
                    if group and group not in ['grant', 'give', 'sudo', 'access', 'make', 'a', 'sudoer', 'add', 'to', 'sudoers', 'needs', 'enable', 'for']:
                        username = group.strip()
                        break
                
                if username:
                    return Intent(
                        type=IntentType.GRANT_SUDO,
                        entities={'username': username},
                        confidence=0.9,
                        raw_text=text
                    )
        
        # Check storage management patterns
        for pattern in self.disk_usage_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    type=IntentType.DISK_USAGE,
                    entities={},
                    confidence=0.9,
                    raw_text=text
                )
        
        for pattern in self.analyze_disk_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    type=IntentType.ANALYZE_DISK,
                    entities={},
                    confidence=0.9,
                    raw_text=text
                )
        
        for pattern in self.mount_device_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                # Extract device and mount point
                device = None
                mount_point = None
                groups = match.groups()
                if groups:
                    for i, g in enumerate(groups):
                        if g and g not in ['mount', 'attach', 'to', 'at', 'on', 'the', 'usb', 'drive', 'disk', 'device', 'connect']:
                            if not device:
                                device = g.strip()
                            elif not mount_point:
                                mount_point = g.strip()
                                break
                
                if device:
                    return Intent(
                        type=IntentType.MOUNT_DEVICE,
                        entities={'device': device, 'mount_point': mount_point},
                        confidence=0.85,
                        raw_text=text
                    )
        
        for pattern in self.unmount_device_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                # Extract device
                device = None
                for group in match.groups():
                    if group and group not in ['unmount', 'umount', 'disconnect', 'detach', 'eject', 'the', 'usb', 'drive', 'disk', 'device', 'safely', 'remove']:
                        device = group.strip()
                        break
                
                if device:
                    return Intent(
                        type=IntentType.UNMOUNT_DEVICE,
                        entities={'device': device},
                        confidence=0.9,
                        raw_text=text
                    )
        
        for pattern in self.find_large_files_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                # Extract optional count
                count = 10  # default
                for group in match.groups():
                    if group and group.isdigit():
                        count = int(group)
                        break
                
                return Intent(
                    type=IntentType.FIND_LARGE_FILES,
                    entities={'count': count},
                    confidence=0.9,
                    raw_text=text
                )
        
        # Check list installed patterns FIRST (before install patterns)
        # This prevents "list installed packages" from matching install pattern
        for pattern in self.list_installed_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    type=IntentType.LIST_INSTALLED,
                    entities={},
                    confidence=0.9,
                    raw_text=text
                )
        
        # Check remove/uninstall patterns SECOND (before install)
        # This prevents "get rid of" from matching the install pattern
        for pattern in self.remove_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                # Extract package name
                if len(match.groups()) >= 3 and match.group(2) in ['remove', 'uninstall', 'delete']:
                    package = match.group(3)
                elif len(match.groups()) >= 2:
                    package = match.group(2)
                else:
                    package = match.group(1)
                    
                # Resolve aliases
                package = package.lower()
                package = self.package_aliases.get(package, package)
                
                return Intent(
                    type=IntentType.REMOVE_PACKAGE,
                    entities={'package': package},
                    confidence=0.9,
                    raw_text=text
                )
        
        # Check install patterns (after list and remove to avoid false matches)
        for pattern in self.install_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                # Extract package name
                if len(match.groups()) >= 2:
                    package = match.group(2) if match.group(1) in ['install', 'add', 'get'] else match.group(3)
                else:
                    package = match.group(1)
                    
                # Resolve aliases
                package = package.lower()
                package = self.package_aliases.get(package, package)
                
                # Calculate confidence based on how specific the package is
                confidence = 0.9
                if package in ['something', 'anything', 'stuff', 'things', 'it']:
                    confidence = 0.6  # Very vague package name
                elif len(package) < 2 or package in ['me', 'a', 'the', 'some']:
                    confidence = 0.5  # Too short or generic
                
                return Intent(
                    type=IntentType.INSTALL_PACKAGE,
                    entities={'package': package},
                    confidence=confidence,
                    raw_text=text
                )
                
        # Check update patterns
        for pattern in self.update_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    type=IntentType.UPDATE_SYSTEM,
                    entities={},
                    confidence=0.85,
                    raw_text=text
                )
                
        # Check search patterns
        for pattern in self.search_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                query = match.group(2) if len(match.groups()) >= 2 else match.group(1)
                return Intent(
                    type=IntentType.SEARCH_PACKAGE,
                    entities={'query': query.strip()},
                    confidence=0.8,
                    raw_text=text
                )
                
        # Check rollback patterns
        for pattern in self.rollback_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    type=IntentType.ROLLBACK,
                    entities={},
                    confidence=0.85,
                    raw_text=text
                )
                
        # Check configure patterns
        for pattern in self.configure_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                if len(match.groups()) >= 2:
                    service = match.group(2) if match.group(1) in ['configure', 'config', 'set up', 'enable'] else match.group(3)
                else:
                    service = match.group(1)
                    
                return Intent(
                    type=IntentType.CONFIGURE,
                    entities={'config': service},
                    confidence=0.75,
                    raw_text=text
                )
                
        # Check explain patterns
        for pattern in self.explain_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                # Get the topic from the last capture group
                topic = match.groups()[-1] if match.groups() else ""
                topic = topic.strip()
                
                if topic:
                    return Intent(
                        type=IntentType.EXPLAIN,
                        entities={'topic': topic},
                        confidence=0.7,
                        raw_text=text
                    )
        
        # Check disk/storage management patterns
        for pattern in self.disk_usage_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    type=IntentType.DISK_USAGE,
                    entities={},
                    confidence=0.9,
                    raw_text=text
                )
        
        for pattern in self.analyze_disk_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    type=IntentType.ANALYZE_DISK,
                    entities={},
                    confidence=0.9,
                    raw_text=text
                )
        
        for pattern in self.find_large_files_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return Intent(
                    type=IntentType.FIND_LARGE_FILES,
                    entities={},
                    confidence=0.9,
                    raw_text=text
                )
                    
        return None
        
    async def _semantic_match(self, text: str) -> Optional[Intent]:
        """Use embeddings for semantic matching (placeholder)"""
        # This would use sentence transformers or similar
        # For now, return None to fall through to unknown
        return None
        
    def extract_entities(self, text: str, intent_type: IntentType) -> Dict[str, Any]:
        """Extract entities based on intent type"""
        entities = {}
        
        if intent_type == IntentType.INSTALL_PACKAGE:
            # Extract package name
            words = text.split()
            for i, word in enumerate(words):
                if word in ['install', 'add', 'get'] and i + 1 < len(words):
                    package = words[i + 1]
                    package = self.package_aliases.get(package, package)
                    entities['package'] = package
                    break
                    
        elif intent_type == IntentType.SEARCH_PACKAGE:
            # Extract search query
            for pattern in self.search_patterns:
                if match := re.search(pattern, text, re.IGNORECASE):
                    query = match.group(2) if len(match.groups()) >= 2 else match.group(1)
                    entities['query'] = query.strip()
                    break
                    
        return entities
    
    def recognize(self, text: str) -> Intent:
        """
        Synchronous version of intent recognition for CLI compatibility
        
        Args:
            text: The user's input text
            
        Returns:
            Recognized Intent
        """
        # 1. Normalize text
        normalized = self._normalize(text)
        
        # 2. Try pattern matching first (fast)
        if intent := self._match_patterns(normalized):
            return intent
            
        # 3. Unknown intent
        return Intent(
            type=IntentType.UNKNOWN,
            entities={},
            confidence=0.1,  # Low confidence for unknown
            raw_text=text
        )

# Export all public classes
__all__ = [
    'Intent',
    'IntentType',
    'IntentRecognizer',
    'Response',
    'Command',
]
