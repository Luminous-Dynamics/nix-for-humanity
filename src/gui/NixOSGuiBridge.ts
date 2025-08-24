/**
 * 🌉 Bridge between Luminous Nix components and nixos-gui backend
 * Integrates TypeScript components with existing JavaScript services
 */

import { SetupAPI, Package, Profile, Conflict, Generation } from './SetupCeremony';
import { Store, EventBus } from './StateManager';

/**
 * Configuration for the bridge
 */
export interface BridgeConfig {
  nixosGuiUrl: string;      // URL to nixos-gui backend
  luminousNixUrl: string;    // URL to Luminous Nix Python API
  useWebSocket?: boolean;    // Enable WebSocket for real-time updates
  authToken?: string;        // Authentication token if needed
}

/**
 * Real-time update events
 */
export enum RealtimeEvent {
  PACKAGE_INSTALLED = 'package:installed',
  PACKAGE_REMOVED = 'package:removed',
  CONFIGURATION_CHANGED = 'config:changed',
  GENERATION_CREATED = 'generation:created',
  PROGRESS_UPDATE = 'progress:update',
  ERROR_OCCURRED = 'error:occurred'
}

/**
 * Bridge implementation that connects to both backends
 */
export class NixOSGuiBridge implements SetupAPI {
  private config: BridgeConfig;
  private eventBus: EventBus;
  private ws?: WebSocket;
  private cache: Map<string, any> = new Map();
  private cacheTimeout = 5 * 60 * 1000; // 5 minutes

  constructor(config: BridgeConfig) {
    this.config = config;
    this.eventBus = new EventBus();
    
    if (config.useWebSocket) {
      this.connectWebSocket();
    }
  }

  /**
   * Connect to WebSocket for real-time updates
   */
  private connectWebSocket(): void {
    const wsUrl = this.config.nixosGuiUrl.replace('http', 'ws') + '/ws';
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.eventBus.emit('ws:connected');
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleRealtimeUpdate(data);
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.eventBus.emit('ws:error', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.eventBus.emit('ws:disconnected');
      // Attempt to reconnect after 5 seconds
      setTimeout(() => this.connectWebSocket(), 5000);
    };
  }

  /**
   * Handle real-time updates from WebSocket
   */
  private handleRealtimeUpdate(data: any): void {
    switch (data.type) {
      case 'package_installed':
        this.eventBus.emit(RealtimeEvent.PACKAGE_INSTALLED, data.package);
        break;
      case 'progress':
        this.eventBus.emit(RealtimeEvent.PROGRESS_UPDATE, data.progress);
        break;
      case 'error':
        this.eventBus.emit(RealtimeEvent.ERROR_OCCURRED, data.error);
        break;
      default:
        console.log('Unknown realtime event:', data.type);
    }
  }

  /**
   * Subscribe to real-time events
   */
  on(event: RealtimeEvent, handler: Function): void {
    this.eventBus.on(event, handler);
  }

  /**
   * Make HTTP request with caching
   */
  private async request<T>(
    url: string,
    options: RequestInit = {},
    useCache = true
  ): Promise<T> {
    const cacheKey = `${options.method || 'GET'}:${url}:${JSON.stringify(options.body)}`;
    
    // Check cache
    if (useCache && this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }
    }

