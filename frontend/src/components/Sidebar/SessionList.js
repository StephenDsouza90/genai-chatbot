import React, { useState, useEffect } from 'react';
import { useChatStore } from '../../store/chatStore';
import { MessageSquare, Trash2, Clock, Loader, Plus } from 'lucide-react';
import toast from 'react-hot-toast';

const SessionList = () => {
  const { 
    sessions, 
    sessionsLoading, 
    sessionId: currentSessionId, 
    fetchSessions, 
    switchSession, 
    deleteSession,
    initializeSession 
  } = useChatStore();
  
  const [deletingSession, setDeletingSession] = useState(null);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  const handleSwitchSession = async (sessionId) => {
    if (sessionId === currentSessionId) return;
    
    try {
      await switchSession(sessionId);
      toast.success('Switched to chat session');
    } catch (error) {
      toast.error('Failed to switch session');
    }
  };

  const handleDeleteSession = async (sessionId) => {
    if (!window.confirm('Are you sure you want to delete this chat session? This action cannot be undone.')) {
      return;
    }

    setDeletingSession(sessionId);
    try {
      await deleteSession(sessionId);
      toast.success('Session deleted successfully');
    } catch (error) {
      toast.error('Failed to delete session');
    } finally {
      setDeletingSession(null);
    }
  };

  const handleNewSession = async () => {
    try {
      await initializeSession();
      toast.success('New chat session created');
    } catch (error) {
      toast.error('Failed to create new session');
    }
  };

  const formatTimeAgo = (timestamp) => {
    if (!timestamp) return 'Unknown';
    try {
      const date = new Date(parseInt(timestamp));
      const now = new Date();
      const diffMs = now - date;
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);
      const diffDays = Math.floor(diffMs / 86400000);

      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffHours < 24) return `${diffHours}h ago`;
      return `${diffDays}d ago`;
    } catch {
      return 'Unknown';
    }
  };

  return (
    <div className="session-list">
      <div className="section-header">
        <h3 className="section-title">Chat Sessions</h3>
        <button 
          className="new-session-btn"
          onClick={handleNewSession}
          title="Start new chat"
        >
          <Plus size={16} />
        </button>
      </div>

      {sessionsLoading ? (
        <div className="loading-state">
          <Loader size={20} className="animate-spin" />
          <span>Loading sessions...</span>
        </div>
      ) : sessions.length === 0 ? (
        <div className="empty-state">
          <MessageSquare size={24} />
          <span>No chat sessions yet</span>
          <button 
            className="start-chat-btn"
            onClick={handleNewSession}
          >
            Start your first chat
          </button>
        </div>
      ) : (
        <div className="sessions-container">
          {sessions.map((session) => (
            <div 
              key={session.session_id}
              className={`session-item ${session.session_id === currentSessionId ? 'active' : ''}`}
            >
              <div 
                className="session-content"
                onClick={() => handleSwitchSession(session.session_id)}
              >
                <div className="session-header">
                  <MessageSquare size={16} className="session-icon" />
                  <div className="session-info">
                    <span className="session-id">
                      {session.session_id.slice(0, 8)}...
                    </span>
                    <span className="message-count">
                      {session.message_count} message{session.message_count !== 1 ? 's' : ''}
                    </span>
                  </div>
                </div>
                
                <div className="session-meta">
                  <div className="meta-item">
                    <Clock size={12} />
                    <span>{formatTimeAgo(session.created_at)}</span>
                  </div>
                  {session.last_message && (
                    <div className="last-message">
                      {session.last_message.content?.slice(0, 50)}...
                    </div>
                  )}
                </div>
              </div>
              
              <button
                className="delete-btn"
                onClick={() => handleDeleteSession(session.session_id)}
                disabled={deletingSession === session.session_id}
                title="Delete session"
              >
                {deletingSession === session.session_id ? (
                  <Loader size={14} className="animate-spin" />
                ) : (
                  <Trash2 size={14} />
                )}
              </button>
            </div>
          ))}
        </div>
      )}

      <style jsx>{`
        .session-list {
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

        .new-session-btn {
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

        .new-session-btn:hover {
          background: #5a67d8;
          transform: translateY(-1px);
        }

        .loading-state, .empty-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.5rem;
          padding: 2rem;
          color: #64748b;
          text-align: center;
        }

        .start-chat-btn {
          margin-top: 0.5rem;
          padding: 0.5rem 1rem;
          background: #667eea;
          color: white;
          border: none;
          border-radius: 6px;
          font-size: 0.85rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .start-chat-btn:hover {
          background: #5a67d8;
        }

        .sessions-container {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          max-height: 400px;
          overflow-y: auto;
        }

        .session-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background: #f8fafc;
          border: 1px solid #e2e8f0;
          border-radius: 6px;
          padding: 0.75rem;
          transition: all 0.2s;
        }

        .session-item:hover {
          border-color: #cbd5e1;
          background: #f1f5f9;
        }

        .session-item.active {
          border-color: #667eea;
          background: #eff6ff;
        }

        .session-content {
          flex: 1;
          cursor: pointer;
          min-width: 0;
        }

        .session-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.25rem;
        }

        .session-icon {
          color: #667eea;
          flex-shrink: 0;
        }

        .session-info {
          display: flex;
          flex-direction: column;
          min-width: 0;
        }

        .session-id {
          font-size: 0.85rem;
          font-weight: 500;
          color: #1e293b;
          font-family: monospace;
        }

        .message-count {
          font-size: 0.75rem;
          color: #64748b;
        }

        .session-meta {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .meta-item {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          font-size: 0.75rem;
          color: #64748b;
        }

        .last-message {
          font-size: 0.75rem;
          color: #475569;
          font-style: italic;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .delete-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 28px;
          height: 28px;
          background: #ef4444;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          transition: all 0.2s;
          flex-shrink: 0;
        }

        .delete-btn:hover:not(:disabled) {
          background: #dc2626;
          transform: scale(1.05);
        }

        .delete-btn:disabled {
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

export default SessionList; 