"""
Plugin management CLI commands.

Provides commands for discovering, installing, managing, and using plugins.
"""

import click
import json
import subprocess
import tempfile
import shutil
import urllib.request
import zipfile
import tarfile
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

# Import plugin system
try:
    from ..plugins.manager import PluginManager
    from ..plugins.base import PluginConfig
    PLUGINS_AVAILABLE = True
except ImportError:
    PLUGINS_AVAILABLE = False
    PluginManager = None
    PluginConfig = None

console = Console()

# Global plugin manager instance
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """Get or create plugin manager singleton."""
    global _plugin_manager
    if _plugin_manager is None:
        if not PLUGINS_AVAILABLE:
            console.print("[red]Plugin system not available[/red]")
            raise click.Abort()
        _plugin_manager = PluginManager()
    return _plugin_manager


@click.group()
def plugins():
    """
    Manage Luminous Nix plugins.

    Plugins extend functionality with custom operations, security checks,
    hooks, and AI integrations.
    """
    pass


@plugins.command()
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON')
@click.option('--type', 'plugin_type', help='Filter by type (operation, security, hook, ai)')
def list(as_json: bool, plugin_type: Optional[str]):
    """
    List all available plugins.

    Shows both installed and discovered plugins with their status.
    """
    if not PLUGINS_AVAILABLE:
        console.print("[red]Plugin system not available. Install required dependencies.[/red]")
        return

    try:
        manager = get_plugin_manager()
        manifests = manager.discover_plugins()

        if as_json:
            # JSON output
            plugin_data = []
            for manifest in manifests:
                # Get type from loaded plugin or infer from capabilities
                plugin_obj = manager.get_plugin(manifest.name)
                if plugin_obj:
                    ptype = plugin_obj.type
                elif manifest.operation_types:
                    ptype = "operation"
                else:
                    ptype = "unknown"

                if plugin_type and ptype != plugin_type:
                    continue

                plugin_data.append({
                    'name': manifest.name,
                    'version': manifest.version,
                    'type': ptype,
                    'description': manifest.description,
                    'author': manifest.author,
                    'loaded': manifest.name in manager._plugins
                })
            print(json.dumps(plugin_data, indent=2))
        else:
            # Rich table output
            if not manifests:
                console.print("[yellow]No plugins found.[/yellow]")
                console.print("\nPlugin discovery paths:")
                for path in manager.config.plugin_paths:
                    console.print(f"  • {path}")
                return

            table = Table(title="Available Plugins")
            table.add_column("Name", style="cyan", no_wrap=True)
            table.add_column("Version", style="green")
            table.add_column("Type", style="yellow")
            table.add_column("Status", style="magenta")
            table.add_column("Description")

            filtered_count = 0
            for manifest in manifests:
                # Get type from loaded plugin or infer from capabilities
                plugin_obj = manager.get_plugin(manifest.name)
                if plugin_obj:
                    ptype = plugin_obj.type
                elif manifest.operation_types:
                    ptype = "operation"
                else:
                    ptype = "unknown"

                # Filter by type if specified
                if plugin_type and ptype != plugin_type:
                    continue

                filtered_count += 1
                status = "✅ Loaded" if manifest.name in manager._plugins else "⚪ Available"
                table.add_row(
                    manifest.name,
                    manifest.version,
                    ptype,
                    status,
                    manifest.description or ""
                )

            if filtered_count == 0 and plugin_type:
                console.print(f"[yellow]No {plugin_type} plugins found.[/yellow]")
                return

            console.print(table)
            console.print(f"\n[dim]Found {len(manifests)} plugin(s)[/dim]")

    except Exception as e:
        console.print(f"[red]Error listing plugins: {e}[/red]")
        raise click.Abort()


