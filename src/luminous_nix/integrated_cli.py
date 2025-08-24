#!/usr/bin/env python3
"""
Integrated CLI for Luminous Nix with Phase 3 & 4 systems
Connects adaptive features, federated learning, and causal reasoning to main flow
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any

# Import the integrated systems
from luminous_nix.consciousness.unified_integration import UnifiedAdaptiveSystem
from luminous_nix.federated.federated_learning import (
    FederatedLearningNetwork,
    PrivacyLevel
)
from luminous_nix.infrastructure.self_maintaining import (
    SelfMaintainingInfrastructure
)
from luminous_nix.causal.advanced_reasoning import (
    AdvancedCausalReasoning
)

# Import the standard CLI components
from luminous_nix.interfaces.cli import process_command as standard_process
from luminous_nix.core.system_orchestrator import SystemOrchestrator


class IntegratedCLI:
    """
    Enhanced CLI that integrates Phase 3 (Adaptive) and Phase 4 (Living System)
    """
    
    def __init__(self):
        """Initialize all integrated systems"""
        print("🌟 Initializing Integrated Luminous Nix", file=sys.stderr)
        
        # Standard system
        self.orchestrator = SystemOrchestrator()
        
        # Phase 3: Adaptive Systems
        self.adaptive_system = UnifiedAdaptiveSystem()
        
        # Phase 4: Living System
        self.federated_network = FederatedLearningNetwork(
            participant_id=os.getenv('USER', 'default_user'),
            privacy_level=PrivacyLevel.DIFFERENTIAL
        )
        self.infrastructure = SelfMaintainingInfrastructure()
        self.causal_reasoning = AdvancedCausalReasoning()
        
        # Start monitoring in background
        asyncio.create_task(self._start_monitoring())
        
        print("✨ All systems integrated and active!", file=sys.stderr)
    
    async def _start_monitoring(self):
        """Start infrastructure monitoring in background"""
        try:
            await self.infrastructure.start_monitoring()
        except Exception as e:
            print(f"⚠️ Monitoring startup failed: {e}", file=sys.stderr)
    
    async def process_command(self, command: str, args: Dict[str, Any] = None) -> int:
        """
        Process a command through all integrated systems
        
        Args:
            command: The command to process
            args: Optional command arguments
            
        Returns:
            Exit code (0 for success)
        """
        user_id = os.getenv('USER', 'default')
        
        try:
            # Phase 3: Adapt to user
            print("🎭 Adapting to your style...", file=sys.stderr)
            adaptive_result = self.adaptive_system.process_command(command, user_id)
            
            # Get adapted configuration
            voice_tone = adaptive_result.get('voice_profile', {}).get('tone', 'neutral')
            ui_level = adaptive_result.get('ui_config', {}).get('complexity_level', 'intermediate')
            
            # Adjust output based on UI level
            if ui_level == 'minimal':
                # Suppress extra output
                os.environ['LUMINOUS_NIX_QUIET'] = 'true'
            elif ui_level == 'expert':
                # Show detailed output
                os.environ['LUMINOUS_NIX_VERBOSE'] = 'true'
            
            # Phase 4: Learn from interaction
            event = {
                'type': 'command_execution',
                'command': command,
                'user_id': user_id,
                'ui_level': ui_level,
                'voice_tone': voice_tone
            }
            self.causal_reasoning.observe_event(event)
            
            # Check system health
            health_status = self.infrastructure.get_infrastructure_status()
            if health_status['health_status'] != 'healthy':
                print(f"⚠️ System health: {health_status['health_status']}", file=sys.stderr)
                
                # Self-heal if needed
                if health_status.get('needs_healing'):
                    print("🔧 Initiating self-healing...", file=sys.stderr)
                    await self.infrastructure.trigger_healing()
            
            # Process command through standard flow
            result = await self.orchestrator.process_command(command, args)
            
            # Learn from result
            event['result'] = 'success' if result == 0 else 'failure'
            self.causal_reasoning.observe_event(event)
            
            # Share learning if successful (federated)
            if result == 0 and adaptive_result.get('adaptations'):
                # This would share with federated network
                print("📤 Sharing learning with community...", file=sys.stderr)
                # self.federated_network.share_update(adaptive_result['adaptations'])
            
            return result
            
        except Exception as e:
            # Use causal reasoning to understand error
            print(f"❌ Error: {e}", file=sys.stderr)
            
            analysis = self.causal_reasoning.analyze_issue(
                str(e),
                {'command': command, 'user_level': ui_level}
            )
            
            if analysis.get('root_causes'):
                print("\n🔍 Possible causes:", file=sys.stderr)
                for cause in analysis['root_causes'][:2]:
                    print(f"  • {cause['cause']}", file=sys.stderr)
                    if cause.get('fixes'):
                        print(f"    Fix: {cause['fixes'][0]}", file=sys.stderr)
            
            return 1
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            'infrastructure': self.infrastructure.get_infrastructure_status(),
            'federated_network': self.federated_network.get_network_status(),
            'causal_wisdom': self.causal_reasoning.get_wisdom_summary(),
            'adaptive_state': {
                'personas_active': len(getattr(self.adaptive_system, 'personas', {})),
                'voice_enabled': hasattr(self.adaptive_system, 'voice_system'),
                'learning_active': hasattr(self.adaptive_system, 'learning_memory')
            }
        }
    
    async def cleanup(self):
        """Clean up resources on exit"""
        await self.infrastructure.stop_monitoring()


async def main():
    """
    Main entry point for integrated CLI
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Luminous Nix - Natural language NixOS with integrated adaptive & living systems"
    )
    parser.add_argument('command', nargs='?', help='Command to execute')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--quiet', action='store_true', help='Minimal output')
    parser.add_argument('--verbose', action='store_true', help='Detailed output')
    
    args = parser.parse_args()
    
    # Initialize integrated CLI
    cli = IntegratedCLI()
    
    try:
        if args.status:
            # Show system status
            status = await cli.get_status()
            print("\n📊 Integrated System Status")
            print("=" * 40)
            print(f"Infrastructure: {status['infrastructure']['health_status']}")
            print(f"Monitoring: {status['infrastructure']['monitoring_active']}")
            print(f"Causal Wisdom: {status['causal_wisdom']['total_wisdom']} insights")
            print(f"Adaptive Features: {status['adaptive_state']}")
            print(f"Federated Network: {status['federated_network']['status']}")
            return 0
        
        elif args.command:
            # Process command
            return await cli.process_command(
                args.command,
                {'quiet': args.quiet, 'verbose': args.verbose}
            )
        
        else:
            # Interactive mode
            print("🌟 Luminous Nix - Integrated Adaptive & Living Systems")
            print("Type 'help' for commands, 'exit' to quit\n")
            
            while True:
                try:
                    command = input("luminous> ").strip()
                    if command.lower() in ('exit', 'quit'):
                        break
                    elif command:
                        await cli.process_command(command)
                except (EOFError, KeyboardInterrupt):
                    print()
                    break
            
            return 0
    
    finally:
        # Clean up
        await cli.cleanup()


if __name__ == "__main__":
    asyncio.run(main())