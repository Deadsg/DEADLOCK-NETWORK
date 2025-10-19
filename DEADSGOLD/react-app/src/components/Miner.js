import React from 'react';

const Miner = () => {
  return (
    <div style={{ padding: '20px', color: 'white' }}>
      <h2>Miner Content</h2>
      <div style={sectionStyle}>
        <h3>Mining Operations</h3>
        <button style={buttonStyle}>Start Mining</button>
        <p>Status: Idle</p>
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

export default Miner;
