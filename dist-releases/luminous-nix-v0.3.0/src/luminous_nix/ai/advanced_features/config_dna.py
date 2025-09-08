#!/usr/bin/env python3
"""
Configuration DNA Analysis - Understand your config's genetic makeup
Analyzes NixOS configurations to identify patterns, lineage, and evolution
"""

import logging
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from collections import Counter
import re

logger = logging.getLogger(__name__)

@dataclass
class ConfigGene:
    """Represents a configuration pattern/gene"""
    name: str
    category: str  # security, performance, development, desktop, server
    pattern: str  # Regex or identifier
    description: str
    impact: str  # low, medium, high
    prevalence: float  # 0.0 to 1.0

@dataclass
class ConfigLineage:
    """Tracks configuration evolution"""
    generation: int
    timestamp: datetime
    parent_hash: Optional[str]
    mutations: List[str]  # Changes from parent
    fitness_score: float  # How well it works

@dataclass
class ConfigDNA:
    """Complete DNA analysis of a configuration"""
    fingerprint: str  # Unique hash
    genes: List[ConfigGene]  # Detected patterns
    lineage: ConfigLineage
    
    # Analysis results
    profile_type: str  # desktop, server, development, hybrid
    complexity_score: float  # 0-100
    evolution_stage: str  # nascent, developing, mature, optimized
    
    # Relationships
    similar_configs: List[str]  # Hashes of similar configs
    inherited_traits: List[str]  # From imports/modules
    mutations: List[str]  # Unique patterns
    
    # Health metrics
    gene_diversity: float  # Variety of patterns
    mutation_rate: float  # Rate of change
    stability_score: float  # Consistency over time
    
    # Recommendations
    beneficial_mutations: List[str]  # Suggested improvements
    harmful_patterns: List[str]  # Anti-patterns detected
    evolution_path: List[str]  # Suggested next steps
    
    confidence: float

