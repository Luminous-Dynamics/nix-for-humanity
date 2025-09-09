#!/usr/bin/env python3
"""
CLI commands for Configuration DNA Analysis
"""

import click
import json
from pathlib import Path
from typing import Optional

from ..ai.advanced_features.config_dna import ConfigDNAAnalyzer
from ..ai.advanced_features.dna_visualizer import ConfigDNAVisualizer
from ..ai.advanced_features.dna_manager import ConfigDNAManager, DNAFormat

@click.group()
def dna():
    """Configuration DNA analysis commands"""
    pass

@dna.command()
@click.argument('config_path', default='/etc/nixos/configuration.nix')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def analyze(config_path: str, output_json: bool):
    """Analyze configuration DNA and evolution"""
    try:
        analyzer = ConfigDNAAnalyzer()
        dna_result = analyzer.analyze_dna(config_path)
        
        if output_json:
            # Convert to dict for JSON serialization
            result = {
                'fingerprint': dna_result.fingerprint,
                'profile_type': dna_result.profile_type,
                'complexity_score': dna_result.complexity_score,
                'evolution_stage': dna_result.evolution_stage,
                'gene_count': len(dna_result.genes),
                'genes': [g.name for g in dna_result.genes],
                'diversity': dna_result.gene_diversity,
                'stability': dna_result.stability_score,
                'harmful_patterns': dna_result.harmful_patterns,
                'beneficial_mutations': dna_result.beneficial_mutations,
                'confidence': dna_result.confidence
            }
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(click.style("🧬 Configuration DNA Analysis", fg='cyan', bold=True))
            click.echo()
            click.echo(f"📍 Fingerprint: {dna_result.fingerprint}")
            click.echo(f"🏷️ Profile: {dna_result.profile_type}")
            click.echo(f"📊 Complexity: {dna_result.complexity_score:.1f}/100")
            click.echo(f"🌱 Evolution: {dna_result.evolution_stage}")
            click.echo()
            
            click.echo(click.style("🧬 Detected Genes:", fg='green'))
            for gene in dna_result.genes[:10]:  # Show top 10
                click.echo(f"  • {gene.name} ({gene.category})")
            if len(dna_result.genes) > 10:
                click.echo(f"  ... and {len(dna_result.genes) - 10} more")
            
            click.echo()
            click.echo(click.style("📈 Health Metrics:", fg='yellow'))
            click.echo(f"  Diversity: {dna_result.gene_diversity:.1%}")
            click.echo(f"  Stability: {dna_result.stability_score:.1%}")
            click.echo(f"  Mutation Rate: {dna_result.mutation_rate:.2f}")
            
            if dna_result.harmful_patterns:
                click.echo()
                click.echo(click.style("⚠️ Harmful Patterns:", fg='red'))
                for pattern in dna_result.harmful_patterns:
                    click.echo(f"  • {pattern}")
            
            if dna_result.beneficial_mutations:
                click.echo()
                click.echo(click.style("💡 Beneficial Mutations:", fg='cyan'))
                for mutation in dna_result.beneficial_mutations[:3]:
                    click.echo(f"  • {mutation}")
            
            click.echo()
            click.echo(f"Confidence: {dna_result.confidence:.0%}")
            
    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg='red'), err=True)
        raise click.ClickException(str(e))

