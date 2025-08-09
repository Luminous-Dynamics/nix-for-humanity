#!/usr/bin/env python3
"""
Download comprehensive Nix/NixOS documentation for training
Includes official docs, thesis, best practices, and community wisdom
"""

import os
import time
import json
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import subprocess
from typing import Dict, List, Optional
import hashlib

class NixDocumentationDownloader:
    def __init__(self, output_dir: str = "training-data/nix-docs-comprehensive"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NixForHumanity-DocCollector/1.0 (Educational; Training LLMs on Nix)'
        })
        
        # Track what we've downloaded to avoid duplicates
        self.downloaded = set()
        self.metadata_file = self.output_dir / "download_metadata.json"
        self.load_metadata()
    
    def load_metadata(self):
        """Load previous download metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file) as f:
                data = json.load(f)
                self.downloaded = set(data.get('downloaded', []))
    
    def save_metadata(self):
        """Save download metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump({
                'downloaded': list(self.downloaded),
                'last_update': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=2)
    
    def download_file(self, url: str, local_path: Path, description: str = "") -> bool:
        """Download a file with progress indication"""
        if url in self.downloaded:
            print(f"✓ Already downloaded: {description or url}")
            return True
        
        try:
            print(f"📥 Downloading: {description or url}")
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            # Write file
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.downloaded.add(url)
            self.save_metadata()
            time.sleep(1)  # Be respectful
            return True
            
        except Exception as e:
            print(f"❌ Failed to download {url}: {e}")
            return False
    
    def download_eelco_thesis(self):
        """Download Eelco Dolstra's PhD thesis - foundational Nix theory"""
        print("\n📚 Downloading Eelco Dolstra's PhD Thesis...")
        
        thesis_dir = self.output_dir / "thesis"
        thesis_dir.mkdir(exist_ok=True)
        
        # The thesis PDF
        thesis_url = "https://edolstra.github.io/pubs/phd-thesis.pdf"
        thesis_path = thesis_dir / "eelco-dolstra-phd-thesis.pdf"
        
        self.download_file(
            thesis_url, 
            thesis_path,
            "The Purely Functional Software Deployment Model (PhD Thesis)"
        )
        
        # Also save metadata about the thesis
        thesis_meta = {
            "title": "The Purely Functional Software Deployment Model",
            "author": "Eelco Dolstra",
            "year": 2006,
            "institution": "Utrecht University",
            "importance": "Foundational work that established Nix's theoretical basis",
            "key_concepts": [
                "Purely functional deployment",
                "Cryptographic hashing for dependencies",
                "Nix store model",
                "Derivations",
                "Binary substitutes"
            ]
        }
        
        with open(thesis_dir / "thesis_metadata.json", 'w') as f:
            json.dump(thesis_meta, f, indent=2)
    
    def download_nix_papers(self):
        """Download academic papers about Nix"""
        print("\n📄 Downloading Nix Academic Papers...")
        
        papers_dir = self.output_dir / "papers"
        papers_dir.mkdir(exist_ok=True)
        
        papers = [
            {
                "url": "https://edolstra.github.io/pubs/nixos-jfp-final.pdf",
                "filename": "nixos-purely-functional-linux.pdf",
                "title": "NixOS: A Purely Functional Linux Distribution"
            },
            {
                "url": "https://edolstra.github.io/pubs/nspfssd-lisa2004-final.pdf",
                "filename": "nix-safe-policy-free-deployment.pdf",
                "title": "Nix: A Safe and Policy-Free System for Software Deployment"
            }
        ]
        
        for paper in papers:
            self.download_file(
                paper["url"],
                papers_dir / paper["filename"],
                paper["title"]
            )
    
    def download_official_manuals(self):
        """Download official Nix and NixOS manuals"""
        print("\n📖 Downloading Official Manuals...")
        
        manuals_dir = self.output_dir / "manuals"
        manuals_dir.mkdir(exist_ok=True)
        
        # Download manuals as single-page HTML for easier processing
        manuals = [
            {
                "name": "nix-manual",
                "url": "https://nixos.org/manual/nix/stable/",
                "single_page": "https://nixos.org/manual/nix/stable/manual.html"
            },
            {
                "name": "nixos-manual", 
                "url": "https://nixos.org/manual/nixos/stable/",
                "single_page": "https://nixos.org/manual/nixos/stable/index.html"
            },
            {
                "name": "nixpkgs-manual",
                "url": "https://nixos.org/manual/nixpkgs/stable/",
                "single_page": "https://nixos.org/manual/nixpkgs/stable/"
            }
        ]
        
        for manual in manuals:
            manual_dir = manuals_dir / manual["name"]
            manual_dir.mkdir(exist_ok=True)
            
            # Try to download the manual
            if "single_page" in manual:
                self.download_file(
                    manual["single_page"],
                    manual_dir / "manual.html",
                    f"{manual['name']} (HTML)"
                )
    
    def download_nix_pills(self):
        """Download Nix Pills - the beloved tutorial series"""
        print("\n💊 Downloading Nix Pills...")
        
        pills_dir = self.output_dir / "nix-pills"
        pills_dir.mkdir(exist_ok=True)
        
        # Nix Pills are numbered chapters
        base_url = "https://nixos.org/guides/nix-pills/"
        
        try:
            # First, get the index to find all chapters
            response = self.session.get(base_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all pill links
            pill_links = soup.find_all('a', href=True)
            chapter_count = 0
            
            for link in pill_links:
                href = link['href']
                if 'pill' in href and href.endswith('.html'):
                    pill_url = urljoin(base_url, href)
                    pill_name = Path(href).stem
                    
                    self.download_file(
                        pill_url,
                        pills_dir / f"{pill_name}.html",
                        f"Nix Pill: {link.text.strip()}"
                    )
                    chapter_count += 1
            
            print(f"✓ Downloaded {chapter_count} Nix Pills")
            
        except Exception as e:
            print(f"⚠️  Error downloading Nix Pills: {e}")
    
    def download_best_practices(self):
        """Download Nix best practices from various sources"""
        print("\n🌟 Downloading Best Practices...")
        
        practices_dir = self.output_dir / "best-practices"
        practices_dir.mkdir(exist_ok=True)
        
        # Key best practices resources
        resources = [
            {
                "url": "https://nix.dev/",
                "name": "nix.dev",
                "description": "Official learning resource with best practices"
            },
            {
                "url": "https://zero-to-nix.com/",
                "name": "zero-to-nix",
                "description": "Modern Nix introduction with best practices"
            },
            {
                "url": "https://github.com/nix-community/awesome-nix",
                "name": "awesome-nix",
                "description": "Curated list of Nix resources"
            }
        ]
        
        # For now, save the URLs and descriptions
        # In production, we'd scrape these sites respecting robots.txt
        resources_meta = practices_dir / "resources.json"
        with open(resources_meta, 'w') as f:
            json.dump(resources, f, indent=2)
        
        # Download specific best practices documents if available
        best_practices_content = {
            "anti_patterns": [
                "Avoid using nix-env -i for permanent installations",
                "Don't use channels in production - use flakes or pinned nixpkgs",
                "Avoid impure derivations depending on network state",
                "Don't hardcode paths - use Nix store paths",
                "Avoid mutable state in derivations"
            ],
            "patterns": [
                "Use overlays for package customization",
                "Pin nixpkgs versions for reproducibility", 
                "Use flakes for modern Nix development",
                "Leverage binary caches for faster builds",
                "Write tests for your Nix expressions",
                "Use lib functions instead of reinventing",
                "Structure configuration with modules"
            ],
            "security": [
                "Use sandbox for builds",
                "Verify package hashes",
                "Use allowed-users for nix-daemon",
                "Be careful with IFD (Import From Derivation)",
                "Review fixed-output derivations carefully"
            ]
        }
        
        with open(practices_dir / "collected_best_practices.json", 'w') as f:
            json.dump(best_practices_content, f, indent=2)
    
    def download_rfcs(self):
        """Download important Nix RFCs"""
        print("\n📋 Downloading Nix RFCs...")
        
        rfcs_dir = self.output_dir / "rfcs"
        rfcs_dir.mkdir(exist_ok=True)
        
        # Key RFCs that explain design decisions
        important_rfcs = [
            {
                "number": "0049",
                "title": "Flakes",
                "url": "https://github.com/NixOS/rfcs/blob/master/rfcs/0049-flakes.md"
            },
            {
                "number": "0042",
                "title": "NixOS Settings Options",
                "url": "https://github.com/NixOS/rfcs/blob/master/rfcs/0042-config-option.md"
            },
            {
                "number": "0072",
                "title": "Nix Path Configuration",
                "url": "https://github.com/NixOS/rfcs/blob/master/rfcs/0072-nix-path.md"
            }
        ]
        
        rfc_meta = []
        for rfc in important_rfcs:
            rfc_meta.append({
                "number": rfc["number"],
                "title": rfc["title"],
                "url": rfc["url"],
                "status": "See GitHub for current status"
            })
        
        with open(rfcs_dir / "rfc_list.json", 'w') as f:
            json.dump(rfc_meta, f, indent=2)
    
    def download_cookbook_examples(self):
        """Download practical cookbook examples"""
        print("\n🍳 Collecting Cookbook Examples...")
        
        cookbook_dir = self.output_dir / "cookbook"
        cookbook_dir.mkdir(exist_ok=True)
        
        # Common patterns and solutions
        cookbook = {
            "common_tasks": {
                "install_package": {
                    "imperative": "nix-env -iA nixos.firefox",
                    "declarative": "environment.systemPackages = [ pkgs.firefox ];",
                    "flake": "nix profile install nixpkgs#firefox"
                },
                "update_system": {
                    "channel": "sudo nix-channel --update && sudo nixos-rebuild switch",
                    "flake": "sudo nixos-rebuild switch --flake /etc/nixos#hostname"
                },
                "rollback": {
                    "command": "sudo nixos-rebuild switch --rollback",
                    "explanation": "Reverts to previous system generation"
                }
            },
            "development_shells": {
                "python": """
{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = with pkgs; [
    python3
    python3Packages.pip
    python3Packages.virtualenv
  ];
}""",
                "rust": """
{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = with pkgs; [
    rustc
    cargo
    rustfmt
    rust-analyzer
  ];
}"""
            },
            "flake_templates": {
                "basic": """
{
  description = "A basic flake";
  
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };
  
  outputs = { self, nixpkgs }: {
    # Your outputs here
  };
}"""
            }
        }
        
        with open(cookbook_dir / "nix_cookbook.json", 'w') as f:
            json.dump(cookbook, f, indent=2)
    
    def create_training_summary(self):
        """Create a summary of all downloaded content"""
        print("\n📊 Creating Training Summary...")
        
        summary = {
            "collection_date": time.strftime('%Y-%m-%d %H:%M:%S'),
            "content_categories": {
                "foundational_theory": {
                    "description": "Core theoretical foundations of Nix",
                    "includes": ["PhD thesis", "Academic papers", "RFCs"]
                },
                "official_documentation": {
                    "description": "Official manuals and guides",
                    "includes": ["Nix manual", "NixOS manual", "Nixpkgs manual"]
                },
                "tutorials": {
                    "description": "Learning resources and tutorials",
                    "includes": ["Nix Pills", "nix.dev", "zero-to-nix"]
                },
                "best_practices": {
                    "description": "Community wisdom and patterns",
                    "includes": ["Anti-patterns", "Security practices", "Common patterns"]
                },
                "practical_examples": {
                    "description": "Real-world usage examples",
                    "includes": ["Cookbook", "Flake examples", "Shell templates"]
                }
            },
            "training_recommendations": {
                "order": [
                    "1. Start with Nix Pills for conceptual understanding",
                    "2. Study the thesis for deep theoretical knowledge",
                    "3. Reference manuals for comprehensive coverage",
                    "4. Learn best practices to avoid common mistakes",
                    "5. Use cookbook examples for practical patterns"
                ],
                "focus_areas": [
                    "Declarative vs imperative approaches",
                    "Flakes as the modern way",
                    "Security considerations",
                    "Reproducibility principles",
                    "Development workflows"
                ]
            }
        }
        
        with open(self.output_dir / "training_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
    
    def download_all(self):
        """Download all documentation"""
        print("🚀 Starting Comprehensive Nix Documentation Download")
        print("=" * 50)
        
        # Core downloads
        self.download_eelco_thesis()
        self.download_nix_papers()
        self.download_official_manuals()
        self.download_nix_pills()
        self.download_best_practices()
        self.download_rfcs()
        self.download_cookbook_examples()
        
        # Create summary
        self.create_training_summary()
        
        print("\n✅ Documentation download complete!")
        print(f"📁 All content saved to: {self.output_dir}")
        print("\n📚 Recommended reading order:")
        print("  1. Nix Pills (tutorial)")
        print("  2. Eelco's thesis (theory)")  
        print("  3. Official manuals (reference)")
        print("  4. Best practices (wisdom)")
        print("  5. Cookbook (practical)")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Download comprehensive Nix documentation for training"
    )
    parser.add_argument(
        "--output-dir",
        default="training-data/nix-docs-comprehensive",
        help="Output directory for downloaded documentation"
    )
    parser.add_argument(
        "--thesis-only",
        action="store_true",
        help="Download only Eelco's PhD thesis"
    )
    
    args = parser.parse_args()
    
    downloader = NixDocumentationDownloader(args.output_dir)
    
    if args.thesis_only:
        downloader.download_eelco_thesis()
    else:
        downloader.download_all()


if __name__ == "__main__":
    main()