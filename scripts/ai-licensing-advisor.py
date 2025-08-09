#!/usr/bin/env python3
"""
from typing import List, Optional
AI Licensing Advisor for Nix for Humanity
Provides comprehensive licensing guidance for AI models and datasets
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum
import re

class LicenseType(Enum):
    """Common AI model and dataset licenses"""
    MIT = "MIT"
    APACHE_2 = "Apache-2.0"
    BSD_3 = "BSD-3-Clause"
    CC_BY = "CC-BY-4.0"
    CC_BY_SA = "CC-BY-SA-4.0"
    CC_BY_NC = "CC-BY-NC-4.0"
    CC_BY_NC_SA = "CC-BY-NC-SA-4.0"
    CC0 = "CC0-1.0"
    GPL_2 = "GPL-2.0"
    GPL_3 = "GPL-3.0"
    AGPL_3 = "AGPL-3.0"
    LGPL_3 = "LGPL-3.0"
    OPENRAIL = "OpenRAIL"
    OPENRAIL_M = "OpenRAIL-M"
    LLAMA = "Llama-2"
    GEMMA = "Gemma"
    CUSTOM = "Custom"
    UNKNOWN = "Unknown"

class CommercialUse(Enum):
    """Commercial use compatibility"""
    YES = "Yes - Safe for commercial use"
    NO = "No - Non-commercial only"
    RESTRICTED = "Restricted - Check specific terms"
    COPYLEFT = "Yes, but with copyleft obligations"
    CONDITIONAL = "Conditional - Requires compliance"

class AILicensingAdvisor:
    def __init__(self):
        self.base_dir = Path("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity")
        self.db_path = self.base_dir / "ai_licensing.db"
        self.init_db()
        
    def init_db(self):
        """Initialize AI licensing database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Model licenses table
        c.execute('''
            CREATE TABLE IF NOT EXISTS model_licenses (
                id INTEGER PRIMARY KEY,
                model_name TEXT NOT NULL UNIQUE,
                model_type TEXT,
                base_license TEXT NOT NULL,
                dataset_license TEXT,
                commercial_use TEXT NOT NULL,
                saas_compatible BOOLEAN,
                attribution_required BOOLEAN,
                share_alike BOOLEAN,
                modifications_allowed BOOLEAN,
                special_restrictions TEXT,
                alternatives TEXT,
                notes TEXT
            )
        ''')
        
        # License compatibility matrix
        c.execute('''
            CREATE TABLE IF NOT EXISTS license_compatibility (
                id INTEGER PRIMARY KEY,
                license_a TEXT NOT NULL,
                license_b TEXT NOT NULL,
                compatible BOOLEAN NOT NULL,
                compatibility_notes TEXT,
                UNIQUE(license_a, license_b)
            )
        ''')
        
        # License details
        c.execute('''
            CREATE TABLE IF NOT EXISTS license_details (
                id INTEGER PRIMARY KEY,
                license_name TEXT NOT NULL UNIQUE,
                full_name TEXT,
                commercial_use TEXT,
                copyleft BOOLEAN,
                patent_grant BOOLEAN,
                saas_loophole BOOLEAN,
                key_obligations TEXT,
                common_uses TEXT,
                avoid_if TEXT
            )
        ''')
        
        # Populate initial data
        self._populate_model_licenses(c)
        self._populate_license_details(c)
        self._populate_compatibility_matrix(c)
        
        conn.commit()
        conn.close()
        
    def _populate_model_licenses(self, cursor):
        """Populate model licensing information"""
        models = [
            # Open source friendly models
            ("mistral-7b", "LLM", "Apache-2.0", "Mixed", "Yes - Safe for commercial use", 
             True, False, False, True, None, None, 
             "Excellent choice for commercial use, no restrictions"),
            
            ("llama-2-7b", "LLM", "Llama-2", "Mixed", "Conditional - Requires compliance",
             True, False, False, True, "Custom license with commercial use restrictions for >700M MAU",
             "mistral-7b, falcon-7b", 
             "Commercial use allowed but requires acceptance of Llama 2 license"),
            
            ("llama-3-8b", "LLM", "Llama-2", "Mixed", "Conditional - Requires compliance",
             True, False, False, True, "Monthly active users < 700M for commercial use",
             "mistral-7b, gemma-7b",
             "Updated Llama license, still has MAU restrictions"),
            
            ("falcon-7b", "LLM", "Apache-2.0", "Mixed", "Yes - Safe for commercial use",
             True, False, False, True, None, None,
             "Fully open source, no restrictions"),
            
            ("gpt2", "LLM", "MIT", "WebText", "Yes - Safe for commercial use",
             True, False, False, True, None, None,
             "One of the most permissive model licenses"),
            
            ("bert-base", "LLM", "Apache-2.0", "BookCorpus+Wikipedia", "Yes - Safe for commercial use",
             True, False, False, True, None, None,
             "Standard Apache 2.0, safe for all uses"),
            
            # Restricted models
            ("stable-diffusion-1.5", "Diffusion", "OpenRAIL-M", "LAION-2B", "Restricted - Check specific terms",
             True, True, False, True, "No illegal use, no harm, must display license",
             "stable-diffusion-xl, kandinsky-2",
             "OpenRAIL-M has use-based restrictions"),
            
            ("stable-diffusion-xl", "Diffusion", "OpenRAIL-M", "LAION-2B", "Restricted - Check specific terms",
             True, True, False, True, "Ethical use restrictions apply",
             "kandinsky-2, wurstchen",
             "Same OpenRAIL-M restrictions as SD 1.5"),
            
            # Research only models
            ("imagenet-21k", "Vision", "Custom", "ImageNet", "No - Non-commercial only",
             False, True, False, False, "Research use only, no commercial use",
             "open-images, laion-400m",
             "ImageNet license prohibits commercial use"),
            
            # GPL/AGPL models (rare but important)
            ("gpl-bert", "LLM", "GPL-3.0", "Mixed", "Yes, but with copyleft obligations",
             False, True, True, True, "Must open source entire application",
             "bert-base, roberta-base",
             "GPL requires sharing source code of entire application"),
            
            # Commercial models with API access
            ("gpt-4", "LLM", "Proprietary", "Proprietary", "Conditional - Requires compliance",
             True, False, False, False, "OpenAI Terms of Service apply",
             "claude-2, mistral-large",
             "API use only, subject to OpenAI's terms"),
            
            ("claude-2", "LLM", "Proprietary", "Proprietary", "Conditional - Requires compliance",
             True, False, False, False, "Anthropic Terms of Service apply",
             "gpt-4, mistral-large",
             "API use only, subject to Anthropic's terms"),
            
            # Gemma models
            ("gemma-7b", "LLM", "Gemma", "Mixed", "Restricted - Check specific terms",
             True, True, False, True, "Google's Gemma license has specific terms",
             "mistral-7b, llama-2-7b",
             "Gemma license allows commercial use with attribution"),
            
            # Vision models
            ("clip", "Vision-Language", "MIT", "LAION-400M", "Yes - Safe for commercial use",
             True, False, False, True, None, None,
             "OpenAI CLIP is MIT licensed, very permissive"),
            
            ("yolo-v8", "Vision", "AGPL-3.0", "COCO", "Yes, but with copyleft obligations",
             False, True, True, True, "AGPL requires source disclosure for network use",
             "yolo-v5, detectron2",
             "AGPL is viral for SaaS - must share source code"),
            
            # Audio models
            ("whisper", "Audio", "MIT", "Mixed", "Yes - Safe for commercial use",
             True, False, False, True, None, None,
             "OpenAI Whisper is MIT licensed"),
            
            ("musicgen", "Audio", "CC-BY-NC-4.0", "Mixed", "No - Non-commercial only",
             False, True, False, True, "Non-commercial Creative Commons license",
             "audiocraft, musiclm",
             "Meta's MusicGen is non-commercial only"),
        ]
        
        for model in models:
            cursor.execute('''
                INSERT OR REPLACE INTO model_licenses 
                (model_name, model_type, base_license, dataset_license, commercial_use,
                 saas_compatible, attribution_required, share_alike, modifications_allowed,
                 special_restrictions, alternatives, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', model)
            
    def _populate_license_details(self, cursor):
        """Populate license details"""
        licenses = [
            ("MIT", "MIT License", "Yes - Safe for commercial use", False, False, False,
             "Include copyright notice", "Everything", "Nothing"),
            
            ("Apache-2.0", "Apache License 2.0", "Yes - Safe for commercial use", False, True, False,
             "Include license, state changes", "Commercial products, SaaS", "Nothing"),
            
            ("GPL-3.0", "GNU General Public License v3", "Yes, but with copyleft obligations", 
             True, True, False, "Share source code, preserve license", 
             "Open source projects", "Proprietary software, SaaS without source disclosure"),
            
            ("AGPL-3.0", "GNU Affero General Public License v3", "Yes, but with copyleft obligations",
             True, True, True, "Share source code even for network use",
             "Open source SaaS", "Any proprietary software or closed-source SaaS"),
            
            ("CC-BY-4.0", "Creative Commons Attribution 4.0", "Yes - Safe for commercial use",
             False, False, False, "Provide attribution", "Content, datasets", "Nothing"),
            
            ("CC-BY-NC-4.0", "Creative Commons Attribution-NonCommercial 4.0", 
             "No - Non-commercial only", False, False, False,
             "Attribution + non-commercial only", "Research, education", "Any commercial use"),
            
            ("CC-BY-SA-4.0", "Creative Commons Attribution-ShareAlike 4.0",
             "Yes - Safe for commercial use", True, False, False,
             "Attribution + share derivatives under same license", 
             "Content that will be modified", "Proprietary derivatives"),
            
            ("CC0-1.0", "Creative Commons Zero", "Yes - Safe for commercial use",
             False, False, False, "None - public domain", "Everything", "Nothing"),
            
            ("OpenRAIL-M", "Open RAIL-M License", "Restricted - Check specific terms",
             False, True, False, "Use-based restrictions, display license",
             "Research, controlled commercial use", "Applications that might cause harm"),
            
            ("Llama-2", "Llama 2 Community License", "Conditional - Requires compliance",
             False, False, False, "Accept license, <700M MAU for commercial",
             "Most commercial applications", "Large-scale consumer applications"),
            
            ("Gemma", "Google Gemma Terms", "Restricted - Check specific terms",
             False, True, False, "Attribution, follow Gemma terms",
             "Applications with attribution", "Use without attribution"),
        ]
        
        for license_info in licenses:
            cursor.execute('''
                INSERT OR REPLACE INTO license_details
                (license_name, full_name, commercial_use, copyleft, patent_grant,
                 saas_loophole, key_obligations, common_uses, avoid_if)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', license_info)
            
    def _populate_compatibility_matrix(self, cursor):
        """Populate license compatibility information"""
        compatibilities = [
            # MIT is compatible with everything
            ("MIT", "Apache-2.0", True, "MIT is permissive, can be combined with Apache"),
            ("MIT", "GPL-3.0", True, "MIT code can be included in GPL projects"),
            ("MIT", "AGPL-3.0", True, "MIT code can be included in AGPL projects"),
            
            # Apache-2.0 compatibility
            ("Apache-2.0", "MIT", True, "Both are permissive licenses"),
            ("Apache-2.0", "GPL-3.0", True, "Apache 2.0 is GPL-3.0 compatible"),
            ("Apache-2.0", "GPL-2.0", False, "Apache 2.0 is NOT compatible with GPL-2.0"),
            
            # GPL compatibility
            ("GPL-3.0", "AGPL-3.0", True, "GPL-3.0 and AGPL-3.0 are compatible"),
            ("GPL-3.0", "Apache-2.0", True, "Can include Apache code in GPL project"),
            ("GPL-3.0", "MIT", True, "Can include MIT code in GPL project"),
            
            # Creative Commons
            ("CC-BY-4.0", "MIT", True, "Different domains - content vs code"),
            ("CC-BY-NC-4.0", "Commercial", False, "Non-commercial restriction"),
            ("CC-BY-SA-4.0", "Proprietary", False, "ShareAlike prevents proprietary use"),
            
            # Special licenses
            ("OpenRAIL-M", "Commercial", True, "With use restrictions"),
            ("Llama-2", "Commercial", True, "If under 700M MAU"),
        ]
        
        for compat in compatibilities:
            cursor.execute('''
                INSERT OR REPLACE INTO license_compatibility
                (license_a, license_b, compatible, compatibility_notes)
                VALUES (?, ?, ?, ?)
            ''', compat)
            # Add reverse compatibility
            cursor.execute('''
                INSERT OR REPLACE INTO license_compatibility
                (license_a, license_b, compatible, compatibility_notes)
                VALUES (?, ?, ?, ?)
            ''', (compat[1], compat[0], compat[2], compat[3]))
            
    def check_model_license(self, model_name: str) -> Optional[Dict]:
        """Check licensing information for a specific model"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Normalize model name
        model_search = model_name.lower().replace('_', '-')
        
        # Try exact match first
        c.execute('''
            SELECT * FROM model_licenses WHERE LOWER(model_name) = ?
        ''', (model_search,))
        
        result = c.fetchone()
        
        # Try partial match if no exact match
        if not result:
            c.execute('''
                SELECT * FROM model_licenses WHERE LOWER(model_name) LIKE ?
            ''', (f'%{model_search}%',))
            result = c.fetchone()
            
        conn.close()
        
        if not result:
            return None
            
        return {
            'model_name': result[1],
            'model_type': result[2],
            'base_license': result[3],
            'dataset_license': result[4],
            'commercial_use': result[5],
            'saas_compatible': bool(result[6]),
            'attribution_required': bool(result[7]),
            'share_alike': bool(result[8]),
            'modifications_allowed': bool(result[9]),
            'special_restrictions': result[10],
            'alternatives': result[11],
            'notes': result[12]
        }
        
    def check_license_compatibility(self, license_a: str, license_b: str) -> Dict:
        """Check if two licenses are compatible"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT compatible, compatibility_notes 
            FROM license_compatibility 
            WHERE license_a = ? AND license_b = ?
        ''', (license_a, license_b))
        
        result = c.fetchone()
        conn.close()
        
        if result:
            return {
                'compatible': bool(result[0]),
                'notes': result[1]
            }
        else:
            return {
                'compatible': None,
                'notes': 'No compatibility information available'
            }
            
    def get_license_details(self, license_name: str) -> Optional[Dict]:
        """Get detailed information about a license"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT * FROM license_details WHERE license_name = ?
        ''', (license_name,))
        
        result = c.fetchone()
        conn.close()
        
        if not result:
            return None
            
        return {
            'license_name': result[1],
            'full_name': result[2],
            'commercial_use': result[3],
            'copyleft': bool(result[4]),
            'patent_grant': bool(result[5]),
            'saas_loophole': bool(result[6]),
            'key_obligations': result[7],
            'common_uses': result[8],
            'avoid_if': result[9]
        }
        
    def recommend_models_for_use_case(self, use_case: str) -> List[Dict]:
        """Recommend models based on use case"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if "commercial" in use_case.lower() or "business" in use_case.lower():
            # Commercial use - avoid restricted licenses
            c.execute('''
                SELECT model_name, model_type, base_license, commercial_use, notes
                FROM model_licenses
                WHERE commercial_use LIKE '%Yes%' 
                AND saas_compatible = 1
                ORDER BY model_name
            ''')
        elif "saas" in use_case.lower() or "api" in use_case.lower():
            # SaaS use - avoid AGPL
            c.execute('''
                SELECT model_name, model_type, base_license, commercial_use, notes
                FROM model_licenses
                WHERE saas_compatible = 1
                AND base_license NOT LIKE '%AGPL%'
                ORDER BY model_name
            ''')
        elif "research" in use_case.lower() or "academic" in use_case.lower():
            # Research use - all models okay
            c.execute('''
                SELECT model_name, model_type, base_license, commercial_use, notes
                FROM model_licenses
                ORDER BY model_name
            ''')
        else:
            # General use - prefer permissive
            c.execute('''
                SELECT model_name, model_type, base_license, commercial_use, notes
                FROM model_licenses
                WHERE base_license IN ('MIT', 'Apache-2.0', 'BSD-3-Clause')
                ORDER BY model_name
            ''')
            
        results = c.fetchall()
        conn.close()
        
        return [{
            'model_name': r[0],
            'model_type': r[1],
            'license': r[2],
            'commercial_use': r[3],
            'notes': r[4]
        } for r in results]
        
    def format_license_advice(self, model_info: Dict) -> str:
        """Format licensing advice in user-friendly language"""
        advice = f"🤖 **{model_info['model_name']}** License Analysis\n\n"
        
        # License type
        advice += f"📜 **License**: {model_info['base_license']}\n"
        if model_info['dataset_license']:
            advice += f"📊 **Dataset License**: {model_info['dataset_license']}\n"
        
        # Commercial use
        commercial_emoji = "✅" if "Yes" in model_info['commercial_use'] else "❌"
        advice += f"\n{commercial_emoji} **Commercial Use**: {model_info['commercial_use']}\n"
        
        # Key requirements
        advice += "\n📋 **Key Requirements**:\n"
        if model_info['attribution_required']:
            advice += "- ⚠️ Attribution required (must credit the model)\n"
        if model_info['share_alike']:
            advice += "- 🔄 Share-alike (derivatives must use same license)\n"
        if not model_info['modifications_allowed']:
            advice += "- 🚫 Modifications not allowed\n"
        if not model_info['saas_compatible']:
            advice += "- ☁️ Not suitable for SaaS (source code disclosure required)\n"
            
        # Special restrictions
        if model_info['special_restrictions']:
            advice += f"\n⚠️ **Special Restrictions**:\n{model_info['special_restrictions']}\n"
            
        # Alternatives
        if model_info['alternatives']:
            advice += f"\n🔄 **Alternative Models**:\n"
            for alt in model_info['alternatives'].split(','):
                advice += f"- {alt.strip()}\n"
                
        # Notes
        if model_info['notes']:
            advice += f"\n💡 **Notes**: {model_info['notes']}\n"
            
        # Bottom line advice
        advice += "\n📌 **Bottom Line**:\n"
        if "Yes - Safe" in model_info['commercial_use']:
            advice += "✅ This model is safe for commercial use with minimal restrictions.\n"
        elif "Conditional" in model_info['commercial_use']:
            advice += "⚠️ Commercial use is allowed but check the specific terms carefully.\n"
        elif "copyleft" in model_info['commercial_use'].lower():
            advice += "⚠️ Commercial use allowed but you must open-source your entire application.\n"
        else:
            advice += "❌ This model is not suitable for commercial use.\n"
            
        return advice
        
    def check_use_case_compatibility(self, model_name: str, use_case: str) -> Dict:
        """Check if a model is suitable for a specific use case"""
        model_info = self.check_model_license(model_name)
        
        if not model_info:
            return {
                'suitable': None,
                'reason': f"No licensing information found for '{model_name}'",
                'advice': "Please check the model documentation for license details."
            }
            
        suitable = True
        reasons = []
        advice = []
        
        # Check commercial use
        if any(term in use_case.lower() for term in ['commercial', 'business', 'startup', 'company']):
            if "No" in model_info['commercial_use']:
                suitable = False
                reasons.append("Model license prohibits commercial use")
                advice.append("Consider Apache-2.0 or MIT licensed models instead")
            elif "Conditional" in model_info['commercial_use']:
                reasons.append("Commercial use has conditions - review carefully")
                advice.append(f"Check specific terms: {model_info['special_restrictions']}")
                
        # Check SaaS compatibility
        if any(term in use_case.lower() for term in ['saas', 'api', 'service', 'cloud']):
            if not model_info['saas_compatible']:
                suitable = False
                reasons.append("License requires source code disclosure for network use")
                advice.append("Avoid AGPL-licensed models for SaaS applications")
                
        # Check proprietary use
        if any(term in use_case.lower() for term in ['proprietary', 'closed', 'private']):
            if model_info['share_alike'] or 'GPL' in model_info['base_license']:
                suitable = False
                reasons.append("License requires sharing modifications under same terms")
                advice.append("Use MIT or Apache-2.0 licensed models for proprietary software")
                
        return {
            'suitable': suitable,
            'reasons': reasons,
            'advice': advice,
            'model_info': model_info
        }


def main():
    """Test the AI Licensing Advisor"""
    advisor = AILicensingAdvisor()
    
    # Test model lookups
    test_models = ["llama-2-7b", "mistral-7b", "stable-diffusion-xl", "yolo-v8", "gpt2"]
    
    print("🤖 AI Licensing Advisor Test\n")
    print("=" * 60)
    
    for model in test_models:
        print(f"\n📊 Checking: {model}")
        info = advisor.check_model_license(model)
        if info:
            print(advisor.format_license_advice(info))
        else:
            print(f"❌ No information found for {model}")
        print("-" * 60)
        
    # Test use case compatibility
    print("\n\n🎯 Use Case Compatibility Tests")
    print("=" * 60)
    
    test_cases = [
        ("llama-2-7b", "commercial SaaS application"),
        ("yolo-v8", "proprietary security system"),
        ("mistral-7b", "startup AI product"),
        ("stable-diffusion-xl", "commercial art generation service")
    ]
    
    for model, use_case in test_cases:
        print(f"\n🔍 Model: {model}")
        print(f"📋 Use Case: {use_case}")
        
        result = advisor.check_use_case_compatibility(model, use_case)
        
        if result['suitable'] is None:
            print(f"❓ {result['reason']}")
        elif result['suitable']:
            print("✅ Suitable for this use case")
        else:
            print("❌ NOT suitable for this use case")
            
        if result.get('reasons'):
            print("\nReasons:")
            for reason in result['reasons']:
                print(f"  - {reason}")
                
        if result.get('advice'):
            print("\nAdvice:")
            for advice in result['advice']:
                print(f"  💡 {advice}")
                
        print("-" * 60)


if __name__ == "__main__":
    main()