#!/bin/bash
# Discord Setup Launcher - One command to run everything!

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          🌟 LUMINOUS NIX DISCORD SETUP LAUNCHER 🌟           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "This script will set up your Discord server for launch!"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    exit 1
fi

# Install required packages if needed
echo "📦 Checking dependencies..."
pip3 install --quiet pyperclip 2>/dev/null || pip install --quiet pyperclip 2>/dev/null

# Choose setup method
echo ""
echo "Choose your setup method:"
echo "1) Instant Setup (copies to clipboard step-by-step)"
echo "2) Browser Automation (automates clicking)"
echo "3) API Creator (uses Discord API)"
echo "4) Just show me the web guide"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo "🚀 Launching Instant Setup..."
        python3 discord_instant_setup.py
        ;;
    2)
        echo "🤖 Launching Browser Automation..."
        echo "Installing Selenium..."
        pip3 install selenium webdriver-manager
        python3 discord_browser_automation.py
        ;;
    3)
        echo "🔧 Launching API Creator..."
        python3 discord_api_creator.py
        ;;
    4)
        echo "🌐 Opening web guide..."
        if command -v xdg-open &> /dev/null; then
            xdg-open discord_web_creator.html
        elif command -v open &> /dev/null; then
            open discord_web_creator.html
        else
            echo "Please open discord_web_creator.html in your browser"
        fi
        ;;
    *)
        echo "Invalid choice. Running Instant Setup by default..."
        python3 discord_instant_setup.py
        ;;
esac

echo ""
echo "✅ Setup launcher complete!"
echo ""
echo "If you need help, all content is saved in text files:"
echo "  - discord_welcome_content.txt"
echo "  - discord_rules_content.txt"
echo "  - discord_announcements_content.txt"
echo "  - discord_invite.txt (after setup)"