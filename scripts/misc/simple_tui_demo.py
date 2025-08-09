#!/usr/bin/env python3
"""
Simple TUI Demo for Nix for Humanity
Demonstrates the core TUI architecture without complex dependencies
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

# Simple colored output for terminal
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(text, color=Colors.END):
    print(f"{color}{text}{Colors.END}")

def print_header():
    print_colored("🌟 Nix for Humanity - Beautiful TUI Demo", Colors.BOLD + Colors.CYAN)
    print_colored("════════════════════════════════════════", Colors.CYAN)
    print_colored("Where consciousness meets computation", Colors.YELLOW)
    print()

def print_help():
    print_colored("\n📚 Available Commands:", Colors.BOLD)
    print("  • Type naturally: 'install firefox', 'update system', 'help me'")
    print("  • Commands: help, quit, status, demo")
    print("  • Press Enter to send, Ctrl+C to quit")
    print()

def process_query(query: str) -> dict:
    """Process user query through mock backend"""
    query = query.strip().lower()
    
    if query in ['quit', 'exit', 'q']:
        return {'action': 'quit'}
    
    elif query in ['help', 'h', '?']:
        return {
            'action': 'help',
            'response': 'I can help you with NixOS management through natural conversation!'
        }
        
    elif query in ['status', 'info']:
        return {
            'action': 'info',
            'response': 'System: NixOS 25.11 | Python Backend: Active | TUI: Demo Mode',
            'details': {
                'generation': 42,
                'flakes': 'enabled',
                'native_api': True
            }
        }
        
    elif query == 'demo':
        return {
            'action': 'demo',
            'response': 'This demonstrates the TUI architecture without full dependencies',
            'features': [
                '🎨 Beautiful terminal interface',
                '💬 Natural language processing',
                '🔒 100% local operation',
                '♿ Accessibility-first design',
                '🚀 10x faster with native Python-Nix'
            ]
        }
        
    elif 'install' in query:
        package = query.replace('install', '').strip()
        return {
            'action': 'install',
            'package': package or 'firefox',
            'response': f'I would install {package or "firefox"} for you.',
            'command': f'nix-env -iA nixos.{package or "firefox"}',
            'requires_confirmation': True
        }
        
    elif 'update' in query:
        return {
            'action': 'update',
            'response': 'I would update your system safely.',
            'command': 'sudo nixos-rebuild switch',
            'requires_confirmation': True
        }
        
    else:
        return {
            'action': 'unknown',
            'response': f'I understand you want help with: "{query}". In the full version, I would process this naturally!'
        }

def show_conversation_message(text: str, is_user: bool = True):
    """Display a conversation message with proper formatting"""
    timestamp = datetime.now().strftime("%H:%M")
    
    if is_user:
        print_colored(f"[{timestamp}] → You: {text}", Colors.BOLD)
    else:
        print_colored(f"[{timestamp}] ← Nix: {text}", Colors.GREEN)

def show_command_preview(result: dict):
    """Show command preview with confirmation"""
    if result.get('command'):
        print_colored("\n📋 Command Preview:", Colors.YELLOW)
        print_colored(f"   {result['command']}", Colors.BOLD)
        
        if result.get('requires_confirmation'):
            print_colored("⚠️  This action requires confirmation", Colors.YELLOW)
            
        response = input("\n✨ Execute this command? [y/N]: ").strip().lower()
        if response in ['y', 'yes']:
            print_colored("✅ In full version, this would execute safely!", Colors.GREEN)
        else:
            print_colored("❌ Command cancelled", Colors.RED)
        print()

def main():
    """Main TUI loop"""
    print_header()
    print_help()
    
    # Show welcome message
    show_conversation_message(
        "👋 Welcome! I'm your AI partner for NixOS. What would you like to do?", 
        is_user=False
    )
    
    while True:
        try:
            # Get user input
            user_input = input(f"\n{Colors.CYAN}✨ Ask me anything: {Colors.END}").strip()
            
            if not user_input:
                continue
                
            # Show user message
            show_conversation_message(user_input, is_user=True)
            
            # Process query
            result = process_query(user_input)
            
            # Handle result
            if result['action'] == 'quit':
                print_colored("\n✨ Thank you for using Nix for Humanity!", Colors.GREEN)
                print_colored("🌊 We flow with gratitude.", Colors.CYAN)
                break
                
            elif result['action'] == 'help':
                show_conversation_message(result['response'], is_user=False)
                print_help()
                
            elif result['action'] == 'info':
                show_conversation_message(result['response'], is_user=False)
                if result.get('details'):
                    print_colored("📊 System Details:", Colors.YELLOW)
                    for key, value in result['details'].items():
                        print(f"   {key}: {value}")
                    
            elif result['action'] == 'demo':
                show_conversation_message(result['response'], is_user=False)
                print_colored("\n🎨 TUI Features:", Colors.YELLOW)
                for feature in result['features']:
                    print(f"   {feature}")
                    
            elif result['action'] in ['install', 'update']:
                show_conversation_message(result['response'], is_user=False)
                show_command_preview(result)
                
            else:
                show_conversation_message(result['response'], is_user=False)
                
        except KeyboardInterrupt:
            print_colored("\n\n✨ Thank you for using Nix for Humanity!", Colors.GREEN)
            print_colored("🌊 We flow with gratitude.", Colors.CYAN)
            break
        except Exception as e:
            print_colored(f"\n❌ An error occurred: {e}", Colors.RED)
            print_colored("Please try again or type 'help' for assistance.", Colors.YELLOW)

if __name__ == "__main__":
    main()