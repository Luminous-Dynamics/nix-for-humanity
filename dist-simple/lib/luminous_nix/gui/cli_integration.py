#!/usr/bin/env python3
"""
🔗 CLI Integration for AI-Driven Interface Generation
Integrates the UI generation system with the main Luminous Nix CLI
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from learning_persistence import InterfaceMetrics, LearningDatabase
from nl_interface_builder_v2 import NLInterfaceBuilderV2, UserContext
from performance_monitor import PerformanceMetric, PerformanceMonitor

try:
    from textual_ui_renderer import TextualUIRenderer

    TEXTUAL_AVAILABLE = True
except ImportError:
    print("Warning: Textual not available - preview disabled")
    TEXTUAL_AVAILABLE = False

    class TextualUIRenderer:
        """Mock renderer when Textual not available"""

        def preview(self, interface):
            print("🎨 Preview not available (install Textual: pip install textual)")
            print(f"   Would display {len(interface.components)} components")


class UIGeneratorCLI:
    """CLI interface for UI generation system"""

    def __init__(self):
        # Initialize components
        self.builder = NLInterfaceBuilderV2(use_llm=True, enable_learning=True)
        self.renderer = TextualUIRenderer()
        self.learning = LearningDatabase()
        self.monitor = PerformanceMonitor()

        # User context cache
        self.user_contexts = {}
        self._load_user_preferences()

    def _load_user_preferences(self):
        """Load saved user preferences"""

        prefs_path = Path.home() / ".config" / "luminous-nix" / "ui-preferences.json"
        if prefs_path.exists():
            try:
                with open(prefs_path) as f:
                    self.user_contexts = json.load(f)
            except:
                pass

    def _save_user_preferences(self):
        """Save user preferences"""

        prefs_path = Path.home() / ".config" / "luminous-nix" / "ui-preferences.json"
        prefs_path.parent.mkdir(parents=True, exist_ok=True)

        with open(prefs_path, "w") as f:
            json.dump(self.user_contexts, f, indent=2)

    def _get_user_context(self, user_id: str | None = None) -> UserContext:
        """Get or create user context"""

        if user_id is None:
            user_id = "default"

        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = {
                "expertise_level": "intermediate",
                "device_type": "desktop",
                "preferences": {},
            }

        ctx_data = self.user_contexts[user_id]
        return UserContext(
            user_id=user_id,
            expertise_level=ctx_data["expertise_level"],
            device_type=ctx_data["device_type"],
            preferences=ctx_data["preferences"],
        )

    def create_interface(
        self, request: str, user_id: str | None = None, preview: bool = True
    ) -> dict:
        """Create an interface from natural language request"""

        start_time = datetime.now()

        # Get user context
        context = self._get_user_context(user_id)

        # Build interface
        print(f"🔨 Building interface: {request[:50]}...")
        interface = self.builder.build_interface(request, context)

        # Record metrics
        generation_time = (datetime.now() - start_time).total_seconds() * 1000

        metric = PerformanceMetric(
            timestamp=datetime.now(),
            request=request,
            generation_time=generation_time,
            component_count=len(interface.components),
            success=True,
            accuracy=interface.metadata.get("confidence", 0),
            persona=context.expertise_level,
            cache_hits=self.builder.hybrid_parser.stats.get("cache_hits", 0),
        )
        self.monitor.record_metric(metric)

        # Learn from this interaction
        if interface.metadata.get("confidence", 0) > 0.7:
            # Record successful pattern (simplified without ParsedIntent)
            metrics = InterfaceMetrics(
                interface_id=str(id(interface)),
                request=request,
                generation_time=generation_time,  # Already in milliseconds
                component_count=len(interface.components),
                user_satisfaction=interface.metadata.get("confidence", 0),
                interaction_time=None,
                task_completion=None,
                modifications_made=0,
                timestamp=datetime.now(),
            )
            self.learning.save_interface_metrics(metrics)

        # Save interface specification
        spec_path = self._save_interface_spec(interface, request)

        result = {
            "success": True,
            "interface_id": str(id(interface)),
            "components": len(interface.components),
            "confidence": interface.metadata.get("confidence", 0),
            "generation_time": generation_time,
            "spec_path": str(spec_path),
        }

        # Preview if requested
        if preview:
            print("🎨 Launching preview...")
            self.renderer.preview(interface)

        return result

    def refine_interface(
        self,
        refinement: str,
        interface_id: str | None = None,
        user_id: str | None = None,
    ) -> dict:
        """Refine an existing interface"""

        # Load last interface if not specified
        if interface_id is None:
            interface = self._load_last_interface()
            if interface is None:
                return {"success": False, "error": "No interface to refine"}
        else:
            interface = self._load_interface(interface_id)
            if interface is None:
                return {
                    "success": False,
                    "error": f"Interface {interface_id} not found",
                }

        # Get user context
        context = self._get_user_context(user_id)

        # Apply refinement
        print(f"✏️ Refining interface: {refinement[:50]}...")
        refined = self.builder.refine_interface(interface, refinement, context)

        # Save refined interface
        spec_path = self._save_interface_spec(refined, f"Refined: {refinement}")

        return {
            "success": True,
            "interface_id": str(id(refined)),
            "components": len(refined.components),
            "spec_path": str(spec_path),
        }

    def show_last_interface(self):
        """Show the last created interface"""

        interface = self._load_last_interface()
        if interface is None:
            print("❌ No interfaces created yet")
            return

        print("🎨 Showing last interface...")
        self.renderer.preview(interface)

    def list_interfaces(self) -> list[dict]:
        """List all saved interfaces"""

        interfaces_dir = (
            Path.home() / ".local" / "share" / "luminous-nix" / "interfaces"
        )
        if not interfaces_dir.exists():
            return []

        interfaces = []
        for spec_file in sorted(interfaces_dir.glob("*.json"), reverse=True)[:20]:
            with open(spec_file) as f:
                spec = json.load(f)
                interfaces.append(
                    {
                        "id": spec_file.stem,
                        "created": spec.get("metadata", {}).get(
                            "generated_at", "unknown"
                        ),
                        "request": spec.get("metadata", {}).get("request", "unknown"),
                        "components": len(spec.get("components", [])),
                    }
                )

        return interfaces

    def export_interface(
        self,
        interface_id: str | None = None,
        format: str = "json",
        output_path: str | None = None,
    ) -> dict:
        """Export interface to various formats"""

        # Load interface
        if interface_id is None:
            interface = self._load_last_interface()
        else:
            interface = self._load_interface(interface_id)

        if interface is None:
            return {"success": False, "error": "Interface not found"}

        # Determine output path
        if output_path is None:
            output_path = (
                Path.cwd()
                / f"interface_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
            )
        else:
            output_path = Path(output_path)

        # Export based on format
        if format == "json":
            self._export_json(interface, output_path)
        elif format == "html":
            self._export_html(interface, output_path)
        elif format == "python":
            self._export_python(interface, output_path)
        else:
            return {"success": False, "error": f"Unknown format: {format}"}

        return {"success": True, "path": str(output_path)}

    def get_statistics(self) -> dict:
        """Get usage statistics"""

        # Get builder stats
        builder_stats = self.builder.get_statistics()

        # Get performance stats
        perf_summary = self.monitor.calculate_summary()

        # Get learning stats
        patterns = self.learning.get_patterns()

        return {
            "builder": builder_stats,
            "performance": perf_summary,
            "patterns_learned": len(patterns),
            "interfaces_created": len(self.list_interfaces()),
        }

    def _save_interface_spec(self, interface, request: str) -> Path:
        """Save interface specification to disk"""

        # Create save directory
        save_dir = Path.home() / ".local" / "share" / "luminous-nix" / "interfaces"
        save_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        spec_file = save_dir / f"interface_{timestamp}.json"

        # Prepare specification
        spec = {
            "components": [
                {
                    "id": comp.id,
                    "name": comp.name,
                    "purpose": comp.dna.purpose,
                    "structure": comp.structure,
                }
                for comp in interface.components
            ],
            "layout": interface.layout,
            "theme": interface.theme,
            "interactions": interface.interactions,
            "data_bindings": interface.data_bindings,
            "metadata": {
                **interface.metadata,
                "request": request,
                "saved_at": datetime.now().isoformat(),
            },
        }

        # Save to file
        with open(spec_file, "w") as f:
            json.dump(spec, f, indent=2)

        # Also save as "last"
        last_file = save_dir / "last.json"
        with open(last_file, "w") as f:
            json.dump(spec, f, indent=2)

        return spec_file

    def _load_last_interface(self):
        """Load the last created interface"""

        last_file = (
            Path.home()
            / ".local"
            / "share"
            / "luminous-nix"
            / "interfaces"
            / "last.json"
        )
        if not last_file.exists():
            return None

        return self._load_interface_from_file(last_file)

    def _load_interface(self, interface_id: str):
        """Load a specific interface"""

        spec_file = (
            Path.home()
            / ".local"
            / "share"
            / "luminous-nix"
            / "interfaces"
            / f"{interface_id}.json"
        )
        if not spec_file.exists():
            # Try as full filename
            spec_file = (
                Path.home()
                / ".local"
                / "share"
                / "luminous-nix"
                / "interfaces"
                / f"interface_{interface_id}.json"
            )

        if not spec_file.exists():
            return None

        return self._load_interface_from_file(spec_file)

    def _load_interface_from_file(self, spec_file: Path):
        """Load interface from JSON file"""

        from component_synthesis_engine import ComponentDNA, SynthesizedComponent
        from nl_interface_builder import InterfaceSpecification

        with open(spec_file) as f:
            spec = json.load(f)

        # Reconstruct components
        components = []
        for comp_spec in spec["components"]:
            dna = ComponentDNA(
                purpose=comp_spec["purpose"],
                capabilities=[],
                visual_traits={},
                behaviors={},
                data_bindings={},
                evolution={},
            )

            component = SynthesizedComponent(
                id=comp_spec["id"],
                name=comp_spec["name"],
                dna=dna,
                structure=comp_spec.get("structure", {}),
                styles={},
                behaviors={},
            )
            components.append(component)

        return InterfaceSpecification(
            components=components,
            layout=spec["layout"],
            theme=spec["theme"],
            interactions=spec["interactions"],
            data_bindings=spec["data_bindings"],
            metadata=spec["metadata"],
        )

    def _export_json(self, interface, output_path: Path):
        """Export as JSON"""

        spec = {
            "components": [
                {
                    "id": comp.id,
                    "name": comp.name,
                    "purpose": comp.dna.purpose,
                    "structure": comp.structure,
                }
                for comp in interface.components
            ],
            "layout": interface.layout,
            "theme": interface.theme,
        }

        with open(output_path, "w") as f:
            json.dump(spec, f, indent=2)

    def _export_html(self, interface, output_path: Path):
        """Export as HTML (basic)"""

        html = """<!DOCTYPE html>
