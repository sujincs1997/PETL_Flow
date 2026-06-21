import React, { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Box, Paper, Typography, IconButton } from '@mui/material';
import { 
  Input as InputIcon, 
  Output as OutputIcon, 
  Transform as TransformIcon, 
  Map as MapIcon, 
  AltRoute as RouteIcon,
  Delete as DeleteIcon,
  FindInPage as InspectorIcon
} from '@mui/icons-material';
import { useWorkflowStore } from '../../store/useWorkflowStore';

const categoryStyles: Record<string, { color: string; bg: string; icon: any }> = {
  Readers: { color: '#059669', bg: '#ecfdf5', icon: InputIcon },
  Writers: { color: '#dc2626', bg: '#fff5f5', icon: OutputIcon },
  Transformations: { color: '#4f46e5', bg: '#eef2ff', icon: TransformIcon },
  GIS: { color: '#d97706', bg: '#fffbeb', icon: MapIcon },
  'Network Analysis': { color: '#7c3aed', bg: '#f5f3ff', icon: RouteIcon },
  Quality: { color: '#0891b2', bg: '#ecfeff', icon: InspectorIcon },
};

export const BaseCanvasNode: React.FC<NodeProps> = ({ id, data, selected }) => {
  const deleteNode = useWorkflowStore((state) => state.deleteNode);
  const style = categoryStyles[data.category] || { color: '#4b5563', bg: '#f3f4f6', icon: TransformIcon };
  const IconComponent = style.icon;

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    deleteNode(id);
  };

  return (
    <Paper
      elevation={selected ? 6 : 2}
      sx={{
        width: 220,
        borderRadius: 2.5,
        border: selected ? `2px solid ${style.color}` : '2px solid transparent',
        backgroundColor: '#ffffff',
        overflow: 'visible',
        position: 'relative',
        transition: 'all 0.15s ease-in-out',
        '&:hover': {
          boxShadow: '0 8px 30px rgba(0,0,0,0.08)'
        }
      }}
    >
      {/* Target Handles (Inputs) */}
      {data.inputs && data.inputs.map((input: any, index: number) => {
        const topPos = `${((index + 1) / (data.inputs.length + 1)) * 100}%`;
        return (
          <React.Fragment key={input.name}>
            <Handle
              type="target"
              position={Position.Left}
              id={input.name}
              style={{
                top: topPos,
                background: style.color,
                width: 10,
                height: 10,
                border: '2px solid #ffffff'
              }}
            />
            <Typography
              variant="caption"
              sx={{
                position: 'absolute',
                left: 12,
                top: `calc(${topPos} - 8px)`,
                fontSize: '9px',
                fontWeight: 600,
                color: '#64748b',
                pointerEvents: 'none'
              }}
            >
              {input.label}
            </Typography>
          </React.Fragment>
        );
      })}

      {/* Node Content Header */}
      <Box 
        sx={{ 
          p: 1.5, 
          display: 'flex', 
          alignItems: 'center', 
          borderBottom: '1px solid #f3f4f6',
          backgroundColor: style.bg,
          borderTopLeftRadius: 8,
          borderTopRightRadius: 8
        }}
      >
        <Box 
          sx={{ 
            p: 0.6, 
            borderRadius: 1.5, 
            backgroundColor: '#ffffff', 
            color: style.color,
            display: 'flex',
            boxShadow: '0 2px 4px rgba(0,0,0,0.02)'
          }}
        >
          <IconComponent fontSize="small" />
        </Box>
        <Box sx={{ ml: 1.2, flexGrow: 1, minWidth: 0 }}>
          <Typography 
            variant="subtitle2" 
            sx={{ 
              fontWeight: 700, 
              fontSize: '13px', 
              color: '#1f2937', 
              lineHeight: 1.2,
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis'
            }}
          >
            {data.label}
          </Typography>
          <Typography 
            variant="caption" 
            sx={{ 
              fontSize: '9px', 
              color: style.color, 
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}
          >
            {data.category}
          </Typography>
        </Box>
        <IconButton size="small" onClick={handleDelete} sx={{ color: '#9ca3af', '&:hover': { color: '#ef4444' } }}>
          <DeleteIcon sx={{ fontSize: 16 }} />
        </IconButton>
      </Box>

      {/* Description */}
      {data.description && (
        <Box sx={{ px: 1.5, py: 1.2, pb: 2.5 }}>
          <Typography 
            variant="caption" 
            sx={{ 
              color: '#6b7280', 
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
              lineHeight: 1.3,
              fontSize: '10.5px'
            }}
          >
            {data.description}
          </Typography>
        </Box>
      )}

      {/* Source Handles (Outputs) */}
      {data.outputs && data.outputs.map((output: any, index: number) => {
        const topPos = `${((index + 1) / (data.outputs.length + 1)) * 100}%`;
        return (
          <React.Fragment key={output.name}>
            <Handle
              type="source"
              position={Position.Right}
              id={output.name}
              style={{
                top: topPos,
                background: style.color,
                width: 10,
                height: 10,
                border: '2px solid #ffffff'
              }}
            />
            <Typography
              variant="caption"
              sx={{
                position: 'absolute',
                right: 12,
                top: `calc(${topPos} - 8px)`,
                fontSize: '9px',
                fontWeight: 600,
                color: '#64748b',
                pointerEvents: 'none',
                textAlign: 'right'
              }}
            >
              {output.label}
            </Typography>
          </React.Fragment>
        );
      })}
    </Paper>
  );
};

export default memo(BaseCanvasNode);
