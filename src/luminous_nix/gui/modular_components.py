#!/usr/bin/env python3
"""
🎨 Modular GUI Components for Luminous Nix
Reusable components that can be composed for different interfaces
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

# For web integration with existing nixos-gui
import asyncio
import aiohttp
from aiohttp import web


class ComponentType(Enum):
    """Types of reusable components"""
    PROFILE_CARD = "profile_card"
    PACKAGE_SELECTOR = "package_selector"
    CONFLICT_RESOLVER = "conflict_resolver"
    PROGRESS_INDICATOR = "progress_indicator"
    NATURAL_LANGUAGE_INPUT = "natural_language_input"
    ESTIMATION_PANEL = "estimation_panel"
    ROLLBACK_TIMELINE = "rollback_timeline"
    SYSTEM_PREVIEW = "system_preview"


@dataclass
class ComponentSpec:
    """Specification for a modular component"""
    type: ComponentType
    props: Dict[str, Any]
    events: Dict[str, Callable]
    children: List['ComponentSpec'] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'type': self.type.value,
            'props': self.props,
            'children': [c.to_dict() for c in self.children] if self.children else []
        }


class ModularComponentFactory:
    """
    Factory for creating reusable GUI components
    These can be rendered in different contexts (TUI, Web, CLI)
    """
    
    @staticmethod
    def create_profile_card(profile_data: Dict[str, Any], 
                           selected: bool = False) -> ComponentSpec:
        """Create a profile selection card"""
        return ComponentSpec(
            type=ComponentType.PROFILE_CARD,
            props={
                'emoji': profile_data.get('emoji', '📦'),
                'name': profile_data.get('name', 'Unknown'),
                'description': profile_data.get('description', ''),
                'package_count': len(profile_data.get('packages', [])),
                'optimizations': profile_data.get('optimizations', []),
                'selected': selected,
                'style': {
                    'border': 'primary' if selected else 'default',
                    'highlight': selected
                }
            },
            events={
                'onClick': lambda: None,  # Will be overridden by consumer
                'onHover': lambda: None
            }
        )
    
    @staticmethod
    def create_package_selector(packages: List[Dict], 
                               category: str,
                               multi_select: bool = True) -> ComponentSpec:
        """Create a package selection component"""
        return ComponentSpec(
            type=ComponentType.PACKAGE_SELECTOR,
            props={
                'category': category,
                'packages': packages,
                'multi_select': multi_select,
                'show_descriptions': True,
                'show_size': True,
                'grouping': 'category',  # or 'alphabetical', 'popularity'
                'search_enabled': True
            },
            events={
                'onSelect': lambda pkg: None,
                'onDeselect': lambda pkg: None,
                'onSearch': lambda query: None
            }
        )
    
    @staticmethod
    def create_conflict_resolver(conflicts: List[Dict]) -> ComponentSpec:
        """Create a conflict resolution component"""
        return ComponentSpec(
            type=ComponentType.CONFLICT_RESOLVER,
            props={
                'conflicts': conflicts,
                'show_explanations': True,
                'auto_resolve_enabled': True,
                'style': {
                    'severity': 'warning',
                    'modal': True
                }
            },
            events={
                'onResolve': lambda resolution: None,
                'onCancel': lambda: None
            }
        )
    
    @staticmethod
    def create_progress_indicator(total: int, current: int = 0,
                                 message: str = "") -> ComponentSpec:
        """Create a progress indicator"""
        return ComponentSpec(
            type=ComponentType.PROGRESS_INDICATOR,
            props={
                'total': total,
                'current': current,
                'message': message,
                'show_percentage': True,
                'show_eta': True,
                'style': {
                    'color': 'primary',
                    'animated': True
                }
            },
            events={
                'onComplete': lambda: None
            }
        )
    
    @staticmethod
    def create_natural_language_input(placeholder: str = "Describe what you need...",
                                     suggestions: List[str] = None) -> ComponentSpec:
        """Create natural language input component"""
        return ComponentSpec(
            type=ComponentType.NATURAL_LANGUAGE_INPUT,
            props={
                'placeholder': placeholder,
                'suggestions': suggestions or [],
                'show_examples': True,
                'voice_enabled': True,
                'ai_assist': True
            },
            events={
                'onSubmit': lambda text: None,
                'onVoiceInput': lambda: None,
                'onSuggestionSelect': lambda suggestion: None
            }
        )
    
    @staticmethod
    def create_estimation_panel(packages: List[str]) -> ComponentSpec:
        """Create installation estimation panel"""
        return ComponentSpec(
            type=ComponentType.ESTIMATION_PANEL,
            props={
                'package_count': len(packages),
                'estimated_size': len(packages) * 50,  # MB
                'estimated_time': len(packages) * 0.5,  # minutes
                'show_breakdown': True,
                'show_mirror_info': True
            },
            events={
                'onRefresh': lambda: None
            }
        )
    
    @staticmethod
    def create_rollback_timeline(generations: List[Dict]) -> ComponentSpec:
        """Create rollback timeline component"""
        return ComponentSpec(
            type=ComponentType.ROLLBACK_TIMELINE,
            props={
                'generations': generations,
                'show_diff': True,
                'visual_style': 'timeline',  # or 'list', 'cards'
                'preview_enabled': True
            },
            events={
                'onSelect': lambda gen: None,
                'onPreview': lambda gen: None,
                'onRollback': lambda gen: None
            }
        )
    
    @staticmethod
    def create_system_preview(config: Dict) -> ComponentSpec:
        """Create system configuration preview"""
        return ComponentSpec(
            type=ComponentType.SYSTEM_PREVIEW,
            props={
                'config': config,
                'show_desktop': True,
                'show_packages': True,
                'show_services': True,
                'interactive': True
            },
            events={
                'onEdit': lambda section: None,
                'onTest': lambda: None
            }
        )


class ComponentRenderer:
    """
    Base class for rendering components in different contexts
    """
    
    def render(self, component: ComponentSpec) -> Any:
        """Render a component - to be overridden by subclasses"""
        raise NotImplementedError


class WebComponentRenderer(ComponentRenderer):
    """
    Renders components as HTML/JavaScript for web interfaces
    Integrates with existing nixos-gui
    """
    
    def render(self, component: ComponentSpec) -> str:
        """Render component as HTML"""
        renderers = {
            ComponentType.PROFILE_CARD: self._render_profile_card,
            ComponentType.PACKAGE_SELECTOR: self._render_package_selector,
            ComponentType.CONFLICT_RESOLVER: self._render_conflict_modal,
            ComponentType.PROGRESS_INDICATOR: self._render_progress,
            ComponentType.NATURAL_LANGUAGE_INPUT: self._render_nl_input,
            ComponentType.ESTIMATION_PANEL: self._render_estimation,
            ComponentType.ROLLBACK_TIMELINE: self._render_timeline,
            ComponentType.SYSTEM_PREVIEW: self._render_preview
        }
        
        renderer = renderers.get(component.type)
        if renderer:
            return renderer(component)
        return ""
    
    def _render_profile_card(self, component: ComponentSpec) -> str:
        """Render profile card as HTML"""
        props = component.props
        selected_class = 'selected' if props.get('selected') else ''
        
        return f"""
        <div class="profile-card {selected_class}" data-profile="{props.get('name')}">
            <div class="profile-emoji">{props.get('emoji')}</div>
            <h3 class="profile-name">{props.get('name')}</h3>
            <p class="profile-description">{props.get('description')}</p>
            <div class="profile-stats">
                <span class="package-count">📦 {props.get('package_count')} packages</span>
                <span class="optimizations">⚡ {', '.join(props.get('optimizations', []))}</span>
            </div>
        </div>
        """
    
    def _render_package_selector(self, component: ComponentSpec) -> str:
        """Render package selector as HTML"""
        props = component.props
        packages_html = []
        
        for pkg in props.get('packages', []):
            packages_html.append(f"""
                <div class="package-item">
                    <input type="checkbox" 
                           id="pkg_{pkg.get('name')}" 
                           name="packages"
                           value="{pkg.get('name')}"
                           {'checked' if pkg.get('selected') else ''}>
                    <label for="pkg_{pkg.get('name')}">
                        <span class="package-name">{pkg.get('name')}</span>
                        <span class="package-reason">{pkg.get('reason', '')}</span>
                    </label>
                </div>
            """)
        
        return f"""
        <div class="package-selector" data-category="{props.get('category')}">
            <h3>{props.get('category')}</h3>
            {'<input type="text" class="package-search" placeholder="Search packages...">' if props.get('search_enabled') else ''}
            <div class="package-list">
                {''.join(packages_html)}
            </div>
        </div>
        """
    
    def _render_conflict_modal(self, component: ComponentSpec) -> str:
        """Render conflict resolver as modal"""
        props = component.props
        conflicts_html = []
        
        for conflict in props.get('conflicts', []):
            conflicts_html.append(f"""
                <div class="conflict-item">
                    <div class="conflict-description">
                        <strong>{conflict.get('package1')} ↔ {conflict.get('package2')}</strong>
                        <p>{conflict.get('reason')}</p>
                    </div>
                    <div class="conflict-resolution">
                        <select name="resolve_{conflict.get('id')}">
                            <option value="{conflict.get('package1')}">Keep {conflict.get('package1')}</option>
                            <option value="{conflict.get('package2')}">Keep {conflict.get('package2')}</option>
                            <option value="both">Keep both (advanced)</option>
                            <option value="neither">Skip both</option>
                        </select>
                    </div>
                </div>
            """)
        
        return f"""
        <div class="modal conflict-resolver">
            <div class="modal-content">
                <h2>⚠️ Package Conflicts Detected</h2>
                <div class="conflicts-list">
                    {''.join(conflicts_html)}
                </div>
                <div class="modal-actions">
                    <button class="btn-resolve">Resolve Conflicts</button>
                    <button class="btn-cancel">Cancel</button>
                </div>
            </div>
        </div>
        """
    
    def _render_progress(self, component: ComponentSpec) -> str:
        """Render progress indicator"""
        props = component.props
        percentage = (props.get('current', 0) / props.get('total', 1)) * 100
        
        return f"""
        <div class="progress-indicator">
            <div class="progress-message">{props.get('message', '')}</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {percentage}%"></div>
            </div>
            <div class="progress-stats">
                <span class="progress-percentage">{percentage:.0f}%</span>
                {'<span class="progress-eta">ETA: calculating...</span>' if props.get('show_eta') else ''}
            </div>
        </div>
        """
    
    def _render_nl_input(self, component: ComponentSpec) -> str:
        """Render natural language input"""
        props = component.props
        
        return f"""
        <div class="natural-language-input">
            <input type="text" 
                   placeholder="{props.get('placeholder')}"
                   class="nl-input">
            {'<button class="voice-input-btn">🎤</button>' if props.get('voice_enabled') else ''}
            {self._render_suggestions(props.get('suggestions', []))}
        </div>
        """
    
    def _render_suggestions(self, suggestions: List[str]) -> str:
        """Render suggestions for natural language input"""
        if not suggestions:
            return ""
        
        items = ''.join([f'<li class="suggestion">{s}</li>' for s in suggestions])
        return f'<ul class="suggestions">{items}</ul>'
    
    def _render_estimation(self, component: ComponentSpec) -> str:
        """Render estimation panel"""
        props = component.props
        
        return f"""
        <div class="estimation-panel">
            <h3>Installation Estimate</h3>
            <div class="estimation-stats">
                <div>📦 {props.get('package_count')} packages</div>
                <div>💾 ~{props.get('estimated_size')} MB</div>
                <div>⏱️ ~{props.get('estimated_time')} minutes</div>
            </div>
            {'<button class="refresh-estimate">Refresh</button>' if props.get('show_breakdown') else ''}
        </div>
        """
    
    def _render_timeline(self, component: ComponentSpec) -> str:
        """Render rollback timeline"""
        props = component.props
        generations = props.get('generations', [])
        
        items = []
        for gen in generations:
            items.append(f"""
                <div class="timeline-item" data-generation="{gen.get('id')}">
                    <div class="timeline-marker"></div>
                    <div class="timeline-content">
                        <h4>Generation {gen.get('id')}</h4>
                        <p>{gen.get('description')}</p>
                        <small>{gen.get('date')}</small>
                    </div>
                </div>
            """)
        
        return f"""
        <div class="rollback-timeline">
            {''.join(items)}
        </div>
        """
    
    def _render_preview(self, component: ComponentSpec) -> str:
        """Render system preview"""
        props = component.props
        
        return f"""
        <div class="system-preview">
            <h3>System Configuration Preview</h3>
            <div class="preview-sections">
                {'<div class="preview-desktop">Desktop Preview</div>' if props.get('show_desktop') else ''}
                {'<div class="preview-packages">Installed Packages</div>' if props.get('show_packages') else ''}
                {'<div class="preview-services">System Services</div>' if props.get('show_services') else ''}
            </div>
        </div>
        """


class ComponentOrchestrator:
    """
    Orchestrates components for different use cases
    Makes it easy to compose interfaces from modular parts
    """
    
    def __init__(self):
        self.factory = ModularComponentFactory()
        self.web_renderer = WebComponentRenderer()
    
    def create_setup_ceremony_components(self, stage: str) -> List[ComponentSpec]:
        """Create components for setup ceremony based on stage"""
        if stage == "welcome":
            return [
                self.factory.create_profile_card(profile, False)
                for profile in self.get_available_profiles()
            ]
        elif stage == "packages":
            return [
                self.factory.create_package_selector(
                    self.get_recommended_packages(),
                    "Essential Packages"
                ),
                self.factory.create_estimation_panel([])
            ]
        elif stage == "conflicts":
            return [
                self.factory.create_conflict_resolver(
                    self.get_current_conflicts()
                )
            ]
        elif stage == "natural":
            return [
                self.factory.create_natural_language_input(
                    "Describe any additional software you need..."
                )
            ]
        elif stage == "preview":
            return [
                self.factory.create_system_preview(
                    self.get_system_config()
                ),
                self.factory.create_progress_indicator(100, 0)
            ]
        return []
    
    def create_dashboard_components(self) -> List[ComponentSpec]:
        """Create components for main dashboard"""
        return [
            self.factory.create_estimation_panel(
                self.get_installed_packages()
            ),
            self.factory.create_rollback_timeline(
                self.get_generations()
            )
        ]
    
    def create_package_manager_components(self) -> List[ComponentSpec]:
        """Create components for package management interface"""
        return [
            self.factory.create_natural_language_input(
                "Search for packages..."
            ),
            self.factory.create_package_selector(
                self.search_packages(""),
                "Available Packages"
            )
        ]
    
    def render_for_web(self, components: List[ComponentSpec]) -> str:
        """Render components for web interface"""
        html_parts = []
        for component in components:
            html_parts.append(self.web_renderer.render(component))
        
        return f"""
        <div class="component-container">
            {''.join(html_parts)}
        </div>
        """
    
    def get_available_profiles(self) -> List[Dict]:
        """Get available user profiles"""
        # This would connect to the ProfileManager
        return [
            {'name': 'Home User', 'emoji': '🏠', 'packages': [], 'optimizations': ['ease']},
            {'name': 'Developer', 'emoji': '⚡', 'packages': [], 'optimizations': ['speed']},
            {'name': 'Creative', 'emoji': '🎨', 'packages': [], 'optimizations': ['gpu']}
        ]
    
    def get_recommended_packages(self) -> List[Dict]:
        """Get recommended packages for current profile"""
        return []
    
    def get_current_conflicts(self) -> List[Dict]:
        """Get current package conflicts"""
        return []
    
    def get_system_config(self) -> Dict:
        """Get current system configuration"""
        return {}
    
    def get_installed_packages(self) -> List[str]:
        """Get list of installed packages"""
        return []
    
    def get_generations(self) -> List[Dict]:
        """Get system generations for rollback"""
        return []
    
    def search_packages(self, query: str) -> List[Dict]:
        """Search for packages"""
        return []


# Web API for integration with nixos-gui
class ComponentWebAPI:
    """
    Web API to serve components to nixos-gui JavaScript frontend
    """
    
    def __init__(self):
        self.orchestrator = ComponentOrchestrator()
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        """Setup web routes"""
        self.app.router.add_get('/api/components/{use_case}', self.get_components)
        self.app.router.add_post('/api/components/render', self.render_components)
    
    async def get_components(self, request):
        """Get components for a specific use case"""
        use_case = request.match_info['use_case']
        stage = request.rel_url.query.get('stage', 'welcome')
        
        if use_case == 'setup_ceremony':
            components = self.orchestrator.create_setup_ceremony_components(stage)
        elif use_case == 'dashboard':
            components = self.orchestrator.create_dashboard_components()
        elif use_case == 'package_manager':
            components = self.orchestrator.create_package_manager_components()
        else:
            components = []
        
        # Convert to JSON-serializable format
        components_data = [c.to_dict() for c in components]
        
        return web.json_response({
            'use_case': use_case,
            'stage': stage,
            'components': components_data
        })
    
    async def render_components(self, request):
        """Render components as HTML"""
        data = await request.json()
        components_data = data.get('components', [])
        
        # Reconstruct ComponentSpec objects
        components = []
        for comp_data in components_data:
            spec = ComponentSpec(
                type=ComponentType(comp_data['type']),
                props=comp_data['props'],
                events={}  # Events are handled client-side
            )
            components.append(spec)
        
        html = self.orchestrator.render_for_web(components)
        
        return web.json_response({
            'html': html
        })
    
    def run(self, host='localhost', port=8888):
        """Run the web API server"""
        web.run_app(self.app, host=host, port=port)


if __name__ == "__main__":
    # Example: Run the component API server
    api = ComponentWebAPI()
    api.run()