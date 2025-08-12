import React from 'react';
import { MessageSquare, Upload, FileText, MessageCircle } from 'lucide-react';

const EmptyState = () => {
  return (
    <div className="empty-state">
      <div className="empty-content">
        <div className="empty-icon">
          <MessageSquare size={64} />
        </div>
        
        <h2 className="empty-title">Welcome to AI Document Chat</h2>
        <p className="empty-description">
          Upload your PDF documents and start having intelligent conversations with your content.
        </p>
        
        <div className="steps">
          <div className="step">
            <div className="step-icon">
              <Upload size={24} />
            </div>
            <div className="step-content">
              <h3>1. Upload Documents</h3>
              <p>Add PDF files to your document library</p>
            </div>
          </div>
          
          <div className="step">
            <div className="step-icon">
              <FileText size={24} />
            </div>
            <div className="step-content">
              <h3>2. Select Documents</h3>
              <p>Choose which documents to include in your chat</p>
            </div>
          </div>
          
          <div className="step">
            <div className="step-icon">
              <MessageCircle size={24} />
            </div>
            <div className="step-content">
              <h3>3. Start Chatting</h3>
              <p>Ask questions and get AI-powered insights</p>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .empty-state {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 2rem;
        }

        .empty-content {
          text-align: center;
          max-width: 500px;
        }

        .empty-icon {
          color: #cbd5e1;
          margin-bottom: 2rem;
          display: flex;
          justify-content: center;
        }

        .empty-title {
          font-size: 2rem;
          font-weight: 700;
          color: #1e293b;
          margin: 0 0 1rem 0;
        }

        .empty-description {
          font-size: 1.1rem;
          color: #64748b;
          margin: 0 0 3rem 0;
          line-height: 1.6;
        }

        .steps {
          display: flex;
          flex-direction: column;
          gap: 2rem;
          text-align: left;
        }

        .step {
          display: flex;
          align-items: flex-start;
          gap: 1rem;
          padding: 1.5rem;
          background: white;
          border: 1px solid #e2e8f0;
          border-radius: 12px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          transition: all 0.2s;
        }

        .step:hover {
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          transform: translateY(-1px);
        }

        .step-icon {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          width: 48px;
          height: 48px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }

        .step-content h3 {
          margin: 0 0 0.5rem 0;
          font-size: 1.1rem;
          font-weight: 600;
          color: #1e293b;
        }

        .step-content p {
          margin: 0;
          color: #64748b;
          line-height: 1.5;
        }

        @media (max-width: 768px) {
          .empty-state {
            padding: 1rem;
          }

          .empty-title {
            font-size: 1.5rem;
          }

          .empty-description {
            font-size: 1rem;
          }

          .steps {
            gap: 1.5rem;
          }

          .step {
            padding: 1.25rem;
          }

          .step-icon {
            width: 40px;
            height: 40px;
          }
        }
      `}</style>
    </div>
  );
};

export default EmptyState;
