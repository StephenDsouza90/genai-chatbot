import React from 'react';
import { useFileStore } from '../../store/fileStore';
import { useChatStore } from '../../store/chatStore';
import { FileText, Check, Loader, Calendar, HardDrive } from 'lucide-react';
import { formatDistanceToNow } from '../../utils/dateUtils';
import { formatFileSize } from '../../utils/fileUtils';

const FileList = () => {
  const { files, isLoading, selectedFiles, toggleFileSelection } = useFileStore();
  const { clearChat } = useChatStore();

  const handleFileToggle = (fileId) => {
    toggleFileSelection(fileId);
    clearChat(); // Clear chat when changing file selection
  };

  if (isLoading) {
    return (
      <div className="file-list">
        <h3 className="section-title">Your Documents</h3>
        <div className="loading-state">
          <Loader className="animate-spin" />
          <p>Loading documents...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="file-list">
      <h3 className="section-title">
        Your Documents {files.length > 0 && `(${files.length})`}
      </h3>

      {files.length === 0 ? (
        <div className="empty-state">
          <FileText className="empty-icon" />
          <p>No documents uploaded yet</p>
          <p className="empty-hint">Upload a PDF to get started</p>
        </div>
      ) : (
        <div className="files-container">
          {files.map((file) => (
            <div
              key={file.id}
              className={`file-item ${selectedFiles.includes(file.id) ? 'selected' : ''}`}
              onClick={() => handleFileToggle(file.id)}
            >
              <div className="file-checkbox">
                {selectedFiles.includes(file.id) && <Check size={14} />}
              </div>
              
              <div className="file-icon">
                <FileText size={20} />
              </div>
              
              <div className="file-details">
                <h4 className="file-name" title={file.filename}>
                  {file.filename}
                </h4>
                <div className="file-meta">
                  <span className="file-meta-item">
                    <Calendar size={12} />
                    {formatDistanceToNow(new Date(file.upload_date))}
                  </span>
                  <span className="file-meta-item">
                    <HardDrive size={12} />
                    {formatFileSize(file.file_size)}
                  </span>
                </div>
                <div className="file-chunks">
                  {file.chunk_count} chunks processed
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedFiles.length > 0 && (
        <div className="selection-info">
          <p>{selectedFiles.length} document{selectedFiles.length > 1 ? 's' : ''} selected for chat</p>
        </div>
      )}

      <style jsx>{`
        .file-list {
          flex: 1;
          display: flex;
          flex-direction: column;
        }

        .section-title {
          font-size: 1.1rem;
          font-weight: 600;
          color: #1e293b;
          margin-bottom: 1rem;
        }

        .loading-state, .empty-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1rem;
          padding: 2rem 1rem;
          color: #64748b;
          text-align: center;
        }

        .empty-icon {
          width: 48px;
          height: 48px;
          color: #cbd5e1;
        }

        .empty-hint {
          font-size: 0.85rem;
          color: #94a3b8;
        }

        .files-container {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
          max-height: 400px;
          overflow-y: auto;
        }

        .file-item {
          display: flex;
          align-items: flex-start;
          gap: 0.75rem;
          padding: 1rem;
          border: 1px solid #e2e8f0;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
          background: white;
        }

        .file-item:hover {
          border-color: #667eea;
          box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
        }

        .file-item.selected {
          border-color: #667eea;
          background: #f0f4ff;
          box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
        }

        .file-checkbox {
          width: 18px;
          height: 18px;
          border: 2px solid #d1d5db;
          border-radius: 4px;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
          flex-shrink: 0;
          margin-top: 2px;
        }

        .file-item.selected .file-checkbox {
          background: #667eea;
          border-color: #667eea;
          color: white;
        }

        .file-icon {
          color: #667eea;
          flex-shrink: 0;
          margin-top: 2px;
        }

        .file-details {
          flex: 1;
          min-width: 0;
        }

        .file-name {
          font-size: 0.9rem;
          font-weight: 500;
          color: #1e293b;
          margin: 0 0 0.5rem 0;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .file-meta {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
          margin-bottom: 0.5rem;
        }

        .file-meta-item {
          display: flex;
          align-items: center;
          gap: 0.375rem;
          font-size: 0.75rem;
          color: #64748b;
        }

        .file-chunks {
          font-size: 0.75rem;
          color: #10b981;
          font-weight: 500;
        }

        .selection-info {
          margin-top: 1rem;
          padding: 0.75rem;
          background: #f0f9ff;
          border: 1px solid #bae6fd;
          border-radius: 6px;
          text-align: center;
        }

        .selection-info p {
          margin: 0;
          font-size: 0.85rem;
          color: #0369a1;
          font-weight: 500;
        }
      `}</style>
    </div>
  );
};

export default FileList;

