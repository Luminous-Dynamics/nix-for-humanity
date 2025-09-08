#!/bin/sh
# Consolidate all archive directories into one

set -e

echo "📦 Consolidating Archive Directories"
echo "===================================="

# Create consolidated archive
CONSOLIDATED=".archive-consolidated-2025-01-26"
mkdir -p "$CONSOLIDATED"

# List all archive directories
echo "Found archive directories:"
for dir in .archive-*; do
    if [ -d "$dir" ] && [ "$dir" != "$CONSOLIDATED" ]; then
        echo "  - $dir ($(du -sh "$dir" | cut -f1))"
    fi
done

echo ""
echo "Moving all archives to $CONSOLIDATED..."

# Move everything to consolidated archive
for dir in .archive-*; do
    if [ -d "$dir" ] && [ "$dir" != "$CONSOLIDATED" ]; then
        # Create subdirectory with date from original name
        SUBDIR=$(echo "$dir" | sed 's/^\.archive-//')
        mkdir -p "$CONSOLIDATED/$SUBDIR"
        
        # Move contents
        if [ "$(ls -A $dir)" ]; then
            mv "$dir"/* "$CONSOLIDATED/$SUBDIR/" 2>/dev/null || true
        fi
        
        # Remove empty directory
        rmdir "$dir" 2>/dev/null || true
        echo "  ✓ Consolidated $dir"
    fi
done

# Create index file
echo ""
echo "📝 Creating archive index..."
cat > "$CONSOLIDATED/ARCHIVE_INDEX.md" << 'EOF'
# Luminous Nix Archive Index

This consolidated archive contains all historical files from the project cleanup performed on 2025-01-26.

## Archive Directories

EOF

# Add directory listing to index
for subdir in "$CONSOLIDATED"/*; do
    if [ -d "$subdir" ]; then
        dirname=$(basename "$subdir")
        filecount=$(find "$subdir" -type f | wc -l)
        dirsize=$(du -sh "$subdir" | cut -f1)
        echo "- **$dirname**: $filecount files ($dirsize)" >> "$CONSOLIDATED/ARCHIVE_INDEX.md"
    fi
done

# Add retrieval instructions
cat >> "$CONSOLIDATED/ARCHIVE_INDEX.md" << 'EOF'

## Retrieval Instructions

To restore any archived file:

```bash
# View archive contents
ls .archive-consolidated-2025-01-26/

# Restore a specific directory
cp -r .archive-consolidated-2025-01-26/[directory]/* .

# Search for a specific file
find .archive-consolidated-2025-01-26 -name "[filename]"
```

## Archive Purpose

These files were archived during the project simplification initiative to:
1. Reduce project complexity from 600+ Python files to core essentials
2. Remove experimental and duplicate code
3. Consolidate multiple build strategies
4. Clean up test infrastructure

Files can be restored if needed but should be carefully evaluated before reintroduction.
EOF

# Final statistics
echo ""
echo "📊 Consolidation Complete:"
echo "--------------------------"
TOTAL_FILES=$(find "$CONSOLIDATED" -type f | wc -l)
TOTAL_SIZE=$(du -sh "$CONSOLIDATED" | cut -f1)
echo "Total archived files: $TOTAL_FILES"
echo "Total archive size: $TOTAL_SIZE"

echo ""
echo "✅ All archives consolidated into: $CONSOLIDATED"
echo "📝 Index created at: $CONSOLIDATED/ARCHIVE_INDEX.md"