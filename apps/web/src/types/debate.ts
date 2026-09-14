export interface DebateCitation {
  source_id?: string;
  title: string;
  url?: string;
  snippet: string;
  reliability: number;
}

export interface DebateRound {
  id: string;
  round_number: number;
  proposer_argument: string;
  opposer_argument: string;
  proposer_citations: DebateCitation[];
  opposer_citations: DebateCitation[];
  proposer_score: number;
  opposer_score: number;
  arbiter_critique?: string;
  round_winner?: string;
  elo_delta: number;
  created_at: string;
}

export interface AcceptedClaim {
  claim: string;
  confidence: number;
  grounding?: string;
}

export interface RefutedClaim {
  claim: string;
  reason: string;
}

export interface Concession {
  side: 'proposer' | 'opposer';
  point: string;
}

export interface DebateConsensus {
  id: string;
  debate_id: string;
  consensus_statement: string;
  accepted_claims: AcceptedClaim[];
  refuted_claims: RefutedClaim[];
  concessions: Concession[];
  remaining_uncertainties: string[];
  overall_confidence: number;
  winner_overall: string;
  final_proposer_elo: number;
  final_opposer_elo: number;
  created_at: string;
}

export interface AgentDebate {
  id: string;
  topic: string;
  initial_thesis: string;
  counter_thesis?: string;
  status: 'active' | 'concluded' | 'deadlocked' | 'paused';
  max_rounds: number;
  current_round: number;
  proposer_model: string;
  opposer_model: string;
  arbiter_model: string;
  proposer_elo: number;
  opposer_elo: number;
  rounds_count?: number;
  has_consensus?: boolean;
  rounds?: DebateRound[];
  consensus?: DebateConsensus;
  created_at: string;
}

export interface DebateMetrics {
  total_debates: number;
  active_debates: number;
  concluded_debates: number;
  mean_confidence: number;
  proposer_avg_elo: number;
  opposer_avg_elo: number;
}

export interface CreateDebatePayload {
  topic: string;
  initial_thesis: string;
  counter_thesis?: string;
  max_rounds: number;
  proposer_model?: string;
  opposer_model?: string;
  arbiter_model?: string;
  workspace_id?: string;
  project_id?: string;
}
