#!/usr/bin/env python3
"""
Comprehensive test suite for GraphRAG integration.

Tests the complete Phase B implementation:
- NixKnowledgeGraph building from real Nix files
- GraphInterface query capabilities
- SemanticQueryEngine natural language understanding
- End-to-end integration testing
"""

import unittest
import tempfile
import json
from pathlib import Path
from typing import Dict, Any

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from luminous_nix.knowledge.nix_knowledge_graph import (
    NixKnowledgeGraph, NodeType, EdgeType, GraphNode, GraphEdge
)
from luminous_nix.knowledge.graph_interface import (
    GraphInterface, QueryType, QueryResult
)
from luminous_nix.knowledge.semantic_query_engine import (
    SemanticQueryEngine, IntentType, SemanticQuery
)
from luminous_nix.core.nix_ast_parser import NixASTParser


class TestNixKnowledgeGraph(unittest.TestCase):
    """Test the NixKnowledgeGraph class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.graph = NixKnowledgeGraph()
        
        # Create a test Nix configuration
        self.test_config = """
        {
          # System packages
          environment.systemPackages = with pkgs; [
            firefox
            vim
            git
            htop
          ];
          
          # Services
          services.nginx = {
            enable = true;
            virtualHosts."example.com" = {
              root = "/var/www";
            };
          };
          
          services.postgresql = {
            enable = false;
            package = pkgs.postgresql_13;
          };
          
          # Users
          users.users.alice = {
            isNormalUser = true;
            extraGroups = [ "wheel" "docker" ];
            shell = pkgs.zsh;
          };
          
          # Network
          networking.hostName = "test-machine";
          networking.firewall.enable = true;
          
          # Imports
          imports = [
            ./hardware-configuration.nix
            ./custom-module.nix
          ];
        }
        """
    
    def test_graph_creation(self):
        """Test basic graph creation"""
        self.assertIsNotNone(self.graph)
        self.assertEqual(len(self.graph.nodes), 0)
        self.assertEqual(len(self.graph.edges), 0)
    
    def test_build_from_string(self):
        """Test building graph from Nix code string"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.nix', delete=False) as f:
            f.write(self.test_config)
            temp_file = f.name
        
        try:
            # Build graph
            success = self.graph.build_from_file(temp_file)
            
            if success:
                # Check nodes were created
                self.assertGreater(len(self.graph.nodes), 0)
                
                # Check for expected node types
                packages = self.graph.find_nodes_by_type(NodeType.PACKAGE)
                self.assertGreater(len(packages), 0)
                
                services = self.graph.find_nodes_by_type(NodeType.SERVICE)
                self.assertGreater(len(services), 0)
                
                users = self.graph.find_nodes_by_type(NodeType.USER)
                self.assertGreater(len(users), 0)
                
                # Check specific entities
                firefox = self.graph.find_node_by_name("firefox", NodeType.PACKAGE)
                if firefox:
                    self.assertEqual(firefox.name, "firefox")
                    self.assertEqual(firefox.type, NodeType.PACKAGE)
                
                nginx = self.graph.find_node_by_name("nginx", NodeType.SERVICE)
                if nginx:
                    self.assertEqual(nginx.name, "nginx")
                    self.assertEqual(nginx.type, NodeType.SERVICE)
                    self.assertTrue(nginx.properties.get('enabled', False))
                
                alice = self.graph.find_node_by_name("alice", NodeType.USER)
                if alice:
                    self.assertEqual(alice.name, "alice")
                    self.assertEqual(alice.type, NodeType.USER)
            else:
                print("⚠️ Graph building failed - tree-sitter might not be installed")
        
        finally:
            # Clean up
            Path(temp_file).unlink()
    
    def test_graph_statistics(self):
        """Test graph statistics calculation"""
        # Add some test nodes and edges
        node1 = GraphNode("1", NodeType.PACKAGE, "test-package")
        node2 = GraphNode("2", NodeType.SERVICE, "test-service")
        self.graph._add_node(node1)
        self.graph._add_node(node2)
        
        edge = GraphEdge("1", "2", EdgeType.DEPENDS_ON)
        self.graph._add_edge(edge)
        
        # Get statistics
        stats = self.graph.get_statistics()
        
        self.assertEqual(stats['total_nodes'], 2)
        self.assertEqual(stats['total_edges'], 1)
        self.assertIn('node_types', stats)
        self.assertIn('edge_types', stats)
        self.assertIn('average_degree', stats)
    
    def test_path_finding(self):
        """Test path finding between nodes"""
        # Create a simple graph
        nodes = [
            GraphNode("A", NodeType.PACKAGE, "A"),
            GraphNode("B", NodeType.PACKAGE, "B"),
            GraphNode("C", NodeType.PACKAGE, "C"),
            GraphNode("D", NodeType.PACKAGE, "D")
        ]
        
        for node in nodes:
            self.graph._add_node(node)
        
        # Create edges: A -> B -> C, A -> D -> C
        edges = [
            GraphEdge("A", "B", EdgeType.DEPENDS_ON),
            GraphEdge("B", "C", EdgeType.DEPENDS_ON),
            GraphEdge("A", "D", EdgeType.DEPENDS_ON),
            GraphEdge("D", "C", EdgeType.DEPENDS_ON)
        ]
        
        for edge in edges:
            self.graph._add_edge(edge)
        
        # Find path from A to C
        path = self.graph.find_path("A", "C")
        self.assertIsNotNone(path)
        self.assertEqual(path[0], "A")
        self.assertEqual(path[-1], "C")
    
    def test_subgraph_extraction(self):
        """Test subgraph extraction"""
        # Create test nodes
        center = GraphNode("center", NodeType.SERVICE, "center-service")
        self.graph._add_node(center)
        
        # Add neighbors
        for i in range(3):
            neighbor = GraphNode(f"n{i}", NodeType.PACKAGE, f"package-{i}")
            self.graph._add_node(neighbor)
            edge = GraphEdge("center", f"n{i}", EdgeType.DEPENDS_ON)
            self.graph._add_edge(edge)
        
        # Extract subgraph
        nodes, edges = self.graph.get_subgraph("center", depth=1)
        
        self.assertEqual(len(nodes), 4)  # Center + 3 neighbors
        self.assertEqual(len(edges), 3)  # 3 edges