    // Add auth token if provided
    if (this.config.authToken) {
      options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${this.config.authToken}`
      };
    }

    try {
      const response = await fetch(url, options);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Cache successful responses
      if (useCache) {
        this.cache.set(cacheKey, {
          data,
          timestamp: Date.now()
        });
      }
      
      return data;
    } catch (error) {
      console.error('Request failed:', error);
      throw error;
    }
  }

  /**
   * Detect installed packages using nixos-gui backend
   */
  async detectInstalledPackages(): Promise<Package[]> {
    const data = await this.request<any[]>(
      `${this.config.nixosGuiUrl}/api/packages/installed`
    );
    
    return data.map(pkg => ({
      name: pkg.name,
      description: pkg.description,
      version: pkg.version,
      size: pkg.size,
      category: pkg.category,
      selected: false
    }));
  }

  /**
   * Infer profile using Luminous Nix AI
   */
  async inferProfile(packages: Package[]): Promise<Profile> {
    const data = await this.request<any>(
      `${this.config.luminousNixUrl}/api/profiles/infer`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ packages })
      }
    );
    
    return {
      type: data.type,
      name: data.name,
      emoji: data.emoji,
      description: data.description,
      packages: data.packages,
      optionalPackages: data.optional_packages,
      optimizations: data.optimizations,
      aiPersona: data.ai_persona,
      settings: data.settings
    };
  }

  /**
   * Get available profiles
   */
  async getProfiles(): Promise<Profile[]> {
    // Try Luminous Nix first for AI-enhanced profiles
    try {
      const data = await this.request<any[]>(
        `${this.config.luminousNixUrl}/api/profiles`
      );
      return data;
    } catch (e) {
      // Fallback to static profiles from nixos-gui
      const data = await this.request<any[]>(
        `${this.config.nixosGuiUrl}/api/profiles`
      );
      return data;
    }
  }

  /**
   * Get package recommendations using AI
   */
  async getRecommendations(
    profile: Profile,
    installed: Package[]
  ): Promise<{ essential: Package[]; recommended: Package[]; companions: Package[] }> {
    // Use Luminous Nix AI for intelligent recommendations
    const data = await this.request<any>(
      `${this.config.luminousNixUrl}/api/packages/recommendations`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile, installed })
      }
    );
    
    return {
      essential: data.essential || [],
      recommended: data.recommended || [],
      companions: data.companions || []
    };
  }

  /**
   * Detect package conflicts
   */
  async detectConflicts(packages: Package[]): Promise<Conflict[]> {
    const data = await this.request<any[]>(
      `${this.config.nixosGuiUrl}/api/packages/conflicts`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ packages })
      }
    );
    
    return data.map(conflict => ({
      id: conflict.id || `${conflict.package1}-${conflict.package2}`,
      package1: conflict.package1,
      package2: conflict.package2,
      reason: conflict.reason,
      resolution: conflict.resolution,
      autoResolve: conflict.auto_resolve
    }));
  }

  /**
   * Search packages using natural language
   */
  async searchPackages(query: string): Promise<Package[]> {
    // Try Luminous Nix natural language search first
    try {
      const data = await this.request<any[]>(
        `${this.config.luminousNixUrl}/api/packages/search?q=${encodeURIComponent(query)}`
      );
      return data;
    } catch (e) {
      // Fallback to nixos-gui regular search
      const data = await this.request<any[]>(
        `${this.config.nixosGuiUrl}/api/packages/search?q=${encodeURIComponent(query)}`
      );
      return data;
    }
  }

  /**
   * Apply configuration with progress tracking
   */
  async applyConfiguration(state: any): Promise<boolean> {
    // Send to nixos-gui for actual installation
    const installPromise = this.request<any>(
      `${this.config.nixosGuiUrl}/api/setup/apply`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(state)
      },
      false // Don't cache this
    );

    // Also notify Luminous Nix for learning
    this.request(
      `${this.config.luminousNixUrl}/api/setup/learn`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          profile: state.selectedProfile,
          packages: state.selectedPackages,
          timestamp: Date.now()
        })
      },
      false
    ).catch(e => console.log('Failed to send learning data:', e));

    const result = await installPromise;
    return result.success;
  }

  /**
   * Create system checkpoint/generation
   */
  async createCheckpoint(description: string): Promise<Generation> {
    const data = await this.request<any>(
      `${this.config.nixosGuiUrl}/api/generations/checkpoint`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description })
      },
      false
    );
    
    return {
      id: data.id,
      description: data.description,
      date: data.date,
      packages: data.packages,
      changes: data.changes
    };
  }

  /**
   * Get installation progress
   */
  async getProgress(): Promise<{ current: number; total: number; message: string }> {
    const data = await this.request<any>(
      `${this.config.nixosGuiUrl}/api/setup/progress`,
      {},
      false // Don't cache progress
    );
    
    return {
      current: data.current,
      total: data.total,
      message: data.message
    };
  }

  /**
   * Cancel ongoing installation
   */
  async cancelInstallation(): Promise<boolean> {
    const data = await this.request<any>(
      `${this.config.nixosGuiUrl}/api/setup/cancel`,
      { method: 'POST' },
      false
    );
    
    return data.success;
  }

  /**
   * Get system health status
   */
  async getSystemHealth(): Promise<any> {
    const data = await this.request<any>(
      `${this.config.nixosGuiUrl}/api/system/health`
    );
    
    return data;
  }

  /**
   * Clear cache
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * Disconnect and cleanup
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
    }
    this.clearCache();
  }
}

/**
 * Factory function to create configured bridge
 */
export function createBridge(config?: Partial<BridgeConfig>): NixOSGuiBridge {
  const defaultConfig: BridgeConfig = {
    nixosGuiUrl: process.env.NIXOS_GUI_URL || 'http://localhost:8080',
    luminousNixUrl: process.env.LUMINOUS_NIX_URL || 'http://localhost:8888',
    useWebSocket: true
  };

  return new NixOSGuiBridge({
    ...defaultConfig,
    ...config
  });
}

/**
 * Integration helper for existing nixos-gui pages
 */
export class NixOSGuiIntegration {
  private bridge: NixOSGuiBridge;
  private store?: Store<any>;

  constructor(bridge: NixOSGuiBridge) {
    this.bridge = bridge;
  }

  /**
   * Inject setup ceremony into existing page
   */
  injectSetupCeremony(containerId: string): void {
    const container = document.getElementById(containerId);
    if (!container) {
      console.error(`Container ${containerId} not found`);
      return;
    }

    // Add styles
    this.injectStyles();

    // Import and initialize SetupCeremony
    import('./SetupCeremony').then(({ SetupCeremony }) => {
      const ceremony = new SetupCeremony(container, this.bridge);
      ceremony.start();
    });
  }

  /**
   * Add modular component to existing page
   */
  addComponent(
    containerId: string,
    componentType: string,
    props: any
  ): void {
    const container = document.getElementById(containerId);
    if (!container) return;

    import('./components/ModularComponents').then((module) => {
      let component;
      
      switch (componentType) {
        case 'ProfileCard':
          component = module.ComponentFactory.createProfileCard(
            props.profile,
            props.selected,
            props.onSelect
          );
          break;
        case 'PackageSelector':
          component = module.ComponentFactory.createPackageSelector(
            props.packages,
            props.category,
            props
          );
          break;
        case 'NaturalLanguageInput':
          component = module.ComponentFactory.createNaturalLanguageInput(props);
          break;
        default:
          console.error(`Unknown component type: ${componentType}`);
          return;
      }

      component.mount(container);
    });
  }

  /**
   * Inject required styles
   */
  private injectStyles(): void {
    if (document.getElementById('setup-ceremony-styles')) {
      return; // Already injected
    }

    const link = document.createElement('link');
    link.id = 'setup-ceremony-styles';
    link.rel = 'stylesheet';
    link.href = '/styles/SetupCeremony.css';
    document.head.appendChild(link);
  }

  /**
   * Connect to state management
   */
  connectToStore(store: Store<any>): void {
    this.store = store;
    
    // Subscribe to real-time events and update store
    this.bridge.on(RealtimeEvent.PROGRESS_UPDATE, (progress: any) => {
      store.setState({
        progress: {
          current: progress.current,
          total: progress.total,
          message: progress.message
        }
      });
    });

    this.bridge.on(RealtimeEvent.ERROR_OCCURRED, (error: string) => {
      store.setState({
        ui: {
          ...store.getState().ui,
          error
        }
      });
    });
  }
}

/**
 * Global integration object for easy access from existing JavaScript
 */
if (typeof window !== 'undefined') {
  (window as any).LuminousNixIntegration = {
    createBridge,
    NixOSGuiIntegration,
    
    // Quick setup for existing pages
    quickSetup: (containerId: string, config?: Partial<BridgeConfig>) => {
      const bridge = createBridge(config);
      const integration = new NixOSGuiIntegration(bridge);
      integration.injectSetupCeremony(containerId);
      return integration;
    },
    
    // Add individual components
    addComponent: (containerId: string, type: string, props: any, config?: Partial<BridgeConfig>) => {
      const bridge = createBridge(config);
      const integration = new NixOSGuiIntegration(bridge);
      integration.addComponent(containerId, type, props);
      return integration;
    }
  };
}