import React from 'react';
import { useChatStore } from '../../store/chatStore';
import { MessageSquare, RotateCcw, Loader, Plus } from 'lucide-react';
import toast from 'react-hot-toast';

const SessionInfo = () => {
  const { sessionId, messages, clearChat, isLoading, initializeSession } = useChatStore();

  const handleClearChat = () => {
    if (messages.length === 0) return;
    
    clearChat();
    toast.success('Chat cleared');
  };

  const handleNewChat = async () => {
    try {
      await initializeSession();
      toast.success('New chat session created');
    } catch (error) {
      toast.error('Failed to create new session');
    }
  };

  return (
    <div className="session-info">
      <div className="section-header">
        <h3 className="section-title">Current Session</h3>
        <button 
          className="new-chat-btn"
          onClick={handleNewChat}
          title="Start new chat"
        >
          <Plus size={16} />
        </button>
      </div>
      
      <div className="session-card">
        <div className="session-status">
          <MessageSquare className="status-icon" />
          <div className="status-details">
            <p className="status-text">
              {sessionId ? 'Connected' : 'Not connected'}
            </p>
            <p className="session-id">
              {sessionId ? `ID: ${sessionId.slice(0, 8)}...` : 'No active session'}
            </p>
          </div>
        </div>
        
        <div className="session-stats">
          <div className="stat">
            <span className="stat-value">{messages.length}</span>
            <span className="stat-label">Messages</span>
          </div>
        </div>
        
        {messages.length > 0 && (
          <button 
            className="clear-btn"
            onClick={handleClearChat}
            disabled={isLoading}
          >
            {isLoading ? (
              <Loader size={16} className="animate-spin" />
            ) : (
              <RotateCcw size={16} />
            )}
            Clear Chat
          </button>
        )}
      </div>

      <style jsx>{`
        .session-info {
          width: 100%;
        }

        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .section-title {
          font-size: 1.1rem;
          font-weight: 600;
          color: #1e293b;
          margin: 0;
        }

        .new-chat-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 32px;
          height: 32px;
          background: #667eea;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .new-chat-btn:hover {
          background: #5a67d8;
          transform: translateY(-1px);
        }

        .session-card {
          background: #f8fafc;
          border: 1px solid #e2e8f0;
          border-radius: 8px;
          padding: 1rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .session-status {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .status-icon {
          color: ${sessionId ? '#10b981' : '#64748b'};
          width: 20px;
          height: 20px;
        }

        .status-details {
          flex: 1;
        }

        .status-text {
          margin: 0;
          font-size: 0.9rem;
          font-weight: 500;
          color: ${sessionId ? '#10b981' : '#64748b'};
        }

        .session-id {
          margin: 0;
          font-size: 0.75rem;
          color: #64748b;
          font-family: monospace;
        }

        .session-stats {
          display: flex;
          justify-content: space-around;
          padding: 0.75rem 0;
          border-top: 1px solid #e2e8f0;
        }

        .stat {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.25rem;
        }

        .stat-value {
          font-size: 1.5rem;
          font-weight: 700;
          color: #667eea;
        }

        .stat-label {
          font-size: 0.75rem;
          color: #64748b;
        }

        .clear-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          padding: 0.5rem 1rem;
          background: #ef4444;
          color: white;
          border: none;
          border-radius: 6px;
          font-size: 0.85rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .clear-btn:hover:not(:disabled) {
          background: #dc2626;
          transform: translateY(-1px);
        }

        .clear-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .animate-spin {
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default SessionInfo;
