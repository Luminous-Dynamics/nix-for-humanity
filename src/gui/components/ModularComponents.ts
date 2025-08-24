/**
 * 🎨 Modular GUI Components for Luminous Nix
 * TypeScript components that can be reused across different interfaces
 * Integrates with both nixos-gui and Luminous Nix backend
 */

// Component type definitions
export enum ComponentType {
  PROFILE_CARD = 'profile_card',
  PACKAGE_SELECTOR = 'package_selector',
  CONFLICT_RESOLVER = 'conflict_resolver',
  PROGRESS_INDICATOR = 'progress_indicator',
  NATURAL_LANGUAGE_INPUT = 'natural_language_input',
  ESTIMATION_PANEL = 'estimation_panel',
  ROLLBACK_TIMELINE = 'rollback_timeline',
  SYSTEM_PREVIEW = 'system_preview'
}

// Base interfaces
export interface ComponentProps {
  id?: string;
  className?: string;
  style?: Record<string, any>;
}

export interface ComponentEvents {
  onClick?: (event: MouseEvent) => void;
  onChange?: (value: any) => void;
  onSubmit?: (data: any) => void;
}

// Profile types
export interface Profile {
  type: string;
  name: string;
  emoji: string;
  description: string;
  packages: string[];
  optionalPackages?: string[];
  optimizations: string[];
  aiPersona: string;
  settings?: Record<string, any>;
}

export interface ProfileCardProps extends ComponentProps {
  profile: Profile;
  selected?: boolean;
  onSelect?: (profile: Profile) => void;
}

// Package types
export interface Package {
  name: string;
  description?: string;
  version?: string;
  size?: number;
  category?: string;
  selected?: boolean;
  reason?: string;
  dependencies?: string[];
}

export interface PackageSelectorProps extends ComponentProps {
  packages: Package[];
  category: string;
  multiSelect?: boolean;
  showSearch?: boolean;
  showSize?: boolean;
  onPackageSelect?: (packages: Package[]) => void;
}

// Conflict types
export interface Conflict {
  id: string;
  package1: string;
  package2: string;
  reason: string;
  resolution?: string;
  autoResolve?: boolean;
}

export interface ConflictResolverProps extends ComponentProps {
  conflicts: Conflict[];
  onResolve?: (resolutions: Record<string, string>) => void;
  onCancel?: () => void;
}

// Progress types
export interface ProgressIndicatorProps extends ComponentProps {
  total: number;
  current: number;
  message?: string;
  showPercentage?: boolean;
  showETA?: boolean;
  onComplete?: () => void;
}

// Natural language types
export interface NaturalLanguageInputProps extends ComponentProps {
  placeholder?: string;
  suggestions?: string[];
  voiceEnabled?: boolean;
  aiAssist?: boolean;
  onSubmit?: (text: string) => void;
  onVoiceInput?: () => void;
}

// Estimation types
export interface EstimationPanelProps extends ComponentProps {
  packageCount: number;
  estimatedSize?: number;
  estimatedTime?: number;
  showBreakdown?: boolean;
  showMirrorInfo?: boolean;
  onRefresh?: () => void;
}

// Timeline types
export interface Generation {
  id: number;
  description: string;
  date: string;
  packages?: string[];
  changes?: string[];
}

export interface RollbackTimelineProps extends ComponentProps {
  generations: Generation[];
  currentGeneration?: number;
  showDiff?: boolean;
  onSelect?: (generation: Generation) => void;
  onRollback?: (generation: Generation) => void;
}

// System preview types
export interface SystemConfig {
  profile: string;
  packages: string[];
  services: string[];
  settings: Record<string, any>;
}

export interface SystemPreviewProps extends ComponentProps {
  config: SystemConfig;
  showDesktop?: boolean;
  showPackages?: boolean;
  showServices?: boolean;
  interactive?: boolean;
  onEdit?: (section: string) => void;
}

/**
 * Base Component class that all components extend
 */
export abstract class Component<T extends ComponentProps> {
  protected props: T;
  protected element: HTMLElement | null = null;

  constructor(props: T) {
    this.props = props;
  }

  abstract render(): HTMLElement;

  mount(container: HTMLElement): void {
    this.element = this.render();
    container.appendChild(this.element);
  }

  unmount(): void {
    if (this.element && this.element.parentNode) {
      this.element.parentNode.removeChild(this.element);
    }
  }

  update(props: Partial<T>): void {
    this.props = { ...this.props, ...props };
    if (this.element && this.element.parentNode) {
      const parent = this.element.parentNode;
      const newElement = this.render();
      parent.replaceChild(newElement, this.element);
      this.element = newElement;
    }
  }
}

