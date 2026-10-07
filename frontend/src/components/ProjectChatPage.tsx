import { FormEvent, useState } from 'react';
import { ArrowLeft, Bot, Send, Sparkles, User } from 'lucide-react';
import { apiClient } from '../api';

interface ProjectChatPageProps {
  projectId: string;
  projectName: string;
  onBack: () => void;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
}

function AssistantContent({ content }: { content: string }) {
  const blocks = content.split(/\n\s*\n/).filter(Boolean);

  return (
    <div className="project-chat-markdown">
      {blocks.map((block, index) => {
        const lines = block.split('\n');
        const isList = lines.every((line) => /^\s*[-*]\s+/.test(line));
        if (isList) {
          return (
            <ul key={index}>
              {lines.map((line) => <li key={line}>{line.replace(/^\s*[-*]\s+/, '')}</li>)}
            </ul>
          );
        }
        if (lines.length === 1 && /^#{1,3}\s/.test(lines[0])) {
          return <h3 key={index}>{lines[0].replace(/^#{1,3}\s/, '')}</h3>;
        }
        return <p key={index}>{block}</p>;
      })}
    </div>
  );
}

export default function ProjectChatPage({ projectId, projectName, onBack }: ProjectChatPageProps) {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const askQuestion = async (event: FormEvent) => {
    event.preventDefault();
    const value = question.trim();
    if (!value || isLoading) return;

    setMessages((current) => [...current, { role: 'user', content: value }]);
    setQuestion('');
    setError('');
    setIsLoading(true);
    try {
      const assistantIndex = messages.length + 1;
      setMessages((current) => [...current, { role: 'assistant', content: '' }]);
      await apiClient.streamProjectChat(
        projectId,
        value,
        (sources) => setMessages((current) => current.map((message, index) => index === assistantIndex ? { ...message, sources } : message)),
        (token) => setMessages((current) => current.map((message, index) => index === assistantIndex ? { ...message, content: message.content + token } : message)),
        () => setIsLoading(false),
        (streamError) => {
          setError(streamError);
          setIsLoading(false);
        },
      );
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'The project chatbot is unavailable.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="signal-shell project-chat-shell">
      <header className="project-chat-topbar">
        <button onClick={onBack} className="header-back-button" title="Back to generation">
          <ArrowLeft size={16} /> Back to generation
        </button>
        <div className="project-chat-brand"><span className="project-chat-brand-icon"><Bot size={17} /></span><strong>Ask your project</strong><span>{projectName}</span></div>
        <div className="project-chat-online"><span className="status-dot" /> Grounded context online</div>
      </header>

      <main className="project-chat-layout">
        <div className="project-chat-heading">
          <div className="eyebrow">{projectName} / project intelligence</div>
          <h1 className="results-title">Ask your project</h1>
          <p>Answers are grounded in this project's generated files.</p>
        </div>

        <section className="project-chat-panel">
          <div className="project-chat-status"><Sparkles size={18} /><span>Answers use requirements, architecture, boilerplate, backend, frontend, and README context.</span></div>
          <div className="project-chat-messages" aria-live="polite">
            {messages.length === 0 && (
              <div className="project-chat-empty">
                <span className="project-chat-empty-icon"><Sparkles size={22} /></span>
                <strong>What would you like to understand?</strong>
                <span>Ask about setup, architecture, APIs, or how a feature works.</span>
              </div>
            )}
            {messages.map((message, index) => (
              <div className={`project-chat-message ${message.role}`} key={`${message.role}-${index}`}>
                <span className="project-chat-avatar">{message.role === 'user' ? <User size={16} /> : <Bot size={16} />}</span>
                <div>
                  {message.role === 'assistant' ? <AssistantContent content={message.content || 'Thinking...'} /> : <div className="project-chat-bubble">{message.content}</div>}
                  {message.sources && message.sources.length > 0 && (
                    <div className="project-chat-sources"><span>Sources</span>{message.sources.map((source) => <span className="project-chat-source-pill" key={source}>{source}</span>)}</div>
                  )}
                </div>
              </div>
            ))}
            {isLoading && <div className="project-chat-loading"><span /> Searching project documents...</div>}
          </div>
          <form className="project-chat-form" onSubmit={askQuestion}>
            <input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask anything about this project..." disabled={isLoading} />
            <button type="submit" disabled={isLoading || !question.trim()} title="Ask project chatbot"><Send size={17} /></button>
          </form>
          {error && <div className="project-chat-error">{error}</div>}
        </section>
      </main>
    </div>
  );
}
