import React, { useState } from 'react';
import { Container, Typography, Paper, Button, TextField, Box, IconButton, InputAdornment, Alert } from '@mui/material';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';

const WalletPage: React.FC = () => {
  const [publicKey, setPublicKey] = useState<string | null>(null);
  const [privateKey, setPrivateKey] = useState<string | null>(null);
  const [showPrivateKey, setShowPrivateKey] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Transaction state
  const [recipient, setRecipient] = useState<string>('');
  const [amount, setAmount] = useState<string>('');
  const [senderPrivateKey, setSenderPrivateKey] = useState<string>('');
  const [showSenderPrivateKey, setShowSenderPrivateKey] = useState<boolean>(false);

  const handleGenerateWallet = async () => {
    try {
      const response = await fetch('YOUR_NGROK_URL_HERE/wallet/new', {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setPublicKey(data.public_key);
      setPrivateKey(data.private_key);
      setError(null);
      setSuccessMessage("New wallet generated successfully!");
    } catch (e: any) {
      setError(e.message);
      setPublicKey(null);
      setPrivateKey(null);
      setSuccessMessage(null);
    }
  };

  const handleSendTransaction = async () => {
    setError(null);
    setSuccessMessage(null);
    try {
      if (!publicKey) {
        throw new Error("Please generate or import a wallet first to get the sender's public key.");
      }
      const response = await fetch('YOUR_NGROK_URL_HERE/transaction/new', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sender: publicKey, // Assuming the generated wallet is the sender
          recipient: recipient,
          amount: parseFloat(amount),
          private_key: senderPrivateKey,
        }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      setSuccessMessage("Transaction successfully sent!");
      setRecipient('');
      setAmount('');
      setSenderPrivateKey('');
    } catch (e: any) {
      setError(e.message);
      setSuccessMessage(null);
    }
  };

  const handleClickShowPrivateKey = () => setShowPrivateKey((show) => !show);
  const handleMouseDownPrivateKey = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
  };

  const handleClickShowSenderPrivateKey = () => setShowSenderPrivateKey((show) => !show);
  const handleMouseDownSenderPrivateKey = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Wallet Management
      </Typography>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Button variant="contained" color="primary" onClick={handleGenerateWallet}>
          Generate New Wallet
        </Button>
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
        {successMessage && (
          <Alert severity="success" sx={{ mt: 2 }}>
            {successMessage}
          </Alert>
        )}
        {publicKey && privateKey && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6">Your New Wallet:</Typography>
            <TextField
              label="Public Key (Address)"
              fullWidth
              margin="normal"
              value={publicKey}
              InputProps={{
                readOnly: true,
              }}
            />
            <TextField
              label="Private Key"
              fullWidth
              margin="normal"
              type={showPrivateKey ? 'text' : 'password'}
              value={privateKey}
              InputProps={{
                readOnly: true,
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle private key visibility"
                      onClick={handleClickShowPrivateKey}
                      onMouseDown={handleMouseDownPrivateKey}
                      edge="end"
                    >
                      {showPrivateKey ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
              Please save your private key securely. It is required to sign transactions.
            </Typography>
          </Box>
        )}
      </Paper>

      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Send Transaction
        </Typography>
        <TextField
          label="Recipient Public Key (Address)"
          fullWidth
          margin="normal"
          value={recipient}
          onChange={(e) => setRecipient(e.target.value)}
        />
        <TextField
          label="Amount"
          fullWidth
          margin="normal"
          type="number"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
        />
        <TextField
          label="Sender Private Key"
          fullWidth
          margin="normal"
          type={showSenderPrivateKey ? 'text' : 'password'}
          value={senderPrivateKey}
          onChange={(e) => setSenderPrivateKey(e.target.value)}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  aria-label="toggle sender private key visibility"
                  onClick={handleClickShowSenderPrivateKey}
                  onMouseDown={handleMouseDownSenderPrivateKey}
                  edge="end"
                >
                  {showSenderPrivateKey ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            ),
          }}
        />
        <Button
          variant="contained"
          color="primary"
          onClick={handleSendTransaction}
          sx={{ mt: 2 }}
        >
          Send Transaction
        </Button>
      </Paper>
    </Container>
  );
};

export default WalletPage;
