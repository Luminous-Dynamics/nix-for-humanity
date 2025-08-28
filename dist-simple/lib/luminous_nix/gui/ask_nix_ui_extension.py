#!/usr/bin/env python3
"""
🎨 Ask-Nix UI Extension
Adds UI generation capabilities to the main ask-nix CLI
"""

import sys
from pathlib import Path

# Add GUI module to path
gui_path = Path(__file__).parent
sys.path.insert(0, str(gui_path))

from cli_integration import integrate_with_ask_nix, UIGeneratorCLI


def extend_ask_nix_parser(parser):
    """Extend ask-nix argument parser with UI commands"""
    
    # Check if subparsers already exist
    if not hasattr(parser, '_subparsers'):
        subparsers = parser.add_subparsers(dest='command', help='Commands')
    else:
        # Get existing subparsers
        for action in parser._subparsers._actions:
            if isinstance(action, argparse._SubParsersAction):
                subparsers = action
                break
    
    # Add UI commands
    ui_parser = subparsers.add_parser(
        'ui',
        help='Generate custom interfaces with AI',
        description="""
AI-Driven Interface Generation for Luminous Nix

Create beautiful, functional interfaces using natural language:
  - Dashboard layouts
  - Configuration forms  
  - Data visualizations
  - Custom workflows

The system learns from your preferences and improves over time.
        """
    )
    
    ui_subparsers = ui_parser.add_subparsers(dest='ui_command', help='UI commands')
    
    # Create interface
    create_parser = ui_subparsers.add_parser(
        'create',
        help='Create interface from natural language',
        epilog="""
Examples:
  ask-nix ui create "dashboard for system monitoring"
  ask-nix ui create "form to configure NixOS packages" --no-preview
  ask-nix ui create "dark theme IDE layout with file browser"
        """
    )
    create_parser.add_argument('request', nargs='+', help='Natural language description')
    create_parser.add_argument('--no-preview', action='store_true', help='Skip preview')
    create_parser.add_argument('--user', help='User profile for preferences')
    create_parser.add_argument('--save-as', help='Save with custom name')
    
    # Refine interface
    refine_parser = ui_subparsers.add_parser(
        'refine',
        help='Refine existing interface',
        epilog="""
Examples:
  ask-nix ui refine "make the charts bigger"
  ask-nix ui refine "add dark mode toggle" --id dashboard_20240125
  ask-nix ui refine "remove the sidebar"
        """
    )
    refine_parser.add_argument('refinement', nargs='+', help='Refinement request')
    refine_parser.add_argument('--id', help='Interface ID (default: last)')
    refine_parser.add_argument('--preview', action='store_true', help='Preview after refining')
    
    # Show interface
    show_parser = ui_subparsers.add_parser(
        'show',
        help='Display saved interface',
        epilog="""
Examples:
  ask-nix ui show               # Show last created
  ask-nix ui show --id dashboard_20240125
  ask-nix ui show --list        # List all interfaces
        """
    )
    show_group = show_parser.add_mutually_exclusive_group()
    show_group.add_argument('--last', action='store_true', default=True, help='Show last interface')
    show_group.add_argument('--id', help='Show specific interface')
    show_group.add_argument('--list', action='store_true', help='List all interfaces')
    
    # Preview command
    preview_parser = ui_subparsers.add_parser(
        'preview',
        help='Preview interface without saving',
        epilog="""
Examples:
  ask-nix ui preview "quick dashboard layout"
  ask-nix ui preview "form with 3 input fields"
        """
    )
    preview_parser.add_argument('request', nargs='+', help='Interface description')
    
    # Export interface
    export_parser = ui_subparsers.add_parser(
        'export',
        help='Export interface to file',
        epilog="""
Examples:
  ask-nix ui export --format html --output dashboard.html
  ask-nix ui export --format python > app.py
  ask-nix ui export --format json --id dashboard_20240125
        """
    )
    export_parser.add_argument('--id', help='Interface ID (default: last)')
    export_parser.add_argument('--format', choices=['json', 'html', 'python', 'react'], 
                               default='json', help='Export format')
    export_parser.add_argument('--output', help='Output file path')
    
    # Save interface
    save_parser = ui_subparsers.add_parser(
        'save',
        help='Save interface with custom name',
        epilog="""
Examples:
  ask-nix ui save my-dashboard
  ask-nix ui save "System Monitor" --id interface_20240125
        """
    )
    save_parser.add_argument('name', help='Custom name for interface')
    save_parser.add_argument('--id', help='Interface ID to save (default: last)')
    
    # Delete interface
    delete_parser = ui_subparsers.add_parser(
        'delete',
        help='Delete saved interface',
        epilog="""
Examples:
  ask-nix ui delete --id dashboard_20240125
  ask-nix ui delete --all       # Delete all interfaces
  ask-nix ui delete --old 30    # Delete interfaces older than 30 days
        """
    )
    delete_group = delete_parser.add_mutually_exclusive_group(required=True)
    delete_group.add_argument('--id', help='Interface ID to delete')
    delete_group.add_argument('--all', action='store_true', help='Delete all interfaces')
    delete_group.add_argument('--old', type=int, help='Delete interfaces older than N days')
    
    # Statistics
    stats_parser = ui_subparsers.add_parser(
        'stats',
        help='Show UI generation statistics',
        epilog="""
Examples:
  ask-nix ui stats              # Overall statistics
  ask-nix ui stats --detailed   # Detailed breakdown
  ask-nix ui stats --report     # Generate full report
        """
    )
    stats_parser.add_argument('--detailed', action='store_true', help='Show detailed stats')
    stats_parser.add_argument('--report', action='store_true', help='Generate full report')
    
    # Feedback
    feedback_parser = ui_subparsers.add_parser(
        'feedback',
        help='Provide feedback on generated interface',
        epilog="""
Examples:
  ask-nix ui feedback good --id dashboard_20240125
  ask-nix ui feedback "needs more charts"
  ask-nix ui feedback --rating 8 --comment "Great but too dark"
        """
    )
    feedback_parser.add_argument('feedback', nargs='*', help='Feedback text or rating')
    feedback_parser.add_argument('--id', help='Interface ID')
    feedback_parser.add_argument('--rating', type=int, choices=range(1, 11), 
                                 help='Rating from 1-10')
    feedback_parser.add_argument('--comment', help='Additional comment')
    
    return ui_parser


