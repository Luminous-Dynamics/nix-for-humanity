#!/usr/bin/env python3
"""
Setup script for the Causal XAI environment

This script:
1. Checks Python version
2. Installs XAI dependencies
3. Verifies DoWhy installation
4. Runs basic tests
"""

import sys
import subprocess
import importlib.util
from pathlib import Path


def check_python_version():
    """Ensure we're running Python 3.11+"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Python 3.11+ required, found {version.major}.{version.minor}")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor} - OK")


def install_dependencies():
    """Install XAI dependencies"""
    print("\nInstalling XAI dependencies...")
    requirements_file = Path(__file__).parent / "requirements-xai.txt"
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)


def verify_dowhy():
    """Verify DoWhy is properly installed"""
    print("\nVerifying DoWhy installation...")
    
    try:
        import dowhy
        print(f"✅ DoWhy version {dowhy.__version__} installed")
        
        # Test basic functionality
        from dowhy import CausalModel
        import pandas as pd
        import numpy as np
        
        # Create simple test data
        n = 100
        data = pd.DataFrame({
            'treatment': np.random.binomial(1, 0.5, n),
            'outcome': np.random.normal(0, 1, n),
            'confounder': np.random.normal(0, 1, n)
        })
        
        # Create simple causal model
        model = CausalModel(
            data=data,
            treatment='treatment',
            outcome='outcome',
            common_causes=['confounder']
        )
        
        print("✅ DoWhy basic functionality verified")
        
    except ImportError:
        print("❌ DoWhy not installed properly")
        sys.exit(1)
    except Exception as e:
        print(f"❌ DoWhy test failed: {e}")
        sys.exit(1)


def verify_networkx():
    """Verify NetworkX is properly installed"""
    print("\nVerifying NetworkX installation...")
    
    try:
        import networkx as nx
        print(f"✅ NetworkX version {nx.__version__} installed")
        
        # Test basic graph creation
        G = nx.DiGraph()
        G.add_edge('cause', 'effect')
        assert G.has_edge('cause', 'effect')
        print("✅ NetworkX basic functionality verified")
        
    except ImportError:
        print("❌ NetworkX not installed properly")
        sys.exit(1)
    except Exception as e:
        print(f"❌ NetworkX test failed: {e}")
        sys.exit(1)


def test_xai_imports():
    """Test that our XAI modules can be imported"""
    print("\nTesting XAI module imports...")
    
    # Add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        from nix_humanity.xai import (
            CausalXAIEngine,
            ExplanationLevel,
            Decision,
            CausalKnowledgeBase
        )
        print("✅ XAI modules import successfully")
        
        # Test knowledge base
        kb = CausalKnowledgeBase()
        model = kb.get_model('install_package')
        assert model is not None
        assert 'nodes' in model
        assert 'edges' in model
        print("✅ Knowledge base functional")
        
    except ImportError as e:
        print(f"❌ Failed to import XAI modules: {e}")
        print("Note: This is expected if running setup before implementation")
    except Exception as e:
        print(f"❌ XAI module test failed: {e}")


def create_test_harness():
    """Create a simple test harness"""
    print("\nCreating test harness...")
    
    test_file = Path(__file__).parent / "test_xai_basic.py"
    test_content = '''#!/usr/bin/env python3
"""Basic test harness for XAI functionality"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from nix_humanity.xai import (
    CausalKnowledgeBase,
    Decision,
    ExplanationLevel,
    CausalFactor
)
from nix_humanity.xai.models import AlternativeExplanation, Explanation


def test_knowledge_base():
    """Test the causal knowledge base"""
    kb = CausalKnowledgeBase()
    
    # Test getting models
    install_model = kb.get_model('install_package')
    assert install_model is not None
    print(f"✓ Install model has {len(install_model['nodes'])} nodes")
    
    # Test building graph
    graph = kb.build_graph(install_model)
    assert graph.number_of_nodes() == len(install_model['nodes'])
    print(f"✓ Built graph with {graph.number_of_nodes()} nodes")
    
    # Test getting treatments
    treatments = kb.get_treatments('install_package')
    assert 'installation_method' in treatments
    print(f"✓ Found treatments: {treatments}")
    
    # Test getting outcomes
    outcomes = kb.get_outcomes('install_package')
    assert 'installation_success' in outcomes
    print(f"✓ Found outcomes: {outcomes}")


def test_models():
    """Test the data models"""
    # Test CausalFactor
    factor = CausalFactor(
        name="package_availability",
        value=True,
        influence=0.8,
        confidence=0.95,
        description="Package exists in nixpkgs"
    )
    assert factor.influence == 0.8
    print("✓ CausalFactor created")
    
    # Test Decision
    decision = Decision(
        action="install",
        target="firefox",
        context={"user_need": "web_browser"},
        confidence=0.92,
        alternatives=[{"package": "chromium", "score": 0.85}]
    )
    assert decision.action == "install"
    print("✓ Decision created")
    
    # Test Explanation
    explanation = Explanation(
        simple="Installing Firefox because it matches your need for a web browser.",
        detailed="I recommend installing Firefox based on several factors...",
        expert={"causal_graph": "..."},
        confidence=0.92,
        factors=[factor],
        alternatives_rejected=[
            AlternativeExplanation(
                alternative="chromium",
                reason_rejected="Lower user preference score",
                confidence_difference=0.07
            )
        ]
    )
    primary = explanation.get_primary_factor()
    assert primary.name == "package_availability"
    print("✓ Explanation created with primary factor")


if __name__ == "__main__":
    print("Running XAI basic tests...")
    
    try:
        test_knowledge_base()
        print("\\n✅ Knowledge base tests passed")
    except Exception as e:
        print(f"\\n❌ Knowledge base tests failed: {e}")
    
    try:
        test_models()
        print("\\n✅ Model tests passed")
    except Exception as e:
        print(f"\\n❌ Model tests failed: {e}")
    
    print("\\nTest harness complete!")
'''
    
    test_file.write_text(test_content)
    test_file.chmod(0o755)
    print(f"✅ Created test harness: {test_file}")


def main():
    """Main setup function"""
    print("=== Nix for Humanity - Causal XAI Setup ===\n")
    
    check_python_version()
    install_dependencies()
    verify_dowhy()
    verify_networkx()
    test_xai_imports()
    create_test_harness()
    
    print("\n=== Setup Complete! ===")
    print("\nNext steps:")
    print("1. Run the test harness: python test_xai_basic.py")
    print("2. Implement CausalModelBuilder")
    print("3. Implement CausalInferenceEngine")
    print("4. Implement ExplanationGenerator")
    print("5. Create the main CausalXAIEngine")
    
    print("\nTo test the basic functionality:")
    print("  cd backend")
    print("  python test_xai_basic.py")


if __name__ == "__main__":
    main()