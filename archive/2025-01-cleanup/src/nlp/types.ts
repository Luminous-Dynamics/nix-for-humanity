// Core NLP types

export interface Intent {
  action: IntentAction;
  entities: Entity[];
  confidence: number;
  rawInput: string;
}

export type IntentAction = 
  | 'install_package'
  | 'remove_package'
  | 'update_system'
  | 'search_packages'
  | 'get_help'
  | 'troubleshoot'
  | 'query_info'
  | 'configure'
  | 'unknown';

export interface Entity {
  type: EntityType;
  value: string;
  confidence: number;
  startIndex?: number;
  endIndex?: number;
}

export type EntityType = 
  | 'package'
  | 'service'
  | 'config_option'
  | 'file_path'
  | 'number'
  | 'duration';

export interface Context {
  previousIntents: Intent[];
  lastEntities: Map<string, Entity>;
  conversationId: string;
  timestamp: number;
}

export interface NLPResult extends Intent {
  processingTime: number;
  engine: 'rule-based' | 'statistical' | 'neural';
  suggestions?: string[];
  needsClarification?: boolean;
  clarificationPrompt?: string;
}

export interface Pattern {
  pattern: RegExp | string;
  intent: IntentAction;
  entities?: string[];
  confidence: number;
}

// Response types
export interface Response {
  message: string;
  action?: SystemAction;
  visualization?: Visualization;
  audioResponse?: AudioResponse;
}

export interface SystemAction {
  type: 'execute' | 'confirm' | 'preview';
  command?: string;
  requiresConfirmation?: boolean;
}

export interface Visualization {
  type: 'progress' | 'result' | 'error' | 'info';
  data: any;
}

export interface AudioResponse {
  text: string;
  priority: 'high' | 'normal' | 'low';
}