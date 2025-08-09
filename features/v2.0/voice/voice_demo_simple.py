#!/usr/bin/env python3
"""
from typing import Dict
Simple Voice Interface Demo for Grandma Rose
===========================================

A lightweight demo that simulates voice interaction without requiring
Whisper or audio hardware. Perfect for testing the interface design
and user experience.
"""

import time
import sys
import os
from typing import Dict, Any
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nix_knowledge_engine import NixOSKnowledgeEngine


class SimpleVoiceDemo:
    """Simulated voice interface for testing Grandma Rose experience"""
    
    def __init__(self):
        self.nix_engine = NixOSKnowledgeEngine()
        self.command_history = []
        
    def show_visual_feedback(self, message: str, type: str = "info"):
        """Display large, clear visual feedback"""
        border = "=" * 60
        
        if type == "listening":
            symbol = "🎤"
            color = "\033[92m"  # Green
        elif type == "processing":
            symbol = "⏳"
            color = "\033[93m"  # Yellow
        elif type == "success":
            symbol = "✅"
            color = "\033[92m"  # Green
        elif type == "error":
            symbol = "❌"
            color = "\033[91m"  # Red
        elif type == "speaking":
            symbol = "🔊"
            color = "\033[96m"  # Cyan
        else:
            symbol = "ℹ️"
            color = "\033[94m"  # Blue
        
        print(f"\n{color}{border}")
        print(f"{symbol}  {message.upper()}")
        print(f"{border}\033[0m\n")
    
    def simulate_speak(self, text: str):
        """Simulate TTS with visual feedback"""
        self.show_visual_feedback("SPEAKING", "speaking")
        
        # Show text in chunks to simulate speech
        words = text.split()
        line = ""
        for i, word in enumerate(words):
            line += word + " "
            if len(line) > 50 or i == len(words) - 1:
                print(f"    🔊 {line}")
                time.sleep(0.5)  # Simulate speech timing
                line = ""
        print()
    
    def simulate_listening(self) -> str:
        """Simulate voice input with typed text"""
        self.show_visual_feedback("LISTENING - PLEASE SPEAK", "listening")
        print("    🎤 (In real version, I would be listening to your voice)")
        print("    💡 Type what you want to say and press ENTER:\n")
        
        # Get input with prompt
        user_input = input("    You: ").strip()
        
        if user_input:
            self.show_visual_feedback(f"I HEARD: {user_input}", "success")
        
        return user_input
    
    def make_grandma_friendly(self, response: str, intent: Dict) -> str:
        """Convert technical response to grandma-friendly language"""
        if intent.get('action') == 'install_package':
            package = intent.get('package', 'that program')
            
            # Check if it's a common program grandma would know
            friendly_names = {
                'firefox': 'Firefox web browser',
                'chrome': 'Google Chrome browser',
                'google-chrome': 'Google Chrome browser',
                'zoom': 'Zoom for video calls',
                'skype': 'Skype for video calls',
                'vlc': 'VLC media player for videos',
                'libreoffice': 'LibreOffice for documents'
            }
            
            friendly_name = friendly_names.get(package, package)
            
            return (f"I'll help you get {friendly_name} on your computer! 🌟\n\n"
                   f"Here's what I'll do for you:\n\n"
                   f"1. 📥 Download {friendly_name} safely\n"
                   f"2. 🔧 Install it properly on your computer\n"
                   f"3. 📱 Put an icon on your desktop\n\n"
                   f"This will take about 2-3 minutes.\n"
                   f"Would you like me to do this now? (Say 'yes' or 'no')")
            
        elif intent.get('action') == 'update_system':
            return ("I'll update your computer to keep it safe and running smoothly! 🛡️\n\n"
                   "Think of it like getting a check-up at the doctor:\n\n"
                   "• 🏥 I'll check for security updates (like vaccines!)\n"
                   "• 🔧 Fix any small problems\n" 
                   "• ✨ Make sure everything runs nicely\n\n"
                   "This usually takes 5-10 minutes.\n"
                   "Your computer might restart when it's done.\n\n"
                   "Shall I start the update now?")
                   
        elif intent.get('action') == 'fix_wifi':
            return ("Oh no! Let's get your internet working again! 🌐\n\n"
                   "I'll help you step by step:\n\n"
                   "1. 📡 First, I'll check if your WiFi is turned on\n"
                   "2. 🔍 Then look for your home network\n"
                   "3. 🔑 Help you connect with your password\n\n"
                   "Most of the time, this fixes the problem!\n"
                   "Ready to start?")
        
        elif intent.get('action') == 'search_package':
            return ("I'll help you find programs on your computer! 🔍\n\n"
                   "Just tell me:\n"
                   "• What kind of program you need\n" 
                   "• What you want to do with it\n\n"
                   "For example:\n"
                   "- 'I need to video call my grandchildren'\n"
                   "- 'I want to look at my photos'\n"
                   "- 'I need to write a letter'\n\n"
                   "What would you like to do?")
        
        # Default response
        return response
    
    def process_command(self, text: str) -> Dict[str, Any]:
        """Process command with grandma-friendly responses"""
        # Handle common grandma phrases
        grandma_translations = {
            "open the internet": "install firefox",
            "get on the web": "install firefox", 
            "check my email": "install firefox",
            "video call": "install zoom",
            "call my grandkids": "install zoom",
            "watch videos": "install vlc",
            "write a letter": "install libreoffice",
            "my internet isn't working": "fix wifi",
            "can't get online": "fix wifi",
            "update computer": "update system"
        }
        
        # Translate grandma speak to commands
        lower_text = text.lower()
        for phrase, command in grandma_translations.items():
            if phrase in lower_text:
                text = command
                break
        
        # Process through NixOS engine
        intent = self.nix_engine.extract_intent(text)
        solution = self.nix_engine.get_solution(intent)
        response = self.nix_engine.format_response(intent, solution)
        
        # Make it grandma-friendly
        friendly_response = self.make_grandma_friendly(response, intent)
        
        return {
            "original": text,
            "intent": intent,
            "response": friendly_response,
            "success": solution.get('found', False)
        }
    
    def show_common_commands(self):
        """Show helpful examples for Grandma"""
        examples = """
    📚 Here are some things you can ask me:
    
    🌐 Internet & Email:
       • "I need to check my email"
       • "Open the internet"
       • "My internet isn't working"
    
    📞 Video Calls:
       • "I want to video call my grandkids"
       • "Set up Zoom"
       • "Help me with Skype"
    
    📷 Photos & Videos:
       • "I want to look at my photos"
       • "Play my videos"
       • "Open my pictures"
    
    ✍️ Writing:
       • "I need to write a letter"
       • "Open a document"
    
    🔧 Computer Care:
       • "Update my computer"
       • "Is my computer safe?"
       • "Fix my WiFi"
    
    Just speak naturally - I'll understand! 😊
        """
        print(examples)
    
    def run_demo(self):
        """Run the interactive demo"""
        print("""
    👵 Welcome to Grandma Rose's Computer Helper! 
    =============================================
    
    I'm here to help you with your computer in simple, 
    friendly language. No technical jargon - I promise!
        """)
        
        self.simulate_speak("Hello! I'm your computer helper. I'm here to make using your computer easy and fun!")
        
        # Show examples
        self.show_common_commands()
        
        try:
            while True:
                # Simulate wake word
                print("\n" + "="*60)
                print("💡 Say 'Hello Computer' to start (or press ENTER)")
                print("   Type 'help' to see examples again")
                print("   Type 'goodbye' to exit")
                print("="*60)
                
                wake = input("\n> ").strip().lower()
                
                if wake == 'goodbye':
                    self.simulate_speak("Goodbye! Remember, I'm always here when you need help. Take care!")
                    break
                elif wake == 'help':
                    self.show_common_commands()
                    continue
                
                # Get voice command
                command = self.simulate_listening()
                
                if command:
                    # Process it
                    self.show_visual_feedback("THINKING ABOUT YOUR REQUEST", "processing")
                    time.sleep(1)  # Simulate processing
                    
                    result = self.process_command(command)
                    
                    # Speak response
                    self.simulate_speak(result['response'])
                    
                    # Log for learning
                    self.command_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "input": command,
                        "intent": result['intent'],
                        "success": result['success']
                    })
                    
                    # Handle follow-up
                    if "Would you like me to" in result['response'] or "Shall I" in result['response']:
                        print("\n    💬 (Say 'yes' to continue or 'no' to cancel)")
                        response = input("    You: ").strip().lower()
                        
                        if response in ['yes', 'yeah', 'sure', 'ok', 'okay', 'please']:
                            self.simulate_speak("Great! I'll take care of that for you right away.")
                            self.show_visual_feedback("WORKING ON IT", "processing")
                            time.sleep(2)
                            self.show_visual_feedback("ALL DONE!", "success")
                            self.simulate_speak("All finished! Your computer is ready to use.")
                        else:
                            self.simulate_speak("No problem! Just let me know when you're ready.")
                
        except KeyboardInterrupt:
            print("\n")
            self.simulate_speak("Goodbye! Take care!")
        
        print(f"\n📝 Processed {len(self.command_history)} commands this session")


def main():
    """Run the demo"""
    demo = SimpleVoiceDemo()
    demo.run_demo()


if __name__ == "__main__":
    main()