import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useFileStore } from '../../store/fileStore';
import { Upload, FileText, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';

const FileUpload = () => {
  const { uploadFile, isUploading } = useFileStore();

  const onDrop = useCallback(
    async (acceptedFiles) => {
      const file = acceptedFiles[0];
      if (!file) return;

      if (file.type !== 'application/pdf') {
        toast.error('Please upload a PDF file');
        return;
      }

      if (file.size > 50 * 1024 * 1024) {
        toast.error('File size must be less than 50MB');
        return;
      }

      try {
        await uploadFile(file);
        toast.success('File uploaded successfully!');
      } catch (error) {
        toast.error('Failed to upload file');
      }
    },
    [uploadFile]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: false,
    disabled: isUploading
  });

  return (
    <div className="file-upload">
      <h3 className="section-title">Upload Document</h3>
      
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'drag-active' : ''} ${
          isDragReject ? 'drag-reject' : ''
        } ${isUploading ? 'uploading' : ''}`}
      >
        <input {...getInputProps()} />
        
        <div className="dropzone-content">
          {isUploading ? (
            <>
              <div className="spinner" />
              <p>Uploading and processing...</p>
            </>
          ) : isDragReject ? (
            <>
              <AlertCircle className="dropzone-icon error" />
              <p>Only PDF files are supported</p>
            </>
          ) : isDragActive ? (
            <>
              <Upload className="dropzone-icon active" />
              <p>Drop your PDF here</p>
            </>
          ) : (
            <>
              <FileText className="dropzone-icon" />
              <p>
                <strong>Click to upload</strong> or drag and drop
              </p>
              <p className="dropzone-hint">PDF files only (max 50MB)</p>
            </>
          )}
        </div>
      </div>

      <style jsx>{`
        .file-upload {
          width: 100%;
        }

        .section-title {
          font-size: 1.1rem;
          font-weight: 600;
          color: #1e293b;
          margin-bottom: 1rem;
        }

        .dropzone {
          border: 2px dashed #cbd5e1;
          border-radius: 12px;
          padding: 2rem 1rem;
          text-align: center;
          cursor: pointer;
          transition: all 0.3s ease;
          background: #f8fafc;
        }

        .dropzone:hover:not(.uploading) {
          border-color: #667eea;
          background: #f1f5f9;
        }

        .dropzone.drag-active {
          border-color: #667eea;
          background: #eff6ff;
          transform: scale(1.02);
        }

        .dropzone.drag-reject {
          border-color: #ef4444;
          background: #fef2f2;
        }

        .dropzone.uploading {
          border-color: #667eea;
          background: #f1f5f9;
          cursor: not-allowed;
        }

        .dropzone-content {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.75rem;
        }

        .dropzone-icon {
          width: 40px;
          height: 40px;
          color: #64748b;
          transition: color 0.2s;
        }

        .dropzone-icon.active {
          color: #667eea;
        }

        .dropzone-icon.error {
          color: #ef4444;
        }

        .dropzone p {
          margin: 0;
          color: #475569;
          font-size: 0.9rem;
        }

        .dropzone-hint {
          font-size: 0.8rem !important;
          color: #64748b !important;
        }

        .spinner {
          width: 40px;
          height: 40px;
          border: 3px solid #e2e8f0;
          border-top: 3px solid #667eea;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default FileUpload;
