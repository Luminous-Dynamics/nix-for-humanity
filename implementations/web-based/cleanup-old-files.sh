#!/bin/bash

echo "🧹 Cleaning up old files from Nix for Humanity..."

# Remove old TypeScript files that have been replaced
echo "Removing replaced TypeScript files..."
rm -f js/nlp/nix-wrapper.ts js/nlp/nix-wrapper.js js/nlp/nix-wrapper.js.map js/nlp/nix-wrapper.d.ts
rm -f js/nlp/intent-engine.ts js/nlp/intent-engine.js js/nlp/intent-engine.js.map js/nlp/intent-engine.d.ts

# Remove other replaced files
echo "Removing other replaced files..."
rm -f js/nlp/intent-patterns.ts js/nlp/intent-patterns.js js/nlp/intent-patterns.js.map js/nlp/intent-patterns.d.ts
rm -f js/nlp/ambiguity-resolver.ts js/nlp/ambiguity-resolver.js js/nlp/ambiguity-resolver.js.map js/nlp/ambiguity-resolver.d.ts
rm -f js/nlp/error-recovery.ts js/nlp/error-recovery.js js/nlp/error-recovery.js.map js/nlp/error-recovery.d.ts
rm -f js/nlp/learning-engine.ts js/nlp/learning-engine.js js/nlp/learning-engine.js.map js/nlp/learning-engine.d.ts
rm -f js/nlp/safety-validator.ts js/nlp/safety-validator.js js/nlp/safety-validator.js.map js/nlp/safety-validator.d.ts
rm -f js/nlp/service-normalizer.ts js/nlp/service-normalizer.js js/nlp/service-normalizer.js.map js/nlp/service-normalizer.d.ts
rm -f js/nlp/typo-corrector.ts js/nlp/typo-corrector.js js/nlp/typo-corrector.js.map js/nlp/typo-corrector.d.ts
rm -f js/nlp/unsupported-handler.ts js/nlp/unsupported-handler.js js/nlp/unsupported-handler.js.map js/nlp/unsupported-handler.d.ts
rm -f js/nlp/voice-interface.ts js/nlp/voice-interface.js js/nlp/voice-interface.js.map js/nlp/voice-interface.d.ts
rm -f js/nlp/websocket-client.ts js/nlp/websocket-client.js js/nlp/websocket-client.js.map js/nlp/websocket-client.d.ts
rm -f js/nlp/test-intents.ts js/nlp/test-intents.js js/nlp/test-intents.js.map js/nlp/test-intents.d.ts

# Remove old dist-cjs directory (will be regenerated)
echo "Removing old dist-cjs directory..."
rm -rf js/nlp/dist-cjs/

# Remove demo files (too many)
echo "Removing demo files..."
rm -f demo-*.html

# Remove old test files
echo "Removing old test html files..."
rm -f test-*.html
# Keep our new test-simple.html
git checkout test-simple.html 2>/dev/null || echo "test-simple.html is new"

# Remove old start scripts
echo "Removing old start scripts..."
rm -f start-demo*.sh
rm -f start-nixos-gui.sh
rm -f start-real.sh

# Remove backend directory (replaced by layered architecture)
echo "Removing old backend directory..."
rm -rf backend/

# Remove system-helper (will reimplement if needed)
echo "Removing system-helper directory..."
rm -rf system-helper/

# Remove old HTML files
echo "Removing old HTML files..."
rm -f nix-humanity-*.html
rm -f nix-for-humanity-demo.html
rm -f login*.html
rm -f dashboard-simple.html
rm -f system-dashboard.html
rm -f plugin-manager.html

# Clean up root directory files
echo "Cleaning up root files..."
rm -f DAY*.md
rm -f IMPLEMENTATION_SUMMARY.md
rm -f NIX_FOR_HUMANITY.md  # Old version

# Remove generated JS/map files from dist directories
echo "Cleaning dist directories..."
rm -rf dist/
rm -rf dist-cjs/

# Clean up webpack and old build files
echo "Removing old build configurations..."
rm -f webpack.config.js
rm -f babel.config.js
rm -f postcss.config.js

# Summary
echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Remaining structure:"
echo "- js/nlp/layers/     (pure function layers)"
echo "- js/nlp/*.ts        (new refactored modules)"
echo "- js/ui/             (minimal interface)"
echo "- docs/              (documentation)"
echo "- tests/             (test files)"
echo ""
echo "To rebuild:"
echo "  npm run build"
echo ""