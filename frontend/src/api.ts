import axios, { AxiosInstance } from 'axios';
import { GenerationResult, StreamMessage } from './types';

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ProjectSummary {
  project_id: string;
  project_name: string;
  created_at: string;
}

export interface ProjectDetails extends ProjectSummary {
  artifacts: {
    requirements: string | null;
    architecture: string | null;
    boilerplate: string | null;
    generated_code: string | null;
    backend_code: string | null;  
    frontend_code: string | null;
    readme: string | null;
  } | null;
}

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await this.client.get('/api/health');
    return response.data;
  }

  async getProjects(): Promise<ProjectSummary[]> {
    const response = await this.client.get('/api/projects');
    return response.data;
  }

  // Added start Risk assesment module
  async startRiskAssessment(projectId: string) {
    try {
      const response = await this.client.post(
        `/api/projects/${projectId}/audit`
      );
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const detail = error.response?.data?.detail;
        if (typeof detail === 'string') {
          throw new Error(detail);
        }
      }
      throw error;
    }
  }


  async getProject(projectId: string): Promise<ProjectDetails> {
    const response = await this.client.get(`/api/projects/${projectId}`);
    return response.data;
  }

  async deleteProject(projectId: string): Promise<void> {
    await this.client.delete(`/api/projects/${projectId}`);
  }

  async streamProjectChat(
    projectId: string,
    question: string,
    onSources: (sources: string[]) => void,
    onToken: (token: string) => void,
    onComplete: () => void,
    onError: (error: string) => void,
  ): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/projects/${projectId}/chat-stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });
      if (!response.ok || !response.body) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.detail || 'The project chatbot is unavailable.');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      while (true) {
        const { value, done } = await reader.read();
        buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
        const events = buffer.split('\n\n');
        buffer = events.pop() || '';
        for (const event of events) {
          const line = event.split('\n').find((item) => item.startsWith('data: '));
          if (!line) continue;
          const message = JSON.parse(line.slice(6)) as { type: string; token?: string; sources?: string[]; error?: string };
          if (message.type === 'sources') onSources(message.sources || []);
          if (message.type === 'token' && message.token) onToken(message.token);
          if (message.type === 'complete') onComplete();
          if (message.type === 'error') onError(message.error || 'The project chatbot failed.');
        }
        if (done) break;
      }
    } catch (error) {
      onError(error instanceof Error ? error.message : 'The project chatbot is unavailable.');
    }
  }

  async generateCode(requirements: string, projectId?: string): Promise<GenerationResult> {
    try {
      const response = await this.client.post('/api/generate', {
        requirements,
        project_id: projectId,
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const detail = error.response?.data?.detail;
        if (typeof detail === 'string') throw new Error(detail);
      }
      throw error;
    }
  }

  async generateCodeStream(
    requirements: string,
    onMessage: (message: StreamMessage) => void,
    onError: (error: string) => void,
    onComplete: () => void,
    projectId?: string
  ): Promise<void> {
    try {
      const params = new URLSearchParams({
        requirements,
      });
      if (projectId) {
        params.append('project_id', projectId);
      }
      const eventSource = new EventSource(
        `${API_BASE_URL}/api/generate-stream?${params}`
      );
      let streamOpened = false;
      let streamCompleted = false;

      eventSource.addEventListener('open', () => {
        streamOpened = true;
      });

      eventSource.addEventListener('message', (event) => {
        try {
          const message = JSON.parse(event.data) as StreamMessage;
          onMessage(message);
          if (message.type === 'complete') {
            streamCompleted = true;
            eventSource.close();
            onComplete();
          }
        } catch (e) {
          console.error('Failed to parse message:', e);
        }
      });

      eventSource.addEventListener('error', (event) => {
        eventSource.close();
        if (!streamCompleted && !streamOpened) {
          const errorMessage = (event as ErrorEvent).message || 'Stream connection failed';
          onError(errorMessage);
        }
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      onError(errorMessage);
    }
  }
}

export const apiClient = new APIClient();
