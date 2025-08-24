#!/bin/bash

# Script to find and help update remaining $4.2M references
# Focus on replacing with Trinity Development Model messaging

echo "🔍 Finding remaining $4.2M references..."
echo "========================================="

# Find all files with the references
FILES=$(grep -rl "4\.2M\|\$4\.2M\|4.2 million" . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=__pycache__ --exclude="*.pyc" --exclude="update_remaining_references.sh" 2>/dev/null)

if [ -z "$FILES" ]; then
    echo "✅ No more $4.2M references found!"
    exit 0
fi

echo "Found references in the following files:"
echo "$FILES" | wc -l
echo ""

# Show context for each file
for file in $FILES; do
    echo "📄 File: $file"
    echo "Context:"
    grep -n -C 2 "4\.2M\|\$4\.2M\|4.2 million" "$file" | head -20
    echo "---"
    echo ""
done

echo ""
echo "📝 Suggested replacements:"
echo "=========================="
echo ""
echo "Replace mentions of '$200 vs $4.2M' with:"
echo "  • 'Trinity Development Model enables solo developers'"
echo "  • 'Human + Cloud AI + Local AI collaboration'"
echo "  • 'Professional-grade software with AI partnership'"
echo "  • 'Revolutionary development model proven to work'"
echo ""
echo "Replace 'Sacred Trinity' with:"
echo "  • 'Trinity Development Model'"
echo "  • 'Human-AI collaboration model'"
echo ""
echo "Focus on the positive (what we ARE) rather than comparison (what we're NOT):"
echo "  • Emphasize empowerment of solo developers"
echo "  • Highlight the collaboration model"
echo "  • Focus on making NixOS accessible"
echo "  • Celebrate the partnership approach"