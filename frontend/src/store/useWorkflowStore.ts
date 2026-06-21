import { create } from 'zustand';
import { Connection, Edge, Node, addEdge } from 'reactflow';
import { NodeMetadata, Workflow, Execution, Log } from '../types';

interface WorkflowState {
  nodes: Node[];
  edges: Edge[];
  nodeMetadataList: NodeMetadata[];
  selectedNodeId: string | null;
  workflowId: string | null;
  workflowName: string;
  workflowDesc: string;
  isExecuting: boolean;
  activeExecution: Execution | null;
  
  // Actions
  fetchNodeMetadata: () => Promise<void>;
  setNodes: (nodes: Node[]) => void;
  setEdges: (edges: Edge[]) => void;
  onConnect: (connection: Connection) => void;
  addNode: (type: string, position: { x: number; y: number }) => void;
  deleteNode: (id: string) => void;
  selectNode: (id: string | null) => void;
  updateNodeConfig: (id: string, config: Record<string, any>) => void;
  updateNodePorts: (id: string, inputs: any[], outputs: any[]) => void;
  setWorkflowName: (name: string) => void;
  setWorkflowDesc: (desc: string) => void;
  
  // Workflows REST
  loadWorkflow: (id: string) => Promise<void>;
  saveWorkflow: () => Promise<string>;
  
  // Executions REST
  runWorkflow: () => Promise<void>;
  pollExecution: (executionId: string) => Promise<void>;
}

const API_BASE = '/api';

// Helper to construct authorization header (Mock token for simplicity, change in prod)
const getHeaders = () => {
  const token = localStorage.getItem('token') || '';
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
};

