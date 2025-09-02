import React, { useState } from 'react';
import axios from 'axios';

const DocumentUploader = ({ project, onUploadSuccess }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [message, setMessage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    setMessage(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setMessage({ type: 'error', text: 'Please select a file to upload.' });
      return;
    }

    setIsLoading(true);
    setMessage(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      // The path includes the project ID and the endpoint defined in the project-input-service
      const url = `/project-api/projects/${project.id}/documents/`;
      const response = await axios.post(url, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setMessage({ type: 'success', text: `File "${response.data.filename}" uploaded successfully!` });
      onUploadSuccess({ name: response.data.filename, location: response.data.location });
    } catch (error) {
      const errorText = error.response?.data?.detail || 'An unexpected error occurred during upload.';
      setMessage({ type: 'error', text: `Error: ${errorText}` });
      console.error("Error uploading document:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="document">Select Document</label>
          <input
            type="file"
            id="document"
            onChange={handleFileChange}
            disabled={isLoading}
          />
        </div>
        <button type="submit" disabled={isLoading || !selectedFile}>
          {isLoading ? 'Uploading...' : 'Upload Document'}
        </button>
      </form>
      {message && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}
    </div>
  );
};

export default DocumentUploader;