@plugins.command()
@click.argument('plugin_name')
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON')
def show(plugin_name: str, as_json: bool):
    """
    Show detailed information about a specific plugin.

    Displays metadata, permissions, dependencies, and more.
    """
    if not PLUGINS_AVAILABLE:
        console.print("[red]Plugin system not available[/red]")
        return

    try:
        manager = get_plugin_manager()

        # Find plugin manifest
        manifest = manager.discovery.find_plugin(plugin_name)
        if not manifest:
            console.print(f"[red]Plugin '{plugin_name}' not found[/red]")
            return

        # Get type from loaded plugin or infer from capabilities
        plugin_obj = manager.get_plugin(manifest.name)
        if plugin_obj:
            ptype = plugin_obj.type
        elif manifest.operation_types:
            ptype = "operation"
        else:
            ptype = "unknown"

        if as_json:
            # JSON output
            data = {
                'name': manifest.name,
                'version': manifest.version,
                'type': ptype,
                'description': manifest.description,
                'author': manifest.author,
                'license': manifest.license,
                'permissions': manifest.requires_permissions,
                'dependencies': manifest.dependencies,
                'entry_point': f"{manifest.entry_point_module}:{manifest.entry_point_class}",
                'loaded': manifest.name in manager._plugins
            }
            print(json.dumps(data, indent=2))
        else:
            # Rich panel output
            is_loaded = manifest.name in manager._plugins
            status_emoji = "✅" if is_loaded else "⚪"

            info_text = f"""[bold cyan]{manifest.name}[/bold cyan] {manifest.version}

[bold]Type:[/bold] {ptype}
[bold]Author:[/bold] {manifest.author or 'Unknown'}
[bold]License:[/bold] {manifest.license or 'Unknown'}
[bold]Status:[/bold] {status_emoji} {'Loaded' if is_loaded else 'Not loaded'}

[bold]Description:[/bold]
{manifest.description or 'No description provided'}

[bold]Permissions:[/bold]
{', '.join(manifest.requires_permissions) if manifest.requires_permissions else 'None'}

[bold]Dependencies:[/bold]
{', '.join(manifest.dependencies) if manifest.dependencies else 'None'}

[bold]Entry Point:[/bold]
{manifest.entry_point_module}:{manifest.entry_point_class}
"""
            console.print(Panel(info_text, title=f"Plugin: {manifest.name}", border_style="cyan"))

    except Exception as e:
        console.print(f"[red]Error showing plugin: {e}[/red]")
        raise click.Abort()


