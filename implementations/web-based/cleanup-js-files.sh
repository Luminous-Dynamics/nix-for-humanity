#!/bin/sh

echo "🧹 Cleaning up old JavaScript files..."

# Remove old JS files that aren't part of the new architecture
echo "Removing old JavaScript files from js/ directory..."

# Core old files
rm -f js/admin-bundle.js
rm -f js/api.js
rm -f js/app.js
rm -f js/core.js
rm -f js/engine.js
rm -f js/dashboard.js
rm -f js/audit-dashboard.js
rm -f js/config.js
rm -f js/config-editor.js
rm -f js/auth-manager-v2.js
rm -f js/auth-manager.js
rm -f js/error-handler.js
rm -f js/error-recovery.js
rm -f js/help-menu.js
rm -f js/install-dialog.js
rm -f js/learning-engine.js
rm -f js/nix-bridge.js
rm -f js/nlp-bridge.js
rm -f js/onboarding-wizard.js
rm -f js/patterns-enhanced.js
rm -f js/plugin-manager.js
rm -f js/plugin-system.js
rm -f js/preview-system.js
rm -f js/rollback-manager.js
rm -f js/safety-validator.js
rm -f js/service-config.js
rm -f js/ui-controller.js
rm -f js/voice-interface.js
rm -f js/core-enhanced.js

# Remove old directories
rm -rf js/components/
rm -rf js/help/
rm -rf js/utils/

# Clean up generated files in nlp
echo "Cleaning up generated files in js/nlp/..."
rm -f js/nlp/*.js js/nlp/*.js.map js/nlp/*.d.ts

# Keep only TypeScript source files and the layers directory
echo "Keeping only TypeScript source files..."

# Remove old voice directory (we have voice-input.ts in nlp now)
rm -rf js/voice/

# Clean up CSS files we don't need
echo "Cleaning up unused CSS files..."
rm -f css/audit-dashboard.css
rm -f css/auth.css
rm -f css/config-editor.css
rm -f css/contextual-help.css
rm -f css/core.css
rm -f css/dashboard.css
rm -f css/error-handler.css
rm -f css/error-recovery.css
rm -f css/help-menu.css
rm -f css/install-dialog.css
rm -f css/onboarding.css
rm -f css/plugin-system.css
rm -f css/preview-system.css
rm -f css/rollback-manager.css
rm -f css/safety-dialog.css
rm -f css/service-config.css
rm -f css/animations.css

# Remove old scripts
echo "Removing old scripts..."
rm -f demo-all-features.sh
rm -f create-installer.sh
rm -f start-nix-humanity.sh
rm -f build-nlp.sh

# Remove old test files
rm -f test.html
rm -f tests/performance-test.html
rm -f tests/test-core.html

echo ""
echo "✅ JavaScript cleanup complete!"
echo ""
echo "Clean structure:"
echo "├── js/"
echo "│   ├── nlp/"
echo "│   │   ├── layers/        (pure functions)"
echo "│   │   └── *.ts          (TypeScript modules)"
echo "│   └── ui/"
echo "│       └── minimal-interface.ts"
echo "├── index.html"
echo "├── test-simple.html"
echo "└── docs/"
echo ""