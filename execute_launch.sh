#!/bin/bash
# Execute the full launch sequence for Luminous Nix v0.3.0

set -e

echo "🚀 LAUNCHING LUMINOUS NIX v0.3.0"
echo "=================================="
echo "Time: $(date)"
echo ""

# Step 1: Final build verification
echo "📦 Step 1: Verifying builds..."
if [ -f "dist/luminous_nix-0.3.0-py3-none-any.whl" ] && \
   [ -f "dist-standalone/luminous-nix-v0.3.0-standalone.tar.gz" ]; then
    echo "✅ All packages verified"
else
    echo "❌ Missing packages! Run build scripts first."
    exit 1
fi

# Step 2: Create GitHub release (draft first)
echo ""
echo "📝 Step 2: Creating GitHub release..."
echo "Note: This will create a DRAFT release for review"

# Check if tag exists
if git rev-parse v0.3.0 >/dev/null 2>&1; then
    echo "Tag v0.3.0 already exists"
else
    echo "Creating tag v0.3.0..."
    git tag -a v0.3.0 -m "Release v0.3.0: Neural Networks Meet NixOS - 96.3% accuracy achieved"
fi

# Create release with gh CLI
if command -v gh &> /dev/null; then
    echo "Creating GitHub release..."
    # Note: This creates a draft - needs manual publish
    echo "gh release create v0.3.0 --draft --title 'v0.3.0: Neural Networks Meet NixOS' --notes-file RELEASE_ANNOUNCEMENT_V030.md"
    echo "📌 Run this command manually after reviewing"
else
    echo "⚠️  GitHub CLI not installed. Install with: nix-shell -p gh"
fi

# Step 3: PyPI upload preparation
echo ""
echo "📤 Step 3: PyPI Upload Preparation"
echo "Commands to run:"
echo ""
echo "# Test on TestPyPI first:"
echo "twine upload --repository testpypi dist/luminous_nix-0.3.0*"
echo ""
echo "# Then upload to PyPI:"
echo "twine upload dist/luminous_nix-0.3.0*"
echo ""
echo "📌 Note: Requires PyPI account and API token"

# Step 4: Social media launch checklist
echo ""
echo "📢 Step 4: Social Media Launch Checklist"
echo ""
echo "[ ] HackerNews (9am EST optimal):"
echo "    Title: Show HN: 96% accurate natural language for NixOS using neural networks"
echo "    URL: https://github.com/Luminous-Dynamics/luminous-nix"
echo ""
echo "[ ] Reddit r/NixOS:"
echo "    Title: [Release] Luminous Nix v0.3.0 - Natural language interface with 96% accuracy"
echo "    Post: See HACKERNEWS_SUBMISSION_v030.md"
echo ""
echo "[ ] Twitter/X Thread:"
echo "    Start with: '🚀 Just shipped Luminous Nix v0.3.0!'"
echo "    Thread: See HACKERNEWS_SUBMISSION_v030.md"
echo ""
echo "[ ] LinkedIn Post:"
echo "    Professional announcement"
echo "    See HACKERNEWS_SUBMISSION_v030.md"

# Step 5: Start monitoring
echo ""
echo "📊 Step 5: Starting Monitoring"
echo "Run in separate terminal:"
echo "  python monitoring_dashboard.py"
echo ""
echo "Also monitor:"
echo "  - GitHub notifications"
echo "  - PyPI download stats"
echo "  - HackerNews comments"
echo "  - Reddit responses"

# Step 6: Prepare for feedback
echo ""
echo "📝 Step 6: Feedback Collection Ready"
echo "Run feedback collector:"
echo "  python feedback_collection_system.py"
echo ""
echo "Track issues at:"
echo "  https://github.com/Luminous-Dynamics/luminous-nix/issues"

# Create launch tracking file
cat > launch_status.json << EOF
{
  "version": "0.3.0",
  "launch_time": "$(date -Iseconds)",
  "packages": {
    "pypi": "ready",
    "standalone": "ready",
    "nixpkgs": "ready"
  },
  "social": {
    "hackernews": "pending",
    "reddit": "pending",
    "twitter": "pending",
    "linkedin": "pending"
  },
  "metrics": {
    "github_stars_at_launch": 0,
    "pypi_downloads_at_launch": 0
  }
}
EOF

echo ""
echo "✅ Launch checklist created: launch_status.json"
echo ""
echo "🎯 READY TO LAUNCH!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Review and publish GitHub release"
echo "2. Upload to PyPI"
echo "3. Post to social media"
echo "4. Monitor feedback"
echo "5. Prepare v0.3.1 fixes"
