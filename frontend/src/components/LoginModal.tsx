import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useWorkflowStore } from '../store/useWorkflowStore';

/**
 * Simple login modal used by the ETL UI.
 * It authenticates against the FastAPI backend and stores the JWT token in
 * localStorage under the key `token`.
 */
const LoginModal: React.FC = () => {
  const [open, setOpen] = useState(!localStorage.getItem('token'));
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleClose = () => {
    // Keep modal open if token not stored
    if (localStorage.getItem('token')) {
      setOpen(false);
    }
  };

  const handleSubmit = async () => {
    setError(null);
    setLoading(true);
    try {
      if (!isLogin) {
        // Register flow
        const regRes = await fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, email, password, role: 'Developer' }),
        });
        if (!regRes.ok) {
          const data = await regRes.json().catch(() => ({}));
          const errMsg = Array.isArray(data.detail) ? data.detail.map((d: any) => d.msg).join(', ') : (typeof data.detail === 'string' ? data.detail : 'Registration failed');
          throw new Error(errMsg);
        }
      }

      // Login flow (always runs to get token)
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        const errMsg = Array.isArray(data.detail) ? data.detail.map((d: any) => d.msg).join(', ') : (typeof data.detail === 'string' ? data.detail : 'Login failed');
        throw new Error(errMsg);
      }

      const data = await res.json();
      localStorage.setItem('token', data.access_token);
      
      // Fetch nodes immediately so the sidebar populates after login
      useWorkflowStore.getState().fetchNodeMetadata();
      
      setOpen(false);
    } catch (e: any) {
      setError(e.message || 'Unexpected error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="xs" fullWidth sx={{ zIndex: 1300 }}>
      <DialogTitle>{isLogin ? 'Sign In' : 'Sign Up'}</DialogTitle>
      <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
        {error && <Alert severity="error">{error}</Alert>}
        
        <TextField
          label="Username"
          variant="outlined"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          fullWidth
        />
        
        {!isLogin && (
          <TextField
            label="Email"
            type="email"
            variant="outlined"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            fullWidth
          />
        )}
        
        <TextField
          label="Password"
          type="password"
          variant="outlined"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          fullWidth
        />

        <Button 
          variant="text" 
          size="small" 
          onClick={() => {
            setIsLogin(!isLogin);
            setError(null);
          }}
          sx={{ alignSelf: 'flex-start', textTransform: 'none' }}
        >
          {isLogin ? "Don't have an account? Sign Up" : "Already have an account? Sign In"}
        </Button>
      </DialogContent>
      
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={handleClose} disabled={loading} variant="text">
          Cancel
        </Button>
        <Button 
          onClick={handleSubmit} 
          disabled={loading || !username || !password || (!isLogin && !email)} 
          variant="contained" 
          color="primary"
        >
          {loading ? <CircularProgress size={20} /> : (isLogin ? 'Login' : 'Register')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default LoginModal;