@dna.command()
@click.argument('config1')
@click.argument('config2')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def compare(config1: str, config2: str, output_json: bool):
    """Compare DNA of two configurations"""
    try:
        analyzer = ConfigDNAAnalyzer()
        comparison = analyzer.compare_dna(config1, config2)
        
        if output_json:
            click.echo(json.dumps(comparison, indent=2))
        else:
            click.echo(click.style("🧬 Configuration DNA Comparison", fg='cyan', bold=True))
            click.echo()
            click.echo(f"📊 Similarity: {comparison['similarity_score']:.0%}")
            click.echo(f"🏷️ Profile Match: {comparison['profile_match']}")
            click.echo(f"📈 Complexity Difference: {comparison['complexity_diff']:.1f}")
            click.echo()
            
            if comparison['common_genes']:
                click.echo(click.style(f"🤝 Common Genes ({len(comparison['common_genes'])}):", fg='green'))
                for gene in comparison['common_genes'][:5]:
                    click.echo(f"  • {gene}")
            
            if comparison['unique_to_first']:
                click.echo()
                click.echo(click.style(f"1️⃣ Unique to First ({len(comparison['unique_to_first'])}):", fg='yellow'))
                for gene in comparison['unique_to_first'][:3]:
                    click.echo(f"  • {gene}")
            
            if comparison['unique_to_second']:
                click.echo()
                click.echo(click.style(f"2️⃣ Unique to Second ({len(comparison['unique_to_second'])}):", fg='yellow'))
                for gene in comparison['unique_to_second'][:3]:
                    click.echo(f"  • {gene}")
            
            click.echo()
            click.echo(f"💡 Recommendation: {comparison['recommendation']}")
            
    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg='red'), err=True)
        raise click.ClickException(str(e))

@dna.command()
@click.argument('config_path', default='/etc/nixos/configuration.nix')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def lineage(config_path: str, output_json: bool):
    """Trace configuration lineage and evolution"""
    try:
        analyzer = ConfigDNAAnalyzer()
        lineage_history = analyzer.trace_lineage(config_path)
        
        if output_json:
            result = [
                {
                    'generation': l.generation,
                    'timestamp': l.timestamp.isoformat(),
                    'parent_hash': l.parent_hash,
                    'mutations': l.mutations,
                    'fitness_score': l.fitness_score
                }
                for l in lineage_history
            ]
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(click.style("🧬 Configuration Lineage", fg='cyan', bold=True))
            click.echo()
            
            for entry in lineage_history[:5]:  # Show recent 5
                click.echo(f"Generation {entry.generation}:")
                click.echo(f"  📅 {entry.timestamp.strftime('%Y-%m-%d %H:%M')}")
                if entry.mutations:
                    click.echo(f"  🔄 {', '.join(entry.mutations[:2])}")
                click.echo(f"  💪 Fitness: {entry.fitness_score:.1%}")
                click.echo()
            
    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg='red'), err=True)
        raise click.ClickException(str(e))

@dna.command()
@click.argument('config_path', default='/etc/nixos/configuration.nix')
def evolve(config_path: str):
    """Suggest evolution path for configuration"""
    try:
        analyzer = ConfigDNAAnalyzer()
        dna_result = analyzer.analyze_dna(config_path)
        
        click.echo(click.style("🌱 Configuration Evolution Path", fg='cyan', bold=True))
        click.echo()
        click.echo(f"Current Stage: {dna_result.evolution_stage}")
        click.echo()
        
        click.echo(click.style("📈 Next Steps:", fg='green'))
        for i, step in enumerate(dna_result.evolution_path, 1):
            click.echo(f"  {i}. {step}")
        
        if dna_result.beneficial_mutations:
            click.echo()
            click.echo(click.style("💡 Quick Improvements:", fg='yellow'))
            for mutation in dna_result.beneficial_mutations[:5]:
                click.echo(f"  • {mutation}")
        
    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg='red'), err=True)
        raise click.ClickException(str(e))

@dna.command()
@click.argument('config_path', default='/etc/nixos/configuration.nix')
@click.option('--type', 'viz_type', type=click.Choice(['helix', 'chromosome', 'fingerprint', 'health', 'full']), 
              default='helix', help='Visualization type')
def visualize(config_path: str, viz_type: str):
    """Visualize configuration DNA in ASCII art"""
    try:
        analyzer = ConfigDNAAnalyzer()
        visualizer = ConfigDNAVisualizer()
        
        # Analyze DNA
        dna_result = analyzer.analyze_dna(config_path)
        
        # Create visualization based on type
        if viz_type == 'helix':
            output = visualizer.visualize_dna_helix(dna_result)
        elif viz_type == 'chromosome':
            output = visualizer.visualize_chromosome_map(dna_result)
        elif viz_type == 'fingerprint':
            output = visualizer.visualize_fingerprint(dna_result)
        elif viz_type == 'health':
            output = visualizer.visualize_health_chart(dna_result)
        elif viz_type == 'full':
            lineage = analyzer.trace_lineage(config_path)
            viz = visualizer.visualize_full_report(dna_result, lineage)
            output = viz.ascii_art
        
        click.echo(output)
        
    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg='red'), err=True)
        raise click.ClickException(str(e))

