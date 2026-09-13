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
