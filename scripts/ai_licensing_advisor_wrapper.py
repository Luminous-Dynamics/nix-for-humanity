"""
Wrapper module to allow clean imports of ai-licensing-advisor
"""

import importlib.util
import sys
from pathlib import Path

# Load the module with hyphens in the name
module_path = Path(__file__).parent / "ai-licensing-advisor.py"
spec = importlib.util.spec_from_file_location("ai_licensing_advisor", module_path)
ai_licensing_advisor = importlib.util.module_from_spec(spec)
sys.modules["ai_licensing_advisor"] = ai_licensing_advisor
spec.loader.exec_module(ai_licensing_advisor)

# Export the classes
AILicensingAdvisor = ai_licensing_advisor.AILicensingAdvisor
LicenseType = ai_licensing_advisor.LicenseType
CommercialUse = ai_licensing_advisor.CommercialUse