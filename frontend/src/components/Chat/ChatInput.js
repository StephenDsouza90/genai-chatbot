import React, { useState, useRef } from 'react';
import { useChatStore } from '../../store/chatStore';
import { useFileStore } from '../../store/fileStore';
import { Send, Loader } from 'lucide-react';
import toast from 'react-hot-toast';

const ChatInput = ({ disabled }) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);
  const { sendMessage, isLoading } = useChatStore();
  const { selectedFiles } = useFileStore();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!input.trim() || isLoading || disabled) return;

    if (selectedFiles.length === 0) {
      toast.error('Please select at least one document first');
      return;
    }

    const message = input.trim();
    setInput('');
    
    try {
      await sendMessage(message, selectedFiles);
    } catch (error) {
      toast.error('Failed to send message');
      setInput(message); // Restore input on error
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
  };

  React.useEffect(() => {
    adjustTextareaHeight();
  }, [input]);

  return (
    <div className="chat-input-container">
      <div className="chat-input-wrapper">
        <form onSubmit={handleSubmit} className="chat-form">
          <div className="input-group">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                disabled 
                  ? "Select documents to start chatting..." 
                  : "Ask a question about your documents..."
              }
              disabled={disabled || isLoading}
              className="chat-textarea"
              rows={1}
            />
            
            <button
              type="submit"
              disabled={!input.trim() || isLoading || disabled}
              className="send-button"
            >
              {isLoading ? (
                <Loader className="animate-spin" size={20} />
              ) : (
                <Send size={20} />
              )}
            </button>
          </div>
        </form>
        
        <div className="input-hint">
          <p>
            {selectedFiles.length > 0 ? (
              <>Press Enter to send, Shift+Enter for new line</>
            ) : (
              <>Select documents from the sidebar to begin chatting</>
            )}
          </p>
        </div>
      </div>

      <style jsx>{`
        .chat-input-container {
          border-top: 1px solid #e2e8f0;
          background: white;
          padding: 1.5rem 2rem;
        }

        .chat-input-wrapper {
          max-width: 4xl;
          margin: 0 auto;
        }

        .chat-form {
          margin-bottom: 0.75rem;
        }

        .input-group {
          display: flex;
          align-items: flex-end;
          gap: 0.75rem;
          padding: 0.75rem;
          border: 2px solid #e2e8f0;
          border-radius: 12px;
          background: #f8fafc;
          transition: all 0.2s;
        }

        .input-group:focus-within {
          border-color: #667eea;
          background: white;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .chat-textarea {
          flex: 1;
          border: none;
          outline: none;
          background: transparent;
          resize: none;
          font-family: inherit;
          font-size: 1rem;
          line-height: 1.5;
          color: #1e293b;
          min-height: 24px;
          max-height: 120px;
        }

        .chat-textarea::placeholder {
          color: #94a3b8;
        }

        .chat-textarea:disabled {
          color: #94a3b8;
          cursor: not-allowed;
        }

        .send-button {
          background: #667eea;
          color: white;
          border: none;
          border-radius: 8px;
          padding: 0.75rem;
          cursor: pointer;
          transition: all 0.2s;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }

        .send-button:hover:not(:disabled) {
          background: #5a67d8;
          transform: translateY(-1px);
        }

        .send-button:disabled {
          background: #cbd5e1;
          cursor: not-allowed;
          transform: none;
        }

        .input-hint {
          text-align: center;
        }

        .input-hint p {
          margin: 0;
          font-size: 0.8rem;
          color: #64748b;
        }

        @media (max-width: 768px) {
          .chat-input-container {
            padding: 1rem;
          }

          .input-group {
            padding: 0.625rem;
          }

          .chat-textarea {
            font-size: 0.9rem;
          }

          .send-button {
            padding: 0.625rem;
          }
        }
      `}</style>
    </div>
  );
};

export default ChatInput;
