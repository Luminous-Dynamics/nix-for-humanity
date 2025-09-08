#!/usr/bin/env python3
"""
Configuration DNA Visualizer - Create visual representations of config DNA
Generates ASCII art, charts, and visual DNA sequences
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib

from .config_dna import ConfigDNA, ConfigGene

# Define GeneCategory here since it's not in config_dna
from enum import Enum

class GeneCategory(Enum):
    """Categories of configuration genes"""
    SYSTEM = "system"
    PACKAGES = "packages"
    SERVICES = "services"
    NETWORKING = "networking"
    SECURITY = "security"
    USERS = "users"
    BOOT = "boot"
    FILESYSTEM = "filesystem"
    HARDWARE = "hardware"
    CUSTOM = "custom"


class VisualizationType(Enum):
    """Types of DNA visualizations available"""
    HELIX = "helix"
    CHROMOSOME = "chromosome"
    FINGERPRINT = "fingerprint"
    EVOLUTION_TREE = "evolution_tree"
    HEALTH_CHART = "health_chart"
    GENE_MAP = "gene_map"


@dataclass
class DNAVisualization:
    """Container for DNA visualization data"""
    type: VisualizationType
    ascii_art: str
    summary: Dict[str, any]
    color_map: Optional[Dict[str, str]] = None


class ConfigDNAVisualizer:
    """
    Visualizes configuration DNA in various formats
    Creates beautiful ASCII representations of config genetics
    """
    
    def __init__(self):
        # DNA base pair representations
        self.base_pairs = {
            'A': '═══',  # Adenine
            'T': '───',  # Thymine  
            'G': '≡≡≡',  # Guanine
            'C': '···',  # Cytosine
        }
        
        # Gene category symbols (using string categories from actual ConfigGene)
        self.category_symbols = {
            'system': '⚙',
            'packages': '📦',
            'services': '🔧',
            'networking': '🌐',
            'security': '🔒',
            'users': '👤',
            'boot': '🚀',
            'filesystem': '💾',
            'hardware': '🖥️',
            'development': '💻',
            'desktop': '🖥️',
            'server': '🖧',
            'performance': '⚡',
            'custom': '✨'
        }
    
    def visualize_dna_helix(self, dna: ConfigDNA, height: int = 20) -> str:
        """Create ASCII art DNA double helix"""
        helix = []
        helix.append("     🧬 Configuration DNA Helix 🧬")
        helix.append("     ══════════════════════════")
        helix.append("")
        
        # Convert fingerprint to DNA sequence
        sequence = self._fingerprint_to_sequence(dna.fingerprint)
        
        # Create helix structure
        for i in range(height):
            # Calculate helix position
            angle = (i * math.pi / 5)
            left_offset = int(5 + 4 * math.sin(angle))
            right_offset = int(5 - 4 * math.sin(angle))
            
            # Get base pair
            base_idx = i % len(sequence)
            base = sequence[base_idx]
            pair = self._get_base_pair(base)
            connector = self.base_pairs[base]
            
            # Build helix line
            if left_offset < right_offset:
                line = (" " * left_offset + 
                       f"{base}{connector}{pair}" + 
                       " " * (10 - right_offset))
            else:
                line = (" " * right_offset + 
                       f"{pair}{connector}{base}" + 
                       " " * (10 - left_offset))
            
            helix.append(f"     │{line}│")
        
        helix.append("     ══════════════════════════")
        helix.append(f"     Complexity: {dna.complexity_score:.0f}/100")
        helix.append(f"     Health: {dna.evolution_stage.upper()}")
        
        return '\n'.join(helix)
    
    def visualize_chromosome_map(self, dna: ConfigDNA) -> str:
        """Create chromosome-style gene map"""
        lines = []
        lines.append("🧬 Configuration Chromosome Map")
        lines.append("=" * 50)
        lines.append("")
        
        # Group genes by category
        by_category = {}
        for gene in dna.genes:
            if gene.category not in by_category:
                by_category[gene.category] = []
            by_category[gene.category].append(gene)
        
        # Create chromosome bands
        for category, genes in by_category.items():
            symbol = self.category_symbols.get(category, '•')
            lines.append(f"{symbol} {category.upper()}")
            
            # Create visual band
            band_str = "  ["
            for gene in genes[:10]:  # Limit to 10 per category
                # Use prevalence since ConfigGene doesn't have expression_level
                strength = min(9, int(gene.prevalence * 10))
                band_str += str(strength)
            band_str += "]"
            
            if len(genes) > 10:
                band_str += f" +{len(genes)-10} more"
            
            lines.append(band_str)
            
            # Show key genes
            for gene in genes[:3]:
                # ConfigGene doesn't have is_dominant, use impact instead
                marker = "►" if gene.impact == "high" else "▸"
                lines.append(f"    {marker} {gene.name}")
            
            lines.append("")
        
        return '\n'.join(lines)
    
    def visualize_evolution_tree(self, lineage: List) -> str:
        """Create evolution tree visualization"""
        lines = []
        lines.append("🌳 Configuration Evolution Tree")
        lines.append("=" * 40)
        lines.append("")
        
        for i, gen in enumerate(lineage[:10]):  # Show last 10 generations
            # Calculate indent based on fitness
            indent = "  " * i
            
            # Determine evolution symbol
            if i == 0:
                symbol = "🌱"  # Origin
            elif gen.fitness_score > 0.8:
                symbol = "🌿"  # Healthy evolution
            elif gen.fitness_score > 0.6:
                symbol = "🍃"  # Normal evolution
            else:
                symbol = "🍂"  # Degraded evolution
            
            # Format generation line
            lines.append(f"{indent}{symbol} Gen {gen.generation}")
            
            # Show mutations
            if gen.mutations:
                for mutation in gen.mutations[:2]:
                    lines.append(f"{indent}  └─ {mutation}")
            
            # Show fitness
            fitness_bar = "█" * int(gen.fitness_score * 10)
            lines.append(f"{indent}  Fitness: [{fitness_bar:<10}] {gen.fitness_score:.0%}")
            lines.append("")
        
        return '\n'.join(lines)
    
    def visualize_health_chart(self, dna: ConfigDNA) -> str:
        """Create health status chart"""
        lines = []
        lines.append("📊 Configuration Health Report")
        lines.append("=" * 40)
        lines.append("")
        
        # Overall health bar
        health_pct = (100 - len(dna.harmful_patterns) * 10 + 
                     len(dna.beneficial_mutations) * 5)
        health_pct = max(0, min(100, health_pct))
        
        health_bar = "█" * int(health_pct / 5)
        lines.append(f"Overall Health: [{health_bar:<20}] {health_pct}%")
        lines.append("")
        
        # Individual metrics
        metrics = {
            "Stability": dna.stability_score * 100,
            "Diversity": dna.gene_diversity * 100,
            "Evolution": (1.0 - dna.mutation_rate) * 100,
            "Complexity": 100 - dna.complexity_score  # Lower is better
        }
        
        for metric, value in metrics.items():
            # Create visual bar
            bar_len = int(value / 5)
            bar = "▓" * bar_len + "░" * (20 - bar_len)
            
            # Determine color/symbol
            if value >= 80:
                symbol = "✅"
            elif value >= 60:
                symbol = "⚠️"
            else:
                symbol = "❌"
            
            lines.append(f"{symbol} {metric:12} [{bar}] {value:.0f}%")
        
        lines.append("")
        
        # Issues and improvements
        if dna.harmful_patterns:
            lines.append("⚠️ Issues Detected:")
            for issue in dna.harmful_patterns[:3]:
                lines.append(f"  • {issue}")
        
        if dna.beneficial_mutations:
            lines.append("")
            lines.append("💡 Suggested Improvements:")
            for improvement in dna.beneficial_mutations[:3]:
                lines.append(f"  • {improvement}")
        
        return '\n'.join(lines)
    
    def visualize_fingerprint(self, dna: ConfigDNA) -> str:
        """Create visual fingerprint pattern"""
        lines = []
        lines.append("🔍 Configuration Fingerprint")
        lines.append("=" * 32)
        lines.append("")
        
        # Convert fingerprint to visual pattern
        fp = dna.fingerprint
        
        # Create 8x8 grid pattern
        for row in range(8):
            line = ""
            for col in range(8):
                # Get character from fingerprint
                idx = (row * 8 + col) % len(fp)
                char = fp[idx]
                
                # Convert to visual
                val = ord(char)
                if val % 4 == 0:
                    symbol = "██"
                elif val % 4 == 1:
                    symbol = "▓▓"
                elif val % 4 == 2:
                    symbol = "░░"
                else:
                    symbol = "  "
                
                line += symbol
            
            lines.append(f"  │{line}│")
        
        lines.append("  " + "─" * 18)
        lines.append(f"  ID: {fp[:8]}...")
        lines.append(f"  Type: {dna.profile_type}")
        
        return '\n'.join(lines)
    
    def create_gene_heatmap(self, dna: ConfigDNA) -> str:
        """Create heatmap of gene expression levels"""
        lines = []
        lines.append("🔥 Gene Expression Heatmap")
        lines.append("=" * 40)
        lines.append("")
        
        # Group by category
        by_category = {}
        for gene in dna.genes:
            if gene.category not in by_category:
                by_category[gene.category] = []
            by_category[gene.category].append(gene)
        
        # Create heatmap
        for category, genes in by_category.items():
            symbol = self.category_symbols.get(category, '•')
            lines.append(f"{symbol} {category}:")
            
            # Create heat row
            heat_row = "  "
            for gene in genes[:20]:  # Max 20 per row
                level = gene.prevalence  # Use prevalence instead of expression_level
                if level > 0.8:
                    heat = "🔴"  # Hot/High
                elif level > 0.6:
                    heat = "🟠"  # Warm
                elif level > 0.4:
                    heat = "🟡"  # Medium
                elif level > 0.2:
                    heat = "🟢"  # Cool
                else:
                    heat = "🔵"  # Cold/Low
                heat_row += heat
            
            lines.append(heat_row)
            lines.append("")
        
        lines.append("Legend: 🔴High 🟠Med-High 🟡Medium 🟢Med-Low 🔵Low")
        
        return '\n'.join(lines)
    
    def visualize_full_report(self, dna: ConfigDNA, lineage: Optional[List] = None) -> DNAVisualization:
        """Create comprehensive DNA visualization report"""
        sections = []
        
        # Add header
        sections.append("╔" + "═" * 50 + "╗")
        sections.append("║" + "Configuration DNA Analysis Report".center(50) + "║")
        sections.append("╚" + "═" * 50 + "╝")
        sections.append("")
        
        # Add fingerprint
        sections.append(self.visualize_fingerprint(dna))
        sections.append("")
        sections.append("-" * 52)
        sections.append("")
        
        # Add helix
        sections.append(self.visualize_dna_helix(dna, height=15))
        sections.append("")
        sections.append("-" * 52)
        sections.append("")
        
        # Add chromosome map
        sections.append(self.visualize_chromosome_map(dna))
        sections.append("")
        sections.append("-" * 52)
        sections.append("")
        
        # Add health chart
        sections.append(self.visualize_health_chart(dna))
        sections.append("")
        
        # Add evolution tree if lineage provided
        if lineage:
            sections.append("-" * 52)
            sections.append("")
            sections.append(self.visualize_evolution_tree(lineage))
        
        # Create summary
        summary = {
            'total_genes': len(dna.genes),
            'categories': len(set(g.category for g in dna.genes)),
            'complexity': dna.complexity_score,
            'health': health_pct if 'health_pct' in locals() else 75,
            'evolution_stage': dna.evolution_stage
        }
        
        return DNAVisualization(
            type=VisualizationType.HELIX,
            ascii_art='\n'.join(sections),
            summary=summary
        )
    
    def _fingerprint_to_sequence(self, fingerprint: str) -> str:
        """Convert fingerprint hash to DNA sequence"""
        sequence = ""
        bases = ['A', 'T', 'G', 'C']
        
        for char in fingerprint:
            # Convert hex to base
            val = ord(char) % 4
            sequence += bases[val]
        
        return sequence
    
    def _get_base_pair(self, base: str) -> str:
        """Get complementary base pair"""
        pairs = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
        return pairs.get(base, 'N')