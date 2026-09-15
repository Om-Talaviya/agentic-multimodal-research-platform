/**
 * Official TypeScript Client SDK for AI Research OS (Agentic Multimodal Research Platform).
 * Supports browser, Node.js, and edge environments.
 */

export interface SDKClientOptions {
  apiKey?: string;
  baseUrl?: string;
  authToken?: string; // Optional JWT token for user session mode
  timeoutMs?: number;
}

export interface ResearchJobCreatePayload {
  question: string;
  objective?: string;
  domain?: string;
  scope?: "shallow" | "deep" | "exhaustive";
  projectId?: string;
  timeoutSeconds?: number;
}

export interface TaskStatus {
  id: string;
  description: string;
  agent_type: string;
  status: string;
  dependencies: string[];
  output?: Record<string, any>;
  error?: string;
}

export interface SynthesisReport {
  id?: string;
  executive_summary: string;
  findings: Array<{ claim: string; confidence: number; sources?: string[] }>;
  methodology: Record<string, any>;
  conclusions: string[];
  limitations: string[];
  confidence_score: number;
}

export interface ResearchJobDetails {
  job_id: string;
  request_id: string;
  status: "pending" | "running" | "completed" | "failed" | "cancelled";
  question: string;
  objective?: string;
  domain: string;
  scope: string;
  created_at?: string;
  started_at?: string;
  completed_at?: string;
  tasks: TaskStatus[];
  report?: SynthesisReport;
  poll_url?: string;
}

export interface DocumentIngestPayload {
  title: string;
  text_content: string;
  filename?: string;
  project_id?: string;
}

export interface DocumentIngestResponse {
  document_id: string;
  title: string;
  filename?: string;
  chunks_count: number;
  status: string;
  message: string;
}

export interface ApiUsageSummary {
  key_prefix: string;
  rate_limit_tier: string;
  rate_limit_rpm: number;
  scopes: string[];
  total_requests: number;
  total_tokens_consumed: number;
  total_cost_usd: number;
}

export class AIResearchOSError extends Error {
  constructor(message: string, public statusCode?: number, public details?: any) {
    super(message);
    this.name = "AIResearchOSError";
  }
}

export class AIResearchClient {
  private baseUrl: string;
  private apiKey?: string;
  private authToken?: string;
  private timeoutMs: number;

  constructor(options: SDKClientOptions = {}) {
    this.baseUrl = (options.baseUrl || "http://localhost:8000").replace(/\/$/, "");
    this.apiKey = options.apiKey;
    this.authToken = options.authToken;
    this.timeoutMs = options.timeoutMs || 60000;
  }

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (this.apiKey) {
      headers["X-API-Key"] = this.apiKey;
    } else if (this.authToken) {
      headers["Authorization"] = `Bearer ${this.authToken}`;
    }

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeoutMs);

    try {
      const response = await fetch(`${this.baseUrl}${path}`, {
        ...options,
        headers,
        signal: controller.signal,
      });

      if (!response.ok) {
        let errorData: any = {};
        try {
          errorData = await response.json();
        } catch {
          errorData = { detail: await response.text() };
        }
        throw new AIResearchOSError(
          errorData.detail || `HTTP error ${response.status}`,
          response.status,
          errorData
        );
      }

      return (await response.json()) as T;
    } finally {
      clearTimeout(timer);
    }
  }

  // ==========================================
  // Research Job Operations
  // ==========================================
  public research = {
    create: async (payload: ResearchJobCreatePayload): Promise<ResearchJobDetails> => {
      return this.request<ResearchJobDetails>("/api/v1/developer/research", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },

    get: async (jobId: string): Promise<ResearchJobDetails> => {
      return this.request<ResearchJobDetails>(`/api/v1/developer/research/${jobId}`, {
        method: "GET",
      });
    },

    list: async (limit = 50, offset = 0): Promise<{ jobs: ResearchJobDetails[]; total: number }> => {
      return this.request<{ jobs: ResearchJobDetails[]; total: number }>(
        `/api/v1/developer/research?limit=${limit}&offset=${offset}`,
        { method: "GET" }
      );
    },

    pollUntilComplete: async (
      jobId: string,
      intervalMs = 2000,
      maxWaitMs = 300000
    ): Promise<ResearchJobDetails> => {
      const startTime = Date.now();
      while (Date.now() - startTime < maxWaitMs) {
        const job = await this.research.get(jobId);
        if (job.status === "completed" || job.status === "failed" || job.status === "cancelled") {
          return job;
        }
        await new Promise((resolve) => setTimeout(resolve, intervalMs));
      }
      throw new AIResearchOSError(`Polling timed out after ${maxWaitMs}ms for job ${jobId}`);
    },
  };

  // ==========================================
  // Document Operations
  // ==========================================
  public documents = {
    ingest: async (payload: DocumentIngestPayload): Promise<DocumentIngestResponse> => {
      return this.request<DocumentIngestResponse>("/api/v1/developer/documents", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    },
  };

  // ==========================================
  // Developer Usage & Quotas
  // ==========================================
  public usage = {
    getSummary: async (): Promise<ApiUsageSummary> => {
      return this.request<ApiUsageSummary>("/api/v1/developer/usage", {
        method: "GET",
      });
    },
  };
}

export default AIResearchClient;
