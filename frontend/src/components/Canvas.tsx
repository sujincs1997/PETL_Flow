import React, { useRef, useCallback, useEffect } from 'react';
import { useReactFlow } from 'reactflow';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  BackgroundVariant,
  Node,
  Edge,
  applyNodeChanges,
  applyEdgeChanges,
  NodeChange,
  EdgeChange
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Box } from '@mui/material';
import { useWorkflowStore } from '../store/useWorkflowStore';
import BaseCanvasNode from './nodes/BaseCanvasNode';

// Define nodeTypes OUTSIDE the component to avoid re-registration on every render
const nodeTypes = {
  customNode: BaseCanvasNode,
};

export const Canvas: React.FC = () => {
  const { screenToFlowPosition } = useReactFlow();
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  
  const nodes = useWorkflowStore((state) => state.nodes);
  const edges = useWorkflowStore((state) => state.edges);
  const setNodes = useWorkflowStore((state) => state.setNodes);
  const setEdges = useWorkflowStore((state) => state.setEdges);
  const onConnect = useWorkflowStore((state) => state.onConnect);
  const addNode = useWorkflowStore((state) => state.addNode);
  const selectNode = useWorkflowStore((state) => state.selectNode);
  const fetchNodeMetadata = useWorkflowStore((state) => state.fetchNodeMetadata);

  // Fetch registered node categories at component mount
  useEffect(() => {
    fetchNodeMetadata();
  }, [fetchNodeMetadata]);

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      if (!reactFlowWrapper.current) return;

      const type = event.dataTransfer.getData('application/reactflow');
      if (!type) return;

      // screenToFlowPosition converts raw client (screen) coordinates to canvas space
      const position = screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      console.log('[Canvas] Dropping node type:', type, 'at position:', position);
      addNode(type, position);
    },
    [addNode, screenToFlowPosition]
  );

  const onNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      selectNode(node.id);
    },
    [selectNode]
  );

  const onPaneClick = useCallback(() => {
    selectNode(null);
  }, [selectNode]);

  // ✅ CRITICAL: Use applyNodeChanges so React Flow's internal engine stays in sync
  // Without this, nodes added to the Zustand store won't render on the canvas
  const onNodesChange = useCallback(
    (changes: NodeChange[]) => {
      setNodes(applyNodeChanges(changes, nodes));
    },
    [nodes, setNodes]
  );

  // ✅ Use applyEdgeChanges for consistent edge handling
  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => {
      setEdges(applyEdgeChanges(changes, edges));
    },
    [edges, setEdges]
  );

  return (
    <Box 
      ref={reactFlowWrapper} 
      sx={{ 
        flexGrow: 1, 
        height: '100%', 
        position: 'relative',
        backgroundColor: '#f8fafc' 
      }}
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        deleteKeyCode="Delete"
        defaultEdgeOptions={{
          animated: true,
          style: { stroke: '#6366f1', strokeWidth: 2 },
        }}
      >
        <Background variant={BackgroundVariant.Dots} gap={16} size={1} color="#cbd5e1" />
        <Controls showInteractive={false} style={{ bottom: 10, left: 10 }} />
        <MiniMap 
          style={{ bottom: 10, right: 10, width: 120, height: 80 }} 
          nodeColor={(n) => {
            if (n.data.category === 'Readers') return '#10b981';
            if (n.data.category === 'Writers') return '#f43f5e';
            if (n.data.category === 'GIS') return '#f59e0b';
            return '#6366f1';
          }}
        />
      </ReactFlow>
    </Box>
  );
};
export default Canvas;