/**
 * Profile Card Component
 */
export class ProfileCard extends Component<ProfileCardProps> {
  render(): HTMLElement {
    const card = document.createElement('div');
    card.className = `profile-card ${this.props.selected ? 'selected' : ''} ${this.props.className || ''}`;
    
    card.innerHTML = `
      <div class="profile-emoji">${this.props.profile.emoji}</div>
      <h3 class="profile-name">${this.props.profile.name}</h3>
      <p class="profile-description">${this.props.profile.description}</p>
      <div class="profile-stats">
        <span class="package-count">📦 ${this.props.profile.packages.length} packages</span>
        <span class="optimizations">⚡ ${this.props.profile.optimizations.join(', ')}</span>
      </div>
      <div class="profile-persona">🤖 Guided by ${this.props.profile.aiPersona}</div>
    `;

    if (this.props.onSelect) {
      card.addEventListener('click', () => {
        this.props.onSelect?.(this.props.profile);
      });
    }

    return card;
  }
}

/**
 * Package Selector Component
 */
export class PackageSelector extends Component<PackageSelectorProps> {
  private selectedPackages: Set<string> = new Set();

  render(): HTMLElement {
    const container = document.createElement('div');
    container.className = `package-selector ${this.props.className || ''}`;

    // Header with category
    const header = document.createElement('h3');
    header.textContent = this.props.category;
    container.appendChild(header);

    // Search bar if enabled
    if (this.props.showSearch) {
      const searchInput = document.createElement('input');
      searchInput.type = 'text';
      searchInput.placeholder = 'Search packages...';
      searchInput.className = 'package-search';
      searchInput.addEventListener('input', (e) => this.filterPackages((e.target as HTMLInputElement).value));
      container.appendChild(searchInput);
    }

    // Package list
    const packageList = document.createElement('div');
    packageList.className = 'package-list';

    this.props.packages.forEach(pkg => {
      const packageItem = this.createPackageItem(pkg);
      packageList.appendChild(packageItem);
    });

    container.appendChild(packageList);

    return container;
  }

  private createPackageItem(pkg: Package): HTMLElement {
    const item = document.createElement('div');
    item.className = 'package-item';
    item.dataset.packageName = pkg.name;

    const checkbox = document.createElement('input');
    checkbox.type = this.props.multiSelect ? 'checkbox' : 'radio';
    checkbox.name = 'packages';
    checkbox.value = pkg.name;
    checkbox.checked = pkg.selected || false;
    checkbox.id = `pkg_${pkg.name}`;

    checkbox.addEventListener('change', () => {
      if (checkbox.checked) {
        this.selectedPackages.add(pkg.name);
      } else {
        this.selectedPackages.delete(pkg.name);
      }
      this.notifySelection();
    });

    const label = document.createElement('label');
    label.htmlFor = `pkg_${pkg.name}`;
    label.innerHTML = `
      <span class="package-name">${pkg.name}</span>
      ${pkg.description ? `<span class="package-description">${pkg.description}</span>` : ''}
      ${pkg.reason ? `<span class="package-reason">${pkg.reason}</span>` : ''}
      ${this.props.showSize && pkg.size ? `<span class="package-size">${this.formatSize(pkg.size)}</span>` : ''}
    `;

    item.appendChild(checkbox);
    item.appendChild(label);

    return item;
  }

  private filterPackages(query: string): void {
    const items = this.element?.querySelectorAll('.package-item') as NodeListOf<HTMLElement>;
    items.forEach(item => {
      const name = item.dataset.packageName?.toLowerCase() || '';
      item.style.display = name.includes(query.toLowerCase()) ? '' : 'none';
    });
  }

  private notifySelection(): void {
    const selected = this.props.packages.filter(p => this.selectedPackages.has(p.name));
    this.props.onPackageSelect?.(selected);
  }

  private formatSize(bytes: number): string {
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    return `${size.toFixed(1)} ${units[unitIndex]}`;
  }
}

/**
 * Conflict Resolver Component
 */
export class ConflictResolver extends Component<ConflictResolverProps> {
  private resolutions: Record<string, string> = {};

