/**
 * 🌟 Luminous Setup Ceremony
 * Orchestrates the modular components for intelligent system setup
 * Integrates with both nixos-gui backend and Luminous Nix Python services
 */

import {
  ComponentFactory,
  ProfileCard,
  PackageSelector,
  ConflictResolver,
  NaturalLanguageInput,
  Profile,
  Package,
  Conflict,
  Generation
} from './components/ModularComponents';

// Setup stages
export enum SetupStage {
  WELCOME = 'welcome',
  PROFILE_SELECTION = 'profile_selection',
  ESSENTIALS = 'essentials',
  SPECIALIZED = 'specialized',
  PERSONAL = 'personal',
  NATURAL_LANGUAGE = 'natural_language',
  CONFLICTS = 'conflicts',
  PREVIEW = 'preview',
  INSTALLING = 'installing',
  COMPLETE = 'complete'
}

// Ceremony state
export interface CeremonyState {
  currentStage: SetupStage;
  selectedProfile: Profile | null;
  selectedPackages: Package[];
  conflicts: Conflict[];
  resolutions: Record<string, string>;
  checkpoints: Generation[];
  installedPackages: Package[];
}

// API interfaces
export interface SetupAPI {
  detectInstalledPackages(): Promise<Package[]>;
  inferProfile(packages: Package[]): Promise<Profile>;
  getProfiles(): Promise<Profile[]>;
  getRecommendations(profile: Profile, installed: Package[]): Promise<{
    essential: Package[];
    recommended: Package[];
    companions: Package[];
  }>;
  detectConflicts(packages: Package[]): Promise<Conflict[]>;
  searchPackages(query: string): Promise<Package[]>;
  applyConfiguration(state: CeremonyState): Promise<boolean>;
  createCheckpoint(description: string): Promise<Generation>;
}

/**
 * Main Setup Ceremony Orchestrator
 */
export class SetupCeremony {
  private container: HTMLElement;
  private api: SetupAPI;
  private state: CeremonyState;
  private components: Map<string, any> = new Map();

  constructor(container: HTMLElement, api: SetupAPI) {
    this.container = container;
    this.api = api;
    this.state = {
      currentStage: SetupStage.WELCOME,
      selectedProfile: null,
      selectedPackages: [],
      conflicts: [],
      resolutions: {},
      checkpoints: [],
      installedPackages: []
    };
  }

  /**
   * Start the ceremony
   */
  async start(): Promise<void> {
    // Detect what's already installed
    this.state.installedPackages = await this.api.detectInstalledPackages();
    
    // Infer profile from installed packages
    const suggestedProfile = await this.api.inferProfile(this.state.installedPackages);
    
    // Show welcome screen
    this.renderWelcome(suggestedProfile);
  }

  /**
   * Render welcome screen
   */
  private renderWelcome(suggestedProfile: Profile): void {
    this.clearContainer();
    
    const welcome = document.createElement('div');
    welcome.className = 'ceremony-welcome';
    welcome.innerHTML = `
      <div class="welcome-header">
        <h1>🌟 Welcome to Your System Setup Ceremony</h1>
        <p>Let's create the perfect environment for you</p>
      </div>
      
      <div class="detected-info">
        <h3>I've detected:</h3>
        <ul>
          <li>📦 ${this.state.installedPackages.length} packages already installed</li>
          <li>👤 You look like a: <strong>${suggestedProfile.name}</strong></li>
        </ul>
      </div>
      
      <div class="ceremony-overview">
        <h3>This ceremony will guide you through:</h3>
        <ol>
          <li>Selecting your user profile</li>
          <li>Installing essential packages</li>
          <li>Adding specialized tools</li>
          <li>Personal customization</li>
        </ol>
      </div>
      
      <button class="btn-primary start-ceremony">Begin Setup Ceremony</button>
    `;
    
    const startBtn = welcome.querySelector('.start-ceremony');
    startBtn?.addEventListener('click', () => this.nextStage());
    
    this.container.appendChild(welcome);
  }

