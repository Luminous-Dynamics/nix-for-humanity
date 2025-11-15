#!/usr/bin/env bash

# Cleanup old confusing releases to maintain clean release history
# Keep only the momentum strategy releases

echo "🧹 Cleaning up old releases..."
echo "================================"

# List of releases to keep (our momentum strategy)
KEEP_RELEASES="v0.3.1"

# List of releases to delete (old development iterations)
DELETE_RELEASES="v0.5.3 v0.5.2 v0.5.1 v0.5.0 v0.4.1 v0.4.0 v0.3.0 v0.2.2 v0.2.1 v0.2.0"

echo "Releases to delete:"
for release in $DELETE_RELEASES; do
    echo "  - $release"
done

echo ""
echo "Releases to keep:"
echo "  - v0.3.1 (latest with neural networks)"

echo ""
read -p "Are you sure you want to delete these old releases? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    for release in $DELETE_RELEASES; do
        echo "Deleting $release..."
        gh release delete "$release" --yes 2>/dev/null || echo "  Already deleted or not found"
    done
    echo "✅ Old releases cleaned up!"
else
    echo "❌ Cleanup cancelled"
fi

echo ""
echo "Current releases:"
gh release list | head -5