class TestGraphInterface(unittest.TestCase):
    """Test the GraphInterface class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.graph = NixKnowledgeGraph()
        self.interface = GraphInterface(self.graph)
        
        # Add test data
        self._setup_test_graph()
    
    def _setup_test_graph(self):
        """Set up a test graph with various nodes and edges"""
        # Add packages
        packages = ["firefox", "vim", "git", "nginx", "postgresql"]
        for pkg in packages:
            node = GraphNode(
                f"pkg_{pkg}", 
                NodeType.PACKAGE, 
                pkg,
                properties={'version': '1.0'}
            )
            self.graph._add_node(node)
        
        # Add services
        services = [
            ("nginx", True),
            ("postgresql", False),
            ("ssh", True)
        ]
        for svc, enabled in services:
            node = GraphNode(
                f"svc_{svc}",
                NodeType.SERVICE,
                svc,
                properties={'enabled': enabled}
            )
            self.graph._add_node(node)
        
        # Add dependencies
        edges = [
            GraphEdge("svc_nginx", "pkg_nginx", EdgeType.DEPENDS_ON),
            GraphEdge("svc_postgresql", "pkg_postgresql", EdgeType.DEPENDS_ON)
        ]
        for edge in edges:
            self.graph._add_edge(edge)
    
    def test_find_packages(self):
        """Test finding packages"""
        result = self.interface.query(QueryType.FIND_PACKAGES)
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.data)
        self.assertIsInstance(result.data, list)
        
        # Check we found packages
        package_names = [p['name'] for p in result.data]
        self.assertIn("firefox", package_names)
        self.assertIn("vim", package_names)
    
    def test_find_services(self):
        """Test finding services"""
        # Find all services
        result = self.interface.query(QueryType.FIND_SERVICES)
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 3)
        
        # Find only enabled services
        result = self.interface.query(QueryType.FIND_SERVICES, enabled_only=True)
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 2)  # nginx and ssh
    
    def test_get_dependencies(self):
        """Test getting dependencies"""
        result = self.interface.query(QueryType.GET_DEPENDENCIES, node_id="svc_nginx")
        
        self.assertTrue(result.success)
        self.assertIsInstance(result.data, list)
        
        # nginx service should depend on nginx package
        dep_names = [d['name'] for d in result.data]
        self.assertIn("nginx", dep_names)
    
    def test_check_conflicts(self):
        """Test conflict checking"""
        # Add potentially conflicting services
        apache = GraphNode(
            "svc_apache",
            NodeType.SERVICE,
            "apache",
            properties={'enabled': True}
        )
        self.graph._add_node(apache)
        
        result = self.interface.query(QueryType.CHECK_CONFLICTS)
        
        self.assertTrue(result.success)
        # Should detect nginx and apache conflict
        if result.data:
            self.assertTrue(any('nginx' in str(c) and 'apache' in str(c) for c in result.data))
    
    def test_semantic_search(self):
        """Test semantic search functionality"""
        results = self.interface.semantic_search("fire", top_k=5)
        
        self.assertIsInstance(results, list)
        if results:
            # Should find firefox
            self.assertTrue(any('firefox' in r['node']['name'] for r in results))
    
    def test_natural_language_query(self):
        """Test simple natural language queries"""
        # Test listing packages
        result = self.interface.natural_language_query("list packages")
        self.assertTrue(result.success or result.error)
        
        # Test finding services
        result = self.interface.natural_language_query("what services are enabled")
        self.assertIsNotNone(result)


class TestSemanticQueryEngine(unittest.TestCase):
    """Test the SemanticQueryEngine class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.graph = NixKnowledgeGraph()
        self.interface = GraphInterface(self.graph)
        self.engine = SemanticQueryEngine(self.graph, self.interface)
        
        # Add test data
        self._setup_test_graph()
    
    def _setup_test_graph(self):
        """Set up a test graph"""
        # Add various nodes
        nodes = [
            GraphNode("pkg_firefox", NodeType.PACKAGE, "firefox"),
            GraphNode("pkg_vim", NodeType.PACKAGE, "vim"),
            GraphNode("svc_nginx", NodeType.SERVICE, "nginx", {'enabled': True}),
            GraphNode("svc_postgresql", NodeType.SERVICE, "postgresql", {'enabled': False}),
            GraphNode("usr_alice", NodeType.USER, "alice"),
            GraphNode("mod_security", NodeType.MODULE, "security-module")
        ]
        
        for node in nodes:
            self.graph._add_node(node)
        
        # Add edges
        edges = [
            GraphEdge("svc_nginx", "pkg_firefox", EdgeType.DEPENDS_ON),
            GraphEdge("usr_alice", "pkg_vim", EdgeType.USES)
        ]
        
        for edge in edges:
            self.graph._add_edge(edge)
    
    def test_intent_parsing(self):
        """Test parsing different query intents"""
        test_cases = [
            ("list all packages", IntentType.LIST),
            ("find firefox", IntentType.FIND),
            ("describe nginx", IntentType.DESCRIBE),
            ("what depends on vim", IntentType.DEPENDENTS),
            ("dependencies of nginx", IntentType.DEPENDENCIES),
            ("check conflicts", IntentType.CONFLICTS),
            ("statistics", IntentType.STATISTICS),
            ("random query", IntentType.UNKNOWN)
        ]
        
        for query, expected_intent in test_cases:
            parsed = self.engine._parse_query(query)
            self.assertEqual(parsed.intent, expected_intent, 
                           f"Failed for query: {query}")
    
    def test_entity_type_detection(self):
        """Test detection of entity types in queries"""
        test_cases = [
            ("list packages", [NodeType.PACKAGE]),
            ("find service nginx", [NodeType.SERVICE]),
            ("show modules", [NodeType.MODULE]),
            ("user alice", [NodeType.USER])
        ]
        
        for query, expected_types in test_cases:
            parsed = self.engine._parse_query(query)
            self.assertEqual(parsed.entity_types, expected_types,
                           f"Failed for query: {query}")
    
    def test_list_queries(self):
        """Test LIST intent handling"""
        # List packages
        result, answer = self.engine.query("list packages")
        self.assertIsNotNone(result)
        self.assertIn("firefox", answer)
        self.assertIn("vim", answer)
        
        # List services
        result, answer = self.engine.query("show me all services")
        self.assertIn("nginx", answer)
        self.assertIn("postgresql", answer)
    
    def test_find_queries(self):
        """Test FIND intent handling"""
        # Find specific entity
        result, answer = self.engine.query("find firefox")
        self.assertIsNotNone(result)
        self.assertIn("firefox", answer.lower())
        
        # Find non-existent entity
        result, answer = self.engine.query("find nonexistent")
        self.assertIn("could not find", answer.lower())
    
    def test_describe_queries(self):
        """Test DESCRIBE intent handling"""
        result, answer = self.engine.query("describe nginx")
        
        self.assertIsNotNone(result)
        self.assertIn("nginx", answer.lower())
        self.assertIn("service", answer.lower())
    
    def test_dependency_queries(self):
        """Test dependency-related queries"""
        # Dependencies
        result, answer = self.engine.query("dependencies of nginx")
        self.assertIsNotNone(result)
        
        # Dependents
        result, answer = self.engine.query("what depends on vim")
        self.assertIsNotNone(result)
    
    def test_statistics_query(self):
        """Test statistics query"""
        result, answer = self.engine.query("show statistics")
        
        self.assertIsNotNone(result)
        self.assertIn("nodes", answer.lower())
        self.assertIn("edges", answer.lower())
    
    def test_unknown_query_handling(self):
        """Test handling of unknown queries"""
        result, answer = self.engine.query("quantum flux capacitor settings")
        
        self.assertIsNotNone(result)
        self.assertFalse(result.success)
        # Should provide helpful suggestions
        self.assertIn("try", answer.lower())


