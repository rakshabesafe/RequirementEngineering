import React, { useState } from 'react';
import axios from 'axios';

const ProjectCreator = ({ onProjectCreated }) => {
  const [projectName, setProjectName] = useState('');
  const [message, setMessage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!projectName) {
      setMessage({ type: 'error', text: 'Please enter a project name.' });
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      // The request goes to the Kong Gateway, which routes it.
      // The path is `/project-api/projects/` but since we used `strip_path: true`
      // in kong.yml, Kong forwards `/projects/` to the service.
      // So the frontend just needs to know the gateway's API prefix.
      const response = await axios.post('/project-api/projects/', { name: projectName });

      setMessage({ type: 'success', text: `Project "${response.data.name}" created successfully!` });
      onProjectCreated(response.data);
      setProjectName(''); // Reset form
    } catch (error) {
      const errorText = error.response?.data?.detail || 'An unexpected error occurred.';
      setMessage({ type: 'error', text: `Error: ${errorText}` });
      console.error("Error creating project:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="projectName">Project Name</label>
          <input
            type="text"
            id="projectName"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            placeholder="e.g., 'E-commerce Platform'"
            disabled={isLoading}
          />
        </div>
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Creating...' : 'Create Project'}
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

export default ProjectCreator;
