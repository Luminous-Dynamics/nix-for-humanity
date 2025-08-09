#!/usr/bin/env python3
"""
Simple test for NixOSIntegration to verify the test framework works
"""

import sys
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "backend"))

# Mock dependencies before import
from unittest.mock import Mock, patch

# Mock the native backend
sys.modules['python'] = type(sys)('python')
sys.modules['python.native_nix_backend'] = type(sys)('python.native_nix_backend')

mock_backend = sys.modules['python.native_nix_backend']
mock_backend.NativeNixBackend = Mock
mock_backend.OperationType = type('OperationType', (), {
    'UPDATE': Mock(value='update'),
    'ROLLBACK': Mock(value='rollback'),
    'INSTALL': Mock(value='install'),
    'REMOVE': Mock(value='remove'),
    'SEARCH': Mock(value='search'),
    'BUILD': Mock(value='build'),
    'TEST': Mock(value='test'),
    'LIST_GENERATIONS': Mock(value='list_generations'),
})
mock_backend.NixOperation = Mock
mock_backend.NixResult = Mock
mock_backend.NATIVE_API_AVAILABLE = True

# Now try to import and test
try:
    # Import the module directly
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "nix_integration",
        project_root / "backend" / "core" / "nix_integration.py"
    )
    nix_integration = importlib.util.module_from_spec(spec)
    
    # Mock Intent and Context before loading
    sys.modules['api'] = type(sys)('api')
    sys.modules['api.schema'] = type(sys)('api.schema')
    sys.modules['api.schema'].Intent = Mock
    sys.modules['api.schema'].Context = Mock
    
    # Load the module
    spec.loader.exec_module(nix_integration)
    
    # Run a simple test
    print("✅ Successfully imported nix_integration module")
    
    # Test NixOSIntegration class
    integration = nix_integration.NixOSIntegration()
    print(f"✅ Created NixOSIntegration instance: {integration}")
    
    # Test status report
    status = integration.get_status()
    print(f"✅ Got status: {status}")
    
    print("\n🎉 Basic test passed! The module can be imported and instantiated.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()