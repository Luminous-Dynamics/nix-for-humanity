#!/usr/bin/env python3
"""
Patch script to integrate AI Environment Architect into ask-nix
This adds the ability to detect and handle AI/ML environment requests
"""

import os
import sys
from pathlib import Path

def create_integration_snippet():
    """Create the code snippet to integrate AI environments"""
    
    return '''
        # Check if this is an AI environment request
        if hasattr(self, 'ai_integration') and self.ai_integration.is_environment_request(query):
            # Handle AI environment generation
            print("\\n🤖 AI Environment Architect detected your request!")
            print("Preparing to generate a specialized AI/ML development environment...\\n")
            
            # Get response from AI integration
            response = self.ai_integration.handle_environment_request(query)
            
            # Format and display
            formatted = self.ai_integration.format_response(response, self.personality)
            print(formatted)
            
            # Ask for confirmation
            print()
            confirm = input("📁 Create this environment? [Y/n] ").strip().lower()
            
            if confirm in ['', 'y', 'yes']:
                # Import generator
                from ai_environment_generator import AIEnvironmentGenerator
                generator = AIEnvironmentGenerator()
                
                # Generate files
                success, message = generator.create_environment(response)
                print()
                if success:
                    print(message)
                    
                    # Record success if learning enabled
                    if self.learning_enabled and hasattr(self, 'learning_system'):
                        self.learning_system.record_success(
                            self.current_command_id,
                            f"AI environment created at {response['output_dir']}"
                        )
                else:
                    print(f"❌ {message}")
                    
                    # Record failure if learning enabled
                    if self.learning_enabled and hasattr(self, 'learning_system'):
                        self.learning_system.record_failure(
                            self.current_command_id,
                            message
                        )
            else:
                print("Environment creation cancelled.")
            
            return
'''

def create_import_snippet():
    """Create import statements for AI integration"""
    
    return '''
# Import AI Environment integration
try:
    from ai_environment_integration import AIEnvironmentIntegration
    AI_ENV_AVAILABLE = True
except ImportError:
    AI_ENV_AVAILABLE = False
    print("Warning: AI Environment Architect not available", file=sys.stderr)
'''

def create_init_snippet():
    """Create initialization code for AI integration"""
    
    return '''
        # Initialize AI Environment integration if available
        if AI_ENV_AVAILABLE:
            try:
                self.ai_integration = AIEnvironmentIntegration()
            except Exception as e:
                print(f"Warning: Failed to initialize AI Environment Architect: {e}", file=sys.stderr)
                self.ai_integration = None
        else:
            self.ai_integration = None
'''

def main():
    """Generate integration instructions"""
    
    print("AI Environment Architect Integration Instructions")
    print("=" * 50)
    print()
    print("To integrate AI Environment Architect into ask-nix, add the following:")
    print()
    
    print("1. Add imports near the top of ask-nix (after other imports):")
    print("-" * 40)
    print(create_import_snippet())
    print()
    
    print("2. Add initialization in __init__ method of UnifiedNixAssistant:")
    print("-" * 40)
    print(create_init_snippet())
    print()
    
    print("3. Add this at the beginning of the answer() method (after intent extraction):")
    print("-" * 40)
    print(create_integration_snippet())
    print()
    
    print("4. Update the usage information to include AI environment examples:")
    print("-" * 40)
    print('''
        console.print("  ask-nix 'Create a PyTorch environment with CUDA'")
        console.print("  ask-nix 'Set up Jupyter notebook for ML'")
        console.print("  ask-nix 'I want to run Llama locally'")
''')
    print()
    
    print("5. Test the integration:")
    print("-" * 40)
    print("ask-nix 'Create an AI environment with transformers and CUDA support'")
    print()

if __name__ == "__main__":
    main()