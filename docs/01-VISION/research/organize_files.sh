#!/usr/bin/env bash

# Script to organize loose research files into appropriate subdirectories
# Based on content analysis and existing directory structure

cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/docs/01-VISION/research

# Technical deep-dives
mv "AI's Transcendence Through Technologies_.md" 02-SPECIALIZED-RESEARCH/technical/
mv "Advanced AI for NixOS_.md" 02-SPECIALIZED-RESEARCH/technical/
mv "Hybrid AI System Architecture_.md" 02-SPECIALIZED-RESEARCH/technical/
mv "NixOS AI Development Refined_.md" 02-SPECIALIZED-RESEARCH/technical/
mv "NixOS AI Evolution Research_.md" 02-SPECIALIZED-RESEARCH/technical/
mv "Robotics Integration for AI Partner_.md" 02-SPECIALIZED-RESEARCH/technical/

# Architecture synthesis and system design
mv "Forest Vision_ Polycentric System Design_.md" 02-SPECIALIZED-RESEARCH/architecture-synthesis/
mv "Project Architecture_ AI and Interface_.md" 02-SPECIALIZED-RESEARCH/architecture-synthesis/
mv "Architectural Refinement and Research Priorities_.md" 02-SPECIALIZED-RESEARCH/architecture-synthesis/
mv "Symbiotic AI Architecture Analysis_.md" 02-SPECIALIZED-RESEARCH/architecture-synthesis/

# Philosophical and civilization design
mv "Civilization Design_ Refinement and Inquiry_.md" 02-SPECIALIZED-RESEARCH/philosophical-inquiries/
mv "Oracle's Evolution_ Roadmap and Refinements_.md" 02-SPECIALIZED-RESEARCH/philosophical-inquiries/

# Kosmos-related philosophical concepts
mv "Fractal Kosmos_ Ethical Inquiries_.md" 02-SPECIALIZED-RESEARCH/kosmos-concepts/
mv "Fractal Kosmos_ Infinite Dimensions_.md" 02-SPECIALIZED-RESEARCH/kosmos-concepts/

# Core research and roadmaps  
mv "AI Symbiosis_ Architectural Roadmap Research_.md" 01-CORE-RESEARCH/
mv "AI Symbiosis_ Future Technologies_.md" 01-CORE-RESEARCH/

# Index and navigation files
mv "ENHANCED_RESEARCH_INDEX.md" archive/
mv "RESEARCH_NAVIGATION_GUIDE.md" archive/
mv "RESEARCH_ORGANIZATION_PLAN.md" archive/
mv "REORGANIZATION_PLAN.md" archive/

# Implementation and meta files
mv "IMPLEMENTATION_GUIDE.md" 04-IMPLEMENTATION-GUIDES/
mv "IMPLEMENTATION_VALIDATION.md" 04-IMPLEMENTATION-GUIDES/
mv "RESEARCH_IMPLEMENTATION_ROADMAP.md" 04-IMPLEMENTATION-GUIDES/
mv "META_SYNTHESIS.md" 01-CORE-RESEARCH/
mv "RESEARCH_SUMMARY.md" 01-CORE-RESEARCH/

# Multimedia catalog
mv "MULTIMEDIA_CATALOG.md" 03-VISUAL-RESEARCH/

echo "File organization complete!"