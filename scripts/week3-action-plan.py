#!/usr/bin/env python3
"""Week 3 Action Plan - Building on Strengths"""

import json
from pathlib import Path
from datetime import datetime

def create_action_plan():
    """Create a detailed action plan for Week 3."""
    
    plan = {
        "week": 3,
        "theme": "Polish & Performance - Making Excellence Visible",
        "generated": datetime.now().isoformat(),
        "context": {
            "current_score": 7.0,
            "target_score": 8.5,
            "validated_strengths": [
                "Native API: 9064x faster (0.29ms avg)",
                "NLP: 4.54ms processing time",
                "Project structure: 10/10",
                "Type hints: 78.6% coverage"
            ],
            "working_features": [
                "Natural Language (4/5 tests)",
                "Native API (100%)",
                "Generation Management",
                "Settings/Profiles"
            ],
            "broken_features": [
                "TUI (not connected)",
                "Smart Discovery (1/4 tests)",
                "Flake Support (0/3 tests)",
                "Error Handling (0/3 tests)"
            ]
        },
        "priorities": [
            {
                "id": 1,
                "title": "Fix Natural Language CLI (4/5 → 5/5)",
                "impact": "High - First user touchpoint",
                "effort": "Low - One test failing",
                "tasks": [
                    "Identify which natural language test is failing",
                    "Fix the specific parsing/intent issue",
                    "Add regression tests",
                    "Update CLI examples in README"
                ]
            },
            {
                "id": 2,
                "title": "Create Performance Showcase",
                "impact": "High - Validates core value prop",
                "effort": "Low - Data already exists",
                "tasks": [
                    "Create performance comparison script",
                    "Generate visual benchmarks",
                    "Add performance section to README",
                    "Create demo video/GIF"
                ]
            },
            {
                "id": 3,
                "title": "Fix Import Issues",
                "impact": "High - Blocks contributors",
                "effort": "Medium - Multiple files",
                "tasks": [
                    "Fix circular imports in core/engine.py",
                    "Consolidate security module imports",
                    "Create import test script",
                    "Document module structure"
                ]
            },
            {
                "id": 4,
                "title": "Smart Discovery Repair (1/4 → 4/4)",
                "impact": "Medium - Key differentiator",
                "effort": "Medium - Algorithm work",
                "tasks": [
                    "Analyze failing discovery tests",
                    "Fix fuzzy matching logic",
                    "Improve category detection",
                    "Add package metadata"
                ]
            },
            {
                "id": 5,
                "title": "Documentation Reality Check",
                "impact": "High - User trust",
                "effort": "Low - Update existing",
                "tasks": [
                    "Update README with real examples",
                    "Create WORKING_FEATURES.md",
                    "Add performance metrics",
                    "Remove aspirational claims"
                ]
            }
        ],
        "daily_goals": {
            "day1": {
                "focus": "Fix Natural Language CLI",
                "deliverables": [
                    "5/5 natural language tests passing",
                    "Updated CLI documentation"
                ]
            },
            "day2": {
                "focus": "Performance Showcase",
                "deliverables": [
                    "Performance comparison script",
                    "README performance section",
                    "Benchmark visualizations"
                ]
            },
            "day3": {
                "focus": "Import & Structure Fixes",
                "deliverables": [
                    "All imports working",
                    "No circular dependencies",
                    "Import test suite"
                ]
            },
            "day4": {
                "focus": "Smart Discovery",
                "deliverables": [
                    "4/4 discovery tests passing",
                    "Improved fuzzy matching"
                ]
            },
            "day5": {
                "focus": "Polish & Documentation",
                "deliverables": [
                    "Honest README",
                    "Working examples",
                    "Quick start guide"
                ]
            }
        },
        "success_metrics": {
            "quantitative": {
                "natural_language_tests": "5/5 (from 4/5)",
                "smart_discovery_tests": "4/4 (from 1/4)",
                "working_features": "5/10 (from 3/10)",
                "import_errors": "0 (from unknown)",
                "performance_documented": True
            },
            "qualitative": {
                "contributor_experience": "Can run code immediately",
                "user_trust": "README matches reality",
                "performance_visibility": "Benchmarks prominently displayed"
            }
        },
        "scripts_to_create": [
            "scripts/find-failing-tests.py",
            "scripts/performance-comparison.py",
            "scripts/fix-imports.py",
            "scripts/test-smart-discovery.py",
            "scripts/generate-working-features.py"
        ]
    }
    
    # Save the plan
    with open('docs/planning/WEEK3_ACTION_PLAN.json', 'w') as f:
        json.dump(plan, f, indent=2)
    
    # Generate markdown version
    generate_markdown_plan(plan)
    
    print("✅ Week 3 Action Plan created")
    print("📄 JSON: docs/planning/WEEK3_ACTION_PLAN.json")
    print("📄 Markdown: docs/planning/WEEK3_ACTION_PLAN.md")

def generate_markdown_plan(plan):
    """Generate readable markdown version of the plan."""
    
    md = f"""# Week 3 Action Plan: {plan['theme']}

Generated: {plan['generated']}

## 🎯 Goal: {plan['context']['current_score']}/10 → {plan['context']['target_score']}/10

## 💪 Validated Strengths
{chr(10).join('- ' + s for s in plan['context']['validated_strengths'])}

## 🔧 Working Features (Build on These!)
{chr(10).join('- ' + f for f in plan['context']['working_features'])}

## ❌ Broken Features (Fix Strategically)
{chr(10).join('- ' + f for f in plan['context']['broken_features'])}

## 📋 Week 3 Priorities

"""
    
    for priority in plan['priorities']:
        md += f"### {priority['id']}. {priority['title']}\n"
        md += f"- **Impact**: {priority['impact']}\n"
        md += f"- **Effort**: {priority['effort']}\n"
        md += f"- **Tasks**:\n"
        for task in priority['tasks']:
            md += f"  - {task}\n"
        md += "\n"
    
    md += "## 📅 Daily Focus\n\n"
    for day, details in plan['daily_goals'].items():
        md += f"### {day.title()}: {details['focus']}\n"
        md += "**Deliverables**:\n"
        for deliverable in details['deliverables']:
            md += f"- {deliverable}\n"
        md += "\n"
    
    md += "## 📊 Success Metrics\n\n"
    md += "### Quantitative\n"
    for metric, value in plan['success_metrics']['quantitative'].items():
        md += f"- **{metric.replace('_', ' ').title()}**: {value}\n"
    
    md += "\n### Qualitative\n"
    for metric, value in plan['success_metrics']['qualitative'].items():
        md += f"- **{metric.replace('_', ' ').title()}**: {value}\n"
    
    md += f"\n## 🛠️ Scripts to Create\n"
    for script in plan['scripts_to_create']:
        md += f"- {script}\n"
    
    md += """
## 🚀 Key Insight

We have a PHENOMENAL performance story (9064x faster!) that nobody knows about. 
Week 3 is about making our strengths visible while systematically fixing the 
basics that users actually touch.

**Remember**: Fast software feels magical. Let's make sure users can experience 
that magic from their very first command.
"""
    
    with open('docs/planning/WEEK3_ACTION_PLAN.md', 'w') as f:
        f.write(md)

if __name__ == '__main__':
    create_action_plan()