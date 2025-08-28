"""
Dependency Resolver - The Thread Weaver

This module resolves plugin dependencies, creating the mycelial network
that connects individual plugins into a living ecosystem.

Following the principle of Sophisticated Simplicity, we start with
the most elegant, mathematical core before adding complexity.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path
import json
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class RelationshipType(Enum):
    """Types of plugin relationships"""
    REQUIRES = "requires"      # Hard dependency - cannot function without
    ENHANCES = "enhances"      # Soft dependency - adds functionality
    COMPLEMENTS = "complements" # Works well together
    EXTENDS = "extends"        # Builds upon another plugin


@dataclass
class PluginDependency:
    """A single dependency relationship"""
    plugin_id: str
    version_constraint: str
    relationship_type: RelationshipType
    rationale: Optional[str] = None
    fallback_behavior: str = "fail"
    
    @property
    def is_required(self) -> bool:
        """Whether this dependency is mandatory"""
        return self.relationship_type == RelationshipType.REQUIRES
    
    @property
    def can_degrade(self) -> bool:
        """Whether plugin can work without this dependency"""
        return self.fallback_behavior in ["degrade", "warn"]


@dataclass
class DependencyGraph:
    """The complete dependency graph for a set of plugins"""
    nodes: Dict[str, Dict]  # plugin_id -> manifest data
    edges: Dict[str, List[PluginDependency]]  # plugin_id -> dependencies
    
    def get_all_dependencies(self, plugin_id: str, 
                            include_optional: bool = False) -> Set[str]:
        """Get all dependencies (recursive) for a plugin"""
        visited = set()
        to_visit = [plugin_id]
        dependencies = set()
        
        while to_visit:
            current = to_visit.pop()
            if current in visited:
                continue
            visited.add(current)
            
            if current in self.edges:
                for dep in self.edges[current]:
                    if dep.is_required or include_optional:
                        dependencies.add(dep.plugin_id)
                        if dep.plugin_id not in visited:
                            to_visit.append(dep.plugin_id)
        
        return dependencies
    
    def has_cycles(self) -> bool:
        """Check if the dependency graph has cycles"""
        # Use DFS with recursion stack to detect cycles
        visited = set()
        rec_stack = set()
        
        def has_cycle_util(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            if node in self.edges:
                for dep in self.edges[node]:
                    if dep.plugin_id not in visited:
                        if has_cycle_util(dep.plugin_id):
                            return True
                    elif dep.plugin_id in rec_stack:
                        return True
            
            rec_stack.remove(node)
            return False
        
        for node in self.nodes:
            if node not in visited:
                if has_cycle_util(node):
                    return True
        return False
    
    def topological_sort(self) -> Optional[List[str]]:
        """
        Return plugins in installation order (dependencies first).
        Returns None if cycles exist.
        """
        if self.has_cycles():
            return None
        
        # Calculate in-degree for each node
        in_degree = {node: 0 for node in self.nodes}
        
        for node in self.edges:
            for dep in self.edges[node]:
                if dep.plugin_id in in_degree:
                    in_degree[dep.plugin_id] += 1
        
        # Queue for nodes with no dependencies
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            # Reduce in-degree for dependent nodes
            for check_node, deps in self.edges.items():
                for dep in deps:
                    if dep.plugin_id == node and check_node in in_degree:
                        in_degree[check_node] -= 1
                        if in_degree[check_node] == 0:
                            queue.append(check_node)
        
        return result if len(result) == len(self.nodes) else None


class DependencyResolver:
    """
    The elegant core of dependency resolution.
    
    This is the "embarrassingly simple" version that delivers
    immediate value before we add complex version resolution.
    """
    
    def __init__(self, plugin_directory: Optional[Path] = None):
        """Initialize the resolver"""
        self.plugin_directory = plugin_directory or Path.home() / ".luminous-nix" / "plugins"
        self.manifests_cache: Dict[str, Dict] = {}
    
    def load_manifest(self, plugin_id: str) -> Optional[Dict]:
        """Load a plugin's manifest"""
        if plugin_id in self.manifests_cache:
            return self.manifests_cache[plugin_id]
        
        manifest_path = self.plugin_directory / plugin_id / "manifest.json"
        if not manifest_path.exists():
            manifest_path = self.plugin_directory / plugin_id / "manifest.yaml"
        
        if manifest_path.exists():
            try:
                if manifest_path.suffix == '.json':
                    with open(manifest_path) as f:
                        manifest = json.load(f)
                else:
                    # YAML support
                    import yaml
                    with open(manifest_path) as f:
                        manifest = yaml.safe_load(f)
                
                self.manifests_cache[plugin_id] = manifest
                return manifest
            except Exception as e:
                logger.error(f"Failed to load manifest for {plugin_id}: {e}")
        
        return None
    
    def resolve_single(self, plugin_id: str) -> List[str]:
        """
        Resolve dependencies for a single plugin.
        Returns list of plugin IDs in installation order.
        
        This is the simple version - just returns the dependency list
        without complex version resolution.
        """
        manifest = self.load_manifest(plugin_id)
        if not manifest:
            return []
        
        dependencies = []
        
        # Check for v2 manifest format
        if 'relationships' in manifest and 'dependencies' in manifest['relationships']:
            for dep in manifest['relationships']['dependencies']:
                if dep.get('relationship_type') == 'requires':
                    dependencies.append(dep['plugin_id'])
        # Fallback to v1 format
        elif 'dependencies' in manifest and 'plugins' in manifest['dependencies']:
            for dep in manifest['dependencies']['plugins']:
                dependencies.append(dep['id'])
        
        # Recursively resolve dependencies
        all_deps = []
        visited = set()
        
        def resolve_recursive(pid: str):
            if pid in visited:
                return
            visited.add(pid)
            
            deps = self.resolve_single(pid)
            for dep in deps:
                if dep not in visited:
                    resolve_recursive(dep)
                    if dep not in all_deps:
                        all_deps.append(dep)
        
        for dep in dependencies:
            resolve_recursive(dep)
        
        return all_deps
    
    def build_graph(self, plugin_ids: List[str]) -> DependencyGraph:
        """Build a complete dependency graph for a set of plugins"""
        nodes = {}
        edges = {}
        
        # Load all manifests
        for plugin_id in plugin_ids:
            manifest = self.load_manifest(plugin_id)
            if manifest:
                nodes[plugin_id] = manifest
                edges[plugin_id] = []
                
                # Parse dependencies
                if 'relationships' in manifest and 'dependencies' in manifest['relationships']:
                    for dep_data in manifest['relationships']['dependencies']:
                        dep = PluginDependency(
                            plugin_id=dep_data['plugin_id'],
                            version_constraint=dep_data.get('version_constraint', '*'),
                            relationship_type=RelationshipType(dep_data.get('relationship_type', 'requires')),
                            rationale=dep_data.get('rationale'),
                            fallback_behavior=dep_data.get('fallback_behavior', 'fail')
                        )
                        edges[plugin_id].append(dep)
                        
                        # Ensure dependency is in nodes
                        if dep.plugin_id not in nodes:
                            dep_manifest = self.load_manifest(dep.plugin_id)
                            if dep_manifest:
                                nodes[dep.plugin_id] = dep_manifest
        
        return DependencyGraph(nodes=nodes, edges=edges)
    
    def check_compatibility(self, plugin_id: str, 
                           installed_plugins: List[str]) -> Tuple[bool, List[str]]:
        """
        Check if a plugin is compatible with installed plugins.
        Returns (is_compatible, list_of_conflicts)
        """
        manifest = self.load_manifest(plugin_id)
        if not manifest:
            return True, []
        
        conflicts = []
        
        # Check for explicit conflicts
        if 'relationships' in manifest and 'conflicts' in manifest['relationships']:
            for conflict in manifest['relationships']['conflicts']:
                if conflict['plugin_id'] in installed_plugins:
                    conflicts.append(f"{conflict['plugin_id']}: {conflict.get('reason', 'Unknown conflict')}")
        
        return len(conflicts) == 0, conflicts
    
    def suggest_companions(self, plugin_id: str) -> List[Dict[str, str]]:
        """
        Suggest companion plugins that work well with this one.
        Returns list of {plugin_id, synergy} dicts.
        """
        manifest = self.load_manifest(plugin_id)
        if not manifest:
            return []
        
        companions = []
        
        if 'relationships' in manifest and 'companions' in manifest['relationships']:
            for comp in manifest['relationships']['companions']:
                companions.append({
                    'plugin_id': comp['plugin_id'],
                    'synergy': comp.get('synergy', 'Works well together')
                })
        
        return companions


