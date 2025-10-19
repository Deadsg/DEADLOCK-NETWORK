import React from 'react';

const Blockchain = () => {
  return (
    <div style={{ padding: '20px', color: 'white' }}>
      <h2>Blockchain Content</h2>
      <div style={sectionStyle}>
        <h3>Blockchain View</h3>
        {/* Placeholder for a table/list of blocks */}
        <p>Block 1: ...</p>
        <p>Block 2: ...</p>
        <button style={buttonStyle}>Refresh Blockchain</button>
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

export default Blockchain;
