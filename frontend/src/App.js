import React from 'react';
import { Toaster } from 'react-hot-toast';
import ChatApp from './components/ChatApp';
import './App.css';

function App() {
  return (
    <div className="app">
      <ChatApp />
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#ffffff',
            color: '#1e293b',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
            border: '1px solid #e2e8f0',
          },
        }}
      />
    </div>
  );
}

export default App;

