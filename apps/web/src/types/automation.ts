/**
 * TypeScript types for Research Automation, Scheduled Sweeps, and Alerts (Phase 26).
 */

export interface ScheduledResearch {
  id: string;
  user_id: string;
  workspace_id?: string | null;
  title: string;
  query_topic: string;
  cron_expression: string;
  routing_profile: string;
  source_types: string[];
  novelty_threshold: number;
  confidence_threshold: number;
  contradiction_alert: boolean;
  webhook_url?: string | null;
  email_notifications: string[];
  status: 'active' | 'paused' | 'completed' | 'failed';
  total_sweeps_count: number;
  last_run_at?: string | null;
  next_run_at?: string | null;
  last_findings_summary?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ResearchSweepResult {
  id: string;
  schedule_id: string;
  job_id?: string | null;
  status: 'completed' | 'no_novel_findings' | 'alert_dispatched' | 'failed';
  findings_count: number;
  novel_claims_count: number;
  novelty_score: number;
  novel_claims: Array<{
    claim?: string;
    summary?: string;
    confidence?: number;
    topic?: string;
    source?: string;
  }>;
  contradictions_found: Array<{
    claim_a?: string;
    claim_b?: string;
    reason?: string;
  }>;
  alert_dispatched: boolean;
  execution_duration_ms: number;
  executed_at: string;
}

export interface AutomationAlert {
  id: string;
  schedule_id: string;
  sweep_id?: string | null;
  job_id?: string | null;
  workspace_id?: string | null;
  title: string;
  severity: 'info' | 'warning' | 'critical';
  channel: 'in_app' | 'webhook' | 'email';
  message: string;
  payload: Record<string, any>;
  is_acknowledged: boolean;
  acknowledged_at?: string | null;
  created_at: string;
}

export interface AutomationMetrics {
  total_schedules: number;
  active_schedules: number;
  total_sweeps: number;
  average_novelty_score: number;
  total_alerts: number;
  unacknowledged_alerts: number;
}

export interface CreateSchedulePayload {
  title: string;
  query_topic: string;
  cron_expression?: string;
  routing_profile?: string;
  source_types?: string[];
  novelty_threshold?: number;
  confidence_threshold?: number;
  contradiction_alert?: boolean;
  webhook_url?: string;
  email_notifications?: string[];
  workspace_id?: string;
}
