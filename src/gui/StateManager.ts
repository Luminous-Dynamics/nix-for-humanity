/**
 * 🧠 State Management System
 * Manages state across components with event-driven architecture
 */

export type StateListener<T> = (state: T) => void;
export type StateSelector<T, R> = (state: T) => R;

/**
 * Event system for component communication
 */
export class EventBus {
  private events: Map<string, Set<Function>> = new Map();

  on(event: string, handler: Function): void {
    if (!this.events.has(event)) {
      this.events.set(event, new Set());
    }
    this.events.get(event)!.add(handler);
  }

  off(event: string, handler: Function): void {
    const handlers = this.events.get(event);
    if (handlers) {
      handlers.delete(handler);
    }
  }

  emit(event: string, ...args: any[]): void {
    const handlers = this.events.get(event);
    if (handlers) {
      handlers.forEach(handler => handler(...args));
    }
  }

  once(event: string, handler: Function): void {
    const wrapper = (...args: any[]) => {
      handler(...args);
      this.off(event, wrapper);
    };
    this.on(event, wrapper);
  }
}

/**
 * State store with immutable updates
 */
export class Store<T> {
  private state: T;
  private listeners: Set<StateListener<T>> = new Set();
  private selectorCache: Map<string, any> = new Map();

  constructor(initialState: T) {
    this.state = Object.freeze({ ...initialState });
  }

  getState(): T {
    return this.state;
  }

  setState(updater: Partial<T> | ((state: T) => Partial<T>)): void {
    const updates = typeof updater === 'function' ? updater(this.state) : updater;
    const newState = Object.freeze({ ...this.state, ...updates });
    
    if (this.hasChanged(this.state, newState)) {
      this.state = newState;
      this.notify();
    }
  }

  subscribe(listener: StateListener<T>): () => void {
    this.listeners.add(listener);
    listener(this.state); // Call immediately with current state
    
    // Return unsubscribe function
    return () => {
      this.listeners.delete(listener);
    };
  }

  select<R>(selector: StateSelector<T, R>, cacheKey?: string): R {
    if (cacheKey && this.selectorCache.has(cacheKey)) {
      return this.selectorCache.get(cacheKey);
    }
    
    const result = selector(this.state);
    
    if (cacheKey) {
      this.selectorCache.set(cacheKey, result);
    }
    
    return result;
  }

  private notify(): void {
    this.selectorCache.clear(); // Clear selector cache on state change
    this.listeners.forEach(listener => listener(this.state));
  }

  private hasChanged(oldState: T, newState: T): boolean {
    return JSON.stringify(oldState) !== JSON.stringify(newState);
  }
}

/**
 * Action types for state updates
 */
export enum ActionType {
  // Profile actions
  SET_PROFILE = 'SET_PROFILE',
  UPDATE_PROFILE_SETTINGS = 'UPDATE_PROFILE_SETTINGS',
  
  // Package actions
  ADD_PACKAGE = 'ADD_PACKAGE',
  REMOVE_PACKAGE = 'REMOVE_PACKAGE',
  SET_PACKAGES = 'SET_PACKAGES',
  UPDATE_PACKAGE = 'UPDATE_PACKAGE',
  
  // Conflict actions
  ADD_CONFLICT = 'ADD_CONFLICT',
  RESOLVE_CONFLICT = 'RESOLVE_CONFLICT',
  CLEAR_CONFLICTS = 'CLEAR_CONFLICTS',
  
  // Progress actions
  SET_PROGRESS = 'SET_PROGRESS',
  UPDATE_PROGRESS = 'UPDATE_PROGRESS',
  
  // UI actions
  SET_STAGE = 'SET_STAGE',
  SET_LOADING = 'SET_LOADING',
  SET_ERROR = 'SET_ERROR',
  CLEAR_ERROR = 'CLEAR_ERROR',
  
  // Session actions
  SAVE_CHECKPOINT = 'SAVE_CHECKPOINT',
  RESTORE_CHECKPOINT = 'RESTORE_CHECKPOINT',
}

/**
 * Action creators
 */
