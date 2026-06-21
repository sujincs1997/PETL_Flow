import React from 'react';
import { ReactFlowProvider } from 'reactflow';
import { Box } from '@mui/material';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Canvas from './components/Canvas';
import PropertiesPanel from './components/PropertiesPanel';
import ExecutionPanel from './components/ExecutionPanel';
import LoginModal from './components/LoginModal';

function App() {

  return (
    <ReactFlowProvider>
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', overflow: 'hidden' }}>
        {/* Top Header Controls */}
        <Header />
        
        {/* Authentication Login Dialog */}
        <LoginModal />

        {/* Main Studio Area */}
        <Box sx={{ display: 'flex', flexGrow: 1, overflow: 'hidden', position: 'relative' }}>
          {/* Left Side Node Toolbox */}
          <Sidebar />

          {/* Central visual workspace graph canvas */}
          <Canvas />

          {/* Right side contextual configuration parameter forms */}
          <PropertiesPanel />

          {/* Floating overlays for terminal logs */}
          <ExecutionPanel />
        </Box>
      </Box>
    </ReactFlowProvider>
  );
}

export default App;