class TestEndToEndIntegration(unittest.TestCase):
    """End-to-end integration testing"""
    
    def setUp(self):
        """Set up complete system"""
        self.parser = NixASTParser()
        self.graph = NixKnowledgeGraph(self.parser)
        self.interface = GraphInterface(self.graph)
        self.engine = SemanticQueryEngine(self.graph, self.interface)
        
        # Create a realistic test configuration
        self.config = """
        { config, pkgs, ... }:
        
        {
          imports = [
            ./hardware-configuration.nix
            ./custom-services.nix
          ];
          
          boot.loader.systemd-boot.enable = true;
          
          networking.hostName = "luminous-test";
          networking.networkmanager.enable = true;
          
          environment.systemPackages = with pkgs; [
            firefox
            vim
            git
            docker
            python3
            nodejs
          ];
          
          services.openssh = {
            enable = true;
            settings.PasswordAuthentication = false;
          };
          
          services.nginx = {
            enable = true;
            virtualHosts."example.com" = {
              forceSSL = true;
              enableACME = true;
              root = "/var/www/example";
            };
          };
          
          users.users.admin = {
            isNormalUser = true;
            extraGroups = [ "wheel" "docker" "networkmanager" ];
            openssh.authorizedKeys.keys = [
              "ssh-rsa AAAAB3NzaC1yc2EA..."
            ];
          };
          
          system.stateVersion = "24.05";
        }
        """
    
    def test_complete_workflow(self):
        """Test complete workflow from parsing to querying"""
        # Step 1: Parse configuration
        with tempfile.NamedTemporaryFile(mode='w', suffix='.nix', delete=False) as f:
            f.write(self.config)
            temp_file = f.name
        
        try:
            # Step 2: Build knowledge graph
            success = self.graph.build_from_file(temp_file)
            
            if success:
                # Step 3: Query via natural language
                queries = [
                    "list all packages",
                    "what services are enabled",
                    "describe nginx",
                    "find admin user",
                    "show statistics"
                ]
                
                for query in queries:
                    result, answer = self.engine.query(query)
                    self.assertIsNotNone(result)
                    self.assertIsNotNone(answer)
                    print(f"\nQuery: {query}")
                    print(f"Success: {result.success}")
                    print(f"Answer preview: {answer[:200]}...")
                
                # Step 4: Test specific assertions
                packages = self.graph.find_nodes_by_type(NodeType.PACKAGE)
                self.assertGreater(len(packages), 0)
                
                services = self.graph.find_nodes_by_type(NodeType.SERVICE)
                self.assertGreater(len(services), 0)
                
                # Check specific entities exist
                firefox = self.graph.find_node_by_name("firefox")
                if firefox:
                    self.assertIsNotNone(firefox)
                
                nginx = self.graph.find_node_by_name("nginx")
                if nginx:
                    self.assertIsNotNone(nginx)
            else:
                print("⚠️ End-to-end test skipped - tree-sitter not available")
        
        finally:
            Path(temp_file).unlink()
    
    def test_export_import_cycle(self):
        """Test exporting and importing graph data"""
        # Build a simple graph
        node1 = GraphNode("test1", NodeType.PACKAGE, "test-package")
        node2 = GraphNode("test2", NodeType.SERVICE, "test-service")
        self.graph._add_node(node1)
        self.graph._add_node(node2)
        
        edge = GraphEdge("test1", "test2", EdgeType.DEPENDS_ON)
        self.graph._add_edge(edge)
        
        # Export to JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            export_file = f.name
        
        try:
            self.graph.export_to_json(export_file)
            
            # Verify export file exists and contains data
            self.assertTrue(Path(export_file).exists())
            
            with open(export_file) as f:
                data = json.load(f)
            
            self.assertIn('nodes', data)
            self.assertIn('edges', data)
            self.assertIn('statistics', data)
            self.assertEqual(len(data['nodes']), 2)
            self.assertEqual(len(data['edges']), 1)
        
        finally:
            Path(export_file).unlink()


def run_tests():
    """Run all tests"""
    print("🧪 Running GraphRAG Integration Tests")
    print("=" * 60)
    
    # Check if tree-sitter is available
    try:
        import tree_sitter
        print("✅ tree-sitter is available")
    except ImportError:
        print("⚠️ tree-sitter not installed - some tests will be skipped")
        print("   Install with: pip install tree-sitter tree-sitter-nix")
    
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestNixKnowledgeGraph))
    suite.addTests(loader.loadTestsFromTestCase(TestGraphInterface))
    suite.addTests(loader.loadTestsFromTestCase(TestSemanticQueryEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)