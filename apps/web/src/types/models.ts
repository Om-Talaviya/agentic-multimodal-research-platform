export type ProfileType = 'balanced' | 'cost_minimized' | 'speed_maximized' | 'quality_maximized' | 'custom'

export interface OptimizationProfile {
  name: string
  profile_type: ProfileType
  quality_weight: number
  speed_weight: number
  cost_weight: number
  locality_weight: number
  max_latency_ms?: number
  max_cost_per_1k?: number
  require_local?: boolean
  prefer_local?: boolean
  description?: string
}

export interface ModelScore {
  model_id: string
  provider_name: string
  total_score: number
  quality_score: number
  speed_score: number
  cost_score: number
  locality_score: number
  is_pareto_optimal: boolean
  rank: number
  tier: string
  is_local: boolean
  estimated_cost_per_1k: number
  rationale: string
}

export interface OptimizationResult {
  selected_model_id: string
  selected_provider: string
  profile_used: OptimizationProfile
  ranked_candidates: ModelScore[]
  pareto_frontier: string[]
  tradeoff_analysis: string
}

export interface LeaderboardEntry {
  rank: number
  model_id: string
  provider_name: string
  overall_score: number
  factual_accuracy: number
  reasoning_depth: number
  retrieval_faithfulness: number
  citation_precision: number
  mean_latency_ms: number
  cost_per_1k_usd: number
  tier: string
  is_local: boolean
  is_pareto_optimal: boolean
  last_evaluated: string | null
}

export interface SampleEvaluationResult {
  id?: string
  sample_id: string
  category: string
  prompt: string
  response_text: string
  passed: boolean
  score: number
  metrics: Record<string, number>
  latency_ms: number
  prompt_tokens: number
  completion_tokens: number
  cost_usd: number
  error_message?: string
}

export interface EvaluationRecord {
  id: string
  model_id: string
  provider_name: string
  benchmark_name: string
  total_samples: number
  passed_samples: number
  pass_rate: number
  overall_score: number
  mean_accuracy: number
  mean_reasoning: number
  mean_faithfulness: number
  mean_citation_precision: number
  mean_latency_ms: number
  total_cost_usd: number
  category_scores: Record<string, number>
  triggered_by?: string | null
  created_at: string
  sample_results?: SampleEvaluationResult[]
}