  /**
   * Render profile selection
   */
  private async renderProfileSelection(): Promise<void> {
    this.clearContainer();
    
    const profiles = await this.api.getProfiles();
    
    const container = document.createElement('div');
    container.className = 'profile-selection';
    container.innerHTML = `
      <h2>Choose Your Digital Personality</h2>
      <p>Select the profile that best matches how you'll use this computer</p>
    `;
    
    const profileGrid = document.createElement('div');
    profileGrid.className = 'profile-grid';
    
    profiles.forEach(profile => {
      const card = ComponentFactory.createProfileCard(
        profile,
        false,
        (selectedProfile) => {
          this.state.selectedProfile = selectedProfile;
          // Update visual selection
          this.updateProfileSelection(profileGrid, selectedProfile);
        }
      );
      card.mount(profileGrid);
    });
    
    container.appendChild(profileGrid);
    
    const continueBtn = document.createElement('button');
    continueBtn.className = 'btn-primary';
    continueBtn.textContent = 'Continue with Selected Profile';
    continueBtn.disabled = !this.state.selectedProfile;
    continueBtn.addEventListener('click', () => this.nextStage());
    
    container.appendChild(continueBtn);
    this.container.appendChild(container);
  }

  /**
   * Update profile selection visually
   */
  private updateProfileSelection(grid: HTMLElement, selected: Profile): void {
    grid.querySelectorAll('.profile-card').forEach(card => {
      card.classList.remove('selected');
    });
    const selectedCard = grid.querySelector(`[data-profile="${selected.name}"]`);
    selectedCard?.classList.add('selected');
    
    // Enable continue button
    const btn = this.container.querySelector('.btn-primary') as HTMLButtonElement;
    if (btn) btn.disabled = false;
  }

  /**
   * Render package selection round
   */
  private async renderPackageSelection(round: 'essentials' | 'specialized' | 'personal'): Promise<void> {
    this.clearContainer();
    
    if (!this.state.selectedProfile) return;
    
    const recommendations = await this.api.getRecommendations(
      this.state.selectedProfile,
      this.state.installedPackages
    );
    
    let packages: Package[] = [];
    let title = '';
    let description = '';
    
    switch (round) {
      case 'essentials':
        packages = recommendations.essential;
        title = 'Essential Packages';
        description = 'These are the core packages for your profile';
        break;
      case 'specialized':
        packages = recommendations.recommended;
        title = 'Professional Tools';
        description = 'Specialized tools for your workflow';
        break;
      case 'personal':
        packages = recommendations.companions;
        title = 'Personal Touches';
        description = 'Additional software to enhance your experience';
        break;
    }
    
    const container = document.createElement('div');
    container.className = 'package-selection-round';
    container.innerHTML = `
      <h2>${title}</h2>
      <p>${description}</p>
    `;
    
    // Create package selector
    const selector = ComponentFactory.createPackageSelector(
      packages,
      title,
      {
        multiSelect: true,
        showSearch: true,
        showSize: true,
        onPackageSelect: (selected) => {
          // Add to selected packages
          this.state.selectedPackages = [
            ...this.state.selectedPackages.filter(p => 
              !packages.find(pkg => pkg.name === p.name)
            ),
            ...selected
          ];
          this.updateEstimation();
        }
      }
    );
    
    selector.mount(container);
    
    // Add estimation panel
    this.renderEstimation(container);
    
    // Navigation buttons
    const nav = document.createElement('div');
    nav.className = 'navigation';
    nav.innerHTML = `
      <button class="btn-secondary back">Back</button>
      <button class="btn-primary continue">Continue</button>
      <button class="btn-ghost skip">Skip</button>
    `;
    
    nav.querySelector('.back')?.addEventListener('click', () => this.previousStage());
    nav.querySelector('.continue')?.addEventListener('click', () => this.handlePackagesContinue());
    nav.querySelector('.skip')?.addEventListener('click', () => this.skipStage());
    
    container.appendChild(nav);
    this.container.appendChild(container);
  }

  /**
   * Handle continuing after package selection
   */
  private async handlePackagesContinue(): Promise<void> {
    // Check for conflicts
    const conflicts = await this.api.detectConflicts(this.state.selectedPackages);
    
    if (conflicts.length > 0) {
      this.state.conflicts = conflicts;
      this.state.currentStage = SetupStage.CONFLICTS;
      this.renderConflicts();
    } else {
      // Create checkpoint
      await this.createCheckpoint();
      this.nextStage();
    }
  }

