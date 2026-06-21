import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, Typography, Paper, Divider, Chip, CircularProgress, 
  IconButton, Accordion, AccordionSummary, AccordionDetails
} from '@mui/material';
import { 
  Terminal as TerminalIcon,
  ExpandMore as ExpandMoreIcon,
  ClearAll as ClearIcon,
  KeyboardArrowDown as ArrowDownIcon,
  KeyboardArrowUp as ArrowUpIcon
} from '@mui/icons-material';
import { useWorkflowStore } from '../store/useWorkflowStore';

export const ExecutionPanel: React.FC = () => {
  const activeExecution = useWorkflowStore((state) => state.activeExecution);
  const isExecuting = useWorkflowStore((state) => state.isExecuting);
  const [expanded, setExpanded] = useState(true);
  const logEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll logs to bottom on new updates
  useEffect(() => {
    if (logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [activeExecution?.logs]);

  if (!activeExecution) return null;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED': return 'success';
      case 'FAILED': return 'error';
      case 'RUNNING': return 'primary';
      default: return 'warning';
    }
  };

  const getLogLevelColor = (level: string) => {
    switch (level) {
      case 'ERROR': return '#f87171'; // Red
      case 'WARNING': return '#fbbf24'; // Yellow
      case 'DEBUG': return '#60a5fa'; // Blue
      default: return '#e2e8f0'; // Gray/White
    }
  };

  return (
    <Paper 
      elevation={8}
      sx={{ 
        position: 'absolute', 
        bottom: 0, 
        left: 280, 
        right: 320, 
        borderTop: '1px solid #e2e8f0',
        zIndex: 1000,
        backgroundColor: '#ffffff',
        borderTopLeftRadius: 16,
        borderTopRightRadius: 16,
        overflow: 'hidden',
        maxHeight: expanded ? 320 : 48,
        transition: 'max-height 0.25s cubic-bezier(0.4, 0, 0.2, 1)'
      }}
    >
      {/* Header Bar */}
      <Box 
        onClick={() => setExpanded(!expanded)}
        sx={{ 
          px: 3, 
          py: 1.2, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          cursor: 'pointer',
          backgroundColor: '#f8fafc',
          '&:hover': {
            backgroundColor: '#f1f5f9'
          }
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <TerminalIcon sx={{ color: '#475569', fontSize: 18 }} />
          <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#334155' }}>
            Workflow Execution Logs
          </Typography>
          {isExecuting && <CircularProgress size={12} thickness={5} />}
          <Chip 
            label={activeExecution.status} 
            size="small" 
            color={getStatusColor(activeExecution.status)}
            sx={{ fontWeight: 700, fontSize: '10px', height: 20 }}
          />
        </Box>
        <IconButton size="small">
          {expanded ? <ArrowDownIcon /> : <ArrowUpIcon />}
        </IconButton>
      </Box>

      <Divider />

      {/* Terminal Logs Output */}
      {expanded && (
        <Box 
          sx={{ 
            p: 2, 
            height: 270, 
            backgroundColor: '#0f172a', // Slate 900
            overflowY: 'auto',
            fontFamily: 'monospace',
            fontSize: '11px',
            lineHeight: 1.5,
            color: '#e2e8f0'
          }}
        >
          {activeExecution.logs && activeExecution.logs.length > 0 ? (
            activeExecution.logs.map((log) => (
              <Box 
                key={log.id} 
                sx={{ 
                  display: 'flex', 
                  mb: 0.6,
                  borderLeft: `2px solid ${log.node_key ? '#6366f1' : 'transparent'}`,
                  pl: log.node_key ? 1 : 0
                }}
              >
                <Typography 
                  variant="caption" 
                  sx={{ 
                    color: '#64748b', 
                    mr: 1.5, 
                    fontSize: '10px', 
                    fontFamily: 'inherit',
                    userSelect: 'none' 
                  }}
                >
                  [{new Date(log.timestamp).toLocaleTimeString()}]
                </Typography>
                
                <Typography 
                  variant="caption" 
                  sx={{ 
                    color: getLogLevelColor(log.log_level), 
                    fontWeight: 700,
                    mr: 1.5, 
                    fontSize: '10px', 
                    fontFamily: 'inherit',
                    userSelect: 'none' 
                  }}
                >
                  {log.log_level}
                </Typography>

                {log.node_key && (
                  <Typography 
                    variant="caption" 
                    sx={{ 
                      color: '#818cf8', 
                      fontWeight: 600,
                      mr: 1.5, 
                      fontSize: '10px', 
                      fontFamily: 'inherit',
                      userSelect: 'none'
                    }}
                  >
                    ({log.node_key})
                  </Typography>
                )}

                <Typography 
                  variant="body2" 
                  sx={{ 
                    fontFamily: 'inherit', 
                    fontSize: '11px', 
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-all'
                  }}
                >
                  {log.message}
                </Typography>
              </Box>
            ))
          ) : (
            <Typography variant="body2" sx={{ color: '#64748b', fontFamily: 'inherit', fontStyle: 'italic' }}>
              Initializing worker task and preparing DAG components...
            </Typography>
          )}
          <div ref={logEndRef} />
        </Box>
      )}
    </Paper>
  );
};
export default ExecutionPanel;
