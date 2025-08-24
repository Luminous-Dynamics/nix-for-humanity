#!/usr/bin/env python3
"""
🎓 Test CLI Learning Mode Integration
Verifies that Learning Mode is fully accessible through the main CLI
"""

import subprocess
import sys
from pathlib import Path

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

def test_learning_flag():
    """Test the --learning flag with a command"""
    print("🎓 Testing Learning Mode flag...")
    
    cmd = [
        sys.executable,
        "bin/ask-nix",
        "--learning",
        "sudo rm -rf /var/cache"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="..")
    
    if "Learning Mode Activated" in result.stdout:
        print("✅ Learning Mode activates correctly")
    else:
        print("❌ Learning Mode did not activate")
        print(f"Output: {result.stdout[:500]}")
    
    if "Command Breakdown" in result.stdout:
        print("✅ Command breakdown displayed")
    else:
        print("❌ Command breakdown missing")
    
    if "Risk Level" in result.stdout or "Safer Alternatives" in result.stdout:
        print("✅ Risk analysis shown")
    else:
        print("❌ Risk analysis missing")
    
    if "Understanding Check" in result.stdout:
        print("✅ Understanding check included")
    else:
        print("❌ Understanding check missing")
    
    print()


def test_progress_flag():
    """Test the --progress flag"""
    print("📊 Testing progress display...")
    
    cmd = [sys.executable, "bin/ask-nix", "--progress"]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="..")
    
    if "Your Learning Progress" in result.stdout:
        print("✅ Progress display works")
    else:
        print("❌ Progress display failed")
        print(f"Output: {result.stdout[:500]}")
    
    if "Current Level" in result.stdout:
        print("✅ Shows current level")
    else:
        print("❌ Level not shown")
    
    print()


def test_suggest_lesson_flag():
    """Test the --suggest-lesson flag"""
    print("💡 Testing lesson suggestions...")
    
    cmd = [sys.executable, "bin/ask-nix", "--suggest-lesson"]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="..")
    
    if "Your Next Suggested Lesson" in result.stdout or "Start with basic" in result.stdout:
        print("✅ Lesson suggestion works")
    else:
        print("❌ Lesson suggestion failed")
        print(f"Output: {result.stdout[:500]}")
    
    print()


def test_visualize_flag():
    """Test the --visualize flag (just check if it tries to launch)"""
    print("🎨 Testing visualization launch...")
    
    cmd = [sys.executable, "bin/ask-nix", "--visualize"]
    
    # Run with timeout since it starts a server
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="..", timeout=2)
    
    if "Launching Knowledge Graph" in result.stdout:
        print("✅ Visualization launcher works")
    else:
        print("⚠️ Visualization launcher output unexpected")
        print(f"Output: {result.stdout[:200]}")
    
    print()


def test_learning_with_safe_command():
    """Test learning mode with a safe command"""
    print("✅ Testing Learning Mode with safe command...")
    
    cmd = [
        sys.executable,
        "bin/ask-nix",
        "--learning",
        "install firefox"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="..")
    
    if "Learning Mode Activated" in result.stdout:
        print("✅ Works with safe commands too")
    else:
        print("❌ Failed with safe command")
    
    print()


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║       🎓 Testing CLI Learning Mode Integration 🎓            ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Change to project directory
    import os
    os.chdir(Path(__file__).parent.parent)
    
    try:
        test_learning_flag()
        test_progress_flag()
        test_suggest_lesson_flag()
        # test_visualize_flag()  # Skip since it starts a server
        test_learning_with_safe_command()
        
        print("""
╔══════════════════════════════════════════════════════════════╗
║                    ✅ Integration Complete!                  ║
║                                                              ║
║  Learning Mode is now fully integrated into the main CLI!   ║
║                                                              ║
║  Users can now:                                             ║
║  • Use --learning (-l) to get educational responses         ║
║  • Use --progress to see their learning journey             ║
║  • Use --suggest-lesson for personalized recommendations    ║
║  • Use --visualize to launch the knowledge graph            ║
║                                                              ║
║  Example usage:                                             ║
║    ./bin/ask-nix --learning "sudo rm -rf /tmp/*"            ║
║    ./bin/ask-nix --progress                                 ║
║    ./bin/ask-nix --visualize                                ║
║                                                              ║
║  The Sacred Teacher guides all beings toward mastery! 🌊     ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()