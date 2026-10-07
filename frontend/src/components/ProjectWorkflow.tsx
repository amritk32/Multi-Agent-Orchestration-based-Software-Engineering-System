import { useState, useCallback, useRef, useEffect } from 'react';
import { CheckCircle2, Circle, AlertCircle, Activity, ArrowUpRight, RotateCcw, Sparkles, Copy, Check, ArrowLeft, Layers, Bot } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { apiClient } from '../api';
import { WorkflowStep, StreamMessage, GenerationResult } from '../types';
import ArtifactPage from './ArtifactPage';
import ProjectChatPage from './ProjectChatPage';

const WORKFLOW_STEPS: WorkflowStep[] = [
  {
    id: 'requirements',
    name: 'Requirements',
    description: 'Analyzing requirements',
    status: 'pending',
  },
  {
    id: 'architecture',
    name: 'Architecture',
    description: 'Designing architecture',
    status: 'pending',
  },
  {
    id: 'boilerplate',
    name: 'Boilerplate',
    description: 'Creating structure',
    status: 'pending',
  },
  {
    id: 'code_writing',
    name: 'Code Writing',
    description: 'Generating code',
    status: 'pending',
  },
  {
    id: 'syntax_analysis',
    name: 'Syntax Analysis',
    description: 'Checking generated code',
    status: 'pending',
  },
  {
    id: 'analysis',
    name: 'README Generation',
    description: 'Analyzing code and writing README',
    status: 'pending',
  },
];

interface ProjectWorkflowProps {
  onBack: () => void;
  projectId: string;
  projectName: string;
  initialResult?: GenerationResult | null;
}

