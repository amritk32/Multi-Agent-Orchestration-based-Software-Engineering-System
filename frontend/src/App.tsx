import { useState } from 'react';
import HomePage from './components/HomePage';
import ProjectWorkflow from './components/ProjectWorkflow';
import OpenProject from './components/OpenProject';
import { ProjectDetails } from './api';
import { GenerationResult } from './types';
import './styles.css';

type AppScreen = 'home' | 'new-project' | 'open-project';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<AppScreen>('home');
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [selectedProjectName, setSelectedProjectName] = useState<string | null>(null);
  const [initialResult, setInitialResult] = useState<GenerationResult | null>(null);

  const handleNavigateToNewProject = (projectId: string, projectName: string) => {
    setSelectedProjectId(projectId);
    setSelectedProjectName(projectName);
    setInitialResult(null);
    setCurrentScreen('new-project');
  };

  const handleOpenExistingProject = (project: ProjectDetails) => {
    setSelectedProjectId(project.project_id);
    setSelectedProjectName(project.project_name);
    setInitialResult(project.artifacts ? {
      requirements: project.artifacts.requirements || '',
      architecture: project.artifacts.architecture || '',
      boilerplate: project.artifacts.boilerplate || '',
      code: project.artifacts.generated_code || '',
      backend_code: project.artifacts.backend_code || '',
      frontend_code: project.artifacts.frontend_code || '',
      report: project.artifacts.readme || '',
    } : null);
    setCurrentScreen('new-project');
  };

  const handleNavigateToOpenProject = () => {
    setCurrentScreen('open-project');
  };

  const handleNavigateHome = () => {
    setCurrentScreen('home');
  };

  return (
    <>
      {currentScreen === 'home' && (
        <HomePage
          onNewProject={handleNavigateToNewProject}
          onOpenProject={handleNavigateToOpenProject}
        />
      )}
      {currentScreen === 'new-project' && (
        <ProjectWorkflow 
          onBack={handleNavigateHome}
          projectId={selectedProjectId || ''}
          projectName={selectedProjectName || ''}
          initialResult={initialResult}
        />
      )}
      {currentScreen === 'open-project' && (
        <OpenProject onBack={handleNavigateHome} onOpenProject={handleOpenExistingProject} />
      )}
    </>
  );
}
