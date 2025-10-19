import React, { useState } from 'react';
import { Container, Typography, Paper, Button, Box } from '@mui/material';

const MinerPage: React.FC = () => {
  const [miningStatus, setMiningStatus] = useState<string>("Idle");
  const [error, setError] = useState<string | null>(null);

  const handleMineBlock = async () => {
    setMiningStatus("Mining...");
    setError(null);
    try {
      const response = await fetch('YOUR_NGROK_URL_HERE/mine', {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setMiningStatus(`Mined Block ${data.index}`);
    } catch (e: any) {
      setError(e.message);
      setMiningStatus("Failed");
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Miner Control
      </Typography>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Current Status: {miningStatus}
        </Typography>
        <Button variant="contained" color="primary" onClick={handleMineBlock}>
          Mine New Block
        </Button>
        {error && (
          <Typography color="error" sx={{ mt: 2 }}>
            Error: {error}
          </Typography>
        )}
      </Paper>
    </Container>
  );
};

export default MinerPage;
