import { useState } from 'react';
import { ArrowUpRight, X } from 'lucide-react';
import { API_BASE_URL } from '../api';

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateProject: (projectName: string, projectId: string) => void;
  isLoading: boolean;
}

export default function CreateProjectModal({
  isOpen,
  onClose,
  onCreateProject,
  isLoading,
}: CreateProjectModalProps) {
  const [projectName, setProjectName] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const busy = isLoading || isSubmitting;

  if (!isOpen) return null;

  const handleSubmit = async () => {
    if (!projectName.trim()) {
      setError('Project name cannot be empty');
      return;
    }

    try {
      setIsSubmitting(true);
      setError('');
      const response = await fetch(`${API_BASE_URL}/api/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_name: projectName,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create project');
      }

      const project = await response.json();
      onCreateProject(project.project_name, project.project_id);
      setProjectName('');
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !busy) {
      handleSubmit();
    }
    if (e.key === 'Escape') {
      onClose();
    }
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="create-project-backdrop"
        onClick={onClose}
        role="presentation"
      />

      {/* Modal */}
      <div className="create-project-modal">
        <div className="modal-content">
          {/* Header */}
          <div className="modal-header">
            <h2 className="modal-title">Create New Project</h2>
            <button
              onClick={onClose}
              className="modal-close-button"
              title="Close"
              disabled={busy}
            >
              <X size={20} />
            </button>
          </div>

          {/* Body */}
          <div className="modal-body">
            <label htmlFor="project-name" className="modal-label">
              Project Name
            </label>
            <textarea
              id="project-name"
              value={projectName}
              onChange={(e) => {
                setProjectName(e.target.value);
                setError('');
              }}
              onKeyDown={handleKeyDown}
              placeholder="e.g. Todo App Backend, E-commerce Platform, etc."
              className="modal-input"
              rows={2}
              disabled={busy}
              autoFocus
            />
            {error && <p className="modal-error">{error}</p>}
          </div>

          {/* Footer */}
          <div className="modal-footer">
            <button
              onClick={onClose}
              className="modal-button modal-button-cancel"
              disabled={busy}
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              className="modal-button modal-button-create"
              disabled={isLoading}
            >
              {busy ? (
                <>
                  <span className="animate-spin inline-block">⏳</span> Creating...
                </>
              ) : (
                <>
                  <span>Create Project</span>
                  <ArrowUpRight size={16} />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
