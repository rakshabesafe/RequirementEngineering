import React, { useState } from 'react';
import axios from 'axios';

const RequirementsGenerator = ({ project, document }) => {
  const [prompt, setPrompt] = useState('Generate user stories for the key features described in the document.');
  const [jiraProjectKey, setJiraProjectKey] = useState('PROJ');
  const [message, setMessage] = useState({ type: 'info', text: 'Ready to begin generation.' });
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setResults(null);
    setMessage(null);

    try {
      // Step 1: Ingest the document
      setMessage({ type: 'info', text: 'Step 1/2: Ingesting document into vector store... (This may take a moment)' });
      const ingestUrl = `/req-agent-api/projects/${project.id}/ingest-document`;
      await axios.post(ingestUrl, {
        bucket_name: `project-${project.id}`,
        object_name: document.name,
      });
      setMessage({ type: 'info', text: 'Document ingested successfully. Step 2/2: Generating requirements and pushing to Jira...' });

      // Step 2: Trigger the generation process
      const generateUrl = `/req-agent-api/projects/${project.id}/generate-requirements`;
      const response = await axios.post(generateUrl, {
        initial_prompt: prompt,
        jira_project_key: jiraProjectKey,
      });

      setMessage({ type: 'success', text: 'Successfully generated requirements and pushed to Jira!' });
      setResults(response.data.final_state);

    } catch (error) {
      const errorText = error.response?.data?.detail || 'An unexpected error occurred.';
      setMessage({ type: 'error', text: `Error: ${errorText}` });
      console.error("Error generating requirements:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="prompt">Analysis Prompt</label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows="3"
            disabled={isLoading}
          />
        </div>
        <div className="form-group">
          <label htmlFor="jiraKey">Jira Project Key</label>
          <input
            type="text"
            id="jiraKey"
            value={jiraProjectKey}
            onChange={(e) => setJiraProjectKey(e.target.value.toUpperCase())}
            placeholder="e.g., 'PROJ'"
            disabled={isLoading}
          />
        </div>
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Processing...' : 'Generate & Push to Jira'}
        </button>
      </form>

      {message && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      {results && (
        <div className="results-output">
          <h3>Generation Results</h3>
          <pre>{JSON.stringify(results.jira_results, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default RequirementsGenerator;
