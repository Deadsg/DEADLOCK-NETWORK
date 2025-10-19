import React, { useEffect, useState } from 'react';
import { Container, Typography, Paper } from '@mui/material';

const BlockchainStatusPage: React.FC = () => {
  const [blockchainStatus, setBlockchainStatus] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBlockchainStatus = async () => {
      try {
        const response = await fetch('YOUR_NGROK_URL_HERE/blockchain/status');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setBlockchainStatus(data);
      } catch (e: any) {
        setError(e.message);
      }
    };

    fetchBlockchainStatus();
  }, []);

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Blockchain Status
      </Typography>
      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          Error: {error}
        </Typography>
      )}
      {blockchainStatus ? (
        <Paper elevation={3} sx={{ p: 2 }}>
          <Typography variant="h6">Chain Length: {blockchainStatus.chain_length}</Typography>
          <Typography variant="h6">Last Block Index: {blockchainStatus.last_block.index}</Typography>
          <Typography variant="h6">Pending Transactions: {blockchainStatus.pending_transactions.length}</Typography>
          {/* You can display more details about the last block and pending transactions here */}
        </Paper>
      ) : (
        <Typography>Loading blockchain status...</Typography>
      )}
    </Container>
  );
};

export default BlockchainStatusPage;