export class Actions {
  static setProfile(profile: any) {
    return { type: ActionType.SET_PROFILE, payload: profile };
  }

  static addPackage(pkg: any) {
    return { type: ActionType.ADD_PACKAGE, payload: pkg };
  }

  static removePackage(pkgName: string) {
    return { type: ActionType.REMOVE_PACKAGE, payload: pkgName };
  }

  static setPackages(packages: any[]) {
    return { type: ActionType.SET_PACKAGES, payload: packages };
  }

  static setStage(stage: string) {
    return { type: ActionType.SET_STAGE, payload: stage };
  }

  static setLoading(isLoading: boolean, message?: string) {
    return { type: ActionType.SET_LOADING, payload: { isLoading, message } };
  }

  static setError(error: string) {
    return { type: ActionType.SET_ERROR, payload: error };
  }

  static clearError() {
    return { type: ActionType.CLEAR_ERROR };
  }

  static setProgress(current: number, total: number, message?: string) {
    return { type: ActionType.SET_PROGRESS, payload: { current, total, message } };
  }
}

/**
 * Reducer pattern for complex state updates
 */
export type Reducer<S, A> = (state: S, action: A) => S;

export function createReducer<S, A>(
  initialState: S,
  handlers: Record<string, (state: S, action: any) => S>
): Reducer<S, A> {
  return (state: S = initialState, action: any): S => {
    const handler = handlers[action.type];
    return handler ? handler(state, action) : state;
  };
}

/**
 * Middleware system for intercepting actions
 */
export type Middleware<S> = (store: Store<S>) => (next: Function) => (action: any) => any;

export class MiddlewareManager<S> {
  private middlewares: Middleware<S>[] = [];
  private store: Store<S>;

  constructor(store: Store<S>) {
    this.store = store;
  }

  use(middleware: Middleware<S>): void {
    this.middlewares.push(middleware);
  }

  dispatch(action: any): any {
    const chain = this.middlewares.map(mw => mw(this.store));
    const dispatch = this.compose(...chain)((action: any) => {
      // Final dispatch to store
      this.handleAction(action);
      return action;
    });
    
    return dispatch(action);
  }

  private handleAction(action: any): void {
    // This would be overridden by specific implementations
    console.log('Action dispatched:', action);
  }

  private compose(...funcs: Function[]): Function {
    if (funcs.length === 0) {
      return (arg: any) => arg;
    }
    
    if (funcs.length === 1) {
      return funcs[0];
    }
    
    return funcs.reduce((a, b) => (...args: any[]) => a(b(...args)));
  }
}

/**
 * Logger middleware for debugging
 */
export const loggerMiddleware: Middleware<any> = (store) => (next) => (action) => {
  console.group(`Action: ${action.type}`);
  console.log('Previous State:', store.getState());
  console.log('Action:', action);
  
  const result = next(action);
  
  console.log('Next State:', store.getState());
  console.groupEnd();
  
  return result;
};

/**
 * Async middleware for handling promises
 */
export const asyncMiddleware: Middleware<any> = (store) => (next) => (action) => {
  if (typeof action === 'function') {
    return action(store.dispatch, store.getState);
  }
  
  if (action.payload instanceof Promise) {
    return action.payload
      .then((result: any) => {
        next({ ...action, payload: result });
      })
      .catch((error: any) => {
        next({ type: ActionType.SET_ERROR, payload: error.message });
      });
  }
  
  return next(action);
};

/**
 * Persistence middleware for saving state
 */
export const persistenceMiddleware: Middleware<any> = (store) => (next) => (action) => {
  const result = next(action);
  
  // Save to localStorage after each action
  if (typeof window !== 'undefined' && window.localStorage) {
    try {
      window.localStorage.setItem('ceremony-state', JSON.stringify(store.getState()));
    } catch (e) {
      console.error('Failed to persist state:', e);
    }
  }
  
  return result;
};

/**
 * Component connection helper
 */
export class ComponentConnector<S, P = {}> {
  private store: Store<S>;
  private component: any;
  private unsubscribe?: () => void;
  private mapStateToProps?: (state: S) => Partial<P>;
  private mapDispatchToProps?: Record<string, Function>;

