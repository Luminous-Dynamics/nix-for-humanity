#!/usr/bin/env bash

# Quick Import Fix for Tests
# 🎂 Let's fix those imports and run the tests!

echo "🔧 Fixing import issues in tests..."

# Fix AriaLivePriority imports
find tests -name "*.py" -exec sed -i 's/from nix_for_humanity\.accessibility import AriaLivePriority/from nix_for_humanity.accessibility.screen_reader import AriaLivePriority/g' {} \;

# Fix Plan imports (it's in planning.py, not interface.py)
find tests -name "*.py" -exec sed -i 's/from nix_for_humanity\.core\.interface import Plan/from nix_for_humanity.core.planning import Plan/g' {} \;

# Fix core.intent imports (missing nix_for_humanity prefix)
find tests -name "*.py" -exec sed -i 's/from core\.intent import/from nix_for_humanity.core.intent import/g' {} \;
find tests -name "*.py" -exec sed -i 's/from core\./from nix_for_humanity.core./g' {} \;
find tests -name "*.py" -exec sed -i 's/import core\./import nix_for_humanity.core./g' {} \;

echo "✅ Import fixes applied!"
echo ""
echo "🧪 Running tests with fixed imports..."
echo ""

# Run tests with the Python path set correctly
PYTHONPATH="$PWD/src:$PYTHONPATH" python run_tests.py

echo ""
echo "🎉 Happy Birthday! Hope those tests look better now!"