export const useWorkflowStore = create<WorkflowState>((set, get) => ({
  nodes: [],
  edges: [],
  nodeMetadataList: [],
  selectedNodeId: null,
  workflowId: null,
  workflowName: "Unnamed Spatial ETL",
  workflowDesc: "Geospatial workflow process",
  isExecuting: false,
  activeExecution: null,

  fetchNodeMetadata: async () => {
    try {
      const res = await fetch(`${API_BASE}/nodes`, { headers: getHeaders() });
      if (res.ok) {
        const data = await res.json();
        set({ nodeMetadataList: data });
      }
    } catch (err) {
      console.error("Failed to fetch node metadata:", err);
    }
  },

  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  setWorkflowName: (name) => set({ workflowName: name }),
  setWorkflowDesc: (desc) => set({ workflowDesc: desc }),

  onConnect: (connection) => {
    set((state) => ({
      edges: addEdge({ 
        ...connection, 
        animated: true, 
        style: { stroke: '#6366f1', strokeWidth: 2 } 
      }, state.edges)
    }));
  },

  addNode: (type, position) => {
    const { nodeMetadataList, nodes } = get();
    const meta = nodeMetadataList.find(m => m.type === type);
    if (!meta) return;

    // Create default configuration mapping
    const defaultConfig: Record<string, any> = {};
    meta.parameters.forEach(p => {
      defaultConfig[p.name] = p.default;
    });

    const nodeId = `${type.toLowerCase()}_${Date.now()}`;
    const newNode: Node = {
      id: nodeId,
      type: 'customNode',
      position,
      data: {
        label: meta.name,
        type: meta.type,
        category: meta.category,
        description: meta.description,
        config: defaultConfig,
        parameters: meta.parameters,
        inputs: meta.inputs,
        outputs: meta.outputs
      }
    };

    set({ nodes: [...nodes, newNode], selectedNodeId: nodeId });
  },

  deleteNode: (id) => {
    set((state) => ({
      nodes: state.nodes.filter(n => n.id !== id),
      edges: state.edges.filter(e => e.source !== id && e.target !== id),
      selectedNodeId: state.selectedNodeId === id ? null : state.selectedNodeId
    }));
  },

  selectNode: (id) => set({ selectedNodeId: id }),

  updateNodeConfig: (id, config) => {
    set((state) => ({
      nodes: state.nodes.map(node => {
        if (node.id === id) {
          return {
            ...node,
            data: {
              ...node.data,
              config: { ...node.data.config, ...config }
            }
          };
        }
        return node;
      })
    }));
  },

  updateNodePorts: (id, inputs, outputs) => {
    set((state) => ({
      nodes: state.nodes.map(node => {
        if (node.id === id) {
          return {
            ...node,
            data: {
              ...node.data,
              inputs,
              outputs
            }
          };
        }
        return node;
      })
    }));
  },

  loadWorkflow: async (id) => {
    try {
      const res = await fetch(`${API_BASE}/workflows/${id}`, { headers: getHeaders() });
      if (!res.ok) throw new Error("Workflow not found.");
      const workflow: Workflow = await res.json();
      
      // Parse database nodes to React Flow format
      const canvasNodes: Node[] = workflow.nodes.map(n => {
        const meta = get().nodeMetadataList.find(m => m.type === n.type);
        return {
          id: n.node_key,
          type: 'customNode',
          position: { x: n.pos_x, y: n.pos_y },
          data: {
            label: meta?.name || n.type,
            type: n.type,
            category: meta?.category || 'Transformations',
            description: meta?.description || '',
            config: n.config,
            parameters: meta?.parameters || [],
            inputs: meta?.inputs || [],
            outputs: meta?.outputs || []
          }
        };
      });

      // Parse database edges to React Flow format
      const canvasEdges: Edge[] = workflow.edges.map(e => ({
        id: `e_${e.source_node}_${e.target_node}`,
        source: e.source_node,
        target: e.target_node,
        sourceHandle: e.source_handle,
        targetHandle: e.target_handle,
        animated: true,
        style: { stroke: '#6366f1', strokeWidth: 2 }
      }));

      set({
        workflowId: workflow.id,
        workflowName: workflow.name,
        workflowDesc: workflow.description || '',
        nodes: canvasNodes,
        edges: canvasEdges
      });
    } catch (err) {
      console.error("Load workflow failed:", err);
    }
  },

  saveWorkflow: async () => {
    const { workflowId, workflowName, workflowDesc, nodes, edges } = get();
    
    // Construct database schema format payloads
    const payload = {
      name: workflowName,
      description: workflowDesc,
      version: 1,
      nodes: nodes.map(n => ({
        node_key: n.id,
        type: n.data.type,
        config: n.data.config,
        pos_x: n.position.x,
        pos_y: n.position.y
      })),
      edges: edges.map(e => ({
        source_node: e.source,
        target_node: e.target,
        source_handle: e.sourceHandle || 'output',
        target_handle: e.targetHandle || 'input'
      }))
    };

    const method = workflowId ? 'PUT' : 'POST';
    const url = workflowId ? `${API_BASE}/workflows/${workflowId}` : `${API_BASE}/workflows`;

    try {
      const res = await fetch(url, {
        method,
        headers: getHeaders(),
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error("Save workflow failed.");
      const data = await res.json();
      set({ workflowId: data.id });
      return data.id;
    } catch (err) {
      console.error("Save workflow error:", err);
      throw err;
    }
  },

  runWorkflow: async () => {
    // 1. Ensure latest workspace configuration is saved
    let currentId = get().workflowId;
    if (!currentId) {
      currentId = await get().saveWorkflow();
    } else {
      await get().saveWorkflow();
    }

    set({ isExecuting: true, activeExecution: null });
    
    try {
      const runRes = await fetch(`${API_BASE}/executions/run/${currentId}`, {
        method: 'POST',
        headers: getHeaders()
      });
      if (!runRes.ok) throw new Error("Execution trigger failed.");
      const execution: Execution = await runRes.json();
      set({ activeExecution: execution });
      
      // Start polling
      get().pollExecution(execution.id);
    } catch (err) {
      console.error("Execution failed:", err);
      set({ isExecuting: false });
    }
  },

  pollExecution: async (executionId) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/executions/${executionId}`, { headers: getHeaders() });
        if (!res.ok) return;
        const execution: Execution = await res.json();
        
        set({ activeExecution: execution });
        
        if (execution.status === 'COMPLETED' || execution.status === 'FAILED') {
          clearInterval(interval);
          set({ isExecuting: false });
        }
      } catch (err) {
        console.error("Poll execution error:", err);
        clearInterval(interval);
        set({ isExecuting: false });
      }
    }, 1500);
  }
}));
