export type AgentStatus = 
  | 'idle' 
  | 'requirements' 
  | 'architecture' 
  | 'boilerplate' 
  | 'code_writing' 
  | 'syntax_analysis'
  | 'analysis'
  | 'complete' 
  | 'error';

export interface WorkflowStep {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'in-progress' | 'completed' | 'error';
  output?: string;
  error?: string;
  timestamp?: number;
}

export interface StreamMessage {
  type: 'agent_start' | 'agent_end' | 'file_start' | 'file_end' | 'code_token' | 'status' | 'complete' | 'error';
  agent?: string;
  file?: 'backend' | 'frontend';
  message?: string;
  token?: string;
  data?: Record<string, unknown>;
  syntax_valid?: boolean;
  syntax_error?: string | null;
  error?: string;
}

export interface GenerationResult {
  requirements: string;
  architecture: string;
  boilerplate: string;
  code: string;
  backend_code?: string;
  frontend_code?: string;
  syntax_valid?: boolean;
  syntax_error?: string | null;
  report: string;
}
