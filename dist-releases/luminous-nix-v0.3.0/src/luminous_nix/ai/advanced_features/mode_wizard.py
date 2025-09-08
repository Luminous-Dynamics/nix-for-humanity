#!/usr/bin/env python3
"""
System Mode Wizard - Interactive guide to find and customize perfect modes
Helps users discover optimal modes based on their workflow
"""

import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, time
from enum import Enum

from .system_modes import SystemMode, ModeProfile, SystemModeManager
from .extended_modes import ExtendedModeManager


class WizardQuestion(Enum):
    """Types of questions in the wizard"""
    WORK_TYPE = "work_type"
    SCHEDULE = "schedule"
    PRIORITIES = "priorities"
    HARDWARE = "hardware"
    PREFERENCES = "preferences"
    AUTOMATION = "automation"


@dataclass
class UserProfile:
    """User profile built from wizard answers"""
    work_type: str  # developer, creative, student, etc.
    schedule: Dict[str, str]  # time -> mode mappings
    priorities: List[str]  # performance, battery, quiet, etc.
    hardware: Dict[str, bool]  # gpu, external_monitor, etc.
    preferences: Dict[str, Any]  # notifications, effects, etc.
    automation_level: str  # manual, guided, automatic


@dataclass
class ModeRecommendation:
    """Recommended mode configuration"""
    primary_mode: str
    alternative_modes: List[str]
    schedule: Dict[str, str]
    customizations: Dict[str, Any]
    confidence: float
    reasoning: str


