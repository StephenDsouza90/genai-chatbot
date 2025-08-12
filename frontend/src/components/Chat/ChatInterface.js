import React, { useRef, useEffect } from 'react';
import { useChatStore } from '../../store/chatStore';
import { useFileStore } from '../../store/fileStore';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import EmptyState from './EmptyState';

const ChatInterface = () => {
  const messagesEndRef = useRef(null);
  const { messages, isLoading } = useChatStore();
  const { selectedFiles } = useFileStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const showEmptyState = messages.length === 0 && !isLoading;

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <div className="header-content">
          <h2 className="chat-title">AI Assistant</h2>
          <p className="chat-subtitle">
            {selectedFiles.length > 0 
              ? `Chatting with ${selectedFiles.length} document${selectedFiles.length > 1 ? 's' : ''}`
              : 'Select documents to start chatting'
            }
          </p>
        </div>
      </div>

      <div className="chat-messages">
        {showEmptyState ? (
          <EmptyState />
        ) : (
          <>
            {messages.map((message, index) => (
              <ChatMessage
                key={index}
                message={message}
                isLast={index === messages.length - 1}
              />
            ))}
            {isLoading && (
              <ChatMessage
                message={{
                  role: 'assistant',
                  content: '',
                  isLoading: true
                }}
                isLast={true}
              />
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <ChatInput disabled={selectedFiles.length === 0} />

      <style jsx>{`
        .chat-interface {
          height: 100%;
          display: flex;
          flex-direction: column;
          background: white;
        }

        .chat-header {
          padding: 1.5rem 2rem;
          border-bottom: 1px solid #e2e8f0;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .header-content {
          max-width: 4xl;
          margin: 0 auto;
        }

        .chat-title {
          font-size: 1.5rem;
          font-weight: 700;
          color: white;
          margin: 0 0 0.25rem 0;
        }

        .chat-subtitle {
          font-size: 0.9rem;
          color: rgba(255, 255, 255, 0.8);
          margin: 0;
        }

        .chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 1rem 0;
          background: #f8fafc;
        }

        @media (max-width: 768px) {
          .chat-header {
            padding: 1rem;
          }
          
          .chat-title {
            font-size: 1.25rem;
          }
        }
      `}</style>
    </div>
  );
};

export default ChatInterface;
