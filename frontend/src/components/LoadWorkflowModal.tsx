import React, { useState, useEffect } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions, Button,
  Box, Typography, List, ListItem, ListItemText, ListItemButton,
  CircularProgress, Alert, IconButton, Divider
} from '@mui/material';
import { Close as CloseIcon, CloudDownload as LoadIcon } from '@mui/icons-material';
import { useWorkflowStore } from '../store/useWorkflowStore';
import { Workflow } from '../types';

interface LoadWorkflowModalProps {
  open: boolean;
  onClose: () => void;
}

const LoadWorkflowModal: React.FC<LoadWorkflowModalProps> = ({ open, onClose }) => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const loadWorkflow = useWorkflowStore((state) => state.loadWorkflow);

  useEffect(() => {
    if (open) {
      setLoading(true);
      setError(null);
      const token = localStorage.getItem('token') || '';
      
      fetch('/api/workflows', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      .then(res => {
        if (!res.ok) throw new Error(`Failed to load workflows (${res.status})`);
        return res.json();
      })
      .then(data => {
        setWorkflows(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
    }
  }, [open]);

  const handleSelectWorkflow = async (id: string) => {
    try {
      await loadWorkflow(id);
      onClose();
    } catch (e: any) {
      alert("Failed to load workflow: " + e.message);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 3 } }}>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', backgroundColor: '#f8fafc', py: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <LoadIcon sx={{ color: '#6366f1' }} />
          <Typography variant="h6" sx={{ fontWeight: 800, color: '#0f172a' }}>
            Load Pipeline
          </Typography>
        </Box>
        <IconButton onClick={onClose} size="small"><CloseIcon /></IconButton>
      </DialogTitle>
      <Divider />
      
      <DialogContent sx={{ minHeight: 300, p: 0 }}>
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', mt: 5 }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Box sx={{ p: 3 }}>
            <Alert severity="error">{error}</Alert>
          </Box>
        )}

        {!loading && !error && workflows.length === 0 && (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="body1" color="text.secondary">
              No saved pipelines found.
            </Typography>
          </Box>
        )}

        {!loading && !error && workflows.length > 0 && (
          <List sx={{ pt: 0 }}>
            {workflows.map((wf) => (
              <ListItem key={wf.id} disablePadding sx={{ borderBottom: '1px solid #f1f5f9' }}>
                <ListItemButton onClick={() => handleSelectWorkflow(wf.id)} sx={{ py: 2, px: 3 }}>
                  <ListItemText 
                    primary={<Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#334155' }}>{wf.name}</Typography>}
                    secondary={
                      <React.Fragment>
                        <Typography variant="body2" sx={{ color: '#64748b', mt: 0.5 }}>
                          {wf.description || 'No description provided'}
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#94a3b8', display: 'block', mt: 1 }}>
                          Version {wf.version} • Last updated: {new Date(wf.updated_at).toLocaleString()}
                        </Typography>
                      </React.Fragment>
                    }
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        )}
      </DialogContent>
      <Divider />
      <DialogActions sx={{ p: 2, backgroundColor: '#f8fafc' }}>
        <Button onClick={onClose} variant="outlined" sx={{ borderRadius: 2, fontWeight: 600, textTransform: 'none' }}>
          Cancel
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default LoadWorkflowModal;