@dna.command()
@click.argument('config_path', default='/etc/nixos/configuration.nix')
@click.option('--format', type=click.Choice(['json', 'yaml', 'nix', 'compressed']), 
              default='json', help='Export format')
@click.option('--output', '-o', help='Output file (stdout if not specified)')
@click.option('--include-raw', is_flag=True, help='Include raw configuration')
def export(config_path: str, format: str, output: Optional[str], include_raw: bool):
    """Export configuration DNA for sharing"""
    try:
        manager = ConfigDNAManager()
        
        # Map string format to enum
        format_map = {
            'json': DNAFormat.JSON,
            'yaml': DNAFormat.YAML,
            'nix': DNAFormat.NIX,
            'compressed': DNAFormat.COMPRESSED
        }
        
        # Export DNA
        dna_export = manager.export_dna(
            config_path, 
            format=format_map[format],
            include_raw=include_raw
        )
        
        # Output to file or stdout
        if output:
            Path(output).write_text(dna_export)
            click.echo(click.style(f"✅ DNA exported to {output}", fg='green'))
            
            # Show size
            size = len(dna_export)
            if size > 1024 * 1024:
                size_str = f"{size / (1024*1024):.1f} MB"
            elif size > 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size} bytes"
            click.echo(f"📦 Size: {size_str}")
        else:
            click.echo(dna_export)
            
    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg='red'), err=True)
        raise click.ClickException(str(e))

@dna.command(name='import')
@click.argument('dna_file')
@click.option('--validate', is_flag=True, default=True, help='Validate compatibility')
@click.option('--apply', 'apply_to', help='Apply to configuration file')
@click.option('--preserve-custom', is_flag=True, default=True, help='Keep custom settings')
def import_dna(dna_file: str, validate: bool, apply_to: Optional[str], preserve_custom: bool):
    """Import configuration DNA from export"""
    try:
        manager = ConfigDNAManager()
        
        # Read DNA file
        dna_data = Path(dna_file).read_text()
        
        # Import DNA
        package = manager.import_dna(dna_data, validate=validate)
        
        click.echo(click.style("🧬 DNA Import Successful", fg='green', bold=True))
        click.echo()
        click.echo(f"📍 Fingerprint: {package.dna.fingerprint}")
        click.echo(f"🏷️ Profile: {package.dna.profile_type}")
        click.echo(f"📊 Complexity: {package.dna.complexity_score:.1f}/100")
        click.echo(f"🌱 Evolution: {package.dna.evolution_stage}")
        
        if package.source_system:
            click.echo(f"🖥️ Source: {package.source_system}")
        if package.description:
            click.echo(f"📝 Description: {package.description}")
        if package.tags:
            click.echo(f"🏷️ Tags: {', '.join(package.tags)}")
        
        # Apply if requested
        if apply_to:
            click.echo()
            click.echo(click.style("📝 Applying DNA to configuration...", fg='cyan'))
            
            new_config = manager.apply_dna(package, apply_to, preserve_custom)
            
            # Write to file
            output_path = Path(apply_to)
            if output_path.suffix == '.nix':
                output_path = output_path.with_suffix('.dna.nix')
            else:
                output_path = Path(f"{apply_to}.dna")
            
            output_path.write_text(new_config)
            click.echo(click.style(f"✅ DNA applied to {output_path}", fg='green'))
            
            if preserve_custom:
                click.echo("💡 Custom settings preserved")
                
    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg='red'), err=True)
        raise click.ClickException(str(e))

@dna.command()
@click.argument('parent1')
@click.argument('parent2')
@click.option('--strategy', type=click.Choice(['best_of_both', 'hybrid_vigor', 'selective', 'random_mix']),
              default='best_of_both', help='Breeding strategy')
