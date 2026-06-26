import React, { useRef } from 'react';
import { 
  Box, Typography, Button, Stack, AppBar, Toolbar, 
  IconButton, Tooltip, Input, Dialog, DialogTitle, 
  DialogContent, DialogActions, TextField, FormControlLabel, Switch
} from '@mui/material';
import { 
  PlayArrow as PlayIcon, 
  Save as SaveIcon, 
  FileDownload as ExportIcon, 
  FileUpload as ImportIcon,
  Map as MapIcon,
  CloudDownload as LoadIcon,
  Edit as EditIcon,
  Logout as LogoutIcon
} from '@mui/icons-material';
import { useWorkflowStore } from '../store/useWorkflowStore';
import LoadWorkflowModal from './LoadWorkflowModal';

export const Header: React.FC = () => {
  const workflowName = useWorkflowStore((state) => state.workflowName);
  const workflowDesc = useWorkflowStore((state) => state.workflowDesc);
  const setWorkflowName = useWorkflowStore((state) => state.setWorkflowName);
  const setWorkflowDesc = useWorkflowStore((state) => state.setWorkflowDesc);
  const runWorkflow = useWorkflowStore((state) => state.runWorkflow);
  const saveWorkflow = useWorkflowStore((state) => state.saveWorkflow);
  const isExecuting = useWorkflowStore((state) => state.isExecuting);
  const debugMode = useWorkflowStore((state) => state.debugMode);
  const setDebugMode = useWorkflowStore((state) => state.setDebugMode);
  
  const nodes = useWorkflowStore((state) => state.nodes);
  const edges = useWorkflowStore((state) => state.edges);
  const setNodes = useWorkflowStore((state) => state.setNodes);
  const setEdges = useWorkflowStore((state) => state.setEdges);
  const nodeMetadataList = useWorkflowStore((state) => state.nodeMetadataList);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isLoadModalOpen, setIsLoadModalOpen] = React.useState(false);
  const [isEditDetailsOpen, setIsEditDetailsOpen] = React.useState(false);
  const [editName, setEditName] = React.useState('');
  const [editDesc, setEditDesc] = React.useState('');

  const openEditDetails = () => {
    setEditName(workflowName);
    setEditDesc(workflowDesc);
    setIsEditDetailsOpen(true);
  };

  const handleSaveDetails = () => {
    setWorkflowName(editName);
    setWorkflowDesc(editDesc);
    setIsEditDetailsOpen(false);
  };

  const handleExport = async () => {
    const payload = {
      name: workflowName,
      description: workflowDesc,
      nodes: nodes.map(n => ({
        id: n.id,
        type: n.data.type,
        config: n.data.config,
        position: n.position
      })),
      edges: edges.map(e => ({
        source: e.source,
        target: e.target,
        sourceHandle: e.sourceHandle,
        targetHandle: e.targetHandle
      }))
    };

    const suggestedName = `${workflowName.toLowerCase().replace(/\s+/g, '_')}_workflow.json`;
    const dataStr = JSON.stringify(payload, null, 2);

    try {
      if ('showSaveFilePicker' in window) {
        // Modern approach: lets user pick the exact directory
        const handle = await (window as any).showSaveFilePicker({
          suggestedName,
          types: [{
            description: 'JSON Files',
            accept: { 'application/json': ['.json'] },
          }],
        });
        const writable = await handle.createWritable();
        await writable.write(dataStr);
        await writable.close();
        return; // Success
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        alert("Export failed: " + err.message);
      }
      return; // If aborted, do nothing; if error, alerted and stop.
    }

    // Fallback for browsers that don't support File System API
    const uri = "data:text/json;charset=utf-8," + encodeURIComponent(dataStr);
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", uri);
    downloadAnchor.setAttribute("download", suggestedName);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const handleImportClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleImportFile = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target?.result as string);
        
        // Convert back to React Flow nodes format
        const parsedNodes = json.nodes.map((n: any) => {
          const meta = nodeMetadataList.find(m => m.type === n.type);
          return {
            id: n.id,
            type: 'customNode',
            position: n.position || { x: 100, y: 100 },
            data: {
              label: meta?.name || n.type,
              type: n.type,
              category: meta?.category || 'Transformations',
              description: meta?.description || '',
              config: n.config || {},
              parameters: meta?.parameters || [],
              inputs: meta?.inputs || [],
              outputs: meta?.outputs || []
            }
          };
        });

        // Convert back to React Flow edges format
        const parsedEdges = json.edges.map((e: any) => ({
          id: `e_${e.source}_${e.target}`,
          source: e.source,
          target: e.target,
          sourceHandle: e.sourceHandle || 'output',
          targetHandle: e.targetHandle || 'input',
          animated: true,
          style: { stroke: '#6366f1', strokeWidth: 2 }
        }));

        setNodes(parsedNodes);
        setEdges(parsedEdges);
        alert("Workflow imported successfully onto canvas!");
      } catch (err) {
        alert("Failed to parse JSON file. Ensure it is a valid visual ETL export.");
      }
    };
    reader.readAsText(file);
  };

  return (
    <AppBar position="static" color="default" elevation={0} sx={{ borderBottom: '1px solid #e2e8f0', backgroundColor: '#ffffff' }}>
      <Toolbar sx={{ justifyContent: 'space-between', px: 3 }}>
        {/* Left Brand Details */}
        <Stack direction="row" alignItems="center" spacing={1.5}>
          <Box 
            sx={{ 
              p: 0.8, 
              borderRadius: 2, 
              backgroundColor: '#6366f1', 
              color: '#ffffff',
              display: 'flex'
            }}
          >
            <MapIcon />
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box>
              <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#0f172a', lineHeight: 1.2 }}>
                {workflowName}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {workflowDesc}
              </Typography>
            </Box>
            <IconButton size="small" onClick={openEditDetails}>
              <EditIcon fontSize="small" sx={{ color: '#94a3b8' }} />
            </IconButton>
          </Box>
        </Stack>

        {/* Right Actions Trigger */}
        <Stack direction="row" spacing={1.5}>
          <Input 
            type="file" 
            inputRef={fileInputRef} 
            onChange={handleImportFile} 
            sx={{ display: 'none' }} 
            inputProps={{ accept: '.json' }} 
          />
          
          <Tooltip title="Import JSON config">
            <Button 
              size="small"
              variant="outlined" 
              startIcon={<ImportIcon />} 
              onClick={handleImportClick}
              sx={{ textTransform: 'none', fontWeight: 600, borderRadius: 2 }}
            >
              Import
            </Button>
          </Tooltip>

          <Tooltip title="Export JSON config">
            <Button 
              size="small"
              variant="outlined" 
              startIcon={<ExportIcon />} 
              onClick={handleExport}
              sx={{ textTransform: 'none', fontWeight: 600, borderRadius: 2 }}
            >
              Export
            </Button>
          </Tooltip>

          <Button 
            size="small"
            variant="outlined" 
            startIcon={<LoadIcon />} 
            onClick={() => setIsLoadModalOpen(true)}
            sx={{ textTransform: 'none', fontWeight: 600, borderRadius: 2 }}
          >
            Load Pipeline
          </Button>

          <Button 
            size="small"
            variant="outlined" 
            startIcon={<SaveIcon />} 
            onClick={async () => {
              try {
                await saveWorkflow();
                alert("Pipeline saved successfully!");
              } catch (err: any) {
                alert("Failed to save pipeline: " + err.message);
              }
            }}
            sx={{ textTransform: 'none', fontWeight: 600, borderRadius: 2 }}
          >
            Save Pipeline
          </Button>

          <FormControlLabel
            control={
              <Switch
                size="small"
                checked={debugMode}
                onChange={(e) => setDebugMode(e.target.checked)}
                color="secondary"
              />
            }
            label={
              <Typography variant="body2" sx={{ fontWeight: 600, color: '#64748b' }}>
                Cache to Disk
              </Typography>
            }
            sx={{ mr: 1, ml: 1 }}
          />

          <Button 
            size="small"
            variant="contained" 
            color="success" 
            startIcon={<PlayIcon />} 
            onClick={runWorkflow}
            disabled={isExecuting}
            sx={{ 
              textTransform: 'none', 
              fontWeight: 700, 
              borderRadius: 2,
              backgroundColor: '#10b981',
              '&:hover': {
                backgroundColor: '#059669'
              }
            }}
          >
            {isExecuting ? 'Running...' : 'Execute DAG'}
          </Button>

          <Button
            size="small"
            variant="outlined"
            color="error"
            startIcon={<LogoutIcon />}
            onClick={() => {
              localStorage.removeItem('token');
              window.location.reload();
            }}
            sx={{ textTransform: 'none', fontWeight: 600, borderRadius: 2 }}
          >
            Logout
          </Button>
        </Stack>
      </Toolbar>

      <LoadWorkflowModal open={isLoadModalOpen} onClose={() => setIsLoadModalOpen(false)} />
      
      <Dialog open={isEditDetailsOpen} onClose={() => setIsEditDetailsOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>Edit Pipeline Details</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          <TextField 
            label="Pipeline Name" 
            variant="outlined" 
            fullWidth 
            value={editName}
            onChange={(e) => setEditName(e.target.value)}
          />
          <TextField 
            label="Description" 
            variant="outlined" 
            fullWidth 
            multiline
            rows={2}
            value={editDesc}
            onChange={(e) => setEditDesc(e.target.value)}
          />
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setIsEditDetailsOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveDetails}>Save</Button>
        </DialogActions>
      </Dialog>
    </AppBar>
  );
};
export default Header;