class ConfigDNAAnalyzer:
    """
    Analyzes NixOS configurations like genetic code
    Identifies patterns, evolution, and relationships
    """
    
    def __init__(self):
        # Gene catalog - common configuration patterns
        self.gene_catalog = {
            'security': [
                ConfigGene('firewall', 'security', r'networking\.firewall\.enable\s*=\s*true', 
                          'Firewall enabled', 'high', 0.7),
                ConfigGene('sudo', 'security', r'security\.sudo\.enable\s*=\s*true',
                          'Sudo configured', 'high', 0.9),
                ConfigGene('sshd', 'security', r'services\.openssh\.enable\s*=\s*true',
                          'SSH server enabled', 'medium', 0.5),
                ConfigGene('fail2ban', 'security', r'services\.fail2ban\.enable\s*=\s*true',
                          'Fail2ban protection', 'high', 0.3),
            ],
            'performance': [
                ConfigGene('zram', 'performance', r'zramSwap\.enable\s*=\s*true',
                          'ZRAM swap enabled', 'medium', 0.4),
                ConfigGene('tmpfs', 'performance', r'boot\.tmp\.useTmpfs\s*=\s*true',
                          'Tmpfs for /tmp', 'medium', 0.3),
                ConfigGene('kernel_latest', 'performance', r'boot\.kernelPackages\s*=.*latest',
                          'Latest kernel', 'low', 0.2),
                ConfigGene('cpu_gov', 'performance', r'powerManagement\.cpuFreqGovernor',
                          'CPU governor configured', 'medium', 0.3),
            ],
            'desktop': [
                ConfigGene('xorg', 'desktop', r'services\.xserver\.enable\s*=\s*true',
                          'X11 enabled', 'high', 0.5),
                ConfigGene('wayland', 'desktop', r'wayland.*enable\s*=\s*true',
                          'Wayland compositor', 'high', 0.3),
                ConfigGene('plasma', 'desktop', r'services\.xserver\.desktopManager\.plasma',
                          'KDE Plasma desktop', 'high', 0.2),
                ConfigGene('gnome', 'desktop', r'services\.xserver\.desktopManager\.gnome',
                          'GNOME desktop', 'high', 0.2),
            ],
            'development': [
                ConfigGene('docker', 'development', r'virtualisation\.docker\.enable\s*=\s*true',
                          'Docker enabled', 'medium', 0.4),
                ConfigGene('vscode', 'development', r'vscode|visualstudiocode',
                          'VS Code installed', 'low', 0.3),
                ConfigGene('direnv', 'development', r'programs\.direnv\.enable\s*=\s*true',
                          'Direnv for dev environments', 'medium', 0.2),
                ConfigGene('lorri', 'development', r'services\.lorri\.enable\s*=\s*true',
                          'Lorri for Nix shells', 'medium', 0.1),
            ],
            'server': [
                ConfigGene('nginx', 'server', r'services\.nginx\.enable\s*=\s*true',
                          'Nginx web server', 'high', 0.2),
                ConfigGene('postgresql', 'server', r'services\.postgresql\.enable\s*=\s*true',
                          'PostgreSQL database', 'high', 0.1),
                ConfigGene('prometheus', 'server', r'services\.prometheus\.enable\s*=\s*true',
                          'Prometheus monitoring', 'medium', 0.05),
                ConfigGene('containers', 'server', r'virtualisation\.oci-containers',
                          'Container orchestration', 'high', 0.1),
            ]
        }
        
        # Evolution patterns
        self.evolution_patterns = {
            'nascent': ['basic packages', 'minimal configuration', 'default settings'],
            'developing': ['custom packages', 'service configuration', 'user management'],
            'mature': ['modular structure', 'overlays', 'custom modules'],
            'optimized': ['flakes', 'binary caches', 'distributed builds']
        }
        
        # Known anti-patterns
        self.anti_patterns = [
            ('allowUnfree = true without specific packages', 'security'),
            ('permitRootLogin = "yes"', 'security'),
            ('firewall.enable = false', 'security'),
            ('No automatic updates configured', 'maintenance'),
            ('No garbage collection configured', 'storage'),
        ]
    
    def analyze_dna(self, config_path: str = '/etc/nixos/configuration.nix') -> ConfigDNA:
        """
        Perform complete DNA analysis of configuration
        
        Args:
            config_path: Path to configuration file
        
        Returns:
            ConfigDNA with complete analysis
        """
        try:
            path = Path(config_path)
            
            # Read configuration
            content = self._read_config(path)
            
            # Generate fingerprint
            fingerprint = self._generate_fingerprint(content)
            
            # Extract genes (patterns)
            genes = self._extract_genes(content)
            
            # Analyze lineage
            lineage = self._analyze_lineage(path, content)
            
            # Determine profile type
            profile_type = self._determine_profile(genes)
            
            # Calculate complexity
            complexity = self._calculate_complexity(content, genes)
            
            # Determine evolution stage
            evolution_stage = self._determine_evolution_stage(content, genes)
            
            # Find similar configurations
            similar = self._find_similar_configs(fingerprint, genes)
            
            # Identify inherited traits
            inherited = self._identify_inherited_traits(content)
            
            # Detect mutations
            mutations = self._detect_mutations(genes, inherited)
            
            # Calculate health metrics
            diversity = self._calculate_diversity(genes)
            mutation_rate = self._calculate_mutation_rate(lineage)
            stability = self._calculate_stability(lineage, mutation_rate)
            
            # Generate recommendations
            beneficial = self._suggest_beneficial_mutations(genes, profile_type)
            harmful = self._detect_harmful_patterns(content, genes)
            evolution_path = self._suggest_evolution_path(evolution_stage, genes)
            
            return ConfigDNA(
                fingerprint=fingerprint,
                genes=genes,
                lineage=lineage,
                profile_type=profile_type,
                complexity_score=complexity,
                evolution_stage=evolution_stage,
                similar_configs=similar,
                inherited_traits=inherited,
                mutations=mutations,
                gene_diversity=diversity,
                mutation_rate=mutation_rate,
                stability_score=stability,
                beneficial_mutations=beneficial,
                harmful_patterns=harmful,
                evolution_path=evolution_path,
                confidence=0.85
            )
            
        except Exception as e:
            logger.error(f"DNA analysis failed: {e}")
            return self._create_fallback_dna(str(e))
    
    def compare_dna(self, config1: str, config2: str) -> Dict[str, Any]:
        """
        Compare DNA of two configurations
        
        Args:
            config1: Path to first config
            config2: Path to second config
        
        Returns:
            Comparison analysis
        """
        try:
            dna1 = self.analyze_dna(config1)
            dna2 = self.analyze_dna(config2)
            
            # Find common genes
            genes1 = {g.name for g in dna1.genes}
            genes2 = {g.name for g in dna2.genes}
            common = genes1 & genes2
            unique1 = genes1 - genes2
            unique2 = genes2 - genes1
            
            # Calculate similarity
            similarity = len(common) / max(len(genes1), len(genes2)) if genes1 or genes2 else 0
            
            return {
                'similarity_score': similarity,
                'common_genes': list(common),
                'unique_to_first': list(unique1),
                'unique_to_second': list(unique2),
                'profile_match': dna1.profile_type == dna2.profile_type,
                'complexity_diff': abs(dna1.complexity_score - dna2.complexity_score),
                'evolution_diff': self._compare_evolution(dna1.evolution_stage, dna2.evolution_stage),
                'recommendation': self._recommend_merge_strategy(dna1, dna2)
            }
            
        except Exception as e:
            logger.error(f"DNA comparison failed: {e}")
            return {'error': str(e)}
    
    def trace_lineage(self, config_path: str) -> List[ConfigLineage]:
        """
        Trace evolutionary lineage of a configuration
        
        Args:
            config_path: Path to configuration
        
        Returns:
            List of lineage entries
        """
        try:
            # Look for Git history
            lineage = []
            path = Path(config_path)
            
            if (path.parent / '.git').exists():
                # Use Git to trace history
                import subprocess
                result = subprocess.run(
                    ['git', 'log', '--oneline', path.name],
                    cwd=path.parent,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    commits = result.stdout.strip().split('\n')
                    for i, commit in enumerate(commits[:10]):  # Last 10 commits
                        lineage.append(ConfigLineage(
                            generation=len(commits) - i,
                            timestamp=datetime.now(),  # Would need proper Git timestamp
                            parent_hash=commits[i+1].split()[0] if i+1 < len(commits) else None,
                            mutations=[commit.split(' ', 1)[1] if ' ' in commit else 'Unknown'],
                            fitness_score=0.5 + (i * 0.05)  # Assume improving over time
                        ))
            
            if not lineage:
                # No Git history, create single entry
                lineage = [ConfigLineage(
                    generation=1,
                    timestamp=datetime.now(),
                    parent_hash=None,
                    mutations=['Initial configuration'],
                    fitness_score=0.5
                )]
            
            return lineage
            
        except Exception as e:
            logger.error(f"Lineage trace failed: {e}")
            return []
    
    def _read_config(self, path: Path) -> str:
        """Read configuration file"""
        if not path.exists():
            # Try to read from current directory
            local_config = Path('configuration.nix')
            if local_config.exists():
                path = local_config
            else:
                raise FileNotFoundError(f"Configuration not found: {path}")
        
        with open(path) as f:
            return f.read()
    
    def _generate_fingerprint(self, content: str) -> str:
        """Generate unique fingerprint for configuration"""
        # Remove comments and whitespace for consistent hashing
        cleaned = re.sub(r'#.*$', '', content, flags=re.MULTILINE)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return hashlib.sha256(cleaned.encode()).hexdigest()[:16]
    
    def _extract_genes(self, content: str) -> List[ConfigGene]:
        """Extract configuration genes (patterns)"""
        detected_genes = []
        
        for category, genes in self.gene_catalog.items():
            for gene in genes:
                if re.search(gene.pattern, content):
                    detected_genes.append(gene)
        
        return detected_genes
    
    def _analyze_lineage(self, path: Path, content: str) -> ConfigLineage:
        """Analyze configuration lineage"""
        # Simple analysis based on content
        imports = re.findall(r'imports\s*=\s*\[(.*?)\]', content, re.DOTALL)
        
        mutations = []
        if 'flake.nix' in content:
            mutations.append('Migrated to flakes')
        if 'home-manager' in content:
            mutations.append('Added home-manager')
        if 'nixops' in content:
            mutations.append('Added NixOps deployment')
        
        return ConfigLineage(
            generation=1,  # Would need Git history for accurate generation
            timestamp=datetime.now(),
            parent_hash=None,
            mutations=mutations or ['Base configuration'],
            fitness_score=0.7  # Default fitness
        )
    
    def _determine_profile(self, genes: List[ConfigGene]) -> str:
        """Determine configuration profile type"""
        category_counts = Counter(g.category for g in genes)
        
        if category_counts.get('desktop', 0) >= 2:
            if category_counts.get('development', 0) >= 2:
                return 'development-desktop'
            return 'desktop'
        elif category_counts.get('server', 0) >= 2:
            return 'server'
        elif category_counts.get('development', 0) >= 3:
            return 'development'
        else:
            return 'minimal'
    
    def _calculate_complexity(self, content: str, genes: List[ConfigGene]) -> float:
        """Calculate configuration complexity score"""
        factors = {
            'lines': len(content.split('\n')),
            'genes': len(genes),
            'imports': len(re.findall(r'imports', content)),
            'overlays': len(re.findall(r'overlay', content)),
            'modules': len(re.findall(r'module', content)),
            'functions': len(re.findall(r'=>', content)),
        }
        
        # Weighted complexity score
        complexity = (
            min(factors['lines'] / 10, 30) +  # Lines contribute max 30
            factors['genes'] * 3 +  # Each gene adds 3
            factors['imports'] * 5 +  # Imports add complexity
            factors['overlays'] * 10 +  # Overlays are complex
            factors['modules'] * 8 +  # Modules add complexity
            factors['functions'] * 2  # Functions add some complexity
        )
        
        return min(complexity, 100)  # Cap at 100
    
    def _determine_evolution_stage(self, content: str, genes: List[ConfigGene]) -> str:
        """Determine evolutionary stage of configuration"""
        if 'flake.nix' in content or 'flake' in content:
            return 'optimized'
        elif len(genes) > 15 and 'overlay' in content:
            return 'mature'
        elif len(genes) > 8:
            return 'developing'
        else:
            return 'nascent'
    
    def _find_similar_configs(self, fingerprint: str, genes: List[ConfigGene]) -> List[str]:
        """Find similar configurations (would need database in production)"""
        # Placeholder - would query a database of known configurations
        return []
    
    def _identify_inherited_traits(self, content: str) -> List[str]:
        """Identify traits inherited from imports/modules"""
        inherited = []
        
        # Check for common NixOS modules
        if 'hardware-configuration.nix' in content:
            inherited.append('Hardware auto-configuration')
        if 'home-manager' in content:
            inherited.append('Home Manager integration')
        if 'nixos-hardware' in content:
            inherited.append('Hardware optimizations')
        
        return inherited
    
    def _detect_mutations(self, genes: List[ConfigGene], inherited: List[str]) -> List[str]:
        """Detect unique mutations (patterns)"""
        mutations = []
        
        # Find rare genes
        rare_genes = [g for g in genes if g.prevalence < 0.2]
        for gene in rare_genes:
            mutations.append(f"Rare pattern: {gene.name}")
        
        return mutations
    
    def _calculate_diversity(self, genes: List[ConfigGene]) -> float:
        """Calculate genetic diversity score"""
        if not genes:
            return 0.0
        
        categories = set(g.category for g in genes)
        return len(categories) / 5.0  # 5 main categories
    
    def _calculate_mutation_rate(self, lineage: ConfigLineage) -> float:
        """Calculate rate of configuration changes"""
        if lineage.generation == 1:
            return 0.0
        return len(lineage.mutations) / lineage.generation
    
    def _calculate_stability(self, lineage: ConfigLineage, mutation_rate: float) -> float:
        """Calculate configuration stability score"""
        # High fitness + low mutation rate = high stability
        stability = lineage.fitness_score * (1 - min(mutation_rate, 1.0))
        return stability
    
    def _suggest_beneficial_mutations(self, genes: List[ConfigGene], profile: str) -> List[str]:
        """Suggest beneficial configuration changes"""
        suggestions = []
        gene_names = {g.name for g in genes}
        
        # Profile-specific suggestions
        if profile == 'desktop' and 'zram' not in gene_names:
            suggestions.append('Enable ZRAM for better memory management')
        
        if profile == 'server' and 'fail2ban' not in gene_names:
            suggestions.append('Add fail2ban for intrusion prevention')
        
        if 'docker' in gene_names and 'docker_gc' not in gene_names:
            suggestions.append('Add Docker garbage collection')
        
        # Universal suggestions
        if 'firewall' not in gene_names:
            suggestions.append('Enable firewall for security')
        
        return suggestions
    
    def _detect_harmful_patterns(self, content: str, genes: List[ConfigGene]) -> List[str]:
        """Detect anti-patterns or harmful configurations"""
        harmful = []
        
        for pattern, category in self.anti_patterns:
            if pattern.lower() in content.lower():
                harmful.append(f"{category}: {pattern}")
        
        return harmful
    
    def _suggest_evolution_path(self, stage: str, genes: List[ConfigGene]) -> List[str]:
        """Suggest next evolutionary steps"""
        paths = {
            'nascent': [
                'Add more service configurations',
                'Implement user management',
                'Configure automatic updates'
            ],
            'developing': [
                'Modularize configuration',
                'Add overlays for customization',
                'Implement secrets management'
            ],
            'mature': [
                'Migrate to flakes for reproducibility',
                'Set up binary caches',
                'Implement distributed builds'
            ],
            'optimized': [
                'Fine-tune performance settings',
                'Implement A/B testing for configs',
                'Share patterns with community'
            ]
        }
        return paths.get(stage, ['Continue evolving configuration'])
    
    def _compare_evolution(self, stage1: str, stage2: str) -> str:
        """Compare evolution stages"""
        stages = ['nascent', 'developing', 'mature', 'optimized']
        try:
            idx1 = stages.index(stage1)
            idx2 = stages.index(stage2)
            diff = idx2 - idx1
            
            if diff > 0:
                return f"Second is {diff} stage(s) ahead"
            elif diff < 0:
                return f"First is {-diff} stage(s) ahead"
            else:
                return "Same evolution stage"
        except ValueError:
            return "Cannot compare stages"
    
    def _recommend_merge_strategy(self, dna1: ConfigDNA, dna2: ConfigDNA) -> str:
        """Recommend strategy for merging configurations"""
        if dna1.profile_type == dna2.profile_type:
            if dna1.complexity_score < dna2.complexity_score:
                return "Use first as base, cherry-pick from second"
            else:
                return "Use second as base, cherry-pick from first"
        else:
            return "Create modular structure to combine both profiles"
    
    def _create_fallback_dna(self, error: str) -> ConfigDNA:
        """Create fallback DNA analysis on error"""
        return ConfigDNA(
            fingerprint="unknown",
            genes=[],
            lineage=ConfigLineage(1, datetime.now(), None, [error], 0.1),
            profile_type="unknown",
            complexity_score=0,
            evolution_stage="nascent",
            similar_configs=[],
            inherited_traits=[],
            mutations=[],
            gene_diversity=0,
            mutation_rate=0,
            stability_score=0.5,
            beneficial_mutations=["Unable to analyze"],
            harmful_patterns=[],
            evolution_path=["Fix configuration errors first"],
            confidence=0.1
        )