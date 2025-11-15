#!/usr/bin/env python3
"""
Configuration DNA Manager - Export, import, and breed configurations
Enables sharing and combining configuration genetics
"""

import json
import hashlib
import base64
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

from .config_dna import ConfigDNA, ConfigGene, ConfigDNAAnalyzer, ConfigLineage


class DNAFormat(Enum):
    """Export/import formats for configuration DNA"""

    JSON = "json"
    YAML = "yaml"
    NIX = "nix"
    COMPRESSED = "compressed"


@dataclass
class DNAPackage:
    """Container for exportable DNA data"""

    version: str = "1.0.0"
    exported_at: datetime = None
    source_system: Optional[str] = None

    # Core DNA data
    dna: ConfigDNA = None

    # Metadata
    description: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = None

    # Compatibility info
    nixos_version: Optional[str] = None
    required_features: List[str] = None

    # Breeding information
    parent_dnas: List[str] = None  # Fingerprints of parent DNAs
    generation: int = 0

    def __post_init__(self):
        if self.exported_at is None:
            self.exported_at = datetime.now()
        if self.tags is None:
            self.tags = []
        if self.required_features is None:
            self.required_features = []
        if self.parent_dnas is None:
            self.parent_dnas = []


class ConfigDNAManager:
    """
    Manages configuration DNA import, export, and breeding
    Enables sharing configurations and combining their best traits
    """

    def __init__(self):
        self.analyzer = ConfigDNAAnalyzer()
        self.dna_cache = {}

    def export_dna(
        self,
        config_path: str,
        format: DNAFormat = DNAFormat.JSON,
        include_raw: bool = False,
        compress: bool = False,
    ) -> str:
        """
        Export configuration DNA to shareable format

        Args:
            config_path: Path to configuration file
            format: Export format (JSON, YAML, NIX, COMPRESSED)
            include_raw: Include raw configuration text
            compress: Compress the output

        Returns:
            Exported DNA as string
        """
        # Analyze configuration
        dna = self.analyzer.analyze_dna(config_path)

        # Create DNA package
        package = DNAPackage(
            dna=dna,
            source_system=self._get_system_info(),
            nixos_version=self._get_nixos_version(),
            description=f"Configuration DNA from {Path(config_path).name}",
            author=self._get_author_info(),
        )

        # Add raw configuration if requested
        if include_raw and Path(config_path).exists():
            raw_config = Path(config_path).read_text()
            package.raw_config = base64.b64encode(raw_config.encode()).decode()

        # Export based on format
        if format == DNAFormat.JSON:
            output = self._export_json(package)
        elif format == DNAFormat.YAML:
            output = self._export_yaml(package)
        elif format == DNAFormat.NIX:
            output = self._export_nix(package)
        elif format == DNAFormat.COMPRESSED:
            output = self._export_compressed(package)
        else:
            output = self._export_json(package)

        # Compress if requested
        if compress and format != DNAFormat.COMPRESSED:
            import gzip

            output = base64.b64encode(gzip.compress(output.encode())).decode()

        return output

    def import_dna(self, dna_data: str, validate: bool = True) -> DNAPackage:
        """
        Import DNA from exported data

        Args:
            dna_data: Exported DNA data (JSON/YAML/etc)
            validate: Whether to validate compatibility

        Returns:
            DNAPackage with imported configuration
        """
        # Detect format and parse
        if dna_data.startswith("{"):
            # JSON format
            package = self._import_json(dna_data)
        elif dna_data.startswith("# DNA"):
            # NIX format
            package = self._import_nix(dna_data)
        elif "version:" in dna_data[:100]:
            # YAML format
            package = self._import_yaml(dna_data)
        else:
            # Try compressed
            try:
                import gzip

                decompressed = gzip.decompress(base64.b64decode(dna_data)).decode()
                package = self._import_json(decompressed)
            except:
                # Default to JSON
                package = self._import_json(dna_data)

        # Validate if requested
        if validate:
            self._validate_compatibility(package)

        # Cache the DNA
        self.dna_cache[package.dna.fingerprint] = package

        return package

    def breed_dna(
        self,
        parent1_path: str,
        parent2_path: str,
        breeding_strategy: str = "best_of_both",
        trait_weights: Optional[Dict[str, float]] = None,
    ) -> ConfigDNA:
        """
        Breed two configuration DNAs to create offspring

        Args:
            parent1_path: Path to first parent config or DNA export
            parent2_path: Path to second parent config or DNA export
            breeding_strategy: How to combine traits
            trait_weights: Custom weights for trait selection

        Returns:
            New ConfigDNA combining best traits from parents
        """
        # Get parent DNAs
        if parent1_path.endswith(".json"):
            with open(parent1_path) as f:
                parent1 = self.import_dna(f.read()).dna
        else:
            parent1 = self.analyzer.analyze_dna(parent1_path)

        if parent2_path.endswith(".json"):
            with open(parent2_path) as f:
                parent2 = self.import_dna(f.read()).dna
        else:
            parent2 = self.analyzer.analyze_dna(parent2_path)

        # Apply breeding strategy
        if breeding_strategy == "best_of_both":
            offspring = self._breed_best_of_both(parent1, parent2, trait_weights)
        elif breeding_strategy == "hybrid_vigor":
            offspring = self._breed_hybrid_vigor(parent1, parent2)
        elif breeding_strategy == "selective":
            offspring = self._breed_selective(parent1, parent2, trait_weights)
        elif breeding_strategy == "random_mix":
            offspring = self._breed_random_mix(parent1, parent2)
        else:
            offspring = self._breed_best_of_both(parent1, parent2, trait_weights)

        # Set breeding metadata
        offspring.lineage = ConfigLineage(
            generation=max(parent1.lineage.generation, parent2.lineage.generation) + 1,
            timestamp=datetime.now(),
            parent_hash=f"{parent1.fingerprint}+{parent2.fingerprint}",
            mutations=self._identify_mutations(parent1, parent2, offspring),
            fitness_score=self._calculate_fitness(offspring),
        )

        # Update fingerprint for offspring
        offspring.fingerprint = self._generate_fingerprint(offspring)

        return offspring

    def apply_dna(
        self, dna_package: DNAPackage, target_config: str, preserve_custom: bool = True
    ) -> str:
        """
        Apply imported DNA to current configuration

        Args:
            dna_package: Imported DNA package
            target_config: Path to target configuration
            preserve_custom: Keep custom local settings

        Returns:
            New configuration with applied DNA
        """
        # Load current config
        if Path(target_config).exists():
            current_config = Path(target_config).read_text()
        else:
            current_config = self._generate_base_config()

        # Extract genes to apply
        genes_to_apply = dna_package.dna.genes

        # Generate new configuration
        new_config = self._apply_genes_to_config(
            current_config, genes_to_apply, preserve_custom
        )

        # Add DNA metadata as comments
        dna_header = f"""# Configuration DNA Applied
# Fingerprint: {dna_package.dna.fingerprint}
# Profile: {dna_package.dna.profile_type}
# Applied: {datetime.now().isoformat()}
# Source: {dna_package.source_system or 'Unknown'}

"""

        return dna_header + new_config

    def compare_dna_packages(
        self, package1: DNAPackage, package2: DNAPackage
    ) -> Dict[str, Any]:
        """
        Compare two DNA packages for compatibility and differences

        Args:
            package1: First DNA package
            package2: Second DNA package

        Returns:
            Comparison results
        """
        comparison = {
            "compatible": True,
            "similarity_score": 0.0,
            "shared_genes": [],
            "unique_to_first": [],
            "unique_to_second": [],
            "conflicts": [],
            "breeding_potential": 0.0,
        }

        # Check version compatibility
        if package1.nixos_version and package2.nixos_version:
            v1_major = package1.nixos_version.split(".")[0]
            v2_major = package2.nixos_version.split(".")[0]
            if v1_major != v2_major:
                comparison["compatible"] = False
                comparison["conflicts"].append(
                    f"NixOS version mismatch: {package1.nixos_version} vs {package2.nixos_version}"
                )

        # Compare genes
        genes1 = {g.name: g for g in package1.dna.genes}
        genes2 = {g.name: g for g in package2.dna.genes}

        shared = set(genes1.keys()) & set(genes2.keys())
        unique1 = set(genes1.keys()) - set(genes2.keys())
        unique2 = set(genes2.keys()) - set(genes1.keys())

        comparison["shared_genes"] = list(shared)
        comparison["unique_to_first"] = list(unique1)
        comparison["unique_to_second"] = list(unique2)

        # Calculate similarity
        total_genes = len(set(genes1.keys()) | set(genes2.keys()))
        if total_genes > 0:
            comparison["similarity_score"] = len(shared) / total_genes

        # Calculate breeding potential
        # Higher diversity = better breeding potential
        comparison["breeding_potential"] = 1.0 - comparison["similarity_score"]

        # Check for conflicts
        for gene_name in shared:
            gene1 = genes1[gene_name]
            gene2 = genes2[gene_name]
            if gene1.impact == "high" and gene2.impact == "high":
                if gene1.pattern != gene2.pattern:
                    comparison["conflicts"].append(
                        f"Conflicting high-impact gene: {gene_name}"
                    )

        return comparison

    def _breed_best_of_both(
        self,
        parent1: ConfigDNA,
        parent2: ConfigDNA,
        trait_weights: Optional[Dict[str, float]] = None,
    ) -> ConfigDNA:
        """Breed by selecting best traits from each parent"""
        # Combine genes, preferring higher fitness
        all_genes = {}

        for gene in parent1.genes:
            all_genes[gene.name] = gene

        for gene in parent2.genes:
            if gene.name in all_genes:
                # Choose better gene based on prevalence/impact
                existing = all_genes[gene.name]
                if gene.prevalence > existing.prevalence:
                    all_genes[gene.name] = gene
            else:
                all_genes[gene.name] = gene

        # Create offspring DNA
        offspring = ConfigDNA(
            fingerprint="",  # Will be updated
            genes=list(all_genes.values()),
            lineage=ConfigLineage(
                generation=0,
                timestamp=datetime.now(),
                parent_hash=None,
                mutations=[],
                fitness_score=0.0,
            ),
            profile_type=self._determine_profile_type(all_genes.values()),
            complexity_score=(parent1.complexity_score + parent2.complexity_score) / 2,
            evolution_stage="bred",
            similar_configs=[],
            inherited_traits=[],
            mutations=[],
            gene_diversity=self._calculate_diversity(all_genes.values()),
            mutation_rate=0.1,
            stability_score=(parent1.stability_score + parent2.stability_score) / 2,
            beneficial_mutations=[],
            harmful_patterns=[],
            evolution_path=["Continue evolution", "Monitor health"],
            confidence=0.75,
        )

        return offspring

    def _breed_hybrid_vigor(self, parent1: ConfigDNA, parent2: ConfigDNA) -> ConfigDNA:
        """Breed for hybrid vigor - combine diverse traits"""
        # Take unique genes from each parent
        genes1 = {g.name: g for g in parent1.genes}
        genes2 = {g.name: g for g in parent2.genes}

        # Keep all unique genes
        offspring_genes = []

        # Add unique from parent1
        for name, gene in genes1.items():
            if name not in genes2:
                offspring_genes.append(gene)

        # Add unique from parent2
        for name, gene in genes2.items():
            if name not in genes1:
                offspring_genes.append(gene)

        # For shared genes, alternate selection
        shared = set(genes1.keys()) & set(genes2.keys())
        use_parent1 = True
        for gene_name in shared:
            if use_parent1:
                offspring_genes.append(genes1[gene_name])
            else:
                offspring_genes.append(genes2[gene_name])
            use_parent1 = not use_parent1

        # Create vigorous offspring
        offspring = ConfigDNA(
            fingerprint="",
            genes=offspring_genes,
            lineage=ConfigLineage(
                generation=0,
                timestamp=datetime.now(),
                parent_hash=None,
                mutations=["hybrid_vigor"],
                fitness_score=0.9,
            ),
            profile_type="hybrid",
            complexity_score=max(parent1.complexity_score, parent2.complexity_score),
            evolution_stage="hybrid",
            similar_configs=[],
            inherited_traits=[],
            mutations=["hybrid_vigor"],
            gene_diversity=0.9,  # High diversity from hybrid
            mutation_rate=0.15,  # Higher mutation rate for hybrids
            stability_score=0.8,
            beneficial_mutations=["hybrid_vigor", "diverse_genetics"],
            harmful_patterns=[],
            evolution_path=["Leverage hybrid advantages"],
            confidence=0.8,
        )

        return offspring

    def _breed_selective(
        self, parent1: ConfigDNA, parent2: ConfigDNA, trait_weights: Dict[str, float]
    ) -> ConfigDNA:
        """Selective breeding based on specific trait weights"""
        # Select genes based on weights
        offspring_genes = []

        for category, weight in trait_weights.items():
            # Get genes from this category
            p1_genes = [g for g in parent1.genes if g.category == category]
            p2_genes = [g for g in parent2.genes if g.category == category]

            # Select based on weight (higher weight = prefer parent1)
            import random

            for gene in p1_genes:
                if random.random() < weight:
                    offspring_genes.append(gene)

            for gene in p2_genes:
                if random.random() < (1 - weight):
                    offspring_genes.append(gene)

        offspring = ConfigDNA(
            fingerprint="",
            genes=offspring_genes,
            lineage=ConfigLineage(
                generation=0,
                timestamp=datetime.now(),
                parent_hash=None,
                mutations=["selective_breeding"],
                fitness_score=0.85,
            ),
            profile_type="custom",
            complexity_score=(parent1.complexity_score + parent2.complexity_score) / 2,
            evolution_stage="selected",
            similar_configs=[],
            inherited_traits=[],
            mutations=["selective_breeding"],
            gene_diversity=0.7,
            mutation_rate=0.05,  # Low mutation for selected traits
            stability_score=0.85,
            beneficial_mutations=["selective_optimization"],
            harmful_patterns=[],
            evolution_path=["Maintain selected traits"],
            confidence=0.9,
        )

        return offspring

    def _breed_random_mix(self, parent1: ConfigDNA, parent2: ConfigDNA) -> ConfigDNA:
        """Random mixing of genes from both parents"""
        import random

        all_genes = list(parent1.genes) + list(parent2.genes)
        random.shuffle(all_genes)

        # Take random subset
        num_genes = (len(parent1.genes) + len(parent2.genes)) // 2
        offspring_genes = all_genes[:num_genes]

        offspring = ConfigDNA(
            fingerprint="",
            genes=offspring_genes,
            lineage=ConfigLineage(
                generation=0,
                timestamp=datetime.now(),
                parent_hash=None,
                mutations=["random_mix"],
                fitness_score=0.5,  # Unknown fitness
            ),
            profile_type="experimental",
            complexity_score=(parent1.complexity_score + parent2.complexity_score) / 2,
            evolution_stage="experimental",
            similar_configs=[],
            inherited_traits=[],
            mutations=["random_mix"],
            gene_diversity=0.8,
            mutation_rate=0.2,  # High mutation for random mix
            stability_score=0.5,  # Unknown stability
            beneficial_mutations=[],
            harmful_patterns=[],
            evolution_path=["Test and refine"],
            confidence=0.5,
        )

        return offspring

    def _export_json(self, package: DNAPackage) -> str:
        """Export DNA package as JSON"""
        # Convert to dict
        data = {
            "version": package.version,
            "exported_at": package.exported_at.isoformat(),
            "source_system": package.source_system,
            "description": package.description,
            "author": package.author,
            "tags": package.tags,
            "nixos_version": package.nixos_version,
            "required_features": package.required_features,
            "parent_dnas": package.parent_dnas,
            "generation": package.generation,
            "dna": {
                "fingerprint": package.dna.fingerprint,
                "profile_type": package.dna.profile_type,
                "complexity_score": package.dna.complexity_score,
                "evolution_stage": package.dna.evolution_stage,
                "gene_diversity": package.dna.gene_diversity,
                "stability_score": package.dna.stability_score,
                "mutation_rate": package.dna.mutation_rate,
                "genes": [
                    {
                        "name": g.name,
                        "category": g.category,
                        "pattern": g.pattern,
                        "description": g.description,
                        "impact": g.impact,
                        "prevalence": g.prevalence,
                    }
                    for g in package.dna.genes
                ],
            },
        }

        if hasattr(package, "raw_config"):
            data["raw_config"] = package.raw_config

        return json.dumps(data, indent=2)

    def _export_yaml(self, package: DNAPackage) -> str:
        """Export DNA package as YAML"""
        try:
            import yaml

            data = json.loads(self._export_json(package))
            return yaml.dump(data, default_flow_style=False)
        except ImportError:
            # Fallback to JSON if YAML not available
            return self._export_json(package)

    def _export_nix(self, package: DNAPackage) -> str:
        """Export DNA package as Nix expression"""
        nix = []
        nix.append("# DNA Configuration Export")
        nix.append(f"# Fingerprint: {package.dna.fingerprint}")
        nix.append(f"# Profile: {package.dna.profile_type}")
        nix.append(f"# Exported: {package.exported_at.isoformat()}")
        nix.append("")
        nix.append("{")
        nix.append("  dna = {")
        nix.append(f'    fingerprint = "{package.dna.fingerprint}";')
        nix.append(f'    profile = "{package.dna.profile_type}";')
        nix.append(f"    complexity = {package.dna.complexity_score};")
        nix.append("")
        nix.append("    genes = [")

        for gene in package.dna.genes[:10]:  # Limit to key genes
            nix.append("      {")
            nix.append(f'        name = "{gene.name}";')
            nix.append(f'        category = "{gene.category}";')
            nix.append(f'        impact = "{gene.impact}";')
            nix.append("      }")

        nix.append("    ];")
        nix.append("  };")
        nix.append("}")

        return "\n".join(nix)

    def _export_compressed(self, package: DNAPackage) -> str:
        """Export compressed DNA package"""
        import gzip

        json_data = self._export_json(package)
        compressed = gzip.compress(json_data.encode())
        return base64.b64encode(compressed).decode()

    def _import_json(self, data: str) -> DNAPackage:
        """Import DNA package from JSON"""
        parsed = json.loads(data)

        # Reconstruct genes
        genes = []
        for g in parsed["dna"]["genes"]:
            genes.append(
                ConfigGene(
                    name=g["name"],
                    category=g["category"],
                    pattern=g["pattern"],
                    description=g["description"],
                    impact=g["impact"],
                    prevalence=g["prevalence"],
                )
            )

        # Reconstruct DNA
        dna = ConfigDNA(
            fingerprint=parsed["dna"]["fingerprint"],
            genes=genes,
            lineage=ConfigLineage(
                generation=0,
                timestamp=datetime.now(),
                parent_hash=None,
                mutations=[],
                fitness_score=0.0,
            ),
            profile_type=parsed["dna"]["profile_type"],
            complexity_score=parsed["dna"]["complexity_score"],
            evolution_stage=parsed["dna"]["evolution_stage"],
            similar_configs=[],
            inherited_traits=[],
            mutations=[],
            gene_diversity=parsed["dna"]["gene_diversity"],
            mutation_rate=parsed["dna"]["mutation_rate"],
            stability_score=parsed["dna"]["stability_score"],
            beneficial_mutations=[],
            harmful_patterns=[],
            evolution_path=[],
            confidence=0.0,
        )

        # Create package
        package = DNAPackage(
            version=parsed["version"],
            exported_at=datetime.fromisoformat(parsed["exported_at"]),
            source_system=parsed.get("source_system"),
            dna=dna,
            description=parsed.get("description"),
            author=parsed.get("author"),
            tags=parsed.get("tags", []),
            nixos_version=parsed.get("nixos_version"),
            required_features=parsed.get("required_features", []),
            parent_dnas=parsed.get("parent_dnas", []),
            generation=parsed.get("generation", 0),
        )

        if "raw_config" in parsed:
            package.raw_config = parsed["raw_config"]

        return package

    def _import_yaml(self, data: str) -> DNAPackage:
        """Import DNA package from YAML"""
        try:
            import yaml

            parsed = yaml.safe_load(data)
            return self._import_json(json.dumps(parsed))
        except ImportError:
            raise ValueError("YAML support not available")

    def _import_nix(self, data: str) -> DNAPackage:
        """Import DNA package from Nix expression"""
        # Simple parser for Nix format
        # In production, would use proper Nix parser
        raise NotImplementedError("Nix import not yet implemented")

    def _get_system_info(self) -> str:
        """Get system information"""
        import platform

        return f"{platform.node()} ({platform.system()} {platform.release()})"

    def _get_nixos_version(self) -> Optional[str]:
        """Get NixOS version"""
        try:
            version_file = Path("/etc/nixos-version")
            if version_file.exists():
                return version_file.read_text().strip()
        except:
            pass
        return None

    def _get_author_info(self) -> str:
        """Get author information"""
        import os

        return os.environ.get("USER", "unknown")

    def _validate_compatibility(self, package: DNAPackage):
        """Validate DNA package compatibility"""
        # Check NixOS version
        current_version = self._get_nixos_version()
        if current_version and package.nixos_version:
            current_major = current_version.split(".")[0]
            package_major = package.nixos_version.split(".")[0]
            if current_major != package_major:
                import warnings

                warnings.warn(
                    f"NixOS version mismatch: {current_version} vs {package.nixos_version}"
                )

    def _generate_fingerprint(self, dna: ConfigDNA) -> str:
        """Generate unique fingerprint for DNA"""
        hasher = hashlib.sha256()
        for gene in sorted(dna.genes, key=lambda g: g.name):
            hasher.update(f"{gene.name}{gene.category}{gene.pattern}".encode())
        return hasher.hexdigest()[:16]

    def _identify_mutations(
        self, parent1: ConfigDNA, parent2: ConfigDNA, offspring: ConfigDNA
    ) -> List[str]:
        """Identify mutations in offspring"""
        mutations = []

        # Check for new genes not in parents
        parent_genes = set(g.name for g in parent1.genes + parent2.genes)
        offspring_genes = set(g.name for g in offspring.genes)

        new_genes = offspring_genes - parent_genes
        if new_genes:
            mutations.append(f"New genes: {', '.join(new_genes)}")

        # Check for lost genes
        lost_genes = parent_genes - offspring_genes
        if lost_genes:
            mutations.append(f"Lost genes: {', '.join(lost_genes)}")

        return mutations

    def _calculate_fitness(self, dna: ConfigDNA) -> float:
        """Calculate fitness score for DNA"""
        fitness = 0.5  # Base fitness

        # Diversity bonus
        fitness += dna.gene_diversity * 0.2

        # Stability bonus
        fitness += dna.stability_score * 0.2

        # Complexity penalty (too complex is bad)
        if dna.complexity_score > 80:
            fitness -= 0.1

        # Harmful patterns penalty
        fitness -= len(dna.harmful_patterns) * 0.05

        # Beneficial mutations bonus
        fitness += len(dna.beneficial_mutations) * 0.05

        return min(1.0, max(0.0, fitness))

    def _determine_profile_type(self, genes) -> str:
        """Determine profile type from genes"""
        categories = {}
        for gene in genes:
            if gene.category not in categories:
                categories[gene.category] = 0
            categories[gene.category] += 1

        # Find dominant category
        if categories:
            dominant = max(categories, key=categories.get)
            if dominant == "development":
                return "developer"
            elif dominant == "desktop":
                return "desktop"
            elif dominant == "server":
                return "server"

        return "hybrid"

    def _calculate_diversity(self, genes) -> float:
        """Calculate gene diversity"""
        if not genes:
            return 0.0

        categories = set(g.category for g in genes)
        return len(categories) / 10.0  # Assume 10 max categories

    def _generate_base_config(self) -> str:
        """Generate base NixOS configuration"""
        return """{ config, pkgs, ... }:

{
  imports = [ ./hardware-configuration.nix ];

  # DNA-applied configuration will be added here

  system.stateVersion = "24.11";
}"""

    def _apply_genes_to_config(
        self, current_config: str, genes: List[ConfigGene], preserve_custom: bool
    ) -> str:
        """Apply genes to configuration"""
        # This would parse and modify the Nix configuration
        # For now, return with comments about genes

        gene_comments = []
        for gene in genes[:10]:  # Top 10 genes
            gene_comments.append(
                f"  # Gene: {gene.name} ({gene.category}) - {gene.description}"
            )

        return current_config + "\n\n" + "\n".join(gene_comments)