export default function ProjectWorkflow({ onBack, projectId, projectName, initialResult = null }: ProjectWorkflowProps) {
  const [requirements, setRequirements] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [steps, setSteps] = useState<WorkflowStep[]>(WORKFLOW_STEPS);
  const [result, setResult] = useState<GenerationResult | null>(null);
  const [backendCode, setBackendCode] = useState('');
  const [frontendCode, setFrontendCode] = useState('');
  const [showResults, setShowResults] = useState(false);
  const [showArtifacts, setShowArtifacts] = useState(false);
  const [showProjectChat, setShowProjectChat] = useState(false);
  const [copiedFile, setCopiedFile] = useState<string | null>(null);
  const currentFileRef = useRef<'backend' | 'frontend'>('backend');

  useEffect(() => {
    if (!initialResult) return;

    setRequirements(initialResult.requirements || '');
    setResult(initialResult);
    setBackendCode(initialResult.backend_code || initialResult.code || '');
    setFrontendCode(initialResult.frontend_code || '');
    setSteps(WORKFLOW_STEPS.map((step) => ({
      ...step,
      status: 'completed',
      description: step.id === 'syntax_analysis'
        ? initialResult.syntax_valid === false
          ? `Syntax errors found${initialResult.syntax_error ? `: ${initialResult.syntax_error}` : ''}`
          : 'No syntax errors found'
        : step.description,
      error: step.id === 'syntax_analysis' && initialResult.syntax_valid === false
        ? initialResult.syntax_error || 'Generated code contains syntax errors.'
        : undefined,
      timestamp: Date.now(),
    })));
    setShowResults(true);
  }, [initialResult]);

  const copyGeneratedCode = useCallback(async (file: 'backend' | 'frontend', content: string) => {
    if (!content) return;
    try {
      await navigator.clipboard.writeText(content);
      setCopiedFile(file);
      window.setTimeout(() => setCopiedFile(null), 1800);
    } catch {
      setError('Unable to copy generated code.');
    }
  }, []);

  const updateStep = useCallback((stepId: string, updates: Partial<WorkflowStep>) => {
    setSteps((prev) =>
      prev.map((step) =>
        step.id === stepId ? { ...step, ...updates } : step
      )
    );
  }, []);

  const handleStreamMessage = useCallback(
    (message: StreamMessage) => {
      console.log('Stream message:', message);

      switch (message.type) {
        case 'agent_start':
          updateStep(message.agent || '', {
            status: 'in-progress',
            timestamp: Date.now(),
          });
          break;

        case 'agent_end':
          const syntaxUpdate = message.agent === 'syntax_analysis'
            ? {
                description: message.syntax_valid
                  ? 'No syntax errors found'
                  : `Syntax errors found${message.syntax_error ? `: ${message.syntax_error}` : ''}`,
                error: message.syntax_valid === false
                  ? message.syntax_error || 'Generated code contains syntax errors.'
                  : undefined,
              }
            : {};
          updateStep(message.agent || '', {
            status: 'completed',
            timestamp: Date.now(),
            ...syntaxUpdate,
          });
          break;

        case 'file_start':
          if (message.file) {
            currentFileRef.current = message.file;
            if (message.file === 'backend') setBackendCode('');
            if (message.file === 'frontend') setFrontendCode('');
          }
          break;

        case 'code_token':
          if (message.token) {
            const file = message.file || currentFileRef.current;
            if (file === 'backend') {
              setBackendCode((current) => current + message.token);
            } else {
              setFrontendCode((current) => current + message.token);
            }
          }
          break;

        case 'status':
          setError(null);
          break;

        case 'complete':
          if (message.data) {
            const fullResult = message.data as unknown as GenerationResult;
            setResult(fullResult);

            // Added changes
            if (fullResult.backend_code || fullResult.code) {
                setBackendCode(fullResult.backend_code || fullResult.code || '');
            }
            if (fullResult.frontend_code) {
                setFrontendCode(fullResult.frontend_code);
            }
            // -------------------

            if (fullResult.code) setBackendCode(fullResult.code);
            updateStep('syntax_analysis', {
              description: fullResult.syntax_valid === false
                ? `Syntax errors found${fullResult.syntax_error ? `: ${fullResult.syntax_error}` : ''}`
                : 'No syntax errors found',
              error: fullResult.syntax_valid === false
                ? fullResult.syntax_error || 'Generated code contains syntax errors.'
                : undefined,
            });
          }
          setIsLoading(false);
          break;

        case 'error':
          setError(message.error || 'An error occurred');
          updateStep(message.agent || '', {
            status: 'error',
            error: message.error,
          });
          setIsLoading(false);
          break;
      }
    },
    [updateStep]
  );

  const handleGenerate = useCallback(async (req: string) => {
    if (!req.trim()) {
      setError('Please enter your requirements');
      return;
    }

    setIsLoading(true);
    setError(null);
    setBackendCode('');
    setFrontendCode('');
    currentFileRef.current = 'backend';
    setResult(null);
    setShowArtifacts(false);
    setShowResults(true);
    setSteps(WORKFLOW_STEPS.map((step) => ({ ...step, status: 'pending', error: undefined })));

    try {
      const streamPromise = new Promise<void>((resolve, reject) => {
        apiClient.generateCodeStream(
          req,
          handleStreamMessage,
          (error) => {
            console.error('Stream error:', error);
            reject(error);
          },
          () => resolve(),
          projectId
        );
      });

      try {
        await streamPromise;
      } catch (streamError) {
        console.log('Stream endpoint not available, using standard API...', streamError);
        const fullResult = await apiClient.generateCode(req, projectId);
        setResult(fullResult);

        // Added changes
        setBackendCode(fullResult.backend_code || fullResult.code || '');
        setFrontendCode(fullResult.frontend_code || '');
        // ---------------------
        setSteps((prev) =>
          prev.map((step) => ({
            ...step,
            description: step.id === 'syntax_analysis'
              ? fullResult.syntax_valid === false
                ? `Syntax errors found${fullResult.syntax_error ? `: ${fullResult.syntax_error}` : ''}`
                : 'No syntax errors found'
              : step.description,
            error: step.id === 'syntax_analysis' && fullResult.syntax_valid === false
              ? fullResult.syntax_error || 'Generated code contains syntax errors.'
              : undefined,
            status: 'completed' as const,
            timestamp: Date.now(),
          }))
        );
        setIsLoading(false);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate code';
      setError(errorMessage);
      setIsLoading(false);
    }
  }, [handleStreamMessage]);

  const getStepIcon = (status: string) => {
    if (status === 'completed') {
      return <CheckCircle2 className="w-5 h-5 text-emerald-green" />;
    }
    if (status === 'in-progress') {
      return <div className="w-5 h-5 border-2 border-emerald-green border-t-transparent rounded-full animate-spin" />;
    }
    if (status === 'error') {
      return <AlertCircle className="w-5 h-5 text-red-500" />;
    }
    return <Circle className="w-5 h-5 text-gray-500" />;
  };

  if (showResults) {
    if (showArtifacts && result) {
      return (
        <ArtifactPage
          result={result}
          projectName={projectName}
          onBack={() => setShowArtifacts(false)}
        />
      );
    }
    if (showProjectChat && result) {
      return (
        <ProjectChatPage
          projectId={projectId}
          projectName={projectName}
          onBack={() => setShowProjectChat(false)}
        />
      );
    }

    return (
      <div className="signal-shell">
        {/* Header */}
        <div className="signal-header">
          <div className="header-back-group">
            <button
              onClick={() => {
                setShowResults(false);
                setRequirements('');
                setSteps(WORKFLOW_STEPS.map((s) => ({ ...s, status: 'pending' })));
              }}
              className="header-back-button"
              title="Start a new run"
            >
              <RotateCcw size={16} /> New run
            </button>
            <div className="header-back-divider" />
            <button
              onClick={onBack}
              className="header-back-button"
              title="Back to home"
            >
              <ArrowLeft size={16} /> Home
            </button>
          </div>
          <div className="brand-mark"><span className="brand-icon"><Activity size={21} /></span> krishna.code</div>
          <div className="network-status"><span className="status-dot" /><span className="mono-label">Agent network online</span></div>
        </div>

        <div className="results-shell">
          <div className="results-header"><div><div className="eyebrow">Intelligence workspace / 06</div><h1 className="results-title">Generation signal</h1></div></div>
          <div className="results-actions">
            <button
              className="artifacts-launcher"
              onClick={() => setShowArtifacts(true)}
              disabled={!result || isLoading}
              title="Open project artifacts"
            >
              <Layers size={18} />
              <span><small>Workspace</small>Artifacts</span>
              <ArrowUpRight size={17} />
            </button>
            <button
              className="project-chat-launcher"
              onClick={() => setShowProjectChat(true)}
              disabled={!result || isLoading}
              title="Ask questions about this project"
            >
              <Bot size={18} />
              <span><small>Grounded assistant</small>Ask the project</span>
              <ArrowUpRight size={17} />
            </button>
          </div>
          <div className="results-grid">
            {/* Workflow Steps */}
            <div className="lg:col-span-1">
              <div className="sticky top-20 space-y-3">
                <h2 className="workflow-title mono-label">Agent pipeline</h2>
                {steps.map((step) => (
                  <div
                    key={step.id}
                    className={`workflow-item ${
                      step.status === 'completed'
                        ? 'border-emerald-green/50 bg-emerald-green/5'
                        : step.status === 'in-progress'
                        ? 'border-emerald-green bg-emerald-green/10'
                        : step.status === 'error'
                        ? 'border-red-500/50 bg-red-500/5'
                        : 'border-gray-700 bg-gray-900/50'
                    }`}
                  >
                    <div className="mt-0.5">{getStepIcon(step.status)}</div>
                    <div className="flex-1 min-w-0">
                      <p>{step.name}</p>
                      <p className="text-xs text-gray-400 truncate">{step.description}</p>
                    </div>
                  </div>
                ))}
                {steps.find((step) => step.id === 'syntax_analysis')?.status === 'completed' && (
                  <div className={`syntax-verdict ${steps.find((step) => step.id === 'syntax_analysis')?.error ? 'has-errors' : 'is-valid'}`}>
                    <span className="syntax-verdict-icon">
                      {steps.find((step) => step.id === 'syntax_analysis')?.error ? <AlertCircle size={17} /> : <CheckCircle2 size={17} />}
                    </span>
                    <span>
                      <strong>{steps.find((step) => step.id === 'syntax_analysis')?.error ? 'Syntax errors found' : 'No syntax errors found'}</strong>
                      <small>{steps.find((step) => step.id === 'syntax_analysis')?.error || 'Generated code passed the syntax check.'}</small>
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Code Display */}
            <div className="lg:col-span-2">
              <div className="space-y-4">
                {error && (
                  <div className="p-4 rounded-lg border border-red-500/50 bg-red-500/10">
                    <p className="text-sm text-red-300 font-mono">{error}</p>
                  </div>
                )}

                {[
                  { id: 'backend', label: 'Backend file', code: backendCode, language: 'python' },
                  { id: 'frontend', label: 'Frontend file', code: frontendCode, language: 'javascript' },
                ].map((file) => (
                  <div className="result-code" key={file.id}>
                    <div className="code-toolbar">
                      <span className="text-sm text-gray-300 font-medium flex items-center gap-2">
                        {isLoading && currentFileRef.current === file.id && <div className="w-2 h-2 rounded-full bg-emerald-green animate-pulse" />}
                        {file.label}
                      </span>
                      <button
                        className="copy-code-button"
                        onClick={() => void copyGeneratedCode(file.id as 'backend' | 'frontend', file.code)}
                        disabled={!file.code}
                        title={`Copy ${file.label}`}
                      >
                        {copiedFile === file.id ? <Check size={15} /> : <Copy size={15} />}
                        {copiedFile === file.id ? 'Copied' : 'Copy code'}
                      </button>
                    </div>
                    <div className="p-2">
                      <SyntaxHighlighter
                        language={file.language}
                        style={vscDarkPlus}
                        useInlineStyles={false}
                        customStyle={{ margin: 0, background: 'transparent', fontSize: '13px', fontFamily: "'JetBrains Mono', monospace" }}
                        showLineNumbers={true}
                        lineNumberStyle={{ color: '#414a63', paddingRight: '16px', minWidth: '40px' }}
                      >
                        {file.code || `# Waiting for ${file.label}...`}
                      </SyntaxHighlighter>
                    </div>
                  </div>
                ))}

              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="signal-shell">
      <header className="signal-header">
        <button
          onClick={onBack}
          className="header-back-button"
          title="Back to home"
        >
          <ArrowLeft size={16} /> Home
        </button>
        <div className="brand-mark"><span className="brand-icon"><Activity size={21} /></span> krishna.code</div>
        <div className="network-status"><span className="status-dot" /><span className="mono-label">Agent network online</span></div>
        <button className="new-generation" title="Reset workspace" onClick={() => setRequirements('')}><RotateCcw size={16} /></button>
      </header>

      <main className="intake-layout">
        <section>
          <div className="eyebrow">{projectName} / workspace</div>
          <h1 className="hero-title">Turn the<br />noise <em>into signal.</em></h1>
          <p className="hero-copy">A focused engineering desk for turning your ideas into working software, with an agent network that explains every decision.</p>
          <div className="hero-meta"><span className="meta-icon"><Sparkles size={15} /></span> Complete agent orchestration <ArrowUpRight size={15} /></div>
          <div className="hero-stats"><div className="hero-stat">05<small>agents ready</small></div><div className="hero-stat">7D<small>always learning</small></div><div className="hero-stat">AI<small>native workflow</small></div></div>
        </section>

        <section className="intake-panel">
          <div className="panel-topline mono-label"><span>Node_04 / intake</span><span className="secure-link">Secure link</span></div>
          <div className="panel-question">What should we investigate?</div>
          <textarea
            value={requirements}
            onChange={(e) => setRequirements(e.target.value)}
            placeholder="e.g. A REST API for a todo app with database integration"
            className="intake-textarea"
            rows={2}
            onKeyDown={(e) => { if (e.ctrlKey && e.key === 'Enter') handleGenerate(requirements); }}
          />
          <div className="panel-controls">
            <button className="panel-submit" onClick={() => handleGenerate(requirements)} disabled={isLoading || !requirements.trim()} title="Start agentic workflow">
              <span>{isLoading ? 'Launching Workflow...' : 'Start Agentic Workflow 🚀'}</span>
              <ArrowUpRight size={19} />
            </button>
          </div>
          <div className="pipeline"><div className="pipeline-label mono-label">Agent pipeline <span>/ ready to deploy</span></div><div className="pipeline-nodes"><div className="pipeline-node"><span className="node-icon"><Activity size={14} /></span>Discover</div><span className="pipeline-line" /><div className="pipeline-node"><span className="node-icon"><Circle size={14} /></span>Verify</div><span className="pipeline-line" /><div className="pipeline-node"><span className="node-icon"><Sparkles size={14} /></span>Synthesize</div></div></div>
          {error && <div className="error-banner">{error}</div>}
        </section>
      </main>
    </div>
  );
}
