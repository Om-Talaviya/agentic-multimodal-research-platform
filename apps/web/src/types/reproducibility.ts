export interface ClaimVerificationTrace {
  id: string;
  run_id: string;
  claim_statement: string;
  metric_name: string;
  claimed_value: number;
  reproduced_value: number;
  delta_relative_error: number;
  tolerance_threshold: number;
  verdict: 'reproduced' | 'discrepant' | 'refuted' | 'inconclusive';
  analysis_notes?: string;
  created_at?: string;
}

export interface ReproducibilityRun {
  id: string;
  status: 'pending' | 'running' | 'succeeded' | 'failed' | 'timeout';
  execution_time_ms: number;
  memory_peak_mb: number;
  reproduced_metrics: Record<string, number>;
  reproducibility_score: number;
  runtime_logs?: string;
  error_message?: string;
  created_at: string;
}

export interface ExperimentProtocol {
  id: string;
  name: string;
  description?: string;
  source_paper_title?: string;
  source_doi?: string;
  runtime_language: string;
  executable_code?: string;
  parameters?: Record<string, any>;
  dependencies?: string[];
  claimed_metrics?: Record<string, number>;
  verification_status: 'unverified' | 'fully_reproduced' | 'partially_reproduced' | 'discrepant' | 'failed';
  total_runs?: number;
  runs?: ReproducibilityRun[];
  verification_traces?: ClaimVerificationTrace[];
  created_at: string;
}

export interface ReproducibilityMetrics {
  total_protocols: number;
  total_runs: number;
  succeeded_runs: number;
  run_success_rate: number;
  total_verified_claims: number;
  reproduced_claims: number;
  claim_reproducibility_rate: number;
  average_reproducibility_score: number;
}

export interface CreateProtocolPayload {
  name: string;
  executable_code: string;
  description?: string;
  source_paper_title?: string;
  source_doi?: string;
  runtime_language?: string;
  parameters?: Record<string, any>;
  dependencies?: string[];
  claimed_metrics?: Record<string, number>;
  workspace_id?: string;
  project_id?: string;
}