<html>
<head>
    <title>Generated Interface</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .component { border: 1px solid #ccc; padding: 10px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>Generated Interface</h1>
"""

        for comp in interface.components:
            html += (
                f'    <div class="component">{comp.name}: {comp.dna.purpose}</div>\n'
            )

        html += """</body>
</html>"""

        with open(output_path, "w") as f:
            f.write(html)

    def _export_python(self, interface, output_path: Path):
        """Export as Python Textual code"""

        code = '''#!/usr/bin/env python3
"""Generated Textual UI Application"""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button
from textual.containers import Vertical

class GeneratedApp(App):
    """Generated interface application"""
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
'''

        for comp in interface.components:
            code += f'            yield Static("{comp.name}")\n'

        code += """        yield Footer()

if __name__ == "__main__":
    app = GeneratedApp()
    app.run()
"""

        with open(output_path, "w") as f:
            f.write(code)


def integrate_with_ask_nix():
    """Integration function for main ask-nix CLI"""

    def add_ui_commands(subparsers):
        """Add UI generation commands to ask-nix"""

        ui_parser = subparsers.add_parser("ui", help="AI-driven interface generation")
        ui_subparsers = ui_parser.add_subparsers(dest="ui_command")

        # Create interface command
        create_parser = ui_subparsers.add_parser(
            "create", help="Create interface from natural language"
        )
        create_parser.add_argument(
            "request", nargs="+", help="Natural language request"
        )
        create_parser.add_argument(
            "--no-preview", action="store_true", help="Skip preview"
        )
        create_parser.add_argument("--user", help="User ID for preferences")

        # Refine interface command
        refine_parser = ui_subparsers.add_parser("refine", help="Refine last interface")
        refine_parser.add_argument("refinement", nargs="+", help="Refinement request")
        refine_parser.add_argument("--id", help="Interface ID to refine")

        # Show interface command
        show_parser = ui_subparsers.add_parser("show", help="Show interface")
        show_parser.add_argument(
            "--last", action="store_true", help="Show last interface"
        )
        show_parser.add_argument("--id", help="Interface ID to show")

        # List interfaces command
        list_parser = ui_subparsers.add_parser("list", help="List saved interfaces")

        # Export interface command
        export_parser = ui_subparsers.add_parser("export", help="Export interface")
        export_parser.add_argument(
            "--format", choices=["json", "html", "python"], default="json"
        )
        export_parser.add_argument("--output", help="Output path")
        export_parser.add_argument("--id", help="Interface ID to export")

        # Statistics command
        stats_parser = ui_subparsers.add_parser(
            "stats", help="Show UI generation statistics"
        )

        return ui_parser

    def handle_ui_command(args):
        """Handle UI generation commands"""

        cli = UIGeneratorCLI()

        if args.ui_command == "create":
            request = " ".join(args.request)
            result = cli.create_interface(
                request=request, user_id=args.user, preview=not args.no_preview
            )

            if result["success"]:
                print("✅ Interface created successfully!")
                print(f"   Components: {result['components']}")
                print(f"   Confidence: {result['confidence']:.0%}")
                print(f"   Time: {result['generation_time']:.2f}ms")
                print(f"   Saved to: {result['spec_path']}")
            else:
                print("❌ Failed to create interface")

        elif args.ui_command == "refine":
            refinement = " ".join(args.refinement)
            result = cli.refine_interface(refinement=refinement, interface_id=args.id)

            if result["success"]:
                print("✅ Interface refined successfully!")
                print(f"   Components: {result['components']}")
            else:
                print(f"❌ {result.get('error', 'Failed to refine')}")

        elif args.ui_command == "show":
            if args.last or not args.id:
                cli.show_last_interface()
            else:
                # Load and show specific interface
                interface = cli._load_interface(args.id)
                if interface:
                    cli.renderer.preview(interface)
                else:
                    print(f"❌ Interface {args.id} not found")

        elif args.ui_command == "list":
            interfaces = cli.list_interfaces()
            if interfaces:
                print("📋 Saved Interfaces:")
                print("-" * 60)
                for intf in interfaces:
                    print(f"ID: {intf['id']}")
                    print(f"   Created: {intf['created']}")
                    print(f"   Request: {intf['request'][:50]}...")
                    print(f"   Components: {intf['components']}")
                    print()
            else:
                print("No interfaces saved yet")

        elif args.ui_command == "export":
            result = cli.export_interface(
                interface_id=args.id, format=args.format, output_path=args.output
            )

            if result["success"]:
                print(f"✅ Exported to: {result['path']}")
            else:
                print(f"❌ {result.get('error', 'Export failed')}")

        elif args.ui_command == "stats":
            stats = cli.get_statistics()

            print("📊 UI Generation Statistics")
            print("=" * 60)

            print("\n🔨 Builder Stats:")
            for key, value in stats["builder"].items():
                print(f"   {key}: {value}")

            if stats["performance"]:
                print("\n⚡ Performance:")
                for key, value in stats["performance"].items():
                    if isinstance(value, float):
                        print(f"   {key}: {value:.2f}")
                    else:
                        print(f"   {key}: {value}")

            print(f"\n📚 Patterns Learned: {stats['patterns_learned']}")
            print(f"🎨 Interfaces Created: {stats['interfaces_created']}")

    return add_ui_commands, handle_ui_command


# Standalone CLI for testing
def main():
    """Main CLI entry point for standalone testing"""

    parser = argparse.ArgumentParser(
        description="AI-Driven Interface Generation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create "dashboard for system metrics"
  %(prog)s refine "make it darker with bigger charts"  
  %(prog)s show --last
  %(prog)s export --format html --output dashboard.html
  %(prog)s stats
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create interface")
    create_parser.add_argument("request", nargs="+", help="Natural language request")
    create_parser.add_argument("--no-preview", action="store_true")

    # Refine command
    refine_parser = subparsers.add_parser("refine", help="Refine interface")
    refine_parser.add_argument("refinement", nargs="+", help="Refinement request")

    # Show command
    show_parser = subparsers.add_parser("show", help="Show last interface")

    # List command
    list_parser = subparsers.add_parser("list", help="List interfaces")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export interface")
    export_parser.add_argument(
        "--format", choices=["json", "html", "python"], default="json"
    )
    export_parser.add_argument("--output", help="Output path")

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = UIGeneratorCLI()

    if args.command == "create":
        request = " ".join(args.request)
        result = cli.create_interface(request, preview=not args.no_preview)

        if result["success"]:
            print("\n✅ Interface created!")
            print(f"Components: {result['components']}")
            print(f"Confidence: {result['confidence']:.0%}")

    elif args.command == "refine":
        refinement = " ".join(args.refinement)
        result = cli.refine_interface(refinement)

        if result["success"]:
            print("\n✅ Interface refined!")

    elif args.command == "show":
        cli.show_last_interface()

    elif args.command == "list":
        interfaces = cli.list_interfaces()
        for intf in interfaces:
            print(
                f"{intf['id']}: {intf['request'][:40]}... ({intf['components']} components)"
            )

    elif args.command == "export":
        result = cli.export_interface(format=args.format, output_path=args.output)

        if result["success"]:
            print(f"✅ Exported to: {result['path']}")

    elif args.command == "stats":
        stats = cli.get_statistics()
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
