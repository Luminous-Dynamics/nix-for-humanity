"""
Sophia-Shell: Shell Scripting & Command Line Expert

A specialized Sophia agent with deep expertise in:
- Shell scripting (bash, zsh, fish)
- Command-line utilities and pipelines
- Process management and debugging
- System diagnostics and troubleshooting
"""

from typing import Dict, List, Any, Union
from ..sophia.unified_consciousness import UnifiedSophiaEngine
from ..context import ensure_context, Context


class SophiaShell(UnifiedSophiaEngine):
    """
    Shell Scripting Specialist Agent

    Extends the unified 9-layer consciousness with domain-specific
    knowledge about shell commands, scripting, and debugging.
    """

    def __init__(self):
        """Initialize Sophia-Shell specialist"""
        super().__init__()

        # Domain-specific knowledge
        self.specialization = "Shell"
        self.expertise_domains = [
            "shell",
            "bash",
            "scripting",
            "command-line",
            "debugging",
            "process-management"
        ]

        # Common command patterns
        self.command_patterns = {
            "file_operations": {
                "find": "find <path> -name '<pattern>'",
                "grep": "grep -r '<pattern>' <path>",
                "sed": "sed 's/old/new/g' file",
                "awk": "awk '{print $1}' file",
            },
            "process_management": {
                "ps": "ps aux | grep <process>",
                "kill": "kill -9 <pid>",
                "top": "top -o %CPU",
                "htop": "htop",
            },
            "networking": {
                "netstat": "netstat -tulpn",
                "ss": "ss -tulpn",
                "curl": "curl -I <url>",
                "wget": "wget <url>",
            },
            "system_info": {
                "df": "df -h",
                "du": "du -sh <path>",
                "free": "free -h",
                "uname": "uname -a",
            }
        }

        # Debugging techniques
        self.debugging_techniques = {
            "script_debugging": [
                "Add 'set -x' for trace mode",
                "Add 'set -e' to exit on error",
                "Use 'set -u' for undefined variable detection",
                "Add 'trap' for cleanup on exit",
            ],
            "command_debugging": [
                "Use 'strace' to trace system calls",
                "Use 'ltrace' to trace library calls",
                "Add 'bash -x script.sh' for debugging",
                "Check exit code with '$?'",
            ],
        }

    def respond_to_query(self, query: str, context: Union[Dict[str, Any], Context]) -> Dict[str, Any]:
        """
        Respond to shell-related queries with deep domain expertise

        Args:
            query: User query about shell/scripting
            context: Query context (dict or Context object)

        Returns:
            Enhanced response with shell-specific insights
        """
        # Ensure we have a proper Context object
        context = ensure_context(context)

        # Get base response from unified consciousness
        sophia_response = super().respond_to_query(query, context)

        # Convert SophiaResponse to dict for enhancement
        base_response = {
            "message": sophia_response.message,
            "insights": sophia_response.insights.copy(),
            "suggestions": sophia_response.suggestions.copy(),
            "actions": [],
            "confidence": 0.8,  # Default confidence
        }

        # Enhance with shell-specific knowledge
        query_lower = query.lower()

        # Debugging help (check first - more specific)
        if any(word in query_lower for word in ["debug", "error", "not working", "fails"]):
            base_response = self._enhance_debugging_query(query_lower, base_response)

        # Command suggestions
        elif any(word in query_lower for word in ["command", "how to", "find", "search"]):
            base_response = self._enhance_command_query(query_lower, base_response)

        # Script assistance
        elif any(word in query_lower for word in ["script", "bash", "automate"]):
            base_response = self._enhance_script_query(query_lower, base_response)

        # Process management
        elif any(word in query_lower for word in ["process", "kill", "stop", "running"]):
            base_response = self._enhance_process_query(query_lower, base_response)

        # Add shell-specific confidence boost
        if base_response.get("confidence", 0) < 0.9:
            base_response["confidence"] = min(0.95, base_response.get("confidence", 0.8) + 0.1)

        return base_response

    def _enhance_command_query(self, query: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance command-related queries"""
        insights = response.get("insights", [])
        suggestions = response.get("suggestions", [])

        # Find matching command patterns
        for category, commands in self.command_patterns.items():
            for cmd_name, cmd_pattern in commands.items():
                if cmd_name in query:
                    insights.append(
                        f"💻 Shell Expert: Common {cmd_name} usage:\n"
                        f"   {cmd_pattern}"
                    )

                    # Add related commands
                    related = [c for c in commands.keys() if c != cmd_name]
                    if related:
                        suggestions.append(
                            f"Related commands: {', '.join(related[:2])}"
                        )
                    break

        # Add general shell advice
        if "pipe" in query or "|" in query:
            insights.append(
                "⚡ Pro Tip: Pipe commands together for powerful combinations"
            )
            suggestions.append("Example: ps aux | grep firefox | awk '{print $2}'")

        response["insights"] = insights
        response["suggestions"] = suggestions
        return response

    def _enhance_script_query(self, query: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance scripting-related queries"""
        insights = response.get("insights", [])
        suggestions = response.get("suggestions", [])

        insights.append(
            "📝 Shell Scripting Best Practices:"
        )

        suggestions.extend([
            "Always add shebang: #!/bin/bash",
            "Use 'set -e' to exit on error",
            "Quote variables: \"$variable\"",
            "Check arguments: if [ $# -eq 0 ]",
            "Add error handling with trap",
        ])

        # Add script template
        actions = response.get("actions", [])
        actions.append("show_script_template")

        response["insights"] = insights
        response["suggestions"] = suggestions
        response["actions"] = actions
        return response

    def _enhance_debugging_query(self, query: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance debugging-related queries"""
        insights = response.get("insights", [])
        suggestions = response.get("suggestions", [])

        insights.append(
            "🔍 Debugging Techniques:"
        )

        # Add relevant debugging techniques
        if "script" in query:
            suggestions.extend(self.debugging_techniques["script_debugging"])
        else:
            suggestions.extend(self.debugging_techniques["command_debugging"])

        response["insights"] = insights
        response["suggestions"] = suggestions
        return response

    def _enhance_process_query(self, query: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance process management queries"""
        insights = response.get("insights", [])
        suggestions = response.get("suggestions", [])

        insights.append(
            "⚙️ Process Management:"
        )

        suggestions.extend([
            "List processes: ps aux | grep <name>",
            "Kill process: kill -9 <pid>",
            "Background job: <command> &",
            "Foreground job: fg",
            "Monitor processes: top or htop",
        ])

        response["insights"] = insights
        response["suggestions"] = suggestions
        return response

    def get_command_template(self, command: str) -> str:
        """Get command template"""
        for category, commands in self.command_patterns.items():
            if command in commands:
                return commands[command]
        return ""

    def get_script_template(self) -> str:
        """Get basic script template"""
        return """#!/bin/bash
set -e  # Exit on error
set -u  # Exit on undefined variable

# Script description
# Usage: script.sh <arg1> <arg2>

# Check arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <arg>"
    exit 1
fi

# Main logic
main() {
    echo "Running script..."
    # Your code here
}

# Cleanup on exit
cleanup() {
    echo "Cleaning up..."
}
trap cleanup EXIT

# Run main
main "$@"
"""

    def get_expertise_summary(self) -> Dict[str, Any]:
        """Get summary of shell expertise"""
        return {
            "specialization": self.specialization,
            "expertise_domains": self.expertise_domains,
            "command_categories": list(self.command_patterns.keys()),
            "debugging_types": list(self.debugging_techniques.keys()),
            "confidence_in_domain": 0.95,
        }