  /**
   * Render conflict resolution
   */
  private renderConflicts(): void {
    this.clearContainer();
    
    const resolver = ComponentFactory.createConflictResolver(
      this.state.conflicts,
      (resolutions) => {
        this.state.resolutions = resolutions;
        this.applyResolutions();
        this.nextStage();
      },
      () => {
        // Cancel - go back
        this.previousStage();
      }
    );
    
    resolver.mount(this.container);
  }

  /**
   * Apply conflict resolutions
   */
  private applyResolutions(): void {
    // Remove conflicting packages based on resolutions
    Object.entries(this.state.resolutions).forEach(([conflictId, resolution]) => {
      const conflict = this.state.conflicts.find(c => c.id === conflictId);
      if (!conflict) return;
      
      if (resolution === 'neither') {
        // Remove both packages
        this.state.selectedPackages = this.state.selectedPackages.filter(p => 
          p.name !== conflict.package1 && p.name !== conflict.package2
        );
      } else if (resolution !== 'both') {
        // Keep only the selected one
        const toRemove = resolution === conflict.package1 ? conflict.package2 : conflict.package1;
        this.state.selectedPackages = this.state.selectedPackages.filter(p => 
          p.name !== toRemove
        );
      }
      // If 'both', keep both (advanced users)
    });
    
    // Clear conflicts
    this.state.conflicts = [];
  }

  /**
   * Render natural language input for final additions
   */
  private renderNaturalLanguage(): void {
    this.clearContainer();
    
    const container = document.createElement('div');
    container.className = 'natural-language-round';
    container.innerHTML = `
      <h2>Anything Else You Need?</h2>
      <p>Describe any additional software or tools you need</p>
      
      <div class="current-selection">
        <h3>Your current selection:</h3>
        <ul>
          <li>Profile: ${this.state.selectedProfile?.name}</li>
          <li>Packages: ${this.state.selectedPackages.length} selected</li>
        </ul>
      </div>
    `;
    
    const nlInput = ComponentFactory.createNaturalLanguageInput({
      placeholder: 'e.g., "I need video editing software" or "Tools for Python development"',
      suggestions: [
        'Video editing software',
        'Music production tools',
        'Python development environment',
        'Photo editing tools',
        'Gaming software'
      ],
      voiceEnabled: true,
      onSubmit: async (text) => {
        await this.handleNaturalLanguageRequest(text);
      }
    });
    
    nlInput.mount(container);
    
    // Results area
    const results = document.createElement('div');
    results.className = 'nl-results';
    results.id = 'nl-results';
    container.appendChild(results);
    
    // Navigation
    const nav = document.createElement('div');
    nav.className = 'navigation';
    nav.innerHTML = `
      <button class="btn-secondary back">Back</button>
      <button class="btn-primary finish">Finish Setup</button>
    `;
    
    nav.querySelector('.back')?.addEventListener('click', () => this.previousStage());
    nav.querySelector('.finish')?.addEventListener('click', () => this.finishSetup());
    
    container.appendChild(nav);
    this.container.appendChild(container);
  }

  /**
   * Handle natural language package request
   */
  private async handleNaturalLanguageRequest(text: string): Promise<void> {
    const results = document.getElementById('nl-results');
    if (!results) return;
    
    results.innerHTML = '<div class="loading">Searching for packages...</div>';
    
    const packages = await this.api.searchPackages(text);
    
    if (packages.length === 0) {
      results.innerHTML = '<p>No packages found for that description</p>';
      return;
    }
    
    // Create mini package selector for results
    const miniSelector = ComponentFactory.createPackageSelector(
      packages.slice(0, 5),
      'Search Results',
      {
        multiSelect: true,
        showSize: true,
        onPackageSelect: (selected) => {
          this.state.selectedPackages = [
            ...this.state.selectedPackages,
            ...selected
          ];
          this.updateEstimation();
        }
      }
    );
    
    results.innerHTML = '';
    miniSelector.mount(results);
  }

