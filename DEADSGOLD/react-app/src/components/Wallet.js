import React from 'react';

const Wallet = () => {
  return (
    <div style={{ padding: '20px', color: 'white' }}>
      <h2>Wallet Content</h2>
      {/* Wallet Information Section */}
      <div style={sectionStyle}>
        <h3>Wallet Information</h3>
        <p>Address: [Wallet Address]</p>
        <p>Balance: [Wallet Balance]</p>
        <p>Private Key: ************</p>
        <p style={{ color: 'red' }}>WARNING: Keep your private key secret!</p>
        <button style={buttonStyle}>Update Balance</button>
      </div>

      {/* Send Transaction Section */}
      <div style={sectionStyle}>
        <h3>Send Transaction</h3>
        <p>Recipient: <input type="text" style={inputStyle} /></p>
        <p>Amount: <input type="text" style={inputStyle} /></p>
        <button style={buttonStyle}>Send</button>
      </div>

      {/* Load Wallet from Mnemonic Section */}
      <div style={sectionStyle}>
        <h3>Load Wallet from Mnemonic</h3>
        <p>Mnemonic Phrase: <input type="text" style={inputStyle} /></p>
        <button style={buttonStyle}>Load Wallet</button>
      </div>
    </div>
  );
};

const sectionStyle = {
  backgroundColor: '#2a2a2a',
  padding: '15px',
  margin: '15px 0',
  borderRadius: '5px',
  border: '1px solid #ff0000',
};

const inputStyle = {
  backgroundColor: '#333333',
  border: '1px solid #ff0000',
  color: 'white',
  padding: '5px',
  margin: '5px',
  borderRadius: '3px',
};

const buttonStyle = {
  backgroundColor: '#ff0000',
  color: 'white',
  border: 'none',
  padding: '10px 15px',
  margin: '5px',
  borderRadius: '5px',
  cursor: 'pointer',
  fontWeight: 'bold',
};

export default Wallet;
