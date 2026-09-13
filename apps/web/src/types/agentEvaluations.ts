export interface AgentStepMetric {
  id?: string
  evaluation_id?: string
  step_index: number
  agent_type: string
  action_type: string
  tool_name?: string | null
  tool_args: Record<string, any>
  tool_output_length: number
  success: boolean
  error_message?: string | null
  latency_ms: number
  tokens_consumed: number
  created_at?: string | null
}

export interface AgentEvaluationRecord {
  id: string
  job_id?: string | null
  agent_name: string
  total_steps: number
  successful_steps: number
  failed_steps: number
  plan_precision: number
  tool_accuracy: number
  evidence_coverage: number
  hallucination_rate: number
  synthesis_fidelity: number
  overall_score: number
  execution_time_ms: number
  total_tokens: number
  estimated_cost_usd: number
  findings_audit: Record<string, any>
  evaluated_by?: string | null
  created_at: string
  steps?: AgentStepMetric[]
}

export interface AgentMetricsSummary {
  total_evaluations: number
  avg_score: number
  avg_plan_precision: number
  avg_tool_accuracy: number
  avg_evidence_coverage: number
  avg_hallucination_rate: number
  avg_synthesis_fidelity: number
  total_tokens_consumed: number
  total_cost_usd: number
}