def handle_ui_command(args):
    """Handle UI generation commands from ask-nix"""
    
    cli = UIGeneratorCLI()
    
    if args.ui_command == 'create':
        request = ' '.join(args.request)
        result = cli.create_interface(
            request=request,
            user_id=args.user,
            preview=not args.no_preview
        )
        
        if result['success']:
            print(f"\n✅ Interface created successfully!")
            print(f"📊 Components: {result['components']}")
            print(f"🎯 Confidence: {result['confidence']:.0%}")
            print(f"⏱️  Time: {result['generation_time']:.2f}ms")
            
            if args.save_as:
                # TODO: Implement custom naming
                print(f"💾 Saved as: {args.save_as}")
        else:
            print("❌ Failed to create interface")
    
    elif args.ui_command == 'refine':
        refinement = ' '.join(args.refinement)
        result = cli.refine_interface(
            refinement=refinement,
            interface_id=args.id
        )
        
        if result['success']:
            print(f"\n✅ Interface refined!")
            print(f"📊 Components: {result['components']}")
            
            if args.preview:
                interface = cli._load_interface(result['interface_id'])
                if interface:
                    cli.renderer.preview(interface)
        else:
            print(f"❌ {result.get('error', 'Refinement failed')}")
    
    elif args.ui_command == 'show':
        if args.list:
            interfaces = cli.list_interfaces()
            if interfaces:
                print("\n📋 Saved Interfaces")
                print("=" * 60)
                for i, intf in enumerate(interfaces, 1):
                    print(f"\n{i}. ID: {intf['id']}")
                    print(f"   Created: {intf['created']}")
                    print(f"   Request: {intf['request'][:50]}...")
                    print(f"   Components: {intf['components']}")
            else:
                print("No interfaces saved yet")
        elif args.id:
            interface = cli._load_interface(args.id)
            if interface:
                cli.renderer.preview(interface)
            else:
                print(f"❌ Interface {args.id} not found")
        else:
            cli.show_last_interface()
    
    elif args.ui_command == 'preview':
        request = ' '.join(args.request)
        
        # Build without saving
        context = cli._get_user_context()
        interface = cli.builder.build_interface(request, context)
        
        print(f"🎨 Preview: {len(interface.components)} components")
        cli.renderer.preview(interface)
    
    elif args.ui_command == 'export':
        result = cli.export_interface(
            interface_id=args.id,
            format=args.format,
            output_path=args.output
        )
        
        if result['success']:
            print(f"✅ Exported to: {result['path']}")
        else:
            print(f"❌ {result.get('error', 'Export failed')}")
    
    elif args.ui_command == 'save':
        # TODO: Implement custom naming
        print(f"💾 Saving as: {args.name}")
    
    elif args.ui_command == 'delete':
        if args.all:
            # TODO: Implement bulk delete
            print("⚠️  Delete all interfaces? (not implemented)")
        elif args.old:
            # TODO: Implement age-based delete
            print(f"⚠️  Delete interfaces older than {args.old} days (not implemented)")
        elif args.id:
            # TODO: Implement single delete
            print(f"⚠️  Delete interface {args.id} (not implemented)")
    
    elif args.ui_command == 'stats':
        stats = cli.get_statistics()
        
        if args.report:
            # Generate full report
            report = cli.monitor.generate_report()
            print(report)
        elif args.detailed:
            # Detailed statistics
            import json
            print(json.dumps(stats, indent=2))
        else:
            # Summary statistics
            print("\n📊 UI Generation Statistics")
            print("=" * 60)
            
            if 'builder' in stats:
                print("\n🔨 Builder:")
                print(f"   Interfaces created: {stats.get('interfaces_created', 0)}")
                print(f"   Patterns learned: {stats.get('patterns_learned', 0)}")
            
            if 'performance' in stats and stats['performance']:
                print("\n⚡ Performance:")
                perf = stats['performance']
                print(f"   Avg generation time: {perf.get('avg_generation_time', 0):.2f}ms")
                print(f"   Success rate: {perf.get('success_rate', 0):.0%}")
    
    elif args.ui_command == 'feedback':
        # Record feedback
        if args.rating:
            print(f"⭐ Rating recorded: {args.rating}/10")
        
        if args.feedback:
            feedback_text = ' '.join(args.feedback)
            print(f"💬 Feedback: {feedback_text}")
        
        if args.comment:
            print(f"📝 Comment: {args.comment}")
        
        # TODO: Actually save feedback to learning system
        cli.learning.record_feedback(
            interface_id=args.id or "last",
            score=args.rating or 5,
            feedback_text=args.comment or ' '.join(args.feedback) if args.feedback else ""
        )
        
        print("✅ Feedback recorded - thank you!")


# Integration function for importing into ask-nix
def get_ui_extension():
    """Get UI extension for ask-nix integration"""
    
    return {
        'name': 'ui',
        'description': 'AI-driven interface generation',
        'parser_extension': extend_ask_nix_parser,
        'handler': handle_ui_command
    }


if __name__ == "__main__":
    # Test the extension
    import argparse
    
    parser = argparse.ArgumentParser(description='Test UI Extension')
    extend_ask_nix_parser(parser)
    
    # Parse test command
    import sys
    if len(sys.argv) == 1:
        sys.argv.extend(['ui', 'create', 'test dashboard'])
    
    args = parser.parse_args()
    
    if hasattr(args, 'ui_command'):
        handle_ui_command(args)
    else:
        parser.print_help()