class SystemModeWizard:
    """
    Interactive wizard to help users find their perfect system modes
    Asks questions and builds personalized mode profiles
    """
    
    def __init__(self):
        self.manager = ExtendedModeManager()
        self.questions = self._initialize_questions()
        self.user_profile = None
        
    def _initialize_questions(self) -> Dict[WizardQuestion, Dict]:
        """Initialize wizard questions"""
        return {
            WizardQuestion.WORK_TYPE: {
                'question': "What best describes your primary computer use?",
                'options': [
                    ('developer', '💻 Software Development'),
                    ('creative', '🎨 Creative Work (Design/Video/Music)'),
                    ('gamer', '🎮 Gaming & Entertainment'),
                    ('student', '📚 Studying & Research'),
                    ('professional', '💼 Office & Business'),
                    ('server', '🖥️ Server/Hosting'),
                    ('mixed', '🔄 Mixed Use')
                ],
                'multiple': False
            },
            
            WizardQuestion.SCHEDULE: {
                'question': "When do you typically use your computer for different tasks?",
                'options': [
                    ('morning_work', '🌅 Morning (6am-12pm): Work/Study'),
                    ('afternoon_focus', '☀️ Afternoon (12pm-6pm): Deep Focus'),
                    ('evening_relax', '🌆 Evening (6pm-10pm): Relaxation'),
                    ('night_creative', '🌙 Night (10pm-2am): Creative/Gaming'),
                    ('24_7', '🔄 24/7: Always On'),
                    ('flexible', '📅 Flexible: No Fixed Schedule')
                ],
                'multiple': True
            },
            
            WizardQuestion.PRIORITIES: {
                'question': "What are your top priorities? (Select up to 3)",
                'options': [
                    ('performance', '🚀 Maximum Performance'),
                    ('battery', '🔋 Battery Life'),
                    ('quiet', '🔇 Quiet Operation'),
                    ('privacy', '🔒 Privacy & Security'),
                    ('stability', '⚖️ System Stability'),
                    ('responsiveness', '⚡ Fast Response Times')
                ],
                'multiple': True,
                'max_selections': 3
            },
            
            WizardQuestion.HARDWARE: {
                'question': "What hardware do you have?",
                'options': [
                    ('laptop', '💻 Laptop'),
                    ('desktop', '🖥️ Desktop'),
                    ('gpu', '🎮 Dedicated GPU'),
                    ('multi_monitor', '🖥️🖥️ Multiple Monitors'),
                    ('external_devices', '🔌 External Devices (Tablets, etc)'),
                    ('limited_ram', '💾 Limited RAM (<8GB)')
                ],
                'multiple': True
            },
            
            WizardQuestion.PREFERENCES: {
                'question': "What are your preferences?",
                'options': [
                    ('no_distractions', '🚫 No Distractions'),
                    ('visual_effects', '✨ Visual Effects'),
                    ('notifications', '🔔 Smart Notifications'),
                    ('auto_organize', '📁 Auto-organize Windows'),
                    ('quick_switch', '⚡ Quick Mode Switching'),
                    ('minimal', '📦 Minimal Interface')
                ],
                'multiple': True
            },
            
            WizardQuestion.AUTOMATION: {
                'question': "How much automation do you want?",
                'options': [
                    ('manual', '🎯 Manual: I control everything'),
                    ('guided', '🧭 Guided: Suggest but ask first'),
                    ('smart', '🤖 Smart: Auto-switch with confirmation'),
                    ('automatic', '🔮 Automatic: Full AI control')
                ],
                'multiple': False
            }
        }
    
    def run_wizard(self, answers: Optional[Dict[WizardQuestion, Any]] = None) -> ModeRecommendation:
        """
        Run the wizard with provided answers or interactively
        
        Args:
            answers: Pre-provided answers for non-interactive mode
        
        Returns:
            ModeRecommendation with personalized configuration
        """
        if answers:
            self.user_profile = self._build_profile(answers)
        else:
            # Would be interactive in a real CLI
            self.user_profile = self._build_default_profile()
        
        return self._generate_recommendation()
    
    def _build_profile(self, answers: Dict[WizardQuestion, Any]) -> UserProfile:
        """Build user profile from wizard answers"""
        return UserProfile(
            work_type=answers.get(WizardQuestion.WORK_TYPE, 'mixed'),
            schedule=self._build_schedule(answers.get(WizardQuestion.SCHEDULE, [])),
            priorities=answers.get(WizardQuestion.PRIORITIES, ['performance']),
            hardware=self._build_hardware(answers.get(WizardQuestion.HARDWARE, [])),
            preferences=self._build_preferences(answers.get(WizardQuestion.PREFERENCES, [])),
            automation_level=answers.get(WizardQuestion.AUTOMATION, 'guided')
        )
    
    def _build_default_profile(self) -> UserProfile:
        """Build a sensible default profile"""
        return UserProfile(
            work_type='mixed',
            schedule={
                '09:00': 'work',
                '18:00': 'personal',
                '22:00': 'quiet'
            },
            priorities=['performance', 'stability'],
            hardware={'laptop': True, 'gpu': False},
            preferences={'no_distractions': True, 'quick_switch': True},
            automation_level='guided'
        )
    
    def _build_schedule(self, schedule_answers: List[str]) -> Dict[str, str]:
        """Build schedule from answers"""
        schedule = {}
        
        for answer in schedule_answers:
            if answer == 'morning_work':
                schedule['06:00'] = 'work'
                schedule['09:00'] = 'developer'
            elif answer == 'afternoon_focus':
                schedule['12:00'] = 'focus'
                schedule['14:00'] = 'work'
            elif answer == 'evening_relax':
                schedule['18:00'] = 'personal'
                schedule['20:00'] = 'gaming'
            elif answer == 'night_creative':
                schedule['22:00'] = 'creative'
                schedule['00:00'] = 'quiet'
        
        return schedule
    
    def _build_hardware(self, hardware_answers: List[str]) -> Dict[str, bool]:
        """Build hardware profile from answers"""
        return {
            'laptop': 'laptop' in hardware_answers,
            'desktop': 'desktop' in hardware_answers,
            'gpu': 'gpu' in hardware_answers,
            'multi_monitor': 'multi_monitor' in hardware_answers,
            'external_devices': 'external_devices' in hardware_answers,
            'limited_ram': 'limited_ram' in hardware_answers
        }
    
    def _build_preferences(self, pref_answers: List[str]) -> Dict[str, Any]:
        """Build preferences from answers"""
        return {
            'no_distractions': 'no_distractions' in pref_answers,
            'visual_effects': 'visual_effects' in pref_answers,
            'notifications': 'notifications' in pref_answers,
            'auto_organize': 'auto_organize' in pref_answers,
            'quick_switch': 'quick_switch' in pref_answers,
            'minimal': 'minimal' in pref_answers
        }
    
    def _generate_recommendation(self) -> ModeRecommendation:
        """Generate mode recommendations based on user profile"""
        profile = self.user_profile
        
        # Determine primary mode
        primary_mode = self._get_primary_mode(profile)
        
        # Get alternative modes
        alternatives = self._get_alternative_modes(profile, primary_mode)
        
        # Generate customizations
        customizations = self._generate_customizations(profile)
        
        # Build schedule
        schedule = self._optimize_schedule(profile)
        
        # Calculate confidence
        confidence = self._calculate_confidence(profile, primary_mode)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(profile, primary_mode)
        
        return ModeRecommendation(
            primary_mode=primary_mode,
            alternative_modes=alternatives,
            schedule=schedule,
            customizations=customizations,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def _get_primary_mode(self, profile: UserProfile) -> str:
        """Determine primary mode based on profile"""
        mode_map = {
            'developer': 'developer',
            'creative': 'creative',
            'gamer': 'gaming',
            'student': 'learning',
            'professional': 'work',
            'server': 'server',
            'mixed': 'work'
        }
        
        base_mode = mode_map.get(profile.work_type, 'work')
        
        # Adjust based on priorities
        if 'battery' in profile.priorities and profile.hardware.get('laptop'):
            if base_mode == 'gaming':
                base_mode = 'battery_saver'
        
        if 'privacy' in profile.priorities:
            base_mode = 'privacy'
        
        if 'quiet' in profile.priorities:
            if base_mode in ['gaming', 'performance']:
                base_mode = 'quiet'
        
        return base_mode
    
    def _get_alternative_modes(self, profile: UserProfile, primary: str) -> List[str]:
        """Get alternative mode suggestions"""
        alternatives = []
        
        # Based on work type
        if profile.work_type == 'developer':
            alternatives.extend(['compilation', 'focus', 'learning'])
        elif profile.work_type == 'creative':
            alternatives.extend(['recording', 'presentation', 'focus'])
        elif profile.work_type == 'mixed':
            alternatives.extend(['work', 'gaming', 'creative'])
        
        # Based on priorities
        if 'battery' in profile.priorities:
            alternatives.append('battery_saver')
        if 'privacy' in profile.priorities:
            alternatives.append('privacy')
        if 'performance' in profile.priorities:
            alternatives.append('performance')
        
        # Remove primary and duplicates
        alternatives = list(set(alternatives) - {primary})
        
        return alternatives[:5]  # Top 5 alternatives
    
    def _generate_customizations(self, profile: UserProfile) -> Dict[str, Any]:
        """Generate custom settings based on profile"""
        custom = {}
        
        # Hardware customizations
        if profile.hardware.get('gpu'):
            custom['gpu_profile'] = 'performance'
        else:
            custom['gpu_profile'] = 'integrated'
        
        if profile.hardware.get('limited_ram'):
            custom['memory_swappiness'] = 100
            custom['disable_services'] = ['heavy_services']
        
        # Preference customizations
        if profile.preferences.get('no_distractions'):
            custom['notification_sounds'] = False
            custom['compositor_effects'] = False
        
        if profile.preferences.get('visual_effects'):
            custom['compositor_effects'] = True
            custom['animations'] = True
        
        if profile.preferences.get('minimal'):
            custom['ui_mode'] = 'minimal'
            custom['auto_hide'] = True
        
        # Priority customizations
        if 'battery' in profile.priorities:
            custom['cpu_governor'] = 'powersave'
            custom['display_brightness'] = 60
        
        if 'performance' in profile.priorities:
            custom['cpu_governor'] = 'performance'
            custom['cache_aggressive'] = True
        
        if 'quiet' in profile.priorities:
            custom['fan_mode'] = 'quiet'
            custom['cpu_governor'] = 'powersave'
        
        return custom
    
    def _optimize_schedule(self, profile: UserProfile) -> Dict[str, str]:
        """Optimize mode schedule based on profile"""
        schedule = profile.schedule.copy()
        
        # Add smart transitions
        if profile.automation_level in ['smart', 'automatic']:
            # Add transition modes
            if '09:00' in schedule and schedule['09:00'] == 'work':
                schedule['08:45'] = 'morning_prep'  # Gentle wake-up
            
            if '22:00' in schedule:
                schedule['21:45'] = 'wind_down'  # Prepare for rest
        
        return schedule
    
    def _calculate_confidence(self, profile: UserProfile, mode: str) -> float:
        """Calculate confidence in recommendation"""
        confidence = 0.5  # Base confidence
        
        # Work type match
        if profile.work_type in mode:
            confidence += 0.2
        
        # Priority alignment
        mode_priorities = {
            'gaming': ['performance'],
            'battery_saver': ['battery'],
            'privacy': ['privacy'],
            'quiet': ['quiet']
        }
        
        if mode in mode_priorities:
            for priority in mode_priorities[mode]:
                if priority in profile.priorities:
                    confidence += 0.1
        
        # Hardware compatibility
        if profile.hardware.get('gpu') and mode in ['gaming', 'creative']:
            confidence += 0.1
        
        if profile.hardware.get('laptop') and mode == 'battery_saver':
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _generate_reasoning(self, profile: UserProfile, mode: str) -> str:
        """Generate human-readable reasoning for recommendation"""
        reasons = []
        
        # Work type reasoning
        if profile.work_type == 'developer':
            reasons.append("As a developer, you need quick compilation and testing")
        elif profile.work_type == 'creative':
            reasons.append("Creative work requires GPU acceleration and color accuracy")
        elif profile.work_type == 'student':
            reasons.append("Students benefit from distraction-free focus modes")
        
        # Priority reasoning
        if 'battery' in profile.priorities:
            reasons.append("Battery life is prioritized with power-saving features")
        if 'performance' in profile.priorities:
            reasons.append("Maximum performance for demanding tasks")
        if 'privacy' in profile.priorities:
            reasons.append("Enhanced privacy with VPN and encrypted connections")
        
        # Hardware reasoning
        if profile.hardware.get('limited_ram'):
            reasons.append("Optimized for limited RAM with aggressive swapping")
        if profile.hardware.get('gpu'):
            reasons.append("GPU acceleration enabled for better performance")
        
        return ". ".join(reasons)
    
    def export_configuration(self, recommendation: ModeRecommendation) -> str:
        """Export recommendation as NixOS configuration snippet"""
        config = []
        config.append("# Luminous Nix Mode Configuration")
        config.append("# Generated by System Mode Wizard")
        config.append("")
        config.append("programs.luminous-nix = {")
        config.append("  enable = true;")
        config.append(f'  defaultMode = "{recommendation.primary_mode}";')
        config.append("  ")
        config.append("  modes = {")
        
        # Add primary mode config
        config.append(f'    {recommendation.primary_mode} = {{')
        for key, value in recommendation.customizations.items():
            if isinstance(value, str):
                config.append(f'      {key} = "{value}";')
            elif isinstance(value, bool):
                config.append(f'      {key} = {str(value).lower()};')
            else:
                config.append(f'      {key} = {value};')
        config.append("    };")
        config.append("  };")
        config.append("  ")
        
        # Add schedule
        config.append("  schedule = {")
        for time, mode in recommendation.schedule.items():
            config.append(f'    "{time}" = "{mode}";')
        config.append("  };")
        config.append("  ")
        
        # Add automation
        config.append(f'  automation = "{self.user_profile.automation_level}";')
        config.append("};")
        
        return '\n'.join(config)