@click.option('--output', '-o', help='Output file for offspring DNA')
@click.option('--visualize', is_flag=True, help='Show visual DNA of offspring')
def breed(parent1: str, parent2: str, strategy: str, output: Optional[str], visualize: bool):
    """Breed two configurations to create offspring"""
    try:
        manager = ConfigDNAManager()
        visualizer = ConfigDNAVisualizer()
        
        click.echo(click.style("🧬 Breeding Configuration DNA", fg='magenta', bold=True))
        click.echo()
        click.echo(f"👨 Parent 1: {Path(parent1).name}")
        click.echo(f"👩 Parent 2: {Path(parent2).name}")
        click.echo(f"🧪 Strategy: {strategy}")
        click.echo()
        
        # Breed configurations
        offspring = manager.breed_dna(parent1, parent2, breeding_strategy=strategy)
        
        click.echo(click.style("👶 Offspring Created!", fg='green', bold=True))
        click.echo()
        click.echo(f"📍 Fingerprint: {offspring.fingerprint}")
        click.echo(f"🏷️ Profile: {offspring.profile_type}")
        click.echo(f"📊 Complexity: {offspring.complexity_score:.1f}/100")
        click.echo(f"🧬 Gene Count: {len(offspring.genes)}")
        click.echo(f"🌈 Diversity: {offspring.gene_diversity:.1%}")
        click.echo(f"💪 Fitness: {offspring.lineage.fitness_score:.1%}")
        
        if offspring.lineage.mutations:
            click.echo()
            click.echo(click.style("🔄 Mutations:", fg='yellow'))
            for mutation in offspring.lineage.mutations[:3]:
                click.echo(f"  • {mutation}")
        
        # Show visual if requested
        if visualize:
            click.echo()
            click.echo(visualizer.visualize_dna_helix(offspring, height=10))
        
        # Export if output specified
        if output:
            # Create DNA package for export
            package = manager.export_dna(parent1, format=DNAFormat.JSON)
            
            # Save offspring DNA
            Path(output).write_text(package)
            click.echo()
            click.echo(click.style(f"✅ Offspring DNA saved to {output}", fg='green'))
            
    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg='red'), err=True)
        raise click.ClickException(str(e))

@dna.command()
@click.argument('dna_file1')
@click.argument('dna_file2')
def compatibility(dna_file1: str, dna_file2: str):
    """Check compatibility between two DNA packages"""
    try:
        manager = ConfigDNAManager()
        
        # Import both DNA packages
        dna1 = Path(dna_file1).read_text()
        dna2 = Path(dna_file2).read_text()
        
        package1 = manager.import_dna(dna1)
        package2 = manager.import_dna(dna2)
        
        # Compare packages
        comparison = manager.compare_dna_packages(package1, package2)
        
        click.echo(click.style("🧬 DNA Compatibility Check", fg='cyan', bold=True))
        click.echo()
        
        # Compatibility status
        if comparison['compatible']:
            click.echo(click.style("✅ Compatible", fg='green', bold=True))
        else:
            click.echo(click.style("❌ Incompatible", fg='red', bold=True))
            for conflict in comparison['conflicts']:
                click.echo(f"  ⚠️ {conflict}")
        
        click.echo()
        click.echo(f"📊 Similarity: {comparison['similarity_score']:.0%}")
        click.echo(f"🧬 Shared Genes: {len(comparison['shared_genes'])}")
        click.echo(f"1️⃣ Unique to First: {len(comparison['unique_to_first'])}")
        click.echo(f"2️⃣ Unique to Second: {len(comparison['unique_to_second'])}")
        click.echo(f"💍 Breeding Potential: {comparison['breeding_potential']:.0%}")
        
        if comparison['conflicts'] and comparison['compatible']:
            click.echo()
            click.echo(click.style("⚠️ Minor Issues:", fg='yellow'))
            for conflict in comparison['conflicts'][:3]:
                click.echo(f"  • {conflict}")
                
    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg='red'), err=True)
        raise click.ClickException(str(e))