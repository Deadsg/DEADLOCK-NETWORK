import React, { useState } from 'react';
import './App.css'; // We'll define global styles here

import Wallet from './components/Wallet';
import Blockchain from './components/Blockchain';
import Miner from './components/Miner';
import Solana from './components/Solana';

function App() {
  const [activeTab, setActiveTab] = useState('Wallet');

  const renderContent = () => {
    switch (activeTab) {
      case 'Wallet':
        return <Wallet />;
      case 'Blockchain':
        return <Blockchain />;
      case 'Miner':
        return <Miner />;
      case 'Solana':
        return <Solana />;
      default:
        return <Wallet />;
    }
  };

  return (
    <div style={appContainerStyle}>
      <nav style={navbarStyle}>
        {['Wallet', 'Blockchain', 'Miner', 'Solana'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              ...navButtonStyle,
              ...(activeTab === tab ? activeNavButtonStyle : {}),
            }}
          >
            {tab}
          </button>
        ))}
      </nav>
      <div style={contentAreaStyle}>
        {renderContent()}
      </div>
    </div>
  );
}

// Styles for the black and red theme
const appContainerStyle = {
  backgroundColor: '#1a1a1a', // Dark background
  minHeight: '100vh',
  color: 'white',
  fontFamily: 'Arial, sans-serif',
};

const navbarStyle = {
  display: 'flex',
  justifyContent: 'center',
  backgroundColor: '#333333', // Slightly lighter dark for navbar
  padding: '10px 0',
  borderBottom: '2px solid #ff0000', // Red accent
};

const navButtonStyle = {
  background: 'none',
  border: 'none',
  color: 'white',
  padding: '10px 20px',
  margin: '0 5px',
  cursor: 'pointer',
  fontSize: '16px',
  fontWeight: 'bold',
  transition: 'color 0.3s, border-bottom 0.3s',
};

const activeNavButtonStyle = {
  color: '#ff0000', // Red for active tab
  borderBottom: '2px solid #ff0000',
};

const contentAreaStyle = {
  padding: '20px',
};

export default App;
