export interface NodeParameter {
  name: string;
  label: string;
  type: 'str' | 'int' | 'float' | 'bool' | 'select' | 'column_select' | 'sql' | 'python';
  default: any;
  required: boolean;
  options?: string[];
  description?: string;
}

export interface PortMetadata {
  name: string;
  label: string;
  type: string;
}

export interface NodeMetadata {
  type: string;
  name: string;
  category: 'Readers' | 'Writers' | 'Transformations' | 'GIS' | 'Network Analysis' | 'Quality';
  description: string;
  parameters: NodeParameter[];
  inputs: PortMetadata[];
  outputs: PortMetadata[];
}

export interface CustomNodeCreateInput {
  type: string;
  name: string;
  category: string;
  description: string;
  code: string;
  parameters: Omit<NodeParameter, 'default' | 'options'>[];
}

export interface Log {
  id: string;
  node_key: string | null;
  log_level: 'INFO' | 'WARNING' | 'ERROR' | 'DEBUG';
  message: string;
  timestamp: string;
}

export interface Execution {
  id: string;
  workflow_id: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
  started_at: string;
  completed_at: string | null;
  triggered_by: string | null;
  logs?: Log[];
}

export interface WorkflowNode {
  id: string;
  node_key: string;
  type: string;
  config: Record<string, any>;
  pos_x: number;
  pos_y: number;
}

export interface WorkflowEdge {
  source_node: string;
  target_node: string;
  source_handle: string;
  target_handle: string;
}

export interface Workflow {
  id: string;
  name: string;
  description: string | null;
  version: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}
