import { useState } from 'react';
import { ArrowLeft, Check, Clipboard, FileText, Layers, Network, Package } from 'lucide-react';
import { GenerationResult } from '../types';

interface ArtifactPageProps {
  result: GenerationResult;
  projectName: string;
  onBack: () => void;
}

type ArtifactKey = 'requirements' | 'architecture' | 'boilerplate' | 'readme';

const ARTIFACTS: Array<{
  key: ArtifactKey;
  label: string;
  description: string;
  icon: typeof FileText;
  accent: string;
}> = [
  {
    key: 'requirements',
    label: 'Requirements',
    description: 'The structured brief extracted from your idea.',
    icon: FileText,
    accent: 'artifact-cyan',
  },
  {
    key: 'architecture',
    label: 'Architecture',
    description: 'The system design and implementation plan.',
    icon: Network,
    accent: 'artifact-blue',
  },
  {
    key: 'boilerplate',
    label: 'Boilerplate',
    description: 'The project structure prepared for code generation.',
    icon: Package,
    accent: 'artifact-amber',
  },
  {
    key: 'readme',
    label: 'README',
    description: 'The generated guide for using and extending the project.',
    icon: Layers,
    accent: 'artifact-pink',
  },
];

export default function ArtifactPage({ result, projectName, onBack }: ArtifactPageProps) {
  const [selected, setSelected] = useState<ArtifactKey>('requirements');
  const [copied, setCopied] = useState<ArtifactKey | null>(null);

  const values: Record<ArtifactKey, string> = {
    requirements: result.requirements || 'No requirements were saved.',
    architecture: result.architecture || 'No architecture was saved.',
    boilerplate: result.boilerplate || 'No boilerplate was saved.',
    readme: result.report || 'No README was saved for this project.',
  };

  const copyArtifact = async (key: ArtifactKey) => {
    try {
      await navigator.clipboard.writeText(values[key]);
      setCopied(key);
      window.setTimeout(() => setCopied(null), 1800);
    } catch {
      setCopied(null);
    }
  };

  const selectedArtifact = ARTIFACTS.find((artifact) => artifact.key === selected)!;

  return (
    <div className="signal-shell artifact-shell">
      <header className="signal-header">
        <button onClick={onBack} className="header-back-button" title="Back to generation">
          <ArrowLeft size={16} /> Back to generation
        </button>
        <div className="brand-mark"><span className="brand-icon"><Layers size={21} /></span> krishna.code</div>
        <div className="network-status"><span className="status-dot" /><span className="mono-label">Artifact vault</span></div>
      </header>

      <main className="artifact-layout">
        <div className="artifact-heading">
          <div>
            <div className="eyebrow">{projectName} / artifacts</div>
            <h1 className="results-title">Project artifacts</h1>
            <p className="artifact-intro">Choose an output to inspect, copy, or carry into your next build.</p>
          </div>
          <div className="artifact-count mono-label">04 outputs ready</div>
        </div>

        <div className="artifact-page-grid">
          <nav className="artifact-list" aria-label="Project artifacts">
            {ARTIFACTS.map((artifact) => {
              const Icon = artifact.icon;
              return (
                <button
                  key={artifact.key}
                  onClick={() => setSelected(artifact.key)}
                  className={`artifact-choice ${artifact.accent} ${selected === artifact.key ? 'selected' : ''}`}
                >
                  <span className="artifact-choice-icon"><Icon size={19} /></span>
                  <span className="artifact-choice-copy">
                    <strong>{artifact.label}</strong>
                    <small>{artifact.description}</small>
                  </span>
                  <ArrowLeft className="artifact-choice-arrow" size={16} />
                </button>
              );
            })}
          </nav>

          <section className={`artifact-view ${selectedArtifact.accent}`}>
            <div className="artifact-view-header">
              <div>
                <span className="artifact-kicker mono-label">Selected artifact</span>
                <h2>{selectedArtifact.label}</h2>
              </div>
              <button className="copy-code-button artifact-copy" onClick={() => copyArtifact(selected)} title={`Copy ${selectedArtifact.label}`}>
                {copied === selected ? <Check size={16} /> : <Clipboard size={16} />}
                {copied === selected ? 'Copied' : 'Copy artifact'}
              </button>
            </div>
            <pre className="artifact-content">{values[selected]}</pre>
          </section>
        </div>
      </main>
    </div>
  );
}
