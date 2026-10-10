import { useEffect, useState } from 'react';
import {
  Activity,
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  FolderOpen,
  Loader2,
  ShieldCheck,
  ShieldAlert,
} from 'lucide-react';
import { apiClient, ProjectDetails, ProjectSummary } from '../api';

interface CyberIntelligencePageProps {
  onBack: () => void;
}


interface AssessmentFinding {
  title?: string;
  severity?: string;
  description?: string;
  recommendation?: string;
  file_path?: string;
  file?: string;
  line_number?: number;
  line?: number;
  confidence?: number | string;
  [key: string]: unknown;
}

interface AssessmentReportData {
  overall_summary?: string;
  security_findings?: AssessmentFinding[];
  static_analysis_findings?: AssessmentFinding[];
  complexity_findings?: AssessmentFinding[];
  [key: string]: unknown;
}

interface AssessmentResponse {
  success?: boolean;
  project_id?: string;
  report_id?: string;
  status?: string;
  created_at?: string;
  report?: AssessmentReportData;
}


export default function CyberIntelligencePage({
  onBack,
}: CyberIntelligencePageProps) {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [selectedProject, setSelectedProject] =
    useState<ProjectDetails | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
  const [isAssessing, setIsAssessing] = useState(false);

  const [error, setError] = useState('');
  const [report, setReport] = useState<AssessmentResponse | null>(null);

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
          setError(
            requestError instanceof Error
              ? requestError.message
              : 'Unable to load projects.',
          );
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

  const selectProject = async (projectId: string) => {
    setIsLoadingDetails(true);
    setError('');
    setReport(null);
    setSelectedProject(null);

    try {
      const details = await apiClient.getProject(projectId);
      setSelectedProject(details);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : 'Unable to load project details.',
      );
    } finally {
      setIsLoadingDetails(false);
    }
  };

  const startAssessment = async () => {
    if (!selectedProject) return;

    const backendCode = selectedProject.artifacts?.backend_code;

    if (!backendCode?.trim()) {
      setError(
        'This project has no generated backend code to assess. Select a project with backend code.',
      );
      return;
    }

    setIsAssessing(true);
    setError('');
    setReport(null);

    try {
      const result = await apiClient.startRiskAssessment(
        selectedProject.project_id,
      );

      setReport(result as AssessmentResponse);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : 'Risk assessment failed.',
      );
    } finally {
      setIsAssessing(false);
    }
  };

  return (
    <div className="signal-shell">
      <header className="signal-header">
        <button
          onClick={onBack}
          className="header-back-button"
          type="button"
        >
          <ArrowLeft size={16} />
          Home
        </button>

        <div className="brand-mark">
          <span className="brand-icon">
            <Activity size={21} />
          </span>
          krishna.code
        </div>

        <div className="network-status">
          <span className="status-dot" />
          <span className="mono-label">Agent network online</span>
        </div>
      </header>

      <main className="open-project-layout cyber-assessment-page">
        <div className="open-project-container">
          <div className="eyebrow">
            Intelligence workspace / 03
          </div>

          <h1 className="open-project-title">
            Cyber Intelligence Assessment
          </h1>

          <p className="open-project-description">
            Assess generated backend code using security analysis,
            static analysis, and code complexity checks.
          </p>

          {error && (
            <div className="project-browser-error" role="alert">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          <div className="project-browser-grid">
            <section className="project-list-panel">
              <div className="project-panel-heading">
                <span className="mono-label">Select a project</span>
                <span className="project-count">
                  {projects.length}
                </span>
              </div>

              {isLoading ? (
                <div className="project-state">
                  <Loader2
                    className="project-spinner"
                    size={22}
                  />
                  <span>Loading projects...</span>
                </div>
              ) : projects.length === 0 ? (
                <div className="project-state">
                  <FolderOpen size={30} />
                  <strong>No saved projects</strong>
                  <span>
                    Create a project before starting an assessment.
                  </span>
                </div>
              ) : (
                <div className="project-list">
                  {projects.map((project) => (
                    <button
                      key={project.project_id}
                      type="button"
                      className={`project-list-item ${
                        selectedProject?.project_id ===
                        project.project_id
                          ? 'selected'
                          : ''
                      }`}
                      onClick={() =>
                        void selectProject(project.project_id)
                      }
                      disabled={isLoadingDetails || isAssessing}
                    >
                      <span className="project-list-icon">
                        <FolderOpen size={17} />
                      </span>

                      <span className="project-list-copy">
                        <strong>{project.project_name}</strong>
                        <small>
                          {new Date(
                            project.created_at,
                          ).toLocaleDateString()}
                        </small>
                      </span>

                      {selectedProject?.project_id ===
                        project.project_id && (
                        <CheckCircle2 size={18} />
                      )}
                    </button>
                  ))}
                </div>
              )}
            </section>

            <section className="project-detail-panel">
              {isLoadingDetails ? (
                <div className="project-state">
                  <Loader2
                    className="project-spinner"
                    size={24}
                  />
                  <span>Loading project details...</span>
                </div>
              ) : !selectedProject ? (
                <div className="project-state project-select-state">
                  <ShieldCheck size={38} />
                  <strong>Ready for assessment</strong>
                  <span>
                    Select a saved project to inspect its backend
                    availability and start the risk assessment.
                  </span>
                </div>
              ) : (
                <div className="cyber-assessment-details">
                  <div className="project-detail-header">
                    <div>
                      <span className="mono-label">
                        Selected project
                      </span>
                      <h2>{selectedProject.project_name}</h2>
                    </div>
                  </div>

                  <div className="cyber-code-status">
                    {selectedProject.artifacts?.backend_code?.trim() ? (
                      <>
                        <CheckCircle2 size={20} />
                        <div>
                          <strong>Backend code available</strong>
                          <p>
                            This project can be submitted for
                            assessment.
                          </p>
                        </div>
                      </>
                    ) : (
                      <>
                        <ShieldAlert size={20} />
                        <div>
                          <strong>Backend code unavailable</strong>
                          <p>
                            Choose a project with generated backend
                            code to continue.
                          </p>
                        </div>
                      </>
                    )}
                  </div>

                  <div className="cyber-assessment-scope">
                    <h3>🛡️ Assessment Scope</h3>

                    <div className="cyber-scope-list">
                      <div className="cyber-scope-item">
                        <span>🔐</span>
                        <div>
                          <strong>Security Analysis</strong>
                          <p>Potential vulnerabilities and security risks</p>
                        </div>
                      </div>

                      <div className="cyber-scope-item">
                        <span>🔎</span>
                        <div>
                          <strong>Static Code Analysis</strong>
                          <p>Code quality issues and suspicious patterns</p>
                        </div>
                      </div>

                      <div className="cyber-scope-item">
                        <span>🧩</span>
                        <div>
                          <strong>Complexity Analysis</strong>
                          <p>Complex functions and maintainability concerns</p>
                        </div>
                      </div>

                      <div className="cyber-scope-item">
                        <span>📋</span>
                        <div>
                          <strong>Consolidated Report</strong>
                          <p>Findings and recommended next steps</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <button
                    type="button"
                    className="cyber-assessment-button"
                    onClick={() => void startAssessment()}
                    disabled={
                      isAssessing ||
                      !selectedProject.artifacts?.backend_code?.trim()
                    }
                  >
                    {isAssessing ? (
                      <>
                        <Loader2
                          className="project-spinner"
                          size={18}
                        />
                        Running assessment...
                      </>
                    ) : (
                      <>
                        <ShieldCheck size={18} />
                        Start Risk Assessment
                      </>
                    )}
                  </button>

                  {isAssessing && (
                    <p className="cyber-assessment-hint">
                      The agents are analyzing the backend. This may
                      take some time; keep this page open.
                    </p>
                  )}
                </div>
              )}
            </section>
          </div>


          {report !== null && (
            <section className="cyber-report-panel">
              <div className="cyber-report-header">
                <div>
                  <span className="mono-label">
                    🛡️ ASSESSMENT COMPLETED
                  </span>
                  <h2>Cyber Intelligence Report</h2>
                  <p>
                    {selectedProject?.project_name}
                  </p>
                </div>
          
                <span className="cyber-report-status">
                  <CheckCircle2 size={16} />
                  {report.status || 'Completed'}
                </span>
              </div>
          
              <div className="cyber-report-body">
                <div className="cyber-report-section">
                  <h3>📝 Executive Summary</h3>
                  <p className="cyber-summary-text">
                    {report.report?.overall_summary ||
                      'The report did not provide an overall summary.'}
                  </p>
                </div>
                    
                {(
                  [
                    {
                      key: 'security_findings',
                      title: '🔐 Security Findings',
                    },
                    {
                      key: 'static_analysis_findings',
                      title: '🔎 Static Analysis Findings',
                    },
                    {
                      key: 'complexity_findings',
                      title: '🧩 Complexity Findings',
                    },
                  ] as const
                ).map(({ key, title }) => {
                  const findings = report.report?.[key];
                
                  return (
                    <div className="cyber-report-section" key={key}>
                      <h3>{title}</h3>
                  
                      {!Array.isArray(findings) || findings.length === 0 ? (
                        <p className="cyber-empty-findings">
                          No findings were returned in this category.
                        </p>
                      ) : (
                        <div className="cyber-findings-list">
                          {findings.map((finding, index) => {
                            const severity = String(
                              finding.severity || 'Unspecified',
                            ).toLowerCase();
                          
                            const location =
                              finding.file_path || finding.file;
                          
                            const line =
                              finding.line_number ?? finding.line;
                          
                            return (
                              <article
                                className="cyber-finding-card"
                                key={`${key}-${index}`}
                              >
                                <div className="cyber-finding-heading">
                                  <h4>
                                    {finding.title || `Finding ${index + 1}`}
                                  </h4>
                            
                                  <span
                                    className={`cyber-severity severity-${severity}`}
                                  >
                                    {severity.toUpperCase()}
                                  </span>
                                </div>
                            
                                {finding.description && (
                                  <p>{finding.description}</p>
                                )}
          
                                {location && (
                                  <p className="cyber-finding-location">
                                    📁 {String(location)}
                                    {line != null ? ` · Line ${line}` : ''}
                                  </p>
                                )}
          
                                {finding.recommendation && (
                                  <div className="cyber-recommendation">
                                    <strong>💡 Recommendation</strong>
                                    <p>{finding.recommendation}</p>
                                  </div>
                                )}
                              </article>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  );
                })}
          
                <details className="cyber-raw-details">
                  <summary>🔧 View raw API response (debugging)</summary>
                  <pre>{JSON.stringify(report, null, 2)}</pre>
                </details>
              </div>
            </section>
          )}

        </div>
      </main>
    </div>
  );
}
