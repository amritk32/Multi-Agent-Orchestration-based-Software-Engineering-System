import { useEffect, useState } from 'react';
import { Activity, AlertCircle, ArrowLeft, FileCode2, FolderOpen, Loader2, Trash2, X } from 'lucide-react';
import { apiClient, ProjectDetails, ProjectSummary } from '../api';

interface OpenProjectProps {
  onBack: () => void;
  onOpenProject: (project: ProjectDetails) => void;
}

export default function OpenProject({ onBack, onOpenProject }: OpenProjectProps) {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [selectedProject, setSelectedProject] = useState<ProjectDetails | null>(null);
  const [activeTab, setActiveTab] = useState('code');
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
  const [projectToDelete, setProjectToDelete] = useState<ProjectSummary | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    let isMounted = true;

    const loadProjects = async () => {
      try {
        const savedProjects = await apiClient.getProjects();
        if (isMounted) {
          setProjects(savedProjects);
          setError('');
        }
      } catch (requestError) {
        if (isMounted) {
          setError(requestError instanceof Error ? requestError.message : 'Unable to load projects.');
        }
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };

    void loadProjects();
    return () => {
      isMounted = false;
    };
  }, []);

  const openProject = async (projectId: string) => {
    setIsLoadingDetails(true);
    setError('');
    try {
      const details = await apiClient.getProject(projectId);
      setSelectedProject(details);
      setActiveTab('code');
      onOpenProject(details);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Unable to open project.');
    } finally {
      setIsLoadingDetails(false);
    }
  };

  const deleteProject = async () => {
    if (!projectToDelete) return;

    setIsDeleting(true);
    setError('');
    try {
      await apiClient.deleteProject(projectToDelete.project_id);
      setProjects((currentProjects) => currentProjects.filter(
        (project) => project.project_id !== projectToDelete.project_id,
      ));
      if (selectedProject?.project_id === projectToDelete.project_id) {
        setSelectedProject(null);
      }
      setProjectToDelete(null);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Unable to delete project.');
    } finally {
      setIsDeleting(false);
    }
  };

  const artifactContent = selectedProject?.artifacts
    ? {
        code: selectedProject.artifacts.generated_code,
        requirements: selectedProject.artifacts.requirements,
        architecture: selectedProject.artifacts.architecture,
        boilerplate: selectedProject.artifacts.boilerplate,
        readme: selectedProject.artifacts.readme,
      }
    : null;

  return (
    <div className="signal-shell">
      <header className="signal-header">
        <button onClick={onBack} className="header-back-button" title="Back to home">
          <ArrowLeft size={16} /> Home
        </button>
        <div className="brand-mark">
          <span className="brand-icon"><Activity size={21} /></span> krishna.code
        </div>
        <div className="network-status">
          <span className="status-dot" />
          <span className="mono-label">Agent network online</span>
        </div>
      </header>

      <main className="open-project-layout">
        <div className="open-project-container open-project-browser">
          <div className="eyebrow">Intelligence workspace / 02</div>
          <h1 className="open-project-title">Open Project</h1>
          <p className="open-project-description">
            Browse your saved projects and reopen the work produced by the agent network.
          </p>

          {error && (
            <div className="project-browser-error">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          <div className="project-browser-grid">
            <section className="project-list-panel">
              <div className="project-panel-heading">
                <span className="mono-label">Saved projects</span>
                <span className="project-count">{projects.length}</span>
              </div>

              {isLoading ? (
                <div className="project-state"><Loader2 className="project-spinner" size={22} /><span>Loading projects...</span></div>
              ) : projects.length === 0 ? (
                <div className="project-state">
                  <FolderOpen size={30} />
                  <strong>No projects yet</strong>
                  <span>Create a new project to see it here.</span>
                  <button onClick={onBack} className="placeholder-button">Create New Project</button>
                </div>
              ) : (
                <div className="project-list">
                  {projects.map((project) => (
                    <div
                      key={project.project_id}
                      className={`project-list-item ${selectedProject?.project_id === project.project_id ? 'selected' : ''}`}
                      onClick={() => void openProject(project.project_id)}
                      onKeyDown={(event) => {
                        if (event.key === 'Enter' || event.key === ' ') {
                          event.preventDefault();
                          void openProject(project.project_id);
                        }
                      }}
                      role="button"
                      tabIndex={0}
                    >
                      <span className="project-list-icon"><FolderOpen size={17} /></span>
                      <span className="project-list-copy">
                        <strong>{project.project_name}</strong>
                        <small>{new Date(project.created_at).toLocaleDateString()}</small>
                      </span>
                      <button
                        type="button"
                        className="project-delete-button"
                        onClick={(event) => {
                          event.stopPropagation();
                          setProjectToDelete(project);
                        }}
                        title={`Delete ${project.project_name}`}
                      >
                        <Trash2 size={14} />
                        <span>DELETE</span>
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </section>

            <section className="project-detail-panel">
              {isLoadingDetails ? (
                <div className="project-state"><Loader2 className="project-spinner" size={24} /><span>Opening project...</span></div>
              ) : selectedProject ? (
                <>
                  <div className="project-detail-header">
                    <div>
                      <span className="mono-label">Project details</span>
                      <h2>{selectedProject.project_name}</h2>
                    </div>
                    <span className="project-detail-date">Created {new Date(selectedProject.created_at).toLocaleString()}</span>
                  </div>
                  <div className="project-detail-tabs">
                    {[
                      ['code', 'Generated Code'],
                      ['requirements', 'Requirements'],
                      ['architecture', 'Architecture'],
                      ['boilerplate', 'Boilerplate'],
                    ].map(([id, label]) => (
                      <button key={id} className={activeTab === id ? 'active' : ''} onClick={() => setActiveTab(id)}>{label}</button>
                    ))}
                  </div>
                  <div className="project-detail-content">
                    <div className="project-content-heading"><FileCode2 size={16} /><span>{activeTab === 'code' ? 'Generated Code' : activeTab}</span></div>
                    <pre>{artifactContent?.[activeTab as keyof NonNullable<typeof artifactContent>] || 'No saved data for this section.'}</pre>
                  </div>
                </>
              ) : (
                <div className="project-state project-select-state"><FolderOpen size={38} /><strong>Select a project</strong><span>Choose a saved project to view its generated artifacts.</span></div>
              )}
            </section>
          </div>
        </div>
      </main>

      {projectToDelete && (
        <>
          <div
            className="delete-project-backdrop"
            onClick={() => !isDeleting && setProjectToDelete(null)}
            role="presentation"
          />
          <div className="delete-project-modal" role="dialog" aria-modal="true" aria-labelledby="delete-project-title">
            <div className="delete-project-modal-content">
              <div className="delete-project-modal-header">
                <div>
                  <span className="mono-label delete-project-kicker">Permanent action</span>
                  <h2 id="delete-project-title">Delete project?</h2>
                </div>
                <button type="button" className="delete-project-close" onClick={() => setProjectToDelete(null)} disabled={isDeleting} title="Close">
                  <X size={18} />
                </button>
              </div>
              <div className="delete-project-modal-body">
                <p>Are you sure you want to delete <strong>{projectToDelete.project_name}</strong>?</p>
                <span>This action can't be undone. The project and its saved artifacts will be permanently removed.</span>
              </div>
              <div className="delete-project-modal-footer">
                <button type="button" className="modal-button modal-button-cancel" onClick={() => setProjectToDelete(null)} disabled={isDeleting}>
                  No, keep it
                </button>
                <button type="button" className="modal-button delete-confirm-button" onClick={() => void deleteProject()} disabled={isDeleting}>
                  <Trash2 size={15} />
                  {isDeleting ? 'Deleting...' : 'Yes, delete'}
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