  render(): HTMLElement {
    const modal = document.createElement('div');
    modal.className = `conflict-resolver-modal ${this.props.className || ''}`;

    const content = document.createElement('div');
    content.className = 'modal-content';

    // Header
    const header = document.createElement('h2');
    header.innerHTML = '⚠️ Package Conflicts Detected';
    content.appendChild(header);

    // Conflicts list
    const conflictsList = document.createElement('div');
    conflictsList.className = 'conflicts-list';

    this.props.conflicts.forEach(conflict => {
      const conflictItem = this.createConflictItem(conflict);
      conflictsList.appendChild(conflictItem);
    });

    content.appendChild(conflictsList);

    // Action buttons
    const actions = document.createElement('div');
    actions.className = 'modal-actions';

    const resolveBtn = document.createElement('button');
    resolveBtn.textContent = 'Resolve Conflicts';
    resolveBtn.className = 'btn-primary';
    resolveBtn.addEventListener('click', () => this.handleResolve());

    const cancelBtn = document.createElement('button');
    cancelBtn.textContent = 'Cancel';
    cancelBtn.className = 'btn-secondary';
    cancelBtn.addEventListener('click', () => this.props.onCancel?.());

    actions.appendChild(resolveBtn);
    actions.appendChild(cancelBtn);
    content.appendChild(actions);

    modal.appendChild(content);
    return modal;
  }

  private createConflictItem(conflict: Conflict): HTMLElement {
    const item = document.createElement('div');
    item.className = 'conflict-item';

    item.innerHTML = `
      <div class="conflict-description">
        <strong>${conflict.package1} ↔ ${conflict.package2}</strong>
        <p>${conflict.reason}</p>
        ${conflict.resolution ? `<p class="suggested-resolution">Suggested: ${conflict.resolution}</p>` : ''}
      </div>
    `;

    const select = document.createElement('select');
    select.className = 'conflict-resolution-select';
    select.innerHTML = `
      <option value="${conflict.package1}">Keep ${conflict.package1}</option>
      <option value="${conflict.package2}">Keep ${conflict.package2}</option>
      <option value="both">Keep both (advanced)</option>
      <option value="neither">Skip both</option>
    `;

    if (conflict.autoResolve && conflict.resolution) {
      select.value = conflict.resolution;
    }

    select.addEventListener('change', () => {
      this.resolutions[conflict.id] = select.value;
    });

    item.appendChild(select);
    return item;
  }

  private handleResolve(): void {
    this.props.onResolve?.(this.resolutions);
  }
}

/**
 * Natural Language Input Component
 */
export class NaturalLanguageInput extends Component<NaturalLanguageInputProps> {
  render(): HTMLElement {
    const container = document.createElement('div');
    container.className = `natural-language-input ${this.props.className || ''}`;

    const inputWrapper = document.createElement('div');
    inputWrapper.className = 'input-wrapper';

    const input = document.createElement('input');
    input.type = 'text';
    input.placeholder = this.props.placeholder || 'Describe what you need...';
    input.className = 'nl-input';

    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.props.onSubmit?.((e.target as HTMLInputElement).value);
      }
    });

    inputWrapper.appendChild(input);

    // Voice input button if enabled
    if (this.props.voiceEnabled) {
      const voiceBtn = document.createElement('button');
      voiceBtn.className = 'voice-input-btn';
      voiceBtn.innerHTML = '🎤';
      voiceBtn.addEventListener('click', () => this.props.onVoiceInput?.());
      inputWrapper.appendChild(voiceBtn);
    }

    container.appendChild(inputWrapper);

    // Suggestions if provided
    if (this.props.suggestions && this.props.suggestions.length > 0) {
      const suggestionsList = document.createElement('ul');
      suggestionsList.className = 'suggestions';

      this.props.suggestions.forEach(suggestion => {
        const li = document.createElement('li');
        li.className = 'suggestion';
        li.textContent = suggestion;
        li.addEventListener('click', () => {
          input.value = suggestion;
          this.props.onSubmit?.(suggestion);
        });
        suggestionsList.appendChild(li);
      });

      container.appendChild(suggestionsList);
    }

    return container;
  }
}

/**
 * Component Factory for easy creation
 */
export class ComponentFactory {
  static createProfileCard(profile: Profile, selected = false, onSelect?: (p: Profile) => void): ProfileCard {
    return new ProfileCard({ profile, selected, onSelect });
  }

  static createPackageSelector(
    packages: Package[], 
    category: string,
    options: Partial<PackageSelectorProps> = {}
  ): PackageSelector {
    return new PackageSelector({
      packages,
      category,
      multiSelect: true,
      showSearch: true,
      ...options
    });
  }

  static createConflictResolver(
    conflicts: Conflict[],
    onResolve?: (resolutions: Record<string, string>) => void,
    onCancel?: () => void
  ): ConflictResolver {
    return new ConflictResolver({ conflicts, onResolve, onCancel });
  }

  static createNaturalLanguageInput(
    options: Partial<NaturalLanguageInputProps> = {}
  ): NaturalLanguageInput {
    return new NaturalLanguageInput({
      placeholder: 'Describe what you need...',
      voiceEnabled: true,
      aiAssist: true,
      ...options
    });
  }
}