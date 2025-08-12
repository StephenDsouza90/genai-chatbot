import React, { useState, useEffect } from 'react';
import { useChatStore } from '../store/chatStore';
import { useFileStore } from '../store/fileStore';
import Sidebar from './Sidebar/Sidebar';
import ChatInterface from './Chat/ChatInterface';
import { Menu, X } from 'lucide-react';

const ChatApp = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isMobile, setIsMobile] = useState(false);
  const { initializeSession } = useChatStore();
  const { loadFiles } = useFileStore();

  useEffect(() => {
    // Check if mobile
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth < 768) {
        setSidebarOpen(false);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);

    // Initialize app data
    initializeSession();
    loadFiles();

    return () => window.removeEventListener('resize', checkMobile);
  }, [initializeSession, loadFiles]);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className="chat-app">
      {/* Mobile header */}
      {isMobile && (
        <div className="mobile-header">
          <button onClick={toggleSidebar} className="mobile-menu-btn">
            {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
          <h1 className="mobile-title">AI Document Chat</h1>
        </div>
      )}

      <div className="chat-app-content">
        {/* Sidebar */}
        <div className={`sidebar-container ${sidebarOpen ? 'open' : 'closed'}`}>
          <Sidebar onClose={() => isMobile && setSidebarOpen(false)} />
        </div>

        {/* Mobile overlay */}
        {isMobile && sidebarOpen && (
          <div className="mobile-overlay" onClick={() => setSidebarOpen(false)} />
        )}

        {/* Main chat area */}
        <div className="chat-container">
          <ChatInterface />
        </div>
      </div>

      <style jsx>{`
        .chat-app {
          height: 100vh;
          display: flex;
          flex-direction: column;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .mobile-header {
          display: none;
          align-items: center;
          padding: 1rem;
          background: white;
          border-bottom: 1px solid #e2e8f0;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        @media (max-width: 768px) {
          .mobile-header {
            display: flex;
          }
        }

        .mobile-menu-btn {
          background: none;
          border: none;
          color: #64748b;
          cursor: pointer;
          padding: 0.5rem;
          border-radius: 0.5rem;
          transition: all 0.2s;
        }

        .mobile-menu-btn:hover {
          background: #f1f5f9;
          color: #334155;
        }

        .mobile-title {
          font-size: 1.25rem;
          font-weight: 600;
          color: #1e293b;
          margin-left: 1rem;
        }

        .chat-app-content {
          flex: 1;
          display: flex;
          position: relative;
          overflow: hidden;
        }

        .sidebar-container {
          transition: all 0.3s ease;
          background: white;
          border-right: 1px solid #e2e8f0;
          box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
        }

        .sidebar-container.open {
          width: 320px;
        }

        .sidebar-container.closed {
          width: 0;
        }

        @media (max-width: 768px) {
          .sidebar-container {
            position: absolute;
            top: 0;
            left: 0;
            height: 100%;
            z-index: 20;
          }

          .sidebar-container.open {
            width: 280px;
          }
        }

        .mobile-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          z-index: 10;
        }

        .chat-container {
          flex: 1;
          display: flex;
          flex-direction: column;
          min-width: 0;
        }
      `}</style>
    </div>
  );
};

export default ChatApp;
