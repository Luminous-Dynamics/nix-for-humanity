/**
 * WebSocket Client for Real-time Nix Execution
 * Connects frontend to backend with progress tracking
 */
export interface CommandExecution {
    sessionId: string;
    command: any;
    status: 'pending' | 'running' | 'success' | 'error';
    progress?: number;
    message?: string;
    result?: any;
    error?: string;
}
export declare class NixWebSocketClient {
    private serverUrl;
    private socket;
    private connected;
    private executions;
    private eventHandlers;
    constructor(serverUrl?: string);
    /**
     * Connect to WebSocket server
     */
    connect(): Promise<void>;
    /**
     * Setup WebSocket event handlers
     */
    private setupEventHandlers;
    /**
     * Execute a Nix command
     */
    executeCommand(command: any): Promise<CommandExecution>;
    /**
     * Search for packages
     */
    searchPackages(query: string): Promise<any[]>;
    /**
     * Request rollback
     */
    rollback(generation: number): Promise<boolean>;
    /**
     * Simulate execution in demo mode
     */
    private simulateExecution;
    /**
     * Simulate package search
     */
    private simulateSearch;
    /**
     * Event handling
     */
    on(event: string, handler: Function): void;
    off(event: string, handler: Function): void;
    private emit;
    /**
     * Generate unique session ID
     */
    private generateSessionId;
    /**
     * Get connection status
     */
    isConnected(): boolean;
    /**
     * Disconnect from server
     */
    disconnect(): void;
}
export declare const nixClient: NixWebSocketClient;