  /**
   * Render estimation panel
   */
  private renderEstimation(container: HTMLElement): void {
    const estimation = document.createElement('div');
    estimation.className = 'estimation-panel';
    estimation.id = 'estimation';
    
    this.updateEstimationContent(estimation);
    container.appendChild(estimation);
  }

  /**
   * Update estimation content
   */
  private updateEstimationContent(element?: HTMLElement): void {
    const target = element || document.getElementById('estimation');
    if (!target) return;
    
    const count = this.state.selectedPackages.length;
    const sizeGB = (count * 50 / 1024).toFixed(1);
    const timeMin = Math.ceil(count * 0.5);
    
    target.innerHTML = `
      <h3>Installation Estimate</h3>
      <div class="estimation-stats">
        <div>📦 ${count} packages</div>
        <div>💾 ~${sizeGB} GB</div>
        <div>⏱️ ~${timeMin} minutes</div>
      </div>
    `;
  }

  /**
   * Update estimation globally
   */
  private updateEstimation(): void {
    this.updateEstimationContent();
  }

  /**
   * Finish setup and apply configuration
   */
  private async finishSetup(): Promise<void> {
    this.state.currentStage = SetupStage.INSTALLING;
    this.renderInstalling();
    
    const success = await this.api.applyConfiguration(this.state);
    
    if (success) {
      this.state.currentStage = SetupStage.COMPLETE;
      this.renderComplete();
    } else {
      this.renderError();
    }
  }

  /**
   * Render installing screen
   */
  private renderInstalling(): void {
    this.clearContainer();
    
    const installing = document.createElement('div');
    installing.className = 'installing-screen';
    installing.innerHTML = `
      <h2>✨ Manifesting Your Perfect System...</h2>
      <div class="progress-container">
        <div class="progress-bar">
          <div class="progress-fill" style="width: 0%"></div>
        </div>
        <p class="progress-message">Preparing installation...</p>
      </div>
    `;
    
    this.container.appendChild(installing);
    
    // Simulate progress (in real app, would get updates from backend)
    this.simulateProgress();
  }

  /**
   * Simulate installation progress
   */
  private simulateProgress(): void {
    let progress = 0;
    const fill = this.container.querySelector('.progress-fill') as HTMLElement;
    const message = this.container.querySelector('.progress-message') as HTMLElement;
    
    const interval = setInterval(() => {
      progress += Math.random() * 15;
      if (progress > 100) progress = 100;
      
      fill.style.width = `${progress}%`;
      
      if (progress < 30) {
        message.textContent = 'Downloading packages...';
      } else if (progress < 60) {
        message.textContent = 'Installing packages...';
      } else if (progress < 90) {
        message.textContent = 'Configuring system...';
      } else {
        message.textContent = 'Finalizing...';
      }
      
      if (progress >= 100) {
        clearInterval(interval);
      }
    }, 500);
  }

  /**
   * Render completion screen
   */
  private renderComplete(): void {
    this.clearContainer();
    
    const complete = document.createElement('div');
    complete.className = 'ceremony-complete';
    complete.innerHTML = `
      <div class="success-icon">✅</div>
      <h1>System Setup Complete!</h1>
      
      <div class="summary">
        <h3>Your ${this.state.selectedProfile?.name} environment is ready</h3>
        <ul>
          <li>✓ ${this.state.selectedPackages.length} packages installed</li>
          <li>✓ System optimized for ${this.state.selectedProfile?.optimizations.join(', ')}</li>
          <li>✓ Configuration saved and backed up</li>
        </ul>
      </div>
      
      <div class="next-steps">
        <h3>Next Steps:</h3>
        <ol>
          <li>Restart your system to apply all changes</li>
          <li>Explore your new environment</li>
          <li>Run <code>ask-nix help</code> for assistance</li>
        </ol>
      </div>
      
      <button class="btn-primary" onclick="location.reload()">Close Setup</button>
    `;
    
    this.container.appendChild(complete);
  }

  /**
   * Render error screen
   */
  private renderError(): void {
    this.clearContainer();
    
    const error = document.createElement('div');
    error.className = 'ceremony-error';
    error.innerHTML = `
      <div class="error-icon">❌</div>
      <h1>Setup Failed</h1>
      <p>There was an error applying your configuration.</p>
      <p>Your system has not been modified.</p>
      <button class="btn-primary" onclick="location.reload()">Try Again</button>
    `;
    
    this.container.appendChild(error);
  }

