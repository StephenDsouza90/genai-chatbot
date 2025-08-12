import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Bot, User, Loader } from 'lucide-react';

const ChatMessage = ({ message, isLast }) => {
  const isUser = message.role === 'user';
  const isLoading = message.isLoading;

  return (
    <div className={`message-container ${isUser ? 'user' : 'assistant'} ${isLast ? 'animate-fade-in' : ''}`}>
      <div className="message-wrapper">
        <div className="message-avatar">
          {isUser ? <User size={20} /> : <Bot size={20} />}
        </div>
        
        <div className="message-content">
          <div className="message-bubble">
            {isLoading ? (
              <div className="loading-content">
                <Loader className="animate-spin" size={16} />
                <span>Thinking...</span>
              </div>
            ) : (
              <ReactMarkdown className="markdown-content">
                {message.content}
              </ReactMarkdown>
            )}
          </div>
          
          {message.sources && message.sources.length > 0 && (
            <div className="message-sources">
              <h4>Sources:</h4>
              <ul>
                {message.sources.map((source, index) => (
                  <li key={index}>{source}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        .message-container {
          padding: 0 2rem;
          margin-bottom: 1.5rem;
        }

        .message-container.user {
          display: flex;
          justify-content: flex-end;
        }

        .message-container.assistant {
          display: flex;
          justify-content: flex-start;
        }

        .message-wrapper {
          display: flex;
          gap: 0.75rem;
          max-width: 70%;
          width: 100%;
        }

        .message-container.user .message-wrapper {
          flex-direction: row-reverse;
        }

        .message-avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
          margin-top: 0.25rem;
        }

        .message-container.user .message-avatar {
          background: #667eea;
          color: white;
        }

        .message-container.assistant .message-avatar {
          background: #f1f5f9;
          color: #64748b;
          border: 2px solid #e2e8f0;
        }

        .message-content {
          flex: 1;
          min-width: 0;
        }

        .message-bubble {
          padding: 1rem 1.25rem;
          border-radius: 18px;
          word-wrap: break-word;
          line-height: 1.6;
        }

        .message-container.user .message-bubble {
          background: #667eea;
          color: white;
          border-bottom-right-radius: 6px;
        }

        .message-container.assistant .message-bubble {
          background: white;
          color: #1e293b;
          border: 1px solid #e2e8f0;
          border-bottom-left-radius: 6px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .loading-content {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: #64748b;
        }

        .markdown-content {
          margin: 0;
        }

        .markdown-content p {
          margin: 0 0 0.75rem 0;
        }

        .markdown-content p:last-child {
          margin-bottom: 0;
        }

        .markdown-content h1,
        .markdown-content h2,
        .markdown-content h3,
        .markdown-content h4,
        .markdown-content h5,
        .markdown-content h6 {
          margin: 1rem 0 0.5rem 0;
          font-weight: 600;
        }

        .markdown-content h1:first-child,
        .markdown-content h2:first-child,
        .markdown-content h3:first-child,
        .markdown-content h4:first-child,
        .markdown-content h5:first-child,
        .markdown-content h6:first-child {
          margin-top: 0;
        }

        .markdown-content ul,
        .markdown-content ol {
          margin: 0.75rem 0;
          padding-left: 1.5rem;
        }

        .markdown-content li {
          margin-bottom: 0.25rem;
        }

        .markdown-content code {
          background: ${isUser ? 'rgba(255, 255, 255, 0.2)' : '#f1f5f9'};
          padding: 0.125rem 0.375rem;
          border-radius: 4px;
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
          font-size: 0.875em;
        }

        .markdown-content pre {
          background: ${isUser ? 'rgba(255, 255, 255, 0.1)' : '#f8fafc'};
          padding: 1rem;
          border-radius: 8px;
          overflow-x: auto;
          margin: 0.75rem 0;
        }

        .markdown-content pre code {
          background: none;
          padding: 0;
        }

        .message-sources {
          margin-top: 0.75rem;
          padding: 0.75rem 1rem;
          background: #f0f9ff;
          border: 1px solid #bae6fd;
          border-radius: 8px;
          font-size: 0.85rem;
        }

        .message-sources h4 {
          margin: 0 0 0.5rem 0;
          font-size: 0.8rem;
          font-weight: 600;
          color: #0369a1;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .message-sources ul {
          margin: 0;
          padding-left: 1.25rem;
          color: #075985;
        }

        .message-sources li {
          margin-bottom: 0.25rem;
        }

        @media (max-width: 768px) {
          .message-container {
            padding: 0 1rem;
          }

          .message-wrapper {
            max-width: 85%;
          }

          .message-avatar {
            width: 36px;
            height: 36px;
          }

          .message-bubble {
            padding: 0.875rem 1rem;
          }
        }
      `}</style>
    </div>
  );
};

export default ChatMessage;