@plugins.command()
@click.argument('source')
@click.option('--name', help='Custom plugin name (default: from manifest)')
@click.option('--enable', 'auto_enable', is_flag=True, help='Enable plugin after installation')
def install(source: str, name: Optional[str], auto_enable: bool):
    """
    Install a plugin from URL, Git repository, or local path.

    SOURCE can be:
      - Git repository URL (https://github.com/user/plugin.git)
      - Archive URL (.zip, .tar.gz)
      - Local directory path

    Examples:
      ask-nix plugins install https://github.com/luminous/docker-plugin.git
      ask-nix plugins install ./my-local-plugin
      ask-nix plugins install https://example.com/plugin.zip --enable
    """
    if not PLUGINS_AVAILABLE:
        console.print("[red]Plugin system not available[/red]")
        return

    try:
        manager = get_plugin_manager()

        # Determine user plugin directory
        user_plugin_dir = Path.home() / ".local/share/luminous-nix/plugins"
        user_plugin_dir.mkdir(parents=True, exist_ok=True)

        console.print(f"[cyan]Installing plugin from {source}...[/cyan]")

        # Create temporary directory for download/extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            plugin_dir = None

            # Detect source type and download
            if source.startswith(('http://', 'https://')):
                if source.endswith('.git') or 'github.com' in source or 'gitlab.com' in source:
                    # Git repository
                    console.print("[dim]Detected Git repository[/dim]")
                    try:
                        subprocess.run(
                            ['git', 'clone', '--depth', '1', source, str(temp_path / 'plugin')],
                            check=True,
                            capture_output=True,
                            text=True
                        )
                        plugin_dir = temp_path / 'plugin'
                    except subprocess.CalledProcessError as e:
                        console.print(f"[red]Git clone failed: {e.stderr}[/red]")
                        raise click.Abort()
                elif source.endswith(('.zip', '.tar.gz', '.tgz', '.tar')):
                    # Archive download
                    console.print("[dim]Detected archive download[/dim]")
                    archive_path = temp_path / 'plugin_archive'
                    try:
                        urllib.request.urlretrieve(source, archive_path)
                    except Exception as e:
                        console.print(f"[red]Download failed: {e}[/red]")
                        raise click.Abort()

                    # Extract archive
                    extract_dir = temp_path / 'extracted'
                    extract_dir.mkdir()
                    try:
                        if source.endswith('.zip'):
                            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                                zip_ref.extractall(extract_dir)
                        else:  # tar.gz, tgz, tar
                            with tarfile.open(archive_path, 'r:*') as tar_ref:
                                tar_ref.extractall(extract_dir)

                        # Find the plugin directory (might be in subdirectory)
                        extracted_items = list(extract_dir.iterdir())
                        if len(extracted_items) == 1 and extracted_items[0].is_dir():
                            plugin_dir = extracted_items[0]
                        else:
                            plugin_dir = extract_dir
                    except Exception as e:
                        console.print(f"[red]Extraction failed: {e}[/red]")
                        raise click.Abort()
                else:
                    console.print(f"[red]Unsupported URL format. Use .git, .zip, or .tar.gz[/red]")
                    raise click.Abort()
            else:
                # Local path
                console.print("[dim]Detected local path[/dim]")
                local_path = Path(source).resolve()
                if not local_path.exists():
                    console.print(f"[red]Local path does not exist: {source}[/red]")
                    raise click.Abort()
                if not local_path.is_dir():
                    console.print(f"[red]Path is not a directory: {source}[/red]")
                    raise click.Abort()
                plugin_dir = local_path

            # Validate plugin structure
            if not plugin_dir:
                console.print("[red]Failed to locate plugin directory[/red]")
                raise click.Abort()

            manifest_path = plugin_dir / 'plugin.toml'
            if not manifest_path.exists():
                console.print(f"[red]Invalid plugin: missing plugin.toml[/red]")
                console.print(f"[dim]Looked in: {plugin_dir}[/dim]")
                raise click.Abort()

            # Parse manifest to get plugin name
            try:
                try:
                    import tomllib  # Python 3.11+
                except ImportError:
                    import tomli as tomllib  # Fallback for older Python

                with open(manifest_path, 'rb') as f:
                    manifest_data = tomllib.load(f)
                plugin_name = name or manifest_data.get('plugin', {}).get('name')
                if not plugin_name:
                    console.print("[red]Plugin manifest missing 'name' field[/red]")
                    raise click.Abort()
            except Exception as e:
                console.print(f"[red]Failed to parse plugin.toml: {e}[/red]")
                raise click.Abort()

            # Check if plugin already exists
            dest_dir = user_plugin_dir / plugin_name
            if dest_dir.exists():
                console.print(f"[yellow]Plugin '{plugin_name}' already exists. Removing old version...[/yellow]")
                shutil.rmtree(dest_dir)

            # Copy plugin to user directory
            console.print(f"[dim]Installing to {dest_dir}[/dim]")
            shutil.copytree(plugin_dir, dest_dir)

            console.print(f"[green]✅ Plugin '{plugin_name}' installed successfully![/green]")
            console.print(f"[dim]Location: {dest_dir}[/dim]")

            # Re-discover plugins to make it available
            manager.discover_plugins()

            # Auto-enable if requested
            if auto_enable:
                try:
                    with console.status(f"[cyan]Enabling plugin '{plugin_name}'...[/cyan]"):
                        plugin = manager.load_plugin(plugin_name)
                    console.print(f"[green]✅ Plugin '{plugin_name}' enabled![/green]")
                except Exception as e:
                    console.print(f"[yellow]Installation successful but enable failed: {e}[/yellow]")
                    console.print(f"[dim]You can enable it later with: ask-nix plugins enable {plugin_name}[/dim]")
            else:
                console.print(f"\n[dim]To enable: ask-nix plugins enable {plugin_name}[/dim]")

    except click.Abort:
        raise
    except Exception as e:
        console.print(f"[red]Error installing plugin: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise click.Abort()


@plugins.command()
@click.argument('plugin_name')
def enable(plugin_name: str):
    """
    Enable (load) a plugin.

    Makes the plugin available for use.
    """
    if not PLUGINS_AVAILABLE:
        console.print("[red]Plugin system not available[/red]")
        return

    try:
        manager = get_plugin_manager()

        # Check if already loaded
        if manager.get_plugin(plugin_name):
            console.print(f"[yellow]Plugin '{plugin_name}' is already loaded[/yellow]")
            return

        with console.status(f"[cyan]Loading plugin '{plugin_name}'...[/cyan]"):
            plugin = manager.load_plugin(plugin_name)

        # Get permissions from metadata
        permissions = plugin.metadata.requires_permissions if hasattr(plugin, 'metadata') and hasattr(plugin.metadata, 'requires_permissions') else []

        console.print(f"[green]✅ Plugin '{plugin_name}' enabled successfully![/green]")
        console.print(f"[dim]Type: {plugin.type} | Permissions: {', '.join(permissions) if permissions else 'None'}[/dim]")

    except Exception as e:
        console.print(f"[red]Error enabling plugin: {e}[/red]")
        raise click.Abort()


@plugins.command()
@click.argument('plugin_name')
def disable(plugin_name: str):
    """
    Disable (unload) a plugin.

    Removes the plugin from active use.
    """
    if not PLUGINS_AVAILABLE:
        console.print("[red]Plugin system not available[/red]")
        return

    try:
        manager = get_plugin_manager()

        # Check if loaded
        if not manager.get_plugin(plugin_name):
            console.print(f"[yellow]Plugin '{plugin_name}' is not loaded[/yellow]")
            return

        with console.status(f"[cyan]Unloading plugin '{plugin_name}'...[/cyan]"):
            manager.unload_plugin(plugin_name)

        console.print(f"[green]✅ Plugin '{plugin_name}' disabled successfully![/green]")

    except Exception as e:
        console.print(f"[red]Error disabling plugin: {e}[/red]")
        raise click.Abort()


@plugins.command()
@click.argument('plugin_name')
def reload(plugin_name: str):
    """
    Reload a plugin.

    Useful for development - reloads plugin code without restarting.
    """
    if not PLUGINS_AVAILABLE:
        console.print("[red]Plugin system not available[/red]")
        return

    try:
        manager = get_plugin_manager()

        with console.status(f"[cyan]Reloading plugin '{plugin_name}'...[/cyan]"):
            plugin = manager.reload_plugin(plugin_name)

        console.print(f"[green]✅ Plugin '{plugin_name}' reloaded successfully![/green]")
        console.print(f"[dim]Type: {plugin.type} | Version: {plugin.version}[/dim]")

    except Exception as e:
        console.print(f"[red]Error reloading plugin: {e}[/red]")
        raise click.Abort()


@plugins.command()
def status():
    """
    Show plugin system status.

    Displays loaded plugins, available plugins, and system health.
    """
    if not PLUGINS_AVAILABLE:
        console.print("[red]Plugin system not available[/red]")
        return

    try:
        manager = get_plugin_manager()
        manifests = manager.discover_plugins()
        loaded = manager._plugins

        # Summary panel
        summary = f"""[bold]Plugin System Status[/bold]

[bold cyan]Discovered Plugins:[/bold cyan] {len(manifests)}
[bold green]Loaded Plugins:[/bold green] {len(loaded)}

[bold]Loaded by Type:[/bold]
  • Operation: {len(manager.get_operation_plugins())}
  • Security: {len(manager.get_security_plugins())}
  • Hook: {len(manager.get_hook_plugins())}
  • AI: {len(manager.get_ai_plugins())}

[bold]Discovery Paths:[/bold]
"""
        for path in manager.config.plugin_paths:
            summary += f"  • {path}\n"

        console.print(Panel(summary, border_style="cyan"))

        # List currently loaded plugins
        if loaded:
            console.print("\n[bold]Currently Loaded:[/bold]")
            for name, plugin in loaded.items():
                console.print(f"  [green]✅[/green] {name} ({plugin.type})")

    except Exception as e:
        console.print(f"[red]Error getting status: {e}[/red]")
        raise click.Abort()


@plugins.command()
def paths():
    """
    Show plugin discovery paths.

    Lists all directories where plugins are searched.
    """
    if not PLUGINS_AVAILABLE:
        console.print("[red]Plugin system not available[/red]")
        return

    try:
        manager = get_plugin_manager()

        console.print("[bold]Plugin Discovery Paths:[/bold]\n")
        for i, path in enumerate(manager.config.plugin_paths, 1):
            path_obj = Path(path)
            exists = path_obj.exists()
            status = "[green]✓[/green]" if exists else "[red]✗[/red]"
            console.print(f"{status} {i}. {path}")
            if exists and path_obj.is_dir():
                # Count plugins in this directory
                try:
                    plugin_count = len(list(path_obj.iterdir()))
                    console.print(f"   [dim]({plugin_count} items)[/dim]")
                except:
                    pass

    except Exception as e:
        console.print(f"[red]Error listing paths: {e}[/red]")
        raise click.Abort()


@plugins.group()
def autoload():
    """
    Manage auto-load plugins.

    Auto-load plugins are automatically loaded when Luminous Nix starts.
    """
    pass


@autoload.command('add')
@click.argument('plugin_name')
def autoload_add(plugin_name: str):
    """
    Add a plugin to auto-load list.

    The plugin will be automatically loaded on startup.
    """
    if not PLUGINS_AVAILABLE:
        console.print("[red]Plugin system not available[/red]")
        return

    try:
        manager = get_plugin_manager()

        # Check if plugin exists
        manifest = manager.discovery.find_plugin(plugin_name)
        if not manifest:
            console.print(f"[red]Plugin '{plugin_name}' not found[/red]")
            console.print("[dim]Use 'ask-nix plugins list' to see available plugins[/dim]")
            return

        # Add to autoload
        added = manager.config_manager.add_to_autoload(plugin_name)

        if added:
            console.print(f"[green]✅ Added '{plugin_name}' to auto-load list[/green]")
            console.print(f"[dim]Plugin will load automatically on next startup[/dim]")
        else:
            console.print(f"[yellow]Plugin '{plugin_name}' already in auto-load list[/yellow]")

    except Exception as e:
        console.print(f"[red]Error adding to auto-load: {e}[/red]")
        raise click.Abort()


@autoload.command('remove')
@click.argument('plugin_name')
def autoload_remove(plugin_name: str):
    """
    Remove a plugin from auto-load list.

    The plugin will no longer load automatically on startup.
    """
    if not PLUGINS_AVAILABLE:
        console.print("[red]Plugin system not available[/red]")
        return

    try:
        manager = get_plugin_manager()

        # Remove from autoload
        removed = manager.config_manager.remove_from_autoload(plugin_name)

        if removed:
            console.print(f"[green]✅ Removed '{plugin_name}' from auto-load list[/green]")
            console.print(f"[dim]Plugin will not load automatically on next startup[/dim]")
        else:
            console.print(f"[yellow]Plugin '{plugin_name}' not in auto-load list[/yellow]")

    except Exception as e:
        console.print(f"[red]Error removing from auto-load: {e}[/red]")
        raise click.Abort()


@autoload.command('list')
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON')
def autoload_list(as_json: bool):
    """
    List plugins in auto-load list.

    Shows which plugins will be automatically loaded on startup.
    """
    if not PLUGINS_AVAILABLE:
        console.print("[red]Plugin system not available[/red]")
        return

    try:
        manager = get_plugin_manager()
        autoload_plugins = manager.config_manager.get_autoload_plugins()

        if as_json:
            print(json.dumps(autoload_plugins, indent=2))
        else:
            if not autoload_plugins:
                console.print("[yellow]No plugins in auto-load list[/yellow]")
                console.print("\n[dim]Add plugins with: ask-nix plugins autoload add <name>[/dim]")
                return

            console.print(f"[bold]Auto-Load Plugins ({len(autoload_plugins)}):[/bold]\n")
            for plugin_name in autoload_plugins:
                # Check if plugin exists
                manifest = manager.discovery.find_plugin(plugin_name)
                if manifest:
                    console.print(f"  [green]✓[/green] {plugin_name} [dim](v{manifest.version})[/dim]")
                else:
                    console.print(f"  [red]✗[/red] {plugin_name} [dim](not found)[/dim]")

            console.print(f"\n[dim]These plugins will load automatically on startup[/dim]")

    except Exception as e:
        console.print(f"[red]Error listing auto-load plugins: {e}[/red]")
        raise click.Abort()


# Export the group
__all__ = ['plugins']
