import React, { useState } from 'react';
import './App.css';
import ProjectCreator from './components/ProjectCreator';
import DocumentUploader from './components/DocumentUploader';
import RequirementsGenerator from './components/RequirementsGenerator';

function App() {
  const [currentProject, setCurrentProject] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);

  const handleProjectCreated = (project) => {
    setCurrentProject(project);
    setUploadedFile(null); // Reset file when project changes
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI SDLC Platform</h1>
      </header>
      <main className="App-main">
        <div className="workflow-container">
          <div className="workflow-step">
            <h2>Step 1: Create a Project</h2>
            <ProjectCreator onProjectCreated={handleProjectCreated} />
          </div>

          {currentProject && (
            <div className="workflow-step">
              <h2>Step 2: Upload Requirements Document</h2>
              <p>Current Project: <strong>{currentProject.name} (ID: {currentProject.id})</strong></p>
              <DocumentUploader
                project={currentProject}
                onUploadSuccess={setUploadedFile}
              />
            </div>
          )}

          {currentProject && uploadedFile && (
            <div className="workflow-step">
              <h2>Step 3: Generate Requirements</h2>
               <p>Ready to process <strong>{uploadedFile.name}</strong> for project <strong>{currentProject.name}</strong>.</p>
              <RequirementsGenerator
                project={currentProject}
                document={uploadedFile}
              />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
