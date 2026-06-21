import React, { useState } from 'react';
import { 
  Box, Typography, TextField, FormControlLabel, Switch, 
  MenuItem, Divider, Paper, Stack, Button
} from '@mui/material';
import { FindInPage as InspectorIcon } from '@mui/icons-material';
import { useWorkflowStore } from '../store/useWorkflowStore';
import InspectorResultsModal from './InspectorResultsModal';

export const PropertiesPanel: React.FC = () => {
  const selectedNodeId = useWorkflowStore((state) => state.selectedNodeId);
  const nodes = useWorkflowStore((state) => state.nodes);
  const updateNodeConfig = useWorkflowStore((state) => state.updateNodeConfig);
  const activeExecution = useWorkflowStore((state) => state.activeExecution);

  const [inspectorModalOpen, setInspectorModalOpen] = useState(false);

  const selectedNode = nodes.find(node => node.id === selectedNodeId);

  if (!selectedNode) {
    return (
      <Box 
        sx={{ 
          width: 320, 
          borderLeft: '1px solid #e2e8f0', 
          backgroundColor: '#f8fafc',
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          p: 3,
          textAlign: 'center'
        }}
      >
        <Typography variant="body2" color="text.secondary">
          Select a processor on the canvas to configure parameters.
        </Typography>
      </Box>
    );
  }

  const { label, type, category, description, config, parameters } = selectedNode.data;
  const isInspectorNode = type === 'InspectorNode';

  const handleChange = (paramName: string, value: any) => {
    updateNodeConfig(selectedNode.id, { [paramName]: value });
  };

  return (
    <Box 
      sx={{ 
        width: 320, 
        borderLeft: '1px solid #e2e8f0', 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        backgroundColor: '#ffffff'
      }}
    >
      <Box sx={{ p: 2.5 }}>
        <Typography variant="subtitle2" color="text.secondary" sx={{ textTransform: 'uppercase', fontSize: '10px', fontWeight: 700, letterSpacing: 0.8 }}>
          Configuration Panel
        </Typography>
        <Typography variant="h6" sx={{ fontWeight: 800, mt: 0.5, color: '#0f172a' }}>
          {label}
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
          Type: <code>{type}</code> | Category: {category}
        </Typography>
        {description && (
          <Typography variant="caption" sx={{ display: 'block', mt: 1.5, color: '#475569', backgroundColor: '#f8fafc', p: 1, borderRadius: 1.5 }}>
            {description}
          </Typography>
        )}
      </Box>

      <Divider />

      <Box sx={{ flexGrow: 1, overflowY: 'auto', p: 2.5 }}>
        <Stack spacing={2.5}>
          {parameters && parameters.length > 0 ? (
            parameters.map((param: any) => {
              const currentValue = config[param.name] !== undefined ? config[param.name] : param.default;

              if (param.type === 'bool') {
                return (
                  <FormControlLabel
                    key={param.name}
                    control={
                      <Switch
                        checked={!!currentValue}
                        onChange={(e) => handleChange(param.name, e.target.checked)}
                        color="primary"
                      />
                    }
                    label={
                      <Box>
                        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>{param.label}</Typography>
                        {param.description && <Typography variant="caption" color="text.secondary">{param.description}</Typography>}
                      </Box>
                    }
                  />
                );
              }

              if (param.type === 'select') {
                return (
                  <TextField
                    key={param.name}
                    select
                    label={param.label}
                    value={currentValue || ''}
                    onChange={(e) => handleChange(param.name, e.target.value)}
                    fullWidth
                    size="small"
                    helperText={param.description}
                  >
                    {param.options?.map((opt: string) => (
                      <MenuItem key={opt} value={opt}>
                        {opt}
                      </MenuItem>
                    ))}
                  </TextField>
                );
              }

              // SQL or Python Code Block
              if (param.type === 'sql' || param.type === 'python') {
                return (
                  <TextField
                    key={param.name}
                    label={param.label}
                    value={currentValue || ''}
                    onChange={(e) => handleChange(param.name, e.target.value)}
                    multiline
                    rows={8}
                    fullWidth
                    size="small"
                    helperText={param.description}
                    InputProps={{
                      style: { fontFamily: 'monospace', fontSize: '12px' }
                    }}
                  />
                );
              }

              // Standard Input text/number fields
              return (
                <TextField
                  key={param.name}
                  label={param.label}
                  type={param.type === 'int' || param.type === 'float' ? 'number' : 'text'}
                  value={currentValue !== null && currentValue !== undefined ? currentValue : ''}
                  onChange={(e) => {
                    let val: any = e.target.value;
                    if (param.type === 'int') val = parseInt(val) || 0;
                    else if (param.type === 'float') val = parseFloat(val) || 0.0;
                    handleChange(param.name, val);
                  }}
                  fullWidth
                  size="small"
                  helperText={param.description}
                />
              );
            })
          ) : (
            <Typography variant="caption" color="text.secondary">
              This node has no configurable parameters.
            </Typography>
          )}

          {/* Inspector Node: View Report Button */}
          {isInspectorNode && (
            <Box sx={{ mt: 1 }}>
              <Divider sx={{ mb: 2 }} />
              <Button
                variant="contained"
                startIcon={<InspectorIcon />}
                onClick={() => setInspectorModalOpen(true)}
                fullWidth
                sx={{
                  borderRadius: 2,
                  textTransform: 'none',
                  fontWeight: 700,
                  backgroundColor: '#0891b2',
                  '&:hover': { backgroundColor: '#0e7490' },
                  py: 1.2
                }}
              >
                View Inspection Report
              </Button>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1, textAlign: 'center' }}>
                {activeExecution?.status === 'COMPLETED'
                  ? 'Report available from last execution'
                  : 'Execute the pipeline to generate a report'}
              </Typography>
            </Box>
          )}
          {/* Port Management for Python Script Node */}
          {type === 'PythonScriptNode' && (
            <Box sx={{ mt: 2 }}>
              <Divider sx={{ mb: 2 }} />
              <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1.5, color: '#0f172a' }}>
                Port Management
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="caption" sx={{ fontWeight: 600, color: '#475569', display: 'block', mb: 1 }}>Input Ports</Typography>
                <Stack spacing={1}>
                  {selectedNode.data.inputs?.map((input: any, idx: number) => (
                    <Box key={idx} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', backgroundColor: '#f1f5f9', p: 0.8, borderRadius: 1 }}>
                      <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>{input.name}</Typography>
                      <Button size="small" color="error" sx={{ minWidth: 'auto', p: 0.2 }} onClick={() => {
                        const newInputs = selectedNode.data.inputs.filter((_: any, i: number) => i !== idx);
                        useWorkflowStore.getState().updateNodePorts(selectedNode.id, newInputs, selectedNode.data.outputs || []);
                      }}>X</Button>
                    </Box>
                  ))}
                  <Button 
                    variant="outlined" 
                    size="small" 
                    sx={{ textTransform: 'none', fontSize: '10px' }}
                    onClick={() => {
                      const name = prompt("Enter input port name:");
                      if (name) {
                        const newInputs = [...(selectedNode.data.inputs || []), { name, label: name, type: 'any' }];
                        useWorkflowStore.getState().updateNodePorts(selectedNode.id, newInputs, selectedNode.data.outputs || []);
                      }
                    }}
                  >
                    + Add Input Port
                  </Button>
                </Stack>
              </Box>

              <Box>
                <Typography variant="caption" sx={{ fontWeight: 600, color: '#475569', display: 'block', mb: 1 }}>Output Ports</Typography>
                <Stack spacing={1}>
                  {selectedNode.data.outputs?.map((output: any, idx: number) => (
                    <Box key={idx} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', backgroundColor: '#f1f5f9', p: 0.8, borderRadius: 1 }}>
                      <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>{output.name}</Typography>
                      <Button size="small" color="error" sx={{ minWidth: 'auto', p: 0.2 }} onClick={() => {
                        const newOutputs = selectedNode.data.outputs.filter((_: any, i: number) => i !== idx);
                        useWorkflowStore.getState().updateNodePorts(selectedNode.id, selectedNode.data.inputs || [], newOutputs);
                      }}>X</Button>
                    </Box>
                  ))}
                  <Button 
                    variant="outlined" 
                    size="small" 
                    sx={{ textTransform: 'none', fontSize: '10px' }}
                    onClick={() => {
                      const name = prompt("Enter output port name:");
                      if (name) {
                        const newOutputs = [...(selectedNode.data.outputs || []), { name, label: name, type: 'any' }];
                        useWorkflowStore.getState().updateNodePorts(selectedNode.id, selectedNode.data.inputs || [], newOutputs);
                      }
                    }}
                  >
                    + Add Output Port
                  </Button>
                </Stack>
              </Box>
            </Box>
          )}
        </Stack>
      </Box>

      {/* Inspector Results Modal */}
      {isInspectorNode && (
        <InspectorResultsModal
          open={inspectorModalOpen}
          onClose={() => setInspectorModalOpen(false)}
          executionId={activeExecution?.id || null}
          nodeKey={selectedNode.id}
        />
      )}
    </Box>
  );
};
export default PropertiesPanel;