class NixDependencyResolver(DependencyResolver):
    """
    Extended resolver that generates Nix expressions for dependencies.
    This is the bridge to leverage Nix's powerful dependency resolution.
    """
    
    def generate_nix_expression(self, plugin_ids: List[str]) -> str:
        """
        Generate a Nix expression that describes the plugin environment.
        Nix will handle the actual version resolution.
        """
        graph = self.build_graph(plugin_ids)
        
        if graph.has_cycles():
            raise ValueError("Circular dependencies detected!")
        
        # Get installation order
        install_order = graph.topological_sort()
        if not install_order:
            raise ValueError("Could not determine installation order")
        
        # Generate Nix expression
        nix_expr = """
{ pkgs ? import <nixpkgs> {} }:

let
  luminous-plugins = {
"""
        
        for plugin_id in install_order:
            manifest = graph.nodes.get(plugin_id, {})
            plugin_data = manifest.get('plugin', {})
            
            nix_expr += f"""
    {plugin_id.replace('-', '_')} = {{
      name = "{plugin_data.get('name', plugin_id)}";
      version = "{plugin_data.get('version', '0.0.0')}";
      dependencies = [
"""
            
            if plugin_id in graph.edges:
                for dep in graph.edges[plugin_id]:
                    if dep.is_required:
                        nix_expr += f'        luminous-plugins.{dep.plugin_id.replace("-", "_")}\n'
            
            nix_expr += """      ];
    };
"""
        
        nix_expr += """  };
in
  luminous-plugins
"""
        
        return nix_expr


# Example usage and testing
if __name__ == "__main__":
    # Create a simple test
    resolver = DependencyResolver()
    
    # Test single plugin resolution
    deps = resolver.resolve_single("pomodoro-timer")
    print(f"Dependencies for pomodoro-timer: {deps}")
    
    # Test graph building
    graph = resolver.build_graph(["pomodoro-timer", "flow-guardian"])
    print(f"Graph has cycles: {graph.has_cycles()}")
    
    if not graph.has_cycles():
        order = graph.topological_sort()
        print(f"Installation order: {order}")
    
    # Test Nix expression generation
    nix_resolver = NixDependencyResolver()
    try:
        nix_expr = nix_resolver.generate_nix_expression(["pomodoro-timer"])
        print(f"Generated Nix expression:\n{nix_expr}")
    except ValueError as e:
        print(f"Error: {e}")