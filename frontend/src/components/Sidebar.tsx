import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, TextField, List, ListItem, ListItemIcon, 
  ListItemText, Divider, Accordion, AccordionSummary, AccordionDetails,
  Button, Modal, Card, CardContent, Grid, MenuItem, IconButton
} from '@mui/material';
import { 
  ExpandMore as ExpandMoreIcon,
  Search as SearchIcon,
  Add as AddIcon,
  Code as CodeIcon,
  Input as InputIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { useWorkflowStore } from '../store/useWorkflowStore';
import { NodeMetadata } from '../types';

export const Sidebar: React.FC = () => {
  const nodeMetadataList = useWorkflowStore((state) => state.nodeMetadataList);
  const fetchNodeMetadata = useWorkflowStore((state) => state.fetchNodeMetadata);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Custom Node Builder state
  useEffect(() => {
    fetchNodeMetadata();
  }, [fetchNodeMetadata]);
  const [openBuilder, setOpenBuilder] = useState(false);
  const [customType, setCustomType] = useState('');
  const [customName, setCustomName] = useState('');
  const [customCategory, setCustomCategory] = useState('Transformations');
  const [customDesc, setCustomDesc] = useState('');
  const [customCode, setCustomCode] = useState(
    '# Read from inputs_dict, write to outputs_dict\n# Example: outputs_dict["output"] = inputs_dict["input"].copy()\n'
  );
  
  const [parameters, setParameters] = useState<Array<{ name: string; label: string; type: string; required: boolean }>>([]);
  const [customInputs, setCustomInputs] = useState<string[]>(['input']);
  const [customOutputs, setCustomOutputs] = useState<string[]>(['output']);

  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  const handleAddParam = () => {
    setParameters([...parameters, { name: '', label: '', type: 'str', required: true }]);
  };

  const handleRemoveParam = (index: number) => {
    setParameters(parameters.filter((_, i) => i !== index));
  };

  const handleParamChange = (index: number, key: string, val: any) => {
    const updated = [...parameters];
    updated[index] = { ...updated[index], [key]: val };
    setParameters(updated);
  };

  const handleSubmitCustomNode = async () => {
    const payload = {
      type: customType.replace(/\s+/g, ''), // remove whitespace
      name: customName,
      category: customCategory,
      description: customDesc,
      code: customCode,
      parameters: parameters.map(p => ({
        name: p.name,
        label: p.label || p.name,
        type: p.type,
        required: p.required
      })),
      inputs: customInputs.filter(Boolean),
      outputs: customOutputs.filter(Boolean)
    };

    try {
      const res = await fetch('/api/nodes/custom', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
        },
        body: JSON.stringify(payload)
      });
      
      const resData = await res.json();
      if (!res.ok) {
        alert(`Error: ${resData.detail}`);
      } else {
        alert("Custom node compiled and registered successfully!");
        setOpenBuilder(false);
        // Reset form
        setCustomType('');
        setCustomName('');
        setCustomDesc('');
        setParameters([]);
        setCustomInputs(['input']);
        setCustomOutputs(['output']);
        fetchNodeMetadata();
      }
    } catch (err) {
      console.error(err);
      alert("Failed to submit custom node.");
    }
  };

  // Group nodes by category
  const categories: Record<string, NodeMetadata[]> = {};
  nodeMetadataList
    .filter(meta => meta.name.toLowerCase().includes(searchTerm.toLowerCase()))
    .forEach(meta => {
      if (!categories[meta.category]) {
        categories[meta.category] = [];
      }
      categories[meta.category].push(meta);
    });

  return (
    <Box 
      sx={{ 
        width: 280, 
        borderRight: '1px solid #e2e8f0', 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        backgroundColor: '#ffffff'
      }}
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" sx={{ fontWeight: 800, color: '#1e293b', mb: 1 }}>
          ETL Processors
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
          Drag and drop nodes onto the canvas to model your pipeline.
        </Typography>
        
        <TextField
          size="small"
          placeholder="Search processors..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          fullWidth
          InputProps={{
            startAdornment: <SearchIcon fontSize="small" sx={{ color: 'text.secondary', mr: 1 }} />
          }}
        />

        <Button 
          variant="outlined" 
          startIcon={<AddIcon />} 
          onClick={() => setOpenBuilder(true)} 
          fullWidth 
          sx={{ mt: 2, borderRadius: 2, textTransform: 'none', fontWeight: 600 }}
        >
          Create Custom Node
        </Button>
      </Box>

      <Divider />

      <Box sx={{ flexGrow: 1, overflowY: 'auto', p: 1 }}>
        {Object.entries(categories).map(([catName, nodes]) => (
          <Accordion key={catName} defaultExpanded disableGutters sx={{ boxShadow: 'none', border: 'none', '&:before': { display: 'none' } }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography sx={{ fontWeight: 700, fontSize: '12.5px', color: '#475569', letterSpacing: '0.5px' }}>
                {catName.toUpperCase()} ({nodes.length})
              </Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ p: 0.5 }}>
              <List disablePadding>
                {nodes.map((node) => (
                  <ListItem
                    key={node.type}
                    draggable
                    onDragStart={(event) => onDragStart(event, node.type)}
                    sx={{
                      cursor: 'grab',
                      m: '4px 0',
                      p: 1.2,
                      borderRadius: 2,
                      border: '1px solid #f1f5f9',
                      backgroundColor: '#f8fafc',
                      '&:hover': {
                        backgroundColor: '#f1f5f9',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.03)'
                      }
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 32, color: '#6366f1' }}>
                      <CodeIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText 
                      primary={node.name} 
                      primaryTypographyProps={{ fontSize: '12.5px', fontWeight: 600, color: '#334155' }}
                      secondary={node.description}
                      secondaryTypographyProps={{ fontSize: '10px', noWrap: true }}
                    />
                  </ListItem>
                ))}
              </List>
            </AccordionDetails>
          </Accordion>
        ))}
      </Box>

      {/* Visual Node Designer Modal */}
      <Modal open={openBuilder} onClose={() => setOpenBuilder(false)}>
        <Card sx={{ position: 'absolute', top: '5%', left: '10%', width: '80%', height: '90%', display: 'flex', flexDirection: 'column', overflow: 'hidden', borderRadius: 4, boxShadow: 24 }}>
          <Box sx={{ p: 2, borderBottom: '1px solid #e2e8f0', backgroundColor: '#f8fafc' }}>
            <Typography variant="h6" sx={{ fontWeight: 800 }}>Custom Node Builder</Typography>
            <Typography variant="caption" color="text.secondary">Design a custom Python processing step dynamically without building code locally.</Typography>
          </Box>
          
          <CardContent sx={{ flexGrow: 1, overflowY: 'auto', p: 3 }}>
            <Grid container spacing={3}>
              <Grid item xs={6}>
                <TextField label="Node Type ID (e.g. CustomBufferNode)" value={customType} onChange={(e) => setCustomType(e.target.value)} fullWidth sx={{ mb: 2 }} />
                <TextField label="Node Display Name (e.g. Custom Buffer)" value={customName} onChange={(e) => setCustomName(e.target.value)} fullWidth sx={{ mb: 2 }} />
                <TextField select label="Category" value={customCategory} onChange={(e) => setCustomCategory(e.target.value)} fullWidth sx={{ mb: 2 }}>
                  <MenuItem value="Transformations">Transformations</MenuItem>
                  <MenuItem value="GIS">GIS</MenuItem>
                  <MenuItem value="Readers">Readers</MenuItem>
                  <MenuItem value="Writers">Writers</MenuItem>
                  <MenuItem value="Quality">Quality</MenuItem>
                </TextField>
                <TextField label="Description" value={customDesc} onChange={(e) => setCustomDesc(e.target.value)} multiline rows={2} fullWidth sx={{ mb: 2 }} />
                
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>Node Parameters</Typography>
                  {parameters.map((param, index) => (
                    <Box key={index} sx={{ display: 'flex', gap: 1, mb: 1, alignItems: 'center' }}>
                      <TextField size="small" placeholder="Param Key" value={param.name} onChange={(e) => handleParamChange(index, 'name', e.target.value)} />
                      <TextField size="small" placeholder="Label" value={param.label} onChange={(e) => handleParamChange(index, 'label', e.target.value)} />
                      <TextField select size="small" value={param.type} onChange={(e) => handleParamChange(index, 'type', e.target.value)} style={{ width: 120 }}>
                        <MenuItem value="str">String</MenuItem>
                        <MenuItem value="int">Integer</MenuItem>
                        <MenuItem value="float">Float</MenuItem>
                        <MenuItem value="bool">Boolean</MenuItem>
                      </TextField>
                      <IconButton onClick={() => handleRemoveParam(index)} color="error"><DeleteIcon /></IconButton>
                    </Box>
                  ))}
                  <Button startIcon={<AddIcon />} size="small" onClick={handleAddParam}>Add Parameter</Button>
                </Box>
                
                <Box sx={{ mt: 3 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>Input Ports</Typography>
                  {customInputs.map((port, index) => (
                    <Box key={index} sx={{ display: 'flex', gap: 1, mb: 1, alignItems: 'center' }}>
                      <TextField size="small" placeholder="Port Name (e.g. left_data)" value={port} onChange={(e) => {
                        const newInputs = [...customInputs];
                        newInputs[index] = e.target.value;
                        setCustomInputs(newInputs);
                      }} fullWidth />
                      <IconButton onClick={() => setCustomInputs(customInputs.filter((_, i) => i !== index))} color="error"><DeleteIcon /></IconButton>
                    </Box>
                  ))}
                  <Button startIcon={<AddIcon />} size="small" onClick={() => setCustomInputs([...customInputs, ''])}>Add Input Port</Button>
                </Box>

                <Box sx={{ mt: 3 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>Output Ports</Typography>
                  {customOutputs.map((port, index) => (
                    <Box key={index} sx={{ display: 'flex', gap: 1, mb: 1, alignItems: 'center' }}>
                      <TextField size="small" placeholder="Port Name (e.g. success)" value={port} onChange={(e) => {
                        const newOutputs = [...customOutputs];
                        newOutputs[index] = e.target.value;
                        setCustomOutputs(newOutputs);
                      }} fullWidth />
                      <IconButton onClick={() => setCustomOutputs(customOutputs.filter((_, i) => i !== index))} color="error"><DeleteIcon /></IconButton>
                    </Box>
                  ))}
                  <Button startIcon={<AddIcon />} size="small" onClick={() => setCustomOutputs([...customOutputs, ''])}>Add Output Port</Button>
                </Box>
              </Grid>

              <Grid item xs={6} sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>Python Execute Code</Typography>
                <TextField
                  multiline
                  rows={15}
                  value={customCode}
                  onChange={(e) => setCustomCode(e.target.value)}
                  fullWidth
                  InputProps={{
                    style: { fontFamily: 'monospace', fontSize: '12px' }
                  }}
                />
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                  Note: The input DataFrame is loaded as `input_df`. Write operations on it and save final result to `output_df`. Refer parameters via `self.params["param_name"]`.
                </Typography>
              </Grid>
            </Grid>
          </CardContent>

          <Box sx={{ p: 2, borderTop: '1px solid #e2e8f0', display: 'flex', justifyContent: 'flex-end', gap: 2, backgroundColor: '#f8fafc' }}>
            <Button variant="outlined" onClick={() => setOpenBuilder(false)}>Cancel</Button>
            <Button variant="contained" onClick={handleSubmitCustomNode} color="primary" sx={{ fontWeight: 600 }}>Compile & Register</Button>
          </Box>
        </Card>
      </Modal>
    </Box>
  );
};
export default Sidebar;
