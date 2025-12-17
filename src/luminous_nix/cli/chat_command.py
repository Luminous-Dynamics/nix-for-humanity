"""
Chat command - Interactive AI assistant with full context awareness
"""

import click
from rich.console import Console

console = Console()


@click.command()
def chat():
    """
    Start an interactive chat session with the Luminous Nix AI assistant.

    The AI has complete context awareness including:
    \\b
    - Your NixOS configuration and system state
    - Your skill level and preferences (auto-detected)
    - Conversation history for multi-turn dialogues
    - System information (hardware, services, packages)

    \\b
    Use natural language to:
    - Ask questions about NixOS
    - Get help with errors
    - Generate configurations
    - Find and install packages
    - Learn NixOS concepts

    \\b
    Special commands:
    - /help       - Show available commands
    - /context    - View system and user context
    - /skill      - View/set your skill level
    - /flakes     - Toggle flake recommendations
    - /history    - View conversation history
    - /status     - Show AI component status
    - /clear      - Clear conversation history
    - exit        - Quit chat mode

    \\b
    Examples:
      $ ask-nix chat

      You: error: attribute 'vim' missing
      AI: [analyzes error and provides solution]

      You: setup nginx with SSL for example.com
      AI: [generates complete nginx config]

      You: what's the best text editor?
      AI: [recommends packages based on your preferences]

    The AI adapts its responses to your skill level:
    - Beginners get detailed explanations
    - Experts get concise, technical responses
    - Automatic skill detection based on your success rate
    """
    try:
        from ..ai.conversation.simple_chat import SimpleChat
        chat = SimpleChat()
        chat.chat_loop()
    except ImportError as e:
        console.print(f"[bold red]Error:[/bold red] Could not load chat system: {e}")
        console.print("\n[yellow]Make sure all dependencies are installed:[/yellow]")
        console.print("  poetry install")
        return 1
    except KeyboardInterrupt:
        console.print("\n[cyan]Chat interrupted. Goodbye![/cyan]")
        return 0
    except Exception as e:
        # Escape markup in error message to avoid rich formatting issues
        error_msg = str(e).replace("[", "\\[").replace("]", "\\]")
        console.print(f"[bold red]Error:[/bold red] {error_msg}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    chat()
