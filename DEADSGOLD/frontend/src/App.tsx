import React, { useRef } from 'react';
import { AppBar, Toolbar, Typography, Box, Button } from '@mui/material';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import BlockchainStatusPage from './components/BlockchainStatusPage';
import WalletPage, { WalletPageRef } from './components/WalletPage';
import MinerPage from './components/MinerPage';

function App() {
  const walletPageRef = useRef<WalletPageRef>(null);

  const handleUpdateBalance = () => {
    walletPageRef.current?.fetchBalance();
  };

  return (
    <Router>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              DEADSGOLD
            </Typography>
            <Button color="inherit" component={Link} to="/">
              Blockchain
            </Button>
            <Button color="inherit" component={Link} to="/wallet">
              Wallet
            </Button>
            <Button color="inherit" component={Link} to="/miner">
              Miner
            </Button>
            <Button color="inherit" onClick={handleUpdateBalance}>
              Update Balance
            </Button>
          </Toolbar>
        </AppBar>
        <Routes>
          <Route path="/" element={<BlockchainStatusPage />} />
          <Route path="/wallet" element={<WalletPage ref={walletPageRef} />} />
          <Route path="/miner" element={<MinerPage />} />
        </Routes>
      </Box>
    </Router>
  );
}

export default App;