  /**
   * Create a checkpoint
   */
  private async createCheckpoint(): Promise<void> {
    const description = `Setup Round - ${this.state.currentStage}`;
    const checkpoint = await this.api.createCheckpoint(description);
    this.state.checkpoints.push(checkpoint);
  }

  /**
   * Navigate to next stage
   */
  private nextStage(): void {
    const stages = Object.values(SetupStage);
    const currentIndex = stages.indexOf(this.state.currentStage);
    
    if (currentIndex < stages.length - 1) {
      this.state.currentStage = stages[currentIndex + 1];
      this.renderCurrentStage();
    }
  }

  /**
   * Navigate to previous stage
   */
  private previousStage(): void {
    const stages = Object.values(SetupStage);
    const currentIndex = stages.indexOf(this.state.currentStage);
    
    if (currentIndex > 0) {
      this.state.currentStage = stages[currentIndex - 1];
      this.renderCurrentStage();
    }
  }

  /**
   * Skip current stage
   */
  private skipStage(): void {
    this.nextStage();
  }

  /**
   * Render current stage
   */
  private renderCurrentStage(): void {
    switch (this.state.currentStage) {
      case SetupStage.WELCOME:
        this.start();
        break;
      case SetupStage.PROFILE_SELECTION:
        this.renderProfileSelection();
        break;
      case SetupStage.ESSENTIALS:
        this.renderPackageSelection('essentials');
        break;
      case SetupStage.SPECIALIZED:
        this.renderPackageSelection('specialized');
        break;
      case SetupStage.PERSONAL:
        this.renderPackageSelection('personal');
        break;
      case SetupStage.NATURAL_LANGUAGE:
        this.renderNaturalLanguage();
        break;
      case SetupStage.CONFLICTS:
        this.renderConflicts();
        break;
      case SetupStage.INSTALLING:
        this.renderInstalling();
        break;
      case SetupStage.COMPLETE:
        this.renderComplete();
        break;
    }
  }

  /**
   * Clear container
   */
  private clearContainer(): void {
    this.container.innerHTML = '';
  }
}

/**
 * Initialize the Setup Ceremony
 */
export function initSetupCeremony(containerId: string, apiUrl: string): SetupCeremony {
  const container = document.getElementById(containerId);
  if (!container) {
    throw new Error(`Container with id "${containerId}" not found`);
  }

  // Create API implementation
  const api = createSetupAPI(apiUrl);
  
  // Create and return ceremony instance
  return new SetupCeremony(container, api);
}

/**
 * Create API implementation that connects to backend
 */
function createSetupAPI(baseUrl: string): SetupAPI {
  return {
    async detectInstalledPackages(): Promise<Package[]> {
      const response = await fetch(`${baseUrl}/api/packages/installed`);
      return response.json();
    },

    async inferProfile(packages: Package[]): Promise<Profile> {
      const response = await fetch(`${baseUrl}/api/profiles/infer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ packages })
      });
      return response.json();
    },

    async getProfiles(): Promise<Profile[]> {
      const response = await fetch(`${baseUrl}/api/profiles`);
      return response.json();
    },

    async getRecommendations(profile: Profile, installed: Package[]): Promise<any> {
      const response = await fetch(`${baseUrl}/api/packages/recommendations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile, installed })
      });
      return response.json();
    },

    async detectConflicts(packages: Package[]): Promise<Conflict[]> {
      const response = await fetch(`${baseUrl}/api/packages/conflicts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ packages })
      });
      return response.json();
    },

    async searchPackages(query: string): Promise<Package[]> {
      const response = await fetch(`${baseUrl}/api/packages/search?q=${encodeURIComponent(query)}`);
      return response.json();
    },

    async applyConfiguration(state: CeremonyState): Promise<boolean> {
      const response = await fetch(`${baseUrl}/api/setup/apply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(state)
      });
      return response.ok;
    },

    async createCheckpoint(description: string): Promise<Generation> {
      const response = await fetch(`${baseUrl}/api/generations/checkpoint`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description })
      });
      return response.json();
    }
  };
}