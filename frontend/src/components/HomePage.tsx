import { useState } from 'react';
import { Activity, ArrowRight, Sparkles, Plus, FolderOpen,ShieldCheck, ScanSearch } from 'lucide-react';
import CreateProjectModal from './CreateProjectModal';

interface HomePageProps {
  onNewProject: (projectId: string, projectName: string) => void;
  onOpenProject: () => void;
  onCyberAssessment: () => void;
}

export default function HomePage({
  onNewProject,
  onOpenProject,
  onCyberAssessment,
}: HomePageProps) {
  const [showModal, setShowModal] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleCreateProjectClick = () => {
    setShowModal(true);
  };

  const handleCreateProject = (projectName: string, projectId: string) => {
    setIsLoading(false);
    setShowModal(false);
    onNewProject(projectId, projectName);
  };
  return (
    <div className="signal-shell">
      {/* Header */}
      <header className="signal-header">
        <div className="brand-mark">
          <span className="brand-icon"><Activity size={21} /></span> krishna.code
        </div>
        <div className="network-status">
          <span className="status-dot" />
          <span className="mono-label">Agent network online</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="home-layout">
        {/* Hero Section */}
        <section className="home-hero">
          <div className="eyebrow">Intelligence workspace / 01</div>
          <h1 className="home-title">
            Turn ideas into<br />
            <em>working software.</em>
          </h1>
          <p className="home-subtitle">
            An AI-native engineering platform for designing, building, and deploying full-stack applications with an agent network that explains every decision.
          </p>
          <div className="home-features">
            <div className="feature-item">
              <span className="feature-icon"><Sparkles size={16} /></span>
              <span>AI-Powered Code Generation</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon"><Activity size={16} /></span>
              <span>Agent Network Orchestration</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon"><ArrowRight size={16} /></span>
              <span>Real-time Workflow Visualization</span>
            </div>
          </div>
        </section>

        {/* Project Options */}
        <section className="home-options">
          {/* New Project Card */}
          <div
            className="project-card new-project-card"
            onClick={handleCreateProjectClick}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                handleCreateProjectClick();
              }
            }}
          >
            <div className="card-header">
              <div className="card-icon new-project-icon">
                <Plus size={28} />
              </div>
              <h2 className="card-title">New Project</h2>
            </div>

            <p className="card-description">
              Start fresh with a new agentic project. Describe your requirements and let our AI agents design and build your full-stack application.
            </p>

            <div className="card-features">
              <div className="feature-badge">AI Design & Architecture</div>
              <div className="feature-badge">Auto Code Generation</div>
              <div className="feature-badge">README & Documentation</div>
            </div>

            <div className="card-footer">
              <span className="action-text">Create new project</span>
              <div className="action-icon">
                <ArrowRight size={20} />
              </div>
            </div>

            {/* Gradient orb decoration */}
            <div className="card-orb orb-emerald" />
          </div>

          {/* Open Project Card */}
          <div
            className="project-card open-project-card"
            onClick={onOpenProject}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                onOpenProject();
              }
            }}
          >
            <div className="card-header">
              <div className="card-icon open-project-icon">
                <FolderOpen size={28} />
              </div>
              <h2 className="card-title">Open Project</h2>
            </div>

            <p className="card-description">
              Continue working on existing projects. Access your saved projects, view iterations, and manage your project portfolio in one place.
            </p>

            <div className="card-features">
              <div className="feature-badge">Project History</div>
              <div className="feature-badge">Version Control</div>
              <div className="feature-badge">Collaboration Ready</div>
            </div>

            <div className="card-footer">
              <span className="action-text">Browse projects</span>
              <div className="action-icon">
                <ArrowRight size={20} />
              </div>
            </div>

            {/* Gradient orb decoration */}
            <div className="card-orb orb-blue" />
          </div>

                    {/* Cyber Intelligence Assessment Card */}
          <div
            className="project-card cyber-assessment-card"
            onClick={onCyberAssessment}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onCyberAssessment();
              }
            }}
          >
            <div className="card-header">
              <div className="card-icon cyber-assessment-icon">
                <ShieldCheck size={28} />
              </div>
              <h2 className="card-title">
                Cyber Intelligence Assessment
              </h2>
            </div>
          
            <p className="card-description">
              Analyze your generated backend for potential security
              vulnerabilities, static analysis findings, and code complexity.
              Generate a consolidated assessment report with actionable
              recommendations.
            </p>
          
            <div className="card-features">
              <div className="feature-badge">
                Security Analysis
              </div>
              <div className="feature-badge">
                Static Code Analysis
              </div>
              <div className="feature-badge">
                Risk Assessment Report
              </div>
            </div>
          
            <div className="card-footer">
              <span className="action-text">
                Assess project security
              </span>
              <div className="action-icon">
                <ArrowRight size={20} />
              </div>
            </div>
          
            <div className="card-orb orb-cyber" />
          </div>
        </section>

        {/* Stats Section */}
        <section className="home-stats">
          <div className="stat-item">
            <div className="stat-number">4</div>
            <div className="stat-label">Specialized<br />AI Agents</div>
          </div>
          <div className="stat-divider" />
          <div className="stat-item">
            <div className="stat-number">100%</div>
            <div className="stat-label">Open Source<br />Architecture</div>
          </div>
          <div className="stat-divider" />
          <div className="stat-item">
            <div className="stat-number">⚡</div>
            <div className="stat-label">Real-time<br />Agentic Workflow</div>
          </div>
        </section>
      </main>

      {/* Create Project Modal */}
      <CreateProjectModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onCreateProject={handleCreateProject}
        isLoading={isLoading}
      />
    </div>
  );
}