  constructor(
    store: Store<S>,
    component: any,
    mapStateToProps?: (state: S) => Partial<P>,
    mapDispatchToProps?: Record<string, Function>
  ) {
    this.store = store;
    this.component = component;
    this.mapStateToProps = mapStateToProps;
    this.mapDispatchToProps = mapDispatchToProps;
  }

  connect(): void {
    if (this.mapStateToProps) {
      this.unsubscribe = this.store.subscribe((state) => {
        const props = this.mapStateToProps!(state);
        this.component.update(props);
      });
    }

    if (this.mapDispatchToProps) {
      // Bind dispatch functions to component
      Object.entries(this.mapDispatchToProps).forEach(([key, fn]) => {
        this.component[key] = fn;
      });
    }
  }

  disconnect(): void {
    if (this.unsubscribe) {
      this.unsubscribe();
    }
  }
}

/**
 * Global state shape for Setup Ceremony
 */
export interface SetupCeremonyState {
  // Current stage
  stage: string;
  
  // Profile
  profile: {
    selected: any | null;
    settings: Record<string, any>;
  };
  
  // Packages
  packages: {
    installed: any[];
    selected: any[];
    available: any[];
    searchResults: any[];
  };
  
  // Conflicts
  conflicts: {
    active: any[];
    resolutions: Record<string, string>;
  };
  
  // Progress
  progress: {
    current: number;
    total: number;
    message: string;
  };
  
  // UI State
  ui: {
    loading: boolean;
    loadingMessage: string;
    error: string | null;
    modalOpen: boolean;
  };
  
  // Session
  session: {
    checkpoints: any[];
    startTime: number;
    completionTime?: number;
  };
}

/**
 * Create the global store
 */
export function createSetupCeremonyStore(): Store<SetupCeremonyState> {
  const initialState: SetupCeremonyState = {
    stage: 'welcome',
    profile: {
      selected: null,
      settings: {}
    },
    packages: {
      installed: [],
      selected: [],
      available: [],
      searchResults: []
    },
    conflicts: {
      active: [],
      resolutions: {}
    },
    progress: {
      current: 0,
      total: 0,
      message: ''
    },
    ui: {
      loading: false,
      loadingMessage: '',
      error: null,
      modalOpen: false
    },
    session: {
      checkpoints: [],
      startTime: Date.now(),
      completionTime: undefined
    }
  };

  // Try to restore from localStorage
  if (typeof window !== 'undefined' && window.localStorage) {
    try {
      const saved = window.localStorage.getItem('ceremony-state');
      if (saved) {
        const parsed = JSON.parse(saved);
        // Merge with initial state to ensure all fields exist
        Object.assign(initialState, parsed);
      }
    } catch (e) {
      console.error('Failed to restore state:', e);
    }
  }

  return new Store(initialState);
}

/**
 * Selectors for accessing state
 */
export class Selectors {
  static getProfile = (state: SetupCeremonyState) => state.profile.selected;
  static getSelectedPackages = (state: SetupCeremonyState) => state.packages.selected;
  static getInstalledPackages = (state: SetupCeremonyState) => state.packages.installed;
  static getCurrentStage = (state: SetupCeremonyState) => state.stage;
  static getConflicts = (state: SetupCeremonyState) => state.conflicts.active;
  static getProgress = (state: SetupCeremonyState) => state.progress;
  static isLoading = (state: SetupCeremonyState) => state.ui.loading;
  static getError = (state: SetupCeremonyState) => state.ui.error;
  
  static getPackageCount = (state: SetupCeremonyState) => 
    state.packages.selected.length;
  
  static getEstimatedSize = (state: SetupCeremonyState) => 
    state.packages.selected.reduce((sum, pkg) => sum + (pkg.size || 50), 0);
  
  static getEstimatedTime = (state: SetupCeremonyState) => 
    Math.ceil(state.packages.selected.length * 0.5);
  
  static hasConflicts = (state: SetupCeremonyState) => 
    state.conflicts.active.length > 0;
  
  static isComplete = (state: SetupCeremonyState) => 
    state.stage === 'complete';
}