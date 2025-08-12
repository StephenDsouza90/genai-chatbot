import React from 'react';
import FileUpload from './FileUpload';
import FileList from './FileList';
import SessionInfo from './SessionInfo';
import { Bot } from 'lucide-react';

const Sidebar = ({ onClose }) => {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <Bot className="logo-icon" />
          <span className="logo-text">AI Document Chat</span>
        </div>
      </div>

      <div className="sidebar-content">
        <SessionInfo />
        <FileUpload />
        <FileList />
      </div>

      <style jsx>{`
        .sidebar {
          height: 100%;
          display: flex;
          flex-direction: column;
          background: white;
          width: 100%;
        }

        .sidebar-header {
          padding: 1.5rem;
          border-bottom: 1px solid #e2e8f0;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .sidebar-logo {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .logo-icon {
          color: white;
          width: 28px;
          height: 28px;
        }

        .logo-text {
          font-size: 1.25rem;
          font-weight: 700;
          color: white;
        }

        .sidebar-content {
          flex: 1;
          padding: 1.5rem;
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
          overflow-y: auto;
        }
      `}</style>
    </div>
  );
};

export default Sidebar;
