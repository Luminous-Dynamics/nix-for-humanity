"""
Integration wrapper for dev environment fix
Routes queries through the specialist first
"""

from luminous_nix.ai.hrm_enhanced_v3 import HRMEnhancedV3
from luminous_nix.ai.dev_environment_specialist import DevEnvironmentSpecialist
import logging

logger = logging.getLogger(__name__)

class EnhancedBackend:
    """Backend with dev environment fix integrated"""
    
    def __init__(self):
        self.hrm = HRMEnhancedV3()
        self.specialist = DevEnvironmentSpecialist()
        logger.info("Enhanced backend with dev fix initialized")
    
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
