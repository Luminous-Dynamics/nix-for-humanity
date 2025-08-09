#!/usr/bin/env python3
"""
Enable Causal XAI in ask-nix
This script patches the ask-nix command to include causal explanations

Usage:
    python3 enable_xai_in_ask_nix.py
"""

import os
import sys
from pathlib import Path

def create_xai_enabled_wrapper():
    """Create a wrapper that enables XAI in ask-nix"""
    
    wrapper_content = '''#!/usr/bin/env python3
"""
ask-nix with Causal XAI enabled
This wrapper adds causal explanations to the standard ask-nix command
"""

import sys
import os

# Add scripts directory to path
script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
sys.path.insert(0, script_dir)

# Import XAI integration
from causal_xai_integration import create_xai_enhanced_engine

# Import the standard ask-nix components
bin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, bin_dir)

# Patch the ModernNixOSKnowledgeEngine to include XAI
import importlib.util
spec = importlib.util.spec_from_file_location("nix_knowledge_engine_modern", 
    os.path.join(script_dir, "nix-knowledge-engine-modern.py"))
nix_knowledge_engine_modern = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nix_knowledge_engine_modern)

# Create XAI-enhanced version
XAIModernNixOSKnowledgeEngine = create_xai_enhanced_engine(
    nix_knowledge_engine_modern.ModernNixOSKnowledgeEngine,
    enable_xai=True
)

# Monkey-patch the module
nix_knowledge_engine_modern.ModernNixOSKnowledgeEngine = XAIModernNixOSKnowledgeEngine

# Now run the standard ask-nix with XAI enhancements
if __name__ == "__main__":
    # Import and run ask-nix
    spec = importlib.util.spec_from_file_location("ask_nix", 
        os.path.join(bin_dir, "ask-nix"))
    ask_nix = importlib.util.module_from_spec(spec)
    
    # Add command line flag for XAI features
    if '--explain' in sys.argv:
        sys.argv.remove('--explain')
        os.environ['NIX_HUMANITY_XAI_EXPLAIN'] = 'detailed'
    elif '--why' in sys.argv:
        sys.argv.remove('--why')
        os.environ['NIX_HUMANITY_XAI_EXPLAIN'] = 'simple'
    
    spec.loader.exec_module(ask_nix)
'''
    
    # Write the wrapper
    wrapper_path = Path(__file__).parent.parent / 'bin' / 'ask-nix-xai'
    wrapper_path.write_text(wrapper_content)
    wrapper_path.chmod(0o755)
    
    print(f"✅ Created XAI-enabled wrapper at: {wrapper_path}")
    return wrapper_path

def add_xai_flags_to_help():
    """Add XAI-specific flags to the help system"""
    
    help_addition = """
    
## Causal Explanation Options

    --why               Show simple explanation of why this command is suggested
    --explain          Show detailed causal explanation with confidence scores
    --explain-error    Explain why an error occurred and how to fix it
    
Examples:
    ask-nix --why "install firefox"
    ask-nix --explain "update my system"
"""
    
    print("📝 XAI help flags to add to documentation:")
    print(help_addition)

def create_demo_script():
    """Create a demo script showing XAI features"""
    
    demo_content = '''#!/usr/bin/env python3
"""
Demo of Causal XAI features in Nix for Humanity
"""

import subprocess
import sys
import os

print("🧠 Causal XAI Demo for Nix for Humanity")
print("=" * 50)

demos = [
    {
        'title': 'Simple Why Explanation',
        'command': ['ask-nix-xai', '--why', 'install firefox'],
        'description': 'Get a quick explanation of why a command is suggested'
    },
    {
        'title': 'Detailed Causal Explanation',
        'command': ['ask-nix-xai', '--explain', 'update my system'],
        'description': 'See detailed reasoning with confidence scores'
    },
    {
        'title': 'Technical Explanation',
        'command': ['ask-nix-xai', '--explain', '--technical', 'remove unused packages'],
        'description': 'Get technical details including causal graphs'
    },
    {
        'title': 'Error Explanation',
        'command': ['ask-nix-xai', '--dry-run', 'install nonexistent-package'],
        'description': 'Understand why errors occur and how to fix them'
    }
]

for demo in demos:
    print(f"\\n📋 {demo['title']}")
    print(f"   {demo['description']}")
    print(f"\\n   Command: {' '.join(demo['command'])}")
    print("   " + "-" * 40)
    
    try:
        # Run the command
        result = subprocess.run(
            demo['command'], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        
        # Show output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"   ⚠️ Error: {result.stderr}", file=sys.stderr)
            
    except subprocess.TimeoutExpired:
        print("   ⏱️ Command timed out")
    except Exception as e:
        print(f"   ❌ Error running demo: {e}")
    
    input("\\nPress Enter to continue...")

print("\\n✅ Demo complete!")
print("\\nTo use XAI in your daily workflow:")
print("  • Add --why for quick explanations")
print("  • Add --explain for detailed reasoning")
print("  • The AI will explain its confidence and reasoning")
'''
    
    demo_path = Path(__file__).parent.parent / 'scripts' / 'demo' / 'demo-causal-xai.py'
    demo_path.parent.mkdir(exist_ok=True)
    demo_path.write_text(demo_content)
    demo_path.chmod(0o755)
    
    print(f"✅ Created demo script at: {demo_path}")
    return demo_path

def main():
    """Main function to enable XAI in ask-nix"""
    
    print("🧠 Enabling Causal XAI in Nix for Humanity")
    print("=" * 50)
    
    # Check if we're in the right directory
    base_path = Path(__file__).parent.parent
    if not (base_path / 'bin' / 'ask-nix').exists():
        print("❌ Error: Could not find ask-nix. Are you in the right directory?")
        return 1
    
    # Create XAI-enabled wrapper
    print("\n1️⃣ Creating XAI-enabled wrapper...")
    wrapper_path = create_xai_enabled_wrapper()
    
    # Add help documentation
    print("\n2️⃣ Documentation additions...")
    add_xai_flags_to_help()
    
    # Create demo script
    print("\n3️⃣ Creating demo script...")
    demo_path = create_demo_script()
    
    print("\n✅ Causal XAI successfully enabled!")
    print("\nTo use XAI features:")
    print(f"  1. Run: {wrapper_path} --why 'install firefox'")
    print(f"  2. Or: {wrapper_path} --explain 'update my system'")
    print(f"  3. Try the demo: python3 {demo_path}")
    
    print("\n💡 The XAI system provides:")
    print("  • Why explanations for every action")
    print("  • Confidence scores for recommendations")
    print("  • Multiple explanation depths")
    print("  • Error understanding and recovery")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())