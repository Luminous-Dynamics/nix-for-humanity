"""
Integration wrapper for dev environment fix
Routes queries through the specialist first

NOTE: This file uses hrm_enhanced_v3 which was archived 2025-11-20.
Consider updating to use hrm_reasoner_v2 or marking this as deprecated.
"""

# DEPRECATED: hrm_enhanced_v3 was archived - this file may need updating
# from luminous_nix.ai.hrm_enhanced_v3 import HRMEnhancedV3
from luminous_nix.ai.hrm.base.hrm_reasoner_v2 import HierarchicalReasoningModel
from luminous_nix.ai.dev_environment_specialist import DevEnvironmentSpecialist
import logging

logger = logging.getLogger(__name__)

class EnhancedBackend:
    """Backend with dev environment fix integrated

    DEPRECATED: Uses archived hrm_enhanced_v3. Consider updating to hrm_reasoner_v2.
    """

    def __init__(self):
        # Updated to use HierarchicalReasoningModel (v2) instead of archived v3
        self.hrm = HierarchicalReasoningModel()
        self.specialist = DevEnvironmentSpecialist()
        logger.info("Enhanced backend with dev fix initialized (using HRM v2)")
    
    def process_query(self, query: str) -> dict:
        """Process query with dev specialist priority"""
        # Use HRM v3 which includes the specialist
        result = self.hrm.process_query(query)
        
        if result.get('success'):
            logger.info(f"Query handled by {result.get('source', 'unknown')}")
        else:
            logger.warning(f"Query failed: {query}")
        
        return result
    
    def get_metrics(self) -> dict:
        """Get performance metrics"""
        return self.hrm.get_metrics()

# Global instance
backend = EnhancedBackend()
